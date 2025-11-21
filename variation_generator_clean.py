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
    if 'replace spaces with special characters' in query_template.lower():
        requirements['rules'].append('replace_spaces_with_special_characters')
    if 'delete a random letter' in query_template.lower() or 'delete random letter' in query_template.lower():
        requirements['rules'].append('delete_random_letter')
    if 'replace double letters' in query_template.lower():
        requirements['rules'].append('replace_double_letters')
    if 'swap adjacent consonants' in query_template.lower():
        requirements['rules'].append('swap_adjacent_consonants')
    if 'swap adjacent syllables' in query_template.lower():
        requirements['rules'].append('swap_adjacent_syllables')
    if 'add a title suffix' in query_template.lower() or 'title suffix' in query_template.lower():
        requirements['rules'].append('add_title_suffix')
    if 'abbreviate name parts' in query_template.lower() or 'abbreviate' in query_template.lower():
        requirements['rules'].append('abbreviate_name_parts')
    
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

def apply_rule_to_name(name: str, rule: str) -> str:
    """Apply a rule to a name"""
    rule_map = {
        'replace_spaces_with_special_characters': apply_replace_spaces_with_special_chars,
        'delete_random_letter': apply_delete_random_letter,
        'replace_double_letters': apply_replace_double_letters,
        'swap_adjacent_consonants': apply_swap_adjacent_consonants,
        'swap_adjacent_syllables': apply_swap_adjacent_syllables,
        'add_title_suffix': apply_add_title_suffix,
        'abbreviate_name_parts': apply_abbreviate_name_parts,
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
    
    # Strategy 1: Transliterate and generate variations, then keep original script
    if UNIDECODE_AVAILABLE:
        transliterated = unidecode(name)
        if transliterated and transliterated != name:
            # Generate variations on transliterated version
            latin_vars = generate_name_variations(transliterated, limit=count * 2)
            # Keep some transliterated variations as-is (valid for non-Latin names)
            for var in latin_vars[:count // 2]:
                if var.lower() not in used:
                    variations.append(var)
                    used.add(var.lower())
    
    # Strategy 2: Script-specific transformations
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
    
    # For CJK: Character-level variations
    if script == 'cjk':
        # Swap characters
        if len(parts) >= 2:
            swapped = " ".join([parts[-1]] + parts[:-1])
            if swapped.lower() not in used:
                variations.append(swapped)
                used.add(swapped.lower())
    
    # Strategy 3: Simple transformations (work for all scripts)
    # Add/remove punctuation-like characters
    for i in range(min(count // 2, 3)):
        # Remove middle character if long enough
        if len(name) > 3:
            idx = random.randint(1, len(name) - 2)
            var = name[:idx] + name[idx+1:]
            if var.lower() not in used:
                variations.append(var)
                used.add(var.lower())
        
        # Duplicate a character
        if len(name) > 2:
            idx = random.randint(0, len(name) - 1)
            var = name[:idx+1] + name[idx] + name[idx+1:]
            if var.lower() not in used:
                variations.append(var)
                used.add(var.lower())
    
    # Strategy 4: If we have transliteration, use those variations directly
    if UNIDECODE_AVAILABLE and len(variations) < count:
        transliterated = unidecode(name)
        if transliterated and transliterated != name:
            # Get more transliterated variations
            more_latin_vars = generate_name_variations(transliterated, limit=(count - len(variations)) * 2)
            for var in more_latin_vars:
                if len(variations) >= count:
                    break
                if var.lower() not in used:
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
    
    # Generate non-rule variations using name_variations.py DIRECTLY
    print(f"   🔬 Non-rule: {non_rule_count} (using name_variations.py)")
    if non_rule_count > 0:
        non_rule_vars = generate_name_variations(original_name, limit=non_rule_count * 2)
        
        for var in non_rule_vars:
            if len(variations) >= variation_count:
                break
            if var.lower() not in used_variations:
                variations.append(var)
                used_variations.add(var.lower())
        
        # If we got too few variations and it's a non-Latin script, use special handling
        if len(variations) < variation_count and is_non_latin and len(non_rule_vars) < non_rule_count:
            print(f"   🌍 Detected {script} script - using script-specific variations")
            remaining = variation_count - len(variations)
            non_latin_vars = generate_non_latin_variations(original_name, script, remaining)
            
            for var in non_latin_vars:
                if len(variations) >= variation_count:
                    break
                if var.lower() not in used_variations:
                    variations.append(var)
                    used_variations.add(var.lower())
    
    # Final fallback - only if we still don't have enough
    if len(variations) < variation_count:
        if is_non_latin:
            # For non-Latin, use script-specific variations as last resort
            remaining = variation_count - len(variations)
            non_latin_vars = generate_non_latin_variations(original_name, script, remaining)
            for var in non_latin_vars:
                if len(variations) >= variation_count:
                    break
                if var.lower() not in used_variations:
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

