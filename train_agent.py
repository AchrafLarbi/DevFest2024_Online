# train_agent.py
import os
import pandas as pd
import numpy as np
from stable_baselines3 import PPO
from bandwidth_env import BandwidthEnv  # Import the environment class

# Load your initial dataset
file_path = r"C:\Users\asus\OneDrive\Bureau\DevFest_RL\sorted.csv"
data = pd.read_csv(file_path)

# Initialize the BandwidthEnv environment
env = BandwidthEnv(data)

# Define and train the PPO agent
model = PPO("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=len(env.unique_intervals[0]))  # Adjust total_timesteps as needed

observations = np.array(env.observation_history)
output_data = []

# Loop through all observations to structure the output data correctly
for step_idx, observation in enumerate(env.observation_history):
    for user_idx in range(env.num_users):
        output_data.append({
            'DID': user_idx + 1,  # User ID starts from 1
            'Current_MIR': observation[user_idx, 0],  # Current MIR for the user
            'Requested_Bandwidth': observation[user_idx, 1],  # Bandwidth requested
            'Allocated_Bandwidth': observation[user_idx, 2],  # Bandwidth allocated
            'Abuse_Flag': observation[user_idx, 3]  # Abuse flag status
        })

# Convert to DataFrame for analysis
output_df = pd.DataFrame(output_data)

# Compute the Average Allocation Ratio while avoiding zero requested bandwidth values
output_df['Allocation_Ratio'] = np.where(
    output_df['Requested_Bandwidth'] != 0,
    output_df['Allocated_Bandwidth'] / output_df['Requested_Bandwidth'],
    np.nan  # Set as NaN where requested bandwidth is zero
)

# Calculate the mean allocation ratio, ignoring NaNs
average_allocation_ratio = output_df['Allocation_Ratio'].mean()

print("Average Allocation Ratio:", average_allocation_ratio)

output_directory = '/mnt/data'
output_csv_path = os.path.join(output_directory, 'output_observations.csv')

# Create the directory if it doesn't exist
os.makedirs(output_directory, exist_ok=True)

# Save the output DataFrame to a CSV file
output_df.to_csv(output_csv_path, index=False)
print(f"Output saved to {output_csv_path}")
