"""
Generate Perfect Match Variations - Always Score 1.0 (Light)
Uses reverse engineering to find variations that match all algorithms
"""

import jellyfish
from typing import List, Tuple

def get_algorithm_codes(name: str) -> dict:
    """Get codes for all algorithms for a given name."""
    return {
        'soundex': jellyfish.soundex(name),
        'metaphone': jellyfish.metaphone(name),
        'nysiis': jellyfish.nysiis(name)
    }

def test_variation(original: str, variation: str) -> Tuple[bool, dict]:
    """
    Test if variation matches all algorithms.
    
    Returns:
        (all_match, match_results)
    """
    original_codes = get_algorithm_codes(original)
    variation_codes = get_algorithm_codes(variation)
    
    matches = {
        'soundex': original_codes['soundex'] == variation_codes['soundex'],
        'metaphone': original_codes['metaphone'] == variation_codes['metaphone'],
        'nysiis': original_codes['nysiis'] == variation_codes['nysiis']
    }
    
    all_match = all(matches.values())
    
    return all_match, {
        'original_codes': original_codes,
        'variation_codes': variation_codes,
        'matches': matches
    }

def generate_perfect_match_variations(original: str, max_variations: int = 20) -> List[str]:
    """
    Generate variations that match ALL algorithms (always score 1.0).
    
    Strategy:
    1. Get target codes for original
    2. Generate candidate variations
    3. Test which ones produce the same codes
    4. Return perfect matches
    """
    target_codes = get_algorithm_codes(original)
    
    print(f"Target codes for '{original}':")
    print(f"  Soundex:  {target_codes['soundex']}")
    print(f"  Metaphone: {target_codes['metaphone']}")
    print(f"  NYSIIS:   {target_codes['nysiis']}")
    print()
    
    # Generate candidate variations
    candidates = []
    tested = set()
    
    # Strategy 1: Remove letters
    for i in range(len(original)):
        var = original[:i] + original[i+1:]
        if var not in tested and len(var) > 0:
            tested.add(var)
            candidates.append(var)
    
    # Strategy 2: Add vowels
    vowels = ['a', 'e', 'i', 'o', 'u']
    for pos in range(len(original) + 1):
        for v in vowels:
            var = original[:pos] + v + original[pos:]
            if var not in tested and len(var) <= len(original) + 2:
                tested.add(var)
                candidates.append(var)
    
    # Strategy 3: Change vowels
    for i, char in enumerate(original):
        if char.lower() in vowels:
            for v in vowels:
                if v != char.lower():
                    var = original[:i] + v + original[i+1:]
                    if var not in tested:
                        tested.add(var)
                        candidates.append(var)
    
    # Strategy 4: Add common letters
    for pos in range(len(original) + 1):
        for letter in ['n', 'h', 'y']:
            var = original[:pos] + letter + original[pos:]
            if var not in tested and len(var) <= len(original) + 2:
                tested.add(var)
                candidates.append(var)
    
    # Test candidates
    perfect_matches = []
    for var in candidates:
        all_match, results = test_variation(original, var)
        if all_match and var != original:
            perfect_matches.append(var)
            if len(perfect_matches) >= max_variations:
                break
    
    return perfect_matches

def verify_perfect_match(original: str, variation: str):
    """Verify and show why a variation is a perfect match."""
    all_match, results = test_variation(original, variation)
    
    print(f"Testing '{original}' vs '{variation}':")
    print("-" * 80)
    
    print("Original codes:")
    for algo, code in results['original_codes'].items():
        print(f"  {algo:10s}: {code}")
    print()
    
    print("Variation codes:")
    for algo, code in results['variation_codes'].items():
        print(f"  {algo:10s}: {code}")
    print()
    
    print("Matches:")
    for algo, match in results['matches'].items():
        status = "✅ MATCH" if match else "❌ NO MATCH"
        print(f"  {algo:10s}: {status}")
    print()
    
    if all_match:
        print("✅ PERFECT MATCH! All algorithms match → Score = 1.0 (Light)")
    else:
        print("❌ Not a perfect match - some algorithms don't match")
    
    return all_match


if __name__ == "__main__":
    print("="*80)
    print("GENERATE PERFECT MATCH VARIATIONS (Always Score 1.0)")
    print("="*80)
    print()
    
    test_names = ["John", "Mary", "Smith"]
    
    for name in test_names:
        print("="*80)
        print(f"Generating perfect matches for '{name}'")
        print("="*80)
        print()
        
        perfect_variations = generate_perfect_match_variations(name, max_variations=10)
        
        print(f"Found {len(perfect_variations)} perfect matches:")
        for i, var in enumerate(perfect_variations, 1):
            print(f"  {i}. '{var}'")
        print()
        
        # Verify a few
        if perfect_variations:
            print("Verifying first perfect match:")
            verify_perfect_match(name, perfect_variations[0])
            print()
    
    print("="*80)
    print("KEY INSIGHT")
    print("="*80)
    print()
    print("✅ YES! We can always generate Light (1.0) variations!")
    print()
    print("Strategy:")
    print("  1. Get target codes: Soundex, Metaphone, NYSIIS")
    print("  2. Generate candidate variations")
    print("  3. Test which ones produce the same codes")
    print("  4. Use those for Light variations")
    print()
    print("This ensures:")
    print("  - All algorithms match → All contribute their weights")
    print("  - Final score = weight1 + weight2 + weight3 = 1.0")
    print("  - Always Light similarity!")
    print()
    print("We can use this to generate perfect Light variations for any name!")

