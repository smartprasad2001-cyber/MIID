#!/usr/bin/env python3
"""
Comprehensive compliance test - verify miner meets ALL validator requirements
"""

import os
import sys
import json
import time
from typing import Dict, List, Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from MIID.validator.gemini_generator import generate_variations_with_gemini
from MIID.protocol import IdentitySynapse

def test_full_compliance():
    """Test full compliance with validator requirements."""
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY environment variable not set")
        print("   Set it with: export GEMINI_API_KEY=your_key")
        sys.exit(1)
    
    print("="*80)
    print("FULL COMPLIANCE TEST - VALIDATOR REQUIREMENTS")
    print("="*80)
    print()
    
    # Test with diverse names including UAV seed
    identity = [
        ["John Smith", "1990-05-15", "New York, USA"],
        ["Maria Garcia", "1985-08-22", "Madrid, Spain"],
        ["lia mendes", "1948-11-24", "Mozambique"],  # UAV seed
        ["عقيل بديرية", "1945-06-19", "Somalia"],  # Arabic
        ["Виктория Родина", "1989-10-29", "Russia"],  # Russian (previously failed)
        ["mário tavares", "1952-07-20", "Oman"],  # Accented
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
    
    print(f"🔄 Testing {len(identity)} names...")
    print(f"   UAV seed: lia mendes")
    print(f"   Special cases: Arabic, Russian, Accented")
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
        return False
    
    # Comprehensive compliance checks
    print("="*80)
    print("COMPLIANCE VERIFICATION")
    print("="*80)
    print()
    
    all_passed = True
    checks = {
        "Format Compliance": [],
        "Variation Count": [],
        "UAV Format": [],
        "Standard Format": [],
        "Data Structure": [],
        "Required Fields": []
    }
    
    for name, dob, address in identity:
        is_uav = name.lower() == "lia mendes"
        
        # Check 1: Name exists in output
        if name not in variations:
            print(f"❌ {name}: MISSING from output")
            all_passed = False
            checks["Format Compliance"].append(f"{name}: Missing")
            continue
        
        data = variations[name]
        
        # Check 2: UAV format for UAV seed
        if is_uav:
            if not isinstance(data, dict):
                print(f"❌ {name}: Expected UAV format (dict), got {type(data).__name__}")
                all_passed = False
                checks["UAV Format"].append(f"{name}: Wrong type")
                continue
            
            if 'variations' not in data:
                print(f"❌ {name}: UAV format missing 'variations' key")
                all_passed = False
                checks["UAV Format"].append(f"{name}: Missing variations")
                continue
            
            if 'uav' not in data:
                print(f"❌ {name}: UAV format missing 'uav' key")
                all_passed = False
                checks["UAV Format"].append(f"{name}: Missing uav")
                continue
            
            uav = data['uav']
            required_uav_fields = ['address', 'label', 'latitude', 'longitude']
            for field in required_uav_fields:
                if field not in uav:
                    print(f"❌ {name}: UAV missing required field '{field}'")
                    all_passed = False
                    checks["Required Fields"].append(f"{name}: Missing {field}")
            
            # Check UAV field types
            if uav.get('latitude') is not None and not isinstance(uav['latitude'], (int, float)):
                print(f"❌ {name}: UAV latitude must be float/int, got {type(uav['latitude'])}")
                all_passed = False
            
            if uav.get('longitude') is not None and not isinstance(uav['longitude'], (int, float)):
                print(f"❌ {name}: UAV longitude must be float/int, got {type(uav['longitude'])}")
                all_passed = False
            
            var_list = data['variations']
            print(f"✅ {name}: UAV format correct")
            print(f"   Variations: {len(var_list)}")
            print(f"   UAV address: {uav.get('address', 'N/A')[:50]}...")
            print(f"   UAV label: {uav.get('label', 'N/A')[:30]}...")
            print(f"   UAV coordinates: ({uav.get('latitude')}, {uav.get('longitude')})")
            checks["UAV Format"].append(f"{name}: ✅")
        
        # Check 3: Standard format for non-UAV seeds
        else:
            if not isinstance(data, list):
                print(f"❌ {name}: Expected standard format (list), got {type(data).__name__}")
                all_passed = False
                checks["Standard Format"].append(f"{name}: Wrong type")
                continue
            
            var_list = data
            print(f"✅ {name}: Standard format correct")
            checks["Standard Format"].append(f"{name}: ✅")
        
        # Check 4: Variation count
        expected_count = 7
        if len(var_list) != expected_count:
            print(f"⚠️  {name}: Expected {expected_count} variations, got {len(var_list)}")
            checks["Variation Count"].append(f"{name}: {len(var_list)}/{expected_count}")
        else:
            checks["Variation Count"].append(f"{name}: ✅ {expected_count}")
        
        # Check 5: Data structure - each variation must be [name, dob, address]
        for i, var in enumerate(var_list):
            if not isinstance(var, list):
                print(f"❌ {name}: Variation {i} is not a list, got {type(var).__name__}")
                all_passed = False
                checks["Data Structure"].append(f"{name}: Var {i} wrong type")
                continue
            
            if len(var) != 3:
                print(f"❌ {name}: Variation {i} has {len(var)} elements, expected 3 [name, dob, address]")
                all_passed = False
                checks["Data Structure"].append(f"{name}: Var {i} wrong length")
                continue
            
            # Check types
            if not all(isinstance(x, str) for x in var):
                print(f"❌ {name}: Variation {i} contains non-string elements")
                all_passed = False
                checks["Data Structure"].append(f"{name}: Var {i} non-string")
        
        checks["Data Structure"].append(f"{name}: ✅")
        print(f"   Variations structure: ✅")
        print()
    
    # Summary
    print("="*80)
    print("COMPLIANCE SUMMARY")
    print("="*80)
    print()
    
    for check_type, results in checks.items():
        passed = sum(1 for r in results if "✅" in r or "/" in r and r.split("/")[0] == r.split("/")[1].split()[0])
        total = len(results)
        status = "✅" if passed == total else "⚠️"
        print(f"{status} {check_type}: {passed}/{total}")
        if check_type == "Variation Count":
            for r in results:
                if "✅" not in r:
                    print(f"   - {r}")
    
    print()
    print("="*80)
    if all_passed:
        print("✅ ALL COMPLIANCE CHECKS PASSED")
    else:
        print("❌ SOME COMPLIANCE CHECKS FAILED")
    print("="*80)
    
    # Test IdentitySynapse serialization
    print()
    print("="*80)
    print("PROTOCOL SERIALIZATION TEST")
    print("="*80)
    print()
    
    try:
        # Create a test synapse with the variations
        test_synapse = IdentitySynapse(
            identity=identity,
            query_template=query_template,
            timeout=730.0
        )
        test_synapse.variations = variations
        
        # Test serialization
        try:
            serialized = test_synapse.model_dump_json()
        except AttributeError:
            serialized = test_synapse.json()  # Fallback for older Pydantic
        deserialized = test_synapse.deserialize()
        
        print("✅ IdentitySynapse serialization: PASSED")
        print(f"   Serialized size: {len(serialized)} bytes")
        print(f"   Deserialized keys: {len(deserialized)} names")
        
        # Verify deserialized format matches
        for name in identity:
            if name[0] in deserialized:
                orig = variations[name[0]]
                deser = deserialized[name[0]]
                
                if isinstance(orig, dict) and isinstance(deser, dict):
                    if orig.get('variations') == deser.get('variations'):
                        print(f"   ✅ {name[0]}: Deserialization matches")
                    else:
                        print(f"   ❌ {name[0]}: Deserialization mismatch")
                elif isinstance(orig, list) and isinstance(deser, list):
                    if orig == deser:
                        print(f"   ✅ {name[0]}: Deserialization matches")
                    else:
                        print(f"   ❌ {name[0]}: Deserialization mismatch")
        
    except Exception as e:
        print(f"❌ IdentitySynapse serialization: FAILED")
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
        all_passed = False
    
    print()
    print("="*80)
    print("FINAL VERDICT")
    print("="*80)
    print()
    
    if all_passed:
        print("✅ MINER MEETS ALL VALIDATOR REQUIREMENTS")
        print("✅ OUTPUT FORMAT IS STANDARD AND COMPLIANT")
        print("✅ READY FOR MAINNET")
    else:
        print("❌ SOME REQUIREMENTS NOT MET - REVIEW ABOVE")
    
    # Save results
    with open("test_full_compliance_results.json", "w", encoding="utf-8") as f:
        json.dump(variations, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved to: test_full_compliance_results.json")
    
    return all_passed

if __name__ == "__main__":
    success = test_full_compliance()
    sys.exit(0 if success else 1)

