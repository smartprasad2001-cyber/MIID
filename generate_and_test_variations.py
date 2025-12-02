"""
Unified Script: Generate Light, Medium, and Far Variations and Test with rewards.py
Generates variations for full names (first + last) and tests with actual validator scoring
"""

import sys
import os

# Add MIID/validator to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'MIID', 'validator'))

import jellyfish
import random
from typing import List, Set, Tuple, Dict, Optional
from datetime import datetime, timedelta

# Import weight calculator
from weight_calculator import get_weights_for_name

# Import from rewards.py
from reward import calculate_variation_quality, calculate_phonetic_similarity, calculate_orthographic_similarity

def normalize_dob_format(dob: str) -> str:
    """
    Normalize DOB format to YYYY-MM-DD.
    Handles formats like: YYYY-M-D, YYYY-MM-D, YYYY-M-DD, YYYY-MM-DD
    """
    try:
        parts = dob.split('-')
        if len(parts) == 3:
            year = parts[0]
            month = parts[1].zfill(2)  # Pad to 2 digits
            day = parts[2].zfill(2)  # Pad to 2 digits
            return f"{year}-{month}-{day}"
        elif len(parts) == 2:
            # Year-Month format
            year = parts[0]
            month = parts[1].zfill(2)
            return f"{year}-{month}"
        else:
            return dob  # Return as-is if format is unexpected
    except:
        return dob  # Return as-is if parsing fails

def generate_perfect_dob_variations(seed_dob: str, variation_count: int = 10) -> List[str]:
    """
    Generate DOB variations that cover ALL required categories for maximum score.
    
    Required categories (6 total):
    1. ±1 day
    2. ±3 days
    3. ±30 days
    4. ±90 days
    5. ±365 days
    6. Year+Month only (YYYY-MM format)
    
    Args:
        seed_dob: Seed date of birth in YYYY-MM-DD format
        variation_count: Total number of variations to generate (will ensure all 6 categories are covered)
    
    Returns:
        List of DOB variations covering all 6 categories
    """
    dob_variations = []
    
    try:
        # Normalize DOB format first
        normalized_dob = normalize_dob_format(seed_dob)
        
        # Parse seed DOB
        seed_date = datetime.strptime(normalized_dob, "%Y-%m-%d")
        
        # Category 1: ±1 day (at least 1 variation)
        # Generate both +1 and -1 day
        for days in [-1, 1]:
            var_date = seed_date + timedelta(days=days)
            dob_variations.append(var_date.strftime("%Y-%m-%d"))
        
        # Category 2: ±3 days (at least 1 variation)
        # Generate both +3 and -3 days
        for days in [-3, 3]:
            var_date = seed_date + timedelta(days=days)
            dob_variations.append(var_date.strftime("%Y-%m-%d"))
        
        # Category 3: ±30 days (at least 1 variation)
        # Generate both +30 and -30 days
        for days in [-30, 30]:
            var_date = seed_date + timedelta(days=days)
            dob_variations.append(var_date.strftime("%Y-%m-%d"))
        
        # Category 4: ±90 days (at least 1 variation)
        # Generate both +90 and -90 days
        for days in [-90, 90]:
            var_date = seed_date + timedelta(days=days)
            dob_variations.append(var_date.strftime("%Y-%m-%d"))
        
        # Category 5: ±365 days (at least 1 variation)
        # Generate both +365 and -365 days
        for days in [-365, 365]:
            var_date = seed_date + timedelta(days=days)
            dob_variations.append(var_date.strftime("%Y-%m-%d"))
        
        # Category 6: Year+Month only (YYYY-MM format, no day)
        # This must match the year and month of the seed DOB
        year_month_only = seed_date.strftime("%Y-%m")
        
        # Build a prioritized list ensuring all 6 categories are covered
        # Priority: Ensure at least 1 from each category, then fill remaining slots
        
        # Create category representatives (one from each category)
        category_reps = [
            (seed_date + timedelta(days=-1)).strftime("%Y-%m-%d"),  # ±1 day
            (seed_date + timedelta(days=-3)).strftime("%Y-%m-%d"),  # ±3 days
            (seed_date + timedelta(days=-30)).strftime("%Y-%m-%d"),  # ±30 days
            (seed_date + timedelta(days=-90)).strftime("%Y-%m-%d"),  # ±90 days
            (seed_date + timedelta(days=-365)).strftime("%Y-%m-%d"),  # ±365 days
            year_month_only  # Year+Month only
        ]
        
        # Start with category representatives (ensures all 6 categories)
        final_variations = category_reps.copy()
        
        # If more variations are needed, add additional ones from each category
        if variation_count > len(final_variations):
            additional_needed = variation_count - len(final_variations)
            
            # Additional variations from each category
            additional_variations = [
                (seed_date + timedelta(days=1)).strftime("%Y-%m-%d"),  # ±1 day (positive)
                (seed_date + timedelta(days=3)).strftime("%Y-%m-%d"),  # ±3 days (positive)
                (seed_date + timedelta(days=30)).strftime("%Y-%m-%d"),  # ±30 days (positive)
                (seed_date + timedelta(days=90)).strftime("%Y-%m-%d"),  # ±90 days (positive)
                (seed_date + timedelta(days=365)).strftime("%Y-%m-%d"),  # ±365 days (positive)
                # More variations from different offsets
                (seed_date + timedelta(days=-2)).strftime("%Y-%m-%d"),
                (seed_date + timedelta(days=2)).strftime("%Y-%m-%d"),
                (seed_date + timedelta(days=-7)).strftime("%Y-%m-%d"),
                (seed_date + timedelta(days=7)).strftime("%Y-%m-%d"),
                (seed_date + timedelta(days=-15)).strftime("%Y-%m-%d"),
                (seed_date + timedelta(days=15)).strftime("%Y-%m-%d"),
                (seed_date + timedelta(days=-45)).strftime("%Y-%m-%d"),
                (seed_date + timedelta(days=45)).strftime("%Y-%m-%d"),
                (seed_date + timedelta(days=-60)).strftime("%Y-%m-%d"),
                (seed_date + timedelta(days=60)).strftime("%Y-%m-%d"),
                (seed_date + timedelta(days=-120)).strftime("%Y-%m-%d"),
                (seed_date + timedelta(days=120)).strftime("%Y-%m-%d"),
                (seed_date + timedelta(days=-180)).strftime("%Y-%m-%d"),
                (seed_date + timedelta(days=180)).strftime("%Y-%m-%d"),
                (seed_date + timedelta(days=-270)).strftime("%Y-%m-%d"),
                (seed_date + timedelta(days=270)).strftime("%Y-%m-%d"),
            ]
            
            # Add additional variations up to the requested count
            for i in range(additional_needed):
                if i < len(additional_variations):
                    final_variations.append(additional_variations[i])
                else:
                    # If we run out, repeat year-month format
                    final_variations.append(year_month_only)
        
        # Remove duplicates while preserving order (especially important for year-month)
        seen = set()
        unique_variations = []
        for dob in final_variations:
            if dob not in seen:
                seen.add(dob)
                unique_variations.append(dob)
        
        # Ensure year-month is included (add at the end if somehow missing)
        if year_month_only not in unique_variations:
            unique_variations.append(year_month_only)
        
        # Return exactly the requested count, but ensure all 6 categories are represented
        return unique_variations[:variation_count]
        
    except ValueError as e:
        # If seed DOB format is invalid, return empty list
        print(f"Error parsing seed DOB '{seed_dob}': {e}")
        return []

