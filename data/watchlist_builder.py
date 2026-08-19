"""
Full Universe Watchlist Builder.
Dynamically builds the complete symbol watchlist based on environment configuration.

Categories supported:
  - Forex Majors  (7 pairs)
  - Forex Minors  (22 pairs)
  - Forex Exotics (31 pairs)   → total ~60 forex pairs
  - Metals        (5 symbols)
  - Energy        (5 symbols)
  - Agriculture   (5 symbols)
  - Global Indices(20 symbols)
  - Cryptocurrency(20 symbols)
  - US Stocks     (S&P 500 ~480 symbols)

pip_scale: price distance per "1 pip" for each asset class.
  Used for proximity-to-EMA display and SL pip calculations.
"""
from typing import List, Dict

# ─── Forex Majors ─────────────────────────────────────────────────────────────

FOREX_MAJORS: List[Dict] = [
    {"name": "EUR/USD",  "ticker": "EURUSD=X", "tier": "Forex Major",  "rec": "RECOMMENDED",             "pip_scale": 0.0001},
    {"name": "GBP/USD",  "ticker": "GBPUSD=X", "tier": "Forex Major",  "rec": "RECOMMENDED",             "pip_scale": 0.0001},
    {"name": "USD/JPY",  "ticker": "USDJPY=X", "tier": "Forex Major",  "rec": "RECOMMENDED",             "pip_scale": 0.01},
    {"name": "USD/CHF",  "ticker": "USDCHF=X", "tier": "Forex Major",  "rec": "RECOMMENDED",             "pip_scale": 0.0001},
    {"name": "AUD/USD",  "ticker": "AUDUSD=X", "tier": "Forex Major",  "rec": "RECOMMENDED",             "pip_scale": 0.0001},
    {"name": "USD/CAD",  "ticker": "USDCAD=X", "tier": "Forex Major",  "rec": "RECOMMENDED",             "pip_scale": 0.0001},
    {"name": "NZD/USD",  "ticker": "NZDUSD=X", "tier": "Forex Major",  "rec": "RECOMMENDED",             "pip_scale": 0.0001},
]

# ─── Forex Minors ─────────────────────────────────────────────────────────────

FOREX_MINORS: List[Dict] = [
    {"name": "EUR/GBP",  "ticker": "EURGBP=X", "tier": "Forex Minor",  "rec": "MODERATE",                "pip_scale": 0.0001},
    {"name": "EUR/JPY",  "ticker": "EURJPY=X", "tier": "Forex Minor",  "rec": "MODERATE",                "pip_scale": 0.01},
    {"name": "EUR/CHF",  "ticker": "EURCHF=X", "tier": "Forex Minor",  "rec": "MODERATE",                "pip_scale": 0.0001},
    {"name": "EUR/AUD",  "ticker": "EURAUD=X", "tier": "Forex Minor",  "rec": "MODERATE",                "pip_scale": 0.0001},
    {"name": "EUR/CAD",  "ticker": "EURCAD=X", "tier": "Forex Minor",  "rec": "MODERATE",                "pip_scale": 0.0001},
    {"name": "EUR/NZD",  "ticker": "EURNZD=X", "tier": "Forex Minor",  "rec": "MODERATE",                "pip_scale": 0.0001},
    {"name": "GBP/JPY",  "ticker": "GBPJPY=X", "tier": "Forex Minor",  "rec": "MODERATE",                "pip_scale": 0.01},
    {"name": "GBP/CHF",  "ticker": "GBPCHF=X", "tier": "Forex Minor",  "rec": "MODERATE",                "pip_scale": 0.0001},
    {"name": "GBP/AUD",  "ticker": "GBPAUD=X", "tier": "Forex Minor",  "rec": "MODERATE",                "pip_scale": 0.0001},
    {"name": "GBP/CAD",  "ticker": "GBPCAD=X", "tier": "Forex Minor",  "rec": "MODERATE",                "pip_scale": 0.0001},
    {"name": "GBP/NZD",  "ticker": "GBPNZD=X", "tier": "Forex Minor",  "rec": "MODERATE",                "pip_scale": 0.0001},
    {"name": "AUD/JPY",  "ticker": "AUDJPY=X", "tier": "Forex Minor",  "rec": "MODERATE",                "pip_scale": 0.01},
    {"name": "AUD/CHF",  "ticker": "AUDCHF=X", "tier": "Forex Minor",  "rec": "MODERATE",                "pip_scale": 0.0001},
    {"name": "AUD/CAD",  "ticker": "AUDCAD=X", "tier": "Forex Minor",  "rec": "MODERATE",                "pip_scale": 0.0001},
    {"name": "AUD/NZD",  "ticker": "AUDNZD=X", "tier": "Forex Minor",  "rec": "MODERATE",                "pip_scale": 0.0001},
    {"name": "CAD/JPY",  "ticker": "CADJPY=X", "tier": "Forex Minor",  "rec": "MODERATE",                "pip_scale": 0.01},
    {"name": "CAD/CHF",  "ticker": "CADCHF=X", "tier": "Forex Minor",  "rec": "MODERATE",                "pip_scale": 0.0001},
    {"name": "CHF/JPY",  "ticker": "CHFJPY=X", "tier": "Forex Minor",  "rec": "MODERATE",                "pip_scale": 0.01},
    {"name": "NZD/JPY",  "ticker": "NZDJPY=X", "tier": "Forex Minor",  "rec": "MODERATE",                "pip_scale": 0.01},
    {"name": "NZD/CHF",  "ticker": "NZDCHF=X", "tier": "Forex Minor",  "rec": "MODERATE",                "pip_scale": 0.0001},
    {"name": "NZD/CAD",  "ticker": "NZDCAD=X", "tier": "Forex Minor",  "rec": "MODERATE",                "pip_scale": 0.0001},
    {"name": "EUR/SGD",  "ticker": "EURSGD=X", "tier": "Forex Minor",  "rec": "MODERATE",                "pip_scale": 0.0001},
]

