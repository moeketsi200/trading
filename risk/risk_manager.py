"""
Quantitative Risk Management Engine.
Handles position sizing, Stop Loss / Take Profit calculations, and drawdown circuit breakers.
"""
from typing import Dict, Optional
from config.config import config

class RiskManager:
    def __init__(self, initial_balance: float = config.INITIAL_BALANCE):
        self.initial_balance = initial_balance
        self.current_equity = initial_balance
        self.daily_starting_equity = initial_balance
        self.monthly_starting_equity = initial_balance
        self.trading_halted_today = False
        self.monthly_target_reached = False
        
    def update_equity(self, current_equity: float):
        """Update current live account equity and check circuit breakers."""
        self.current_equity = current_equity
        
        # Check Daily Drawdown Limit
        daily_loss_pct = (self.daily_starting_equity - self.current_equity) / self.daily_starting_equity
        if daily_loss_pct >= config.MAX_DAILY_DRAWDOWN_PCT:
            self.trading_halted_today = True
            
        # Check Total Drawdown Limit
        total_loss_pct = (self.initial_balance - self.current_equity) / self.initial_balance
        if total_loss_pct >= config.MAX_TOTAL_DRAWDOWN_PCT:
            self.trading_halted_today = True
            
        # Check Monthly Target
        monthly_profit_pct = (self.current_equity - self.monthly_starting_equity) / self.monthly_starting_equity
        if monthly_profit_pct >= config.MONTHLY_PROFIT_TARGET_PCT:
            self.monthly_target_reached = True

    def is_trading_allowed(self) -> bool:
        """Returns True if trading is permitted under current risk metrics."""
        if self.trading_halted_today:
            return False
        if self.monthly_target_reached:
            return False
        return True

    def calculate_position_size(
        self, entry_price: float, stop_loss_price: float, pip_value_per_lot: float = 10.0, atr: Optional[float] = None
    ) -> Optional[Dict[str, float]]:
        """
        Calculates position lot size and Take Profit level using strict 1% risk rule and 1:3 R:R ratio.
        Dynamic ATR-based Stop Loss is applied if atr is provided.
        """
        if not self.is_trading_allowed():
            return None

        # Use ATR for dynamic stop loss if provided, otherwise fallback to Support/Resistance distance
        if atr is not None and atr > 0:
            sl_distance = atr * config.ATR_SL_MULTIPLIER
            if stop_loss_price < entry_price:  # Long Trade
                stop_loss_price = entry_price - sl_distance
            else:                              # Short Trade
                stop_loss_price = entry_price + sl_distance
        else:
            sl_distance = abs(entry_price - stop_loss_price)

        if sl_distance <= 0:
            return None
            
        # Determine pip scaling factor dynamically based on asset price (Crypto/Indices vs Forex)
        pip_scale = 0.1 if entry_price > 1000 else 0.0001
        pips_at_risk = sl_distance / pip_scale
        
        # Risk amount in currency (1% of current equity)
        dollar_risk = self.current_equity * config.RISK_PER_TRADE_PCT
        
        # Calculate Lot Size
        # Lot Size = (Dollar Risk) / (Pips at Risk * Pip Value per Standard Lot)
        lot_size = dollar_risk / (pips_at_risk * pip_value_per_lot)
        lot_size = round(lot_size, 3) if entry_price > 1000 else round(lot_size, 2)

        
        # Calculate Take Profit and Break-Even Trigger
        if getattr(config, 'INTRADAY_SWING_MODE', False):
            target_rr = config.RUNNER_MAX_RR
            be_distance = sl_distance * config.TRAILING_STOP_TRIGGER_RR
            if entry_price > stop_loss_price:
                break_even_trigger = entry_price + be_distance
            else:
                break_even_trigger = entry_price - be_distance
        else:
            target_rr = config.MIN_RISK_REWARD_RATIO
            break_even_trigger = None
            
        tp_distance = sl_distance * target_rr
        if entry_price > stop_loss_price:  # Long Trade
            take_profit_price = entry_price + tp_distance
        else:                              # Short Trade
            take_profit_price = entry_price - tp_distance

        return {
            "entry_price": entry_price,
            "stop_loss": stop_loss_price,
            "take_profit": take_profit_price,
            "lot_size": max(0.01, lot_size),  # Minimum 0.01 micro-lot
            "dollar_risk": dollar_risk,
            "reward_risk_ratio": target_rr,
            "break_even_trigger": break_even_trigger
        }

    def reset_daily_circuit_breaker(self):
        """Called at midnight UTC to reset daily drawdown check."""
        self.daily_starting_equity = self.current_equity
        self.trading_halted_today = False
