"""
Generate Far Similarity Variations (0.3-0.6, targeting ~0.4-0.5)
Uses known weights to find variations where few algorithms match
"""

import jellyfish
import random
from typing import List, Set, Tuple, Dict
from weight_calculator import get_weights_for_name

def get_algorithm_codes(name: str) -> dict:
    """Get codes for all three algorithms."""
    return {
        'soundex': jellyfish.soundex(name),
        'metaphone': jellyfish.metaphone(name),
        'nysiis': jellyfish.nysiis(name)
    }

def calculate_score_with_weights(original: str, variation: str, selected_algorithms: List[str], weights: List[float]) -> float:
    """
    Calculate similarity score using specific algorithms and weights.
    
    Args:
        original: Original name
        variation: Variation to test
        selected_algorithms: List of algorithm names (e.g., ['soundex', 'metaphone', 'nysiis'])
        weights: List of weights for each algorithm
    
    Returns:
        Similarity score (0.0-1.0)
    """
    algorithms = {
        "soundex": lambda x, y: jellyfish.soundex(x) == jellyfish.soundex(y),
        "metaphone": lambda x, y: jellyfish.metaphone(x) == jellyfish.metaphone(y),
        "nysiis": lambda x, y: jellyfish.nysiis(x) == jellyfish.nysiis(y),
    }
    
    score = sum(
        algorithms[algo](original, variation) * weight
        for algo, weight in zip(selected_algorithms, weights)
    )
    
    return float(score)

def get_match_pattern(original: str, variation: str, selected_algorithms: List[str]) -> Dict[str, bool]:
    """Get which algorithms match for a variation."""
    algorithms = {
        "soundex": lambda x, y: jellyfish.soundex(x) == jellyfish.soundex(y),
        "metaphone": lambda x, y: jellyfish.metaphone(x) == jellyfish.metaphone(y),
        "nysiis": lambda x, y: jellyfish.nysiis(x) == jellyfish.nysiis(y),
    }
    
    return {
        algo: algorithms[algo](original, variation)
        for algo in selected_algorithms
    }

def generate_candidates(original: str) -> List[str]:
    """Generate candidate variations using multiple strategies (focused on more aggressive changes for Far similarity)."""
    candidates = []
    tested: Set[str] = set()
    vowels = ['a', 'e', 'i', 'o', 'u']
    common_letters = ['n', 'h', 'y', 'r', 'l', 'm', 'd', 't', 's']
    
    # Strategy 1: Remove letters (more aggressive for Far)
    for i in range(len(original)):
        var = original[:i] + original[i+1:]
        if var not in tested and len(var) > 0:
            tested.add(var)
            candidates.append(var)
    
    # Strategy 2: Remove multiple letters (for Far similarity)
    if len(original) > 3:
        for i in range(len(original)):
            for j in range(i+1, len(original)):
                var = original[:i] + original[i+1:j] + original[j+1:]
                if var not in tested and len(var) > 0:
                    tested.add(var)
                    candidates.append(var)
    
    # Strategy 3: Remove 3 letters (very aggressive)
    if len(original) > 4:
        for i in range(len(original)):
            for j in range(i+1, len(original)):
                for k in range(j+1, len(original)):
                    var = original[:i] + original[i+1:j] + original[j+1:k] + original[k+1:]
                    if var not in tested and len(var) > 0:
                        tested.add(var)
                        candidates.append(var)
    
    # Strategy 4: Change vowels (more aggressive)
    for i, char in enumerate(original):
        if char.lower() in vowels:
            for v in vowels:
                if v != char.lower():
                    var = original[:i] + v + original[i+1:]
                    if var not in tested:
                        tested.add(var)
                        candidates.append(var)
    
    # Strategy 5: Change consonants (more aggressive)
    consonants = 'bcdfghjklmnpqrstvwxyz'
    for i, char in enumerate(original):
        if char.lower() in consonants:
            for c in consonants:
                if c != char.lower():
                    var = original[:i] + c + original[i+1:]
                    if var not in tested and len(var) == len(original):
                        tested.add(var)
                        candidates.append(var)
    
    # Strategy 6: Swap non-adjacent letters
    for i in range(len(original)):
        for j in range(i+2, len(original)):
            var = original[:i] + original[j] + original[i+1:j] + original[i] + original[j+1:]
            if var not in tested:
                tested.add(var)
                candidates.append(var)
    
    # Strategy 7: Add letters in middle (can break phonetic codes)
    for pos in range(1, len(original)):
        for letter in common_letters:
            var = original[:pos] + letter + original[pos:]
            if var not in tested and len(var) <= len(original) + 2:
                tested.add(var)
                candidates.append(var)
    
    # Strategy 8: Change multiple letters
    if len(original) > 2:
        for i in range(len(original)):
            for j in range(i+1, len(original)):
                # Change both positions
                for c1 in 'abcdefghijklmnopqrstuvwxyz':
                    for c2 in 'abcdefghijklmnopqrstuvwxyz':
                        var = original[:i] + c1 + original[i+1:j] + c2 + original[j+1:]
                        if var not in tested and len(var) == len(original):
                            tested.add(var)
                            candidates.append(var)
                            if len(candidates) > 10000:  # Limit to avoid too many
                                break
                    if len(candidates) > 10000:
                        break
                if len(candidates) > 10000:
                    break
    
    return candidates