# ─── Forex Exotics ────────────────────────────────────────────────────────────

FOREX_EXOTICS: List[Dict] = [
    {"name": "USD/ZAR",  "ticker": "USDZAR=X", "tier": "Forex Exotic", "rec": "CAUTION — Wide Spreads", "pip_scale": 0.0001},
    {"name": "USD/TRY",  "ticker": "USDTRY=X", "tier": "Forex Exotic", "rec": "CAUTION — Wide Spreads", "pip_scale": 0.0001},
    {"name": "USD/MXN",  "ticker": "USDMXN=X", "tier": "Forex Exotic", "rec": "CAUTION — Wide Spreads", "pip_scale": 0.0001},
    {"name": "USD/SGD",  "ticker": "USDSGD=X", "tier": "Forex Exotic", "rec": "CAUTION — Wide Spreads", "pip_scale": 0.0001},
    {"name": "USD/HKD",  "ticker": "USDHKD=X", "tier": "Forex Exotic", "rec": "CAUTION — Wide Spreads", "pip_scale": 0.0001},
    {"name": "USD/NOK",  "ticker": "USDNOK=X", "tier": "Forex Exotic", "rec": "CAUTION — Wide Spreads", "pip_scale": 0.0001},
    {"name": "USD/SEK",  "ticker": "USDSEK=X", "tier": "Forex Exotic", "rec": "CAUTION — Wide Spreads", "pip_scale": 0.0001},
    {"name": "USD/DKK",  "ticker": "USDDKK=X", "tier": "Forex Exotic", "rec": "CAUTION — Wide Spreads", "pip_scale": 0.0001},
    {"name": "USD/PLN",  "ticker": "USDPLN=X", "tier": "Forex Exotic", "rec": "CAUTION — Wide Spreads", "pip_scale": 0.0001},
    {"name": "USD/HUF",  "ticker": "USDHUF=X", "tier": "Forex Exotic", "rec": "CAUTION — Wide Spreads", "pip_scale": 0.01},
    {"name": "USD/CZK",  "ticker": "USDCZK=X", "tier": "Forex Exotic", "rec": "CAUTION — Wide Spreads", "pip_scale": 0.001},
    {"name": "USD/THB",  "ticker": "USDTHB=X", "tier": "Forex Exotic", "rec": "CAUTION — Wide Spreads", "pip_scale": 0.001},
    {"name": "USD/INR",  "ticker": "USDINR=X", "tier": "Forex Exotic", "rec": "CAUTION — Wide Spreads", "pip_scale": 0.001},
    {"name": "USD/CNY",  "ticker": "USDCNY=X", "tier": "Forex Exotic", "rec": "CAUTION — Wide Spreads", "pip_scale": 0.0001},
    {"name": "USD/ILS",  "ticker": "USDILS=X", "tier": "Forex Exotic", "rec": "CAUTION — Wide Spreads", "pip_scale": 0.0001},
    {"name": "USD/SAR",  "ticker": "USDSAR=X", "tier": "Forex Exotic", "rec": "CAUTION — Wide Spreads", "pip_scale": 0.0001},
    {"name": "USD/PHP",  "ticker": "USDPHP=X", "tier": "Forex Exotic", "rec": "CAUTION — Wide Spreads", "pip_scale": 0.001},
    {"name": "USD/IDR",  "ticker": "USDIDR=X", "tier": "Forex Exotic", "rec": "CAUTION — Wide Spreads", "pip_scale": 0.1},
    {"name": "USD/KRW",  "ticker": "USDKRW=X", "tier": "Forex Exotic", "rec": "CAUTION — Wide Spreads", "pip_scale": 0.1},
    {"name": "USD/MYR",  "ticker": "USDMYR=X", "tier": "Forex Exotic", "rec": "CAUTION — Wide Spreads", "pip_scale": 0.0001},
    {"name": "EUR/ZAR",  "ticker": "EURZAR=X", "tier": "Forex Exotic", "rec": "CAUTION — Wide Spreads", "pip_scale": 0.0001},
    {"name": "EUR/TRY",  "ticker": "EURTRY=X", "tier": "Forex Exotic", "rec": "CAUTION — Wide Spreads", "pip_scale": 0.0001},
    {"name": "EUR/NOK",  "ticker": "EURNOK=X", "tier": "Forex Exotic", "rec": "CAUTION — Wide Spreads", "pip_scale": 0.0001},
    {"name": "EUR/SEK",  "ticker": "EURSEK=X", "tier": "Forex Exotic", "rec": "CAUTION — Wide Spreads", "pip_scale": 0.0001},
    {"name": "EUR/PLN",  "ticker": "EURPLN=X", "tier": "Forex Exotic", "rec": "CAUTION — Wide Spreads", "pip_scale": 0.0001},
    {"name": "EUR/HUF",  "ticker": "EURHUF=X", "tier": "Forex Exotic", "rec": "CAUTION — Wide Spreads", "pip_scale": 0.01},
    {"name": "EUR/CZK",  "ticker": "EURCZK=X", "tier": "Forex Exotic", "rec": "CAUTION — Wide Spreads", "pip_scale": 0.001},
    {"name": "GBP/ZAR",  "ticker": "GBPZAR=X", "tier": "Forex Exotic", "rec": "CAUTION — Wide Spreads", "pip_scale": 0.0001},
    {"name": "GBP/NOK",  "ticker": "GBPNOK=X", "tier": "Forex Exotic", "rec": "CAUTION — Wide Spreads", "pip_scale": 0.0001},
    {"name": "GBP/SEK",  "ticker": "GBPSEK=X", "tier": "Forex Exotic", "rec": "CAUTION — Wide Spreads", "pip_scale": 0.0001},
    {"name": "AUD/ZAR",  "ticker": "AUDZAR=X", "tier": "Forex Exotic", "rec": "CAUTION — Wide Spreads", "pip_scale": 0.0001},
]

