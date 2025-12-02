# Free Geocoding Alternatives - Detailed Guide

## 🎯 Overview

These are free geocoding services that don't require your own hardware. However, they have different APIs and response formats, so you'll need to modify your code.

---

## 1. BigDataCloud ⭐ Best Free Option

### What It Is
A free geocoding API with generous limits and no rate limits for client-side use.

### Free Tier Details
- **50,000 requests/month** (server-side)
- **Unlimited requests** (client-side/browser)
- **No rate limits** for client-side
- **No API key required** for basic usage

### API Endpoints

#### Forward Geocoding (Address → Coordinates)
```python
url = "https://api.bigdatacloud.net/data/forward-geocode-client"
params = {
    "query": "26 High Street, Oxford, OX1 1DP, United Kingdom",
    "localityLanguage": "en"
}
```

#### Reverse Geocoding (Coordinates → Address)
```python
url = "https://api.bigdatacloud.net/data/reverse-geocode-client"
params = {
    "latitude": 51.7520,
    "longitude": -1.2577,
    "localityLanguage": "en"
}
```

### Response Format

```json
{
  "results": [
    {
      "geometry": {
        "latitude": 51.7520,
        "longitude": -1.2577
      },
      "formattedAddress": "26 High Street, Oxford OX1 1DP, UK",
      "locality": "Oxford",
      "postcode": "OX1 1DP",
      "country": "United Kingdom",
      "countryCode": "GB",
      "confidence": 0.95
    }
  ]
}
```

### Implementation Example

```python
import requests
import os

def check_with_bigdatacloud(address: str) -> dict:
    """
    Validate address using BigDataCloud API.
    Returns: dict with 'score' and 'details' similar to Nominatim format
    """
    try:
        url = "https://api.bigdatacloud.net/data/forward-geocode-client"
        params = {
            "query": address,
            "localityLanguage": "en"
        }
        
        # No API key needed for free tier
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code != 200:
            return 0.0
        
        data = response.json()
        
        if not data.get("results"):
            return 0.0
        
        result = data["results"][0]
        confidence = result.get("confidence", 0)
        
        # Convert confidence to score (similar to Nominatim scoring)
        # BigDataCloud doesn't provide bounding box areas, so we use confidence
        if confidence >= 0.9:
            score = 1.0  # High confidence = perfect match
        elif confidence >= 0.7:
            score = 0.9  # Good confidence
        elif confidence >= 0.5:
            score = 0.8  # Medium confidence
        elif confidence >= 0.3:
            score = 0.7  # Low confidence
        else:
            score = 0.3  # Very low confidence
        
        return {
            "score": score,
            "confidence": confidence,
            "formatted_address": result.get("formattedAddress"),
            "country": result.get("country"),
            "locality": result.get("locality"),
            "postcode": result.get("postcode")
        }
        
    except requests.exceptions.Timeout:
        return "TIMEOUT"
    except Exception as e:
        print(f"BigDataCloud error: {e}")
        return 0.0
```

### Pros
- ✅ 50k free requests/month
- ✅ No rate limits for client-side
- ✅ No API key required
- ✅ Good coverage
- ✅ Fast responses

### Cons
- ❌ Different response format (no bounding box areas)
- ❌ Uses confidence scores instead of area-based scoring
- ❌ Monthly limit (50k requests)
- ❌ Need to modify scoring logic

### How to Use in Your Code

**Step 1**: Replace `check_with_nominatim` in `rewards.py`:

```python
# Option 1: Add as alternative function
def check_with_bigdatacloud(address: str, validator_uid: int, miner_uid: int, 
                            seed_address: str, seed_name: str) -> Union[float, str, dict]:
    # Use the implementation above
    pass

# Option 2: Modify existing function to support both
def check_with_nominatim(address: str, validator_uid: int, miner_uid: int,
                         seed_address: str, seed_name: str, 
                         use_bigdatacloud: bool = False) -> Union[float, str, dict]:
    if use_bigdatacloud:
        return check_with_bigdatacloud(address, validator_uid, miner_uid, seed_address, seed_name)
    else:
        # Original Nominatim code
        ...
```

