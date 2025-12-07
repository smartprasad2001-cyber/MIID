#!/usr/bin/env python3
"""
Generate addresses for countries with partial addresses (1-14) using REVERSE GEOCODING ONLY.
Stores results in a separate cache file.

For countries with partial addresses:
- Loads existing addresses from normalized_address_cache.json
- Generates remaining addresses to reach 15 total using REVERSE GEOCODING ONLY
- Ensures all 15 addresses have unique normalized strings
- Skips countries with 0 addresses and countries with 15 addresses
"""

import os
import sys
import json
import time
import signal
import shutil
import math
from typing import List, Tuple

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None

# Put MIID validator on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'MIID', 'validator'))

from reward import (
    looks_like_address,
    extract_city_country,
    validate_address_region,
    check_with_nominatim
)
from cheat_detection import normalize_address_for_deduplication

# Import from main script
sys.path.insert(0, os.path.dirname(__file__))
# Import functions from main script
import importlib.util
spec = importlib.util.spec_from_file_location("generate_address_cache_priority", 
    os.path.join(os.path.dirname(__file__), "generate_address_cache_priority.py"))
main_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main_module)

# Extract needed functions and constants
fetch_nodes_from_overpass_bbox = main_module.fetch_nodes_from_overpass_bbox
reverse_geocode = main_module.reverse_geocode
country_to_code = main_module.country_to_code
NOMINATIM_SLEEP = main_module.NOMINATIM_SLEEP
OVERPASS_SLEEP = main_module.OVERPASS_SLEEP
MAX_OVERPASS_NODES = main_module.MAX_OVERPASS_NODES
USER_AGENT = main_module.USER_AGENT
DISABLE_REVERSE_COUNTRIES = main_module.DISABLE_REVERSE_COUNTRIES

# Helper function to create bounding box from city
def create_bbox_from_city(city_lat: float, city_lon: float, radius_km: float = 5.0) -> Tuple[float, float, float, float]:
    """Create a bounding box around a city center."""
    # Approximate: 1 degree latitude ≈ 111 km
    lat_offset = radius_km / 111.0
    # Longitude offset depends on latitude
    lon_offset = radius_km / (111.0 * abs(math.cos(math.radians(city_lat))))
    
    min_lat = city_lat - lat_offset
    max_lat = city_lat + lat_offset
    min_lon = city_lon - lon_offset
    max_lon = city_lon + lon_offset
    
    return (min_lat, min_lon, max_lat, max_lon)

import geonamescache

# Separate cache file for zero-address countries
ZERO_COUNTRIES_CACHE_FILE = os.path.join(os.path.dirname(__file__), "zero_addresses_cache.json")

# Global flag for graceful shutdown
_shutdown_requested = False

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    global _shutdown_requested
    if not _shutdown_requested:
        print("\n\n⚠️  Ctrl+C detected. Saving progress...")
        _shutdown_requested = True
    else:
        print("\n\n⚠️  Force exit requested. Exiting immediately...")
        sys.exit(1)

signal.signal(signal.SIGINT, signal_handler)

def save_cache(address_cache: dict):
    """Save cache to separate file."""
    try:
        backup_file = ZERO_COUNTRIES_CACHE_FILE + ".backup"
        if os.path.exists(ZERO_COUNTRIES_CACHE_FILE):
            shutil.copy2(ZERO_COUNTRIES_CACHE_FILE, backup_file)
        
        temp_file = ZERO_COUNTRIES_CACHE_FILE + ".tmp"
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump({
                "description": "Addresses for countries with partial addresses (1-14) using REVERSE GEOCODING ONLY",
                "created_at": time.strftime('%Y-%m-%d'),
                "addresses": address_cache
            }, f, indent=2, ensure_ascii=False)
        
        if os.path.exists(ZERO_COUNTRIES_CACHE_FILE):
            os.replace(temp_file, ZERO_COUNTRIES_CACHE_FILE)
        else:
            os.rename(temp_file, ZERO_COUNTRIES_CACHE_FILE)
        
        print(f"✅ Cache saved to {ZERO_COUNTRIES_CACHE_FILE}")
    except Exception as e:
        print(f"❌ Error saving cache: {e}")

