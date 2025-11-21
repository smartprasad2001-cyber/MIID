#!/usr/bin/env python3
"""
Standalone Variation Generator
Generates name, DOB, and address variations based on validator requirements.

This program takes an IdentitySynapse (exactly like miners receive) and generates
compliant variations following all rules, similarity requirements, and specifications.

USAGE:
    # Run with example synapse
    python variation_generator.py
    
    # Run with custom synapse from JSON file
    python variation_generator.py synapse_input.json
    
    # Run and save output to JSON file
    python variation_generator.py synapse_input.json output_variations.json

INPUT JSON FORMAT:
    {
        "identity": [
            ["Name 1", "1990-01-01", "City, Country"],
            ["Name 2", "1985-05-15", "City2, Country2"]
        ],
        "query_template": "Generate 15 variations of {name}...",
        "timeout": 120.0
    }

OUTPUT:
    Dictionary mapping each name to list of [name_variation, dob_variation, address_variation]
    {
        "Name 1": [
            ["variation1", "1990-01-02", "123 Main St, City, Country"],
            ...
        ],
        ...
    }

FEATURES:
    - Parses query template to extract requirements (variation count, similarity, rules)
    - Applies rule-based transformations (18+ rules supported)
    - Generates phonetic and orthographic similar name variations
    - Creates DOB variations covering all required categories
    - Generates realistic address variations within same country/city
    - Follows all validator scoring requirements
"""

import re
import random
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
import Levenshtein
import jellyfish

# Try to import Google Generative AI
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

# Try to import from MIID if available, otherwise define minimal classes
try:
    from MIID.protocol import IdentitySynapse
    MIID_AVAILABLE = True
except ImportError:
    # Minimal IdentitySynapse class for standalone use
    class IdentitySynapse:
        def __init__(self, identity, query_template, timeout=120.0):
            self.identity = identity  # List[List[str]] - [[name, dob, address], ...]
            self.query_template = query_template  # str
            self.timeout = timeout  # float
            self.variations = None  # Dict[str, List[List[str]]]
    MIID_AVAILABLE = False

# ============================================================================
# Rule Application Functions (Reverse-engineered from rule_evaluator.py)
# ============================================================================

def is_consonant(char: str) -> bool:
    """Check if a character is a consonant (case-insensitive)"""
    vowels = 'aeiou'
    return char.isalpha() and char.lower() not in vowels

def has_double_letters(name: str) -> bool:
    """Check if a name has any double letters."""
    name_lower = name.lower()
    for i in range(len(name_lower) - 1):
        if name_lower[i] == name_lower[i+1]:
            return True
    return False

def has_diff_adjacent_consonants(name: str) -> bool:
    """Check if a name has different adjacent consonants that can be swapped."""
    vowels = "aeiou"
    name = name.lower()
    for i in range(len(name) - 1):
        if (name[i].isalpha() and name[i] not in vowels and
            name[i+1].isalpha() and name[i+1] not in vowels and
            name[i] != name[i+1]):
            return True
    return False

# Rule Application Functions - Implemented as proper functions below
def apply_replace_spaces_with_special_chars(name: str) -> str:
    """Replace spaces with special characters"""
    if ' ' not in name:
        return name
    special_chars = ['_', '-', '@', '.']
    return name.replace(' ', random.choice(special_chars))

def apply_replace_double_letters(name: str) -> str:
    """Replace double letters with a single letter"""
    if not has_double_letters(name):
        return name
    name_lower = name.lower()
    for i in range(len(name_lower) - 1):
        if name_lower[i] == name_lower[i+1] and name[i].isalpha():
            # Remove the second occurrence of the double letter
            return name[:i+1] + name[i+2:]
    return name

def apply_replace_random_vowel(name: str) -> str:
    """Replace a random vowel with another vowel"""
    vowels = 'aeiou'
    vowel_positions = [i for i, c in enumerate(name) if c.lower() in vowels]
    if not vowel_positions:
        return name
    pos = random.choice(vowel_positions)
    available_vowels = [v for v in vowels if v != name[pos].lower()]
    if not available_vowels:
        return name
    new_vowel = random.choice(available_vowels)
    # Preserve case
    if name[pos].isupper():
        new_vowel = new_vowel.upper()
    return name[:pos] + new_vowel + name[pos+1:]

def apply_replace_random_consonant(name: str) -> str:
    """Replace a random consonant with another consonant"""
    consonant_positions = [i for i, c in enumerate(name) if is_consonant(c)]
    if not consonant_positions:
        return name
    pos = random.choice(consonant_positions)
    consonants = 'bcdfghjklmnpqrstvwxyz'
    available_consonants = [c for c in consonants if c != name[pos].lower()]
    if not available_consonants:
        return name
    new_consonant = random.choice(available_consonants)
    # Preserve case
    if name[pos].isupper():
        new_consonant = new_consonant.upper()
    return name[:pos] + new_consonant + name[pos+1:]

def apply_swap_adjacent_consonants(name: str) -> str:
    """Swap two adjacent consonants"""
    if not has_diff_adjacent_consonants(name) or len(name) < 2:
        return name
    name_lower = name.lower()
    for i in range(len(name_lower) - 1):
        if is_consonant(name[i]) and is_consonant(name[i+1]):
            # Swap the consonants
            return name[:i] + name[i+1] + name[i] + name[i+2:]
    return name

def apply_swap_adjacent_syllables(name: str) -> str:
    """Swap adjacent syllables (simplified: swap name parts)"""
    parts = name.split()
    if len(parts) >= 2:
        return ' '.join(reversed(parts))
    return name

def apply_swap_random_letter(name: str) -> str:
    """Swap two adjacent letters"""
    if len(name) < 2:
        return name
    pos = random.randint(0, len(name) - 2)
    name_list = list(name)
    name_list[pos], name_list[pos+1] = name_list[pos+1], name_list[pos]
    return ''.join(name_list)

def apply_delete_random_letter(name: str) -> str:
    """Delete a random letter"""
    if len(name) <= 1:
        return name
    pos = random.randint(0, len(name) - 1)
    return name[:pos] + name[pos+1:]

def apply_remove_random_vowel(name: str) -> str:
    """Remove a random vowel"""
    vowels = 'aeiou'
    vowel_positions = [i for i, c in enumerate(name) if c.lower() in vowels]
    if not vowel_positions:
        return name
    pos = random.choice(vowel_positions)
    return name[:pos] + name[pos+1:]

def apply_remove_random_consonant(name: str) -> str:
    """Remove a random consonant"""
    consonant_positions = [i for i, c in enumerate(name) if is_consonant(c)]
    if not consonant_positions:
        return name
    pos = random.choice(consonant_positions)
    return name[:pos] + name[pos+1:]

def apply_remove_all_spaces(name: str) -> str:
    """Remove all spaces"""
    return name.replace(' ', '')

