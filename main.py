import sys
import argparse
from config.config import config
from execution.backtester import PropFirmBacktester
from scanner import MarketScanner

def main():
    parser = argparse.ArgumentParser(description="Automated Forex Trading & Market Scanner System")
    parser.add_argument("--scan", action="store_true", help="Run market scanner across watchlist pairs for trade recommendations")
    parser.add_argument("--fast-scan", action="store_true", help="Run hyper-sensitive test scanner (EMA 5/15) to force signal testing")
    parser.add_argument("--demo-signal", action="store_true", help="Preview sample trade recommendation card formatting")
    parser.add_argument("--demo-order", action="store_true", help="Execute a test trade on MT5 Demo Account")
    parser.add_argument("--backtest", action="store_true", help="Run backtest simulation engine on EUR/USD")
    args = parser.parse_args()

    print("=" * 65)
    print(" AUTOMATED FOREX TRADING & MARKET SCANNER SYSTEM")
    print(f" Target: R4,000 ZAR/mo (~$220 USD) on ${config.INITIAL_BALANCE:,.0f} Account")
    print(f" Strategy: John Murphy TA + 3-Mode News Handler")
    print(f" Risk per trade: {config.RISK_PER_TRADE_PCT*100}% | Min R:R = 1:{config.MIN_RISK_REWARD_RATIO}")
    print("=" * 65)
    
    # If --fast-scan flag passed
    if args.fast_scan:
        scanner = MarketScanner(balance=config.INITIAL_BALANCE)
        scanner.scan_market(fast_mode=True)
        return 0

    # If --demo-order flag passed
    if args.demo_order:
        scanner = MarketScanner(balance=config.INITIAL_BALANCE)
        scanner.execute_demo_trade()
        return 0

    # If --demo-signal flag passed
    if args.demo_signal:
        scanner = MarketScanner(balance=config.INITIAL_BALANCE)
        scanner.generate_demo_signal_card()
        return 0

    # If --scan flag passed, run Market Scanner
    if args.scan:
        scanner = MarketScanner(balance=config.INITIAL_BALANCE)
        scanner.scan_market()
        return 0

    # Default / --backtest mode
    print("\n[+] Running Backtest Engine on EUR/USD...")
    backtester = PropFirmBacktester(initial_balance=config.INITIAL_BALANCE)
    
    try:
        results_df = backtester.run_backtest(period="60d", interval=config.TIMEFRAME)
        
        final_equity = backtester.risk_manager.current_equity
        total_pnl = final_equity - config.INITIAL_BALANCE
        return_pct = (total_pnl / config.INITIAL_BALANCE) * 100
        
        print("\n" + "=" * 65)
        print(" BACKTEST RESULTS SUMMARY")
        print("=" * 65)
        print(f" Initial Account Balance : ${config.INITIAL_BALANCE:,.2f}")
        print(f" Final Account Equity   : ${final_equity:,.2f}")
        print(f" Total Net Profit/Loss  : ${total_pnl:+,.2f} ({return_pct:+.2f}%)")
        print(f" Target Monthly Yield    : +{config.MONTHLY_PROFIT_TARGET_PCT*100}% (${config.INITIAL_BALANCE*config.MONTHLY_PROFIT_TARGET_PCT:.2f})")
        
        if not results_df.empty:
            total_trades = len(results_df)
            wins = len(results_df[results_df['result'] == 'WIN'])
            losses = len(results_df[results_df['result'] == 'LOSS'])
            win_rate = (wins / total_trades) * 100 if total_trades > 0 else 0
            print(f" Total Trades Executed  : {total_trades}")
            print(f" Winning Trades         : {wins} ({win_rate:.1f}%)")
            print(f" Losing Trades          : {losses}")
        else:
            print(" Total Trades Executed  : 0 (Strict risk filters kept bot safe)")
            
        print("=" * 65 + "\n")
        
    except Exception as e:
        print(f"\n[-] Error running backtest: {e}")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
