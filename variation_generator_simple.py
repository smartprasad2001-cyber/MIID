#!/usr/bin/env python3
"""
Simple Variation Generator
Generates name, DOB, and address variations based on validator requirements.

This program takes an IdentitySynapse (exactly like miners receive) and generates
compliant variations following all rules, similarity requirements, and specifications.

USAGE:
    # Run with example synapse
    python variation_generator_simple.py
    
    # Run with custom synapse from JSON file
    python variation_generator_simple.py synapse_input.json
    
    # Run and save output to JSON file
    python variation_generator_simple.py synapse_input.json output_variations.json

FEATURES:
    - Parses query template to extract requirements (variation count, similarity, rules)
    - Applies rule-based transformations (18+ rules supported)
    - Generates name variations using simple algorithm (no Gemini, no validation)
    - Creates DOB variations covering all required categories
    - Generates realistic address variations within same country/city
"""

import re
import random
import json
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

# Import EXACT functions from name_variations.py - use it directly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from name_variations import generate_name_variations as generate_name_variations_direct

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
# Simple Name Variation Algorithm (from name_variations.py)
# ============================================================================

# Common phonetic/orthographic transformation rules
TRANSFORMATIONS = [
    ("ph", ["f"]),
    ("f", ["ph"]),
    ("c", ["k", "s"]),
    ("k", ["c", "ck"]),
    ("j", ["jh"]),
    ("s", ["z"]),
    ("z", ["s"]),
    ("x", ["ks"]),
    ("v", ["w"]),
    ("w", ["v"]),
    ("oo", ["u"]),
    ("u", ["oo"]),
    ("ee", ["i"]),
    ("i", ["ee", "y"]),
    ("y", ["i"]),
    ("o", ["oh", "o"]),
    ("a", ["ah", "aa"]),
    ("h", ["", "h"]),
]

# Import the EXACT functions from name_variations.py - no modifications
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from name_variations import generate_name_variations as generate_name_variations_from_module

def generate_name_variations_simple(full_name: str, limit: int = 10) -> List[str]:
    """
    Generate name variations using EXACT name_variations.py module.
    Direct import - zero modifications, zero combinations logic added.
    
    Args:
        full_name: Full name string (can have multiple words)
        limit: Maximum number of variations to return
        
    Returns:
        List of name variations
    """
    # Use EXACT function from name_variations.py - no changes, no additions
    return generate_name_variations_from_module(full_name, limit)

