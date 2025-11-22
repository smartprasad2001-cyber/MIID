#!/usr/bin/env python3
"""
Test that miner output format exactly matches validator expectations.
Simulates the actual flow from miner to validator.
"""

import os
import sys
import json
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from MIID.validator.gemini_generator import generate_variations_with_gemini
from MIID.protocol import IdentitySynapse

def test_miner_validator_format():
    """Test that miner output matches validator format exactly."""
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not set")
        return
    
    print("="*80)
    print("MINER-VALIDATOR FORMAT VERIFICATION")
    print("="*80)
    print()
    
    # Create a realistic validator request
    seed_names = ["John Smith", "Maria Garcia", "Ahmed Hassan"]
    seed_dobs = ["1990-05-15", "1985-08-22", "1992-03-10"]
    seed_addresses = ["New York, USA", "Madrid, Spain", "Cairo, Egypt"]
    
    identity = [
        [name, dob, addr] 
        for name, dob, addr in zip(seed_names, seed_dobs, seed_addresses)
    ]
    
    query_template = """Generate 15 variations of {name}, ensuring phonetic similarity based on 10% Light, 50% Medium, and 40% Far types, and orthographic similarity based on 20% Light, 60% Medium, and 20% Far types. Approximately 30% of the total 15 variations should follow these rule-based transformations: Replace random consonants with different consonants, Replace random vowels with different vowels, and Delete a random letter. The following address is the seed country/city to generate address variations for: {address}. Generate unique real addresses within the specified country/city for each variation. The following date of birth is the seed DOB to generate variations for: {dob}."""
    
    # Create synapse as validator would
    synapse = IdentitySynapse(
        identity=identity,
        query_template=query_template,
        timeout=360.0
    )
    
    print("📥 Validator sends synapse:")
    print(f"   - Identity: {len(synapse.identity)} names")
    print(f"   - Query template: {len(synapse.query_template)} chars")
    print(f"   - Timeout: {synapse.timeout}s")
    print()
    
    # Simulate miner processing
    print("🔄 Miner processes request...")
    start_time = time.time()
    
    try:
        variations = generate_variations_with_gemini(
            synapse,
            gemini_api_key=api_key,
            gemini_model="gemini-2.0-flash-exp"
        )
        
        process_time = time.time() - start_time
        
        # Miner sets variations in synapse (as it would in forward())
        synapse.variations = variations
        synapse.process_time = process_time
        
        print(f"✅ Miner completed in {process_time:.2f}s")
        print()
        
    except Exception as e:
        print(f"❌ Miner processing failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Verify format matches validator expectations
    print("="*80)
    print("FORMAT VERIFICATION")
    print("="*80)
    print()
    
    issues = []
    
    # 1. Check variations is a dict
    if not isinstance(synapse.variations, dict):
        issues.append(f"❌ variations is not a dict (type: {type(synapse.variations)})")
        print(issues[-1])
    else:
        print("✅ variations is a dict")
    
    # 2. Check all seed names are present
    missing_names = set(seed_names) - set(synapse.variations.keys())
    if missing_names:
        issues.append(f"❌ Missing names: {missing_names}")
        print(issues[-1])
    else:
        print(f"✅ All {len(seed_names)} seed names present")
    
    # 3. Check format for each name
    for seed_name in seed_names:
        if seed_name not in synapse.variations:
            continue
        
        seed_data = synapse.variations[seed_name]
        
        # Check if it's old format (list) or new format (dict with variations)
        if isinstance(seed_data, list):
            # Old format: List[List[str]]
            var_list = seed_data
            print(f"\n📋 {seed_name}: Old format (List[List[str]])")
        elif isinstance(seed_data, dict):
            # New format: {variations: [...], uav: {...}}
            if "variations" in seed_data:
                var_list = seed_data["variations"]
                print(f"\n📋 {seed_name}: New format (dict with variations)")
                if "uav" in seed_data:
                    print(f"   ✅ Has UAV data")
            else:
                issues.append(f"❌ {seed_name}: dict format missing 'variations' key")
                print(issues[-1])
                continue
        else:
            issues.append(f"❌ {seed_name}: Invalid format (type: {type(seed_data)})")
            print(issues[-1])
            continue
        
        # Check each variation is [name, dob, address]
        for i, var in enumerate(var_list, 1):
            if not isinstance(var, list):
                issues.append(f"❌ {seed_name} var {i}: Not a list (type: {type(var)})")
                continue
            
            if len(var) < 3:
                issues.append(f"❌ {seed_name} var {i}: Less than 3 elements (has {len(var)})")
                continue
            
            name_var, dob_var, addr_var = var[0], var[1], var[2]
            
            # Check types
            if not isinstance(name_var, str):
                issues.append(f"❌ {seed_name} var {i}: name_var is not str (type: {type(name_var)})")
            if not isinstance(dob_var, str):
                issues.append(f"❌ {seed_name} var {i}: dob_var is not str (type: {type(dob_var)})")
            if not isinstance(addr_var, str):
                issues.append(f"❌ {seed_name} var {i}: addr_var is not str (type: {type(addr_var)})")
        
        if not issues or not any(f"{seed_name}" in issue for issue in issues):
            print(f"   ✅ All {len(var_list)} variations have correct format [name, dob, address]")
    
    # 4. Test deserialize() method (as validator would use)
    print("\n" + "="*80)
    print("DESERIALIZE TEST (Validator Method)")
    print("="*80)
    print()
    
    try:
        deserialized = synapse.deserialize()
        print("✅ deserialize() works")
        print(f"   Type: {type(deserialized)}")
        print(f"   Keys: {list(deserialized.keys())[:3]}...")
        
        # Verify deserialized format
        if isinstance(deserialized, dict):
            print("✅ Deserialized is a dict")
            for name in list(deserialized.keys())[:2]:
                data = deserialized[name]
                if isinstance(data, list):
                    print(f"   ✅ {name}: List format (old)")
                elif isinstance(data, dict) and "variations" in data:
                    print(f"   ✅ {name}: Dict format with variations (new)")
                else:
                    issues.append(f"❌ {name}: Invalid deserialized format")
        else:
            issues.append(f"❌ Deserialized is not a dict")
            
    except Exception as e:
        issues.append(f"❌ deserialize() failed: {e}")
        print(issues[-1])
    
    # 5. Test JSON serialization (as Bittensor would do)
    print("\n" + "="*80)
    print("JSON SERIALIZATION TEST (Bittensor Transport)")
    print("="*80)
    print()
    
    try:
        # Simulate what Bittensor does internally
        variations_dict = synapse.variations
        
        # Convert to JSON-serializable format
        json_serializable = {}
        for name, data in variations_dict.items():
            if isinstance(data, list):
                json_serializable[name] = data
            elif isinstance(data, dict):
                json_serializable[name] = data
        
        json_str = json.dumps(json_serializable, ensure_ascii=False)
        print(f"✅ JSON serialization works")
        print(f"   Size: {len(json_str)} bytes")
        
        # Deserialize back
        json_deserialized = json.loads(json_str)
        print(f"✅ JSON deserialization works")
        print(f"   Keys match: {set(json_deserialized.keys()) == set(variations_dict.keys())}")
        
    except Exception as e:
        issues.append(f"❌ JSON serialization failed: {e}")
        print(issues[-1])
        import traceback
        traceback.print_exc()
    
    # 6. Verify validator can process it (simulate validator processing)
    print("\n" + "="*80)
    print("VALIDATOR PROCESSING SIMULATION")
    print("="*80)
    print()
    
    try:
        # Simulate validator's process_new_variations_structure logic
        validator_variations = {}
        
        for seed_name in seed_names:
            if seed_name not in synapse.variations:
                continue
            
            seed_data = synapse.variations[seed_name]
            
            if isinstance(seed_data, list):
                # Old format: use directly
                validator_variations[seed_name] = seed_data
            elif isinstance(seed_data, dict) and "variations" in seed_data:
                # New format: extract variations
                validator_variations[seed_name] = seed_data["variations"]
            else:
                issues.append(f"❌ {seed_name}: Cannot process format")
                continue
        
        print(f"✅ Validator can process {len(validator_variations)}/{len(seed_names)} names")
        
        # Verify validator can extract name variations
        for name, var_list in validator_variations.items():
            name_vars = [var[0] for var in var_list if len(var) > 0]
            dob_vars = [var[1] for var in var_list if len(var) > 1]
            addr_vars = [var[2] for var in var_list if len(var) > 2]
            
            print(f"   ✅ {name}: {len(name_vars)} names, {len(dob_vars)} DOBs, {len(addr_vars)} addresses")
        
    except Exception as e:
        issues.append(f"❌ Validator processing simulation failed: {e}")
        print(issues[-1])
        import traceback
        traceback.print_exc()
    
    # Final summary
    print("\n" + "="*80)
    print("FINAL VERIFICATION")
    print("="*80)
    print()
    
    if not issues:
        print("🎉 PERFECT - All format checks passed!")
        print("✅ Miner output format matches validator expectations exactly")
        print("✅ Ready for mainnet deployment")
    else:
        print(f"⚠️  Found {len(issues)} issues:")
        for issue in issues:
            print(f"   {issue}")
        print("\n❌ Format issues need to be fixed before mainnet")
    
    # Save test results
    test_results = {
        "timestamp": time.time(),
        "process_time": process_time,
        "seed_names": seed_names,
        "variations_count": {name: len(synapse.variations.get(name, [])) if isinstance(synapse.variations.get(name), list) else len(synapse.variations.get(name).get("variations", [])) if isinstance(synapse.variations.get(name), dict) else 0 for name in seed_names},
        "issues": issues,
        "format_valid": len(issues) == 0
    }
    
    with open("miner_validator_format_test.json", "w") as f:
        json.dump(test_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Test results saved to: miner_validator_format_test.json")
    
    return len(issues) == 0

if __name__ == "__main__":
    success = test_miner_validator_format()
    sys.exit(0 if success else 1)

