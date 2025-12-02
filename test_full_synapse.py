"""
Test full validator synapse with unified_generator
Simulates exactly how validator sends data to miner and tests with rewards.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'MIID', 'validator'))

from unified_generator import process_full_synapse
from reward import get_name_variation_rewards
import numpy as np

# Simulate a validator synapse exactly as it sends to miner
# Format: List of [name, dob, address] arrays
identity_list = [
    ["Sebastian Martinez", "1990-05-15", "New York, USA"],
    ["Constantinople Alexandrov", "1985-03-22", "Moscow, Russia"],
    ["Xavier Rodriguez", "1992-11-08", "Madrid, Spain"],
    ["Theodore Williams", "1988-07-14", "London, UK"],
    ["Archimedes Johnson", "1995-01-30", "Chicago, USA"],
    ["Guillermo Fernandez", "1991-09-25", "Barcelona, Spain"],
    ["Bartholomew Anderson", "1987-12-05", "Sydney, Australia"],
    ["Christopher Thompson", "1993-06-18", "Toronto, Canada"],
    ["Alexander Petrovich", "1989-04-12", "St. Petersburg, Russia"],
    ["Benjamin Harrison", "1994-08-20", "Boston, USA"],
]

# Extract seed data
seed_names = [identity[0] for identity in identity_list]
seed_dob = [identity[1] for identity in identity_list]
seed_addresses = [identity[2] for identity in identity_list]
seed_script = ["latin"] * len(seed_names)  # All are Latin script

# Query parameters (as validator would send)
variation_count = 10
phonetic_similarity = {"Light": 0.2, "Medium": 0.6, "Far": 0.2}
orthographic_similarity = {"Light": 0.2, "Medium": 0.6, "Far": 0.2}
rule_based = None

print("="*100)
print("FULL VALIDATOR SYNAPSE TEST")
print("="*100)
print()
print(f"Processing {len(identity_list)} identities")
print(f"Variation count per identity: {variation_count}")
print(f"Phonetic similarity: {phonetic_similarity}")
print(f"Orthographic similarity: {orthographic_similarity}")
print()

# Process the synapse (simulate miner processing)
print("="*100)
print("PROCESSING SYNAPSE (MINER SIMULATION)")
print("="*100)
print()

variations_dict = process_full_synapse(
    identity_list=identity_list,
    variation_count=variation_count,
    light_pct=phonetic_similarity["Light"],
    medium_pct=phonetic_similarity["Medium"],
    far_pct=phonetic_similarity["Far"],
    verbose=False,  # Set to False to speed up
    use_perfect_addresses=True  # Use real addresses that score 1.0 (set False for exploit method)
)

print()
print("="*100)
print("MINER OUTPUT (VARIATIONS)")
print("="*100)
print()

for name, vars_list in variations_dict.items():
    print(f"{name}: {len(vars_list)} variations")
    # Show first 3 variations
    for i, var in enumerate(vars_list[:3], 1):
        print(f"  {i}. Name: {var[0]}, DOB: {var[1]}, Address: {var[2]}")

print()
print("="*100)
print("TESTING WITH REWARDS.PY (VALIDATOR SCORING)")
print("="*100)
print()

# Create a mock response object (as validator expects)
class MockResponse:
    def __init__(self, variations):
        self.variations = variations

# Create response as validator expects
response = MockResponse(variations_dict)
responses = [response]  # List of responses (one miner)
uids = [1]  # Mock UID

# Calculate rewards using validator's function
# Note: get_name_variation_rewards is a method, so we need to create a mock object
class MockNeuron:
    burn_fraction = 0.40
    top_miner_cap = 10
    quality_threshold = 0.5
    decay_rate = 0.1
    blend_factor = 0.5

class MockConfig:
    def __init__(self):
        self.neuron = MockNeuron()

class MockValidator:
    def __init__(self):
        self.uid = 0  # Validator UID (required by reward function)
        self.config = MockConfig()  # Config object with neuron attributes
    
    def get_name_variation_rewards(self, seed_names, seed_dob, seed_addresses, seed_script, 
                                   responses, uids, variation_count, phonetic_similarity, 
                                   orthographic_similarity, rule_based):
        return get_name_variation_rewards(
            self, seed_names, seed_dob, seed_addresses, seed_script,
            responses, uids, variation_count, phonetic_similarity,
            orthographic_similarity, rule_based
        )

validator = MockValidator()

try:
    rewards, base_rewards, detailed_metrics = validator.get_name_variation_rewards(
        seed_names=seed_names,
        seed_dob=seed_dob,
        seed_addresses=seed_addresses,
        seed_script=seed_script,
        responses=responses,
        uids=uids,
        variation_count=variation_count,
        phonetic_similarity=phonetic_similarity,
        orthographic_similarity=orthographic_similarity,
        rule_based=rule_based
    )
    
    print(f"Final Reward: {rewards[0]:.4f}")
    print(f"Base Reward: {base_rewards[0]:.4f}")
    print()
    
    if detailed_metrics:
        metrics = detailed_metrics[0]
        print("="*100)
        print("DETAILED SCORING BREAKDOWN")
        print("="*100)
        print()
        
        # Final score (post-penalty, after all processing)
        final_score = metrics.get('final_reward', 0.0)
        print(f"Final score")
        print(f"{final_score:.3f}")
        print()
        
        # Names score (average quality)
        names_score = metrics.get('average_quality', 0.0)
        print(f"Names")
        print(f"{names_score:.3f}")
        print()
        
        # Aggregate name metrics from all identities
        if "name_metrics" in metrics and metrics["name_metrics"]:
            name_metrics = metrics["name_metrics"]
            
            # Calculate aggregate metrics
            all_base_scores = []
            all_similarity_scores = []
            all_phonetic_scores = []
            all_orthographic_scores = []
            all_count_scores = []
            all_uniqueness_scores = []
            all_length_scores = []
            all_rule_compliance_scores = []
            
            for name, name_data in name_metrics.items():
                # Base score
                if "base_score" in name_data:
                    all_base_scores.append(name_data["base_score"])
                
                # First name metrics
                if "first_name" in name_data and "metrics" in name_data["first_name"]:
                    first_metrics = name_data["first_name"]["metrics"]
                    if "similarity" in first_metrics:
                        sim = first_metrics["similarity"]
                        if "combined" in sim:
                            all_similarity_scores.append(sim["combined"])
                        if "phonetic" in sim:
                            all_phonetic_scores.append(sim["phonetic"])
                        if "orthographic" in sim:
                            all_orthographic_scores.append(sim["orthographic"])
                    if "count" in first_metrics and "score" in first_metrics["count"]:
                        all_count_scores.append(first_metrics["count"]["score"])
                    if "uniqueness" in first_metrics and "score" in first_metrics["uniqueness"]:
                        all_uniqueness_scores.append(first_metrics["uniqueness"]["score"])
                    if "length" in first_metrics and "score" in first_metrics["length"]:
                        all_length_scores.append(first_metrics["length"]["score"])
                
                # Last name metrics (add to same lists for averaging)
                if "last_name" in name_data and "metrics" in name_data["last_name"]:
                    last_metrics = name_data["last_name"]["metrics"]
                    if "similarity" in last_metrics:
                        sim = last_metrics["similarity"]
                        if "combined" in sim:
                            all_similarity_scores.append(sim["combined"])
                        if "phonetic" in sim:
                            all_phonetic_scores.append(sim["phonetic"])
                        if "orthographic" in sim:
                            all_orthographic_scores.append(sim["orthographic"])
                    if "count" in last_metrics and "score" in last_metrics["count"]:
                        all_count_scores.append(last_metrics["count"]["score"])
                    if "uniqueness" in last_metrics and "score" in last_metrics["uniqueness"]:
                        all_uniqueness_scores.append(last_metrics["uniqueness"]["score"])
                    if "length" in last_metrics and "score" in last_metrics["length"]:
                        all_length_scores.append(last_metrics["length"]["score"])
                
                # Rule compliance (if exists)
                if "rule_compliance" in name_data and "score" in name_data["rule_compliance"]:
                    all_rule_compliance_scores.append(name_data["rule_compliance"]["score"])
            
            # Basic Quality Score (average base score)
            basic_quality = sum(all_base_scores) / len(all_base_scores) if all_base_scores else 0.0
            print(f"Basic Quality Score")
            print(f"{basic_quality:.3f}")
            print()
            
            # Similarity Score (average combined similarity)
            similarity_score = sum(all_similarity_scores) / len(all_similarity_scores) if all_similarity_scores else 0.0
            print(f"Similarity Score")
            print(f"{similarity_score:.3f}")
            print()
            
            # Phonetic Similarity
            phonetic_score = sum(all_phonetic_scores) / len(all_phonetic_scores) if all_phonetic_scores else 0.0
            print(f"Phonetic Similarity")
            print(f"{phonetic_score:.3f}")
            print()
            
            # Orthographic Similarity
            orthographic_score = sum(all_orthographic_scores) / len(all_orthographic_scores) if all_orthographic_scores else 0.0
            print(f"Orthographic Similarity")
            print(f"{orthographic_score:.3f}")
            print()
            
            # Count Score
            count_score = sum(all_count_scores) / len(all_count_scores) if all_count_scores else 0.0
            print(f"Count Score")
            print(f"{count_score:.3f}")
            print()
            
            # Uniqueness Score
            uniqueness_score = sum(all_uniqueness_scores) / len(all_uniqueness_scores) if all_uniqueness_scores else 0.0
            print(f"Uniqueness Score")
            print(f"{uniqueness_score:.3f}")
            print()
            
            # Length Score
            length_score = sum(all_length_scores) / len(all_length_scores) if all_length_scores else 0.0
            print(f"Length Score")
            print(f"{length_score:.3f}")
            print()
            
            # Rule Compliance Score
            rule_compliance_score = sum(all_rule_compliance_scores) / len(all_rule_compliance_scores) if all_rule_compliance_scores else 0.0
            print(f"Rule Compliance Score")
            print(f"{rule_compliance_score:.3f}")
            print()
        
        # Address Score
        address_grading = metrics.get('address_grading', {})
        address_score = address_grading.get('overall_score', 0.0)
        print(f"Address Score")
        print(f"{address_score:.3f}")
        print()
        
        # Address sub-scores
        # heuristic_perfect is boolean, convert to 0.0 or 1.0
        address_looks_like = 1.0 if address_grading.get('heuristic_perfect', False) else 0.0
        # region_matches is a count, but we need a score (0.0-1.0)
        # For now, show as 0.0 if no matches, 1.0 if any matches
        address_region_match = 1.0 if address_grading.get('region_matches', 0) > 0 else 0.0
        # api_result is boolean
        address_api_call = 1.0 if address_grading.get('api_result', False) else 0.0
        
        print(f"Looks Like Address")
        print(f"{address_looks_like:.3f}")
        print()
        print(f"Address Regain Match")
        print(f"{address_region_match:.3f}")
        print()
        print(f"Address API call")
        print(f"{address_api_call:.3f}")
        print()
        
        # DOB Score
        dob_grading = metrics.get('dob_grading', {})
        dob_score = dob_grading.get('overall_score', 0.0)
        print(f"DOB Score")
        print(f"{dob_score:.3f}")
        print()
        
        # Completeness Multiplier
        completeness_multiplier = metrics.get('completeness_multiplier', 1.0)
        print(f"Completeness Multiplier")
        print(f"{completeness_multiplier:.3f}")
        print()
        
        # Penalties
        penalties = metrics.get("penalties", {})
        print(f"Extra names penalty")
        print(f"{penalties.get('extra_names', 0.0):.3f}")
        print()
        print(f"Missing names penalty")
        print(f"{penalties.get('missing_names', 0.0):.3f}")
        print()
        
        # Post penalty (similarity penalty)
        post_penalty = metrics.get('similarity_penalty', 0.0)
        print(f"Post Penalty")
        print(f"{post_penalty:.3f}")
        print()
        
        # Address penalty
        address_penalty = penalties.get('insufficient_addresses', 0.0)
        print(f"Address Penalty")
        print(f"{address_penalty:.3f}")
        print()
        
        # Other penalties
        collusion_penalty = metrics.get('collusion_penalty', 0.0)
        duplication_penalty = penalties.get('total_penalty', 0.0) - address_penalty - penalties.get('extra_names', 0.0) - penalties.get('missing_names', 0.0)
        signature_copy_penalty = metrics.get('signature_copy_penalty', 0.0)
        special_chars_penalty = penalties.get('numbers_in_names', 0.0)
        
        print(f"Collusion Penalty")
        print(f"{collusion_penalty:.3f}")
        print()
        print(f"Duplication Penalty")
        print(f"{duplication_penalty:.3f}")
        print()
        print(f"Signature Copy Penalty")
        print(f"{signature_copy_penalty:.3f}")
        print()
        print(f"Special Chars Penalty")
        print(f"{special_chars_penalty:.3f}")
        print()
        
        print("="*100)
        print("NOTE: Using exploit address method")
        print("="*100)
        print("The address generation uses generate_exploit_addresses() which generates")
        print("valid-looking addresses that pass the looks_like_address() heuristic.")
        print("If the validator has empty seed_addresses, this will get a 1.0 score automatically.")
        print("Otherwise, addresses will pass looks_like_address but may fail region/API validation.")
        print()
        
except Exception as e:
    print(f"❌ Error calculating rewards: {e}")
    import traceback
    traceback.print_exc()

