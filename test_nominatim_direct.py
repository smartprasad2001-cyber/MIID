#!/usr/bin/env python3
"""
Direct test of Nominatim API to see what's actually being returned
"""

import requests
import json

def test_nominatim_direct(address: str):
    """Test Nominatim API directly to see response."""
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": address, "format": "json"}
    user_agent = "YanezCompliance/101 (https://yanezcompliance.com; omar@yanezcompliance.com)"
    
    print(f"\n{'='*80}")
    print(f"Testing: {address}")
    print(f"{'='*80}")
    print(f"URL: {url}")
    print(f"Params: {params}")
    print(f"User-Agent: {user_agent}\n")
    
    try:
        response = requests.get(url, params=params, headers={"User-Agent": user_agent}, timeout=5)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}\n")
        
        if response.status_code != 200:
            print(f"❌ Non-200 status code: {response.status_code}")
            print(f"Response text (first 500 chars):")
            print(response.text[:500])
            return
        
        try:
            results = response.json()
            print(f"✅ JSON parsed successfully")
            print(f"Number of results: {len(results)}")
            if results:
                print(f"\nFirst result:")
                print(json.dumps(results[0], indent=2))
            else:
                print("⚠️  No results returned")
        except ValueError as e:
            print(f"❌ JSON decode error: {e}")
            print(f"Response text (first 500 chars):")
            print(response.text[:500])
            
    except Exception as e:
        print(f"❌ Exception: {type(e).__name__}: {e}")

if __name__ == "__main__":
    # Test with one of the failing addresses
    test_address = "37, Rruga Europa, Partizani, Lagjja 2, Shkoder, Shkodër Municipality, Shkodër County, Northern Albania, 4001, Albania"
    test_nominatim_direct(test_address)
    
    # Test with a simpler address
    print("\n\n" + "="*80)
    print("Testing simpler address...")
    test_nominatim_direct("15, Avinguda Doctor Mitjavila, Andorra la Vella, AD500, Andorra")

