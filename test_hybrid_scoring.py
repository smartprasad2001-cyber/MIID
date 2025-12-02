#!/usr/bin/env python3
"""
Test hybrid generator with complete scoring
Generates a synapse and checks the score
"""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gemini_generator_hybrid import generate_with_gemini_hybrid, parse_query_template
from MIID.validator.reward import (
    calculate_variation_quality,
    _grade_dob_variations,
    _grade_address_variations,
    MIID_REWARD_WEIGHTS
)


def test_hybrid_scoring():
    """Test hybrid generator with complete scoring."""
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY environment variable not set")
        sys.exit(1)
    
    print("="*80)
    print("HYBRID GENERATOR - COMPLETE SCORING TEST")
    print("="*80)
    print()
    
    # Test identity
    name = "John Smith"
    dob = "1990-06-15"
    address = "New York, USA"
    
    # Query template with rules
    query_template = """Generate exactly 8 variations of {name}, ensuring phonetic similarity (20% Light, 60% Medium, 20% Far) and orthographic similarity (30% Light, 40% Medium, 30% Far). Approximately 60% of the total 8 variations should follow these rule-based transformations: Convert {name} to initials, and Swap random adjacent letters. The following address is the seed country/city to generate address variations for: {address}. Generate unique real addresses within the specified country/city for each variation. The following date of birth is the seed DOB to generate variations for: {dob}."""
    
    print(f"📝 Test Identity:")
    print(f"   Name: {name}")
    print(f"   DOB: {dob}")
    print(f"   Address: {address}")
    print()
    
    # Parse requirements
    requirements = parse_query_template(query_template)
    print(f"📋 Requirements:")
    print(f"   Variation count: {requirements['variation_count']}")
    print(f"   Rule percentage: {requirements['rule_percentage']*100:.0f}%")
    print(f"   Rules: {requirements['rules']}")
    print(f"   Phonetic: {requirements.get('phonetic_similarity', {})}")
    print(f"   Orthographic: {requirements.get('orthographic_similarity', {})}")
    print()
    
    # Generate variations using hybrid approach
    print("🔄 Generating variations with Hybrid Generator (Manual Rules + Gemini)...")
    variations_list = generate_with_gemini_hybrid(name, dob, address, query_template, api_key)
    
    if not variations_list:
        print("❌ Failed to generate variations")
        return
    
    print(f"✅ Generated {len(variations_list)} variations")
    print()
    
    # Format for scoring
    variations_dict = {name: variations_list}
    seed_names = [name]
    seed_dob = [dob]
    seed_addresses = [address]
    
    print("="*80)
    print("SCORING BREAKDOWN")
    print("="*80)
    print()
    
    # 1. NAME QUALITY SCORE (20% weight)
    print("1. NAME QUALITY SCORE (20% of total):")
    print("-" * 80)
    
    name_variations = [var[0].lower() if var[0] else "" for var in variations_list if len(var) > 0]
    
    phonetic_sim = requirements.get('phonetic_similarity', {})
    ortho_sim = requirements.get('orthographic_similarity', {})
    rule_based = {
        "selected_rules": requirements.get('rules', []),
        "rule_percentage": int(requirements['rule_percentage'] * 100)
    }
    
    name_quality, base_score, name_metrics = calculate_variation_quality(
        original_name=name,
        variations=name_variations,
        phonetic_similarity=phonetic_sim,
        orthographic_similarity=ortho_sim,
        expected_count=requirements['variation_count'],
        rule_based=rule_based
    )
    
    print(f"   Name Quality Score: {name_quality:.4f}")
    print(f"   Base Score: {base_score:.4f}")
    
    if "first_name" in name_metrics:
        first_metrics = name_metrics["first_name"]["metrics"]
        print(f"   First Name:")
        print(f"      Similarity: {first_metrics.get('similarity', {}).get('combined', 0):.4f}")
        print(f"      Count: {first_metrics.get('count', {}).get('score', 0):.4f}")
        print(f"      Uniqueness: {first_metrics.get('uniqueness', {}).get('score', 0):.4f}")
        print(f"      Length: {first_metrics.get('length', {}).get('score', 0):.4f}")
    
    if "last_name" in name_metrics:
        last_metrics = name_metrics["last_name"]["metrics"]
        print(f"   Last Name:")
        print(f"      Similarity: {last_metrics.get('similarity', {}).get('combined', 0):.4f}")
        print(f"      Count: {last_metrics.get('count', {}).get('score', 0):.4f}")
        print(f"      Uniqueness: {last_metrics.get('uniqueness', {}).get('score', 0):.4f}")
        print(f"      Length: {last_metrics.get('length', {}).get('score', 0):.4f}")
    
    if "rule_compliance" in name_metrics:
        rule_score = name_metrics["rule_compliance"]["score"]
        rule_count = name_metrics.get("rule_compliant_variations_count", 0)
        expected_rule_count = int(requirements['variation_count'] * requirements['rule_percentage'])
        print(f"   Rule Compliance: {rule_score:.4f} ({rule_count}/{expected_rule_count} expected)")
        
        if "metrics" in name_metrics["rule_compliance"]:
            rule_metrics = name_metrics["rule_compliance"]["metrics"]
            print(f"      Rules satisfied:")
            for rule_name, vars_list in rule_metrics.get("compliant_variations_by_rule", {}).items():
                print(f"         {rule_name}: {len(vars_list)} variations")
    
    name_component = name_quality * 0.2
    print(f"   → Name Component (20% weight): {name_component:.4f}")
    print()
    
    # 2. DOB SCORE (10% weight)
    print("2. DOB SCORE (10% of total):")
    print("-" * 80)
    
    miner_metrics = {}
    dob_result = _grade_dob_variations(variations_dict, seed_dob, miner_metrics)
    dob_score = dob_result.get("overall_score", 0.0)
    
    print(f"   DOB Score: {dob_score:.4f}")
    
    if "detailed_breakdown" in dob_result:
        breakdown = dob_result["detailed_breakdown"]
        if "category_classifications" in breakdown and name in breakdown["category_classifications"]:
            categories = breakdown["category_classifications"][name].get("categories", {})
            print(f"   Categories found:")
            for cat, dobs in categories.items():
                print(f"      {cat}: {len(dobs)} variation(s)")
    
    dob_component = dob_score * 0.1
    print(f"   → DOB Component (10% weight): {dob_component:.4f}")
    print()
    
    # 3. ADDRESS SCORE (70% weight)
    print("3. ADDRESS SCORE (70% of total - MOST IMPORTANT!):")
    print("-" * 80)
    
    validator_uid = 1
    miner_uid = 1
    
    address_result = _grade_address_variations(
        variations_dict, seed_addresses, miner_metrics, validator_uid, miner_uid
    )
    address_score = address_result.get("overall_score", 0.0)
    
    print(f"   Address Score: {address_score:.4f}")
    print(f"   Heuristic Perfect: {address_result.get('heuristic_perfect', False)}")
    print(f"   Region Matches: {address_result.get('region_matches', 0)}")
    print(f"   Total Addresses: {address_result.get('total_addresses', 0)}")
    
    if "detailed_breakdown" in address_result:
        breakdown = address_result["detailed_breakdown"]
        if "api_validation" in breakdown:
            api_info = breakdown["api_validation"]
            print(f"   API Validation:")
            print(f"      Result: {api_info.get('api_result', 'N/A')}")
            print(f"      Successful: {api_info.get('nominatim_successful_calls', 0)}")
            print(f"      Failed: {api_info.get('nominatim_failed_calls', 0)}")
        
        if "validation_results" in breakdown and name in breakdown["validation_results"]:
            results = breakdown["validation_results"][name]
            print(f"   Address Validation Details:")
            for i, result in enumerate(results[:3], 1):  # Show first 3
                print(f"      {i}. {result.get('address', 'N/A')[:50]}...")
                print(f"         Format: {result.get('looks_like_address', False)}")
                print(f"         Region: {result.get('region_match', False)}")
                print(f"         API: {result.get('passed_validation', False)}")
    
    address_component = address_score * 0.7
    print(f"   → Address Component (70% weight): {address_component:.4f}")
    print()
    
    # FINAL SCORE
    print("="*80)
    print("FINAL SCORE CALCULATION")
    print("="*80)
    print()
    
    final_score = name_component + dob_component + address_component
    
    print(f"Name Component (20%):  {name_component:.4f}")
    print(f"DOB Component (10%):   {dob_component:.4f}")
    print(f"Address Component (70%): {address_component:.4f}")
    print(f"{'='*80}")
    print(f"FINAL SCORE: {final_score:.4f}")
    print(f"{'='*80}")
    print()
    
    # Show variations
    print("Generated Variations:")
    print("-" * 80)
    for i, var in enumerate(variations_list, 1):
        print(f"{i}. Name: {var[0] if len(var) > 0 else 'N/A'}")
        print(f"   DOB:  {var[1] if len(var) > 1 else 'N/A'}")
        print(f"   Addr: {var[2] if len(var) > 2 else 'N/A'}")
        print()
    
    # Save results
    results = {
        "name": name,
        "dob": dob,
        "address": address,
        "query_template": query_template,
        "variations": variations_list,
        "scores": {
            "name_quality": name_quality,
            "name_component": name_component,
            "dob_score": dob_score,
            "dob_component": dob_component,
            "address_score": address_score,
            "address_component": address_component,
            "final_score": final_score
        },
        "name_metrics": name_metrics,
        "dob_result": dob_result,
        "address_result": address_result
    }
    
    with open("test_hybrid_scoring_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Results saved to: test_hybrid_scoring_results.json")
    
    return final_score


if __name__ == "__main__":
    score = test_hybrid_scoring()
    print(f"\n{'✅ PASS' if score >= 0.8 else '❌ FAIL'}: Final Score = {score:.4f} (Target: 0.8)")
    sys.exit(0 if score >= 0.8 else 1)

