const api = (path) => fetch(path).then((r) => r.json());
let liveData = [];
let chart;
let candleSeries;
let predictionSeries;

function initTabs() {
  document.querySelectorAll('.tab-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-btn').forEach((b) => b.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach((c) => c.classList.remove('active'));
      btn.classList.add('active');
      document.getElementById(btn.dataset.tab).classList.add('active');
    });
  });
}

function renderCards(rows) {
  const container = document.getElementById('live-table');
  container.innerHTML = '';
  rows.forEach((s) => {
    const div = document.createElement('div');
    div.className = 'card';
    div.innerHTML = `
      <strong>${s.name}</strong> <small>(${s.symbol})</small>
      <div>₹ ${s.close.toLocaleString()}</div>
      <div class="${s.change_pct >= 0 ? 'pos' : 'neg'}">${s.change_pct}%</div>
      <small>O: ${s.open} H: ${s.high} L: ${s.low} C: ${s.close}</small><br>
      <small>Volume: ${s.volume.toLocaleString()} | ${s.index}</small>
    `;
    div.onclick = () => loadChart(s.symbol);
    container.appendChild(div);
  });
}

function initChart() {
  chart = LightweightCharts.createChart(document.getElementById('chart-container'), {
    layout: { background: { color: '#1e293b' }, textColor: '#e2e8f0' },
    grid: { vertLines: { color: '#334155' }, horzLines: { color: '#334155' } },
    crosshair: { mode: 1 },
    timeScale: { timeVisible: true, secondsVisible: false },
  });
  candleSeries = chart.addCandlestickSeries();
  predictionSeries = chart.addLineSeries({ color: '#f59e0b', lineWidth: 2 });
}

async function loadChart(symbol) {
  const data = await api(`/api/market/historical/${symbol}`);
  if (data.error) return;
  candleSeries.setData(data.candles);
  predictionSeries.setData(data.prediction);
}

function updateSwitch() {
  const sw = document.getElementById('symbol-switch');
  sw.innerHTML = liveData.map((i) => `<option value="${i.symbol}">${i.name} (${i.symbol})</option>`).join('');
  sw.onchange = (e) => loadChart(e.target.value);
}

function renderHeatmap() {
  const grouped = {};
  liveData.forEach((s) => {
    grouped[s.sector] = grouped[s.sector] || [];
    grouped[s.sector].push(s.change_pct);
  });
  const container = document.getElementById('heatmap');
  container.innerHTML = '';
  Object.entries(grouped).forEach(([sector, vals]) => {
    const avg = vals.reduce((a, b) => a + b, 0) / vals.length;
    const div = document.createElement('div');
    div.className = 'heat-cell';
    div.style.background = avg >= 0 ? '#14532d' : '#7f1d1d';
    div.innerHTML = `${sector}<br>${avg.toFixed(2)}%`;
    container.appendChild(div);
  });
}

async function loadWatchlist() {
  const data = await api('/api/watchlist');
  const ul = document.getElementById('watchlist');
  ul.innerHTML = '';
  data.forEach((w) => {
    const li = document.createElement('li');
    li.innerHTML = `${w.name} (${w.symbol}) <button data-s="${w.symbol}">Remove</button>`;
    li.querySelector('button').onclick = async () => {
      await fetch('/api/watchlist', { method: 'DELETE', headers: {'Content-Type':'application/json'}, body: JSON.stringify({symbol: w.symbol})});
      loadWatchlist();
    };
    ul.appendChild(li);
  });
}

async function loadNews(symbol) {
  const news = await api(`/api/news/${symbol}`);
  const ul = document.getElementById('news-list');
  ul.innerHTML = '';
  news.forEach((n) => {
    const li = document.createElement('li');
    li.innerHTML = `<a href="${n.url}" target="_blank">${n.title}</a> <small>${n.source || ''}</small>`;
    ul.appendChild(li);
  });
}

async function loadSentiment() {
  const s = await api('/api/market/sentiment');
  document.getElementById('sentiment').textContent = `Sentiment: ${s.sentiment} (${s.score}%)`;
}

async function loadGainersLosers() {
  const gl = await api('/api/market/gainers-losers');
  const div = document.getElementById('gainers-losers');
  const gainers = (gl.gainers || []).map((g) => `<li class='pos'>${g.symbol}: ${g.change_pct}%</li>`).join('');
  const losers = (gl.losers || []).map((g) => `<li class='neg'>${g.symbol}: ${g.change_pct}%</li>`).join('');
  div.innerHTML = `<strong>Gainers</strong><ul>${gainers}</ul><strong>Losers</strong><ul>${losers}</ul>`;
}

async function loadLive() {
  document.getElementById('loader').style.display = 'block';
  const response = await api('/api/market/live');
  liveData = response.data;
  const filter = document.getElementById('sector-filter').value;
  const q = document.getElementById('search-box').value.toLowerCase();
  const filtered = liveData.filter((x) => (filter === 'all' || x.sector === filter) && (`${x.name} ${x.symbol}`.toLowerCase().includes(q)));
  renderCards(filtered);
  renderHeatmap();
  updateSwitch();
  if (filtered.length) {
    await loadChart(filtered[0].symbol);
    await loadNews(filtered[0].symbol);
    document.getElementById('market-status').textContent = `Market: ${filtered[0].market_status}`;
  }
  document.getElementById('loader').style.display = 'none';
  loadSentiment();
  loadGainersLosers();
}

function setupSearchAndFilter() {
  document.getElementById('search-box').addEventListener('input', loadLive);
  document.getElementById('sector-filter').addEventListener('change', loadLive);
}

window.addEventListener('load', async () => {
  initTabs();
  initChart();
  setupSearchAndFilter();
  await loadLive();
  await loadWatchlist();

  setInterval(loadLive, 20000);

  document.getElementById('live-table').addEventListener('dblclick', async (e) => {
    const card = e.target.closest('.card');
    if (!card) return;
    const symbol = card.querySelector('small').textContent.match(/\((.*?)\)/)?.[1];
    if (!symbol) return;
    await fetch('/api/watchlist', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({symbol})});
    loadWatchlist();
  });
});
