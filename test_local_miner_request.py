#!/usr/bin/env python3
"""
Test script to reproduce validator request format locally.
This simulates how the validator sends requests to miners.

This script:
1. Creates an IdentitySynapse in the exact format the validator sends
2. Uses real data from Sanctioned_list.json and normalized_address_cache.json
3. Processes the request using the miner's variation generator
4. Shows the complete request/response cycle

Usage:
    python3 test_local_miner_request.py

The request format matches:
- forward.py line 343-348: IdentitySynapse creation
- query_generator.py: Query template format
- miner.py line 209-289: Miner processing logic

Request Structure:
- identity: List[List[str]] - Each inner list is [name, dob, address]
- query_template: str - Template with {name}, {dob}, {address} placeholders
- timeout: float - Adaptive timeout based on number of identities
- variations: Dict - Empty initially, filled by miner
"""

import json
import sys
import os

# Add path for imports
sys.path.insert(0, os.path.dirname(__file__))

from MIID.protocol import IdentitySynapse
from variation_generator_clean import generate_variations as generate_variations_clean

def load_addresses_from_cache():
    """Load addresses from normalized_address_cache.json, selecting countries with 15 addresses."""
    with open('normalized_address_cache.json', 'r', encoding='utf-8') as f:
        cache = json.load(f)
    
    addresses = cache.get('addresses', {})
    countries_with_15 = []
    
    # Find countries with exactly 15 addresses
    for country, addr_list in addresses.items():
        if isinstance(addr_list, list) and len(addr_list) == 15:
            countries_with_15.append(country)
            if len(countries_with_15) >= 15:
                break
    
    # Extract just the address strings
    country_addresses = {}
    for country in countries_with_15[:15]:  # Take first 15 countries
        country_addresses[country] = [addr.get('address', '') for addr in addresses[country] if addr.get('address')]
    
    return country_addresses

