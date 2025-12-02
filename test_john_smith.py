#!/usr/bin/env python3
"""
Test John Smith with 30% Light, 50% Medium, 20% Far distribution
Generate 15 variations and get score from rewards.py
"""

import sys
import os

# Add paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'MIID', 'validator'))

# Flush output immediately
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

from unified_generator import generate_full_name_variations, test_with_rewards

print("="*80)
print("TEST: John Smith - 30% Light, 50% Medium, 20% Far")
print("="*80)
print()

# Configuration
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

print(f"Configuration:")
print(f"  Name: {test_name}")
print(f"  Total variations: {variation_count}")
print(f"  Distribution: {light_pct:.0%} Light, {medium_pct:.0%} Medium, {far_pct:.0%} Far")
print(f"  Counts: {light_count} Light, {medium_count} Medium, {far_count} Far")
print()

# Generate variations
print("="*80)
print("GENERATING VARIATIONS")
print("="*80)
print()

variations = generate_full_name_variations(
    test_name,
    light_count=light_count,
    medium_count=medium_count,
    far_count=far_count,
    verbose=True
)

print()
print(f"Generated {len(variations)} variations:")
print("-" * 80)
for i, var in enumerate(variations, 1):
    if i <= light_count:
        category = "Light"
    elif i <= light_count + medium_count:
        category = "Medium"
    else:
        category = "Far"
    print(f"{i:2d}. {var:40s} ({category})")
print()

# Test with rewards.py
print("="*80)
print("TESTING WITH REWARDS.PY")
print("="*80)
print()

final_score, base_score, detailed_metrics = test_with_rewards(
    test_name,
    variations,
    expected_count=variation_count,
    light_count=light_count,
    medium_count=medium_count,
    far_count=far_count
)

print()
print("="*80)
print("SUMMARY")
print("="*80)
print()
print(f"✅ Name: {test_name}")
print(f"✅ Total variations: {len(variations)}")
print(f"✅ Distribution: {light_count} Light ({light_pct:.0%}), {medium_count} Medium ({medium_pct:.0%}), {far_count} Far ({far_pct:.0%})")
print(f"✅ Final score: {final_score:.4f}")
print(f"✅ Base score: {base_score:.4f}")
print()

# Show phonetic distribution breakdown
if "first_name" in detailed_metrics and "metrics" in detailed_metrics["first_name"]:
    first_metrics = detailed_metrics["first_name"]["metrics"]
    if "similarity" in first_metrics:
        sim = first_metrics["similarity"]
        print(f"First Name Similarity:")
        print(f"  Phonetic: {sim.get('phonetic', 0):.4f}")
        print(f"  Orthographic: {sim.get('orthographic', 0):.4f}")
        print(f"  Combined: {sim.get('combined', 0):.4f}")

if "last_name" in detailed_metrics and "metrics" in detailed_metrics["last_name"]:
    last_metrics = detailed_metrics["last_name"]["metrics"]
    if "similarity" in last_metrics:
        sim = last_metrics["similarity"]
        print(f"Last Name Similarity:")
        print(f"  Phonetic: {sim.get('phonetic', 0):.4f}")
        print(f"  Orthographic: {sim.get('orthographic', 0):.4f}")
        print(f"  Combined: {sim.get('combined', 0):.4f}")

print("="*80)





