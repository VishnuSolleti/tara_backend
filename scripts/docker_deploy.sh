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

# Run the container
docker run -d -p 8000:8000 --name tarafirst tarafirst

echo "✅ Deployment complete! App running on port 8000"
