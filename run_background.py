"""
Background Trading Bot Runner.
Runs the market scanner in an infinite loop every 30 minutes.
  - Sends an instant email the moment a trade signal is detected.
  - Sends a 30-min heartbeat status report at the end of every cycle.
  - Logs everything to scanner.log.

Usage:
    python3 run_background.py          # runs in foreground (Ctrl+C to stop)
    ./run_scanner_cron.sh              # launches in background, saves PID
"""
import os
import sys
import time
import signal
import logging
from datetime import datetime, timedelta

from config.config import config
from scanner import MarketScanner, DEFAULT_WATCHLIST_EXPANDED
from data.market_data import MarketDataEngine
from utils.notifier import EmailNotifier

# ─── Logging Setup ────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("scanner.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("background_runner")

# ─── Config ───────────────────────────────────────────────────────────────────
SCAN_INTERVAL_MINUTES = 30
SCAN_INTERVAL_SECONDS = SCAN_INTERVAL_MINUTES * 60

# ─── Graceful Shutdown ────────────────────────────────────────────────────────
_running = True

def _handle_shutdown(signum, frame):
    global _running
    log.info("Shutdown signal received. Stopping after current cycle...")
    _running = False

signal.signal(signal.SIGTERM, _handle_shutdown)
signal.signal(signal.SIGINT, _handle_shutdown)


def collect_market_snapshot(scanner: MarketScanner) -> list:
    """
    Builds a lightweight market snapshot (trend + price per pair) for the
    heartbeat email — without running a full signal evaluation scan.
    """
    snapshot = []
    for pair in scanner.watchlist:
        name = pair["name"]
        ticker = pair["ticker"]
        try:
            data_engine = MarketDataEngine(symbol=ticker)
            df = data_engine.fetch_historical_candles(period="5d", interval=config.TIMEFRAME)
            df = data_engine.calculate_technical_indicators(df)
            latest = df.iloc[-1]

            trend = "UPTREND" if latest.get("Uptrend") else ("DOWNTREND" if latest.get("Downtrend") else "SIDEWAYS")
            close_p = latest["Close"]
            ema_50 = latest.get("EMA_50", close_p)
            pip_scale = 0.1 if ("=" not in ticker or "GC=F" in ticker) else 0.0001
            pips_to_ema = abs(close_p - ema_50) / pip_scale
            direction = "above Support" if latest.get("Uptrend") else "below Resistance"

            snapshot.append({
                "pair": name,
                "trend": trend,
                "price": f"{close_p:.5f}",
                "proximity": f"{pips_to_ema:.1f} pips {direction}",
            })
        except Exception as e:
            snapshot.append({"pair": name, "trend": "N/A", "price": "—", "proximity": str(e)[:40]})

    return snapshot


def run_loop():
    """Main background loop — scans every 30 minutes forever."""
    log.info("=" * 65)
    log.info(" BACKGROUND TRADING BOT STARTING")
    log.info(f" Scan interval : every {SCAN_INTERVAL_MINUTES} minutes")
    log.info(f" Account       : ${config.INITIAL_BALANCE:,.2f}")
    log.info(f" Risk per trade: {config.RISK_PER_TRADE_PCT * 100}%")
    log.info("=" * 65)

    scanner = MarketScanner(balance=config.INITIAL_BALANCE)
    notifier = EmailNotifier()
    cycle = 0

    # Send startup notification
    notifier.send_startup_email()

    while _running:
        cycle += 1
        cycle_start = datetime.now()
        next_scan_at = (cycle_start + timedelta(seconds=SCAN_INTERVAL_SECONDS)).strftime("%H:%M:%S")

        log.info(f"\n{'='*65}")
        log.info(f" CYCLE #{cycle} | Started: {cycle_start.strftime('%Y-%m-%d %H:%M:%S')}")
        log.info(f"{'='*65}")

        # ── Run the scanner ──────────────────────────────────────────────────
        try:
            # scan_market already sends individual signal emails via notifier
            recommendations = scanner.scan_market()
            signals_found = len(recommendations)
        except Exception as e:
            log.error(f"Scanner error on cycle #{cycle}: {e}")
            signals_found = 0
            recommendations = []

        # ── Build market snapshot for heartbeat ──────────────────────────────
        try:
            snapshot = collect_market_snapshot(scanner)
        except Exception as e:
            log.warning(f"Market snapshot failed: {e}")
            snapshot = []

        # ── Send 30-min heartbeat email ──────────────────────────────────────
        execution_mode = scanner.news_handler.update_execution_mode()
        summary = {
            "cycle_number": cycle,
            "pairs_scanned": len(scanner.watchlist),
            "signals_found": signals_found,
            "next_scan_at": next_scan_at,
            "mode": execution_mode.value,
            "market_snapshot": snapshot,
        }
        notifier.send_heartbeat_email(summary)

        # ── Wait for next cycle ──────────────────────────────────────────────
        if not _running:
            break

        log.info(f"\n[⏳] Sleeping {SCAN_INTERVAL_MINUTES} minutes until next scan at {next_scan_at}...")
        elapsed = (datetime.now() - cycle_start).total_seconds()
        sleep_time = max(0, SCAN_INTERVAL_SECONDS - elapsed)

        # Sleep in 5-second chunks so Ctrl+C / SIGTERM responds quickly
        slept = 0
        while slept < sleep_time and _running:
            time.sleep(min(5, sleep_time - slept))
            slept += 5

    log.info("\n[✓] Background bot stopped cleanly.")


if __name__ == "__main__":
    # Write PID file so shell script can kill the process
    pid_file = os.path.join(os.path.dirname(__file__), "bot.pid")
    with open(pid_file, "w") as f:
        f.write(str(os.getpid()))
    log.info(f"[PID] Bot running as process {os.getpid()} (saved to bot.pid)")

    try:
        run_loop()
    finally:
        if os.path.exists(pid_file):
            os.remove(pid_file)
