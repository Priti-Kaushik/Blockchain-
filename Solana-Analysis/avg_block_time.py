from solana.rpc.api import Client
import time

# Initialize Solana JSON RPC client
client = Client("https://api.mainnet-beta.solana.com")

# Function to get 25 recent blocks
def get_recent_blocks():
    # Fetch the current slot (latest block)
    current_slot = client.get_slot().value
    
    # Get 25 blocks ending at the current slot
    blocks = client.get_blocks(current_slot - 25, current_slot).value
    
    return blocks

# Function to compute average block time
def compute_average_block_time(blocks):
    block_times = []
    
    # Fetch block time for each block, with a delay to avoid rate-limiting
    for block in blocks:
        block_time = client.get_block_time(block).value
        if block_time is not None:
            block_times.append(block_time)
        time.sleep(1)  # Delay of 1 second between requests to avoid rate limits

    # Ensure we have enough blocks to compute time differences
    if len(block_times) < 2:
        print("Not enough blocks to compute average block time.")
        return None
    
    # Calculate the time differences between consecutive blocks
    time_differences = [
        t2 - t1 for t1, t2 in zip(block_times[:-1], block_times[1:])
    ]
    
    # Compute average block time
    average_time = sum(time_differences) / len(time_differences)
    
    # Print average block time
    print(f"Average Block Time: {average_time:.2f} seconds")
    
    return average_time

# Example usage
# Fetch 25 recent blocks
recent_blocks = get_recent_blocks()

# Compute and print average block time
average_block_time = compute_average_block_time(recent_blocks)

