#!/bin/bash
set -e

echo "🚀 Starting Docker deployment..."

cd /home/ubuntu/tarafirst

docker stop tarafirst || true
docker rm tarafirst || true

docker build -t tarafirst .

# Run container with env file
docker run -d \
  --env-file /home/ubuntu/.env \
  -p 8001:8000 \
  --name tarafirst \
  tarafirst



echo "✅ Deployment complete! App running with secure envs"
