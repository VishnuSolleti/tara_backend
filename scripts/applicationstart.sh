#!/bin/bash
set -e

echo "[ApplicationStart] Starting containers..."
cd /home/ubuntu/tara_dev_backend

# In deployment scripts
export DOCKER_IMAGE="sadanandtummuri/my_backend_images"
# export IMAGE_TAG=$(cat image_tag.txt)
IMAGE_TAG=$(cat image_tag.txt | tr -d '\n')
docker-compose up -d

echo "[ApplicationStart] Running DB migrations..."
CONTAINER_ID=$(docker ps -qf "name=backend")
docker exec $CONTAINER_ID python manage.py migrate --noinput