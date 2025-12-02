#!/usr/bin/env python3
"""Analyze why orthographic scores are low"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'MIID', 'validator'))

from reward import calculate_orthographic_similarity
from unified_generator import generate_full_name_variations

# Test with actual generated variations
test_name = 'John Smith'
variations = generate_full_name_variations(test_name, light_count=2, medium_count=6, far_count=2, verbose=False)

print('='*80)
print('ORTHOGRAPHIC SCORE ANALYSIS')
print('='*80)
print()
print('Generated Variations and Their Orthographic Scores:')
print('-'*80)
print(f"{'Variation':<35} {'First Name':<15} {'Last Name':<15} {'Avg':<10}")
print('-'*80)

orthographic_scores = []

for var in variations:
    # Split to get first and last name variations
    parts = var.split()
    if len(parts) >= 2:
        first_var = parts[0]
        last_var = parts[-1]
        
        first_score = calculate_orthographic_similarity('John', first_var)
        last_score = calculate_orthographic_similarity('Smith', last_var)
        avg_score = (first_score + last_score) / 2
        
        orthographic_scores.append(avg_score)
        
        first_range = 'Light' if first_score >= 0.70 else ('Medium' if first_score >= 0.50 else 'Far')
        last_range = 'Light' if last_score >= 0.70 else ('Medium' if last_score >= 0.50 else 'Far')
        
        print(f"{var:<35} {first_score:.4f} ({first_range:<7}) {last_score:.4f} ({last_range:<7}) {avg_score:.4f}")

print('-'*80)
print()
print('Summary:')
print(f"  Average Orthographic Score: {sum(orthographic_scores) / len(orthographic_scores):.4f}")
print(f"  Min Score: {min(orthographic_scores):.4f}")
print(f"  Max Score: {max(orthographic_scores):.4f}")
print()
print('Boundaries:')
print('  Light:   0.70 - 1.00')
print('  Medium:  0.50 - 0.69')
print('  Far:     0.20 - 0.49')
print()
print('Problem: The unified generator creates variations that change many characters,')
print('         leading to high Levenshtein distance and low orthographic scores.')
print('         It prioritizes PHONETIC similarity (which is high) but not ORTHOGRAPHIC.')

