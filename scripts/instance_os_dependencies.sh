#!/usr/bin/env bash

# Function to handle dpkg interruption
fix_dpkg() {
  echo "Running 'sudo dpkg --configure -a' to fix any interrupted dpkg processes"
  sudo dpkg --configure -a
}

# Run the fix_dpkg function before proceeding
fix_dpkg

# Update the package list
echo "Updating package list"
sudo apt-get update
sudo apt-get upgrade

echo "Installing required packages..."
sudo apt-get install -y wkhtmltopdf python3-pip nginx virtualenv python3-distutils python3-setuptools

# Ensure pip is updated
echo "Upgrading pip..."
python3 -m ensurepip
python3 -m pip install --upgrade pip setuptools wheel

echo "All dependencies installed successfully."