#!/usr/bin/env python3
"""
Analyze why Poland addresses score 1.0 and others fail.
Compare address formats and validation results.
"""

import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'MIID'))

from validator.reward import _grade_address_variations, validate_address_region, looks_like_address, check_with_nominatim

class MockValidator:
    def __init__(self):
        self.uid = 0

class MockMiner:
    def __init__(self):
        self.uid = 0

validator = MockValidator()
miner = MockMiner()

# Load cache
with open('address_cache.json', 'r') as f:
    cache = json.load(f)

print("=" * 80)
print("ANALYZING POLAND vs OTHER COUNTRIES")
print("=" * 80)

# Compare Poland with failing countries
countries_to_test = {
    'Poland': cache['addresses']['Poland'][:15],
    'Philippines': cache['addresses']['Philippines'][:15],
    'Russia': cache['addresses']['Russia'][:15],
    'Albania': cache['addresses']['Albania'][:15]
}

for country, addresses in countries_to_test.items():
    print(f"\n{'='*80}")
    print(f"📍 {country.upper()}")
    print(f"{'='*80}")
    
    # Analyze first 3 addresses in detail
    print(f"\n📋 Analyzing first 3 addresses:")
    for i, addr in enumerate(addresses[:3], 1):
        print(f"\n  {i}. {addr}")
        
        # Check format
        first_part = addr.split(',')[0].strip()
        has_number = any(char.isdigit() for char in first_part[:5])
        print(f"     Format: First part = '{first_part}'")
        print(f"     Has number in first 5 chars: {has_number}")
        
        # Validate each check
        looks = looks_like_address(addr)
        region = validate_address_region(addr, country)
        print(f"     ✅ Looks Like Address: {looks}")
        print(f"     ✅ Region Match: {region}")
        
        if looks and region:
            print(f"     🔄 Testing API...")
            sys.stdout.flush()
            api_result = check_with_nominatim(addr, validator.uid, miner.uid, country, 'Test')
            if isinstance(api_result, dict):
                score = api_result.get('score', 0)
                area = api_result.get('min_area', 0)
                print(f"     ✅ API Score: {score:.4f}, Area: {area:.2f} m²")
            elif isinstance(api_result, (int, float)):
                print(f"     ⚠️  API Score: {api_result:.4f}")
            else:
                print(f"     ❌ API Failed: {api_result}")
        else:
            print(f"     ⏭️  Skipping API (failed earlier checks)")
    
    # Test all 15 with rewards.py
    print(f"\n🔄 Testing all 15 addresses with rewards.py...")
    sys.stdout.flush()
    
    variations = {
        'John Smith': [
            ['John Smith', '1990-01-01', addr] for addr in addresses[:15]
        ]
    }
    
    result = _grade_address_variations(
        variations=variations,
        seed_addresses=[country],
        miner_metrics={},
        validator_uid=validator.uid,
        miner_uid=miner.uid
    )
    
    overall_score = result.get('overall_score', 0.0)
    breakdown = result.get('detailed_breakdown', {})
    validation_results = breakdown.get('validation_results', {}).get('John Smith', [])
    
    if validation_results:
        looks_count = sum(1 for r in validation_results if r.get('looks_like_address', False))
        region_count = sum(1 for r in validation_results if r.get('region_match', False))
        passed_count = sum(1 for r in validation_results if r.get('passed_validation', False))
        
        print(f"\n  📊 Validation Results:")
        print(f"     - Looks Like Address: {looks_count}/15")
        print(f"     - Region Match: {region_count}/15")
        print(f"     - Passed Validation: {passed_count}/15")
        
        # Show failed addresses
        if region_count < 15:
            print(f"\n  ❌ Failed Region Validation ({15 - region_count} addresses):")
            for r in validation_results:
                if not r.get('region_match', False):
                    print(f"     - {r.get('address', '')[:60]}...")
    
    api_validation = breakdown.get('api_validation', {})
    api_attempts = api_validation.get('api_attempts', [])
    if api_attempts:
        api_scores = []
        for attempt in api_attempts:
            r = attempt.get('result', 0.0)
            if isinstance(r, (int, float)):
                api_scores.append(r)
            elif isinstance(r, dict):
                api_scores.append(r.get('score', 0.0))
        
        if api_scores:
            avg_api = sum(api_scores) / len(api_scores)
            print(f"     - API Scores: {api_scores} (avg: {avg_api:.4f})")
    
    print(f"\n  🎯 Overall Score: {overall_score:.4f}")
    if overall_score >= 0.99:
        print(f"  ✅ PERFECT SCORE!")
    else:
        print(f"  ⚠️  NOT PERFECT")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print("Poland format: 'HouseNumber, Street, City, Postcode, Country'")
print("Other countries: Need to match this exact format for score 1.0")
print("=" * 80)

