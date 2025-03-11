#!/usr/bin/env bash

set -e  # Exit immediately if a command exits with a non-zero status
LOGFILE="/tmp/codepipeline_log.txt"

# Function to handle dpkg interruption
fix_dpkg() {
  echo "Running 'sudo dpkg --configure -a'" | tee -a $LOGFILE
  sudo dpkg --configure -a >> $LOGFILE 2>&1
}

# Log all output to file and stdout
exec > >(tee -a $LOGFILE) 2>&1

echo "Starting dependency installation script..."

# Run fix_dpkg before proceeding
fix_dpkg

# Update package list
echo "Updating package list..."
sudo apt-get update && sudo apt-get upgrade -y

# Fix potential dpkg lock issue
echo "Checking for dpkg lock issues..."
sudo killall apt apt-get || true
sudo rm -rf /var/lib/dpkg/lock
sudo rm -rf /var/lib/dpkg/lock-frontend
sudo dpkg --configure -a

# Install required system dependencies
echo "Installing dependencies..."
sudo apt install -y wkhtmltopdf python3-pip nginx virtualenv libtesseract-dev tesseract-ocr poppler-utils

# Upgrade pip and setuptools to avoid build issues
echo "Upgrading pip and setuptools..."
python3 -m pip install --upgrade pip setuptools wheel

echo "Installation complete!"

# Print logs at the end
cat $LOGFILE
