from __future__ import annotations

import os
import time
from datetime import datetime, timedelta
from typing import Dict, List

import numpy as np
import pandas as pd
import requests
import yfinance as yf
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from sklearn.linear_model import LinearRegression

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(os.path.dirname(BASE_DIR), "frontend")

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
CORS(app)

CACHE_TTL_SECONDS = 20
cache: Dict[str, Dict] = {}

WATCHLIST_FILE = os.path.join(BASE_DIR, "watchlist.json")

MARKET_SYMBOLS = {
    "NIFTY50": ["RELIANCE.NS", "HDFCBANK.NS", "INFY.NS"],
    "SENSEX": ["TCS.NS", "ICICIBANK.NS", "LT.NS"],
    "NIFTYBANK": ["AXISBANK.NS", "SBIN.NS", "KOTAKBANK.NS"],
    "COMMODITIES": ["CL=F", "GC=F", "SI=F"],
}

STOCK_META = {
    "RELIANCE.NS": {"name": "Reliance Industries", "sector": "Energy", "index": "NIFTY50"},
    "HDFCBANK.NS": {"name": "HDFC Bank", "sector": "Banking", "index": "NIFTY50"},
    "INFY.NS": {"name": "Infosys", "sector": "IT", "index": "NIFTY50"},
    "TCS.NS": {"name": "Tata Consultancy Services", "sector": "IT", "index": "SENSEX"},
    "ICICIBANK.NS": {"name": "ICICI Bank", "sector": "Banking", "index": "SENSEX"},
    "LT.NS": {"name": "Larsen & Toubro", "sector": "Infrastructure", "index": "SENSEX"},
    "AXISBANK.NS": {"name": "Axis Bank", "sector": "Banking", "index": "NIFTYBANK"},
    "SBIN.NS": {"name": "State Bank of India", "sector": "Banking", "index": "NIFTYBANK"},
    "KOTAKBANK.NS": {"name": "Kotak Mahindra Bank", "sector": "Banking", "index": "NIFTYBANK"},
    "CL=F": {"name": "Crude Oil (MCX Proxy)", "sector": "Commodities", "index": "COMMODITIES"},
    "GC=F": {"name": "Gold (MCX Proxy)", "sector": "Commodities", "index": "COMMODITIES"},
    "SI=F": {"name": "Silver (MCX Proxy)", "sector": "Commodities", "index": "COMMODITIES"},
}


def now_ts() -> float:
    return time.time()


def get_cache(key: str):
    data = cache.get(key)
    if data and now_ts() - data["ts"] < CACHE_TTL_SECONDS:
        return data["value"]
    return None


def set_cache(key: str, value):
    cache[key] = {"ts": now_ts(), "value": value}


def fetch_quote(symbol: str):
    tk = yf.Ticker(symbol)
    hist = tk.history(period="2d", interval="1d")
    if hist.empty:
        raise ValueError(f"No data for {symbol}")

    latest = hist.iloc[-1]
    previous_close = hist.iloc[-2]["Close"] if len(hist) > 1 else latest["Open"]

    change_pct = ((latest["Close"] - previous_close) / previous_close) * 100 if previous_close else 0

    info = STOCK_META.get(symbol, {})

    return {
        "symbol": symbol,
        "name": info.get("name", symbol),
        "sector": info.get("sector", "Unknown"),
        "index": info.get("index", "Other"),
        "open": round(float(latest["Open"]), 2),
        "high": round(float(latest["High"]), 2),
        "low": round(float(latest["Low"]), 2),
        "close": round(float(latest["Close"]), 2),
        "volume": int(latest["Volume"]),
        "change_pct": round(float(change_pct), 2),
        "currency": "INR",
        "market_status": market_status_india(),
    }


def market_status_india() -> str:
    now = datetime.utcnow() + timedelta(hours=5, minutes=30)
    if now.weekday() >= 5:
        return "Closed"
    start = now.replace(hour=9, minute=15, second=0, microsecond=0)
    end = now.replace(hour=15, minute=30, second=0, microsecond=0)
    return "Open" if start <= now <= end else "Closed"


def sample_quote(symbol: str):
    base = {
        "symbol": symbol,
        "name": STOCK_META.get(symbol, {}).get("name", symbol),
        "sector": STOCK_META.get(symbol, {}).get("sector", "Unknown"),
        "index": STOCK_META.get(symbol, {}).get("index", "Other"),
        "open": 1000.0,
        "high": 1020.0,
        "low": 995.0,
        "close": 1010.0,
        "volume": 500000,
        "change_pct": 1.0,
        "currency": "INR",
        "market_status": market_status_india(),
    }
    return base


