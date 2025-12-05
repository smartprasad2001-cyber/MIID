#!/usr/bin/env python3
"""
Verify orthographic distribution for both rule-compliant and non-rule-compliant variations.
Check if all names meet the required categories for both types.
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'MIID', 'validator'))

from maximize_orthographic_similarity import OrthographicBruteForceGenerator
from MIID.validator.rule_evaluator import evaluate_rule_compliance
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

def test_distribution_for_both_types(name: str, rules: list):
    """Test orthographic distribution for both rule-compliant and non-rule-compliant variations."""
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
    
    # Check rule compliance
    compliant_by_rule, compliance_ratio = evaluate_rule_compliance(
        original_name=name,
        variations=variations,
        rules=rules
    )
    
    # Get all compliant variations
    all_compliant = set()
    for rule_vars in compliant_by_rule.values():
        all_compliant.update(rule_vars)
    
    # Categorize all variations
    rule_compliant_categories = {"Light": [], "Medium": [], "Far": [], "VeryFar": []}
    non_rule_compliant_categories = {"Light": [], "Medium": [], "Far": [], "VeryFar": []}
    all_categories = {"Light": [], "Medium": [], "Far": [], "VeryFar": []}
    
    for var in variations:
        category = categorize_orthographic(name, var)
        all_categories[category].append(var)
        
        if var in all_compliant:
            rule_compliant_categories[category].append(var)
        else:
            non_rule_compliant_categories[category].append(var)
    
    # Check if distribution matches target
    target_light = 3
    target_medium = 9
    target_far = 3
    
    # All variations
    all_light = len(all_categories["Light"])
    all_medium = len(all_categories["Medium"])
    all_far = len(all_categories["Far"])
    all_match = (all_light == target_light and all_medium == target_medium and all_far == target_far)
    
    # Rule-compliant variations
    rule_light = len(rule_compliant_categories["Light"])
    rule_medium = len(rule_compliant_categories["Medium"])
    rule_far = len(rule_compliant_categories["Far"])
    
    # Non-rule-compliant variations
    non_rule_light = len(non_rule_compliant_categories["Light"])
    non_rule_medium = len(non_rule_compliant_categories["Medium"])
    non_rule_far = len(non_rule_compliant_categories["Far"])
    
    # Check if non-rule-compliant also maintains distribution (when combined with rule-compliant)
    # The total should still be 3 Light, 9 Medium, 3 Far
    non_rule_match = (non_rule_light + rule_light == target_light and 
                     non_rule_medium + rule_medium == target_medium and 
                     non_rule_far + rule_far == target_far)
    
    return {
        "name": name,
        "all_match": all_match,
        "all_light": all_light,
        "all_medium": all_medium,
        "all_far": all_far,
        "rule_light": rule_light,
        "rule_medium": rule_medium,
        "rule_far": rule_far,
        "non_rule_light": non_rule_light,
        "non_rule_medium": non_rule_medium,
        "non_rule_far": non_rule_far,
        "non_rule_match": non_rule_match,
        "rule_compliant_count": len(all_compliant),
        "non_rule_compliant_count": 15 - len(all_compliant)
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
    
    print("=" * 120)
    print("ORTHOGRAPHIC DISTRIBUTION VERIFICATION - RULE-COMPLIANT vs NON-RULE-COMPLIANT")
    print("=" * 120)
    print()
    print("Target Distribution (Total):")
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
        result = test_distribution_for_both_types(name, mixed_rules)
        results.append(result)
        
        all_status = "✅" if result['all_match'] else "❌"
        non_rule_status = "✅" if result['non_rule_match'] else "❌"
        
        print(f"  Total: Light={result['all_light']}/3, Medium={result['all_medium']}/9, Far={result['all_far']}/3 {all_status}")
        print(f"  Rule-compliant ({result['rule_compliant_count']}): Light={result['rule_light']}, Medium={result['rule_medium']}, Far={result['rule_far']}")
        print(f"  Non-rule-compliant ({result['non_rule_compliant_count']}): Light={result['non_rule_light']}, Medium={result['non_rule_medium']}, Far={result['non_rule_far']} {non_rule_status}")
        print()
    
    # Summary
    print("=" * 120)
    print("SUMMARY - DISTRIBUTION VERIFICATION")
    print("=" * 120)
    print()
    print(f"{'Name':<35} {'Total Dist':<15} {'Rule-Compliant':<20} {'Non-Rule-Compliant':<25} {'Status':<10}")
    print("-" * 120)
    
    all_pass = True
    pass_count = 0
    
    for r in results:
        total_dist = f"{r['all_light']}/3, {r['all_medium']}/9, {r['all_far']}/3"
        rule_dist = f"L:{r['rule_light']} M:{r['rule_medium']} F:{r['rule_far']}"
        non_rule_dist = f"L:{r['non_rule_light']} M:{r['non_rule_medium']} F:{r['non_rule_far']}"
        
        total_status = "✅" if r['all_match'] else "❌"
        non_rule_status = "✅" if r['non_rule_match'] else "❌"
        overall_status = "✅ PASS" if (r['all_match'] and r['non_rule_match']) else "❌ FAIL"
        
        print(f"{r['name'][:35]:<35} {total_dist:<15} {rule_dist:<20} {non_rule_dist:<25} {overall_status:<10}")
        
        if r['all_match'] and r['non_rule_match']:
            pass_count += 1
        else:
            all_pass = False
    
    print("-" * 120)
    print()
    print(f"Total names tested: {len(results)}")
    print(f"Names meeting distribution (both types): {pass_count}/{len(results)} ({pass_count/len(results)*100:.1f}%)")
    print()
    
    if all_pass:
        print("✅ ALL NAMES MEET ORTHOGRAPHIC DISTRIBUTION FOR BOTH RULE-COMPLIANT AND NON-RULE-COMPLIANT!")
    else:
        print("❌ Some names do NOT meet distribution requirements:")
        for r in results:
            if not (r['all_match'] and r['non_rule_match']):
                issues = []
                if not r['all_match']:
                    issues.append(f"Total: L={r['all_light']}/3, M={r['all_medium']}/9, F={r['all_far']}/3")
                if not r['non_rule_match']:
                    issues.append(f"Non-rule: L={r['non_rule_light']}, M={r['non_rule_medium']}, F={r['non_rule_far']}")
                print(f"  • {r['name']}: {', '.join(issues)}")
    print()
    
    # Statistics
    avg_rule_light = sum(r['rule_light'] for r in results) / len(results)
    avg_rule_medium = sum(r['rule_medium'] for r in results) / len(results)
    avg_rule_far = sum(r['rule_far'] for r in results) / len(results)
    
    avg_non_rule_light = sum(r['non_rule_light'] for r in results) / len(results)
    avg_non_rule_medium = sum(r['non_rule_medium'] for r in results) / len(results)
    avg_non_rule_far = sum(r['non_rule_far'] for r in results) / len(results)
    
    print("Average Distribution:")
    print(f"  Rule-compliant: Light={avg_rule_light:.2f}, Medium={avg_rule_medium:.2f}, Far={avg_rule_far:.2f}")
    print(f"  Non-rule-compliant: Light={avg_non_rule_light:.2f}, Medium={avg_non_rule_medium:.2f}, Far={avg_non_rule_far:.2f}")
    print(f"  Combined: Light={avg_rule_light + avg_non_rule_light:.2f}, Medium={avg_rule_medium + avg_non_rule_medium:.2f}, Far={avg_rule_far + avg_non_rule_far:.2f}")
    print()

if __name__ == "__main__":
    main()