def find_far_variations(original: str, target_score: float = 0.45, count: int = 15, tolerance: float = 0.15) -> List[Tuple[str, float, Dict[str, bool]]]:
    """
    Find variations that score in Far range (0.3-0.6, targeting ~0.4-0.5).
    
    Args:
        original: Original name
        target_score: Target score (default 0.45)
        count: Number of variations needed
        tolerance: Acceptable range around target (default 0.15, so 0.3-0.6)
    
    Returns:
        List of (variation, score, match_pattern) tuples
    """
    # Get weights for this name
    selected_algorithms, weights = get_weights_for_name(original)
    
    print(f"Weights for '{original}':")
    for algo, weight in zip(selected_algorithms, weights):
        print(f"  {algo:10s}: {weight:.4f} ({weight*100:.1f}%)")
    print()
    
    # Generate candidates
    candidates = generate_candidates(original)
    
    # Test candidates and find ones in Far range
    far_variations = []
    min_score = target_score - tolerance
    max_score = target_score + tolerance
    
    for var in candidates:
        if var == original:
            continue
        
        score = calculate_score_with_weights(original, var, selected_algorithms, weights)
        match_pattern = get_match_pattern(original, var, selected_algorithms)
        
        if min_score <= score <= max_score:
            far_variations.append((var, score, match_pattern))
    
    # Sort by closeness to target
    far_variations.sort(key=lambda x: abs(x[1] - target_score))
    
    # Remove duplicates
    result = []
    seen = set()
    for var, score, pattern in far_variations:
        if var not in seen:
            result.append((var, score, pattern))
            seen.add(var)
            if len(result) >= count:
                break
    
    return result

def display_results(original: str, variations: List[Tuple[str, float, Dict[str, bool]]]):
    """Display results with detailed information."""
    selected_algorithms, weights = get_weights_for_name(original)
    target_codes = get_algorithm_codes(original)
    
    print("="*80)
    print(f"FAR VARIATIONS FOR: '{original}'")
    print("="*80)
    print()
    print(f"Target codes:")
    print(f"  Soundex:  {target_codes['soundex']}")
    print(f"  Metaphone: {target_codes['metaphone']}")
    print(f"  NYSIIS:   {target_codes['nysiis']}")
    print()
    print(f"Algorithm weights:")
    for algo, weight in zip(selected_algorithms, weights):
        print(f"  {algo:10s}: {weight:.4f} ({weight*100:.1f}%)")
    print()
    print(f"Found {len(variations)} Far variations (0.3-0.6 range):")
    print("-" * 80)
    print()
    
    for i, (var, score, pattern) in enumerate(variations, 1):
        var_codes = get_algorithm_codes(var)
        
        print(f"{i:2d}. '{var:25s}' → Score: {score:.4f} (Far)")
        print(f"     Match pattern:")
        for algo in selected_algorithms:
            matches = pattern[algo]
            original_code = target_codes[algo]
            var_code = var_codes[algo]
            weight = weights[selected_algorithms.index(algo)]
            contribution = weight if matches else 0.0
            
            status = "✓" if matches else "✗"
            print(f"       {algo:10s}: {status} (contributes {contribution:.4f}) "
                  f"[{original_code} vs {var_code}]")
        
        # Show score breakdown
        contributions = [weights[i] if pattern[algo] else 0.0 
                        for i, algo in enumerate(selected_algorithms)]
        print(f"     Score breakdown: {' + '.join(f'{c:.4f}' for c in contributions)} = {score:.4f}")
        print()
    
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print()
    print(f"✅ Generated {len(variations)} Far variations for '{original}'")
    print("✅ All variations score in 0.3-0.6 range (Far similarity)")
    print("✅ Score is calculated as weighted sum of matching algorithms")
    print("✅ Far variations typically match 0-1 algorithms (fewer matches = lower score)")
    print()

if __name__ == "__main__":
    print("="*80)
    print("GENERATING FAR SIMILARITY VARIATIONS (0.3-0.6)")
    print("="*80)
    print()
    
    # Test with different words
    test_words = ["John", "Christopher", "Elizabeth", "Alexander"]
    
    for word in test_words:
        print("\n" + "="*80)
        variations = find_far_variations(word, target_score=0.45, count=15, tolerance=0.15)
        
        if len(variations) >= 10:
            display_results(word, variations[:15])
            break
        else:
            print(f"⚠️  '{word}': Found {len(variations)} Far variations (need 15)")
    
    # Test with a specific word
    print("\n" + "="*80)
    print("TEST WITH SPECIFIC WORD")
    print("="*80)
    print()
    
    test_word = "John"
    variations = find_far_variations(test_word, target_score=0.45, count=15, tolerance=0.15)
    display_results(test_word, variations[:15])

