"""
Test region validation with detailed logging to see which condition fails.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'MIID', 'validator'))

from reward import validate_address_region, extract_city_country, COUNTRY_MAPPING

def test_region_validation_detailed(seed_address: str, generated_address: str):
    """
    Test region validation with detailed logging of every step.
    """
    print("="*100)
    print("DETAILED REGION VALIDATION TEST")
    print("="*100)
    print()
    
    print(f"Seed Address (from validator): {seed_address}")
    print(f"Generated Address (from miner): {generated_address}")
    print()
    print("-"*100)
    print()
    
    # Step 1: Check if addresses are empty
    print("STEP 1: Check if addresses are empty")
    print("-"*100)
    if not generated_address or not seed_address:
        print("❌ FAILED: Empty address")
        return False
    print("✅ PASSED: Both addresses are not empty")
    print()
    
    # Step 2: Check special regions
    print("STEP 2: Check special regions")
    print("-"*100)
    SPECIAL_REGIONS = ["luhansk", "crimea", "donetsk", "west sahara", 'western sahara']
    seed_lower = seed_address.lower()
    print(f"Seed (lowercase): {seed_lower}")
    print(f"Is special region? {seed_lower in SPECIAL_REGIONS}")
    
    if seed_lower in SPECIAL_REGIONS:
        gen_lower = generated_address.lower()
        result = seed_lower in gen_lower
        print(f"Special region check: '{seed_lower}' in '{gen_lower}' = {result}")
        if result:
            print("✅ PASSED: Special region match")
            return True
        else:
            print("❌ FAILED: Special region not found in generated address")
            return False
    
    print("✅ Not a special region, continuing with normal validation")
    print()
    
    # Step 3: Extract city and country from generated address
    print("STEP 3: Extract city and country from GENERATED address")
    print("-"*100)
    two_parts = ',' in seed_address
    print(f"Two parts flag: {two_parts} (because ',' in seed_address = {',' in seed_address})")
    
    gen_city, gen_country = extract_city_country(generated_address, two_parts=two_parts)
    print(f"Extracted from generated address:")
    print(f"  gen_city = '{gen_city}'")
    print(f"  gen_country = '{gen_country}'")
    print()
    
    # Step 4: Check if extraction succeeded
    print("STEP 4: Check if extraction succeeded")
    print("-"*100)
    if not gen_city:
        print("❌ FAILED: No city extracted from generated address")
        return False
    print(f"✅ City extracted: '{gen_city}'")
    
    if not gen_country:
        print("❌ FAILED: No country extracted from generated address")
        return False
    print(f"✅ Country extracted: '{gen_country}'")
    print()
    
    # Step 5: Prepare seed address for comparison
    print("STEP 5: Prepare seed address for comparison")
    print("-"*100)
    seed_address_lower = seed_address.lower()
    seed_address_mapped = COUNTRY_MAPPING.get(seed_address.lower(), seed_address.lower())
    
    print(f"seed_address_lower = '{seed_address_lower}'")
    print(f"seed_address_mapped = '{seed_address_mapped}'")
    print()
    print("⚠️  NOTE: Seed address is NOT extracted! Using entire string!")
    print()
    
    # Step 6: Perform the three comparisons
    print("STEP 6: Perform the three comparison checks")
    print("-"*100)
    
    # Comparison 1: City match
    print("COMPARISON 1: City Match")
    print(f"  gen_city = '{gen_city}'")
    print(f"  seed_address_lower = '{seed_address_lower}'")
    city_match = gen_city and seed_address_lower and gen_city == seed_address_lower
    print(f"  city_match = gen_city == seed_address_lower")
    print(f"  city_match = '{gen_city}' == '{seed_address_lower}'")
    print(f"  Result: {city_match}")
    if city_match:
        print("  ✅ MATCH!")
    else:
        print(f"  ❌ NO MATCH: '{gen_city}' != '{seed_address_lower}'")
    print()
    
    # Comparison 2: Country match
    print("COMPARISON 2: Country Match")
    print(f"  gen_country = '{gen_country}'")
    print(f"  seed_address_lower = '{seed_address_lower}'")
    country_match = gen_country and seed_address_lower and gen_country == seed_address_lower
    print(f"  country_match = gen_country == seed_address_lower")
    print(f"  country_match = '{gen_country}' == '{seed_address_lower}'")
    print(f"  Result: {country_match}")
    if country_match:
        print("  ✅ MATCH!")
    else:
        print(f"  ❌ NO MATCH: '{gen_country}' != '{seed_address_lower}'")
    print()
    
    # Comparison 3: Mapped country match
    print("COMPARISON 3: Mapped Country Match")
    print(f"  gen_country = '{gen_country}'")
    print(f"  seed_address_mapped = '{seed_address_mapped}'")
    mapped_match = gen_country and seed_address_mapped and gen_country == seed_address_mapped
    print(f"  mapped_match = gen_country == seed_address_mapped")
    print(f"  mapped_match = '{gen_country}' == '{seed_address_mapped}'")
    print(f"  Result: {mapped_match}")
    if mapped_match:
        print("  ✅ MATCH!")
    else:
        print(f"  ❌ NO MATCH: '{gen_country}' != '{seed_address_mapped}'")
    print()
    
    # Step 7: Final result
    print("STEP 7: Final Result")
    print("-"*100)
    final_result = city_match or country_match or mapped_match
    print(f"Final check: city_match OR country_match OR mapped_match")
    print(f"Final check: {city_match} OR {country_match} OR {mapped_match}")
    print(f"Final result: {final_result}")
    print()
    
    if final_result:
        print("✅✅✅ REGION VALIDATION PASSED ✅✅✅")
    else:
        print("❌❌❌ REGION VALIDATION FAILED ❌❌❌")
        print()
        print("REASON: None of the three comparisons matched:")
        print(f"  1. City match: '{gen_city}' == '{seed_address_lower}' → {city_match}")
        print(f"  2. Country match: '{gen_country}' == '{seed_address_lower}' → {country_match}")
        print(f"  3. Mapped match: '{gen_country}' == '{seed_address_mapped}' → {mapped_match}")
        print()
        print("THE BUG: Comparing extracted values against entire seed string!")
        print("  - Extracted: city='{gen_city}', country='{gen_country}'")
        print(f"  - Seed string: '{seed_address_lower}'")
        print(f"  - These will never match for 'City, Country' format!")
    
    print()
    print("="*100)
    
    return final_result

# Test cases
test_cases = [
    {
        "name": "Standard 'City, Country' format (WILL FAIL)",
        "seed": "New York, USA",
        "generated": "123 Main Street, Manhattan, New York, 10001, United States of America"
    },
    {
        "name": "Just city name (MIGHT WORK)",
        "seed": "London",
        "generated": "115 New Cavendish Street, London W1T 5DU, United Kingdom"
    },
    {
        "name": "Just country name (MIGHT WORK)",
        "seed": "USA",
        "generated": "123 Main Street, New York, 10001, United States of America"
    },
    {
        "name": "Special region (WILL WORK)",
        "seed": "Crimea",
        "generated": "123 Main Street, Sevastopol, Crimea, Russia"
    }
]

print("\n" + "="*100)
print("RUNNING ALL TEST CASES")
print("="*100)
print()

for i, test in enumerate(test_cases, 1):
    print(f"\n{'='*100}")
    print(f"TEST CASE {i}: {test['name']}")
    print(f"{'='*100}\n")
    
    result = test_region_validation_detailed(test['seed'], test['generated'])
    
    print(f"\nTest Result: {'✅ PASSED' if result else '❌ FAILED'}\n")
    print("\n" + "-"*100 + "\n")

