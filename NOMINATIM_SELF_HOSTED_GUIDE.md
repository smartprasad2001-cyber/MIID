# Self-Hosted Nominatim Setup Guide

## 🎯 Why Self-Hosted Nominatim?

- **No rate limits** - Unlimited requests
- **No policy restrictions** - Full control
- **Faster** - No network latency to external API
- **Privacy** - Your data stays on your server
- **Reliability** - No dependency on external services

## 📋 Requirements

### Hardware Requirements:
- **RAM**: 32GB minimum (64GB recommended)
- **Storage**: 500GB+ SSD (1TB+ recommended for full planet)
- **CPU**: 4+ cores (8+ recommended)
- **Network**: Good internet connection for initial data download

### Software Requirements:
- **OS**: Ubuntu 20.04/22.04 or Debian 11/12 (recommended)
- **Docker** (easiest method) OR
- **PostgreSQL 14+**, **PostGIS**, **Python 3.8+** (manual install)

## 🚀 Method 1: Docker (EASIEST - Recommended)

### Step 1: Install Docker

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify installation
docker --version
```

### Step 2: Create Docker Compose File

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  nominatim:
    image: mediagis/nominatim:4.2
    container_name: nominatim
    ports:
      - "8080:8080"  # Nominatim API
      - "5432:5432"  # PostgreSQL (optional, for direct DB access)
    environment:
      - PBF_URL=https://download.geofabrik.de/europe/monaco-latest.osm.pbf
      - REPLICATION_URL=https://download.geofabrik.de/europe/monaco-updates
      - IMPORT_WIKIPEDIA=false
      - NOMINATIM_PASSWORD=very_secure_password
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
```

### Step 3: Start Nominatim

```bash
# Start the container
docker-compose up -d

# Watch the logs (initial import takes hours/days)
docker-compose logs -f nominatim
```

### Step 4: Wait for Import

- **Small country** (Monaco): ~1-2 hours
- **Medium country** (UK): ~12-24 hours
- **Large country** (USA): ~3-7 days
- **Full planet**: ~2-4 weeks

### Step 5: Test Your Instance

```bash
# Test the API
curl "http://localhost:8080/search?q=London&format=json"

# Check status
curl "http://localhost:8080/status"
```

## 🛠️ Method 2: Manual Installation (More Control)

### Step 1: Install Dependencies

```bash
sudo apt update
sudo apt install -y \
    build-essential \
    cmake \
    libboost-dev \
    libboost-system-dev \
    libboost-filesystem-dev \
    libexpat1-dev \
    zlib1g-dev \
    libbz2-dev \
    libpq-dev \
    postgresql-14-postgis-3 \
    postgresql-contrib-14 \
    apache2 \
    php \
    php-pgsql \
    libapache2-mod-php \
    php-intl \
    python3 \
    python3-pip \
    python3-psycopg2 \
    python3-setuptools \
    python3-dev \
    python3-tidylib \
    git
```

### Step 2: Install Nominatim

```bash
# Clone Nominatim
cd /opt
sudo git clone --recursive https://github.com/osm-search/Nominatim.git
cd Nominatim
sudo git checkout 4.2  # Use stable version

# Build Nominatim
sudo mkdir build
cd build
sudo cmake ..
sudo make
```

### Step 3: Configure PostgreSQL

```bash
# Create database
sudo -u postgres createuser -s nominatim
sudo -u postgres createdb -O nominatim -E UTF8 nominatim
sudo -u postgres psql -d nominatim -c "CREATE EXTENSION IF NOT EXISTS postgis;"
sudo -u postgres psql -d nominatim -c "CREATE EXTENSION IF NOT EXISTS hstore;"
```

### Step 4: Download OSM Data

```bash
# For a specific country (example: Monaco)
cd /opt/Nominatim
wget https://download.geofabrik.de/europe/monaco-latest.osm.pbf

# Or download full planet (VERY LARGE - 60GB+)
# wget https://planet.openstreetmap.org/pbf/planet-latest.osm.pbf
```

### Step 5: Import Data

```bash
# Set up configuration
sudo mkdir -p /var/lib/nominatim
sudo chown nominatim:nominatim /var/lib/nominatim

# Import (this takes HOURS/DAYS)
sudo -u nominatim ./utils/setup.php --osm-file /opt/Nominatim/monaco-latest.osm.pbf --all
```

### Step 6: Configure Apache

```bash
# Copy Apache configuration
sudo cp /opt/Nominatim/build/module/nominatim.so /usr/lib/apache2/modules/
sudo cp /opt/Nominatim/build/settings/local.php /var/lib/nominatim/settings/

# Create Apache virtual host
sudo tee /etc/apache2/sites-available/nominatim.conf <<EOF
<VirtualHost *:80>
    ServerName nominatim.local
    ServerAdmin admin@localhost
    DocumentRoot /opt/Nominatim/build/website
    <Directory /opt/Nominatim/build/website>
        Options FollowSymLinks
        AllowOverride None
        Require all granted
    </Directory>
    AddType application/x-httpd-php .php
</VirtualHost>
EOF

# Enable site
sudo a2ensite nominatim.conf
sudo a2enmod php
sudo systemctl restart apache2
```

