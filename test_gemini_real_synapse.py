#!/usr/bin/env python3
"""
Test Gemini with a REAL validator synapse - exact format that validator sends.
"""

import os
import json
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from MIID.validator.gemini_generator import generate_variations_with_gemini
from MIID.protocol import IdentitySynapse

def main():
    """Test with a real validator synapse format."""
    
    # Real validator synapse format (from example_synapse.json)
    synapse = IdentitySynapse(
        identity=[
            ["John Doe", "1990-05-15", "New York, USA"],
            ["محمد شفیع پور", "1987-12-01", "Tehran, Iran"]
        ],
        query_template="The following name is the seed name to generate variations for: {name}. Generate 15 variations of the name {name}, ensuring phonetic similarity: 100% Medium, and orthographic similarity: 100% Medium, and also include 45% of variations that follow: Replace spaces with special characters, and Delete a random letter. The following address is the seed country/city to generate address variations for: {address}. Generate unique real addresses within the specified country/city for each variation. The following date of birth is the seed DOB to generate variations for: {dob}.\n\n[ADDITIONAL CONTEXT]:\n- Address variations should be realistic addresses within the specified country/city\n- DOB variations ATLEAST one in each category (±1 day, ±3 days, ±30 days, ±90 days, ±365 days, year+month only)\n- For year+month, generate the exact DOB without day\n- Each variation must have a different, realistic address and DOB",
        timeout=360.0
    )
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not set")
        return
    
    print("="*80)
    print("Testing Gemini with REAL Validator Synapse")
    print("="*80)
    print(f"\n📋 Synapse Details:")
    print(f"   Identities: {len(synapse.identity)}")
    for i, identity in enumerate(synapse.identity, 1):
        print(f"   {i}. {identity[0]} | {identity[1]} | {identity[2]}")
    print(f"\n   Query Template Length: {len(synapse.query_template)} chars")
    print(f"   Timeout: {synapse.timeout}s")
    
    print(f"\n🔄 Generating variations with Gemini...")
    print("   (This may take a minute - generating for multiple identities)")
    
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
                    print(f"      Coordinates: ({uav.get('latitude')}, {uav.get('longitude')})")
                
                # Show first 3 variations
                print(f"\n   First 3 Variations:")
                for i, var in enumerate(var_list.get('variations', [])[:3], 1):
                    print(f"   {i}. Name: {var[0]}")
                    print(f"      DOB:  {var[1]}")
                    print(f"      Addr: {var[2]}")
            else:
                print(f"\n📝 {name}: {len(var_list)} variations")
                print(f"\n   First 3 Variations:")
                for i, var in enumerate(var_list[:3], 1):
                    print(f"   {i}. Name: {var[0]}")
                    print(f"      DOB:  {var[1]}")
                    print(f"      Addr: {var[2]}")
                if len(var_list) > 3:
                    print(f"   ... and {len(var_list) - 3} more variations")
        
        # Validate structure
        print("\n" + "="*80)
        print("Structure Validation")
        print("="*80)
        
        all_valid = True
        for name, var_list in variations.items():
            if isinstance(var_list, dict):
                vars_list = var_list.get('variations', [])
            else:
                vars_list = var_list
            
            if len(vars_list) != 15:
                print(f"❌ {name}: Expected 15 variations, got {len(vars_list)}")
                all_valid = False
            else:
                print(f"✅ {name}: Correct count (15 variations)")
            
            # Check format
            for i, var in enumerate(vars_list[:3], 1):
                if not isinstance(var, list) or len(var) != 3:
                    print(f"❌ {name} variation {i}: Invalid format (expected [name, dob, address])")
                    all_valid = False
                else:
                    if not var[0] or not var[1] or not var[2]:
                        print(f"⚠️  {name} variation {i}: Missing data")
        
        if all_valid:
            print("\n🎉 All validations passed! Structure is correct!")
        else:
            print("\n⚠️  Some validations failed. Check output above.")
        
        print("\n" + "="*80)
        print("🎉 TEST COMPLETE!")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Generation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

