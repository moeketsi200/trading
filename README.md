# 🤖 Automated Forex Trading & Market Scanner System

**Strategy**: John Murphy Technical Analysis + 3-Mode News Handler  
**Target**: R4,000 ZAR/month (~$220 USD) on a $5,000 account  
**Risk per trade**: 1% | Minimum R:R = 1:3  
**Universe**: 555 symbols — Forex, Metals, Energy, Indices, Crypto, S&P 500 Stocks

---

## 📋 Table of Contents

1. [First-Time Setup](#1-first-time-setup)
2. [Email Alerts Configuration](#2-email-alerts-configuration)
3. [Running the Bot](#3-running-the-bot)
4. [Background Mode (Recommended)](#4-background-mode-recommended)
5. [Scan Universe Configuration](#5-scan-universe-configuration)
6. [Understanding the Output](#6-understanding-the-output)
7. [How the Strategy Works](#7-how-the-strategy-works)
8. [Project Structure](#8-project-structure)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. First-Time Setup

### Requirements
- **Python 3.9+**
- **macOS / Linux** (Windows supported via WSL or Docker)
- Internet connection (for market data via Yahoo Finance)

### Installation Steps

```bash
# 1. Navigate to the project folder
cd /Users/katlego/work/trading

# 2. Create a Python virtual environment
python3 -m venv venv

# 3. Activate it
source venv/bin/activate

# 4. Install all dependencies
pip install -r requirements.txt

# 5. Make the shell script executable (first time only)
chmod +x run_scanner_cron.sh
```

---

## 2. Email Alerts Configuration

The bot sends you emails when:
- 🚀 **Bot starts** — one-time startup notification
- 🔥 **Signal detected** — instant email with full trade details
- ✅ **Every 30 minutes** — heartbeat status report (market conditions, signals found)

### Setup

Copy the example file and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```env
ENABLE_EMAIL_ALERTS=true
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=tradingrooibot@gmail.com
SENDER_PASSWORD=vsjp ascl asnf ngon     # Gmail App Password (not your login password)
RECIPIENT_EMAIL=tradingrooibot@gmail.com
```

> **What is a Gmail App Password?**  
> It's a special 16-character password Gmail generates for apps.  
> Get one at: **Google Account → Security → 2-Step Verification → App Passwords**  
> You already have it set up: `vsjp ascl asnf ngon`

### Test Your Email

```bash
source venv/bin/activate
python3 -c "
from utils.notifier import EmailNotifier
n = EmailNotifier()
n.send_startup_email()
print('Check your inbox!')
"
```

---

## 3. Running the Bot

### Option A — One-Shot Scan (Manual, runs once and exits)

```bash
source venv/bin/activate
python3 main.py --scan
```

Best for: testing, checking current market conditions quickly.

---

### Option B — Fast Test Mode (forces signals for testing)

```bash
source venv/bin/activate
python3 main.py --fast-scan
```

Uses EMA 5/15 instead of 50/200 to generate signals even in flat markets.  
Best for: testing email alerts and signal card formatting.

---

### Option C — Demo Signal Preview

```bash
source venv/bin/activate
python3 main.py --demo-signal
```

Prints a sample trade signal card and sends a demo email.  
Best for: testing email formatting without needing a real signal.

---

### Option D — Demo MT5 Order

```bash
source venv/bin/activate
python3 main.py --demo-order
```

Simulates placing an order on the MT5 Demo account.  
Best for: testing the MT5 execution bridge.

---

### Option E — Backtest Engine

```bash
source venv/bin/activate
python3 main.py --backtest
```

Runs a 60-day historical simulation on EUR/USD.  
Best for: validating the strategy's historical performance.

---

## 4. Background Mode (Recommended)

This is the main way to run the bot 24/7. It scans every 30 minutes automatically and emails you.

### Start the Background Bot

```bash
./run_scanner_cron.sh bg
```

Output:
```
[+] Starting background bot (every 30 min, with email alerts)...
[✓] Bot started in background. PID: 14601
[✓] Logs: /Users/katlego/work/trading/scanner.log
[✓] To stop: ./run_scanner_cron.sh stop
```

The bot will immediately:
1. Send a **🚀 "Bot Online" email** to your inbox
2. Run the first full scan across all 555 symbols
3. Email you results and go to sleep for 30 minutes
4. Repeat forever until you stop it

---

### Check if the Bot is Running

```bash
./run_scanner_cron.sh status
```

Output:
```
[✓] Bot is RUNNING (PID 14601)
```

---

### View Live Logs

```bash
tail -f scanner.log
```

Press `Ctrl+C` to stop watching logs (bot keeps running).

---

### Stop the Background Bot

```bash
./run_scanner_cron.sh stop
```

---

### Shell Script Quick Reference

| Command | What it does |
|---|---|
| `./run_scanner_cron.sh` | One-shot scan (runs once, exits) |
| `./run_scanner_cron.sh bg` | Start background loop (30-min scans) |
| `./run_scanner_cron.sh stop` | Stop the background bot |
| `./run_scanner_cron.sh status` | Check if bot is running |

---

## 5. Scan Universe Configuration

Control which asset classes the bot scans by editing `.env`:

```env
# ─── Full Universe Scanner Settings ──────────────────────────────────────────
SCAN_FOREX=true          # ~60 Forex pairs (Majors + Minors + Exotics)
SCAN_METALS=true         # Gold, Silver, Platinum, Palladium, Copper
SCAN_COMMODITIES=true    # Oil WTI, Brent, Natural Gas + Agricultural
SCAN_INDICES=true        # 20 Global Indices (US, EU, Asia, Americas)
SCAN_CRYPTO=true         # 20 Crypto pairs (BTC, ETH, SOL, etc.)
SCAN_US_STOCKS=true      # ~480 S&P 500 stocks (adds ~10-15 min per scan)
MAX_STOCKS=500           # Max number of S&P 500 stocks to include
```

After editing `.env`, restart the bot:

```bash
./run_scanner_cron.sh stop
./run_scanner_cron.sh bg
```

### Symbol Universe Breakdown

| Category | Symbols | Scan Time |
|---|---|---|
| Forex Major | 7 | Fast (~10s) |
| Forex Minor | 22 | Fast (~30s) |
| Forex Exotic | 31 | Moderate (~45s) |
| Metals | 5 | Fast (~10s) |
| Energy & Agriculture | 10 | Fast (~15s) |
| Global Indices | 20 | Fast (~30s) |
| Cryptocurrency | 20 | Fast (~30s) |
| US Stocks (S&P 500) | ~440 | **Slow (~12 min)** |
| **TOTAL** | **555** | **~15-20 min/cycle** |

> **💡 Tip**: Set `SCAN_US_STOCKS=false` for faster 2-3 minute scans when you only need Forex/Metals/Indices signals.

---

## 6. Understanding the Output

### Scan Header
```
======================================================================
 QUANTITATIVE MARKET SCANNER & DURATION GUIDANCE ENGINE
 Mode: NORMAL | Account Equity: $5,000.00
 Max Risk: 1.0% ($50.00) | Min R:R: 1:3.0
 Universe: Total: 555 symbols | Forex Major: 7 | Metals: 5 | ...
======================================================================
```

### No-Signal Line (most common)
```
  [•] EUR/USD                : No Signal (Trend: UPTREND   | Price: 1.16645 | 62.9 pips above EMA50 Support)
  [•] BITCOIN (BTC)          : No Signal (Trend: UPTREND   | Price: 107432.00000 | 5432.1 pts above EMA50 Support)
```

### Signal Card (when a setup is found)
```
┌────────────────────────────────────────────────────────────────────┐
│ 🔥 [TRADE RECOMMENDATION: EUR/USD] (Forex Major)                   │
├────────────────────────────────────────────────────────────────────┤
│  MT5 Execution Ticker : EURUSD=X                                   │
│  Action               : BUY LIMIT / MARKET                         │
│  Entry Price          : 1.16200                                     │
│  Stop Loss            : 1.15700 (50.0 pips)                        │
│  Take Profit          : 1.17700 (1:3 R:R Target)                   │
│  Max Risk (1%)        : $50.00                                      │
│  Recommended Lots     : 0.10 Lots (Micro/Standard)                 │
│  Signal Rationale     : Uptrend EMA 50 Support Bounce              │
├────────────────────────────────────────────────────────────────────┤
│ ⏱️ DURATION & HOLDING TIME GUIDANCE:                               │
│  • Trade Style        : Day Trade (1H Timeframe)                   │
│  • Estimated Duration : 4 to 9 Hours                               │
│  • Max Expiry Limit   : Cancel / Close after 24 Hours if stagnant  │
└────────────────────────────────────────────────────────────────────┘
```

### Execution Modes

| Mode | What it means |
|---|---|
| `NORMAL` | Regular scanning — signals allowed |
| `SHIELD` | High-impact news within 30 min — **no new trades** |
| `HUNTER` | Within 30 min after major news — momentum signals only |

---

## 7. How the Strategy Works

### Signal Generation (John Murphy TA)

A signal is generated when **all 3 conditions are met**:

1. **Trend Confirmation**: EMA 50 is above EMA 200 (Uptrend) or below (Downtrend)
2. **Price Pullback**: Price has pulled back to the EMA 50 Support/Resistance level
3. **Bounce Signal**: Price starts moving back in the trend direction

### Risk Management (1% Rule)

- **Risk per trade**: Always exactly 1% of account = **$50 on $5,000**
- **Minimum R:R**: Must be at least 1:3 — risking $50 to make $150
- **Stop Loss**: Placed below EMA 50 support (or above for sells)
- **Take Profit**: Automatically set at 3× the stop loss distance

### 3-Mode News Handler

| Time | Mode | Action |
|---|---|---|
| 30 min before news | SHIELD | Blocks all new signals |
| During news | SHIELD | Blocks all new signals |
| 30 min after news | HUNTER | Allows momentum signals |
| Normal hours | NORMAL | Full scanning active |

---

## 8. Project Structure

```
trading/
│
├── main.py                    # Entry point — CLI argument handler
├── scanner.py                 # Core multi-asset market scanner
├── run_background.py          # 30-min loop background runner
├── run_scanner_cron.sh        # Shell script (start/stop/status)
├── scanner.log                # Live log file (tail -f to watch)
├── bot.pid                    # Process ID file (auto-created when running)
│
├── .env                       # YOUR CREDENTIALS (never commit to git!)
├── .env.example               # Template for .env
├── requirements.txt           # Python dependencies
│
├── config/
│   └── config.py              # Global settings (balance, risk, timeframes)
│
├── data/
│   ├── market_data.py         # Yahoo Finance OHLC data fetcher
│   ├── news_data.py           # Economic calendar / news timing
│   └── watchlist_builder.py   # Full 555-symbol universe builder
│
├── strategy/
│   ├── john_murphy_strategy.py  # EMA + S/R signal evaluation
│   └── news_handler.py          # 3-Mode execution controller
│
├── risk/
│   └── risk_manager.py        # Position sizing, drawdown limits
│
├── execution/
│   ├── mt5_bridge.py          # MT5 automated order execution
│   └── backtester.py          # Historical simulation engine
│
└── utils/
    └── notifier.py            # Email alert engine (signal + heartbeat)
```

---

## 9. Troubleshooting

### ❌ "No module named X"
```bash
source venv/bin/activate      # activate the virtual environment first
pip install -r requirements.txt
```

### ❌ Email not sending
```bash
# Test credentials manually
source venv/bin/activate
python3 -c "from utils.notifier import EmailNotifier; EmailNotifier().send_startup_email()"
```

Common causes:
- `ENABLE_EMAIL_ALERTS` is not set to `true` in `.env`
- App Password has spaces — keep them: `vsjp ascl asnf ngon` ✅
- Gmail "Less secure apps" blocked — use App Password (not your Gmail password)

### ❌ Bot not starting / stops immediately
```bash
tail -50 scanner.log          # check last 50 lines for error messages
```

### ❌ "bot.pid exists but process is NOT running"
The bot crashed. Check logs and restart:
```bash
rm bot.pid
tail -30 scanner.log           # find the error
./run_scanner_cron.sh bg       # restart
```

### ❌ Scan is very slow (>20 min)
Set `SCAN_US_STOCKS=false` in `.env` to skip the 440 S&P 500 stocks.  
Forex + Metals + Indices alone take ~2-3 minutes.

### ❌ "Failed to fetch market data for X"
Some exotic tickers may not be available on Yahoo Finance.  
The bot skips them automatically and continues scanning.

---

## 🔐 Security Notes

- `.env` is in `.gitignore` — it will **never** be pushed to GitHub
- Your Gmail App Password is stored locally only
- Never share or commit your `.env` file
- The bot does **not** store any trade data to the cloud

---

*Built on John Murphy's Technical Analysis principles. For educational purposes. Trade at your own risk.*