"""
Strategy-Based Generator: Cycles through all strategies systematically
Ensures all strategies are used before exhausting limits
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'MIID', 'validator'))

import jellyfish
from typing import List, Set, Tuple, Dict, Callable
from reward import calculate_phonetic_similarity

def get_algorithm_codes(name: str) -> dict:
    """Get codes for all three algorithms."""
    return {
        'soundex': jellyfish.soundex(name),
        'metaphone': jellyfish.metaphone(name),
        'nysiis': jellyfish.nysiis(name)
    }

# Define all strategies as separate functions
def strategy_remove_single_letter(word: str, tested: Set[str], candidates: List[str], original: str) -> List[str]:
    """Strategy 1: Remove single letters"""
    new_vars = []
    for i in range(len(word)):
        var = word[:i] + word[i+1:]
        if var and var != original and var not in tested and len(var) > 0:
            if len(var) >= 1 and len(var) <= len(original) + 5:
                tested.add(var)
                candidates.append(var)
                new_vars.append(var)
    return new_vars

def strategy_add_vowels(word: str, tested: Set[str], candidates: List[str], original: str) -> List[str]:
    """Strategy 2: Add vowels at different positions"""
    vowels = ['a', 'e', 'i', 'o', 'u', 'y']
    new_vars = []
    for pos in range(len(word) + 1):
        for v in vowels:
            var = word[:pos] + v + word[pos:]
            if var and var != original and var not in tested and len(var) > 0:
                if len(var) >= 1 and len(var) <= len(original) + 5:
                    tested.add(var)
                    candidates.append(var)
                    new_vars.append(var)
    return new_vars

def strategy_change_vowels(word: str, tested: Set[str], candidates: List[str], original: str) -> List[str]:
    """Strategy 3: Change vowels"""
    vowels = ['a', 'e', 'i', 'o', 'u', 'y']
    new_vars = []
    for i, char in enumerate(word):
        if char.lower() in vowels:
            for v in vowels:
                if v != char.lower():
                    var = word[:i] + v + word[i+1:]
                    if var and var != original and var not in tested and len(var) > 0:
                        if len(var) >= 1 and len(var) <= len(original) + 5:
                            tested.add(var)
                            candidates.append(var)
                            new_vars.append(var)
    return new_vars

def strategy_change_consonants(word: str, tested: Set[str], candidates: List[str], original: str) -> List[str]:
    """Strategy 4: Change consonants"""
    consonants = 'bcdfghjklmnpqrstvwxyz'
    new_vars = []
    for i, char in enumerate(word):
        if char.lower() in consonants:
            for c in consonants:
                if c != char.lower():
                    var = word[:i] + c + word[i+1:]
                    if var and var != original and var not in tested and len(var) > 0:
                        if len(var) >= 1 and len(var) <= len(original) + 5:
                            tested.add(var)
                            candidates.append(var)
                            new_vars.append(var)
    return new_vars

def strategy_swap_adjacent(word: str, tested: Set[str], candidates: List[str], original: str) -> List[str]:
    """Strategy 5: Swap adjacent letters"""
    new_vars = []
    for i in range(len(word) - 1):
        var = word[:i] + word[i+1] + word[i] + word[i+2:]
        if var and var != original and var not in tested and len(var) > 0:
            if len(var) >= 1 and len(var) <= len(original) + 5:
                tested.add(var)
                candidates.append(var)
                new_vars.append(var)
    return new_vars

def strategy_swap_non_adjacent(word: str, tested: Set[str], candidates: List[str], original: str) -> List[str]:
    """Strategy 6: Swap non-adjacent letters"""
    new_vars = []
    for i in range(len(word)):
        for j in range(i+2, len(word)):
            var = word[:i] + word[j] + word[i+1:j] + word[i] + word[j+1:]
            if var and var != original and var not in tested and len(var) > 0:
                if len(var) >= 1 and len(var) <= len(original) + 5:
                    tested.add(var)
                    candidates.append(var)
                    new_vars.append(var)
    return new_vars

def strategy_add_letters(word: str, tested: Set[str], candidates: List[str], original: str) -> List[str]:
    """Strategy 7: Add letters at all positions"""
    all_letters = 'abcdefghijklmnopqrstuvwxyz'
    new_vars = []
    for pos in range(len(word) + 1):
        for letter in all_letters:
            var = word[:pos] + letter + word[pos:]
            if var and var != original and var not in tested and len(var) > 0:
                if len(var) >= 1 and len(var) <= len(original) + 5:
                    tested.add(var)
                    candidates.append(var)
                    new_vars.append(var)
    return new_vars

def strategy_remove_multiple(word: str, tested: Set[str], candidates: List[str], original: str) -> List[str]:
    """Strategy 8: Remove multiple letters (2 letters)"""
    new_vars = []
    if len(word) > 3:
        for i in range(len(word)):
            for j in range(i+1, len(word)):
                var = word[:i] + word[i+1:j] + word[j+1:]
                if var and var != original and var not in tested and len(var) > 0:
                    if len(var) >= 1 and len(var) <= len(original) + 5:
                        tested.add(var)
                        candidates.append(var)
                        new_vars.append(var)
    return new_vars

def strategy_remove_three(word: str, tested: Set[str], candidates: List[str], original: str) -> List[str]:
    """Strategy 9: Remove 3 letters"""
    new_vars = []
    if len(word) > 4:
        for i in range(len(word)):
            for j in range(i+1, len(word)):
                for k in range(j+1, len(word)):
                    var = word[:i] + word[i+1:j] + word[j+1:k] + word[k+1:]
                    if var and var != original and var not in tested and len(var) > 0:
                        if len(var) >= 1 and len(var) <= len(original) + 5:
                            tested.add(var)
                            candidates.append(var)
                            new_vars.append(var)
    return new_vars

def strategy_double_letters(word: str, tested: Set[str], candidates: List[str], original: str) -> List[str]:
    """Strategy 10: Double letters"""
    new_vars = []
    for i in range(len(word)):
        var = word[:i] + word[i] + word[i:]
        if var and var != original and var not in tested and len(var) > 0:
            if len(var) >= 1 and len(var) <= len(original) + 5:
                tested.add(var)
                candidates.append(var)
                new_vars.append(var)
    return new_vars

def strategy_insert_vowel_combos(word: str, tested: Set[str], candidates: List[str], original: str) -> List[str]:
    """Strategy 11: Insert vowel combinations"""
    vowel_combos = ['ae', 'ai', 'ao', 'au', 'ea', 'ei', 'eo', 'eu', 'ia', 'ie', 'io', 'iu', 'oa', 'oe', 'oi', 'ou', 'ua', 'ue', 'ui', 'uo']
    new_vars = []
    for pos in range(len(word) + 1):
        for combo in vowel_combos:
            var = word[:pos] + combo + word[pos:]
            if var and var != original and var not in tested and len(var) > 0:
                if len(var) >= 1 and len(var) <= len(original) + 5:
                    tested.add(var)
                    candidates.append(var)
                    new_vars.append(var)
    return new_vars

def strategy_insert_letter_pairs(word: str, tested: Set[str], candidates: List[str], original: str) -> List[str]:
    """Strategy 12: Insert letter pairs"""
    all_letters = 'abcdefghijklmnopqrstuvwxyz'
    new_vars = []
    for pos in range(len(word) + 1):
        for letter1 in all_letters[:13]:  # Limit to first half to reduce combinations
            for letter2 in all_letters[:13]:
                var = word[:pos] + letter1 + letter2 + word[pos:]
                if var and var != original and var not in tested and len(var) > 0:
                    if len(var) >= 1 and len(var) <= len(original) + 5:
                        tested.add(var)
                        candidates.append(var)
                        new_vars.append(var)
    return new_vars

def strategy_replace_letters(word: str, tested: Set[str], candidates: List[str], original: str) -> List[str]:
    """Strategy 13: Replace with all possible letters"""
    all_letters = 'abcdefghijklmnopqrstuvwxyz'
    new_vars = []
    for i in range(len(word)):
        for letter in all_letters:
            if letter != word[i].lower():
                var = word[:i] + letter + word[i+1:]
                if var and var != original and var not in tested and len(var) > 0:
                    if len(var) >= 1 and len(var) <= len(original) + 5:
                        tested.add(var)
                        candidates.append(var)
                        new_vars.append(var)
    return new_vars

def strategy_phonetic_replace(word: str, tested: Set[str], candidates: List[str], original: str) -> List[str]:
    """Strategy 14: Replace with phonetic equivalents"""
    phonetic_equivalents = {
        'a': ['e', 'i', 'o'], 'e': ['a', 'i', 'y'], 'i': ['e', 'y', 'a'],
        'o': ['a', 'u'], 'u': ['o', 'a'], 'y': ['i', 'e'],
        'b': ['p', 'v'], 'p': ['b', 'f'], 'v': ['b', 'f', 'w'],
        'd': ['t'], 't': ['d'], 'g': ['k', 'j'], 'k': ['g', 'c'],
        's': ['z', 'c'], 'z': ['s', 'x'], 'c': ['s', 'k'],
        'f': ['v', 'ph'], 'm': ['n'], 'n': ['m'],
        'l': ['r'], 'r': ['l'], 'w': ['v'], 'h': ['']
    }
    new_vars = []
    for i, char in enumerate(word):
        base_char = char.lower()
        if base_char in phonetic_equivalents:
            for equiv in phonetic_equivalents[base_char]:
                if equiv:  # Skip empty
                    var = word[:i] + equiv + word[i+1:]
                    if var and var != original and var not in tested and len(var) > 0:
                        if len(var) >= 1 and len(var) <= len(original) + 5:
                            tested.add(var)
                            candidates.append(var)
                            new_vars.append(var)
    return new_vars

def strategy_duplicate_letters(word: str, tested: Set[str], candidates: List[str], original: str) -> List[str]:
    """Strategy 15: Duplicate letters at positions"""
    new_vars = []
    for i in range(len(word)):
        var = word[:i] + word[i] + word[i] + word[i+1:]
        if var and var != original and var not in tested and len(var) > 0:
            if len(var) >= 1 and len(var) <= len(original) + 5:
                tested.add(var)
                candidates.append(var)
                new_vars.append(var)
    return new_vars

def strategy_remove_duplicates(word: str, tested: Set[str], candidates: List[str], original: str) -> List[str]:
    """Strategy 16: Remove duplicate letters"""
    new_vars = []
    for i in range(len(word) - 1):
        if word[i] == word[i+1]:
            var = word[:i] + word[i+1:]
            if var and var != original and var not in tested and len(var) > 0:
                if len(var) >= 1 and len(var) <= len(original) + 5:
                    tested.add(var)
                    candidates.append(var)
                    new_vars.append(var)
    return new_vars

def strategy_swap_rotate(word: str, tested: Set[str], candidates: List[str], original: str) -> List[str]:
    """Strategy 17: Swap 3 letters (rotate)"""
    new_vars = []
    if len(word) >= 3:
        for i in range(len(word) - 2):
            var = word[:i] + word[i+1] + word[i+2] + word[i] + word[i+3:]
            if var and var != original and var not in tested and len(var) > 0:
                if len(var) >= 1 and len(var) <= len(original) + 5:
                    tested.add(var)
                    candidates.append(var)
                    new_vars.append(var)
    return new_vars

def strategy_reverse_substring(word: str, tested: Set[str], candidates: List[str], original: str) -> List[str]:
    """Strategy 18: Reverse substring"""
    new_vars = []
    for i in range(len(word) - 1):
        for j in range(i+2, min(i+5, len(word)+1)):
            var = word[:i] + word[i:j][::-1] + word[j:]
            if var and var != original and var not in tested and len(var) > 0:
                if len(var) >= 1 and len(var) <= len(original) + 5:
                    tested.add(var)
                    candidates.append(var)
                    new_vars.append(var)
    return new_vars

def strategy_insert_common_pairs(word: str, tested: Set[str], candidates: List[str], original: str) -> List[str]:
    """Strategy 19: Insert common letter pairs"""
    common_pairs = ['th', 'sh', 'ch', 'ph', 'ck', 'ng', 'st', 'tr', 'br', 'cr', 'dr', 'fr', 'gr', 'pr']
    new_vars = []
    for pos in range(len(word) + 1):
        for pair in common_pairs:
            var = word[:pos] + pair + word[pos:]
            if var and var != original and var not in tested and len(var) > 0:
                if len(var) >= 1 and len(var) <= len(original) + 5:
                    tested.add(var)
                    candidates.append(var)
                    new_vars.append(var)
    return new_vars

def strategy_add_prefix(word: str, tested: Set[str], candidates: List[str], original: str) -> List[str]:
    """Strategy 20: Add prefix"""
    common_prefixes = ['a', 'e', 'i', 'o', 'u', 're', 'un', 'in', 'de', 'pre']
    new_vars = []
    for prefix in common_prefixes:
        var = prefix + word
        if var and var != original and var not in tested and len(var) > 0:
            if len(var) >= 1 and len(var) <= len(original) + 5:
                tested.add(var)
                candidates.append(var)
                new_vars.append(var)
    return new_vars

def strategy_add_suffix(word: str, tested: Set[str], candidates: List[str], original: str) -> List[str]:
    """Strategy 21: Add suffix"""
    common_suffixes = ['a', 'e', 'i', 'o', 'u', 's', 'es', 'ed', 'er', 'ing', 'ly']
    new_vars = []
    for suffix in common_suffixes:
        var = word + suffix
        if var and var != original and var not in tested and len(var) > 0:
            if len(var) >= 1 and len(var) <= len(original) + 5:
                tested.add(var)
                candidates.append(var)
                new_vars.append(var)
    return new_vars

def strategy_split_insert(word: str, tested: Set[str], candidates: List[str], original: str) -> List[str]:
    """Strategy 22: Split and insert letter"""
    new_vars = []
    if len(word) > 2:
        mid = len(word) // 2
        for letter in 'aeiou':  # Limit to vowels
            var = word[:mid] + letter + word[mid:]
            if var and var != original and var not in tested and len(var) > 0:
                if len(var) >= 1 and len(var) <= len(original) + 5:
                    tested.add(var)
                    candidates.append(var)
                    new_vars.append(var)
    return new_vars

def strategy_move_letter(word: str, tested: Set[str], candidates: List[str], original: str) -> List[str]:
    """Strategy 23: Move letter to different position"""
    new_vars = []
    for i in range(len(word)):
        for j in range(len(word) + 1):
            if j != i and j != i + 1:
                var = word[:i] + word[i+1:j] + word[i] + word[j:]
                if var and var != original and var not in tested and len(var) > 0:
                    if len(var) >= 1 and len(var) <= len(original) + 5:
                        tested.add(var)
                        candidates.append(var)
                        new_vars.append(var)
    return new_vars

def strategy_replace_double(word: str, tested: Set[str], candidates: List[str], original: str) -> List[str]:
    """Strategy 24: Replace with double letter"""
    vowels = 'aeiou'
    new_vars = []
    for i in range(len(word)):
        for letter in vowels:
            var = word[:i] + letter + letter + word[i+1:]
            if var and var != original and var not in tested and len(var) > 0:
                if len(var) >= 1 and len(var) <= len(original) + 5:
                    tested.add(var)
                    candidates.append(var)
                    new_vars.append(var)
    return new_vars

def strategy_cyclic_shift(word: str, tested: Set[str], candidates: List[str], original: str) -> List[str]:
    """Strategy 25: Cyclic shift (rotate letters)"""
    new_vars = []
    if len(word) > 1:
        for shift in range(1, min(4, len(word))):
            var = word[shift:] + word[:shift]
            if var and var != original and var not in tested and len(var) > 0:
                if len(var) >= 1 and len(var) <= len(original) + 5:
                    tested.add(var)
                    candidates.append(var)
                    new_vars.append(var)
    return new_vars

# List of all strategies
ALL_STRATEGIES = [
    strategy_remove_single_letter,
    strategy_add_vowels,
    strategy_change_vowels,
    strategy_change_consonants,
    strategy_swap_adjacent,
    strategy_swap_non_adjacent,
    strategy_add_letters,
    strategy_remove_multiple,
    strategy_remove_three,
    strategy_double_letters,
    strategy_insert_vowel_combos,
    strategy_insert_letter_pairs,
    strategy_replace_letters,
    strategy_phonetic_replace,
    strategy_duplicate_letters,
    strategy_remove_duplicates,
    strategy_swap_rotate,
    strategy_reverse_substring,
    strategy_insert_common_pairs,
    strategy_add_prefix,
    strategy_add_suffix,
    strategy_split_insert,
    strategy_move_letter,
    strategy_replace_double,
    strategy_cyclic_shift,
]

def generate_candidates_strategy_based(
    original: str,
    target_count: int,
    target_score_range: Tuple[float, float],
    max_total_candidates: int = 500000,
    max_depth: int = 3,
    verbose: bool = False
) -> List[str]:
    """
    Generate candidates by cycling through all strategies systematically.
    
    Args:
        original: Original word
        target_count: Number of variations needed
        target_score_range: (min_score, max_score) for filtering
        max_total_candidates: Maximum total candidates to check
        max_depth: Maximum recursion depth per strategy
        verbose: Print progress
    """
    candidates = []
    tested: Set[str] = set()
    min_score, max_score = target_score_range
    
    # Adaptive limits based on name length
    name_length = len(original)
    if name_length >= 12:
        max_total_candidates = 1000000
        max_depth = 5
    elif name_length >= 8:
        max_total_candidates = 750000
        max_depth = 4
    else:
        max_total_candidates = 500000
        max_depth = 4
    
    total_checked = 0
    strategy_index = 0
    round_num = 0
    
    # Continue until we have enough or exhaust all strategies
    # We'll go through ALL strategies multiple times if needed
    max_rounds = len(ALL_STRATEGIES) * 3  # Go through all strategies 3 times
    
    while len(candidates) < target_count and total_checked < max_total_candidates and round_num < max_rounds:
        round_num += 1
        strategy = ALL_STRATEGIES[strategy_index]
        
        if verbose:
            print(f"  Round {round_num}, Strategy {strategy_index + 1}/{len(ALL_STRATEGIES)}: {strategy.__name__}")
        
        # Apply strategy with recursion
        def apply_strategy_recursive(word: str, depth: int):
            nonlocal total_checked, candidates
            
            if depth >= max_depth or total_checked >= max_total_candidates:
                return
            
            # Apply current strategy
            temp_candidates = []
            new_vars = strategy(word, tested, temp_candidates, original)
            
            # Score and filter new variations
            for var in new_vars:
                if total_checked >= max_total_candidates:
                    break
                
                total_checked += 1
                score = calculate_phonetic_similarity(original, var)
                
                if min_score <= score <= max_score:
                    if var not in candidates:
                        candidates.append(var)
            
            # Recursively apply to new variations (limited recursion)
            if depth < max_depth - 1 and len(candidates) < target_count:
                # Process more variations per strategy for better coverage
                recursion_limit = 20 if name_length < 8 else (30 if name_length < 12 else 40)
                for var in new_vars[:recursion_limit]:
                    if len(candidates) >= target_count or total_checked >= max_total_candidates:
                        break
                    apply_strategy_recursive(var, depth + 1)
        
        # Apply strategy starting from original word
        apply_strategy_recursive(original, 0)
        
        if verbose:
            print(f"    Found {len(candidates)}/{target_count} candidates, checked {total_checked}/{max_total_candidates}")
        
        # Move to next strategy (always cycle through all)
        strategy_index = (strategy_index + 1) % len(ALL_STRATEGIES)
        
        # If we've completed one full cycle and have enough, we can stop
        if strategy_index == 0 and len(candidates) >= target_count:
            if verbose:
                print(f"  Completed full cycle, found {len(candidates)}/{target_count}")
            break
    
    return candidates[:target_count]

def generate_light_variations_strategy_based(original: str, count: int, verbose: bool = False) -> List[str]:
    """Generate Light variations (score 1.0) using strategy-based approach."""
    target_codes = get_algorithm_codes(original)
    perfect_matches = []
    tested: Set[str] = set()
    
    strategy_index = 0
    round_num = 0
    max_total_checked = 300000 if len(original) < 8 else (450000 if len(original) < 12 else 600000)
    max_rounds = len(ALL_STRATEGIES) * 3  # Go through all strategies 3 times
    total_checked = 0
    
    while len(perfect_matches) < count and total_checked < max_total_checked and round_num < max_rounds:
        round_num += 1
        strategy = ALL_STRATEGIES[strategy_index]
        
        if verbose:
            print(f"  Round {round_num}, Strategy {strategy_index + 1}/{len(ALL_STRATEGIES)}: {strategy.__name__}")
        
        # Apply strategy with recursion for Light variations
        def apply_light_strategy_recursive(word: str, depth: int):
            nonlocal total_checked, perfect_matches
            
            if depth >= 3 or total_checked >= max_total_checked:  # Max depth 3 for Light
                return
            
            temp_candidates = []
            new_vars = strategy(word, tested, temp_candidates, original)
            
            for var in new_vars:
                if total_checked >= max_total_checked:
                    break
                
                total_checked += 1
                var_codes = get_algorithm_codes(var)
                
                if (var_codes['soundex'] == target_codes['soundex'] and
                    var_codes['metaphone'] == target_codes['metaphone'] and
                    var_codes['nysiis'] == target_codes['nysiis']):
                    if var not in perfect_matches:
                        perfect_matches.append(var)
                        if len(perfect_matches) >= count:
                            return
                
                # Recursively apply to new variations
                if depth < 2 and len(perfect_matches) < count:
                    apply_light_strategy_recursive(var, depth + 1)
        
        apply_light_strategy_recursive(original, 0)
        
        if verbose:
            print(f"    Found {len(perfect_matches)}/{count} perfect matches, checked {total_checked}/{max_total_checked}")
        
        # Always move to next strategy (cycle through all)
        strategy_index = (strategy_index + 1) % len(ALL_STRATEGIES)
        
        # If we've completed one full cycle and have enough, we can stop
        if strategy_index == 0 and len(perfect_matches) >= count:
            if verbose:
                print(f"  Completed full cycle, found {len(perfect_matches)}/{count}")
            break
    
    return perfect_matches[:count]

def generate_medium_variations_strategy_based(original: str, count: int, verbose: bool = False) -> List[str]:
    """Generate Medium variations (0.6-0.79) using strategy-based approach."""
    return generate_candidates_strategy_based(
        original, count, (0.6, 0.79), verbose=verbose
    )

def generate_far_variations_strategy_based(original: str, count: int, verbose: bool = False) -> List[str]:
    """Generate Far variations (0.3-0.59) using strategy-based approach."""
    return generate_candidates_strategy_based(
        original, count, (0.3, 0.59), verbose=verbose
    )

def generate_full_name_variations_strategy_based(
    full_name: str,
    light_count: int,
    medium_count: int,
    far_count: int,
    verbose: bool = True
) -> List[str]:
    """Generate variations for full name using strategy-based approach."""
    parts = full_name.split()
    if len(parts) < 2:
        first_name = full_name
        last_name = None
    else:
        first_name = parts[0]
        last_name = parts[-1]
    
    if verbose:
        print(f"Generating variations for '{full_name}':")
        print(f"  First: '{first_name}', Last: '{last_name}'")
    
    # Generate for first name
    first_light = generate_light_variations_strategy_based(first_name, light_count, verbose=verbose)
    first_medium = generate_medium_variations_strategy_based(first_name, medium_count, verbose=verbose)
    first_far = generate_far_variations_strategy_based(first_name, far_count, verbose=verbose)
    
    # Generate for last name
    if last_name:
        last_light = generate_light_variations_strategy_based(last_name, light_count, verbose=verbose)
        last_medium = generate_medium_variations_strategy_based(last_name, medium_count, verbose=verbose)
        last_far = generate_far_variations_strategy_based(last_name, far_count, verbose=verbose)
    else:
        last_light = [first_name] * light_count
        last_medium = [first_name] * medium_count
        last_far = [first_name] * far_count
    
    # Combine
    variations = []
    for i in range(light_count):
        if i < len(first_light) and i < len(last_light):
            variations.append(f"{first_light[i]} {last_light[i]}")
    for i in range(medium_count):
        if i < len(first_medium) and i < len(last_medium):
            variations.append(f"{first_medium[i]} {last_medium[i]}")
    for i in range(far_count):
        if i < len(first_far) and i < len(last_far):
            variations.append(f"{first_far[i]} {last_far[i]}")
    
    return variations

if __name__ == "__main__":
    # Test with a single name
    test_name = "Sebastian Martinez"
    variations = generate_full_name_variations_strategy_based(
        test_name,
        light_count=2,
        medium_count=6,
        far_count=2,
        verbose=True
    )
    print(f"\nGenerated {len(variations)} variations:")
    for i, var in enumerate(variations, 1):
        print(f"  {i}. {var}")

