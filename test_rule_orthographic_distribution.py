#!/usr/bin/env python3
"""
Test if rule-compliant variations also match orthographic distribution.
Uses maximize_orthographic_similarity.py generator.
"""

import sys
import os

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

def test_rule_and_orthographic(name: str, rules: list, rule_percentage: float = 0.3):
    """Test if rule-compliant variations match orthographic distribution."""
    print("=" * 80)
    print(f"TESTING: '{name}'")
    print("=" * 80)
    print()
    
    # Use maximize_orthographic_similarity generator
    target_distribution = {"Light": 0.2, "Medium": 0.6, "Far": 0.2}
    rule_based = {
        "selected_rules": rules,
        "rule_percentage": int(rule_percentage * 100)
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
    
    # Categorize all variations by orthographic similarity
    print("Orthographic Distribution Analysis:")
    print("-" * 80)
    
    # Target distribution
    target_light = int(15 * 0.2)  # 3
    target_medium = int(15 * 0.6)  # 9
    target_far = int(15 * 0.2)     # 3
    
    print(f"Target: Light={target_light}, Medium={target_medium}, Far={target_far}")
    print()
    
    # Categorize all variations
    all_categories = {"Light": [], "Medium": [], "Far": [], "VeryFar": []}
    compliant_categories = {"Light": [], "Medium": [], "Far": [], "VeryFar": []}
    non_compliant_categories = {"Light": [], "Medium": [], "Far": [], "VeryFar": []}
    
    for var in variations:
        category = categorize_orthographic(name, var)
        all_categories[category].append(var)
        
        if var in all_compliant:
            compliant_categories[category].append(var)
        else:
            non_compliant_categories[category].append(var)
    
    print("All Variations Distribution:")
    print(f"  Light ({len(all_categories['Light'])}/{target_light}): {all_categories['Light']}")
    print(f"  Medium ({len(all_categories['Medium'])}/{target_medium}): {all_categories['Medium']}")
    print(f"  Far ({len(all_categories['Far'])}/{target_far}): {all_categories['Far']}")
    if all_categories['VeryFar']:
        print(f"  VeryFar ({len(all_categories['VeryFar'])}): {all_categories['VeryFar']}")
    print()
    
    print("Rule-Compliant Variations Distribution:")
    print(f"  Light ({len(compliant_categories['Light'])}): {compliant_categories['Light']}")
    print(f"  Medium ({len(compliant_categories['Medium'])}): {compliant_categories['Medium']}")
    print(f"  Far ({len(compliant_categories['Far'])}): {compliant_categories['Far']}")
    if compliant_categories['VeryFar']:
        print(f"  VeryFar ({len(compliant_categories['VeryFar'])}): {compliant_categories['VeryFar']}")
    print()
    
    print("Non-Rule-Compliant Variations Distribution:")
    print(f"  Light ({len(non_compliant_categories['Light'])}): {non_compliant_categories['Light']}")
    print(f"  Medium ({len(non_compliant_categories['Medium'])}): {non_compliant_categories['Medium']}")
    print(f"  Far ({len(non_compliant_categories['Far'])}): {non_compliant_categories['Far']}")
    if non_compliant_categories['VeryFar']:
        print(f"  VeryFar ({len(non_compliant_categories['VeryFar'])}): {non_compliant_categories['VeryFar']}")
    print()
    
    # Detailed breakdown
    print("=" * 80)
    print("DETAILED BREAKDOWN")
    print("=" * 80)
    print()
    
    for i, var in enumerate(variations, 1):
        is_compliant = var in all_compliant
        category = categorize_orthographic(name, var)
        score = calculate_orthographic_similarity(name, var)
        
        # Find which rule it matches
        matching_rules = []
        for rule, compliant_vars in compliant_by_rule.items():
            if var in compliant_vars:
                matching_rules.append(rule)
        
        status = "✅ RULE" if is_compliant else "   non-rule"
        rules_str = ", ".join(matching_rules) if matching_rules else "none"
        
        print(f"{i:2d}. {var[:30]:30s} | {status:10s} | {category:6s} | score={score:.3f} | rules={rules_str}")
    
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total variations: {len(variations)}")
    print(f"Rule-compliant: {len(all_compliant)} ({compliance_ratio*100:.1f}%)")
    print(f"Target rule compliance: {rule_percentage*100:.0f}%")
    print()
    print("Orthographic distribution (all):")
    print(f"  Light: {len(all_categories['Light'])}/{target_light} ({len(all_categories['Light'])/15*100:.1f}%)")
    print(f"  Medium: {len(all_categories['Medium'])}/{target_medium} ({len(all_categories['Medium'])/15*100:.1f}%)")
    print(f"  Far: {len(all_categories['Far'])}/{target_far} ({len(all_categories['Far'])/15*100:.1f}%)")
    print()
    print("Orthographic distribution (rule-compliant only):")
    print(f"  Light: {len(compliant_categories['Light'])}")
    print(f"  Medium: {len(compliant_categories['Medium'])}")
    print(f"  Far: {len(compliant_categories['Far'])}")
    print()
    print("=" * 80)
    print()

if __name__ == "__main__":
    test_names = [
        "Mohammed ALBASHIR",
        "John Smith",
        "Maria Garcia"
    ]
    
    rules = ["delete_random_letter", "insert_random_letter", "swap_random_letter"]
    rule_percentage = 0.3
    
    for name in test_names:
        test_rule_and_orthographic(name, rules, rule_percentage)
        print("\n" * 2)

