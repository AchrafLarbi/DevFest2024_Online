"""
BandwidthMonitor Class

This script monitors bandwidth usage for specific clients on a network by analyzing packet capture (PCAP) files. 

Key Components:
- **PCAP File**: The script reads from a specified packet capture file (usually generated by tools like Wireshark) that contains network traffic data.
- **CSV Output**: The bandwidth statistics for each client are recorded in a CSV file, including details such as the Date, DDI (Data Device Identifier), and calculated bandwidth.
- **Clients**: The script tracks multiple clients based on their IP addresses, and each client is mapped to a specific name and DDI value.

How It Works:
1. **Initialization**: The `BandwidthMonitor` class is initialized with the paths to the PCAP and CSV files. It sets up client mappings and initializes cumulative statistics.
2. **Running Tshark**: The script uses the `tshark` command-line tool (part of the Wireshark suite) to analyze the PCAP file for bandwidth statistics related to each client IP.
3. **Processing Output**: It processes the output from `tshark`, extracting the number of frames and bytes transmitted for each client.
4. **Statistics Calculation**: Cumulative statistics for frames and bytes are updated, and the bandwidth is calculated in Mbps.
5. **CSV Logging**: The results, including DDI, date, and bandwidth usage, are appended to a CSV file for record-keeping and analysis.
6. **Display**: The script prints out the current statistics for each client in a formatted manner.

Usage:
- **Network Analysis**: This tool can be beneficial for network administrators or researchers looking to analyze bandwidth usage patterns for specific clients within a network.
- **Modeling and Simulation**: The recorded data can be used to model bandwidth utilization and identify potential abuse or inefficiencies in network resource allocation. It can help in creating predictive models for bandwidth management, capacity planning, and network optimization.

Example Workflow:
1. Modify the `pcap_file` and `csv_file` paths in the `main` function to point to your specific files.
2. Run the script, and it will collect bandwidth usage statistics for the defined duration.
3. Analyze the generated CSV file to study bandwidth trends, which can be fed into other models for deeper insights or simulations.
"""


import subprocess
import time
import re
import csv
import os

class BandwidthMonitor:
    def __init__(self, pcap_file, csv_file):
        self.pcap_file = pcap_file
        self.csv_file = csv_file
        # Map client IPs to their respective DDI values
        self.clients = {
            '192.168.108.2': {'name': 'PC1', 'ddi': '2407561'},
            '192.168.108.3': {'name': 'PC2', 'ddi': '2407562'}
        }
        # Initialize cumulative statistics for each client
        self.stats = {client_ip: {'frames': 0, 'bytes': 0} for client_ip in self.clients.keys()}
        
        # Create CSV file and write header if it doesn't exist
        if not os.path.isfile(self.csv_file):
            with open(self.csv_file, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['DDI', 'Date', 'Bandwidth'])  # Set header order

    @property
    def client_ips(self):
        """Return the list of client IPs."""
        return list(self.clients.keys())

    def run_tshark(self):
        try:
            # Command to run tshark for each client
            for client_ip in self.clients:
                cmd = [
                    'tshark',
                    '-r', self.pcap_file,
                    '-q', '-z', 'io,stat,0', f'ip.addr=={client_ip}'
                ]

                # Run the command and capture the output
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                output, _ = process.communicate()

                # Process the output
                self.process_output(client_ip, output.decode())

        except Exception as e:
            print(f"Error running tshark: {e}")

    def process_output(self, client_ip, output):
        # Regex to capture the frames and bytes statistics
        match = re.search(r'\| *(\d+) *\| *(\d+) *\|', output)

        if match:
            frames = int(match.group(1))
            bytes_ = int(match.group(2))

            # Update cumulative statistics
            if client_ip in self.stats:
                self.stats[client_ip]['frames'] += frames
                self.stats[client_ip]['bytes'] += bytes_

            # Write cumulative statistics to CSV
            self.write_statistics_to_csv(client_ip)

            # Display the updated statistics in an organized way
            self.display_statistics(client_ip)

    def display_statistics(self, client_ip):
        client_info = self.clients[client_ip]
        client_name = client_info['name']
        frames = self.stats[client_ip]['frames']
        bytes_ = self.stats[client_ip]['bytes']
        bandwidth_mbps = (bytes_ * 8) / (1024 * 1024)  # Convert bytes to Mbps

        print(f"\nClient: {client_name} ({client_ip})")
        print(f"Frames: {frames}")
        print(f"Bytes: {bytes_:,} bytes")
        print(f"BW_REQUESTED: {bandwidth_mbps:.2f} Mbps")

    def write_statistics_to_csv(self, client_ip):
        Date = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
        client_info = self.clients[client_ip]
        DDI = client_info['ddi']
        total_bytes = self.stats[client_ip]['bytes']
        BW_REQUESTED = (total_bytes * 8) / (1024 * 1024)  # Convert bytes to Mbps

        with open(self.csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([DDI, Date, f"{BW_REQUESTED:.2f}"])  # Write in the desired order

def main():
    pcap_file = r"C:\Users\asus\OneDrive\Bureau\DevFest2024\Devfest2024_backend\udp.pcapng"  # Replace with your actual file path
    csv_file = r"C:\Users\asus\OneDrive\Bureau\DevFest_RL\bandwidth_usage.csv"  # Replace with your desired CSV file path
    monitor = BandwidthMonitor(pcap_file, csv_file)

    start_time = time.time()
    duration = 60  # Duration in seconds

    # Run the bandwidth monitor for a limited time
    while time.time() - start_time < duration:
        monitor.run_tshark()
        time.sleep(5)  # Adjust the interval to 5 seconds

if __name__ == "__main__":
    main()
