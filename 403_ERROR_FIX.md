# Why 403 Errors Still Occur (Even with 1 Second Delays)

## 🔍 Root Causes

Even though you're respecting 1 second per call, 403 errors can still occur due to:

### 1. **No Rate Limiting BEFORE First Call**
- **Problem**: The script sleeps 2 seconds AFTER validation, but not BEFORE the first Nominatim call
- **Impact**: If multiple addresses are validated quickly, the first call has no delay
- **Fix**: Added `time.sleep(1.0)` BEFORE each Nominatim API call

### 2. **Multiple Nominatim Calls Without Spacing**
- **Problem**: `get_country_area_id()` makes a Nominatim call with no rate limiting
- **Impact**: This call happens before address validation, potentially triggering rate limits
- **Fix**: Added rate limiting before `get_country_area_id()` calls

### 3. **Insufficient User-Agent**
- **Problem**: 
  - `get_country_area_id()` used generic "AddressGenerator/1.0" (no contact info)
  - Nominatim requires proper User-Agent with contact information
- **Impact**: Nominatim may block requests without proper User-Agent
- **Fix**: 
  - Updated to use `USER_AGENT` environment variable
  - Added proper User-Agent support in `rewards.py`

### 4. **IP Already Rate-Limited**
- **Problem**: If your IP was previously rate-limited, Nominatim may still block it
- **Impact**: Even with proper delays, previously blocked IPs may continue to get 403s
- **Solution**: 
  - Wait 10-15 minutes before retrying
  - Use a different IP/VPN
  - Use self-hosted Nominatim instance

### 5. **Concurrent Scripts**
- **Problem**: If multiple scripts are running simultaneously, they share the same IP
- **Impact**: Combined requests exceed 1 req/sec limit
- **Solution**: Only run one script at a time

## ✅ Fixes Applied

### Fix 1: Rate Limiting Before API Calls
```python
# BEFORE (missing rate limit before call)
api_result = check_with_nominatim(...)

# AFTER (rate limit before call)
time.sleep(1.0)  # CRITICAL: Rate limit BEFORE Nominatim call
api_result = check_with_nominatim(...)
```

### Fix 2: Proper User-Agent
```python
# BEFORE
headers = {"User-Agent": "AddressGenerator/1.0"}

# AFTER
user_agent = os.getenv("USER_AGENT", "AddressGenerator/1.0 (contact: youremail@example.com)")
headers = {"User-Agent": user_agent}
```

### Fix 3: Rate Limiting in get_country_area_id()
```python
# Added rate limiting before Nominatim call
time.sleep(1.0)
response = requests.get(url, params=params, headers=headers, timeout=10)
```

### Fix 4: Adjusted Sleep After Validation
```python
# BEFORE: 2 seconds after (too much, but no delay before)
time.sleep(2.0)

# AFTER: 1 second before + API call time + 1 second after = safe spacing
time.sleep(1.0)  # Total spacing ensures 1 req/sec
```

## 📊 Current Rate Limiting Strategy

```
Timeline for each address validation:
┌─────────────────────────────────────────────────────────┐
│ 0.0s: Start validation                                  │
│ 1.0s: Sleep (rate limit BEFORE call)                    │
│ 2.0s: Call Nominatim API (~1-2 seconds)                │
│ 3-4s: Process response                                 │
│ 4-5s: Sleep (rate limit AFTER call)                    │
│ 5-6s: Next address validation                           │
└─────────────────────────────────────────────────────────┘

Total spacing: ~5-6 seconds per address (very safe)
Effective rate: ~0.2 req/sec (well below 1 req/sec limit)
```

## 🚨 Why 403 Errors May Still Occur

### 1. **IP Already Blocked**
If your IP was previously rate-limited:
- Nominatim may continue blocking for 10-60 minutes
- Even with proper delays, you'll still get 403s
- **Solution**: Wait 15-30 minutes, or use different IP

### 2. **Burst Detection**
Nominatim may detect bursts even with proper spacing:
- If you make 10+ requests in a row, it may temporarily block
- **Solution**: Add longer cooldown after every 10 requests

### 3. **User-Agent Issues**
If User-Agent is missing or invalid:
- Nominatim immediately returns 403
- **Solution**: Always set proper `USER_AGENT` environment variable

### 4. **Multiple Scripts Running**
If other scripts are also calling Nominatim:
- Combined rate exceeds 1 req/sec
- **Solution**: Only run one script at a time

## 🔧 Recommended Usage

### Set Proper User-Agent
```bash
export USER_AGENT="MIIDSubnet/1.0 (contact: your@email.com)"
python3 generate_and_test_addresses.py --country "United Kingdom"
```

### If Still Getting 403s

1. **Wait 15-30 minutes** (let IP cooldown)
2. **Check if other scripts are running**:
   ```bash
   ps aux | grep "generate_address"
   ```
3. **Use self-hosted Nominatim** (no rate limits)
4. **Use VPN/proxy** (different IP)

## 📈 Expected Behavior After Fixes

- **Before fixes**: 403 errors common, even with 2s delays
- **After fixes**: 403 errors rare, only if IP was previously blocked
- **Rate**: ~0.2 req/sec (very conservative, well below limit)

## 🎯 Summary

The script now:
- ✅ Sleeps 1 second BEFORE each Nominatim call
- ✅ Sleeps 1 second AFTER each validation
- ✅ Uses proper User-Agent with contact info
- ✅ Rate limits all Nominatim calls (including `get_country_area_id()`)
- ✅ Total spacing: ~5-6 seconds per address (very safe)

If you still get 403 errors, it's likely because:
1. Your IP was previously blocked (wait 15-30 minutes)
2. Multiple scripts are running simultaneously
3. Nominatim is having temporary issues

The fixes ensure proper rate limiting, but can't fix an already-blocked IP.