# ============================================================================
# Rule Application Functions
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
    if rule_name in ('name_parts_permutations', 'initial_only_first_name', 
                     'shorten_name_to_initials', 'shorten_name_to_abbreviations'):
        return len(name.split()) >= 2
    if rule_name in ('replace_spaces_with_random_special_characters', 'remove_all_spaces'):
        return ' ' in name
    if rule_name == 'replace_double_letters_with_single_letter':
        return has_double_letters(name)
    if rule_name == 'swap_adjacent_consonants':
        return has_diff_adjacent_consonants(name)
    return True

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
    
    # Extract variation count
    count_match = re.search(r'Generate\s+(\d+)\s+variations?', query_template, re.IGNORECASE)
    if count_match:
        req.variation_count = int(count_match.group(1))
    else:
        count_match = re.search(r'(\d+)\s+variations?', query_template, re.IGNORECASE)
        if count_match:
            req.variation_count = int(count_match.group(1))
    
    # Extract rule percentage
    rule_pct_match = re.search(r'(\d+)%\s+of\s+variations?', query_template, re.IGNORECASE)
    if rule_pct_match:
        req.rule_percentage = int(rule_pct_match.group(1))
    else:
        rule_pct_match = re.search(r'include\s+(\d+)%', query_template, re.IGNORECASE)
        if rule_pct_match:
            req.rule_percentage = int(rule_pct_match.group(1))
    
    # Extract rules
    rule_patterns = {
        "replace_spaces_with_random_special_characters": [r"Replace\s+spaces\s+with\s+special\s+characters", r"spaces\s+with\s+special"],
        "replace_double_letters_with_single_letter": [r"Replace\s+double\s+letters\s+with\s+a\s+single\s+letter", r"double\s+letters\s+with\s+single"],
        "replace_random_vowel_with_random_vowel": [r"Replace\s+random\s+vowels\s+with\s+different\s+vowels", r"vowels\s+with\s+different"],
        "replace_random_consonant_with_random_consonant": [r"Replace\s+random\s+consonants\s+with\s+different\s+consonants", r"consonants\s+with\s+different"],
        "swap_adjacent_consonants": [r"Swap\s+adjacent\s+consonants", r"adjacent\s+consonants"],
        "swap_adjacent_syllables": [r"Swap\s+adjacent\s+syllables", r"adjacent\s+syllables"],
        "swap_random_letter": [r"Swap\s+random\s+adjacent\s+letters", r"swap\s+.*\s+letters"],
        "delete_random_letter": [r"Delete\s+a\s+random\s+letter", r"delete.*letter"],
        "remove_random_vowel": [r"Remove\s+a\s+random\s+vowel", r"remove.*vowel"],
        "remove_random_consonant": [r"Remove\s+a\s+random\s+consonant", r"remove.*consonant"],
        "remove_all_spaces": [r"Remove\s+all\s+spaces", r"remove.*spaces"],
        "duplicate_random_letter_as_double_letter": [r"Duplicate\s+a\s+random\s+letter", r"duplicate.*letter"],
        "insert_random_letter": [r"Insert\s+a\s+random\s+letter", r"insert.*letter"],
        "add_random_leading_title": [r"Add\s+a\s+title\s+prefix", r"title\s+prefix"],
        "add_random_trailing_title": [r"Add\s+a\s+title\s+suffix", r"title\s+suffix"],
        "initial_only_first_name": [r"Use\s+first\s+name\s+initial\s+with\s+last\s+name", r"first\s+name\s+initial"],
        "shorten_name_to_initials": [r"Convert\s+name\s+to\s+initials", r"name\s+to\s+initials"],
        "shorten_name_to_abbreviations": [r"Abbreviate\s+name\s+parts", r"abbreviate.*name"],
        "name_parts_permutations": [r"Reorder\s+name\s+parts", r"reorder.*parts"],
    }
    
    detected_rules = []
    for rule_name, patterns in rule_patterns.items():
        for pattern in patterns:
            if re.search(pattern, query_template, re.IGNORECASE):
                if rule_name not in detected_rules:
                    detected_rules.append(rule_name)
                break
    
    req.rules = detected_rules
    
    # Extract phonetic similarity
    ph_match = re.search(r'phonetic\s+similarity[:\s]+(?:100%[\s]+)?(Light|Medium|Far)', query_template, re.IGNORECASE)
    if ph_match:
        level = ph_match.group(1).capitalize()
        req.phonetic_similarity = {level: 1.0}
    elif "phonetic similarity" in query_template.lower():
        req.phonetic_similarity = {"Medium": 1.0}
    
    # Extract orthographic similarity
    or_match = re.search(r'orthographic\s+similarity[:\s]+(?:100%[\s]+)?(Light|Medium|Far)', query_template, re.IGNORECASE)
    if or_match:
        level = or_match.group(1).capitalize()
        req.orthographic_similarity = {level: 1.0}
    elif "orthographic similarity" in query_template.lower():
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
            seed_date = datetime.strptime(seed_dob, "%Y-%m")
            seed_date = seed_date.replace(day=1)
        except ValueError:
            return [seed_dob] * count
    
    variations = []
    
    # Required categories
    required_variations = [
        (seed_date + timedelta(days=1)).strftime("%Y-%m-%d"),
        (seed_date + timedelta(days=-1)).strftime("%Y-%m-%d"),
        (seed_date + timedelta(days=3)).strftime("%Y-%m-%d"),
        (seed_date + timedelta(days=-3)).strftime("%Y-%m-%d"),
        (seed_date + timedelta(days=30)).strftime("%Y-%m-%d"),
        (seed_date + timedelta(days=-30)).strftime("%Y-%m-%d"),
        (seed_date + timedelta(days=90)).strftime("%Y-%m-%d"),
        (seed_date + timedelta(days=-90)).strftime("%Y-%m-%d"),
        (seed_date + timedelta(days=365)).strftime("%Y-%m-%d"),
        (seed_date + timedelta(days=-365)).strftime("%Y-%m-%d"),
        seed_date.strftime("%Y-%m"),
    ]
    
    variations.extend(required_variations[:min(len(required_variations), count)])
    
    # Fill remaining with random variations
    categories = [1, 3, 30, 90, 365]
    while len(variations) < count:
        days = random.choice(categories)
        sign = random.choice([1, -1])
        var_date = seed_date + timedelta(days=days * sign)
        variations.append(var_date.strftime("%Y-%m-%d"))
    
    # Remove duplicates
    unique_variations = []
    seen = set()
    for var in variations:
        if var not in seen:
            unique_variations.append(var)
            seen.add(var)
        if len(unique_variations) >= count:
            break
    
    # Fill any remaining slots
    while len(unique_variations) < count:
        days = random.choice([1, 3, 30, 90, 365])
        sign = random.choice([1, -1])
        var_date = seed_date + timedelta(days=days * sign)
        var_str = var_date.strftime("%Y-%m-%d")
        if var_str not in seen:
            unique_variations.append(var_str)
            seen.add(var_str)
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
    parts = [p.strip() for p in address.split(',')]
    if len(parts) >= 2:
        country = parts[-1]
        city = parts[-2] if len(parts) >= 2 else parts[0]
        return city, country
    return address, address

