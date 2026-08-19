"""
Multi-Asset Market Scanner & Quantitative Signal Recommendation Engine.
Scans the full symbol universe (Forex, Metals, Energy, Indices, Crypto, US Stocks),
evaluates John Murphy TA + News Shield, and outputs trade recommendations with
1% risk lot sizing and ATR Holding Duration Guidance.
"""
import os
from typing import List, Dict
import pandas as pd
from dotenv import load_dotenv
from config.config import config
from risk.risk_manager import RiskManager
from data.market_data import MarketDataEngine
from data.news_data import NewsDataEngine
from data.watchlist_builder import build_full_watchlist, get_watchlist_summary
from strategy.john_murphy_strategy import JohnMurphyStrategy
from strategy.news_handler import NewsExecutionHandler, ExecutionMode
from utils.notifier import EmailNotifier
from execution.mt5_bridge import MT5ExecutionBridge

load_dotenv()

# ─── Legacy 12-symbol fallback (used by --demo-signal and --demo-order) ───────
DEFAULT_WATCHLIST_COMPACT = [
    {"name": "EUR/USD",          "ticker": "EURUSD=X", "tier": "Tier 1: Forex Major",      "rec": "RECOMMENDED",             "pip_scale": 0.0001},
    {"name": "GBP/USD",          "ticker": "GBPUSD=X", "tier": "Tier 1: Forex Major",      "rec": "RECOMMENDED",             "pip_scale": 0.0001},
    {"name": "USD/JPY",          "ticker": "USDJPY=X", "tier": "Tier 1: Forex Major",      "rec": "RECOMMENDED",             "pip_scale": 0.01},
    {"name": "AUD/USD",          "ticker": "AUDUSD=X", "tier": "Tier 1: Forex Major",      "rec": "RECOMMENDED",             "pip_scale": 0.0001},
    {"name": "USD/CAD",          "ticker": "USDCAD=X", "tier": "Tier 1: Forex Major",      "rec": "RECOMMENDED",             "pip_scale": 0.0001},
    {"name": "USD/CHF",          "ticker": "USDCHF=X", "tier": "Tier 1: Forex Major",      "rec": "RECOMMENDED",             "pip_scale": 0.0001},
    {"name": "GOLD (XAU/USD)",   "ticker": "GC=F",     "tier": "Tier 1: Metal / Commodity","rec": "RECOMMENDED (Post-News)", "pip_scale": 0.1},
    {"name": "EUR/GBP",          "ticker": "EURGBP=X", "tier": "Tier 2: Forex Minor",      "rec": "MODERATE",                "pip_scale": 0.0001},
    {"name": "GBP/JPY",          "ticker": "GBPJPY=X", "tier": "Tier 2: Forex Minor",      "rec": "MODERATE",                "pip_scale": 0.01},
    {"name": "EUR/JPY",          "ticker": "EURJPY=X", "tier": "Tier 2: Forex Minor",      "rec": "MODERATE",                "pip_scale": 0.01},
    {"name": "NASDAQ (NAS100)",  "ticker": "^NDX",     "tier": "Tier 3: US Index",         "rec": "HIGH VOLATILITY",         "pip_scale": 1.0},
    {"name": "US30 (DOW JONES)", "ticker": "^DJI",     "tier": "Tier 3: US Index",         "rec": "HIGH VOLATILITY",         "pip_scale": 1.0},
]


