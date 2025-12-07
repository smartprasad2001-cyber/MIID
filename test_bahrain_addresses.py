#!/usr/bin/env python3
"""
Test all 15 Bahrain addresses from zero_addresses_cache.json
to verify they pass all 4 validation phases.
"""

import json
import sys
import os
import time

# Add MIID validator to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'MIID', 'validator'))

from reward import (
    looks_like_address,
    validate_address_region,
    check_with_nominatim
)
from cheat_detection import normalize_address_for_deduplication

USER_AGENT = "MIIDSubnet/1.0 (contact: prasadpsd2001@gmail.com)"
os.environ["USER_AGENT"] = USER_AGENT

def test_address(address: str, country: str, idx: int) -> dict:
    """Test a single address with all 4 validation phases."""
    result = {
        "index": idx,
        "address": address,
        "country": country,
        "phase1_looks_like_address": False,
        "phase2_region_validation": False,
        "phase3_api_score": 0.0,
        "phase3_api_passed": False,
        "phase4_normalized": "",
        "all_passed": False,
        "errors": []
    }
    
    # Phase 1: looks_like_address
    try:
        result["phase1_looks_like_address"] = looks_like_address(address)
        if not result["phase1_looks_like_address"]:
            result["errors"].append("Phase 1: looks_like_address failed")
    except Exception as e:
        result["errors"].append(f"Phase 1 error: {e}")
    
    # Phase 2: validate_address_region
    try:
        result["phase2_region_validation"] = validate_address_region(address, country)
        if not result["phase2_region_validation"]:
            result["errors"].append("Phase 2: region validation failed")
    except Exception as e:
        result["errors"].append(f"Phase 2 error: {e}")
    
    # Phase 3: check_with_nominatim (score >= 0.9)
    try:
        api_result = check_with_nominatim(
            address=address,
            validator_uid=1,
            miner_uid=1,
            seed_address=country,
            seed_name="Test"
        )
        
        if isinstance(api_result, dict):
            result["phase3_api_score"] = api_result.get("score", 0.0)
        elif isinstance(api_result, (int, float)):
            result["phase3_api_score"] = float(api_result)
        else:
            result["phase3_api_score"] = 0.0
        
        result["phase3_api_passed"] = result["phase3_api_score"] >= 0.9
        if not result["phase3_api_passed"]:
            result["errors"].append(f"Phase 3: API score {result['phase3_api_score']:.2f} < 0.9")
    except Exception as e:
        result["errors"].append(f"Phase 3 error: {e}")
    
    # Phase 4: normalize_address_for_deduplication
    try:
        result["phase4_normalized"] = normalize_address_for_deduplication(address)
    except Exception as e:
        result["errors"].append(f"Phase 4 error: {e}")
    
    # Check if all passed
    result["all_passed"] = (
        result["phase1_looks_like_address"] and
        result["phase2_region_validation"] and
        result["phase3_api_passed"]
    )
    
    return result

def main():
    """Test all Bahrain addresses."""
    # Load addresses from cache
    cache_file = "zero_addresses_cache.json"
    
    if not os.path.exists(cache_file):
        print(f"❌ Cache file not found: {cache_file}")
        return
    
    with open(cache_file, 'r') as f:
        cache_data = json.load(f)
    
    addresses = cache_data.get('addresses', {}).get('Bahrain', [])
    
    if not addresses:
        print("❌ No Bahrain addresses found in cache")
        return
    
    print("=" * 80)
    print(f"TESTING {len(addresses)} BAHRAIN ADDRESSES")
    print("=" * 80)
    print(f"Testing all 4 validation phases:")
    print(f"  1. looks_like_address")
    print(f"  2. validate_address_region")
    print(f"  3. check_with_nominatim (score >= 0.9)")
    print(f"  4. normalize_address_for_deduplication")
    print("=" * 80)
    print()
    
    results = []
    for idx, addr_obj in enumerate(addresses, 1):
        address = addr_obj.get('address', '')
        country = addr_obj.get('country', 'Bahrain')
        
        print(f"[{idx}/{len(addresses)}] Testing: {address[:70]}...")
        
        result = test_address(address, country, idx)
        results.append(result)
        
        # Print result
        status = "✅ PASSED" if result["all_passed"] else "❌ FAILED"
        print(f"  {status}")
        print(f"    Phase 1 (looks_like_address): {'✅' if result['phase1_looks_like_address'] else '❌'}")
        print(f"    Phase 2 (region_validation): {'✅' if result['phase2_region_validation'] else '❌'}")
        print(f"    Phase 3 (API score): {result['phase3_api_score']:.2f} {'✅' if result['phase3_api_passed'] else '❌'}")
        print(f"    Phase 4 (normalized): {result['phase4_normalized'][:50]}...")
        
        if result["errors"]:
            print(f"    Errors: {', '.join(result['errors'])}")
        
        print()
        
        # Rate limiting
        time.sleep(1)
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for r in results if r["all_passed"])
    failed = len(results) - passed
    
    print(f"Total addresses tested: {len(results)}")
    print(f"✅ Passed all 4 phases: {passed}")
    print(f"❌ Failed one or more phases: {failed}")
    print()
    
    # Phase-by-phase breakdown
    phase1_passed = sum(1 for r in results if r["phase1_looks_like_address"])
    phase2_passed = sum(1 for r in results if r["phase2_region_validation"])
    phase3_passed = sum(1 for r in results if r["phase3_api_passed"])
    
    print("Phase-by-phase results:")
    print(f"  Phase 1 (looks_like_address): {phase1_passed}/{len(results)} ({phase1_passed*100/len(results):.1f}%)")
    print(f"  Phase 2 (region_validation): {phase2_passed}/{len(results)} ({phase2_passed*100/len(results):.1f}%)")
    print(f"  Phase 3 (API score >= 0.9): {phase3_passed}/{len(results)} ({phase3_passed*100/len(results):.1f}%)")
    print()
    
    # Show failed addresses
    if failed > 0:
        print("Failed addresses:")
        for r in results:
            if not r["all_passed"]:
                print(f"  [{r['index']}] {r['address'][:70]}...")
                print(f"      Errors: {', '.join(r['errors'])}")
    
    print("=" * 80)

if __name__ == "__main__":
    main()

