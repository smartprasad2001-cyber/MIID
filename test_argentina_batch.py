#!/usr/bin/env python3
"""
Batch validation test for Argentina addresses
"""

import os
import sys

# Add MIID validator to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'MIID', 'validator'))

from reward import _grade_address_variations

def main():
    """Test Argentina addresses with batch validator"""
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
    print("BATCH VALIDATION OF ARGENTINA ADDRESSES")
    print("="*80)
    print(f"\n📋 Testing {len(argentina_addresses)} addresses as a batch\n")
    
    variations = {
        "Test Name": [
            ["Test Name", "1990-01-01", addr] for addr in argentina_addresses
        ]
    }
    
    seed_addresses = ["Argentina"] * len(variations)
    
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
    
    print("="*80)
    print("RESULTS")
    print("="*80)
    print(f"Overall Score: {overall_score:.4f}")
    print(f"Heuristic Perfect: {heuristic_perfect}")
    print(f"Region Matches: {region_matches}/15")
    print(f"API Result: {api_result}")
    print()
    
    if overall_score >= 0.99:
        print("✅✅✅ SUCCESS: Overall score 1.0!")
    elif overall_score >= 0.9:
        print("✅ SUCCESS: Overall score >= 0.9 (acceptable)")
    else:
        print("❌ FAILED: Overall score < 0.9")
    
    print("="*80)

if __name__ == '__main__':
    main()

