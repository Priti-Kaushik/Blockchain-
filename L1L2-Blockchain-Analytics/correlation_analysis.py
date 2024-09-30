import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
from datetime import datetime, timedelta

# Mapping from CoinGecko 'coin_id' to Yahoo Finance tickers
COINGECKO_TO_YAHOO_TICKER = {
    'ethereum': 'ETH-USD',
    'bitcoin': 'BTC-USD',
    'tether': 'USDT-USD',
    'binancecoin': 'BNB-USD',
    'solana': 'SOL-USD',
    'ripple': 'XRP-USD',
    'usd-coin': 'USDC-USD',
    'staked-ether': 'STETH-USD',  # May not be available on Yahoo Finance
    'dogecoin': 'DOGE-USD',
    'the-open-network': 'TON-USD',  # Assuming 'TON-USD' is available
    'cardano': 'ADA-USD',
    'tron': 'TRX-USD',
    'avalanche-2': 'AVAX-USD',
    'shiba-inu': 'SHIB-USD',
    'wrapped-bitcoin': 'WBTC-USD',
    'chainlink': 'LINK-USD',
    'weth': 'WETH-USD',
    'bitcoin-cash': 'BCH-USD',
    'polkadot': 'DOT-USD',
    'near': 'NEAR-USD'
    # Add more mappings as needed
}

def get_top_coins(limit=20):
    """
    Returns a list of top coins with their CoinGecko 'coin_id's.
    """
    # Predefined list of top coins excluding Ethereum
    top_coins = [
        {'id': 'bitcoin', 'symbol': 'btc', 'name': 'Bitcoin'},
        {'id': 'tether', 'symbol': 'usdt', 'name': 'Tether'},
        {'id': 'binancecoin', 'symbol': 'bnb', 'name': 'Binance Coin'},
        {'id': 'solana', 'symbol': 'sol', 'name': 'Solana'},
        {'id': 'ripple', 'symbol': 'xrp', 'name': 'XRP'},
        {'id': 'usd-coin', 'symbol': 'usdc', 'name': 'USD Coin'},
        {'id': 'dogecoin', 'symbol': 'doge', 'name': 'Dogecoin'},
        {'id': 'cardano', 'symbol': 'ada', 'name': 'Cardano'},
        {'id': 'tron', 'symbol': 'trx', 'name': 'TRON'},
        {'id': 'avalanche-2', 'symbol': 'avax', 'name': 'Avalanche'},
        {'id': 'shiba-inu', 'symbol': 'shib', 'name': 'Shiba Inu'},
        {'id': 'wrapped-bitcoin', 'symbol': 'wbtc', 'name': 'Wrapped Bitcoin'},
        {'id': 'chainlink', 'symbol': 'link', 'name': 'Chainlink'},
        {'id': 'weth', 'symbol': 'weth', 'name': 'Wrapped Ether'},
        {'id': 'bitcoin-cash', 'symbol': 'bch', 'name': 'Bitcoin Cash'},
        {'id': 'polkadot', 'symbol': 'dot', 'name': 'Polkadot'},
        {'id': 'near', 'symbol': 'near', 'name': 'NEAR Protocol'},
        {'id': 'the-open-network', 'symbol': 'ton', 'name': 'The Open Network'},
        {'id': 'staked-ether', 'symbol': 'steth', 'name': 'Staked Ether'},
        {'id': 'wrapped-steth', 'symbol': 'wsteth', 'name': 'Wrapped Staked Ether'}
    ]
    
    # Limit to the top 'limit' coins
    return top_coins[:limit]

def get_historical_price_data(ticker, period_days=730):
    """
    Fetch historical price data for a given ticker over a specified period.
    
    Parameters:
    - ticker (str): Yahoo Finance ticker symbol.
    - period_days (int): Number of days to fetch data for.
    
    Returns:
    - pd.DataFrame: DataFrame containing 'price' column indexed by date.
    """
    try:
        # Define the date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        # Fetch data
        df = yf.download(ticker, start=start_date, end=end_date)
        
        if df.empty:
            print(f"No price data for {ticker}")
            return pd.DataFrame()
        
        # Keep only the 'Close' price
        df = df[['Close']].rename(columns={'Close': 'price'})
        df.index = pd.to_datetime(df.index)
        return df
    except Exception as e:
        print(f"An error occurred while fetching data for {ticker}: {e}")
        return pd.DataFrame()

def compute_daily_returns(price_series):
    """
    Compute daily returns from price data.
    
    Parameters:
    - price_series (pd.Series): Series of prices indexed by date.
    
    Returns:
    - pd.Series: Series of daily returns.
    """
    return price_series.pct_change()