**Step 2**: Update your script to use BigDataCloud:

```python
# In generate_and_test_addresses.py
api_result = check_with_nominatim(
    address=address,
    validator_uid=101,
    miner_uid=501,
    seed_address=country,
    seed_name="Generator",
    use_bigdatacloud=True  # Use BigDataCloud instead
)
```

---

## 2. Mapbox Geocoding API

### What It Is
A powerful geocoding service by Mapbox with a generous free tier.

### Free Tier Details
- **100,000 requests/month** (very generous!)
- **Rate limit**: Varies by plan
- **Requires API key** (free to get)
- **Excellent coverage** and accuracy

### Getting API Key

1. Sign up at https://www.mapbox.com
2. Go to Account → Access Tokens
3. Copy your default public token
4. Use it in API requests

### API Endpoints

#### Forward Geocoding
```python
url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{address}.json"
params = {
    "access_token": "your-api-key-here",
    "country": "GB",  # Optional: restrict to country
    "limit": 1
}
```

#### Reverse Geocoding
```python
url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{lon},{lat}.json"
params = {
    "access_token": "your-api-key-here",
    "limit": 1
}
```

### Response Format

```json
{
  "features": [
    {
      "place_name": "26 High Street, Oxford, England OX1 1DP, United Kingdom",
      "center": [-1.2577, 51.7520],
      "geometry": {
        "type": "Point",
        "coordinates": [-1.2577, 51.7520]
      },
      "properties": {
        "accuracy": "point",
        "confidence": 0.9
      },
      "bbox": [-1.2580, 51.7518, -1.2574, 51.7522]  # Bounding box!
    }
  ]
}
```

### Implementation Example

```python
import requests
import os

def check_with_mapbox(address: str, api_key: str) -> dict:
    """
    Validate address using Mapbox API.
    Returns: dict with 'score' and 'details'
    """
    try:
        # URL encode address
        import urllib.parse
        encoded_address = urllib.parse.quote(address)
        
        url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{encoded_address}.json"
        params = {
            "access_token": api_key,
            "limit": 1,
            "types": "address"  # Only return addresses, not POIs
        }
        
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code != 200:
            if response.status_code == 401:
                print("Invalid Mapbox API key")
            return 0.0
        
        data = response.json()
        
        if not data.get("features"):
            return 0.0
        
        feature = data["features"][0]
        bbox = feature.get("bbox")
        
        # Calculate bounding box area (similar to Nominatim)
        if bbox:
            # bbox = [min_lon, min_lat, max_lon, max_lat]
            width = (bbox[2] - bbox[0]) * 111320 * math.cos(math.radians((bbox[1] + bbox[3]) / 2))
            height = (bbox[3] - bbox[1]) * 111320
            area_m2 = width * height
        else:
            # No bounding box, use confidence
            confidence = feature.get("properties", {}).get("confidence", 0)
            if confidence >= 0.9:
                area_m2 = 50  # Assume small area for high confidence
            else:
                area_m2 = 10000  # Larger area for low confidence
        
        # Score based on area (same as Nominatim)
        if area_m2 < 100:
            score = 1.0
        elif area_m2 < 1000:
            score = 0.9
        elif area_m2 < 10000:
            score = 0.8
        elif area_m2 < 100000:
            score = 0.7
        else:
            score = 0.3
        
        return {
            "score": score,
            "min_area": area_m2,
            "formatted_address": feature.get("place_name"),
            "bbox": bbox
        }
        
    except requests.exceptions.Timeout:
        return "TIMEOUT"
    except Exception as e:
        print(f"Mapbox error: {e}")
        return 0.0
```

### Pros
- ✅ 100k free requests/month (very generous!)
- ✅ Provides bounding box (can use similar scoring)
- ✅ Excellent coverage and accuracy
- ✅ Well-documented