# ─── Metals ───────────────────────────────────────────────────────────────────

METALS: List[Dict] = [
    {"name": "GOLD (XAU/USD)",    "ticker": "GC=F",  "tier": "Metal",       "rec": "RECOMMENDED (Post-News)",  "pip_scale": 0.1},
    {"name": "SILVER (XAG/USD)",  "ticker": "SI=F",  "tier": "Metal",       "rec": "RECOMMENDED (Post-News)",  "pip_scale": 0.01},
    {"name": "PLATINUM",          "ticker": "PL=F",  "tier": "Metal",       "rec": "MODERATE",                 "pip_scale": 0.1},
    {"name": "PALLADIUM",         "ticker": "PA=F",  "tier": "Metal",       "rec": "MODERATE",                 "pip_scale": 1.0},
    {"name": "COPPER",            "ticker": "HG=F",  "tier": "Metal",       "rec": "MODERATE",                 "pip_scale": 0.001},
]

# ─── Energy & Agriculture ─────────────────────────────────────────────────────

ENERGY: List[Dict] = [
    {"name": "CRUDE OIL WTI",     "ticker": "CL=F",  "tier": "Energy",      "rec": "MODERATE",                 "pip_scale": 0.01},
    {"name": "BRENT CRUDE OIL",   "ticker": "BZ=F",  "tier": "Energy",      "rec": "MODERATE",                 "pip_scale": 0.01},
    {"name": "NATURAL GAS",       "ticker": "NG=F",  "tier": "Energy",      "rec": "MODERATE",                 "pip_scale": 0.001},
    {"name": "GASOLINE RBOB",     "ticker": "RB=F",  "tier": "Energy",      "rec": "MODERATE",                 "pip_scale": 0.001},
    {"name": "HEATING OIL",       "ticker": "HO=F",  "tier": "Energy",      "rec": "MODERATE",                 "pip_scale": 0.001},
    {"name": "CORN",              "ticker": "ZC=F",  "tier": "Agriculture", "rec": "MODERATE",                 "pip_scale": 0.01},
    {"name": "WHEAT",             "ticker": "ZW=F",  "tier": "Agriculture", "rec": "MODERATE",                 "pip_scale": 0.01},
    {"name": "SOYBEANS",          "ticker": "ZS=F",  "tier": "Agriculture", "rec": "MODERATE",                 "pip_scale": 0.01},
    {"name": "SUGAR",             "ticker": "SB=F",  "tier": "Agriculture", "rec": "MODERATE",                 "pip_scale": 0.001},
    {"name": "COFFEE",            "ticker": "KC=F",  "tier": "Agriculture", "rec": "MODERATE",                 "pip_scale": 0.01},
]

