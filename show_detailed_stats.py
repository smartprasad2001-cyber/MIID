#!/usr/bin/env python3
"""
Show detailed stats for all variations with individual scores
"""

import sys
import os

# Add paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'MIID', 'validator'))

# Flush output immediately
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

from unified_generator import generate_full_name_variations
from reward import calculate_phonetic_similarity, calculate_orthographic_similarity

test_name = "John Smith"
variation_count = 15
light_pct = 0.30
medium_pct = 0.50
far_pct = 0.20

# Calculate counts
light_count = max(1, int(variation_count * light_pct))
medium_count = max(1, int(variation_count * medium_pct))
far_count = max(1, int(variation_count * far_pct))

# Adjust to ensure total equals variation_count
total = light_count + medium_count + far_count
if total < variation_count:
    medium_count += (variation_count - total)
elif total > variation_count:
    medium_count -= (total - variation_count)

print("="*100)
print("DETAILED STATISTICS FOR ALL VARIATIONS")
print("="*100)
print()
print(f"Name: {test_name}")
print(f"Total variations: {variation_count}")
print(f"Distribution: {light_count} Light ({light_pct:.0%}), {medium_count} Medium ({medium_pct:.0%}), {far_count} Far ({far_pct:.0%})")
print()

# Generate variations
variations = generate_full_name_variations(
    test_name,
    light_count=light_count,
    medium_count=medium_count,
    far_count=far_count,
    verbose=False
)

# Split name
name_parts = test_name.split()
first_name = name_parts[0] if len(name_parts) > 0 else test_name
last_name = name_parts[-1] if len(name_parts) > 1 else None

print("="*100)
print("INDIVIDUAL VARIATION SCORES")
print("="*100)
print()

# Calculate scores for each variation
all_stats = []

for i, variation in enumerate(variations, 1):
    var_parts = variation.split()
    var_first = var_parts[0] if len(var_parts) > 0 else variation
    var_last = var_parts[-1] if len(var_parts) > 1 else ""
    
    # Determine category
    if i <= light_count:
        category = "Light"
    elif i <= light_count + medium_count:
        category = "Medium"
    else:
        category = "Far"
    
    # Calculate phonetic and orthographic similarity for full name
    phonetic_full = calculate_phonetic_similarity(test_name, variation)
    orthographic_full = calculate_orthographic_similarity(test_name, variation)
    
    # Calculate for first name
    phonetic_first = calculate_phonetic_similarity(first_name, var_first)
    orthographic_first = calculate_orthographic_similarity(first_name, var_first)
    
    # Calculate for last name
    if last_name and var_last:
        phonetic_last = calculate_phonetic_similarity(last_name, var_last)
        orthographic_last = calculate_orthographic_similarity(last_name, var_last)
    else:
        phonetic_last = 0.0
        orthographic_last = 0.0
    
    all_stats.append({
        "index": i,
        "variation": variation,
        "category": category,
        "phonetic_full": phonetic_full,
        "orthographic_full": orthographic_full,
        "phonetic_first": phonetic_first,
        "orthographic_first": orthographic_first,
        "phonetic_last": phonetic_last,
        "orthographic_last": orthographic_last,
    })

# Print detailed table
print(f"{'#':<4} {'Variation':<40} {'Cat':<6} {'Phonetic':<10} {'Orthographic':<12} {'First Ph':<10} {'First Or':<10} {'Last Ph':<10} {'Last Or':<10}")
print("-" * 100)

for stat in all_stats:
    print(f"{stat['index']:<4} {stat['variation']:<40} {stat['category']:<6} "
          f"{stat['phonetic_full']:<10.4f} {stat['orthographic_full']:<12.4f} "
          f"{stat['phonetic_first']:<10.4f} {stat['orthographic_first']:<10.4f} "
          f"{stat['phonetic_last']:<10.4f} {stat['orthographic_last']:<10.4f}")

print()
print("="*100)
print("SUMMARY STATISTICS BY CATEGORY")
print("="*100)
print()

# Group by category
light_stats = [s for s in all_stats if s['category'] == 'Light']
medium_stats = [s for s in all_stats if s['category'] == 'Medium']
far_stats = [s for s in all_stats if s['category'] == 'Far']

