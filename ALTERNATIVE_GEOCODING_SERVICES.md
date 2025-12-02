# Alternative Geocoding Services (No/Low Rate Limits)

## ⚠️ Important Note

**Most services still have rate limits**, but some are more lenient than Nominatim. However, your code is **specifically designed for Nominatim** and uses its **bounding box area calculation** for scoring. Switching to another service would require code modifications.

## 🎯 Best Option: Self-Hosted Nominatim

**No rate limits** - You control everything!

- ✅ **Unlimited requests**
- ✅ **Same API format** (no code changes needed)
- ✅ **Same scoring logic** (bounding box areas)
- ✅ **Full control**

**Setup**: See `NOMINATIM_SELF_HOSTED_GUIDE.md`

---

## 🌐 Alternative Services (With Rate Limits)

### 1. **BigDataCloud** ⭐ Best Free Option

**Rate Limits**:
- **Client-side**: No rate limits (browser-based)
- **Server-side**: 50,000 free queries/month
- **Paid**: Higher limits available

**API**:
```python
# Reverse geocoding
url = "https://api.bigdatacloud.net/data/reverse-geocode-client"
params = {"latitude": lat, "longitude": lon}

# Forward geocoding
url = "https://api.bigdatacloud.net/data/forward-geocode-client"
params = {"query": address}
```

**Pros**:
- Generous free tier (50k/month)
- No rate limits for client-side
- Good coverage

**Cons**:
- Different API format (needs code changes)
- No bounding box areas (different scoring needed)
- Monthly limit (not unlimited)

**Website**: https://www.bigdatacloud.com

---

### 2. **Geoapify**

**Rate Limits**:
- **Free**: 3,000 credits/day, 5 requests/second
- **Paid**: Higher limits

**API**:
```python
url = "https://api.geoapify.com/v1/geocode/search"
params = {"text": address, "apiKey": "your-api-key"}
```