# ─── Global Indices ───────────────────────────────────────────────────────────

INDICES: List[Dict] = [
    {"name": "S&P 500",            "ticker": "^GSPC",     "tier": "US Index",       "rec": "HIGH VOLATILITY", "pip_scale": 1.0},
    {"name": "NASDAQ 100",         "ticker": "^NDX",      "tier": "US Index",       "rec": "HIGH VOLATILITY", "pip_scale": 1.0},
    {"name": "DOW JONES",          "ticker": "^DJI",      "tier": "US Index",       "rec": "HIGH VOLATILITY", "pip_scale": 1.0},
    {"name": "RUSSELL 2000",       "ticker": "^RUT",      "tier": "US Index",       "rec": "HIGH VOLATILITY", "pip_scale": 1.0},
    {"name": "DAX (GERMANY)",      "ticker": "^GDAXI",    "tier": "EU Index",       "rec": "MODERATE",        "pip_scale": 1.0},
    {"name": "FTSE 100 (UK)",      "ticker": "^FTSE",     "tier": "EU Index",       "rec": "MODERATE",        "pip_scale": 1.0},
    {"name": "CAC 40 (FRANCE)",    "ticker": "^FCHI",     "tier": "EU Index",       "rec": "MODERATE",        "pip_scale": 1.0},
    {"name": "EURO STOXX 50",      "ticker": "^STOXX50E", "tier": "EU Index",       "rec": "MODERATE",        "pip_scale": 1.0},
    {"name": "SMI (SWITZERLAND)",  "ticker": "^SSMI",     "tier": "EU Index",       "rec": "MODERATE",        "pip_scale": 1.0},
    {"name": "AEX (NETHERLANDS)",  "ticker": "^AEX",      "tier": "EU Index",       "rec": "MODERATE",        "pip_scale": 0.1},
    {"name": "IBEX 35 (SPAIN)",    "ticker": "^IBEX",     "tier": "EU Index",       "rec": "MODERATE",        "pip_scale": 1.0},
    {"name": "NIKKEI 225 (JP)",    "ticker": "^N225",     "tier": "Asia Index",     "rec": "MODERATE",        "pip_scale": 10.0},
    {"name": "HANG SENG (HK)",     "ticker": "^HSI",      "tier": "Asia Index",     "rec": "MODERATE",        "pip_scale": 1.0},
    {"name": "ASX 200 (AUS)",      "ticker": "^AXJO",     "tier": "Asia Index",     "rec": "MODERATE",        "pip_scale": 1.0},
    {"name": "KOSPI (S.KOREA)",    "ticker": "^KS11",     "tier": "Asia Index",     "rec": "MODERATE",        "pip_scale": 1.0},
    {"name": "NIFTY 50 (INDIA)",   "ticker": "^NSEI",     "tier": "Asia Index",     "rec": "MODERATE",        "pip_scale": 1.0},
    {"name": "SENSEX (INDIA)",     "ticker": "^BSESN",    "tier": "Asia Index",     "rec": "MODERATE",        "pip_scale": 10.0},
    {"name": "TSX (CANADA)",       "ticker": "^GSPTSE",   "tier": "Americas Index", "rec": "MODERATE",        "pip_scale": 1.0},
    {"name": "BOVESPA (BRAZIL)",   "ticker": "^BVSP",     "tier": "Americas Index", "rec": "MODERATE",        "pip_scale": 10.0},
    {"name": "MXX (MEXICO)",       "ticker": "^MXX",      "tier": "Americas Index", "rec": "MODERATE",        "pip_scale": 1.0},
]

