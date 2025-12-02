#!/usr/bin/env python3
"""
Strategy 3: Static Geospatial Dataset Mining
Uses pre-existing address datasets (OpenAddresses) to generate high-scoring addresses.
Pre-filters locally, then validates a small subset with Nominatim API.
"""

import sys
import os
import csv
import json
import time
import requests
import geonamescache
from typing import List, Dict, Tuple, Optional
import os
from collections import defaultdict

# Import address validation functions
from evaluate_addresses import (
    looks_like_address,
    check_with_nominatim,
    validate_address_region,
    COUNTRY_MAPPING
)

# Configuration
VALIDATOR_UID = 101
MINER_UID = 501
TARGET_SCORE = 1.0
TARGET_COUNT = 15
VALIDATION_SAMPLE_SIZE = 50  # Validate 50 pre-filtered addresses per country
NOMINATIM_SLEEP = 1.0

# OpenAddresses data source
OPENADDRESSES_BASE_URL = "https://data.openaddresses.io/runs"
USER_AGENT = "YanezCompliance/AddressGenerator (contact@example.com)"

def get_country_code_mapping() -> Dict[str, str]:
    """Get mapping from country names to ISO 3166-1 alpha-2 codes."""
    gc = geonamescache.GeonamesCache()
    countries = gc.get_countries()
    
    mapping = {}
    for code, data in countries.items():
        country_name = data.get('name', '').lower()
        mapping[country_name] = code.lower()
        
        # Add mapped variations
        for raw, mapped in COUNTRY_MAPPING.items():
            if mapped == country_name:
                mapping[raw] = code.lower()
    
    return mapping

def construct_address_string(record: Dict) -> Optional[str]:
    """
    Construct full address string from OpenAddresses record.
    Format: "[House Number], [Street Name], [City/District], [Postal Code], [Country Name]"
    Note: Uses comma after house number (like Poland format: "26, Siedlisko...")
    """
    # Extract fields (OpenAddresses uses lowercase field names)
    housenumber = record.get('housenumber', '').strip()
    street = record.get('street', '').strip()
    city = record.get('city', '').strip()
    district = record.get('district', '').strip()  # Additional location detail
    postcode = record.get('postcode', '').strip()
    country = record.get('country', '').strip()
    
    # Must have house number, street, and at least city or country
    if not housenumber or not street:
        return None
    
    if not city and not country:
        return None
    
    # Build address string (Poland format: "26, Siedlisko, ...")
    parts = []
    
    # Start with house number (comma after number for Poland format)
    parts.append(housenumber)
    
    # Add street
    parts.append(street)
    
    # Add district if available (before city)
    if district and district != city:
        parts.append(district)
    
    # Add city if available
    if city:
        parts.append(city)
    
    # Add postcode if available
    if postcode:
        parts.append(postcode)
    
    # Add country (capitalize for display)
    if country:
        # Convert country code to country name if needed
        country_name = country
        if len(country) == 2:
            # Try to get country name from code
            gc = geonamescache.GeonamesCache()
            countries = gc.get_countries()
            for code, data in countries.items():
                if code.lower() == country.lower():
                    country_name = data.get('name', country)
                    break
        
        parts.append(country_name)
    
    return ", ".join(parts)

def pre_filter_addresses(addresses: List[Dict], country_name: str) -> List[str]:
    """
    Pre-filter addresses locally using heuristic checks.
    Only keeps addresses with:
    - House number (preferred but not required for some countries)
    - Street name
    - Postal code (preferred)
    - Passes looks_like_address() check
    """
    filtered = []
    
    print(f"  🔍 Pre-filtering {len(addresses)} addresses locally...")
    sys.stdout.flush()
    
    for record in addresses:
        # Construct address string
        address = construct_address_string(record)
        
        if not address:
            continue
        
        # For countries like Russia, house number might not always be present
        # But we still prefer addresses with postal codes
        has_postcode = bool(record.get('postcode'))
        has_housenumber = bool(record.get('housenumber'))
        
        # Prefer addresses with both house number and postcode, but accept either
        if not has_postcode and not has_housenumber:
            continue
        
        # Heuristic check
        if not looks_like_address(address):
            continue
        
        # Region check (basic - address should contain country name)
        address_lower = address.lower()
        country_lower = country_name.lower()
        if country_lower not in address_lower:
            # Try mapped country name
            mapped_country = COUNTRY_MAPPING.get(country_lower, country_lower)
            if mapped_country not in address_lower:
                continue
        
        filtered.append(address)
    
    print(f"  ✅ {len(filtered)} addresses passed pre-filtering")
    sys.stdout.flush()
    
    return filtered