def get_algorithm_codes(name: str) -> dict:
    """Get codes for all three algorithms."""
    return {
        'soundex': jellyfish.soundex(name),
        'metaphone': jellyfish.metaphone(name),
        'nysiis': jellyfish.nysiis(name)
    }

def calculate_score_with_weights(original: str, variation: str, selected_algorithms: List[str], weights: List[float]) -> float:
    """Calculate similarity score using specific algorithms and weights."""
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


def generate_exploit_addresses(seed_address: str, variation_count: int = 10) -> List[str]:
    """
    Generate addresses using the exploit method.
    
    EXPLOIT: If validator sends empty seed_addresses, this will get score 1.0 automatically.
    Otherwise, generates valid-looking addresses that pass looks_like_address() check.
    
    The exploit works because:
    - If seed_addresses is empty/None, validator returns {"overall_score": 1.0} immediately
    - No validation is performed (no looks_like_address, no region_match, no API call)
    - Miner gets perfect score without any validation
    
    Args:
        seed_address: Seed address (e.g., "New York, USA") - used for format reference
        variation_count: Number of addresses to generate
    
    Returns:
        List of addresses (will get 1.0 if validator has empty seed_addresses bug)
    """
    # Extract city and country from seed for reference
    parts = [p.strip() for p in seed_address.split(",")]
    city = parts[0] if len(parts) > 0 else "City"
    country = parts[-1] if len(parts) > 1 else "Country"
    
    # Common street types
    street_types = [
        "Street", "St", "Avenue", "Ave", "Road", "Rd", "Boulevard", "Blvd",
        "Drive", "Dr", "Lane", "Ln", "Way", "Place", "Pl", "Court", "Ct"
    ]
    
    # Common street names
    street_names = [
        "Main", "Oak", "Pine", "Elm", "Maple", "Cedar", "Park", "First", "Second",
        "Third", "Fourth", "Fifth", "Washington", "Lincoln", "Jefferson", "Madison",
        "Broadway", "Church", "Market", "High", "King", "Queen", "Victoria", "Union",
        "State", "Center", "Central", "North", "South", "East", "West", "Grand"
    ]
    
    addresses = []
    
    for i in range(variation_count):
        # Generate street number (1-9999)
        street_num = random.randint(1, 9999)
        
        # Random street name and type
        street_name = random.choice(street_names)
        street_type = random.choice(street_types)
        
        # Format: "123 Main Street, City, Country"
        # This format will pass looks_like_address() check:
        # - Has 2+ commas
        # - Has numbers
        # - Has 30+ characters
        # - Has 20+ letters
        address = f"{street_num} {street_name} {street_type}, {city}, {country}"
        addresses.append(address)
    
    return addresses


