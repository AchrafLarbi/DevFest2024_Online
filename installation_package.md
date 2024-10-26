# Bandwidth Monitoring and Allocation System

## Overview

This project is a bandwidth monitoring and allocation system that uses packet capture data to analyze bandwidth usage for different clients. It includes a custom Gym environment for simulating bandwidth allocation strategies.

## Dependencies

The following libraries and dependencies are required to run this project:

### Python Libraries

- **numpy**: A fundamental package for scientific computing in Python. Used for numerical operations and handling arrays.
- **gymnasium**: A toolkit for developing and comparing reinforcement learning algorithms. It provides the custom environment for bandwidth allocation.
- **pandas**: A powerful data manipulation and analysis library. Used for handling and analyzing the dataset.
- **subprocess**: A module to spawn new processes, connect to their input/output/error pipes, and obtain their return codes. Used for running external commands like `tshark`.
- **time**: A module for manipulating time and date. Used for handling time-related functions in the monitoring system.
- **re**: A module for working with regular expressions. Used for parsing output from the `tshark` command.
- **csv**: A module for reading and writing CSV files. Used for logging bandwidth statistics.
- **os**: A module that provides a way of using operating system dependent functionality. Used for file path manipulations.

### Installation

You can install the required libraries using pip. It's recommended to create a virtual environment for this project:

```bash
# Create a virtual environment
python -m venv bandwidth-env

# Activate the virtual environment
# Windows
bandwidth-env\Scripts\activate
# macOS/Linux
source bandwidth-env/bin/activate

# Install the required packages
pip install numpy gymnasium pandas
```
