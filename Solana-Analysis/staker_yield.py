
import requests
import pandas as pd
from solana.rpc.api import Client
from solana.publickey import PublicKey

# Initialize Solana client
client = Client("https://api.mainnet-beta.solana.com")

def get_total_staked():
    """
    Fetches the total amount of SOL staked on the network.
    """
    response = client.get_vote_accounts()

    if response and hasattr(response, 'value'):
        current_validators = response.value.current
        total_staked = sum(
            validator.activated_stake for validator in current_validators
        )
        # Convert lamports to SOL
        total_staked_sol = total_staked / 1e9
        return total_staked_sol
    else:
        print("Failed to fetch vote accounts or 'value' attribute missing.")
        return 0

def estimate_rewards(apr, epochs, staked_amount):
    """
    Estimates rewards based on APR and number of epochs.
    
    :param apr: Annual Percentage Rate (e.g., 0.05 for 5%)
    :param epochs: Number of epochs
    :param staked_amount: Amount of SOL staked
    :return: Estimated rewards in SOL
    """
    # Solana has ~180 epochs per year (assuming 2 days per epoch)
    epochs_per_year = 180
    reward_per_epoch = (apr / epochs_per_year) * staked_amount
    total_rewards = reward_per_epoch * epochs
    return total_rewards

def get_staker_info(stake_account_address, apr=0.05, epochs=10):
    """
    Fetches staking information for a specific stake account and estimates rewards.
    
    :param stake_account_address: The stake account address of the staker
    :param apr: Annual Percentage Rate for reward estimation
    :param epochs: Number of epochs to estimate rewards for
    :return: Tuple of (staked_amount, estimated_rewards)
    """
    try:
        # Validate the public key format
        stake_pubkey = PublicKey(stake_account_address)
        
        # Fetch account info using the PublicKey object
        response = client.get_account_info(stake_pubkey, encoding="base64")
        
        # Check if the account exists
        if response.value is None:
            print("Stake account not found or inactive.")
            return 0, 0
        
        # Access the lamports and convert to SOL
        staked_amount_lamports = response.value.lamports
        staked_amount_sol = staked_amount_lamports / 1e9
        
        # Estimate rewards based on APR and number of epochs
        rewards_sol = estimate_rewards(apr, epochs, staked_amount_sol)
        
        return staked_amount_sol, rewards_sol
    except ValueError as ve:
        print(f"Invalid public key format: {ve}")
        return 0, 0
    except Exception as e:
        print(f"Error fetching staker info: {e}")
        return 0, 0




def compute_current_real_yield(staked_amount, rewards, fees=0):
    """
    Computes the current real yield.
    
    :param staked_amount: Amount of SOL staked
    :param rewards: Rewards earned in SOL
    :param fees: Fees in SOL
    :return: Yield percentage
    """
    if staked_amount <= 0:
        print("Staked amount is zero or negative. Cannot compute yield.")
        return 0
    net_rewards = rewards - fees
    yield_percent = (net_rewards / staked_amount) * 100
    return yield_percent

def compute_historical_real_yield(historical_rewards, historical_fees, staked_amount):
    """
    Computes the historical real yield.
    
    :param historical_rewards: Rewards earned in a past period (SOL)
    :param historical_fees: Fees in that period (SOL)
    :param staked_amount: Amount of SOL staked during that period
    :return: Historical yield percentage
    """
    if staked_amount <= 0:
        print("Historical staked amount is zero or negative. Cannot compute yield.")
        return 0
    net_rewards = historical_rewards - historical_fees
    historical_yield = (net_rewards / staked_amount) * 100
    return historical_yield

def main():
    # Fetch total staked SOL
    total_staked = get_total_staked()
    print(f"\nTotal Staked SOL: {total_staked} SOL")
    
    # Input your stake account address (updated from your snippet)
    staker_address = "6MBpP5Fm913JvCnw42JYEJeKEceu4K2kmSPCqY6Y1q8y"
    
    # Fetch staker info
    staked_amount, rewards = get_staker_info(staker_address, apr=0.05, epochs=10)
    print(f"Staked Amount: {staked_amount} SOL")
    print(f"Rewards Earned: {rewards} SOL")
    
    # Compute current real yield
    estimated_fees = 0.1  # Replace with actual or estimated fees
    current_yield = compute_current_real_yield(staked_amount, rewards, fees=estimated_fees)
    print(f"Current Real Yield: {current_yield:.2f}%")
    
    # Estimate historical real yield
    # Manual inputs based on historical data or estimations
    historical_rewards = 5.0    # SOL earned in a past epoch
    historical_fees = 0.2       # SOL fees in that epoch
    staked_amount_historical = 100.0  # SOL staked during that epoch
    
    historical_yield = compute_historical_real_yield(
        historical_rewards, historical_fees, staked_amount_historical
    )
    print(f"Historical Real Yield: {historical_yield:.2f}%")

if __name__ == "__main__":
    main()