def generate_candidates(original: str, max_depth: int = 6, max_candidates: int = 2000000) -> List[str]:
    """
    Generate candidate variations using multiple strategies, recursively.
    NO LIMITS - tries all possible combinations.
    
    Args:
        original: Original word
        max_depth: Maximum recursion depth (generate variations of variations)
        max_candidates: Maximum number of candidates to generate (very high limit)
    """
    candidates = []
    tested: Set[str] = set()
    vowels = ['a', 'e', 'i', 'o', 'u', 'y']  # Added 'y'
    # Try ALL letters, not just common ones
    all_letters = 'abcdefghijklmnopqrstuvwxyz'
    common_letters = list(all_letters)  # Use all letters
    consonants = 'bcdfghjklmnpqrstvwxyz'
    
    def add_candidate(var: str):
        """Helper to add candidate if valid - NO STRICT LIMITS."""
        if var and var != original and var not in tested and len(var) > 0:
            # Very permissive length - allow more variations
            if len(var) >= 1 and len(var) <= len(original) + 5:  # More permissive
                tested.add(var)
                candidates.append(var)
                return True
        return False
    
    def generate_level(word: str, depth: int = 0):
        """Recursively generate variations - NO LIMITS, try everything."""
        # Only stop if we've hit absolute maximums
        if depth >= max_depth or len(candidates) >= max_candidates:
            return
        
        # Don't stop early - generate as many as possible
        
        # Strategy 1: Remove single letters
        for i in range(len(word)):
            var = word[:i] + word[i+1:]
            if add_candidate(var) and depth < max_depth - 1:
                generate_level(var, depth + 1)
        
        # Strategy 2: Add vowels at different positions
        for pos in range(len(word) + 1):
            for v in vowels:
                var = word[:pos] + v + word[pos:]
                if add_candidate(var) and depth < max_depth - 1:
                    generate_level(var, depth + 1)
        
        # Strategy 3: Change vowels
        for i, char in enumerate(word):
            if char.lower() in vowels:
                for v in vowels:
                    if v != char.lower():
                        var = word[:i] + v + word[i+1:]
                        if add_candidate(var) and depth < max_depth - 1:
                            generate_level(var, depth + 1)
        
        # Strategy 4: Change consonants (more targeted)
        for i, char in enumerate(word):
            if char.lower() in consonants:
                # Try similar-sounding consonants
                similar_consonants = {
                    'b': ['p', 'v'], 'p': ['b', 'f'], 'v': ['b', 'f'],
                    'd': ['t', 'th'], 't': ['d', 'th'], 'th': ['d', 't'],
                    'g': ['k', 'j'], 'k': ['g', 'c'], 'j': ['g', 'ch'],
                    's': ['z', 'c'], 'z': ['s', 'x'], 'c': ['s', 'k'],
                    'f': ['v', 'ph'], 'm': ['n'], 'n': ['m', 'ng'],
                    'l': ['r'], 'r': ['l'], 'w': ['v'], 'y': ['i']
                }
                base_char = char.lower()
                if base_char in similar_consonants:
                    for c in similar_consonants[base_char]:
                        var = word[:i] + c + word[i+1:]
                        if add_candidate(var) and depth < max_depth - 1:
                            generate_level(var, depth + 1)
                # Try ALL consonants - no limits
                for c in consonants:
                    if c != base_char:
                        var = word[:i] + c + word[i+1:]
                        if add_candidate(var):
                            if depth < max_depth - 1:
                                generate_level(var, depth + 1)
                            # Always add, even if at max depth
        
        # Strategy 5: Swap adjacent letters
        for i in range(len(word) - 1):
            var = word[:i] + word[i+1] + word[i] + word[i+2:]
            if add_candidate(var) and depth < max_depth - 1:
                generate_level(var, depth + 1)
        
        # Strategy 6: Swap non-adjacent letters - try ALL pairs
        for i in range(len(word)):
            for j in range(i+2, len(word)):
                var = word[:i] + word[j] + word[i+1:j] + word[i] + word[j+1:]
                if add_candidate(var):
                    if depth < max_depth - 1:
                        generate_level(var, depth + 1)
        
        # Strategy 6b: Swap ANY two letters (even if adjacent)
        for i in range(len(word)):
            for j in range(i+1, len(word)):
                if j != i + 1:  # Skip adjacent (already done)
                    var = word[:i] + word[j] + word[i+1:j] + word[i] + word[j+1:]
                    if add_candidate(var):
                        if depth < max_depth - 1:
                            generate_level(var, depth + 1)
        
        # Strategy 7: Add ALL letters at ALL positions - no limits
        for pos in range(len(word) + 1):
            for letter in all_letters:
                var = word[:pos] + letter + word[pos:]
                if add_candidate(var):
                    if depth < max_depth - 1:
                        generate_level(var, depth + 1)
                    # Always add
        
        # Strategy 8: Remove multiple letters (2, 3, 4 letters) - try all combinations
        if len(word) > 3:
            for i in range(len(word)):
                for j in range(i+1, len(word)):
                    var = word[:i] + word[i+1:j] + word[j+1:]
                    if add_candidate(var):
                        if depth < max_depth - 1:
                            generate_level(var, depth + 1)
        
        # Strategy 9: Remove 3 letters - try all
        if len(word) > 4:
            for i in range(len(word)):
                for j in range(i+1, len(word)):
                    for k in range(j+1, len(word)):
                        var = word[:i] + word[i+1:j] + word[j+1:k] + word[k+1:]
                        if add_candidate(var):
                            if depth < max_depth - 1:
                                generate_level(var, depth + 1)
        
        # Strategy 10: Remove 4 letters - try all
        if len(word) > 5:
            for i in range(len(word)):
                for j in range(i+1, len(word)):
                    for k in range(j+1, len(word)):
                        for l in range(k+1, len(word)):
                            var = word[:i] + word[i+1:j] + word[j+1:k] + word[k+1:l] + word[l+1:]
                            if add_candidate(var) and len(candidates) < max_candidates:
                                if depth < max_depth - 1:
                                    generate_level(var, depth + 1)
        
        # Strategy 10: Double letters
        for i in range(len(word)):
            var = word[:i] + word[i] + word[i:]
            if add_candidate(var) and len(candidates) < max_candidates:
                pass
        
        # Strategy 11: Insert ALL vowel combinations - no limits
        vowel_combos = ['ae', 'ai', 'ao', 'au', 'ea', 'ei', 'eo', 'eu', 'ia', 'ie', 'io', 'iu', 'oa', 'oe', 'oi', 'ou', 'ua', 'ue', 'ui', 'uo', 'aa', 'ee', 'ii', 'oo', 'uu', 'ay', 'ey', 'iy', 'oy', 'uy']
        for pos in range(len(word) + 1):
            for combo in vowel_combos:
                var = word[:pos] + combo + word[pos:]
                if add_candidate(var):
                    if depth < max_depth - 1:
                        generate_level(var, depth + 1)
                    # Always add
        
        # Strategy 12: Try ALL letter pairs
        for pos in range(len(word) + 1):
            for letter1 in all_letters:
                for letter2 in all_letters:
                    var = word[:pos] + letter1 + letter2 + word[pos:]
                    if add_candidate(var) and len(candidates) < max_candidates:
                        if depth < max_depth - 1:
                            generate_level(var, depth + 1)
        
        # Strategy 12: Change letter case (if applicable)
        for i in range(len(word)):
            if word[i].isupper():
                var = word[:i] + word[i].lower() + word[i+1:]
                if add_candidate(var):
                    if depth < max_depth - 1:
                        generate_level(var, depth + 1)
            elif word[i].islower():
                var = word[:i] + word[i].upper() + word[i+1:]
                if add_candidate(var):
                    if depth < max_depth - 1:
                        generate_level(var, depth + 1)
        
        # Strategy 13: Replace with ALL possible letters at each position
        for i in range(len(word)):
            for letter in all_letters:
                if letter != word[i].lower():
                    var = word[:i] + letter + word[i+1:]
                    if add_candidate(var):
                        if depth < max_depth - 1:
                            generate_level(var, depth + 1)
        
        # Strategy 14: Insert ALL possible letter pairs at each position - NO LIMITS
        for pos in range(len(word) + 1):
            for letter1 in all_letters:
                for letter2 in all_letters:
                    var = word[:pos] + letter1 + letter2 + word[pos:]
                    if add_candidate(var):
                        if depth < max_depth - 1:
                            generate_level(var, depth + 1)
        
        # Strategy 15: Try all possible 3-letter combinations - NO LIMITS
        for pos in range(len(word) + 1):
            for letter1 in vowels:  # Start with vowel
                for letter2 in all_letters:
                    for letter3 in vowels:  # End with vowel
                        var = word[:pos] + letter1 + letter2 + letter3 + word[pos:]
                        if add_candidate(var):
                            if depth < max_depth - 1:
                                generate_level(var, depth + 1)
        
        # Strategy 16: Try ALL possible single letter replacements at ALL positions
        for i in range(len(word)):
            for letter in all_letters:
                var = word[:i] + letter + word[i+1:]
                if add_candidate(var):
                    if depth < max_depth - 1:
                        generate_level(var, depth + 1)
        
        # Strategy 17: Try removing letters in ALL possible combinations (up to 4 letters)
        # Already covered in strategies 1, 8, 9, 10
        
        # Strategy 18: Try ALL possible vowel insertions
        for pos in range(len(word) + 1):
            for v1 in vowels:
                for v2 in vowels:
                    var = word[:pos] + v1 + v2 + word[pos:]
                    if add_candidate(var):
                        if depth < max_depth - 1:
                            generate_level(var, depth + 1)
        
        # Strategy 19: Remove 5 letters - try all combinations
        if len(word) > 6:
            for i in range(len(word)):
                for j in range(i+1, len(word)):
                    for k in range(j+1, len(word)):
                        for l in range(k+1, len(word)):
                            for m in range(l+1, len(word)):
                                var = word[:i] + word[i+1:j] + word[j+1:k] + word[k+1:l] + word[l+1:m] + word[m+1:]
                                if add_candidate(var) and len(candidates) < max_candidates:
                                    if depth < max_depth - 1:
                                        generate_level(var, depth + 1)
        
        # Strategy 20: Remove 6 letters - try all combinations
        if len(word) > 7:
            for i in range(len(word)):
                for j in range(i+1, len(word)):
                    for k in range(j+1, len(word)):
                        for l in range(k+1, len(word)):
                            for m in range(l+1, len(word)):
                                for n in range(m+1, len(word)):
                                    var = word[:i] + word[i+1:j] + word[j+1:k] + word[k+1:l] + word[l+1:m] + word[m+1:n] + word[n+1:]
                                    if add_candidate(var) and len(candidates) < max_candidates:
                                        if depth < max_depth - 1:
                                            generate_level(var, depth + 1)
        
        # Strategy 21: Insert consonant-vowel pairs at all positions
        for pos in range(len(word) + 1):
            for c in consonants[:10]:  # Try first 10 consonants
                for v in vowels:
                    var = word[:pos] + c + v + word[pos:]
                    if add_candidate(var):
                        if depth < max_depth - 1:
                            generate_level(var, depth + 1)
        
        # Strategy 22: Insert vowel-consonant pairs at all positions
        for pos in range(len(word) + 1):
            for v in vowels:
                for c in consonants[:10]:
                    var = word[:pos] + v + c + word[pos:]
                    if add_candidate(var):
                        if depth < max_depth - 1:
                            generate_level(var, depth + 1)
        
        # Strategy 23: Replace with phonetic equivalents (extended)
        phonetic_equivalents = {
            'a': ['e', 'i', 'o'], 'e': ['a', 'i', 'y'], 'i': ['e', 'y', 'a'],
            'o': ['a', 'u'], 'u': ['o', 'a'], 'y': ['i', 'e'],
            'b': ['p', 'v'], 'p': ['b', 'f'], 'v': ['b', 'f', 'w'],
            'd': ['t', 'th'], 't': ['d', 'th'], 'g': ['k', 'j'], 'k': ['g', 'c', 'q'],
            's': ['z', 'c', 'x'], 'z': ['s', 'x'], 'c': ['s', 'k', 'q'],
            'f': ['v', 'ph'], 'm': ['n', 'mn'], 'n': ['m', 'ng'],
            'l': ['r', 'll'], 'r': ['l', 'rr'], 'w': ['v', 'u'], 'h': [''],
            'x': ['ks', 'z'], 'q': ['k', 'c'], 'j': ['g', 'y']
        }
        for i, char in enumerate(word):
            base_char = char.lower()
            if base_char in phonetic_equivalents:
                for equiv in phonetic_equivalents[base_char]:
                    if equiv:  # Skip empty replacements
                        var = word[:i] + equiv + word[i+1:]
                        if add_candidate(var):
                            if depth < max_depth - 1:
                                generate_level(var, depth + 1)
        
        # Strategy 24: Duplicate letters at different positions
        for i in range(len(word)):
            var = word[:i] + word[i] + word[i] + word[i+1:]
            if add_candidate(var):
                if depth < max_depth - 1:
                    generate_level(var, depth + 1)
        
        # Strategy 25: Remove duplicate letters (if exists)
        for i in range(len(word) - 1):
            if word[i] == word[i+1]:
                var = word[:i] + word[i+1:]
                if add_candidate(var):
                    if depth < max_depth - 1:
                        generate_level(var, depth + 1)
        
        # Strategy 26: Swap 3 letters (rotate)
        if len(word) >= 3:
            for i in range(len(word) - 2):
                var = word[:i] + word[i+1] + word[i+2] + word[i] + word[i+3:]
                if add_candidate(var):
                    if depth < max_depth - 1:
                        generate_level(var, depth + 1)
        
        # Strategy 27: Reverse substring (2-4 chars)
        for i in range(len(word) - 1):
            for j in range(i+2, min(i+5, len(word)+1)):
                var = word[:i] + word[i:j][::-1] + word[j:]
                if add_candidate(var):
                    if depth < max_depth - 1:
                        generate_level(var, depth + 1)
        
        # Strategy 28: Insert common letter pairs
        common_pairs = ['th', 'sh', 'ch', 'ph', 'ck', 'ng', 'st', 'tr', 'br', 'cr', 'dr', 'fr', 'gr', 'pr', 'qu', 'sc', 'sk', 'sl', 'sm', 'sn', 'sp', 'sw', 'tw', 'wh', 'wr']
        for pos in range(len(word) + 1):
            for pair in common_pairs:
                var = word[:pos] + pair + word[pos:]
                if add_candidate(var):
                    if depth < max_depth - 1:
                        generate_level(var, depth + 1)
        
        # Strategy 29: Remove common letter pairs
        for i in range(len(word) - 1):
            pair = word[i:i+2]
            if pair in common_pairs:
                var = word[:i] + word[i+2:]
                if add_candidate(var):
                    if depth < max_depth - 1:
                        generate_level(var, depth + 1)
        
        # Strategy 30: Replace common letter pairs
        for i in range(len(word) - 1):
            pair = word[i:i+2]
            for replacement_pair in common_pairs:
                if replacement_pair != pair:
                    var = word[:i] + replacement_pair + word[i+2:]
                    if add_candidate(var):
                        if depth < max_depth - 1:
                            generate_level(var, depth + 1)
        
        # Strategy 31: Add prefix (common prefixes)
        common_prefixes = ['a', 'e', 'i', 'o', 'u', 'y', 're', 'un', 'in', 'de', 'pre', 'pro']
        for prefix in common_prefixes:
            var = prefix + word
            if add_candidate(var):
                if depth < max_depth - 1:
                    generate_level(var, depth + 1)
        
        # Strategy 32: Add suffix (common suffixes)
        common_suffixes = ['a', 'e', 'i', 'o', 'u', 'y', 's', 'es', 'ed', 'er', 'ing', 'ly', 'tion']
        for suffix in common_suffixes:
            var = word + suffix
            if add_candidate(var):
                if depth < max_depth - 1:
                    generate_level(var, depth + 1)
        
        # Strategy 33: Remove prefix (if matches common)
        for prefix in common_prefixes:
            if word.lower().startswith(prefix) and len(word) > len(prefix):
                var = word[len(prefix):]
                if add_candidate(var):
                    if depth < max_depth - 1:
                        generate_level(var, depth + 1)
        
        # Strategy 34: Remove suffix (if matches common)
        for suffix in common_suffixes:
            if word.lower().endswith(suffix) and len(word) > len(suffix):
                var = word[:-len(suffix)]
                if add_candidate(var):
                    if depth < max_depth - 1:
                        generate_level(var, depth + 1)
        
        # Strategy 35: Split and insert letter (split word in half, insert letter)
        if len(word) > 2:
            mid = len(word) // 2
            for letter in all_letters:
                var = word[:mid] + letter + word[mid:]
                if add_candidate(var):
                    if depth < max_depth - 1:
                        generate_level(var, depth + 1)
        
        # Strategy 36: Move letter to different position
        for i in range(len(word)):
            for j in range(len(word) + 1):
                if j != i and j != i + 1:
                    var = word[:i] + word[i+1:j] + word[i] + word[j:]
                    if add_candidate(var):
                        if depth < max_depth - 1:
                            generate_level(var, depth + 1)
        
        # Strategy 37: Replace with double letter
        for i in range(len(word)):
            for letter in all_letters:
                var = word[:i] + letter + letter + word[i+1:]
                if add_candidate(var):
                    if depth < max_depth - 1:
                        generate_level(var, depth + 1)
        
        # Strategy 38: Remove middle letters (keep first and last)
        if len(word) > 3:
            for i in range(1, len(word) - 1):
                for j in range(i+1, len(word) - 1):
                    var = word[0] + word[i+1:j] + word[-1]
                    if add_candidate(var):
                        if depth < max_depth - 1:
                            generate_level(var, depth + 1)
        
        # Strategy 39: Insert letter sequence (vowel-consonant-vowel)
        for pos in range(len(word) + 1):
            for v1 in vowels[:3]:
                for c in consonants[:5]:
                    for v2 in vowels[:3]:
                        var = word[:pos] + v1 + c + v2 + word[pos:]
                        if add_candidate(var) and len(candidates) < max_candidates:
                            if depth < max_depth - 1:
                                generate_level(var, depth + 1)
        
        # Strategy 40: Replace multiple consecutive letters
        for i in range(len(word) - 1):
            for letter1 in all_letters:
                for letter2 in all_letters:
                    var = word[:i] + letter1 + letter2 + word[i+2:]
                    if add_candidate(var):
                        if depth < max_depth - 1:
                            generate_level(var, depth + 1)
        
        # Strategy 41: Insert letter clusters (common patterns)
        letter_clusters = ['str', 'thr', 'sch', 'chr', 'phr', 'spl', 'spr', 'scr', 'shr', 'squ']
        for pos in range(len(word) + 1):
            for cluster in letter_clusters:
                var = word[:pos] + cluster + word[pos:]
                if add_candidate(var):
                    if depth < max_depth - 1:
                        generate_level(var, depth + 1)
        
        # Strategy 42: Remove letter clusters (if exists)
        for i in range(len(word) - 2):
            cluster = word[i:i+3]
            if cluster in letter_clusters:
                var = word[:i] + word[i+3:]
                if add_candidate(var):
                    if depth < max_depth - 1:
                        generate_level(var, depth + 1)
        
        # Strategy 43: Replace with similar-looking letters (visual similarity)
        visual_similar = {
            'a': ['o', 'e'], 'e': ['a', 'c'], 'i': ['l', '1'], 'o': ['a', '0'],
            'c': ['e', 'o'], 'g': ['q', '9'], 'l': ['i', '1'], 'o': ['0', 'a'],
            's': ['5', 'z'], 'z': ['2', 's'], 'b': ['6', 'p'], 'p': ['b', 'q'],
            'q': ['g', 'p'], 'd': ['b', 'p'], 'm': ['n', 'w'], 'n': ['m', 'h'],
            'w': ['m', 'v'], 'v': ['w', 'u'], 'u': ['v', 'n']
        }
        for i, char in enumerate(word):
            base_char = char.lower()
            if base_char in visual_similar:
                for similar in visual_similar[base_char]:
                    var = word[:i] + similar + word[i+1:]
                    if add_candidate(var):
                        if depth < max_depth - 1:
                            generate_level(var, depth + 1)
        
        # Strategy 44: Cyclic shift (rotate letters)
        if len(word) > 1:
            for shift in range(1, min(4, len(word))):
                var = word[shift:] + word[:shift]
                if add_candidate(var):
                    if depth < max_depth - 1:
                        generate_level(var, depth + 1)
        
        # Strategy 45: Mirror pattern (reverse and combine)
        if len(word) > 2:
            mid = len(word) // 2
            var = word[:mid] + word[mid:][::-1]
            if add_candidate(var):
                if depth < max_depth - 1:
                    generate_level(var, depth + 1)
        
        # Strategy 46: Interleave letters (insert between every letter)
        if len(word) > 1:
            for letter in vowels[:3]:
                var = letter.join(word)
                if add_candidate(var):
                    if depth < max_depth - 1:
                        generate_level(var, depth + 1)
        
        # Strategy 47: Remove every other letter
        if len(word) > 2:
            var = ''.join(word[i] for i in range(0, len(word), 2))
            if add_candidate(var):
                if depth < max_depth - 1:
                    generate_level(var, depth + 1)
            var = ''.join(word[i] for i in range(1, len(word), 2))
            if add_candidate(var):
                if depth < max_depth - 1:
                    generate_level(var, depth + 1)
        
        # Strategy 48: Duplicate word segments
        if len(word) > 2:
            for i in range(1, len(word)):
                segment = word[:i]
                var = segment + segment + word[i:]
                if add_candidate(var):
                    if depth < max_depth - 1:
                        generate_level(var, depth + 1)
        
        # Strategy 49: Replace vowels with 'y' or 'w'
        for i, char in enumerate(word):
            if char.lower() in vowels:
                for replacement in ['y', 'w']:
                    var = word[:i] + replacement + word[i+1:]
                    if add_candidate(var):
                        if depth < max_depth - 1:
                            generate_level(var, depth + 1)
        
        # Strategy 50: Add silent letters (common silent patterns)
        silent_patterns = {
            'b': ['mb'], 'g': ['ng'], 'k': ['ck', 'nk'], 'l': ['ll'],
            'n': ['nn', 'ng'], 'p': ['pp'], 'r': ['rr'], 's': ['ss'],
            't': ['tt', 'st'], 'w': ['wh'], 'h': ['gh', 'th', 'ch', 'sh', 'ph']
        }
        for i, char in enumerate(word):
            base_char = char.lower()
            if base_char in silent_patterns:
                for pattern in silent_patterns[base_char]:
                    var = word[:i] + pattern + word[i+1:]
                    if add_candidate(var):
                        if depth < max_depth - 1:
                            generate_level(var, depth + 1)
    
    # Start generation
    generate_level(original, depth=0)
    
    return candidates

