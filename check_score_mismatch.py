"""
Check if there's a mismatch between our scoring and validator's scoring
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'MIID', 'validator'))

from unified_generator import generate_light_variations, generate_medium_variations, generate_far_variations
from unified_generator import calculate_score_with_weights, get_weights_for_name
from reward import calculate_phonetic_similarity

# Test with one name
original = "Sebastian"

light_count = 2
medium_count = 6
far_count = 2

print("="*80)
print(f"CHECKING SCORE MISMATCH: {original}")
print("="*80)
print()

# Get weights
selected_algorithms, weights = get_weights_for_name(original)
print(f"Algorithms: {selected_algorithms}")
print(f"Weights: {weights}")
print()

# Generate variations
print("Generating variations...")
light_vars = generate_light_variations(original, light_count, verbose=False)
medium_vars = generate_medium_variations(original, medium_count, verbose=False)
far_vars = generate_far_variations(original, far_count, verbose=False)

print(f"Light: {len(light_vars)}")
print(f"Medium: {len(medium_vars)}")
print(f"Far: {len(far_vars)}")
print()

# Check scores with both methods
print("="*80)
print("SCORE COMPARISON")
print("="*80)
print()

print(f"{'Variation':<20} {'Our Score':<12} {'Validator Score':<15} {'Category':<10}")
print("-" * 60)

# Light variations
for var in light_vars[:3]:
    our_score = calculate_score_with_weights(original, var, selected_algorithms, weights)
    validator_score = calculate_phonetic_similarity(original, var)
    category = "Light" if validator_score >= 0.8 else ("Medium" if validator_score >= 0.6 else "Far")
    print(f"{var:<20} {our_score:<12.4f} {validator_score:<15.4f} {category:<10}")

print()

# Medium variations
for var in medium_vars[:5]:
    our_score = calculate_score_with_weights(original, var, selected_algorithms, weights)
    validator_score = calculate_phonetic_similarity(original, var)
    category = "Light" if validator_score >= 0.8 else ("Medium" if validator_score >= 0.6 else "Far")
    match = "✅" if 0.6 <= validator_score <= 0.79 else "❌"
    print(f"{var:<20} {our_score:<12.4f} {validator_score:<15.4f} {category:<10} {match}")

print()

# Far variations
for var in far_vars[:3]:
    our_score = calculate_score_with_weights(original, var, selected_algorithms, weights)
    validator_score = calculate_phonetic_similarity(original, var)
    category = "Light" if validator_score >= 0.8 else ("Medium" if validator_score >= 0.6 else "Far")
    match = "✅" if 0.3 <= validator_score <= 0.59 else "❌"
    print(f"{var:<20} {our_score:<12.4f} {validator_score:<15.4f} {category:<10} {match}")

print()
print("="*80)
print("ANALYSIS")
print("="*80)
print()

# Count how many are in correct ranges
light_correct = sum(1 for var in light_vars if calculate_phonetic_similarity(original, var) >= 0.8)
medium_correct = sum(1 for var in medium_vars if 0.6 <= calculate_phonetic_similarity(original, var) <= 0.79)
far_correct = sum(1 for var in far_vars if 0.3 <= calculate_phonetic_similarity(original, var) <= 0.59)

print(f"Light variations: {light_correct}/{len(light_vars)} in correct range (>= 0.8)")
print(f"Medium variations: {medium_correct}/{len(medium_vars)} in correct range (0.6-0.79)")
print(f"Far variations: {far_correct}/{len(far_vars)} in correct range (0.3-0.59)")

print()

