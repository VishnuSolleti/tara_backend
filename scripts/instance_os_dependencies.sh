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

echo "Installing wkhtmltopdf"
sudo apt-get install -y wkhtmltopdf

sudo apt install -y python3-pip
sudo apt install -y nginx
sudo apt install -y virtualenv