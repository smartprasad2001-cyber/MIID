#!/usr/bin/env python3
"""
Test exact synapse from logs and optimize for 0.8 score
"""

import os
import sys
import json
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from MIID.validator.gemini_generator import generate_variations_with_gemini
from MIID.protocol import IdentitySynapse
from MIID.validator.reward import calculate_variation_quality, MIID_REWARD_WEIGHTS

def test_exact_synapse_scoring():
    """Test with EXACT synapse from logs and optimize for 0.8 score."""
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY environment variable not set")
        sys.exit(1)
    
    print("="*80)
    print("EXACT SYNAPSE SCORING TEST - TARGET: 0.8")
    print("="*80)
    print()
    
    # EXACT identity from logs
    identity = [
        ["Anatoly Vyborny", "1965-6-8", "Russia"],
        ["رشدي مرمش", "1956-03-23", "Hong Kong"],
        ["Leonid Pasechnik", "1970-3-15", "Ukraine"],
        ["Aliaksei Rymasheuski", "1981-6-29", "Belarus"],
        ["denis bonneau", "1991-04-17", "Monaco"],
        ["luce guyon", "1998-03-02", "Turks and Caicos Islands"],
        ["purificación franch", "1982-09-09", "Cuba"],  # UAV seed
        ["Ilya Buzin", "1980-8-21", "Russia"],
        ["thibaut marchal", "1995-09-25", "Portugal"],
        ["éric lebrun", "1946-05-15", "Fiji"],
        ["zoé joseph", "1979-08-08", "Thailand"],
        ["ягода пачаръзка", "1994-09-26", "Bulgaria"],
        ["cesar taylor", "1928-07-26", "South Sudan"],
        ["Володимир Бандура", "1990-7-15", "Ukraine"],
        ["alfred boulay", "1943-10-23", "Ivory Coast"]
    ]
    
    # EXACT query template from logs
    query_template = """Generate exactly 8 variations of {name}, ensuring phonetic similarity (20% Light, 60% Medium, 20% Far) and orthographic similarity (30% Light, 40% Medium, 30% Far). Approximately 60% of the total 8 variations should follow these rule-based transformations: Additionally, generate variations that perform these transformations: Convert {name} to initials, and Swap random adjacent letters. The following address is the seed country/city to generate address variations for: {address}. Generate unique real addresses within the specified country/city for each variation.  The following date of birth is the seed DOB to generate variations for: {dob}.

[ADDITIONAL CONTEXT]:

- Address variations should be realistic addresses within the specified country/city

- DOB variations ATLEAST one in each category (±1 day, ±3 days, ±30 days, ±90 days, ±365 days, year+month only)

- For year+month, generate the exact DOB without day

- Each variation must have a different, realistic address and DOB

[UAV REQUIREMENTS - Phase 3]:

Return variations in the NEW structure. For the seed "purificación franch" ONLY, use this structure:

{

  "purificación franch": {

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
    
    synapse = IdentitySynapse(
        identity=identity,
        query_template=query_template,
        timeout=740.0
    )
    
    print(f"🔄 Generating variations for {len(identity)} names...")
    print(f"   Expected: 8 variations per name")
    print(f"   UAV seed: purificación franch")
    print(f"   Phonetic: 20% Light, 60% Medium, 20% Far")
    print(f"   Orthographic: 30% Light, 40% Medium, 30% Far")
    print(f"   Rules: 60% (5 out of 8) - Convert to initials, Swap adjacent letters")
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
    
    # Calculate scores using validator's exact scoring mechanism
    print("="*80)
    print("VALIDATOR SCORING (Target: 0.8 per name)")
    print("="*80)
    print()
    
    # Parse requirements from query template
    phonetic_similarity = {"Light": 0.20, "Medium": 0.60, "Far": 0.20}
    orthographic_similarity = {"Light": 0.30, "Medium": 0.40, "Far": 0.30}
    variation_count = 8
    rule_percentage = 0.60
    
    rule_based = {
        "selected_rules": ["shorten_name_to_initials", "swap_random_letter"],
        "rule_percentage": 60
    }
    
    total_score = 0.0
    name_scores = {}
    detailed_results = {}
    
    for name, dob, address in identity:
        if name not in variations:
            print(f"❌ {name}: Missing")
            name_scores[name] = 0.0
            continue
        
        data = variations[name]
        
        # Extract name variations
        if isinstance(data, dict) and 'variations' in data:
            name_variations = [var[0].lower() if var[0] else "" for var in data['variations'] if len(var) > 0]
        elif isinstance(data, list):
            name_variations = [var[0].lower() if var[0] else "" for var in data if len(var) > 0]
        else:
            print(f"❌ {name}: Unexpected format")
            name_scores[name] = 0.0
            continue
        
        print(f"📊 Scoring: {name}")
        print(f"   Variations: {len(name_variations)} (expected: {variation_count})")
        
        # Calculate score
        try:
            final_score, base_score, detailed_metrics = calculate_variation_quality(
                original_name=name,
                variations=name_variations,
                phonetic_similarity=phonetic_similarity,
                orthographic_similarity=orthographic_similarity,
                expected_count=variation_count,
                rule_based=rule_based
            )
            
            name_scores[name] = final_score
            detailed_results[name] = {
                "final_score": final_score,
                "base_score": base_score,
                "metrics": detailed_metrics
            }
            
            status = "✅" if final_score >= 0.8 else "⚠️" if final_score >= 0.6 else "❌"
            print(f"   {status} Final Score: {final_score:.4f} (Target: 0.8000)")
            
            # Show key metrics
            if "first_name" in detailed_metrics:
                first_metrics = detailed_metrics["first_name"]["metrics"]
                print(f"   First Name:")
                print(f"      Similarity: {first_metrics.get('similarity', {}).get('combined', 0):.4f}")
                print(f"      Count: {first_metrics.get('count', {}).get('score', 0):.4f}")
                print(f"      Uniqueness: {first_metrics.get('uniqueness', {}).get('score', 0):.4f}")
            
            if "rule_compliance" in detailed_metrics:
                rule_score = detailed_metrics["rule_compliance"]["score"]
                rule_count = detailed_metrics.get("rule_compliant_variations_count", 0)
                print(f"   Rule Compliance: {rule_score:.4f} ({rule_count}/{variation_count})")
            
            print()
            
            total_score += final_score
            
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
    
    scores_above_08 = sum(1 for s in name_scores.values() if s >= 0.8)
    scores_above_06 = sum(1 for s in name_scores.values() if s >= 0.6)
    
    for name, score in sorted(name_scores.items(), key=lambda x: x[1], reverse=True):
        status = "✅" if score >= 0.8 else "⚠️" if score >= 0.6 else "❌"
        print(f"{status} {name}: {score:.4f}")
    
    avg_score = total_score / len(identity) if identity else 0.0
    print()
    print(f"📊 Average Score: {avg_score:.4f}")
    print(f"✅ Scores ≥ 0.8: {scores_above_08}/{len(identity)}")
    print(f"⚠️  Scores ≥ 0.6: {scores_above_06}/{len(identity)}")
    print()
    
    # Save results
    with open("test_exact_synapse_scoring_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "variations": variations,
            "scores": name_scores,
            "detailed_results": detailed_results,
            "average_score": avg_score
        }, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Results saved to: test_exact_synapse_scoring_results.json")
    
    return avg_score

if __name__ == "__main__":
    score = test_exact_synapse_scoring()
    sys.exit(0 if score >= 0.8 else 1)

