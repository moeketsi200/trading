"""
Manual fundamental-bias filter.

The scanner does not invent fundamentals. Bias values come from config and are
used only to block technical signals that fight the chosen macro direction.
"""
from typing import Dict, Optional, Tuple

from config.config import config
from utils.market_symbols import parse_forex_pair


class FundamentalBiasFilter:
    def __init__(self, bias_map: Optional[Dict[str, str]] = None, enabled: bool = True):
        self.bias_map = {
            key.upper(): value.lower()
            for key, value in (bias_map or config.FUNDAMENTAL_BIAS).items()
        }
        self.enabled = enabled

    def get_pair_bias(self, name: str, ticker: str) -> Dict[str, Optional[str]]:
        base, quote = parse_forex_pair(name, ticker)
        if not base or not quote:
            return {
                "base": None,
                "quote": None,
                "direction": None,
                "strength": "n/a",
                "label": "N/A",
            }

        base_score = self._currency_score(base)
        quote_score = self._currency_score(quote)
        pair_score = base_score - quote_score

        direction = None
        if pair_score > 0:
            direction = "BUY"
        elif pair_score < 0:
            direction = "SELL"

        strength = "strong" if abs(pair_score) >= 2 else ("light" if abs(pair_score) == 1 else "neutral")
        label = f"{base}:{self.bias_map.get(base, 'neutral')} / {quote}:{self.bias_map.get(quote, 'neutral')}"
        if direction:
            label = f"{label} => {direction} only ({strength})"
        else:
            label = f"{label} => neutral"

        return {
            "base": base,
            "quote": quote,
            "direction": direction,
            "strength": strength,
            "label": label,
        }

    def filter_signal(
        self, signal: Optional[Dict], name: str, ticker: str
    ) -> Tuple[Optional[Dict], Dict[str, Optional[str]], Optional[str]]:
        bias = self.get_pair_bias(name, ticker)

        if not signal or not self.enabled:
            return signal, bias, None

        direction = bias.get("direction")
        if not direction:
            return signal, bias, None

        if signal.get("action") != direction:
            return None, bias, f"Blocked by fundamental bias: {bias['label']}"

        filtered_signal = dict(signal)
        filtered_signal["reason"] = f"{signal['reason']} | Bias aligned: {bias['label']}"
        return filtered_signal, bias, None

    def _currency_score(self, code: str) -> int:
        value = self.bias_map.get(code.upper(), "neutral")
        if value in {"bullish", "buy", "strong"}:
            return 1
        if value in {"bearish", "sell", "weak"}:
            return -1
        return 0