def download_openaddresses_data(country_code: str, proxies: Optional[Dict[str, str]] = None) -> List[Dict]:
    """
    Download OpenAddresses data for a country.
    Returns list of address records.
    
    Args:
        proxies: Optional dict with 'http' and 'https' proxy URLs
    """
    # OpenAddresses provides country-specific CSV files
    # Format: https://data.openaddresses.io/runs/{country_code}/latest.csv
    url = f"{OPENADDRESSES_BASE_URL}/{country_code}/latest.csv"
    
    print(f"  📥 Downloading OpenAddresses data for {country_code}...")
    sys.stdout.flush()
    
    try:
        response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30, stream=True, proxies=proxies)
        
        if response.status_code != 200:
            print(f"    ⚠️  HTTP {response.status_code} - data not available")
            return []
        
        # Parse CSV
        addresses = []
        import io
        csv_content = response.content.decode('utf-8')
        reader = csv.DictReader(io.StringIO(csv_content))
        
        for row in reader:
            addresses.append(row)
        
        print(f"  ✅ Downloaded {len(addresses)} address records")
        sys.stdout.flush()
        
        return addresses
        
    except Exception as e:
        print(f"    ❌ Error downloading data: {e}")
        return []

def generate_from_local_dataset(country_name: str, dataset_file: Optional[str] = None, proxies: Optional[Dict[str, str]] = None) -> List[Dict]:
    """
    Generate addresses from a local dataset file (CSV or JSON).
    If dataset_file is None, tries to download from OpenAddresses.
    
    Args:
        proxies: Optional dict with 'http' and 'https' proxy URLs
    """
    country_code_map = get_country_code_mapping()
    country_code = country_code_map.get(country_name.lower())
    
    if not country_code:
        print(f"  ⚠️  Country code not found for {country_name}")
        return []
    
    # Try local file first
    if dataset_file and os.path.exists(dataset_file):
        print(f"  📂 Loading from local dataset: {dataset_file}")
        addresses = []
        with open(dataset_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                addresses.append(row)
        return addresses
    
    # Download from OpenAddresses
    return download_openaddresses_data(country_code, proxies=proxies)

def validate_sample_addresses(pre_filtered: List[str], country_name: str, sample_size: int = 50, proxies: Optional[Dict[str, str]] = None) -> List[Tuple[str, float]]:
    """
    Validate a sample of pre-filtered addresses with Nominatim API.
    Returns list of (address, score) tuples for addresses that score 1.0.
    
    Args:
        proxies: Optional dict with 'http' and 'https' proxy URLs
    """
    # Sample addresses for validation
    sample = pre_filtered[:sample_size] if len(pre_filtered) > sample_size else pre_filtered
    
    print(f"  🔄 Validating {len(sample)} addresses with Nominatim API...")
    if proxies:
        print(f"  🌐 Using proxy: {proxies.get('https', proxies.get('http', 'N/A'))}")
    sys.stdout.flush()
    
    validated = []
    
    for idx, address in enumerate(sample, 1):
        print(f"    [{idx}/{len(sample)}] Testing: {address[:70]}...", end=" ")
        sys.stdout.flush()
        
        # Full validation check
        is_valid, score = full_validation_check(
            address,
            country_name,
            VALIDATOR_UID,
            MINER_UID,
            proxies=proxies
        )
        
        if is_valid and score == TARGET_SCORE:
            if address not in [v[0] for v in validated]:
                validated.append((address, score))
                print(f"✅ PASSED (Score: {score:.4f})")
            else:
                print(f"⏭️  DUPLICATE")
        else:
            if score > 0:
                print(f"❌ FAILED (Score: {score:.4f})")
            else:
                print(f"❌ FAILED")
        
        sys.stdout.flush()
        
        if len(validated) >= TARGET_COUNT:
            break
        
        time.sleep(NOMINATIM_SLEEP)
    
    print(f"\n  📊 Validated: {len(validated)}/{TARGET_COUNT} addresses with score {TARGET_SCORE}")
    sys.stdout.flush()
    
    return validated

def full_validation_check(address: str, seed_region: str, validator_uid: int, miner_uid: int, proxies: Optional[Dict[str, str]] = None) -> Tuple[bool, float]:
    """
    Applies all three core checks defined in the validator code.
    Returns (is_valid, score)
    
    Args:
        proxies: Optional dict with 'http' and 'https' proxy URLs
    """
    # Check 1: Heuristic Check
    if not looks_like_address(address):
        return False, 0.0
    
    # Check 2: Nominatim Score Check (must be 1.0)
    nominatim_result = check_with_nominatim(address, validator_uid, miner_uid, seed_region, "N/A", proxies=proxies)
    
    if nominatim_result == "TIMEOUT" or nominatim_result == 0.0:
        return False, 0.0
    
    # Extract score from result
    if isinstance(nominatim_result, dict):
        nominatim_score = nominatim_result.get('score', 0.0)
    elif isinstance(nominatim_result, (int, float)):
        nominatim_score = float(nominatim_result)
    else:
        return False, 0.0
    
    # Require score of 1.0 (area < 100 m²)
    if nominatim_score < TARGET_SCORE:
        return False, nominatim_score
    
    # Check 3: Region Validation Check
    if not validate_address_region(address, seed_region):
        return False, nominatim_score
    
    # Passed all checks with score 1.0
    return True, nominatim_score

def generate_addresses_for_country(country_name: str, dataset_file: Optional[str] = None, proxies: Optional[Dict[str, str]] = None) -> List[Tuple[str, str, float]]:
    """
    Generate and validate addresses for a country using static dataset.
    Returns list of (country, address, score) tuples.
    
    Args:
        proxies: Optional dict with 'http' and 'https' proxy URLs
    """
    print(f"\n{'='*80}")
    print(f"PROCESSING: {country_name.upper()}")
    print(f"{'='*80}")
    sys.stdout.flush()
    
    # Step 1: Load dataset
    raw_addresses = generate_from_local_dataset(country_name, dataset_file)
    
    if not raw_addresses:
        print(f"  ⚠️  No dataset available for {country_name}")
        return []
    
    # Step 2: Pre-filter locally
    pre_filtered = pre_filter_addresses(raw_addresses, country_name)
    
    if not pre_filtered:
        print(f"  ⚠️  No addresses passed pre-filtering")
        return []
    
    # Step 3: Validate sample with Nominatim
    validated = validate_sample_addresses(pre_filtered, country_name, VALIDATION_SAMPLE_SIZE, proxies=proxies)
    
    # Format results
    results = [(country_name, addr, score) for addr, score in validated]
    
    return results

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate addresses from static dataset")
    parser.add_argument("--country", type=str, required=True, help="Country name to test")
    parser.add_argument("--count", type=int, default=15, help="Number of addresses to generate (default: 15)")
    parser.add_argument("--output", type=str, default="validated_addresses.csv", help="Output CSV file")
    parser.add_argument("--dataset", type=str, help="Path to local dataset CSV file (optional)")
    parser.add_argument("--sample-size", type=int, default=50, help="Number of addresses to validate with API (default: 50)")
    parser.add_argument("--proxy", type=str, help="Proxy URL (e.g., http://proxy:port or https://proxy:port)")
    parser.add_argument("--proxy-http", type=str, help="HTTP proxy URL (e.g., http://proxy:port)")
    parser.add_argument("--proxy-https", type=str, help="HTTPS proxy URL (e.g., https://proxy:port)")
    
    args = parser.parse_args()
    
    # Setup proxies
    proxies = None
    if args.proxy:
        # Use same proxy for both HTTP and HTTPS
        proxies = {
            'http': args.proxy,
            'https': args.proxy
        }
    elif args.proxy_http or args.proxy_https:
        proxies = {}
        if args.proxy_http:
            proxies['http'] = args.proxy_http
        if args.proxy_https:
            proxies['https'] = args.proxy_https
    
    # Check environment variables if no proxy specified
    if not proxies:
        env_proxies = {}
        if os.getenv('HTTP_PROXY'):
            env_proxies['http'] = os.getenv('HTTP_PROXY')
        if os.getenv('HTTPS_PROXY'):
            env_proxies['https'] = os.getenv('HTTPS_PROXY')
        if env_proxies:
            proxies = env_proxies
    
    if proxies:
        print(f"🌐 Using proxy: {proxies}")
        sys.stdout.flush()
    
    global VALIDATION_SAMPLE_SIZE, TARGET_COUNT
    VALIDATION_SAMPLE_SIZE = args.sample_size
    TARGET_COUNT = args.count
    
    print("="*80)
    print("STATIC DATASET MINING STRATEGY")
    print("="*80)
    print(f"Target Score: {TARGET_SCORE} (area < 100 m²)")
    print(f"Target Count: {args.count} addresses per country")
    print(f"Validation Sample: {args.sample_size} addresses per country")
    print(f"Test Country: {args.country}")
    print("="*80)
    sys.stdout.flush()
    
    # Generate and validate addresses
    validated_addresses = generate_addresses_for_country(args.country, args.dataset, proxies=proxies)
    
    if not validated_addresses:
        print(f"\n❌ No valid addresses found for {args.country}")
        sys.exit(1)
    
    # Export to CSV
    print(f"\n💾 Exporting to {args.output}...")
    sys.stdout.flush()
    
    with open(args.output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Country', 'Address', 'Nominatim_Score'])
        
        for country, address, score in validated_addresses:
            writer.writerow([country, address, score])
    
    print(f"✅ Successfully exported {len(validated_addresses)} addresses to {args.output}")
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Country: {args.country}")
    print(f"Validated Addresses: {len(validated_addresses)}/{args.count}")
    print(f"All addresses have score: {TARGET_SCORE}")
    print("="*80)
    
    # Show addresses
    print("\n📋 Validated addresses:")
    for i, (country, address, score) in enumerate(validated_addresses, 1):
        print(f"  {i}. {address}")
        print(f"     Score: {score:.4f}")

if __name__ == "__main__":
    main()