# ─── Cryptocurrency ───────────────────────────────────────────────────────────

CRYPTO: List[Dict] = [
    {"name": "BITCOIN (BTC)",        "ticker": "BTC-USD",  "tier": "Crypto", "rec": "HIGH VOLATILITY — Crypto", "pip_scale": 1.0},
    {"name": "ETHEREUM (ETH)",       "ticker": "ETH-USD",  "tier": "Crypto", "rec": "HIGH VOLATILITY — Crypto", "pip_scale": 0.1},
    {"name": "BNB",                  "ticker": "BNB-USD",  "tier": "Crypto", "rec": "HIGH VOLATILITY — Crypto", "pip_scale": 0.1},
    {"name": "XRP",                  "ticker": "XRP-USD",  "tier": "Crypto", "rec": "HIGH VOLATILITY — Crypto", "pip_scale": 0.0001},
    {"name": "SOLANA (SOL)",         "ticker": "SOL-USD",  "tier": "Crypto", "rec": "HIGH VOLATILITY — Crypto", "pip_scale": 0.01},
    {"name": "CARDANO (ADA)",        "ticker": "ADA-USD",  "tier": "Crypto", "rec": "HIGH VOLATILITY — Crypto", "pip_scale": 0.0001},
    {"name": "DOGECOIN (DOGE)",      "ticker": "DOGE-USD", "tier": "Crypto", "rec": "HIGH VOLATILITY — Crypto", "pip_scale": 0.00001},
    {"name": "AVALANCHE (AVAX)",     "ticker": "AVAX-USD", "tier": "Crypto", "rec": "HIGH VOLATILITY — Crypto", "pip_scale": 0.01},
    {"name": "CHAINLINK (LINK)",     "ticker": "LINK-USD", "tier": "Crypto", "rec": "HIGH VOLATILITY — Crypto", "pip_scale": 0.01},
    {"name": "POLKADOT (DOT)",       "ticker": "DOT-USD",  "tier": "Crypto", "rec": "HIGH VOLATILITY — Crypto", "pip_scale": 0.001},
    {"name": "UNISWAP (UNI)",        "ticker": "UNI-USD",  "tier": "Crypto", "rec": "HIGH VOLATILITY — Crypto", "pip_scale": 0.001},
    {"name": "LITECOIN (LTC)",       "ticker": "LTC-USD",  "tier": "Crypto", "rec": "HIGH VOLATILITY — Crypto", "pip_scale": 0.01},
    {"name": "COSMOS (ATOM)",        "ticker": "ATOM-USD", "tier": "Crypto", "rec": "HIGH VOLATILITY — Crypto", "pip_scale": 0.001},
    {"name": "STELLAR (XLM)",        "ticker": "XLM-USD",  "tier": "Crypto", "rec": "HIGH VOLATILITY — Crypto", "pip_scale": 0.00001},
    {"name": "NEAR PROTOCOL",        "ticker": "NEAR-USD", "tier": "Crypto", "rec": "HIGH VOLATILITY — Crypto", "pip_scale": 0.001},
    {"name": "APTOS (APT)",          "ticker": "APT-USD",  "tier": "Crypto", "rec": "HIGH VOLATILITY — Crypto", "pip_scale": 0.001},
    {"name": "ARBITRUM (ARB)",       "ticker": "ARB-USD",  "tier": "Crypto", "rec": "HIGH VOLATILITY — Crypto", "pip_scale": 0.0001},
    {"name": "FILECOIN (FIL)",       "ticker": "FIL-USD",  "tier": "Crypto", "rec": "HIGH VOLATILITY — Crypto", "pip_scale": 0.001},
    {"name": "POLYGON (MATIC)",      "ticker": "MATIC-USD","tier": "Crypto", "rec": "HIGH VOLATILITY — Crypto", "pip_scale": 0.0001},
    {"name": "SHIBA INU (SHIB)",     "ticker": "SHIB-USD", "tier": "Crypto", "rec": "HIGH VOLATILITY — Crypto", "pip_scale": 0.00000001},
]

