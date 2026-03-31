# Practice-Projects

## Live Stock Analysis + Predictor

This repository now includes `live_stock_analysis_predictor.py`, a Python script that:

- Pulls live market data from Yahoo Finance at runtime.
- Analyzes **3 stocks from each of 3 major US indices**:
  - S&P 500: `AAPL`, `MSFT`, `JPM`
  - NASDAQ-100: `NVDA`, `AMZN`, `META`
  - Dow Jones: `UNH`, `HD`, `V`
- Predicts price targets for approximately:
  - **2 months ahead** (`~42` trading days)
  - **5 months ahead** (`~105` trading days)

### Run

```bash
python3 live_stock_analysis_predictor.py
```

Optional period override (historical window used for fitting):

```bash
python3 live_stock_analysis_predictor.py --period 24mo
```

### Dependencies

```bash
pip install yfinance pandas numpy
```

> Forecasts are trend-based estimates for educational use and are **not financial advice**.
