#!/usr/bin/env python3
"""
Test orthographic generator output against rewards.py and cheat_detection.py
"""

import sys
import os
import json
import numpy as np

# Set USER_AGENT to avoid 403 errors from Nominatim
os.environ['USER_AGENT'] = "MIIDSubnet/1.0 (contact: prasadpsd2001@gmail.com)"

# Add MIID/validator to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'MIID', 'validator'))

from reward import get_name_variation_rewards
from cheat_detection import detect_cheating_patterns, normalize_address_for_deduplication

def display_detailed_scores(metrics: dict, final_reward: float, total_penalty: float):
    """Display detailed score breakdown in the requested format"""
    print("\n" + "=" * 80)
    print("DETAILED SCORE BREAKDOWN")
    print("=" * 80)
    
    # Calculate components to verify formula
    avg_quality = metrics.get('average_quality', 0.0)
    dob_grading = metrics.get('dob_grading', {})
    dob_score = dob_grading.get('overall_score', 0.0) if dob_grading else 0.0
    address_grading = metrics.get('address_grading', {})
    address_score = address_grading.get('overall_score', 0.0) if address_grading else 0.0
    completeness = metrics.get('completeness_multiplier', 1.0)
    
    # Formula: final_quality = (avg_quality * 0.2) + (dob_score * 0.1) + (address_score * 0.7)
    # Then: final_reward = final_quality * completeness_multiplier
    # Then penalties are applied
    quality_weight = 0.2
    dob_weight = 0.1
    address_weight = 0.7
    
    quality_component = avg_quality * quality_weight
    dob_component = dob_score * dob_weight
    address_component = address_score * address_weight
    final_quality = quality_component + dob_component + address_component
    before_penalties = final_quality * completeness
    
    # Final Score (after all penalties and ranking)
    print(f"\nFinal Score\n  {final_reward:.3f}")
    
    # Show formula breakdown
    print(f"\n  Formula Breakdown:")
    print(f"    Step 1: Calculate Identity Quality")
    print(f"      Names Component: {avg_quality:.3f} × {quality_weight} = {quality_component:.3f}")
    print(f"      DOB Component: {dob_score:.3f} × {dob_weight} = {dob_component:.3f}")
    print(f"      Address Component: {address_score:.3f} × {address_weight} = {address_component:.3f}")
    print(f"      → Identity Quality: {final_quality:.3f}")
    print(f"    Step 2: Apply Completeness Multiplier")
    print(f"      {final_quality:.3f} × {completeness:.3f} = {before_penalties:.3f}")
    
    # Check ranking info
    ranking_info = metrics.get('ranking_info', {})
    if ranking_info:
        initial_reward = ranking_info.get('initial_reward', before_penalties)
        final_blended = ranking_info.get('final_blended_reward', final_reward)
        is_qualified = ranking_info.get('is_qualified_for_ranking', True)
        meets_threshold = ranking_info.get('meets_quality_threshold', True)
        within_cap = ranking_info.get('within_top_cap', True)
        global_rank = ranking_info.get('global_rank', 0)
        
        print(f"    Step 3: Apply Penalties (if any)")
        print(f"      After Penalties: {initial_reward:.3f}")
        print(f"    Step 4: Apply Ranking/Cap/Quality Threshold")
        print(f"      Within Top Cap: {within_cap}")
        print(f"      Meets Quality Threshold: {meets_threshold}")
        print(f"      Qualified for Ranking: {is_qualified}")
        print(f"      Global Rank: {global_rank}")
        if is_qualified:
            print(f"      Blended Reward: {final_blended:.3f}")
            # Check if burn fraction is applied (rescaling)
            if abs(final_reward - final_blended) > 0.01:
                burn_fraction = 0.40  # Default from config
                keep_fraction = 1.0 - burn_fraction
                # The actual formula is: final = blended × (keep_fraction / sum_of_all_blended)
                # For single miner: rescale_factor ≈ keep_fraction / blended_reward
                if final_blended > 0:
                    rescale_factor = final_reward / final_blended
                    print(f"    Step 5: Apply Burn Fraction & Rescaling")
                    print(f"      Burn Fraction: {burn_fraction*100:.0f}% burn, {keep_fraction*100:.0f}% keep")
                    print(f"      Rescale Factor: {rescale_factor:.3f}")
                    print(f"      {final_blended:.3f} × {rescale_factor:.3f} = {final_reward:.3f}")
                else:
                    print(f"    Step 5: Apply Burn Fraction ({burn_fraction*100:.0f}% burn)")
                    print(f"      {final_blended:.3f} × {keep_fraction:.2f} ≈ {final_reward:.3f}")
            else:
                print(f"    Step 5: No burn/rescaling applied")
        print(f"    → Final Reward: {final_reward:.3f}")
    else:
        print(f"    Step 3: Apply Penalties (if any)")
        print(f"      After Penalties: {before_penalties:.3f}")
        print(f"    → Final Reward: {final_reward:.3f}")
    
    # Names Score
    avg_quality = metrics.get('average_quality', 0.0)
    avg_base_score = metrics.get('average_base_score', 0.0)
    print(f"\nNames\n  {avg_quality:.3f}")
    
    # Basic Quality Score
    print(f"\n  Basic Quality Score\n    {avg_base_score:.3f}")
    
    # Similarity Score - extract from name_metrics
    name_metrics = metrics.get('name_metrics', {})
    similarity_scores = []
    phonetic_scores = []
    orthographic_scores = []
    count_scores = []
    uniqueness_scores = []
    length_scores = []
    
    for name, name_metric in name_metrics.items():
        first_name_data = name_metric.get('first_name', {})
        last_name_data = name_metric.get('last_name', {})
        
        # Extract from nested metrics structure
        first_metrics = first_name_data.get('metrics', {}) if isinstance(first_name_data, dict) else {}
        last_metrics = last_name_data.get('metrics', {}) if isinstance(last_name_data, dict) else {}
        
        # Get similarity scores
        first_sim = first_metrics.get('similarity', {})
        last_sim = last_metrics.get('similarity', {})
        
        if first_sim:
            phonetic_scores.append(first_sim.get('phonetic', 0.0))
            orthographic_scores.append(first_sim.get('orthographic', 0.0))
            similarity_scores.append(first_sim.get('combined', 0.0))
        
        if last_sim:
            phonetic_scores.append(last_sim.get('phonetic', 0.0))
            orthographic_scores.append(last_sim.get('orthographic', 0.0))
            similarity_scores.append(last_sim.get('combined', 0.0))
        
        # Count scores
        if first_metrics.get('count'):
            count_scores.append(first_metrics['count'].get('score', 0.0))
        if last_metrics.get('count'):
            count_scores.append(last_metrics['count'].get('score', 0.0))
        
        # Uniqueness scores
        if first_metrics.get('uniqueness'):
            uniqueness_scores.append(first_metrics['uniqueness'].get('score', 0.0))
        if last_metrics.get('uniqueness'):
            uniqueness_scores.append(last_metrics['uniqueness'].get('score', 0.0))
        
        # Length scores
        if first_metrics.get('length'):
            length_scores.append(first_metrics['length'].get('score', 0.0))
        if last_metrics.get('length'):
            length_scores.append(last_metrics['length'].get('score', 0.0))
    
    avg_similarity = sum(similarity_scores) / len(similarity_scores) if similarity_scores else 0.0
    avg_phonetic = sum(phonetic_scores) / len(phonetic_scores) if phonetic_scores else 0.0
    avg_orthographic = sum(orthographic_scores) / len(orthographic_scores) if orthographic_scores else 0.0
    avg_count = sum(count_scores) / len(count_scores) if count_scores else 0.0
    avg_uniqueness = sum(uniqueness_scores) / len(uniqueness_scores) if uniqueness_scores else 0.0
    avg_length = sum(length_scores) / len(length_scores) if length_scores else 0.0
    
    print(f"\n  Similarity Score\n    {avg_similarity:.3f}")
    
    print(f"\n    Phonetic Similarity\n      {avg_phonetic:.3f}")
    
    print(f"\n    Orthographic Similarity\n      {avg_orthographic:.3f}")
    
    print(f"\n  Count Score\n    {avg_count:.3f}")
    
    print(f"\n  Uniqueness Score\n    {avg_uniqueness:.3f}")
    
    print(f"\n  Length Score\n    {avg_length:.3f}")
    
    # Rule Compliance Score
    rule_compliance = metrics.get('rule_compliance', {})
    rule_score = rule_compliance.get('overall_score', 0.0) if rule_compliance else 0.0
    print(f"\n  Rule Compliance Score\n    {rule_score:.3f}")
    
    # Address Score
    address_grading = metrics.get('address_grading', {})
    address_score = address_grading.get('overall_score', 0.0) if address_grading else 0.0
    print(f"\nAddress Score\n  {address_score:.3f}")
    
    # Address sub-scores - extract from detailed_breakdown
    address_details = address_grading.get('detailed_breakdown', {}) if address_grading else {}
    validation_results = address_details.get('validation_results', {})
    
    # Calculate averages from all addresses
    looks_like_count = 0
    looks_like_total = 0
    region_match_count = 0
    region_match_total = 0
    
    for name, results in validation_results.items():
        if isinstance(results, list):
            for result in results:
                if result.get('looks_like_address', False):
                    looks_like_total += 1
                looks_like_count += 1
                
                if result.get('region_match', False):
                    region_match_total += 1
                region_match_count += 1
    
    looks_like = looks_like_total / looks_like_count if looks_like_count > 0 else 0.0
    region_match = region_match_total / region_match_count if region_match_count > 0 else 0.0
    
    # API score - check if API validation was successful
    api_validation = address_details.get('api_validation', {})
    api_result = api_validation.get('api_result', False)
    api_score = 1.0 if api_result else 0.0
    
    print(f"\n  Looks Like Address\n    {looks_like:.3f}")
    
    print(f"\n  Address Region Match\n    {region_match:.3f}")
    
    print(f"\n  Address API call\n    {api_score:.3f}")
    
    # DOB Score
    dob_grading = metrics.get('dob_grading', {})
    dob_score = dob_grading.get('overall_score', 0.0) if dob_grading else 0.0
    print(f"\nDOB Score\n  {dob_score:.3f}")
    
    # Completeness Multiplier
    completeness = metrics.get('completeness_multiplier', 1.0)
    print(f"\nCompleteness Multiplier\n  {completeness:.3f}")
    
    # Penalties
    penalties_dict = metrics.get('penalties', {})
    print(f"\nExtra names penalty\n  {penalties_dict.get('extra_names', 0.0):.3f}")
    
    print(f"\nMissing names penalty\n  {penalties_dict.get('missing_names', 0.0):.3f}")
    
    print(f"\nPost Penalty\n  {penalties_dict.get('post_total_penalty', 0.0):.3f}")
    
    print(f"\nAddress Penalty\n  {penalties_dict.get('post_address_duplication', 0.0):.3f}")
    
    print(f"\nCollusion Penalty\n  {penalties_dict.get('collusion', 0.0):.3f}")
    
    print(f"\nDuplication Penalty\n  {penalties_dict.get('duplication', 0.0):.3f}")
    
    print(f"\nSignature Copy Penalty\n  {penalties_dict.get('signature_copy', 0.0):.3f}")
    
    print(f"\nSpecial Chars Penalty\n  {penalties_dict.get('special_chars', 0.0):.3f}")
    
    print("=" * 80)

