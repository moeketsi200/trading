"""
Global Configuration for Automated Forex Trading System.
"""
import os
from dataclasses import dataclass

@dataclass
class TradingConfig:
    # Asset Settings
    SYMBOL: str = "EURUSD=X"           # Yahoo Finance ticker for EUR/USD
    TIMEFRAME: str = "1h"              # Default candle interval (1 hour)
    INITIAL_BALANCE: float = 5000.0    # Prop Firm Challenge Account Size ($5,000 USD)
    
    # Risk Management Parameters
    RISK_PER_TRADE_PCT: float = 0.01   # 1% risk per trade
    MIN_RISK_REWARD_RATIO: float = 3.0 # 1:3 Risk-to-Reward ratio
    MAX_DAILY_DRAWDOWN_PCT: float = 0.03 # 3% hard daily drawdown limit
    MAX_TOTAL_DRAWDOWN_PCT: float = 0.08 # 8% total max drawdown limit
    MONTHLY_PROFIT_TARGET_PCT: float = 0.044 # 4.4% profit target (~$220 USD / R4,000 ZAR)
    
    # Strategy Indicators
    FAST_EMA_PERIOD: int = 50
    SLOW_EMA_PERIOD: int = 200
    SR_LOOKBACK_PERIODS: int = 50
    
    # News Handler Settings
    PRE_NEWS_SHIELD_MINUTES: int = 30  # Pause 30 minutes before high-impact news
    POST_NEWS_HUNTER_MINUTES: int = 30 # Wait 30 minutes after news before hunting trend
    
config = TradingConfig()