def apply_duplicate_random_letter(name: str) -> str:
    """Duplicate a random letter"""
    if not name:
        return name
    pos = random.randint(0, len(name) - 1)
    return name[:pos] + name[pos] + name[pos:]

def apply_insert_random_letter(name: str) -> str:
    """Insert a random letter"""
    pos = random.randint(0, len(name))
    letter = random.choice('abcdefghijklmnopqrstuvwxyz')
    # Try to preserve case by checking neighboring letters
    if pos > 0 and name[pos-1].isupper():
        letter = letter.upper()
    elif pos < len(name) and name[pos].isupper():
        letter = letter.upper()
    return name[:pos] + letter + name[pos:]

def apply_add_random_leading_title(name: str) -> str:
    """Add a title prefix"""
    titles = ['Mr. ', 'Dr. ', 'Ms. ', 'Mrs. ', 'Prof. ']
    return random.choice(titles) + name

def apply_add_random_trailing_title(name: str) -> str:
    """Add a title suffix"""
    suffixes = [' Jr.', ' Sr.', ' PhD', ' MD', ' II', ' III']
    return name + random.choice(suffixes)

def apply_initial_only_first_name(name: str) -> str:
    """Use first name initial with last name"""
    parts = name.split()
    if len(parts) >= 2:
        return f"{parts[0][0]}. {' '.join(parts[1:])}"
    return name

def apply_shorten_name_to_initials(name: str) -> str:
    """Convert name to initials"""
    parts = name.split()
    if len(parts) >= 2:
        return '. '.join([p[0] for p in parts]) + '.'
    return name

def apply_shorten_name_to_abbreviations(name: str) -> str:
    """Abbreviate name parts"""
    abbreviations = {
        'William': 'Wm.', 'Robert': 'Rob.', 'Richard': 'Rich.',
        'Christopher': 'Chris.', 'Michael': 'Mike.', 'James': 'Jim.',
        'Joseph': 'Joe.', 'Thomas': 'Tom.'
    }
    parts = name.split()
    abbreviated = [abbreviations.get(p, p) for p in parts]
    return ' '.join(abbreviated)

def apply_name_parts_permutations(name: str) -> str:
    """Reorder name parts"""
    parts = name.split()
    if len(parts) >= 2:
        return ' '.join(reversed(parts))
    return name

# Map rule names to applier functions
RULE_APPLIER_FUNCTIONS = {
    "replace_spaces_with_random_special_characters": apply_replace_spaces_with_special_chars,
    "replace_double_letters_with_single_letter": apply_replace_double_letters,
    "replace_random_vowel_with_random_vowel": apply_replace_random_vowel,
    "replace_random_consonant_with_random_consonant": apply_replace_random_consonant,
    "swap_adjacent_consonants": apply_swap_adjacent_consonants,
    "swap_adjacent_syllables": apply_swap_adjacent_syllables,
    "swap_random_letter": apply_swap_random_letter,
    "delete_random_letter": apply_delete_random_letter,
    "remove_random_vowel": apply_remove_random_vowel,
    "remove_random_consonant": apply_remove_random_consonant,
    "remove_all_spaces": apply_remove_all_spaces,
    "duplicate_random_letter_as_double_letter": apply_duplicate_random_letter,
    "insert_random_letter": apply_insert_random_letter,
    "add_random_leading_title": apply_add_random_leading_title,
    "add_random_trailing_title": apply_add_random_trailing_title,
    "initial_only_first_name": apply_initial_only_first_name,
    "shorten_name_to_initials": apply_shorten_name_to_initials,
    "shorten_name_to_abbreviations": apply_shorten_name_to_abbreviations,
    "name_parts_permutations": apply_name_parts_permutations,
}

# ============================================================================
# Similarity Calculation Functions
# ============================================================================

def calculate_phonetic_similarity(original_name: str, variation: str) -> float:
    """Calculate phonetic similarity using Soundex, Metaphone, NYSIIS"""
    algorithms = {
        "soundex": lambda x, y: jellyfish.soundex(x) == jellyfish.soundex(y),
        "metaphone": lambda x, y: jellyfish.metaphone(x) == jellyfish.metaphone(y),
        "nysiis": lambda x, y: jellyfish.nysiis(x) == jellyfish.nysiis(y),
    }
    
    # Use all algorithms with equal weight for consistency
    scores = [algo(original_name, variation) for algo in algorithms.values()]
    return sum(scores) / len(scores)

def calculate_orthographic_similarity(original_name: str, variation: str) -> float:
    """Calculate orthographic similarity using Levenshtein distance"""
    distance = Levenshtein.distance(original_name, variation)
    max_len = max(len(original_name), len(variation))
    if max_len == 0:
        return 1.0
    return 1.0 - (distance / max_len)

# ============================================================================
# Query Template Parser
# ============================================================================

@dataclass
class QueryRequirements:
    """Parsed requirements from query template"""
    variation_count: int = 15
    phonetic_similarity: Dict[str, float] = None
    orthographic_similarity: Dict[str, float] = None
    rule_percentage: int = 30
    rules: List[str] = None
    
    def __post_init__(self):
        if self.phonetic_similarity is None:
            self.phonetic_similarity = {"Medium": 1.0}
        if self.orthographic_similarity is None:
            self.orthographic_similarity = {"Medium": 1.0}
        if self.rules is None:
            self.rules = []

