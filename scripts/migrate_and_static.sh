#!/bin/bash
set -e

echo "[Migrate/Static] Running DB migrations and collectstatic..."
cd /home/ubuntu/tara_dev_backend

CONTAINER_ID=$(docker ps -qf "name=backend")
if [[ -z "$CONTAINER_ID" ]]; then
    echo "❌ Backend container not found!"
    docker ps
    exit 1
fi

# # Run migrations
# echo "[Migrate/Static] Applying migrations..."
# docker exec "$CONTAINER_ID" python manage.py migrate --noinput

# # Collect static files
# echo "[Migrate/Static] Collecting static files..."
# docker exec "$CONTAINER_ID" python manage.py collectstatic --noinput

echo "[Migrate/Static] ✅ Done."
