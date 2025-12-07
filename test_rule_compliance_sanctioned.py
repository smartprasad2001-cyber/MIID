#!/usr/bin/env python3
"""
Test rule compliance for 15 names from sanctioned list using validator synapse structure.
"""

import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'MIID', 'validator'))

from maximize_orthographic_similarity import OrthographicBruteForceGenerator
from reward import calculate_rule_compliance_score, calculate_variation_quality
from rule_evaluator import evaluate_rule_compliance

# Load sanctioned list
def load_sanctioned_names(count=15):
    """Load names from sanctioned list."""
    with open('MIID/validator/Sanctioned_list.json', 'r') as f:
        data = json.load(f)
    
    names = []
    for item in data[:count]:
        if isinstance(item, dict):
            first_name = item.get('FirstName', '').strip()
            last_name = item.get('LastName', '').strip()
            if first_name and last_name:
                full_name = f"{first_name} {last_name}"
                names.append(full_name)
    
    return names

# Monkey patch to reduce candidates for faster execution
def patch_generator_for_speed():
    """Patch the generator to use fewer candidates."""
    import maximize_orthographic_similarity as mod
    original_method = mod.OrthographicBruteForceGenerator.generate_all_variations
    
    def faster_generate(self, max_candidates=5000):
        return original_method(self, max_candidates=max_candidates)
    
    mod.OrthographicBruteForceGenerator.generate_all_variations = faster_generate

# Define rules to test
TEST_RULES = [
    "swap_adjacent_consonants",
    "replace_double_letters_with_single_letter",
    "remove_all_spaces",
    "replace_spaces_with_random_special_characters",
    "delete_random_letter",
    "replace_random_vowel_with_random_vowel",
    "replace_random_consonant_with_random_consonant",
    "swap_random_letter",
    "insert_random_letter",
    "duplicate_random_letter_as_double_letter",
    "initial_only_first_name",
    "shorten_name_to_initials",
    "name_parts_permutations"
]

# Target distribution
TARGET_DISTRIBUTION = {"Light": 0.2, "Medium": 0.6, "Far": 0.2}
RULE_PERCENTAGE = 30
VARIATION_COUNT = 15