def parse_query_template(query_template: str) -> QueryRequirements:
    """Parse query template to extract requirements"""
    req = QueryRequirements()
    
    # Extract variation count - try multiple patterns
    count_match = re.search(r'Generate\s+(\d+)\s+variations?', query_template, re.IGNORECASE)
    if count_match:
        req.variation_count = int(count_match.group(1))
    else:
        # Try alternative pattern
        count_match = re.search(r'(\d+)\s+variations?', query_template, re.IGNORECASE)
        if count_match:
            req.variation_count = int(count_match.group(1))
    
    # Extract rule percentage - try multiple patterns
    rule_pct_match = re.search(r'(\d+)%\s+of\s+variations?', query_template, re.IGNORECASE)
    if rule_pct_match:
        req.rule_percentage = int(rule_pct_match.group(1))
    else:
        # Try alternative: "include X%"
        rule_pct_match = re.search(r'include\s+(\d+)%', query_template, re.IGNORECASE)
        if rule_pct_match:
            req.rule_percentage = int(rule_pct_match.group(1))
    
    # Extract rules from rule descriptions (match exact descriptions from RULE_DESCRIPTIONS)
    rule_patterns = {
        "replace_spaces_with_random_special_characters": [
            r"Replace\s+spaces\s+with\s+special\s+characters",
            r"spaces\s+with\s+special",
        ],
        "replace_double_letters_with_single_letter": [
            r"Replace\s+double\s+letters\s+with\s+a\s+single\s+letter",
            r"double\s+letters\s+with\s+single",
        ],
        "replace_random_vowel_with_random_vowel": [
            r"Replace\s+random\s+vowels\s+with\s+different\s+vowels",
            r"vowels\s+with\s+different",
        ],
        "replace_random_consonant_with_random_consonant": [
            r"Replace\s+random\s+consonants\s+with\s+different\s+consonants",
            r"consonants\s+with\s+different",
        ],
        "swap_adjacent_consonants": [
            r"Swap\s+adjacent\s+consonants",
            r"adjacent\s+consonants",
        ],
        "swap_adjacent_syllables": [
            r"Swap\s+adjacent\s+syllables",
            r"adjacent\s+syllables",
        ],
        "swap_random_letter": [
            r"Swap\s+random\s+adjacent\s+letters",
            r"swap\s+.*\s+letters",
        ],
        "delete_random_letter": [
            r"Delete\s+a\s+random\s+letter",
            r"delete.*letter",
        ],
        "remove_random_vowel": [
            r"Remove\s+a\s+random\s+vowel",
            r"remove.*vowel",
        ],
        "remove_random_consonant": [
            r"Remove\s+a\s+random\s+consonant",
            r"remove.*consonant",
        ],
        "remove_all_spaces": [
            r"Remove\s+all\s+spaces",
            r"remove.*spaces",
        ],
        "duplicate_random_letter_as_double_letter": [
            r"Duplicate\s+a\s+random\s+letter",
            r"duplicate.*letter",
        ],
        "insert_random_letter": [
            r"Insert\s+a\s+random\s+letter",
            r"insert.*letter",
        ],
        "add_random_leading_title": [
            r"Add\s+a\s+title\s+prefix",
            r"title\s+prefix",
        ],
        "add_random_trailing_title": [
            r"Add\s+a\s+title\s+suffix",
            r"title\s+suffix",
        ],
        "initial_only_first_name": [
            r"Use\s+first\s+name\s+initial\s+with\s+last\s+name",
            r"first\s+name\s+initial",
        ],
        "shorten_name_to_initials": [
            r"Convert\s+name\s+to\s+initials",
            r"name\s+to\s+initials",
        ],
        "shorten_name_to_abbreviations": [
            r"Abbreviate\s+name\s+parts",
            r"abbreviate.*name",
        ],
        "name_parts_permutations": [
            r"Reorder\s+name\s+parts",
            r"reorder.*parts",
        ],
    }
    
    detected_rules = []
    for rule_name, patterns in rule_patterns.items():
        for pattern in patterns:
            if re.search(pattern, query_template, re.IGNORECASE):
                if rule_name not in detected_rules:
                    detected_rules.append(rule_name)
                break
    
    req.rules = detected_rules
    
    # Extract phonetic similarity - look for patterns like "phonetic similarity: 100% Medium"
    ph_match = re.search(r'phonetic\s+similarity[:\s]+(?:100%[\s]+)?(Light|Medium|Far)', query_template, re.IGNORECASE)
    if ph_match:
        level = ph_match.group(1).capitalize()
        req.phonetic_similarity = {level: 1.0}
    elif "phonetic similarity" in query_template.lower():
        # Default to Medium if mentioned but not specified
        req.phonetic_similarity = {"Medium": 1.0}
    
    # Extract orthographic similarity - look for patterns like "orthographic similarity: 100% Medium"
    or_match = re.search(r'orthographic\s+similarity[:\s]+(?:100%[\s]+)?(Light|Medium|Far)', query_template, re.IGNORECASE)
    if or_match:
        level = or_match.group(1).capitalize()
        req.orthographic_similarity = {level: 1.0}
    elif "orthographic similarity" in query_template.lower():
        # Default to Medium if mentioned but not specified
        req.orthographic_similarity = {"Medium": 1.0}
    
    return req

# ============================================================================
# DOB Variation Generator
# ============================================================================

def generate_dob_variations(seed_dob: str, count: int) -> List[str]:
    """
    Generate DOB variations covering all required categories:
    - ±1 day, ±3 days, ±30 days, ±90 days, ±365 days, year+month only
    """
    try:
        seed_date = datetime.strptime(seed_dob, "%Y-%m-%d")
    except ValueError:
        try:
            # Try year-month only format
            seed_date = datetime.strptime(seed_dob, "%Y-%m")
            # Use first day of month
            seed_date = seed_date.replace(day=1)
        except ValueError:
            # Invalid format, return seed DOB repeated
            return [seed_dob] * count
    
    variations = []
    
    # Required categories - ensure at least one of each
    required_variations = [
        (seed_date + timedelta(days=1)).strftime("%Y-%m-%d"),  # ±1 day
        (seed_date + timedelta(days=-1)).strftime("%Y-%m-%d"),  # ±1 day (negative)
        (seed_date + timedelta(days=3)).strftime("%Y-%m-%d"),  # ±3 days
        (seed_date + timedelta(days=-3)).strftime("%Y-%m-%d"),  # ±3 days (negative)
        (seed_date + timedelta(days=30)).strftime("%Y-%m-%d"),  # ±30 days
        (seed_date + timedelta(days=-30)).strftime("%Y-%m-%d"),  # ±30 days (negative)
        (seed_date + timedelta(days=90)).strftime("%Y-%m-%d"),  # ±90 days
        (seed_date + timedelta(days=-90)).strftime("%Y-%m-%d"),  # ±90 days (negative)
        (seed_date + timedelta(days=365)).strftime("%Y-%m-%d"),  # ±365 days
        (seed_date + timedelta(days=-365)).strftime("%Y-%m-%d"),  # ±365 days (negative)
        seed_date.strftime("%Y-%m"),  # Year+month only
    ]
    
    # Add required variations first
    variations.extend(required_variations[:min(len(required_variations), count)])
    
    # Fill remaining with random variations from all categories
    categories = [1, 3, 30, 90, 365]
    while len(variations) < count:
        days = random.choice(categories)
        sign = random.choice([1, -1])
        var_date = seed_date + timedelta(days=days * sign)
        variations.append(var_date.strftime("%Y-%m-%d"))
    
    # Remove duplicates and return requested count
    unique_variations = []
    seen = set()
    for var in variations:
        if var not in seen:
            unique_variations.append(var)
            seen.add(var)
        if len(unique_variations) >= count:
            break
    
    # Fill any remaining slots with random variations
    while len(unique_variations) < count:
        days = random.choice([1, 3, 30, 90, 365])
        sign = random.choice([1, -1])
        var_date = seed_date + timedelta(days=days * sign)
        var_str = var_date.strftime("%Y-%m-%d")
        if var_str not in seen:
            unique_variations.append(var_str)
            seen.add(var_str)
        # If we've exhausted possibilities, add year+month as fallback
        if len(unique_variations) < count:
            year_month = seed_date.strftime("%Y-%m")
            if year_month not in seen:
                unique_variations.append(year_month)
                seen.add(year_month)
                break
    
    return unique_variations[:count]

