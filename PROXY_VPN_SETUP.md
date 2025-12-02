# Proxy/VPN Setup Guide

## How to Change IP Address

The script now supports using proxies/VPNs to change your IP address and bypass network restrictions.

## Method 1: Command Line Proxy

### Single Proxy (HTTP and HTTPS)
```bash
python3 generate_from_static_dataset.py \
    --country "Poland" \
    --count 15 \
    --dataset sample_poland_addresses.csv \
    --proxy "http://proxy.example.com:8080"
```

### Separate HTTP/HTTPS Proxies
```bash
python3 generate_from_static_dataset.py \
    --country "Poland" \
    --count 15 \
    --dataset sample_poland_addresses.csv \
    --proxy-http "http://proxy.example.com:8080" \
    --proxy-https "https://proxy.example.com:8080"
```

## Method 2: Environment Variables

Set proxy environment variables (works automatically):

```bash
# For HTTP
export HTTP_PROXY="http://proxy.example.com:8080"

# For HTTPS
export HTTPS_PROXY="https://proxy.example.com:8080"

# Then run script normally
python3 generate_from_static_dataset.py --country "Poland" --count 15
```

## Method 3: VPN Services

### Free VPN Options:
1. **Tor** (via SOCKS proxy):
   ```bash
   # Install Tor, then use SOCKS proxy
   --proxy "socks5://127.0.0.1:9050"
   ```

2. **Cloudflare WARP**:
   ```bash
   # Install WARP, then use its proxy
   --proxy "socks5://127.0.0.1:40000"
   ```

3. **Free Proxy Lists**:
   - https://www.proxy-list.download/
   - https://free-proxy-list.net/
   - Use HTTP proxies from these lists

### Paid VPN Options:
- **NordVPN**: Provides SOCKS5 proxies
- **ExpressVPN**: Provides HTTP/HTTPS proxies
- **Surfshark**: Provides proxy servers

## Method 4: SSH Tunnel (If you have a remote server)

```bash
# Create SSH tunnel
ssh -D 8080 user@remote-server.com

# Use SOCKS proxy
python3 generate_from_static_dataset.py \
    --country "Poland" \
    --count 15 \
    --proxy "socks5://127.0.0.1:8080"
```

## Testing Proxy Connection

Test if your proxy works:

```bash
# Test with curl
curl -x http://proxy.example.com:8080 https://nominatim.openstreetmap.org

# Test with Python
python3 -c "
import requests
proxies = {'https': 'http://proxy.example.com:8080'}
r = requests.get('https://nominatim.openstreetmap.org', proxies=proxies, timeout=5)
print(f'Status: {r.status_code}')
"
```

## Quick Start Examples

### Example 1: Using Free HTTP Proxy
```bash
python3 generate_from_static_dataset.py \
    --country "Poland" \
    --count 5 \
    --dataset sample_poland_addresses.csv \
    --proxy "http://185.199.229.156:7492"
```

### Example 2: Using SOCKS5 Proxy (Tor)
```bash
python3 generate_from_static_dataset.py \
    --country "Poland" \
    --count 5 \
    --dataset sample_poland_addresses.csv \
    --proxy "socks5://127.0.0.1:9050"
```

### Example 3: Using Environment Variable
```bash
export HTTPS_PROXY="http://proxy.example.com:8080"
python3 generate_from_static_dataset.py \
    --country "Poland" \
    --count 5 \
    --dataset sample_poland_addresses.csv
```

## Notes

- **HTTP vs HTTPS Proxies**: Most proxies support both, but you can specify separately
- **SOCKS5 Support**: The script supports SOCKS5 proxies (e.g., Tor)
- **Authentication**: If proxy requires auth, use format: `http://user:pass@proxy:port`
- **Rate Limits**: Even with proxy, respect Nominatim's 1 req/sec limit
- **Free Proxies**: May be slow or unreliable - test first

## Troubleshooting

### Proxy Connection Failed
- Check proxy URL and port
- Verify proxy is running and accessible
- Test with curl first

### Still Getting Connection Refused
- Try a different proxy
- Check if proxy supports HTTPS
- Verify firewall allows proxy connections

### Slow Performance
- Free proxies are often slow
- Try paid VPN/proxy service
- Use multiple proxies and rotate

