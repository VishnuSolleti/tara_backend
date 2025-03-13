#!/usr/bin/env bash

set -e  # Exit on error

echo "Starting Django application..."

VENV_DIR="/home/ubuntu/TaraFirst/myenv"
APP_DIR="/home/ubuntu/TaraFirst"

# Activate the virtual environment
source "$VENV_DIR/bin/activate"

# Navigate to the app directory
cd "$APP_DIR"

# Run Django migrations and collect static files
python manage.py makemigrations --noinput
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# Restart Gunicorn and Nginx
sudo systemctl restart gunicorn
sudo systemctl restart nginx

echo "Django application started successfully!"
