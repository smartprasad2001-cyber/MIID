#!/usr/bin/env python3
"""
Test script to generate Afghanistan addresses and compare with manually generated ones.
"""

import json
import sys
import os
import requests
import time
from unidecode import unidecode

# Add MIID validator to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'MIID', 'validator'))
from cheat_detection import normalize_address_for_deduplication
from reward import (
    looks_like_address,
    validate_address_region,
    check_with_nominatim,
    extract_city_country
)

USER_AGENT = "MIIDSubnet/1.0 (contact: prasadpsd2001@gmail.com)"

def fetch_nominatim(query: str):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": query, "format": "json", "addressdetails": 1, "limit": 5}
    headers = {"User-Agent": USER_AGENT}
    resp = requests.get(url, params=params, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.json()

def extract_components(nom_json):
    if not nom_json:
        return {}
    base = nom_json[0]
    addr = base.get("address", {})
    components = {
        "road": addr.get("road"),
        "suburb": addr.get("suburb"),
        "residential": addr.get("residential"),
        "city": addr.get("city"),
        "county": addr.get("county"),
        "state": addr.get("state"),
        "postcode": addr.get("postcode"),
        "country": addr.get("country"),
    }
    return {k: v for k, v in components.items() if v}

def transliterate_road(road: str) -> str:
    """Transliterate Persian/Arabic script road names to English using unidecode."""
    if not road:
        return road
    has_non_latin = any(ord(c) > 127 for c in road)
    if has_non_latin:
        transliterated = unidecode(road)
        words = transliterated.split()
        transliterated = ' '.join(word.capitalize() for word in words)
        return transliterated
    return road

def abbreviate_road(road: str) -> str:
    """Create abbreviation variations of road names."""
    abbreviations = {
        'Road': 'Rd',
        'Street': 'St',
        'Avenue': 'Ave',
        'Boulevard': 'Blvd',
        'Drive': 'Dr',
        'Lane': 'Ln',
        'Place': 'Pl',
    }
    result = road
    for full, abbrev in abbreviations.items():
        if full in result:
            result = result.replace(full, abbrev)
            break
    return result

def extract_district_province_names(components: dict, display_name: str, seed_city: str = None) -> list:
    """Extract valid district/province names that appear in display_name."""
    valid_names = []
    city_name = seed_city if seed_city else components.get("city", "")
    
    county = components.get("county", "")
    state = components.get("state", "")
    suburb = components.get("suburb", "")
    
    # Pattern 1: Direct county/state if they contain "District" or "Province"
    if county and county in display_name:
        county_lower = county.lower()
        if 'district' in county_lower or 'province' in county_lower:
            valid_names.append(county)
        if city_name:
            city_lower = city_name.lower()
            if city_lower in county_lower or any(word in county_lower for word in city_lower.split()):
                valid_names.append(f"{city_name} District")
                valid_names.append(f"{city_name} Province")
    
    if state and state in display_name:
        state_lower = state.lower()
        if 'province' in state_lower or 'district' in state_lower:
            valid_names.append(state)
        if city_name:
            city_lower = city_name.lower()
            if city_lower in state_lower or any(word in state_lower for word in city_lower.split()):
                valid_names.append(f"{city_name} Province")
    
    # Pattern 2: Suburb patterns like "3rd District"
    if suburb and suburb in display_name:
        suburb_lower = suburb.lower()
        ordinals = ['1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th', '10th',
                   '11th', '12th', '13th', '14th', '15th']
        if any(ord in suburb_lower for ord in ordinals) or 'district' in suburb_lower:
            valid_names.append(suburb)
    
    return list(dict.fromkeys(valid_names))

def generate_variations(base_road: str, components: dict, nominatim_result: dict = None, seed_city: str = None) -> list:
    """Generate valid variations matching manually generated address patterns."""
    if not nominatim_result:
        return []
    
    disp = nominatim_result.get("display_name", "")
    road = components.get("road")
    city = seed_city if seed_city else components.get("city")
    postcode = components.get("postcode")
    country = components.get("country")
    
    if not (road and city and country):
        return []
    
    variations = []
    
    # Generate road variations
    road_variations = [road]
    transliterated_road = transliterate_road(road)
    if transliterated_road != road:
        road_variations.append(transliterated_road)
        abbrev_trans = abbreviate_road(transliterated_road)
        if abbrev_trans != transliterated_road:
            road_variations.append(abbrev_trans)
    
    abbrev_road = abbreviate_road(road)
    if abbrev_road != road:
        road_variations.append(abbrev_road)
    
    road_variations = list(dict.fromkeys(road_variations))
    
    # Extract valid district/province names
    district_province_names = extract_district_province_names(components, disp, seed_city=city)
    
    # Generate variations for each road variation
    for road_var in road_variations:
        # Base variation
        if postcode:
            variations.append(f"{road_var}, {city}, {postcode}, {country}")
        else:
            variations.append(f"{road_var}, {city}, {country}")
        
        # Add district/province variations
        for district_province in district_province_names:
            if postcode:
                # Format 1: ROAD, District City, POSTCODE, COUNTRY (no comma)
                variations.append(f"{road_var}, {district_province} {city}, {postcode}, {country}")
                # Format 2: ROAD, District, City, POSTCODE, COUNTRY (with comma)
                variations.append(f"{road_var}, {district_province}, {city}, {postcode}, {country}")
    
    return list(dict.fromkeys(variations))

# Test with Afghanistan addresses
print("=" * 80)
print("TESTING AFGHANISTAN ADDRESS GENERATION")
print("=" * 80)
print()

# Load cache
with open('normalized_address_cache.json', 'r') as f:
    cache_data = json.load(f)

# Get Afghanistan addresses
afghanistan_addresses = cache_data.get('addresses', {}).get('Afghanistan', [])

for addr_obj in afghanistan_addresses:
    original_addr = addr_obj.get('address', '')
    print(f"\n{'='*80}")
    print(f"Testing: {original_addr}")
    print(f"{'='*80}")
    
    # Fetch Nominatim
    print(f"Fetching Nominatim...")
    nom_data = fetch_nominatim(original_addr)
    time.sleep(1)
    
    if not nom_data:
        print("  ❌ No Nominatim results")
        continue
    
    # Extract components
    components = extract_components(nom_data)
    if not components.get('road') or not components.get('city'):
        print(f"  ❌ Missing road or city")
        continue
    
    # Extract city from seed
    seed_city, seed_country = extract_city_country(original_addr)
    if not seed_city:
        seed_city = components.get('city')
    
    # Normalize city name (capitalize)
    if seed_city:
        seed_city = seed_city.capitalize()
    
    print(f"  Road: {components.get('road')}")
    print(f"  City (from seed, normalized): {seed_city}")
    print(f"  Components: county={components.get('county')}, state={components.get('state')}, suburb={components.get('suburb')}")
    print(f"  Display name: {nom_data[0].get('display_name', '')[:100]}...")
    
    # Test district extraction
    from generate_address_variations_from_cache import extract_district_province_names
    district_names = extract_district_province_names(components, nom_data[0].get('display_name', ''), seed_city=seed_city)
    print(f"  Extracted district/province names: {district_names}")
    
    # Generate variations
    variations = generate_variations(
        components.get('road'),
        components,
        nom_data[0],
        seed_city=seed_city
    )
    
    print(f"\n  Generated {len(variations)} variations:")
    for i, var in enumerate(variations, 1):
        print(f"    {i}. {var}")
    
    # Test validation
    print(f"\n  Testing validation:")
    passed = []
    for var in variations[:10]:  # Test first 10
        try:
            if looks_like_address(var):
                if validate_address_region(var, original_addr):
                    api_result = check_with_nominatim(
                        address=var,
                        validator_uid=1,
                        miner_uid=1,
                        seed_address=original_addr,
                        seed_name="Test"
                    )
                    if isinstance(api_result, dict) and api_result.get("score", 0) >= 0.9:
                        passed.append((var, api_result.get("score", 0)))
                        print(f"      ✅ {var[:60]}... (score: {api_result.get('score', 0):.2f})")
                    else:
                        print(f"      ❌ {var[:60]}... (API failed)")
                else:
                    print(f"      ❌ {var[:60]}... (region validation failed)")
            else:
                print(f"      ❌ {var[:60]}... (looks_like_address failed)")
        except Exception as e:
            print(f"      ❌ {var[:60]}... (error: {e})")
        time.sleep(1)
    
    print(f"\n  ✅ Passed: {len(passed)}/{len(variations[:10])}")
    if passed:
        print(f"  Working addresses:")
        for addr, score in passed:
            print(f"    - {addr} (score: {score:.2f})")
    
    print()

