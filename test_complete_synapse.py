"""
Complete Synapse Test: Generate Name, DOB, and Address variations for multiple identities
Tests with actual rewards.py scoring functions
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'MIID', 'validator'))

import jellyfish
import random
from typing import List, Set, Tuple, Dict
from datetime import datetime, timedelta

# Import weight calculator
from weight_calculator import get_weights_for_name

# Import from rewards.py
from reward import (
    calculate_variation_quality,
    calculate_phonetic_similarity,
    calculate_orthographic_similarity,
    _grade_dob_variations,
    _grade_address_variations,
    MIID_REWARD_WEIGHTS
)

# ============================================================================
# DOB Generation Functions
# ============================================================================

def normalize_dob_format(dob: str) -> str:
    """Normalize DOB format to YYYY-MM-DD."""
    try:
        parts = dob.split('-')
        if len(parts) == 3:
            year = parts[0]
            month = parts[1].zfill(2)
            day = parts[2].zfill(2)
            return f"{year}-{month}-{day}"
        elif len(parts) == 2:
            year = parts[0]
            month = parts[1].zfill(2)
            return f"{year}-{month}"
        else:
            return dob
    except:
        return dob

def generate_perfect_dob_variations(seed_dob: str, variation_count: int = 10) -> List[str]:
    """Generate DOB variations covering all 6 required categories for maximum score."""
    dob_variations = []
    
    try:
        normalized_dob = normalize_dob_format(seed_dob)
        seed_date = datetime.strptime(normalized_dob, "%Y-%m-%d")
        
        # Category representatives (one from each category)
        category_reps = [
            (seed_date + timedelta(days=-1)).strftime("%Y-%m-%d"),  # ±1 day
            (seed_date + timedelta(days=-3)).strftime("%Y-%m-%d"),  # ±3 days
            (seed_date + timedelta(days=-30)).strftime("%Y-%m-%d"),  # ±30 days
            (seed_date + timedelta(days=-90)).strftime("%Y-%m-%d"),  # ±90 days
            (seed_date + timedelta(days=-365)).strftime("%Y-%m-%d"),  # ±365 days
            seed_date.strftime("%Y-%m")  # Year+Month only
        ]
        
        final_variations = category_reps.copy()
        
        # Add more variations if needed
        if variation_count > len(final_variations):
            additional_variations = [
                (seed_date + timedelta(days=1)).strftime("%Y-%m-%d"),
                (seed_date + timedelta(days=3)).strftime("%Y-%m-%d"),
                (seed_date + timedelta(days=30)).strftime("%Y-%m-%d"),
                (seed_date + timedelta(days=90)).strftime("%Y-%m-%d"),
                (seed_date + timedelta(days=365)).strftime("%Y-%m-%d"),
            ]
            
            for i in range(variation_count - len(final_variations)):
                if i < len(additional_variations):
                    final_variations.append(additional_variations[i])
                else:
                    final_variations.append(seed_date.strftime("%Y-%m"))
        
        # Remove duplicates
        seen = set()
        unique_variations = []
        for dob in final_variations:
            if dob not in seen:
                seen.add(dob)
                unique_variations.append(dob)
        
        # Ensure year-month is included
        year_month_only = seed_date.strftime("%Y-%m")
        if year_month_only not in unique_variations:
            unique_variations.append(year_month_only)
        
        return unique_variations[:variation_count]
        
    except ValueError as e:
        print(f"Error parsing seed DOB '{seed_dob}': {e}")
        return []

# ============================================================================
# Address Generation Functions
# ============================================================================

def generate_exploit_addresses(seed_address: str, variation_count: int = 10) -> List[str]:
    """Generate addresses using the exploit method."""
    parts = [p.strip() for p in seed_address.split(",")]
    city = parts[0] if len(parts) > 0 else "City"
    country = parts[-1] if len(parts) > 1 else "Country"
    
    street_types = [
        "Street", "St", "Avenue", "Ave", "Road", "Rd", "Boulevard", "Blvd",
        "Drive", "Dr", "Lane", "Ln", "Way", "Place", "Pl", "Court", "Ct"
    ]
    
    street_names = [
        "Main", "Oak", "Pine", "Elm", "Maple", "Cedar", "Park", "First", "Second",
        "Third", "Fourth", "Fifth", "Washington", "Lincoln", "Jefferson", "Madison",
        "Broadway", "Church", "Market", "High", "King", "Queen", "Victoria", "Union",
        "State", "Center", "Central", "North", "South", "East", "West", "Grand"
    ]
    
    addresses = []
    for i in range(variation_count):
        street_num = random.randint(1, 9999)
        street_name = random.choice(street_names)
        street_type = random.choice(street_types)
        address = f"{street_num} {street_name} {street_type}, {city}, {country}"
        addresses.append(address)
    
    return addresses

# ============================================================================
# Name Generation Functions (from user's provided code)
# ============================================================================

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

def generate_candidates(original: str, max_depth: int = 6, max_candidates: int = 2000000) -> List[str]:
    """Generate candidate variations using multiple strategies, recursively."""
    candidates = []
    tested: Set[str] = set()
    vowels = ['a', 'e', 'i', 'o', 'u', 'y']
    all_letters = 'abcdefghijklmnopqrstuvwxyz'
    consonants = 'bcdfghjklmnpqrstvwxyz'
    
    def add_candidate(var: str):
        if var and var != original and var not in tested and len(var) > 0:
            if len(var) >= 1 and len(var) <= len(original) + 5:
                tested.add(var)
                candidates.append(var)
                return True
        return False
    
    def generate_level(word: str, depth: int = 0):
        if depth >= max_depth or len(candidates) >= max_candidates:
            return
        
        # Strategy 1: Remove single letters
        for i in range(len(word)):
            var = word[:i] + word[i+1:]
            if add_candidate(var) and depth < max_depth - 1:
                generate_level(var, depth + 1)
        
        # Strategy 2: Add vowels
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
        
        # Strategy 4: Change consonants
        for i, char in enumerate(word):
            if char.lower() in consonants:
                for c in consonants:
                    if c != char.lower():
                        var = word[:i] + c + word[i+1:]
                        if add_candidate(var):
                            if depth < max_depth - 1:
                                generate_level(var, depth + 1)
        
        # Strategy 5: Swap adjacent letters
        for i in range(len(word) - 1):
            var = word[:i] + word[i+1] + word[i] + word[i+2:]
            if add_candidate(var) and depth < max_depth - 1:
                generate_level(var, depth + 1)
        
        # Strategy 6: Swap non-adjacent letters
        for i in range(len(word)):
            for j in range(i+2, len(word)):
                var = word[:i] + word[j] + word[i+1:j] + word[i] + word[j+1:]
                if add_candidate(var):
                    if depth < max_depth - 1:
                        generate_level(var, depth + 1)
        
        # Strategy 7: Add letters
        for pos in range(len(word) + 1):
            for letter in all_letters:
                var = word[:pos] + letter + word[pos:]
                if add_candidate(var):
                    if depth < max_depth - 1:
                        generate_level(var, depth + 1)
        
        # Strategy 8: Remove multiple letters
        if len(word) > 3:
            for i in range(len(word)):
                for j in range(i+1, len(word)):
                    var = word[:i] + word[i+1:j] + word[j+1:]
                    if add_candidate(var):
                        if depth < max_depth - 1:
                            generate_level(var, depth + 1)
    
    generate_level(original, depth=0)
    return candidates

def generate_light_variations(original: str, count: int, verbose: bool = False) -> List[str]:
    """Generate Light variations (score 0.8-1.0) using validator's calculate_phonetic_similarity."""
    perfect_matches = []
    tested: Set[str] = set()
    max_depth = 1
    max_candidates = 100000
    
    while len(perfect_matches) < count and max_depth <= 10:
        if verbose:
            print(f"  Searching Light variations (depth={max_depth})...", end=" ")
        
        candidates = generate_candidates(original, max_depth=max_depth, max_candidates=max_candidates)
        
        initial_count = len(perfect_matches)
        for var in candidates:
            if var == original or var in tested:
                continue
            
            tested.add(var)
            score = calculate_phonetic_similarity(original, var)
            
            if 0.8 <= score <= 1.0:
                if var not in perfect_matches:
                    perfect_matches.append(var)
                    if len(perfect_matches) >= count:
                        break
        
        if verbose:
            found = len(perfect_matches) - initial_count
            print(f"Found {found} new, total {len(perfect_matches)}/{count}")
        
        if len(perfect_matches) < count:
            max_depth += 1
            max_candidates = min(max_candidates * 2, 5000000)
        else:
            break
    
    return perfect_matches[:count]

