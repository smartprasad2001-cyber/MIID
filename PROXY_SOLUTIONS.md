# Solutions for BrightData Nominatim Policy Block

BrightData blocks Nominatim by policy (classified as "Philanthropy & Non-Profit Organizations"). Here are practical solutions:

## ✅ Solution 1: Switch to Alternative Proxy Service (RECOMMENDED)

Use a proxy provider that **doesn't block Nominatim**:

### Recommended Providers:
1. **SmartProxy** - https://smartproxy.com
   - Residential proxies
   - Usually allows Nominatim
   - Format: `http://username:password@gate.smartproxy.com:7000`

2. **Oxylabs** - https://oxylabs.io
   - Residential proxies
   - Check if Nominatim is allowed in their policy
   - Format: `http://customer-USERNAME:PASSWORD@pr.oxylabs.io:7777`

3. **IPRoyal** - https://iproyal.com
   - Residential proxies
   - Generally more permissive policies
   - Format: `http://username:password@gate.iproyal.com:12321`

4. **GeoSurf** - https://geosurf.com
   - Residential proxies
   - Check policy before subscribing

### How to Use:
```bash
# Set new proxy URL
export PROXY_URL="http://username:password@new-proxy-host:port"

# Run script
python3 generate_address_cache.py
```

---

## ✅ Solution 2: Use VPN with IP Rotation

Instead of a proxy, use a VPN service that rotates IPs:

### Recommended VPN Services:
1. **NordVPN** - Has rotating IP feature
2. **Surfshark** - Residential IP rotation
3. **ExpressVPN** - IP rotation support

### How to Use:
1. Connect to VPN
2. Run script (it will use your VPN IP)
3. If you get rate-limited, disconnect and reconnect to get a new IP
4. Continue script

**Note**: You still need to respect 1 req/sec limit per IP.

---

## ✅ Solution 3: Use Alternative Nominatim Mirrors

Some public Nominatim mirrors may have different rate limits:

### Known Nominatim Mirrors:
- `https://nominatim.openstreetmap.org` (official - rate limited)
- `https://nominatim.openstreetmap.fr` (French mirror)
- `https://nominatim.mazdermind.de` (German mirror)
- `https://nominatim.gentpoortstraat.be` (Belgian mirror)
- `https://nominatim.hsbp.org` (Swiss mirror)

### How to Use:
```bash
# Set alternative Nominatim URL
export NOMINATIM_URL="https://nominatim.openstreetmap.fr/reverse"

# Run script
python3 generate_address_cache.py
```

**Note**: These mirrors may also have rate limits, but might be less strict.

---

## ✅ Solution 4: Self-Hosted Nominatim Instance

For complete control, host your own Nominatim instance:

### Requirements:
- Server with 32GB+ RAM
- 500GB+ SSD storage
- Docker or direct installation

### Resources:
- Official docs: https://nominatim.org/release-docs/latest/admin/Installation/
- Docker image: https://github.com/mediagis/nominatim-docker

### Benefits:
- No rate limits
- No policy restrictions
- Full control
- Can use with any proxy

---

## ✅ Solution 5: Optimize Direct Connection (Current Approach)

If you can't use a proxy, optimize your direct connection:

### Current Settings:
- `NOMINATIM_SLEEP = 1.0` (1 second between calls)
- Proper User-Agent header
- Exponential backoff on 403 errors
- 60-second cooldown after 5+ 403 errors

### Additional Optimizations:
1. **Increase delay** to 2-3 seconds if still getting 403s:
   ```python
   NOMINATIM_SLEEP = 2.5  # More conservative
   ```

2. **Use multiple IPs** (if you have multiple machines/VMs):
   - Run script on different machines
   - Each uses its own IP
   - Distribute load across IPs

3. **Request API key** from Nominatim:
   - Contact Nominatim maintainers
   - Request higher rate limit for legitimate use
   - May take time to get approved

---

## 🔧 Quick Implementation: Add URL Rotation

If you want to try multiple Nominatim mirrors automatically, I can add URL rotation to the script. This would:
- Try primary URL first
- Fallback to mirrors if 403 error
- Rotate through available mirrors

Would you like me to implement this?

---

## 📊 Comparison Table

| Solution | Cost | Setup Time | Reliability | Rate Limits |
|----------|------|------------|-------------|-------------|
| Alternative Proxy | $50-200/mo | 5 min | High | 1000+ req/min |
| VPN Rotation | $5-15/mo | 2 min | Medium | 1 req/sec per IP |
| Nominatim Mirrors | Free | 1 min | Low-Medium | Varies |
| Self-Hosted | $50-200/mo | 2-4 hours | Very High | Unlimited |
| Direct (Optimized) | Free | 0 min | Low | 1 req/sec |

---

## 🎯 Recommended Action Plan

1. **Short-term**: Continue with direct connection (current setup) + increase delay to 2.5s if needed
2. **Medium-term**: Try alternative proxy service (SmartProxy or IPRoyal)
3. **Long-term**: Consider self-hosted Nominatim if you need high volume

---

## ❓ Questions?

- Which solution would you like to try first?
- Do you have budget for a proxy service?
- Would you like me to implement URL rotation for Nominatim mirrors?

