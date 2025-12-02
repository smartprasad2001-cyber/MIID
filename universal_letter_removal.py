"""
Universal Letter Removal Strategy for Generating Name Variations

IMPORTANT: Validator calculates FIRST and LAST names SEPARATELY!
Both must match the target distribution (20% Light, 60% Medium, 20% Far).

Strategy:
- Light (0.8-1.0): Keep both first and last names original
- Medium (0.6-0.8): Vary both first and last names (remove 1 letter from middle)
- Far (0.3-0.6): Vary both first and last names more (remove 2 letters)
"""

from MIID.validator.reward import calculate_phonetic_similarity


def vary_first_name_medium(first_name: str) -> str:
    """Generate Medium similarity variation for first name (0.6-0.8)."""
    if len(first_name) < 3:
        return first_name
    
    # Strategy 1: Swap second and third letters (works for "John" -> "Jhon" = 0.6417)
    if len(first_name) >= 4:
        var = first_name[0] + first_name[2] + first_name[1] + first_name[3:]
        score = calculate_phonetic_similarity(first_name, var)
        if 0.6 <= score < 0.8:
            return var
    
    # Strategy 2: Swap first two letters (if name is long enough)
    if len(first_name) >= 4:
        var = first_name[1] + first_name[0] + first_name[2:]
        score = calculate_phonetic_similarity(first_name, var)
        if 0.6 <= score < 0.8:
            return var
    
    # Strategy 3: Change vowel
    vowels = ['a', 'e', 'i', 'o', 'u']
    for i, char in enumerate(first_name):
        if char.lower() in vowels:
            for v in vowels:
                if v != char.lower():
                    var = first_name[:i] + v + first_name[i+1:]
                    score = calculate_phonetic_similarity(first_name, var)
                    if 0.6 <= score < 0.8:
                        return var
    
    # Fallback: Swap second and third letters (best default for Medium)
    if len(first_name) >= 4:
        return first_name[0] + first_name[2] + first_name[1] + first_name[3:]
    elif len(first_name) == 3:
        return first_name[1] + first_name[0] + first_name[2]
    
    return first_name


def vary_first_name_far(first_name: str) -> str:
    """Generate Far similarity variation for first name (0.3-0.6)."""
    if len(first_name) < 3:
        return first_name
    
    # Strategy 1: Remove vowel from middle (works for "John" -> "Jhn" = 0.4240)
    vowels = ['a', 'e', 'i', 'o', 'u']
    for i, char in enumerate(first_name):
        if char.lower() in vowels and i > 0 and i < len(first_name) - 1:
            var = first_name[:i] + first_name[i+1:]
            score = calculate_phonetic_similarity(first_name, var)
            if 0.3 <= score < 0.6:
                return var
    
    # Strategy 2: Remove 1 letter from middle
    if len(first_name) >= 4:
        mid_pos = len(first_name) // 2
        var = first_name[:mid_pos] + first_name[mid_pos+1:]
        score = calculate_phonetic_similarity(first_name, var)
        if 0.3 <= score < 0.6:
            return var
    
    # Strategy 3: Remove 2 letters from middle
    if len(first_name) >= 5:
        mid_pos = len(first_name) // 2
        var = first_name[:mid_pos-1] + first_name[mid_pos+1:]
        score = calculate_phonetic_similarity(first_name, var)
        if 0.3 <= score < 0.6:
            return var
    
    # Fallback: Remove vowel from middle
    for i, char in enumerate(first_name):
        if char.lower() in vowels and i > 0 and i < len(first_name) - 1:
            return first_name[:i] + first_name[i+1:]
    
    return first_name