def generate_medium_variations(original: str, count: int, verbose: bool = False) -> List[str]:
    """Generate Medium variations (0.6-0.79 range) using validator's calculate_phonetic_similarity."""
    scored_candidates = []
    tested: Set[str] = set()
    max_depth = 1
    max_candidates = 100000
    target_candidates = count * 500
    
    while len(scored_candidates) < target_candidates and max_depth <= 10:
        if verbose:
            print(f"  Searching Medium variations (depth={max_depth})...", end=" ")
        
        candidates = generate_candidates(original, max_depth=max_depth, max_candidates=max_candidates)
        
        for var in candidates:
            if var == original or var in tested:
                continue
            
            tested.add(var)
            score = calculate_phonetic_similarity(original, var)
            
            if 0.6 <= score <= 0.79:
                scored_candidates.append((var, score))
                if len(scored_candidates) >= target_candidates:
                    break
        
        if verbose:
            print(f"Found {len(scored_candidates)}/{target_candidates}")
        
        if len(scored_candidates) < target_candidates:
            max_depth += 1
            max_candidates = min(max_candidates * 2, 5000000)
        else:
            break
    
    scored_candidates.sort(key=lambda x: abs(x[1] - 0.695))
    
    result = []
    seen = set()
    for var, score in scored_candidates:
        if var not in seen:
            result.append(var)
            seen.add(var)
            if len(result) >= count:
                break
    
    return result

