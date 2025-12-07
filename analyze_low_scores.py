#!/usr/bin/env python3
"""
Analyze why some names have low orthographic quality scores.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'MIID', 'validator'))

from maximize_orthographic_similarity import OrthographicBruteForceGenerator, ORTHOGRAPHIC_BOUNDARIES

# Names with different scores
high_score_names = [
    "Asma Al-Akhras",      # 1.0000
    "Leonid Pasechnik",    # 1.0000
    "Anna Molchanova",     # 1.0000
]

low_score_names = [
    "Akhmed Dudaev",       # 0.3400
    "Yuriy Hovtvin",       # 0.3400
    "Zeinab Jammeh",       # 0.3400
]

TARGET_DISTRIBUTION = {"Light": 0.2, "Medium": 0.6, "Far": 0.2}
VARIATION_COUNT = 15

def analyze_name(name, expected_quality):
    """Analyze a name's quality score."""
    print("=" * 80)
    print(f"Analyzing: {name} (Expected Quality: {expected_quality:.4f})")
    print("=" * 80)
    
    generator = OrthographicBruteForceGenerator(
        original_name=name,
        target_distribution=TARGET_DISTRIBUTION
    )
    
    # Generate variations
    variations, metrics = generator.generate_optimal_variations(variation_count=VARIATION_COUNT)
    
    # Get final scores
    final_scores = [generator.calculate_orthographic_score(var) for var in variations]
    
    # Categorize scores
    categories = {"Light": [], "Medium": [], "Far": [], "Below": [], "Above": []}
    for score in final_scores:
        if score >= 0.70:
            categories["Light"].append(score)
        elif score >= 0.50:
            categories["Medium"].append(score)
        elif score >= 0.20:
            categories["Far"].append(score)
        elif score < 0.20:
            categories["Below"].append(score)
        else:
            categories["Above"].append(score)
    
    # Calculate distribution
    total = len(final_scores)
    actual_dist = {
        "Light": len(categories["Light"]) / total,
        "Medium": len(categories["Medium"]) / total,
        "Far": len(categories["Far"]) / total,
        "Below": len(categories["Below"]) / total,
        "Above": len(categories["Above"]) / total
    }
    
    # Calculate quality manually
    quality = 0.0
    total_matched = 0
    
    for level, (lower, upper) in ORTHOGRAPHIC_BOUNDARIES.items():
        target_percentage = TARGET_DISTRIBUTION.get(level, 0.0)
        if target_percentage == 0.0:
            continue
        
        count = sum(1 for score in final_scores if lower <= score <= upper)
        target_count = int(target_percentage * total)
        
        if target_count > 0:
            match_ratio = count / target_count
            if match_ratio <= 1.0:
                match_quality = match_ratio
            else:
                match_quality = 1.0 - (1.0 / (1.0 + match_ratio - 1.0))
            quality += target_percentage * match_quality
            total_matched += count
    
    # Penalty for unmatched
    unmatched = total - total_matched
    if unmatched > 0:
        penalty = 0.1 * (unmatched / total)
        quality = max(0.0, quality - penalty)
    
    print(f"\nQuality Score: {quality:.4f} (Expected: {expected_quality:.4f})")
    print(f"Actual Quality from Metrics: {metrics.get('quality_score', 0.0):.4f}")
    print()
    
    print("Distribution Analysis:")
    print(f"  Target: Light=20.0%, Medium=60.0%, Far=20.0%")
    print(f"  Actual: Light={actual_dist['Light']:.1%}, Medium={actual_dist['Medium']:.1%}, Far={actual_dist['Far']:.1%}")
    if actual_dist['Below'] > 0:
        print(f"  ⚠️  Below threshold (<0.20): {actual_dist['Below']:.1%} ({len(categories['Below'])} variations)")
    if actual_dist['Above'] > 0:
        print(f"  ⚠️  Above range (>1.00): {actual_dist['Above']:.1%} ({len(categories['Above'])} variations)")
    print()
    
    print("Score Breakdown:")
    print(f"  Light (0.70-1.00):   {len(categories['Light'])} variations")
    print(f"  Medium (0.50-0.69):  {len(categories['Medium'])} variations")
    print(f"  Far (0.20-0.49):     {len(categories['Far'])} variations")
    print(f"  Below (<0.20):       {len(categories['Below'])} variations")
    print(f"  Above (>1.00):       {len(categories['Above'])} variations")
    print(f"  Total matched:       {total_matched}/{total}")
    print(f"  Unmatched:           {unmatched} (penalty: {0.1 * (unmatched / total) if unmatched > 0 else 0.0:.4f})")
    print()
    
    print("Score Ranges:")
    if final_scores:
        print(f"  Min: {min(final_scores):.4f}")
        print(f"  Max: {max(final_scores):.4f}")
        print(f"  Avg: {sum(final_scores) / len(final_scores):.4f}")
    print()
    
    # Show problematic variations
    if categories['Below']:
        print("⚠️  Variations Below Threshold (<0.20):")
        for i, var in enumerate(variations):
            score = final_scores[i]
            if score < 0.20:
                print(f"    {var:40s} | Score: {score:.4f}")
        print()
    
    # Calculate match quality per category
    print("Category Match Quality:")
    for level, (lower, upper) in ORTHOGRAPHIC_BOUNDARIES.items():
        target_percentage = TARGET_DISTRIBUTION.get(level, 0.0)
        if target_percentage == 0.0:
            continue
        
        count = sum(1 for score in final_scores if lower <= score <= upper)
        target_count = int(target_percentage * total)
        
        if target_count > 0:
            match_ratio = count / target_count
            if match_ratio <= 1.0:
                match_quality = match_ratio
            else:
                match_quality = 1.0 - (1.0 / (1.0 + match_ratio - 1.0))
            contribution = target_percentage * match_quality
            print(f"  {level:6s}: {count:2d}/{target_count:2d} variations, ratio={match_ratio:.3f}, quality={match_quality:.3f}, contribution={contribution:.4f}")
    
    print()
    return quality, actual_dist, final_scores

