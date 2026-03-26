"""
EPS Consensus Earnings Trend Dashboard - Backend
Fetches analyst estimate data from Yahoo Finance via yfinance
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import traceback
import os
import requests

app = Flask(__name__)
CORS(app)

# Fix for cloud server IP blocks by Yahoo Finance
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
})


def safe_float(val, default=None):
    try:
        if val is None or (isinstance(val, float) and np.isnan(val)):
            return default
        return round(float(val), 4)
    except:
        return default


def get_eps_trend_data(ticker: str):
    """
    Fetches eps_trend, eps_revisions, earnings_estimate from yfinance.
    Returns a structured dict matching the book's table format.
    """
    t = yf.Ticker(ticker, session=session)
    info = t.info

    result = {
        "ticker": ticker.upper(),
        "company_name": info.get("longName", ticker.upper()),
        "currency": info.get("currency", "USD"),
        "current_price": safe_float(info.get("currentPrice") or info.get("regularMarketPrice")),
        "market_cap": info.get("marketCap"),
        "sector": info.get("sector", "N/A"),
        "eps_trend_table": None,
        "eps_revisions_table": None,
        "earnings_estimate_table": None,
        "earnings_history": None,
        "upgrades_downgrades": None,
        "errors": []
    }

    # --- EPS Trend (the main table from the book) ---
    try:
        eps_trend = t.eps_trend
        if eps_trend is not None and not eps_trend.empty:
            result["eps_trend_table"] = eps_trend.to_dict()
    except Exception as e:
        result["errors"].append(f"eps_trend: {str(e)}")

    # --- EPS Revisions ---
    try:
        eps_rev = t.eps_revisions
        if eps_rev is not None and not eps_rev.empty:
            result["eps_revisions_table"] = eps_rev.to_dict()
    except Exception as e:
        result["errors"].append(f"eps_revisions: {str(e)}")

    # --- Earnings Estimate ---
    try:
        ee = t.earnings_estimate
        if ee is not None and not ee.empty:
            result["earnings_estimate_table"] = ee.to_dict()
    except Exception as e:
        result["errors"].append(f"earnings_estimate: {str(e)}")

    # --- Earnings History (actual vs estimate) ---
    try:
        eh = t.earnings_history
        if eh is not None and not eh.empty:
            eh_recent = eh.tail(8).copy()
            eh_recent.index = eh_recent.index.astype(str)
            result["earnings_history"] = eh_recent.to_dict(orient="index")
    except Exception as e:
        result["errors"].append(f"earnings_history: {str(e)}")

    # --- Upgrades/Downgrades (recent 30) ---
    try:
        ud = t.upgrades_downgrades
        if ud is not None and not ud.empty:
            ud_recent = ud.head(30).copy()
            ud_recent.index = ud_recent.index.astype(str)
            result["upgrades_downgrades"] = ud_recent.to_dict(orient="index")
    except Exception as e:
        result["errors"].append(f"upgrades_downgrades: {str(e)}")

    return result


def build_revision_table(eps_trend_dict, earnings_estimate=None):
    """
    Build revision table from eps_trend if available,
    otherwise fall back to earnings_estimate for Current row.
    """
    period_map = {
        "0q": "This Quarter",
        "+1q": "Next Quarter",
        "0y": "This Year",
        "+1y": "Next Year"
    }

    row_map = {
        "current": "Current",
        "7daysAgo": "7 Days Ago",
        "30daysAgo": "30 Days Ago",
        "60daysAgo": "60 Days Ago",
        "90daysAgo": "90 Days Ago"
    }

    # Initialize all cells to None
    table = {label: {p: None for p in period_map.values()} for label in row_map.values()}

    # Try eps_trend first (gives all 5 rows)
    if eps_trend_dict:
        for row_key, row_label in row_map.items():
            for period_key, period_label in period_map.items():
                try:
                    val = eps_trend_dict.get(period_key, {}).get(row_key)
                    table[row_label][period_label] = safe_float(val)
                except:
                    pass

    # Fall back to earnings_estimate for Current row if eps_trend unavailable
    if earnings_estimate and all(v is None for v in table["Current"].values()):
        avg = earnings_estimate.get("avg", {})
        for period_key, period_label in period_map.items():
            table["Current"][period_label] = safe_float(avg.get(period_key))

    return table


def compute_revision_pct(table):
    """
    Compute % revision from 30 days ago to current for each period.
    """
    if not table:
        return {}

    revisions = {}
    current = table.get("Current", {})
    thirty = table.get("30 Days Ago", {})

    for period in ["This Quarter", "Next Quarter", "This Year", "Next Year"]:
        cur = current.get(period)
        old = thirty.get(period)
        if cur is not None and old is not None and old != 0:
            pct = ((cur - old) / abs(old)) * 100
            revisions[period] = round(pct, 2)
        else:
            revisions[period] = None

    return revisions


@app.route("/api/eps/<ticker>", methods=["GET"])
def get_eps(ticker):
    try:
        data = get_eps_trend_data(ticker.upper())
        revision_table = build_revision_table(
            data.get("eps_trend_table"),
            data.get("earnings_estimate_table")
        )
        revision_pct = compute_revision_pct(revision_table)

        return jsonify({
            "success": True,
            "ticker": data["ticker"],
            "company_name": data["company_name"],
            "currency": data["currency"],
            "current_price": data["current_price"],
            "market_cap": data["market_cap"],
            "sector": data["sector"],
            "revision_table": revision_table,
            "revision_pct": revision_pct,
            "eps_revisions_table": data.get("eps_revisions_table"),
            "earnings_estimate_table": data.get("earnings_estimate_table"),
            "earnings_history": data.get("earnings_history"),
            "upgrades_downgrades": data.get("upgrades_downgrades"),
            "errors": data["errors"],
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "trace": traceback.format_exc()
        }), 500


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "time": datetime.now().isoformat()})


@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "message": "EPS Earnings Estimate Tracker API",
        "endpoints": {
            "health": "/api/health",
            "eps_data": "/api/eps/<ticker>  e.g. /api/eps/AAPL"
        }
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting EPS Dashboard Backend on http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port)