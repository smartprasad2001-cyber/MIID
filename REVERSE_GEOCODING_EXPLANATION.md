# Reverse Geocoding in `generate_address_cache_priority.py`

## What is Reverse Geocoding?

**Reverse Geocoding** converts **coordinates (latitude, longitude)** → **Address String**

It's the opposite of forward geocoding:
- **Forward Geocoding:** Address → Coordinates
- **Reverse Geocoding:** Coordinates → Address

---

## The Function: `reverse_geocode()`

Located at **line 476** in `generate_address_cache_priority.py`:

```python
def reverse_geocode(lat: float, lon: float, zoom: int = 19, verbose: bool = False, max_retries: int = 3) -> dict:
    """
    Reverse geocode coordinates to get address from Nominatim.
    
    Args:
        lat: Latitude
        lon: Longitude
        zoom: Zoom level (19 = building level detail)
        verbose: Print debug info
        max_retries: Number of retry attempts
        
    Returns:
        dict with address components and display_name
    """
    params = {
        "format": "json",
        "lat": str(lat),      # ← Input: Coordinates
        "lon": str(lon),
        "zoom": str(zoom),    # 19 = building-level detail
        "addressdetails": "1",
        "extratags": "1",
        "namedetails": "1",
        "accept-language": "en"
    }
    headers = {"User-Agent": USER_AGENT}
    
    # Call Nominatim reverse endpoint
    url = "https://nominatim.openstreetmap.org/reverse"
    # Returns address string and components
```

**Example:**
- **Input:** `lat=34.5284, lon=69.1717`
- **Output:** 
  ```json
  {
    "display_name": "Seh Aqrab Road, Kabul, 1006, Afghanistan",
    "address": {
      "road": "Seh Aqrab Road",
      "city": "Kabul",
      "postcode": "1006",
      "country": "Afghanistan"
    }
  }
  ```

---

## Role in `generate_address_cache_priority.py`

### The Complete Workflow:

```
1. City Name
   ↓
2. Query Overpass API (get OSM nodes with coordinates)
   ↓
3. Extract coordinates from nodes: (lat, lon)
   ↓
4. Reverse Geocode coordinates → Address string
   ↓
5. Validate address with Nominatim
   ↓
6. Save to cache
```

### Step-by-Step:

#### **Step 1: Query Overpass** (line 307)
```python
def fetch_nodes_from_overpass_bbox(bbox):
    # Query Overpass API for OSM nodes in bounding box
    # Returns nodes with:
    #   - lat, lon (coordinates)
    #   - tags (addr:housenumber, addr:street, etc.)
```

**What Overpass Returns:**
```json
{
  "type": "node",
  "id": 123456,
  "lat": 34.5284,
  "lon": 69.1717,
  "tags": {
    "addr:housenumber": "8",
    "addr:street": "جاده شهید مزاری",
    "addr:city": "کابل"
  }
}
```

#### **Step 2: Extract Coordinates** (line 1223-1315)
```python
for node in nodes:
    lat = node.get("lat")
    lon = node.get("lon")
    
    # Option 1: Validate locally (if node has complete tags)
    if has_complete_address_tags(node):
        # Skip reverse geocoding - use tags directly
        address = build_address_from_tags(node)
    
    # Option 2: Use reverse geocoding (line 1315)
    else:
        nom = reverse_geocode(lat, lon, zoom=19)
        address = nom.get("display_name")
```

#### **Step 3: Reverse Geocode** (line 1315)
```python
# Use reverse geocoding to get Nominatim's version of the address
nom = reverse_geocode(lat, lon, zoom=19, verbose=verbose and processed % 10 == 0)

if nom and nom.get("display_name"):
    nom_display = nom.get("display_name")
    stats["reverse_geocoded"] += 1
    # Use this address string
```

**Why Reverse Geocode?**

