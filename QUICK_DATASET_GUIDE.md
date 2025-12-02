# Quick Guide: Alternative Dataset Sources

## ✅ **Recommended: Use Existing Cache Generation**

The `generate_address_cache.py` script already uses Overpass API and works perfectly:

```bash
# Generate addresses for Russia (uses Overpass + Nominatim)
python3 generate_address_cache.py

# This will:
# 1. Query Overpass API for nodes with addr tags
# 2. Validate with Nominatim
# 3. Save to address_cache.json
```

**Advantages:**
- ✅ Already working
- ✅ Uses Overpass API (same as alternative)
- ✅ Validates with Nominatim
- ✅ Caches results
- ✅ Handles all countries

---

## Alternative: OpenAddresses (If Available)

**Website:** https://openaddresses.io/

### Download manually:
1. Visit: https://data.openaddresses.io/
2. Find country (e.g., "Poland" → `pl`)
3. Download ZIP: `https://data.openaddresses.io/runs/pl/latest.zip`
4. Extract CSV files
5. Convert to our format

### Convert OpenAddresses CSV:
```python
import csv

# OpenAddresses format: LON,LAT,NUMBER,STREET,CITY,DISTRICT,REGION,POSTCODE,ID
# Our format: housenumber,street,city,district,postcode,country

with open('openaddresses.csv', 'r') as f_in, open('our_format.csv', 'w') as f_out:
    reader = csv.DictReader(f_in)
    writer = csv.DictWriter(f_out, fieldnames=['housenumber','street','city','district','postcode','country'])
    writer.writeheader()
    
    for row in reader:
        writer.writerow({
            'housenumber': row['NUMBER'],
            'street': row['STREET'],
            'city': row['CITY'],
            'district': row['DISTRICT'],
            'postcode': row['POSTCODE'],
            'country': 'Poland'  # or your country
        })
```

---

## Alternative: Use Existing Cache

The `address_cache.json` already has addresses for many countries:

```python
import json

with open('address_cache.json', 'r') as f:
    cache = json.load(f)

# Get addresses for any country
russia_addresses = cache['addresses'].get('Russia', [])
poland_addresses = cache['addresses'].get('Poland', [])

# Export to CSV
import csv
with open('russia_from_cache.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['address'])
    for addr in russia_addresses:
        writer.writerow([addr])
```

---

## Best Approach for Russia

Since Russia addresses in cache might be limited, use:

1. **Generate more addresses:**
   ```bash
   # Edit generate_address_cache.py to focus on Russia
   # Or run it and let it complete all countries
   python3 generate_address_cache.py
   ```

2. **Use static dataset strategy:**
   ```bash
   # Export Russia addresses from cache to CSV
   python3 -c "
   import json, csv
   with open('address_cache.json') as f:
       cache = json.load(f)
   with open('russia.csv', 'w', encoding='utf-8') as f:
       writer = csv.writer(f)
       writer.writerow(['address'])
       for addr in cache['addresses'].get('Russia', []):
           writer.writerow([addr])
   "
   
   # Then use static dataset strategy
   python3 generate_from_static_dataset.py --country "Russia" --count 15 --dataset russia.csv
   ```

---

## Summary

**For maximum addresses:**
- Use `generate_address_cache.py` (already uses Overpass)
- It will generate 15 addresses per country
- Already handles Russia and all other countries

**For testing:**
- Export from `address_cache.json` to CSV
- Use `generate_from_static_dataset.py` to validate

**For production:**
- Pre-generate cache for all countries
- Use cache in miner for fast responses