def main():
    print("=" * 80)
    print("RULE COMPLIANCE TEST - 15 SANCTIONED NAMES")
    print("=" * 80)
    print()
    
    # Patch for faster execution
    patch_generator_for_speed()
    
    # Load 15 names
    names = load_sanctioned_names(15)
    print(f"Loaded {len(names)} names from sanctioned list:")
    for i, name in enumerate(names, 1):
        print(f"  {i}. {name}")
    print()
    
    # Test each name
    results = []
    
    for idx, original_name in enumerate(names, 1):
        print("=" * 80)
        print(f"Testing Name {idx}/{len(names)}: {original_name}")
        print("=" * 80)
        print()
        
        # Initialize generator with rules
        generator = OrthographicBruteForceGenerator(
            original_name=original_name,
            target_distribution=TARGET_DISTRIBUTION,
            rule_based={
                "selected_rules": TEST_RULES,
                "rule_percentage": RULE_PERCENTAGE
            }
        )
        
        # Generate variations
        print("Generating variations...")
        variations, metrics = generator.generate_optimal_variations(variation_count=VARIATION_COUNT)
        
        print(f"\nGenerated {len(variations)} variations")
        print()
        
        # Calculate rule compliance using validator function
        print("Calculating rule compliance score using validator...")
        rule_compliance_score, rule_metrics = calculate_rule_compliance_score(
            original_name=original_name,
            variations=variations,
            target_rules=TEST_RULES,
            target_percentage=RULE_PERCENTAGE / 100.0
        )
        
        # Also calculate overall quality (returns quality_score, metrics dict)
        try:
            quality_result = calculate_variation_quality(
                original_name=original_name,
                variations=variations,
                phonetic_similarity={"Medium": 1.0},
                orthographic_similarity=TARGET_DISTRIBUTION,
                expected_count=VARIATION_COUNT,
                rule_based={
                    "selected_rules": TEST_RULES,
                    "rule_percentage": RULE_PERCENTAGE
                }
            )
            if isinstance(quality_result, tuple) and len(quality_result) == 2:
                quality_score, quality_metrics = quality_result
            else:
                quality_score = quality_result if isinstance(quality_result, (int, float)) else 0.0
                quality_metrics = {}
        except Exception as e:
            print(f"  Warning: Could not calculate quality score: {e}")
            quality_score = 0.0
            quality_metrics = {}
        
        # Extract orthographic quality score from generator metrics
        orthographic_quality_score = metrics.get('quality_score', 0.0)
        average_orthographic_score = metrics.get('average_score', 0.0)
        actual_distribution = metrics.get('actual_distribution', {})
        
        # Store results
        result = {
            "original_name": original_name,
            "variations": variations,
            "rule_compliance_score": rule_compliance_score,
            "rule_metrics": rule_metrics,
            "quality_score": quality_score,
            "quality_metrics": quality_metrics,
            "generator_metrics": metrics,
            "orthographic_quality_score": orthographic_quality_score,
            "average_orthographic_score": average_orthographic_score,
            "actual_distribution": actual_distribution
        }
        results.append(result)
        
        # Print summary
        print()
        print("SUMMARY:")
        print(f"  Rule Compliance Score: {rule_compliance_score:.4f}")
        print(f"  Quality Score: {quality_score:.4f}")
        print(f"  Orthographic Quality Score: {orthographic_quality_score:.4f}")
        print(f"  Average Orthographic Score: {average_orthographic_score:.4f}")
        print(f"  Rule Compliance Ratio: {rule_metrics.get('compliance_ratio_overall_variations', 0.0):.2%}")
        print(f"  Compliant Variations: {rule_metrics.get('overall_compliant_unique_variations_count', 0)}/{len(variations)}")
        print(f"  Expected Compliant: {rule_metrics.get('expected_compliant_variations_count', 0)}")
        print()
        
        # Print rule breakdown
        compliant_by_rule = rule_metrics.get('compliant_variations_by_rule', {})
        if compliant_by_rule:
            print("  Rule Breakdown:")
            for rule, rule_variations in compliant_by_rule.items():
                print(f"    {rule}: {len(rule_variations)} variations")
        print()
    
    # Final summary
    print("=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    print()
    
    avg_rule_compliance = sum(r['rule_compliance_score'] for r in results) / len(results)
    avg_quality = sum(r['quality_score'] for r in results) / len(results)
    avg_orthographic_quality = sum(r['orthographic_quality_score'] for r in results) / len(results)
    avg_orthographic_score = sum(r['average_orthographic_score'] for r in results) / len(results)
    avg_compliance_ratio = sum(r['rule_metrics'].get('compliance_ratio_overall_variations', 0.0) for r in results) / len(results)
    
    print(f"Average Rule Compliance Score: {avg_rule_compliance:.4f}")
    print(f"Average Quality Score: {avg_quality:.4f}")
    print(f"Average Orthographic Quality Score: {avg_orthographic_quality:.4f}")
    print(f"Average Orthographic Score: {avg_orthographic_score:.4f}")
    print(f"Average Compliance Ratio: {avg_compliance_ratio:.2%}")
    print()
    
    print("Per-Name Breakdown:")
    print(f"{'Name':<40} {'Orthographic Quality':<20} {'Avg Orthographic':<18} {'Rule Score':<12} {'Compliance %':<12}")
    print("-" * 110)
    for r in results:
        name = r['original_name'][:38]
        ortho_quality = r['orthographic_quality_score']
        avg_ortho = r['average_orthographic_score']
        rule_score = r['rule_compliance_score']
        compliance_pct = r['rule_metrics'].get('compliance_ratio_overall_variations', 0.0) * 100
        print(f"{name:<40} {ortho_quality:<20.4f} {avg_ortho:<18.4f} {rule_score:<12.4f} {compliance_pct:<12.2f}%")
    
    print()
    print("=" * 110)
    print("ORTHOGRAPHIC QUALITY SCORES (Detailed)")
    print("=" * 110)
    print()
    print(f"{'Name':<40} {'Quality Score':<15} {'Avg Score':<12} {'Light %':<10} {'Medium %':<12} {'Far %':<10}")
    print("-" * 110)
    for r in results:
        name = r['original_name'][:38]
        ortho_quality = r['orthographic_quality_score']
        avg_ortho = r['average_orthographic_score']
        dist = r['actual_distribution']
        light_pct = dist.get('Light', 0.0) * 100
        medium_pct = dist.get('Medium', 0.0) * 100
        far_pct = dist.get('Far', 0.0) * 100
        print(f"{name:<40} {ortho_quality:<15.4f} {avg_ortho:<12.4f} {light_pct:<10.1f} {medium_pct:<12.1f} {far_pct:<10.1f}")
    
    print()
    print("=" * 80)

if __name__ == "__main__":
    main()

