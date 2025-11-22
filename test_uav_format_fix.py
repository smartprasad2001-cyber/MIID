#!/usr/bin/env python3
"""
Test the UAV format fix - verify non-UAV seeds don't get UAV format
"""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from MIID.validator.gemini_generator import generate_variations_with_gemini
from MIID.protocol import IdentitySynapse

def test_uav_format_fix():
    """Test that non-UAV seeds return standard format even if Gemini returns UAV format."""
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not set")
        return
    
    print("="*80)
    print("TESTING UAV FORMAT FIX")
    print("="*80)
    print()
    
    # Create test with UAV seed "thomas moore" and non-UAV seed "fernando flynn"
    identity = [
        ["fernando flynn", "1990-01-01", "South Africa"],  # NOT UAV seed
        ["thomas moore", "1951-05-21", "Namibia"]  # UAV seed
    ]
    
    query_template = """Generate 5 variations of {name}. The following address is the seed country/city to generate address variations for: {address}. Generate unique real addresses within the specified country/city for each variation. The following date of birth is the seed DOB to generate variations for: {dob}.

[UAV REQUIREMENTS - Phase 3]:
Return variations in the NEW structure. For the seed "thomas moore" ONLY, use this structure:
{
  "thomas moore": {
    "variations": [["name_var", "dob_var", "addr_var"], ...],
    "uav": {
      "address": "address_variant",
      "label": "explanation",
      "latitude": float,
      "longitude": float
    }
  }
}

For all OTHER seeds, use the standard structure (variations only):
{
  "other_seed_name": [["name_var", "dob_var", "addr_var"], ...]
}"""
    
    synapse = IdentitySynapse(
        identity=identity,
        query_template=query_template,
        timeout=360.0
    )
    
    print("🔄 Generating variations...")
    try:
        variations = generate_variations_with_gemini(
            synapse,
            gemini_api_key=api_key,
            gemini_model="gemini-2.0-flash-exp"
        )
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("✅ Generation complete\n")
    
    # Verify format
    print("="*80)
    print("FORMAT VERIFICATION")
    print("="*80)
    print()
    
    all_correct = True
    
    for name in ["fernando flynn", "thomas moore"]:
        if name not in variations:
            print(f"❌ {name}: Missing from variations")
            all_correct = False
            continue
        
        data = variations[name]
        print(f"Checking: {name}")
        print(f"  Type: {type(data)}")
        
        if name == "thomas moore":
            # Should be UAV format
            if isinstance(data, dict) and 'variations' in data and 'uav' in data:
                print(f"  ✅ Correct: UAV format")
                uav = data['uav']
                print(f"  UAV fields:")
                print(f"    - address: {uav.get('address', 'MISSING')}")
                print(f"    - label: {uav.get('label', 'MISSING')}")
                print(f"    - latitude: {uav.get('latitude', 'MISSING')}")
                print(f"    - longitude: {uav.get('longitude', 'MISSING')}")
                
                # Check all fields are present
                if not all(k in uav for k in ['address', 'label', 'latitude', 'longitude']):
                    print(f"  ⚠️  Missing UAV fields")
                    all_correct = False
            else:
                print(f"  ❌ Wrong format: Expected UAV format with variations and uav keys")
                all_correct = False
        else:
            # Should be standard format (list)
            if isinstance(data, list):
                print(f"  ✅ Correct: Standard format (List[List[str]])")
                print(f"  Variations: {len(data)}")
            elif isinstance(data, dict) and 'variations' in data:
                # Gemini returned UAV format but we should extract just variations
                print(f"  ⚠️  Gemini returned UAV format, but should be standard")
                print(f"  Checking if fix extracts variations...")
                if 'uav' in data:
                    print(f"  ❌ Still has UAV key - fix may not be working")
                    all_correct = False
                else:
                    print(f"  ✅ UAV key removed")
            else:
                print(f"  ❌ Wrong format: Expected List[List[str]], got {type(data)}")
                all_correct = False
        
        print()
    
    # Final verdict
    print("="*80)
    if all_correct:
        print("🎉 ALL CHECKS PASSED - Format fix is working!")
    else:
        print("⚠️  SOME ISSUES FOUND - Review the output above")
    print("="*80)
    
    # Save results
    with open("test_uav_format_results.json", "w") as f:
        json.dump(variations, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved to: test_uav_format_results.json")

if __name__ == "__main__":
    test_uav_format_fix()

