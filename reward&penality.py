import pandas as pd

# Sample data as a dictionary
data = {
    'DID': ['user_1', 'user_2', 'user_1', 'user_2'],
    'BW_REQUESTED': [1200, 800, 1300, 900],
    'abn': [0, 1, 1, 0],
    'time': ['00:00 - 00:05', '00:00 - 00:05', '00:05 - 00:10', '00:05 - 00:10'],
    'allocated': [1000, 800, 1000, 700],
    'mir': [1000, 800, 1000, 700]
}

# Convert dictionary to DataFrame
df = pd.DataFrame(data)

# Constants
MAX_CAPACITY = 1000  # System capacity in Kbps
BETA = 3  # Penalty coefficient for over-allocation
THETA = 0.2  # Threshold for abusive usage
GAMMA = -0.5  # Penalty coefficient for sustained abusive usage
MIN_DURATION = 3  # Minimum duration for abuse to count
N = len(df['DID'].unique())  # Total number of users
T = len(df['time'].unique())  # Total time steps

# Function to calculate allocation efficiency reward
def allocation_efficiency_reward(data):
    total_efficiency = 0
    for _, row in data.iterrows():
        requested = row['BW_REQUESTED']
        allocated = row['allocated']
        mir = row['mir']
        
        # Calculate efficiency based on requested and minimum guaranteed bandwidth (MIR)
        if requested >= mir:
            efficiency = mir / requested
        else:
            efficiency = 1  # Full satisfaction when requested bandwidth < MIR
        
        total_efficiency += efficiency

    # Return average efficiency over all requests
    return total_efficiency / len(data)

# Function to calculate over-allocation penalty
def over_allocation_penalty(data, max_capacity=MAX_CAPACITY, penalty_coefficient=BETA):
    total_allocated = data['allocated'].sum()  # Sum allocated bandwidth
    over_penalty = 0
    
    # Check if total allocation exceeds max capacity
    if total_allocated > max_capacity:
        overage = (total_allocated - max_capacity) / max_capacity  # Calculate overage ratio
        over_penalty = penalty_coefficient * overage  # Calculate penalty based on overage
    
    return over_penalty

# Function to calculate abusive usage penalty
def abusive_usage_penalty(data, abuse_threshold=THETA, min_duration=MIN_DURATION, penalty_coefficient=GAMMA):
    abuse_penalty = 0
    abuse_scores = {}
    
    # Evaluate abuse for each unique user
    for user in data['DID'].unique():
        user_data = data[data['DID'] == user]
        abuse_count = 0
        abuse_score = 0
        
        # Iterate through user data to detect abusive requests
        for _, row in user_data.iterrows():
            requested = row['BW_REQUESTED']
            mir = row['mir']
            
            # Check if the requested bandwidth is abusive
            if requested > mir * (1 + abuse_threshold):
                abuse_count += 1
            else:
                # Accumulate abuse score based on previous abuse counts
                if abuse_count >= min_duration:
                    abuse_score += abuse_count - min_duration
                abuse_count = 0  # Reset if not abusive
            
        # Final check at the end of user data
        if abuse_count >= min_duration:
            abuse_score += abuse_count - min_duration
            
        abuse_scores[user] = abuse_score  # Store abuse score for the user
    
    # Aggregate abuse scores and normalize
    S_total = sum(abuse_scores.values())
    abuse_penalty = penalty_coefficient * (S_total / (N * T))  # Normalize by total users and time steps
    
    return abuse_penalty

# Function to calculate and print each reward component
def calculate_rewards(data):
    R_efficiency = allocation_efficiency_reward(data)  # Calculate efficiency reward
    P_over = over_allocation_penalty(data)  # Calculate over-allocation penalty
    P_abusive = abusive_usage_penalty(data)  # Calculate abusive usage penalty
    
    # Total reward calculation
    R_t = R_efficiency - P_over - P_abusive

    return R_efficiency, P_over, P_abusive, R_t

# Group by time step and calculate rewards for each time step
results = []
for time_step, group in df.groupby('time'):
    R_efficiency, P_over, P_abusive, R_t = calculate_rewards(group)  # Calculate rewards for the group
    results.append((time_step, R_efficiency, P_over, P_abusive, R_t))  # Store results

# Display results for each time step
for result in results:
    time_step, R_efficiency, P_over, P_abusive, R_t = result
    print(f"Time Step: {time_step}")
    print("Allocation Efficiency Reward (R_efficiency):", R_efficiency)
    print("Over-Allocation Penalty (P_over):", P_over)
    print("Abusive Usage Penalty (P_abusive):", P_abusive)
    print("Total Reward (R_t):", R_t)
    print("-" * 40)
