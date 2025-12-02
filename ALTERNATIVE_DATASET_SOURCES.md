# Alternative Dataset Sources for Address Generation

Instead of using cached addresses, you can prepare datasets from multiple sources:

## 1. OpenAddresses (Recommended)

**Website:** https://openaddresses.io/  
**Data:** https://data.openaddresses.io/

### Advantages:
- ✅ Free and open
- ✅ Global coverage (200+ countries)
- ✅ Standardized format
- ✅ Regularly updated
- ✅ Large datasets (millions of addresses per country)

### Usage:
```bash
# Download Poland addresses
python download_openaddresses.py --country "Poland" --output poland_addresses.csv

# Download Russia addresses
python download_openaddresses.py --country "Russia" --output russia_addresses.csv
```

### Format:
- CSV files with columns: `LON,LAT,NUMBER,STREET,CITY,DISTRICT,REGION,POSTCODE,ID`
- Automatically converted to our format: `housenumber,street,city,district,postcode,country`

### Coverage:
- **Poland:** ~2.5M addresses
- **Russia:** ~15M addresses
- **United States:** ~200M addresses
- Many other countries available

---

## 2. Overpass API (OpenStreetMap Direct Query)

**API:** https://overpass-api.de/api/interpreter  
**Documentation:** https://wiki.openstreetmap.org/wiki/Overpass_API

### Advantages:
- ✅ Real-time data
- ✅ Most comprehensive (OSM has the most address data)
- ✅ Can filter by city, region, tags
- ✅ Free (but respect rate limits)

### Usage:
```bash
# Query entire country
python download_openaddresses.py --source overpass --country "Poland" --output poland_addresses.csv --limit 5000

# Query specific city
python download_openaddresses.py --source overpass --country "Russia" --city "Moscow" --output moscow_addresses.csv
```

### Query Types:
- **Nodes with house numbers:** `node["addr:housenumber"]["addr:street"]`
- **Buildings with addresses:** `way["building"]["addr:housenumber"]`
- **Filter by city:** `node["addr:city"~"Moscow",i]`

---

## 3. Country-Specific Government Datasets

Many countries publish open address datasets:

### Examples:
- **Poland:** https://www.geoportal.gov.pl/
- **United Kingdom:** https://www.ordnancesurvey.co.uk/
- **Netherlands:** https://www.pdok.nl/
- **Germany:** https://www.bkg.bund.de/

### Advantages:
- ✅ Official data
- ✅ High quality
- ✅ Complete coverage

### Disadvantages:
- ⚠️ Varies by country
- ⚠️ Different formats
- ⚠️ May require registration

---

## 4. Geonames + OSM Combination

Use Geonames for cities/regions, then query OSM for addresses in those areas.

### Advantages:
- ✅ Structured city data
- ✅ Can target specific regions
- ✅ Good for sparse countries

### Usage:
```python
import geonamescache

gc = geonamescache.GeonamesCache()
cities = gc.get_cities_by_country('PL')  # Poland

# Then query OSM for each city
for city in cities:
    addresses = query_overpass_for_city(city['name'])
```

---

## 5. Hybrid Approach (Recommended for Production)

Combine multiple sources for maximum coverage:

```python
# 1. Try OpenAddresses first (fastest, largest)
addresses = download_openaddresses('Poland')

# 2. If insufficient, query Overpass for specific cities
if len(addresses) < 1000:
    cities = get_major_cities('Poland')
    for city in cities:
        addresses.extend(query_overpass_for_city(city))

# 3. Pre-filter locally (no API calls)
filtered = pre_filter_addresses(addresses)

# 4. Validate sample with Nominatim
validated = validate_with_nominatim(filtered[:100])
```

---

## Comparison

| Source | Coverage | Speed | Quality | Ease of Use |
|--------|----------|-------|---------|-------------|
| **OpenAddresses** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Overpass API** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Government Data** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **Geonames + OSM** | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |

---

## Recommended Workflow

1. **Start with OpenAddresses** (if available for country)
   - Download country dataset
   - Pre-filter locally
   - Validate sample

2. **Supplement with Overpass** (if needed)
   - Query major cities
   - Target specific regions
   - Fill gaps

3. **Use static dataset strategy**
   - Pre-filter all addresses locally
   - Validate only a sample with API
   - Cache validated addresses

---

## Example: Getting 15 Valid Addresses for Russia

```bash
# Step 1: Download OpenAddresses dataset (if available)
python download_openaddresses.py --country "Russia" --output russia_oa.csv

# Step 2: If OpenAddresses doesn't have Russia, use Overpass
python download_openaddresses.py --source overpass --country "Russia" --city "Moscow" --output russia_moscow.csv --limit 5000

# Step 3: Use static dataset strategy
python generate_from_static_dataset.py --country "Russia" --count 15 --dataset russia_moscow.csv --sample-size 100
```

This approach gives you:
- **Large dataset** (1000s of addresses)
- **High success rate** (66-70% validation)
- **15+ validated addresses** easily

