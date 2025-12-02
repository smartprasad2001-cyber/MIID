"""
Verify that the address cache covers all countries that the validator might ask for.

This script:
1. Gets all countries from the validator's logic (negative samples)
2. Gets all countries from sanctioned individuals (positive samples)
3. Checks if the cache covers all of them
"""

import sys
import os
import json

# Add MIID/validator to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'MIID', 'validator'))

import geonamescache

def get_validator_negative_countries():
    """Get countries that validator uses for negative samples (get_random_country)."""
    gc = geonamescache.GeonamesCache()
    countries_data = gc.get_countries()
    
    # Same exclusions as query_generator.py
    excluded_territories = {
        'Antarctica', 'Bouvet Island', 'Heard Island and McDonald Islands',
        'United States Minor Outlying Islands', 'Tokelau',
        'British Indian Ocean Territory', 'Netherlands Antilles',
        'Serbia and Montenegro', 'Antigua and Barbuda', 'Anguilla',
        'American Samoa', 'Aland Islands', 'Barbados', 'Saint Barthelemy',
        'Bermuda', 'Bonaire, Saint Eustatius and Saba ', 'Cocos Islands',
        'Cook Islands', 'Christmas Island', 'Dominica', 'Falkland Islands',
        'Micronesia', 'Faroe Islands', 'Grenada', 'Guernsey', 'Gibraltar',
        'Greenland', 'South Georgia and the South Sandwich Islands',
        'Isle of Man', 'Jersey', 'Kiribati', 'Saint Kitts and Nevis',
        'Liechtenstein', 'Saint Martin', 'Marshall Islands',
        'Northern Mariana Islands', 'Maldives', 'Norfolk Island', 'Nauru',
        'Niue', 'Saint Pierre and Miquelon', 'Pitcairn', 'Palau',
        'Solomon Islands', 'Seychelles', 'Saint Helena',
        'Svalbard and Jan Mayen', 'San Marino', 'Sao Tome and Principe',
        'Sint Maarten', 'French Southern Territories', 'Tonga', 'Tuvalu',
        'Vatican', 'Vanuatu', 'Wallis and Futuna', 'Samoa'
    }
    
    # Load sanctioned countries
    sanctioned_countries = []
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(current_dir, 'MIID', 'validator', 'sanctioned_countries.json')
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                countries_data_json = json.load(f)
            for script, countries in countries_data_json.items():
                for country_info in countries:
                    country_name = country_info.get('country', '').strip()
                    if country_name:
                        sanctioned_countries.append(country_name)
    except Exception as e:
        print(f"⚠️  Error loading sanctioned countries: {e}")
    
    sanctioned_countries_set = set(sanctioned_countries)
    
    # Get countries for negative samples (excludes sanctioned countries)
    negative_countries = []
    for country_code, country_info in countries_data.items():
        country_name = country_info.get('name', '').strip()
        if not country_name:
            continue
        if country_name in excluded_territories:
            continue
        if country_name in sanctioned_countries_set:
            continue
        negative_countries.append(country_name)
    
    return sorted(negative_countries), sanctioned_countries_set

