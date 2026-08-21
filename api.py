from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os

from config.config import config
from scanner import MarketScanner
from execution.backtester import PropFirmBacktester
from data.market_data import MarketDataEngine
import sqlite3

def init_db():
    conn = sqlite3.connect('signals.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS signals
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                  pair TEXT,
                  action TEXT,
                  entry REAL,
                  stop_loss REAL,
                  take_profit REAL,
                  reason TEXT)''')
    conn.commit()
    conn.close()

init_db()

app = Flask(__name__, static_folder='dashboard')
CORS(app)

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return "Not found", 404

@app.route('/api/portfolio', methods=['GET'])
def get_portfolio():
    return jsonify({
        "balance": config.INITIAL_BALANCE,
        "risk_per_trade_pct": config.RISK_PER_TRADE_PCT,
        "min_risk_reward_ratio": config.MIN_RISK_REWARD_RATIO
    })

@app.route('/api/scan', methods=['GET'])
def run_scan():
    fast_mode = request.args.get('fast', 'false').lower() == 'true'
    try:
        scanner = MarketScanner(balance=config.INITIAL_BALANCE)
        recommendations = scanner.scan_market(fast_mode=fast_mode)
        
        # Log to DB
        conn = sqlite3.connect('signals.db')
        c = conn.cursor()
        for rec in recommendations:
            c.execute("INSERT INTO signals (pair, action, entry, stop_loss, take_profit, reason) VALUES (?, ?, ?, ?, ?, ?)",
                      (rec['pair'], rec['action'], rec['entry'], rec['stop_loss'], rec['take_profit'], rec['reason']))
        conn.commit()
        conn.close()
        
        return jsonify({"status": "success", "data": recommendations})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/backtest', methods=['GET'])
def run_backtest():
    try:
        backtester = PropFirmBacktester(initial_balance=config.INITIAL_BALANCE)
        results_df = backtester.run_backtest(period="60d", interval=config.TIMEFRAME)
        
        # Format the dataframe for JSON
        trades = []
        for index, row in results_df.iterrows():
            trades.append({
                "time": row['time'].strftime('%Y-%m-%d %H:%M') if hasattr(row['time'], 'strftime') else str(row['time']),
                "result": row['result'],
                "pnl": float(row['pnl']),
                "equity": float(row['equity'])
            })
            
        final_equity = backtester.risk_manager.current_equity
        total_pnl = final_equity - config.INITIAL_BALANCE
        return_pct = (total_pnl / config.INITIAL_BALANCE) * 100
        
        summary = {
            "initial_balance": config.INITIAL_BALANCE,
            "final_equity": final_equity,
            "total_pnl": total_pnl,
            "return_pct": return_pct,
            "total_trades": len(trades),
            "wins": len([t for t in trades if t['result'] == 'WIN']),
            "losses": len([t for t in trades if t['result'] == 'LOSS'])
        }
        
        return jsonify({"status": "success", "summary": summary, "trades": trades})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/candles', methods=['GET'])
def get_candles():
    ticker = request.args.get('ticker')
    if not ticker:
        return jsonify({"status": "error", "message": "Ticker required"}), 400
    try:
        engine = MarketDataEngine(symbol=ticker)
        df = engine.fetch_historical_candles(period="60d", interval=config.TIMEFRAME)
        
        candles = []
        for index, row in df.iterrows():
            candles.append({
                "time": int(index.timestamp()),
                "open": float(row['Open']),
                "high": float(row['High']),
                "low": float(row['Low']),
                "close": float(row['Close'])
            })
        return jsonify({"status": "success", "data": candles})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
