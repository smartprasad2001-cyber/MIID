# Proxy Setup Guide

## How to Set Up Proxy URL

### Format
```
http://username:password@proxy-host:port
```

### Examples by Provider

#### 1. SmartProxy
- **Endpoint**: `gw.smartproxy.com:7000`
- **Format**: `http://username:password@gw.smartproxy.com:7000`
- **Example**: `http://myuser:mypass123@gw.smartproxy.com:7000`

#### 2. BrightData (formerly Luminati)
- **Endpoint**: `zproxy.lum-superproxy.io:22225`
- **Format**: `http://username:password@zproxy.lum-superproxy.io:22225`
- **Example**: `http://customer-username:password@zproxy.lum-superproxy.io:22225`

#### 3. Oxylabs
- **Endpoint**: `pr.oxylabs.io:7777`
- **Format**: `http://username:password@pr.oxylabs.io:7777`
- **Example**: `http://user-12345:pass67890@pr.oxylabs.io:7777`

#### 4. IPRoyal
- **Endpoint**: `rotating-residential.iproyal.com:12321`
- **Format**: `http://username:password@rotating-residential.iproyal.com:12321`
- **Example**: `http://myuser:mypass@rotating-residential.iproyal.com:12321`

#### 5. Custom/Private Proxy
- **Format**: `http://username:password@your-proxy-host:port`
- **Example**: `http://admin:secret123@proxy.example.com:8080`

## How to Use

### Option 1: Set Environment Variable (Recommended)
```bash
# Set the proxy URL
export PROXY_URL="http://username:password@proxy-host:port"

# Run the script
cd /Users/prasad/cursor/MIID-subnet
python3 generate_address_cache.py
```

### Option 2: Set in Same Command
```bash
PROXY_URL="http://username:password@proxy-host:port" python3 generate_address_cache.py
```

### Option 3: Add to .bashrc/.zshrc (Permanent)
```bash
# Add to ~/.zshrc or ~/.bashrc
export PROXY_URL="http://username:password@proxy-host:port"

# Then reload
source ~/.zshrc  # or source ~/.bashrc
```

## Where to Get Proxy Credentials

1. **Sign up** with a proxy provider (SmartProxy, BrightData, etc.)
2. **Go to your dashboard** → API/Proxy settings
3. **Find**:
   - Username (usually your account username or API key)
   - Password (usually your API password or secret)
   - Endpoint (host:port) - provided by the service
4. **Combine** them in the format: `http://username:password@host:port`

## Testing Your Proxy

Test if your proxy works:
```bash
export PROXY_URL="http://username:password@proxy-host:port"
curl -x $PROXY_URL https://api.ipify.org?format=json
```

This should return a different IP address than your real IP.

## Security Note

⚠️ **Never commit proxy credentials to git!**
- Use environment variables
- Don't hardcode in scripts
- Use `.env` files (and add to `.gitignore`)




