# Bandwidth Allocation Reinforcement Learning

This project implements a reinforcement learning model for bandwidth allocation using the Stable Baselines3 library and a custom Gym environment. The goal is to optimize bandwidth allocation based on user requests while detecting and managing potential abuse.

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [File Structure](#file-structure)
- [Environment Details](#environment-details)
- [License](#license)

## Requirements

Make sure you have the following installed:

- Python 3.7 or higher
- Pip (Python package installer)

The following Python packages are required:

```
pandas
numpy
gym
stable-baselines3
```

## Installation

1. Clone the repository:

```bash
git clone <repository_url>
cd <repository_directory>
```

2. Install the required packages:

```bash
pip install pandas numpy gym stable-baselines3
```

3. Prepare your dataset:
   - Format: CSV file
   - Required columns:
     - `DID`: User ID
     - `Date`: Timestamp of the request
     - `BW_REQUESTED`: Bandwidth requested by the user
   - Save as `sorted.csv` in the project directory or update the path in `train_agent.py`

## Usage

### Training the Model

To train the reinforcement learning agent:

```bash
python train_agent.py
```

### Configuration

You can modify the following parameters in `train_agent.py`:

- Learning rate
- Number of episodes
- Batch size
- Network architecture

### Output

The training process generates:

1. Training metrics displayed in real-time
2. A CSV file (`output_observations.csv`) containing:
   - Allocation decisions
   - Reward values
   - State information
3. The trained model saved as `bandwidth_model.zip`

## File Structure

```
.
├── train_agent.py          # Main training script
├── bandwidth_env.py        # Custom Gym environment
├── sorted.csv             # Input dataset
├── output_observations.csv # Training results
└── bandwidth_model.zip    # Saved model
```

## Environment Details

The custom Gym environment (`bandwidth_env.py`) implements:

### State Space

- Current bandwidth usage
- Historical user behavior
- Time-based features
- System capacity indicators

### Action Space

- Continuous action space for bandwidth allocation
- Range: [0, 1] representing percentage of requested bandwidth

### Reward Function

The reward is calculated based on:

- Efficient resource utilization
- Fair distribution
- Abuse prevention
- Service quality maintenance

### Episode Termination

Episodes terminate when:

- Maximum steps reached
- System capacity exceeded
- Abuse detected

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- Stable Baselines3 team for the RL framework
- OpenAI Gym for the environment structure

## Contact

For questions and feedback, please open an issue in the repository.