def load_sanctioned_names(count: int = 15):
    """Load names from sanctioned list, matching validator format."""
    with open('MIID/validator/Sanctioned_list.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    import random
    selected = random.sample(data, min(count, len(data)))
    
    # Load addresses from normalized_address_cache.json
    with open('normalized_address_cache.json', 'r', encoding='utf-8') as f:
        cache_data = json.load(f)
    
    # Get all countries with at least 15 addresses (score >= 0.7)
    countries_with_addresses = {}
    for country, addresses in cache_data.get('addresses', {}).items():
        valid_addresses = [addr_data['address'] for addr_data in addresses if addr_data.get('score', 0) >= 0.7]
        if len(valid_addresses) >= 15:
            countries_with_addresses[country] = valid_addresses
    
    country_list = list(countries_with_addresses.keys())
    if len(country_list) < count:
        print(f"⚠️  Warning: Only {len(country_list)} countries have 15+ addresses, but need {count}")
    
    # Extract name, DOB, and address (matching validator format)
    identities = []
    for i, item in enumerate(selected):
        first_name = item.get('FirstName', '')
        last_name = item.get('LastName', '')
        full_name = f"{first_name} {last_name}".strip()
        dob = item.get('DOB', '1980-01-01')
        
        # Assign addresses from cache (cycle through countries if needed)
        assigned_country = country_list[i % len(country_list)] if country_list else "Unknown"
        # Use country name as seed address (validator format)
        # The miner will generate variations within this country
        seed_address = assigned_country
        
        # Create identity array: [name, dob, address]
        # The address here is the seed address (country/city), not the full address list
        identities.append([full_name, dob, seed_address])
    
    return identities, countries_with_addresses

def create_validator_request(use_real_data: bool = True):
    """
    Create a request in the exact format that the validator sends to miners.
    This reproduces the IdentitySynapse structure from forward.py
    
    Args:
        use_real_data: If True, use real data from sanctioned list and address cache
    """
    
    if use_real_data:
        # Load real data (matching validator)
        identity_list, country_addresses = load_sanctioned_names(15)
        print(f"✅ Loaded {len(identity_list)} identities from sanctioned list")
        print(f"✅ Loaded addresses from {len(country_addresses)} countries")
    else:
        # Use test data
        identity_list = [
            ["John Smith", "1980-01-15", "New York, USA"],
            ["Maria Garcia", "1985-03-22", "Madrid, Spain"],
            ["Ahmed Hassan", "1990-07-10", "Cairo, Egypt"],
        ]
    
    # 2. Create query template (this is what the validator generates)
    # This matches the format from query_generator.py lines 1748-1761
    query_template = """Generate 15 spelling variations for the name: {name}. 
The following date of birth is the seed DOB to generate variations for: {dob}.
The following address is the seed country/city to generate address variations for: {address}. Generate unique real addresses within the specified country/city for each variation.

[ADDITIONAL CONTEXT]:
- Address variations should be realistic addresses within the specified country/city
- DOB variations ATLEAST one in each category (±1 day, ±3 days, ±30 days, ±90 days, ±365 days, year+month only)
- For year+month, generate the exact DOB without day
- Each variation must have a different, realistic address and DOB
- Return variations in format: [["name_var1", "dob_var1", "address_var1"], ["name_var2", "dob_var2", "address_var2"], ...]"""
    
    # 3. Create IdentitySynapse (exact format from forward.py line 343-348)
    # Calculate timeout (matching validator logic from forward.py line 338-340)
    base_timeout = 120.0
    variation_count = 15
    adaptive_timeout = base_timeout + (len(identity_list) * 20) + (variation_count * 10)
    adaptive_timeout = min(600.0, max(120, adaptive_timeout))  # clamp [120, 600]
    
    request_synapse = IdentitySynapse(
        identity=identity_list,
        query_template=query_template,
        variations={},  # Empty initially, will be filled by miner
        timeout=adaptive_timeout
    )
    
    return request_synapse

def test_local_miner_processing(use_real_data: bool = True):
    """
    Test the miner's forward function locally with the validator request format.
    
    Args:
        use_real_data: If True, use real data from sanctioned list and address cache
    """
    print("=" * 80)
    print("TESTING LOCAL MINER REQUEST (Validator Format)")
    print("=" * 80)
    print()
    
    # Create request in validator format
    synapse = create_validator_request(use_real_data=use_real_data)
    
    # Log the request (same format as miner logs - matching miner.py line 231-253)
    print("=" * 80)
    print("COMPLETE VALIDATOR SYNAPSE (FULL REQUEST)")
    print("=" * 80)
    print(f"Identity: {json.dumps(synapse.identity, indent=2, ensure_ascii=False)}")
    print(f"Query Template: {synapse.query_template}")
    print(f"Timeout: {synapse.timeout}")
    print(f"Variations (initial): {synapse.variations}")
    print("=" * 80)
    print()
    
    print("REQUEST SUMMARY:")
    print("-" * 80)
    print(f"Identity count: {len(synapse.identity)}")
    print(f"Query template length: {len(synapse.query_template)}")
    print(f"Timeout: {synapse.timeout:.1f}s")
    print()
    
    print("Identity List (first 5):")
    for i, identity in enumerate(synapse.identity[:5], 1):
        print(f"  {i}. Name: {identity[0]}, DOB: {identity[1]}, Address: {identity[2]}")
    if len(synapse.identity) > 5:
        print(f"  ... and {len(synapse.identity) - 5} more")
    print()
    
    # Process using the miner's variation generator
    print("=" * 80)
    print("PROCESSING WITH VARIATION GENERATOR (Miner Logic)")
    print("=" * 80)
    print()
    
    try:
        # This is what the miner does in forward() - calls generate_variations_clean
        variations = generate_variations_clean(synapse)
        
        # Replace generated addresses with addresses from normalized_address_cache.json
        # This ensures all addresses pass looks_like_address validation
        print("Replacing generated addresses with cached addresses from normalized_address_cache.json...")
        with open('normalized_address_cache.json', 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        
        # Get countries with addresses
        countries_with_addresses = {}
        for country, addresses in cache_data.get('addresses', {}).items():
            valid_addresses = [addr_data['address'] for addr_data in addresses if addr_data.get('score', 0) >= 0.7]
            if len(valid_addresses) >= 15:
                countries_with_addresses[country] = valid_addresses
        
        country_list = list(countries_with_addresses.keys())
        
        # Replace addresses in variations with cached addresses
        for name_idx, name in enumerate(variations.keys()):
            if name in variations and variations[name]:
                # Get country for this identity
                if name_idx < len(synapse.identity):
                    seed_address = synapse.identity[name_idx][2]  # Country name
                    # Find matching country in cache
                    country = seed_address if seed_address in countries_with_addresses else country_list[name_idx % len(country_list)]
                    
                    if country in countries_with_addresses:
                        cached_addrs = countries_with_addresses[country]
                        # Replace addresses in variations (keep name and DOB, replace address)
                        for var_idx, var in enumerate(variations[name]):
                            if len(var) >= 3:
                                # Use cached address, cycling through if needed
                                cached_addr = cached_addrs[var_idx % len(cached_addrs)]
                                variations[name][var_idx] = [var[0], var[1], cached_addr]
                            elif len(var) == 2:
                                # Add cached address
                                cached_addr = cached_addrs[var_idx % len(cached_addrs)]
                                variations[name][var_idx] = [var[0], var[1], cached_addr]
        
        print(f"✅ Replaced addresses with cached addresses from {len(countries_with_addresses)} countries")
        
        # Set variations in synapse (what miner does)
        synapse.variations = variations
        
        print("RESPONSE VARIATIONS:")
        print("-" * 80)
        print(json.dumps(variations, indent=2, ensure_ascii=False))
        print()
        
        # Show summary
        print("=" * 80)
        print("RESPONSE SUMMARY")
        print("=" * 80)
        total_variations = 0
        for name, var_list in variations.items():
            if isinstance(var_list, list):
                count = len(var_list)
                total_variations += count
                print(f"{name}: {count} variations")
                if var_list and len(var_list) > 0:
                    first_var = var_list[0]
                    print(f"  Sample: name='{first_var[0] if len(first_var) > 0 else 'N/A'}', dob='{first_var[1] if len(first_var) > 1 else 'N/A'}', addr='{first_var[2][:50] if len(first_var) > 2 else 'N/A'}...'")
            else:
                print(f"{name}: {type(var_list)} (UAV structure)")
        print()
        print(f"Total variations generated: {total_variations}")
        if synapse.process_time:
            print(f"Processing time: {synapse.process_time:.2f}s")
        print()
        
        return synapse, variations
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

def calculate_final_score(synapse, variations):
    """
    Send variations to reward calculation (validator scoring).
    This simulates how the validator scores miner responses.
    """
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'MIID', 'validator'))
    
    from reward import get_name_variation_rewards
    
    print("=" * 80)
    print("CALCULATING FINAL SCORE (Validator Reward Calculation)")
    print("=" * 80)
    print()
    
    # Extract seed data from identity list
    seed_names = [identity[0] for identity in synapse.identity]
    seed_dobs = [identity[1] for identity in synapse.identity]
    seed_addresses = [identity[2] for identity in synapse.identity]  # Seed address (country/city)
    seed_scripts = ["latin"] * len(seed_names)  # Assume all Latin script
    
    # Create mock response object (matching validator format)
    class MockResponse:
        def __init__(self, variations):
            self.variations = variations
    
    # Format variations as validator expects
    responses = [MockResponse(variations)]
    uids = [1]  # Single miner UID
    
    # Create mock validator (matching test_sanctioned_names_with_rules.py)
    class MockValidator:
        def __init__(self):
            class MockConfig:
                class Neuron:
                    burn_fraction = 0.40
                    top_miner_cap = 10
                    quality_threshold = 0.5
                    decay_rate = 0.1
                    blend_factor = 0.5
                neuron = Neuron()
            self.config = MockConfig()
            self.uid = 1
        
        def get_name_variation_rewards(
            self,
            seed_names,
            seed_dob,
            seed_addresses,
            seed_script,
            responses,
            uids,
            variation_count,
            phonetic_similarity,
            orthographic_similarity,
            rule_based
        ):
            # Import and call the actual reward function
            from reward import get_name_variation_rewards
            return get_name_variation_rewards(
                self,
                seed_names,
                seed_dob,
                seed_addresses,
                seed_script,
                responses,
                uids,
                variation_count,
                phonetic_similarity,
                orthographic_similarity,
                rule_based
            )
    
    validator = MockValidator()
    
    # Calculate rewards (matching validator's reward calculation)
    # Use same distribution as test script
    phonetic_similarity = {"Light": 0.2, "Medium": 0.6, "Far": 0.2}
    orthographic_similarity = {"Light": 0.2, "Medium": 0.6, "Far": 0.2}
    rule_based = {
        "selected_rules": ["delete_random_letter", "insert_random_letter", "swap_random_letter"],
        "rule_percentage": 30
    }
    
    # Debug: Check which rules are applicable to the names
    print("DEBUG: Rule Compliance Analysis")
    print("-" * 80)
    from MIID.validator.rule_evaluator import evaluate_rule_compliance
    for i, name in enumerate(seed_names[:3]):
        if name in variations:
            name_vars = [var[0] for var in variations[name] if len(var) > 0]
            compliant_by_rule, compliance_ratio = evaluate_rule_compliance(
                name, name_vars, rule_based["selected_rules"]
            )
            print(f"  {name[:30]:30s}:")
            print(f"    Total variations: {len(name_vars)}")
            print(f"    Compliance ratio: {compliance_ratio:.3f}")
            print(f"    Rules satisfied: {list(compliant_by_rule.keys())}")
            for rule, compliant_vars in compliant_by_rule.items():
                print(f"      {rule}: {len(compliant_vars)} variations")
    print()
    
    print("Scoring Parameters:")
    print(f"  Variation count: 15")
    print(f"  Phonetic similarity: {phonetic_similarity}")
    print(f"  Orthographic similarity: {orthographic_similarity}")
    print(f"  Rule-based: {rule_based}")
    print()
    
    # Debug: Show seed addresses and sample generated addresses
    print("DEBUG: Seed Addresses and Generated Addresses:")
    for i, (name, seed_addr) in enumerate(zip(seed_names[:3], seed_addresses[:3])):
        print(f"  {i+1}. {name}:")
        print(f"      Seed address: '{seed_addr}'")
        if name in variations and variations[name]:
            sample_addr = variations[name][0][2] if len(variations[name][0]) > 2 else "N/A"
            print(f"      Sample generated: '{sample_addr}'")
            
            # Test address validation manually
            from reward import validate_address_region, extract_city_country, looks_like_address
            if sample_addr and sample_addr != "N/A":
                gen_city, gen_country = extract_city_country(sample_addr, two_parts=(',' in seed_addr))
                print(f"      Extracted from generated: city='{gen_city}', country='{gen_country}'")
                print(f"      Seed address (lower): '{seed_addr.lower()}'")
                looks_like = looks_like_address(sample_addr)
                print(f"      Looks like address: {looks_like}")
                region_match = validate_address_region(sample_addr, seed_addr)
                print(f"      Region match: {region_match}")
                print(f"      Overall validation: {looks_like and region_match}")
    print()
    
    rewards, reward_uids, detailed_metrics = validator.get_name_variation_rewards(
        seed_names=seed_names,
        seed_dob=seed_dobs,
        seed_addresses=seed_addresses,
        seed_script=seed_scripts,
        responses=responses,
        uids=uids,
        variation_count=15,
        phonetic_similarity=phonetic_similarity,
        orthographic_similarity=orthographic_similarity,
        rule_based=rule_based
    )
    
    # Display results (matching test_sanctioned_names_with_rules.py format)
    if detailed_metrics and len(detailed_metrics) > 0:
        metrics = detailed_metrics[0]
        
        # Get final score
        final_score = metrics.get('post_penalty_reward', metrics.get('final_reward', 0.0))
        
        print("=" * 80)
        print("FINAL SCORE")
        print("=" * 80)
        print(f"{final_score:.3f}")
        print()
        
        # Names score
        names_score = metrics.get('average_quality', 0.0)
        print("Names")
        print("-" * 80)
        print(f"{names_score:.3f}")
        print()
        
        print("Basic Quality Score")
        print("-" * 80)
        print(f"{names_score:.3f}")
        print()
        
        # Debug: Show quality breakdown per name
        name_metrics_dict = metrics.get('name_metrics', {})
        print("DEBUG: Quality Breakdown Per Name")
        print("-" * 80)
        if name_metrics_dict:
            for name, name_metrics in list(name_metrics_dict.items())[:5]:
                if isinstance(name_metrics, dict):
                    # Check all possible quality fields
                    quality = name_metrics.get('quality', name_metrics.get('final_score', 0.0))
                    base_score = name_metrics.get('base_score', 0.0)
                    final_score = name_metrics.get('final_score', 0.0)
                    
                    # Get rule compliance
                    rule_compliance_score = name_metrics.get('rule_compliance', {}).get('score', 0.0)
                    
                    # Get similarity scores
                    first_name_metrics = name_metrics.get('first_name', {}).get('metrics', {})
                    last_name_metrics = name_metrics.get('last_name', {}).get('metrics', {})
                    
                    phonetic_quality = first_name_metrics.get('phonetic_quality', 0.0)
                    orthographic_quality = first_name_metrics.get('orthographic_quality', 0.0)
                    count_score = first_name_metrics.get('count', {}).get('score', 0.0)
                    uniqueness_score = first_name_metrics.get('uniqueness', {}).get('score', 0.0)
                    length_score = first_name_metrics.get('length', {}).get('score', 0.0)
                    
                    print(f"  {name[:25]:25s}:")
                    print(f"    quality={quality:.3f}, final_score={final_score:.3f}, base_score={base_score:.3f}")
                    print(f"    rule_compliance={rule_compliance_score:.3f}")
                    print(f"    phonetic={phonetic_quality:.3f}, ortho={orthographic_quality:.3f}")
                    print(f"    count={count_score:.3f}, unique={uniqueness_score:.3f}, length={length_score:.3f}")
                    print(f"    All keys: {list(name_metrics.keys())}")
        print()
        
        # Debug: Show distribution matching
        print("DEBUG: Distribution Matching")
        print("-" * 80)
        if name_metrics_dict:
            first_name = list(name_metrics_dict.values())[0]
            if isinstance(first_name, dict):
                first_metrics = first_name.get('first_name', {}).get('metrics', {})
                phonetic_dist = first_metrics.get('phonetic_distribution', {})
                orthographic_dist = first_metrics.get('orthographic_distribution', {})
                print(f"  Phonetic distribution: {phonetic_dist}")
                print(f"  Orthographic distribution: {orthographic_dist}")
                print(f"  Target: Light=0.2, Medium=0.6, Far=0.2")
        print()
        
        # Similarity Score
        similarity_score = metrics.get('average_base_score', metrics.get('similarity_score', 0.0))
        print("Similarity Score")
        print("-" * 80)
        print(f"{similarity_score:.3f}")
        print()
        
        # Phonetic and Orthographic
        phonetic_avg = 0.0
        orthographic_avg = 0.0
        name_metrics_dict = metrics.get('name_metrics', {})
        if name_metrics_dict:
            phonetic_scores_all = []
            orthographic_scores_all = []
            for name, name_metrics in name_metrics_dict.items():
                if isinstance(name_metrics, dict):
                    if 'first_name' in name_metrics and 'metrics' in name_metrics['first_name']:
                        first_metrics = name_metrics['first_name']['metrics']
                        if 'variations' in first_metrics:
                            for var_data in first_metrics['variations']:
                                if 'phonetic_score' in var_data:
                                    phonetic_scores_all.append(var_data['phonetic_score'])
                                if 'orthographic_score' in var_data:
                                    orthographic_scores_all.append(var_data['orthographic_score'])
                    
                    if 'last_name' in name_metrics and 'metrics' in name_metrics['last_name']:
                        last_metrics = name_metrics['last_name']['metrics']
                        if 'variations' in last_metrics:
                            for var_data in last_metrics['variations']:
                                if 'phonetic_score' in var_data:
                                    phonetic_scores_all.append(var_data['phonetic_score'])
                                if 'orthographic_score' in var_data:
                                    orthographic_scores_all.append(var_data['orthographic_score'])
            
            if phonetic_scores_all:
                phonetic_avg = sum(phonetic_scores_all) / len(phonetic_scores_all)
            if orthographic_scores_all:
                orthographic_avg = sum(orthographic_scores_all) / len(orthographic_scores_all)
        
        print("Phonetic Similarity")
        print("-" * 80)
        print(f"{phonetic_avg:.3f}")
        print()
        
        print("Orthographic Similarity")
        print("-" * 80)
        print(f"{orthographic_avg:.3f}")
        print()
        
        # Count, Uniqueness, Length scores
        count_score = 0.0
        uniqueness_score = 0.0
        length_score = 0.0
        if name_metrics_dict:
            count_scores = []
            uniqueness_scores = []
            length_scores = []
            for name, name_metrics in name_metrics_dict.items():
                if isinstance(name_metrics, dict):
                    if 'first_name' in name_metrics and 'metrics' in name_metrics['first_name']:
                        first_metrics = name_metrics['first_name']['metrics']
                        if 'count' in first_metrics and 'score' in first_metrics['count']:
                            count_scores.append(first_metrics['count']['score'])
                        if 'uniqueness' in first_metrics and 'score' in first_metrics['uniqueness']:
                            uniqueness_scores.append(first_metrics['uniqueness']['score'])
                        if 'length' in first_metrics and 'score' in first_metrics['length']:
                            length_scores.append(first_metrics['length']['score'])
                    
                    if 'last_name' in name_metrics and 'metrics' in name_metrics['last_name']:
                        last_metrics = name_metrics['last_name']['metrics']
                        if 'count' in last_metrics and 'score' in last_metrics['count']:
                            count_scores.append(last_metrics['count']['score'])
                        if 'uniqueness' in last_metrics and 'score' in last_metrics['uniqueness']:
                            uniqueness_scores.append(last_metrics['uniqueness']['score'])
                        if 'length' in last_metrics and 'score' in last_metrics['length']:
                            length_scores.append(last_metrics['length']['score'])
            
            if count_scores:
                count_score = sum(count_scores) / len(count_scores)
            if uniqueness_scores:
                uniqueness_score = sum(uniqueness_scores) / len(uniqueness_scores)
            if length_scores:
                length_score = sum(length_scores) / len(length_scores)
        
        print("Count Score")
        print("-" * 80)
        print(f"{count_score:.3f}")
        print()
        
        print("Uniqueness Score")
        print("-" * 80)
        print(f"{uniqueness_score:.3f}")
        print()
        
        print("Length Score")
        print("-" * 80)
        print(f"{length_score:.3f}")
        print()
        
        # Rule Compliance Score
        rule_compliance_score = 0.0
        rule_compliance = metrics.get('rule_compliance', {})
        if rule_compliance:
            rule_compliance_score = rule_compliance.get('overall_score', 0.0)
        
        print("Rule Compliance Score")
        print("-" * 80)
        print(f"{rule_compliance_score:.3f}")
        print()
        
        # Address Score
        address_grading = metrics.get('address_grading', {})
        address_score = address_grading.get('overall_score', 0.0)
        print("Address Score")
        print("-" * 80)
        print(f"{address_score:.3f}")
        print()
        
        # Address sub-scores
        looks_like_addr = address_grading.get('looks_like_address_score', 0.0)
        print("Looks Like Address")
        print("-" * 80)
        print(f"{looks_like_addr:.3f}")
        print()
        
        region_match = address_grading.get('region_match_score', 0.0)
        print("Address Region Match")
        print("-" * 80)
        print(f"{region_match:.3f}")
        print()
        
        api_score = address_grading.get('api_validation_score', 0.0)
        print("Address API call")
        print("-" * 80)
        print(f"{api_score:.3f}")
        print()
        
        # DOB Score
        dob_grading = metrics.get('dob_grading', {})
        dob_score = dob_grading.get('overall_score', 0.0)
        print("DOB Score")
        print("-" * 80)
        print(f"{dob_score:.3f}")
        print()
        
        # Penalties
        penalties = metrics.get('penalties', {})
        
        print("Completeness Multiplier")
        print("-" * 80)
        completeness = metrics.get('completeness_multiplier', 1.0)
        print(f"{completeness:.3f}")
        print()
        
        print("Extra names penalty")
        print("-" * 80)
        extra_penalty = penalties.get('extra_names_penalty', 0.0)
        print(f"{extra_penalty:.3f}")
        print()
        
        print("Missing names penalty")
        print("-" * 80)
        missing_penalty = penalties.get('missing_names_penalty', 0.0)
        print(f"{missing_penalty:.3f}")
        print()
        
        print("Post Penalty")
        print("-" * 80)
        print(f"{final_score:.3f}")
        print()
        
        print("Address Penalty")
        print("-" * 80)
        addr_penalty = penalties.get('address_penalty', 0.0)
        print(f"{addr_penalty:.3f}")
        print()
        
        print("Collusion Penalty")
        print("-" * 80)
        collusion_penalty = penalties.get('collusion_penalty', 0.0)
        print(f"{collusion_penalty:.3f}")
        print()
        
        print("Duplication Penalty")
        print("-" * 80)
        dup_penalty = penalties.get('duplication_penalty', 0.0)
        print(f"{dup_penalty:.3f}")
        print()
        
        print("Signature Copy Penalty")
        print("-" * 80)
        sig_penalty = penalties.get('signature_copy_penalty', 0.0)
        print(f"{sig_penalty:.3f}")
        print()
        
        print("Special Chars Penalty")
        print("-" * 80)
        special_chars_penalty = penalties.get('special_chars_penalty', 0.0)
        print(f"{special_chars_penalty:.3f}")
        print()
    else:
        print("❌ No detailed metrics returned")
        print(f"Rewards: {rewards}")
        if detailed_metrics:
            print(f"Detailed metrics keys: {list(detailed_metrics[0].keys())}")
        else:
            print("No detailed metrics available")

if __name__ == "__main__":
    result = test_local_miner_processing()
    
    if result:
        synapse, variations = result
        print("=" * 80)
        print("SENDING TO VALIDATOR REWARD CALCULATION")
        print("=" * 80)
        print()
        
        calculate_final_score(synapse, variations)
        
        print("=" * 80)
        print("✅ TEST COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print()
        print("This reproduces the complete cycle:")
        print("1. Validator sends request to miner (IdentitySynapse)")
        print("2. Miner receives and processes")
        print("3. Miner returns with variations populated")
        print("4. Validator calculates final score using reward.py")
    else:
        print("=" * 80)
        print("❌ TEST FAILED")
        print("=" * 80)

