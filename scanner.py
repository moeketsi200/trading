"""
Multi-Pair Market Scanner & Quantitative Signal Recommendation Engine.
Scans expanded MT5 quotes (Majors, Minors, Gold, Indices), evaluates John Murphy TA + News Shield,
and outputs trade recommendations with 1% risk lot sizing and ATR Holding Duration Guidance.
"""
from typing import List, Dict
import pandas as pd
from config.config import config
from risk.risk_manager import RiskManager
from data.market_data import MarketDataEngine
from data.news_data import NewsDataEngine
from strategy.john_murphy_strategy import JohnMurphyStrategy
from strategy.fundamental_bias import FundamentalBiasFilter
from strategy.news_handler import NewsExecutionHandler, ExecutionMode
import json
import os
from utils.notifier import EmailNotifier, TelegramNotifier
from utils.market_symbols import mt5_symbol_from_market, pip_size_for_symbol
from execution.mt5_bridge import MT5ExecutionBridge

def load_watchlist():
    filepath = os.path.join(os.path.dirname(__file__), 'config', 'watchlist.json')
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("[!] Warning: config/watchlist.json not found. Using empty watchlist.")
        return []

DEFAULT_WATCHLIST_EXPANDED = load_watchlist()

class MarketScanner:
    def __init__(self, watchlist: List[Dict] = DEFAULT_WATCHLIST_EXPANDED, balance: float = config.INITIAL_BALANCE):
        self.watchlist = watchlist
        self.balance = balance
        self.risk_manager = RiskManager(initial_balance=balance)
        self.strategy = JohnMurphyStrategy()
        self.bias_filter = FundamentalBiasFilter(enabled=config.ENABLE_FUNDAMENTAL_BIAS_FILTER)
        self.news_engine = NewsDataEngine()
        self.news_handler = NewsExecutionHandler(self.news_engine)
        self.notifier = EmailNotifier()
        self.telegram = TelegramNotifier()
        self.mt5_bridge = MT5ExecutionBridge()
        self._symbols_seen_this_scan = set()

    def calculate_trade_duration(self, df: pd.DataFrame, entry: float, take_profit: float) -> Dict[str, str]:
        """
        Calculates trade holding time and duration estimates based on Average True Range (ATR).
        """
        latest = df.iloc[-1]
        atr = latest.get('ATR_14', 0.0015)
        
        if atr <= 0:
            atr = 0.0015
            
        tp_distance = abs(take_profit - entry)
        # Average candles needed to cover TP distance (assuming ~60% average directional progress per bar)
        estimated_hours = int(max(2, min(48, round(tp_distance / (atr * 0.6)))))
        
        style = "Day Trade (1H Timeframe)" if estimated_hours <= 12 else "Swing Trade (1H/4H Timeframe)"
        
        return {
            "style": style,
            "estimated_duration": f"{estimated_hours - 1} to {estimated_hours + 4} Hours",
            "max_expiry": f"Cancel / Close after {max(24, estimated_hours * 2)} Hours if stagnant"
        }

    def scan_market(self, fast_mode: bool = False) -> List[Dict]:
        """
        Scans all pairs on the watchlist and returns actionable trade recommendations.
        """
        recommendations = []
        execution_mode = self.news_handler.update_execution_mode()
        
        mode_label = "HYPER-SENSITIVE TEST MODE (EMA 5/15)" if fast_mode else execution_mode.value
        
        print("\n" + "=" * 70)
        print(" QUANTITATIVE MARKET SCANNER & DURATION GUIDANCE ENGINE")
        print(f" Mode: {mode_label} | Account Equity: ${self.balance:,.2f}")
        print(f" Max Risk: {config.RISK_PER_TRADE_PCT*100}% (${self.balance*config.RISK_PER_TRADE_PCT:.2f}) | Min R:R: 1:{config.MIN_RISK_REWARD_RATIO}")
        print("=" * 70)
        
        if execution_mode == ExecutionMode.SHIELD and not fast_mode:
            print("\n[!] WARNING: SHIELD MODE IS ACTIVE (High-Impact News Approaching).")
            print("[!] New trade recommendations are temporarily suspended to protect capital.\n")
            return recommendations

        print("\n[+] Scanning MT5 watchlist categories for high-probability setups...\n")
        self._symbols_seen_this_scan = set()
        
        for pair in self.watchlist:
            name = pair["name"]
            ticker = pair["ticker"]
            tier = pair["tier"]
            rec_status = pair["rec"]
            mt5_symbol = mt5_symbol_from_market(name, ticker)

            if mt5_symbol in self._symbols_seen_this_scan:
                continue
            self._symbols_seen_this_scan.add(mt5_symbol)
            
            try:
                data_engine = MarketDataEngine(symbol=ticker)
                df = data_engine.fetch_historical_candles(period="60d", interval=config.TIMEFRAME)
                df = data_engine.calculate_technical_indicators(df, fast_mode=fast_mode)
                
                raw_signal = self.strategy.evaluate_signals(df)
                biased_signal, bias_info, bias_block_reason = self.bias_filter.filter_signal(raw_signal, name, ticker)
                valid_signal = self.news_handler.process_trade_signal(biased_signal)
                
                if valid_signal:
                    latest = df.iloc[-1]
                    atr = latest.get('ATR_14', 0.0015)
                    entry = valid_signal['entry']
                    sl = valid_signal['stop_loss']
                    pip_size = pip_size_for_symbol(mt5_symbol, entry)
                    pos_plan = self.risk_manager.calculate_position_size(
                        entry,
                        sl,
                        atr=atr,
                        symbol=mt5_symbol,
                        pip_size=pip_size,
                    )
                    
                    if pos_plan:
                        pips_sl = pos_plan.get('pips_at_risk') or abs(entry - pos_plan['stop_loss']) / pip_size
                        duration_info = self.calculate_trade_duration(df, entry, pos_plan['take_profit'])
                        
                        rec = {
                            "pair": name,
                            "ticker": ticker,
                            "mt5_symbol": mt5_symbol,
                            "tier": tier,
                            "rec_status": rec_status,
                            "action": valid_signal['action'],
                            "entry": pos_plan['entry_price'],
                            "stop_loss": pos_plan['stop_loss'],
                            "take_profit": pos_plan['take_profit'],
                            "sl_pips": pips_sl,
                            "lot_size": pos_plan['lot_size'],
                            "dollar_risk": pos_plan['dollar_risk'],
                            "reward_risk_ratio": pos_plan.get('reward_risk_ratio', config.MIN_RISK_REWARD_RATIO),
                            "reason": valid_signal['reason'],
                            "fundamental_bias": bias_info["label"],
                            "duration": duration_info,
                            "break_even_trigger": pos_plan.get('break_even_trigger')
                        }
                        recommendations.append(rec)
                        self.print_signal_card(rec)
                        self.notifier.send_trade_signal_email(rec)
                        self.telegram.send_trade_signal(rec)
                        self.mt5_bridge.place_automated_order(rec)
                    else:
                        print(f"  [-] {name:<16} ({tier}) : Setup detected but rejected by Risk Engine.")
                else:
                    latest = df.iloc[-1]
                    trend = "UPTREND" if latest['Uptrend'] else ("DOWNTREND" if latest['Downtrend'] else "SIDEWAYS")
                    close_p = latest['Close']
                    ema_50 = latest['EMA_50']
                    
                    pip_scale = pip_size_for_symbol(mt5_symbol, close_p)
                    pips_to_ema = abs(close_p - ema_50) / pip_scale
                    
                    proximity_str = f"{pips_to_ema:.1f} pips above EMA50 Support" if latest['Uptrend'] else f"{pips_to_ema:.1f} pips below EMA50 Resistance"
                    if bias_block_reason:
                        print(f"  [-] {name:<16} ({tier:<22}) : Signal blocked ({bias_block_reason})")
                    else:
                        print(f"  [•] {name:<16} ({tier:<22}) : No Signal (Trend: {trend:<9} | Price: {close_p:.5f} | Proximity: {proximity_str} | Bias: {bias_info['label']})")
                    
            except Exception as e:
                print(f"  [!] {name:<16} ({tier}) : Data fetch note ({e})")
                
        print("\n" + "=" * 70)
        print(f" SCAN COMPLETE: Found {len(recommendations)} actionable setup(s).")
        print("=" * 70 + "\n")
        
        return recommendations

    def generate_demo_signal_card(self):
        """Generates a sample signal recommendation card for visual testing."""
        demo_rec = {
            "pair": "GOLD (XAU/USD)",
            "ticker": "GC=F (or XAUUSD on MT5)",
            "mt5_symbol": "XAUUSD",
            "tier": "Tier 1: Metal / Commodity",
            "rec_status": "RECOMMENDED (Post-News)",
            "action": "BUY",
            "entry": 4420.50,
            "stop_loss": 4410.00,
            "take_profit": 4451.50,
            "sl_pips": 105.0,
            "lot_size": 0.05,
            "dollar_risk": 50.00,
            "reward_risk_ratio": 10.0,
            "reason": "Uptrend EMA 50 Support Bounce",
            "fundamental_bias": "N/A",
            "break_even_trigger": 4441.50,
            "duration": {
                "style": "Day Trade (1H Timeframe)",
                "estimated_duration": "3 to 7 Hours",
                "max_expiry": "Cancel / Close after 24 Hours if stagnant"
            }
        }
        print("\n[+] DEMO SIGNAL CARD PREVIEW (Triggered when live setup occurs):\n")
        self.print_signal_card(demo_rec)
        self.notifier.send_trade_signal_email(demo_rec)
        self.telegram.send_trade_signal(demo_rec)
        print()

    def execute_demo_trade(self):
        """Triggers a test trade placement on the configured MT5 Demo Account."""
        demo_rec = {
            "pair": "EUR/USD",
            "ticker": "EURUSD",
            "mt5_symbol": "EURUSD",
            "tier": "Tier 1: Forex Major",
            "rec_status": "DEMO TEST ORDER",
            "action": "BUY",
            "entry": 1.15360,
            "stop_loss": 1.14860,
            "take_profit": 1.16860,
            "sl_pips": 50.0,
            "lot_size": 0.01,
            "dollar_risk": 5.00,
            "reward_risk_ratio": 3.0,
            "reason": "Demo Order Execution Test",
            "fundamental_bias": "EUR:neutral / USD:neutral => neutral",
            "break_even_trigger": 1.16360,
            "duration": {
                "style": "Day Trade (1H Timeframe)",
                "estimated_duration": "4 to 8 Hours",
                "max_expiry": "Cancel / Close after 24 Hours"
            }
        }
        print("\n" + "=" * 70)
        print(" MT5 DEMO ORDER EXECUTION TEST")
        print(f" Account: {self.mt5_bridge.login} | Server: {self.mt5_bridge.server}")
        print("=" * 70)
        self.print_signal_card(demo_rec)
        self.notifier.send_trade_signal_email(demo_rec)
        self.telegram.send_trade_signal(demo_rec)
        self.mt5_bridge.place_automated_order(demo_rec)
        print("=" * 70 + "\n")

    def print_signal_card(self, rec: Dict):
        """Prints a clean, formatted recommendation card for a detected setup."""
        dur = rec["duration"]
        print("┌" + "─" * 68 + "┐")
        print(f"│ 🔥 [TRADE RECOMMENDATION: {rec['pair']}] ({rec['tier']})".ljust(69) + "│")
        print("├" + "─" * 68 + "┤")
        print(f"│  MT5 Execution Symbol : {rec.get('mt5_symbol', rec['ticker'])}".ljust(69) + "│")
        print(f"│  Action               : {rec['action']} LIMIT / MARKET".ljust(69) + "│")
        print(f"│  Entry Price          : {rec['entry']:.5f}".ljust(69) + "│")
        print(f"│  Stop Loss            : {rec['stop_loss']:.5f} ({rec['sl_pips']:.1f} pips)".ljust(69) + "│")
        
        if rec.get("break_even_trigger"):
            print(f"│  Take Profit          : {rec['take_profit']:.5f} (1:{rec.get('reward_risk_ratio', 10):g} R:R Runner)".ljust(69) + "│")
            print(f"│  Trade Management     : Move SL to Break-Even at {rec['break_even_trigger']:.5f}".ljust(69) + "│")
            print(f"│  Trailing Stop        : Trail SL behind 1H EMA 50 after Break-Even".ljust(69) + "│")
        else:
            print(f"│  Take Profit          : {rec['take_profit']:.5f} (1:{rec.get('reward_risk_ratio', 3):g} R:R Target)".ljust(69) + "│")
            
        print(f"│  Max Risk (1%)        : ${rec['dollar_risk']:.2f}".ljust(69) + "│")
        print(f"│  Recommended Lots     : {rec['lot_size']} Lots (Micro/Standard)".ljust(69) + "│")
        print(f"│  Signal Rationale     : {rec['reason']}".ljust(69) + "│")
        print(f"│  Fundamental Bias     : {rec.get('fundamental_bias', 'N/A')}".ljust(69) + "│")
        print("├" + "─" * 68 + "┤")
        print("│ ⏱️ DURATION & HOLDING TIME GUIDANCE:".ljust(69) + "│")
        print(f"│  • Trade Style        : {dur['style']}".ljust(69) + "│")
        print(f"│  • Estimated Duration : {dur['estimated_duration']}".ljust(69) + "│")
        print(f"│  • Max Expiry Limit   : {dur['max_expiry']}".ljust(69) + "│")
        print("└" + "─" * 68 + "┘")

if __name__ == "__main__":
    scanner = MarketScanner()
    scanner.scan_market()
