# #!/bin/bash
# set -e

# echo "[ApplicationStart] Starting containers..."
# cd /home/ubuntu/tara_dev_backend

# # 1. STRICT VARIABLE LOADING
# export DOCKER_IMAGE="sadanandtummuri/my_backend_images"
# export IMAGE_TAG=$(head -n 1 image_tag.txt | tr -cd '[:alnum:]')  # Removes ALL non-alphanumeric chars

# # 2. VALIDATION
# if [ -z "$IMAGE_TAG" ] || [ ${#IMAGE_TAG} -lt 7 ]; then
#    echo "ERROR: Invalid IMAGE_TAG: '$IMAGE_TAG'"
#    exit 1
# fi

# # 3. VERBOSE LOGGING
# echo "DEBUG: Raw tag file content:"
# cat -vet image_tag.txt  # Shows hidden characters
# echo "Using image: ${DOCKER_IMAGE}:${IMAGE_TAG}"
# docker-compose up -d

# echo "[ApplicationStart] Running DB migrations..."
# CONTAINER_ID=$(docker ps -qf "name=backend")
# docker exec $CONTAINER_ID python manage.py migrate --noinput

# echo "[ApplicationStart] Collecting static files..."
# docker exec $CONTAINER_ID python manage.py collectstatic --noinput

#!/bin/bash
set -e

echo "[ApplicationStart] Starting containers..."
cd /home/ubuntu/tara_dev_backend

# 1. Load image variables
if [ -f "image_vars.env" ]; then
    source image_vars.env
else
    echo "ERROR: image_vars.env not found!"
    exit 1
fi

# 2. Validation
if [ -z "$DOCKER_IMAGE" ] || [ -z "$IMAGE_TAG" ]; then
    echo "ERROR: Missing DOCKER_IMAGE or IMAGE_TAG in image_vars.env"
    exit 1
fi

# 3. Logging
echo "Using image: ${DOCKER_IMAGE}:${IMAGE_TAG}"

# 4. Start container
docker-compose up -d

# 5. Migrate DB
echo "[ApplicationStart] Running DB migrations..."
CONTAINER_ID=$(docker ps -qf "name=backend")
docker exec $CONTAINER_ID python manage.py migrate --noinput

echo "[ApplicationStart] Collecting static files..."
docker exec $CONTAINER_ID python manage.py collectstatic --noinput

# echo "[ApplicationStart] Syncing static and media to host..."
# docker cp $CONTAINER_ID:/app/staticfiles /home/ubuntu/tara_dev_backend/staticfiles
# docker cp $CONTAINER_ID:/app/media /home/ubuntu/tara_dev_backend/media