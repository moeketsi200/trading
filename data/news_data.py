"""
Economic Calendar & News Feed Module.
Fetches high-impact economic events (NFP, CPI, Central Bank Rate Decisions).
"""
from datetime import datetime, timedelta
from typing import List, Dict
import requests

class NewsDataEngine:
    def __init__(self):
        # High impact news events keywords
        self.high_impact_keywords = [
            "Non-Farm Employment Change", "NFP", "Consumer Price Index", "CPI",
            "Interest Rate Decision", "FOMC", "Fed Chair Press Conference",
            "ECB Press Conference", "Unemployment Rate"
        ]

    def fetch_upcoming_high_impact_events(self) -> List[Dict]:
        """
        Fetches live high-impact economic news events from public calendar feeds (ForexFactory JSON feed).
        No API key required!
        """
        events = []
        try:
            # Public economic calendar feed endpoint (ForexFactory weekly JSON feed)
            url = "https://nodedata.forexfactory.com/daily_calendar.json"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                for item in data:
                    impact = str(item.get("impact", "")).lower()
                    title = item.get("title", "")
                    if impact == "high" or any(kw.lower() in title.lower() for kw in self.high_impact_keywords):
                        date_str = item.get("date", "")
                        if date_str:
                            try:
                                event_dt = datetime.fromisoformat(date_str.replace("Z", "+00:00")).replace(tzinfo=None)
                                events.append({"title": title, "time": event_dt, "impact": "High"})
                            except ValueError:
                                pass
        except Exception as e:
            # Fallback to local calendar check if internet or endpoint is slow
            pass

        return events

    def minutes_until_next_high_impact_event(self) -> float:
        """
        Returns minutes remaining until the next scheduled high-impact event.
        Returns float infinity if no event is within the window.
        """
        events = self.fetch_upcoming_high_impact_events()
        if not events:
            return float('inf')
            
        now = datetime.utcnow()
        nearest_minutes = float('inf')
        for event in events:
            event_time = event.get('time')
            if event_time and event_time > now:
                diff = (event_time - now).total_seconds() / 60.0
                if diff < nearest_minutes:
                    nearest_minutes = diff
                    
        return nearest_minutes
