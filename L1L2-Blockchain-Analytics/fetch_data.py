import requests
import pandas as pd

# Example base URLs for CoinGecko and DefiLlama APIs
COINGECKO_API = 'https://api.coingecko.com/api/v3'
DEFI_LLAMA_API = 'https://api.llama.fi'

# Function to fetch market capitalization and volume data for top 20 L1/L2
def fetch_market_data():
    url = f'{COINGECKO_API}/coins/markets'
    params = {
        'vs_currency': 'usd',
        'order': 'market_cap_desc',
        'per_page': 20,
        'page': 1
    }
    response = requests.get(url, params=params)
    return response.json()

# Function to fetch historical DEX volume for the top 20 L1/L2s
def fetch_dex_volume(coin_id, days=730):
    url = f'{COINGECKO_API}/coins/{coin_id}/market_chart'
    params = {'vs_currency': 'usd', 'days': days}
    response = requests.get(url, params=params)
    return response.json()

# Function to fetch TVL data for Aptos and other chains
def fetch_tvl_data():
    response = requests.get(f'{DEFI_LLAMA_API}/chains')
    return response.json()

# Function to save data to a CSV file
def save_to_csv(data, filename):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"Data has been saved to {filename}")

# Fetch and store market data to CSV
def fetch_and_store_market_data():
    market_data = fetch_market_data()

    # Process data for CSV format
    data_for_csv = []
    for coin in market_data:
        data_for_csv.append({
            'id': coin['id'],
            'name': coin['name'],
            'symbol': coin['symbol'],
            'market_cap': coin.get('market_cap', None),
            'total_volume': coin.get('total_volume', None),
            'price': coin.get('current_price', None),
            'circulating_supply': coin.get('circulating_supply', None)
        })
    
    # Save to CSV
    save_to_csv(data_for_csv, 'market_data.csv')

# Fetch and store TVL data to CSV
def fetch_and_store_tvl_data():
    tvl_data = fetch_tvl_data()

    # Process TVL data for CSV
    data_for_csv = []
    for chain in tvl_data:
        data_for_csv.append({
            'name': chain['name'],
            'tvl': chain.get('tvl', None),
            'symbol': chain.get('symbol', None)
        })
    
    # Save to CSV
    save_to_csv(data_for_csv, 'tvl_data.csv')

# Example use
if __name__ == "__main__":
    fetch_and_store_market_data()   # Save market data to 'market_data.csv'
    fetch_and_store_tvl_data()      # Save TVL data to 'tvl_data.csv'
