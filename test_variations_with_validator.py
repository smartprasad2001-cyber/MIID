#!/usr/bin/env python3
"""
Test variations from unified_generator_output.json with rewards.py
Get detailed score breakdown
"""

import os
import sys
import json

# Flush output immediately
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

print("🔍 Starting validation test...", flush=True)

# Add paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'MIID', 'validator'))

print("📦 Importing modules...", flush=True)

try:
    from reward import get_name_variation_rewards
    print("✅ Imports successful", flush=True)
except Exception as e:
    print(f"❌ Import error: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Create a mock validator class
class MockNeuronConfig:
    """Mock neuron config with default values"""
    def __init__(self):
        self.burn_fraction = 0.40
        self.top_miner_cap = 10
        self.quality_threshold = 0.5
        self.decay_rate = 0.1
        self.blend_factor = 0.5

class MockConfig:
    """Mock config with neuron attribute"""
    def __init__(self):
        self.neuron = MockNeuronConfig()

class MockValidator:
    """Mock validator class to use get_name_variation_rewards"""
    def __init__(self):
        self.config = MockConfig()
        self.uid = 0  # Validator UID

def format_detailed_scores(detailed_metrics: dict) -> str:
    """Format detailed scores like the example"""
    output = []
    
    # Extract scores from detailed_metrics
    final_score = detailed_metrics.get('final_reward', 0.0)
    names_score = detailed_metrics.get('average_quality', 0.0)
    
    # Get name metrics
    name_metrics = detailed_metrics.get('name_metrics', {})
    if name_metrics:
        # Aggregate across all names
        all_basic_quality = []
        all_similarity = []
        all_phonetic = []
        all_orthographic = []
        all_count = []
        all_uniqueness = []
        all_length = []
        all_rule_compliance = []
        
        for name, metrics in name_metrics.items():
            # Get base score (quality_score)
            all_basic_quality.append(metrics.get('base_score', 0.0))
            
            # Extract similarity scores from nested structure
            # Similarity is in first_name.metrics.similarity and last_name.metrics.similarity
            fn_similarity = metrics.get('first_name', {}).get('metrics', {}).get('similarity', {})
            ln_similarity = metrics.get('last_name', {}).get('metrics', {}).get('similarity', {})
            
            # Get phonetic and combined (orthographic) similarity
            fn_phonetic = fn_similarity.get('phonetic', 0.0)
            fn_combined = fn_similarity.get('combined', 0.0)
            ln_phonetic = ln_similarity.get('phonetic', 0.0) if ln_similarity else 0.0
            ln_combined = ln_similarity.get('combined', 0.0) if ln_similarity else 0.0
            
            # Average first and last name similarities
            phonetic = (fn_phonetic + ln_phonetic) / 2.0 if ln_similarity else fn_phonetic
            combined = (fn_combined + ln_combined) / 2.0 if ln_similarity else fn_combined
            
            all_phonetic.append(phonetic)
            all_orthographic.append(combined)  # combined includes orthographic
            all_similarity.append((phonetic + combined) / 2.0)  # Average of phonetic and orthographic
            
            # Extract other scores from nested structure
            fn_metrics = metrics.get('first_name', {}).get('metrics', {})
            ln_metrics = metrics.get('last_name', {}).get('metrics', {}) if metrics.get('last_name') else {}
            
            fn_count = fn_metrics.get('count', {}).get('score', 0.0)
            ln_count = ln_metrics.get('count', {}).get('score', 0.0) if ln_metrics else 0.0
            count = (fn_count + ln_count) / 2.0 if ln_metrics else fn_count
            all_count.append(count)
            
            fn_uniqueness = fn_metrics.get('uniqueness', {}).get('score', 0.0)
            ln_uniqueness = ln_metrics.get('uniqueness', {}).get('score', 0.0) if ln_metrics else 0.0
            uniqueness = (fn_uniqueness + ln_uniqueness) / 2.0 if ln_metrics else fn_uniqueness
            all_uniqueness.append(uniqueness)
            
            fn_length = fn_metrics.get('length', {}).get('score', 0.0)
            ln_length = ln_metrics.get('length', {}).get('score', 0.0) if ln_metrics else 0.0
            length = (fn_length + ln_length) / 2.0 if ln_metrics else fn_length
            all_length.append(length)
            
            # Rule compliance (if exists)
            rule_comp = metrics.get('rule_compliance', {}).get('score', 0.0)
            all_rule_compliance.append(rule_comp)
        
        basic_quality = sum(all_basic_quality) / len(all_basic_quality) if all_basic_quality else 0.0
        similarity_score = sum(all_similarity) / len(all_similarity) if all_similarity else 0.0
        phonetic_similarity = sum(all_phonetic) / len(all_phonetic) if all_phonetic else 0.0
        orthographic_similarity = sum(all_orthographic) / len(all_orthographic) if all_orthographic else 0.0
        count_score = sum(all_count) / len(all_count) if all_count else 0.0
        uniqueness_score = sum(all_uniqueness) / len(all_uniqueness) if all_uniqueness else 0.0
        length_score = sum(all_length) / len(all_length) if all_length else 0.0
        rule_compliance = sum(all_rule_compliance) / len(all_rule_compliance) if all_rule_compliance else 0.0
    else:
        basic_quality = similarity_score = phonetic_similarity = orthographic_similarity = 0.0
        count_score = uniqueness_score = length_score = rule_compliance = 0.0
    
    # Get address and DOB scores from grading objects
    dob_grading = detailed_metrics.get('dob_grading', {})
    dob_score = dob_grading.get('overall_score', 0.0) if dob_grading else 0.0
    
    address_grading = detailed_metrics.get('address_grading', {})
    address_score = address_grading.get('overall_score', 0.0) if address_grading else 0.0
    
    # Get address breakdown from address_grading
    address_breakdown = address_grading.get('breakdown', {}) if address_grading else {}
    looks_like_address = address_breakdown.get('heuristic_perfect', False)
    region_match = address_breakdown.get('region_matches', 0) if isinstance(address_breakdown.get('region_matches'), (int, float)) else (1.0 if address_breakdown.get('region_matches') else 0.0)
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
    print("="*80, flush=True)
    print("TESTING VARIATIONS WITH VALIDATOR", flush=True)
    print("="*80, flush=True)
    print(flush=True)
    
    # Load variations from unified_generator_output.json
    print("📂 Loading variations from unified_generator_output.json...", flush=True)
    input_file = "unified_generator_output.json"
    
    if not os.path.exists(input_file):
        print(f"❌ File not found: {input_file}", flush=True)
        return
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        variations = data.get('variations', {})
        print(f"✅ Loaded variations for {len(variations)} names\n", flush=True)
    except Exception as e:
        print(f"❌ Error loading file: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return
    
    # Prepare parameters for get_name_variation_rewards
    # Extract seed names, DOBs, addresses, and scripts
    seed_names = []
    seed_dob = []
    seed_addresses = []
    seed_script = []
    
    # Load sanctioned names to get scripts
    sanctioned_file = os.path.join(os.path.dirname(__file__), 'MIID', 'validator', 'Sanctioned_Transliteration.json')
    sanctioned_map = {}
    
    try:
        with open(sanctioned_file, 'r', encoding='utf-8') as f:
            sanctioned_list = json.load(f)
            for person in sanctioned_list:
                first_name = person.get('FirstName', '')
                last_name = person.get('LastName', '')
                full_name = f"{first_name} {last_name}".strip()
                script = person.get('Script', 'latin')
                dob = person.get('DOB', '1990-01-01')
                sanctioned_map[full_name] = {'script': script, 'dob': dob}
    except Exception as e:
        print(f"⚠️  Could not load sanctioned list: {e}", flush=True)
    
    for name in variations.keys():
        seed_names.append(name)
        # Get DOB from first variation or sanctioned list
        if variations[name] and len(variations[name]) > 0:
            seed_dob.append(variations[name][0][1] if len(variations[name][0]) > 1 else '1990-01-01')
        else:
            seed_dob.append(sanctioned_map.get(name, {}).get('dob', '1990-01-01'))
        seed_addresses.append("")  # Blank address
        seed_script.append(sanctioned_map.get(name, {}).get('script', 'latin'))
    
    print(f"📊 Prepared {len(seed_names)} names for validation", flush=True)
    print(f"   Seed names: {seed_names[:3]}..." if len(seed_names) > 3 else f"   Seed names: {seed_names}", flush=True)
    print(flush=True)
    
    # Prepare parameters for get_name_variation_rewards
    mock_validator = MockValidator()
    
    # Create a response object with variations attribute
    class ResponseObject:
        def __init__(self, variations_dict):
            self.variations = variations_dict
    
    response_obj = ResponseObject(variations)
    responses = [response_obj]  # List of responses (one miner)
    uids = [501]  # Single miner UID
    variation_count = 15
    phonetic_similarity = {"Medium": 1.0}
    orthographic_similarity = {"Medium": 1.0}
    rule_based = None  # No rule-based requirements for this test
    
    print("🧪 Testing with validator...", flush=True)
    print(f"   Variation count: {variation_count}", flush=True)
    print(f"   Phonetic similarity: {phonetic_similarity}", flush=True)
    print(f"   Orthographic similarity: {orthographic_similarity}", flush=True)
    print(flush=True)
    
    try:
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
        
        if detailed_metrics_list and len(detailed_metrics_list) > 0:
            detailed_metrics = detailed_metrics_list[0]
            final_score = rewards[0] if len(rewards) > 0 else 0.0
            
            print("\n" + "="*80, flush=True)
            print("DETAILED SCORE BREAKDOWN", flush=True)
            print("="*80, flush=True)
            print(flush=True)
            print(format_detailed_scores(detailed_metrics), flush=True)
            print(flush=True)
            
            # Save results
            output_file = "validator_test_results.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "test_date": __import__('datetime').datetime.now().isoformat(),
                    "seed_names": seed_names,
                    "seed_dob": seed_dob,
                    "seed_addresses": seed_addresses,
                    "seed_script": seed_script,
                    "variations": variations,
                    "final_score": float(final_score),
                    "detailed_metrics": detailed_metrics,
                    "formatted_scores": format_detailed_scores(detailed_metrics)
                }, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Results saved to {output_file}", flush=True)
        else:
            print("❌ No detailed metrics returned", flush=True)
            
    except Exception as e:
        print(f"❌ Error testing with validator: {e}", flush=True)
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()