def get_validator_positive_countries():
    """Get countries that validator uses for positive samples (Country_Residence)."""
    positive_countries = set()
    
    try:
        # Load sanctioned individuals
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Check transliteration file
        transliteration_path = os.path.join(current_dir, 'MIID', 'validator', 'Sanctioned_Transliteration.json')
        if os.path.exists(transliteration_path):
            with open(transliteration_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    country = item.get('Country_Residence', '').strip()
                    if country:
                        positive_countries.add(country)
        
        # Check main list
        main_list_path = os.path.join(current_dir, 'MIID', 'validator', 'Sanctioned_list.json')
        if os.path.exists(main_list_path):
            with open(main_list_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    country = item.get('Country_Residence', '').strip()
                    if country:
                        positive_countries.add(country)
    except Exception as e:
        print(f"⚠️  Error loading positive sample countries: {e}")
    
    return sorted(list(positive_countries))

def get_cache_countries():
    """Get countries that are in the cache."""
    cache_file = os.path.join(os.path.dirname(__file__), 'address_cache.json')
    
    if not os.path.exists(cache_file):
        return set()
    
    try:
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
            return set(cache_data.get('addresses', {}).keys())
    except Exception as e:
        print(f"⚠️  Error loading cache: {e}")
        return set()

def main():
    print("="*80)
    print("ADDRESS CACHE COVERAGE VERIFICATION")
    print("="*80)
    
    # Get countries from validator
    print("\n1. Loading validator countries...")
    negative_countries, sanctioned_countries_set = get_validator_negative_countries()
    positive_countries = get_validator_positive_countries()
    
    print(f"   ✅ Negative samples (get_random_country): {len(negative_countries)} countries")
    print(f"   ✅ Positive samples (Country_Residence): {len(positive_countries)} countries")
    print(f"   ✅ Sanctioned countries: {len(sanctioned_countries_set)} countries")
    
    # Get all possible countries validator might ask for
    all_validator_countries = set(negative_countries) | set(positive_countries)
    print(f"\n   📊 Total unique countries validator might ask for: {len(all_validator_countries)}")
    
    # Get cache countries
    print("\n2. Loading cache...")
    cache_countries = get_cache_countries()
    
    if not cache_countries:
        print("   ❌ Cache file not found! Run 'python generate_address_cache.py' first.")
        return
    
    print(f"   ✅ Cache contains: {len(cache_countries)} countries")
    
    # Check coverage
    print("\n3. Checking coverage...")
    missing_negative = set(negative_countries) - cache_countries
    missing_positive = set(positive_countries) - cache_countries
    missing_sanctioned = sanctioned_countries_set - cache_countries
    
    print(f"\n   📊 Coverage Analysis:")
    print(f"   - Negative samples: {len(negative_countries)} total, {len(missing_negative)} missing")
    print(f"   - Positive samples: {len(positive_countries)} total, {len(missing_positive)} missing")
    print(f"   - Sanctioned countries: {len(sanctioned_countries_set)} total, {len(missing_sanctioned)} missing")
    
    # Overall coverage
    all_missing = missing_negative | missing_positive
    coverage_pct = (1 - len(all_missing) / len(all_validator_countries)) * 100 if all_validator_countries else 0
    
    print(f"\n   ✅ Overall Coverage: {coverage_pct:.1f}%")
    print(f"   - Covered: {len(all_validator_countries) - len(all_missing)}/{len(all_validator_countries)}")
    print(f"   - Missing: {len(all_missing)}")
    
    if missing_negative:
        print(f"\n   ⚠️  Missing negative sample countries ({len(missing_negative)}):")
        for country in sorted(missing_negative)[:10]:
            print(f"      - {country}")
        if len(missing_negative) > 10:
            print(f"      ... and {len(missing_negative) - 10} more")
    
    if missing_positive:
        print(f"\n   ⚠️  Missing positive sample countries ({len(missing_positive)}):")
        for country in sorted(missing_positive)[:10]:
            print(f"      - {country}")
        if len(missing_positive) > 10:
            print(f"      ... and {len(missing_positive) - 10} more")
    
    if missing_sanctioned:
        print(f"\n   ⚠️  Missing sanctioned countries ({len(missing_sanctioned)}):")
        for country in sorted(missing_sanctioned):
            print(f"      - {country}")
    
    # Final verdict
    print("\n" + "="*80)
    if len(all_missing) == 0:
        print("✅ VERDICT: Cache covers ALL countries the validator might ask for!")
    else:
        print(f"⚠️  VERDICT: Cache is missing {len(all_missing)} countries")
        print("   Recommendation: Re-run 'python generate_address_cache.py' to update cache")
    print("="*80)

if __name__ == "__main__":
    main()