### Cons
- ❌ Requires API key
- ❌ Different response format
- ❌ Monthly limit (100k requests)
- ❌ Need to modify code

### How to Use

**Step 1**: Get API key from https://www.mapbox.com

**Step 2**: Set environment variable:
```bash
export MAPBOX_API_KEY="your-api-key-here"
```

**Step 3**: Modify `rewards.py` to use Mapbox:
```python
import os
import math

def check_with_mapbox(address: str) -> dict:
    api_key = os.getenv("MAPBOX_API_KEY")
    if not api_key:
        return 0.0
    # Use implementation above
    ...
```

---

## 3. Geoapify

### What It Is
A geocoding API with good free tier and higher rate limits than Nominatim.

### Free Tier Details
- **3,000 credits/day** (90k/month)
- **5 requests/second** (better than Nominatim's 1/sec)
- **Requires API key** (free to get)

### Getting API Key

1. Sign up at https://www.geoapify.com
2. Get free API key from dashboard
3. Use in requests

### API Endpoints

```python
url = "https://api.geoapify.com/v1/geocode/search"
params = {
    "text": address,
    "apiKey": "your-api-key",
    "limit": 1
}
```

### Response Format

```json
{
  "features": [
    {
      "properties": {
        "formatted": "26 High Street, Oxford OX1 1DP, United Kingdom",
        "country": "United Kingdom",
        "city": "Oxford",
        "postcode": "OX1 1DP"
      },
      "geometry": {
        "coordinates": [-1.2577, 51.7520]
      },
      "bbox": [-1.2580, 51.7518, -1.2574, 51.7522]
    }
  ]
}
```

### Pros
- ✅ 3k credits/day (90k/month)
- ✅ 5 req/sec (better than Nominatim)
- ✅ Provides bounding box
- ✅ Good coverage

### Cons
- ❌ Requires API key
- ❌ Daily limits
- ❌ Different response format
- ❌ Need to modify code

---

## 4. Geocode.xyz

### What It Is
A simple geocoding API with free tier.

### Free Tier Details
- **1 request/second** (same as Nominatim)
- **Limited free requests**
- **No API key required** for basic usage

### API Endpoints

```python
url = "https://geocode.xyz"
params = {
    "locate": address,
    "json": 1
}
```

### Response Format

```json
{
  "standard": {
    "addresst": "26 High Street",
    "city": "Oxford",
    "postal": "OX1 1DP",
    "countryname": "United Kingdom"
  },
  "latt": "51.7520",
  "longt": "-1.2577"
}
```

### Pros
- ✅ Simple API
- ✅ No API key needed
- ✅ 1 req/sec (same as Nominatim)

### Cons
- ❌ Limited free tier
- ❌ No bounding box
- ❌ Less coverage
- ❌ Different response format

---

## 📊 Comparison Table

| Service | Free Tier | Rate Limit | Bounding Box | API Key | Best For |
|---------|-----------|------------|--------------|---------|----------|
| **BigDataCloud** | 50k/month | None (client) | ❌ No | ❌ No | Best free option |
| **Mapbox** | 100k/month | Varies | ✅ Yes | ✅ Yes | Highest free tier |
| **Geoapify** | 90k/month | 5 req/sec | ✅ Yes | ✅ Yes | Better rate limit |
| **Geocode.xyz** | Limited | 1 req/sec | ❌ No | ❌ No | Simple API |

---

## 🔧 Implementation Strategy

### Option 1: Fallback Chain (Recommended)

Try services in order, fallback if one fails:

```python
def check_address_with_fallback(address: str) -> dict:
    """Try multiple services, fallback on failure"""
    
    # Try Nominatim first (if not blocked)
    result = check_with_nominatim(address, ...)
    if isinstance(result, dict) and result.get("score", 0) > 0:
        return result
    
    # Fallback to BigDataCloud
    result = check_with_bigdatacloud(address)
    if isinstance(result, dict) and result.get("score", 0) > 0:
        return result
    
    # Fallback to Mapbox (if API key set)
    mapbox_key = os.getenv("MAPBOX_API_KEY")
    if mapbox_key:
        result = check_with_mapbox(address, mapbox_key)
        if isinstance(result, dict) and result.get("score", 0) > 0:
            return result
    
    return 0.0
```

### Option 2: Service Selection

Choose service based on environment variable:

```python
GEOCODING_SERVICE = os.getenv("GEOCODING_SERVICE", "nominatim")

if GEOCODING_SERVICE == "bigdatacloud":
    result = check_with_bigdatacloud(address)
elif GEOCODING_SERVICE == "mapbox":
    result = check_with_mapbox(address, api_key)
else:
    result = check_with_nominatim(address, ...)
```

### Option 3: Rotate Services

Use different services for different requests:

```python
services = ["nominatim", "bigdatacloud", "mapbox"]
current_service = services[request_count % len(services)]

if current_service == "bigdatacloud":
    result = check_with_bigdatacloud(address)
elif current_service == "mapbox":
    result = check_with_mapbox(address, api_key)
else:
    result = check_with_nominatim(address, ...)
```

---

## ✅ Recommended Approach

### For Maximum Free Requests

**Use Multiple Services Together**:

1. **Primary**: BigDataCloud (50k/month)
2. **Secondary**: Mapbox (100k/month)
3. **Fallback**: Nominatim (if not blocked)

**Total**: ~150k free requests/month!

### Implementation

```python
def check_address_multi_service(address: str) -> dict:
    """Use multiple free services with fallback"""
    
    # Service 1: BigDataCloud (50k/month)
    result = check_with_bigdatacloud(address)
    if isinstance(result, dict) and result.get("score", 0) >= 0.99:
        return result
    
    # Service 2: Mapbox (100k/month, if API key set)
    mapbox_key = os.getenv("MAPBOX_API_KEY")
    if mapbox_key:
        result = check_with_mapbox(address, mapbox_key)
        if isinstance(result, dict) and result.get("score", 0) >= 0.99:
            return result
    
    # Service 3: Nominatim (fallback, if not blocked)
    result = check_with_nominatim(address, ...)
    return result
```

---

## 🚀 Quick Start: BigDataCloud

### Step 1: Create Alternative Function

Add to `rewards.py`:

```python
def check_with_bigdatacloud(address: str) -> dict:
    # Use implementation from above
    ...
```

### Step 2: Update Script

Modify `generate_and_test_addresses.py`:

```python
# Option 1: Use BigDataCloud instead
api_result = check_with_bigdatacloud(address)

# Option 2: Use fallback
api_result = check_address_with_fallback(address)
```

### Step 3: Run Script

```bash
# No API key needed for BigDataCloud
python3 generate_and_test_addresses.py --country "United Kingdom"
```

---

## ⚠️ Important Notes

### Scoring Differences

- **Nominatim**: Uses bounding box area (< 100 m² = 1.0)
- **BigDataCloud**: Uses confidence (≥ 0.9 = 1.0)
- **Mapbox**: Can calculate area from bbox (similar to Nominatim)

### Code Modifications Required

All alternatives require:
1. New API functions
2. Different response parsing
3. Modified scoring logic (except Mapbox)
4. Error handling for different formats

### Rate Limits Still Apply

- BigDataCloud: 50k/month limit
- Mapbox: 100k/month limit
- Geoapify: 3k/day limit

**Only self-hosted Nominatim has NO limits!**

---

## 📝 Summary

**Best Free Options**:

1. **BigDataCloud** - 50k/month, no API key, easy to use
2. **Mapbox** - 100k/month, provides bbox, best free tier
3. **Geoapify** - 90k/month, 5 req/sec, good alternative

**Recommendation**: Use **BigDataCloud + Mapbox** together for ~150k free requests/month with fallback to Nominatim.

All require code modifications, but provide generous free tiers without needing your own hardware!