def main():
    print("=" * 80)
    print("ANALYZING LOW QUALITY SCORES")
    print("=" * 80)
    print()
    
    print("HIGH SCORE NAMES (Expected: 1.0000)")
    print("-" * 80)
    high_results = []
    for name in high_score_names:
        quality, dist, scores = analyze_name(name, 1.0000)
        high_results.append((name, quality, dist, scores))
    
    print("\n" + "=" * 80)
    print("LOW SCORE NAMES (Expected: 0.3400)")
    print("-" * 80)
    low_results = []
    for name in low_score_names:
        quality, dist, scores = analyze_name(name, 0.3400)
        low_results.append((name, quality, dist, scores))
    
    print("\n" + "=" * 80)
    print("COMPARISON SUMMARY")
    print("=" * 80)
    print()
    
    print("High Score Names:")
    for name, quality, dist, scores in high_results:
        unmatched = len(scores) - sum(1 for s in scores if 0.20 <= s <= 1.00)
        print(f"  {name:30s}: Quality={quality:.4f}, Below={dist['Below']:.1%}, Unmatched={unmatched}")
    
    print("\nLow Score Names:")
    for name, quality, dist, scores in low_results:
        unmatched = len(scores) - sum(1 for s in scores if 0.20 <= s <= 1.00)
        print(f"  {name:30s}: Quality={quality:.4f}, Below={dist['Below']:.1%}, Unmatched={unmatched}")
    
    print("\n" + "=" * 80)
    print("KEY FINDINGS")
    print("=" * 80)
    print("""
The quality score is calculated based on:
1. How well variations match the target distribution (Light/Medium/Far)
2. Penalty for variations outside boundaries (<0.20 or >1.00)

Low scores (0.3400) likely indicate:
- Variations falling outside the valid range (<0.20 or >1.00)
- Poor match to target distribution within categories
- High penalty from unmatched variations

High scores (1.0000) indicate:
- Perfect match to target distribution
- All variations within valid boundaries
- No unmatched variations
    """)

if __name__ == "__main__":
    main()