def compute_rolling_correlations(eth_returns, coin_returns, window=15):
    """
    Compute rolling correlations between ETH returns and a coin's returns.
    
    Parameters:
    - eth_returns (pd.Series): Ethereum's daily returns.
    - coin_returns (pd.Series): Coin's daily returns.
    - window (int): Rolling window size.
    
    Returns:
    - pd.Series: Rolling correlation series.
    """
    return eth_returns.rolling(window=window).corr(coin_returns)

def identify_low_correlation_periods(rolling_corr, threshold=0.2):
    """
    Identify periods where rolling correlation is below a threshold.
    
    Parameters:
    - rolling_corr (pd.Series): Rolling correlation series.
    - threshold (float): Correlation threshold.
    
    Returns:
    - pd.DataFrame: DataFrame with 'start', 'end', and 'duration' columns of low correlation periods.
    """
    low_corr = rolling_corr[rolling_corr < threshold]
    if low_corr.empty:
        return pd.DataFrame()
    
    # Sort by date to ensure chronological order
    low_corr_sorted = low_corr.sort_index()
    
    # Identify groups of consecutive low correlation days
    low_corr_groups = (low_corr_sorted.index.to_series().diff() != pd.Timedelta(days=1)).cumsum()
    
    # Initialize lists to store start, end, and duration
    start_dates = []
    end_dates = []
    durations = []
    
    for _, group in low_corr_sorted.groupby(low_corr_groups):
        start = group.index[0]
        end = group.index[-1]
        duration = (end - start).days + 1
        start_dates.append(start)
        end_dates.append(end)
        durations.append(duration)
    
    # Create the periods DataFrame
    periods_df = pd.DataFrame({
        'start': start_dates,
        'end': end_dates,
        'duration': durations
    })
    
    return periods_df

def calculate_relative_volatility(returns_df, periods_df, coin_id):
    """
    Calculate relative volatility of a coin compared to ETH during low correlation periods.
    
    Parameters:
    - returns_df (pd.DataFrame): DataFrame containing ETH and coin returns.
    - periods_df (pd.DataFrame): DataFrame with low correlation periods.
    - coin_id (str): The CoinGecko ID of the cryptocurrency.
    
    Returns:
    - List of dictionaries with volatility data.
    """
    volatilities = []
    for _, period in periods_df.iterrows():
        start_date = period['start']
        end_date = period['end']
        # Get returns during the period
        eth_returns_period = returns_df.loc[start_date:end_date, 'ethereum']
        coin_returns_period = returns_df.loc[start_date:end_date, coin_id]
        # Compute standard deviations
        eth_vol = eth_returns_period.std()
        coin_vol = coin_returns_period.std()
        # Compute relative volatility
        rel_vol = coin_vol / eth_vol if eth_vol != 0 else np.nan
        volatilities.append({
            'start': start_date.date(),
            'end': end_date.date(),
            'eth_volatility': eth_vol,
            'coin_volatility': coin_vol,
            'relative_volatility': rel_vol
        })
    return volatilities

