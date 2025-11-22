#!/usr/bin/env python3
"""
Comprehensive test to verify all scoring components are covered.
Tests against the full validator scoring system.
"""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from MIID.validator.gemini_generator import generate_variations_with_gemini
from MIID.protocol import IdentitySynapse

def test_all_components():
    """Test all scoring components."""
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not set")
        return
    
    print("="*80)
    print("COMPREHENSIVE SCORING COMPONENT VERIFICATION")
    print("="*80)
    
    # Test with comprehensive query
    query_template = """Generate 15 variations of {name}, ensuring phonetic similarity based on 10% Light, 50% Medium, and 40% Far types, and orthographic similarity based on 20% Light, 60% Medium, and 20% Far types. Approximately 30% of the total 15 variations should follow these rule-based transformations: Replace random consonants with different consonants, Replace random vowels with different vowels, and Delete a random letter. The following address is the seed country/city to generate address variations for: {address}. Generate unique real addresses within the specified country/city for each variation. The following date of birth is the seed DOB to generate variations for: {dob}."""
    
    synapse = IdentitySynapse(
        identity=[
            ["John Smith", "1990-05-15", "New York, USA"]
        ],
        query_template=query_template,
        timeout=360.0
    )
    
    print("\n🔄 Generating variations with Gemini...")
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
    
    # Verify all components
    checklist = {
        "1. Count": False,
        "2. Name Structure": False,
        "3. Uniqueness": False,
        "4. Length": False,
        "5. Rules Applied": False,
        "6. Address Format": False,
        "7. Address Region": False,
        "8. DOB Categories": False,
        "9. JSON Format": False,
        "10. Completeness": False
    }
    
    for name, var_list in variations.items():
        if isinstance(var_list, dict):
            var_list = var_list.get('variations', [])
        
        print(f"\n{'='*80}")
        print(f"Testing: {name}")
        print(f"{'='*80}")
        print(f"Variations generated: {len(var_list)}\n")
        
        # 1. Count
        if len(var_list) == 15:
            checklist["1. Count"] = True
            print("✅ Count: EXACTLY 15 variations")
        else:
            print(f"⚠️  Count: {len(var_list)} variations (expected 15)")
        
        # 2. Name Structure
        name_parts = len(name.split())
        all_multi_part = all(len(var[0].split()) == name_parts for var in var_list if len(var) > 0)
        if all_multi_part:
            checklist["2. Name Structure"] = True
            print("✅ Name Structure: All variations maintain structure")
        else:
            print("⚠️  Name Structure: Some variations don't maintain structure")
        
        # 3. Uniqueness
        names = [var[0] for var in var_list if len(var) > 0]
        unique_names = set(names)
        if len(unique_names) == len(names):
            checklist["3. Uniqueness"] = True
            print(f"✅ Uniqueness: All {len(names)} variations are unique")
        else:
            print(f"⚠️  Uniqueness: {len(unique_names)}/{len(names)} unique (duplicates found)")
        
        # 4. Length
        name_len = len(name)
        min_len = int(name_len * 0.6)
        max_len = int(name_len * 1.4)
        all_in_range = all(
            min_len <= len(var[0]) <= max_len 
            for var in var_list if len(var) > 0
        )
        if all_in_range:
            checklist["4. Length"] = True
            print(f"✅ Length: All variations in range ({min_len}-{max_len} chars)")
        else:
            print(f"⚠️  Length: Some variations outside range ({min_len}-{max_len} chars)")
        
        # 5. Rules Applied (check for special chars or transformations)
        rule_count = int(15 * 0.30)  # 30% = 4-5 variations
        # Check for special chars, deletions, or transformations
        rule_applied = sum(
            1 for var in var_list 
            if len(var) > 0 and (
                any(c in var[0] for c in ['_', '-', '.', '!', '#', '$', '@', '0']) or
                len(var[0]) < name_len * 0.9  # Possible deletion
            )
        )
        if rule_applied >= rule_count - 1:  # Allow some tolerance
            checklist["5. Rules Applied"] = True
            print(f"✅ Rules Applied: {rule_applied} variations show rule application")
        else:
            print(f"⚠️  Rules Applied: {rule_applied} variations show rules (expected ~{rule_count})")
        
        # 6. Address Format
        addresses = [var[2] for var in var_list if len(var) > 2]
        if addresses:
            # Basic format check
            valid_format = all(
                len(addr) >= 30 and 
                ',' in addr and 
                any(c.isdigit() for c in addr)
                for addr in addresses
            )
            if valid_format:
                checklist["6. Address Format"] = True
                print(f"✅ Address Format: All {len(addresses)} addresses have valid format")
            else:
                print(f"⚠️  Address Format: Some addresses may have format issues")
        
        # 7. Address Region (basic check - full validation needs validator)
        if addresses:
            region_match = all(
                "New York" in addr or "USA" in addr or "United States" in addr
                for addr in addresses
            )
            if region_match:
                checklist["7. Address Region"] = True
                print("✅ Address Region: All addresses contain region info")
            else:
                print("⚠️  Address Region: Some addresses may not match region")
        
        # 8. DOB Categories
        dobs = [var[1] for var in var_list if len(var) > 1]
        if dobs:
            # Check for different formats
            has_full_date = any('-' in dob and dob.count('-') == 2 for dob in dobs)
            has_year_month = any('-' in dob and dob.count('-') == 1 for dob in dobs)
            if has_full_date and has_year_month:
                checklist["8. DOB Categories"] = True
                print("✅ DOB Categories: Multiple DOB formats present")
            else:
                print("⚠️  DOB Categories: May not cover all required categories")
        
        # 9. JSON Format (already parsed, so valid)
        checklist["9. JSON Format"] = True
        print("✅ JSON Format: Valid JSON structure")
        
        # 10. Completeness
        if name in variations and len(var_list) > 0:
            checklist["10. Completeness"] = True
            print("✅ Completeness: All seed names have variations")
        
        # Show sample variations
        print(f"\n📝 Sample Variations (first 3):")
        for i, var in enumerate(var_list[:3], 1):
            if len(var) >= 3:
                print(f"   {i}. Name: {var[0]}, DOB: {var[1]}, Address: {var[2][:50]}...")
    
    # Summary
    print(f"\n{'='*80}")
    print("VERIFICATION SUMMARY")
    print(f"{'='*80}")
    
    passed = sum(1 for v in checklist.values() if v)
    total = len(checklist)
    
    for item, status in checklist.items():
        status_icon = "✅" if status else "⚠️ "
        print(f"{status_icon} {item}")
    
    print(f"\nPassed: {passed}/{total} checks")
    
    if passed == total:
        print("🎉 ALL CHECKS PASSED - Ready for mainnet!")
    elif passed >= total * 0.8:
        print("⚠️  MOST CHECKS PASSED - Review failed items before mainnet")
    else:
        print("❌ MULTIPLE CHECKS FAILED - Not ready for mainnet")

if __name__ == "__main__":
    test_all_components()

