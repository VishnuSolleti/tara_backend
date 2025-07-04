#!/bin/bash
set -e

echo "[BeforeInstall] Starting pre-deployment setup..."

# 1. Install CodeDeploy Agent (first run only)
if [ ! -f /etc/init.d/codedeploy-agent ]; then
    echo "-> Installing CodeDeploy agent..."
    sudo apt-get update
    sudo apt-get install -y ruby wget
    REGION=$(curl -s http://169.254.169.254/latest/meta-data/placement/region)
    cd /tmp
    wget "https://aws-codedeploy-${REGION}.s3.${REGION}.amazonaws.com/latest/install"
    chmod +x ./install
    sudo ./install auto
    sudo service codedeploy-agent start
else
    echo "-> CodeDeploy agent already installed"
fi

# 2. Install Docker (if missing)
if ! command -v docker &>/dev/null; then
    echo "-> Installing Docker..."
    sudo apt-get install -y docker.io
    sudo systemctl enable docker
    sudo usermod -aG docker ubuntu
else
    echo "-> Docker already installed"
fi

# 3. Install Docker Compose (if missing)
if ! command -v docker-compose &>/dev/null; then
    echo "-> Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
        -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
else
    echo "-> Docker Compose already installed"
fi

# 4. Install Nginx (if missing)
if ! command -v nginx &>/dev/null; then
    echo "-> Installing Nginx..."
    sudo apt-get install -y nginx
else
    echo "-> Nginx already installed"
fi

# 5. Clean Docker resources (always run)
echo "-> Cleaning Docker system..."
docker system prune -af --volumes
docker builder prune -af

# 6. Prepare deployment directory (always run)
echo "-> Preparing deployment directory..."
sudo mkdir -p /home/ubuntu/tara_dev_backend
sudo chown -R ubuntu:ubuntu /home/ubuntu/tara_dev_backend

echo "[BeforeInstall] Setup completed successfully"