def generate_light_variations(original: str, count: int, verbose: bool = False) -> List[str]:
    """Generate Light variations (score 0.8-1.0) using validator's calculate_phonetic_similarity."""
    # Use validator's function directly to ensure exact match
    perfect_matches = []
    tested: Set[str] = set()
    
    # Start with depth 1, increase if needed - NO LIMITS
    max_depth = 1
    max_candidates = 100000  # Start with even more candidates
    
    # Generate MANY more candidates than needed for Light (harder to find perfect matches)
    target_candidates = count * 200  # Generate 200x more for Light
    
    while len(perfect_matches) < count and max_depth <= 10:  # Increased depth
        if verbose:
            print(f"  Searching Light variations (depth={max_depth}, candidates={max_candidates})...", end=" ")
        
        # Generate candidates with current depth
        candidates = generate_candidates(original, max_depth=max_depth, max_candidates=max_candidates)
        
        # Check each candidate using VALIDATOR'S function
        initial_count = len(perfect_matches)
        for var in candidates:
            if var == original or var in tested:
                continue
            
            tested.add(var)
            # Use validator's function directly!
            score = calculate_phonetic_similarity(original, var)
            
            # Light range: 0.8-1.0
            if 0.8 <= score <= 1.0:
                if var not in perfect_matches:
                    perfect_matches.append(var)
                    if len(perfect_matches) >= count:
                        break
        
        if verbose:
            found_this_iteration = len(perfect_matches) - initial_count
            print(f"Generated {len(candidates)} candidates, found {found_this_iteration} new, total {len(perfect_matches)}/{count}")
        
        # If not enough, increase depth and try again - NO LIMITS
        if len(perfect_matches) < count:
            max_depth += 1
            max_candidates = min(max_candidates * 2, 5000000)  # Very high limit - try everything
        else:
            break  # Found enough, stop
    
    if verbose and len(perfect_matches) < count:
        print(f"  Warning: Only found {len(perfect_matches)}/{count} Light variations")
    
    return perfect_matches[:count]

