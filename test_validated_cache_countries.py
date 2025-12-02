#!/usr/bin/env python3
"""
Test all countries from validated_address_cache_fresh.json using _grade_address_variations
"""

import os
import sys
import json

# Add MIID validator to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, 'MIID', 'validator'))

from reward import _grade_address_variations

# Load validated cache
CACHE_FILE = os.path.join(BASE_DIR, "validated_address_cache_fresh.json")
with open(CACHE_FILE, 'r', encoding='utf-8') as f:
    cache_data = json.load(f)

addresses_by_country = cache_data.get('addresses', {})

if not addresses_by_country:
    print("No addresses found in validated cache")
    sys.exit(1)

print("=" * 80)
print("TESTING COUNTRIES FROM VALIDATED CACHE")
print("=" * 80)
print(f"Total countries: {len(addresses_by_country)}")
print()

# Test each country
results = []

for country, addresses in addresses_by_country.items():
    if not addresses:
        continue
    
    print("=" * 80)
    print(f"TESTING: {country} ({len(addresses)} addresses)")
    print("=" * 80)
    
    # Format addresses for _grade_address_variations
    variations = {
        'Test': [['Test', '1990-01-01', addr] for addr in addresses]
    }
    
    # Call _grade_address_variations
    result = _grade_address_variations(
        variations=variations,
        seed_addresses=[country],
        miner_metrics={},
        validator_uid=101,
        miner_uid=501
    )
    
    overall_score = result.get('overall_score', 0.0)
    heuristic_perfect = result.get('heuristic_perfect', False)
    region_matches = result.get('region_matches', 0)
    api_result = result.get('api_result', 'N/A')
    
    # Display results
    print(f"Overall Score: {overall_score:.4f}")
    print(f"Heuristic Perfect: {heuristic_perfect}")
    print(f"Region Matches: {region_matches}/{len(addresses)}")
    print(f"API Result: {api_result}")
    print()
    
    # API validation details
    breakdown = result.get('detailed_breakdown', {})
    api_validation = breakdown.get('api_validation', {})
    
    if api_validation:
        print("API Validation:")
        print(f"  Total eligible: {api_validation.get('total_eligible_addresses', 0)}")
        print(f"  API calls made: {api_validation.get('total_calls', 0)}")
        print(f"  Successful: {api_validation.get('total_successful_calls', 0)}")
        print(f"  Failed: {api_validation.get('total_failed_calls', 0)}")
        print()
        
        api_attempts = api_validation.get('api_attempts', [])
        if api_attempts:
            print("API Results:")
            for i, attempt in enumerate(api_attempts, 1):
                addr = attempt.get('address', 'N/A')
                api_result_val = attempt.get('result', 'N/A')
                score_details = attempt.get('score_details', {}) or {}
                
                if isinstance(api_result_val, (int, float)):
                    area = score_details.get('min_area', 'N/A') if score_details else 'N/A'
                    status = "✅" if api_result_val >= 0.99 else "❌"
                    print(f"  {status} [{i}] Score: {api_result_val:.4f}, Area: {area} m²")
                    print(f"      {addr[:60]}...")
                elif api_result_val == "TIMEOUT":
                    print(f"  ⏱️  [{i}] TIMEOUT")
                    print(f"      {addr[:60]}...")
                else:
                    print(f"  ❌ [{i}] FAILED")
                    print(f"      {addr[:60]}...")
            print()
    
    # Store result
    results.append({
        'country': country,
        'address_count': len(addresses),
        'overall_score': overall_score,
        'heuristic_perfect': heuristic_perfect,
        'region_matches': region_matches,
        'api_result': api_result,
        'all_passed': overall_score >= 0.99
    })
    
    print()

# Summary
print("=" * 80)
print("SUMMARY - ALL COUNTRIES")
print("=" * 80)
print(f"{'Country':<20} {'Addresses':<12} {'Score':<10} {'Region':<10} {'API':<15} {'Status'}")
print("-" * 80)

for r in results:
    status = "✅ PASS" if r['all_passed'] else "❌ FAIL"
    print(f"{r['country']:<20} {r['address_count']:<12} {r['overall_score']:<10.4f} {r['region_matches']:<10} {r['api_result']:<15} {status}")

print("-" * 80)
passed = sum(1 for r in results if r['all_passed'])
failed = len(results) - passed
print(f"\nTotal: {len(results)} countries")
print(f"✅ Passed (score >= 0.99): {passed}")
print(f"❌ Failed (score < 0.99): {failed}")

# Save results
output_file = "validated_cache_test_results.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump({
        'countries_tested': len(results),
        'results': results,
        'summary': {
            'passed': passed,
            'failed': failed
        }
    }, f, indent=2, ensure_ascii=False)

print(f"\n💾 Results saved to {output_file}")

