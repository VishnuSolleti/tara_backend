# #!/bin/bash
# set -e

# echo "📦 Setting up shared Redis & PostgreSQL..."

# SHARED_DIR="/home/ubuntu/shared_services"

# if [ ! -d "$SHARED_DIR" ]; then
#   mkdir -p "$SHARED_DIR"
#   chown ubuntu:ubuntu "$SHARED_DIR"
# fi

# # Create docker-compose file only on
# if [ ! -f "$SHARED_DIR/docker-compose.yml" ]; then
#   cat > "$SHARED_DIR/docker-compose.yml" <<EOF
# version: '3.8'

# services:
#   redis:
#     image: docker.io/sadanandtummuri/redis:7.0
#     container_name: redis_shared
#     restart: always
#     ports:
#       - "6379:6379"
#     networks:
#       - taranet

#   db:
#     image: docker.io/sadanandtummuri/postgres:17.5
#     container_name: postgres_shared
#     restart: always
#     env_file:
#       - .env
#     ports:
#       - "5432:5432"
#     volumes:
#       - postgres_data:/var/lib/postgresql/data
#     healthcheck:
#       test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-postgres}"]
#       interval: 10s
#       timeout: 5s
#       retries: 5
#     networks:
#       - taranet

# volumes:
#   postgres_data:

# networks:
#   taranet:
#     # driver: bridge
#     external: true
#     name: taranet
# EOF
# fi

# cd "$SHARED_DIR"

# # Check if Redis and Postgres containers are already running
# if docker ps --format '{{.Names}}' | grep -q 'redis_shared' && docker ps --format '{{.Names}}' | grep -q 'postgres_shared'; then
#   echo "✅ Shared Redis & PostgreSQL are already running."
# else
#   echo "🚀 Starting shared Redis & PostgreSQL..."
#   docker-compose up -d
#   echo "✅ Shared services started: Redis (6379), PostgreSQL (5432)"
# fi

# #!/bin/bash
# set -e

# echo "📦 Setting up shared Redis & PostgreSQL..."

# SHARED_DIR="/home/ubuntu/shared_services"
# NETWORK_NAME="taranet"

# # ✅ Ensure the Docker network exists (DO NOT recreate if already exists)
# if ! docker network ls --format '{{.Name}}' | grep -wq "$NETWORK_NAME"; then
#   echo "🌐 Creating Docker network '$NETWORK_NAME'..."
#   docker network create --driver bridge "$NETWORK_NAME"
# else
#   echo "✅ Docker network '$NETWORK_NAME' already exists"
# fi

# # ✅ Create shared directory if not exists
# if [ ! -d "$SHARED_DIR" ]; then
#   mkdir -p "$SHARED_DIR"
#   chown ubuntu:ubuntu "$SHARED_DIR"
# fi

# # ✅ Create docker-compose.yml only if not present
# if [ ! -f "$SHARED_DIR/docker-compose.yml" ]; then
#   cat > "$SHARED_DIR/docker-compose.yml" <<EOF
# version: '3.8'

# services:
#   redis:
#     image: docker.io/sadanandtummuri/redis:7.0
#     container_name: redis_shared
#     restart: always
#     ports:
#       - "6379:6379"
#     networks:
#       - taranet

#   db:
#     image: docker.io/sadanandtummuri/postgres:17.5
#     container_name: postgres_shared
#     restart: always
#     env_file:
#       - .env
#     ports:
#       - "5432:5432"
#     volumes:
#       - postgres_data:/var/lib/postgresql/data
#     healthcheck:
#       test: ["CMD-SHELL", "pg_isready -U \${POSTGRES_USER:-postgres}"]
#       interval: 10s
#       timeout: 5s
#       retries: 5
#     networks:
#       - taranet

# volumes:
#   postgres_data:

# networks:
#   taranet:
#     external: true
#     name: taranet
# EOF
# fi

# cd "$SHARED_DIR"

# # ✅ Start containers if not already running
# if docker ps --format '{{.Names}}' | grep -q 'redis_shared' && docker ps --format '{{.Names}}' | grep -q 'postgres_shared'; then
#   echo "✅ Shared Redis & PostgreSQL are already running."
# else
#   echo "🚀 Starting shared Redis & PostgreSQL..."
#   docker-compose up -d
#   echo "✅ Shared services started: Redis (6379), PostgreSQL (5432)"
# fi

# # ✅ Wait for postgres_shared to become healthy and DNS-resolvable
# echo "⏳ Waiting for postgres_shared to be healthy..."

# RETRY=10
# for i in $(seq 1 $RETRY); do
#   if docker exec postgres_shared pg_isready -U postgres > /dev/null 2>&1; then
#     echo "✅ postgres_shared is ready!"
#     break
#   else
#     echo "⏳ postgres_shared not ready yet (try $i/$RETRY)..."
#     sleep 3
#   fi
# done

# echo "🎉 Shared service setup complete!"
#!/bin/bash
set -e

echo "📦 Setting up shared Redis & PostgreSQL..."

SHARED_DIR="/home/ubuntu/shared_services"

# Ensure shared directory exists
if [ ! -d "$SHARED_DIR" ]; then
  mkdir -p "$SHARED_DIR"
  chown ubuntu:ubuntu "$SHARED_DIR"
fi

# Ensure taranet network exists
if ! docker network ls | grep -q "\btaranet\b"; then
  echo "🌐 Creating external Docker network 'taranet'..."
  docker network create --driver bridge taranet
else
  echo "🔁 Docker network 'taranet' already exists."
fi

# Write docker-compose.yml if it doesn't exist
if [ ! -f "$SHARED_DIR/docker-compose.yml" ]; then
  cat > "$SHARED_DIR/docker-compose.yml" <<EOF
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
      test: ["CMD-SHELL", "pg_isready -U \${POSTGRES_USER:-postgres}"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - taranet

volumes:
  postgres_data:

networks:
  taranet:
    external: true
    name: taranet
EOF
fi

cd "$SHARED_DIR"

# Start shared services
echo "🚀 Starting Redis & PostgreSQL shared services..."
docker-compose up -d
echo "✅ Redis & PostgreSQL are now running under 'taranet' network."
