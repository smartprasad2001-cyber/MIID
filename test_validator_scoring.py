#!/usr/bin/env python3
"""
Test validator scoring with real query template from logs
"""

import os
import sys
import json
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from MIID.validator.gemini_generator import generate_variations_with_gemini
from MIID.protocol import IdentitySynapse
from MIID.validator.reward import calculate_variation_quality, MIID_REWARD_WEIGHTS

def test_validator_scoring():
    """Test with exact query template from logs and calculate scores."""
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY environment variable not set")
        print("   Set it with: export GEMINI_API_KEY=your_key")
        sys.exit(1)
    
    print("="*80)
    print("VALIDATOR SCORING TEST")
    print("="*80)
    print()
    
    # Exact query template from logs
    query_template = """Generate 9 name variations for {name}. Ensure phonetic similarity by generating names that sound similar to the original name at levels of Light (10%), Medium (30%), and Far (60%) phonetic distance. Also ensure orthographic similarity by generating names that visually resemble the original name at levels of Light (10%), Medium (30%), and Far (60%) visual similarity. Approximately 30% of these generated variations should follow these rule-based transformations: Additionally, generate variations that perform these transformations: Remove a random consonant from the name, and Swap adjacent syllables in the name. The following address is the seed country/city to generate address variations for: {address}. Generate unique real addresses within the specified country/city for each variation.  The following date of birth is the seed DOB to generate variations for: {dob}.



[ADDITIONAL CONTEXT]:

- Address variations should be realistic addresses within the specified country/city

- DOB variations ATLEAST one in each category (±1 day, ±3 days, ±30 days, ±90 days, ±365 days, year+month only)

- For year+month, generate the exact DOB without day

- Each variation must have a different, realistic address and DOB

[UAV REQUIREMENTS - Phase 3]:

Return variations in the NEW structure. For the seed "odette delahaye" ONLY, use this structure:

{

  "odette delahaye": {

    "variations": [["name_var", "dob_var", "addr_var"], ...],  # Your normal variations

    "uav": {

      "address": "address_variant",  # REQUIRED: Address that looks valid but may fail validation

      "label": "explanation",        # REQUIRED: Why this could be a valid address

      "latitude": float,              # REQUIRED: Latitude coordinates

      "longitude": float              # REQUIRED: Longitude coordinates

    }

  }

}

For all OTHER seeds, use the standard structure (variations only):

{

  "other_seed_name": [["name_var", "dob_var", "addr_var"], ...]

}

UAV = Unknown Attack Vector: An address from the seed's country/city/region that looks legitimate but might fail geocoding.

Examples: "123 Main Str" (typo), "456 Oak Av" (abbreviation), "789 1st St" (missing direction)

Label examples: "Common typo", "Local abbreviation", "Missing street direction"
"""
    
    # Test with a few names from the logs
    identity = [
        ["joel miller", "1946-04-12", "Equatorial Guinea"],
        ["odette delahaye", "1964-07-28", "Ivory Coast"],  # UAV seed
        ["kevin davenport", "1958-03-15", "Belgium"],
    ]
    
    synapse = IdentitySynapse(
        identity=identity,
        query_template=query_template,
        timeout=750.0
    )
    
    print(f"🔄 Generating variations for {len(identity)} names...")
    print(f"   Expected: 9 variations per name")
    print(f"   UAV seed: odette delahaye")
    print()
    
    start_time = time.time()
    
    try:
        variations = generate_variations_with_gemini(
            synapse,
            gemini_api_key=api_key,
            gemini_model="gemini-2.5-flash-lite"
        )
        
        elapsed = time.time() - start_time
        
        print(f"✅ Generation complete in {elapsed:.2f}s")
        print()
        
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Calculate scores using validator's scoring mechanism
    print("="*80)
    print("VALIDATOR SCORING CALCULATION")
    print("="*80)
    print()
    
    # Parse requirements from query template
    phonetic_similarity = {"Light": 0.10, "Medium": 0.30, "Far": 0.60}
    orthographic_similarity = {"Light": 0.10, "Medium": 0.30, "Far": 0.60}
    variation_count = 9
    rule_percentage = 0.30
    
    # Map query rules to validator rule names
    # Query says: "Remove a random consonant from the name" and "Swap adjacent syllables in the name"
    rule_based = {
        "selected_rules": ["remove_random_consonant", "swap_adjacent_syllables"],
        "rule_percentage": 30
    }
    
    total_score = 0.0
    name_scores = {}
    
    for name, dob, address in identity:
        if name not in variations:
            print(f"❌ {name}: Missing from output")
            name_scores[name] = 0.0
            continue
        
        data = variations[name]
        
        # Extract name variations
        if isinstance(data, dict) and 'variations' in data:
            name_variations = [var[0] for var in data['variations'] if len(var) > 0]
        elif isinstance(data, list):
            name_variations = [var[0] for var in data if len(var) > 0]
        else:
            print(f"❌ {name}: Unexpected format")
            name_scores[name] = 0.0
            continue
        
        print(f"📊 Scoring: {name}")
        print(f"   Variations generated: {len(name_variations)}")
        print(f"   Expected: {variation_count}")
        print()
        
        # Calculate score using validator's function
        try:
            quality_score, base_score, detailed_metrics = calculate_variation_quality(
                original_name=name,
                variations=name_variations,
                phonetic_similarity=phonetic_similarity,
                orthographic_similarity=orthographic_similarity,
                expected_count=variation_count,
                rule_based=rule_based
            )
            
            name_scores[name] = quality_score
            
            print(f"   ✅ Final Score: {quality_score:.4f}")
            print()
            
            # Show detailed breakdown
            if "first_name" in detailed_metrics:
                first_metrics = detailed_metrics["first_name"]["metrics"]
                print(f"   📈 First Name Metrics:")
                print(f"      Similarity: {first_metrics.get('similarity', {}).get('combined', 0):.4f}")
                print(f"        - Phonetic: {first_metrics.get('similarity', {}).get('phonetic', 0):.4f}")
                print(f"        - Orthographic: {first_metrics.get('similarity', {}).get('orthographic', 0):.4f}")
                print(f"      Count: {first_metrics.get('count', {}).get('score', 0):.4f} ({first_metrics.get('count', {}).get('actual', 0)}/{first_metrics.get('count', {}).get('expected', 0)})")
                print(f"      Uniqueness: {first_metrics.get('uniqueness', {}).get('score', 0):.4f} ({first_metrics.get('uniqueness', {}).get('unique_count', 0)}/{first_metrics.get('uniqueness', {}).get('total_count', 0)})")
                print(f"      Length: {first_metrics.get('length', {}).get('score', 0):.4f}")
                print()
            
            if "last_name" in detailed_metrics:
                last_metrics = detailed_metrics["last_name"]["metrics"]
                print(f"   📈 Last Name Metrics:")
                print(f"      Similarity: {last_metrics.get('similarity', {}).get('combined', 0):.4f}")
                print(f"        - Phonetic: {last_metrics.get('similarity', {}).get('phonetic', 0):.4f}")
                print(f"        - Orthographic: {last_metrics.get('similarity', {}).get('orthographic', 0):.4f}")
                print(f"      Count: {last_metrics.get('count', {}).get('score', 0):.4f} ({last_metrics.get('count', {}).get('actual', 0)}/{last_metrics.get('count', {}).get('expected', 0)})")
                print(f"      Uniqueness: {last_metrics.get('uniqueness', {}).get('score', 0):.4f} ({last_metrics.get('uniqueness', {}).get('unique_count', 0)}/{last_metrics.get('uniqueness', {}).get('total_count', 0)})")
                print(f"      Length: {last_metrics.get('length', {}).get('score', 0):.4f}")
                print()
            
            if "rule_compliance" in detailed_metrics:
                rule_metrics = detailed_metrics["rule_compliance"]
                print(f"   📈 Rule Compliance:")
                print(f"      Score: {rule_metrics.get('score', 0):.4f}")
                print(f"      Rule-compliant variations: {detailed_metrics.get('rule_compliant_variations_count', 0)}/{len(name_variations)}")
                print()
            
            print(f"   📊 Base Score: {detailed_metrics.get('base_score', 0):.4f}")
            print(f"   📊 Final Score: {detailed_metrics.get('final_score', 0):.4f}")
            print()
            
            total_score += quality_score
            
        except Exception as e:
            print(f"   ❌ Scoring failed: {e}")
            import traceback
            traceback.print_exc()
            name_scores[name] = 0.0
    
    # Summary
    print("="*80)
    print("SCORING SUMMARY")
    print("="*80)
    print()
    
    for name, score in name_scores.items():
        status = "✅" if score >= 0.7 else "⚠️" if score >= 0.5 else "❌"
        print(f"{status} {name}: {score:.4f}")
    
    avg_score = total_score / len(identity) if identity else 0.0
    print()
    print(f"📊 Average Score: {avg_score:.4f}")
    print()
    
    # Show weight breakdown
    print("="*80)
    print("SCORING WEIGHTS (from validator)")
    print("="*80)
    print(f"Similarity: {MIID_REWARD_WEIGHTS['similarity_weight']*100:.0f}%")
    print(f"Count: {MIID_REWARD_WEIGHTS['count_weight']*100:.0f}%")
    print(f"Uniqueness: {MIID_REWARD_WEIGHTS['uniqueness_weight']*100:.0f}%")
    print(f"Length: {MIID_REWARD_WEIGHTS['length_weight']*100:.0f}%")
    print(f"Rule Compliance: {MIID_REWARD_WEIGHTS['rule_compliance_weight']*100:.0f}%")
    print()
    
    # Save results
    with open("test_validator_scoring_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "variations": variations,
            "scores": name_scores,
            "average_score": avg_score
        }, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Results saved to: test_validator_scoring_results.json")
    
    return avg_score

if __name__ == "__main__":
    score = test_validator_scoring()
    sys.exit(0 if score >= 0.7 else 1)