def load_generated_variations(json_file: str):
    """Load variations from the generated JSON file"""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def load_address_cache(cache_file: str = "normalized_address_cache.json"):
    """Load address cache from JSON file"""
    if not os.path.exists(cache_file):
        print(f"⚠️  Address cache file not found: {cache_file}")
        return {}
    
    with open(cache_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract addresses by country
    addresses_by_country = data.get('addresses', {})
    print(f"✅ Loaded address cache with {len(addresses_by_country)} countries")
    return addresses_by_country

def get_addresses_for_country(addresses_by_country: dict, country: str, count: int = 15):
    """Get addresses for a specific country"""
    country_addresses = addresses_by_country.get(country, [])
    if not country_addresses:
        # Try to find a similar country name
        for cached_country in addresses_by_country.keys():
            if country.lower() in cached_country.lower() or cached_country.lower() in country.lower():
                country_addresses = addresses_by_country[cached_country]
                break
    
    if not country_addresses:
        return []
    
    # Return up to count addresses, cycling if needed
    result = []
    for i in range(count):
        result.append(country_addresses[i % len(country_addresses)])
    return result

def format_for_validator(generated_data: dict, addresses_by_country: dict = None):
    """
    Convert generated variations to validator format:
    responses: List[Dict[str, List[List[str]]]]
    Each response is: {name: [[name_var, dob_var, address_var], ...]}
    """
    # Single miner response with ALL names
    combined_response = {}
    seed_names = []
    seed_dobs = []
    seed_addresses = []
    seed_scripts = []
    
    # Get list of available countries for round-robin assignment
    # Filter out countries with fewer than 15 addresses to avoid duplicates
    available_countries = []
    if addresses_by_country:
        for country, addresses in addresses_by_country.items():
            if len(addresses) >= 15:
                available_countries.append(country)
            else:
                print(f"⚠️  Skipping {country}: only {len(addresses)} addresses (need 15+)")
    
    if not available_countries:
        print("⚠️  No countries with 15+ addresses found, using all available countries")
        available_countries = list(addresses_by_country.keys()) if addresses_by_country else []
    
    country_index = 0
    
    # For each name in the generated data
    for name, name_data in generated_data.items():
        variations = name_data.get('variations', [])
        dob_variations = name_data.get('dob_variations', [])
        
        # Assign country in round-robin fashion from available countries
        if available_countries:
            seed_country = available_countries[country_index % len(available_countries)]
            country_index += 1
        else:
            seed_country = 'Angola'  # Fallback
        
        # Get addresses for this country - ensure we have enough unique addresses
        country_addresses = []
        if addresses_by_country and seed_country:
            country_addresses = get_addresses_for_country(addresses_by_country, seed_country, len(variations))
        
        # Format as validator expects: [name_var, dob_var, address_var]
        formatted_variations = []
        address_tracking = {}  # Track normalized addresses to find duplicates
        
        for i, var in enumerate(variations):
            name_var = var.get('full_name', '')
            
            # Extract DOB from variation or use from dob_variations list
            dob_var = var.get('dob', '')
            if not dob_var and i < len(dob_variations):
                dob_var = dob_variations[i]
            if not dob_var:
                dob_var = name_data.get('dob', '1985-03-15')
            
            # Use real address from cache if available, otherwise use dummy
            if country_addresses and i < len(country_addresses):
                address_var = country_addresses[i].get('address', '')
            else:
                address_var = f'{100+i} Main St, Test City, {seed_country or "Test Country"}'
            
            # Track normalized address for duplicate detection
            normalized_addr = normalize_address_for_deduplication(address_var)
            if normalized_addr not in address_tracking:
                address_tracking[normalized_addr] = []
            address_tracking[normalized_addr].append({
                'name': name,
                'variation_index': i,
                'address': address_var,
                'normalized': normalized_addr
            })
            
            formatted_variations.append([name_var, dob_var, address_var])
        
        # Add to combined response
        combined_response[name] = formatted_variations
        seed_names.append(name)
        seed_dobs.append(name_data.get('dob', '1985-03-15'))
        seed_addresses.append(seed_country or 'Angola')  # Use country name as seed address
        seed_scripts.append('latin')
    
    # Single miner with all names
    responses = [combined_response]
    uids = [1]
    
    # Collect all address tracking for duplicate analysis
    all_address_tracking = {}
    # This will be populated by the caller if needed
    
    return responses, uids, seed_names, seed_dobs, seed_addresses, seed_scripts, combined_response

def test_rewards_validation(responses, uids, seed_names, seed_dobs, seed_addresses, seed_scripts):
    """Test against rewards.py validation"""
    print("=" * 80)
    print("TESTING AGAINST rewards.py")
    print("=" * 80)
    
    # Wrap responses in objects with .variations attribute (as validator expects)
    class ResponseWrapper:
        def __init__(self, variations_dict):
            self.variations = variations_dict
    
    wrapped_responses = [ResponseWrapper(resp) for resp in responses]
    single_uids = uids
    
    try:
        # Create a proper mock object for self (get_name_variation_rewards expects self)
        class MockValidator:
            uid = 101  # Validator UID
            class MockConfig:
                class MockNeuron:
                    burn_fraction = 0.40
                    top_miner_cap = 10
                    quality_threshold = 0.5
                    decay_rate = 0.1
                    blend_factor = 0.5
                neuron = MockNeuron()
            config = MockConfig()
        
        mock_validator = MockValidator()
        rewards, penalties, detailed_metrics = get_name_variation_rewards(
            mock_validator,
            seed_names=seed_names,
            seed_dob=seed_dobs,
            seed_addresses=seed_addresses,
            seed_script=seed_scripts,
            responses=wrapped_responses,
            uids=single_uids,
            variation_count=15,
            phonetic_similarity=None,
            orthographic_similarity={"Light": 0.2, "Medium": 0.6, "Far": 0.2}
        )
        
        print(f"\n✅ Rewards calculation successful!")
        
        if detailed_metrics:
            metrics = detailed_metrics[0]
            display_detailed_scores(metrics, rewards[0], penalties[0])
        
        return rewards[0] > 0, detailed_metrics[0] if detailed_metrics else {}
        
    except Exception as e:
        print(f"\n❌ Error in rewards validation: {e}")
        import traceback
        traceback.print_exc()
        return False, {}

def test_cheat_detection(responses, uids, seed_names):
    """Test against cheat_detection.py"""
    print("\n" + "=" * 80)
    print("TESTING AGAINST cheat_detection.py")
    print("=" * 80)
    
    # Responses are already in correct format from format_for_validator
    single_response = responses
    single_uids = uids
    rewards = np.array([0.9])  # Assume good reward for testing
    
    try:
        cheating_results = detect_cheating_patterns(
            responses=single_response,
            uids=single_uids,
            rewards=rewards,
            seed_names=seed_names
        )
        
        print(f"\n✅ Cheat detection analysis successful!")
        
        # Check for penalties (exclude metrics that aren't penalties)
        penalty_keys = ['duplication_penalties', 'signature_penalties', 'collusion_penalties', 
                        'special_char_penalties', 'address_duplication_penalties']
        has_penalties = False
        print(f"\n   Cheat Detection Results:")
        for key, value_array in cheating_results.items():
            if isinstance(value_array, np.ndarray) and len(value_array) > 0:
                penalty_value = float(value_array[0])
                # Only check penalty keys, ignore metrics like total_variations_counts
                if key in penalty_keys:
                    if penalty_value > 0:
                        has_penalties = True
                        print(f"   ⚠️  {key}: {penalty_value:.4f}")
                    else:
                        print(f"   ✅ {key}: {penalty_value:.4f}")
                else:
                    # Metrics (not penalties)
                    print(f"   📊 {key}: {penalty_value:.4f}")
        
        if not has_penalties:
            print(f"\n   ✅ No cheating penalties detected!")
        
        return not has_penalties, cheating_results
        
    except Exception as e:
        print(f"\n❌ Error in cheat detection: {e}")
        import traceback
        traceback.print_exc()
        return False, {}

def generate_and_test(count: int = 3, variations: int = 15):
    """Generate names/DOBs and test with addresses from cache"""
    import subprocess
    
    print("=" * 80)
    print("GENERATING NAMES AND DOBs")
    print("=" * 80)
    print(f"Generating {count} names with {variations} variations each...")
    print()
    
    # Run the generation script (using generate_from_maximize.py)
    try:
        result = subprocess.run(
            ["python3", "generate_from_maximize.py", 
             "--count", str(count), 
             "--variations", str(variations)],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode != 0:
            print(f"❌ Generation failed: {result.stderr}")
            return None
        
        # Find the most recent generated file
        import glob
        json_files = glob.glob("orthographic_variations_*.json")
        if not json_files:
            print("❌ No orthographic variations JSON file found after generation!")
            return None
        
        latest_file = max(json_files, key=os.path.getctime)
        print(f"✅ Generated: {latest_file}")
        return latest_file
        
    except subprocess.TimeoutExpired:
        print("❌ Generation timed out")
        return None
    except Exception as e:
        print(f"❌ Error during generation: {e}")
        return None

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate and test orthographic variations")
    parser.add_argument("--count", type=int, default=3, help="Number of names to generate (default: 3)")
    parser.add_argument("--variations", type=int, default=15, help="Number of variations per name (default: 15)")
    parser.add_argument("--use-existing", action="store_true", help="Use existing generated file instead of generating new")
    
    args = parser.parse_args()
    
    # Generate or use existing
    if args.use_existing:
        import glob
        json_files = glob.glob("orthographic_variations_*.json")
        if not json_files:
            print("❌ No orthographic variations JSON file found!")
            print("   Run without --use-existing to generate new variations")
            return
        latest_file = max(json_files, key=os.path.getctime)
        print(f"📂 Using existing file: {latest_file}")
    else:
        latest_file = generate_and_test(args.count, args.variations)
        if not latest_file:
            return
        print(f"📂 Loading: {latest_file}")
    
    # Load generated variations
    generated_data = load_generated_variations(latest_file)
    print(f"✅ Loaded {len(generated_data)} names")
    
    # Load address cache
    addresses_by_country = load_address_cache("normalized_address_cache.json")
    
    # Format for validator
    responses, uids, seed_names, seed_dobs, seed_addresses, seed_scripts, combined_response = format_for_validator(
        generated_data, addresses_by_country
    )
    
    print(f"\n📊 Testing {len(seed_names)} names with variations")
    
    # Analyze addresses for duplicates
    print("\n" + "=" * 80)
    print("ADDRESS ANALYSIS")
    print("=" * 80)
    
    all_addresses = []
    all_normalized = {}
    
    for name, variations_list in combined_response.items():
        print(f"\n📝 Name: {name}")
        print(f"   Country: {seed_addresses[seed_names.index(name)]}")
        print(f"   Variations: {len(variations_list)}")
        
        for i, (name_var, dob_var, address_var) in enumerate(variations_list):
            normalized = normalize_address_for_deduplication(address_var)
            all_addresses.append({
                'name': name,
                'index': i,
                'address': address_var,
                'normalized': normalized
            })
            
            if normalized not in all_normalized:
                all_normalized[normalized] = []
            all_normalized[normalized].append({
                'name': name,
                'index': i,
                'address': address_var
            })
    
    # Find duplicates
    print(f"\n🔍 Duplicate Analysis:")
    duplicates_found = False
    for normalized, addresses in all_normalized.items():
        if len(addresses) > 1:
            duplicates_found = True
            print(f"\n   ⚠️  Duplicate normalized: {normalized}")
            for addr_info in addresses:
                print(f"      - {addr_info['name']} (var {addr_info['index']}): {addr_info['address']}")
    
    if not duplicates_found:
        print("   ✅ No duplicate addresses found!")
    
    print(f"\n   Total addresses: {len(all_addresses)}")
    print(f"   Unique normalized: {len(all_normalized)}")
    print(f"   Duplicates: {len(all_addresses) - len(all_normalized)}")
    
    # Analyze DOBs
    print("\n" + "=" * 80)
    print("DOB ANALYSIS")
    print("=" * 80)
    
    all_dobs = []
    dob_issues = []
    
    for name, variations_list in combined_response.items():
        print(f"\n📝 Name: {name}")
        print(f"   Seed DOB: {seed_dobs[seed_names.index(name)]}")
        print(f"   DOB Variations:")
        
        for i, (name_var, dob_var, address_var) in enumerate(variations_list):
            all_dobs.append(dob_var)
            
            # Check DOB format
            is_valid = True
            issue = None
            
            if not dob_var:
                is_valid = False
                issue = "Empty DOB"
            else:
                try:
                    # Try parsing as YYYY-MM-DD (full date)
                    parts = dob_var.split('-')
                    if len(parts) == 3:
                        # Full date format
                        if len(parts[0]) != 4:  # Year should be 4 digits
                            is_valid = False
                            issue = f"Invalid year: '{dob_var}'"
                        else:
                            # Valid full date
                            is_valid = True
                    elif len(parts) == 2:
                        # YYYY-MM format (Year+Month only - valid for validator!)
                        if len(parts[0]) != 4:
                            is_valid = False
                            issue = f"Invalid year: '{dob_var}'"
                        else:
                            # Valid Year+Month format (needed for score 1.0)
                            is_valid = True
                    else:
                        is_valid = False
                        issue = f"Invalid format: '{dob_var}'"
                except:
                    is_valid = False
                    issue = f"Parse error: '{dob_var}'"
            
            if not is_valid:
                dob_issues.append({
                    'name': name,
                    'variation': i,
                    'dob': dob_var,
                    'issue': issue
                })
                print(f"      ⚠️  Var {i}: {dob_var} - {issue}")
            else:
                # Check if it's YYYY-MM format (Year+Month only)
                if len(dob_var.split('-')) == 2:
                    print(f"      ✅ Var {i}: {dob_var} (Year+Month only - for score 1.0)")
                else:
                    print(f"      ✅ Var {i}: {dob_var}")
    
    print(f"\n📊 DOB Summary:")
    print(f"   Total DOBs: {len(all_dobs)}")
    print(f"   Unique DOBs: {len(set(all_dobs))}")
    print(f"   Issues found: {len(dob_issues)}")
    
    if dob_issues:
        print(f"\n   ⚠️  DOB Issues:")
        for issue in dob_issues:
            print(f"      - {issue['name']} (var {issue['variation']}): {issue['issue']}")
    else:
        print(f"\n   ✅ All DOBs are valid!")
    
    # Test rewards.py
    rewards_pass, rewards_metrics = test_rewards_validation(
        responses, uids, seed_names, seed_dobs, seed_addresses, seed_scripts
    )
    
    # Test cheat_detection.py
    cheat_pass, cheat_results = test_cheat_detection(responses, uids, seed_names)
    
    # Final summary
    print("\n" + "=" * 80)
    print("FINAL VALIDATION SUMMARY")
    print("=" * 80)
    print(f"✅ rewards.py validation: {'PASS' if rewards_pass else 'FAIL'}")
    print(f"✅ cheat_detection.py validation: {'PASS' if cheat_pass else 'FAIL'}")
    
    if rewards_pass and cheat_pass:
        print("\n🎉 All validations passed! Variations are ready for use.")
    else:
        print("\n⚠️  Some validations failed. Review the output above.")

if __name__ == "__main__":
    main()

