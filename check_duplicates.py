#!/usr/bin/env python3
"""
Check for duplicate addresses in the cache file
"""

import json
from collections import Counter

def check_duplicates(cache_file):
    """Check for duplicate addresses in each country"""
    with open(cache_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    addresses = data.get("addresses", {})
    
    total_duplicates = 0
    countries_with_duplicates = []
    
    print("="*80)
    print("DUPLICATE ADDRESS CHECK")
    print("="*80)
    print()
    
    for country, addr_list in addresses.items():
        if not addr_list:
            continue
        
        # Count occurrences of each address
        addr_counter = Counter(addr_list)
        duplicates = {addr: count for addr, count in addr_counter.items() if count > 1}
        
        if duplicates:
            total_duplicates += sum(count - 1 for count in duplicates.values())
            countries_with_duplicates.append(country)
            
            print(f"❌ {country}: {len(duplicates)} duplicate address(es) found")
            for addr, count in duplicates.items():
                print(f"   '{addr[:70]}...' appears {count} times")
            print()
    
    if not countries_with_duplicates:
        print("✅ No duplicate addresses found in any country!")
    else:
        print("="*80)
        print(f"SUMMARY: {len(countries_with_duplicates)} countries with duplicates")
        print(f"Total duplicate entries: {total_duplicates}")
        print("="*80)
        print("\nCountries with duplicates:")
        for country in countries_with_duplicates:
            print(f"  - {country}")

if __name__ == '__main__':
    check_duplicates('validated_address_cache_new.json')

