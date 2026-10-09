"""
Market symbol helpers shared by scanner, risk, and execution layers.
"""
from typing import Optional, Tuple


FOREX_CODES = {
    "ARS", "AUD", "BRL", "CAD", "CHF", "CLP", "CNH", "COP", "CZK", "DKK",
    "EUR", "GBP", "HKD", "HUF", "IDR", "ILS", "INR", "JPY", "KRW", "MXN",
    "NGN", "NOK", "NZD", "PLN", "RUB", "SEK", "SGD", "THB", "TRY", "USD",
    "ZAR",
}

YAHOO_TO_MT5_SYMBOLS = {
    "GC=F": "XAUUSD",
    "SI=F": "XAGUSD",
    "^IXIC": "NAS100",
    "^GSPC": "US500",
    "^DJI": "US30",
}


def parse_forex_pair(name: str = "", ticker: str = "") -> Tuple[Optional[str], Optional[str]]:
    """Returns base and quote currency codes for standard forex pairs."""
    if name and "/" in name:
        base, quote = [part.strip().upper() for part in name.split("/", 1)]
        if base in FOREX_CODES and quote in FOREX_CODES:
            return base, quote

    compact = ticker.upper().replace("=X", "").replace("/", "")
    if len(compact) >= 6:
        base = compact[:3]
        quote = compact[3:6]
        if base in FOREX_CODES and quote in FOREX_CODES:
            return base, quote

    return None, None


def mt5_symbol_from_market(name: str = "", ticker: str = "") -> str:
    """
    Converts a display/Yahoo ticker into the closest plain MT5 symbol.
    Broker suffixes such as EURUSDm still need broker-specific configuration.
    """
    if ticker in YAHOO_TO_MT5_SYMBOLS:
        return YAHOO_TO_MT5_SYMBOLS[ticker]

    base, quote = parse_forex_pair(name, ticker)
    if base and quote:
        return f"{base}{quote}"

    if ticker:
        return ticker.replace("=X", "").replace("/", "")

    return name.replace("/", "").replace(" ", "").upper()


def pip_size_for_symbol(symbol: str = "", price: Optional[float] = None) -> float:
    """
    Returns the usual pip size for display and approximate risk math.
    JPY pairs use 0.01; most forex pairs use 0.0001; metals/indices use 0.1.
    """
    clean = (symbol or "").upper()

    if len(clean) >= 6 and clean[:3] in FOREX_CODES and clean[3:6] in FOREX_CODES:
        quote = clean[3:6]
        if quote in {"JPY", "HUF", "THB"}:
            return 0.01
        if quote in {"KRW", "IDR", "CLP", "COP"}:
            return 1.0
        return 0.0001

    if clean.startswith(("XAU", "XAG")):
        return 0.1

    if price is not None and price > 1000:
        return 0.1

    return 0.0001
