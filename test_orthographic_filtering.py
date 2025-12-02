#!/usr/bin/env python3
"""
Test script to verify orthographic filtering works correctly.
Tests that variations match both phonetic AND orthographic target ranges.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'MIID', 'validator'))

from unified_generator import generate_light_variations, generate_medium_variations, generate_far_variations
from reward import calculate_phonetic_similarity, calculate_orthographic_similarity
import time

def test_orthographic_distribution():
    """Test that generated variations match orthographic target ranges."""
    
    print("="*80)
    print("Testing Orthographic Filtering")
    print("="*80)
    print()
    
    # Test with a complex name
    test_name = "Rodriguez"
    print(f"Testing name: '{test_name}'")
    print()
    
    # Generate variations for each category
    print("Generating Light variations (phonetic: all match, orthographic: 0.70-1.00)...")
    start_time = time.time()
    light_vars = generate_light_variations(test_name, count=3, verbose=True)
    light_time = time.time() - start_time
    print(f"  Generated {len(light_vars)} Light variations in {light_time:.2f}s")
    print()
    
    print("Generating Medium variations (phonetic: 0.60-0.79, orthographic: 0.50-0.69)...")
    start_time = time.time()
    medium_vars = generate_medium_variations(test_name, count=9, verbose=True)
    medium_time = time.time() - start_time
    print(f"  Generated {len(medium_vars)} Medium variations in {medium_time:.2f}s")
    print()
    
    print("Generating Far variations (phonetic: 0.30-0.59, orthographic: 0.20-0.49)...")
    start_time = time.time()
    far_vars = generate_far_variations(test_name, count=3, verbose=True)
    far_time = time.time() - start_time
    print(f"  Generated {len(far_vars)} Far variations in {far_time:.2f}s")
    print()
    
    # Analyze all variations
    all_vars = light_vars + medium_vars + far_vars
    print(f"Total variations: {len(all_vars)}")
    print()
    
    print("="*80)
    print("Analysis: Phonetic Scores")
    print("="*80)
    
    light_phonetic = []
    medium_phonetic = []
    far_phonetic = []
    
    for var in light_vars:
        score = calculate_phonetic_similarity(test_name, var)
        light_phonetic.append(score)
        print(f"  Light: '{var}' → phonetic={score:.4f}")
    
    for var in medium_vars:
        score = calculate_phonetic_similarity(test_name, var)
        medium_phonetic.append(score)
        print(f"  Medium: '{var}' → phonetic={score:.4f}")
    
    for var in far_vars:
        score = calculate_phonetic_similarity(test_name, var)
        far_phonetic.append(score)
        print(f"  Far: '{var}' → phonetic={score:.4f}")
    
    print()
    print(f"Light phonetic range: {min(light_phonetic):.4f} - {max(light_phonetic):.4f} (target: all match)")
    print(f"Medium phonetic range: {min(medium_phonetic):.4f} - {max(medium_phonetic):.4f} (target: 0.60-0.79)")
    print(f"Far phonetic range: {min(far_phonetic):.4f} - {max(far_phonetic):.4f} (target: 0.30-0.59)")
    print()
    
    print("="*80)
    print("Analysis: Orthographic Scores")
    print("="*80)
    
    light_ortho = []
    medium_ortho = []
    far_ortho = []
    
    for var in light_vars:
        score = calculate_orthographic_similarity(test_name, var)
        light_ortho.append(score)
        in_range = "✅" if 0.70 <= score <= 1.00 else "❌"
        print(f"  Light: '{var}' → orthographic={score:.4f} {in_range}")
    
    for var in medium_vars:
        score = calculate_orthographic_similarity(test_name, var)
        medium_ortho.append(score)
        in_range = "✅" if 0.50 <= score <= 0.69 else "❌"
        print(f"  Medium: '{var}' → orthographic={score:.4f} {in_range}")
    
    for var in far_vars:
        score = calculate_orthographic_similarity(test_name, var)
        far_ortho.append(score)
        in_range = "✅" if 0.20 <= score <= 0.49 else "❌"
        print(f"  Far: '{var}' → orthographic={score:.4f} {in_range}")
    
    print()
    print(f"Light orthographic range: {min(light_ortho):.4f} - {max(light_ortho):.4f} (target: 0.70-1.00)")
    print(f"Medium orthographic range: {min(medium_ortho):.4f} - {max(medium_ortho):.4f} (target: 0.50-0.69)")
    print(f"Far orthographic range: {min(far_ortho):.4f} - {max(far_ortho):.4f} (target: 0.20-0.49)")
    print()
    
    # Check compliance
    print("="*80)
    print("Compliance Check")
    print("="*80)
    
    light_ok = all(0.70 <= s <= 1.00 for s in light_ortho)
    medium_ok = all(0.50 <= s <= 0.69 for s in medium_ortho)
    far_ok = all(0.20 <= s <= 0.49 for s in far_ortho)
    
    print(f"Light orthographic compliance: {'✅ PASS' if light_ok else '❌ FAIL'}")
    print(f"Medium orthographic compliance: {'✅ PASS' if medium_ok else '❌ FAIL'}")
    print(f"Far orthographic compliance: {'✅ PASS' if far_ok else '❌ FAIL'}")
    print()
    
    # Distribution check
    total = len(all_vars)
    light_pct = len(light_vars) / total * 100
    medium_pct = len(medium_vars) / total * 100
    far_pct = len(far_vars) / total * 100
    
    print("="*80)
    print("Distribution Check")
    print("="*80)
    print(f"Light: {len(light_vars)}/{total} = {light_pct:.1f}% (target: ~20%)")
    print(f"Medium: {len(medium_vars)}/{total} = {medium_pct:.1f}% (target: ~60%)")
    print(f"Far: {len(far_vars)}/{total} = {far_pct:.1f}% (target: ~20%)")
    print()
    
    # Overall result
    all_ok = light_ok and medium_ok and far_ok
    print("="*80)
    if all_ok:
        print("✅ ALL TESTS PASSED - Orthographic filtering works correctly!")
    else:
        print("❌ SOME TESTS FAILED - Check orthographic ranges")
    print("="*80)
    
    return all_ok

if __name__ == "__main__":
    test_orthographic_distribution()

