#!/bin/bash
set -e

echo "[ApplicationStart] Starting containers..."
cd /home/ubuntu/tara_dev_backend
docker-compose up -d

echo "[ApplicationStart] Running DB migrations..."
CONTAINER_ID=$(docker ps -qf "name=backend")
docker exec $CONTAINER_ID python manage.py migrate --noinput