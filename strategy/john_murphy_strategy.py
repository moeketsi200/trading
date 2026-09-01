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
        rsi = latest.get('RSI', 50)
        macd_line = latest.get('MACD_Line', 0)
        macd_signal = latest.get('MACD_Signal', 0)
        volume = latest.get('Volume', 0)
        volume_ma = latest.get('Volume_MA', 0)
        bb_width = latest.get('BB_Width', 1.0)
        
        # 1. Bullish Setup (Uptrend: EMA 50 > EMA 200)
        if latest['Uptrend']:
            # Signal: Price bounces off EMA 50 or Support level during an uptrend
            prev_low = previous['Low']
            prev_ema_50 = previous['EMA_50']
            
            # Additional Filters
            rsi_filter = rsi < 40  # Pulled back, not overbought
            macd_filter = (macd_line > 0) and (macd_line > macd_signal)  # Strong Bullish MACD confirmation
            vol_filter = volume > volume_ma  # Volume confirmation
            bb_filter = bb_width > config.MIN_BB_WIDTH_PCT  # Volatility confirmation
            
            # EMA 50 bounce or Support level bounce
            if prev_low <= prev_ema_50 and close_price > ema_50 and rsi_filter and macd_filter and vol_filter and bb_filter:
                stop_loss = min(support, latest['Low'] * 0.999) # Below support level
                return {
                    'action': 'BUY',
                    'entry': close_price,
                    'stop_loss': stop_loss,
                    'reason': 'Uptrend EMA 50 Bounce (Confirmed)'
                }

        # 2. Bearish Setup (Downtrend: EMA 50 < EMA 200)
        elif latest['Downtrend']:
            prev_high = previous['High']
            prev_ema_50 = previous['EMA_50']
            
            # Additional Filters
            rsi_filter = rsi > 60  # Pulled back, not oversold
            macd_filter = (macd_line < 0) and (macd_line < macd_signal)  # Strong Bearish MACD confirmation
            vol_filter = volume > volume_ma  # Volume confirmation
            bb_filter = bb_width > config.MIN_BB_WIDTH_PCT  # Volatility confirmation
            
            # EMA 50 rejection or Resistance level rejection
            if prev_high >= prev_ema_50 and close_price < ema_50 and rsi_filter and macd_filter and vol_filter and bb_filter:
                stop_loss = max(resistance, latest['High'] * 1.001) # Above resistance level
                return {
                    'action': 'SELL',
                    'entry': close_price,
                    'stop_loss': stop_loss,
                    'reason': 'Downtrend EMA 50 Rejection (Confirmed)'
                }

        return None
