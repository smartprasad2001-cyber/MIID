#!/usr/bin/env python3
"""
Test Gemini output against actual validator scoring requirements.
Verifies addresses and DOBs will score maximum marks.
"""

import os
import sys
import json
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from MIID.validator.gemini_generator import generate_variations_with_gemini
from MIID.validator.reward import (
    looks_like_address,
    validate_address_region,
    _grade_dob_variations
)
from MIID.protocol import IdentitySynapse

def test_address_format(address: str) -> dict:
    """Test if address passes looks_like_address validation."""
    result = {
        "address": address,
        "passes": False,
        "checks": {}
    }
    
    # Check length (30-300 chars after removing non-word)
    import re
    address_len = re.sub(r'[^\w]', '', address.strip(), flags=re.UNICODE)
    result["checks"]["length_30_300"] = 30 <= len(address_len) <= 300
    result["checks"]["length_value"] = len(address_len)
    
    # Check letter count (>= 20)
    letter_count = len(re.findall(r'[^\W\d]', address, flags=re.UNICODE))
    result["checks"]["letter_count_20+"] = letter_count >= 20
    result["checks"]["letter_count"] = letter_count
    
    # Check for numbers in comma-separated sections
    address_for_number = address.replace('-', '').replace(';', '')
    sections = [s.strip() for s in address_for_number.split(',')]
    sections_with_numbers = [s for s in sections if re.findall(r"[0-9]+", s)]
    result["checks"]["has_numbers"] = len(sections_with_numbers) >= 1
    result["checks"]["sections_with_numbers"] = len(sections_with_numbers)
    
    # Check comma count (>= 2)
    comma_count = address.count(",")
    result["checks"]["comma_count_2+"] = comma_count >= 2
    result["checks"]["comma_count"] = comma_count
    
    # Check for disallowed special chars
    special_chars = ['`', ':', '%', '$', '@', '*', '^', '[', ']', '{', '}', '_', '«', '»']
    has_disallowed = any(char in address for char in special_chars)
    result["checks"]["no_disallowed_chars"] = not has_disallowed
    if has_disallowed:
        result["checks"]["disallowed_found"] = [c for c in special_chars if c in address]
    
    # Check unique chars (>= 5)
    unique_chars = len(set(address))
    result["checks"]["unique_chars_5+"] = unique_chars >= 5
    result["checks"]["unique_chars"] = unique_chars
    
    # Check has letters
    has_letters = bool(re.match(r".*[a-zA-Z].*", address))
    result["checks"]["has_letters"] = has_letters
    
    # Overall pass
    result["passes"] = all([
        result["checks"]["length_30_300"],
        result["checks"]["letter_count_20+"],
        result["checks"]["has_numbers"],
        result["checks"]["comma_count_2+"],
        result["checks"]["no_disallowed_chars"],
        result["checks"]["unique_chars_5+"],
        result["checks"]["has_letters"]
    ])
    
    return result

def test_dob_categories(dob_variations: list, seed_dob: str) -> dict:
    """Test if DOB variations cover all required categories."""
    try:
        seed_date = datetime.strptime(seed_dob, "%Y-%m-%d")
    except:
        return {"error": "Invalid seed DOB format"}
    
    categories_found = {
        "±1 day": False,
        "±3 days": False,
        "±30 days": False,
        "±90 days": False,
        "±365 days": False,
        "Year+Month only": False
    }
    
    category_examples = {}
    
    for dob_var in dob_variations:
        if not dob_var:
            continue
        
        try:
            # Try full date format
            var_date = datetime.strptime(dob_var, "%Y-%m-%d")
            day_diff = abs((var_date - seed_date).days)
            
            if day_diff <= 1:
                categories_found["±1 day"] = True
                category_examples["±1 day"] = dob_var
            elif day_diff <= 3:
                categories_found["±3 days"] = True
                category_examples["±3 days"] = dob_var
            elif day_diff <= 30:
                categories_found["±30 days"] = True
                category_examples["±30 days"] = dob_var
            elif day_diff <= 90:
                categories_found["±90 days"] = True
                category_examples["±90 days"] = dob_var
            elif day_diff <= 365:
                categories_found["±365 days"] = True
                category_examples["±365 days"] = dob_var
        except ValueError:
            # Try year-month only
            try:
                year_month = datetime.strptime(dob_var, "%Y-%m")
                if (seed_date.year == year_month.year and 
                    seed_date.month == year_month.month):
                    categories_found["Year+Month only"] = True
                    category_examples["Year+Month only"] = dob_var
            except:
                pass
    
    found_count = sum(categories_found.values())
    total_categories = len(categories_found)
    score = found_count / total_categories if total_categories > 0 else 0.0
    
    return {
        "categories_found": categories_found,
        "found_count": found_count,
        "total_categories": total_categories,
        "score": score,
        "examples": category_examples,
        "all_found": found_count == total_categories
    }

