#!/usr/bin/env python3
"""
Test 15 names from sanctioned transliteration list:
1. Fetch names from Sanctioned_Transliteration.json (no translation)
2. Generate name and DOB variations using unified generator (address blank)
3. Get detailed score breakdown from rewards.py
"""

import os
import sys
import json
import random
import time
from typing import List, Dict

# Add paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'MIID', 'validator'))

# Import validator functions
from reward import get_name_variation_rewards
from variation_generator_simple import (
    generate_name_variations, 
    generate_dob_variations,
    parse_query_template
)

# Create a mock validator class to use get_name_variation_rewards
# The function expects self but doesn't use it, so we can pass any object
class MockValidator:
    """Mock validator class to use get_name_variation_rewards"""
    def __init__(self):
        # Add any attributes that might be accessed
        pass

def load_sanctioned_names(count: int = 15) -> List[Dict]:
    """Load names from sanctioned transliteration file"""
    json_path = os.path.join(os.path.dirname(__file__), 'MIID', 'validator', 'Sanctioned_Transliteration.json')
    
    with open(json_path, 'r', encoding='utf-8') as f:
        all_names = json.load(f)
    
    # Select random 15 names
    selected = random.sample(all_names, min(count, len(all_names)))
    return selected

def format_query_template(name: str, dob: str, address: str = "") -> str:
    """Format query template exactly as validator sends"""
    template = f"""The following name is the seed name to generate variations for: {name}. Generate 15 variations of the name {name}, ensuring phonetic similarity: 100% Medium, and orthographic similarity: 100% Medium, and also include 45% of variations that follow: Replace spaces with special characters, and Delete a random letter. The following address is the seed country/city to generate address variations for: {address}. Generate unique real addresses within the specified country/city for each variation. The following date of birth is the seed DOB to generate variations for: {dob}.

[ADDITIONAL CONTEXT]:
- Address variations should be realistic addresses within the specified country/city
- DOB variations ATLEAST one in each category (±1 day, ±3 days, ±30 days, ±90 days, ±365 days, year+month only)
- For year+month, generate the exact DOB without day
- Each variation must have a different, realistic address and DOB"""
    return template

def format_detailed_scores(detailed_metrics: Dict) -> str:
    """Format detailed scores like the example"""
    output = []
    
    # Extract scores from detailed_metrics
    final_score = detailed_metrics.get('final_reward', 0.0)
    names_score = detailed_metrics.get('average_quality', 0.0)
    
    # Get name metrics
    name_metrics = detailed_metrics.get('name_metrics', {})
    if name_metrics:
        # Get first name's metrics as representative
        first_name = list(name_metrics.keys())[0] if name_metrics else None
        if first_name:
            first_metrics = name_metrics[first_name]
            basic_quality = first_metrics.get('quality_score', 0.0)
            similarity_score = first_metrics.get('similarity_score', 0.0)
            phonetic_similarity = first_metrics.get('phonetic_similarity', 0.0)
            orthographic_similarity = first_metrics.get('orthographic_similarity', 0.0)
            count_score = first_metrics.get('count_score', 0.0)
            uniqueness_score = first_metrics.get('uniqueness_score', 0.0)
            length_score = first_metrics.get('length_score', 0.0)
            rule_compliance = first_metrics.get('rule_compliance_score', 0.0)
        else:
            basic_quality = similarity_score = phonetic_similarity = orthographic_similarity = 0.0
            count_score = uniqueness_score = length_score = rule_compliance = 0.0
    else:
        basic_quality = similarity_score = phonetic_similarity = orthographic_similarity = 0.0
        count_score = uniqueness_score = length_score = rule_compliance = 0.0
    
    # Get address and DOB scores
    address_score = detailed_metrics.get('address_score', 0.0)
    dob_score = detailed_metrics.get('dob_score', 0.0)
    
    # Get address breakdown
    address_breakdown = detailed_metrics.get('address_breakdown', {})
    looks_like_address = address_breakdown.get('heuristic_perfect', False)
    region_match = address_breakdown.get('region_matches', 0)
    api_call = address_breakdown.get('api_result_score', 0.0)
    
    # Get penalties
    penalties = detailed_metrics.get('penalties', {})
    completeness_multiplier = detailed_metrics.get('completeness_multiplier', 1.0)
    extra_names_penalty = penalties.get('extra_names_penalty', 0.0)
    missing_names_penalty = penalties.get('missing_names_penalty', 0.0)
    post_penalty = penalties.get('post_total_penalty', 0.0)
    address_penalty = penalties.get('address_penalty', 0.0)
    collusion_penalty = penalties.get('collusion_penalty', 0.0)
    duplication_penalty = penalties.get('duplication_penalty', 0.0)
    signature_copy_penalty = penalties.get('signature_copy_penalty', 0.0)
    special_chars_penalty = penalties.get('special_chars_penalty', 0.0)
    
    output.append(f"Final score\n{final_score:.3f}\n")
    output.append(f"Names\n{names_score:.3f}\n")
    output.append(f"Basic Quality Score\n{basic_quality:.3f}\n")
    output.append(f"Similarity Score\n{similarity_score:.3f}\n")
    output.append(f"Phonetic Similarity\n{phonetic_similarity:.3f}\n")
    output.append(f"Orthographic Similarity\n{orthographic_similarity:.3f}\n")
    output.append(f"Count Score\n{count_score:.3f}\n")
    output.append(f"Uniqueness Score\n{uniqueness_score:.3f}\n")
    output.append(f"Length Score\n{length_score:.3f}\n")
    output.append(f"Rule Compliance Score\n{rule_compliance:.3f}\n")
    output.append(f"Address Score\n{address_score:.3f}\n")
    output.append(f"Looks Like Address\n{1.0 if looks_like_address else 0.0:.3f}\n")
    output.append(f"Address Regain Match\n{region_match:.3f}\n")
    output.append(f"Address API call\n{api_call:.3f}\n")
    output.append(f"DOB Score\n{dob_score:.3f}\n")
    output.append(f"Completeness Multiplier\n{completeness_multiplier:.3f}\n")
    output.append(f"Extra names penalty\n{extra_names_penalty:.3f}\n")
    output.append(f"Missing names penalty\n{missing_names_penalty:.3f}\n")
    output.append(f"Post Penalty\n{post_penalty:.3f}\n")
    output.append(f"Address Penalty\n{address_penalty:.3f}\n")
    output.append(f"Collusion Penalty\n{collusion_penalty:.3f}\n")
    output.append(f"Duplication Penalty\n{duplication_penalty:.3f}\n")
    output.append(f"Signature Copy Penalty\n{signature_copy_penalty:.3f}\n")
    output.append(f"Special Chars Penalty\n{special_chars_penalty:.3f}")
    
    return "\n".join(output)