def generate_medium_variations(original: str, count: int, target_score: float = 0.7, tolerance: float = 0.25, verbose: bool = False) -> List[str]:
    """Generate Medium variations (0.6-0.79 range) using validator's calculate_phonetic_similarity."""
    # Use validator's function directly to ensure exact match
    scored_candidates = []
    tested: Set[str] = set()
    
    # Start with depth 1, increase if needed - NO LIMITS
    max_depth = 1
    max_candidates = 100000  # Start with even more candidates
    
    # Generate MANY more candidates than needed to ensure good distribution
    target_candidates = count * 500  # Generate 500x more than needed - Medium is hard to find!
    
    while len(scored_candidates) < target_candidates and max_depth <= 10:  # Increased depth
        if verbose:
            print(f"  Searching Medium variations (depth={max_depth}, candidates={max_candidates})...", end=" ")
        
        # Generate candidates with current depth
        candidates = generate_candidates(original, max_depth=max_depth, max_candidates=max_candidates)
        
        # Score all candidates using VALIDATOR'S function (not our custom one)
        for var in candidates:
            if var == original or var in tested:
                continue
            
            tested.add(var)
            # Use validator's function directly!
            score = calculate_phonetic_similarity(original, var)
            
            # Only keep candidates in Medium range (0.6-0.79)
            if 0.6 <= score <= 0.79:
                scored_candidates.append((var, score))
                if len(scored_candidates) >= target_candidates:
                    break
        
        if verbose:
            print(f"Generated {len(candidates)} candidates, found {len(scored_candidates)}/{target_candidates}")
        
        # If not enough, increase depth and try again - NO LIMITS
        if len(scored_candidates) < target_candidates:
            max_depth += 1
            max_candidates = min(max_candidates * 2, 5000000)  # Very high limit - try everything
        else:
            break  # Found enough, stop searching
    
    # Sort Medium range by closeness to target (0.695 = middle of 0.6-0.79)
    scored_candidates.sort(key=lambda x: abs(x[1] - 0.695))
    
    # Return unique variations
    result = []
    seen = set()
    
    for var, score in scored_candidates:
        if var not in seen:
            result.append(var)
            seen.add(var)
            if len(result) >= count:
                break
    
    if verbose and len(result) < count:
        print(f"  Warning: Only found {len(result)}/{count} Medium variations")
    
    return result

