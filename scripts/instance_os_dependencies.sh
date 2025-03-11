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

# Create a virtual environment (Best practice in Ubuntu 24.04)
VENV_PATH="/opt/my_project_venv"
if [ ! -d "$VENV_PATH" ]; then
    python3 -m venv "$VENV_PATH"
fi

# Activate virtual environment
source "$VENV_PATH/bin/activate"

# Upgrade pip and setuptools within the virtual environment
pip install --upgrade pip setuptools wheel
pip install "setuptools<66"  # Avoid known issue

# Install required Python packages inside the virtual environment
pip install --no-cache-dir rx djongo pytesseract

# Deactivate the virtual environment
deactivate

echo "Dependency installation completed successfully!"
