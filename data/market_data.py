"""
Market Data Engine.
Fetches historical candle data and processes technical indicator series.
"""
import pandas as pd
import yfinance as yf
from config.config import config

class MarketDataEngine:
    def __init__(self, symbol: str = config.SYMBOL):
        self.symbol = symbol

    def fetch_historical_candles(self, period: str = "60d", interval: str = config.TIMEFRAME) -> pd.DataFrame:
        """
        Fetches historical OHLC candle data for the symbol.
        Returns a Pandas DataFrame with DatetimeIndex and columns [Open, High, Low, Close, Volume].
        """
        ticker = yf.Ticker(self.symbol)
        df = ticker.history(period=period, interval=interval)
        
        if df.empty:
            raise ValueError(f"Failed to fetch market data for {self.symbol}")
            
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']].dropna()
        return df

    def calculate_technical_indicators(self, df: pd.DataFrame, fast_mode: bool = False) -> pd.DataFrame:
        """
        Calculates 50 EMA, 200 EMA (or 5 EMA/15 EMA if fast_mode=True), and Support/Resistance levels.
        """
        df = df.copy()
        
        fast_period = 5 if fast_mode else config.FAST_EMA_PERIOD
        slow_period = 15 if fast_mode else config.SLOW_EMA_PERIOD
        sr_window = 10 if fast_mode else config.SR_LOOKBACK_PERIODS
        
        # Calculate Exponential Moving Averages
        df['EMA_50'] = df['Close'].ewm(span=fast_period, adjust=False).mean()
        df['EMA_200'] = df['Close'].ewm(span=slow_period, adjust=False).mean()
        
        # Calculate Support and Resistance (Rolling Minimum and Maximum)
        df['Support'] = df['Low'].rolling(window=sr_window).min()
        df['Resistance'] = df['High'].rolling(window=sr_window).max()
        
        # Calculate Average True Range (ATR 14) for duration estimation
        high_low = df['High'] - df['Low']
        high_close = (df['High'] - df['Close'].shift()).abs()
        low_close = (df['Low'] - df['Close'].shift()).abs()
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['ATR_14'] = tr.rolling(window=14).mean()
        
        # Trend Status
        df['Uptrend'] = df['EMA_50'] > df['EMA_200']
        df['Downtrend'] = df['EMA_50'] < df['EMA_200']
        
        return df