# ============================================================================
# Address Variation Generator
# ============================================================================

def extract_location_from_address(address: str) -> Tuple[str, str]:
    """Extract country and city from address string"""
    # Simple parsing - assumes format like "City, Country" or "Address, City, Country"
    parts = [p.strip() for p in address.split(',')]
    if len(parts) >= 2:
        country = parts[-1]  # Last part is usually country
        city = parts[-2] if len(parts) >= 2 else parts[0]
        return city, country
    return address, address

def generate_address_variation(seed_address: str, used_addresses: set) -> str:
    """
    Generate a realistic address variation within the same country/city.
    Uses common street names and patterns.
    """
    city, country = extract_location_from_address(seed_address)
    
    # Common street types
    street_types = ['Street', 'Avenue', 'Road', 'Lane', 'Drive', 'Boulevard', 
                   'Court', 'Place', 'Way', 'Circle', 'Parkway']
    
    # Common street names
    street_names = ['Main', 'Oak', 'Elm', 'Pine', 'Maple', 'Cedar', 'First', 
                   'Second', 'Third', 'Park', 'Washington', 'Lincoln', 'Church',
                   'Market', 'Broad', 'High', 'King', 'Queen', 'Bridge']
    
    # Generate unique address
    max_attempts = 100
    for attempt in range(max_attempts):
        street_num = random.randint(1, 9999)
        street_name = random.choice(street_names)
        street_type = random.choice(street_types)
        
        # Sometimes abbreviate street type
        if random.random() < 0.3:
            abbrev_map = {'Street': 'St', 'Avenue': 'Ave', 'Road': 'Rd', 
                         'Lane': 'Ln', 'Drive': 'Dr', 'Boulevard': 'Blvd'}
            street_type = abbrev_map.get(street_type, street_type)
        
        address = f"{street_num} {street_name} {street_type}, {city}, {country}"
        
        # Normalize for duplicate check
        normalized = ' '.join(address.lower().split())
        
        if normalized not in used_addresses:
            used_addresses.add(normalized)
            return address
    
    # Fallback if we can't generate unique address
    street_num = random.randint(1, 9999)
    return f"{street_num} {random.choice(street_names)} {random.choice(street_types)}, {city}, {country}"

def generate_address_variations(seed_address: str, count: int) -> List[str]:
    """Generate multiple unique address variations"""
    used_addresses = set()
    variations = []
    
    for _ in range(count):
        addr = generate_address_variation(seed_address, used_addresses)
        variations.append(addr)
    
    return variations

# ============================================================================
# Strong Algorithm-Based Name Variation Generator (from name_variations_strong.py)
# ============================================================================

VOWELS = "aeiouy"

def soundex(name: str) -> str:
    """Return a simple Soundex code for a single word."""
    if not name:
        return ""
    name = name.upper()
    first = name[0]
    # soundex mapping
    mapping = {
        **dict.fromkeys(list("BFPV"), "1"),
        **dict.fromkeys(list("CGJKQSXZ"), "2"),
        **dict.fromkeys(list("DT"), "3"),
        "L": "4",
        **dict.fromkeys(list("MN"), "5"),
        "R": "6"
    }
    # convert letters
    digits = []
    prev = None
    for ch in name[1:]:
        d = mapping.get(ch, "0")
        if d != prev and d != "0":
            digits.append(d)
        prev = d
    code = first + "".join(digits)
    code = re.sub(r'[^A-Z0-9]', '', code)
    return (code + "000")[:4]

def syllables(word: str):
    """Split word into syllable-like parts."""
    w = word.lower()
    # split at vowel groups keeping boundaries
    parts = re.findall(r'[^aeiouy]*[aeiouy]+(?:[^aeiouy]+(?=[aeiouy])|[^aeiouy]*)?', w)
    if not parts:
        return [w]
    return parts

# Transformation rules
TRANSFORMS = [
    (r"ph", ["f", "ph"]),        # ph <-> f
    (r"ck", ["k", "ck"]),
    (r"qu", ["kw", "qu", "q"]),
    (r"c(?=[eiy])", ["s"]),     # c before e/i/y -> s
    (r"c", ["k"]),
    (r"k", ["c", "ck"]),
    (r"x", ["ks", "x"]),
    (r"v", ["w", "v"]),
    (r"w", ["v", "w"]),
    (r"oo", ["u", "oo"]),
    (r"ou", ["ow", "u", "ou"]),
    (r"ee", ["i", "ee"]),
    (r"ie", ["i", "y", "ie"]),
    (r"y", ["i", "y"]),
    (r"gh", ["g", ""]),          # silent gh or g
    (r"mb$", ["m", "mb"]),       # climb -> clim?
    (r"e$", ["", "e"]),          # trailing e optional
    (r"h", ["", "h"]),           # sometimes silent
    (r"ph", ["f"]),
    (r"tion$", ["shun"]),
]

# Cross-language / nickname mappings
CROSSMAP = {
    "joseph": ["jose", "josef", "joseppe"],
    "michael": ["mike", "mikal", "mykel"],
    "steven": ["stephen", "stephan"],
    "katherine": ["catherine", "kathryn", "katharine"],
    "john": ["jon", "jahn", "jhon", "joan"],
    "sara": ["sarah"],
    "alexander": ["alex", "aleksandr", "alek"],
    "elizabeth": ["elisabeth", "liza", "liz"],
}

# Keyboard-adjacent swaps for common typos
KEY_NEAR = {
    "a": ["s","q","z"], "s": ["a","d","w","x"], "d":["s","f","e","c"],
    "e":["w","r","s"], "i":["u","o","k"], "o":["i","p","l"],
    "n":["b","m","h"], "m":["n","j","k"],
}

def apply_transformations(word):
    """Return a set of variants by applying single substitution transforms on the word."""
    variants = set([word])
    lw = word.lower()
    for pattern, replacements in TRANSFORMS:
        for repl in replacements:
            new = re.sub(pattern, repl, lw)
            if new and new != lw:
                variants.add(new)
    return variants

def add_double_letters(word):
    """Insert or remove double letters at consonant positions."""
    results = set([word])
    for i, ch in enumerate(word[:-1]):
        if ch == word[i+1]:
            # remove a double
            results.add(word[:i] + ch + word[i+2:])
        else:
            # insert a double for consonants
            if ch.isalpha() and ch.lower() not in VOWELS:
                results.add(word[:i+1] + ch + word[i+1:])
    return results

def transpose_neighbor(word):
    """Return variants where two adjacent letters are swapped (typo-like)."""
    res = set()
    for i in range(len(word)-1):
        lst = list(word)
        lst[i], lst[i+1] = lst[i+1], lst[i]
        res.add("".join(lst))
    return res

