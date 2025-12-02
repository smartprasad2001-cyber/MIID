# Free Proxy Guide for Nominatim

## ⚠️ Important Limitations

Free proxies have significant limitations:
- **Slow speeds** (often 5-10x slower than paid proxies)
- **Unreliable** (many proxies stop working after a few minutes)
- **Security risks** (some may log your traffic)
- **SSL issues** (many don't support HTTPS properly)
- **May still be blocked** by Nominatim (if proxy IP is already rate-limited)

## ✅ How to Use Free Proxies

### Option 1: Enable Free Proxy Rotator

```bash
# Enable free proxies
export USE_FREE_PROXIES=true

# Run script
python3 generate_address_cache.py
```

The script will:
1. Automatically fetch free proxies from public APIs
2. Rotate through them when one fails
3. Fallback to direct connection if all proxies fail

### Option 2: Test Free Proxies First

Test if free proxies work for your use case:

```python
python3 -c "
from free_proxy_rotator import FreeProxyRotator
rotator = FreeProxyRotator()
proxy = rotator.get_next_proxy()
print(f'Testing proxy: {proxy}')
if rotator.test_proxy(proxy):
    print('✅ Proxy works!')
else:
    print('❌ Proxy failed')
"
```

## 📊 Free Proxy Sources

The script uses these free proxy APIs:
1. **Geonode** - https://geonode.com/free-proxy-list
   - Better quality proxies
   - HTTPS support
   - Updated regularly

2. **ProxyScrape** - https://proxyscrape.com
   - Large proxy list
   - Updated every 5 minutes
   - Mixed quality

## 🔧 Configuration

### Environment Variables

```bash
# Enable free proxies
export USE_FREE_PROXIES=true

# Optional: Set your own proxy as fallback
export PROXY_URL="http://username:password@proxy-host:port"

# Set User-Agent (required for Nominatim)
export USER_AGENT="MIIDSubnet/1.0 (contact: your@email.com)"
```

### Script Behavior

- **Proxy Rotation**: Automatically rotates when proxy fails
- **Fallback**: Falls back to direct connection if all proxies fail
- **SSL Verification**: Disabled for free proxies (they often have cert issues)
- **Rate Limiting**: Still respects 1 req/sec limit per proxy IP

## ⚡ Performance Expectations

- **Success Rate**: 10-30% of free proxies actually work
- **Speed**: 2-5 seconds per request (vs 1-2s direct)
- **Reliability**: Proxies fail frequently, script auto-rotates

## 🎯 Best Practices

1. **Start with direct connection** - It's more reliable
2. **Use free proxies as backup** - Only if direct connection is blocked
3. **Monitor success rate** - If <20% success, disable free proxies
4. **Consider paid proxy** - For production use ($10-50/month)

## 🚨 Troubleshooting

### All proxies failing?
```bash
# Disable free proxies and use direct connection
unset USE_FREE_PROXIES
python3 generate_address_cache.py
```

### SSL errors?
- Free proxies often have SSL certificate issues
- Script automatically disables SSL verification for free proxies
- This is safe for Nominatim (read-only API)

### Still getting 403 errors?
- Free proxy IPs may already be rate-limited by Nominatim
- Try increasing delay: `NOMINATIM_SLEEP = 2.0`
- Consider using a paid proxy service

## 💡 Alternative: Free Tier Proxy Services

Some paid services offer free tiers:

1. **Oxylabs** - 5 free proxy IPs, 5GB/month
   - https://oxylabs.io/products/free-proxies
   - Usually allows Nominatim

2. **SmartProxy** - Free trial available
   - https://smartproxy.com
   - Check if Nominatim is allowed

## 📝 Summary

**Free proxies are NOT recommended for production use** because:
- Low reliability (10-30% success rate)
- Slow speeds
- Security concerns
- May still be blocked

**Better alternatives:**
1. Direct connection with proper rate limiting (current setup)
2. Paid proxy service ($10-50/month)
3. Self-hosted Nominatim instance

Use free proxies only as a last resort if direct connection is completely blocked.

