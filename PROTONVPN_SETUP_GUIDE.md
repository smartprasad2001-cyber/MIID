# ProtonVPN Setup Guide - Step by Step

## 🎯 Goal: Change Your IP Address Using Free ProtonVPN

---

## Step 1: Download ProtonVPN

1. **Open your web browser** (Safari, Chrome, etc.)

2. **Go to**: https://protonvpn.com

3. **Click** the **"Download"** button (usually in the top right)

4. **Select "macOS"** from the download options

5. **Download the installer** (`.dmg` file)

---

## Step 2: Install ProtonVPN

1. **Open the downloaded file** (usually in your Downloads folder)
   - Look for: `ProtonVPN.dmg`

2. **Double-click** the `.dmg` file to open it

3. **Drag "ProtonVPN"** to the **Applications folder**

4. **Open Applications folder** and **double-click "ProtonVPN"** to launch

5. **If macOS asks for permission:**
   - Go to **System Settings** → **Privacy & Security**
   - Click **"Open Anyway"** next to ProtonVPN

---

## Step 3: Create Free Account

1. **In the ProtonVPN app**, click **"Sign Up"** or **"Create Account"**

2. **Choose the Free plan** (it's free forever, no credit card needed)

3. **Fill in your details:**
   - Email address
   - Password
   - Confirm password

4. **Verify your email:**
   - Check your email inbox
   - Click the verification link from ProtonVPN
   - This activates your free account

---

## Step 4: Connect to VPN Server

1. **Log in** to ProtonVPN with your new account

2. **You'll see a list of servers** (or a map)

3. **For Free tier**, you can choose from:
   - **Netherlands** (usually fastest)
   - **United States**
   - **Japan**

4. **Click on any server** (e.g., "Netherlands #1")

5. **Click "Connect"** button

6. **Wait for connection** (usually 5-10 seconds)
   - You'll see "Connected" status
   - The app icon in menu bar will show you're connected

---

## Step 5: Verify IP Changed

1. **Open Terminal** (Applications → Utilities → Terminal)

2. **Check your new IP:**
   ```bash
   curl -s https://api.ipify.org
   ```

3. **Compare with your original IP:**
   - Your original IP was: `49.47.241.253`
   - New IP should be **different** (e.g., something like `185.159.157.xxx`)

4. **If IP is different** → ✅ Success! You're ready to run your script

---

## Step 6: Set Environment Variables & Run Script

1. **In Terminal**, set the User-Agent (required for Nominatim):
   ```bash
   export USER_AGENT="MIIDSubnet/1.0 (contact: your@email.com)"
   ```

2. **Navigate to your project:**
   ```bash
   cd /Users/prasad/cursor/MIID-subnet
   ```

3. **Run your script:**
   ```bash
   python3 generate_address_cache.py
   ```

4. **The script will now use the VPN's IP address** instead of your blocked IP!

---

## Step 7: Disconnect When Done

1. **Open ProtonVPN app**

2. **Click "Disconnect"** button

3. **Or click the ProtonVPN icon** in menu bar → **"Disconnect"**

4. **Your connection returns to normal** (original IP)

---

## 🔍 Troubleshooting

### Problem: Can't connect to server

**Solution:**
- Try a different server (Netherlands, US, or Japan)
- Free tier has limited servers, but all should work
- Wait a few seconds and try again

### Problem: IP didn't change

**Solution:**
1. Make sure ProtonVPN shows "Connected"
2. Check connection status in the app
3. Try disconnecting and reconnecting
4. Try a different server

### Problem: Script still getting 403 errors

**Solution:**
1. **Switch to a different server:**
   - Disconnect current server
   - Connect to a different one (e.g., switch from Netherlands to US)
   - Check new IP: `curl -s https://api.ipify.org`
   - Run script again

2. **Make sure User-Agent is set:**
   ```bash
   echo $USER_AGENT
   # Should show: MIIDSubnet/1.0 (contact: your@email.com)
   ```

3. **Wait a bit:**
   - Sometimes it takes a minute for the new IP to propagate
   - Wait 30 seconds after connecting, then try again

---

## 💡 Pro Tips

### Switch Servers Easily
If one server gets blocked:
1. **Disconnect** current server
2. **Connect** to a different server (e.g., switch from Netherlands to US)
3. **Check new IP**: `curl -s https://api.ipify.org`
4. **Run script** again

### Keep VPN Connected
- Keep ProtonVPN connected while running your script
- Don't disconnect until script finishes
- You can minimize the ProtonVPN window

### Free Tier Limits
- **3 countries** available (Netherlands, US, Japan)
- **Unlimited bandwidth** (no data caps!)
- **1 device** at a time
- **Medium speed** (good enough for API calls)

### Check Connection Status
- Look at the ProtonVPN icon in your menu bar
- Green = Connected
- Gray = Disconnected

---

## 📋 Quick Reference Commands

```bash
# Check current IP
curl -s https://api.ipify.org

# Set User-Agent
export USER_AGENT="MIIDSubnet/1.0 (contact: your@email.com)"

# Navigate to project
cd /Users/prasad/cursor/MIID-subnet

# Run script
python3 generate_address_cache.py
```

---

## ✅ Checklist

Before running your script:
- [ ] ProtonVPN installed
- [ ] Free account created and verified
- [ ] Connected to a VPN server
- [ ] Verified IP changed: `curl -s https://api.ipify.org`
- [ ] User-Agent set: `export USER_AGENT="MIIDSubnet/1.0 (contact: your@email.com)"`
- [ ] Script ready to run

---

## 🎯 Summary

1. **Download** ProtonVPN from https://protonvpn.com
2. **Install** the macOS app
3. **Sign up** for free account (verify email)
4. **Connect** to any server (Netherlands, US, or Japan)
5. **Verify** IP changed: `curl -s https://api.ipify.org`
6. **Set** User-Agent: `export USER_AGENT="MIIDSubnet/1.0 (contact: your@email.com)"`
7. **Run** your script: `python3 generate_address_cache.py`

**That's it!** Your script will now use the VPN's IP address instead of your blocked one.

---

## 🔄 Switching Servers (If One Gets Blocked)

If you get 403 errors even with VPN:

1. **In ProtonVPN app**, click **"Disconnect"**

2. **Click on a different server** (e.g., switch from Netherlands to US)

3. **Click "Connect"**

4. **Check new IP:**
   ```bash
   curl -s https://api.ipify.org
   ```

5. **Run script again:**
   ```bash
   python3 generate_address_cache.py
   ```

You can switch between the 3 free servers (Netherlands, US, Japan) as needed!