def vary_last_name_medium(last_name: str) -> str:
    """Generate Medium similarity variation for last name (0.6-0.8)."""
    if len(last_name) < 3:
        return last_name
    
    # Strategy 1: Remove 1 letter from middle
    if len(last_name) >= 4:
        mid_pos = len(last_name) // 2
        var = last_name[:mid_pos] + last_name[mid_pos+1:]
        score = calculate_phonetic_similarity(last_name, var)
        if 0.6 <= score < 0.8:
            return var
    
    # Strategy 2: Change vowel
    vowels = ['a', 'e', 'i', 'o', 'u']
    for i, char in enumerate(last_name):
        if char.lower() in vowels:
            for v in vowels:
                if v != char.lower():
                    var = last_name[:i] + v + last_name[i+1:]
                    score = calculate_phonetic_similarity(last_name, var)
                    if 0.6 <= score < 0.8:
                        return var
    
    # Fallback: Remove 1 from end
    if len(last_name) > 1:
        return last_name[:-1]
    
    return last_name


def vary_last_name_far(last_name: str) -> str:
    """Generate Far similarity variation for last name (0.3-0.6)."""
    if len(last_name) < 3:
        return last_name
    
    # Strategy 1: Remove non-adjacent letters (works for "Smith" -> "Smt" = 0.3078)
    # For 5-letter words: remove positions 2 and 4 (e.g., "Smith" -> "Smt")
    if len(last_name) == 5:
        var = last_name[0] + last_name[1] + last_name[3]  # Remove positions 2 and 4
        score = calculate_phonetic_similarity(last_name, var)
        if 0.3 <= score < 0.6:
            return var
    
    # Strategy 2: Remove 2 adjacent letters from middle
    if len(last_name) >= 5:
        mid_pos = len(last_name) // 2
        var = last_name[:mid_pos-1] + last_name[mid_pos+1:]
        score = calculate_phonetic_similarity(last_name, var)
        if 0.3 <= score < 0.6:
            return var
    
    # Strategy 3: Remove 1 letter from middle (some give Far)
    if len(last_name) >= 4:
        mid_pos = len(last_name) // 2
        var = last_name[:mid_pos] + last_name[mid_pos+1:]
        score = calculate_phonetic_similarity(last_name, var)
        if 0.3 <= score < 0.6:
            return var
    
    # Fallback: For 5-letter words, remove positions 2 and 4
    if len(last_name) == 5:
        return last_name[0] + last_name[1] + last_name[3]
    elif len(last_name) >= 4:
        mid_pos = len(last_name) // 2
        return last_name[:mid_pos] + last_name[mid_pos+1:]
    
    return last_name


def generate_light_variation(full_name: str) -> str:
    """
    Generate Light similarity variation (0.8-1.0).
    Strategy: Keep original name as-is.
    
    Args:
        full_name: Original full name (e.g., "John Smith")
    
    Returns:
        Variation with Light similarity (same as original)
    """
    return full_name


def generate_medium_variation(full_name: str) -> str:
    """
    Generate Medium similarity variation (0.6-0.8).
    Strategy: Vary BOTH first and last names to get Medium similarity for both parts.
    
    Args:
        full_name: Original full name (e.g., "John Smith")
    
    Returns:
        Variation with Medium similarity for both first and last names
    """
    parts = full_name.split()
    if len(parts) < 2:
        return full_name
    
    first = parts[0]
    last = parts[1]
    
    # Vary both first and last names
    first_var = vary_first_name_medium(first)
    last_var = vary_last_name_medium(last)
    
    return f"{first_var} {last_var}"


def generate_far_variation(full_name: str) -> str:
    """
    Generate Far similarity variation (0.3-0.6).
    Strategy: Vary BOTH first and last names more to get Far similarity for both parts.
    
    Args:
        full_name: Original full name (e.g., "John Smith")
    
    Returns:
        Variation with Far similarity for both first and last names
    """
    parts = full_name.split()
    if len(parts) < 2:
        return full_name
    
    first = parts[0]
    last = parts[1]
    
    # Vary both first and last names more
    first_var = vary_first_name_far(first)
    last_var = vary_last_name_far(last)
    
    return f"{first_var} {last_var}"


