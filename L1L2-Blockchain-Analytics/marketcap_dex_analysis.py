import requests
from requests.exceptions import RequestException
import pandas as pd
import time
import matplotlib.pyplot as plt

def get_historical_market_cap(chain_id, days):
    if days > 365:
        days = 365  # Limit to 365 days due to API restrictions
    url = f'https://api.coingecko.com/api/v3/coins/{chain_id}/market_chart'
    params = {
        'vs_currency': 'usd',
        'days': days
    }
    print(f"Fetching market cap data from URL: {url} with params: {params}")
    try:
        response = requests.get(url, params=params)
        print(f"Response status code: {response.status_code}")
        if response.status_code != 200:
            print(f"Error fetching market cap data for {chain_id}: HTTP {response.status_code}")
            print(f"Response text: {response.text}")
            return pd.DataFrame()
        data = response.json()
        if 'market_caps' in data and data['market_caps']:
            market_caps = data['market_caps']
            df = pd.DataFrame(market_caps, columns=['timestamp', 'market_cap'])
            df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
            df = df[['date', 'market_cap']]
            return df
        else:
            print(f"No market cap data available for {chain_id}")
            return pd.DataFrame()
    except Exception as e:
        print(f"An error occurred for {chain_id}: {e}")
        return pd.DataFrame()



import requests
from requests.exceptions import RequestException
import pandas as pd
import time

def get_historical_dex_volume(chain_name, max_retries=3, base_delay=1):
    url = f"https://api.llama.fi/overview/dexs/{chain_name}"
    params = {
        'excludeTotalDataChart': 'false',
        'excludeTotalDataChartBreakdown': 'true',
        'dataType': 'dailyVolume'
    }
    
    for attempt in range(max_retries):
        try:
            print(f"Fetching DEX volume data for {chain_name} from URL: {url} (Attempt {attempt + 1}/{max_retries})")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if 'totalDataChart' in data and data['totalDataChart']:
                df = pd.DataFrame(data['totalDataChart'], columns=['date', 'dex_volume'])
                df['date'] = pd.to_datetime(df['date'], unit='s')
                return df
            else:
                print(f"No DEX volume data available for {chain_name}")
                return pd.DataFrame()
        
        except RequestException as e:
            print(f"Error fetching DEX volume data for {chain_name}: {e}")
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print(f"Max retries reached. Unable to fetch DEX volume data for {chain_name}")
                return pd.DataFrame()
        
        except Exception as e:
            print(f"An unexpected error occurred for {chain_name}: {e}")
            return pd.DataFrame()

    return pd.DataFrame()

chains = [
    {'name': 'Ethereum', 'coingecko_id': 'ethereum', 'defillama_name': 'Ethereum'},
    {'name': 'BSC', 'coingecko_id': 'binancecoin', 'defillama_name': 'BSC'},
    {'name': 'Polygon', 'coingecko_id': 'matic-network', 'defillama_name': 'Polygon'},
    {'name': 'Avalanche', 'coingecko_id': 'avalanche-2', 'defillama_name': 'Avalanche'},
    {'name': 'Fantom', 'coingecko_id': 'fantom', 'defillama_name': 'Fantom'},
    # Add more chains as needed
]

# Number of days (up to 365 due to API limits)
days = 365*2

for chain in chains:
    print(f"\nProcessing {chain['name']}...")
    print(f"Using CoinGecko ID: {chain['coingecko_id']}")
    print(f"Using DeFiLlama Name: {chain['defillama_name']}")

    # Fetch historical market cap data
    market_cap_df = get_historical_market_cap(chain['coingecko_id'], days)
    time.sleep(1)  # Respect rate limits

    # Fetch historical DEX volume data using the updated function
    dex_volume_df = get_historical_dex_volume(chain['defillama_name'])
    time.sleep(1)  # Respect rate limits

    if market_cap_df.empty:
        print(f"Market cap data not available for {chain['name']}. Skipping.")
        continue

    if dex_volume_df.empty:
        print(f"DEX volume data not available for {chain['name']}. Skipping.")
        continue

    # Merge data on date
    df = pd.merge(market_cap_df, dex_volume_df, on='date', how='inner')

    if df.empty:
        print(f"No overlapping dates for market cap and DEX volume data for {chain['name']}. Skipping.")
        continue

    # Ensure there are no zero or negative dex_volume values
    df = df[df['dex_volume'] > 0]

    if df.empty:
        print(f"No valid DEX volume data for {chain['name']} after filtering. Skipping.")
        continue

    # Calculate the ratio
    df['ratio'] = df['market_cap'] / df['dex_volume']

    # Compute 7-day moving average
    df.set_index('date', inplace=True)
    df.sort_index(inplace=True)
    df['ratio_7d_ma'] = df['ratio'].rolling(window=7).mean()

    # Plot the 7-day moving average ratio
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['ratio_7d_ma'], label=f"{chain['name']} 7-Day MA")
    plt.title(f"{chain['name']} Market Cap to DEX Volume Ratio (7-Day MA)")
    plt.xlabel('Date')
    plt.ylabel('Market Cap to DEX Volume Ratio')
    plt.legend()
    plt.tight_layout()
    plt.show()

    # Optionally, save the DataFrame to a CSV for further analysis
    df.to_csv(f"{chain['name']}_marketcap_dexvolume_ratio.csv")






import pandas as pd
import matplotlib.pyplot as plt

# List of chains (update this list based on your CSV files)
chains = ['Ethereum', 'BSC', 'Polygon', 'Avalanche', 'Fantom']

# Initialize an empty DataFrame to store combined data
combined_df = pd.DataFrame()

for chain in chains:
    # Read the CSV file for each chain
    df = pd.read_csv(f"{chain}_marketcap_dexvolume_ratio.csv", parse_dates=['date'], index_col='date')
    
    # Check if 'ratio_7d_ma' column exists; if not, use 'ratio'
    if 'ratio_7d_ma' in df.columns:
        ratio_column = 'ratio_7d_ma'
    else:
        ratio_column = 'ratio'
    
    # Select the ratio column and rename it to include the chain name
    df_chain = df[[ratio_column]].rename(columns={ratio_column: chain})
    
    # Merge with the combined DataFrame
    if combined_df.empty:
        combined_df = df_chain
    else:
        combined_df = combined_df.join(df_chain, how='outer')

# Sort the combined DataFrame by date
combined_df.sort_index(inplace=True)

# Optional: Save the combined data to a CSV file
combined_df.to_csv('Combined_MarketCap_DexVolume_Ratio.csv')




plt.figure(figsize=(14, 7))

for chain in chains:
    if chain in combined_df.columns:
        plt.plot(combined_df.index, combined_df[chain], label=chain)

plt.title("Market Cap to DEX Volume Ratio (7-Day MA) Across Chains")
plt.xlabel('Date')
plt.ylabel('Market Cap to DEX Volume Ratio')
plt.legend()
plt.tight_layout()
plt.show()




summary_stats = combined_df.describe()
print(summary_stats)




correlation_matrix = combined_df.corr()
print(correlation_matrix)




import seaborn as sns

plt.figure(figsize=(8, 6))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm')
plt.title('Correlation Matrix of Market Cap to DEX Volume Ratios')
plt.show()
