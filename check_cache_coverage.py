#!/usr/bin/env python3
"""
Check if all possible countries that validator sends exist in address_cache.json
and have 15 addresses each.
"""

import json
import geonamescache

# Load sanctioned countries
with open('MIID/validator/sanctioned_countries.json', 'r') as f:
    sanctioned_data = json.load(f)

# Extract all sanctioned countries
sanctioned_countries = set()
for category in sanctioned_data.values():
    for item in category:
        sanctioned_countries.add(item['country'])

# Load address cache
with open('address_cache.json', 'r') as f:
    cache_data = json.load(f)

cached_countries = set(cache_data.get('addresses', {}).keys())
cached_address_counts = {country: len(addresses) for country, addresses in cache_data.get('addresses', {}).items()}

# Load valid countries from GeonamesCache (same logic as query_generator.py)
gc = geonamescache.GeonamesCache()
countries_data = gc.get_countries()

# Countries/territories to exclude (from query_generator.py)
excluded_territories = {
    'Antarctica',
    'Bouvet Island', 
    'Heard Island and McDonald Islands',
    'United States Minor Outlying Islands',
    'Tokelau',
    'British Indian Ocean Territory',
    'Netherlands Antilles',
    'Serbia and Montenegro',
    'Antigua and Barbuda',
    'Anguilla',
    'American Samoa',
    'Aland Islands',
    'Barbados',
    'Saint Barthelemy',
    'Bermuda',
    'Bonaire, Saint Eustatius and Saba ',
    'Cocos Islands',
    'Cook Islands',
    'Christmas Island',
    'Dominica',
    'Falkland Islands',
    'Micronesia',
    'Faroe Islands',
    'Grenada',
    'Guernsey',
    'Gibraltar',
    'Greenland',
    'South Georgia and the South Sandwich Islands',
    'Isle of Man',
    'Jersey',
    'Kiribati',
    'Saint Kitts and Nevis',
    'Liechtenstein',
    'Saint Martin',
    'Marshall Islands',
    'Northern Mariana Islands',
    'Maldives',
    'Norfolk Island',
    'Nauru',
    'Niue',
    'Saint Pierre and Miquelon',
    'Pitcairn',
    'Palau',
    'Solomon Islands',
    'Seychelles',
    'Saint Helena',
    'Svalbard and Jan Mayen',
    'San Marino',
    'Sao Tome and Principe',
    'Sint Maarten',
    'French Southern Territories',
    'Tonga',
    'Tuvalu',
    'Vatican',
    'Vanuatu',
    'Wallis and Futuna',
    'Samoa'
}

# Get valid countries (same logic as query_generator.py)
valid_countries = set()
for country_code, country_info in countries_data.items():
    country_name = country_info.get('name', '').strip()
    
    if not country_name:
        continue
    
    if country_name in excluded_territories:
        continue
    
    if country_name in sanctioned_countries:
        continue
    
    valid_countries.add(country_name)

# Also add sanctioned countries (they can be sent for positive samples)
all_possible_countries = valid_countries | sanctioned_countries

print("=" * 80)
print("ADDRESS CACHE COVERAGE REPORT")
print("=" * 80)
print(f"\n📊 Total possible countries validator can send: {len(all_possible_countries)}")
print(f"   - Valid countries (from GeonamesCache): {len(valid_countries)}")
print(f"   - Sanctioned countries (positive samples): {len(sanctioned_countries)}")
print(f"\n💾 Countries in cache: {len(cached_countries)}")

# Check coverage
missing_countries = all_possible_countries - cached_countries
countries_with_less_than_15 = {country: count for country, count in cached_address_counts.items() 
                                if country in all_possible_countries and count < 15}
countries_with_exactly_15 = {country: count for country, count in cached_address_counts.items() 
                             if country in all_possible_countries and count == 15}
countries_with_more_than_15 = {country: count for country, count in cached_address_counts.items() 
                               if country in all_possible_countries and count > 15}

print(f"\n✅ Countries with exactly 15 addresses: {len(countries_with_exactly_15)}")
print(f"⚠️  Countries with less than 15 addresses: {len(countries_with_less_than_15)}")
print(f"📦 Countries with more than 15 addresses: {len(countries_with_more_than_15)}")
print(f"❌ Missing countries (not in cache): {len(missing_countries)}")

# Detailed reports
if missing_countries:
    print("\n" + "=" * 80)
    print("❌ MISSING COUNTRIES (not in cache):")
    print("=" * 80)
    for country in sorted(missing_countries):
        print(f"   - {country}")

if countries_with_less_than_15:
    print("\n" + "=" * 80)
    print("⚠️  COUNTRIES WITH LESS THAN 15 ADDRESSES:")
    print("=" * 80)
    for country, count in sorted(countries_with_less_than_15.items(), key=lambda x: x[1]):
        print(f"   - {country}: {count} addresses (need {15 - count} more)")

# Summary
total_needed = len(missing_countries) + len(countries_with_less_than_15)
if total_needed == 0:
    print("\n" + "=" * 80)
    print("✅ PERFECT! All possible countries are cached with 15+ addresses!")
    print("=" * 80)
else:
    print("\n" + "=" * 80)
    print(f"📋 SUMMARY: {total_needed} countries need attention")
    print("=" * 80)
    print(f"   - {len(missing_countries)} countries need to be generated")
    print(f"   - {len(countries_with_less_than_15)} countries need more addresses")

# Show some stats
print("\n" + "=" * 80)
print("📈 CACHE STATISTICS:")
print("=" * 80)
if cached_address_counts:
    counts = list(cached_address_counts.values())
    print(f"   - Average addresses per country: {sum(counts) / len(counts):.1f}")
    print(f"   - Min addresses: {min(counts)}")
    print(f"   - Max addresses: {max(counts)}")
    print(f"   - Countries with 15 addresses: {len([c for c in counts if c == 15])}")
    print(f"   - Countries with < 15 addresses: {len([c for c in counts if c < 15])}")
    print(f"   - Countries with > 15 addresses: {len([c for c in counts if c > 15])}")

