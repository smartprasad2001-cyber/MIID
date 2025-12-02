"""
Weight Calculator - Determine weights for any seed/name
"""

import random
from typing import Dict, List, Tuple

def get_weights_for_seed(seed: int) -> Tuple[List[str], List[float]]:
    """
    Get algorithm selection and weights for a given seed.
    
    Args:
        seed: Random seed (0-9999)
    
    Returns:
        Tuple of (selected_algorithms, normalized_weights)
    """
    random.seed(seed)
    
    algorithms = ["soundex", "metaphone", "nysiis"]
    selected = random.sample(algorithms, k=min(3, len(algorithms)))
    
    weights = [random.random() for _ in selected]
    total = sum(weights)
    normalized = [w / total for w in weights]
    
    return selected, normalized


def get_weights_for_name(name: str) -> Tuple[List[str], List[float]]:
    """
    Get algorithm selection and weights for a given name.
    
    Args:
        name: Name to calculate weights for
    
    Returns:
        Tuple of (selected_algorithms, normalized_weights)
    """
    seed = hash(name) % 10000
    return get_weights_for_seed(seed)


def build_weight_lookup_table(max_seed: int = 10000) -> Dict[int, Dict]:
    """
    Build a lookup table for all seeds.
    
    Args:
        max_seed: Maximum seed value (default 10000)
    
    Returns:
        Dictionary mapping seed to {selected, weights}
    """
    lookup = {}
    
    for seed in range(max_seed):
        selected, weights = get_weights_for_seed(seed)
        lookup[seed] = {
            'selected': selected,
            'weights': weights
        }
    
    return lookup


def analyze_weight_distribution(max_seed: int = 10000):
    """Analyze weight distribution across all seeds."""
    print("="*80)
    print("ANALYZING WEIGHT DISTRIBUTION")
    print("="*80)
    print()
    
    # Collect all weights
    all_weights = {'soundex': [], 'metaphone': [], 'nysiis': []}
    
    for seed in range(max_seed):
        selected, weights = get_weights_for_seed(seed)
        for algo, weight in zip(selected, weights):
            all_weights[algo].append(weight)
    
    print("Weight Statistics:")
    print("-" * 80)
    for algo in ['soundex', 'metaphone', 'nysiis']:
        weights = all_weights[algo]
        avg = sum(weights) / len(weights) if weights else 0
        min_w = min(weights) if weights else 0
        max_w = max(weights) if weights else 0
        print(f"{algo:10s}:")
        print(f"  Average: {avg:.6f}")
        print(f"  Min:     {min_w:.6f}")
        print(f"  Max:     {max_w:.6f}")
        print(f"  Count:   {len(weights)}")
        print()


if __name__ == "__main__":
    print("="*80)
    print("WEIGHT CALCULATOR - Determine Weights for Any Seed/Name")
    print("="*80)
    print()
    
    # Test with specific names
    print("1. Testing with specific names:")
    print("-" * 80)
    test_names = ["John", "Mary", "Robert", "Sarah", "Michael"]
    
    for name in test_names:
        selected, weights = get_weights_for_name(name)
        seed = hash(name) % 10000
        
        print(f"\n{name} (seed {seed}):")
        print(f"  Selected: {selected}")
        print(f"  Weights:")
        for algo, weight in zip(selected, weights):
            print(f"    {algo:10s}: {weight:.6f} ({weight*100:.2f}%)")
    
    print()
    print("="*80)
    print("2. Testing with specific seeds:")
    print("-" * 80)
    
    test_seeds = [0, 100, 500, 1000, 5000, 9999]
    for seed in test_seeds:
        selected, weights = get_weights_for_seed(seed)
        print(f"\nSeed {seed:4d}:")
        print(f"  Selected: {selected}")
        print(f"  Weights:")
        for algo, weight in zip(selected, weights):
            print(f"    {algo:10s}: {weight:.6f} ({weight*100:.2f}%)")
    
    print()
    print("="*80)
    print("3. Weight Distribution Analysis:")
    print("="*80)
    print()
    print("Analyzing first 1000 seeds...")
    analyze_weight_distribution(max_seed=1000)
    
    print()
    print("="*80)
    print("KEY INSIGHT")
    print("="*80)
    print()
    print("✅ YES! We can determine weights for ALL seeds!")
    print()
    print("Since there are only 10,000 possible seeds (0-9999),")
    print("we can:")
    print("  1. Calculate weights for any seed instantly")
    print("  2. Build a lookup table for all 10,000 seeds")
    print("  3. Predict weights for any name")
    print("  4. Know which algorithms matter most for each name")
    print()
    print("This gives us complete predictability!")