def generate_address_variation(seed_address: str, used_addresses: set) -> str:
    """Generate a realistic address variation within the same country/city"""
    city, country = extract_location_from_address(seed_address)
    
    street_types = ['Street', 'Avenue', 'Road', 'Lane', 'Drive', 'Boulevard', 
                   'Court', 'Place', 'Way', 'Circle', 'Parkway']
    
    street_names = ['Main', 'Oak', 'Elm', 'Pine', 'Maple', 'Cedar', 'First', 
                   'Second', 'Third', 'Park', 'Washington', 'Lincoln', 'Church',
                   'Market', 'Broad', 'High', 'King', 'Queen', 'Bridge']
    
    max_attempts = 100
    for attempt in range(max_attempts):
        street_num = random.randint(1, 9999)
        street_name = random.choice(street_names)
        street_type = random.choice(street_types)
        
        if random.random() < 0.3:
            abbrev_map = {'Street': 'St', 'Avenue': 'Ave', 'Road': 'Rd', 
                         'Lane': 'Ln', 'Drive': 'Dr', 'Boulevard': 'Blvd'}
            street_type = abbrev_map.get(street_type, street_type)
        
        address = f"{street_num} {street_name} {street_type}, {city}, {country}"
        normalized = ' '.join(address.lower().split())
        
        if normalized not in used_addresses:
            used_addresses.add(normalized)
            return address
    
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
# Name Variation Generator (Main)
# ============================================================================

def generate_name_variations(
    original_name: str,
    variation_count: int,
    phonetic_target: Dict[str, float],
    orthographic_target: Dict[str, float],
    rules: List[str],
    rule_percentage: int
) -> List[str]:
    """
    Generate name variations following all requirements.
    
    Rule-based variations use algorithms, non-rule-based use simple algorithm.
    """
    
    # Calculate how many should follow rules
    rule_based_count = int(variation_count * rule_percentage / 100)
    non_rule_count = variation_count - rule_based_count
    
    variations = []
    used_variations = set()
    
    print(f"   📐 Rule-based: {rule_based_count}, Non-rule (Simple Algorithm): {non_rule_count}")
    
    # Generate rule-based variations (algorithm-based)
    applicable_rules = [r for r in rules if check_rule_applicable(original_name, r)]
    
    if rule_based_count > 0:
        print(f"   🔧 Generating {rule_based_count} rule-based variations...")
        for i in range(rule_based_count):
            if applicable_rules:
                rule = random.choice(applicable_rules)
                var = apply_rule_to_name(original_name, rule)
            else:
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
    
    # Generate non-rule variations using EXACT name_variations.py - ONE CALL, NO EXTRA LOGIC
    if non_rule_count > 0:
        print(f"   🔬 Generating {non_rule_count} non-rule variations using simple algorithm...")
        
        try:
            # Call name_variations.py DIRECTLY - one call, exact number needed
            algorithm_vars = generate_name_variations_direct(
                original_name,
                limit=non_rule_count
            )
            
            # Add unique variations (skip duplicates)
            for var in algorithm_vars:
                if len(variations) >= variation_count:
                    break
                if var.lower() not in used_variations:
                    variations.append(var)
                    used_variations.add(var.lower())
        except Exception as e:
            print(f"   ❌ Error with simple algorithm: {e}")
            raise RuntimeError(f"Failed to generate non-rule variations: {e}")
    
    return variations[:variation_count]

# ============================================================================
# Main Generator Function
# ============================================================================

def generate_variations(synapse: IdentitySynapse) -> Dict[str, List[List[str]]]:
    """
    Main function: Generate variations for all identities in the synapse.
    
    Args:
        synapse: IdentitySynapse object with identity list and query_template
        
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
    print(f"   🔬 Using simple algorithm for non-rule variations (no Gemini)")
    print()
    
    all_variations = {}
    
    # Process each identity
    for identity in synapse.identity:
        name = identity[0] if len(identity) > 0 else "Unknown"
        dob = identity[1] if len(identity) > 1 else "1990-01-01"
        address = identity[2] if len(identity) > 2 else "Unknown"
        
        print(f"🔄 Processing: {name}")
        
        # Generate name variations
        name_variations = generate_name_variations(
            original_name=name,
            variation_count=requirements.variation_count,
            phonetic_target=requirements.phonetic_similarity,
            orthographic_target=requirements.orthographic_similarity,
            rules=requirements.rules,
            rule_percentage=requirements.rule_percentage
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
# Main Entry Point
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
    print("VARIATION GENERATOR (SIMPLE ALGORITHM - NO GEMINI)")
    print("=" * 80)
    print()
    
    # Generate variations
    try:
        variations = generate_variations(synapse)
        
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
            print(f"   Example: python variation_generator_simple.py input.json output.json")
        
        return variations
    except Exception as e:
        print(f"\n❌ Error generating variations: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    import sys
    main()

