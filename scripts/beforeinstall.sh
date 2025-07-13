# #!/bin/bash
# set -e

# echo "[BeforeInstall] Starting pre-deployment setup..."

# # 0. Clean Previous Deployment (NEW)
# echo "-> Cleaning previous deployment..."
# if [ -d "/home/ubuntu/tara_dev_backend" ]; then
#     # Keep .env but remove other files
#     find /home/ubuntu/tara_dev_backend -mindepth 1 ! -name '.env' -exec rm -rf {} +
#     echo "-> Removed existing deployment files (preserved .env)"
# else
#     sudo mkdir -p /home/ubuntu/tara_dev_backend
# fi

# # ... rest of your existing script ...

# # 1. Install CodeDeploy Agent (first run only)
# if [ ! -f /etc/init.d/codedeploy-agent ]; then
#     echo "-> Installing CodeDeploy agent..."
#     sudo apt-get update
#     sudo apt-get install -y ruby wget
#     REGION=$(curl -s http://169.254.169.254/latest/meta-data/placement/region)
#     cd /tmp
#     wget "https://aws-codedeploy-${REGION}.s3.${REGION}.amazonaws.com/latest/install"
#     chmod +x ./install
#     sudo ./install auto
#     sudo service codedeploy-agent start
# else
#     echo "-> CodeDeploy agent already installed"
# fi

# # 2. Install Docker (if missing)
# if ! command -v docker &>/dev/null; then
#     echo "-> Installing Docker..."
#     sudo apt-get install -y docker.io
#     sudo systemctl enable docker
#     sudo usermod -aG docker ubuntu
# else
#     echo "-> Docker already installed"
# fi

# # 3. Install Docker Compose (if missing)
# if ! command -v docker-compose &>/dev/null; then
#     echo "-> Installing Docker Compose..."
#     sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
#         -o /usr/local/bin/docker-compose
#     sudo chmod +x /usr/local/bin/docker-compose
# else
#     echo "-> Docker Compose already installed"
# fi

# # 4. Install Nginx (if missing)
# if ! command -v nginx &>/dev/null; then
#     echo "-> Installing Nginx..."
#     sudo apt-get install -y nginx
# else
#     echo "-> Nginx already installed"
# fi

# # 5. Clean Docker resources (always run)
# echo "-> Cleaning Docker system..."
# docker system prune -af --volumes
# docker builder prune -af

# # 6. Prepare deployment directory (now simplified)
# echo "-> Setting directory permissions..."
# sudo chown -R ubuntu:ubuntu /home/ubuntu/tara_dev_backend
# sudo chmod 755 /home/ubuntu/tara_dev_backend

# echo "[BeforeInstall] Setup completed successfully"

#!/bin/bash
set -e

echo "[BeforeInstall] 🚀 Starting pre-deployment setup..."

DEPLOY_DIR="/home/ubuntu/tara_dev_backend"
PRESERVE_FILES=(".env" "image_vars.env")

# 1. Ensure deployment directory exists
if [ ! -d "$DEPLOY_DIR" ]; then
  echo "📁 Creating deployment directory..."
  mkdir -p "$DEPLOY_DIR"
fi

# 2. Clean directory while preserving key files
echo "🧹 Cleaning previous deployment (preserving .env and image_vars.env)..."

# Create pattern for preserved files
preserve_args=()
for file in "${PRESERVE_FILES[@]}"; do
  preserve_args+=( -not -name "$file" )
done

# Find and delete all except preserved files
find "$DEPLOY_DIR" -mindepth 1 "${preserve_args[@]}" -exec rm -rf {} +

# 3. Fix ownership & permissions
echo "🔒 Setting permissions..."
chown -R ubuntu:ubuntu "$DEPLOY_DIR"
chmod 755 "$DEPLOY_DIR"

# 4. Optional: Clean only unused Docker containers and images
echo "🐳 Cleaning Docker (containers & images only, skipping volumes)..."
docker system prune -af || true
docker builder prune -af || true

echo "[BeforeInstall] ✅ Done."
