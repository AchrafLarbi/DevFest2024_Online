
import numpy as np
import pandas as pd

class BandwidthAllocation:
    def __init__(self, csv_path):
        # System constants
        self.TOTAL_BANDWIDTH = 10000
        self.MIN_BANDWIDTH = 1000
        self.NUM_USERS = 10
        
        # Reward calculation constants
        self.MAX_CAPACITY = 1000
        self.BETA = 3
        self.THETA = 0.2
        self.GAMMA = -0.5
        self.MIN_DURATION = 3
        
        # Load and prepare data
        self.rl_state = self.load_data(csv_path)
        self.N = len(self.rl_state['DID'].unique())
        self.T = len(self.rl_state['step'].unique())

    def load_data(self, csv_path):
        # Read the CSV file
        df = pd.read_csv(csv_path)
        
        # Convert user_id to string format like 'user_1'
        df['DID'] = 'user_' + df['user_id'].astype(str)
        
        # Ensure column names match the expected format
        if 'requested' in df.columns:
            df['BW_REQUESTED'] = df['requested']
        
        return df

    def allocation_efficiency_reward(self, data):
        total_efficiency = 0
        for _, row in data.iterrows():
            requested = row['BW_REQUESTED']
            allocated = row['allocated']
            mir = row['allocated']  # Using allocated as MIR since MIR is 0
            
            if requested >= mir:
                efficiency = mir / requested
            else:
                efficiency = 1
            
            total_efficiency += efficiency
        return total_efficiency / len(data)

    def over_allocation_penalty(self, data):
        total_allocated = data['allocated'].sum()
        over_penalty = 0
        
        if total_allocated > self.MAX_CAPACITY * self.NUM_USERS:
            overage = (total_allocated - self.MAX_CAPACITY * self.NUM_USERS) / (self.MAX_CAPACITY * self.NUM_USERS)
            over_penalty = self.BETA * overage
        
        return over_penalty

    def abusive_usage_penalty(self, data):
        abuse_penalty = 0
        abuse_scores = {}
        
        for user in data['DID'].unique():
            user_data = data[data['DID'] == user]
            abuse_count = 0
            abuse_score = 0
            
            for _, row in user_data.iterrows():
                requested = row['BW_REQUESTED']
                mir = row['allocated']  # Using allocated as MIR
                
                if requested > mir * (1 + self.THETA):
                    abuse_count += 1
                else:
                    if abuse_count >= self.MIN_DURATION:
                        abuse_score += abuse_count - self.MIN_DURATION
                    abuse_count = 0
            
            if abuse_count >= self.MIN_DURATION:
                abuse_score += abuse_count - self.MIN_DURATION
            
            abuse_scores[user] = abuse_score
        
        S_total = sum(abuse_scores.values())
        abuse_penalty = self.GAMMA * (S_total / (self.N * self.T))
        
        return abuse_penalty

    def calculate_step_rewards(self, step_number):
        step_data = self.rl_state[self.rl_state['step'] == step_number]
        
        R_efficiency = self.allocation_efficiency_reward(step_data)
        P_over = self.over_allocation_penalty(step_data)
        P_abusive = self.abusive_usage_penalty(step_data)
        
        # Total reward
        R_t = R_efficiency - P_over - P_abusive
        
        return R_efficiency, P_over, P_abusive, R_t


def main():
    # File path
    csv_path = r"D:\Users\pc\OneDrive\Documents\4cp\bandwidth_allocation_results.csv"
    
    # Create instance with CSV data
    allocator = BandwidthAllocation(csv_path)
    
    # Get unique steps from the data
    unique_steps = sorted(allocator.rl_state['step'].unique())
    
    # Calculate and display rewards for each step
    for step in unique_steps:
        R_efficiency, P_over, P_abusive, R_t = allocator.calculate_step_rewards(step)
        
        print(f"\nStep {step} Results:")
        print(f"Allocation Efficiency Reward (R_efficiency): {R_efficiency:.4f}")
        print(f"Over-allocation Penalty (P_over): {P_over:.4f}")
        print(f"Abusive Usage Penalty (P_abusive): {P_abusive:.4f}")
        print(f"Total Reward (R_t): {R_t:.4f}")
        
        # Print step statistics
        step_data = allocator.rl_state[allocator.rl_state['step'] == step]
        print(f"\nStep {step} Statistics:")
        print(f"Total Requested: {step_data['BW_REQUESTED'].sum()}")
        print(f"Total Allocated: {step_data['allocated'].sum()}")
        print(f"Remaining Bandwidth: {step_data['remaining_bandwidth'].iloc[0]}")
        print("-" * 40)

if __name__ == "__main__":
    main()