# ─── US Stocks — S&P 500 ─────────────────────────────────────────────────────
# Organized by GICS sector. All are yfinance-compatible tickers.

_SP500_TICKERS: List[str] = [
    # ── Information Technology ──────────────────────────────────────────────
    "AAPL", "MSFT", "NVDA", "AVGO", "ORCL", "CSCO", "ACN", "IBM", "TXN", "QCOM",
    "AMAT", "ADBE", "CRM", "NOW", "INTU", "ADI", "MU", "KLAC", "LRCX", "SNPS",
    "CDNS", "ANSS", "MCHP", "NXPI", "TEL", "MSI", "KEYS", "HPQ", "GLW", "STX",
    "WDC", "NTAP", "HPE", "CDW", "ZBRA", "AKAM", "VRSN", "GEN", "CTSH", "LDOS",
    "SAIC", "FSLR", "ENPH", "PLTR", "APP", "CRWD", "PANW", "FTNT", "AMD", "INTC",
    "UBER", "DDOG", "SNOW", "NET", "OKTA", "ZS", "FISV", "FIS", "GPN", "WU",
    "PYPL", "SQ", "GDDY", "EPAM", "PAYC", "PCTY", "JKHY", "WEX", "COIN",

    # ── Healthcare ──────────────────────────────────────────────────────────
    "UNH", "LLY", "JNJ", "ABBV", "MRK", "TMO", "ABT", "DHR", "AMGN", "GILD",
    "VRTX", "MDT", "BSX", "SYK", "ELV", "REGN", "ZTS", "ISRG", "HCA", "IDXX",
    "IQV", "DXCM", "EW", "BDX", "MCK", "A", "HUM", "MOH", "BIIB", "MRNA",
    "HOLX", "RMD", "MTD", "COO", "PODD", "INCY", "CVS", "WBA", "CNC", "ALGN",
    "ILMN", "WAT", "TECH", "STE", "TFX", "MASI", "MMSI", "HAE", "BIO", "PKI",
    "HSIC", "XRAY", "PDCO",

    # ── Financials ──────────────────────────────────────────────────────────
    "JPM", "BAC", "WFC", "GS", "MS", "BX", "BLK", "CB", "PGR", "SPGI",
    "MCO", "SCHW", "AXP", "USB", "COF", "TFC", "STT", "FITB", "HBAN", "RF",
    "MTB", "CFG", "KEY", "CMA", "AIG", "AFL", "MET", "PRU", "TRV", "ALL",
    "PFG", "AMP", "NDAQ", "ICE", "CME", "CBOE", "TROW", "BEN", "IVZ", "WTW",
    "AON", "MMC", "AJG", "ACGL", "HIG", "WRB", "CINF", "DFS", "SYF", "ALLY",
    "OMF", "SLM", "CACC", "FCNCA",

    # ── Consumer Discretionary ──────────────────────────────────────────────
    "AMZN", "TSLA", "HD", "BKNG", "MCD", "NKE", "LOW", "TJX", "SBUX", "CMG",
    "ORLY", "MAR", "HLT", "ABNB", "ROST", "GM", "F", "TGT", "EBAY", "BBY",
    "NVR", "DHI", "PHM", "LEN", "WYNN", "MGM", "CZR", "VFC", "RL", "TPR",
    "PVH", "HAS", "MHK", "WHR", "NCLH", "CCL", "RCL", "AAL", "DAL", "UAL",
    "LUV", "ULTA", "POOL", "DECK", "SKX", "LULU", "RH", "CVNA", "KMX",
    "AZO", "DLTR", "DG", "FIVE", "YUM", "DPZ", "DRI", "EAT", "CAKE", "TXRH",

    # ── Consumer Staples ────────────────────────────────────────────────────
    "WMT", "PG", "KO", "PEP", "PM", "MO", "CL", "MDLZ", "KMB", "GIS",
    "KHC", "KR", "SYY", "ADM", "MNST", "KDP", "CAG", "SJM", "CPB", "HRL",
    "MKC", "TSN", "K", "POST", "CALM", "LW", "FLO", "CLX", "CHD", "EL",

    # ── Energy ──────────────────────────────────────────────────────────────
    "XOM", "CVX", "COP", "EOG", "OXY", "SLB", "MPC", "VLO", "PSX", "HES",
    "DVN", "FANG", "HAL", "BKR", "OKE", "WMB", "KMI", "LNG", "TRGP",
    "SWN", "RRC", "AR", "EQT", "CTRA", "MRO",

    # ── Industrials ─────────────────────────────────────────────────────────
    "GE", "CAT", "HON", "DE", "RTX", "NOC", "LHX", "GD", "EMR", "ETN",
    "ITW", "ROK", "PH", "CARR", "PCAR", "CTAS", "CMI", "TT", "FAST", "WM",
    "RSG", "URI", "EXPD", "NSC", "CSX", "UNP", "FDX", "UPS", "JBHT", "WAB",
    "XPO", "SAIA", "ODFL", "CHRW", "LSTR", "GXO", "RXO", "IR", "PWR", "MTZ",
    "TDG", "HEI", "HII", "TDY", "CW", "KTOS", "BAH", "CACI",

    # ── Materials ───────────────────────────────────────────────────────────
    "LIN", "APD", "ECL", "PPG", "SHW", "NEM", "FCX", "NUE", "STLD", "CF",
    "MOS", "FMC", "DD", "DOW", "LYB", "EMN", "RPM", "AVY", "PKG", "WRK",
    "SEE", "BALL", "MLM", "VMC",

    # ── Real Estate ─────────────────────────────────────────────────────────
    "PLD", "EQIX", "CCI", "DLR", "SPG", "AMT", "PSA", "WELL", "VTR", "ESS",
    "AVB", "EQR", "MAA", "UDR", "CPT", "EXR", "CUBE", "ARE", "BXP", "VNO",
    "KIM", "O", "NNN", "ADC", "IRM", "REXR", "COLD", "STAG", "TRNO",

    # ── Utilities ───────────────────────────────────────────────────────────
    "NEE", "SO", "DUK", "D", "SRE", "AEE", "ETR", "WEC", "EXC", "PEG",
    "ED", "ES", "XEL", "PPL", "EIX", "FE", "CMS", "LNT", "PNW", "NI",
    "EVRG", "AES", "ATO", "NRG", "CNP", "OGE",

    # ── Communication Services ──────────────────────────────────────────────
    "GOOGL", "GOOG", "META", "NFLX", "DIS", "CMCSA", "T", "VZ", "TMUS", "EA",
    "TTWO", "MTCH", "FOXA", "FOX", "OMC", "IPG", "WBD", "PARA", "SIRI", "LYV",
    "NWSA", "NWS", "IAC",
]


