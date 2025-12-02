# Change IP Address - Quick Guide

## 🎯 Best Options for Your Use Case

### ✅ Option 1: Mobile Hotspot (Easiest & Free)
**Steps:**
1. Enable hotspot on your phone
2. Connect laptop to phone's WiFi hotspot
3. Check new IP: `curl -s https://api.ipify.org`
4. Run script: `python3 generate_address_cache.py`

**Pros:**
- ✅ Free
- ✅ Instant
- ✅ Different IP (mobile carrier)
- ✅ No software needed

**Cons:**
- ⚠️ Uses mobile data
- ⚠️ May be slower than WiFi

---

### ✅ Option 2: Free VPN (Recommended)
**Best Free VPNs:**

#### ProtonVPN (Best Free Option)
- **Website**: https://protonvpn.com
- **Free Tier**: Unlimited bandwidth, 3 countries
- **Install**: Download macOS app from website
- **Usage**: Connect to any server, then run script

#### Windscribe
- **Website**: https://windscribe.com
- **Free Tier**: 10GB/month, multiple countries
- **Install**: Download macOS app

#### TunnelBear
- **Website**: https://www.tunnelbear.com
- **Free Tier**: 500MB/month
- **Install**: Download macOS app

**Steps:**
1. Download VPN client
2. Create free account
3. Connect to a server
4. Verify IP changed: `curl -s https://api.ipify.org`
5. Run script: `python3 generate_address_cache.py`

**Pros:**
- ✅ Free options available
- ✅ Easy to use
- ✅ Can switch servers/locations
- ✅ Encrypts traffic

**Cons:**
- ⚠️ Free tiers have limits
- ⚠️ May be slower than direct connection

---

### ✅ Option 3: Different Network
**Options:**
- Office WiFi
- Coffee shop WiFi
- Friend's house WiFi
- Library WiFi
- Public WiFi

**Steps:**
1. Connect to different WiFi network
2. Check IP: `curl -s https://api.ipify.org`
3. Run script

**Pros:**
- ✅ Free
- ✅ No software needed
- ✅ Different IP guaranteed

**Cons:**
- ⚠️ Need physical access to different network
- ⚠️ May need to move location

---

### ⚠️ Option 4: Restart Router (Unreliable)
**Steps:**
1. Unplug router for 10 minutes
2. Plug back in
3. Check if IP changed: `curl -s https://api.ipify.org`

**Pros:**
- ✅ Free
- ✅ No software needed

**Cons:**
- ❌ Not guaranteed to work
- ❌ Depends on ISP policy
- ❌ May take hours to get new IP

---

## 🔍 Verify IP Change

Always check your IP before running the script:

```bash
# Check current IP
curl -s https://api.ipify.org

# Compare with your original IP
# If different, you're good to go!
```

---

## 🚀 Quick Start: Mobile Hotspot

**Fastest way to get a new IP:**

1. **On your phone:**
   - Settings → Personal Hotspot → Turn On
   - Note the WiFi password

2. **On your laptop:**
   ```bash
   # Connect to phone's hotspot WiFi
   # Check new IP
   curl -s https://api.ipify.org
   
   # Set User-Agent (if not already set)
   export USER_AGENT="MIIDSubnet/1.0 (contact: your@email.com)"
   
   # Run script
   python3 generate_address_cache.py
   ```

3. **Done!** You now have a different IP address.

---

## 🚀 Quick Start: Free VPN (ProtonVPN)

1. **Download ProtonVPN:**
   - Go to https://protonvpn.com
   - Click "Download" → macOS
   - Install the app

2. **Create free account:**
   - Sign up for free account
   - Verify email

3. **Connect:**
   - Open ProtonVPN app
   - Click "Quick Connect"
   - Wait for connection

4. **Verify:**
   ```bash
   curl -s https://api.ipify.org
   # Should show different IP
   ```

5. **Run script:**
   ```bash
   export USER_AGENT="MIIDSubnet/1.0 (contact: your@email.com)"
   python3 generate_address_cache.py
   ```

---

## 📊 Comparison

| Method | Cost | Speed | Reliability | Ease |
|--------|------|-------|-------------|------|
| Mobile Hotspot | Free | Medium | High | ⭐⭐⭐⭐⭐ |
| Free VPN | Free | Medium | High | ⭐⭐⭐⭐ |
| Different Network | Free | Fast | High | ⭐⭐⭐ |
| Restart Router | Free | Fast | Low | ⭐⭐ |

---

## ⚠️ Important Notes

### Always Set User-Agent
Even with a new IP, Nominatim requires a proper User-Agent:

```bash
export USER_AGENT="MIIDSubnet/1.0 (contact: your@email.com)"
```

### Rate Limiting Still Applies
- New IP = fresh start
- But still respect 1 request/second
- Don't spam Nominatim

### Check IP Before Running
```bash
curl -s https://api.ipify.org
```

If it's the same as your blocked IP, try another method.

---

## 🎯 Recommended: Mobile Hotspot

**For your use case, I recommend Mobile Hotspot because:**
- ✅ Instant (no software to install)
- ✅ Free (uses your phone's data)
- ✅ Guaranteed different IP
- ✅ Easy to switch back

**Steps:**
1. Turn on phone hotspot
2. Connect laptop to hotspot
3. Verify new IP
4. Run script
5. Done!

---

## 💡 Pro Tips

1. **Use Mobile Hotspot for Testing**
   - Quick way to test if IP is the issue
   - Easy to switch back to WiFi

2. **Use VPN for Long Runs**
   - More stable for long-running scripts
   - Can switch servers if one gets blocked

3. **Keep Original Network**
   - Don't disconnect from original WiFi
   - Just connect to hotspot/VPN
   - Can switch back easily

4. **Monitor Data Usage**
   - Mobile hotspot uses phone data
   - VPN uses WiFi data (but routes through VPN)

---

## ✅ Summary

**Easiest Option**: Mobile Hotspot
- Turn on phone hotspot → Connect laptop → Run script

**Best Free Option**: ProtonVPN
- Download → Sign up → Connect → Run script

**Always**: Check IP first with `curl -s https://api.ipify.org`

