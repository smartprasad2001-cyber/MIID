#!/usr/bin/env python3
"""
Import addresses from zero_addresses_cache.json to normalized_address_cache.json
for countries that have incomplete addresses (<15).
"""

import json
import sys
from typing import Dict, List, Set

def load_caches():
    """Load both cache files."""
    with open('normalized_address_cache.json', 'r') as f:
        normalized_cache = json.load(f)
    
    with open('zero_addresses_cache.json', 'r') as f:
        zero_cache = json.load(f)
    
    # Get addresses (handle nested structure)
    normalized_addrs = normalized_cache.get('addresses', normalized_cache)
    zero_addrs = zero_cache.get('addresses', zero_cache)
    
    return normalized_cache, normalized_addrs, zero_addrs

def get_normalized_addresses_set(addresses: List[Dict]) -> Set[str]:
    """Get set of normalized addresses for deduplication."""
    normalized_set = set()
    for addr in addresses:
        if isinstance(addr, dict):
            normalized = addr.get('cheat_normalized_address', '')
            if normalized:
                normalized_set.add(normalized)
    return normalized_set

def import_addresses():
    """Import addresses from zero_cache to normalized_cache."""
    print("=" * 80)
    print("IMPORTING ADDRESSES FROM ZERO_CACHE TO NORMALIZED_CACHE")
    print("=" * 80)
    print()
    
    # Load caches
    normalized_cache, normalized_addrs, zero_addrs = load_caches()
    
    # Statistics
    total_imported = 0
    total_duplicates = 0
    countries_completed = 0
    countries_partial = 0
    
    # Process each country
    for country in sorted(zero_addrs.keys()):
        if country not in normalized_addrs:
            # Country doesn't exist in normalized_cache, skip
            continue
        
        normalized_list = normalized_addrs[country]
        zero_list = zero_addrs[country]
        
        if not isinstance(normalized_list, list):
            normalized_list = []
            normalized_addrs[country] = normalized_list
        
        if not isinstance(zero_list, list):
            continue
        
        current_count = len(normalized_list)
        if current_count >= 15:
            # Already complete, skip
            continue
        
        needed = 15 - current_count
        if needed <= 0:
            continue
        
        # Get existing normalized addresses
        existing_normalized = get_normalized_addresses_set(normalized_list)
        
        # Import unique addresses
        imported = 0
        duplicates = 0
        
        for zero_addr in zero_list:
            if imported >= needed:
                break
            
            if not isinstance(zero_addr, dict):
                continue
            
            normalized = zero_addr.get('cheat_normalized_address', '')
            if not normalized:
                continue
            
            # Check for duplicates
            if normalized in existing_normalized:
                duplicates += 1
                continue
            
            # Add address
            normalized_list.append(zero_addr)
            existing_normalized.add(normalized)
            imported += 1
        
        total_imported += imported
        total_duplicates += duplicates
        
        new_count = len(normalized_list)
        if new_count >= 15:
            countries_completed += 1
            status = "✅ COMPLETED"
        else:
            countries_partial += 1
            status = f"⚠️  PARTIAL ({new_count}/15)"
        
        if imported > 0:
            print(f"{country:40s}: {current_count:2d} → {new_count:2d} addresses (+{imported}) {status}")
            if duplicates > 0:
                print(f"  {'':40s}  Skipped {duplicates} duplicates")
    
    # Save updated cache
    print()
    print("=" * 80)
    print("SAVING UPDATED CACHE")
    print("=" * 80)
    
    # Ensure addresses are in the right structure
    if 'addresses' not in normalized_cache:
        normalized_cache['addresses'] = normalized_addrs
    
    # Backup original
    import shutil
    shutil.copy('normalized_address_cache.json', 'normalized_address_cache.json.backup')
    print("Created backup: normalized_address_cache.json.backup")
    
    # Save updated cache
    with open('normalized_address_cache.json', 'w') as f:
        json.dump(normalized_cache, f, indent=2, ensure_ascii=False)
    
    print("Saved: normalized_address_cache.json")
    print()
    
    # Final summary
    print("=" * 80)
    print("IMPORT SUMMARY")
    print("=" * 80)
    print(f"Total addresses imported:     {total_imported}")
    print(f"Total duplicates skipped:     {total_duplicates}")
    print(f"Countries completed (15/15): {countries_completed}")
    print(f"Countries partially filled:   {countries_partial}")
    print()
    
    # Count final status
    final_counts = {}
    for country, addresses in normalized_addrs.items():
        if isinstance(addresses, list):
            count = len(addresses)
            if count < 15:
                final_counts[country] = count
    
    if final_counts:
        print(f"Countries still incomplete: {len(final_counts)}")
        for country, count in sorted(final_counts.items(), key=lambda x: x[1]):
            print(f"  {country}: {count}/15")
    else:
        print("✅ All countries have 15+ addresses!")
    
    print()

if __name__ == "__main__":
    try:
        import_addresses()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