def generate_addresses_for_zero_country(
    country: str,
    per_country: int = 15,
    verbose: bool = True,
    existing_normalized_addresses: set = None,
) -> List[dict]:
    """
    Generate addresses for a country using REVERSE GEOCODING ONLY.
    Accepts addresses with score >= 0.9.
    
    Args:
        country: Country name
        per_country: Number of addresses to generate
        verbose: Enable verbose logging
        existing_normalized_addresses: Set of normalized addresses that already exist (for uniqueness check)
    """
    if verbose:
        print(f"\n  🚀 Starting address generation for {country} (REVERSE GEOCODING ONLY)...")
        sys.stdout.flush()
    
    gc = geonamescache.GeonamesCache()
    country_code = country_to_code(country)
    
    if verbose:
        print(f"  📍 Country code: {country_code}")
    
    # Get cities for this country
    cities = [
        c for c in gc.get_cities().values()
        if c.get("countrycode", "").upper() == (country_code or "").upper()
    ]
    
    if not cities:
        if verbose:
            print(f"  ❌ No cities found for {country}")
        return []
    
    # Sort by population
    cities_sorted = sorted(
        cities, key=lambda x: x.get("population", 0) or 0, reverse=True
    )
    
    if verbose:
        print(f"  ✅ Found {len(cities_sorted)} cities for {country}")
        print(f"  🔄 Using REVERSE GEOCODING ONLY (no local node validation)")
    
    results = []
    tried_nodes = set()
    normalized_addresses_seen = set()
    cheat_normalized_addresses_seen = set()
    
    # Pre-load existing normalized addresses to ensure uniqueness
    if existing_normalized_addresses:
        cheat_normalized_addresses_seen.update(existing_normalized_addresses)
        if verbose:
            print(f"  🔍 Pre-loaded {len(existing_normalized_addresses)} existing normalized addresses for uniqueness check")
    
    stats = {
        "overpass_queries": 0,
        "reverse_geocoded": 0,
        "validation_passed": 0,
        "validation_failed": 0,
        "duplicates_skipped": 0,
    }
    
    # Process cities until we have enough addresses
    for city_idx, city in enumerate(cities_sorted, 1):
        if _shutdown_requested:
            break
        if len(results) >= per_country:
            break
        
        city_name = city.get("name", "Unknown")
        lat = city.get("latitude")
        lon = city.get("longitude")
        
        if not lat or not lon:
            continue
        
        if verbose:
            print(f"\n  🏙️  Processing city {city_idx}/{len(cities_sorted)}: {city_name}")
        
        # Create bounding box for city (5km radius)
        bbox = create_bbox_from_city(lat, lon, radius_km=5.0)
        
        # Query Overpass for nodes
        if _shutdown_requested:
            break
        nodes = fetch_nodes_from_overpass_bbox(bbox, verbose=verbose)
        stats["overpass_queries"] += 1
        
        if not nodes:
            if verbose:
                print(f"     ⚠️  No nodes found for {city_name}")
            time.sleep(OVERPASS_SLEEP)
            continue
        
        if verbose:
            print(f"     🔄 Processing {len(nodes)} nodes from {city_name}...")
        
        processed = 0
        for n in nodes:
            if _shutdown_requested:
                break
            if len(results) >= per_country:
                break
            
            element_id = n.get("id")
            if element_id in tried_nodes:
                stats["duplicates_skipped"] += 1
                continue
            tried_nodes.add(element_id)
            processed += 1
            
            # REVERSE GEOCODING ONLY - no local node validation, always use reverse geocoding
            lat = n.get("lat")
            lon = n.get("lon")
            if not lat or not lon:
                continue
            
            # Use reverse geocoding (REQUIRED - no local validation path)
            if _shutdown_requested:
                break
            nom = reverse_geocode(lat, lon, zoom=19, verbose=verbose and processed % 10 == 0)
            
            if not nom:
                stats["validation_failed"] += 1
                continue
            
            stats["reverse_geocoded"] += 1
            nom_display = nom.get("display_name", "")
            
            if not nom_display:
                stats["validation_failed"] += 1
                continue
            
            # Validate with all 4 checks
            # 1. looks_like_address
            if not looks_like_address(nom_display):
                stats["validation_failed"] += 1
                if verbose and processed % 10 == 0:
                    print(f"     ❌ REJECTED: looks_like_address failed")
                continue
            
            # 2. validate_address_region
            if not validate_address_region(nom_display, country):
                stats["validation_failed"] += 1
                if verbose and processed % 10 == 0:
                    print(f"     ❌ REJECTED: region validation failed")
                continue
            
            # 3. check_with_nominatim (accept score >= 0.9)
            api_result = check_with_nominatim(
                address=nom_display,
                validator_uid=1,
                miner_uid=1,
                seed_address=country,
                seed_name="ZeroCountry"
            )
            
            score = 0.0
            if isinstance(api_result, dict):
                score = api_result.get("score", 0.0)
            elif isinstance(api_result, (int, float)):
                score = float(api_result)
            
            if score < 0.9:  # Accept 0.9 or higher
                stats["validation_failed"] += 1
                if verbose and processed % 10 == 0:
                    print(f"     ❌ REJECTED: API score {score:.2f} < 0.9")
                continue
            
            # 4. normalize_address_for_deduplication (uniqueness)
            cheat_norm = normalize_address_for_deduplication(nom_display)
            
            # Check against existing normalized addresses (from main cache) AND newly found addresses
            if cheat_norm in cheat_normalized_addresses_seen:
                stats["duplicates_skipped"] += 1
                if verbose and processed % 10 == 0:
                    print(f"     ⚠️  SKIPPING: Duplicate normalized address (already exists)")
                continue
            
            # Add to results and track normalized address
            cheat_normalized_addresses_seen.add(cheat_norm)
            
            address_dict = {
                "address": nom_display,
                "score": score,
                "cheat_normalized_address": cheat_norm,
                "source_city": city_name,
                "country": country
            }
            
            results.append(address_dict)
            stats["validation_passed"] += 1
            
            if verbose:
                print(f"     ✅✅✅ ACCEPTED (score: {score:.2f}, {len(results)}/{per_country}): {nom_display[:80]}...")
            
            if _shutdown_requested:
                break
            time.sleep(NOMINATIM_SLEEP)
        
        if verbose:
            print(f"     📊 {city_name} summary: {processed} processed, {len(results)}/{per_country} accepted")
        
        if _shutdown_requested:
            break
        time.sleep(OVERPASS_SLEEP)
    
    if verbose:
        print(f"\n  📊 Final stats for {country}:")
        print(f"     Overpass queries: {stats['overpass_queries']}")
        print(f"     Reverse geocoded: {stats['reverse_geocoded']}")
        print(f"     Validation passed: {stats['validation_passed']}")
        print(f"     Validation failed: {stats['validation_failed']}")
        print(f"     Duplicates skipped: {stats['duplicates_skipped']}")
    
    return results