def generate_far_variations(original: str, count: int, verbose: bool = False) -> List[str]:
    """Generate Far variations (0.3-0.59 range) using validator's calculate_phonetic_similarity."""
    scored_candidates = []
    tested: Set[str] = set()
    max_depth = 1
    max_candidates = 100000
    target_candidates = count * 300
    
    while len(scored_candidates) < target_candidates and max_depth <= 10:
        if verbose:
            print(f"  Searching Far variations (depth={max_depth})...", end=" ")
        
        candidates = generate_candidates(original, max_depth=max_depth, max_candidates=max_candidates)
        
        for var in candidates:
            if var == original or var in tested:
                continue
            
            tested.add(var)
            score = calculate_phonetic_similarity(original, var)
            
            if 0.3 <= score <= 0.59:
                scored_candidates.append((var, score))
                if len(scored_candidates) >= target_candidates:
                    break
        
        if verbose:
            print(f"Found {len(scored_candidates)}/{target_candidates}")
        
        if len(scored_candidates) < target_candidates:
            max_depth += 1
            max_candidates = min(max_candidates * 2, 5000000)
        else:
            break
    
    scored_candidates.sort(key=lambda x: abs(x[1] - 0.445))
    
    result = []
    seen = set()
    for var, score in scored_candidates:
        if var not in seen:
            result.append(var)
            seen.add(var)
            if len(result) >= count:
                break
    
    return result

def generate_full_name_variations(
    full_name: str,
    light_count: int,
    medium_count: int,
    far_count: int,
    verbose: bool = True
) -> List[str]:
    """Generate variations for a full name (first + last)."""
    parts = full_name.split()
    if len(parts) < 2:
        if verbose:
            print(f"Warning: '{full_name}' doesn't have first and last name.")
        first_name = full_name
        last_name = None
    else:
        first_name = parts[0]
        last_name = parts[-1]
    
    if verbose:
        print(f"Generating variations for '{full_name}':")
        print(f"  First: '{first_name}', Last: '{last_name}'")
    
    first_light = generate_light_variations(first_name, light_count, verbose=verbose)
    first_medium = generate_medium_variations(first_name, medium_count, verbose=verbose)
    first_far = generate_far_variations(first_name, far_count, verbose=verbose)
    
    if last_name:
        last_light = generate_light_variations(last_name, light_count, verbose=verbose)
        last_medium = generate_medium_variations(last_name, medium_count, verbose=verbose)
        last_far = generate_far_variations(last_name, far_count, verbose=verbose)
    else:
        last_light = [first_name] * light_count
        last_medium = [first_name] * medium_count
        last_far = [first_name] * far_count
    
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

# ============================================================================
# Main Test Function
# ============================================================================

