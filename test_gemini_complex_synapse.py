#!/usr/bin/env python3
"""
Test Gemini with a COMPLEX real validator synapse - includes UAV, multiple countries, complex rules.
"""

import os
import json
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from MIID.validator.gemini_generator import generate_variations_with_gemini
from MIID.protocol import IdentitySynapse

def main():
    """Test with a complex real validator synapse format."""
    
    # Complex validator synapse (from test_final_synapse.json)
    synapse = IdentitySynapse(
        identity=[
            ["John Smith", "1980-01-15", "Cuba"],
            ["Ahmad Hassan", "1975-05-20", "Democratic Republic of the Congo"],
            ["Иван Петров", "1990-08-10", "Russia"],
            ["محمد علي", "1985-12-25", "Iran"],
            ["Christopher Roberts", "1978-03-18", "Belize"],
            ["María García", "1992-07-22", "Venezuela"],
            ["هيثم مشعشع", "1988-11-30", "Iraq"]
        ],
        query_template="Generate 15 variations of {name}, ensuring phonetic similarity based on 10% Light, 50% Medium, and 40% Far types, and orthographic similarity based on 20% Light, 60% Medium, and 20% Far types. Approximately 30% of the total 15 variations should follow these rule-based transformations: Replace random consonants with different consonants, Replace random vowels with different vowels, and Delete a random letter. The following address is the seed country/city to generate address variations for: {address}. Generate unique real addresses within the specified country/city for each variation.  The following date of birth is the seed DOB to generate variations for: {dob}.\n\n[VALIDATION HINTS]: Phonetic similarity: 10% Light, 50% Medium, 40% Far.; Orthographic similarity: 20% Far, 20% Light, 60% Medium. The following address is the seed country/city to generate address variations for: {address}. Generate unique real addresses within the specified country/city for each variation.  The following date of birth is the seed DOB to generate variations for: {dob}.\n\n[ADDITIONAL CONTEXT]:\n- Address variations should be realistic addresses within the specified country/city\n- DOB variations ATLEAST one in each category (±1 day, ±3 days, ±30 days, ±90 days, ±365 days, year+month only)\n- For year+month, generate the exact DOB without day\n- Each variation must have a different, realistic address and DOB\n\n[UAV REQUIREMENTS - Phase 3]:\nReturn variations in the NEW structure. For the seed \"هيثم مشعشع\" ONLY, use this structure:\n{\n  \"هيثم مشعشع\": {\n    \"variations\": [[\"name_var\", \"dob_var\", \"addr_var\"], ...],  # Your normal variations\n    \"uav\": {\n      \"address\": \"address_variant\",  # REQUIRED: Address that looks valid but may fail validation\n      \"label\": \"explanation\",        # REQUIRED: Why this could be a valid address\n      \"latitude\": float,              # REQUIRED: Latitude coordinates\n      \"longitude\": float              # REQUIRED: Longitude coordinates\n    }\n  }\n}\n\nFor all OTHER seeds, use the standard structure (variations only):\n{\n  \"other_seed_name\": [[\"name_var\", \"dob_var\", \"addr_var\"], ...]\n}\n\nUAV = Unknown Attack Vector: An address from the seed's country/city/region that looks legitimate but might fail geocoding.\nExamples: \"123 Main Str\" (typo), \"456 Oak Av\" (abbreviation), \"789 1st St\" (missing direction)\nLabel examples: \"Common typo\", \"Local abbreviation\", \"Missing street direction\"",
        timeout=120.0
    )
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not set")
        return
    
    print("="*80)
    print("Testing Gemini with COMPLEX Real Validator Synapse")
    print("="*80)
    print(f"\n📋 Synapse Details:")
    print(f"   Identities: {len(synapse.identity)}")
    for i, identity in enumerate(synapse.identity, 1):
        print(f"   {i}. {identity[0]} | {identity[1]} | {identity[2]}")
    print(f"\n   Query Template Length: {len(synapse.query_template)} chars")
    print(f"   Timeout: {synapse.timeout}s")
    print(f"   Has UAV Requirements: {'هيثم مشعشع' in synapse.query_template}")
    
    print(f"\n🔄 Generating variations with Gemini...")
    print("   (This will take several minutes - generating for 7 identities with complex requirements)")
    
    try:
        variations = generate_variations_with_gemini(
            synapse,
            gemini_api_key=api_key,
            gemini_model="gemini-2.0-flash-exp"
        )
        
        print("\n" + "="*80)
        print("✅ GENERATION SUCCESSFUL!")
        print("="*80)
        
        for name, var_list in variations.items():
            if isinstance(var_list, dict):
                # UAV structure
                vars_count = len(var_list.get('variations', []))
                print(f"\n📝 {name}: {vars_count} variations + UAV")
                if var_list.get('uav'):
                    uav = var_list['uav']
                    print(f"   🎯 UAV Address: {uav.get('address', 'N/A')}")
                    print(f"      Label: {uav.get('label', 'N/A')}")
                    coords = uav.get('latitude'), uav.get('longitude')
                    print(f"      Coordinates: {coords}")
                
                # Show first 2 variations
                print(f"\n   First 2 Variations:")
                for i, var in enumerate(var_list.get('variations', [])[:2], 1):
                    print(f"   {i}. Name: {var[0]}")
                    print(f"      DOB:  {var[1]}")
                    print(f"      Addr: {var[2][:80]}..." if len(var[2]) > 80 else f"      Addr: {var[2]}")
            else:
                print(f"\n📝 {name}: {len(var_list)} variations")
                print(f"\n   First 2 Variations:")
                for i, var in enumerate(var_list[:2], 1):
                    print(f"   {i}. Name: {var[0]}")
                    print(f"      DOB:  {var[1]}")
                    print(f"      Addr: {var[2][:80]}..." if len(var[2]) > 80 else f"      Addr: {var[2]}")
        
        # Validate structure
        print("\n" + "="*80)
        print("Structure Validation")
        print("="*80)
        
        all_valid = True
        uav_found = False
        
        for name, var_list in variations.items():
            if isinstance(var_list, dict):
                vars_list = var_list.get('variations', [])
                if var_list.get('uav'):
                    uav_found = True
                    print(f"✅ {name}: Has UAV structure")
            else:
                vars_list = var_list
            
            if len(vars_list) != 15:
                print(f"❌ {name}: Expected 15 variations, got {len(vars_list)}")
                all_valid = False
            else:
                print(f"✅ {name}: Correct count (15 variations)")
            
            # Check format
            for i, var in enumerate(vars_list[:2], 1):
                if not isinstance(var, list) or len(var) != 3:
                    print(f"❌ {name} variation {i}: Invalid format")
                    all_valid = False
        
        # Check UAV
        if "هيثم مشعشع" in variations:
            if isinstance(variations["هيثم مشعشع"], dict) and variations["هيثم مشعشع"].get('uav'):
                print(f"✅ UAV found for هيثم مشعشع")
            else:
                print(f"❌ UAV missing for هيثم مشعشع")
                all_valid = False
        
        if all_valid:
            print("\n🎉 All validations passed! Structure is correct!")
        else:
            print("\n⚠️  Some validations failed. Check output above.")
        
        print("\n" + "="*80)
        print("🎉 COMPLEX TEST COMPLETE!")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Generation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

