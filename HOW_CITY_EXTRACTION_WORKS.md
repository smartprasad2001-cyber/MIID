# How City Extraction Works in `extract_city_country()`

## Overview

The `extract_city_country()` function extracts city and country from an address by:
1. **Splitting by commas** to get address parts
2. **Country** = last part (or last 2 parts for two-part countries)
3. **City** = found by checking parts from right to left, validating against geonames database

## Step-by-Step Process

### Step 1: Split Address by Commas

```python
address = "123 Main Street, Manhattan, New York, 10001, United States of America"
parts = address.split(",")
# Result: ["123 Main Street", "Manhattan", "New York", "10001", "United States of America"]
```

### Step 2: Extract Country (Always Last Part)

```python
last_part = parts[-1]  # "United States of America"
normalized_country = COUNTRY_MAPPING.get(last_part, last_part)
# Result: country = "united states" (normalized)
```

### Step 3: Find City (Right to Left, Excluding Country)

The function checks each part from **right to left** (excluding the country):

```python
# Exclude last 1 part (country)
# Check parts: "10001", "New York", "Manhattan", "123 Main Street"

for i in range(2, len(parts) + 1):  # Start from index -2 (second from last)
    candidate_part = parts[-i]  # Get part from right to left
    # Try to find a valid city in this part
```

### Step 4: Try Word Combinations

For each candidate part, it tries different word combinations:

```python
# Example: candidate_part = "New York"
words = ["New", "York"]

# Try combinations:
# 1. "York" (single word)
# 2. "New York" (two words)
```

### Step 5: Validate Against Geonames Database

For each candidate, it checks if it's a **real city** in the country:

```python
if city_in_country(city_candidate, country_checking_name):
    return city_candidate, normalized_country
```

The `city_in_country()` function:
- Checks geonames database
- Verifies the city exists in the specified country
- Returns `True` if valid, `False` otherwise

## Examples

### Example 1: Simple Address

**Address:** `"123 Main Street, Manhattan, New York, 10001, United States of America"`

**Process:**
1. Split: `["123 Main Street", "Manhattan", "New York", "10001", "United States of America"]`
2. Country: `"united states"` (from last part)
3. Check parts from right to left:
   - `"10001"` → Has numbers, skip
   - `"New York"` → Try "York" → ✅ Valid city in USA → Return `("york", "united states")`

**Result:** `("york", "united states")`

### Example 2: Address with City Name

**Address:** `"115 New Cavendish Street, London W1T 5DU, United Kingdom"`

**Process:**
1. Split: `["115 New Cavendish Street", "London W1T 5DU", "United Kingdom"]`
2. Country: `"united kingdom"`
3. Check parts from right to left:
   - `"London W1T 5DU"` → Try "London" → ✅ Valid city in UK → Return `("london", "united kingdom")`

**Result:** `("london", "united kingdom")`

### Example 3: Two-Word City

**Address:** `"3 Upper Alma Road, Rosebank, Cape Town, 7700, South Africa"`

**Process:**
1. Split: `["3 Upper Alma Road", "Rosebank", "Cape Town", "7700", "South Africa"]`
2. Country: `"south africa"`
3. Check parts from right to left:
   - `"7700"` → Has numbers, skip
   - `"Cape Town"` → Try "Town" → ❌ Not valid city
   - `"Cape Town"` → Try "Cape Town" → ✅ Valid city in South Africa → Return `("cape town", "south africa")`

**Result:** `("cape town", "south africa")`

### Example 4: Why "New York" Becomes "York"

**Address:** `"123 Main Street, Manhattan, New York, 10001, United States of America"`

**Process:**
1. Split: `["123 Main Street", "Manhattan", "New York", "10001", "United States of America"]`
2. Country: `"united states"`
3. Check `"New York"`:
   - Words: `["New", "York"]`
   - Try "York" first → ✅ Valid city in USA → **Returns immediately**
   - Never tries "New York" because "York" already matched!

**Result:** `("york", "united states")` ⚠️ **Not "new york"!**

## Why This Matters for Region Validation Bug

When the validator sends seed address `"New York, USA"`:

1. **Your generated address:** `"123 Main Street, Manhattan, New York, 10001, United States of America"`
   - Extracts: `city="york"`, `country="united states"`

2. **Seed address:** `"New York, USA"`
   - Should extract: `city="york"`, `country="united states"`
   - But bug compares: `"york" == "new york, usa"` → False ❌

3. **The bug:** It doesn't extract from seed, just uses entire string `"new york, usa"`

## Key Points

1. **Country is always last part** (or last 2 parts for two-part countries)
2. **City is found right-to-left** (excluding country)
3. **Validates against geonames** to ensure it's a real city
4. **Tries single words first**, then two-word combinations
5. **Stops at first match** (doesn't try all combinations)
6. **Skips parts with numbers** (like zip codes)

## Why "New York" Extracts as "York"

The function tries word combinations in order:
- First tries single words: `"York"` → ✅ Matches → Returns immediately
- Never tries `"New York"` because it already found a match

This is why `"New York"` becomes `"york"` in the extraction!