def main():
    """Main function to process countries with partial addresses (1-14) using REVERSE GEOCODING ONLY."""
    global _shutdown_requested
    
    # Load main cache to find countries with partial addresses (1-14) ONLY
    main_cache_file = os.path.join(os.path.dirname(__file__), "normalized_address_cache.json")
    
    if not os.path.exists(main_cache_file):
        print(f"❌ Main cache file not found: {main_cache_file}")
        return
    
    with open(main_cache_file, 'r') as f:
        main_cache_data = json.load(f)
    
    addresses_by_country = main_cache_data.get('addresses', {})
    
    # Find countries with partial addresses (1-14) ONLY - excluding disabled countries
    # Skip countries with 0 addresses and countries with exactly 15 addresses
    countries_to_process = []
    countries_with_existing = {}  # Store existing addresses for partial countries
    
    for country, addresses in addresses_by_country.items():
        address_count = len(addresses)
        if country in DISABLE_REVERSE_COUNTRIES:
            continue
        
        # Skip countries with 0 addresses - only process countries with 1-14 addresses
        if 1 <= address_count < 15:
            # Country with partial addresses (1-14) - need to generate remaining
            countries_to_process.append((country, address_count, addresses))
            countries_with_existing[country] = addresses
    
    if not countries_to_process:
        print("✅ No countries with partial addresses (1-14) found (excluding disabled countries)")
        return
    
    print("=" * 80)
    print("GENERATING ADDRESSES FOR COUNTRIES WITH PARTIAL ADDRESSES (1-14)")
    print("=" * 80)
    print(f"Countries to process: {len(countries_to_process)}")
    print(f"  - Only processing countries with 1-14 addresses (skipping 0 and 15)")
    print(f"Using reverse geocoding ONLY")
    print(f"Accepting addresses with score >= 0.9")
    print(f"Cache file: {ZERO_COUNTRIES_CACHE_FILE}")
    print("=" * 80)
    print()
    
    # Load or create zero countries cache
    if os.path.exists(ZERO_COUNTRIES_CACHE_FILE):
        with open(ZERO_COUNTRIES_CACHE_FILE, 'r') as f:
            zero_cache_data = json.load(f)
        zero_address_cache = zero_cache_data.get('addresses', {})
        print(f"📂 Loaded existing zero countries cache: {len(zero_address_cache)} countries")
    else:
        zero_address_cache = {}
        print(f"📂 Creating new zero countries cache")
    
    # Process each country
    for idx, (country, existing_count_in_main, existing_addresses_list) in enumerate(sorted(countries_to_process, key=lambda x: x[0]), 1):
        if _shutdown_requested:
            print("\n⚠️  Shutdown requested. Saving progress...")
            save_cache(zero_address_cache)
            break
        
        # Skip if already has 15 addresses in zero cache
        existing_count_in_zero = len(zero_address_cache.get(country, []))
        total_existing = existing_count_in_main + existing_count_in_zero
        
        if total_existing >= 15:
            print(f"\n⏭️  [{idx}/{len(countries_to_process)}] Skipping {country}: Already has {total_existing} addresses total")
            continue
        
        print("\n" + "=" * 80)
        print(f"[{idx}/{len(countries_to_process)}] 🏳️  PROCESSING: {country}")
        print(f"   Existing in main cache: {existing_count_in_main}/15")
        print(f"   Existing in zero cache: {existing_count_in_zero}/15")
        print(f"   Total existing: {total_existing}/15")
        print(f"   Need to generate: {15 - total_existing} more")
        print(f"   Started at: {time.strftime('%H:%M:%S')}")
        print("=" * 80)
        
        # Load existing normalized addresses from main cache for uniqueness check
        existing_normalized_addresses = set()
        if existing_addresses_list:
            for addr_obj in existing_addresses_list:
                if isinstance(addr_obj, dict):
                    addr_str = addr_obj.get("address", "")
                    if addr_str:
                        # Get cheat_normalized_address if already computed, otherwise compute it
                        cheat_norm = addr_obj.get("cheat_normalized_address") or (
                            normalize_address_for_deduplication(addr_str)
                        )
                        if cheat_norm:
                            existing_normalized_addresses.add(cheat_norm)
                elif isinstance(addr_obj, str):
                    # Backward compatibility: plain string
                    cheat_norm = normalize_address_for_deduplication(addr_obj)
                    if cheat_norm:
                        existing_normalized_addresses.add(cheat_norm)
        
        # Also load from zero cache if country exists there
        if country in zero_address_cache:
            for addr_obj in zero_address_cache[country]:
                if isinstance(addr_obj, dict):
                    addr_str = addr_obj.get("address", "")
                    if addr_str:
                        cheat_norm = addr_obj.get("cheat_normalized_address") or (
                            normalize_address_for_deduplication(addr_str)
                        )
                        if cheat_norm:
                            existing_normalized_addresses.add(cheat_norm)
        
        if existing_normalized_addresses:
            print(f"   🔍 Loaded {len(existing_normalized_addresses)} existing normalized addresses for uniqueness check")
        
        try:
            # Generate addresses (only need remaining)
            remaining_needed = max(0, 15 - total_existing)
            new_addresses = generate_addresses_for_zero_country(
                country,
                per_country=remaining_needed,
                verbose=True,
                existing_normalized_addresses=existing_normalized_addresses
            )
            
            # Add to cache
            if country not in zero_address_cache:
                zero_address_cache[country] = []
            
            zero_address_cache[country].extend(new_addresses)
            
            final_count_in_zero = len(zero_address_cache[country])
            total_final = existing_count_in_main + final_count_in_zero
            print(f"\n✅ COMPLETED: {country}")
            print(f"   Total addresses (main + zero): {total_final}/15")
            print(f"   Generated this run: {len(new_addresses)}")
            
            # Save after each country
            save_cache(zero_address_cache)
            
        except KeyboardInterrupt:
            print(f"\n⚠️  Interrupted by user")
            save_cache(zero_address_cache)
            break
        except Exception as e:
            print(f"\n❌ Error processing {country}: {e}")
            import traceback
            traceback.print_exc()
            continue
        
        if _shutdown_requested:
            break
    
    # Final save
    save_cache(zero_address_cache)
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    total_countries = len(zero_address_cache)
    
    # Calculate complete countries (considering both main cache and zero cache)
    complete_countries = 0
    for country in zero_address_cache.keys():
        zero_count = len(zero_address_cache[country])
        main_count = len(addresses_by_country.get(country, []))
        if (zero_count + main_count) >= 15:
            complete_countries += 1
    
    print(f"Total countries processed: {total_countries}")
    print(f"Complete countries (15+ addresses total): {complete_countries}")
    print(f"Cache file: {ZERO_COUNTRIES_CACHE_FILE}")
    if _shutdown_requested:
        print(f"\n⚠️  Script stopped by user (Ctrl+C). Progress saved.")

if __name__ == "__main__":
    main()

