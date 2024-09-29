import pandas as pd
import matplotlib.pyplot as plt
from fetch_data import fetch_tvl_data, fetch_market_data, fetch_dex_volume

# Time-adjusted comparison of Aptos to top 20 L1/L2
def aptos_comparison():
    tvl_data = fetch_tvl_data()
    aptos_tvl = next((chain for chain in tvl_data if chain['name'] == 'Aptos'), None)

    # Fetch comparison data for the top 20 L1/L2
    market_data = fetch_market_data()
    
    comparison_df = pd.DataFrame()
    for coin in market_data:
        coin_id = coin['id']
        dex_volume_data = fetch_dex_volume(coin_id)
        
        if dex_volume_data:
            # Align data starting from t_0 (earliest common date)
            comparison_df[coin_id] = [data[1] for data in dex_volume_data['total_volumes']]
    
    # Compare Aptos with top 20
    comparison_df['aptos'] = [data['tvl'] for data in aptos_tvl['values']]
    
    return comparison_df

# Example plotting function
def plot_comparison(df):
    df.plot(figsize=(12, 6))
    plt.title('Aptos vs Top 20 L1/L2 Comparison (Time-Adjusted)')
    plt.xlabel('Days Since Launch')
    plt.ylabel('Metrics')
    plt.show()

# Example use
if __name__ == "__main__":
    comparison_df = aptos_comparison()
    plot_comparison(comparison_df)

