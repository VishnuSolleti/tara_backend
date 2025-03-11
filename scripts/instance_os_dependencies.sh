#!/usr/bin/env bash

set -e  # Exit on error
LOGFILE="/tmp/codepipeline_log.txt"

# Log all output
exec > >(tee -a $LOGFILE) 2>&1

echo "Starting dependency installation script..."

# Fix dpkg if interrupted
sudo dpkg --configure -a

# Update & upgrade system packages
sudo apt-get update && sudo apt-get upgrade -y

# Install necessary system dependencies
sudo apt install -y wkhtmltopdf python3-pip nginx virtualenv libtesseract-dev tesseract-ocr poppler-utils

# Upgrade pip and setuptools
python3 -m pip install --upgrade pip setuptools wheel
python3 -m pip install "setuptools<66"  # Avoid known issue

# Install required Python packages separately
python3 -m pip install --no-cache-dir rx djongo pytesseract

echo "Dependency installation completed successfully!"
