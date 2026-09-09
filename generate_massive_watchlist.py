import json
import urllib.request
import os

def generate_watchlist():
    watchlist = []

    print("Building Forex combinations...")
    currencies = [
        "USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "NZD", 
        "ZAR", "TRY", "MXN", "SGD", "HKD", "NOK", "SEK", "DKK", 
        "PLN", "HUF", "CZK", "THB", "ILS", "RUB", "CNH"
    ]
    for base in currencies:
        for quote in currencies:
            if base != quote:
                watchlist.append({
                    "name": f"{base}/{quote}",
                    "ticker": f"{base}{quote}=X",
                    "tier": "Tier 1: Forex",
                    "rec": "AUTOMATED"
                })

    print("Adding Metals and Commodities...")
    metals = {
        "Gold (XAU/USD)": "GC=F", 
        "Silver (XAG/USD)": "SI=F", 
        "Platinum": "PL=F", 
        "Palladium": "PA=F", 
        "Copper": "HG=F",
        "WTI Crude Oil": "CL=F",
        "Brent Crude Oil": "BZ=F",
        "Natural Gas": "NG=F"
    }
    for name, ticker in metals.items():
        watchlist.append({"name": name, "ticker": ticker, "tier": "Tier 2: Metal / Commodity", "rec": "AUTOMATED"})

    print("Adding Global Indices...")
    indices = {
        "NASDAQ 100": "^NDX", 
        "DOW JONES 30": "^DJI", 
        "S&P 500": "^GSPC", 
        "Russell 2000": "^RUT", 
        "VIX Volatility": "^VIX",
        "UK 100 (FTSE)": "^FTSE", 
        "German 40 (DAX)": "^GDAXI",
        "France 40 (CAC)": "^FCHI",
        "Euro Stoxx 50": "^STOXX50E",
        "Japan 225 (Nikkei)": "^N225",
        "Hong Kong (HSI)": "^HSI",
        "Australia 200 (ASX)": "^AXJO"
    }
    for name, ticker in indices.items():
        watchlist.append({"name": name, "ticker": ticker, "tier": "Tier 3: Index", "rec": "AUTOMATED"})

    print("Fetching ~11,000+ US Stocks from SEC public database...")
    try:
        req = urllib.request.Request(
            "https://www.sec.gov/files/company_tickers.json", 
            headers={'User-Agent': 'TradingBot/1.0 (contact@example.com)'}
        )
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            for key, item in data.items():
                ticker = item['ticker']
                # Format for Yahoo Finance (e.g. BRK.B -> BRK-B)
                y_ticker = ticker.replace('.', '-')
                watchlist.append({
                    "name": item['title'],
                    "ticker": y_ticker,
                    "tier": "Tier 4: US Stock",
                    "rec": "AUTOMATED"
                })
    except Exception as e:
        print(f"Error fetching US Stocks: {e}")

    # Ensure config directory exists
    os.makedirs('config', exist_ok=True)
    
    with open('config/watchlist.json', 'w') as f:
        json.dump(watchlist, f, indent=4)

    print(f"\n[+] Successfully generated watchlist with {len(watchlist):,} total symbols!")

if __name__ == '__main__':
    generate_watchlist()
