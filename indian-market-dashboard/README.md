# Indian Market Analyzer (NSE/BSE Focus)

A modern, responsive stock market analysis and prediction web app focused on Indian markets.

## Features

- Live quotes (auto-refresh every 20 seconds)
- Indian index coverage:
  - NIFTY 50: Reliance, HDFC Bank, Infosys
  - SENSEX: TCS, ICICI Bank, L&T
  - NIFTY BANK: Axis Bank, SBI, Kotak Bank
- Commodities (MCX proxies via futures symbols): Crude Oil, Gold, Silver
- OHLC, volume, % change, market open/closed status
- 5-month historical candlestick chart
- 2-month Linear Regression forecast overlay
- Multi-stock switcher, search, sector filter
- Watchlist (persistent file storage)
- Market sentiment indicator
- Top gainers/losers widget
- Sector heatmap
- Education tab for Indian stock market basics
- News panel (Alpha Vantage integration + safe fallback)
- Caching and fallback sample data for reliability

## Tech Stack

- Frontend: HTML, CSS, Vanilla JavaScript
- Backend: Python Flask
- Data APIs:
  - Yahoo Finance (via `yfinance`)
  - Alpha Vantage (news, optional)
- Charting: TradingView Lightweight Charts (candlestick + line overlay)

## Project Structure

```text
indian-market-dashboard/
  backend/
    app.py
    requirements.txt
    watchlist.json (auto-generated)
  frontend/
    index.html
    css/styles.css
    js/app.js
```

## Setup

1. Create and activate a virtual environment:
   ```bash
   cd indian-market-dashboard/backend
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. (Optional) Configure Alpha Vantage key for live news:
   ```bash
   export ALPHAVANTAGE_API_KEY="your_key_here"
   ```

4. Run server:
   ```bash
   python app.py
   ```

5. Open in browser:
   - `http://127.0.0.1:5000`

## API Keys (How to Obtain)

### Alpha Vantage (optional, for news)
1. Go to https://www.alphavantage.co/support/#api-key
2. Create free API key.
3. Set env var: `ALPHAVANTAGE_API_KEY`.

### Yahoo Finance
- Used through `yfinance`; no API key required.

## Sample Data Fallback

If live quote APIs fail or are rate limited:
- The backend serves deterministic sample OHLC data per symbol.
- UI continues functioning without crashes.

## Notes

- Prices are displayed using the Indian currency symbol `₹`.
- Commodities are delivered through globally available futures proxies to ensure stability in free-tier environments.
- Prediction is educational only and not investment advice.
