#!/usr/bin/env python3
"""Debug why Elizabeth Rodriguez and Hassan Abdullah generate low variations"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'MIID', 'validator'))

from unified_generator import generate_full_name_variations

def test_name(name, light_count, medium_count, far_count):
    print(f"\n{'='*80}")
    print(f"TESTING: {name}")
    print(f"{'='*80}\n")
    
    print(f"Target: {light_count} Light, {medium_count} Medium, {far_count} Far (total: {light_count + medium_count + far_count})")
    print()
    
    try:
        variations = generate_full_name_variations(
            full_name=name,
            light_count=light_count,
            medium_count=medium_count,
            far_count=far_count,
            verbose=True  # Enable verbose to see what's happening
        )
        
        print(f"\n✅ Generated {len(variations)} variations:")
        for i, var in enumerate(variations, 1):
            print(f"  {i}. {var}")
        
        if len(variations) < (light_count + medium_count + far_count):
            print(f"\n⚠️  WARNING: Expected {light_count + medium_count + far_count}, got {len(variations)}")
            print("   Possible reasons:")
            print("   1. Hit max_total_candidates_checked limit")
            print("   2. Hit max_depth_limit")
            print("   3. Not enough candidates found in target score ranges")
        
        return len(variations)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 0

if __name__ == "__main__":
    # Test the problematic names
    test_cases = [
        ("Elizabeth Rodriguez", 3, 9, 3),
        ("Hassan Abdullah", 3, 9, 3),
    ]
    
    print("="*80)
    print("DEBUGGING LOW VARIATION GENERATION")
    print("="*80)
    
    for name, light, medium, far in test_cases:
        result = test_name(name, light, medium, far)
        print(f"\nResult: {result}/{light + medium + far} variations generated")
    
    print("\n" + "="*80)
    print("ANALYSIS:")
    print("="*80)
    print("""
The generator has limits:
1. max_total_candidates_checked - Maximum candidates to check (300k-1M depending on name length)
2. max_depth_limit - Maximum recursion depth (5-7 depending on name length)
3. Score range requirements - Must find variations in specific phonetic score ranges

If a name is:
- Very long (like "Elizabeth" = 9 chars, "Rodriguez" = 9 chars)
- Has complex phonetic structure
- Doesn't have many variations in the target score ranges

Then it may hit the limits before finding enough variations.
    """)

