#!/bin/bash

# Define network name
NETWORK_NAME="taranet"

# Ensure the network exists
if ! docker network inspect "$NETWORK_NAME" >/dev/null 2>&1; then
    echo "Creating Docker network: $NETWORK_NAME"
    docker network create "$NETWORK_NAME"
else
    echo "Docker network $NETWORK_NAME already exists."
fi

# List of containers to connect
CONTAINERS=(
  "postgres_shared"
  "tara_backend_dev_blue"
  "celery_worker_blue"
  "celery_beat_blue"
  "redis_shared"
  "tara_green"
  "celery_worker_green"
  "celery_beat_green"
)

echo "Connecting containers to $NETWORK_NAME..."

for container in "${CONTAINERS[@]}"; do
  # Check if container is running
  if docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
    # Connect only if not already connected
    if ! docker inspect "$container" | grep -q "$NETWORK_NAME"; then
      docker network connect "$NETWORK_NAME" "$container"
      echo "✅ Connected $container to $NETWORK_NAME"
    else
      echo "🔁 $container already connected to $NETWORK_NAME"
    fi
  else
    echo "❌ Container $container is not running or doesn't exist"
  fi
done