def main():
    print("="*80)
    print("TESTING 15 NAMES FROM SANCTIONED TRANSLITERATION LIST")
    print("="*80)
    print()
    
    # Step 1: Load 15 names
    print("📋 Step 1: Loading 15 names from sanctioned transliteration list...")
    sanctioned_names = load_sanctioned_names(15)
    print(f"   ✅ Loaded {len(sanctioned_names)} names")
    print()
    
    # Step 2: Prepare identities and generate variations
    print("🔬 Step 2: Generating name and DOB variations (address blank)...")
    
    identities = []
    seed_names = []
    seed_dob = []
    seed_addresses = []
    seed_script = []
    
    for i, person in enumerate(sanctioned_names, 1):
        first_name = person.get('FirstName', '')
        last_name = person.get('LastName', '')
        full_name = f"{first_name} {last_name}".strip()
        dob = person.get('DOB', '1990-01-01')
        country = person.get('Country_Residence', '')
        script = person.get('Script', 'latin')
        
        # Use empty address
        address = ""
        
        identities.append([full_name, dob, address])
        seed_names.append(full_name)
        seed_dob.append(dob)
        seed_addresses.append(address)
        seed_script.append(script)
        
        print(f"   [{i}/15] Added: {full_name[:50]}... (script: {script})")
        sys.stdout.flush()
    
    # Create query template (same format as validator) for parsing requirements
    query_template = """The following name is the seed name to generate variations for: {name}. Generate 15 variations of the name {name}, ensuring phonetic similarity: 100% Medium, and orthographic similarity: 100% Medium, and also include 45% of variations that follow: Replace spaces with special characters, and Delete a random letter. The following address is the seed country/city to generate address variations for: {address}. Generate unique real addresses within the specified country/city for each variation. The following date of birth is the seed DOB to generate variations for: {dob}.

[ADDITIONAL CONTEXT]:
- Address variations should be realistic addresses within the specified country/city
- DOB variations ATLEAST one in each category (±1 day, ±3 days, ±30 days, ±90 days, ±365 days, year+month only)
- For year+month, generate the exact DOB without day
- Each variation must have a different, realistic address and DOB"""
    
    # Parse requirements from query template
    print("   📋 Parsing query template requirements...")
    sys.stdout.flush()
    requirements = parse_query_template(query_template)
    print(f"   ✅ Variation count: {requirements.variation_count}, Rules: {requirements.rules}")
    sys.stdout.flush()
    
    # Generate variations directly using unified generator functions
    print(f"   📝 Starting variation generation for {len(identities)} identities...")
    print(f"   ⏱️  Start time: {time.strftime('%H:%M:%S')}")
    sys.stdout.flush()
    
    variations = {}
    
    try:
        start_time = time.time()
        
        for i, identity in enumerate(identities, 1):
            name = identity[0]
            dob = identity[1]
            
            print(f"   [{i}/{len(identities)}] Processing: {name[:50]}...")
            sys.stdout.flush()
            
            # Generate name variations
            print(f"      🔄 Generating name variations...")
            sys.stdout.flush()
            name_variations = generate_name_variations(
                original_name=name,
                variation_count=requirements.variation_count,
                phonetic_target=requirements.phonetic_similarity,
                orthographic_target=requirements.orthographic_similarity,
                rules=requirements.rules,
                rule_percentage=requirements.rule_percentage
            )
            print(f"      ✅ Generated {len(name_variations)} name variations")
            sys.stdout.flush()
            
            # Generate DOB variations
            print(f"      🔄 Generating DOB variations...")
            sys.stdout.flush()
            dob_variations = generate_dob_variations(dob, requirements.variation_count)
            print(f"      ✅ Generated {len(dob_variations)} DOB variations")
            sys.stdout.flush()
            
            # Combine into structured format (address is blank)
            structured_variations = []
            for j in range(requirements.variation_count):
                name_var = name_variations[j] if j < len(name_variations) else name
                dob_var = dob_variations[j] if j < len(dob_variations) else dob
                addr_var = ""  # Blank address
                structured_variations.append([name_var, dob_var, addr_var])
            
            variations[name] = structured_variations
            print(f"      ✅ Completed {name[:50]}...")
            sys.stdout.flush()
        
        elapsed = time.time() - start_time
        print(f"   ✅ Generated variations for {len(variations)} names in {elapsed:.2f} seconds")
        sys.stdout.flush()
        
    except Exception as e:
        print(f"   ❌ Error generating variations: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print()
    
    # Step 4: Test with validator
    print("🧪 Step 3: Testing with validator to get detailed scores...")
    print(f"   ⏱️  Start time: {time.strftime('%H:%M:%S')}")
    sys.stdout.flush()
    
    # Prepare parameters for get_name_variation_rewards
    print("   📋 Preparing validator parameters...")
    sys.stdout.flush()
    
    mock_validator = MockValidator()
    responses = [variations]  # List of responses (one miner)
    uids = [501]  # Single miner UID
    variation_count = 15
    phonetic_similarity = {"Medium": 1.0}
    orthographic_similarity = {"Medium": 1.0}
    rule_based = {
        "rule_percentage": 45,
        "selected_rules": ["replace_spaces_with_random_special_characters", "delete_random_letter"]
    }
    
    print(f"   📊 Parameters: {len(seed_names)} names, {variation_count} variations each")
    print(f"   🔄 Calling get_name_variation_rewards...")
    sys.stdout.flush()
    
    try:
        start_time = time.time()
        rewards, updated_uids, detailed_metrics_list = get_name_variation_rewards(
            mock_validator,
            seed_names,
            seed_dob,
            seed_addresses,
            seed_script,
            responses,
            uids,
            variation_count=variation_count,
            phonetic_similarity=phonetic_similarity,
            orthographic_similarity=orthographic_similarity,
            rule_based=rule_based
        )
        
        elapsed = time.time() - start_time
        print(f"   ✅ Validator scoring completed in {elapsed:.2f} seconds")
        sys.stdout.flush()
        
        if detailed_metrics_list and len(detailed_metrics_list) > 0:
            detailed_metrics = detailed_metrics_list[0]
            final_score = rewards[0] if len(rewards) > 0 else 0.0
            
            print("\n" + "="*80)
            print("DETAILED SCORE BREAKDOWN")
            print("="*80)
            print()
            print(format_detailed_scores(detailed_metrics))
            print()
            
            # Save results
            output_file = "sanctioned_names_detailed_scores.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "test_date": __import__('datetime').datetime.now().isoformat(),
                    "sanctioned_names": sanctioned_names,
                    "seed_names": seed_names,
                    "seed_dob": seed_dob,
                    "seed_addresses": seed_addresses,
                    "seed_script": seed_script,
                    "variations": variations,
                    "final_score": float(final_score),
                    "detailed_metrics": detailed_metrics,
                    "formatted_scores": format_detailed_scores(detailed_metrics)
                }, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Results saved to {output_file}")
        else:
            print("❌ No detailed metrics returned")
            
    except Exception as e:
        print(f"   ❌ Error testing with validator: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()

