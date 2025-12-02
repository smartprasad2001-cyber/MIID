"""
Test the strategy-based generator and compare with unified_generator
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'MIID', 'validator'))

from strategy_based_generator import generate_full_name_variations_strategy_based
from reward import calculate_variation_quality

# Test names
test_names = [
    "Sebastian Martinez",
    "Constantinople Alexandrov",
    "Bartholomew Anderson"
]

light_count = 2
medium_count = 6
far_count = 2
total_count = light_count + medium_count + far_count

# Calculate target distribution
light_pct = light_count / total_count
medium_pct = medium_count / total_count
far_pct = far_count / total_count

phonetic_similarity = {
    "Light": light_pct,
    "Medium": medium_pct,
    "Far": far_pct
}
orthographic_similarity = {
    "Light": light_pct,
    "Medium": medium_pct,
    "Far": far_pct
}

print("="*80)
print("TESTING STRATEGY-BASED GENERATOR")
print("="*80)
print()
print("This generator cycles through all 25 strategies systematically")
print("ensuring maximum diversity of variations.")
print()

for test_name in test_names:
    print(f"\n{'='*80}")
    print(f"Testing: {test_name}")
    print(f"{'='*80}\n")
    
    try:
        # Generate variations
        variations = generate_full_name_variations_strategy_based(
            test_name,
            light_count=light_count,
            medium_count=medium_count,
            far_count=far_count,
            verbose=True
        )
        
        print(f"\n✅ Generated {len(variations)} variations")
        
        if len(variations) < total_count:
            print(f"⚠️  Warning: Expected {total_count}, got {len(variations)}")
        
        # Test with rewards.py
        final_score, base_score, detailed_metrics = calculate_variation_quality(
            original_name=test_name,
            variations=variations,
            phonetic_similarity=phonetic_similarity,
            orthographic_similarity=orthographic_similarity,
            expected_count=total_count,
            rule_based=None
        )
        
        print(f"\n📊 Scores:")
        print(f"  Final Score: {final_score:.4f}")
        print(f"  Base Score: {base_score:.4f}")
        
        # Show sample variations
        print(f"\n📝 Sample variations:")
        for i, var in enumerate(variations[:5], 1):
            print(f"  {i}. {var}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

print()

