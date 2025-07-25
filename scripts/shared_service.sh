#!/bin/bash
set -e

echo "📦 Setting up shared Redis & PostgreSQL..."

SHARED_DIR="/home/ubuntu/shared_services"

if [ ! -d "$SHARED_DIR" ]; then
  mkdir -p "$SHARED_DIR"
  chown ubuntu:ubuntu "$SHARED_DIR"
fi

# Create docker-compose file only on
if [ ! -f "$SHARED_DIR/docker-compose.yml" ]; then
  cat > "$SHARED_DIR/docker-compose.yml" <<EOF
version: '3.8'

services:
  redis:
    image: docker.io/sadanandtummuri/redis:7.0
    container_name: redis_shared
    restart: always
    ports:
      - "6379:6379"
    networks:
      - taranet

  db:
    image: docker.io/sadanandtummuri/postgres:17.5
    container_name: postgres_shared
    restart: always
    env_file:
      - .env
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-postgres}"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - taranet

volumes:
  postgres_data:

networks:
  taranet:
    # driver: bridge
    external: true
    name: taranet
EOF
fi

cd "$SHARED_DIR"

# Check if Redis and Postgres containers are already running
if docker ps --format '{{.Names}}' | grep -q 'redis_shared' && docker ps --format '{{.Names}}' | grep -q 'postgres_shared'; then
  echo "✅ Shared Redis & PostgreSQL are already running."
else
  echo "🚀 Starting shared Redis & PostgreSQL..."
  docker-compose up -d
  echo "✅ Shared services started: Redis (6379), PostgreSQL (5432)"
fi
