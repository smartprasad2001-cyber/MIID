"""
Reverse Engineer Phonetic Similarity Algorithms
Predict which variations will give target similarity scores
"""

import jellyfish
import random
from collections import defaultdict

def calculate_phonetic_similarity(original_name: str, variation: str) -> float:
    """Same as validator - for testing"""
    algorithms = {
        "soundex": lambda x, y: jellyfish.soundex(x) == jellyfish.soundex(y),
        "metaphone": lambda x, y: jellyfish.metaphone(x) == jellyfish.metaphone(y),
        "nysiis": lambda x, y: jellyfish.nysiis(x) == jellyfish.nysiis(y),
    }
    
    random.seed(hash(original_name) % 10000)
    selected_algorithms = random.sample(list(algorithms.keys()), k=min(3, len(algorithms)))
    
    weights = [random.random() for _ in selected_algorithms]
    total_weight = sum(weights)
    normalized_weights = [w / total_weight for w in weights]
    
    phonetic_score = sum(
        algorithms[algo](original_name, variation) * weight
        for algo, weight in zip(selected_algorithms, normalized_weights)
    )
    
    return float(phonetic_score)


def test_all_algorithms(original: str, variation: str):
    """Test variation against all algorithms individually"""
    results = {}
    
    # Soundex
    soundex_match = jellyfish.soundex(original) == jellyfish.soundex(variation)
    results['soundex'] = soundex_match
    
    # Metaphone
    metaphone_match = jellyfish.metaphone(original) == jellyfish.metaphone(variation)
    results['metaphone'] = metaphone_match
    
    # NYSIIS
    nysiis_match = jellyfish.nysiis(original) == jellyfish.nysiis(variation)
    results['nysiis'] = nysiis_match
    
    # Show encodings
    print(f"  Soundex:  '{original}' = {jellyfish.soundex(original)}, '{variation}' = {jellyfish.soundex(variation)} → {soundex_match}")
    print(f"  Metaphone: '{original}' = {jellyfish.metaphone(original)}, '{variation}' = {jellyfish.metaphone(variation)} → {metaphone_match}")
    print(f"  NYSIIS:   '{original}' = {jellyfish.nysiis(original)}, '{variation}' = {jellyfish.nysiis(variation)} → {nysiis_match}")
    
    return results


def generate_variations_for_target_score(original: str, target_score: float, max_tries: int = 100):
    """
    Generate variations that will achieve target similarity score.
    Strategy: Test variations and see which ones match the target.
    """
    print(f"\nGenerating variations for '{original}' targeting score {target_score:.2f}:")
    print("-" * 80)
    
    # Strategy: Try different letter modifications
    variations = []
    tested = set()
    
    # Try removing letters
    for i in range(len(original)):
        if i < len(original):
            var = original[:i] + original[i+1:]
            if var not in tested and len(var) > 0:
                tested.add(var)
                score = calculate_phonetic_similarity(original, var)
                variations.append((var, score, f"remove pos {i}"))
    
    # Try swapping adjacent letters
    for i in range(len(original) - 1):
        var = original[:i] + original[i+1] + original[i] + original[i+2:]
        if var not in tested:
            tested.add(var)
            score = calculate_phonetic_similarity(original, var)
            variations.append((var, score, f"swap {i}-{i+1}"))
    
    # Try changing vowels
    vowels = ['a', 'e', 'i', 'o', 'u']
    for i, char in enumerate(original):
        if char.lower() in vowels:
            for v in vowels:
                if v != char.lower():
                    var = original[:i] + v + original[i+1:]
                    if var not in tested:
                        tested.add(var)
                        score = calculate_phonetic_similarity(original, var)
                        variations.append((var, score, f"vowel change pos {i}"))
    
    # Try adding letters
    for pos in range(len(original) + 1):
        for letter in ['a', 'e', 'i', 'o', 'u', 'y']:
            var = original[:pos] + letter + original[pos:]
            if var not in tested:
                tested.add(var)
                score = calculate_phonetic_similarity(original, var)
                variations.append((var, score, f"add '{letter}' at pos {pos}"))
    
    # Sort by how close to target
    variations.sort(key=lambda x: abs(x[1] - target_score))
    
    # Show top matches
    print(f"\nTop 10 variations closest to target score {target_score:.2f}:")
    for var, score, strategy in variations[:10]:
        diff = abs(score - target_score)
        category = "Light" if 0.8 <= score <= 1.0 else "Medium" if 0.6 <= score < 0.8 else "Far" if 0.3 <= score < 0.6 else "Too Low"
        print(f"  '{var:15s}' → {score:.4f} (diff: {diff:.4f}, {category:8s}) [{strategy}]")
    
    # Find exact matches (within 0.05)
    matches = [v for v in variations if abs(v[1] - target_score) < 0.05]
    if matches:
        print(f"\n✅ Found {len(matches)} variations within 0.05 of target:")
        for var, score, strategy in matches[:5]:
            print(f"  '{var}' → {score:.4f} [{strategy}]")
    else:
        print(f"\n⚠️  No exact matches found. Closest: '{variations[0][0]}' → {variations[0][1]:.4f}")
    
    return variations