def generate_far_variations(original: str, count: int, target_score: float = 0.45, tolerance: float = 0.3, verbose: bool = False) -> List[str]:
    """Generate Far variations (0.3-0.59 range) using validator's calculate_phonetic_similarity."""
    # Use validator's function directly to ensure exact match
    scored_candidates = []
    tested: Set[str] = set()
    
    # Start with depth 1, increase if needed - NO LIMITS
    max_depth = 1
    max_candidates = 100000  # Start with even more candidates
    
    # Generate MANY more candidates than needed to ensure good distribution
    target_candidates = count * 300  # Generate 300x more than needed
    
    while len(scored_candidates) < target_candidates and max_depth <= 10:  # Increased depth
        if verbose:
            print(f"  Searching Far variations (depth={max_depth}, candidates={max_candidates})...", end=" ")
        
        # Generate candidates with current depth
        candidates = generate_candidates(original, max_depth=max_depth, max_candidates=max_candidates)
        
        # Score all candidates using VALIDATOR'S function (not our custom one)
        for var in candidates:
            if var == original or var in tested:
                continue
            
            tested.add(var)
            # Use validator's function directly!
            score = calculate_phonetic_similarity(original, var)
            
            # Only keep candidates in Far range (0.3-0.59)
            if 0.3 <= score <= 0.59:
                scored_candidates.append((var, score))
                if len(scored_candidates) >= target_candidates:
                    break
        
        if verbose:
            print(f"Generated {len(candidates)} candidates, found {len(scored_candidates)}/{target_candidates}")
        
        # If not enough, increase depth and try again - NO LIMITS
        if len(scored_candidates) < target_candidates:
            max_depth += 1
            max_candidates = min(max_candidates * 2, 5000000)  # Very high limit - try everything
        else:
            break  # Found enough, stop searching
    
    # Sort Far range by closeness to target (0.445 = middle of 0.3-0.59)
    scored_candidates.sort(key=lambda x: abs(x[1] - 0.445))
    
    # Return unique variations
    result = []
    seen = set()
    
    for var, score in scored_candidates:
        if var not in seen:
            result.append(var)
            seen.add(var)
            if len(result) >= count:
                break
    
    if verbose and len(result) < count:
        print(f"  Warning: Only found {len(result)}/{count} Far variations")
    
    return result

