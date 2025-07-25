# #!/bin/bash
# set -e

# echo "[BeforeInstall] 🚀 Starting pre-deployment setup..."

# DEPLOY_DIR="/home/ubuntu/tara_dev_backend"
# PRESERVE_FILES=(".env" "image_vars.env")

# # 1. Ensure deployment directory exists
# if [ ! -d "$DEPLOY_DIR" ]; then
#   echo "📁 Creating deployment directory..."
#   mkdir -p "$DEPLOY_DIR"
# fi

# # 2. Clean directory while preserving key files
# echo "🧹 Cleaning previous deployment (preserving .env and image_vars.env)..."

# # Create pattern for preserved files
# preserve_args=()
# for file in "${PRESERVE_FILES[@]}"; do
#   preserve_args+=( -not -name "$file" )
# done

# # Find and delete all except preserved files
# find "$DEPLOY_DIR" -mindepth 1 "${preserve_args[@]}" -exec rm -rf {} +

# # 3. Fix ownership & permissions
# echo "🔒 Setting permissions..."
# chown -R ubuntu:ubuntu "$DEPLOY_DIR"
# chmod 755 "$DEPLOY_DIR"

# # 4. Optional: Clean only unused Docker containers and images
# echo "🐳 Cleaning Docker (containers & images only, skipping volumes)..."
# docker system prune -af || true
# docker builder prune -af || true

# echo "[BeforeInstall] ✅ Done."


#!/bin/bash
set -e

echo "[BeforeInstall] 🚀 Starting pre-deployment setup..."

DEPLOY_DIR="/home/ubuntu/tara_dev_backend"
PRESERVE_FILES=(".env" "image_vars.env")

if [ ! -d "$DEPLOY_DIR" ]; then
  echo "📁 Creating deployment directory..."
  mkdir -p "$DEPLOY_DIR"
fi

echo "🧹 Cleaning previous deployment (preserving .env and image_vars.env)..."

preserve_args=()
for file in "${PRESERVE_FILES[@]}"; do
  preserve_args+=( -not -name "$file" )
done

find "$DEPLOY_DIR" -mindepth 1 "${preserve_args[@]}" -exec rm -rf {} +

chown -R ubuntu:ubuntu "$DEPLOY_DIR"
chmod 755 "$DEPLOY_DIR"

echo "🐳 Cleaning Docker (containers & images only, skipping volumes)..."
docker system prune -af || true
docker builder prune -af || true

echo "[BeforeInstall] ✅ Done."