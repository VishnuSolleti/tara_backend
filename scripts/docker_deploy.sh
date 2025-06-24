#!/bin/bash

cd /home/ubuntu/tarafirst

# Stop old container
docker stop tarafirst || true
docker rm tarafirst || true

# Build new image
docker build -t tarafirst:latest .

# Run new container
docker run -d \
  --name tarafirst \
  -p 8000:8000 \
  --env DJANGO_SETTINGS_MODULE=Tara.settings.default \
  tarafirst:latest
