#!/bin/bash
# Quick setup script for self-hosted Nominatim using Docker

set -e

echo "🚀 Setting up self-hosted Nominatim with Docker"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    echo "✅ Docker installed. Please log out and back in, then run this script again."
    exit 0
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Installing..."
    sudo apt-get update
    sudo apt-get install -y docker-compose-plugin
fi

echo "📝 Creating docker-compose.yml..."

# Create docker-compose.yml
cat > docker-compose.yml <<'EOF'
version: '3.8'

services:
  nominatim:
    image: mediagis/nominatim:4.2
    container_name: nominatim
    ports:
      - "8080:8080"  # Nominatim API
    environment:
      # Start with a small country for testing (change to your country)
      - PBF_URL=https://download.geofabrik.de/europe/monaco-latest.osm.pbf
      - REPLICATION_URL=https://download.geofabrik.de/europe/monaco-updates
      - IMPORT_WIKIPEDIA=false
      - NOMINATIM_PASSWORD=very_secure_password_change_me
      - OSM2PGSQL_CACHE=2048  # 2GB cache (adjust based on your RAM)
    volumes:
      - nominatim-data:/var/lib/postgresql/12/main
      - nominatim-flatnode:/flatnodes
    shm_size: 1g
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/status"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  nominatim-data:
  nominatim-flatnode:
EOF

echo "✅ docker-compose.yml created"
echo ""
echo "📋 Configuration:"
echo "   - API will be available at: http://localhost:8080"
echo "   - Starting with Monaco (small, fast import ~1-2 hours)"
echo "   - To change country, edit PBF_URL in docker-compose.yml"
echo ""
echo "🌍 Available countries: https://download.geofabrik.de/"
echo ""
read -p "Press Enter to start Nominatim (this will download ~100MB and take 1-2 hours to import)..."

# Start Nominatim
echo ""
echo "🚀 Starting Nominatim container..."
docker-compose up -d

echo ""
echo "⏳ Waiting for Nominatim to start..."
sleep 10

# Check status
echo ""
echo "📊 Checking status..."
docker-compose ps

echo ""
echo "📝 Viewing logs (press Ctrl+C to exit, container will keep running)..."
echo "   To view logs later: docker-compose logs -f nominatim"
echo ""
sleep 5

docker-compose logs -f nominatim

