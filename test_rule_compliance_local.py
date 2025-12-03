#!/usr/bin/env python3
"""
Local test script to debug rule compliance validation
"""

import sys
import os
import json

# Add MIID/validator to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'MIID', 'validator'))

from reward import calculate_rule_compliance_score
from rule_evaluator import evaluate_rule_compliance, RULE_EVALUATORS

def test_rule_compliance_local():
    """Test rule compliance validation locally"""
    
    # Load a generated file to get actual variations
    json_files = [f for f in os.listdir('.') if f.startswith('orthographic_variations_') and f.endswith('.json')]
    if not json_files:
        print("❌ No orthographic variations JSON file found!")
        print("   Run test_orthographic_validation.py first to generate variations")
        return
    
    latest_file = max(json_files, key=os.path.getctime)
    print(f"📂 Loading: {latest_file}")
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract rule_based metadata
    rule_based = data.pop('rule_based', None)
    if not rule_based:
        print("❌ No rule_based metadata found in file!")
        print("   Run with --rules to enable rule compliance")
        return
    
    print(f"\n📋 Rule-based metadata:")
    print(f"   Rules: {rule_based.get('selected_rules', [])}")
    print(f"   Percentage: {rule_based.get('rule_percentage', rule_based.get('percentage', 30))}%")
    
    # Test each name
    for name, name_data in data.items():
        if name == 'rule_based':
            continue
            
        print(f"\n{'='*80}")
        print(f"Testing: {name}")
        print(f"{'='*80}")
        
        original_name = name
        variations = []
        for var in name_data.get('variations', []):
            if isinstance(var, dict):
                full_name = var.get('full_name', '')
            else:
                full_name = str(var)
            if full_name:
                variations.append(full_name.lower())
        
        if not variations:
            print("⚠️  No variations found")
            continue
        
        print(f"\nOriginal: {original_name}")
        print(f"Variations ({len(variations)}):")
        for i, var in enumerate(variations[:5], 1):
            print(f"  {i}. {var}")
        if len(variations) > 5:
            print(f"  ... and {len(variations) - 5} more")
        
        # Get target rules and percentage
        target_rules = rule_based.get('selected_rules', [])
        target_percentage = rule_based.get('rule_percentage', 30) / 100.0  # Convert to fraction
        
        print(f"\n📋 Target Rules: {target_rules}")
        print(f"📋 Target Percentage: {target_percentage * 100:.1f}%")
        print(f"📋 Expected Compliant Count: {max(1, int(len(variations) * target_percentage))}")
        
        # Test evaluate_rule_compliance directly
        print(f"\n{'─'*80}")
        print("Step 1: Testing evaluate_rule_compliance")
        print(f"{'─'*80}")
        
        compliant_variations_by_rule, compliance_ratio = evaluate_rule_compliance(
            original_name.lower(),
            variations,
            target_rules
        )
        
        print(f"✅ Compliance Ratio: {compliance_ratio:.3f}")
        print(f"✅ Compliant Variations by Rule:")
        
        if not compliant_variations_by_rule:
            print("   ⚠️  NO RULES WERE SATISFIED!")
            print("\n   Checking each rule individually...")
            for rule in target_rules:
                if rule in RULE_EVALUATORS:
                    evaluator = RULE_EVALUATORS[rule]
                    print(f"\n   Rule: {rule}")
                    matches = 0
                    for var in variations[:10]:  # Check first 10
                        try:
                            if evaluator(original_name.lower(), var):
                                matches += 1
                                print(f"      ✅ {var}")
                        except Exception as e:
                            print(f"      ❌ Error: {e}")
                    print(f"      Matches: {matches}/{min(10, len(variations))}")
                else:
                    print(f"   ⚠️  Rule '{rule}' not found in RULE_EVALUATORS")
        else:
            for rule, compliant_vars in compliant_variations_by_rule.items():
                print(f"   {rule}: {len(compliant_vars)} variations")
                for var in compliant_vars[:3]:
                    print(f"      - {var}")
                if len(compliant_vars) > 3:
                    print(f"      ... and {len(compliant_vars) - 3} more")
        
        # Test calculate_rule_compliance_score
        print(f"\n{'─'*80}")
        print("Step 2: Testing calculate_rule_compliance_score")
        print(f"{'─'*80}")
        
        score, metrics = calculate_rule_compliance_score(
            original_name.lower(),
            variations,
            target_rules,
            target_percentage
        )
        
        print(f"✅ Final Score: {score:.3f}")
        print(f"\n📊 Detailed Metrics:")
        print(f"   Quantity Score: {metrics.get('quantity_score', 0.0):.3f}")
        print(f"   Rule Diversity Factor: {metrics.get('rule_diversity_factor', 0.0):.3f}")
        print(f"   Compliant Variations: {metrics.get('overall_compliant_unique_variations_count', 0)}/{metrics.get('expected_compliant_variations_count', 0)}")
        print(f"   Rules Satisfied: {metrics.get('num_target_rules_met', 0)}/{metrics.get('total_target_rules', 0)}")
        print(f"   Compliance Ratio: {metrics.get('compliance_ratio_overall_variations', 0.0):.3f}")
        
        if score == 0.0:
            print(f"\n⚠️  Score is 0.0! Reasons:")
            if metrics.get('overall_compliant_unique_variations_count', 0) == 0:
                print("   - No variations comply with any rule")
            if metrics.get('quantity_score', 0.0) == 0.0:
                print("   - Quantity score is 0 (not enough compliant variations)")
            if metrics.get('rule_diversity_factor', 0.0) == 0.0:
                print("   - Rule diversity factor is 0 (no rules satisfied)")

if __name__ == "__main__":
    test_rule_compliance_local()