# Main Execution
if __name__ == "__main__":
    # Step 1: Get Top Coins
    top_coins = get_top_coins()
    if not top_coins:
        print("Failed to retrieve top coins. Exiting.")
        exit()
    
    # Step 2: Fetch Historical Price Data
    days = 730  # Past 24 months
    coin_data = {}
    missing_tickers = []
    
    # Fetch data for ETH
    eth_ticker = COINGECKO_TO_YAHOO_TICKER.get('ethereum')
    if not eth_ticker:
        print("ETH ticker not found in mapping. Exiting.")
        exit()
    
    eth_df = get_historical_price_data(eth_ticker, days)
    if eth_df.empty:
        print("Failed to fetch ETH price data. Exiting.")
        exit()
    
    # Compute daily returns for ETH
    eth_returns = compute_daily_returns(eth_df['price'])
    
    # Fetch data for top coins
    for coin in top_coins:
        coin_id = coin['id']
        ticker = COINGECKO_TO_YAHOO_TICKER.get(coin_id)
        
        if not ticker:
            print(f"Ticker not found for {coin_id}. Skipping.")
            missing_tickers.append(coin_id)
            continue
        
        df = get_historical_price_data(ticker, days)
        if not df.empty:
            coin_data[coin_id] = df
        else:
            print(f"No data for {coin_id}")
        time.sleep(1)  # Respect API rate limits
    
    if not coin_data:
        print("No coin data fetched. Exiting.")
        exit()
    
    # Step 3: Compute Daily Returns for Each Coin
    coin_returns = {}
    for coin_id, df in coin_data.items():
        returns = compute_daily_returns(df['price'])
        coin_returns[coin_id] = returns
    
    # Step 4: Align Dates
    returns_df = pd.DataFrame(coin_returns)
    returns_df = returns_df.join(eth_returns.rename('ethereum'), how='inner')
    returns_df.dropna(inplace=True)
    
    if returns_df.empty:
        print("Combined returns DataFrame is empty. Exiting.")
        exit()
    
    # Step 5: Compute 15-Day Rolling Correlations
    rolling_window = 15
    rolling_correlations = {}
    
    for coin_id in coin_returns.keys():
        rolling_corr = compute_rolling_correlations(eth_returns, returns_df[coin_id], window=rolling_window)
        rolling_correlations[coin_id] = rolling_corr
    
    # Step 6: Compute Average Correlation
    average_correlations = {}
    for coin_id, corr_series in rolling_correlations.items():
        avg_corr = corr_series.mean()
        average_correlations[coin_id] = avg_corr
    
    # Sort coins by average correlation (ascending)
    sorted_correlations = sorted(average_correlations.items(), key=lambda x: x[1])
    
    # List tokens with lowest correlations (top 5)
    lowest_correlated_tokens = sorted_correlations[:5]
    
    print("\nTokens with the lowest average 15-day rolling correlation to ETH:")
    for coin_id, avg_corr in lowest_correlated_tokens:  # Corrected variable name
        print(f"{coin_id}: {avg_corr:.4f}")
    
    # Step 7: Identify Low Correlation Periods
    threshold = 0.2  # Define what 'low correlation' means
    low_corr_periods = {}
    
    for coin_id, corr_series in rolling_correlations.items():
        periods_df = identify_low_correlation_periods(corr_series, threshold=threshold)
        if not periods_df.empty:
            low_corr_periods[coin_id] = periods_df
    
    # Step 8: Print Low Correlation Periods
    for coin_id in [token[0] for token in lowest_correlated_tokens]:
        print(f"\nLow correlation periods for {coin_id}:")
        if coin_id in low_corr_periods:
            periods_df = low_corr_periods[coin_id]
            print(periods_df)  # Optional: Print the DataFrame for debugging
            for _, period in periods_df.iterrows():
                # Ensure that 'start', 'end', and 'duration' exist
                if 'start' in period and 'end' in period and 'duration' in period:
                    print(f"From {period['start']} to {period['end']} (Duration: {period['duration']} days)")
                else:
                    print("Error: Missing 'start', 'end', or 'duration' in period data.")
        else:
            print("No periods of low correlation found.")
    
    # Step 9: Calculate Relative Volatility
    relative_volatility = {}
    
    for coin_id in [token[0] for token in lowest_correlated_tokens]:
        if coin_id in low_corr_periods:
            periods_df = low_corr_periods[coin_id]
            vol_data = calculate_relative_volatility(returns_df, periods_df, coin_id)
            relative_volatility[coin_id] = vol_data
        else:
            print(f"\nNo low correlation periods found for {coin_id}. Skipping relative volatility calculation.")
    
    # Step 10: Compute ETH Volatility Over the Past 24 Months
    eth_volatility_full_period = eth_returns.std()
    print(f"\nETH volatility over the past 24 months: {eth_volatility_full_period:.4f}")
    
    # Step 11: Print Relative Volatility Data
    for coin_id, vol_data in relative_volatility.items():
        print(f"\nRelative volatility for {coin_id} during periods of low correlation:")
        for period in vol_data:
            print(f"From {period['start']} to {period['end']}:")
            print(f"  ETH Volatility: {period['eth_volatility']:.4f}")
            print(f"  {coin_id} Volatility: {period['coin_volatility']:.4f}")
            print(f"  Relative Volatility (Coin/ETH): {period['relative_volatility']:.2f}")
    
    # Step 12: Plot Rolling Correlations of Lowest Correlated Tokens
    for coin_id in [token[0] for token in lowest_correlated_tokens]:
        plt.figure(figsize=(12, 6))
        plt.plot(rolling_correlations[coin_id], label=f'{coin_id} vs ETH')
        plt.axhline(y=threshold, color='r', linestyle='--', label='Low Correlation Threshold')
        plt.title(f'15-Day Rolling Correlation between {coin_id} and ETH')
        plt.xlabel('Date')
        plt.ylabel('Correlation')
        plt.legend()
        plt.tight_layout()
        plt.show()