def analyze_algorithm_patterns(original: str):
    """Analyze which types of changes work best for each algorithm"""
    print(f"\nAnalyzing algorithm patterns for '{original}':")
    print("=" * 80)
    
    # Test different variation types
    test_variations = [
        ("Original", original),
        ("Remove 1 end", original[:-1] if len(original) > 1 else original),
        ("Remove 1 middle", original[:len(original)//2] + original[len(original)//2+1:] if len(original) > 1 else original),
        ("Swap adjacent", original[1] + original[0] + original[2:] if len(original) >= 2 else original),
        ("Change vowel", original.replace('a', 'e').replace('e', 'i').replace('i', 'o').replace('o', 'u').replace('u', 'a') if any(c in 'aeiou' for c in original.lower()) else original),
    ]
    
    print(f"\nAlgorithm encodings for '{original}':")
    print(f"  Soundex:  {jellyfish.soundex(original)}")
    print(f"  Metaphone: {jellyfish.metaphone(original)}")
    print(f"  NYSIIS:   {jellyfish.nysiis(original)}")
    print()
    
    print("Testing variations:")
    for desc, var in test_variations:
        if var == original:
            continue
        print(f"\n  {desc}: '{var}'")
        test_all_algorithms(original, var)
        score = calculate_phonetic_similarity(original, var)
        print(f"  Combined Score: {score:.4f}")


def build_prediction_model(original: str, sample_variations: list):
    """Build a model to predict scores for new variations"""
    print(f"\nBuilding prediction model for '{original}':")
    print("=" * 80)
    
    # Test sample variations
    results = []
    for var in sample_variations:
        score = calculate_phonetic_similarity(original, var)
        algo_results = test_all_algorithms(original, var)
        results.append({
            'variation': var,
            'score': score,
            'algorithms': algo_results
        })
    
    # Analyze patterns
    print("\nPattern Analysis:")
    print("-" * 80)
    
    # Which algorithm is most predictive?
    soundex_matches = sum(1 for r in results if r['algorithms']['soundex'])
    metaphone_matches = sum(1 for r in results if r['algorithms']['metaphone'])
    nysiis_matches = sum(1 for r in results if r['algorithms']['nysiis'])
    
    print(f"Soundex matches:  {soundex_matches}/{len(results)}")
    print(f"Metaphone matches: {metaphone_matches}/{len(results)}")
    print(f"NYSIIS matches:   {nysiis_matches}/{len(results)}")
    
    return results


if __name__ == "__main__":
    print("="*80)
    print("REVERSE ENGINEERING PHONETIC SIMILARITY ALGORITHMS")
    print("="*80)
    
    # Test with "John"
    original = "John"
    
    print("\n1. ANALYZING ALGORITHM PATTERNS")
    analyze_algorithm_patterns(original)
    
    print("\n\n2. GENERATING VARIATIONS FOR TARGET SCORES")
    print("="*80)
    
    # Generate for different target scores
    for target in [1.0, 0.7, 0.5, 0.3]:
        generate_variations_for_target_score(original, target, max_tries=50)
    
    print("\n\n3. BUILDING PREDICTION MODEL")
    print("="*80)
    
    # Test with known variations
    sample_variations = ["Jon", "Jhon", "Jhn", "Joh", "Jo", "Jahn", "Jehn"]
    build_prediction_model(original, sample_variations)
    
    print("\n" + "="*80)
    print("KEY INSIGHT:")
    print("="*80)
    print("""
The phonetic algorithms work like this:
1. Soundex: Groups similar-sounding letters (e.g., 'John' and 'Jon' both → 'J500')
2. Metaphone: More sophisticated phonetic matching
3. NYSIIS: New York State Identification and Intelligence System

To get a HIGH score (0.8-1.0):
  - Variations must match in ALL selected algorithms
  - Example: 'John' → 'Jon' (both algorithms match)

To get a MEDIUM score (0.6-0.8):
  - Variations must match in SOME algorithms (weighted average)
  - Example: 'John' → 'Jhon' (some algorithms match)

To get a LOW score (0.3-0.6):
  - Variations match in FEW algorithms
  - Example: 'John' → 'Jhn' (few algorithms match)

To get 0.0 score:
  - Variations match in NO algorithms
  - Example: 'John' → 'Jo' (no algorithms match)
    """)