class MarketScanner:
    def __init__(self, watchlist: List[Dict] = None, balance: float = config.INITIAL_BALANCE):
        # If no watchlist provided, build the full universe from .env flags
        if watchlist is None:
            watchlist = build_full_watchlist(
                include_forex=os.getenv("SCAN_FOREX", "true").lower() == "true",
                include_metals=os.getenv("SCAN_METALS", "true").lower() == "true",
                include_energy=os.getenv("SCAN_COMMODITIES", "true").lower() == "true",
                include_indices=os.getenv("SCAN_INDICES", "true").lower() == "true",
                include_crypto=os.getenv("SCAN_CRYPTO", "false").lower() == "true",
                include_stocks=os.getenv("SCAN_US_STOCKS", "false").lower() == "true",
                max_stocks=int(os.getenv("MAX_STOCKS", "500")),
            )
        self.watchlist = watchlist
        self.balance = balance
        self.risk_manager = RiskManager(initial_balance=balance)
        self.strategy = JohnMurphyStrategy()
        self.news_engine = NewsDataEngine()
        self.news_handler = NewsExecutionHandler(self.news_engine)
        self.notifier = EmailNotifier()
        self.mt5_bridge = MT5ExecutionBridge()

    def calculate_trade_duration(self, df: pd.DataFrame, entry: float, take_profit: float) -> Dict[str, str]:
        """
        Calculates trade holding time and duration estimates based on Average True Range (ATR).
        """
        latest = df.iloc[-1]
        atr = latest.get('ATR_14', 0.0015)

        if atr <= 0:
            atr = 0.0015

        tp_distance = abs(take_profit - entry)
        # Average candles needed to cover TP distance (~60% average directional progress per bar)
        estimated_hours = int(max(2, min(48, round(tp_distance / (atr * 0.6)))))

        style = "Day Trade (1H Timeframe)" if estimated_hours <= 12 else "Swing Trade (1H/4H Timeframe)"

        return {
            "style": style,
            "estimated_duration": f"{estimated_hours - 1} to {estimated_hours + 4} Hours",
            "max_expiry": f"Cancel / Close after {max(24, estimated_hours * 2)} Hours if stagnant"
        }

    def scan_market(self, fast_mode: bool = False) -> List[Dict]:
        """
        Scans all symbols on the watchlist and returns actionable trade recommendations.
        Prints results grouped by asset class tier.
        """
        recommendations = []
        execution_mode = self.news_handler.update_execution_mode()

        mode_label = "HYPER-SENSITIVE TEST MODE (EMA 5/15)" if fast_mode else execution_mode.value

        print("\n" + "=" * 70)
        print(" QUANTITATIVE MARKET SCANNER & DURATION GUIDANCE ENGINE")
        print(f" Mode: {mode_label} | Account Equity: ${self.balance:,.2f}")
        print(f" Max Risk: {config.RISK_PER_TRADE_PCT*100}% (${self.balance*config.RISK_PER_TRADE_PCT:.2f}) | Min R:R: 1:{config.MIN_RISK_REWARD_RATIO}")
        print(f" Universe: {get_watchlist_summary(self.watchlist)}")
        print("=" * 70)

        if execution_mode == ExecutionMode.SHIELD and not fast_mode:
            print("\n[!] WARNING: SHIELD MODE IS ACTIVE (High-Impact News Approaching).")
            print("[!] New trade recommendations are temporarily suspended to protect capital.\n")
            return recommendations

        print(f"\n[+] Scanning {len(self.watchlist)} symbols across all categories...\n")

        current_tier = None

        for pair in self.watchlist:
            name        = pair["name"]
            ticker      = pair["ticker"]
            tier        = pair["tier"]
            rec_status  = pair["rec"]
            pip_scale   = pair.get("pip_scale", 0.0001)

            # ── Print category header when tier changes ──────────────────────
            if tier != current_tier:
                current_tier = tier
                print(f"\n  ── {tier} {'─' * max(0, 54 - len(tier))}")

            # ── Unit label for proximity display ────────────────────────────
            unit = "pips" if "Forex" in tier else "pts"

            try:
                data_engine = MarketDataEngine(symbol=ticker)
                df = data_engine.fetch_historical_candles(period="60d", interval=config.TIMEFRAME)
                df = data_engine.calculate_technical_indicators(df, fast_mode=fast_mode)

                raw_signal   = self.strategy.evaluate_signals(df)
                valid_signal = self.news_handler.process_trade_signal(raw_signal)

                if valid_signal:
                    entry  = valid_signal['entry']
                    sl     = valid_signal['stop_loss']
                    pos_plan = self.risk_manager.calculate_position_size(entry, sl)

                    if pos_plan:
                        pips_sl = abs(entry - sl) / pip_scale
                        duration_info = self.calculate_trade_duration(df, entry, pos_plan['take_profit'])

                        rec = {
                            "pair":         name,
                            "ticker":       ticker,
                            "tier":         tier,
                            "rec_status":   rec_status,
                            "action":       valid_signal['action'],
                            "entry":        pos_plan['entry_price'],
                            "stop_loss":    pos_plan['stop_loss'],
                            "take_profit":  pos_plan['take_profit'],
                            "sl_pips":      pips_sl,
                            "lot_size":     pos_plan['lot_size'],
                            "dollar_risk":  pos_plan['dollar_risk'],
                            "reason":       valid_signal['reason'],
                            "duration":     duration_info,
                            "pip_scale":    pip_scale,
                            "unit":         unit,
                        }
                        recommendations.append(rec)
                        self.print_signal_card(rec)
                        self.notifier.send_trade_signal_email(rec)
                        self.mt5_bridge.place_automated_order(rec)
                    else:
                        print(f"  [-] {name:<20} ({tier}) : Setup detected but rejected by Risk Engine.")
                else:
                    latest  = df.iloc[-1]
                    trend   = "UPTREND" if latest['Uptrend'] else ("DOWNTREND" if latest['Downtrend'] else "SIDEWAYS")
                    close_p = latest['Close']
                    ema_50  = latest['EMA_50']

                    pips_to_ema  = abs(close_p - ema_50) / pip_scale
                    direction    = "above EMA50 Support" if latest['Uptrend'] else "below EMA50 Resistance"
                    print(f"  [•] {name:<22} : No Signal (Trend: {trend:<9} | Price: {close_p:.5f} | {pips_to_ema:.1f} {unit} {direction})")

            except Exception as e:
                print(f"  [!] {name:<22} : Data error — {e}")

        print("\n" + "=" * 70)
        print(f" SCAN COMPLETE: {len(self.watchlist)} symbols scanned | {len(recommendations)} actionable setup(s) found.")
        print("=" * 70 + "\n")

        return recommendations

    def generate_demo_signal_card(self):
        """Generates a sample signal recommendation card for visual testing."""
        demo_rec = {
            "pair":         "GOLD (XAU/USD)",
            "ticker":       "GC=F (or XAUUSD on MT5)",
            "tier":         "Metal",
            "rec_status":   "RECOMMENDED (Post-News)",
            "action":       "BUY",
            "entry":        4420.50,
            "stop_loss":    4410.00,
            "take_profit":  4451.50,
            "sl_pips":      105.0,
            "lot_size":     0.05,
            "dollar_risk":  50.00,
            "reason":       "Uptrend EMA 50 Support Bounce",
            "unit":         "pts",
            "duration": {
                "style":               "Day Trade (1H Timeframe)",
                "estimated_duration":  "3 to 7 Hours",
                "max_expiry":          "Cancel / Close after 24 Hours if stagnant"
            }
        }
        print("\n[+] DEMO SIGNAL CARD PREVIEW (Triggered when live setup occurs):\n")
        self.print_signal_card(demo_rec)
        self.notifier.send_trade_signal_email(demo_rec)
        print()

    def execute_demo_trade(self):
        """Triggers a test trade placement on the configured MT5 Demo Account."""
        demo_rec = {
            "pair":        "EUR/USD",
            "ticker":      "EURUSD",
            "tier":        "Forex Major",
            "rec_status":  "DEMO TEST ORDER",
            "action":      "BUY",
            "entry":       1.15360,
            "stop_loss":   1.14860,
            "take_profit": 1.16860,
            "sl_pips":     50.0,
            "lot_size":    0.01,
            "dollar_risk": 5.00,
            "reason":      "Demo Order Execution Test",
            "unit":        "pips",
            "duration": {
                "style":              "Day Trade (1H Timeframe)",
                "estimated_duration": "4 to 8 Hours",
                "max_expiry":         "Cancel / Close after 24 Hours"
            }
        }
        print("\n" + "=" * 70)
        print(" MT5 DEMO ORDER EXECUTION TEST")
        print(f" Account: {self.mt5_bridge.login} | Server: {self.mt5_bridge.server}")
        print("=" * 70)
        self.print_signal_card(demo_rec)
        self.notifier.send_trade_signal_email(demo_rec)
        self.mt5_bridge.place_automated_order(demo_rec)
        print("=" * 70 + "\n")

    def print_signal_card(self, rec: Dict):
        """Prints a clean, formatted recommendation card for a detected setup."""
        dur  = rec["duration"]
        unit = rec.get("unit", "pips")
        print("┌" + "─" * 68 + "┐")
        print(f"│ 🔥 [TRADE RECOMMENDATION: {rec['pair']}] ({rec['tier']})".ljust(69) + "│")
        print("├" + "─" * 68 + "┤")
        print(f"│  MT5 Execution Ticker : {rec['ticker']}".ljust(69) + "│")
        print(f"│  Action               : {rec['action']} LIMIT / MARKET".ljust(69) + "│")
        print(f"│  Entry Price          : {rec['entry']:.5f}".ljust(69) + "│")
        print(f"│  Stop Loss            : {rec['stop_loss']:.5f} ({rec['sl_pips']:.1f} {unit})".ljust(69) + "│")
        print(f"│  Take Profit          : {rec['take_profit']:.5f} (1:3 R:R Target)".ljust(69) + "│")
        print(f"│  Max Risk (1%)        : ${rec['dollar_risk']:.2f}".ljust(69) + "│")
        print(f"│  Recommended Lots     : {rec['lot_size']} Lots (Micro/Standard)".ljust(69) + "│")
        print(f"│  Signal Rationale     : {rec['reason']}".ljust(69) + "│")
        print("├" + "─" * 68 + "┤")
        print("│ ⏱️ DURATION & HOLDING TIME GUIDANCE:".ljust(69) + "│")
        print(f"│  • Trade Style        : {dur['style']}".ljust(69) + "│")
        print(f"│  • Estimated Duration : {dur['estimated_duration']}".ljust(69) + "│")
        print(f"│  • Max Expiry Limit   : {dur['max_expiry']}".ljust(69) + "│")
        print("└" + "─" * 68 + "┘")


if __name__ == "__main__":
    scanner = MarketScanner()
    scanner.scan_market()
