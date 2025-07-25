# #!/bin/bash
# set -e

# echo "[Start] Starting Docker containers..."
# cd /home/ubuntu/tara_dev_backend

# if [ -f "image_vars.env" ]; then
#     set -a
#     source image_vars.env
#     set +a
# else
#     echo "❌ image_vars.env not found!"
#     exit 1
# fi

# if [[ -z "$DOCKER_IMAGE" || -z "$IMAGE_TAG" ]]; then
#     echo "❌ DOCKER_IMAGE or IMAGE_TAG is missing"
#     exit 1
# fi

# # Validate postgres image variable
# if [[ -z "$POSTGRES_IMAGE" ]]; then
#     echo "❌ POSTGRES_IMAGE is missing"
#     exit 1
# fi

# if [[ -z "$REDIS_IMAGE" ]]; then
#     echo "❌ REDIS_IMAGE is missing"
#     exit 1
# fi

# echo "✅ Using image: ${DOCKER_IMAGE}:${IMAGE_TAG}"
# echo "✅ Using Redis image: ${REDIS_IMAGE}"
# echo "✅ Using postgres image: ${POSTGRES_IMAGE}"

# docker-compose --env-file image_vars.env up -d

# echo "[Start] ✅ Containers launched."



# # echo "[ApplicationStart] Syncing static and media to host..."
# # docker cp $CONTAINER_ID:/app/staticfiles /home/ubuntu/tara_dev_backend/staticfiles
# # docker cp $CONTAINER_ID:/app/media /home/ubuntu/tara_dev_backend/media


#!/bin/bash
set -e

cd /home/ubuntu/tara_dev_backend || exit

echo "[Start] Starting Docker containers..."

if [ -f "image_vars.env" ]; then
    set -a
    source image_vars.env
    set +a
else
    echo "❌ image_vars.env not found!"
    exit 1
fi

if [[ -z "$DOCKER_IMAGE" || -z "$IMAGE_TAG" ]]; then
    echo "❌ DOCKER_IMAGE or IMAGE_TAG is missing"
    exit 1
fi

if [[ -z "$POSTGRES_IMAGE" ]]; then
    echo "❌ POSTGRES_IMAGE is missing"
    exit 1
fi

if [[ -z "$REDIS_IMAGE" ]]; then
    echo "❌ REDIS_IMAGE is missing"
    exit 1
fi

echo "✅ Using image: ${DOCKER_IMAGE}:${IMAGE_TAG}"
echo "✅ Using Redis image: ${REDIS_IMAGE}"
echo "✅ Using postgres image: ${POSTGRES_IMAGE}"

docker-compose --env-file image_vars.env up -d

echo "[Start] ✅ Containers launched."