def predict_prices(df: pd.DataFrame, days_ahead: int = 60):
    closes = df["Close"].values
    x = np.arange(len(closes)).reshape(-1, 1)
    y = closes

    model = LinearRegression()
    model.fit(x, y)

    future_x = np.arange(len(closes), len(closes) + days_ahead).reshape(-1, 1)
    preds = model.predict(future_x)

    last_date = df.index[-1]
    future_dates = [last_date + timedelta(days=i + 1) for i in range(days_ahead)]

    return [
        {"time": d.strftime("%Y-%m-%d"), "value": round(float(v), 2)}
        for d, v in zip(future_dates, preds)
    ]


def fetch_news(symbol: str):
    api_key = os.getenv("ALPHAVANTAGE_API_KEY", "")
    if not api_key:
        return [
            {
                "title": "Set ALPHAVANTAGE_API_KEY for live Indian market news feed",
                "url": "https://www.alphavantage.co/",
                "source": "System",
            }
        ]
    query = symbol.split(".")[0]
    url = (
        "https://www.alphavantage.co/query?function=NEWS_SENTIMENT"
        f"&tickers={query}&apikey={api_key}&limit=6"
    )
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        feed = data.get("feed", [])
        return [
            {"title": i.get("title"), "url": i.get("url"), "source": i.get("source")}
            for i in feed[:6]
        ]
    except Exception:
        return [{"title": "News service unavailable", "url": "#", "source": "System"}]


@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/api/market/live")
def api_live():
    cached = get_cache("live")
    if cached:
        return jsonify({"data": cached, "cached": True})

    output = []
    for group in MARKET_SYMBOLS.values():
        for symbol in group:
            try:
                output.append(fetch_quote(symbol))
            except Exception:
                output.append(sample_quote(symbol))

    set_cache("live", output)
    return jsonify({"data": output, "cached": False})


@app.route("/api/market/historical/<symbol>")
def api_historical(symbol):
    key = f"hist-{symbol}"
    cached = get_cache(key)
    if cached:
        return jsonify(cached)

    symbol = symbol.upper()
    try:
        df = yf.Ticker(symbol).history(period="5mo", interval="1d")
        if df.empty:
            raise ValueError("Empty historical series")

        candles = [
            {
                "time": idx.strftime("%Y-%m-%d"),
                "open": round(float(row["Open"]), 2),
                "high": round(float(row["High"]), 2),
                "low": round(float(row["Low"]), 2),
                "close": round(float(row["Close"]), 2),
            }
            for idx, row in df.iterrows()
        ]
        prediction = predict_prices(df, 60)

        payload = {
            "symbol": symbol,
            "candles": candles,
            "prediction": prediction,
            "label": "AI-Based Prediction (Not Guaranteed)",
        }
        set_cache(key, payload)
        return jsonify(payload)
    except Exception:
        return jsonify({"error": "Could not fetch historical data"}), 500


@app.route("/api/stocks/search")
def api_search():
    q = request.args.get("q", "").lower()
    results = []
    for sym, meta in STOCK_META.items():
        if q in sym.lower() or q in meta.get("name", "").lower():
            results.append({"symbol": sym, **meta})
    return jsonify(results[:12])


@app.route("/api/watchlist", methods=["GET", "POST", "DELETE"])
def api_watchlist():
    if request.method == "GET":
        if not os.path.exists(WATCHLIST_FILE):
            return jsonify([])
        with open(WATCHLIST_FILE, "r", encoding="utf-8") as f:
            return jsonify(pd.read_json(f).to_dict(orient="records"))

    payload = request.json or {}
    symbol = payload.get("symbol")
    if not symbol:
        return jsonify({"error": "symbol is required"}), 400

    watchlist = []
    if os.path.exists(WATCHLIST_FILE):
        with open(WATCHLIST_FILE, "r", encoding="utf-8") as f:
            watchlist = pd.read_json(f).to_dict(orient="records")

    if request.method == "POST":
        if symbol not in [i["symbol"] for i in watchlist]:
            watchlist.append({"symbol": symbol, "name": STOCK_META.get(symbol, {}).get("name", symbol)})
    elif request.method == "DELETE":
        watchlist = [i for i in watchlist if i["symbol"] != symbol]

    pd.DataFrame(watchlist).to_json(WATCHLIST_FILE, orient="records", indent=2)
    return jsonify(watchlist)


@app.route("/api/news/<symbol>")
def api_news(symbol):
    return jsonify(fetch_news(symbol))


@app.route("/api/market/sentiment")
def api_sentiment():
    data = get_cache("live") or []
    if not data:
        return jsonify({"sentiment": "Neutral", "score": 0})
    avg = float(np.mean([i.get("change_pct", 0) for i in data]))
    sentiment = "Bullish" if avg > 0.3 else "Bearish" if avg < -0.3 else "Neutral"
    return jsonify({"sentiment": sentiment, "score": round(avg, 2)})


@app.route("/api/market/gainers-losers")
def api_gainers_losers():
    data = get_cache("live") or []
    sorted_data = sorted(data, key=lambda x: x.get("change_pct", 0), reverse=True)
    return jsonify({"gainers": sorted_data[:5], "losers": sorted_data[-5:]})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