## 🔧 Configuration Options

### For Docker Setup:

Edit `docker-compose.yml` to change:

```yaml
environment:
  # Change country/region
  - PBF_URL=https://download.geofabrik.de/europe/united-kingdom-latest.osm.pbf
  
  # Enable Wikipedia data (slower import, more data)
  - IMPORT_WIKIPEDIA=true
  
  # Set custom password
  - NOMINATIM_PASSWORD=your_secure_password
  
  # Memory limits
  - OSM2PGSQL_CACHE=2048  # 2GB cache
```

### For Manual Setup:

Edit `/var/lib/nominatim/settings/local.php`:

```php
<?php
// Database
@define('CONST_Database_DSN', 'pgsql://nominatim:password@localhost/nominatim');

// Memory
@define('CONST_Osm2pgsql_Cache', 2048);  // 2GB

// Flat node storage (faster, more disk space)
@define('CONST_Flatnode_File', '/var/lib/nominatim/flatnode');
@define('CONST_Use_Flatnode_File', true);
```

## 🌍 Choosing OSM Data

### Small Regions (Fast Import):
- Monaco: ~1 hour
- Luxembourg: ~2 hours
- Small countries: ~4-8 hours

### Medium Regions:
- UK: ~12-24 hours
- France: ~2-3 days
- Germany: ~3-4 days

### Large Regions:
- USA: ~1-2 weeks
- Full planet: ~2-4 weeks

**Download URLs:**
- Geofabrik (by country): https://download.geofabrik.de/
- Full planet: https://planet.openstreetmap.org/pbf/

## 🔌 Integrating with Your Script

### Update `generate_address_cache.py`:

```python
# Change NOMINATIM_URL to your self-hosted instance
NOMINATIM_URL = os.getenv("NOMINATIM_URL", "http://localhost:8080/reverse")

# For search endpoint (in rewards.py):
# Change to: "http://localhost:8080/search"
```

### Or use environment variable:

```bash
# Set your self-hosted Nominatim URL
export NOMINATIM_URL="http://your-server-ip:8080/reverse"

# Run script
python3 generate_address_cache.py
```

### Update `rewards.py`:

```python
# In check_with_nominatim function, change:
url = "http://localhost:8080/search"  # Your self-hosted instance
```

## 📊 Performance Tuning

### PostgreSQL Tuning:

Edit `/etc/postgresql/14/main/postgresql.conf`:

```conf
shared_buffers = 8GB
effective_cache_size = 24GB
maintenance_work_mem = 2GB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 50MB
min_wal_size = 1GB
max_wal_size = 4GB
```

Restart PostgreSQL:
```bash
sudo systemctl restart postgresql
```

## 🔄 Keeping Data Updated

### For Docker:

```bash
# Add update script
docker exec nominatim sudo -u nominatim ./utils/update.php --import-file /app/data/updates.osc
```

### For Manual:

```bash
# Set up replication
sudo -u nominatim ./utils/setup.php --osm-file data.osm.pbf --all --osm2pgsql-cache 2048

# Update daily
sudo -u nominatim ./utils/update.php --import-file updates.osc
```

## 🚨 Troubleshooting

### Out of Memory:
- Reduce `OSM2PGSQL_CACHE` in Docker
- Add swap space: `sudo fallocate -l 8G /swapfile && sudo chmod 600 /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile`

### Import Too Slow:
- Use flat node file
- Increase PostgreSQL shared_buffers
- Use SSD storage
- Import smaller region first

### Connection Refused:
- Check firewall: `sudo ufw allow 8080`
- Check Docker logs: `docker-compose logs nominatim`
- Verify service is running: `docker ps`

## 💰 Cost Estimate

### Cloud Hosting (AWS/GCP/Azure):
- **Small instance** (32GB RAM, 500GB SSD): ~$150-300/month
- **Medium instance** (64GB RAM, 1TB SSD): ~$300-600/month
- **Large instance** (128GB RAM, 2TB SSD): ~$600-1200/month

### Self-Hosted Server:
- **Dedicated server** (Hetzner, OVH): ~$50-200/month
- **VPS** (rarely enough resources): Not recommended

## ✅ Quick Start (Docker - Small Country)

```bash
# 1. Create docker-compose.yml (see above)
# 2. Start
docker-compose up -d

# 3. Watch progress
docker-compose logs -f

# 4. Test when ready
curl "http://localhost:8080/search?q=test&format=json"

# 5. Update your script
export NOMINATIM_URL="http://localhost:8080/reverse"
python3 generate_address_cache.py
```

## 📚 Resources

- **Official Docs**: https://nominatim.org/release-docs/latest/
- **Docker Image**: https://github.com/mediagis/nominatim-docker
- **OSM Data**: https://download.geofabrik.de/
- **Community**: https://help.openstreetmap.org/tags/nominatim/

## 🎯 Recommendation

**For your use case (address validation):**
1. Start with **Docker method** (easiest)
2. Import **one country first** (test with Monaco or Luxembourg)
3. Once working, expand to more countries
4. Use **cloud instance** (AWS/GCP) if you don't have a server
5. **Budget**: ~$100-200/month for a small-medium instance

This will give you unlimited Nominatim requests with no rate limits! 🚀

