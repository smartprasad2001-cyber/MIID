"""
Smart Phonetic Generator - Uses Reverse-Engineered Algorithms
Generates variations that target specific similarity score ranges
"""

import jellyfish
import random
from typing import List, Tuple, Dict

def test_all_algorithms(original: str, variation: str) -> Dict[str, bool]:
    """Test variation against all phonetic algorithms"""
    return {
        'soundex': jellyfish.soundex(original) == jellyfish.soundex(variation),
        'metaphone': jellyfish.metaphone(original) == jellyfish.metaphone(variation),
        'nysiis': jellyfish.nysiis(original) == jellyfish.nysiis(variation),
    }

def predict_score(original: str, variation: str) -> float:
    """Predict similarity score using same logic as validator"""
    algorithms = {
        "soundex": lambda x, y: jellyfish.soundex(x) == jellyfish.soundex(y),
        "metaphone": lambda x, y: jellyfish.metaphone(x) == jellyfish.metaphone(y),
        "nysiis": lambda x, y: jellyfish.nysiis(x) == jellyfish.nysiis(y),
    }
    
    random.seed(hash(original) % 10000)
    selected_algorithms = random.sample(list(algorithms.keys()), k=min(3, len(algorithms)))
    
    weights = [random.random() for _ in selected_algorithms]
    total_weight = sum(weights)
    normalized_weights = [w / total_weight for w in weights]
    
    phonetic_score = sum(
        algorithms[algo](original, variation) * weight
        for algo, weight in zip(selected_algorithms, normalized_weights)
    )
    
    return float(phonetic_score)


def generate_candidate_variations(name: str) -> List[Tuple[str, str]]:
    """Generate candidate variations with strategy description"""
    candidates = []
    tested = set()
    
    # Strategy 1: Remove letters from different positions
    for i in range(len(name)):
        var = name[:i] + name[i+1:]
        if var not in tested and len(var) > 0:
            tested.add(var)
            candidates.append((var, f"remove pos {i}"))
    
    # Strategy 2: Swap adjacent letters
    for i in range(len(name) - 1):
        var = name[:i] + name[i+1] + name[i] + name[i+2:]
        if var not in tested:
            tested.add(var)
            candidates.append((var, f"swap {i}-{i+1}"))
    
    # Strategy 3: Change vowels
    vowels = ['a', 'e', 'i', 'o', 'u']
    for i, char in enumerate(name):
        if char.lower() in vowels:
            for v in vowels:
                if v != char.lower():
                    var = name[:i] + v + name[i+1:]
                    if var not in tested:
                        tested.add(var)
                        candidates.append((var, f"vowel {i}:{char}→{v}"))
    
    # Strategy 4: Add letters
    for pos in range(len(name) + 1):
        for letter in ['a', 'e', 'i', 'o', 'u', 'y']:
            var = name[:pos] + letter + name[pos:]
            if var not in tested and len(var) <= len(name) + 2:  # Limit length
                tested.add(var)
                candidates.append((var, f"add '{letter}' at {pos}"))
    
    # Strategy 5: Remove from middle (specific positions)
    if len(name) >= 4:
        mid = len(name) // 2
        var = name[:mid] + name[mid+1:]
        if var not in tested:
            tested.add(var)
            candidates.append((var, f"remove middle pos {mid}"))
    
    # Strategy 6: Remove 2 letters (for Far variations)
    if len(name) >= 5:
        mid = len(name) // 2
        var = name[:mid-1] + name[mid+1:]
        if var not in tested:
            tested.add(var)
            candidates.append((var, f"remove 2 from middle"))
    
    return candidates


def find_variations_for_target(original: str, target_category: str, count: int) -> List[str]:
    """
    Find variations that match target category (Light/Medium/Far)
    
    Args:
        original: Original name
        target_category: 'Light' (0.8-1.0), 'Medium' (0.6-0.8), or 'Far' (0.3-0.6)
        count: Number of variations needed
    
    Returns:
        List of variations matching the target category
    """
    # Define score ranges
    ranges = {
        'Light': (0.8, 1.0),
        'Medium': (0.6, 0.8),
        'Far': (0.3, 0.6)
    }
    
    if target_category not in ranges:
        return []
    
    min_score, max_score = ranges[target_category]
    
    # Generate candidates
    candidates = generate_candidate_variations(original)
    
    # Test each candidate and filter by score
    matches = []
    for var, strategy in candidates:
        score = predict_score(original, var)
        if min_score <= score <= max_score:
            matches.append((var, score, strategy))
    
    # Sort by score (closest to middle of range)
    target_mid = (min_score + max_score) / 2
    matches.sort(key=lambda x: abs(x[1] - target_mid))
    
    # Return unique variations (up to count)
    result = []
    seen = set()
    for var, score, strategy in matches:
        if var not in seen and var != original:  # Don't include original
            result.append(var)
            seen.add(var)
            if len(result) >= count:
                break
    
    # If we don't have enough, pad with original (for Light only)
    if len(result) < count and target_category == 'Light':
        result.extend([original] * (count - len(result)))
    
    return result


