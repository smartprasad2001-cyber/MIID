#!/usr/bin/env python3
"""
Test Albania addresses from validated_address_cache_priority.json
against the rewards.py validator to check if they score 1.0
"""

import os
import sys
import json

# Add MIID validator to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'MIID', 'validator'))

from reward import _grade_address_variations

CACHE_FILE = os.path.join(os.path.dirname(__file__), "validated_address_cache_priority.json")

def test_addresses_with_validator(country: str, addresses: list, verbose: bool = True) -> dict:
    """
    Test addresses using the actual validator function from rewards.py
    
    Args:
        country: Country name (used as seed address)
        addresses: List of addresses to test
        verbose: Whether to print detailed output
        
    Returns:
        Dictionary with validation results
    """
    if not addresses:
        print(f"❌ No addresses to test for {country}")
        return {"overall_score": 0.0, "error": "No addresses"}
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"🧪 Testing {len(addresses)} addresses for {country}")
        print(f"{'='*60}")
        print(f"Seed address: {country}")
        print(f"\nAddresses to test:")
        for i, addr in enumerate(addresses, 1):
            print(f"  {i}. {addr}")
        print()
    
    # Format addresses like validator expects
    # Structure: {name: [[name_var, dob_var, address_var], ...]}
    variations = {
        "Test Name": [
            ["Test Name", "1990-01-01", addr] for addr in addresses
        ]
    }
    
    # Seed addresses (one per name)
    seed_addresses = [country] * len(variations)
    
    # Call _grade_address_variations (same as validator does)
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
    total_addresses = validation_result.get('total_addresses', 0)
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"📊 VALIDATION RESULTS")
        print(f"{'='*60}")
        print(f"  Overall Score: {overall_score:.4f}")
        print(f"  Heuristic Perfect: {heuristic_perfect}")
        print(f"  Region Matches: {region_matches}/{total_addresses}")
        print(f"  API Result: {api_result}")
        print(f"  Total Addresses: {total_addresses}")
        
        # Show detailed breakdown if available
        detailed_breakdown = validation_result.get('detailed_breakdown', {})
        if detailed_breakdown:
            validation_results = detailed_breakdown.get('validation_results', {})
            if validation_results:
                print(f"\n  📋 Individual Address Results:")
                for name, results in validation_results.items():
                    for i, result in enumerate(results, 1):
                        status = result.get('status', 'UNKNOWN')
                        looks_like = result.get('looks_like_address', False)
                        region_match = result.get('region_match', False)
                        address = result.get('address', '')[:60]
                        print(f"    {i}. {status}: {address}...")
                        print(f"       - Looks like address: {looks_like}")
                        print(f"       - Region match: {region_match}")
            
            api_validation = detailed_breakdown.get('api_validation', {})
            if api_validation:
                print(f"\n  🔍 API Validation Details:")
                print(f"     - Total eligible addresses: {api_validation.get('total_eligible_addresses', 0)}")
                print(f"     - API attempts: {len(api_validation.get('api_attempts', []))}")
                print(f"     - Successful calls: {api_validation.get('nominatim_successful_calls', 0)}")
                print(f"     - Failed calls: {api_validation.get('nominatim_failed_calls', 0)}")
                print(f"     - Timeout calls: {api_validation.get('nominatim_timeout_calls', 0)}")
                
                api_attempts = api_validation.get('api_attempts', [])
                if api_attempts:
                    print(f"\n  📡 API Call Results:")
                    for attempt in api_attempts:
                        addr = attempt.get('address', '')[:50]
                        result = attempt.get('result', 'UNKNOWN')
                        if isinstance(result, dict):
                            score = result.get('score', 'N/A')
                            print(f"     - {addr}... → Score: {score}")
                        else:
                            print(f"     - {addr}... → {result}")
        
        print(f"\n{'='*60}")
        if overall_score >= 0.99:
            print(f"✅✅✅ SUCCESS: Score is {overall_score:.4f} (>= 0.99)")
        elif overall_score >= 0.9:
            print(f"⚠️  PARTIAL: Score is {overall_score:.4f} (>= 0.9 but < 0.99)")
        else:
            print(f"❌ FAILED: Score is {overall_score:.4f} (< 0.9)")
        print(f"{'='*60}\n")
    
    return {
        "overall_score": overall_score,
        "heuristic_perfect": heuristic_perfect,
        "region_matches": region_matches,
        "api_result": api_result,
        "total_addresses": total_addresses,
        "detailed_breakdown": validation_result.get('detailed_breakdown', {})
    }

def main():
    """Main function to test addresses from cache"""
    if not os.path.exists(CACHE_FILE):
        print(f"❌ Cache file not found: {CACHE_FILE}")
        return
    
    # Load cache
    with open(CACHE_FILE, 'r', encoding='utf-8') as f:
        cache_data = json.load(f)
    
    addresses_cache = cache_data.get('addresses', {})
    
    # Test Albania addresses
    country = "Albania"
    if country not in addresses_cache:
        print(f"❌ Country '{country}' not found in cache")
        print(f"Available countries: {list(addresses_cache.keys())}")
        return
    
    addresses_to_test = addresses_cache[country]
    if not addresses_to_test:
        print(f"❌ No addresses found for {country} in cache")
        return
    
    print(f"📋 Testing {len(addresses_to_test)} addresses for {country}")
    
    # Test the addresses
    result = test_addresses_with_validator(country, addresses_to_test, verbose=True)
    
    # Save results
    output_file = f"{country.lower()}_validation_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Results saved to {output_file}")
    
    # Summary
    print(f"\n📊 SUMMARY:")
    print(f"   Country: {country}")
    print(f"   Addresses tested: {len(addresses_to_test)}")
    print(f"   Overall score: {result['overall_score']:.4f}")
    print(f"   Status: {'✅ PASS' if result['overall_score'] >= 0.99 else '❌ FAIL'}")

if __name__ == '__main__':
    main()