**Pros**:
- Good free tier
- 5 req/sec (better than Nominatim's 1 req/sec)
- Good coverage

**Cons**:
- Requires API key
- Different response format
- Daily limits

**Website**: https://www.geoapify.com

---

### 3. **Geocode.xyz**

**Rate Limits**:
- **Free**: 1 request/second
- **Paid**: Up to 10 requests/second, unlimited credits

**API**:
```python
url = "https://geocode.xyz"
params = {"locate": address, "json": 1}
```

**Pros**:
- Simple API
- 1 req/sec (same as Nominatim)
- Paid plans available

**Cons**:
- Same rate limit as Nominatim
- Different response format
- Less coverage than Nominatim

**Website**: https://geocode.xyz

---

### 4. **FreeGeocodingAPI.com**

**Rate Limits**:
- **Free**: 30,000 requests/month, 1 concurrent request
- **Paid**: Higher limits

**API**:
```python
url = "https://api.freegeocodingapi.com/v1/geocode"
params = {"address": address}
```

**Pros**:
- 30k free requests/month
- Simple API

**Cons**:
- Monthly limits
- Different response format
- Less coverage

**Website**: https://freegeocodingapi.com

---

### 5. **Mapbox Geocoding API**

**Rate Limits**:
- **Free**: 100,000 requests/month
- **Paid**: Higher limits

**API**:
```python
url = "https://api.mapbox.com/geocoding/v5/mapbox.places/{address}.json"
params = {"access_token": "your-token"}
```

**Pros**:
- Very generous free tier (100k/month)
- Good coverage
- Well-documented

**Cons**:
- Requires API key
- Different response format
- Monthly limits

**Website**: https://www.mapbox.com

---

### 6. **Google Geocoding API**

**Rate Limits**:
- **Free**: $200 credit/month (~40,000 requests)
- **Paid**: Pay-as-you-go

**API**:
```python
url = "https://maps.googleapis.com/maps/api/geocode/json"
params = {"address": address, "key": "your-api-key"}
```

**Pros**:
- Excellent coverage
- Very accurate
- Good documentation

**Cons**:
- Requires API key and billing
- Different response format
- Credit-based (not truly free)

**Website**: https://developers.google.com/maps/documentation/geocoding

---

## 🔄 Code Modification Required

### Current Nominatim Scoring (Based on Bounding Box Areas)

```python
# Your current code uses bounding box areas for scoring
min_area = min(areas)
if min_area < 100:
    score = 1.0
elif min_area < 1000:
    score = 0.9
# etc...
```

### Alternative Services Don't Provide Bounding Box Areas

Most alternative services return:
- Coordinates (lat/lon)
- Address components
- **But NOT bounding box areas**

**You would need to**:
1. Calculate bounding box from coordinates (less precise)
2. Use different scoring logic (confidence scores, etc.)
3. Modify `check_with_nominatim()` function
4. Update validation logic

---

## 📊 Comparison Table

| Service | Free Tier | Rate Limit | Bounding Box | Code Changes |
|---------|-----------|------------|--------------|--------------|
| **Self-Hosted Nominatim** | ✅ Unlimited | ✅ None | ✅ Yes | ❌ None |
| **BigDataCloud** | 50k/month | Client: None<br>Server: Monthly | ❌ No | ✅ Required |
| **Geoapify** | 3k/day | 5 req/sec | ❌ No | ✅ Required |
| **Geocode.xyz** | Limited | 1 req/sec | ❌ No | ✅ Required |
| **FreeGeocodingAPI** | 30k/month | 1 concurrent | ❌ No | ✅ Required |
| **Mapbox** | 100k/month | Varies | ❌ No | ✅ Required |
| **Google** | $200 credit | Varies | ❌ No | ✅ Required |

---

## 🎯 Recommendations

### Option 1: Self-Hosted Nominatim ⭐ BEST
- **No rate limits**
- **No code changes**
- **Same scoring logic**
- **Full control**

**Cost**: ~$100-200/month for cloud server

### Option 2: BigDataCloud (If You Need Cloud)
- **50k free requests/month**
- **No rate limits for client-side**
- **Good coverage**

**Cost**: Free (up to 50k/month)

### Option 3: Mapbox (If You Need High Volume)
- **100k free requests/month**
- **Good coverage**
- **Well-documented**

**Cost**: Free (up to 100k/month)

### Option 4: Use Multiple Services (Fallback)
- Try Nominatim first
- Fallback to BigDataCloud if 403 error
- Fallback to Mapbox if needed

**Cost**: Free (using free tiers)

---

## 🔧 Implementation Example (BigDataCloud)

If you want to try BigDataCloud as an alternative:

```python
def check_with_bigdatacloud(address: str) -> dict:
    """Alternative to Nominatim using BigDataCloud"""
    try:
        url = "https://api.bigdatacloud.net/data/forward-geocode-client"
        params = {"query": address, "localityLanguage": "en"}
        
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code != 200:
            return 0.0
        
        data = response.json()
        
        # BigDataCloud doesn't provide bounding box areas
        # You'd need to calculate from coordinates or use confidence
        if data.get("results"):
            result = data["results"][0]
            # Use confidence or calculate area from coordinates
            confidence = result.get("confidence", 0)
            
            # Convert confidence to score (example)
            if confidence >= 0.9:
                score = 1.0
            elif confidence >= 0.7:
                score = 0.9
            else:
                score = 0.7
            
            return {"score": score, "confidence": confidence}
        
        return 0.0
    except:
        return 0.0
```

**Note**: This uses confidence scores instead of bounding box areas, so scoring would be different.

---

## ✅ Summary

**Best Options**:

1. **Self-Hosted Nominatim** - No rate limits, no code changes ⭐
2. **BigDataCloud** - 50k/month free, no client-side limits
3. **Mapbox** - 100k/month free, good coverage

**Important**: 
- Most services still have rate limits (just more lenient)
- Your code uses Nominatim-specific features (bounding box areas)
- Switching services requires code modifications
- **Self-hosted Nominatim is the only true "no rate limit" solution**

**Recommendation**: Use self-hosted Nominatim for unlimited requests without code changes.

