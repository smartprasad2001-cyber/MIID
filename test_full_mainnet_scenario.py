#!/usr/bin/env python3
"""
Test full mainnet scenario with improved JSON parsing
Simulates the exact scenario from the logs
"""

import os
import sys
import json
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from MIID.validator.gemini_generator import generate_variations_with_gemini
from MIID.protocol import IdentitySynapse

def test_full_mainnet_scenario():
    """Test with the exact scenario from mainnet logs."""
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY environment variable not set")
        print("   Set it with: export GEMINI_API_KEY=your_key")
        sys.exit(1)
    
    print("="*80)
    print("TESTING FULL MAINNET SCENARIO")
    print("="*80)
    print()
    
    # Exact identity from mainnet logs
    identity = [
        ["Gregory Dimitry", "1961-1-1", "South Sudan"],
        ["عقيل بديرية", "1945-06-19", "Somalia"],
        ["Reza Azami", "1971-5-5", "Iran"],
        ["Ahmad Udih", "1951-1-1", "Jordan"],
        ["larissa nascimento", "1929-05-17", "Bahamas"],
        ["lia mendes", "1948-11-24", "Mozambique"],  # UAV seed
        ["ismael fernandes", "1981-10-05", "Denmark"],
        ["mário tavares", "1952-07-20", "Oman"],
        ["Ali Ghassir", "1990-7-29", "Iran"],
        ["alyssa gray", "1979-12-12", "Nigeria"],
        ["Виктория Родина", "1989-10-29", "Russia"],  # Previously failed
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
    
    print(f"🔄 Processing {len(identity)} names...")
    print(f"   UAV seed: lia mendes")
    print(f"   Previously failed: Виктория Родина")
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
    
    # Verify results
    print("="*80)
    print("RESULTS VERIFICATION")
    print("="*80)
    print()
    
    success_count = 0
    fail_count = 0
    uav_count = 0
    
    for name, dob, address in identity:
        if name not in variations:
            print(f"❌ {name}: MISSING")
            fail_count += 1
            continue
        
        data = variations[name]
        
        if isinstance(data, dict) and 'variations' in data:
            # UAV format
            var_list = data['variations']
            uav = data.get('uav', {})
            if name.lower() == "lia mendes":
                print(f"✅ {name}: UAV format ({len(var_list)} variations)")
                print(f"   UAV: {uav.get('address', 'N/A')[:50]}...")
                uav_count += 1
            else:
                print(f"⚠️  {name}: Unexpected UAV format (extracted {len(var_list)} variations)")
            success_count += 1
        elif isinstance(data, list):
            # Standard format
            if len(data) == 0:
                print(f"❌ {name}: EMPTY LIST")
                fail_count += 1
            else:
                print(f"✅ {name}: Standard format ({len(data)} variations)")
                success_count += 1
        else:
            print(f"❌ {name}: UNEXPECTED FORMAT ({type(data).__name__})")
            fail_count += 1
    
    print()
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print(f"✅ Success: {success_count}/{len(identity)}")
    print(f"❌ Failed: {fail_count}/{len(identity)}")
    print(f"🎯 UAV seeds: {uav_count}")
    print(f"⏱️  Total time: {elapsed:.2f}s")
    print(f"⚡ Avg per name: {elapsed/len(identity):.2f}s")
    print()
    
    # Check specifically for the previously failing name
    if "Виктория Родина" in variations:
        russian_data = variations["Виктория Родина"]
        if isinstance(russian_data, list) and len(russian_data) > 0:
            print("🎉 SUCCESS: Russian name 'Виктория Родина' now works!")
            print(f"   Generated {len(russian_data)} variations")
        else:
            print("⚠️  WARNING: Russian name present but empty or wrong format")
    else:
        print("❌ ERROR: Russian name 'Виктория Родина' still missing")
    
    print()
    print("="*80)
    print("✅ TEST COMPLETE")
    print("="*80)
    
    # Save results
    with open("test_full_mainnet_scenario_results.json", "w", encoding="utf-8") as f:
        json.dump(variations, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved to: test_full_mainnet_scenario_results.json")

if __name__ == "__main__":
    test_full_mainnet_scenario()

