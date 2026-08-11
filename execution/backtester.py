"""
Backtester Framework with Prop Firm Rules & Dynamic 1% Risk Engine.
"""
import pandas as pd
from config.config import config
from risk.risk_manager import RiskManager
from data.market_data import MarketDataEngine
from strategy.john_murphy_strategy import JohnMurphyStrategy
from strategy.news_handler import NewsExecutionHandler, ExecutionMode
from data.news_data import NewsDataEngine

class PropFirmBacktester:
    def __init__(self, initial_balance: float = config.INITIAL_BALANCE):
        self.risk_manager = RiskManager(initial_balance=initial_balance)
        self.market_engine = MarketDataEngine()
        self.strategy = JohnMurphyStrategy()
        self.news_engine = NewsDataEngine()
        self.news_handler = NewsExecutionHandler(self.news_engine)
        self.trades_history = []

    def run_backtest(self, period: str = "60d", interval: str = config.TIMEFRAME) -> pd.DataFrame:
        """
        Runs backtest over historical dataset.
        """
        # Fetch & compute indicators
        df = self.market_engine.fetch_historical_candles(period=period, interval=interval)
        df = self.market_engine.calculate_technical_indicators(df)
        
        position = None
        
        for i in range(config.SLOW_EMA_PERIOD, len(df)):
            sub_df = df.iloc[:i+1]
            current_bar = sub_df.iloc[-1]
            current_price = current_bar['Close']
            
            # Update equity metrics
            self.risk_manager.update_equity(self.risk_manager.current_equity)
            
            # Check open position exit
            if position:
                action = position['action']
                sl = position['stop_loss']
                tp = position['take_profit']
                
                # Check SL hit
                if (action == 'BUY' and current_bar['Low'] <= sl) or (action == 'SELL' and current_bar['High'] >= sl):
                    loss = position['dollar_risk']
                    self.risk_manager.current_equity -= loss
                    self.trades_history.append({
                        'time': current_bar.name, 'result': 'LOSS', 'pnl': -loss, 'equity': self.risk_manager.current_equity
                    })
                    print(f"  [TRADE CLOSED] {current_bar.name.strftime('%Y-%m-%d %H:%M')} | Result: LOSS | PnL: -${loss:.2f} | Equity: ${self.risk_manager.current_equity:.2f}")
                    position = None
                    
                # Check TP hit
                elif (action == 'BUY' and current_bar['High'] >= tp) or (action == 'SELL' and current_bar['Low'] <= tp):
                    profit = position['dollar_risk'] * config.MIN_RISK_REWARD_RATIO
                    self.risk_manager.current_equity += profit
                    self.trades_history.append({
                        'time': current_bar.name, 'result': 'WIN', 'pnl': profit, 'equity': self.risk_manager.current_equity
                    })
                    print(f"  [TRADE CLOSED] {current_bar.name.strftime('%Y-%m-%d %H:%M')} | Result: WIN  | PnL: +${profit:.2f} | Equity: ${self.risk_manager.current_equity:.2f}")
                    position = None

            # Look for new entries if no position open
            if not position and self.risk_manager.is_trading_allowed():
                raw_signal = self.strategy.evaluate_signals(sub_df)
                valid_signal = self.news_handler.process_trade_signal(raw_signal)
                
                if valid_signal:
                    entry = valid_signal['entry']
                    sl = valid_signal['stop_loss']
                    pos_plan = self.risk_manager.calculate_position_size(entry, sl)
                    if pos_plan:
                        position = {
                            'action': valid_signal['action'],
                            'entry': pos_plan['entry_price'],
                            'stop_loss': pos_plan['stop_loss'],
                            'take_profit': pos_plan['take_profit'],
                            'dollar_risk': pos_plan['dollar_risk'],
                            'lot_size': pos_plan['lot_size'],
                            'reason': valid_signal['reason'],
                            'open_time': current_bar.name
                        }
                        print(f"  [ORDER FIRED] {current_bar.name.strftime('%Y-%m-%d %H:%M')} | Action: {position['action']} | Entry: {position['entry']:.5f} | SL: {position['stop_loss']:.5f} | TP: {position['take_profit']:.5f} | Lot Size: {position['lot_size']} | Risk: ${position['dollar_risk']:.2f}")

        return pd.DataFrame(self.trades_history)
