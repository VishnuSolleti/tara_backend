#!/bin/bash
set -e

echo "🚀 Starting Docker deployment..."

# Navigate to the deployment directory
cd /home/ubuntu/tarafirst

# Stop and remove existing container if it exists
docker stop tarafirst || true
docker rm tarafirst || true

# Build Docker image
docker build -t tarafirst .

# Run the container WITHOUT exposing a port, and MOUNT the socket path
docker run -d \
  --name tarafirst \
  -v /home/ubuntu/tarafirst/Tara/:/app/Tara/ \
  tarafirst

echo "✅ Deployment complete! App running behind Nginx via UNIX socket"