1. **OSM nodes have raw tags** - May not be formatted correctly
2. **Nominatim standardizes** - Returns properly formatted address
3. **Validation** - Ensures address exists in Nominatim's index
4. **Consistency** - All addresses use same format

---

## When is Reverse Geocoding Used?

### ✅ **Used When:**
1. **Node has incomplete tags** - Missing some address components
2. **Need Nominatim validation** - Ensure address is in Nominatim's index
3. **Standardization needed** - Want Nominatim's formatted version

### ❌ **Skipped When:**
1. **Node has complete tags** - Can build address directly from tags
2. **Country disabled** - Some countries return large polygons (area > 100 m²)
3. **Local validation only** - `USE_LOCAL_NODES_ONLY = True`

---

## Configuration: When Reverse Geocoding is Disabled

### Line 218:
```python
USE_LOCAL_NODES_ONLY = True  # Set to True to disable reverse geocoding for all countries
```

### Line 140-170: Countries where reverse geocoding is disabled
```python
DISABLE_REVERSE_COUNTRIES = [
    # Countries where reverse geocoding ALWAYS returns large polygons (area > 100 m²)
    # These fail validation, so we skip reverse geocoding
    "Brunei",
    "Burkina Faso",
    "Chad",
    # ... more countries
]
```

**Why Disable?**
- Some countries return **polygons (ways)** instead of **points (nodes)**
- Polygons have area > 100 m² → **fails validation**
- Solution: Use node tags directly (local validation)

---

## The Two Validation Approaches

### **Approach 1: Local Validation (No Reverse Geocoding)**
```python
# Line 645: validate_node_locally()
def validate_node_locally(node, country):
    # Check if node has complete address tags
    if has_complete_address_tags(node):
        # Build address from tags
        address = build_address_from_tags(node)
        # Validate with looks_like_address()
        # Skip reverse geocoding
        return address
```

**Pros:**
- ✅ Faster (no API call)
- ✅ Works for countries with disabled reverse geocoding
- ✅ No rate limits

**Cons:**
- ❌ May not match Nominatim's format
- ❌ Not validated in Nominatim's index

### **Approach 2: Reverse Geocoding (With API Call)**
```python
# Line 1315: reverse_geocode()
nom = reverse_geocode(lat, lon, zoom=19)
address = nom.get("display_name")
# Then validate with check_with_nominatim()
```

**Pros:**
- ✅ Standardized format (Nominatim's version)
- ✅ Validated in Nominatim's index
- ✅ Guaranteed to work with forward geocoding

**Cons:**
- ❌ Slower (API call per address)
- ❌ Rate limits
- ❌ Fails for some countries (large polygons)

---

## Statistics Tracking

The script tracks reverse geocoding usage:

```python
stats = {
    "overpass_queries": 0,
    "local_validations": 0,      # No reverse geocoding
    "reverse_geocoded": 0,       # Used reverse geocoding
    "validation_passed": 0
}

# Line 1730-1732: Report success rate
if stats['reverse_geocoded'] > 0:
    reverse_success_rate = ((stats['validation_passed'] - stats['local_validations']) / stats['reverse_geocoded']) * 100
    print(f"📈 Reverse geocoding success rate: {reverse_success_rate:.1f}%")
```

---

## Summary

**Reverse Geocoding in `generate_address_cache_priority.py`:**

1. **Purpose:** Convert OSM node coordinates → Formatted address string
2. **When Used:** 
   - After getting nodes from Overpass API
   - When node tags are incomplete
   - To get Nominatim's standardized format
3. **API Endpoint:** `https://nominatim.openstreetmap.org/reverse`
4. **Input:** `lat, lon` (coordinates)
5. **Output:** Address string + components
6. **Zoom Level:** 19 (building-level detail)
7. **Can be Disabled:** For countries that return large polygons

**The Complete Flow:**
```
City → Overpass Query → OSM Nodes (with coordinates) → Reverse Geocode → Address String → Validate → Save
```

