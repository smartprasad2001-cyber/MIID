# Strategy to Generate Addresses for 29 Incomplete Countries

## Current Situation

- **29 countries** have incomplete addresses (<15)
- **19 countries**: Disabled for reverse geocoding (polygon issues)
- **9 countries**: Reverse geocoding attempted but failed (0 addresses)
- **1 country**: Got addresses but they were duplicates (North Korea)

## Root Causes

### 1. Disabled Countries (19)
These are in `DISABLE_REVERSE_COUNTRIES` because:
- Reverse geocoding returns **large polygons (>100 m²)** that fail validation
- Examples: Afghanistan, Somalia, Yemen, Libya (conflict zones with poor OSM data)
- Micro-islands/territories (Monaco, Aruba, etc.) have limited OSM coverage

### 2. Failed Countries (9)
Reverse geocoding was attempted but:
- All addresses failed validation (score < 0.9, region mismatch, etc.)
- Limited OSM nodes in cities
- Poor data quality in Nominatim

### 3. Duplicate Issue (1)
- North Korea: Got 6 addresses but they already existed in main cache

## Proposed Strategies

### Strategy 1: Use Local Node Validation (Path A) for Disabled Countries

**For 19 disabled countries**, modify `generate_addresses_zero_countries.py` to:
- **Skip reverse geocoding** (as they're disabled)
- **Use local node validation** (build addresses from OSM node tags)
- This is the same approach as `generate_address_cache_priority.py` Path A

**Implementation:**
```python
# For disabled countries, use local node validation instead
if country in DISABLE_REVERSE_COUNTRIES:
    # Use Path A: Build address from node tags
    # Validate with API but don't use reverse geocoding
```

**Pros:**
- Works for countries where reverse geocoding fails
- Uses existing OSM node data
- Same validation as main script

**Cons:**
- Requires OSM nodes with complete address tags
- May not work for countries with poor OSM coverage

---

### Strategy 2: Process 0-Address Countries

**Modify script to process countries with 0 addresses:**
- Currently script skips countries with 0 addresses (line 360-361)
- Change condition to: `if 0 <= address_count < 15:`

**Implementation:**
```python
# Change from:
if 1 <= address_count < 15:

# To:
if 0 <= address_count < 15:
```

**Pros:**
- Can generate addresses for 15 countries with 0 addresses
- Uses same reverse geocoding approach

**Cons:**
- May fail for same reasons as before (validation issues)

---

### Strategy 3: Use DENSE_CITY_BBOXES for Problematic Countries

**For countries with known dense areas**, use pre-defined bounding boxes:
- Afghanistan already has: `[(34.5220, 69.1600, 34.5360, 69.1860)]` (Kabul center)
- Add more dense bboxes for other problematic countries

**Implementation:**
```python
# Check if country has dense bbox
if country in DENSE_CITY_BBOXES:
    bboxes = DENSE_CITY_BBOXES[country]
    # Use these bboxes instead of city-based bboxes
```

**Pros:**
- Targets known high-density areas
- More likely to find valid addresses

**Cons:**
- Requires manual research to find dense areas
- May not exist for all countries

---

### Strategy 4: Lower Score Threshold for Difficult Countries

**For countries that consistently fail**, temporarily lower score threshold:
- Current: `score >= 0.9`
- Try: `score >= 0.8` or `score >= 0.85` for difficult countries

**Implementation:**
```python
# Country-specific thresholds
DIFFICULT_COUNTRIES_THRESHOLD = {
    "Afghanistan": 0.8,
    "Somalia": 0.8,
    "Yemen": 0.8,
    # ... etc
}

threshold = DIFFICULT_COUNTRIES_THRESHOLD.get(country, 0.9)
if score < threshold:
    continue
```

**Pros:**
- May accept more addresses
- Still maintains quality (0.8 is reasonable)

**Cons:**
- Lower quality addresses
- May not pass validator's strict checks

---

### Strategy 5: Use Address Variation Generation

**For countries with at least 1 address**, use `generate_address_variations_from_cache.py`:
- Takes existing addresses
- Generates variations using patterns
- Validates each variation

**Implementation:**
- Run `generate_address_variations_from_cache.py` for countries with 1-14 addresses
- Target: Generate remaining addresses to reach 15

**Pros:**
- Works well for countries with existing addresses
- Uses proven variation patterns

**Cons:**
- Requires at least 1 valid address to start
- May not work for 0-address countries

---

### Strategy 6: Hybrid Approach - Try Multiple Methods

**For each country, try in order:**
1. **Local node validation** (if disabled or reverse geocoding fails)
2. **Reverse geocoding** (if enabled)
3. **Address variation generation** (if has existing addresses)
4. **Manual generation** (last resort)

**Implementation:**
```python
def generate_addresses_hybrid(country, needed):
    # Try method 1: Local nodes
    addresses = try_local_nodes(country, needed)
    if len(addresses) >= needed:
        return addresses
    
    # Try method 2: Reverse geocoding (if enabled)
    if country not in DISABLE_REVERSE_COUNTRIES:
        addresses.extend(try_reverse_geocoding(country, needed - len(addresses)))
        if len(addresses) >= needed:
            return addresses
    
    # Try method 3: Variations (if has existing)
    if has_existing_addresses(country):
        addresses.extend(try_variations(country, needed - len(addresses)))
    
    return addresses
```

---

## Recommended Implementation Plan

### Phase 1: Quick Wins (Modify Existing Script)

1. **Enable 0-address processing**
   - Change condition to process countries with 0 addresses
   - This will attempt to generate for 15 countries

2. **Add local node validation for disabled countries**
   - For countries in `DISABLE_REVERSE_COUNTRIES`, use Path A (local nodes)
   - Skip reverse geocoding, build from tags

### Phase 2: Enhanced Strategies

3. **Add DENSE_CITY_BBOXES**
   - Research and add dense bboxes for problematic countries
   - Focus on capital cities and major urban areas

4. **Lower threshold for difficult countries**
   - Create country-specific thresholds
   - Accept 0.8-0.85 for countries that consistently fail

### Phase 3: Alternative Methods

5. **Use address variation generation**
   - For countries with 1+ addresses, use variation script
   - Generate remaining addresses from existing patterns

6. **Manual generation**
   - For countries that still fail, manually generate addresses
   - Use patterns from successful countries

---

## Specific Recommendations by Country Group

### Group 1: Disabled Countries (19) - Use Local Nodes
- Afghanistan, Somalia, Yemen, Libya, etc.
- **Action**: Modify script to use local node validation (Path A)

### Group 2: Failed Countries (9) - Try Enhanced Methods
- Cabo Verde, Curacao, Guam, Macao, etc.
- **Action**: 
  - Try different cities
  - Use larger bbox radius
  - Lower score threshold to 0.85

### Group 3: 0-Address Countries (15) - Enable Processing
- Aruba, Brunei, Monaco, etc.
- **Action**: Modify script to process 0-address countries

### Group 4: Partial Countries (14) - Use Variations
- Countries with 1-13 addresses
- **Action**: Use `generate_address_variations_from_cache.py`

---

## Code Changes Needed

### Change 1: Enable 0-address processing
```python
# Line 360-361 in generate_addresses_zero_countries.py
# FROM:
if 1 <= address_count < 15:

# TO:
if 0 <= address_count < 15:
```

### Change 2: Add local node validation for disabled countries
```python
# Add new function to build addresses from node tags
# Similar to Path A in generate_address_cache_priority.py
```

### Change 3: Add country-specific thresholds
```python
DIFFICULT_COUNTRIES_THRESHOLD = {
    "Cabo Verde": 0.85,
    "Curacao": 0.85,
    # ... etc
}
```

---

## Expected Results

- **Phase 1**: Should complete 10-15 countries
- **Phase 2**: Should complete 5-10 more countries
- **Phase 3**: Remaining 4-9 countries may need manual generation

**Total target**: Complete all 29 countries to 15 addresses each.

