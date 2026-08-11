"""
John J. Murphy Technical Analysis Strategy Engine.
Implements trend identification, EMA crossovers, and Support/Resistance entry triggers.
"""
from typing import Optional, Dict
import pandas as pd
from config.config import config

class JohnMurphyStrategy:
    def __init__(self):
        pass

    def evaluate_signals(self, df: pd.DataFrame) -> Optional[Dict[str, str]]:
        """
        Evaluates the latest candles for entry signals.
        Returns signal dictionary if a valid trade setup is detected:
        { 'action': 'BUY' | 'SELL', 'entry': price, 'stop_loss': price }
        """
        if len(df) < config.SLOW_EMA_PERIOD:
            return None

        latest = df.iloc[-1]
        previous = df.iloc[-2]
        
        close_price = latest['Close']
        ema_50 = latest['EMA_50']
        ema_200 = latest['EMA_200']
        support = latest['Support']
        resistance = latest['Resistance']
        
        # 1. Bullish Setup (Uptrend: EMA 50 > EMA 200)
        if latest['Uptrend']:
            # Signal: Price bounces off EMA 50 or Support level during an uptrend
            prev_low = previous['Low']
            prev_ema_50 = previous['EMA_50']
            
            # EMA 50 bounce or Support level bounce
            if prev_low <= prev_ema_50 and close_price > ema_50:
                stop_loss = min(support, latest['Low'] * 0.999) # Below support level
                return {
                    'action': 'BUY',
                    'entry': close_price,
                    'stop_loss': stop_loss,
                    'reason': 'Uptrend EMA 50 Support Bounce'
                }

        # 2. Bearish Setup (Downtrend: EMA 50 < EMA 200)
        elif latest['Downtrend']:
            prev_high = previous['High']
            prev_ema_50 = previous['EMA_50']
            
            # EMA 50 rejection or Resistance level rejection
            if prev_high >= prev_ema_50 and close_price < ema_50:
                stop_loss = max(resistance, latest['High'] * 1.001) # Above resistance level
                return {
                    'action': 'SELL',
                    'entry': close_price,
                    'stop_loss': stop_loss,
                    'reason': 'Downtrend EMA 50 Resistance Rejection'
                }

        return None
