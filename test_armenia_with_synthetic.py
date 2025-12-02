#!/usr/bin/env python3
"""
Test Armenia addresses with translated city names + synthetic replacement for failing address
"""

import os
import sys
import json

# Add MIID validator to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, 'MIID', 'validator'))

from reward import _grade_address_variations

# Original Armenia addresses (translated)
translated_addresses = [
    "Արթ Սվիթ, 122 Նաիրի Զարյան փողոց, Yerevan, 0014, Armenia",
    "Կոնվերս Բանկ, 26/1 Վազգեն Սարգսյանի փողոց, Yerevan, 0010, Armenia",
    "Կոնվերս Բանկ, 19 Սայաթ-Նովայի պողոտա, Yerevan, 0001, Armenia",
    "Կոնվերս Բանկ, 39/12 Մեսրոպ Մաշտոցի պողոտա, Yerevan, 0002, Armenia",
    "Օլդ Մարանի, 7 Ալեք Մանուկյանի փողոց, Yerevan, Armenia",
    # Address #6 - REPLACE with synthetic address
    "15 Abovyan Street, Yerevan, 0001, Armenia",  # Synthetic - proper format
    "Խնկո Ապոր գրադարան, 42/1 Տերյան փողոց, Yerevan, 0001, Armenia",
    "Pizza di Roma, 31 Մովսես Խորենացու փողոց, Yerevan, Armenia",
    "Next, 13 Ամիրյան փողոց, Yerevan, 0002, Armenia",
    "HSBC, 31 Մովսես Խորենացու փողոց, Yerevan, Armenia",
    "Արդշինբանկ, 24 Տիգրան Մեծի պողոտա, Yerevan, Armenia",
    "Grand Hotel Yerevan Royal Tulip, 14 Աբովյան փողոց, Yerevan, 0001, Armenia",
    "Ինեկոբանկ, 17 Թումանյան փողոց, Yerevan, 0001, Armenia",
    "Եվրոպա, 38 Հանրապետության փողոց, Yerevan, 0010, Armenia",
    "Chalet, 8/1 Խանջյան փողոց, Yerevan, Armenia"
]

print("=" * 80)
print("ARMENIA ADDRESSES - WITH SYNTHETIC REPLACEMENT")
print("=" * 80)
print(f"Total addresses: {len(translated_addresses)}")
print(f"Replaced address #6 with synthetic: '15 Abovyan Street, Yerevan, 0001, Armenia'")
print()

# Format addresses for _grade_address_variations
variations = {
    'Test': [['Test', '1990-01-01', addr] for addr in translated_addresses]
}

# Call _grade_address_variations
print("Calling _grade_address_variations from rewards.py...")
print()

result = _grade_address_variations(
    variations=variations,
    seed_addresses=['Armenia'],
    miner_metrics={},
    validator_uid=101,
    miner_uid=501
)

# Display results
print("=" * 80)
print("VALIDATION RESULTS")
print("=" * 80)
print(f"Overall Score: {result.get('overall_score', 0.0):.4f}")
print(f"Heuristic Perfect: {result.get('heuristic_perfect', False)}")
print(f"Region Matches: {result.get('region_matches', 0)}/{len(translated_addresses)}")
print(f"Total Addresses: {result.get('total_addresses', 0)}")
print(f"API Result: {result.get('api_result', 'N/A')}")
print()

# Detailed breakdown
breakdown = result.get('detailed_breakdown', {})
api_validation = breakdown.get('api_validation', {})

if api_validation:
    print("API Validation Details:")
    print(f"  Total eligible: {api_validation.get('total_eligible_addresses', 0)}")
    print(f"  API calls made: {api_validation.get('total_calls', 0)}")
    print(f"  Successful: {api_validation.get('total_successful_calls', 0)}")
    print(f"  Failed: {api_validation.get('total_failed_calls', 0)}")
    print()
    
    api_attempts = api_validation.get('api_attempts', [])
    if api_attempts:
        print("Individual API Results:")
        print()
        for i, attempt in enumerate(api_attempts, 1):
            addr = attempt.get('address', 'N/A')
            api_result_val = attempt.get('result', 'N/A')
            score_details = attempt.get('score_details', {}) or {}
            
            if isinstance(api_result_val, (int, float)):
                area = score_details.get('min_area', 'N/A') if score_details else 'N/A'
                status = "✅" if api_result_val >= 0.99 else "❌"
                print(f"  {status} [{i}] {addr[:60]}...")
                print(f"      Score: {api_result_val:.4f}, Area: {area} m²")
            elif api_result_val == "TIMEOUT":
                print(f"  ⏱️  [{i}] {addr[:60]}...")
                print(f"      Status: TIMEOUT")
            else:
                print(f"  ❌ [{i}] {addr[:60]}...")
                print(f"      Status: FAILED")
            print()
    else:
        print("⚠️  No API calls were made (all addresses may have failed earlier checks)")
        print()

# Validation results per address
validation_results = breakdown.get('validation_results', {})
if validation_results:
    test_results = validation_results.get('Test', [])
    if test_results:
        print("Individual Address Validation:")
        print()
        passed = 0
        failed = 0
        for i, addr_result in enumerate(test_results, 1):
            addr = addr_result.get('address', 'N/A')
            looks_like = addr_result.get('looks_like_address', False)
            region_match = addr_result.get('region_match', False)
            passed_val = addr_result.get('passed_validation', False)
            status = "✅" if passed_val else "❌"
            
            if passed_val:
                passed += 1
            else:
                failed += 1
            
            print(f"  {status} [{i}] {addr[:60]}...")
            print(f"      Heuristic: {looks_like}, Region: {region_match}, Passed: {passed_val}")
            print()
        
        print(f"Summary: {passed} passed, {failed} failed")
        print()

print("=" * 80)

# Save results
output_file = "armenia_synthetic_validation_results.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump({
        "addresses": translated_addresses,
        "validation_result": result,
        "count": len(translated_addresses),
        "note": "Address #6 replaced with synthetic: '15 Abovyan Street, Yerevan, 0001, Armenia'"
    }, f, indent=2, ensure_ascii=False)

print(f"\n💾 Results saved to {output_file}")

