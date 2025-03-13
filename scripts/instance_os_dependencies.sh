#!/usr/bin/env bash

# Function to handle dpkg interruption
fix_dpkg() {
  echo "Running 'sudo dpkg --configure -a' to fix any interrupted dpkg processes"
  sudo dpkg --configure -a
}

# Run the fix_dpkg function before proceeding
fix_dpkg

# Update the package list
echo "Updating package list..."
sudo apt-get update
sudo apt-get upgrade -y

# Install required system dependencies
echo "Installing required packages..."
sudo apt-get install -y wkhtmltopdf python3-pip nginx virtualenv python3-venv python3-setuptools python3-wheel

# Ensure pip and setuptools are updated
echo "Upgrading pip and setuptools..."
python3 -m ensurepip --default-pip
python3 -m pip install --upgrade pip setuptools wheel

echo "All dependencies installed successfully."
