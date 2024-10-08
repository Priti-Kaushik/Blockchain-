
from solana.rpc.api import Client

# Initialize Solana JSON RPC client
client = Client("https://api.mainnet-beta.solana.com")

def get_validator_count():
    # Get current vote accounts (validators)
    vote_accounts = client.get_vote_accounts()
    
    # Extract the active validators count from the response
    active_validators_count = len(vote_accounts.value.current)
    
    return active_validators_count

# Get the number of active validators
validators_count = get_validator_count()

# Print the validator count
print(f"Validator Count: {validators_count}")

