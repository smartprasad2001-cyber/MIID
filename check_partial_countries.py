#!/usr/bin/env python3
"""
Check how many countries with 1-14 addresses are left to process.
"""

import json
import os
import sys

# Load main cache
main_cache_file = "normalized_address_cache.json"
if not os.path.exists(main_cache_file):
    print(f"❌ Main cache file not found: {main_cache_file}")
    exit(1)

with open(main_cache_file, 'r') as f:
    main_cache_data = json.load(f)

main_addresses = main_cache_data.get('addresses', {})

# Load zero cache
zero_cache_file = "zero_addresses_cache.json"
zero_addresses = {}
if os.path.exists(zero_cache_file):
    with open(zero_cache_file, 'r') as f:
        zero_cache_data = json.load(f)
    zero_addresses = zero_cache_data.get('addresses', {})

# Import DISABLE_REVERSE_COUNTRIES
sys.path.insert(0, os.path.dirname(__file__))
import generate_address_cache_priority as main_module
DISABLE_REVERSE_COUNTRIES = main_module.DISABLE_REVERSE_COUNTRIES

# Find countries with 1-14 addresses in main cache
countries_to_process = []

for country, addresses in main_addresses.items():
    main_count = len(addresses)
    
    # Skip disabled countries
    if country in DISABLE_REVERSE_COUNTRIES:
        continue
    
    # Only process countries with 1-14 addresses
    if 1 <= main_count < 15:
        zero_count = len(zero_addresses.get(country, []))
        total_count = main_count + zero_count
        
        countries_to_process.append({
            "country": country,
            "main_count": main_count,
            "zero_count": zero_count,
            "total_count": total_count,
            "needed": max(0, 15 - total_count)
        })

# Sort by country name (alphabetically, like in normalized_address_cache.json)
countries_to_process.sort(key=lambda x: x["country"].lower())

print("=" * 80)
print("COUNTRIES WITH 1-14 ADDRESSES LEFT TO PROCESS")
print("=" * 80)
print(f"Total countries: {len(countries_to_process)}")
print()

# Count by status
complete = [c for c in countries_to_process if c["total_count"] >= 15]
incomplete = [c for c in countries_to_process if c["total_count"] < 15]

print(f"✅ Complete (15+ addresses): {len(complete)}")
print(f"⏳ Incomplete (< 15 addresses): {len(incomplete)}")
print()

if incomplete:
    print("=" * 80)
    print("INCOMPLETE COUNTRIES (NEED MORE ADDRESSES)")
    print("=" * 80)
    print(f"{'Country':<30} {'Main':<6} {'Zero':<6} {'Total':<6} {'Needed':<6}")
    print("-" * 80)
    
    for c in incomplete:
        print(f"{c['country']:<30} {c['main_count']:<6} {c['zero_count']:<6} {c['total_count']:<6} {c['needed']:<6}")
    
    print()
    total_needed = sum(c["needed"] for c in incomplete)
    print(f"Total addresses needed: {total_needed}")
    print()

if complete:
    print("=" * 80)
    print("COMPLETE COUNTRIES (15+ ADDRESSES)")
    print("=" * 80)
    for c in complete[:10]:  # Show first 10
        print(f"  {c['country']:<30} Main: {c['main_count']:<3} Zero: {c['zero_count']:<3} Total: {c['total_count']}")
    if len(complete) > 10:
        print(f"  ... and {len(complete) - 10} more")
    print()

print("=" * 80)