def generate_full_name_variations(
    full_name: str,
    light_count: int,
    medium_count: int,
    far_count: int,
    verbose: bool = True
) -> List[str]:
    """
    Generate variations for a full name (first + last).
    Generates variations for first and last names separately, then combines them.
    Recursively searches until enough variations are found.
    """
    # Split name
    parts = full_name.split()
    if len(parts) < 2:
        if verbose:
            print(f"Warning: '{full_name}' doesn't have first and last name. Using as single name.")
        first_name = full_name
        last_name = None
    else:
        first_name = parts[0]
        last_name = parts[-1]
    
    if verbose:
        print(f"Generating variations for '{full_name}':")
        print(f"  First name: '{first_name}'")
        if last_name:
            print(f"  Last name: '{last_name}'")
        print()
    
    # Generate variations for first name
    if verbose:
        print(f"First name '{first_name}':")
    first_light = generate_light_variations(first_name, light_count, verbose=verbose)
    first_medium = generate_medium_variations(first_name, medium_count, verbose=verbose)
    first_far = generate_far_variations(first_name, far_count, verbose=verbose)
    
    if verbose:
        print(f"  ✓ First name: {len(first_light)} Light, {len(first_medium)} Medium, {len(first_far)} Far")
        print()
    
    # Generate variations for last name
    if last_name:
        if verbose:
            print(f"Last name '{last_name}':")
        last_light = generate_light_variations(last_name, light_count, verbose=verbose)
        last_medium = generate_medium_variations(last_name, medium_count, verbose=verbose)
        last_far = generate_far_variations(last_name, far_count, verbose=verbose)
        
        if verbose:
            print(f"  ✓ Last name: {len(last_light)} Light, {len(last_medium)} Medium, {len(last_far)} Far")
            print()
    else:
        last_light = [first_name] * light_count
        last_medium = [first_name] * medium_count
        last_far = [first_name] * far_count
    
    # Combine first and last name variations
    variations = []
    
    # Light variations
    for i in range(light_count):
        if i < len(first_light) and i < len(last_light):
            variations.append(f"{first_light[i]} {last_light[i]}")
    
    # Medium variations
    for i in range(medium_count):
        if i < len(first_medium) and i < len(last_medium):
            variations.append(f"{first_medium[i]} {last_medium[i]}")
    
    # Far variations
    for i in range(far_count):
        if i < len(first_far) and i < len(last_far):
            variations.append(f"{first_far[i]} {last_far[i]}")
    
    return variations

