import pandas as pd
import numpy as np
from fetch_data import fetch_dex_volume, fetch_market_data

# Function to calculate 15-day correlation between each coin and Ethereum
def calculate_correlation_vs_eth():
    eth_data = fetch_dex_volume('ethereum')

    market_data = fetch_market_data()
    correlation_df = pd.DataFrame()

    # Calculate correlation of each coin with Ethereum
    for coin in market_data:
        coin_id = coin['id']
        dex_volume_data = fetch_dex_volume(coin_id)

        if dex_volume_data:
            coin_volumes = [data[1] for data in dex_volume_data['total_volumes']]
            eth_volumes = [data[1] for data in eth_data['total_volumes']]

            # Ensure lengths match
            if len(coin_volumes) == len(eth_volumes):
                correlation = pd.Series(coin_volumes).rolling(window=15).corr(pd.Series(eth_volumes))
                correlation_df[coin_id] = correlation

    return correlation_df

# Function to find tokens with the lowest correlation vs ETH
def find_lowest_correlation(correlation_df):
    min_correlations = correlation_df.min()
    lowest_corr_tokens = min_correlations.nsmallest(5)
    
    return lowest_corr_tokens

# Example use
if __name__ == "__main__":
    correlation_df = calculate_correlation_vs_eth()
    lowest_corr_tokens = find_lowest_correlation(correlation_df)

    print("Lowest Correlation Tokens vs ETH:", lowest_corr_tokens)

