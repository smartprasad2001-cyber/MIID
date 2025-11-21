#!/usr/bin/env python3
"""
Clean Variation Generator
Generates name, DOB, and address variations - NO VALIDATION, NO SCORING.
Just generates output.

USAGE:
    python variation_generator_clean.py example_synapse.json
"""

import re
import random
import json
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict

# Import name_variations.py directly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from name_variations import generate_name_variations

# Import unidecode for transliteration
try:
    from unidecode import unidecode
    UNIDECODE_AVAILABLE = True
except ImportError:
    UNIDECODE_AVAILABLE = False
    print("⚠️  Warning: unidecode not available. Non-Latin scripts may not work well.")

# Minimal IdentitySynapse class
class IdentitySynapse:
    def __init__(self, identity, query_template, timeout=120.0):
        self.identity = identity
        self.query_template = query_template
        self.timeout = timeout

# ============================================================================
# Parse Query Template
# ============================================================================

def parse_query_template(query_template: str) -> Dict:
    """Extract requirements from query template"""
    requirements = {
        'variation_count': 15,
        'rule_percentage': 0,
        'rules': [],
        'phonetic_similarity': {},
        'orthographic_similarity': {},
        'uav_seed_name': None  # Phase 3: UAV seed name
    }
    
    # Extract variation count
    count_match = re.search(r'Generate\s+(\d+)\s+variations', query_template, re.I)
    if count_match:
        requirements['variation_count'] = int(count_match.group(1))
    
    # Extract rule percentage - look for patterns like "X% of", "approximately X%", "include X%"
    rule_pct_patterns = [
        r'approximately\s+(\d+)%\s+of',  # "Approximately 24% of"
        r'also\s+include\s+(\d+)%\s+of', # "also include 44% of"
        r'(\d+)%\s+of\s+the\s+total',     # "24% of the total"
        r'(\d+)%\s+of\s+variations',      # "24% of variations"
        r'include\s+(\d+)%',              # "include 24%"
        r'(\d+)%\s+should\s+follow'       # "24% should follow"
    ]
    for pattern in rule_pct_patterns:
        rule_pct_match = re.search(pattern, query_template, re.I)
        if rule_pct_match:
            pct = rule_pct_match.group(1)
            requirements['rule_percentage'] = int(pct) / 100
            break
    
    # Extract rules - check various phrasings
    # Character replacement
    if 'replace spaces with special characters' in query_template.lower() or 'replace spaces with random special characters' in query_template.lower():
        requirements['rules'].append('replace_spaces_with_special_characters')
    if 'replace double letters' in query_template.lower() or 'replace double letters with single letter' in query_template.lower():
        requirements['rules'].append('replace_double_letters')
    if 'replace random vowels' in query_template.lower() or 'replace vowels with different vowels' in query_template.lower():
        requirements['rules'].append('replace_random_vowels')
    if 'replace random consonants' in query_template.lower() or 'replace consonants with different consonants' in query_template.lower():
        requirements['rules'].append('replace_random_consonants')
    
    # Character swapping
    if 'swap adjacent consonants' in query_template.lower():
        requirements['rules'].append('swap_adjacent_consonants')
    if 'swap adjacent syllables' in query_template.lower():
        requirements['rules'].append('swap_adjacent_syllables')
    if 'swap random letter' in query_template.lower() or 'swap random adjacent letters' in query_template.lower():
        requirements['rules'].append('swap_random_letter')
    
    # Character removal
    if 'delete a random letter' in query_template.lower() or 'delete random letter' in query_template.lower():
        requirements['rules'].append('delete_random_letter')
    if 'remove random vowel' in query_template.lower() or 'remove a random vowel' in query_template.lower():
        requirements['rules'].append('remove_random_vowel')
    if 'remove random consonant' in query_template.lower() or 'remove a random consonant' in query_template.lower():
        requirements['rules'].append('remove_random_consonant')
    if 'remove all spaces' in query_template.lower() or 'remove spaces' in query_template.lower():
        requirements['rules'].append('remove_all_spaces')
    
    # Character insertion
    if 'duplicate a random letter' in query_template.lower() or 'duplicate random letter' in query_template.lower():
        requirements['rules'].append('duplicate_random_letter')
    if 'insert random letter' in query_template.lower() or 'insert a random letter' in query_template.lower():
        requirements['rules'].append('insert_random_letter')
    if 'add a title prefix' in query_template.lower() or 'title prefix' in query_template.lower() or 'add title prefix' in query_template.lower():
        requirements['rules'].append('add_title_prefix')
    if 'add a title suffix' in query_template.lower() or 'title suffix' in query_template.lower() or 'add title suffix' in query_template.lower():
        requirements['rules'].append('add_title_suffix')
    
    # Name formatting
    if 'use first name initial' in query_template.lower() or 'first name initial with last name' in query_template.lower():
        requirements['rules'].append('initial_only_first_name')
    if 'convert name to initials' in query_template.lower() or 'shorten name to initials' in query_template.lower():
        requirements['rules'].append('shorten_to_initials')
    if 'abbreviate name parts' in query_template.lower() or 'abbreviate' in query_template.lower() or 'shorten name to abbreviations' in query_template.lower():
        requirements['rules'].append('abbreviate_name_parts')
    
    # Structure change
    if 'reorder name parts' in query_template.lower() or 'reorder parts' in query_template.lower() or 'name parts permutations' in query_template.lower():
        requirements['rules'].append('reorder_name_parts')
    
    # Extract similarity (just parse, don't validate)
    if 'phonetic similarity' in query_template.lower():
        if '100%' in query_template or 'Medium' in query_template:
            requirements['phonetic_similarity'] = {'Medium': 1.0}
    
    if 'orthographic similarity' in query_template.lower():
        if '100%' in query_template or 'Medium' in query_template:
            requirements['orthographic_similarity'] = {'Medium': 1.0}
    
    # Extract UAV seed name from Phase 3 requirements
    uav_match = re.search(r'For the seed "([^"]+)" ONLY', query_template, re.I)
    if uav_match:
        requirements['uav_seed_name'] = uav_match.group(1)
    
    return requirements

