# 📈 Automated Forex Trading & Market Scanner System

A quantitative, rule-based trading system built in Python that scans live Forex, Gold, and Equity Index markets for high-probability trade setups using **John Murphy Technical Analysis** principles combined with a **3-Mode News Execution Handler**.

Designed to target **R4,000 ZAR/month (~$220 USD)** on a $5,000 prop-firm challenge account with strict risk controls.

---

## ✨ Features

- **Multi-Pair Market Scanner** — Scans 12 instruments across Forex Majors, Minors, Gold, and US Indices
- **John Murphy Strategy Engine** — EMA 50/200 trend filter + Support/Resistance bounce/rejection entries
- **3-Mode News Execution Handler** — Automatically switches between `NORMAL`, `HUNTER`, and `SHIELD` modes around high-impact news events
- **ATR-Based Duration Guidance** — Estimates trade holding time (day trade vs swing trade) for each setup
- **Risk Manager** — 1% risk per trade, 1:3 R:R minimum, 3% daily drawdown cap, 8% total drawdown limit
- **MT5 Execution Bridge** — Places live/demo orders directly on MetaTrader 5
- **Email Notifications** — Instant email alerts when a trade signal is triggered
- **Backtest Engine** — Simulates strategy performance on 60 days of historical 1H candles
- **Docker Support** — Run the scanner in a containerized, cross-platform environment

---

## 🏗️ Project Structure

```
trading/
├── main.py                   # CLI entrypoint (scan, backtest, demo modes)
├── scanner.py                # MarketScanner — core scanning & signal output engine
├── config/
│   └── config.py             # Global trading parameters (risk, timeframes, targets)
├── data/
│   ├── market_data.py        # Historical candle fetcher + technical indicator calculator
│   └── news_data.py          # Economic calendar / high-impact news data engine
├── strategy/
│   ├── john_murphy_strategy.py  # EMA trend + S/R entry signal logic
│   └── news_handler.py          # NORMAL / HUNTER / SHIELD mode switcher
├── risk/
│   └── risk_manager.py       # Position sizing, drawdown limits, lot calculation
├── execution/
│   ├── mt5_bridge.py         # MetaTrader 5 order placement bridge
│   └── backtester.py         # Historical backtest simulation engine
├── utils/
│   └── notifier.py           # SMTP email alert system
├── Dockerfile                # Multi-platform container build
├── docker-compose.yml        # Docker Compose service definition
├── run_scanner_cron.sh       # Cron helper script for scheduled scanning
├── requirements.txt
└── .env.example              # Environment variable template
```

---

## ⚙️ Configuration

All core parameters live in [`config/config.py`](config/config.py):

| Parameter | Default | Description |
|---|---|---|
| `INITIAL_BALANCE` | `$5,000.00` | Prop firm account size |
| `TIMEFRAME` | `1h` | Candle interval |
| `RISK_PER_TRADE_PCT` | `1%` | Max risk per trade |
| `MIN_RISK_REWARD_RATIO` | `1:3` | Minimum R:R before a trade is accepted |
| `MAX_DAILY_DRAWDOWN_PCT` | `3%` | Hard daily drawdown limit |
| `MAX_TOTAL_DRAWDOWN_PCT` | `8%` | Total max drawdown limit |
| `MONTHLY_PROFIT_TARGET_PCT` | `4.4%` | Target monthly yield (~$220 / R4,000) |
| `FAST_EMA_PERIOD` | `50` | Short-term trend EMA |
| `SLOW_EMA_PERIOD` | `200` | Long-term trend EMA |
| `PRE_NEWS_SHIELD_MINUTES` | `30` | Minutes before news to activate SHIELD mode |
| `POST_NEWS_HUNTER_MINUTES` | `30` | Minutes after news before resuming HUNTER mode |

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/moeketsi200/trading.git
cd trading
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate       # Linux / macOS
venv\Scripts\activate          # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` to set your credentials (see [Environment Variables](#-environment-variables) below).

---

## 🧰 Usage

### Run the Market Scanner
Scans all watchlist pairs and prints actionable trade recommendations.

```bash
python main.py --scan
```

### Run in Fast / Hyper-Sensitive Mode
Uses tighter EMA 5/15 crossovers to force signal detection (for testing purposes).

```bash
python main.py --fast-scan
```

### Preview a Sample Signal Card
Renders a formatted demo recommendation card without live data.

```bash
python main.py --demo-signal
```

### Execute a Demo Trade on MT5
Places a test market order on your configured MT5 Demo Account.

```bash
python main.py --demo-order
```

### Run the Backtest Engine
Backtests the strategy on 60 days of EUR/USD historical 1H data.

```bash
python main.py --backtest
# or simply:
python main.py
```

---

## 📊 Watchlist

The scanner covers **3 tiers** of instruments:

| Tier | Instruments | Recommendation |
|---|---|---|
| **Tier 1 — Majors & Gold** | EUR/USD, GBP/USD, USD/JPY, AUD/USD, USD/CAD, USD/CHF, XAU/USD | ✅ Recommended (Lowest Spreads) |
| **Tier 2 — Forex Minors** | EUR/GBP, GBP/JPY, EUR/JPY | ⚠️ Moderate |
| **Tier 3 — US Indices** | NASDAQ (NAS100), US30 (DOW JONES) | 🔴 High Volatility |

---

## 🛡️ News Execution Modes

The `NewsExecutionHandler` checks the economic calendar and automatically adjusts the scanner's execution posture:

| Mode | Trigger | Behaviour |
|---|---|---|
| **NORMAL** | No major news nearby | Standard trend-following signals |
| **HUNTER** | 30 min after high-impact news | Aggressively scans for breakout/continuation setups |
| **SHIELD** | 30 min before high-impact news | Suspends all new trade recommendations to protect capital |

---

## 🔔 Environment Variables

Copy `.env.example` to `.env` and configure:

```dotenv
# Email Notification Credentials (Optional)
ENABLE_EMAIL_ALERTS=false
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password_here    # Use a Gmail App Password, not your main password
RECIPIENT_EMAIL=your_personal_email@gmail.com
```

> **Note:** To use Gmail, enable 2FA on your Google account and generate an **App Password** at [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords).

---

## 🐳 Running with Docker

### Build and run (single container)

```bash
docker build -t trading-bot .
docker run --env-file .env trading-bot
```

### Run with Docker Compose

```bash
docker compose up --build
```

### Run the scanner via Docker

```bash
docker run --env-file .env trading-bot python main.py --scan
```

---

## ⏰ Scheduled Scanning (Cron)

Use the provided helper script to run the scanner on a schedule:

```bash
chmod +x run_scanner_cron.sh
```

Add to crontab (`crontab -e`) to scan every hour during market hours:

```
0 * * * 1-5 /path/to/trading/run_scanner_cron.sh >> /path/to/trading/scanner.log 2>&1
```

---

## 📦 Dependencies

| Package | Purpose |
|---|---|
| `pandas >= 2.0.0` | Data manipulation and OHLCV DataFrames |
| `numpy >= 1.24.0` | Numerical computation for indicators |
| `yfinance >= 0.2.0` | Historical market data fetching |
| `requests >= 2.31.0` | HTTP client for news API calls |
| `python-dotenv >= 1.0.0` | Loading `.env` configuration |

---

## ⚠️ Disclaimer

This project is for **educational and research purposes only**. Trading Forex and financial derivatives carries significant risk of loss. Past backtest performance does not guarantee future results. Always test on a **demo account** before deploying real capital. The author assumes no liability for trading decisions made using this software.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.