# bandwidth_env.py
import numpy as np
import gymnasium as gym
from gymnasium import spaces
import pandas as pd

class BandwidthEnv(gym.Env):
    """Custom Gym environment for bandwidth allocation."""

    def __init__(self, data, theta=0.2, delta_t_min=3, gamma=0.5):
        super(BandwidthEnv, self).__init__()

        # Load the dataset and prepare unique intervals for time steps
        self.data = data
        self.unique_intervals = [self.data['Date'].unique()]
       
        self.num_users = data['DID'].nunique()  # Number of unique users
        self.delta_t_min = delta_t_min  # Minimum time intervals for abuse detection
        self.gamma = gamma  # Weight for penalty calculation
        self.theta = theta  # Threshold for abuse detection

        # Define observation and action spaces
        self.observation_space = spaces.Box(low=0, high=10_000, shape=(self.num_users, 4), dtype=np.float32)
        self.action_space = spaces.Box(low=1000, high=10_000, shape=(self.num_users,), dtype=np.float32)

        # Initialize state variables
        self.current_step = 0
        self.state = np.zeros((self.num_users, 4))  # Columns: [Current MIR, BW_requested, BW_allocated, Abuse Flag]
        self.abuse_counters = np.zeros(self.num_users)
        self.remaining_bandwidth = 10_000  # Total bandwidth pool in Kbps

        # To store history for analysis later
        self.observation_history = []
        self.time_history = []

    def reset(self, seed=None, options=None):
        """Reset the environment to an initial state."""
        super().reset(seed=seed)
        
        # Reset history and state for the first interval
        self.state = np.zeros((self.num_users, 4))
        self.abuse_counters = np.zeros(self.num_users)
        self.remaining_bandwidth = 10_000

        # Check and reset the current step if out of bounds
        if self.current_step >= len(self.unique_intervals[0]):
            print("Current step is out of bounds. Resetting to 0.")
            self.current_step = 0

        # Loop through each user to set initial states
        for i in range(self.num_users):
            user_data = self.data[
                (self.data['DID'] == 235009875 + i + 1) &
                (self.data['Date'] == self.unique_intervals[0][self.current_step])
            ]

            # Ensure data is available for the user at the current interval
            if not user_data.empty:
                self.state[i, 1] = user_data.iloc[0]['BW_REQUESTED']  # Requested BW
                self.state[i, 0] = 1000  # Initial Current MIR
                self.state[i, 2] = 0  # Initial Allocated BW
                self.state[i, 3] = 0  # Initial Abuse Flag
                self.time_history.append(str(user_data.iloc[0]['Date']))
            else:
                print(f"No data available for DID: {235009875 + i + 1} at interval {self.unique_intervals[0][self.current_step]}")

        return self.state, {}

    def step(self, action):
        """Execute one time step within the environment."""
        rewards, penalties, abuse_scores = [], [], []
        allocated_bandwidths = []
        
        # Phase 1: Allocate initial bandwidth per user
        for j in range(self.num_users):
            requested_bw = self.state[j, 1]
            allocated_bw = min(requested_bw, 1000)  # Cap initial allocation to 1000
            self.state[j, 2] = allocated_bw
            allocated_bandwidths.append(allocated_bw)

        # Update remaining bandwidth after initial allocation
        self.remaining_bandwidth = 10_000 - sum(allocated_bandwidths)

        # Phase 2: Allocate additional bandwidth based on actions taken
        for i in range(self.num_users):
            mir = action[i]
            self.state[i, 0] = mir  # Update Current MIR
            requested_bw = self.state[i, 1]
            additional_bw = min(requested_bw - self.state[i, 2], mir - self.state[i, 2])
            self.state[i, 2] += additional_bw  # Update allocated bandwidth
            allocated_bandwidths[i] += additional_bw

        # Abuse detection logic
        for i in range(self.num_users):
            mir = self.state[i, 0]
            requested_bw = self.state[i, 1]
            if requested_bw > mir * (1 + self.theta):
                self.abuse_counters[i] += 1  # Increment abuse counter
            else:
                self.abuse_counters[i] = 0  # Reset if no abuse

            # Calculate abuse scores for penalties
            if self.abuse_counters[i] >= self.delta_t_min:
                abuse_scores.append(self.abuse_counters[i] - self.delta_t_min)

            # Reward calculation based on efficiency
            r = min(self.state[i, 0] / self.state[i, 1], 1)  # Efficiency reward
            rewards.append(r)

        # Efficiency reward calculation
        efficiency_rewards = np.mean(rewards)

        # Total abuse score and penalty calculation
        S_total = sum(abuse_scores)
        P_abusive = (self.gamma * S_total) / (self.num_users * len(self.unique_intervals))
        total_allocated = sum(allocated_bandwidths)
        
        # Penalty if total allocation exceeds capacity
        if total_allocated > 10_000:
            penalties.append((total_allocated - 10_000) / 10_000 * 3)

        # Final reward computation
        total_reward = efficiency_rewards - sum(penalties) - P_abusive
        self.current_step += 1  # Move to the next time step

        # Determine if the episode is done
        done = (self.current_step >= len(self.unique_intervals[0]))

        # Store observation for analysis
        self.observation_history.append(self.state.copy())
        
        return self.state, total_reward, False, done, {}
