#!/usr/bin/env python3
# List running Multipass instances and allow user to select one.
# Launches a remote Visual Studio Code session on the selected instance.

# We assume that the selected instance is a Ubuntu instance with default user "ubuntu".
# Use `new_instance.py` to create new instances, which also sets up the necessary SSH key.

import yaml
import subprocess

# Get the list of instances in YAML format
command = ["multipass", "list", "--format", "yaml"]
result = subprocess.run(command, capture_output=True, text=True)
if result.returncode != 0:
    print("Error executing multipass command:", result.stderr)
    exit(1)

data = yaml.safe_load(result.stdout)
if not data:
    print("No instances found.")
    exit(0)

# Filter to only running instances with an IPv4 address
data = {
    k: v[0] for k, v in data.items()
    if v[0].get('state', '') == 'Running'
    and v[0].get('ipv4', [])
}
if not data:
    print("No running instances found.")
    exit(0)

ips = []

print("Running instances:")
for i, item in enumerate(data.items()):
    k, v = item
    print (f"{i+1}. {k} ({v['ipv4'][0]})")
    ips.append(v['ipv4'][0])

# Prompt user to select an instance
print()
choice = input("Select an instance by number: ")
try:
    choice = int(choice)
    if choice < 1 or choice > len(data):
        raise ValueError(f"Choice {choice} out of range, exiting.")
except ValueError as e:
    print('Error:', str(e))
    exit(1)

selected_ip = ips[choice - 1]
print(f"Connecting to instance at {selected_ip}...")
command = ["code",
           "--folder-uri", f"vscode-remote://ssh-remote+ubuntu@{selected_ip}/home/ubuntu/",
           "--profile", "Multipass VM"]
subprocess.run(command)