def _stocks_to_watchlist(tickers: List[str], max_count: int) -> List[Dict]:
    """Convert a flat list of stock tickers to standardised watchlist dicts."""
    return [
        {
            "name": ticker,
            "ticker": ticker,
            "tier": "US Stock (S&P 500)",
            "rec": "MODERATE — Equity",
            "pip_scale": 0.01,   # 1 cent per pip (adjusted per-price in scanner display)
        }
        for ticker in tickers[:max_count]
    ]


def build_full_watchlist(
    include_forex: bool = True,
    include_metals: bool = True,
    include_energy: bool = True,
    include_indices: bool = True,
    include_crypto: bool = False,
    include_stocks: bool = False,
    max_stocks: int = 500,
) -> List[Dict]:
    """
    Builds and returns the complete merged watchlist based on category flags.
    Order: Forex Majors → Minors → Exotics → Metals → Energy → Indices → Crypto → Stocks.
    """
    watchlist: List[Dict] = []

    if include_forex:
        watchlist += FOREX_MAJORS
        watchlist += FOREX_MINORS
        watchlist += FOREX_EXOTICS

    if include_metals:
        watchlist += METALS

    if include_energy:
        watchlist += ENERGY

    if include_indices:
        watchlist += INDICES

    if include_crypto:
        watchlist += CRYPTO

    if include_stocks:
        watchlist += _stocks_to_watchlist(_SP500_TICKERS, max_count=max_stocks)

    return watchlist


def get_watchlist_summary(watchlist: List[Dict]) -> str:
    """Returns a human-readable summary of the watchlist composition by tier."""
    from collections import Counter
    counts = Counter(p["tier"] for p in watchlist)
    parts = [f"{tier}: {count}" for tier, count in sorted(counts.items())]
    return f"Total: {len(watchlist)} symbols | " + " | ".join(parts)