def generate_variations_by_category(full_name: str, light_count: int, medium_count: int, far_count: int) -> list:
    """
    Generate variations for a name with specified distribution.
    
    Args:
        full_name: Original full name
        light_count: Number of Light variations (keep original)
        medium_count: Number of Medium variations
        far_count: Number of Far variations
    
    Returns:
        List of variations
    """
    variations = []
    
    # Light variations (keep original)
    for _ in range(light_count):
        variations.append(generate_light_variation(full_name))
    
    # Medium variations
    for _ in range(medium_count):
        var = generate_medium_variation(full_name)
        variations.append(var)
    
    # Far variations
    for _ in range(far_count):
        var = generate_far_variation(full_name)
        variations.append(var)
    
    return variations


# Example usage
if __name__ == "__main__":
    test_name = "John Smith"
    first_original = "John"
    last_original = "Smith"
    
    print("="*80)
    print("Universal Letter Removal Strategy Test")
    print("="*80)
    print(f"Original: {test_name}")
    print("IMPORTANT: Validator calculates FIRST and LAST names SEPARATELY!")
    print()
    
    # Generate one of each
    light_var = generate_light_variation(test_name)
    medium_var = generate_medium_variation(test_name)
    far_var = generate_far_variation(test_name)
    
    print(f"Light variation:   {light_var}")
    print(f"  Full similarity: {calculate_phonetic_similarity(test_name, light_var):.4f}")
    print()
    
    print(f"Medium variation:  {medium_var}")
    parts_m = medium_var.split()
    first_m = parts_m[0]
    last_m = parts_m[1] if len(parts_m) > 1 else ""
    first_score_m = calculate_phonetic_similarity(first_original, first_m)
    last_score_m = calculate_phonetic_similarity(last_original, last_m)
    print(f"  First: '{first_m}' → {first_score_m:.4f}")
    print(f"  Last:  '{last_m}' → {last_score_m:.4f}")
    print(f"  Full similarity: {calculate_phonetic_similarity(test_name, medium_var):.4f}")
    print()
    
    print(f"Far variation:     {far_var}")
    parts_f = far_var.split()
    first_f = parts_f[0]
    last_f = parts_f[1] if len(parts_f) > 1 else ""
    first_score_f = calculate_phonetic_similarity(first_original, first_f)
    last_score_f = calculate_phonetic_similarity(last_original, last_f)
    print(f"  First: '{first_f}' → {first_score_f:.4f}")
    print(f"  Last:  '{last_f}' → {last_score_f:.4f}")
    print(f"  Full similarity: {calculate_phonetic_similarity(test_name, far_var):.4f}")
    print()
    
    # Generate with distribution (20% Light, 60% Medium, 20% Far for 8 variations)
    print("="*80)
    print("Generating 8 variations (2 Light, 5 Medium, 1 Far):")
    print("="*80)
    variations = generate_variations_by_category(test_name, light_count=2, medium_count=5, far_count=1)
    
    print("\nVariations with First/Last Name Similarity:")
    print("-" * 80)
    for i, var in enumerate(variations, 1):
        parts = var.split()
        first_var = parts[0]
        last_var = parts[1] if len(parts) > 1 else ""
        
        first_score = calculate_phonetic_similarity(first_original, first_var)
        last_score = calculate_phonetic_similarity(last_original, last_var)
        full_score = calculate_phonetic_similarity(test_name, var)
        
        first_cat = "Light" if 0.8 <= first_score <= 1.0 else "Medium" if 0.6 <= first_score < 0.8 else "Far" if 0.3 <= first_score < 0.6 else "Too Low"
        last_cat = "Light" if 0.8 <= last_score <= 1.0 else "Medium" if 0.6 <= last_score < 0.8 else "Far" if 0.3 <= last_score < 0.6 else "Too Low"
        
        print(f"  {i}. {var:20s}")
        print(f"      First: {first_score:.4f} ({first_cat}), Last: {last_score:.4f} ({last_cat})")
        print(f"      Full:  {full_score:.4f}")
        print()

