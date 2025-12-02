#!/usr/bin/env python3
"""
Detailed test of Argentina addresses - check each address individually
"""

import os
import sys
import json
import time

# Add MIID validator to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'MIID', 'validator'))

from reward import check_with_nominatim, looks_like_address, validate_address_region

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
    if result["heuristic"] and result["region"] and result["api_score"] >= 0.9:
        result["status"] = "PASS"
    elif result["heuristic"] and result["region"] and result["api_score"] >= 0.9:
        result["status"] = "PASS_09"
    else:
        result["status"] = "FAIL"
    
    # Rate limit
    time.sleep(1.0)
    
    return result

def main():
    """Test all Argentina addresses individually"""
    argentina_addresses = [
        "1550 Avenida Cabildo, Buenos Aires, C1426, Argentina",
        "2447 Avenida Santa Fe, Buenos Aires, C1123, Argentina",
        "1055 San Juan, Rosario, 2000, Argentina",
        "990 Avenida José de San Martín, Granadero Baigorria, 2152, Argentina",
        "1001 Avenida Francia, Rosario, 2002, Argentina",
        "902 Vera Mujíca, Rosario, 2002, Argentina",
        "1925 Alvarez Thomas, Rosario, 2000, Argentina",
        "1101 Balcarce, Rosario, 2000, Argentina",
        "1399 Balcarce, Rosario, 2000, Argentina",
        "1601 Balcarce, Rosario, 2000, Argentina",
        "1799 Mariano Moreno, Rosario, 2000, Argentina",
        "2301 Mariano Moreno, Rosario, 2000, Argentina",
        "1299 España, Rosario, 2000, Argentina",
        "1501 España, Rosario, 2000, Argentina",
        "1001 Montevideo, Rosario, 2000, Argentina"
    ]
    
    print("="*80)
    print("DETAILED VALIDATION OF ARGENTINA ADDRESSES")
    print("="*80)
    print(f"\n📋 Testing {len(argentina_addresses)} addresses individually\n")
    
    results = []
    for i, address in enumerate(argentina_addresses, 1):
        print(f"[{i}/{len(argentina_addresses)}] Testing: {address[:60]}...")
        result = test_individual_address(address, "Argentina")
        results.append(result)
        
        # Print result
        status_icon = "✅" if result["status"] == "PASS" else "⚠️" if result["status"] == "PASS_09" else "❌"
        print(f"     {status_icon} Heuristic: {result['heuristic']}, Region: {result['region']}, API: {result['api_score']:.4f} ({result['api_result']})")
        print()
    
    # Summary
    print("="*80)
    print("SUMMARY")
    print("="*80)
    
    passed_10 = sum(1 for r in results if r["status"] == "PASS" and r["api_score"] >= 0.99)
    passed_09 = sum(1 for r in results if r["status"] == "PASS_09" and 0.9 <= r["api_score"] < 0.99)
    failed = sum(1 for r in results if r["status"] == "FAIL")
    
    print(f"✅ Score 1.0: {passed_10}/15")
    print(f"⚠️  Score 0.9: {passed_09}/15")
    print(f"❌ Failed: {failed}/15")
    print()
    
    # Show failed addresses
    if failed > 0:
        print("Failed addresses:")
        for r in results:
            if r["status"] == "FAIL":
                print(f"  ❌ {r['address']}")
                print(f"     Heuristic: {r['heuristic']}, Region: {r['region']}, API: {r['api_score']:.4f} ({r['api_result']})")
    
    # Save results
    output_file = "argentina_detailed_validation_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "test_date": __import__('datetime').datetime.now().isoformat(),
            "addresses": argentina_addresses,
            "results": results,
            "summary": {
                "total": len(results),
                "score_10": passed_10,
                "score_09": passed_09,
                "failed": failed
            }
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Detailed results saved to {output_file}")

if __name__ == '__main__':
    main()