def main():
    """Test Gemini output against validator requirements."""
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not set")
        return
    
    # Test synapse
    synapse = IdentitySynapse(
        identity=[
            ["John Smith", "1990-05-15", "New York, USA"]
        ],
        query_template="Generate 15 variations of {name}. The following address is the seed country/city to generate address variations for: {address}. Generate unique real addresses within the specified country/city for each variation. The following date of birth is the seed DOB to generate variations for: {dob}.\n\n[ADDITIONAL CONTEXT]:\n- Address variations should be realistic addresses within the specified country/city\n- DOB variations ATLEAST one in each category (±1 day, ±3 days, ±30 days, ±90 days, ±365 days, year+month only)\n- For year+month, generate the exact DOB without day\n- Each variation must have a different, realistic address and DOB",
        timeout=360.0
    )
    
    print("="*80)
    print("Testing Gemini Output Against Validator Requirements")
    print("="*80)
    
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
    
    # Test each identity
    for name, var_list in variations.items():
        if isinstance(var_list, dict):
            var_list = var_list.get('variations', [])
        
        print("="*80)
        print(f"Testing: {name}")
        print("="*80)
        print(f"Variations: {len(var_list)}\n")
        
        # Test addresses
        print("📍 ADDRESS VALIDATION:")
        print("-" * 80)
        address_results = []
        for i, var in enumerate(var_list[:5], 1):  # Test first 5
            addr = var[2] if len(var) > 2 else ""
            result = test_address_format(addr)
            address_results.append(result)
            
            status = "✅" if result["passes"] else "❌"
            print(f"{status} Variation {i}: {addr[:60]}...")
            if not result["passes"]:
                print(f"   Failed checks:")
                for check, passed in result["checks"].items():
                    if not passed and check not in ["length_value", "letter_count", "comma_count", "unique_chars", "sections_with_numbers"]:
                        print(f"      - {check}: {result['checks'].get(check, 'N/A')}")
        
        # Test region validation
        print(f"\n🌍 REGION VALIDATION:")
        print("-" * 80)
        seed_address = "New York, USA"
        region_results = []
        for i, var in enumerate(var_list[:5], 1):
            addr = var[2] if len(var) > 2 else ""
            region_match = validate_address_region(addr, seed_address)
            region_results.append(region_match)
            status = "✅" if region_match else "❌"
            print(f"{status} Variation {i}: Region match = {region_match}")
        
        # Test DOB categories
        print(f"\n📅 DOB CATEGORY VALIDATION:")
        print("-" * 80)
        seed_dob = "1990-05-15"
        dob_variations = [var[1] for var in var_list if len(var) > 1]
        dob_result = test_dob_categories(dob_variations, seed_dob)
        
        if "error" in dob_result:
            print(f"❌ Error: {dob_result['error']}")
        else:
            print(f"Categories Found: {dob_result['found_count']}/{dob_result['total_categories']}")
            print(f"Score: {dob_result['score']:.2%}")
            print(f"\nCategory Status:")
            for category, found in dob_result["categories_found"].items():
                status = "✅" if found else "❌"
                example = dob_result["examples"].get(category, "N/A")
                print(f"   {status} {category}: {example}")
        
        # Summary
        print(f"\n📊 SUMMARY:")
        print("-" * 80)
        address_pass_rate = sum(1 for r in address_results if r["passes"]) / len(address_results) if address_results else 0
        region_pass_rate = sum(region_results) / len(region_results) if region_results else 0
        dob_score = dob_result.get("score", 0.0) if "error" not in dob_result else 0.0
        
        print(f"Address Format: {address_pass_rate:.1%} pass rate")
        print(f"Region Match: {region_pass_rate:.1%} pass rate")
        print(f"DOB Categories: {dob_score:.1%} coverage")
        
        overall = (address_pass_rate + region_pass_rate + dob_score) / 3
        print(f"\nOverall Compliance: {overall:.1%}")
        
        if overall >= 0.9:
            print("🎉 EXCELLENT - Will score maximum marks!")
        elif overall >= 0.7:
            print("✅ GOOD - Should score well")
        else:
            print("⚠️  NEEDS IMPROVEMENT - May not score maximum")

if __name__ == "__main__":
    main()

