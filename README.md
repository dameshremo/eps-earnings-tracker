EPS Consensus Earnings Estimate Tracker
Replicating "Trade Like a Stock Market Wizard" — Chapter 7
A full-stack dashboard that replicates the Consensus EPS Earnings Trends and Earnings Estimate Revisions analysis described in Mark Minervini's book. Uses 100% free data via Yahoo Finance (yfinance).

📁 Project Structure
eps-dashboard/
├── backend/
│   ├── app.py              # Flask API server
│   └── requirements.txt    # Python dependencies
├── frontend/
│   └── index.html          # Full dashboard (single file)
└── README.md

🚀 Quick Start
Step 1 — Install Python backend dependencies
bashcd backend
pip install -r requirements.txt
Step 2 — Start the backend API server
bashpython app.py
You should see:
Starting EPS Dashboard Backend on http://localhost:5001
Step 3 — Open the frontend
Simply open frontend/index.html in your browser:

Double-click the file, OR
Run: open frontend/index.html (macOS) / start frontend/index.html (Windows)

Step 4 — Analyze a stock

Type any US ticker (e.g., AAPL, NVDA, MSFT)
Click Analyze → or press Enter
The dashboard will display live consensus EPS estimate trends


🎯 Demo Mode (No Backend Required)
Click the Demo Mode tab in the top-right to use pre-loaded sample data (AAPL-like) without needing the backend running. Great for testing the UI.

📊 What the Dashboard Shows
1. Consensus EPS Estimate Trends Table (Main)
Mimics Figure 7.3 from the book — shows EPS estimates for:

This Quarter / Next Quarter / This Year / Next Year
Across time: Current → 7 Days Ago → 30 Days Ago → 60 Days Ago → 90 Days Ago

Green = estimates trending up (bullish signal)
2. 30-Day Revision % Tiles
Computes the % change in estimates from 30 days ago to today for each period.



5% revision = strong bullish signal


< -5% revision = red flag (Minervini warns against this)

3. Signal Analysis Panel
Automated interpretation:

Estimate Momentum (short-term)
Broad Estimate Trend (all 4 periods)
Red Flag Check (large downward revisions)

4. EPS Trend Line Chart
Visual of current vs 30-day-ago vs 90-day-ago estimates across all four periods.
5. Revision % Bar Chart
Green/red bars showing direction and magnitude of estimate changes.
6. EPS Revisions Detail
Number of analyst upgrades/downgrades to estimates over 7 and 30 days.
7. Analyst Upgrades/Downgrades
Recent rating changes from firms (upgrade, downgrade, initiate, maintain).
8. Earnings History Chart
Actual EPS vs estimated EPS, with beat/miss tracking.

📖 The Minervini Framework (from the book)

"Look for companies for which analysts are raising estimates. Quarterly as well as current fiscal year estimates should be trending higher; the bigger the estimate revisions, the better."
— Mark Minervini, Trade Like a Stock Market Wizard

Key rules replicated:

Current fiscal year OR next year estimates should trend higher from 30 days earlier
Both trending = even better signal
Large downward revisions = red flag (avoid as buy candidate)
Upward revision of ≥5% = significant bullish signal


⚠️ Data Notes

Data sourced from Yahoo Finance via yfinance (free, no API key needed)
eps_trend provides the main table: current/7d/30d/60d/90d estimates
eps_revisions provides up/down analyst count changes
upgrades_downgrades tracks rating changes
Some tickers may have incomplete data — the app handles missing values gracefully


🛠️ Troubleshooting
IssueSolution"Cannot connect to backend"Make sure python app.py is running, or use Demo ModeEmpty table for a tickerYahoo Finance may not have analyst estimates for this stock (try large-cap US stocks)CORS errorThe Flask backend has CORS enabled by defaultyfinance rate limitedWait a few minutes and retry

📦 Dependencies
Backend

flask — Web server
flask-cors — Cross-origin support
yfinance — Yahoo Finance data
pandas, numpy — Data processing

Frontend

Vanilla HTML/CSS/JS (no build step)
Chart.js (CDN) — Charts
Google Fonts (CDN) — Typography


🔄 Extending the Dashboard
Want to add more? Here are ideas:

Historical estimate trend — Store past API results in SQLite to show true multi-month trends
Screener mode — Scan a list of tickers and rank by estimate momentum
Email alerts — Notify when a stock's estimates revise up >5%
Export to CSV — Download the revision table


Inspired by Chapter 7 "Fundamentals to Focus On" in Trade Like a Stock Market Wizard by Mark Minervini
