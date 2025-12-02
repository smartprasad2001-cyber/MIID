#!/usr/bin/env python3
"""
Evaluate all countries in address_cache.json using rewards.py.
Report which countries get score 1.0 for addresses.
"""

import sys
import os
import json
from typing import Dict, List, Any

# Add MIID to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'MIID'))

from validator.reward import _grade_address_variations

class MockValidator:
    def __init__(self):
        self.uid = 0

class MockMiner:
    def __init__(self):
        self.uid = 0

def evaluate_country_addresses(country: str, addresses: List[str], validator: MockValidator, miner: MockMiner) -> Dict[str, Any]:
    """
    Evaluate addresses for a country using rewards.py.
    Returns evaluation results.
    """
    if not addresses or len(addresses) < 15:
        return {
            "country": country,
            "address_count": len(addresses) if addresses else 0,
            "overall_score": 0.0,
            "status": "INSUFFICIENT" if addresses else "MISSING"
        }
    
    # Use first 15 addresses
    test_addresses = addresses[:15]
    
    variations = {
        'John Smith': [
            ['John Smith', '1990-01-01', addr] for addr in test_addresses
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
    
    # Calculate statistics
    looks_count = 0
    region_count = 0
    passed_count = 0
    
    if validation_results:
        looks_count = sum(1 for r in validation_results if r.get('looks_like_address', False))
        region_count = sum(1 for r in validation_results if r.get('region_match', False))
        passed_count = sum(1 for r in validation_results if r.get('passed_validation', False))
    
    api_scores = []
    if api_attempts:
        for attempt in api_attempts:
            r = attempt.get('result', 0.0)
            if isinstance(r, (int, float)):
                api_scores.append(r)
            elif isinstance(r, dict):
                api_scores.append(r.get('score', 0.0))
    
    avg_api_score = sum(api_scores) / len(api_scores) if api_scores else 0.0
    
    status = "PERFECT" if overall_score >= 0.99 else "GOOD" if overall_score >= 0.8 else "FAIR" if overall_score >= 0.5 else "POOR"
    
    return {
        "country": country,
        "address_count": len(test_addresses),
        "overall_score": overall_score,
        "looks_like_address": looks_count,
        "region_match": region_count,
        "passed_validation": passed_count,
        "api_attempts": len(api_attempts),
        "avg_api_score": avg_api_score,
        "api_scores": api_scores[:5] if api_scores else [],  # First 5 for display
        "status": status
    }

def main():
    print("=" * 80)
    print("EVALUATING ADDRESS CACHE WITH REWARDS.PY")
    print("=" * 80)
    print()
    
    # Load cache
    cache_file = "address_cache.json"
    if not os.path.exists(cache_file):
        print(f"❌ Error: {cache_file} not found!")
        sys.exit(1)
    
    print(f"📂 Loading {cache_file}...")
    sys.stdout.flush()
    
    with open(cache_file, 'r') as f:
        cache = json.load(f)
    
    addresses_dict = cache.get('addresses', {})
    countries = sorted(addresses_dict.keys())
    
    print(f"✅ Found {len(countries)} countries in cache")
    print()
    sys.stdout.flush()
    
    validator = MockValidator()
    miner = MockMiner()
    
    results = []
    perfect_countries = []
    good_countries = []
    fair_countries = []
    poor_countries = []
    insufficient_countries = []
    
    print("🔄 Evaluating countries...")
    print("=" * 80)
    print()
    sys.stdout.flush()
    
    for idx, country in enumerate(countries, 1):
        addresses = addresses_dict[country]
        
        print(f"[{idx}/{len(countries)}] {country} ({len(addresses)} addresses)...", end=" ")
        sys.stdout.flush()
        
        result = evaluate_country_addresses(country, addresses, validator, miner)
        results.append(result)
        
        score = result['overall_score']
        status = result['status']
        
        if status == "PERFECT":
            perfect_countries.append(country)
            print(f"✅ {score:.4f} (PERFECT)")
        elif status == "GOOD":
            good_countries.append(country)
            print(f"✅ {score:.4f} (GOOD)")
        elif status == "FAIR":
            fair_countries.append(country)
            print(f"⚠️  {score:.4f} (FAIR)")
        elif status == "POOR":
            poor_countries.append(country)
            print(f"❌ {score:.4f} (POOR)")
        else:
            insufficient_countries.append(country)
            print(f"⚠️  {status} ({result['address_count']} addresses)")
        
        sys.stdout.flush()
    
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    
    print(f"📊 Total Countries: {len(countries)}")
    print(f"✅ Perfect Score (≥0.99): {len(perfect_countries)}")
    print(f"✅ Good Score (≥0.80): {len(good_countries)}")
    print(f"⚠️  Fair Score (≥0.50): {len(fair_countries)}")
    print(f"❌ Poor Score (<0.50): {len(poor_countries)}")
    print(f"⚠️  Insufficient/Missing: {len(insufficient_countries)}")
    print()
    
    if perfect_countries:
        print("=" * 80)
        print("🎉 COUNTRIES WITH PERFECT SCORE (1.0)")
        print("=" * 80)
        for country in perfect_countries:
            result = next(r for r in results if r['country'] == country)
            print(f"  ✅ {country}: {result['overall_score']:.4f}")
            print(f"     - Looks Like Address: {result['looks_like_address']}/15")
            print(f"     - Region Match: {result['region_match']}/15")
            print(f"     - Passed Validation: {result['passed_validation']}/15")
            print(f"     - API Attempts: {result['api_attempts']}")
            print(f"     - Avg API Score: {result['avg_api_score']:.4f}")
            if result['api_scores']:
                print(f"     - API Scores: {result['api_scores']}")
            print()
    
    if good_countries:
        print("=" * 80)
        print("✅ COUNTRIES WITH GOOD SCORE (≥0.80)")
        print("=" * 80)
        for country in good_countries[:10]:  # Show first 10
            result = next(r for r in results if r['country'] == country)
            print(f"  ✅ {country}: {result['overall_score']:.4f}")
        if len(good_countries) > 10:
            print(f"  ... and {len(good_countries) - 10} more")
        print()
    
    if fair_countries:
        print("=" * 80)
        print("⚠️  COUNTRIES WITH FAIR SCORE (≥0.50, <0.80)")
        print("=" * 80)
        for country in fair_countries[:10]:  # Show first 10
            result = next(r for r in results if r['country'] == country)
            print(f"  ⚠️  {country}: {result['overall_score']:.4f}")
        if len(fair_countries) > 10:
            print(f"  ... and {len(fair_countries) - 10} more")
        print()
    
    if poor_countries:
        print("=" * 80)
        print("❌ COUNTRIES WITH POOR SCORE (<0.50)")
        print("=" * 80)
        for country in poor_countries[:10]:  # Show first 10
            result = next(r for r in results if r['country'] == country)
            print(f"  ❌ {country}: {result['overall_score']:.4f}")
        if len(poor_countries) > 10:
            print(f"  ... and {len(poor_countries) - 10} more")
        print()
    
    if insufficient_countries:
        print("=" * 80)
        print("⚠️  COUNTRIES WITH INSUFFICIENT ADDRESSES")
        print("=" * 80)
        for country in insufficient_countries:
            result = next(r for r in results if r['country'] == country)
            print(f"  ⚠️  {country}: {result['address_count']} addresses (need 15)")
        print()
    
    # Save detailed results to file
    output_file = "cache_evaluation_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            "summary": {
                "total_countries": len(countries),
                "perfect": len(perfect_countries),
                "good": len(good_countries),
                "fair": len(fair_countries),
                "poor": len(poor_countries),
                "insufficient": len(insufficient_countries)
            },
            "perfect_countries": perfect_countries,
            "good_countries": good_countries,
            "fair_countries": fair_countries,
            "poor_countries": poor_countries,
            "insufficient_countries": insufficient_countries,
            "detailed_results": results
        }, f, indent=2)
    
    print(f"💾 Detailed results saved to: {output_file}")
    print()
    print("=" * 80)

if __name__ == "__main__":
    main()

