#!/usr/bin/env python3
"""
Verify orthographic distribution (Light/Medium/Far) for all 15 names.
Check if all names meet the required categories regardless of rule compliance.
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'MIID', 'validator'))

from maximize_orthographic_similarity import OrthographicBruteForceGenerator
from MIID.validator.reward import calculate_orthographic_similarity

def categorize_orthographic(original: str, variation: str) -> str:
    """Categorize variation into Light/Medium/Far based on orthographic similarity."""
    score = calculate_orthographic_similarity(original, variation)
    
    if score >= 0.7:
        return "Light"
    elif score >= 0.5:
        return "Medium"
    elif score >= 0.2:
        return "Far"
    else:
        return "VeryFar"

def test_orthographic_distribution(name: str, rules: list):
    """Test orthographic distribution for a single name."""
    target_distribution = {"Light": 0.2, "Medium": 0.6, "Far": 0.2}
    rule_based = {
        "selected_rules": rules,
        "rule_percentage": 30
    }
    
    generator = OrthographicBruteForceGenerator(
        original_name=name,
        target_distribution=target_distribution,
        rule_based=rule_based
    )
    
    # Generate variations
    variations, metrics = generator.generate_optimal_variations(variation_count=15)
    
    # Categorize all variations
    categories = {"Light": [], "Medium": [], "Far": [], "VeryFar": []}
    
    for var in variations:
        category = categorize_orthographic(name, var)
        categories[category].append(var)
    
    # Check if distribution matches target
    target_light = 3
    target_medium = 9
    target_far = 3
    
    light_count = len(categories["Light"])
    medium_count = len(categories["Medium"])
    far_count = len(categories["Far"])
    
    light_match = light_count == target_light
    medium_match = medium_count == target_medium
    far_match = far_count == target_far
    
    all_match = light_match and medium_match and far_match
    
    return {
        "name": name,
        "light_count": light_count,
        "medium_count": medium_count,
        "far_count": far_count,
        "target_light": target_light,
        "target_medium": target_medium,
        "target_far": target_far,
        "light_match": light_match,
        "medium_match": medium_match,
        "far_match": far_match,
        "all_match": all_match,
        "light_percentage": (light_count / 15) * 100,
        "medium_percentage": (medium_count / 15) * 100,
        "far_percentage": (far_count / 15) * 100
    }

def main():
    # Load sanctioned names
    sanctioned_file = os.path.join(os.path.dirname(__file__), "MIID", "validator", "Sanctioned_list.json")
    
    with open(sanctioned_file, 'r', encoding='utf-8') as f:
        sanctioned_data = json.load(f)
    
    # Get first 15 names
    names = []
    for entry in sanctioned_data[:15]:
        if isinstance(entry, dict):
            first_name = entry.get("FirstName", "")
            last_name = entry.get("LastName", "")
            if first_name and last_name:
                name = f"{first_name} {last_name}"
            elif first_name:
                name = first_name
            elif last_name:
                name = last_name
            else:
                name = ""
        else:
            name = str(entry)
        
        if name:
            names.append(name)
    
    print("=" * 100)
    print("ORTHOGRAPHIC DISTRIBUTION VERIFICATION - 15 NAMES")
    print("=" * 100)
    print()
    print("Target Distribution:")
    print("  Light: 3/15 (20%)")
    print("  Medium: 9/15 (60%)")
    print("  Far: 3/15 (20%)")
    print()
    print(f"Testing {len(names)} names...")
    print()
    
    # Mixed rules
    mixed_rules = [
        "delete_random_letter",
        "insert_random_letter",
        "swap_random_letter",
        "remove_all_spaces",
        "replace_spaces_with_random_special_characters",
        "shorten_name_to_initials",
        "name_parts_permutations",
        "initial_only_first_name"
    ]
    
    results = []
    for i, name in enumerate(names, 1):
        print(f"[{i}/{len(names)}] Testing: {name[:50]}")
        result = test_orthographic_distribution(name, mixed_rules)
        results.append(result)
        
        status = "✅ PASS" if result['all_match'] else "❌ FAIL"
        print(f"  Light: {result['light_count']}/{result['target_light']} ({result['light_percentage']:.1f}%) | "
              f"Medium: {result['medium_count']}/{result['target_medium']} ({result['medium_percentage']:.1f}%) | "
              f"Far: {result['far_count']}/{result['target_far']} ({result['far_percentage']:.1f}%) | {status}")
        print()
    
    # Summary
    print("=" * 100)
    print("SUMMARY - ORTHOGRAPHIC DISTRIBUTION")
    print("=" * 100)
    print()
    print(f"{'Name':<40} {'Light':<12} {'Medium':<12} {'Far':<12} {'Status':<10}")
    print("-" * 100)
    
    all_pass = True
    pass_count = 0
    
    for r in results:
        light_status = "✅" if r['light_match'] else "❌"
        medium_status = "✅" if r['medium_match'] else "❌"
        far_status = "✅" if r['far_match'] else "❌"
        overall_status = "✅ PASS" if r['all_match'] else "❌ FAIL"
        
        print(f"{r['name'][:40]:<40} "
              f"{r['light_count']}/{r['target_light']} {light_status:<3}    "
              f"{r['medium_count']}/{r['target_medium']} {medium_status:<3}    "
              f"{r['far_count']}/{r['target_far']} {far_status:<3}    "
              f"{overall_status:<10}")
        
        if r['all_match']:
            pass_count += 1
        else:
            all_pass = False
    
    print("-" * 100)
    print()
    print(f"Total names tested: {len(results)}")
    print(f"Names meeting distribution: {pass_count}/{len(results)} ({pass_count/len(results)*100:.1f}%)")
    print()
    
    if all_pass:
        print("✅ ALL NAMES MEET ORTHOGRAPHIC DISTRIBUTION REQUIREMENTS!")
    else:
        print("❌ Some names do NOT meet orthographic distribution requirements:")
        for r in results:
            if not r['all_match']:
                issues = []
                if not r['light_match']:
                    issues.append(f"Light: {r['light_count']}/{r['target_light']}")
                if not r['medium_match']:
                    issues.append(f"Medium: {r['medium_count']}/{r['target_medium']}")
                if not r['far_match']:
                    issues.append(f"Far: {r['far_count']}/{r['target_far']}")
                print(f"  • {r['name']}: {', '.join(issues)}")
    print()
    
    # Average percentages
    avg_light = sum(r['light_percentage'] for r in results) / len(results)
    avg_medium = sum(r['medium_percentage'] for r in results) / len(results)
    avg_far = sum(r['far_percentage'] for r in results) / len(results)
    
    print("Average Distribution Across All Names:")
    print(f"  Light: {avg_light:.2f}% (target: 20.0%)")
    print(f"  Medium: {avg_medium:.2f}% (target: 60.0%)")
    print(f"  Far: {avg_far:.2f}% (target: 20.0%)")
    print()

if __name__ == "__main__":
    main()

