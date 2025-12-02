"""
Test to demonstrate the bug in validate_address_region()

The bug: The function compares extracted city/country from generated address
against the ENTIRE seed address string instead of extracting city/country from seed.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'MIID', 'validator'))

from reward import validate_address_region, extract_city_country

# Test case: Seed is "New York, USA"
seed_address = "New York, USA"

# Generated address is in New York City, USA
generated_address = "New York Public Library, 40, Hearst Plaza, Lincoln Square, Manhattan, New York County, City of New York, New York, 10023, United States of America"

print("="*100)
print("TESTING validate_address_region() BUG")
print("="*100)
print()
print(f"Seed Address: {seed_address}")
print(f"Generated Address: {generated_address}")
print()

# Extract city and country from both
gen_city, gen_country = extract_city_country(generated_address)
seed_city, seed_country = extract_city_country(seed_address)

print("Extracted values:")
print(f"  From generated address: city='{gen_city}', country='{gen_country}'")
print(f"  From seed address: city='{seed_city}', country='{seed_country}'")
print()

# What the function currently does (BUGGY):
seed_address_lower = seed_address.lower()
print("Current buggy comparison:")
print(f"  gen_city == seed_address_lower: '{gen_city}' == '{seed_address_lower}' = {gen_city == seed_address_lower}")
print(f"  gen_country == seed_address_lower: '{gen_country}' == '{seed_address_lower}' = {gen_country == seed_address_lower}")
print()

# What it SHOULD do:
print("What it SHOULD compare:")
print(f"  gen_city == seed_city: '{gen_city}' == '{seed_city}' = {gen_city == seed_city}")
print(f"  gen_country == seed_country: '{gen_country}' == '{seed_country}' = {gen_country == seed_country}")
print()

# Actual result
result = validate_address_region(generated_address, seed_address)
print(f"validate_address_region() result: {result}")
print()

if not result:
    print("❌ BUG CONFIRMED: Function returns False even though addresses match!")
    print("   The generated address is clearly in New York, USA, but validation fails.")
    print("   This is because it compares 'new york' (extracted city) with 'new york, usa' (entire seed).")
else:
    print("✅ Function works correctly (unexpected)")

