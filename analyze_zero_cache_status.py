#!/usr/bin/env python3
"""
Analyze zero_addresses_cache.json to show:
- Total addresses cached
- Countries processed
- Countries remaining
- Countries that failed (if any)
"""

import json
import os
import sys

# Import DISABLE_REVERSE_COUNTRIES from main script
sys.path.insert(0, os.path.dirname(__file__))
import generate_address_cache_priority as main_module

DISABLE_REVERSE_COUNTRIES = main_module.DISABLE_REVERSE_COUNTRIES

def main():
    # Load zero addresses cache
    zero_cache_file = "zero_addresses_cache.json"
    if not os.path.exists(zero_cache_file):
        print(f"❌ Zero cache file not found: {zero_cache_file}")
        return
    
    with open(zero_cache_file, 'r') as f:
        zero_cache_data = json.load(f)
    
    zero_addresses = zero_cache_data.get('addresses', {})
    
    # Load main cache to find countries with 0 addresses
    main_cache_file = "normalized_address_cache.json"
    if not os.path.exists(main_cache_file):
        print(f"❌ Main cache file not found: {main_cache_file}")
        return
    
    with open(main_cache_file, 'r') as f:
        main_cache_data = json.load(f)
    
    main_addresses = main_cache_data.get('addresses', {})
    
    # Find countries with 0 addresses (excluding disabled)
    zero_address_countries = []
    for country, addresses in main_addresses.items():
        if len(addresses) == 0 and country not in DISABLE_REVERSE_COUNTRIES:
            zero_address_countries.append(country)
    
    # Count addresses in zero cache
    total_addresses = 0
    countries_with_addresses = []
    countries_with_15_plus = []
    countries_with_less_than_15 = []
    
    for country, addresses in zero_addresses.items():
        count = len(addresses)
        total_addresses += count
        countries_with_addresses.append((country, count))
        
        if count >= 15:
            countries_with_15_plus.append((country, count))
        else:
            countries_with_less_than_15.append((country, count))
    
    # Find countries that still need processing
    processed_countries = set(zero_addresses.keys())
    remaining_countries = [c for c in zero_address_countries if c not in processed_countries]
    
    # Find countries that are partially processed (< 15 addresses)
    partially_processed = [c for c, count in countries_with_less_than_15]
    
    print("=" * 80)
    print("ZERO ADDRESSES CACHE STATUS")
    print("=" * 80)
    print()
    
    # Summary
    print("📊 SUMMARY")
    print("-" * 80)
    print(f"Total addresses cached: {total_addresses}")
    print(f"Countries processed: {len(countries_with_addresses)}")
    print(f"Countries with 15+ addresses: {len(countries_with_15_plus)}")
    print(f"Countries with < 15 addresses: {len(countries_with_less_than_15)}")
    print(f"Countries remaining (not started): {len(remaining_countries)}")
    print()
    
    # Countries with 15+ addresses
    if countries_with_15_plus:
        print("✅ COUNTRIES WITH 15+ ADDRESSES (COMPLETE)")
        print("-" * 80)
        for country, count in sorted(countries_with_15_plus, key=lambda x: x[1], reverse=True):
            print(f"  {country:30} {count:3} addresses")
        print()
    
    # Countries with < 15 addresses
    if countries_with_less_than_15:
        print("⚠️  COUNTRIES WITH < 15 ADDRESSES (INCOMPLETE)")
        print("-" * 80)
        for country, count in sorted(countries_with_less_than_15, key=lambda x: x[1], reverse=True):
            print(f"  {country:30} {count:3} addresses")
        print()
    
    # Countries remaining (not started)
    if remaining_countries:
        print("⏳ COUNTRIES REMAINING (NOT STARTED)")
        print("-" * 80)
        for country in sorted(remaining_countries):
            print(f"  {country}")
        print()
    
    # Progress calculation
    total_to_process = len(zero_address_countries)
    completed = len(countries_with_15_plus)
    in_progress = len(countries_with_less_than_15)
    not_started = len(remaining_countries)
    
    print("📈 PROGRESS")
    print("-" * 80)
    print(f"Total countries to process: {total_to_process}")
    print(f"  ✅ Completed (15+ addresses): {completed} ({completed*100/max(total_to_process,1):.1f}%)")
    print(f"  🔄 In progress (< 15 addresses): {in_progress} ({in_progress*100/max(total_to_process,1):.1f}%)")
    print(f"  ⏳ Not started: {not_started} ({not_started*100/max(total_to_process,1):.1f}%)")
    print()
    
    # Disabled countries (for reference)
    print("🚫 DISABLED COUNTRIES (not processed)")
    print("-" * 80)
    disabled_with_zero = [c for c in main_addresses.keys() if len(main_addresses.get(c, [])) == 0 and c in DISABLE_REVERSE_COUNTRIES]
    print(f"Countries with 0 addresses but disabled: {len(disabled_with_zero)}")
    if disabled_with_zero:
        for country in sorted(disabled_with_zero):
            print(f"  {country}")
    print()
    
    print("=" * 80)

if __name__ == "__main__":
    main()

