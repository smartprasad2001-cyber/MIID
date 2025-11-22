#!/usr/bin/env python3
"""
Test Gemini 2.5 Flash-Lite model
"""

import os
import sys
import json
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from MIID.validator.gemini_generator import generate_variations_with_gemini
from MIID.protocol import IdentitySynapse

def test_gemini_2_5_flash_lite():
    """Test with Gemini 2.5 Flash-Lite model."""
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY environment variable not set")
        print("   Set it with: export GEMINI_API_KEY=your_key")
        sys.exit(1)
    
    print("="*80)
    print("TESTING GEMINI 2.5 FLASH-LITE")
    print("="*80)
    print()
    
    # Test with 3 names
    identity = [
        ["John Smith", "1990-05-15", "New York, USA"],
        ["Maria Garcia", "1985-08-22", "Madrid, Spain"],
        ["thomas moore", "1951-05-21", "Namibia"]  # UAV seed
    ]
    
    query_template = """Generate 5 variations of {name}, ensuring phonetic similarity is maintained with a distribution of 10% Light, 30% Medium, and 60% Far. Additionally, ensure orthographic similarity is reflected at a level of 100% Medium. Approximately 30% of the total 5 variations should follow these rule-based transformations: Add a title prefix (Mr., Dr., etc.). The following address is the seed country/city to generate address variations for: {address}. Generate unique real addresses within the specified country/city for each variation. The following date of birth is the seed DOB to generate variations for: {dob}.

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
    
    print("🔄 Generating variations with Gemini 2.5 Flash-Lite...")
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
    
    # Verify results
    print("="*80)
    print("RESULTS VERIFICATION")
    print("="*80)
    print()
    
    for name in ["John Smith", "Maria Garcia", "thomas moore"]:
        if name not in variations:
            print(f"❌ {name}: Missing")
            continue
        
        data = variations[name]
        print(f"✅ {name}:")
        print(f"   Type: {type(data).__name__}")
        
        if isinstance(data, dict) and 'variations' in data:
            # UAV format
            var_list = data['variations']
            uav = data.get('uav', {})
            print(f"   Format: UAV (with {len(var_list)} variations)")
            print(f"   UAV: address={uav.get('address', 'N/A')[:30]}...")
            print(f"        label={uav.get('label', 'N/A')[:30]}...")
            print(f"        lat={uav.get('latitude')}, lon={uav.get('longitude')}")
        elif isinstance(data, list):
            # Standard format
            print(f"   Format: Standard (List[List[str]])")
            print(f"   Variations: {len(data)}")
        else:
            print(f"   ⚠️  Unexpected format: {type(data)}")
        
        print()
    
    print("="*80)
    print("✅ TEST COMPLETE")
    print("="*80)
    
    # Save results
    with open("test_gemini_2_5_flash_lite_results.json", "w") as f:
        json.dump(variations, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved to: test_gemini_2_5_flash_lite_results.json")

if __name__ == "__main__":
    test_gemini_2_5_flash_lite()

