#!/bin/bash
set -e

echo "[AfterInstall] Setting up Nginx..."
cp /tmp/tara_prod.conf /etc/nginx/sites-available/
ln -sf /etc/nginx/sites-available/tara_prod.conf /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

echo "[AfterInstall] Validating config..."
nginx -t
systemctl restart nginx

echo "[AfterInstall] Ensuring .env exists..."
touch /home/ubuntu/tara_dev_backend/.env
chmod 600 /home/ubuntu/tara_dev_backend/.env
chown ubuntu:ubuntu /home/ubuntu/tara_dev_backend/.env