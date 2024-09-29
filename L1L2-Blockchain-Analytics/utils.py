import requests

# Utility function to handle API requests with retries
def fetch_data_from_api(url, params=None):
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

# Function to convert timestamps to readable dates
def convert_timestamp_to_date(timestamp):
    return pd.to_datetime(timestamp, unit='s').date()

# Example use
if __name__ == "__main__":
    url = 'https://api.coingecko.com/api/v3/coins/markets'
    params = {'vs_currency': 'usd', 'order': 'market_cap_desc'}
    data = fetch_data_from_api(url, params)
    print(data[:2])  # Preview first two entries

