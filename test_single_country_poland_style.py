#!/usr/bin/env python3
"""
Generate 15 addresses for Philippines (Poland-style: house number first)
and validate with rewards.py to ensure score 1.0.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'MIID'))

from generate_address_cache import generate_addresses_for_country
from validator.reward import _grade_address_variations

class MockValidator:
    def __init__(self):
        self.uid = 0

class MockMiner:
    def __init__(self):
        self.uid = 0

validator = MockValidator()
miner = MockMiner()

print("=" * 80)
print("GENERATE ADDRESSES (POLAND-STYLE) FOR PHILIPPINES")
print("=" * 80)
print("Strategy: Generate addresses with house number FIRST (like Poland)")
print("Format: 'HouseNumber, Street, City, Postcode, Country'")
print("=" * 80)
sys.stdout.flush()

country = 'Philippines'
print(f"\n🔄 Generating 15 addresses for {country}...")
print("This will use reverse geocoding to get Nominatim addresses")
print("Only addresses with house number at START will be accepted")
print("-" * 80)
sys.stdout.flush()

try:
    addresses = generate_addresses_for_country(country, per_country=15, verbose=True)
    sys.stdout.flush()
    
    if len(addresses) < 15:
        print(f"\n⚠️  Only generated {len(addresses)}/15 addresses")
        sys.exit(1)
    
    print(f"\n✅ Generated {len(addresses)} addresses")
    print("\n📋 Generated addresses (first 5):")
    for i, addr in enumerate(addresses[:5], 1):
        first_part = addr.split(',')[0].strip()
        has_number = first_part and first_part[0].isdigit()
        status = "✅" if has_number else "❌"
        print(f"  {status} {i}. {addr[:70]}...")
        print(f"     First part: '{first_part}' | Has number at start: {has_number}")
    sys.stdout.flush()
    
    # Test with rewards.py
    print(f"\n🔄 Testing all 15 addresses with rewards.py...")
    print("-" * 80)
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
    api_validation = breakdown.get('api_validation', {})
    api_attempts = api_validation.get('api_attempts', [])
    
    print(f"\n📊 RESULTS:")
    print(f"  Overall Score: {overall_score:.4f}")
    
    if validation_results:
        looks_count = sum(1 for r in validation_results if r.get('looks_like_address', False))
        region_count = sum(1 for r in validation_results if r.get('region_match', False))
        print(f"  Looks Like Address: {looks_count}/15")
        print(f"  Region Match: {region_count}/15")
    
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
            print(f"  API Scores: {api_scores} (avg: {avg_api:.4f})")
            print(f"  API Addresses Checked: {len(api_attempts)}")
    
    print("\n" + "=" * 80)
    if overall_score >= 0.99:
        print("🎉 SUCCESS! Score is 1.0!")
        sys.exit(0)
    else:
        print(f"⚠️  Score is {overall_score:.4f} (not 1.0)")
        sys.exit(1)
        
except Exception as e:
    import traceback
    print(f"\n❌ ERROR: {type(e).__name__}: {e}")
    print(f"Traceback: {traceback.format_exc()}")
    sys.exit(1)

