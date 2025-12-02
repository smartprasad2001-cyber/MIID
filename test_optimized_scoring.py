#!/usr/bin/env python3
"""
Test script for optimized generator - tests with rewards.py scoring
"""

import os
import json
import sys
from datetime import datetime
from typing import Dict, List, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from MIID.protocol import IdentitySynapse
from gemini_generator_optimized import generate_optimized_variations
from MIID.validator.reward import (
    calculate_variation_quality,
    _grade_dob_variations,
    _grade_address_variations
)


def test_optimized_generator():
    """Test the optimized generator with a sample synapse."""
    
    # Get API key from environment
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("ERROR: GEMINI_API_KEY environment variable not set")
        return
    
    # Create a test synapse
    test_synapse = IdentitySynapse(
        identity=[
            ["John Smith", "1990-06-15", "New York, USA"],
            # Add more test identities if needed
        ],
        query_template="""Generate exactly 8 variations of {name}, ensuring phonetic similarity (20% Light, 60% Medium, 20% Far) and orthographic similarity (30% Light, 40% Medium, 30% Far). Approximately 30% of the total 8 variations should follow these rule-based transformations: Convert {name} to initials, and Swap random adjacent letters. The following address is the seed country/city to generate address variations for: {address}. Generate unique real addresses within the specified country/city for each variation. The following date of birth is the seed DOB to generate variations for: {dob}."""
    )
    
    print("="*80)
    print("TESTING OPTIMIZED GENERATOR")
    print("="*80)
    print()
    
    # Generate variations
    print("Generating variations...")
    try:
        variations = generate_optimized_variations(
            test_synapse,
            gemini_api_key=api_key,
            gemini_model="gemini-2.5-flash-lite"
        )
        print(f"✓ Generated variations for {len(variations)} names")
    except Exception as e:
        print(f"✗ Error generating variations: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test scoring with rewards.py
    print()
    print("="*80)
    print("SCORING WITH REWARDS.PY")
    print("="*80)
    print()
    
    # Parse requirements
    from gemini_generator_optimized import parse_query_template
    requirements = parse_query_template(test_synapse.query_template)
    
    # Score each name
    total_name_score = 0.0
    total_dob_score = 0.0
    total_address_score = 0.0
    
    for identity in test_synapse.identity:
        name = identity[0]
        dob = identity[1]
        address = identity[2] if len(identity) > 2 else ""
        
        if name not in variations:
            print(f"✗ No variations found for {name}")
            continue
        
        # Extract variations
        name_vars = []
        dob_vars = []
        addr_vars = []
        
        var_list = variations[name]
        if isinstance(var_list, dict) and 'variations' in var_list:
            var_list = var_list['variations']
        
        for var in var_list:
            if len(var) >= 1:
                name_vars.append(var[0])
            if len(var) >= 2:
                dob_vars.append(var[1])
            if len(var) >= 3:
                addr_vars.append(var[2])
        
        print(f"\nName: {name}")
        print(f"DOB: {dob}")
        print(f"Address: {address}")
        print(f"Variations generated: {len(name_vars)}")
        print()
        
        # Score name variations
        print("1. NAME SCORING:")
        try:
            name_score, base_score, name_metrics = calculate_variation_quality(
                original_name=name,
                variations=name_vars,
                phonetic_similarity=requirements.get('phonetic_similarity', {}),
                orthographic_similarity=requirements.get('orthographic_similarity', {}),
                expected_count=requirements['variation_count'],
                rule_based={
                    'selected_rules': requirements['rules'],
                    'rule_percentage': requirements['rule_percentage'] * 100
                }
            )
            print(f"   Name Score: {name_score:.4f}")
            print(f"   Base Score: {base_score:.4f}")
            # Check different possible metric structures
            if 'first_name' in name_metrics:
                # New structure with first_name/last_name
                first_metrics = name_metrics.get('first_name', {})
                last_metrics = name_metrics.get('last_name', {})
                print(f"   - First Name Similarity: {first_metrics.get('similarity', {}).get('combined', 0):.4f}")
                print(f"   - Last Name Similarity: {last_metrics.get('similarity', {}).get('combined', 0):.4f}")
                print(f"   - Rule Compliance: {name_metrics.get('rule_compliance', {}).get('score', 0):.4f}")
            else:
                # Old structure
                print(f"   - Similarity: {name_metrics.get('similarity', {}).get('combined', 0):.4f}")
                print(f"   - Count: {name_metrics.get('count', {}).get('score', 0):.4f}")
                print(f"   - Uniqueness: {name_metrics.get('uniqueness', {}).get('score', 0):.4f}")
                print(f"   - Length: {name_metrics.get('length', {}).get('score', 0):.4f}")
            print(f"   Full metrics keys: {list(name_metrics.keys())}")
            total_name_score += name_score
        except Exception as e:
            print(f"   ✗ Error scoring name: {e}")
            import traceback
            traceback.print_exc()
        
        # Score DOB variations
        print("\n2. DOB SCORING:")
        try:
            dob_variations_dict = {name: [[n, d, a] for n, d, a in zip(name_vars, dob_vars, addr_vars)]}
            dob_result = _grade_dob_variations(
                variations=dob_variations_dict,
                seed_dob=[dob],
                miner_metrics={}
            )
            dob_score = dob_result['overall_score']
            print(f"   DOB Score: {dob_score:.4f}")
            print(f"   Found ranges: {dob_result.get('found_ranges', [])}")
            print(f"   Total ranges: {dob_result.get('total_ranges', 6)}")
            
            # Show category breakdown
            breakdown = dob_result.get('detailed_breakdown', {}).get('category_classifications', {}).get(name, {})
            categories = breakdown.get('categories', {})
            print(f"   Categories found:")
            for cat, dobs in categories.items():
                print(f"     - {cat}: {len(dobs)} variation(s)")
            
            total_dob_score += dob_score
        except Exception as e:
            print(f"   ✗ Error scoring DOB: {e}")
            import traceback
            traceback.print_exc()
        
        # Score address variations
        print("\n3. ADDRESS SCORING:")
        try:
            addr_variations_dict = {name: [[n, d, a] for n, d, a in zip(name_vars, dob_vars, addr_vars)]}
            addr_result = _grade_address_variations(
                variations=addr_variations_dict,
                seed_addresses=[address],
                miner_metrics={},
                validator_uid=1,
                miner_uid=1
            )
            addr_score = addr_result['overall_score']
            print(f"   Address Score: {addr_score:.4f}")
            print(f"   Heuristic Perfect: {addr_result.get('heuristic_perfect', False)}")
            print(f"   Region Matches: {addr_result.get('region_matches', 0)}")
            print(f"   API Result: {addr_result.get('api_result', 'N/A')}")
            total_address_score += addr_score
        except Exception as e:
            print(f"   ✗ Error scoring address: {e}")
            import traceback
            traceback.print_exc()
    
    # Print summary
    num_names = len(test_synapse.identity)
    print()
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Average Name Score: {total_name_score / num_names:.4f}")
    print(f"Average DOB Score: {total_dob_score / num_names:.4f}")
    print(f"Average Address Score: {total_address_score / num_names:.4f}")
    print()
    
    # Calculate weighted final score (from rewards.py weights)
    # Weights from get_name_variation_rewards function:
    quality_weight = 0.2  # Name quality weight
    dob_weight = 0.1      # DOB weight
    address_weight = 0.7  # Address weight
    
    avg_name = total_name_score / num_names
    avg_dob = total_dob_score / num_names
    avg_addr = total_address_score / num_names
    
    final_score = (
        quality_weight * avg_name +
        dob_weight * avg_dob +
        address_weight * avg_addr
    )
    
    print(f"Final Weighted Score: {final_score:.4f}")
    print(f"  (Name Quality: {quality_weight} * {avg_name:.4f} = {quality_weight * avg_name:.4f})")
    print(f"  (DOB: {dob_weight} * {avg_dob:.4f} = {dob_weight * avg_dob:.4f})")
    print(f"  (Address: {address_weight} * {avg_addr:.4f} = {address_weight * avg_addr:.4f})")
    print()
    
    # Save results
    results = {
        'timestamp': datetime.now().isoformat(),
        'num_names': num_names,
        'scores': {
            'name': avg_name,
            'dob': avg_dob,
            'address': avg_addr,
            'final': final_score
        },
        'variations': variations
    }
    
    with open('test_optimized_scoring_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("Results saved to test_optimized_scoring_results.json")


if __name__ == "__main__":
    test_optimized_generator()

