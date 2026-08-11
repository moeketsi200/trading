"""
3-Mode News Execution Handler.
Manages Normal Mode, Shield Mode (Pre-News Protection), and Hunter Mode (Post-News Momentum).
"""
from enum import Enum
from datetime import datetime, timedelta
from typing import Optional, Dict
from config.config import config
from data.news_data import NewsDataEngine

class ExecutionMode(Enum):
    NORMAL = "NORMAL"   # Regular technical trading
    SHIELD = "SHIELD"   # Pre-news protection (no new trades, tight SL)
    HUNTER = "HUNTER"   # Post-news momentum scanning

class NewsExecutionHandler:
    def __init__(self, news_engine: NewsDataEngine):
        self.news_engine = news_engine
        self.current_mode = ExecutionMode.NORMAL
        self.last_news_time: Optional[datetime] = None

    def update_execution_mode(self) -> ExecutionMode:
        """
        Evaluates current time against economic calendar to update system mode.
        """
        minutes_to_news = self.news_engine.minutes_until_next_high_impact_event()
        
        # 1. Check for Pre-News Shield Mode
        if minutes_to_news <= config.PRE_NEWS_SHIELD_MINUTES:
            self.current_mode = ExecutionMode.SHIELD
            return self.current_mode
            
        # 2. Check for Post-News Hunter Mode (within 30 mins after news)
        if self.last_news_time:
            minutes_since_news = (datetime.utcnow() - self.last_news_time).total_seconds() / 60.0
            if minutes_since_news <= config.POST_NEWS_HUNTER_MINUTES:
                self.current_mode = ExecutionMode.HUNTER
                return self.current_mode

        # 3. Default to Normal Mode
        self.current_mode = ExecutionMode.NORMAL
        return self.current_mode

    def process_trade_signal(self, raw_signal: Optional[Dict]) -> Optional[Dict]:
        """
        Filters or modifies signals based on active ExecutionMode.
        """
        mode = self.update_execution_mode()
        
        if mode == ExecutionMode.SHIELD:
            # Strictly zero new trades during Shield Mode
            return None
            
        if mode == ExecutionMode.HUNTER and raw_signal:
            # In Hunter Mode, require strong post-news momentum validation
            raw_signal['reason'] = f"[Post-News Hunter] {raw_signal['reason']}"
            return raw_signal

        return raw_signal
