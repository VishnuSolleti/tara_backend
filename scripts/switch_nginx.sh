#!/bin/bash
set -e

echo "[SwitchNginx] 🚦 Starting health check & routing..."

# Get actual deployment directory (parent of scripts)
DEPLOY_DIR=$(dirname "$(readlink -f "$0")")/..

# Determine port based on directory name
if [[ "$DEPLOY_DIR" == *"tara_green"* ]]; then
  TARGET_PORT="8002"
  NEW_COLOR="green"
  OLD_COLOR="blue"
  echo "🟢 Detected Green Deployment"
elif [[ "$DEPLOY_DIR" == *"tara_dev_backend"* ]]; then
  TARGET_PORT="8001"
  NEW_COLOR="blue"
  OLD_COLOR="green"
  echo "🔵 Detected Blue Deployment"
else
  echo "❌ Unknown deployment directory: $DEPLOY_DIR"
  exit 1
fi

# Health Check
HEALTH_ENDPOINT="http://localhost:$TARGET_PORT/user_management/happy-coder/"

echo "🔍 Checking $HEALTH_ENDPOINT"
RETRY=5
for i in $(seq 1 $RETRY); do
    sleep 5
    if curl -s "$HEALTH_ENDPOINT" | grep -q "Happy Coder, My Job is to be Consistent and Discipline"; then
        echo "✅ Health check passed on $TARGET_PORT"

        # Replace port in nginx template
        sed "s/__PORT__/${TARGET_PORT}/" /tmp/http_template.conf > /etc/nginx/sites-available/http.conf
        ln -sf /etc/nginx/sites-available/http.conf /etc/nginx/sites-enabled/
        rm -f /etc/nginx/sites-enabled/default

        # Update active color
        echo "$NEW_COLOR" > /home/ubuntu/active_color.txt

        # Reload Nginx
        nginx -t && systemctl reload nginx
        echo "✅ Nginx now routing to port ${TARGET_PORT}"
        exit 0
    else
        echo "⏳ Attempt $i/$RETRY: App not ready on $TARGET_PORT"
    fi
done

echo "❌ Health check failed. Deployment not activated"
exit 1