# ============================================================================
# Rule Application Functions
# ============================================================================

def apply_replace_spaces_with_special_chars(name: str) -> str:
    """Replace spaces with special characters"""
    if ' ' not in name:
        return name
    special_chars = ['_', '-', '@', '.']
    return name.replace(' ', random.choice(special_chars))

def apply_delete_random_letter(name: str) -> str:
    """Delete a random letter"""
    if len(name) <= 1:
        return name
    idx = random.randint(0, len(name) - 1)
    return name[:idx] + name[idx+1:]

def apply_replace_double_letters(name: str) -> str:
    """Replace double letters with single letter"""
    name_lower = name.lower()
    for i in range(len(name_lower) - 1):
        if name_lower[i] == name_lower[i+1] and name[i].isalpha():
            return name[:i+1] + name[i+2:]
    return name

def apply_swap_adjacent_consonants(name: str) -> str:
    """Swap adjacent consonants"""
    vowels = "aeiou"
    name_lower = name.lower()
    for i in range(len(name_lower) - 1):
        if (name_lower[i].isalpha() and name_lower[i] not in vowels and
            name_lower[i+1].isalpha() and name_lower[i+1] not in vowels and
            name_lower[i] != name_lower[i+1]):
            return name[:i] + name[i+1] + name[i] + name[i+2:]
    return name

def apply_swap_adjacent_syllables(name: str) -> str:
    """Swap adjacent syllables (simplified: swap name parts)"""
    parts = name.split()
    if len(parts) >= 2:
        # Swap first and last name
        return " ".join([parts[-1]] + parts[1:-1] + [parts[0]])
    elif len(parts) == 1:
        # For single word, try to split in middle and swap
        word = parts[0]
        mid = len(word) // 2
        if mid > 0:
            return word[mid:] + word[:mid]
    return name

def apply_add_title_suffix(name: str) -> str:
    """Add a title suffix (Jr., PhD, etc.)"""
    suffixes = ['Jr.', 'Sr.', 'PhD', 'MD', 'III', 'II', 'Esq.']
    return name + " " + random.choice(suffixes)

def apply_abbreviate_name_parts(name: str) -> str:
    """Abbreviate name parts (e.g., "John" -> "J.")"""
    parts = name.split()
    if len(parts) >= 2:
        # Abbreviate first name
        parts[0] = parts[0][0] + "." if len(parts[0]) > 0 else parts[0]
    elif len(parts) == 1 and len(parts[0]) > 1:
        # If single word, abbreviate first letter
        parts[0] = parts[0][0] + "."
    return " ".join(parts)

def apply_replace_random_vowels(name: str) -> str:
    """Replace random vowels with different vowels"""
    vowels = {'a': ['e', 'i', 'o', 'u'], 'e': ['a', 'i', 'o', 'u'], 'i': ['a', 'e', 'o', 'u'],
              'o': ['a', 'e', 'i', 'u'], 'u': ['a', 'e', 'i', 'o'],
              'A': ['E', 'I', 'O', 'U'], 'E': ['A', 'I', 'O', 'U'], 'I': ['A', 'E', 'O', 'U'],
              'O': ['A', 'E', 'I', 'U'], 'U': ['A', 'E', 'I', 'O']}
    
    result = list(name)
    vowel_indices = [i for i, char in enumerate(name) if char.lower() in 'aeiou']
    
    if vowel_indices:
        # Replace 1-2 random vowels
        num_replacements = min(random.randint(1, 2), len(vowel_indices))
        indices_to_replace = random.sample(vowel_indices, num_replacements)
        
        for idx in indices_to_replace:
            char = name[idx]
            if char in vowels:
                result[idx] = random.choice(vowels[char])
    
    return ''.join(result)

def apply_remove_all_spaces(name: str) -> str:
    """Remove all spaces from name"""
    return name.replace(' ', '')

def apply_reorder_name_parts(name: str) -> str:
    """Reorder name parts (swap, reverse, etc.)"""
    parts = name.split()
    if len(parts) >= 2:
        # Different reordering strategies
        strategy = random.choice(['swap_first_last', 'reverse_all', 'random_shuffle'])
        
        if strategy == 'swap_first_last':
            # Swap first and last
            return " ".join([parts[-1]] + parts[1:-1] + [parts[0]])
        elif strategy == 'reverse_all':
            # Reverse all parts
            return " ".join(reversed(parts))
        else:  # random_shuffle
            # Shuffle all parts
            shuffled = parts.copy()
            random.shuffle(shuffled)
            return " ".join(shuffled)
    elif len(parts) == 1:
        # For single word, reverse it
        return parts[0][::-1]
    return name

