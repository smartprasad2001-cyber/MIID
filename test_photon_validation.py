#!/usr/bin/env python3
"""
Test all addresses from normalized_address_cache.json against Photon API.
Photon API: https://photon.komoot.io/api/
"""

import json
import requests
import time
from typing import Dict, List, Tuple
from collections import defaultdict

PHOTON_API_URL = "https://photon.komoot.io/api/"

def test_address_with_photon(address: str, timeout: int = 5) -> Tuple[bool, dict]:
    """
    Test an address against Photon API.
    
    Returns:
        (success: bool, result: dict)
        success: True if address returns results, False otherwise
        result: API response details
    """
    try:
        params = {
            "q": address,
            "limit": 1
        }
        
        response = requests.get(PHOTON_API_URL, params=params, timeout=timeout)
        
        if response.status_code != 200:
            return False, {
                "status_code": response.status_code,
                "error": f"HTTP {response.status_code}",
                "has_results": False
            }
        
        data = response.json()
        features = data.get("features", [])
        
        has_results = len(features) > 0
        
        if has_results:
            # Get the first result
            first_result = features[0]
            properties = first_result.get("properties", {})
            geometry = first_result.get("geometry", {})
            
            return True, {
                "status_code": 200,
                "has_results": True,
                "result_count": len(features),
                "name": properties.get("name", ""),
                "country": properties.get("country", ""),
                "city": properties.get("city", ""),
                "state": properties.get("state", ""),
                "postcode": properties.get("postcode", ""),
                "osm_type": properties.get("osm_type", ""),
                "osm_id": properties.get("osm_id", ""),
                "coordinates": geometry.get("coordinates", [])
            }
        else:
            return False, {
                "status_code": 200,
                "has_results": False,
                "result_count": 0
            }
            
    except requests.exceptions.Timeout:
        return False, {
            "status_code": None,
            "error": "Timeout",
            "has_results": False
        }
    except requests.exceptions.RequestException as e:
        return False, {
            "status_code": None,
            "error": str(e),
            "has_results": False
        }
    except Exception as e:
        return False, {
            "status_code": None,
            "error": f"Unexpected error: {str(e)}",
            "has_results": False
        }

def load_addresses_from_cache(cache_file: str) -> Dict[str, List[dict]]:
    """Load addresses from normalized_address_cache.json"""
    try:
        with open(cache_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("addresses", {})
    except Exception as e:
        print(f"Error loading cache file: {e}")
        return {}

def main():
    cache_file = "normalized_address_cache.json"
    
    print("Loading addresses from cache...")
    addresses_by_country = load_addresses_from_cache(cache_file)
    
    if not addresses_by_country:
        print("No addresses found in cache file!")
        return
    
    total_addresses = sum(len(addrs) for addrs in addresses_by_country.values())
    print(f"Found {total_addresses} addresses across {len(addresses_by_country)} countries\n")
    
    # Statistics
    stats = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "timeout": 0,
        "error": 0,
        "by_country": defaultdict(lambda: {"total": 0, "passed": 0, "failed": 0})
    }
    
    failed_addresses = []
    passed_addresses = []
    
    print("Testing addresses against Photon API...")
    print("=" * 80)
    
    for country, address_list in addresses_by_country.items():
        print(f"\nTesting {country} ({len(address_list)} addresses)...")
        
        for idx, addr_data in enumerate(address_list, 1):
            address = addr_data.get("address", "")
            nominatim_score = addr_data.get("score", 0.0)
            
            if not address:
                continue
            
            stats["total"] += 1
            stats["by_country"][country]["total"] += 1
            
            # Test with Photon
            success, result = test_address_with_photon(address)
            
            if success and result.get("has_results"):
                stats["passed"] += 1
                stats["by_country"][country]["passed"] += 1
                passed_addresses.append({
                    "country": country,
                    "address": address,
                    "nominatim_score": nominatim_score,
                    "photon_result": result
                })
                photon_name = result.get("name", "N/A")
                photon_city = result.get("city", "N/A")
                print(f"  ✓ [{idx}/{len(address_list)}] PASSED")
                print(f"     Address: {address}")
                print(f"     Photon found: {photon_name}, {photon_city}")
            else:
                stats["failed"] += 1
                stats["by_country"][country]["failed"] += 1
                
                error_type = result.get("error", "No results")
                if "Timeout" in error_type:
                    stats["timeout"] += 1
                elif "error" in result:
                    stats["error"] += 1
                
                failed_addresses.append({
                    "country": country,
                    "address": address,
                    "nominatim_score": nominatim_score,
                    "photon_error": result
                })
                print(f"  ✗ [{idx}/{len(address_list)}] FAILED: {error_type}")
                print(f"     Address: {address}")
                if "error" in result:
                    print(f"     Error details: {result.get('error', 'Unknown')}")
            
            # Rate limiting - be nice to the API
            time.sleep(0.1)
    
    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total addresses tested: {stats['total']}")
    print(f"Passed Photon validation: {stats['passed']} ({stats['passed']/stats['total']*100:.1f}%)")
    print(f"Failed Photon validation: {stats['failed']} ({stats['failed']/stats['total']*100:.1f}%)")
    print(f"  - Timeouts: {stats['timeout']}")
    print(f"  - API Errors: {stats['error']}")
    print(f"  - No results: {stats['failed'] - stats['timeout'] - stats['error']}")
    
    # Country breakdown
    print("\n" + "=" * 80)
    print("BY COUNTRY BREAKDOWN")
    print("=" * 80)
    print(f"{'Country':<30} {'Total':<10} {'Passed':<10} {'Failed':<10} {'Pass %':<10}")
    print("-" * 80)
    
    for country in sorted(stats["by_country"].keys()):
        country_stats = stats["by_country"][country]
        total = country_stats["total"]
        passed = country_stats["passed"]
        failed = country_stats["failed"]
        pass_pct = (passed / total * 100) if total > 0 else 0
        print(f"{country:<30} {total:<10} {passed:<10} {failed:<10} {pass_pct:<10.1f}%")
    
    # Save detailed results
    results_file = "photon_validation_results.json"
    results = {
        "summary": {
            "total": stats["total"],
            "passed": stats["passed"],
            "failed": stats["failed"],
            "timeout": stats["timeout"],
            "error": stats["error"],
            "pass_rate": stats["passed"]/stats["total"]*100 if stats["total"] > 0 else 0
        },
        "by_country": dict(stats["by_country"]),
        "failed_addresses": failed_addresses[:100],  # Limit to first 100 for file size
        "passed_sample": passed_addresses[:50]  # Sample of passed addresses
    }
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\nDetailed results saved to: {results_file}")
    print(f"  - First 100 failed addresses")
    print(f"  - Sample of 50 passed addresses")

if __name__ == "__main__":
    main()

