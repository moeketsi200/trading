#!/bin/bash
# Trading Bot Runner — supports foreground scan and background daemon mode.
#
# Usage:
#   ./run_scanner_cron.sh          → one-shot scan (original behaviour)
#   ./run_scanner_cron.sh bg       → background loop (emails every 30 min)
#   ./run_scanner_cron.sh stop     → stop the background bot
#   ./run_scanner_cron.sh status   → check if bot is running

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"
source venv/bin/activate

case "${1}" in
  bg)
    echo "[+] Starting background bot (every 30 min, with email alerts)..."
    nohup python3 run_background.py >> scanner.log 2>&1 &
    echo "[✓] Bot started in background. PID: $!"
    echo "[✓] Logs: $DIR/scanner.log"
    echo "[✓] To stop: ./run_scanner_cron.sh stop"
    ;;
  stop)
    if [ -f "bot.pid" ]; then
      PID=$(cat bot.pid)
      echo "[+] Stopping bot (PID $PID)..."
      kill "$PID" && echo "[✓] Bot stopped." || echo "[!] Could not kill PID $PID."
    else
      echo "[!] No bot.pid found. Is the bot running?"
    fi
    ;;
  status)
    if [ -f "bot.pid" ]; then
      PID=$(cat bot.pid)
      if ps -p "$PID" > /dev/null 2>&1; then
        echo "[✓] Bot is RUNNING (PID $PID)"
      else
        echo "[!] bot.pid exists but process $PID is NOT running."
      fi
    else
      echo "[✗] Bot is NOT running (no bot.pid file)."
    fi
    ;;
  *)
    # Default: one-shot scan (original behaviour)
    python3 main.py --scan
    ;;
esac