def apply_replace_random_consonants(name: str) -> str:
    """Replace random consonants with different consonants"""
    consonants = {
        'b': ['c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'q', 'r', 's', 't', 'v', 'w', 'x', 'z'],
        'c': ['b', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'q', 'r', 's', 't', 'v', 'w', 'x', 'z'],
        'd': ['b', 'c', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'q', 'r', 's', 't', 'v', 'w', 'x', 'z'],
        'f': ['b', 'c', 'd', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'q', 'r', 's', 't', 'v', 'w', 'x', 'z'],
        'g': ['b', 'c', 'd', 'f', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'q', 'r', 's', 't', 'v', 'w', 'x', 'z'],
        'h': ['b', 'c', 'd', 'f', 'g', 'j', 'k', 'l', 'm', 'n', 'p', 'q', 'r', 's', 't', 'v', 'w', 'x', 'z'],
        'j': ['b', 'c', 'd', 'f', 'g', 'h', 'k', 'l', 'm', 'n', 'p', 'q', 'r', 's', 't', 'v', 'w', 'x', 'z'],
        'k': ['b', 'c', 'd', 'f', 'g', 'h', 'j', 'l', 'm', 'n', 'p', 'q', 'r', 's', 't', 'v', 'w', 'x', 'z'],
        'l': ['b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'm', 'n', 'p', 'q', 'r', 's', 't', 'v', 'w', 'x', 'z'],
        'm': ['b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'n', 'p', 'q', 'r', 's', 't', 'v', 'w', 'x', 'z'],
        'n': ['b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'p', 'q', 'r', 's', 't', 'v', 'w', 'x', 'z'],
        'p': ['b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'q', 'r', 's', 't', 'v', 'w', 'x', 'z'],
        'q': ['b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'r', 's', 't', 'v', 'w', 'x', 'z'],
        'r': ['b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'q', 's', 't', 'v', 'w', 'x', 'z'],
        's': ['b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'q', 'r', 't', 'v', 'w', 'x', 'z'],
        't': ['b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'q', 'r', 's', 'v', 'w', 'x', 'z'],
        'v': ['b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'q', 'r', 's', 't', 'w', 'x', 'z'],
        'w': ['b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'q', 'r', 's', 't', 'v', 'x', 'z'],
        'x': ['b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'q', 'r', 's', 't', 'v', 'w', 'z'],
        'z': ['b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'q', 'r', 's', 't', 'v', 'w', 'x']
    }
    # Add uppercase versions
    for key in list(consonants.keys()):
        consonants[key.upper()] = [c.upper() for c in consonants[key]]
    
    result = list(name)
    consonant_indices = [i for i, char in enumerate(name) if char.isalpha() and char.lower() not in 'aeiou']
    
    if consonant_indices:
        # Replace 1-2 random consonants
        num_replacements = min(random.randint(1, 2), len(consonant_indices))
        indices_to_replace = random.sample(consonant_indices, num_replacements)
        
        for idx in indices_to_replace:
            char = name[idx]
            if char.lower() in consonants:
                result[idx] = random.choice(consonants[char.lower() if char.islower() else char.upper()])
    
    return ''.join(result)

def apply_swap_random_letter(name: str) -> str:
    """Swap random adjacent letters (not just consonants)"""
    if len(name) < 2:
        return name
    
    # Find all adjacent letter pairs (case-insensitive, any letters)
    swap_candidates = []
    for i in range(len(name) - 1):
        if name[i].isalpha() and name[i+1].isalpha() and name[i].lower() != name[i+1].lower():
            swap_candidates.append(i)
    
    if swap_candidates:
        idx = random.choice(swap_candidates)
        return name[:idx] + name[idx+1] + name[idx] + name[idx+2:]
    
    return name

def apply_remove_random_vowel(name: str) -> str:
    """Remove a random vowel"""
    vowels = 'aeiouAEIOU'
    vowel_indices = [i for i, char in enumerate(name) if char in vowels]
    
    if vowel_indices:
        idx = random.choice(vowel_indices)
        return name[:idx] + name[idx+1:]
    
    return name

def apply_remove_random_consonant(name: str) -> str:
    """Remove a random consonant"""
    consonant_indices = [i for i, char in enumerate(name) if char.isalpha() and char.lower() not in 'aeiou']
    
    if consonant_indices:
        idx = random.choice(consonant_indices)
        return name[:idx] + name[idx+1:]
    
    return name

def apply_duplicate_random_letter(name: str) -> str:
    """Duplicate a random letter"""
    if len(name) == 0:
        return name
    
    letter_indices = [i for i, char in enumerate(name) if char.isalpha()]
    
    if letter_indices:
        idx = random.choice(letter_indices)
        return name[:idx+1] + name[idx] + name[idx+1:]
    
    return name

def apply_insert_random_letter(name: str) -> str:
    """Insert a random letter"""
    if len(name) == 0:
        return random.choice('abcdefghijklmnopqrstuvwxyz')
    
    # Insert at random position
    idx = random.randint(0, len(name))
    random_letter = random.choice('abcdefghijklmnopqrstuvwxyz')
    
    # Preserve case context
    if idx > 0 and name[idx-1].isupper():
        random_letter = random_letter.upper()
    
    return name[:idx] + random_letter + name[idx:]

def apply_add_title_prefix(name: str) -> str:
    """Add a title prefix (Mr., Dr., etc.)"""
    prefixes = ['Mr.', 'Mrs.', 'Ms.', 'Dr.', 'Prof.', 'Rev.', 'Sir', 'Lady']
    return random.choice(prefixes) + " " + name

def apply_initial_only_first_name(name: str) -> str:
    """Use first name initial with last name (e.g., 'John Doe' -> 'J. Doe')"""
    parts = name.split()
    if len(parts) >= 2:
        parts[0] = parts[0][0] + "." if len(parts[0]) > 0 else parts[0]
        return " ".join(parts)
    elif len(parts) == 1 and len(parts[0]) > 1:
        return parts[0][0] + "."
    return name

def apply_shorten_to_initials(name: str) -> str:
    """Convert name to initials (e.g., 'John Doe' -> 'J. D.')"""
    parts = name.split()
    if len(parts) >= 2:
        initials = [part[0] + "." for part in parts if len(part) > 0]
        return " ".join(initials)
    elif len(parts) == 1 and len(parts[0]) > 1:
        return parts[0][0] + "."
    return name

def apply_rule_to_name(name: str, rule: str) -> str:
    """Apply a rule to a name"""
    rule_map = {
        # Character replacement
        'replace_spaces_with_special_characters': apply_replace_spaces_with_special_chars,
        'replace_double_letters': apply_replace_double_letters,
        'replace_random_vowels': apply_replace_random_vowels,
        'replace_random_consonants': apply_replace_random_consonants,
        
        # Character swapping
        'swap_adjacent_consonants': apply_swap_adjacent_consonants,
        'swap_adjacent_syllables': apply_swap_adjacent_syllables,
        'swap_random_letter': apply_swap_random_letter,
        
        # Character removal
        'delete_random_letter': apply_delete_random_letter,
        'remove_random_vowel': apply_remove_random_vowel,
        'remove_random_consonant': apply_remove_random_consonant,
        'remove_all_spaces': apply_remove_all_spaces,
        
        # Character insertion
        'duplicate_random_letter': apply_duplicate_random_letter,
        'insert_random_letter': apply_insert_random_letter,
        'add_title_prefix': apply_add_title_prefix,
        'add_title_suffix': apply_add_title_suffix,
        
        # Name formatting
        'initial_only_first_name': apply_initial_only_first_name,
        'shorten_to_initials': apply_shorten_to_initials,
        'abbreviate_name_parts': apply_abbreviate_name_parts,
        
        # Structure change
        'reorder_name_parts': apply_reorder_name_parts,
        
        # Aliases for validator rule names
        'replace_spaces_with_random_special_characters': apply_replace_spaces_with_special_chars,
        'replace_double_letters_with_single_letter': apply_replace_double_letters,
        'replace_random_vowel_with_random_vowel': apply_replace_random_vowels,
        'replace_random_consonant_with_random_consonant': apply_replace_random_consonants,
        'duplicate_random_letter_as_double_letter': apply_duplicate_random_letter,
        'add_random_leading_title': apply_add_title_prefix,
        'add_random_trailing_title': apply_add_title_suffix,
        'shorten_name_to_initials': apply_shorten_to_initials,
        'shorten_name_to_abbreviations': apply_abbreviate_name_parts,
        'name_parts_permutations': apply_reorder_name_parts,
    }
    func = rule_map.get(rule)
    return func(name) if func else name

# ============================================================================
# DOB Variations
# ============================================================================

def generate_dob_variations(dob: str, count: int = 15) -> List[str]:
    """Generate DOB variations"""
    try:
        base_date = datetime.strptime(dob, "%Y-%m-%d")
    except:
        base_date = datetime(1990, 1, 1)
    
    variations = []
    
    # ±1 day
    variations.append((base_date + timedelta(days=1)).strftime("%Y-%m-%d"))
    variations.append((base_date - timedelta(days=1)).strftime("%Y-%m-%d"))
    
    # ±3 days
    variations.append((base_date + timedelta(days=3)).strftime("%Y-%m-%d"))
    variations.append((base_date - timedelta(days=3)).strftime("%Y-%m-%d"))
    
    # ±30 days
    variations.append((base_date + timedelta(days=30)).strftime("%Y-%m-%d"))
    variations.append((base_date - timedelta(days=30)).strftime("%Y-%m-%d"))
    
    # ±90 days
    variations.append((base_date + timedelta(days=90)).strftime("%Y-%m-%d"))
    variations.append((base_date - timedelta(days=90)).strftime("%Y-%m-%d"))
    
    # ±365 days
    variations.append((base_date + timedelta(days=365)).strftime("%Y-%m-%d"))
    variations.append((base_date - timedelta(days=365)).strftime("%Y-%m-%d"))
    
    # Year+month only
    variations.append(base_date.strftime("%Y-%m"))
    
    # Fill remaining with random variations
    while len(variations) < count:
        days_offset = random.randint(-365, 365)
        new_date = base_date + timedelta(days=days_offset)
        variations.append(new_date.strftime("%Y-%m-%d"))
    
    return variations[:count]

# ============================================================================
# Address Variations
# ============================================================================

def generate_address_variations(address: str, count: int = 15) -> List[str]:
    """Generate address variations - simple approach"""
    # Extract city/country from address
    parts = address.split(',')
    if len(parts) >= 2:
        city = parts[0].strip()
        country = parts[-1].strip()
    else:
        city = address.split()[0] if address.split() else "Unknown"
        country = address.split()[-1] if address.split() else "Unknown"
    
    # Simple street names
    street_names = ["Main St", "Oak Ave", "Park Rd", "Elm St", "First Ave", 
                    "Second St", "Broadway", "Washington Ave", "Lincoln St"]
    
    # Simple building numbers
    building_numbers = list(range(1, 999))
    
    variations = []
    used = set()
    
    for i in range(count):
        street = random.choice(street_names)
        number = random.choice(building_numbers)
        addr = f"{number} {street}, {city}, {country}"
        
        if addr not in used:
            variations.append(addr)
            used.add(addr)
        else:
            # Add apartment number if duplicate
            apt = random.randint(1, 999)
            addr = f"{number} {street}, Apt {apt}, {city}, {country}"
            variations.append(addr)
            used.add(addr)
    
    return variations[:count]

def generate_uav_address(address: str) -> Dict:
    """
    Generate UAV (Unknown Attack Vector) address that looks valid but might fail geocoding.
    Returns: dict with 'address', 'label', 'latitude', 'longitude'
    """
    # Extract city/country from address
    parts = address.split(',')
    if len(parts) >= 2:
        city = parts[0].strip()
        country = parts[-1].strip()
    else:
        city = address.split()[0] if address.split() else "Unknown"
        country = address.split()[-1] if address.split() else "Unknown"
    
    # Generate an address with a potential issue (typo, abbreviation, etc.)
    uav_types = [
        ("typo", lambda: f"{random.randint(1, 999)} Main Str, {city}, {country}", "Common typo (Str vs St)"),
        ("abbreviation", lambda: f"{random.randint(1, 999)} Oak Av, {city}, {country}", "Local abbreviation (Av vs Ave)"),
        ("missing_direction", lambda: f"{random.randint(1, 999)} 1st St, {city}, {country}", "Missing street direction"),
        ("number_only", lambda: f"{random.randint(1, 999)}, {city}, {country}", "Number without street name"),
        ("abbreviated_st", lambda: f"{random.randint(1, 999)} Elm St., {city}, {country}", "Abbreviated with period"),
    ]
    
    uav_type, gen_func, label = random.choice(uav_types)
    uav_address = gen_func()
    
    # Generate realistic coordinates based on country (approximate)
    # Comprehensive country database with geographic centers
    # These are rough approximations - in production, use geocoding API
    country_coords = {
        # North America
        "USA": (39.8283, -98.5795), "United States": (39.8283, -98.5795),
        "US": (39.8283, -98.5795), "United States of America": (39.8283, -98.5795),
        "Canada": (56.1304, -106.3468), "Mexico": (23.6345, -102.5528),
        # Central America & Caribbean
        "Haiti": (18.9712, -72.2852), "Honduras": (15.2000, -86.2419),
        "Cuba": (21.5218, -77.7812), "Jamaica": (18.1096, -77.2975),
        "Guatemala": (15.7835, -90.2308), "Belize": (17.1899, -88.4976),
        "El Salvador": (13.7942, -88.8965), "Nicaragua": (12.2650, -85.2072),
        "Costa Rica": (9.7489, -83.7534), "Panama": (8.5380, -80.7821),
        "Dominican Republic": (18.7357, -70.1627), "Puerto Rico": (18.2208, -66.5901),
        # South America
        "Brazil": (-14.2350, -51.9253), "Argentina": (-38.4161, -63.6167),
        "Colombia": (4.5709, -74.2973), "Peru": (-9.1900, -75.0152),
        "Venezuela": (6.4238, -66.5897), "Chile": (-35.6751, -71.5430),
        "Ecuador": (-1.8312, -78.1834), "Bolivia": (-16.2902, -63.5887),
        "Paraguay": (-23.4425, -58.4438), "Uruguay": (-32.5228, -55.7658),
        # Europe
        "UK": (54.7024, -3.2766), "United Kingdom": (54.7024, -3.2766),
        "Britain": (54.7024, -3.2766), "Great Britain": (54.7024, -3.2766),
        "Germany": (51.1657, 10.4515), "France": (46.2276, 2.2137),
        "Spain": (40.4637, -3.7492), "Italy": (41.8719, 12.5674),
        "Russia": (61.5240, 105.3188), "Poland": (51.9194, 19.1451),
        "Netherlands": (52.1326, 5.2913), "Belgium": (50.5039, 4.4699),
        "Greece": (39.0742, 21.8243), "Portugal": (39.3999, -8.2245),
        "Sweden": (60.1282, 18.6435), "Norway": (60.4720, 8.4689),
        "Denmark": (56.2639, 9.5018), "Finland": (61.9241, 25.7482),
        "Switzerland": (46.8182, 8.2275), "Austria": (47.5162, 14.5501),
        "Czech Republic": (49.8175, 15.4730), "Romania": (45.9432, 24.9668),
        "Hungary": (47.1625, 19.5033), "Ukraine": (48.3794, 31.1656),
        "Turkey": (38.9637, 35.2433), "Ireland": (53.4129, -8.2439),
        # Asia
        "China": (35.8617, 104.1954), "India": (20.5937, 78.9629),
        "Japan": (36.2048, 138.2529), "South Korea": (35.9078, 127.7669),
        "North Korea": (40.3399, 127.5101), "Thailand": (15.8700, 100.9925),
        "Vietnam": (14.0583, 108.2772), "Philippines": (12.8797, 121.7740),
        "Indonesia": (-0.7893, 113.9213), "Malaysia": (4.2105, 101.9758),
        "Singapore": (1.3521, 103.8198), "Bangladesh": (23.6850, 90.3563),
        "Pakistan": (30.3753, 69.3451), "Afghanistan": (33.9391, 67.7100),
        "Iran": (32.4279, 53.6880), "Iraq": (33.2232, 43.6793),
        "Saudi Arabia": (23.8859, 45.0792), "UAE": (23.4241, 53.8478),
        "United Arab Emirates": (23.4241, 53.8478), "Israel": (31.0461, 34.8516),
        "Lebanon": (33.8547, 35.8623), "Jordan": (30.5852, 36.2384),
        "Syria": (34.8021, 38.9968), "Yemen": (15.5527, 48.5164),
        # Africa
        "Egypt": (26.8206, 30.8025), "Libya": (26.3351, 17.2283),
        "Sudan": (12.8628, 30.2176), "Ethiopia": (9.1450, 38.7667),
        "Kenya": (-0.0236, 37.9062), "Nigeria": (9.0820, 8.6753),
        "South Africa": (-30.5595, 22.9375), "Ghana": (7.9465, -1.0232),
        "Morocco": (31.7917, -7.0926), "Algeria": (28.0339, 1.6596),
        "Tunisia": (33.8869, 9.5375), "Mauritius": (-20.3484, 57.5522),
        "Gabon": (-0.8037, 11.6094), "Benin": (9.3077, 2.3158),
        "Namibia": (-22.9576, 18.4904), "Papua New Guinea": (-6.3150, 143.9555),
        # Additional sanctioned countries
        "South Sudan": (6.8770, 31.3070), "Central African Republic": (6.6111, 20.9394),
        "Democratic Republic of the Congo": (-4.0383, 21.7587), "DRC": (-4.0383, 21.7587),
        "Congo, Democratic Republic of the": (-4.0383, 21.7587), "Mali": (17.5707, -3.9962),
        "Angola": (-11.2027, 17.8739), "Burkina Faso": (12.2383, -1.5616),
        "Cameroon": (7.3697, 12.3547), "Ivory Coast": (7.5400, -5.5471),
        "Cote d'Ivoire": (7.5400, -5.5471), "British Virgin Islands": (18.4207, -64.6399),
        "Monaco": (43.7384, 7.4246), "Mozambique": (-18.6657, 35.5296),
        "Myanmar": (21.9162, 95.9560), "Laos": (19.8563, 102.4955),
        "Nepal": (28.3949, 84.1240), "Somalia": (5.1521, 46.1996),
        # Additional Cyrillic sanctioned regions
        "Belarus": (53.7098, 27.9534), "Bulgaria": (42.7339, 25.4858),
        "Crimea": (45.3388, 33.5000), "Donetsk": (48.0159, 37.8029),
        "Luhansk": (48.5740, 39.3078),
        # Oceania
        "Australia": (-25.2744, 133.7751), "New Zealand": (-40.9006, 174.8860),
        # Middle East (already listed above, keeping for organization)
        "Kuwait": (29.3117, 47.4818), "Qatar": (25.3548, 51.1839),
        "Bahrain": (25.9304, 50.6378), "Oman": (21.4735, 55.9754),
    }
    
    # Normalize country name for matching (lowercase, handle common variations)
    country_normalized = country.strip().lower()
    
    # Try to find country in our map (case-insensitive, partial matching)
    lat, lon = None, None
    for country_key, coords in country_coords.items():
        country_key_lower = country_key.lower()
        # Exact match or substring match (either direction)
        if (country_key_lower == country_normalized or
            country_key_lower in country_normalized or
            country_normalized in country_key_lower):
            lat, lon = coords
            # Add small random offset to make it unique (within ~50km)
            lat += random.uniform(-0.5, 0.5)
            lon += random.uniform(-0.5, 0.5)
            break
    
    # Fallback: Try to get approximate coordinates for unrecognized countries
    # Use a basic heuristic based on country name patterns
    if lat is None or lon is None:
        # For unknown countries, generate coordinates in reasonable ranges
        # Most countries are between -60 and 70 latitude
        lat = random.uniform(-35, 60)
        lon = random.uniform(-180, 180)
        # Log for debugging
        print(f"   ⚠️  Country '{country}' not found in database, using approximate coordinates")
    
    return {
        'address': uav_address,
        'label': label,
        'latitude': round(lat, 6),
        'longitude': round(lon, 6)
    }

# ============================================================================
# Non-Latin Script Detection and Variations
# ============================================================================

def detect_script(name: str) -> str:
    """Detect the script type of a name"""
    # Check for Arabic characters
    if re.search(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]', name):
        return 'arabic'
    # Check for Cyrillic characters
    if re.search(r'[\u0400-\u04FF\u0500-\u052F\u2DE0-\u2DFF\uA640-\uA69F]', name):
        return 'cyrillic'
    # Check for Chinese/Japanese/Korean characters
    if re.search(r'[\u4E00-\u9FFF\u3040-\u309F\u30A0-\u30FF\uAC00-\uD7AF]', name):
        return 'cjk'
    # Check if contains non-Latin characters
    if re.search(r'[^\x00-\x7F]', name):
        return 'non-latin'
    return 'latin'

def generate_non_latin_variations(name: str, script: str, count: int) -> List[str]:
    """Generate variations for non-Latin script names"""
    variations = []
    used = set([name.lower()])
    
    # Strategy 1: Script-specific transformations (keep original script) - PRIORITIZE THESE
    parts = name.split()
    
    # For Arabic/Cyrillic: Swap similar-looking characters, add/remove spaces
    if script in ['arabic', 'cyrillic']:
        # Swap adjacent parts
        if len(parts) >= 2:
            swapped = " ".join([parts[-1]] + parts[:-1])
            if swapped.lower() not in used:
                variations.append(swapped)
                used.add(swapped.lower())
        
        # Remove spaces (merge parts)
        if len(parts) >= 2:
            merged = "".join(parts)
            if merged.lower() not in used:
                variations.append(merged)
                used.add(merged.lower())
        
        # Add space in middle of long words
        for idx, part in enumerate(parts):
            if len(part) > 4:
                mid = len(part) // 2
                spaced = part[:mid] + " " + part[mid:]
                var = " ".join(parts[:idx] + [spaced] + parts[idx+1:])
                if var.lower() not in used:
                    variations.append(var)
                    used.add(var.lower())
                    break
        
        # Reverse parts order
        if len(parts) >= 2:
            reversed_parts = " ".join(parts[::-1])
            if reversed_parts.lower() not in used:
                variations.append(reversed_parts)
                used.add(reversed_parts.lower())
    
    # For CJK: Character-level variations
    if script == 'cjk':
        # Swap characters
        if len(parts) >= 2:
            swapped = " ".join([parts[-1]] + parts[:-1])
            if swapped.lower() not in used:
                variations.append(swapped)
                used.add(swapped.lower())
    
    # Strategy 2: Transliterate and generate variations (mix with script-specific)
    transliterated_vars = []
    if UNIDECODE_AVAILABLE and len(variations) < count:
        transliterated = unidecode(name)
        if transliterated and transliterated != name:
            # Generate variations on transliterated version (limit to avoid filling all slots)
            latin_vars = generate_name_variations(transliterated, limit=max(count - len(variations), count // 2))
            # Keep transliterated variations (valid for non-Latin names)
            for var in latin_vars:
                if var.lower() not in used:
                    transliterated_vars.append(var)
                    used.add(var.lower())
    
    # Mix script-specific and transliterated variations (prioritize script-specific)
    # Add script-specific first, then interleave with transliterated
    final_variations = variations[:]  # Copy script-specific variations
    translit_idx = 0
    while len(final_variations) < count and translit_idx < len(transliterated_vars):
        final_variations.append(transliterated_vars[translit_idx])
        translit_idx += 1
    variations = final_variations
    
    # Strategy 3: Character-level transformations (work for all scripts)
    # Generate variations by removing/duplicating/inserting characters
    max_char_variations = count
    attempts = 0
    while len(variations) < count and attempts < count * 3:
        attempts += 1
        
        # Remove a character
        if len(name) > 2:
            idx = random.randint(0, len(name) - 1)
            var = name[:idx] + name[idx+1:]
            if var and var.lower() not in used:
                variations.append(var)
                used.add(var.lower())
                if len(variations) >= count:
                    break
        
        # Duplicate a character
        if len(name) > 1:
            idx = random.randint(0, len(name) - 1)
            var = name[:idx+1] + name[idx] + name[idx+1:]
            if var.lower() not in used:
                variations.append(var)
                used.add(var.lower())
                if len(variations) >= count:
                    break
        
        # Swap adjacent characters (if not already done)
        if len(name) >= 2:
            idx = random.randint(0, len(name) - 2)
            var = name[:idx] + name[idx+1] + name[idx] + name[idx+2:]
            if var.lower() not in used:
                variations.append(var)
                used.add(var.lower())
                if len(variations) >= count:
                    break
    
    # Strategy 4: Add more transliterated variations if we still need more
    if UNIDECODE_AVAILABLE and len(variations) < count:
        transliterated = unidecode(name)
        if transliterated and transliterated != name:
            # Get more transliterated variations
            remaining = count - len(variations)
            more_latin_vars = generate_name_variations(transliterated, limit=remaining * 3)
            for var in more_latin_vars:
                if len(variations) >= count:
                    break
                if var.lower() not in used:
                    variations.append(var)
                    used.add(var.lower())
    
    # Strategy 5: If still not enough, create simple variations by modifying parts
    if len(variations) < count:
        remaining = count - len(variations)
        for i in range(remaining * 2):
            if len(variations) >= count:
                break
            parts = name.split()
            if len(parts) >= 2:
                # Try different part combinations
                if i % 3 == 0:
                    var = " ".join(parts[::-1])
                elif i % 3 == 1:
                    var = "".join(parts)
                else:
                    var = parts[-1] + " " + " ".join(parts[:-1])
            elif len(parts) == 1 and len(parts[0]) > 1:
                # For single word, try removing characters from different positions
                word = parts[0]
                idx = (i * 3) % (len(word) - 1) + 1
                var = word[:idx] + word[idx+1:]
            else:
                continue
            
            if var and var.lower() not in used:
                variations.append(var)
                used.add(var.lower())
    
    return variations[:count]

# ============================================================================
# Main Generation Function
# ============================================================================

def generate_name_variations_clean(original_name: str, variation_count: int, 
                                   rule_percentage: float, rules: List[str]) -> List[str]:
    """Generate name variations - rule-based and non-rule-based"""
    rule_based_count = int(variation_count * rule_percentage)
    non_rule_count = variation_count - rule_based_count
    
    variations = []
    used_variations = set()
    
    # Detect script type
    script = detect_script(original_name)
    is_non_latin = (script != 'latin')
    
    # Generate rule-based variations
    print(f"   🔧 Rule-based: {rule_based_count}")
    for i in range(rule_based_count):
        if rules:
            rule = random.choice(rules)
            var = apply_rule_to_name(original_name, rule)
            
            # Ensure uniqueness
            attempts = 0
            while var.lower() in used_variations and attempts < 10:
                var = apply_rule_to_name(original_name, rule) + str(random.randint(1, 99))
                attempts += 1
            
            if var.lower() not in used_variations:
                variations.append(var)
                used_variations.add(var.lower())
    
    # Generate non-rule variations
    print(f"   🔬 Non-rule: {non_rule_count} (using name_variations.py)")
    if non_rule_count > 0:
        # For non-Latin scripts, skip name_variations.py and go straight to script-specific variations
        if is_non_latin:
            print(f"   🌍 Detected {script} script - using script-specific variations")
            non_latin_vars = generate_non_latin_variations(original_name, script, non_rule_count * 2)
            
            for var in non_latin_vars:
                if len(variations) >= variation_count:
                    break
                if var.lower() not in used_variations:
                    variations.append(var)
                    used_variations.add(var.lower())
        else:
            # For Latin scripts, use name_variations.py
            non_rule_vars = generate_name_variations(original_name, limit=non_rule_count * 2)
            
            for var in non_rule_vars:
                if len(variations) >= variation_count:
                    break
                if var.lower() not in used_variations:
                    variations.append(var)
                    used_variations.add(var.lower())
    
    # Final fallback - only if we still don't have enough
    if len(variations) < variation_count:
        if is_non_latin:
            # For non-Latin, ALWAYS use script-specific variations - NEVER numeric suffixes
            remaining = variation_count - len(variations)
            print(f"   🌍 Generating {remaining} more {script} script variations (no numeric suffixes)")
            
            # Generate many more variations to ensure we have enough
            non_latin_vars = generate_non_latin_variations(original_name, script, remaining * 5)
            
            for var in non_latin_vars:
                if len(variations) >= variation_count:
                    break
                if var.lower() not in used_variations:
                    variations.append(var)
                    used_variations.add(var.lower())
            
            # If still not enough, create character-level variations manually
            if len(variations) < variation_count:
                parts = original_name.split()
                attempts = 0
                while len(variations) < variation_count and attempts < 200:
                    attempts += 1
                    
                    if len(parts) >= 2:
                        # Try different part orders
                        if attempts % 4 == 0:
                            var = " ".join(parts[::-1])
                        elif attempts % 4 == 1:
                            var = "".join(parts)
                        elif attempts % 4 == 2:
                            var = parts[-1] + " " + " ".join(parts[:-1])
                        else:
                            var = " ".join([parts[1]] + [parts[0]] + parts[2:]) if len(parts) > 2 else " ".join(parts[::-1])
                    elif len(parts) == 1 and len(parts[0]) > 1:
                        # For single word, remove characters from different positions
                        word = parts[0]
                        idx = attempts % (len(word) - 1) + 1
                        var = word[:idx] + word[idx+1:]
                    else:
                        continue
                    
                    if var and var.lower() not in used_variations:
                        variations.append(var)
                        used_variations.add(var.lower())
        else:
            # For Latin, only fall back to numeric suffixes as absolute last resort
            while len(variations) < variation_count:
                var = original_name + str(len(variations))
                if var.lower() not in used_variations:
                    variations.append(var)
                    used_variations.add(var.lower())
    
    return variations[:variation_count]

# ============================================================================
# Main Function
# ============================================================================

def generate_variations(synapse: IdentitySynapse) -> Dict:
    """
    Generate variations for all identities.
    Returns different structure for UAV seed vs normal seeds.
    """
    requirements = parse_query_template(synapse.query_template)
    
    print("=" * 80)
    print("CLEAN VARIATION GENERATOR - NO VALIDATION, NO SCORING")
    print("=" * 80)
    print(f"\n📋 Requirements:")
    print(f"   Variation count: {requirements['variation_count']}")
    print(f"   Rule percentage: {requirements['rule_percentage']*100:.0f}%")
    print(f"   Rules: {requirements['rules']}")
    if requirements['uav_seed_name']:
        print(f"   🎯 UAV Seed: {requirements['uav_seed_name']}")
    print()
    
    all_variations = {}
    uav_seed_name = requirements['uav_seed_name']
    
    for identity in synapse.identity:
        name = identity[0] if len(identity) > 0 else "Unknown"
        dob = identity[1] if len(identity) > 1 else "1990-01-01"
        address = identity[2] if len(identity) > 2 else "Unknown"
        
        print(f"🔄 Processing: {name}")
        is_uav_seed = (uav_seed_name and name.lower() == uav_seed_name.lower())
        
        if is_uav_seed:
            print(f"   🎯 This is the UAV seed - will include UAV data")
        
        # Generate variations
        name_vars = generate_name_variations_clean(
            original_name=name,
            variation_count=requirements['variation_count'],
            rule_percentage=requirements['rule_percentage'],
            rules=requirements['rules']
        )
        
        dob_vars = generate_dob_variations(dob, requirements['variation_count'])
        address_vars = generate_address_variations(address, requirements['variation_count'])
        
        # Combine into [name, dob, address] format
        combined = []
        for i in range(requirements['variation_count']):
            combined.append([
                name_vars[i] if i < len(name_vars) else name,
                dob_vars[i] if i < len(dob_vars) else dob,
                address_vars[i] if i < len(address_vars) else address
            ])
        
        # Phase 3: Return different structure for UAV seed
        if is_uav_seed:
            # Generate UAV address
            uav_data = generate_uav_address(address)
            print(f"   🎯 Generated UAV: {uav_data['address']} ({uav_data['label']})")
            print(f"      Coordinates: ({uav_data['latitude']}, {uav_data['longitude']})")
            
            # UAV seed structure: {name: {variations: [...], uav: {...}}}
            all_variations[name] = {
                'variations': combined,
                'uav': uav_data
            }
        else:
            # Normal structure: {name: [[name, dob, addr], ...]}
            all_variations[name] = combined
        
        print(f"   ✅ Generated {len(combined)} variations\n")
    
    return all_variations

# ============================================================================
# Entry Point
# ============================================================================

def main():
    import sys
    
    if len(sys.argv) < 2:
        input_file = "example_synapse.json"
    else:
        input_file = sys.argv[1]
    
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"📂 Loading synapse from: {input_file}\n")
    
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    synapse = IdentitySynapse(
        identity=data['identity'],
        query_template=data['query_template'],
        timeout=data.get('timeout', 120.0)
    )
    
    variations = generate_variations(synapse)
    
    # Print results
    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)
    
    for original_name, var_list in variations.items():
        print(f"\n📝 Variations for: {original_name}")
        for i, var in enumerate(var_list, 1):
            print(f"   {i}. {var[0]} | {var[1]} | {var[2]}")
    
    # Output JSON in EXACT format that miners send to validators
    # Format: {name: [[name_var, dob_var, address_var], ...]}
    output_data = variations
    
    # If output file specified, save it
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Saved to: {output_file}")
        print(f"   Format: Miner response format (synapse.variations)")
    else:
        # Print JSON to stdout (exactly like miner sends)
        print("\n" + "=" * 80)
        print("JSON OUTPUT (Miner Format)")
        print("=" * 80)
        print(json.dumps(output_data, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()

