# Static Dataset Mining Strategy

## Overview

This strategy uses pre-existing geospatial datasets (like OpenAddresses) to generate high-scoring addresses (score 1.0) with minimal API calls.

## How It Works

### Step 1: Acquire Dataset
- Download OpenAddresses data for each country
- Or use a local CSV/JSON file with address records
- Required fields: `housenumber`, `street`, `city`, `postcode`, `country`

### Step 2: Pre-Filter Locally
- Construct address strings: `"[House Number] [Street], [City], [Postcode], [Country]"`
- Filter by structure:
  - Must have house number
  - Must have street name
  - Must have postal code (for high precision)
- Run `looks_like_address()` heuristic check
- Basic region validation

### Step 3: Limited API Validation
- Sample 50 pre-filtered addresses per country
- Validate each with Nominatim API:
  - `check_with_nominatim()` - Must score 1.0 (area < 100 m²)
  - `validate_address_region()` - Must match country
- Keep first 15 that pass all checks

## Advantages

✅ **No Rate Limits**: Heavy filtering done locally, only 50 API calls per country  
✅ **Guaranteed Specificity**: Addresses with house number + postal code = high precision  
✅ **Zero LLM Dependency**: Pure Python + standard libraries  
✅ **Scalable**: Process all 196 countries efficiently  

## Usage

### Basic Usage (Downloads from OpenAddresses)
```bash
python3 generate_from_static_dataset.py --country "Poland" --count 15
```

### With Local Dataset
```bash
python3 generate_from_static_dataset.py \
    --country "Poland" \
    --count 15 \
    --dataset "poland_addresses.csv"
```

### Custom Sample Size
```bash
python3 generate_from_static_dataset.py \
    --country "Poland" \
    --count 15 \
    --sample-size 100  # Validate 100 addresses instead of 50
```

## Dataset Format

Your local CSV file should have these columns:
- `housenumber` - House/building number
- `street` - Street name
- `city` - City name
- `postcode` - Postal/ZIP code
- `country` - Country name or ISO code

Example:
```csv
housenumber,street,city,postcode,country
26,Siedlisko,Grabowiec,22-425,Poland
9,Sadków Duchowny,Belsk Duży,05-622,Poland
```

## Output

The script generates a CSV file with validated addresses:
```csv
Country,Address,Nominatim_Score
Poland,"26, Siedlisko, Grabowiec, 22-425, Poland",1.0
Poland,"9, Sadków Duchowny, Belsk Duży, 05-622, Poland",1.0
```

## Workflow

1. **Download OpenAddresses data** (or use local dataset)
2. **Pre-filter locally** - Discard 90%+ of addresses without API calls
3. **Validate sample** - Only 50 API calls per country (vs thousands)
4. **Select final 15** - Addresses guaranteed to score 1.0

## Expected Results

- **Pre-filtering**: Reduces dataset from thousands to ~100-200 candidates
- **API Validation**: ~30-50% of candidates score 1.0
- **Final Output**: 15 addresses per country with score 1.0

## Notes

- OpenAddresses data availability varies by country
- Some countries may need local datasets
- Network connectivity required only for API validation step
- Total API calls: ~50 per country × 196 countries = ~9,800 calls (vs millions)

