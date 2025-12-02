# Nominatim Cloud Hosting Options (No Local Hardware Required)

## 🎯 Problem

You don't have enough RAM/storage for self-hosted Nominatim locally. Here are cloud-based solutions that don't require your own hardware.

## ✅ Option 1: Cloud VPS with Nominatim (Recommended)

### Providers with Affordable High-RAM Instances

#### 1. **Hetzner** ⭐ Best Value
- **32GB RAM, 500GB SSD**: ~€50/month (~$55)
- **64GB RAM, 1TB SSD**: ~€100/month (~$110)
- **Location**: Germany, Finland, USA
- **Setup**: Easy, one-click Docker

**Why Hetzner**:
- Best price/performance ratio
- High RAM instances available
- Good for Nominatim

**Setup**:
```bash
# 1. Rent Hetzner server
# 2. SSH into server
# 3. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 4. Run Nominatim (see NOMINATIM_SELF_HOSTED_GUIDE.md)
docker-compose up -d
```

#### 2. **OVH**
- **32GB RAM, 500GB SSD**: ~$60/month
- **64GB RAM, 1TB SSD**: ~$120/month
- **Location**: Multiple regions

#### 3. **DigitalOcean**
- **32GB RAM, 640GB SSD**: ~$192/month
- More expensive but easy setup

#### 4. **AWS EC2**
- **r6i.xlarge** (32GB RAM): ~$150/month
- **r6i.2xlarge** (64GB RAM): ~$300/month
- Can use spot instances for ~70% discount

#### 5. **Google Cloud Platform**
- **n1-highmem-4** (26GB RAM): ~$150/month
- **n1-highmem-8** (52GB RAM): ~$300/month

### Cost Comparison

| Provider | 32GB RAM | 64GB RAM | Best For |
|----------|----------|----------|----------|
| **Hetzner** | €50/mo | €100/mo | Best value |
| **OVH** | $60/mo | $120/mo | Good value |
| **DigitalOcean** | $192/mo | $384/mo | Easy setup |
| **AWS** | $150/mo | $300/mo | Enterprise |
| **GCP** | $150/mo | $300/mo | Enterprise |

**Recommendation**: Hetzner or OVH for best value.

---

## ✅ Option 2: Use Smaller Nominatim Instance (Single Country)

Instead of full planet, import only one country at a time:

### Requirements for Single Country
- **RAM**: 8-16GB (much less!)
- **Storage**: 10-50GB per country
- **Cost**: $10-30/month

### Setup Single Country Nominatim

```yaml
# docker-compose.yml (single country)
version: '3.8'

services:
  nominatim:
    image: mediagis/nominatim:4.2
    ports:
      - "8080:8080"
    environment:
      # Import only one country (e.g., UK)
      - PBF_URL=https://download.geofabrik.de/europe/great-britain-latest.osm.pbf
      - IMPORT_WIKIPEDIA=false
      - NOMINATIM_PASSWORD=your_password
    volumes:
      - nominatim-data:/var/lib/postgresql/12/main
    shm_size: 512m  # Less memory needed
```

**Benefits**:
- Much lower RAM requirement (8-16GB)
- Faster import (hours instead of days)
- Cheaper hosting ($10-30/month)
- Can switch countries as needed

**Limitation**:
- Only one country at a time
- Need to re-import to switch countries

---

## ✅ Option 3: Use Managed Nominatim Services

### 1. **Nominatim Hosting Services**

Some companies offer managed Nominatim hosting:

- **Geocode.earth** - Managed Nominatim hosting
- **Mapbox** - Has Nominatim-like service
- **Custom hosting providers**

**Cost**: Varies, usually $50-200/month

---

## ✅ Option 4: Optimize Current Approach (No New Hardware)

### Use Multiple Strategies Together

#### Strategy 1: Better Rate Limiting
- Increase delays to 2-3 seconds
- Add exponential backoff
- Use multiple IPs (different laptops/networks)

#### Strategy 2: Use Nominatim Mirrors
Rotate between multiple public Nominatim instances:

```python
NOMINATIM_URLS = [
    "https://nominatim.openstreetmap.org",
    "https://nominatim.openstreetmap.fr",
    "https://nominatim.mazdermind.de",
    "https://nominatim.gentpoortstraat.be",
]

# Rotate on 403 errors
```

#### Strategy 3: Cache Aggressively
- Cache all successful validations
- Reuse cached results
- Only call API for new addresses

#### Strategy 4: Batch Processing
- Process addresses in batches
- Wait longer between batches
- Use different IPs for different batches

---

## ✅ Option 5: Use Alternative Services (No Hardware)

### BigDataCloud (50k/month free)

