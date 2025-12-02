# Using a Different IP Address Guide

## ✅ Yes, Different Laptop = Different IP

Running the script on a different laptop **on a different network** will give you a **new IP address** that is not blocked by Nominatim.

## 🔍 How IP Addresses Work

### Same Network = Same IP
- ❌ **Laptop 1** and **Laptop 2** on **same WiFi** → **Same IP** (both blocked)
- ✅ **Laptop 1** on **Home WiFi** and **Laptop 2** on **Office WiFi** → **Different IPs**
- ✅ **Laptop 1** on **Home WiFi** and **Laptop 2** on **Mobile Hotspot** → **Different IPs**

### What Determines Your IP
- Your **router/modem** gets an IP from your ISP
- All devices on the same network share that IP (NAT)
- Different network = different router = different IP

## 🚀 Quick Setup on Different Laptop

### Step 1: Transfer Files

```bash
# Option 1: Git (if using version control)
git clone <your-repo-url>
cd MIID-subnet

# Option 2: USB/External Drive
# Copy the entire MIID-subnet folder

# Option 3: Cloud Sync (Dropbox, Google Drive, etc.)
# Upload folder, download on other laptop
```

### Step 2: Install Dependencies

```bash
# On the new laptop
cd MIID-subnet

# Install Python dependencies
pip3 install -r requirements.txt

# Or install manually:
pip3 install requests bittensor geonamescache
```

### Step 3: Set Environment Variables

```bash
# Set proper User-Agent (REQUIRED)
export USER_AGENT="MIIDSubnet/1.0 (contact: your@email.com)"

# Optional: Set Nominatim URL if using self-hosted
export NOMINATIM_URL="http://your-nominatim-server:8080/reverse"
```

### Step 4: Verify New IP

```bash
# Check your IP address
curl -s https://api.ipify.org

# Compare with your original IP
# If different, you're good to go!
```

### Step 5: Run Script

```bash
# Run the script
python3 generate_and_test_addresses.py --country "United Kingdom" --city "London"
```

## 📋 Checklist Before Running

- [ ] Files transferred to new laptop
- [ ] Dependencies installed
- [ ] `USER_AGENT` environment variable set
- [ ] Verified new IP address (different from blocked IP)
- [ ] New laptop is on different network (different WiFi/router)
- [ ] No other scripts running on this network

## 🌐 Network Options

### Option 1: Different WiFi Network
- **Home WiFi** → **Office WiFi**
- **Friend's WiFi** → **Your WiFi**
- **Coffee Shop WiFi** → **Home WiFi**

### Option 2: Mobile Hotspot
- **Laptop 1**: Connected to home WiFi
- **Laptop 2**: Connected to phone's mobile hotspot
- ✅ **Different IPs** (mobile carrier vs home ISP)

### Option 3: Different Location
- **Laptop 1**: At home
- **Laptop 2**: At office/cafe/library
- ✅ **Different IPs** (different ISPs)

## ⚠️ Important Notes

### Same Network = Same IP
If both laptops are on the **same WiFi network**:
- They share the **same public IP**
- If one is blocked, both are blocked
- **Solution**: Use different networks

### Mobile Hotspot Works Great
- Phone hotspot = different IP (mobile carrier)
- Easy to switch between networks
- Good for testing

### Check IP Before Running
Always verify you have a different IP:
```bash
curl -s https://api.ipify.org
```

## 🔄 Alternative: Use VPN on Same Laptop

Instead of using a different laptop, you can use a VPN:

```bash
# Connect to VPN (changes your IP)
# Then run script
python3 generate_and_test_addresses.py --country "United Kingdom"
```

**VPN Options**:
- NordVPN
- ExpressVPN
- Surfshark
- Free VPNs (less reliable)

## 📊 IP Comparison

### Scenario 1: Same Network
```
Laptop 1 (Home WiFi)     → IP: 49.37.200.173
Laptop 2 (Home WiFi)     → IP: 49.37.200.173  ❌ SAME (both blocked)
```

### Scenario 2: Different Networks
```
Laptop 1 (Home WiFi)     → IP: 49.37.200.173  (blocked)
Laptop 2 (Office WiFi)   → IP: 203.0.113.45   ✅ DIFFERENT (not blocked)
```

### Scenario 3: Mobile Hotspot
```
Laptop 1 (Home WiFi)     → IP: 49.37.200.173  (blocked)
Laptop 2 (Phone Hotspot) → IP: 192.0.2.100    ✅ DIFFERENT (not blocked)
```

## 🎯 Best Practices

1. **Check IP First**
   ```bash
   curl -s https://api.ipify.org
   ```

2. **Set User-Agent**
   ```bash
   export USER_AGENT="MIIDSubnet/1.0 (contact: your@email.com)"
   ```

3. **Verify Different Network**
   - Different WiFi name = different network
   - Mobile hotspot = different network

4. **Run One Script at a Time**
   - Don't run on both laptops simultaneously
   - Each network should only have one script running

5. **Monitor for 403 Errors**
   - If you still get 403s, that IP might also be blocked
   - Try another network

## 🚨 Troubleshooting

### Still Getting 403s on New Laptop?

1. **Verify Different IP**:
   ```bash
   curl -s https://api.ipify.org
   ```

2. **Check Network**:
   - Are you on a different WiFi network?
   - Is it a mobile hotspot?

3. **Check User-Agent**:
   ```bash
   echo $USER_AGENT
   # Should show: MIIDSubnet/1.0 (contact: your@email.com)
   ```

4. **Wait a Bit**:
   - If you just switched networks, wait 1-2 minutes
   - Some networks cache IP assignments

5. **Try Another Network**:
   - If mobile hotspot doesn't work, try office WiFi
   - Or try a different location

## 💡 Pro Tips

### Use Mobile Hotspot for Testing
- Easy to switch networks
- Different IP each time you reconnect
- Good for testing if IP is the issue

### Keep Original Laptop Running
- You can run the script on the new laptop
- Keep the original laptop for other tasks
- Just make sure they're on different networks

### Use Cloud Storage
- Upload script to Google Drive/Dropbox
- Download on new laptop
- Easy file transfer

## ✅ Summary

**Yes, using a different laptop on a different network will give you a new IP!**

**Quick Steps**:
1. Transfer files to new laptop
2. Install dependencies
3. Set `USER_AGENT` environment variable
4. Verify new IP: `curl -s https://api.ipify.org`
5. Run script on new laptop (different network)
6. Should work without 403 errors! 🎉

**Remember**: Different network = different IP = not blocked!