def test_synapse(names: List[str], dobs: List[str], addresses: List[str], variation_count: int = 10):
    """Test a complete synapse with multiple identities."""
    print("="*80)
    print("COMPLETE SYNAPSE TEST")
    print("="*80)
    print()
    
    # Distribution for name variations
    light_count = int(variation_count * 0.2)
    medium_count = int(variation_count * 0.6)
    far_count = variation_count - light_count - medium_count
    
    print(f"Configuration:")
    print(f"  Number of identities: {len(names)}")
    print(f"  Variations per identity: {variation_count}")
    print(f"  Distribution: {light_count} Light, {medium_count} Medium, {far_count} Far")
    print()
    
    # Generate variations for all identities
    all_variations = {}
    all_dob_variations = {}
    all_address_variations = {}
    
    print("="*80)
    print("GENERATING VARIATIONS")
    print("="*80)
    print()
    
    for i, (name, dob, address) in enumerate(zip(names, dobs, addresses), 1):
        print(f"[{i}/{len(names)}] Processing: {name}")
        
        # Generate name variations
        name_vars = generate_full_name_variations(
            name,
            light_count=light_count,
            medium_count=medium_count,
            far_count=far_count,
            verbose=False
        )
        all_variations[name] = name_vars
        
        # Generate DOB variations
        dob_vars = generate_perfect_dob_variations(dob, variation_count=variation_count)
        all_dob_variations[name] = dob_vars
        
        # Generate address variations
        addr_vars = generate_exploit_addresses(address, variation_count=variation_count)
        all_address_variations[name] = addr_vars
        
        print(f"  ✓ Generated {len(name_vars)} name, {len(dob_vars)} DOB, {len(addr_vars)} address variations")
    
    print()
    print("="*80)
    print("SCORING WITH REWARDS.PY")
    print("="*80)
    print()
    
    # Calculate target distribution
    target_distribution = {
        "Light": light_count / variation_count,
        "Medium": medium_count / variation_count,
        "Far": far_count / variation_count
    }
    
    # Score each identity
    name_scores = []
    dob_scores = []
    address_scores = []
    
    for name in names:
        # Name scoring
        name_vars = all_variations[name]
        final_score, base_score, detailed_metrics = calculate_variation_quality(
            original_name=name,
            variations=name_vars,
            expected_count=variation_count,
            phonetic_similarity=target_distribution,
            orthographic_similarity=target_distribution
        )
        name_scores.append(final_score)
        
        # DOB scoring
        dob_vars = all_dob_variations[name]
        variations_dict = {
            name: [[name_vars[i], dob_vars[i], all_address_variations[name][i]] 
                   for i in range(min(len(name_vars), len(dob_vars), len(all_address_variations[name])))]
        }
        seed_dobs = [dobs[names.index(name)]]
        dob_result = _grade_dob_variations(variations_dict, seed_dobs, {})
        dob_scores.append(dob_result['overall_score'])
        
        # Address scoring (with exploit - empty seed_addresses)
        seed_addresses = []  # Empty to trigger exploit
        address_result = _grade_address_variations(
            variations_dict,
            seed_addresses,
            {},
            1,  # validator_uid
            1   # miner_uid
        )
        address_scores.append(address_result['overall_score'])
    
    # Calculate final combined scores
    quality_weight = MIID_REWARD_WEIGHTS.get("quality_weight", 0.2)
    dob_weight = MIID_REWARD_WEIGHTS.get("dob_weight", 0.1)
    address_weight = MIID_REWARD_WEIGHTS.get("address_weight", 0.7)
    
    final_scores = []
    for i in range(len(names)):
        combined = (
            name_scores[i] * quality_weight +
            dob_scores[i] * dob_weight +
            address_scores[i] * address_weight
        )
        final_scores.append(combined)
    
    # Print results
    print("Results per Identity:")
    print("-" * 80)
    for i, name in enumerate(names):
        print(f"{i+1}. {name}")
        print(f"   Name Score:   {name_scores[i]:.4f} × {quality_weight} = {name_scores[i] * quality_weight:.4f}")
        print(f"   DOB Score:    {dob_scores[i]:.4f} × {dob_weight} = {dob_scores[i] * dob_weight:.4f}")
        print(f"   Address Score: {address_scores[i]:.4f} × {address_weight} = {address_scores[i] * address_weight:.4f}")
        print(f"   Final Score:  {final_scores[i]:.4f}")
        print()
    
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print()
    print(f"Average Name Score:   {sum(name_scores) / len(name_scores):.4f}")
    print(f"Average DOB Score:    {sum(dob_scores) / len(dob_scores):.4f}")
    print(f"Average Address Score: {sum(address_scores) / len(address_scores):.4f}")
    print(f"Average Final Score:  {sum(final_scores) / len(final_scores):.4f}")
    print()
    
    return {
        "name_scores": name_scores,
        "dob_scores": dob_scores,
        "address_scores": address_scores,
        "final_scores": final_scores,
        "average_final": sum(final_scores) / len(final_scores)
    }

if __name__ == "__main__":
    # Test synapse with 10 names
    test_names = [
        "John Smith",
        "Mary Johnson",
        "Robert Williams",
        "Jennifer Brown",
        "Michael Davis",
        "Sarah Miller",
        "David Wilson",
        "Lisa Anderson",
        "James Taylor",
        "Emily Martinez"
    ]
    
    test_dobs = [
        "1990-06-15",
        "1985-03-22",
        "1992-11-08",
        "1988-09-14",
        "1995-01-30",
        "1991-07-19",
        "1987-12-05",
        "1993-04-25",
        "1989-10-11",
        "1994-02-28"
    ]
    
    test_addresses = [
        "New York, USA",
        "Los Angeles, USA",
        "Chicago, USA",
        "Houston, USA",
        "Phoenix, USA",
        "Philadelphia, USA",
        "San Antonio, USA",
        "San Diego, USA",
        "Dallas, USA",
        "San Jose, USA"
    ]
    
    results = test_synapse(test_names, test_dobs, test_addresses, variation_count=10)