```python
def check_with_bigdatacloud(address: str) -> dict:
    """Use BigDataCloud instead of Nominatim"""
    url = "https://api.bigdatacloud.net/data/forward-geocode-client"
    params = {"query": address}
    response = requests.get(url, params=params, timeout=5)
    # Process response...
```

**Pros**:
- No hardware needed
- 50k free requests/month
- No rate limits for client-side

**Cons**:
- Different API format
- Need to modify scoring logic
- Monthly limit

### Mapbox (100k/month free)

```python
def check_with_mapbox(address: str, api_key: str) -> dict:
    """Use Mapbox instead of Nominatim"""
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{address}.json"
    params = {"access_token": api_key}
    response = requests.get(url, params=params, timeout=5)
    # Process response...
```

**Pros**:
- 100k free requests/month
- Excellent coverage
- No hardware needed

**Cons**:
- Requires API key
- Different response format
- Need to modify scoring

---

## 📊 Comparison of All Options

| Option | Cost/Month | RAM Needed | Setup Difficulty | Rate Limits |
|--------|------------|------------|------------------|-------------|
| **Cloud VPS (Hetzner)** | $55-110 | 32-64GB | Medium | None |
| **Single Country VPS** | $10-30 | 8-16GB | Medium | None |
| **BigDataCloud** | Free | 0GB | Easy | 50k/month |
| **Mapbox** | Free | 0GB | Easy | 100k/month |
| **Optimize Current** | Free | 0GB | Easy | 1 req/sec |
| **Multiple IPs** | Free | 0GB | Easy | 1 req/sec per IP |

---

## 🎯 Recommended Solutions (Based on Budget)

### Budget: $0 (Free)
1. **Optimize current approach** (better rate limiting)
2. **Use multiple IPs** (different laptops/networks)
3. **Use BigDataCloud** (50k/month free)
4. **Use Mapbox** (100k/month free)

### Budget: $10-30/month
1. **Single country Nominatim on cheap VPS**
   - Hetzner: 8GB RAM instance (~€10/month)
   - Import one country at a time
   - Switch countries as needed

### Budget: $50-110/month
1. **Full Nominatim on Hetzner/OVH**
   - 32-64GB RAM instance
   - Full planet or multiple countries
   - Unlimited requests

---

## 🚀 Quick Start: Single Country Nominatim on Cheap VPS

### Step 1: Rent Cheap VPS
- **Hetzner**: 8GB RAM, 80GB SSD (~€10/month)
- **DigitalOcean**: 8GB RAM, 160GB SSD (~$48/month)
- **Vultr**: 8GB RAM, 160GB SSD (~$40/month)

### Step 2: Setup Nominatim (Single Country)

```bash
# SSH into VPS
ssh root@your-server-ip

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Create docker-compose.yml
cat > docker-compose.yml <<EOF
version: '3.8'
services:
  nominatim:
    image: mediagis/nominatim:4.2
    ports:
      - "8080:8080"
    environment:
      - PBF_URL=https://download.geofabrik.de/europe/great-britain-latest.osm.pbf
      - IMPORT_WIKIPEDIA=false
      - NOMINATIM_PASSWORD=secure_password
    volumes:
      - nominatim-data:/var/lib/postgresql/12/main
    shm_size: 512m
volumes:
  nominatim-data:
EOF

# Start Nominatim
docker-compose up -d

# Watch logs
docker-compose logs -f
```

### Step 3: Update Your Script

```bash
# Set your Nominatim URL
export NOMINATIM_URL="http://your-server-ip:8080/reverse"

# Run script
python3 generate_and_test_addresses.py --country "United Kingdom"
```

**Import time**: 2-4 hours for UK (vs days for full planet)

---

## 💡 Pro Tips

### Tip 1: Start Small
- Start with single country Nominatim
- Test if it works for your needs
- Upgrade to full planet later if needed

### Tip 2: Use Spot Instances
- AWS/GCP spot instances: 70% discount
- Good for testing
- Can be interrupted (not for production)

### Tip 3: Share Costs
- Split VPS cost with team
- Use for multiple projects
- Share resources

### Tip 4: Optimize First
- Try optimizing current approach first
- Use multiple IPs
- Better caching
- May not need new hardware

---

## ✅ Summary

**If you don't have enough RAM/storage**:

1. **Cheapest**: Optimize current approach + multiple IPs (Free)
2. **Budget**: Single country Nominatim on cheap VPS ($10-30/month)
3. **Best**: Full Nominatim on Hetzner/OVH ($50-110/month)
4. **Alternative**: Use BigDataCloud/Mapbox (Free, but needs code changes)

**Recommendation**: Start with **single country Nominatim on Hetzner** (~€10/month) - much lower requirements, still unlimited requests for that country.

