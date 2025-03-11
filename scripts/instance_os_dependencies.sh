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
sudo apt-get upgrade -y

# Install required dependencies
echo "Installing dependencies"
sudo apt-get install -y \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    curl \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev

# Install Python 3.10 (if not installed)
if ! command -v python3.10 &>/dev/null; then
    echo "Installing Python 3.10"
    sudo add-apt-repository ppa:deadsnakes/ppa -y
    sudo apt-get update
    sudo apt-get install -y python3.10 python3.10-venv python3.10-dev
fi

# Install wkhtmltopdf
echo "Installing wkhtmltopdf"
sudo apt-get install -y wkhtmltopdf

# Install Python tools
echo "Installing Python tools"
sudo apt install -y python3-pip
sudo apt install -y virtualenv

# Install and configure Nginx
echo "Installing Nginx"
sudo apt install -y nginx
sudo systemctl enable nginx
sudo systemctl start nginx

# Upgrade pip and setuptools
echo "Upgrading pip and setuptools"
pip install --upgrade pip setuptools wheel

echo "Installation completed successfully!"
