"""
Diagnose why phonetic scores are low - check if we're finding enough variations
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'MIID', 'validator'))

from unified_generator import generate_light_variations, generate_medium_variations, generate_far_variations
from reward import calculate_phonetic_similarity

# Test with a few names that had low scores
test_names = [
    ("Sebastian", "Martinez"),
    ("Bartholomew", "Anderson"),
    ("Theodore", "Williams"),
]

light_count = 2
medium_count = 6
far_count = 2

print("="*80)
print("DIAGNOSING VARIATION GENERATION")
print("="*80)
print()

for first_name, last_name in test_names:
    print(f"\n{'='*80}")
    print(f"Testing: {first_name} {last_name}")
    print(f"{'='*80}\n")
    
    # Test first name
    print(f"FIRST NAME: {first_name}")
    print("-" * 80)
    
    print(f"\nGenerating Light variations (need {light_count})...")
    first_light = generate_light_variations(first_name, light_count, verbose=True)
    print(f"Found: {len(first_light)}/{light_count}")
    if first_light:
        print(f"  Examples: {first_light[:3]}")
        # Check scores
        for var in first_light[:3]:
            score = calculate_phonetic_similarity(first_name, var)
            print(f"    '{var}': score = {score:.4f}")
    
    print(f"\nGenerating Medium variations (need {medium_count})...")
    first_medium = generate_medium_variations(first_name, medium_count, verbose=True)
    print(f"Found: {len(first_medium)}/{medium_count}")
    if first_medium:
        print(f"  Examples: {first_medium[:3]}")
        # Check scores
        for var in first_medium[:3]:
            score = calculate_phonetic_similarity(first_name, var)
            print(f"    '{var}': score = {score:.4f} (should be 0.6-0.79)")
    
    print(f"\nGenerating Far variations (need {far_count})...")
    first_far = generate_far_variations(first_name, far_count, verbose=True)
    print(f"Found: {len(first_far)}/{far_count}")
    if first_far:
        print(f"  Examples: {first_far[:3]}")
        # Check scores
        for var in first_far[:3]:
            score = calculate_phonetic_similarity(first_name, var)
            print(f"    '{var}': score = {score:.4f} (should be 0.3-0.59)")
    
    # Test last name
    print(f"\n{'='*80}")
    print(f"LAST NAME: {last_name}")
    print("-" * 80)
    
    print(f"\nGenerating Light variations (need {light_count})...")
    last_light = generate_light_variations(last_name, light_count, verbose=True)
    print(f"Found: {len(last_light)}/{light_count}")
    if last_light:
        print(f"  Examples: {last_light[:3]}")
        # Check scores
        for var in last_light[:3]:
            score = calculate_phonetic_similarity(last_name, var)
            print(f"    '{var}': score = {score:.4f}")
    
    print(f"\nGenerating Medium variations (need {medium_count})...")
    last_medium = generate_medium_variations(last_name, medium_count, verbose=True)
    print(f"Found: {len(last_medium)}/{medium_count}")
    if last_medium:
        print(f"  Examples: {last_medium[:3]}")
        # Check scores
        for var in last_medium[:3]:
            score = calculate_phonetic_similarity(last_name, var)
            print(f"    '{var}': score = {score:.4f} (should be 0.6-0.79)")
    
    print(f"\nGenerating Far variations (need {far_count})...")
    last_far = generate_far_variations(last_name, far_count, verbose=True)
    print(f"Found: {len(last_far)}/{far_count}")
    if last_far:
        print(f"  Examples: {last_far[:3]}")
        # Check scores
        for var in last_far[:3]:
            score = calculate_phonetic_similarity(last_name, var)
            print(f"    '{var}': score = {score:.4f} (should be 0.3-0.59)")
    
    # Summary
    print(f"\n{'='*80}")
    print(f"SUMMARY FOR {first_name} {last_name}")
    print(f"{'='*80}")
    print(f"First name:")
    print(f"  Light: {len(first_light)}/{light_count} {'✅' if len(first_light) >= light_count else '❌'}")
    print(f"  Medium: {len(first_medium)}/{medium_count} {'✅' if len(first_medium) >= medium_count else '❌'}")
    print(f"  Far: {len(first_far)}/{far_count} {'✅' if len(first_far) >= far_count else '❌'}")
    print(f"Last name:")
    print(f"  Light: {len(last_light)}/{light_count} {'✅' if len(last_light) >= light_count else '❌'}")
    print(f"  Medium: {len(last_medium)}/{medium_count} {'✅' if len(last_medium) >= medium_count else '❌'}")
    print(f"  Far: {len(last_far)}/{far_count} {'✅' if len(last_far) >= far_count else '❌'}")

print()

