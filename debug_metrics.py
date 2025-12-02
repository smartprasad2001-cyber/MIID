"""Debug script to check metrics structure"""
import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'MIID', 'validator'))

from unified_generator import process_full_synapse
from reward import get_name_variation_rewards

# Simple test
identity_list = [['John Smith', '1990-05-15', 'New York, USA']]
variations_dict = process_full_synapse(identity_list, variation_count=10, verbose=False)

class MockResponse:
    def __init__(self, variations):
        self.variations = variations

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
        self.uid = 0
        self.config = MockConfig()

validator = MockValidator()
response = MockResponse(variations_dict)
rewards, base_rewards, detailed_metrics = get_name_variation_rewards(
    validator,
    seed_names=['John Smith'],
    seed_dob=['1990-05-15'],
    seed_addresses=['New York, USA'],
    seed_script=['latin'],
    responses=[response],
    uids=[1],
    variation_count=10,
    phonetic_similarity={'Light': 0.2, 'Medium': 0.6, 'Far': 0.2},
    orthographic_similarity={'Light': 0.2, 'Medium': 0.6, 'Far': 0.2},
    rule_based=None
)

# Print the structure
metrics = detailed_metrics[0]
print('='*80)
print('TOP LEVEL KEYS:', list(metrics.keys()))
print('='*80)

if 'name_metrics' in metrics and metrics['name_metrics']:
    first_name = list(metrics['name_metrics'].keys())[0]
    print(f'\nFirst name in name_metrics: {first_name}')
    print(f'\nKeys for {first_name}:', list(metrics['name_metrics'][first_name].keys()))
    
    name_data = metrics['name_metrics'][first_name]
    print(f'\nFull structure for {first_name}:')
    print(json.dumps(name_data, indent=2, default=str)[:3000])

print('\n' + '='*80)
print('ADDRESS GRADING KEYS:', list(metrics.get('address_grading', {}).keys()))
print('ADDRESS GRADING:')
addr_grading = metrics.get('address_grading', {})
print(json.dumps({k: v for k, v in addr_grading.items() if k != 'detailed_results'}, indent=2, default=str))
print('\n' + '='*80)
print('DOB GRADING:')
print(json.dumps(metrics.get('dob_grading', {}), indent=2, default=str)[:1500])

