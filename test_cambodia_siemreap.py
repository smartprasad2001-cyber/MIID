#!/usr/bin/env python3
"""
Detailed test of Cambodia (Siem Reap) addresses - check each address individually and batch validation
"""

import os
import sys
import json
import time

# Add MIID validator to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'MIID', 'validator'))

from reward import check_with_nominatim, looks_like_address, validate_address_region, _grade_address_variations

def test_individual_address(address: str, country: str) -> dict:
    """Test a single address with all validation steps"""
    result = {
        "address": address,
        "heuristic": False,
        "region": False,
        "api_score": 0.0,
        "api_result": None,
        "status": "FAIL"
    }
    
    # Step 1: Heuristic check
    result["heuristic"] = looks_like_address(address)
    
    # Step 2: Region check
    result["region"] = validate_address_region(address, country)
    
    # Step 3: API check
    api_result = check_with_nominatim(
        address=address,
        validator_uid=101,
        miner_uid=501,
        seed_address=country,
        seed_name="Test"
    )
    
    if api_result == "TIMEOUT":
        result["api_result"] = "TIMEOUT"
        result["api_score"] = 0.0
    elif isinstance(api_result, dict):
        result["api_score"] = api_result.get('score', 0.0)
        result["api_result"] = "SUCCESS" if result["api_score"] >= 0.9 else "FAILED"
    elif isinstance(api_result, (int, float)):
        result["api_score"] = float(api_result)
        result["api_result"] = "SUCCESS" if result["api_score"] >= 0.9 else "FAILED"
    else:
        result["api_result"] = "FAILED"
        result["api_score"] = 0.0
    
    # Overall status
    if result["heuristic"] and result["region"] and result["api_score"] >= 0.99:
        result["status"] = "PASS"
    elif result["heuristic"] and result["region"] and result["api_score"] >= 0.9:
        result["status"] = "PASS_09"
    else:
        result["status"] = "FAIL"
    
    # Rate limit
    time.sleep(1.0)
    
    return result

def main():
    """Test all Cambodia (Siem Reap) addresses individually and as a batch"""
    cambodia_addresses = [
        "0207, River Road, Siem Reap, 171201, Cambodia",
        "0210, River Road, Siem Reap, 171201, Cambodia",
        "18, BBU Road, Siem Reap, 171207, Cambodia",
        "22, BBU Road, Siem Reap, 171207, Cambodia",
        "31, Taphul Road, Siem Reap, 171204, Cambodia",
        "33, Taphul Road, Siem Reap, 171204, Cambodia",
        "44, Funky Lane, Siem Reap, 171204, Cambodia",
        "46, Funky Lane, Siem Reap, 171204, Cambodia",
        "11, Wat Damnak Road, Siem Reap, 171202, Cambodia",
        "13, Wat Damnak Road, Siem Reap, 171202, Cambodia"
    ]
    
    print("="*80)
    print("DETAILED VALIDATION OF CAMBODIA (SIEM REAP) ADDRESSES")
    print("="*80)
    print(f"\n📋 Testing {len(cambodia_addresses)} addresses individually\n")
    
    results = []
    for i, address in enumerate(cambodia_addresses, 1):
        print(f"[{i}/{len(cambodia_addresses)}] Testing: {address[:60]}...")
        result = test_individual_address(address, "Cambodia")
        results.append(result)
        
        # Print result
        status_icon = "✅" if result["status"] == "PASS" else "⚠️" if result["status"] == "PASS_09" else "❌"
        print(f"     {status_icon} Heuristic: {result['heuristic']}, Region: {result['region']}, API: {result['api_score']:.4f} ({result['api_result']})")
        print()
    
    # Summary
    print("="*80)
    print("INDIVIDUAL VALIDATION SUMMARY")
    print("="*80)
    
    passed_10 = sum(1 for r in results if r["status"] == "PASS" and r["api_score"] >= 0.99)
    passed_09 = sum(1 for r in results if r["status"] == "PASS_09" and 0.9 <= r["api_score"] < 0.99)
    failed = sum(1 for r in results if r["status"] == "FAIL")
    
    print(f"✅ Score 1.0: {passed_10}/{len(cambodia_addresses)}")
    print(f"⚠️  Score 0.9: {passed_09}/{len(cambodia_addresses)}")
    print(f"❌ Failed: {failed}/{len(cambodia_addresses)}")
    print()
    
    # Show failed addresses
    if failed > 0:
        print("Failed addresses:")
        for r in results:
            if r["status"] == "FAIL":
                print(f"  ❌ {r['address']}")
                print(f"     Heuristic: {r['heuristic']}, Region: {r['region']}, API: {r['api_score']:.4f} ({r['api_result']})")
    
    # Test with batch validator (using all 10 addresses)
    print("\n" + "="*80)
    print("BATCH VALIDATION (using _grade_address_variations)")
    print("="*80)
    print(f"Using all {len(cambodia_addresses)} addresses for batch validation...\n")
    
    variations = {
        "Test Name": [
            ["Test Name", "1990-01-01", addr] for addr in cambodia_addresses
        ]
    }
    
    seed_addresses = ["Cambodia"] * len(variations)
    
    validation_result = _grade_address_variations(
        variations=variations,
        seed_addresses=seed_addresses,
        miner_metrics={},
        validator_uid=101,
        miner_uid=501
    )
    
    overall_score = validation_result.get('overall_score', 0.0)
    heuristic_perfect = validation_result.get('heuristic_perfect', False)
    region_matches = validation_result.get('region_matches', 0)
    api_result = validation_result.get('api_result', 'UNKNOWN')
    
    print(f"Overall Score: {overall_score:.4f}")
    print(f"Heuristic Perfect: {heuristic_perfect}")
    print(f"Region Matches: {region_matches}/{len(cambodia_addresses)}")
    print(f"API Result: {api_result}")
    print(f"Status: {'✅ PASS' if overall_score >= 0.9 else '❌ FAIL'}")
    
    # Save results
    output_file = "cambodia_siemreap_validation_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "test_date": __import__('datetime').datetime.now().isoformat(),
            "addresses": cambodia_addresses,
            "individual_results": results,
            "batch_validation": validation_result,
            "summary": {
                "total": len(results),
                "score_10": passed_10,
                "score_09": passed_09,
                "failed": failed,
                "overall_score": overall_score
            }
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Detailed results saved to {output_file}")

if __name__ == '__main__':
    main()

