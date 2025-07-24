# #!/bin/bash
# set -e

# echo "[AfterInstall] ✅ Setting up Nginx..."

# # 1. Move Nginx config to correct location
# cp /tmp/http.conf /etc/nginx/sites-available/
# ln -sf /etc/nginx/sites-available/http.conf /etc/nginx/sites-enabled/
# rm -f /etc/nginx/sites-enabled/default

# # 2. Test & restart Nginx
# echo "[AfterInstall] 🔍 Validating Nginx config..."
# nginx -t
# systemctl restart nginx

# # 3. Ensure .env exists (used by docker-compose or app)
# echo "[AfterInstall] 🛡️ Ensuring .env exists with secure permissions..."
# touch /home/ubuntu/tara_dev_backend/.env
# chmod 600 /home/ubuntu/tara_dev_backend/.env
# chown ubuntu:ubuntu /home/ubuntu/tara_dev_backend/.env

# echo "[AfterInstall] ✅ Done"


# #!/bin/bash
# set -e

# echo "[AfterInstall] ✅ Setting up Nginx..."

# cp /tmp/http.conf /etc/nginx/sites-available/
# ln -sf /etc/nginx/sites-available/http.conf /etc/nginx/sites-enabled/
# rm -f /etc/nginx/sites-enabled/default

# nginx -t
# systemctl restart nginx

# touch /home/ubuntu/tara_green/.env
# chmod 600 /home/ubuntu/tara_green/.env
# chown ubuntu:ubuntu /home/ubuntu/tara_green/.env

# echo "[AfterInstall] ✅ Done"

# #!/bin/bash
# set -e

# echo "[AfterInstall] ✅ Setting up Nginx..."

# # Detect deployment directory
# if [[ "$PWD" == *"tara_green"* ]]; then
#   TARGET_PORT="8002"
#   echo "🟢 Detected Green Deployment"
# elif [[ "$PWD" == *"tara_blue"* ]]; then
#   TARGET_PORT="8001"
#   echo "🔵 Detected Blue Deployment"
# else
#   echo "❌ Unknown deployment directory"
#   exit 1
# fi

# # Health Check using /healthz endpoint
# HEALTH_ENDPOINT="http://localhost:$TARGET_PORT/healthz"
# echo "🔍 Verifying health check at $HEALTH_ENDPOINT..."
# RETRY=5
# SUCCESS=false

# for i in $(seq 1 $RETRY); do
#     sleep 5
#     if curl -s "$HEALTH_ENDPOINT" | grep -q '"status": *"ok"'; then
#         SUCCESS=true
#         echo "✅ App passed health check on port $TARGET_PORT"
#         break
#     else
#         echo "⏳ Retry $i/$RETRY: App not healthy yet..."
#     fi
# done

# if [ "$SUCCESS" != "true" ]; then
#     echo "❌ Health check failed. Nginx config NOT updated."
#     exit 1
# fi

# # Update Nginx config
# sed "s/__PORT__/${TARGET_PORT}/" /tmp/http_template.conf > /etc/nginx/sites-available/http.conf

# ln -sf /etc/nginx/sites-available/http.conf /etc/nginx/sites-enabled/
# rm -f /etc/nginx/sites-enabled/default

# nginx -t
# systemctl restart nginx
# echo "✅ Nginx now routing to port ${TARGET_PORT}"

# # Ensure .env exists
# DEPLOY_DIR="$PWD"
# touch "$DEPLOY_DIR/.env"
# chmod 600 "$DEPLOY_DIR/.env"
# chown ubuntu:ubuntu "$DEPLOY_DIR/.env"

# echo "[AfterInstall] ✅ Finished"


#!/bin/bash
set -e

echo "[AfterInstall] ✅ Setting up Nginx..."

# Detect deployment directory
if [[ "$PWD" == *"tara_green"* ]]; then
  TARGET_PORT="8002"
  echo "🟢 Detected Green Deployment"
elif [[ "$PWD" == *"tara_blue"* ]]; then
  TARGET_PORT="8001"
  echo "🔵 Detected Blue Deployment"
else
  echo "❌ Unknown deployment directory"
  exit 1
fi

# Health Check
HEALTH_ENDPOINT="http://localhost:$TARGET_PORT/healthz"
echo "🔍 Checking health at $HEALTH_ENDPOINT..."
RETRY=5
SUCCESS=false
for i in $(seq 1 $RETRY); do
    sleep 5
    if curl -s "$HEALTH_ENDPOINT" | grep -q '"status": *"ok"'; then
        SUCCESS=true
        echo "✅ App healthy on port $TARGET_PORT"
        break
    else
        echo "⏳ Retry $i/$RETRY..."
    fi
done

if [ "$SUCCESS" != "true" ]; then
    echo "❌ Health check failed"
    exit 1
fi

# Update active_color.txt and Nginx
if grep -q "blue" /home/ubuntu/active_color.txt; then
  sed -i 's/127.0.0.1:8001/127.0.0.1:8002/' /tmp/http.conf
  echo "green" > /home/ubuntu/active_color.txt
else
  sed -i 's/127.0.0.1:8002/127.0.0.1:8001/' /tmp/http.conf
  echo "blue" > /home/ubuntu/active_color.txt
fi

cp /tmp/http.conf /etc/nginx/sites-available/http.conf
ln -sf /etc/nginx/sites-available/http.conf /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

nginx -t && systemctl restart nginx

DEPLOY_DIR="$PWD"
touch "$DEPLOY_DIR/.env"
chmod 600 "$DEPLOY_DIR/.env"
chown ubuntu:ubuntu "$DEPLOY_DIR/.env"

echo "[AfterInstall] ✅ Finished"