def print_category_stats(category, stats):
    if not stats:
        return
    
    avg_phonetic = sum(s['phonetic_full'] for s in stats) / len(stats)
    avg_orthographic = sum(s['orthographic_full'] for s in stats) / len(stats)
    avg_phonetic_first = sum(s['phonetic_first'] for s in stats) / len(stats)
    avg_orthographic_first = sum(s['orthographic_first'] for s in stats) / len(stats)
    avg_phonetic_last = sum(s['phonetic_last'] for s in stats) / len(stats)
    avg_orthographic_last = sum(s['orthographic_last'] for s in stats) / len(stats)
    
    print(f"{category} ({len(stats)} variations):")
    print(f"  Full Name:")
    print(f"    Average Phonetic:      {avg_phonetic:.4f}")
    print(f"    Average Orthographic:  {avg_orthographic:.4f}")
    print(f"  First Name:")
    print(f"    Average Phonetic:      {avg_phonetic_first:.4f}")
    print(f"    Average Orthographic:  {avg_orthographic_first:.4f}")
    print(f"  Last Name:")
    print(f"    Average Phonetic:      {avg_phonetic_last:.4f}")
    print(f"    Average Orthographic:  {avg_orthographic_last:.4f}")
    print()

print_category_stats("Light", light_stats)
print_category_stats("Medium", medium_stats)
print_category_stats("Far", far_stats)

print("="*100)
print("OVERALL STATISTICS")
print("="*100)
print()

overall_phonetic = sum(s['phonetic_full'] for s in all_stats) / len(all_stats)
overall_orthographic = sum(s['orthographic_full'] for s in all_stats) / len(all_stats)
overall_phonetic_first = sum(s['phonetic_first'] for s in all_stats) / len(all_stats)
overall_orthographic_first = sum(s['orthographic_first'] for s in all_stats) / len(all_stats)
overall_phonetic_last = sum(s['phonetic_last'] for s in all_stats) / len(all_stats)
overall_orthographic_last = sum(s['orthographic_last'] for s in all_stats) / len(all_stats)

print(f"All {len(all_stats)} variations:")
print(f"  Full Name:")
print(f"    Average Phonetic:      {overall_phonetic:.4f}")
print(f"    Average Orthographic:  {overall_orthographic:.4f}")
print(f"  First Name:")
print(f"    Average Phonetic:      {overall_phonetic_first:.4f}")
print(f"    Average Orthographic:  {overall_orthographic_first:.4f}")
print(f"  Last Name:")
print(f"    Average Phonetic:      {overall_phonetic_last:.4f}")
print(f"    Average Orthographic:  {overall_orthographic_last:.4f}")
print()

# Check distribution quality
print("="*100)
print("DISTRIBUTION QUALITY CHECK")
print("="*100)
print()

# Phonetic boundaries
phonetic_light = sum(1 for s in all_stats if 0.8 <= s['phonetic_full'] <= 1.0)
phonetic_medium = sum(1 for s in all_stats if 0.6 <= s['phonetic_full'] < 0.8)
phonetic_far = sum(1 for s in all_stats if 0.3 <= s['phonetic_full'] < 0.6)

print(f"Phonetic Similarity Distribution:")
print(f"  Light range (0.8-1.0):   {phonetic_light:2d} variations ({phonetic_light/len(all_stats)*100:.1f}%)")
print(f"  Medium range (0.6-0.79): {phonetic_medium:2d} variations ({phonetic_medium/len(all_stats)*100:.1f}%)")
print(f"  Far range (0.3-0.59):    {phonetic_far:2d} variations ({phonetic_far/len(all_stats)*100:.1f}%)")
print()

# Expected vs Actual
print(f"Expected Distribution:")
print(f"  Light:  {light_count:2d} ({light_pct*100:.0f}%)")
print(f"  Medium: {medium_count:2d} ({medium_pct*100:.0f}%)")
print(f"  Far:    {far_count:2d} ({far_pct*100:.0f}%)")
print()

print(f"Actual Phonetic Distribution:")
print(f"  Light:  {phonetic_light:2d} ({phonetic_light/len(all_stats)*100:.1f}%)")
print(f"  Medium: {phonetic_medium:2d} ({phonetic_medium/len(all_stats)*100:.1f}%)")
print(f"  Far:    {phonetic_far:2d} ({phonetic_far/len(all_stats)*100:.1f}%)")
print()

print("="*100)





