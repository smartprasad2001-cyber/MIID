#!/usr/bin/env python3
"""
Remove countries with duplicates from cache and failed_countries
"""

import json

# Countries with duplicates (from check_duplicates.py output)
countries_with_duplicates = [
    "Angola",
    "Argentina", 
    "Australia",
    "Bahamas",
    "Bangladesh",
    "Belize",
    "Benin",
    "Bhutan",
    "Bolivia",
    "Brazil"  # Also has duplicate
]

cache_file = "validated_address_cache_new.json"

# Load cache
with open(cache_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

addresses = data.get("addresses", {})
failed_countries = data.get("failed_countries", [])

# Remove countries with duplicates
removed_countries = []
for country in countries_with_duplicates:
    if country in addresses:
        del addresses[country]
        removed_countries.append(country)
        print(f"Removed {country} from addresses")

# Remove from failed_countries too
for country in countries_with_duplicates:
    if country in failed_countries:
        failed_countries.remove(country)
        print(f"Removed {country} from failed_countries")

# Update cache data
data["addresses"] = addresses
data["cached_countries"] = len(addresses)
data["failed_countries"] = failed_countries

# Save updated cache
with open(cache_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"\n✅ Removed {len(removed_countries)} countries with duplicates:")
for country in removed_countries:
    print(f"   - {country}")
print(f"\nUpdated cache: {len(addresses)} countries, {len(failed_countries)} failed countries")

