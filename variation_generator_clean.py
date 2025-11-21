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
        'orthographic_similarity': {}
    }
    
    # Extract variation count
    count_match = re.search(r'Generate\s+(\d+)\s+variations', query_template, re.I)
    if count_match:
        requirements['variation_count'] = int(count_match.group(1))
    
    # Extract rule percentage
    rule_pct_match = re.search(r'(\d+)%\s+of\s+variations', query_template, re.I)
    if rule_pct_match:
        requirements['rule_percentage'] = int(rule_pct_match.group(1)) / 100
    
    # Extract rules
    if 'replace spaces with special characters' in query_template.lower():
        requirements['rules'].append('replace_spaces_with_special_characters')
    if 'delete a random letter' in query_template.lower() or 'delete random letter' in query_template.lower():
        requirements['rules'].append('delete_random_letter')
    if 'replace double letters' in query_template.lower():
        requirements['rules'].append('replace_double_letters')
    if 'swap adjacent consonants' in query_template.lower():
        requirements['rules'].append('swap_adjacent_consonants')
    
    # Extract similarity (just parse, don't validate)
    if 'phonetic similarity' in query_template.lower():
        if '100%' in query_template or 'Medium' in query_template:
            requirements['phonetic_similarity'] = {'Medium': 1.0}
    
    if 'orthographic similarity' in query_template.lower():
        if '100%' in query_template or 'Medium' in query_template:
            requirements['orthographic_similarity'] = {'Medium': 1.0}
    
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

def apply_rule_to_name(name: str, rule: str) -> str:
    """Apply a rule to a name"""
    rule_map = {
        'replace_spaces_with_special_characters': apply_replace_spaces_with_special_chars,
        'delete_random_letter': apply_delete_random_letter,
        'replace_double_letters': apply_replace_double_letters,
        'swap_adjacent_consonants': apply_swap_adjacent_consonants,
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

def generate_variations(synapse: IdentitySynapse) -> Dict[str, List[List[str]]]:
    """Generate variations for all identities"""
    requirements = parse_query_template(synapse.query_template)
    
    print("=" * 80)
    print("CLEAN VARIATION GENERATOR - NO VALIDATION, NO SCORING")
    print("=" * 80)
    print(f"\n📋 Requirements:")
    print(f"   Variation count: {requirements['variation_count']}")
    print(f"   Rule percentage: {requirements['rule_percentage']*100:.0f}%")
    print(f"   Rules: {requirements['rules']}")
    print()
    
    all_variations = {}
    
    for identity in synapse.identity:
        name = identity[0] if len(identity) > 0 else "Unknown"
        dob = identity[1] if len(identity) > 1 else "1990-01-01"
        address = identity[2] if len(identity) > 2 else "Unknown"
        
        print(f"🔄 Processing: {name}")
        
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

