import pandas as pd
import matplotlib.pyplot as plt
from fetch_data import fetch_market_data, fetch_dex_volume

# Function to calculate market cap to DEX volume ratio
def calculate_marketcap_dex_ratio():
    market_data = fetch_market_data()
    
    ratios = []
    for coin in market_data:
        coin_id = coin['id']
        dex_volume_data = fetch_dex_volume(coin_id)

        # Ensure both market cap and volume data are present
        if dex_volume_data and coin['market_cap']:
            market_cap = coin['market_cap']
            total_volume = dex_volume_data['total_volumes'][-1][1]  # Latest DEX volume

            if total_volume > 0:
                ratio = market_cap / total_volume
                ratios.append({
                    'id': coin_id,
                    'market_cap': market_cap,
                    'dex_volume': total_volume,
                    'ratio': ratio
                })
    
    return pd.DataFrame(ratios)

# Function to calculate 7-day moving average
def calculate_moving_average(df):
    df['7d_avg_ratio'] = df['ratio'].rolling(window=7).mean()
    return df

# Example plotting function
def plot_marketcap_dex_ratio(df):
    plt.figure(figsize=(10, 6))
    for coin in df['id'].unique():
        coin_data = df[df['id'] == coin]
        plt.plot(coin_data.index, coin_data['7d_avg_ratio'], label=coin)
    
    plt.title('7-Day Moving Average of Market Cap to DEX Volume Ratio')
    plt.xlabel('Date')
    plt.ylabel('7d Average Ratio')
    plt.legend()
    plt.show()

# Example use
if __name__ == "__main__":
    ratio_df = calculate_marketcap_dex_ratio()
    ratio_df = calculate_moving_average(ratio_df)
    plot_marketcap_dex_ratio(ratio_df)

