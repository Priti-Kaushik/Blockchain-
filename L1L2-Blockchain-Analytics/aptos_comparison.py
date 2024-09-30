import requests
import pandas as pd
import matplotlib.pyplot as plt
import time
from functools import reduce

def get_top_chains_by_tvl(limit=20):
    url = 'https://api.llama.fi/chains'
    response = requests.get(url)
    data = response.json()
    # Convert to DataFrame
    df = pd.DataFrame(data)
    # Sort by TVL
    df.sort_values('tvl', ascending=False, inplace=True)
    # Exclude 'Aptos' as we will add it manually
    df = df[df['name'] != 'Aptos']
    # Select top chains
    top_chains = df.head(limit)['name'].tolist()
    return top_chains

top_chains = get_top_chains_by_tvl()
chains = ['Aptos'] + top_chains

def get_historical_tvl(chain_name):
    url = f'https://api.llama.fi/charts/{chain_name}'
    print(f"Fetching TVL data for {chain_name} from URL: {url}")
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error fetching TVL data for {chain_name}: {response.status_code} - {response.text}")
        return pd.DataFrame()
    data = response.json()
    if data:
        df = pd.DataFrame(data)
        # Ensure 'date' is numeric before conversion
        df['date'] = pd.to_numeric(df['date'], errors='coerce')
        df['date'] = pd.to_datetime(df['date'], unit='s')
        df = df[['date', 'totalLiquidityUSD']]
        df = df.rename(columns={'totalLiquidityUSD': 'tvl'})
        return df
    else:
        print(f"No TVL data available for {chain_name}")
        return pd.DataFrame()

def get_historical_dex_volume(chain_name):
    url = f'https://api.llama.fi/overview/dexs/{chain_name}?excludeTotalDataChart=false&dataType=dailyVolume'
    print(f"Fetching DEX volume data for {chain_name} from URL: {url}")
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error fetching DEX volume data for {chain_name}: {response.status_code} - {response.text}")
            return pd.DataFrame()
        data = response.json()
        if 'totalDataChart' in data and data['totalDataChart']:
            # totalDataChart is a list of [timestamp, value] pairs
            df = pd.DataFrame(data['totalDataChart'], columns=['timestamp', 'dex_volume'])
            df['timestamp'] = pd.to_numeric(df['timestamp'], errors='coerce')
            df['date'] = pd.to_datetime(df['timestamp'], unit='s')
            df = df[['date', 'dex_volume']]
            return df
        else:
            print(f"No DEX volume data available for {chain_name}")
            return pd.DataFrame()
    except Exception as e:
        print(f"Exception occurred while fetching DEX volume data for {chain_name}: {e}")
        return pd.DataFrame()

def collect_and_adjust_data(chain_name):
    # Fetch data
    tvl_df = get_historical_tvl(chain_name)
    dex_volume_df = get_historical_dex_volume(chain_name)
    
    # Merge data on date
    dfs = [tvl_df, dex_volume_df]
    dfs = [df for df in dfs if not df.empty]
    
    if not dfs:
        print(f"No data available for {chain_name}")
        return pd.DataFrame()
    
    # Merge all DataFrames on 'date'
    df = reduce(lambda left, right: pd.merge(left, right, on='date', how='outer'), dfs)
    
    # Sort by date
    df.sort_values('date', inplace=True)
    
    # Adjust time to t_0
    df['days_since_launch'] = (df['date'] - df['date'].iloc[0]).dt.days
    
    return df

# Update chain names to match API expectations
chain_mappings = {
    'Aptos': 'Aptos',
    'Ethereum': 'Ethereum',
    'Solana': 'Solana',
    'Tron': 'Tron',
    'Binance': 'BSC',
    'Arbitrum': 'Arbitrum',
    'Base': 'Base',
    'Avalanche': 'Avalanche',
    'Sui': 'Sui',
    'Blast': 'Blast',
    'Scroll': 'Scroll',
    'Polygon': 'Polygon',
    'Optimism': 'Optimism',
    'Linea': 'Linea',
    'TON': 'Ton',
    'Hyperliquid': 'Hyperliquid',
    'Bitcoin': 'Bitcoin',
    'Near': 'Near',
    'Cronos': 'Cronos',
    'Mantle': 'Mantle',
    'Mode': 'Mode',
}

chain_data = {}

for chain in chains:
    chain_api_name = chain_mappings.get(chain, chain)
    print(f"\nProcessing {chain} (API name: {chain_api_name})...")
    df_chain = collect_and_adjust_data(chain_api_name)
    if not df_chain.empty:
        chain_data[chain] = df_chain
    time.sleep(1)  # Respect API rate limits

# Plot TVL Comparison
plt.figure(figsize=(12, 6))

for chain, df in chain_data.items():
    if 'tvl' in df.columns:
        plt.plot(df['days_since_launch'], df['tvl'], label=chain)

plt.title('TVL Comparison (Time-Adjusted from t₀)')
plt.xlabel('Days Since Launch')
plt.ylabel('Total Value Locked (USD)')
plt.legend()
plt.tight_layout()
plt.show()

# Plot DEX Volume Comparison
plt.figure(figsize=(12, 6))

for chain, df in chain_data.items():
    if 'dex_volume' in df.columns:
        plt.plot(df['days_since_launch'], df['dex_volume'].rolling(window=7).mean(), label=chain)

plt.title('DEX Volume Comparison (7-Day Moving Average, Time-Adjusted from t₀)')
plt.xlabel('Days Since Launch')
plt.ylabel('DEX Volume (USD)')
plt.legend()
plt.tight_layout()
plt.show()
