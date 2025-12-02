"""
Test all components: Name, DOB, and Address generation using reward.py functions
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'MIID', 'validator'))

from generate_and_test_variations import (
    generate_full_name_variations,
    generate_perfect_dob_variations,
    generate_exploit_addresses
)
from reward import (
    calculate_variation_quality,
    _grade_dob_variations,
    _grade_address_variations,
    MIID_REWARD_WEIGHTS
)

def test_all_components():
    """Test name, DOB, and address generation with validator scoring"""
    
    print("="*80)
    print("COMPREHENSIVE TEST: NAME + DOB + ADDRESS")
    print("="*80)
    print()
    
    # Test parameters
    test_name = "John Smith"
    seed_dob = "1990-06-15"
    seed_address = "New York, USA"
    variation_count = 10
    
    # Distribution for name variations
    light_count = 2
    medium_count = 6
    far_count = 2
    
    print(f"Test Configuration:")
    print(f"  Name: {test_name}")
    print(f"  DOB: {seed_dob}")
    print(f"  Address: {seed_address}")
    print(f"  Variation Count: {variation_count}")
    print(f"  Name Distribution: {light_count} Light, {medium_count} Medium, {far_count} Far")
    print()
    print("="*80)
    print()
    
    # ============================================================================
    # STEP 1: Generate Name Variations
    # ============================================================================
    print("STEP 1: Generating Name Variations")
    print("-" * 80)
    name_variations = generate_full_name_variations(
        test_name,
        light_count=light_count,
        medium_count=medium_count,
        far_count=far_count,
        verbose=True
    )
    print(f"✅ Generated {len(name_variations)} name variations")
    print()
    
    # Test name scoring
    print("Testing Name Scoring with calculate_variation_quality()...")
    target_distribution = {
        "Light": light_count / variation_count,
        "Medium": medium_count / variation_count,
        "Far": far_count / variation_count
    }
    
    final_score, base_score, detailed_metrics = calculate_variation_quality(
        original_name=test_name,
        variations=name_variations,
        expected_count=variation_count,
        phonetic_similarity=target_distribution,
        orthographic_similarity=target_distribution
    )
    
    print(f"  Name Final Score: {final_score:.4f}")
    print(f"  Name Base Score: {base_score:.4f}")
    print(f"  Similarity Score: {detailed_metrics.get('similarity_score', 0):.4f}")
    print(f"  Count Score: {detailed_metrics.get('count_score', 0):.4f}")
    print(f"  Uniqueness Score: {detailed_metrics.get('uniqueness_score', 0):.4f}")
    print()
    print("="*80)
    print()
    
    # ============================================================================
    # STEP 2: Generate DOB Variations
    # ============================================================================
    print("STEP 2: Generating DOB Variations")
    print("-" * 80)
    dob_variations = generate_perfect_dob_variations(seed_dob, variation_count=variation_count)
    print(f"✅ Generated {len(dob_variations)} DOB variations")
    print(f"   Sample: {dob_variations[:3]}")
    print()
    
    # Test DOB scoring
    print("Testing DOB Scoring with _grade_dob_variations()...")
    variations_dict = {
        test_name: [[name_variations[i], dob_variations[i], "address"] for i in range(min(len(name_variations), len(dob_variations)))]
    }
    seed_dobs = [seed_dob]
    miner_metrics = {}
    
    dob_result = _grade_dob_variations(variations_dict, seed_dobs, miner_metrics)
    
    print(f"  DOB Score: {dob_result['overall_score']:.4f}")
    found_ranges = dob_result.get('found_ranges', [])
    sorted_ranges = sorted([x for x in found_ranges if isinstance(x, int)]) + [x for x in found_ranges if isinstance(x, str)]
    print(f"  Found Categories: {sorted_ranges}")
    print(f"  Total Categories: {dob_result.get('total_ranges', 0)}")
    print()
    print("="*80)
    print()
    
    # ============================================================================
    # STEP 3: Generate Address Variations
    # ============================================================================
    print("STEP 3: Generating Address Variations (Exploit Method)")
    print("-" * 80)
    address_variations = generate_exploit_addresses(
        seed_address=seed_address,
        variation_count=variation_count
    )
    print(f"✅ Generated {len(address_variations)} address variations")
    print(f"   Sample: {address_variations[0]}")
    print()
    
    # Test address scoring
    print("Testing Address Scoring with _grade_address_variations()...")
    # Combine all variations
    final_variations = []
    min_count = min(len(name_variations), len(dob_variations), len(address_variations))
    for i in range(min_count):
        final_variations.append([
            name_variations[i],
            dob_variations[i],
            address_variations[i]
        ])
    
    variations_dict = {
        test_name: final_variations
    }
    seed_addresses = [seed_address]
    validator_uid = 1
    miner_uid = 1
    
    address_result = _grade_address_variations(
        variations_dict,
        seed_addresses,
        miner_metrics,
        validator_uid,
        miner_uid
    )
    
    print(f"  Address Score: {address_result['overall_score']:.4f}")
    print(f"  Heuristic Perfect: {address_result.get('heuristic_perfect', False)}")
    print(f"  API Result: {address_result.get('api_result', 'N/A')}")
    print(f"  Region Matches: {address_result.get('region_matches', 0)}")
    print(f"  Total Addresses: {address_result.get('total_addresses', 0)}")
    print()
    
    # Test exploit scenario (empty seed_addresses)
    print("Testing Exploit Scenario (Empty seed_addresses)...")
    empty_seed_addresses = []
    exploit_result = _grade_address_variations(
        variations_dict,
        empty_seed_addresses,
        miner_metrics,
        validator_uid,
        miner_uid
    )
    print(f"  Exploit Address Score (empty seed_addresses): {exploit_result['overall_score']:.4f}")
    print(f"  ⚠️  This demonstrates the exploit - empty seed_addresses = 1.0 score!")
    print()
    print("="*80)
    print()
    
    # ============================================================================
    # FINAL SUMMARY
    # ============================================================================
    print("="*80)
    print("FINAL SUMMARY")
    print("="*80)
    print()
    
    # Calculate final combined score
    quality_weight = 0.2
    dob_weight = 0.1
    address_weight = 0.7
    
    quality_component = final_score * quality_weight
    dob_component = dob_result['overall_score'] * dob_weight
    address_component = address_result['overall_score'] * address_weight
    exploit_address_component = exploit_result['overall_score'] * address_weight
    
    final_combined_score = quality_component + dob_component + address_component
    exploit_combined_score = quality_component + dob_component + exploit_address_component
    
    print("Component Scores:")
    print(f"  Name Score:   {final_score:.4f} × {quality_weight} = {quality_component:.4f}")
    print(f"  DOB Score:    {dob_result['overall_score']:.4f} × {dob_weight} = {dob_component:.4f}")
    print(f"  Address Score: {address_result['overall_score']:.4f} × {address_weight} = {address_component:.4f}")
    print()
    print(f"Final Combined Score: {final_combined_score:.4f}")
    print()
    print("With Exploit (empty seed_addresses):")
    print(f"  Address Score: {exploit_result['overall_score']:.4f} × {address_weight} = {exploit_address_component:.4f}")
    print(f"  Exploit Combined Score: {exploit_combined_score:.4f}")
    print()
    
    # Status
    print("Status:")
    if final_score >= 0.7:
        print(f"  ✅ Name: EXCELLENT ({final_score:.4f})")
    elif final_score >= 0.5:
        print(f"  ⚠️  Name: GOOD ({final_score:.4f})")
    else:
        print(f"  ❌ Name: NEEDS IMPROVEMENT ({final_score:.4f})")
    
    if dob_result['overall_score'] >= 0.99:
        print(f"  ✅ DOB: PERFECT ({dob_result['overall_score']:.4f})")
    else:
        print(f"  ❌ DOB: NEEDS IMPROVEMENT ({dob_result['overall_score']:.4f})")
    
    if address_result['overall_score'] >= 0.7:
        print(f"  ✅ Address: GOOD ({address_result['overall_score']:.4f})")
    elif exploit_result['overall_score'] >= 0.99:
        print(f"  ⚠️  Address: EXPLOIT WORKS ({exploit_result['overall_score']:.4f} with empty seed_addresses)")
    else:
        print(f"  ❌ Address: NEEDS IMPROVEMENT ({address_result['overall_score']:.4f})")
    
    print()
    print("="*80)
    
    return {
        "name_score": final_score,
        "dob_score": dob_result['overall_score'],
        "address_score": address_result['overall_score'],
        "exploit_address_score": exploit_result['overall_score'],
        "final_score": final_combined_score,
        "exploit_final_score": exploit_combined_score
    }


if __name__ == "__main__":
    results = test_all_components()