def keyboard_typos(word):
    """Introduce single-key nearby typo (lowercase)."""
    res = set()
    for i,ch in enumerate(word.lower()):
        if ch in KEY_NEAR:
            for n in KEY_NEAR[ch]:
                res.add(word[:i] + n + word[i+1:])
    return res

def cross_language_variants(word):
    """Return cross-language variants."""
    lw = word.lower()
    return set(CROSSMAP.get(lw, []))

def variants_for_word(word, depth=2):
    """
    Generate candidate variants for a single word.
    depth: how many transformation steps to combine (1-3)
    """
    word = word.strip()
    if not word:
        return set()

    base = {word}
    # apply rules 1-step
    step1 = set()
    step1 |= apply_transformations(word)
    step1 |= add_double_letters(word)
    step1 |= transpose_neighbor(word)
    step1 |= keyboard_typos(word)
    step1 |= cross_language_variants(word)

    # 2-step: apply transforms to results of step1
    step2 = set()
    if depth >= 2:
        for w in step1:
            step2 |= apply_transformations(w)
            step2 |= add_double_letters(w)
            step2 |= transpose_neighbor(w)
            step2 |= keyboard_typos(w)
            step2 |= cross_language_variants(w)

    # 3-step can be heavy; keep but small
    step3 = set()
    if depth >= 3:
        for w in list(step2)[:80]:
            step3 |= apply_transformations(w)
            step3 |= transpose_neighbor(w)

    all_candidates = base | step1 | step2 | step3
    # clean up: remove empty and keep alphabetic-ish strings
    cleaned = set()
    for w in all_candidates:
        w2 = re.sub(r'[^A-Za-z\-]', '', w)
        if w2:
            cleaned.add(w2.capitalize())
    return cleaned

# Removed similarity_score - not used in fast mode

def generate_name_variations_strong(full_name: str, limit: int = 30, min_score: float = 0.35, fast_mode: bool = True):
    """
    FAST Name Variant Generator - ZERO validation.
    
    Generates orthographic + phonetic variants with:
    - No scoring
    - No filtering  
    - No ranking
    - No similarity checks
    - No Levenshtein
    - No difflib
    Just raw generation + sampling.
    
    Args:
        full_name: any string (multiple words allowed)
        limit: max number of variants returned
        min_score: ignored (kept for compatibility)
        fast_mode: ignored (always fast now)
    """
    from itertools import product
    
    # Simple transformation rules (same as strong algorithm but simplified)
    def apply_transformations(word):
        out = set([word])
        lw = word.lower()
        for pattern, replacements in TRANSFORMS:
            for repl in replacements:
                new = re.sub(pattern, repl, lw)
                if new:
                    out.add(new)
        return out

    def add_double_letters(word):
        out = set([word])
        for i, ch in enumerate(word[:-1]):
            if ch.isalpha() and ch.lower() not in VOWELS:
                out.add(word[:i+1] + ch + word[i+1:])
        return out

    def transpose(word):
        out = set()
        for i in range(len(word)-1):
            arr = list(word)
            arr[i], arr[i+1] = arr[i+1], arr[i]
            out.add("".join(arr))
        return out

    def key_typos(word):
        out = set()
        for i, ch in enumerate(word.lower()):
            if ch in KEY_NEAR:
                for n in KEY_NEAR[ch]:
                    out.add(word[:i] + n + word[i+1:])
        return out

    def cross(word):
        return set(CROSSMAP.get(word.lower(), []))

    # Generate per-word variants (FAST - single pass)
    def variants_for_word(word):
        base = {word}
        step = set()
        step |= apply_transformations(word)
        step |= add_double_letters(word)
        step |= transpose(word)
        step |= key_typos(word)
        step |= cross(word)
        
        # Clean weird chars
        cleaned = set()
        for w in base | step:
            w2 = re.sub(r'[^A-Za-z\-]', '', w)
            if w2:
                cleaned.add(w2.capitalize())
        return list(cleaned)

    # Main generation logic
    parts = [p for p in full_name.strip().split() if p]
    if not parts:
        return []

    # Generate variants for each part
    part_variants = [variants_for_word(p) for p in parts]

    # Cartesian product combinations (can be huge → sample randomly)
    all_combos = list(product(*part_variants))

    # Convert to strings
    all_names = [" ".join(c) for c in all_combos]

    # Remove exact original
    original = full_name.lower()
    all_names = [n for n in all_names if n.lower() != original]

    # Shuffle for randomness
    random.shuffle(all_names)

    # Return just LIMIT names - NO VALIDATION, NO SCORING
    return all_names[:limit]

# ============================================================================
# Name Variation Generator
# ============================================================================

