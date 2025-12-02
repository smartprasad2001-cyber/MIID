#!/usr/bin/env python3
"""
Test variations using phonetic and orthographic similarity functions from rewards.py
"""

import os
import sys
import json

# Flush output immediately
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

print("🔍 Testing variations with phonetic and orthographic similarity...", flush=True)

# Add paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'MIID', 'validator'))

print("📦 Importing modules...", flush=True)

try:
    from reward import (
        calculate_phonetic_similarity,
        calculate_orthographic_similarity
    )
    print("✅ Imports successful", flush=True)
except Exception as e:
    print(f"❌ Import error: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

def main():
    print("="*80, flush=True)
    print("PHONETIC AND ORTHOGRAPHIC SIMILARITY TEST")
    print("="*80, flush=True)
    print()
    
    # Load variations
    input_file = "zero_phonetic_variations.json"
    if not os.path.exists(input_file):
        print(f"❌ File not found: {input_file}", flush=True)
        return
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    variations = data.get('variations', {})
    print(f"✅ Loaded variations for {len(variations)} names\n", flush=True)
    
    all_results = {}
    
    for name, name_variations in variations.items():
        print(f"📝 Testing: {name}", flush=True)
        print(f"   Original: {name}", flush=True)
        print(f"   Variations: {len(name_variations)}", flush=True)
        print()
        
        name_results = []
        
        for i, variation in enumerate(name_variations, 1):
            # Calculate phonetic similarity
            phonetic_score = calculate_phonetic_similarity(name, variation)
            
            # Calculate orthographic similarity
            orthographic_score = calculate_orthographic_similarity(name, variation)
            
            # Determine range
            phonetic_range = "Unknown"
            if phonetic_score >= 0.8:
                phonetic_range = "Light"
            elif phonetic_score >= 0.6:
                phonetic_range = "Medium"
            elif phonetic_score >= 0.3:
                phonetic_range = "Far"
            else:
                phonetic_range = "Very Far"
            
            orthographic_range = "Unknown"
            if orthographic_score >= 0.7:
                orthographic_range = "Light"
            elif orthographic_score >= 0.5:
                orthographic_range = "Medium"
            elif orthographic_score >= 0.2:
                orthographic_range = "Far"
            else:
                orthographic_range = "Very Far"
            
            name_results.append({
                "variation": variation,
                "phonetic_score": phonetic_score,
                "orthographic_score": orthographic_score,
                "phonetic_range": phonetic_range,
                "orthographic_range": orthographic_range
            })
            
            # Print first 5 variations
            if i <= 5:
                print(f"   [{i:2d}] {variation}", flush=True)
                print(f"        Phonetic:      {phonetic_score:.4f} ({phonetic_range})", flush=True)
                print(f"        Orthographic:   {orthographic_score:.4f} ({orthographic_range})", flush=True)
                print()
        
        # Calculate averages
        avg_phonetic = sum(r['phonetic_score'] for r in name_results) / len(name_results) if name_results else 0.0
        avg_orthographic = sum(r['orthographic_score'] for r in name_results) / len(name_results) if name_results else 0.0
        
        # Count by range
        phonetic_light = sum(1 for r in name_results if r['phonetic_range'] == 'Light')
        phonetic_medium = sum(1 for r in name_results if r['phonetic_range'] == 'Medium')
        phonetic_far = sum(1 for r in name_results if r['phonetic_range'] == 'Far')
        phonetic_very_far = sum(1 for r in name_results if r['phonetic_range'] == 'Very Far')
        
        orthographic_light = sum(1 for r in name_results if r['orthographic_range'] == 'Light')
        orthographic_medium = sum(1 for r in name_results if r['orthographic_range'] == 'Medium')
        orthographic_far = sum(1 for r in name_results if r['orthographic_range'] == 'Far')
        orthographic_very_far = sum(1 for r in name_results if r['orthographic_range'] == 'Very Far')
        
        print(f"   📊 Summary for {name}:", flush=True)
        print(f"      Average Phonetic:      {avg_phonetic:.4f}", flush=True)
        print(f"      Average Orthographic:  {avg_orthographic:.4f}", flush=True)
        print(f"      Phonetic Distribution: Light={phonetic_light}, Medium={phonetic_medium}, Far={phonetic_far}, Very Far={phonetic_very_far}", flush=True)
        print(f"      Orthographic Distribution: Light={orthographic_light}, Medium={orthographic_medium}, Far={orthographic_far}, Very Far={orthographic_very_far}", flush=True)
        print()
        print("="*80, flush=True)
        print()
        
        all_results[name] = {
            "original": name,
            "variations": name_results,
            "summary": {
                "avg_phonetic": avg_phonetic,
                "avg_orthographic": avg_orthographic,
                "phonetic_distribution": {
                    "light": phonetic_light,
                    "medium": phonetic_medium,
                    "far": phonetic_far,
                    "very_far": phonetic_very_far
                },
                "orthographic_distribution": {
                    "light": orthographic_light,
                    "medium": orthographic_medium,
                    "far": orthographic_far,
                    "very_far": orthographic_very_far
                }
            }
        }
    
    # Save results
    output_file = "phonetic_orthographic_test_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "test_date": __import__('datetime').datetime.now().isoformat(),
            "results": all_results
        }, f, indent=2, ensure_ascii=False)
    
    print("="*80, flush=True)
    print(f"✅ COMPLETE - Tested {len(all_results)} names", flush=True)
    print(f"💾 Results saved to {output_file}", flush=True)
    print("="*80, flush=True)
    
    # Print overall summary
    print()
    print("="*80, flush=True)
    print("OVERALL SUMMARY", flush=True)
    print("="*80, flush=True)
    
    all_avg_phonetic = []
    all_avg_orthographic = []
    
    for name, result in all_results.items():
        all_avg_phonetic.append(result['summary']['avg_phonetic'])
        all_avg_orthographic.append(result['summary']['avg_orthographic'])
    
    if all_avg_phonetic:
        print(f"Average Phonetic Similarity across all names:      {sum(all_avg_phonetic) / len(all_avg_phonetic):.4f}", flush=True)
        print(f"Average Orthographic Similarity across all names: {sum(all_avg_orthographic) / len(all_avg_orthographic):.4f}", flush=True)
    
    print("="*80, flush=True)

if __name__ == '__main__':
    main()





