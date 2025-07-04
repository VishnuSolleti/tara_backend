#!/bin/bash
set -e

echo "[BeforeInstall] Checking system packages..."

# Only install if missing
command -v docker >/dev/null || {
    echo "Installing Docker..."
    sudo apt-get update
    sudo apt-get install -y docker.io
    sudo systemctl enable docker
    sudo usermod -aG docker ubuntu
}

command -v docker-compose >/dev/null || {
    echo "Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
        -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
}

command -v nginx >/dev/null || {
    echo "Installing Nginx..."
    sudo apt-get install -y nginx
}

echo "[BeforeInstall] Cleaning Docker resources..."
docker system prune -af --volumes  # Remove ALL unused images, containers, volume
docker builder prune -af  # Clean build cache

echo "[BeforeInstall] Preparing deployment directory..."
sudo mkdir -p /home/ubuntu/tara_dev_backend
sudo chown -R ubuntu:ubuntu /home/ubuntu/tara_dev_backend