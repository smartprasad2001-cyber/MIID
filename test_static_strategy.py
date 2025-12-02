#!/usr/bin/env python3
"""
Test script for static dataset strategy.
Creates a sample dataset and tests the generation logic.
"""

import csv
import sys
import os

# Sample address data (simulating OpenAddresses format)
SAMPLE_DATA = [
    {
        'housenumber': '26',
        'street': 'Siedlisko',
        'city': 'Grabowiec',
        'postcode': '22-425',
        'country': 'Poland'
    },
    {
        'housenumber': '9',
        'street': 'Sadków Duchowny',
        'city': 'Belsk Duży',
        'postcode': '05-622',
        'country': 'Poland'
    },
    {
        'housenumber': '7',
        'street': 'Wrzosowa',
        'city': 'Radziejowice',
        'postcode': '96-325',
        'country': 'Poland'
    },
    {
        'housenumber': '63',
        'street': 'Aleja Pod Lasem',
        'city': 'Celinów',
        'postcode': '05-300',
        'country': 'Poland'
    },
    {
        'housenumber': '25',
        'street': 'Nowe Gałki',
        'city': 'Mała Wieś',
        'postcode': '09-460',
        'country': 'Poland'
    },
    {
        'housenumber': '410B',
        'street': 'Trawniki',
        'city': 'Trawniki',
        'postcode': '21-044',
        'country': 'Poland'
    },
    {
        'housenumber': '6',
        'street': 'Księcia Janusza',
        'city': 'Wólka Radzymińska',
        'postcode': '05-126',
        'country': 'Poland'
    },
    {
        'housenumber': '86',
        'street': 'Studzianek',
        'city': 'Biała Rawska',
        'postcode': '96-200',
        'country': 'Poland'
    },
    {
        'housenumber': '29A',
        'street': 'Nuna',
        'city': 'Nasielsk',
        'postcode': '05-190',
        'country': 'Poland'
    },
    {
        'housenumber': '135',
        'street': 'Nowowiejska',
        'city': 'Pilaszków',
        'postcode': '05-860',
        'country': 'Poland'
    },
]

def create_sample_dataset(filename: str = "sample_poland_addresses.csv"):
    """Create a sample dataset file for testing."""
    print(f"📝 Creating sample dataset: {filename}")
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['housenumber', 'street', 'city', 'postcode', 'country'])
        writer.writeheader()
        writer.writerows(SAMPLE_DATA)
    
    print(f"✅ Created {filename} with {len(SAMPLE_DATA)} addresses")
    return filename

def test_pre_filtering():
    """Test the pre-filtering logic."""
    from generate_from_static_dataset import construct_address_string, pre_filter_addresses
    
    print("\n" + "="*80)
    print("TESTING PRE-FILTERING LOGIC")
    print("="*80)
    
    # Test address construction
    print("\n1. Testing address construction:")
    for record in SAMPLE_DATA[:3]:
        address = construct_address_string(record)
        print(f"   ✅ {address}")
    
    # Test pre-filtering
    print("\n2. Testing pre-filtering:")
    filtered = pre_filter_addresses(SAMPLE_DATA, "Poland")
    print(f"   ✅ {len(filtered)}/{len(SAMPLE_DATA)} addresses passed pre-filtering")
    
    # Show filtered addresses
    print("\n3. Pre-filtered addresses:")
    for i, addr in enumerate(filtered[:5], 1):
        print(f"   {i}. {addr}")

def main():
    """Main test function."""
    print("="*80)
    print("STATIC DATASET STRATEGY - TEST SCRIPT")
    print("="*80)
    
    # Create sample dataset
    dataset_file = create_sample_dataset()
    
    # Test pre-filtering
    test_pre_filtering()
    
    print("\n" + "="*80)
    print("NEXT STEPS")
    print("="*80)
    print(f"1. Review the sample dataset: {dataset_file}")
    print("2. Run the generator with the sample dataset:")
    print(f"   python3 generate_from_static_dataset.py --country Poland --count 5 --dataset {dataset_file}")
    print("3. The script will:")
    print("   - Load addresses from the dataset")
    print("   - Pre-filter locally (no API calls)")
    print("   - Validate sample with Nominatim API")
    print("   - Export validated addresses to CSV")
    print("="*80)

if __name__ == "__main__":
    main()