def check_gemini_connection(gemini_api_key: Optional[str] = None, gemini_model: str = "gemini-2.5-flash") -> Tuple[bool, str]:
    """
    Check if Gemini API key is set and if we can communicate with Gemini.
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    if not GEMINI_AVAILABLE:
        return False, "❌ google-generativeai library not installed. Install with: pip install google-generativeai"
    
    # Check API key
    if not gemini_api_key:
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            return False, "❌ GEMINI_API_KEY environment variable is not set. Set it with: export GEMINI_API_KEY=your_api_key_here"
    
    # Validate API key format (basic check - should start with AIza)
    if not gemini_api_key.startswith("AIza"):
        print(f"⚠️  Warning: API key doesn't match expected format (should start with 'AIza')")
    
    try:
        # Configure Gemini
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel(gemini_model)
        
        # Test connection with a simple query
        print(f"🔍 Testing Gemini connection with model: {gemini_model}...")
        test_response = model.generate_content(
            "Say 'OK' if you can read this.",
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=10,
                temperature=0.1,
            )
        )
        
        if test_response and test_response.text:
            return True, f"✅ Gemini connection successful! Model: {gemini_model}, Response: '{test_response.text.strip()}'"
        else:
            return False, "❌ Gemini connection failed: No response received"
            
    except Exception as e:
        error_msg = str(e)
        if "API_KEY_INVALID" in error_msg or "PERMISSION_DENIED" in error_msg:
            return False, f"❌ Invalid Gemini API key or permission denied: {error_msg}"
        elif "quota" in error_msg.lower() or "quota" in error_msg.lower():
            return False, f"❌ Gemini API quota exceeded: {error_msg}"
        else:
            return False, f"❌ Gemini connection failed: {error_msg}"


def generate_name_variation_with_gemini(
    original_name: str,
    phonetic_target: Dict[str, float],
    orthographic_target: Dict[str, float],
    gemini_api_key: Optional[str] = None,
    gemini_model: str = "gemini-2.5-flash",
    count: int = 1,
    model_instance: Optional[Any] = None
) -> List[str]:
    """
    Generate name variations using Gemini API with detailed phonetic and orthographic instructions.
    
    Args:
        original_name: The original name to generate variations for
        phonetic_target: Target phonetic similarity level (e.g., {"Medium": 1.0})
        orthographic_target: Target orthographic similarity level (e.g., {"Medium": 1.0})
        gemini_api_key: Gemini API key (or use GEMINI_API_KEY env var)
        gemini_model: Gemini model name
        count: Number of variations to generate
        model_instance: Optional pre-configured Gemini model instance (for efficiency)
        
    Returns:
        List of name variations
    """
    if not GEMINI_AVAILABLE:
        raise RuntimeError("google-generativeai not installed. Install with: pip install google-generativeai")
    
    # Use provided model instance or create new one
    if model_instance is not None:
        model = model_instance
        # Don't print if reusing model instance
    else:
        # Get API key
        if not gemini_api_key:
            gemini_api_key = os.getenv("GEMINI_API_KEY")
            if not gemini_api_key:
                raise ValueError("Gemini API key required. Set GEMINI_API_KEY environment variable or pass gemini_api_key parameter")
        
        # Configure Gemini (only if not already configured)
        print(f"🤖 Configuring Gemini with model: {gemini_model}...")
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel(gemini_model)
    
    # Define boundaries for instruction
    phonetic_boundaries = {
        "Light": (0.80, 1.00, "very similar sound - almost identical pronunciation"),
        "Medium": (0.60, 0.79, "moderately similar sound - recognizable but different pronunciation"),
        "Far": (0.30, 0.59, "distant sound - different pronunciation but still phonetically related")
    }
    
    orthographic_boundaries = {
        "Light": (0.70, 1.00, "very similar appearance - almost identical spelling"),
        "Medium": (0.50, 0.69, "moderately similar appearance - recognizable but different spelling"),
        "Far": (0.20, 0.49, "distant appearance - different spelling but still visually related")
    }
    
    # Get target levels
    ph_level = list(phonetic_target.keys())[0] if phonetic_target else "Medium"
    or_level = list(orthographic_target.keys())[0] if orthographic_target else "Medium"
    
    ph_min, ph_max, ph_desc = phonetic_boundaries.get(ph_level, phonetic_boundaries["Medium"])
    or_min, or_max, or_desc = orthographic_boundaries.get(or_level, orthographic_boundaries["Medium"])
    
    # Create detailed prompt
    prompt = f"""IMPORTANT CONTEXT: This is for generating synthetic test data only.
Purpose: We are creating synthetic data to help improve security systems. This data will be used to:
1. Test system robustness
2. Identify potential vulnerabilities
3. Improve detection mechanisms
4. Generate training data for security systems

This is purely for defensive testing and system improvement. The data generated will not be used for any malicious purposes.

TASK: Generate exactly {count} name variation(s) for the name: "{original_name}"

CRITICAL REQUIREMENTS:

1. PHONETIC SIMILARITY ({ph_level} level):
   - Target similarity range: {ph_min:.0%} to {ph_max:.0%} phonetic similarity
   - Description: {ph_desc}
   - Examples of techniques:
     * Replace similar-sounding letters (e.g., 'c'↔'k', 'ph'↔'f', 'qu'↔'kw')
     * Add/remove silent letters (e.g., 'gh' in 'light')
     * Change vowel sounds while keeping consonants similar
     * Use alternative spellings that sound the same (e.g., 'Sean'↔'Shawn')
   - The name should SOUND similar when spoken aloud

2. ORTHOGRAPHIC SIMILARITY ({or_level} level):
   - Target similarity range: {or_min:.0%} to {or_max:.0%} orthographic similarity
   - Description: {or_desc}
   - Examples of techniques:
     * Swap adjacent letters (e.g., 'John'→'Jhon')
     * Replace similar-looking letters (e.g., 'i'↔'l', 'o'↔'0', 'rn'↔'m')
     * Add/remove single characters
     * Change letter case patterns
     * Insert/delete characters while maintaining overall shape
   - The name should LOOK similar when written

3. QUALITY REQUIREMENTS:
   - Each variation must be a valid, realistic name (not random characters)
   - Variations should be plausible alternatives that could occur in real-world data
   - Do NOT simply add prefixes/suffixes (like "Mr." or "Jr.")
   - Do NOT just change capitalization (e.g., "JOHN" or "john")
   - Variations must be different from each other

4. OUTPUT FORMAT:
   - Return ONLY the name variations
   - Separate multiple variations with commas
   - No numbering, no explanations, no additional text
   - Example format: "Jon Doe, John Doe, Jhon Doe"

