# #!/bin/bash
# set -e

# echo "[ApplicationStop] Stopping containers..."
# cd /home/ubuntu/tara_dev_backend
# docker-compose down || true

#!/bin/bash
set -e

cd /home/ubuntu/tara_green || exit

echo "[ApplicationStop] Stopping containers..."
docker-compose down || true