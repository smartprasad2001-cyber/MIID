#!/usr/bin/env python3
"""
Generate real addresses for disputed regions (Crimea, Donetsk, Luhansk)
using Overpass API and Nominatim, replacing synthetic addresses.
"""

import json
import sys
import os

# Add parent directory to path to import from generate_address_cache
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from generate_address_cache import (
    generate_addresses_for_country,
    CACHE_FILE,
    save_cache_safely
)

# Known coordinates for major cities in disputed regions
DISPUTED_REGIONS = {
    "Crimea": {
        "bboxes": [
            # Simferopol (capital of Crimea)
            (44.95, 33.95, 45.05, 34.15),
            # Sevastopol
            (44.55, 33.45, 44.65, 33.65),
            # Yalta
            (44.45, 34.05, 44.55, 34.25),
        ],
        "cities": ["Simferopol", "Sevastopol", "Yalta", "Kerch", "Feodosia"]
    },
    "Donetsk": {
        "bboxes": [
            # Donetsk city center
            (47.95, 37.75, 48.05, 37.95),
            # Mariupol (nearby major city)
            (47.05, 37.50, 47.15, 37.70),
        ],
        "cities": ["Donetsk", "Mariupol", "Makiivka", "Horlivka"]
    },
    "Luhansk": {
        "bboxes": [
            # Luhansk city center
            (48.55, 39.25, 48.65, 39.45),
            # Alchevsk (nearby city)
            (48.45, 38.75, 48.55, 38.95),
        ],
        "cities": ["Luhansk", "Alchevsk", "Krasnyi Luch", "Antratsyt"]
    }
}

def generate_for_disputed_region(region_name: str, verbose: bool = True):
    """Generate addresses for a disputed region using known coordinates."""
    print("\n" + "="*80)
    print(f"🏳️  PROCESSING DISPUTED REGION: {region_name}")
    print("="*80)
    
    # Temporarily add dense bboxes for this region
    from generate_address_cache import DENSE_CITY_BBOXES
    original_bboxes = DENSE_CITY_BBOXES.get(region_name, [])
    DENSE_CITY_BBOXES[region_name] = DISPUTED_REGIONS[region_name]["bboxes"]
    
    try:
        # Use the normal generation function
        # Since these regions aren't in GeonamesCache, we'll need to handle them specially
        # But first, let's try using the normal function with the bboxes we set
        addresses = generate_addresses_for_country(region_name, per_country=15, verbose=verbose)
        
        if len(addresses) >= 15:
            print(f"✅ Successfully generated {len(addresses)} addresses for {region_name}")
            return addresses[:15]
        else:
            print(f"⚠️ Only generated {len(addresses)} addresses for {region_name} (need 15)")
            return addresses
    except Exception as e:
        import traceback
        print(f"❌ Error generating for {region_name}: {type(e).__name__}: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return []
    finally:
        # Restore original bboxes
        if original_bboxes:
            DENSE_CITY_BBOXES[region_name] = original_bboxes
        elif region_name in DENSE_CITY_BBOXES:
            del DENSE_CITY_BBOXES[region_name]

def main():
    """Generate real addresses for disputed regions and update cache."""
    print("="*80)
    print("GENERATING REAL ADDRESSES FOR DISPUTED REGIONS")
    print("="*80)
    print("Regions: Crimea, Donetsk, Luhansk")
    print("="*80)
    
    # Load existing cache
    address_cache = {}
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                existing = json.load(f)
                address_cache = existing.get("addresses", {}) or {}
                print(f"📦 Loaded existing cache: {len(address_cache)} countries")
        except Exception as e:
            print(f"⚠️ Could not load existing cache: {e}")
            address_cache = {}
    
    # Generate for each disputed region
    disputed_regions = ["Crimea", "Donetsk", "Luhansk"]
    results = {}
    
    for region in disputed_regions:
        print(f"\n🔄 Processing {region}...")
        addresses = generate_for_disputed_region(region, verbose=True)
        results[region] = addresses
        
        if len(addresses) >= 15:
            address_cache[region] = addresses[:15]
            print(f"✅ {region}: {len(addresses[:15])}/15 addresses generated")
        else:
            print(f"⚠️ {region}: Only {len(addresses)}/15 addresses generated")
            if len(addresses) > 0:
                address_cache[region] = addresses  # Store partial results
    
    # Save updated cache
    print("\n" + "="*80)
    print("💾 SAVING UPDATED CACHE")
    print("="*80)
    
    # Calculate statistics
    total_countries = len(address_cache)
    complete = len([c for c in address_cache.keys() if len(address_cache[c]) >= 15])
    
    if save_cache_safely(address_cache, [], CACHE_FILE, total_countries, force=True):
        print(f"✅ Cache saved successfully!")
        print(f"   - Total countries: {total_countries}")
        print(f"   - Complete (15 addresses): {complete}")
        print(f"   - Disputed regions updated:")
        for region in disputed_regions:
            count = len(address_cache.get(region, []))
            status = "✅" if count >= 15 else "⚠️"
            print(f"     {status} {region}: {count} addresses")
    else:
        print("❌ Failed to save cache")
        return 1
    
    print("\n" + "="*80)
    print("✅ COMPLETE!")
    print("="*80)
    return 0

if __name__ == "__main__":
    sys.exit(main())