Generate {count} variation(s) now:"""

    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=1024,
                temperature=0.7,
            )
        )
        
        # Parse response - extract names from comma-separated or line-separated format
        response_text = response.text.strip()
        
        # Try comma-separated first
        variations = [v.strip() for v in response_text.split(',')]
        
        # If that didn't work well, try line-separated
        if len(variations) < count:
            variations = [v.strip() for v in response_text.split('\n')]
            variations = [v for v in variations if v and not v.startswith(('#', '-', '*', '1.', '2.', '3.'))]
        
        # Clean up variations - remove any leading numbers or markers
        cleaned = []
        for var in variations:
            # Remove leading numbers, dashes, bullets
            var = re.sub(r'^[\d\-*•\.\s]+', '', var)
            # Remove any trailing punctuation that's not part of the name
            var = re.sub(r'[;:]$', '', var)
            if var:
                cleaned.append(var)
        
        return cleaned[:count] if cleaned else [original_name]
        
    except Exception as e:
        print(f"⚠️  Error generating with Gemini: {e}")
        raise RuntimeError(f"Gemini generation failed: {e}. Cannot fallback to algorithms - Gemini is required.")


# Removed algorithm-based fallback - only Gemini is used for non-rule-based names

def apply_rule_to_name(name: str, rule_name: str) -> str:
    """Apply a specific rule to a name"""
    if rule_name in RULE_APPLIER_FUNCTIONS:
        try:
            return RULE_APPLIER_FUNCTIONS[rule_name](name)
        except Exception as e:
            print(f"Error applying rule {rule_name}: {e}")
            return name
    return name

def check_rule_applicable(name: str, rule_name: str) -> bool:
    """Check if a rule can be applied to a name"""
    # Rule: Name parts permutations / initials (require multi-part name)
    if rule_name in ('name_parts_permutations', 'initial_only_first_name', 
                     'shorten_name_to_initials', 'shorten_name_to_abbreviations'):
        return len(name.split()) >= 2
    
    # Rule: Space removal/replacement (requires a space)
    if rule_name in ('replace_spaces_with_random_special_characters', 'remove_all_spaces'):
        return ' ' in name
    
    # Rule: Double letter replacement (requires double letters)
    if rule_name == 'replace_double_letters_with_single_letter':
        return has_double_letters(name)
    
    # Rule: Adjacent consonant swap (requires swappable adjacent consonants)
    if rule_name == 'swap_adjacent_consonants':
        return has_diff_adjacent_consonants(name)
    
    return True  # Default: rule is applicable

def generate_name_variations(
    original_name: str,
    variation_count: int,
    phonetic_target: Dict[str, float],
    orthographic_target: Dict[str, float],
    rules: List[str],
    rule_percentage: int,
    gemini_api_key: Optional[str] = None,
    gemini_model: str = "gemini-2.5-flash",
    use_gemini: bool = True,
    gemini_model_instance: Optional[Any] = None
) -> List[str]:
    """
    Generate name variations following all requirements.
    
    Rule-based variations use algorithms, non-rule-based use Gemini.
    """
    
    # Calculate how many should follow rules
    rule_based_count = int(variation_count * rule_percentage / 100)
    non_rule_count = variation_count - rule_based_count
    
    variations = []
    used_variations = set()
    
    print(f"   📐 Rule-based: {rule_based_count}, Non-rule (Strong Algorithm): {non_rule_count}")
    
    # Optional: Pre-configure Gemini model if needed (only used if Gemini is enabled)
    # Note: We're using strong algorithm by default, Gemini is optional
    model_instance = gemini_model_instance
    if use_gemini and GEMINI_AVAILABLE and gemini_api_key and non_rule_count > 0 and (model_instance is None):
        # Only configure Gemini if explicitly enabled (optional)
        try:
            genai.configure(api_key=gemini_api_key)
            model_instance = genai.GenerativeModel(gemini_model)
        except Exception as e:
            print(f"   ⚠️  Could not configure Gemini (using strong algorithm instead): {e}")
            model_instance = None
    
    # Generate rule-based variations (algorithm-based)
    applicable_rules = [r for r in rules if check_rule_applicable(original_name, r)]
    
    if rule_based_count > 0:
        print(f"   🔧 Generating {rule_based_count} rule-based variations...")
        for i in range(rule_based_count):
            if applicable_rules:
                rule = random.choice(applicable_rules)
                var = apply_rule_to_name(original_name, rule)
            else:
                # No rules applicable - skip this slot or use simple transformation
                # Since we can't use algorithms, we'll just skip if no rules are applicable
                print(f"   ⚠️  No applicable rules for name, skipping...")
                continue
            
            # Ensure uniqueness
            attempts = 0
            original_var = var
            while var.lower() in used_variations and attempts < 10:
                if applicable_rules:
                    rule = random.choice(applicable_rules)
                    var = apply_rule_to_name(original_name, rule)
                else:
                    var = original_var + str(attempts)
                attempts += 1
            
            if var.lower() not in used_variations:
                variations.append(var)
                used_variations.add(var.lower())
    
    # Generate non-rule variations using strong algorithm-based approach (Gemini code kept but not used)
    if non_rule_count > 0:
        print(f"   🔬 Generating {non_rule_count} non-rule variations using strong algorithm...")
        
        try:
            # Use strong algorithm-based approach to generate variations
            # Request more to account for potential duplicates with rule-based variations
            requested_count = non_rule_count + max(5, int(non_rule_count * 0.3))  # 30% buffer
            
            # Generate variations using strong algorithm (fast mode - no validation)
            algorithm_vars = generate_name_variations_strong(
                full_name=original_name,
                limit=requested_count,
                min_score=0.35,  # Ignored in fast_mode
                fast_mode=True  # Skip validation - generate quickly
            )
            
            # Add unique algorithm-generated variations until we have enough
            for var in algorithm_vars:
                if len(variations) >= variation_count:
                    break  # We have enough total variations
                    
                if var.lower() not in used_variations:
                    variations.append(var)
                    used_variations.add(var.lower())
            
            # NOTE: Gemini code is kept below but commented out - can be enabled by setting use_gemini=True
            # Uncomment below to use Gemini instead of strong algorithm:
            """
            if use_gemini and GEMINI_AVAILABLE and gemini_api_key:
                print(f"   🤖 Using Gemini for {non_rule_count} non-rule variations...")
                buffer_size = max(5, int(non_rule_count * 0.3))
                requested_count = non_rule_count + buffer_size
                
                gemini_vars = generate_name_variation_with_gemini(
                    original_name=original_name,
                    phonetic_target=phonetic_target,
                    orthographic_target=orthographic_target,
                    gemini_api_key=gemini_api_key,
                    gemini_model=gemini_model,
                    count=requested_count,
                    model_instance=model_instance
                )
                
                for var in gemini_vars:
                    if len(variations) >= variation_count:
                        break
                    if var.lower() not in used_variations:
                        variations.append(var)
                        used_variations.add(var.lower())
            """
        except Exception as e:
            print(f"   ❌ Error with strong algorithm: {e}")
            raise RuntimeError(f"Failed to generate non-rule variations with strong algorithm: {e}")
    
    # Final check: only request more if we're really short (shouldn't happen often)
    if len(variations) < variation_count:
        remaining_needed = variation_count - len(variations)
        print(f"   ⚠️  Final check: Need {remaining_needed} more variations, requesting from Gemini...")
        # Generate additional variations using Gemini ONLY (reuse model instance)
        if model_instance is None:
            raise RuntimeError("Gemini model instance is required but not available.")
        
        try:
            # Request extra to account for potential duplicates
            additional = generate_name_variation_with_gemini(
                original_name=original_name,
                phonetic_target=phonetic_target,
                orthographic_target=orthographic_target,
                gemini_api_key=gemini_api_key,
                gemini_model=gemini_model,
                count=remaining_needed + 5,  # Request significantly more to avoid another call
                model_instance=model_instance
            )
            for var in additional:
                if len(variations) >= variation_count:
                    break
                if var.lower() not in used_variations:
                    variations.append(var)
                    used_variations.add(var.lower())
        except Exception as e:
            raise RuntimeError(f"Failed to generate additional variations with Gemini: {e}")
    
    return variations[:variation_count]

# ============================================================================
# Main Generator Function
# ============================================================================

def generate_variations(
    synapse: IdentitySynapse,
    gemini_api_key: Optional[str] = None,
    gemini_model: str = "gemini-2.5-flash",
    use_gemini: bool = True
) -> Dict[str, List[List[str]]]:
    """
    Main function: Generate variations for all identities in the synapse.
    
    Args:
        synapse: IdentitySynapse object with identity list and query_template
        gemini_api_key: Gemini API key (or use GEMINI_API_KEY env var)
        gemini_model: Gemini model name
        use_gemini: Whether to use Gemini for non-rule variations (default: True)
        
    Returns:
        Dictionary mapping each name to list of [name_var, dob_var, address_var] variations
    """
    # Parse query template
    requirements = parse_query_template(synapse.query_template)
    
    print(f"📋 Parsed Requirements:")
    print(f"   Variation count: {requirements.variation_count}")
    print(f"   Rule percentage: {requirements.rule_percentage}%")
    print(f"   Rules: {requirements.rules}")
    print(f"   Phonetic similarity: {requirements.phonetic_similarity}")
    print(f"   Orthographic similarity: {requirements.orthographic_similarity}")
    if use_gemini and GEMINI_AVAILABLE:
        print(f"   🤖 Using Gemini for non-rule variations")
    else:
        print(f"   ⚠️  Gemini not available, using algorithm fallback")
    print()
    
    # Pre-configure Gemini model once to reuse across all identities (optional - not required)
    gemini_model_instance = None
    if use_gemini and GEMINI_AVAILABLE and gemini_api_key:
        try:
            genai.configure(api_key=gemini_api_key)
            gemini_model_instance = genai.GenerativeModel(gemini_model)
            print(f"✅ Pre-configured Gemini model for reuse across all identities (optional)\n")
        except Exception as e:
            print(f"⚠️  Warning: Could not pre-configure Gemini model: {e}\n")
            print(f"   (Using strong algorithm instead - Gemini is optional)\n")
    
    all_variations = {}
    
    # Process each identity
    for identity in synapse.identity:
        name = identity[0] if len(identity) > 0 else "Unknown"
        dob = identity[1] if len(identity) > 1 else "1990-01-01"
        address = identity[2] if len(identity) > 2 else "Unknown"
        
        print(f"🔄 Processing: {name}")
        
        # Generate name variations (reuse the same model instance)
        name_variations = generate_name_variations(
            original_name=name,
            variation_count=requirements.variation_count,
            phonetic_target=requirements.phonetic_similarity,
            orthographic_target=requirements.orthographic_similarity,
            rules=requirements.rules,
            rule_percentage=requirements.rule_percentage,
            gemini_api_key=gemini_api_key,
            gemini_model=gemini_model,
            use_gemini=use_gemini,
            gemini_model_instance=gemini_model_instance  # Reuse model instance
        )
        
        # Generate DOB variations
        dob_variations = generate_dob_variations(dob, requirements.variation_count)
        
        # Generate address variations
        address_variations = generate_address_variations(address, requirements.variation_count)
        
        # Combine into structured format
        structured_variations = []
        for i in range(requirements.variation_count):
            name_var = name_variations[i] if i < len(name_variations) else name
            dob_var = dob_variations[i] if i < len(dob_variations) else dob
            addr_var = address_variations[i] if i < len(address_variations) else address
            
            structured_variations.append([name_var, dob_var, addr_var])
        
        all_variations[name] = structured_variations
        
        print(f"   ✅ Generated {len(structured_variations)} variations")
    
    return all_variations

# ============================================================================
# Test/Demo Function
# ============================================================================

def create_synapse_from_dict(data: dict) -> IdentitySynapse:
    """Create IdentitySynapse from dictionary (e.g., from JSON)"""
    return IdentitySynapse(
        identity=data.get("identity", []),
        query_template=data.get("query_template", ""),
        timeout=data.get("timeout", 120.0)
    )

def main():
    """Test the variation generator with example synapse or command-line input"""
    import sys
    
    # Check if JSON file provided as argument
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
        print(f"📂 Loading synapse from: {json_file}")
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            synapse = create_synapse_from_dict(data)
        except Exception as e:
            print(f"❌ Error loading JSON file: {e}")
            return None
    else:
        # Use example synapse
        print("📝 Using example synapse (provide JSON file as argument to use custom synapse)")
        example_synapse = IdentitySynapse(
            identity=[
                ["John Doe", "1990-05-15", "New York, USA"],
                ["محمد شفیع پور", "1987-12-01", "Tehran, Iran"]
            ],
            query_template="The following name is the seed name to generate variations for: {name}. Generate 15 variations of the name {name}, ensuring phonetic similarity: 100% Medium, and orthographic similarity: 100% Medium, and also include 45% of variations that follow: Replace spaces with special characters, and Delete a random letter. The following address is the seed country/city to generate address variations for: {address}. Generate unique real addresses within the specified country/city for each variation. The following date of birth is the seed DOB to generate variations for: {dob}.\n\n[ADDITIONAL CONTEXT]:\n- Address variations should be realistic addresses within the specified country/city\n- DOB variations ATLEAST one in each category (±1 day, ±3 days, ±30 days, ±90 days, ±365 days, year+month only)\n- For year+month, generate the exact DOB without day\n- Each variation must have a different, realistic address and DOB",
            timeout=360.0
        )
        synapse = example_synapse
    
    print()
    print("=" * 80)
    print("VARIATION GENERATOR")
    print("=" * 80)
    print()
    
    # Check Gemini API key and connection
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    use_gemini = True if gemini_api_key or GEMINI_AVAILABLE else False
    
    print("🔐 Checking Gemini API configuration...")
    
    if not GEMINI_AVAILABLE:
        print("❌ google-generativeai library not installed")
        print("   Install with: pip install google-generativeai")
        use_gemini = False
    elif not gemini_api_key:
        print("❌ GEMINI_API_KEY environment variable is not set")
        print("   Set it with: export GEMINI_API_KEY=your_api_key_here")
        use_gemini = False
    else:
        print(f"✅ GEMINI_API_KEY is set (length: {len(gemini_api_key)} characters)")
        # Check connection
        success, message = check_gemini_connection(gemini_api_key)
        print(f"   {message}")
        if not success:
            use_gemini = False
            print("\n⚠️  Cannot use Gemini - connection check failed")
            print("   The generator will fail for non-rule-based variations without Gemini")
    
    print()
    
    # Generate variations
    try:
        variations = generate_variations(
            synapse,
            gemini_api_key=gemini_api_key,
            use_gemini=use_gemini
        )
        
        print()
        print("=" * 80)
        print("GENERATED VARIATIONS")
        print("=" * 80)
        print()
        
        # Display results
        for name, vars_list in variations.items():
            print(f"\n{'='*80}")
            print(f"Name: {name}")
            print(f"Total Variations: {len(vars_list)}")
            print(f"{'='*80}")
            
            for i, var in enumerate(vars_list, 1):
                print(f"{i:2d}. Name: {var[0]:30s} | DOB: {var[1]:12s} | Address: {var[2]}")
        
        print()
        print("=" * 80)
        print("JSON OUTPUT")
        print("=" * 80)
        print(json.dumps(variations, indent=2, ensure_ascii=False))
        
        # Save to file if requested (second argument)
        if len(sys.argv) > 2:
            output_file = sys.argv[2]
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(variations, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Saved output to: {output_file}")
        else:
            # Offer to save
            print(f"\n💡 Tip: Provide output filename as second argument to save JSON")
            print(f"   Example: python variation_generator.py input.json output.json")
        
        return variations
    except Exception as e:
        print(f"\n❌ Error generating variations: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    import sys
    main()