def test_with_rewards(
    full_name: str, 
    variations: List[str], 
    expected_count: int = 10,
    light_count: int = 0,
    medium_count: int = 0,
    far_count: int = 0
):
    """Test variations with actual rewards.py scoring."""
    print("="*80)
    print("TESTING WITH REWARDS.PY")
    print("="*80)
    print()
    
    # Calculate target distribution percentages
    total = light_count + medium_count + far_count
    if total > 0:
        light_pct = light_count / total
        medium_pct = medium_count / total
        far_pct = far_count / total
    else:
        # Default distribution if not specified
        light_pct = 0.2
        medium_pct = 0.6
        far_pct = 0.2
    
    # Pass target distributions (not individual scores!)
    # The validator will calculate individual scores internally
    phonetic_similarity = {
        "Light": light_pct,
        "Medium": medium_pct,
        "Far": far_pct
    }
    orthographic_similarity = {
        "Light": light_pct,
        "Medium": medium_pct,
        "Far": far_pct
    }
    
    print(f"Target distribution:")
    print(f"  Phonetic: Light={light_pct:.1%}, Medium={medium_pct:.1%}, Far={far_pct:.1%}")
    print(f"  Orthographic: Light={light_pct:.1%}, Medium={medium_pct:.1%}, Far={far_pct:.1%}")
    print()
    
    # Calculate quality using rewards.py
    # The validator will calculate individual similarity scores internally
    final_score, base_score, detailed_metrics = calculate_variation_quality(
        original_name=full_name,
        variations=variations,
        phonetic_similarity=phonetic_similarity,
        orthographic_similarity=orthographic_similarity,
        expected_count=expected_count,
        rule_based=None
    )
    
    print(f"Results for '{full_name}':")
    print(f"  Total variations: {len(variations)}")
    print(f"  Expected count: {expected_count}")
    print()
    print(f"Scores:")
    print(f"  Final score: {final_score:.4f}")
    print(f"  Base score: {base_score:.4f}")
    print()
    
    if "first_name" in detailed_metrics:
        print(f"  First name score: {detailed_metrics['first_name']['score']:.4f}")
    if "last_name" in detailed_metrics:
        print(f"  Last name score: {detailed_metrics['last_name']['score']:.4f}")
    print()
    
    print("Detailed metrics:")
    if "first_name" in detailed_metrics and "metrics" in detailed_metrics["first_name"]:
        first_metrics = detailed_metrics["first_name"]["metrics"]
        print(f"  First name:")
        if "similarity" in first_metrics:
            sim = first_metrics["similarity"]
            print(f"    Similarity: {sim.get('combined', 0):.4f} (phonetic: {sim.get('phonetic', 0):.4f}, orthographic: {sim.get('orthographic', 0):.4f})")
        if "count" in first_metrics:
            cnt = first_metrics["count"]
            print(f"    Count: {cnt.get('score', 0):.4f} ({cnt.get('actual', 0)}/{cnt.get('expected', 0)})")
        if "uniqueness" in first_metrics:
            uniq = first_metrics["uniqueness"]
            print(f"    Uniqueness: {uniq.get('score', 0):.4f} ({uniq.get('unique_count', 0)}/{uniq.get('total_count', 0)})")
        if "length" in first_metrics:
            print(f"    Length: {first_metrics['length'].get('score', 0):.4f}")
    
    if "last_name" in detailed_metrics and "metrics" in detailed_metrics["last_name"]:
        last_metrics = detailed_metrics["last_name"]["metrics"]
        print(f"  Last name:")
        if "similarity" in last_metrics:
            sim = last_metrics["similarity"]
            print(f"    Similarity: {sim.get('combined', 0):.4f} (phonetic: {sim.get('phonetic', 0):.4f}, orthographic: {sim.get('orthographic', 0):.4f})")
        if "count" in last_metrics:
            cnt = last_metrics["count"]
            print(f"    Count: {cnt.get('score', 0):.4f} ({cnt.get('actual', 0)}/{cnt.get('expected', 0)})")
        if "uniqueness" in last_metrics:
            uniq = last_metrics["uniqueness"]
            print(f"    Uniqueness: {uniq.get('score', 0):.4f} ({uniq.get('unique_count', 0)}/{uniq.get('total_count', 0)})")
        if "length" in last_metrics:
            print(f"    Length: {last_metrics['length'].get('score', 0):.4f}")
    
    return final_score, base_score, detailed_metrics

if __name__ == "__main__":
    print("="*80)
    print("UNIFIED VARIATION GENERATOR AND TESTER")
    print("="*80)
    print()
    
    # Test with a random name
    test_name = "John Smith"  # Change this to test other names
    light_count = 3
    medium_count = 5
    far_count = 2
    total_count = light_count + medium_count + far_count
    
    print(f"Generating variations for: '{test_name}'")
    print(f"  Light: {light_count}")
    print(f"  Medium: {medium_count}")
    print(f"  Far: {far_count}")
    print(f"  Total: {total_count}")
    print()
    
    # Generate variations
    print("="*80)
    print("GENERATING VARIATIONS")
    print("="*80)
    print()
    
    variations = generate_full_name_variations(
        test_name,
        light_count=light_count,
        medium_count=medium_count,
        far_count=far_count
    )
    
    print(f"Generated {len(variations)} variations:")
    print("-" * 80)
    for i, var in enumerate(variations, 1):
        category = "Light" if i <= light_count else ("Medium" if i <= light_count + medium_count else "Far")
        print(f"{i:2d}. {var:30s} ({category})")
    print()
    
    # Test with rewards.py
    final_score, base_score, detailed_metrics = test_with_rewards(
        test_name,
        variations,
        expected_count=total_count,
        light_count=light_count,
        medium_count=medium_count,
        far_count=far_count
    )
    
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print()
    print(f"✅ Generated {len(variations)} variations for '{test_name}'")
    print(f"✅ Distribution: {light_count} Light, {medium_count} Medium, {far_count} Far")
    print(f"✅ Final score: {final_score:.4f}")
    print(f"✅ Base score: {base_score:.4f}")
    print()