def generate_smart_variations(full_name: str, light_count: int, medium_count: int, far_count: int) -> List[str]:
    """
    Generate variations for full name with target distribution.
    Works on first and last names separately.
    """
    parts = full_name.split()
    if len(parts) < 2:
        return [full_name] * (light_count + medium_count + far_count)
    
    first_original = parts[0]
    last_original = parts[1]
    
    # Generate variations for first name
    first_light = find_variations_for_target(first_original, 'Light', light_count)
    first_medium = find_variations_for_target(first_original, 'Medium', medium_count)
    first_far = find_variations_for_target(first_original, 'Far', far_count)
    
    # Generate variations for last name
    last_light = find_variations_for_target(last_original, 'Light', light_count)
    last_medium = find_variations_for_target(last_original, 'Medium', medium_count)
    last_far = find_variations_for_target(last_original, 'Far', far_count)
    
    # Combine first and last name variations
    variations = []
    
    # Light variations (keep original or use found light variations)
    for i in range(light_count):
        first_var = first_light[i] if i < len(first_light) else first_original
        last_var = last_light[i] if i < len(last_light) else last_original
        variations.append(f"{first_var} {last_var}")
    
    # Medium variations
    for i in range(medium_count):
        first_var = first_medium[i] if i < len(first_medium) else first_original
        last_var = last_medium[i] if i < len(last_medium) else last_original
        variations.append(f"{first_var} {last_var}")
    
    # Far variations
    for i in range(far_count):
        first_var = first_far[i] if i < len(first_far) else first_original
        last_var = last_far[i] if i < len(last_far) else last_original
        variations.append(f"{first_var} {last_var}")
    
    return variations


def analyze_variations(original: str, variations: List[str]):
    """Analyze and show predicted scores for variations"""
    print(f"\nAnalyzing variations for '{original}':")
    print("-" * 80)
    
    results = []
    for var in variations:
        score = predict_score(original, var)
        algo_results = test_all_algorithms(original, var)
        matches = sum(1 for v in algo_results.values() if v)
        category = "Light" if 0.8 <= score <= 1.0 else "Medium" if 0.6 <= score < 0.8 else "Far" if 0.3 <= score < 0.6 else "Too Low"
        results.append((var, score, matches, category, algo_results))
    
    # Sort by score
    results.sort(key=lambda x: x[1], reverse=True)
    
    print(f"{'Variation':<20} {'Score':<8} {'Matches':<8} {'Category':<10} {'Algorithms'}")
    print("-" * 80)
    for var, score, matches, category, algo_results in results:
        algo_str = f"S:{int(algo_results['soundex'])} M:{int(algo_results['metaphone'])} N:{int(algo_results['nysiis'])}"
        print(f"{var:<20} {score:<8.4f} {matches}/3      {category:<10} {algo_str}")
    
    return results


if __name__ == "__main__":
    print("="*80)
    print("SMART PHONETIC GENERATOR - Reverse-Engineered Algorithm Predictions")
    print("="*80)
    
    # Test with "John Smith"
    test_name = "John Smith"
    first = "John"
    last = "Smith"
    
    print(f"\nTesting with: {test_name}")
    print(f"Target: 2 Light, 5 Medium, 1 Far (20% Light, 60% Medium, 20% Far)")
    
    # Generate variations
    variations = generate_smart_variations(test_name, light_count=2, medium_count=5, far_count=1)
    
    print(f"\nGenerated {len(variations)} variations:")
    print("-" * 80)
    for i, var in enumerate(variations, 1):
        parts = var.split()
        first_var = parts[0] if len(parts) > 0 else ""
        last_var = parts[1] if len(parts) > 1 else ""
        
        first_score = predict_score(first, first_var)
        last_score = predict_score(last, last_var)
        
        first_cat = "Light" if 0.8 <= first_score <= 1.0 else "Medium" if 0.6 <= first_score < 0.8 else "Far" if 0.3 <= first_score < 0.6 else "Too Low"
        last_cat = "Light" if 0.8 <= last_score <= 1.0 else "Medium" if 0.6 <= last_score < 0.8 else "Far" if 0.3 <= last_score < 0.6 else "Too Low"
        
        print(f"  {i}. {var:20s}")
        print(f"      First: {first_var:10s} → {first_score:.4f} ({first_cat})")
        print(f"      Last:  {last_var:10s} → {last_score:.4f} ({last_cat})")
    
    # Analyze first name variations
    print("\n" + "="*80)
    print("FIRST NAME ANALYSIS:")
    print("="*80)
    first_variations = list(set([v.split()[0] for v in variations if len(v.split()) > 0]))
    analyze_variations(first, first_variations)
    
    # Analyze last name variations
    print("\n" + "="*80)
    print("LAST NAME ANALYSIS:")
    print("="*80)
    last_variations = list(set([v.split()[1] for v in variations if len(v.split()) > 1]))
    analyze_variations(last, last_variations)
    
    # Count distribution
    print("\n" + "="*80)
    print("DISTRIBUTION CHECK:")
    print("="*80)
    
    first_scores = [predict_score(first, v.split()[0]) for v in variations if len(v.split()) > 0]
    last_scores = [predict_score(last, v.split()[1]) for v in variations if len(v.split()) > 1]
    
    first_light = sum(1 for s in first_scores if 0.8 <= s <= 1.0)
    first_medium = sum(1 for s in first_scores if 0.6 <= s < 0.8)
    first_far = sum(1 for s in first_scores if 0.3 <= s < 0.6)
    
    last_light = sum(1 for s in last_scores if 0.8 <= s <= 1.0)
    last_medium = sum(1 for s in last_scores if 0.6 <= s < 0.8)
    last_far = sum(1 for s in last_scores if 0.3 <= s < 0.6)
    
    print(f"First Name: Light {first_light}/8 (target: 2), Medium {first_medium}/8 (target: 5), Far {first_far}/8 (target: 1)")
    print(f"Last Name:  Light {last_light}/8 (target: 2), Medium {last_medium}/8 (target: 5), Far {last_far}/8 (target: 1)")

