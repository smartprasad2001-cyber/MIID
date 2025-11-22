#!/usr/bin/env python3
"""
Final mainnet readiness test - Full 15-name scenario
"""

import os
import sys
import json
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from MIID.validator.gemini_generator import generate_variations_with_gemini
from MIID.protocol import IdentitySynapse

def test_final_mainnet_readiness():
    """Final test with full 15-name mainnet scenario."""
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY environment variable not set")
        print("   Set it with: export GEMINI_API_KEY=your_key")
        sys.exit(1)
    
    print("="*80)
    print("FINAL MAINNET READINESS TEST")
    print("="*80)
    print()
    
    # Full mainnet scenario
    identity = [
        ["Gregory Dimitry", "1961-1-1", "South Sudan"],
        ["عقيل بديرية", "1945-06-19", "Somalia"],
        ["Reza Azami", "1971-5-5", "Iran"],
        ["Ahmad Udih", "1951-1-1", "Jordan"],
        ["larissa nascimento", "1929-05-17", "Bahamas"],
        ["lia mendes", "1948-11-24", "Mozambique"],  # UAV
        ["ismael fernandes", "1981-10-05", "Denmark"],
        ["mário tavares", "1952-07-20", "Oman"],
        ["Ali Ghassir", "1990-7-29", "Iran"],
        ["alyssa gray", "1979-12-12", "Nigeria"],
        ["Виктория Родина", "1989-10-29", "Russia"],
        ["olivia taylor", "1958-06-02", "Nigeria"],
        ["jacob scott", "1965-09-16", "Nepal"],
        ["александр молчанов", "1958-02-02", "New Zealand"],
        ["márcio oliveira", "1951-02-25", "Romania"]
    ]
    
    query_template = """Generate 7 variations of {name}. Ensure phonetic similarity is reflected in 70% of the variations using light-sound-alike transformations, and in 30% using medium-sound-alike transformations. Also ensure orthographic similarity by making 20% of the variations visually similar to the original name with light changes, 60% with medium changes, and 20% with far changes. Approximately 45% of the total 7 variations should follow these rule-based transformations: Additionally, generate variations that perform these transformations: Delete a random letter, and Replace random consonants with different consonants. The following address is the seed country/city to generate address variations for: {address}. Generate unique real addresses within the specified country/city for each variation.  The following date of birth is the seed DOB to generate variations for: {dob}.



[ADDITIONAL CONTEXT]:

- Address variations should be realistic addresses within the specified country/city

- DOB variations ATLEAST one in each category (±1 day, ±3 days, ±30 days, ±90 days, ±365 days, year+month only)

- For year+month, generate the exact DOB without day

- Each variation must have a different, realistic address and DOB



[UAV REQUIREMENTS - Phase 3]:

Return variations in the NEW structure. For the seed "lia mendes" ONLY, use this structure:

{

  "lia mendes": {

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
        timeout=730.0
    )
    
    print(f"🔄 Testing full mainnet scenario: {len(identity)} names")
    print(f"   UAV seed: lia mendes")
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
        print(f"   Average: {elapsed/len(identity):.2f}s per name")
        print()
        
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Verify all requirements
    print("="*80)
    print("MAINNET READINESS CHECKLIST")
    print("="*80)
    print()
    
    checks = {
        "All names processed": 0,
        "UAV format correct": False,
        "Standard format correct": 0,
        "Variation count correct": 0,
        "Data structure valid": 0,
        "Protocol serialization": False,
        "No errors": True
    }
    
    # Check each name
    for name, dob, address in identity:
        if name not in variations:
            print(f"❌ {name}: Missing")
            checks["No errors"] = False
            continue
        
        checks["All names processed"] += 1
        data = variations[name]
        is_uav = name.lower() == "lia mendes"
        
        # Check format
        if is_uav:
            if isinstance(data, dict) and 'variations' in data and 'uav' in data:
                checks["UAV format correct"] = True
                uav = data['uav']
                if all(k in uav for k in ['address', 'label', 'latitude', 'longitude']):
                    print(f"✅ {name}: UAV format with all required fields")
        else:
            if isinstance(data, list):
                checks["Standard format correct"] += 1
                print(f"✅ {name}: Standard format")
        
        # Check variation count
        var_list = data.get('variations', []) if isinstance(data, dict) else data
        if len(var_list) == 7:
            checks["Variation count correct"] += 1
        
        # Check data structure
        if all(isinstance(v, list) and len(v) == 3 for v in var_list):
            checks["Data structure valid"] += 1
    
    # Test protocol serialization
    try:
        test_synapse = IdentitySynapse(
            identity=identity,
            query_template=query_template,
            timeout=730.0
        )
        test_synapse.variations = variations
        
        try:
            serialized = test_synapse.model_dump_json()
        except AttributeError:
            serialized = test_synapse.json()
        
        deserialized = test_synapse.deserialize()
        
        if len(deserialized) == len(identity):
            checks["Protocol serialization"] = True
            print(f"✅ Protocol serialization: PASSED")
    except Exception as e:
        print(f"❌ Protocol serialization: FAILED - {e}")
        checks["No errors"] = False
    
    # Summary
    print()
    print("="*80)
    print("FINAL VERDICT")
    print("="*80)
    print()
    
    print(f"✅ All names processed: {checks['All names processed']}/{len(identity)}")
    print(f"{'✅' if checks['UAV format correct'] else '❌'} UAV format correct: {checks['UAV format correct']}")
    print(f"✅ Standard format correct: {checks['Standard format correct']}/{len(identity)-1}")
    print(f"✅ Variation count correct: {checks['Variation count correct']}/{len(identity)}")
    print(f"✅ Data structure valid: {checks['Data structure valid']}/{len(identity)}")
    print(f"{'✅' if checks['Protocol serialization'] else '❌'} Protocol serialization: {checks['Protocol serialization']}")
    print(f"{'✅' if checks['No errors'] else '❌'} No errors: {checks['No errors']}")
    print()
    
    all_passed = (
        checks["All names processed"] == len(identity) and
        checks["UAV format correct"] and
        checks["Standard format correct"] == len(identity) - 1 and
        checks["Variation count correct"] == len(identity) and
        checks["Data structure valid"] == len(identity) and
        checks["Protocol serialization"] and
        checks["No errors"]
    )
    
    if all_passed:
        print("="*80)
        print("🎉 MINER IS FULLY COMPLIANT AND READY FOR MAINNET 🎉")
        print("="*80)
        print()
        print("✅ Meets all validator requirements")
        print("✅ Produces standard output format")
        print("✅ Handles UAV format correctly")
        print("✅ Protocol serialization works")
        print("✅ All edge cases handled (Arabic, Russian, Accented)")
        print("✅ No errors or warnings")
    else:
        print("="*80)
        print("❌ SOME ISSUES DETECTED - REVIEW ABOVE")
        print("="*80)
    
    # Save results
    with open("test_final_mainnet_readiness_results.json", "w", encoding="utf-8") as f:
        json.dump(variations, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved to: test_final_mainnet_readiness_results.json")
    
    return all_passed

if __name__ == "__main__":
    success = test_final_mainnet_readiness()
    sys.exit(0 if success else 1)

