"""
Generate 15 Light Similarity Variations for Any Word
Uses systematic modification strategies to find variations that score 1.0
"""

import jellyfish
import random
from typing import List, Set

def get_algorithm_codes(name: str) -> dict:
    """Get codes for all three algorithms."""
    return {
        'soundex': jellyfish.soundex(name),
        'metaphone': jellyfish.metaphone(name),
        'nysiis': jellyfish.nysiis(name)
    }

def predict_score(original: str, variation: str) -> float:
    """Predict similarity score using same logic as validator."""
    algorithms = {
        "soundex": lambda x, y: jellyfish.soundex(x) == jellyfish.soundex(y),
        "metaphone": lambda x, y: jellyfish.metaphone(x) == jellyfish.metaphone(y),
        "nysiis": lambda x, y: jellyfish.nysiis(x) == jellyfish.nysiis(y),
    }
    
    random.seed(hash(original) % 10000)
    selected = random.sample(list(algorithms.keys()), k=min(3, len(algorithms)))
    weights = [random.random() for _ in selected]
    total = sum(weights)
    normalized = [w / total for w in weights]
    
    score = sum(
        algorithms[algo](original, variation) * weight
        for algo, weight in zip(selected, normalized)
    )
    
    return float(score)

def generate_light_variations(original: str, count: int = 15) -> List[str]:
    """
    Generate variations that always score 1.0 (Light) by ensuring all algorithms match.
    
    Strategies:
    1. Add vowels at different positions
    2. Change vowels to other vowels
    3. Add common letters (n, h, y, r, l)
    4. Remove letters that don't affect phonetic codes
    5. Swap adjacent letters (if codes match)
    """
    target_codes = get_algorithm_codes(original)
    vowels = ['a', 'e', 'i', 'o', 'u']
    common_letters = ['n', 'h', 'y', 'r', 'l', 'm', 'd']
    
    candidates = []
    tested: Set[str] = set()
    
    # Strategy 1: Add vowels at different positions
    for pos in range(len(original) + 1):
        for v in vowels:
            var = original[:pos] + v + original[pos:]
            if var not in tested and len(var) <= len(original) + 2:
                tested.add(var)
                candidates.append(var)
    
    # Strategy 2: Change vowels to other vowels
    for i, char in enumerate(original):
        if char.lower() in vowels:
            for v in vowels:
                if v != char.lower():
                    var = original[:i] + v + original[i+1:]
                    if var not in tested:
                        tested.add(var)
                        candidates.append(var)
    
    # Strategy 3: Add common letters at different positions
    for pos in range(len(original) + 1):
        for letter in common_letters:
            var = original[:pos] + letter + original[pos:]
            if var not in tested and len(var) <= len(original) + 2:
                tested.add(var)
                candidates.append(var)
    
    # Strategy 4: Remove letters (test if codes still match)
    for i in range(len(original)):
        var = original[:i] + original[i+1:]
        if var not in tested and len(var) > 0:
            tested.add(var)
            candidates.append(var)
    
    # Strategy 5: Swap adjacent letters
    for i in range(len(original) - 1):
        var = original[:i] + original[i+1] + original[i] + original[i+2:]
        if var not in tested:
            tested.add(var)
            candidates.append(var)
    
    # Strategy 6: Double letters
    for i in range(len(original)):
        var = original[:i] + original[i] + original[i:]
        if var not in tested:
            tested.add(var)
            candidates.append(var)
    
    # Strategy 7: Add vowel combinations
    vowel_combos = ['ae', 'ai', 'ao', 'au', 'ea', 'ei', 'eo', 'eu', 'ia', 'ie', 'io', 'iu']
    for pos in range(len(original) + 1):
        for combo in vowel_combos:
            var = original[:pos] + combo + original[pos:]
            if var not in tested and len(var) <= len(original) + 3:
                tested.add(var)
                candidates.append(var)
    
    # Test candidates for perfect matches (all 3 algorithms match)
    perfect_matches = []
    for var in candidates:
        if var == original:
            continue
        
        var_codes = get_algorithm_codes(var)
        
        # Check if all codes match
        if (var_codes['soundex'] == target_codes['soundex'] and
            var_codes['metaphone'] == target_codes['metaphone'] and
            var_codes['nysiis'] == target_codes['nysiis']):
            
            if var not in perfect_matches:
                perfect_matches.append(var)
                if len(perfect_matches) >= count:
                    break
    
    return perfect_matches

def display_results(original: str, variations: List[str]):
    """Display results with detailed scoring information."""
    target_codes = get_algorithm_codes(original)
    
    print("="*80)
    print(f"LIGHT VARIATIONS FOR: '{original}'")
    print("="*80)
    print()
    print(f"Target codes:")
    print(f"  Soundex:  {target_codes['soundex']}")
    print(f"  Metaphone: {target_codes['metaphone']}")
    print(f"  NYSIIS:   {target_codes['nysiis']}")
    print()
    print(f"Found {len(variations)} perfect Light variations (all score 1.0):")
    print("-" * 80)
    print()
    
    for i, var in enumerate(variations, 1):
        score = predict_score(original, var)
        var_codes = get_algorithm_codes(var)
        
        # Verify all match
        all_match = (var_codes['soundex'] == target_codes['soundex'] and
                    var_codes['metaphone'] == target_codes['metaphone'] and
                    var_codes['nysiis'] == target_codes['nysiis'])
        
        print(f"{i:2d}. '{var:25s}' → Score: {score:.4f}")
        print(f"     Soundex: {var_codes['soundex']:6s} {'✓' if var_codes['soundex'] == target_codes['soundex'] else '✗'}, "
              f"Metaphone: {var_codes['metaphone']:8s} {'✓' if var_codes['metaphone'] == target_codes['metaphone'] else '✗'}, "
              f"NYSIIS: {var_codes['nysiis']:12s} {'✓' if var_codes['nysiis'] == target_codes['nysiis'] else '✗'}")
        
        if all_match:
            print(f"     ✅ All algorithms match → Perfect 1.0!")
        print()
    
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print()
    print(f"✅ Generated {len(variations)} Light variations for '{original}'")
    print("✅ All variations score 1.0 (Light) because all algorithms match")
    print("✅ These can be used to guarantee Light similarity in validator scoring")
    print()

if __name__ == "__main__":
    # Test with difficult words
    difficult_words = [
        "Christopher",
        "Elizabeth", 
        "Alexander",
        "Catherine",
        "Benjamin",
        "Theodore",
        "Guadalupe",
        "Constantinople"
    ]
    
    print("="*80)
    print("GENERATING 15 LIGHT VARIATIONS FOR DIFFICULT WORDS")
    print("="*80)
    print()
    
    for word in difficult_words:
        variations = generate_light_variations(word, count=15)
        
        if len(variations) >= 15:
            display_results(word, variations[:15])
            break
        else:
            print(f"⚠️  '{word}': Found {len(variations)} perfect matches (need 15)")
            print()
    
    # Also test with a custom word
    print("\n" + "="*80)
    print("TEST WITH CUSTOM WORD")
    print("="*80)
    print()
    
    custom_word = "Christopher"  # Change this to test other words
    variations = generate_light_variations(custom_word, count=15)
    display_results(custom_word, variations[:15])

