#!/usr/bin/env python3
"""
Show what the validator actually sends to miners - the synapse structure
"""

import json
import sys
import os

# Add paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'MIID', 'validator'))

print("="*80)
print("VALIDATOR SYNAPSE STRUCTURE")
print("="*80)
print()

# Show the IdentitySynapse structure
print("📦 IdentitySynapse Structure (what gets sent to miners):")
print("-" * 80)
print("""
IdentitySynapse(
    identity: List[Dict] - List of identity objects with:
        - name: str (e.g., "John Doe")
        - dob: str (e.g., "1990-01-15")
        - address: str (e.g., "123 Main St, City, Country")
        - script: str (e.g., "latin", "cyrillic", "arabic")
    
    query_template: str - The actual query text sent to miners
        Example format:
        "The following name is the seed name to generate variations for: {name}. 
         Generate 15 variations of the name {name}, ensuring phonetic similarity: 
         30% Light, 40% Medium, 30% Far, and orthographic similarity: 30% Light, 
         40% Medium, 30% Far, and also include 30% of variations that follow: 
         [rule-based transformations]"
    
    variations: Dict - Empty dict initially, filled by miner response
    timeout: float - Request timeout
)
""")

print()
print("="*80)
print("POSSIBLE PHONETIC & ORTHOGRAPHIC SIMILARITY DISTRIBUTIONS")
print("="*80)
print()

# Show all possible distributions from query_generator.py
phonetic_configs = [
    {"Light": 0.3, "Medium": 0.4, "Far": 0.3},  # 25% weight
    {"Light": 0.2, "Medium": 0.6, "Far": 0.2},  # 20% weight
    {"Light": 0.1, "Medium": 0.3, "Far": 0.6},  # 15% weight
    {"Light": 0.5, "Medium": 0.5},              # 12% weight
    {"Light": 0.1, "Medium": 0.5, "Far": 0.4},  # 10% weight
    {"Medium": 1.0},                            # 8% weight
    {"Light": 0.7, "Medium": 0.3},              # 5% weight
    {"Far": 1.0},                               # 3% weight
    {"Light": 1.0},                             # 2% weight
]

weights = [0.25, 0.20, 0.15, 0.12, 0.10, 0.08, 0.05, 0.03, 0.02]

print("Phonetic Similarity Configurations (weighted random selection):")
print("-" * 80)
for i, (config, weight) in enumerate(zip(phonetic_configs, weights), 1):
    config_str = ", ".join([f"{int(pct*100)}% {level}" for level, pct in config.items()])
    print(f"{i:2d}. {config_str:50s} (Weight: {weight*100:.0f}%)")

print()
print("Orthographic Similarity Configurations (same as phonetic):")
print("-" * 80)
for i, (config, weight) in enumerate(zip(phonetic_configs, weights), 1):
    config_str = ", ".join([f"{int(pct*100)}% {level}" for level, pct in config.items()])
    print(f"{i:2d}. {config_str:50s} (Weight: {weight*100:.0f}%)")

print()
print("="*80)
print("EXAMPLE QUERY TEMPLATE")
print("="*80)
print()

# Example query template
example_phonetic = {"Light": 0.3, "Medium": 0.4, "Far": 0.3}
example_orthographic = {"Light": 0.3, "Medium": 0.4, "Far": 0.3}
variation_count = 15
rule_percentage = 30

phonetic_spec = ", ".join([f"{int(pct*100)}% {level}" for level, pct in example_phonetic.items()])
orthographic_spec = ", ".join([f"{int(pct*100)}% {level}" for level, pct in example_orthographic.items()])

example_template = (
    f"The following name is the seed name to generate variations for: {{name}}. "
    f"Generate {variation_count} variations of the name {{name}}, "
    f"ensuring phonetic similarity: {phonetic_spec}, "
    f"and orthographic similarity: {orthographic_spec}, "
    f"and also include {rule_percentage}% of variations that follow: "
    f"[rule-based transformations]"
)

print("Example Query Template:")
print("-" * 80)
print(example_template)
print()

print("="*80)
print("KEY POINTS")
print("="*80)
print()
print("1. ✅ The validator does NOT always send 100% Medium similarity")
print("2. ✅ It randomly selects from 9 different distributions")
print("3. ✅ Most common: Balanced (30% Light, 40% Medium, 30% Far) - 25% chance")
print("4. ✅ Second most common: Focused Medium (20% Light, 60% Medium, 20% Far) - 20% chance")
print("5. ✅ 100% Medium only happens 8% of the time")
print("6. ✅ The query_template is a string with {name} placeholder")
print("7. ✅ Miners receive the same query_template for all names in the batch")
print("8. ✅ Each name gets the template with {name} replaced by actual name")
print()

print("="*80)
print("WHAT MINERS SEE")
print("="*80)
print()
print("For a name like 'John Doe', miners receive:")
print("-" * 80)
formatted_example = example_template.replace("{name}", "John Doe")
print(formatted_example)
print()

print("="*80)

