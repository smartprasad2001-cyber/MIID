#!/usr/bin/env python3
"""
Download and prepare address dataset from OpenAddresses.

OpenAddresses is a free, open dataset of global addresses.
Website: https://openaddresses.io/
Data: https://data.openaddresses.io/

Usage:
    python download_openaddresses.py --country "Poland" --output poland_addresses.csv
    python download_openaddresses.py --country "Russia" --output russia_addresses.csv
"""

import argparse
import csv
import os
import sys
import requests
import zipfile
import io
import time
from typing import List, Dict, Optional

# OpenAddresses country codes mapping
COUNTRY_CODES = {
    "Poland": "pl",
    "Russia": "ru",
    "United States": "us",
    "United Kingdom": "gb",
    "Germany": "de",
    "France": "fr",
    "Spain": "es",
    "Italy": "it",
    # Add more as needed
}

OPENADDRESSES_BASE_URL = "https://data.openaddresses.io/"


def download_openaddresses_country(country_name: str, output_file: str, verbose: bool = True) -> bool:
    """
    Download OpenAddresses data for a country and convert to our CSV format.
    
    Args:
        country_name: Full country name (e.g., "Poland")
        output_file: Output CSV file path
        verbose: Print progress
    
    Returns:
        True if successful, False otherwise
    """
    country_code = COUNTRY_CODES.get(country_name)
    if not country_code:
        print(f"❌ Country '{country_name}' not in mapping. Available: {list(COUNTRY_CODES.keys())}")
        return False
    
    if verbose:
        print(f"🌍 Downloading OpenAddresses data for {country_name} ({country_code.upper()})...")
        print(f"   Source: {OPENADDRESSES_BASE_URL}")
    
    # OpenAddresses provides country-level ZIP files
    # Format: https://data.openaddresses.io/runs/{country_code}/latest.zip
    zip_url = f"{OPENADDRESSES_BASE_URL}runs/{country_code}/latest.zip"
    
    try:
        if verbose:
            print(f"   📥 Downloading from: {zip_url}")
        
        response = requests.get(zip_url, stream=True, timeout=60)
        response.raise_for_status()
        
        # Check if file exists
        if response.status_code == 404:
            print(f"❌ No OpenAddresses data available for {country_name}")
            print(f"   💡 Try checking: https://data.openaddresses.io/")
            return False
        
        # Download ZIP
        zip_data = io.BytesIO()
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        if verbose:
            print(f"   📦 Downloading ZIP ({total_size / 1024 / 1024:.1f} MB)...")
        
        for chunk in response.iter_content(chunk_size=8192):
            zip_data.write(chunk)
            downloaded += len(chunk)
            if verbose and total_size > 0:
                progress = (downloaded / total_size) * 100
                print(f"\r   Progress: {progress:.1f}%", end='', flush=True)
        
        if verbose:
            print()  # New line after progress
        
        zip_data.seek(0)
        
        # Extract CSV files from ZIP
        if verbose:
            print(f"   📂 Extracting CSV files...")
        
        addresses = []
        with zipfile.ZipFile(zip_data, 'r') as zip_ref:
            csv_files = [f for f in zip_ref.namelist() if f.endswith('.csv')]
            
            if verbose:
                print(f"   Found {len(csv_files)} CSV files")
            
            for csv_file in csv_files:
                if verbose:
                    print(f"   Processing: {csv_file}")
                
                # Read CSV
                with zip_ref.open(csv_file) as f:
                    reader = csv.DictReader(io.TextIOWrapper(f, encoding='utf-8'))
                    
                    for row in reader:
                        # OpenAddresses format: LON,LAT,NUMBER,STREET,CITY,DISTRICT,REGION,POSTCODE,ID
                        address = {
                            'housenumber': row.get('NUMBER', '').strip(),
                            'street': row.get('STREET', '').strip(),
                            'city': row.get('CITY', '').strip() or row.get('DISTRICT', '').strip(),
                            'district': row.get('DISTRICT', '').strip(),
                            'postcode': row.get('POSTCODE', '').strip(),
                            'country': country_name
                        }
                        
                        # Only include addresses with street and (house number or postcode)
                        if address['street'] and (address['housenumber'] or address['postcode']):
                            addresses.append(address)
        
        if verbose:
            print(f"   ✅ Extracted {len(addresses)} addresses")
        
        # Write to output CSV
        if verbose:
            print(f"   💾 Writing to {output_file}...")
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['housenumber', 'street', 'city', 'district', 'postcode', 'country'])
            writer.writeheader()
            writer.writerows(addresses)
        
        if verbose:
            print(f"✅ Successfully created {output_file} with {len(addresses)} addresses")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Download failed: {e}")
        return False
    except zipfile.BadZipFile:
        print(f"❌ Invalid ZIP file")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def query_overpass_for_addresses(country_name: str, city_name: Optional[str] = None, 
                                  output_file: str = None, limit: int = 1000, verbose: bool = True) -> List[Dict]:
    """
    Query Overpass API directly for addresses in a country/city.
    This is an alternative to downloading OpenAddresses.
    
    Args:
        country_name: Full country name
        city_name: Optional city name to filter (uses city bbox)
        output_file: Optional output CSV file
        limit: Maximum number of addresses to fetch
        verbose: Print progress
    
    Returns:
        List of address dictionaries
    """
    import geonamescache
    
    if verbose:
        print(f"🌍 Querying Overpass API for {country_name}...")
        if city_name:
            print(f"   City filter: {city_name}")
    
    # Get city bounding box from GeonamesCache
    gc = geonamescache.GeonamesCache()
    
    # Get cities for the country
    cities = gc.get_cities()
    country_cities = []
    
    # Find country code
    countries = gc.get_countries()
    country_code = None
    for code, data in countries.items():
        if data.get('name', '').lower() == country_name.lower():
            country_code = code
            break
    
    if not country_code:
        print(f"❌ Country '{country_name}' not found in GeonamesCache")
        return []
    
    # Find city bbox if city_name provided
    bbox = None
    if city_name:
        for city_id, city_data in cities.items():
            if (city_data.get('countrycode', '').upper() == country_code.upper() and
                city_name.lower() in city_data.get('name', '').lower()):
                lat = city_data.get('latitude', 0)
                lon = city_data.get('longitude', 0)
                # Create small bbox around city center (±0.1 degrees ≈ 11km)
                bbox = (lat - 0.1, lon - 0.1, lat + 0.1, lon + 0.1)
                if verbose:
                    print(f"   Found city: {city_data.get('name')} at ({lat:.4f}, {lon:.4f})")
                break
    
    # Overpass query for addresses
    overpass_url = "https://overpass-api.de/api/interpreter"
    
    # Build query using bbox
    # Overpass bbox format: (south, west, north, east)
    if bbox:
        min_lat, min_lon, max_lat, max_lon = bbox
        query = f"""[out:json][timeout:180];
node["addr:housenumber"]["addr:street"]({min_lat},{min_lon},{max_lat},{max_lon});
out body;
limit {limit};"""
    else:
        # For entire country, use major cities
        # Get top 5 cities by population
        country_cities_list = []
        for city_id, city_data in cities.items():
            if city_data.get('countrycode', '').upper() == country_code.upper():
                country_cities_list.append(city_data)
        
        # Sort by population (if available) or use first 5
        country_cities_list = sorted(country_cities_list, 
                                    key=lambda x: x.get('population', 0), 
                                    reverse=True)[:5]
        
        if verbose:
            print(f"   Querying {len(country_cities_list)} major cities...")
        
        # Query each city
        all_addresses = []
        for city_data in country_cities_list:
            lat = city_data.get('latitude', 0)
            lon = city_data.get('longitude', 0)
            city_bbox = (lat - 0.1, lon - 0.1, lat + 0.1, lon + 0.1)
            min_lat, min_lon, max_lat, max_lon = city_bbox
            
            query = f"""
[out:json][timeout:180];
(
  node["addr:housenumber"]["addr:street"]({min_lat},{min_lon},{max_lat},{max_lon});
);
out body;
limit {limit // len(country_cities_list)};
"""
    
    try:
        if verbose:
            print(f"   🔍 Querying Overpass API...")
        
        if bbox:
            # Single query for specific city
            response = requests.post(overpass_url, data={'data': query}, timeout=300)
            response.raise_for_status()
            
            data = response.json()
            elements = data.get('elements', [])
            
            if verbose:
                print(f"   ✅ Found {len(elements)} address nodes")
            
            addresses = []
            for element in elements:
                tags = element.get('tags', {})
                
                address = {
                    'housenumber': tags.get('addr:housenumber', '').strip(),
                    'street': tags.get('addr:street', '').strip(),
                    'city': tags.get('addr:city', '').strip() or tags.get('addr:place', '').strip() or city_name or '',
                    'district': tags.get('addr:district', '').strip() or tags.get('addr:suburb', '').strip(),
                    'postcode': tags.get('addr:postcode', '').strip(),
                    'country': country_name
                }
                
                if address['housenumber'] and address['street']:
                    addresses.append(address)
        else:
            # Multiple queries for major cities
            addresses = []
            for city_data in country_cities_list:
                lat = city_data.get('latitude', 0)
                lon = city_data.get('longitude', 0)
                city_bbox = (lat - 0.1, lon - 0.1, lat + 0.1, lon + 0.1)
                min_lat, min_lon, max_lat, max_lon = city_bbox
                
                city_query = f"""[out:json][timeout:180];
node["addr:housenumber"]["addr:street"]({min_lat},{min_lon},{max_lat},{max_lon});
out body;
limit {limit // len(country_cities_list)};"""
                try:
                    response = requests.post(overpass_url, data={'data': city_query}, timeout=300)
                    response.raise_for_status()
                    
                    data = response.json()
                    elements = data.get('elements', [])
                    
                    if verbose:
                        print(f"   ✅ {city_data.get('name')}: {len(elements)} nodes")
                    
                    for element in elements:
                        tags = element.get('tags', {})
                        
                        address = {
                            'housenumber': tags.get('addr:housenumber', '').strip(),
                            'street': tags.get('addr:street', '').strip(),
                            'city': tags.get('addr:city', '').strip() or tags.get('addr:place', '').strip() or city_data.get('name', ''),
                            'district': tags.get('addr:district', '').strip() or tags.get('addr:suburb', '').strip(),
                            'postcode': tags.get('addr:postcode', '').strip(),
                            'country': country_name
                        }
                        
                        if address['housenumber'] and address['street']:
                            addresses.append(address)
                    
                    time.sleep(1)  # Rate limit
                except Exception as e:
                    if verbose:
                        print(f"   ⚠️  Error querying {city_data.get('name')}: {e}")
                    continue
        
        if verbose:
            print(f"   ✅ Extracted {len(addresses)} valid addresses")
        
        # Write to CSV if requested
        if output_file:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['housenumber', 'street', 'city', 'district', 'postcode', 'country'])
                writer.writeheader()
                writer.writerows(addresses)
            
            if verbose:
                print(f"   💾 Saved to {output_file}")
        
        return addresses
        
    except Exception as e:
        print(f"❌ Overpass query failed: {e}")
        return []


def main():
    parser = argparse.ArgumentParser(description='Download address datasets from OpenAddresses or Overpass API')
    parser.add_argument('--country', required=True, help='Country name (e.g., "Poland", "Russia")')
    parser.add_argument('--output', required=True, help='Output CSV file path')
    parser.add_argument('--source', choices=['openaddresses', 'overpass'], default='openaddresses',
                       help='Data source: openaddresses or overpass')
    parser.add_argument('--city', help='City name (for Overpass only)')
    parser.add_argument('--limit', type=int, default=1000, help='Limit for Overpass queries')
    parser.add_argument('--verbose', action='store_true', default=True, help='Verbose output')
    
    args = parser.parse_args()
    
    if args.source == 'openaddresses':
        success = download_openaddresses_country(args.country, args.output, args.verbose)
        sys.exit(0 if success else 1)
    else:
        addresses = query_overpass_for_addresses(args.country, args.city, args.output, args.limit, args.verbose)
        sys.exit(0 if addresses else 1)


if __name__ == '__main__':
    main()

