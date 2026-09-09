import pandas as pd
import json

def add_sp500():
    import requests
    print("Fetching S&P 500 list from Wikipedia...")
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    headers = {'User-Agent': 'Mozilla/5.0'}
    html = requests.get(url, headers=headers).text
    table = pd.read_html(html)
    df = table[0]
    tickers = df['Symbol'].tolist()
    names = df['Security'].tolist()

    with open('config/watchlist.json', 'r') as f:
        watchlist = json.load(f)

    existing_tickers = {item['ticker'] for item in watchlist}
    added = 0

    for ticker, name in zip(tickers, names):
        # Yahoo Finance uses '-' instead of '.' for classes (e.g. BRK.B -> BRK-B)
        y_ticker = ticker.replace('.', '-')
        
        if y_ticker not in existing_tickers:
            watchlist.append({
                "name": name,
                "ticker": y_ticker,
                "tier": "Tier 5: S&P 500 Stock",
                "rec": "MODERATE"
            })
            added += 1

    with open('config/watchlist.json', 'w') as f:
        json.dump(watchlist, f, indent=4)

    print(f"Successfully added {added} S&P 500 stocks to the watchlist!")
    print(f"Total symbols in watchlist is now: {len(watchlist)}")

if __name__ == '__main__':
    add_sp500()
