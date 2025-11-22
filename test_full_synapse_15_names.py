#!/usr/bin/env python3
"""
Comprehensive test with full validator synapse:
- 15 seed names
- 15 variations per name
- Full query template with all requirements
- Verify output matches validator expectations
"""

import os
import sys
import json
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from MIID.validator.gemini_generator import generate_variations_with_gemini
from MIID.protocol import IdentitySynapse

def test_full_synapse():
    """Test with full validator synapse - 15 names, 15 variations each."""
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not set")
        return
    
    # Create realistic seed data - 15 names with different countries
    seed_names = [
        "John Smith",
        "Maria Garcia",
        "Ahmed Hassan",
        "Li Wei",
        "Emma Johnson",
        "Carlos Rodriguez",
        "Yuki Tanaka",
        "Sophie Martin",
        "Mohammed Ali",
        "Anna Schmidt",
        "David Brown",
        "Isabella Rossi",
        "James Wilson",
        "Olivia Anderson",
        "Michael Taylor"
    ]
    
    seed_dobs = [
        "1990-05-15",
        "1985-08-22",
        "1992-03-10",
        "1988-11-30",
        "1995-01-18",
        "1991-07-05",
        "1987-12-25",
        "1993-04-14",
        "1989-09-08",
        "1994-06-20",
        "1990-02-28",
        "1986-10-12",
        "1992-08-03",
        "1988-05-17",
        "1991-11-22"
    ]
    
    seed_addresses = [
        "New York, USA",
        "Madrid, Spain",
        "Cairo, Egypt",
        "Beijing, China",
        "London, UK",
        "Mexico City, Mexico",
        "Tokyo, Japan",
        "Paris, France",
        "Dubai, UAE",
        "Berlin, Germany",
        "Toronto, Canada",
        "Rome, Italy",
        "Sydney, Australia",
        "Stockholm, Sweden",
        "Amsterdam, Netherlands"
    ]
    
    # Build identity list
    identity = [
        [name, dob, addr] 
        for name, dob, addr in zip(seed_names, seed_dobs, seed_addresses)
    ]
    
    # Full query template with all requirements
    query_template = """Generate 15 variations of {name}, ensuring phonetic similarity based on 10% Light, 50% Medium, and 40% Far types, and orthographic similarity based on 20% Light, 60% Medium, and 20% Far types. Approximately 30% of the total 15 variations should follow these rule-based transformations: Replace random consonants with different consonants, Replace random vowels with different vowels, and Delete a random letter. The following address is the seed country/city to generate address variations for: {address}. Generate unique real addresses within the specified country/city for each variation. The following date of birth is the seed DOB to generate variations for: {dob}."""
    
    synapse = IdentitySynapse(
        identity=identity,
        query_template=query_template,
        timeout=360.0
    )
    
    print("="*80)
    print("FULL SYNAPSE TEST - 15 NAMES, 15 VARIATIONS EACH")
    print("="*80)
    print(f"\n📋 Test Configuration:")
    print(f"   - Seed Names: {len(seed_names)}")
    print(f"   - Variations per name: 15")
    print(f"   - Total expected variations: {len(seed_names) * 15}")
    print(f"   - Countries: {len(set(seed_addresses))} different countries")
    print()
    
    start_time = time.time()
    
    print("🔄 Generating variations with Gemini...")
    print("   (This may take several minutes for 15 names)")
    print()
    
    try:
        variations = generate_variations_with_gemini(
            synapse,
            gemini_api_key=api_key,
            gemini_model="gemini-2.0-flash-exp"
        )
        
        elapsed_time = time.time() - start_time
        
        print("✅ Generation complete")
        print(f"⏱️  Total time: {elapsed_time:.2f} seconds")
        print(f"⏱️  Average per name: {elapsed_time/len(seed_names):.2f} seconds")
        print()
        
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Verify output
    print("="*80)
    print("OUTPUT VERIFICATION")
    print("="*80)
    print()
    
    verification_results = {
        "total_names": len(seed_names),
        "names_with_variations": 0,
        "total_variations": 0,
        "correct_count": 0,
        "structure_issues": 0,
        "missing_names": [],
        "issues": []
    }
    
    # Check each seed name
    for i, seed_name in enumerate(seed_names):
        print(f"Checking: {seed_name}")
        
        if seed_name not in variations:
            verification_results["missing_names"].append(seed_name)
            print(f"   ❌ Missing: No variations found")
            continue
        
        var_data = variations[seed_name]
        
        # Handle new structure with UAV
        if isinstance(var_data, dict):
            var_list = var_data.get('variations', [])
        else:
            var_list = var_data
        
        if not var_list:
            verification_results["missing_names"].append(seed_name)
            print(f"   ❌ Missing: Empty variations list")
            continue
        
        verification_results["names_with_variations"] += 1
        verification_results["total_variations"] += len(var_list)
        
        # Check count
        expected_count = 15
        actual_count = len(var_list)
        if actual_count == expected_count:
            verification_results["correct_count"] += 1
            print(f"   ✅ Count: {actual_count}/{expected_count}")
        else:
            print(f"   ⚠️  Count: {actual_count}/{expected_count} (expected {expected_count})")
            verification_results["issues"].append(f"{seed_name}: Count mismatch ({actual_count}/{expected_count})")
        
        # Check structure (all variations should be [name, dob, address])
        structure_ok = True
        for j, var in enumerate(var_list):
            if not isinstance(var, list) or len(var) < 3:
                structure_ok = False
                print(f"   ⚠️  Variation {j+1}: Invalid structure (expected [name, dob, address])")
                verification_results["issues"].append(f"{seed_name} var {j+1}: Invalid structure")
                break
            
            name_var, dob_var, addr_var = var[0], var[1], var[2]
            
            # Check name structure (should maintain multi-part if original is multi-part)
            # Count parts: split by space OR hyphen (both are acceptable)
            seed_parts = len([p for p in seed_name.replace('-', ' ').split() if p])
            var_parts = len([p for p in name_var.replace('-', ' ').split() if p])
            if seed_parts > 1 and var_parts == 1:
                structure_ok = False
                print(f"   ⚠️  Variation {j+1}: Name structure issue ('{name_var}' should be multi-part)")
                verification_results["issues"].append(f"{seed_name} var {j+1}: Name structure issue")
        
        if structure_ok:
            print(f"   ✅ Structure: All variations have correct format")
        else:
            verification_results["structure_issues"] += 1
        
        # Check DOB format
        dob_formats = set()
        for var in var_list:
            if len(var) > 1:
                dob = var[1]
                if '-' in dob:
                    parts = dob.split('-')
                    if len(parts) == 3:
                        dob_formats.add('full_date')
                    elif len(parts) == 2:
                        dob_formats.add('year_month')
        
        print(f"   📅 DOB formats: {len(dob_formats)} types found")
        
        # Check address format
        addresses = [var[2] for var in var_list if len(var) > 2]
        valid_addresses = sum(
            1 for addr in addresses 
            if len(addr) >= 30 and ',' in addr and any(c.isdigit() for c in addr)
        )
        print(f"   📍 Addresses: {valid_addresses}/{len(addresses)} have valid format")
        
        print()
    
    # Summary
    print("="*80)
    print("VERIFICATION SUMMARY")
    print("="*80)
    print()
    
    print(f"📊 Results:")
    print(f"   - Names with variations: {verification_results['names_with_variations']}/{verification_results['total_names']}")
    print(f"   - Total variations generated: {verification_results['total_variations']}")
    print(f"   - Expected variations: {verification_results['total_names'] * 15}")
    print(f"   - Names with correct count: {verification_results['correct_count']}/{verification_results['names_with_variations']}")
    print(f"   - Structure issues: {verification_results['structure_issues']}")
    print()
    
    if verification_results['missing_names']:
        print(f"❌ Missing Names ({len(verification_results['missing_names'])}):")
        for name in verification_results['missing_names']:
            print(f"   - {name}")
        print()
    
    if verification_results['issues']:
        print(f"⚠️  Issues Found ({len(verification_results['issues'])}):")
        for issue in verification_results['issues'][:10]:  # Show first 10
            print(f"   - {issue}")
        if len(verification_results['issues']) > 10:
            print(f"   ... and {len(verification_results['issues']) - 10} more")
        print()
    
    # Final verdict
    success_rate = verification_results['names_with_variations'] / verification_results['total_names']
    count_rate = verification_results['correct_count'] / verification_results['names_with_variations'] if verification_results['names_with_variations'] > 0 else 0
    
    print("="*80)
    if success_rate == 1.0 and count_rate == 1.0 and verification_results['structure_issues'] == 0:
        print("🎉 PERFECT - All checks passed! Miner output matches validator requirements!")
    elif success_rate >= 0.9 and count_rate >= 0.8:
        print("✅ GOOD - Most checks passed. Minor issues to review.")
    elif success_rate >= 0.7:
        print("⚠️  NEEDS IMPROVEMENT - Some issues found. Review before mainnet.")
    else:
        print("❌ FAILED - Multiple issues found. Not ready for mainnet.")
    
    print(f"\nSuccess Rate: {success_rate*100:.1f}%")
    print(f"Count Accuracy: {count_rate*100:.1f}%")
    print("="*80)
    
    # Save results
    output_file = "test_full_synapse_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            "verification_results": verification_results,
            "variations": variations,
            "elapsed_time": elapsed_time,
            "timestamp": time.time()
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved to: {output_file}")

if __name__ == "__main__":
    test_full_synapse()

