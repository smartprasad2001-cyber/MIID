#!/usr/bin/env python3
"""
Detailed test to see if generator variations match validator rule checks.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'MIID', 'validator'))

from variation_generator_clean import apply_delete_random_letter, apply_insert_random_letter, apply_swap_random_letter
from MIID.validator.rule_evaluator import is_letter_removed, is_random_letter_inserted, is_letters_swapped
import Levenshtein

def test_rule_matching(name: str, rule: str, generator_func, evaluator_func):
    """Test if generator function produces variations that pass evaluator."""
    print(f"\n{'='*80}")
    print(f"Testing: {rule}")
    print(f"Original name: '{name}'")
    print(f"{'='*80}")
    
    # Generate 10 variations using the generator
    variations = []
    for i in range(10):
        var = generator_func(name)
        variations.append(var)
    
    print(f"\nGenerated variations:")
    for i, var in enumerate(variations, 1):
        print(f"  {i:2d}. '{var}'")
    
    print(f"\nValidator check results:")
    passed = 0
    failed = 0
    for i, var in enumerate(variations, 1):
        try:
            result = evaluator_func(name, var)
            status = "✅ PASS" if result else "❌ FAIL"
            if result:
                passed += 1
            else:
                failed += 1
            
            # Show details
            if rule == "delete_random_letter":
                len_diff = len(name) - len(var)
                lev_dist = Levenshtein.distance(name, var)
                print(f"  {i:2d}. '{var}' - {status} (len_diff={len_diff}, lev_dist={lev_dist})")
            elif rule == "insert_random_letter":
                len_diff = len(var) - len(name)
                lev_dist = Levenshtein.distance(name, var)
                print(f"  {i:2d}. '{var}' - {status} (len_diff={len_diff}, lev_dist={lev_dist})")
            elif rule == "swap_random_letter":
                len_same = len(name) == len(var)
                diffs = [i for i in range(len(name)) if i < len(var) and name[i] != var[i]]
                print(f"  {i:2d}. '{var}' - {status} (len_same={len_same}, diffs={diffs})")
            else:
                print(f"  {i:2d}. '{var}' - {status}")
        except Exception as e:
            print(f"  {i:2d}. '{var}' - ❌ ERROR: {e}")
            failed += 1
    
    print(f"\nSummary: {passed}/{len(variations)} passed ({passed/len(variations)*100:.1f}%)")
    return passed, failed

if __name__ == "__main__":
    test_names = [
        "Mohammed ALBASHIR",
        "John Smith",
        "Maria Garcia"
    ]
    
    rules_to_test = [
        ("delete_random_letter", apply_delete_random_letter, is_letter_removed),
        ("insert_random_letter", apply_insert_random_letter, is_random_letter_inserted),
        ("swap_random_letter", apply_swap_random_letter, is_letters_swapped),
    ]
    
    for name in test_names:
        print("\n" + "="*80)
        print(f"TESTING NAME: '{name}'")
        print("="*80)
        
        for rule_name, gen_func, eval_func in rules_to_test:
            test_rule_matching(name, rule_name, gen_func, eval_func)

