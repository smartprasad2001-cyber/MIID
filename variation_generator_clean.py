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
    
    # Extract rule percentage - look for "also include X%" or "X% of variations"
    rule_pct_match = re.search(r'(\d+)%\s+of\s+variations|include\s+(\d+)%', query_template, re.I)
    if rule_pct_match:
        pct = rule_pct_match.group(1) or rule_pct_match.group(2)
        requirements['rule_percentage'] = int(pct) / 100
    
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

def apply_rule_to_name(name: str, rule: str) -> str:
    """Apply a rule to a name"""
    rule_map = {
        'replace_spaces_with_special_characters': apply_replace_spaces_with_special_chars,
        'delete_random_letter': apply_delete_random_letter,
        'replace_double_letters': apply_replace_double_letters,
        'swap_adjacent_consonants': apply_swap_adjacent_consonants,
        'swap_adjacent_syllables': apply_swap_adjacent_syllables,
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
    # These are rough approximations - in production, use geocoding API
    country_coords = {
        "USA": (39.8283, -98.5795),  # Geographic center
        "UK": (54.7024, -3.2766),
        "Canada": (56.1304, -106.3468),
        "Germany": (51.1657, 10.4515),
        "France": (46.2276, 2.2137),
        "Spain": (40.4637, -3.7492),
        "Italy": (41.8719, 12.5674),
        "Russia": (61.5240, 105.3188),
        "China": (35.8617, 104.1954),
        "India": (20.5937, 78.9629),
        "Japan": (36.2048, 138.2529),
        "Brazil": (-14.2350, -51.9253),
        "Mexico": (23.6345, -102.5528),
    }
    
    # Try to find country in our map (case-insensitive)
    lat, lon = None, None
    for country_key, coords in country_coords.items():
        if country_key.lower() in country.lower() or country.lower() in country_key.lower():
            lat, lon = coords
            # Add small random offset to make it unique
            lat += random.uniform(-0.5, 0.5)
            lon += random.uniform(-0.5, 0.5)
            break
    
    # Fallback coordinates if country not found
    if lat is None or lon is None:
        lat = random.uniform(-90, 90)
        lon = random.uniform(-180, 180)
    
    return {
        'address': uav_address,
        'label': label,
        'latitude': round(lat, 6),
        'longitude': round(lon, 6)
    }

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
        non_rule_vars = generate_name_variations(original_name, limit=non_rule_count)
        
        for var in non_rule_vars:
            if len(variations) >= variation_count:
                break
            if var.lower() not in used_variations:
                variations.append(var)
                used_variations.add(var.lower())
    
    # Fill remaining if needed (shouldn't happen but just in case)
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

