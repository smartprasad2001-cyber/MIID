# Validated Address Cache Generator

## Overview

This script generates addresses and validates each one using `rewards.py` functions to ensure they score exactly **1.0**. Only addresses that pass all checks and score 1.0 are accepted.

After generating 15 addresses for a country, it tests them all together using `_grade_address_variations` (like the validator does) to confirm they all score 1.0.

## Key Features

✅ **Two-Stage Validation:**
1. **Fast local validation** (heuristic + region) - no API calls
2. **API validation** - only for addresses that pass local checks

✅ **Saves to different location:** `validated_address_cache.json` (not `address_cache.json`)

✅ **Final validation test:** After generating 15 addresses, tests them all together with `_grade_address_variations` to confirm score 1.0

## Usage

### Generate for one country:
```bash
python3 generate_validated_address_cache.py --country "Poland" --count 15
```

### Generate for all countries:
```bash
python3 generate_validated_address_cache.py --count 15
```

## Speed Optimization

The script is optimized for speed:

1. **Local validation first** (heuristic + region) - < 1ms per address
2. **API validation only** for addresses that pass local checks
3. **90%+ reduction** in API calls (much faster!)

**Expected time:**
- Local validation: < 1ms per address
- API validation: 1 second per address (rate limit)
- If 90% fail local checks, only 10% need API calls
- **Result: 10x faster than validating everything with API**

## Output

The script saves to `validated_address_cache.json`:

```json
{
  "addresses": {
    "Poland": [
      "26, Siedlisko, Grabowiec, 22-425, Poland",
      "9, Sadków Duchowny, Belsk Duży, 05-622, Poland",
      ...
    ]
  },
  "metadata": {
    "Poland": {
      "count": 15,
      "generated_at": "2025-01-XX XX:XX:XX",
      "test_score": 1.0
    }
  }
}
```

## Validation Process

For each address:

1. ✅ **Heuristic check** (`looks_like_address`) - must have 30+ chars, 20+ letters, 2+ commas
2. ✅ **Region validation** (`validate_address_region`) - must match country/city
3. ✅ **API check** (`check_with_nominatim`) - must score 1.0 (area < 100 m²)

Only addresses that pass ALL three checks are accepted.

## Final Test

After generating 15 addresses, the script automatically tests them all together:

```python
# Format like validator expects
variations = {
    "Test Name": [
        ["Test Name", "1990-01-01", addr] for addr in addresses
    ]
}

# Test with _grade_address_variations
result = _grade_address_variations(
    variations=variations,
    seed_addresses=[country],
    ...
)

# Must score >= 0.99 to be saved
if result['overall_score'] >= 0.99:
    # Save to cache
else:
    # Don't save (validation failed)
```

## Comparison with Original Script

| Feature | `generate_address_cache.py` | `generate_validated_address_cache.py` |
|---------|---------------------------|--------------------------------------|
| **Location** | `address_cache.json` | `validated_address_cache.json` |
| **Validation** | Local + area check | Local + API check (score 1.0) |
| **Final Test** | No | Yes (tests all 15 together) |
| **Speed** | Fast | Slower (API calls) |
| **Guarantee** | Addresses pass local checks | Addresses score 1.0 in validator |

## Notes

- ⚠️ **Slower than original:** API validation takes ~1 second per address
- ✅ **More reliable:** All addresses guaranteed to score 1.0
- ✅ **Final test:** Confirms all 15 addresses score 1.0 together
- ✅ **Different cache:** Won't overwrite your existing `address_cache.json`

