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
  -v /home/ubuntu/tarafirst/Tara/:/app/Tara/ \
  --name tarafirst \
  tarafirst gunicorn Tara.wsgi:application --bind unix:/app/Tara/Tara.sock --workers 1


echo "✅ Deployment complete! App running with secure envs"
