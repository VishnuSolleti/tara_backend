#!/bin/bash

set -e

NETWORK_NAME="taranet"

# Delete if half-exists or broken
if docker network ls --format '{{.Name}}' | grep -w "$NETWORK_NAME" > /dev/null; then
  echo "🔁 Network $NETWORK_NAME already exists. Re-creating to ensure clean state."
  docker network rm "$NETWORK_NAME" || true
fi

echo "🌐 Creating external Docker network: $NETWORK_NAME"
docker network create --driver bridge "$NETWORK_NAME"

# List of containers to conne
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
