#!/bin/bash
set -e

echo "[ApplicationStop] Stopping containers..."
cd /home/ubuntu/tara_dev_backend
docker-compose down || true