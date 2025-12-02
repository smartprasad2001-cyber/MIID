"""
Free Proxy Rotator for Nominatim API calls
Fetches free proxies from public APIs and rotates them automatically
"""

import requests
import time
import random
from typing import Optional, List, Dict
import os

class FreeProxyRotator:
    """Rotates through free proxies from public APIs"""
    
    def __init__(self):
        self.proxies: List[Dict] = []
        self.current_index = 0
        self.failed_proxies = set()
        self.last_fetch = 0
        self.fetch_interval = 3600  # Fetch new proxies every hour
        
    def fetch_proxies_from_geonode(self) -> List[Dict]:
        """Fetch free proxies from Geonode API"""
        try:
            url = "https://proxylist.geonode.com/api/proxy-list?limit=50&page=1&sort_by=lastChecked&sort_type=desc&protocols=http%2Chttps"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                proxies = []
                for proxy in data.get("data", []):
                    protocols = proxy.get("protocols", [])
                    # Accept both HTTP and HTTPS proxies (HTTP proxies can work with HTTPS)
                    if protocols and ("http" in protocols or "https" in protocols):
                        proxies.append({
                            "host": proxy.get("ip"),
                            "port": proxy.get("port"),
                            "country": proxy.get("country"),
                            "protocol": "https" if "https" in protocols else "http",
                            "source": "geonode"
                        })
                return proxies
        except Exception as e:
            print(f"⚠️  Failed to fetch proxies from Geonode: {e}")
        return []
    
    def fetch_proxies_from_proxyscrape(self) -> List[Dict]:
        """Fetch free proxies from ProxyScrape API"""
        try:
            # Try v2 API first
            url = "https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all"
            response = requests.get(url, timeout=10)
            if response.status_code == 200 and response.text.strip() and not response.text.strip().startswith("Invalid"):
                proxies = []
                for line in response.text.strip().split("\n"):
                    line = line.strip()
                    if ":" in line and not line.startswith("Invalid"):
                        parts = line.split(":")
                        if len(parts) == 2:
                            proxies.append({
                                "host": parts[0],
                                "port": parts[1],
                                "country": "unknown",
                                "protocol": "http",
                                "source": "proxyscrape"
                            })
                if proxies:
                    return proxies[:20]  # Limit to 20
            
            # Fallback to v1 API
            url = "https://api.proxyscrape.com/?request=get&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all"
            response = requests.get(url, timeout=10)
            if response.status_code == 200 and response.text.strip():
                proxies = []
                for line in response.text.strip().split("\n"):
                    line = line.strip()
                    if ":" in line:
                        parts = line.split(":")
                        if len(parts) == 2:
                            proxies.append({
                                "host": parts[0],
                                "port": parts[1],
                                "country": "unknown",
                                "protocol": "http",
                                "source": "proxyscrape"
                            })
                if proxies:
                    return proxies[:20]  # Limit to 20
        except Exception as e:
            print(f"⚠️  Failed to fetch proxies from ProxyScrape: {e}")
        return []
    
    def fetch_all_proxies(self) -> List[Dict]:
        """Fetch proxies from all sources"""
        all_proxies = []
        print("🔍 Fetching free proxies from public APIs...")
        
        # Fetch from Geonode (better quality, HTTPS support)
        geonode_proxies = self.fetch_proxies_from_geonode()
        all_proxies.extend(geonode_proxies)
        print(f"   ✅ Found {len(geonode_proxies)} proxies from Geonode")
        
        # Fetch from ProxyScrape (backup)
        proxyscrape_proxies = self.fetch_proxies_from_proxyscrape()
        all_proxies.extend(proxyscrape_proxies)
        print(f"   ✅ Found {len(proxyscrape_proxies)} proxies from ProxyScrape")
        
        # Remove duplicates
        seen = set()
        unique_proxies = []
        for proxy in all_proxies:
            key = (proxy["host"], proxy["port"])
            if key not in seen:
                seen.add(key)
                unique_proxies.append(proxy)
        
        print(f"   📊 Total unique proxies: {len(unique_proxies)}")
        return unique_proxies
    
    def get_next_proxy(self) -> Optional[Dict]:
        """Get next working proxy, rotating through available ones"""
        current_time = time.time()
        
        # Refresh proxies if needed
        if current_time - self.last_fetch > self.fetch_interval or len(self.proxies) == 0:
            self.proxies = self.fetch_all_proxies()
            self.last_fetch = current_time
            self.failed_proxies.clear()
        
        if not self.proxies:
            return None
        
        # Try to find a working proxy
        attempts = 0
        while attempts < len(self.proxies):
            proxy = self.proxies[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.proxies)
            
            # Skip failed proxies
            key = (proxy["host"], proxy["port"])
            if key not in self.failed_proxies:
                return proxy
            
            attempts += 1
        
        # All proxies failed, reset and try again
        if len(self.failed_proxies) >= len(self.proxies) * 0.8:  # 80% failed
            print("⚠️  Most proxies failed, fetching new ones...")
            self.proxies = self.fetch_all_proxies()
            self.failed_proxies.clear()
            self.current_index = 0
        
        return None
    
    def mark_proxy_failed(self, proxy: Dict):
        """Mark a proxy as failed"""
        if proxy:
            key = (proxy["host"], proxy["port"])
            self.failed_proxies.add(key)
    
    def get_proxy_url(self, proxy: Dict) -> str:
        """Convert proxy dict to URL format"""
        if not proxy:
            return None
        return f"http://{proxy['host']}:{proxy['port']}"
    
    def test_proxy(self, proxy: Dict, test_url: str = "https://httpbin.org/ip") -> bool:
        """Test if a proxy is working"""
        try:
            proxy_url = self.get_proxy_url(proxy)
            proxies = {
                "http": proxy_url,
                "https": proxy_url
            }
            response = requests.get(test_url, proxies=proxies, timeout=5, verify=False)
            return response.status_code == 200
        except:
            return False


# Global instance
_rotator = FreeProxyRotator()

def get_free_proxy() -> Optional[str]:
    """
    Get a free proxy URL for use in requests.
    Returns None if no working proxy is available.
    """
    proxy = _rotator.get_next_proxy()
    if proxy:
        return _rotator.get_proxy_url(proxy)
    return None

def mark_proxy_failed(proxy_url: str):
    """Mark a proxy as failed (call this when you get errors)"""
    if proxy_url:
        # Parse URL back to dict format
        try:
            # Format: http://host:port
            parts = proxy_url.replace("http://", "").split(":")
            if len(parts) == 2:
                proxy_dict = {
                    "host": parts[0],
                    "port": parts[1]
                }
                _rotator.mark_proxy_failed(proxy_dict)
        except:
            pass

