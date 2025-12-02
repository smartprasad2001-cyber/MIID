# DOB Generation Function

## Overview
The `generate_perfect_dob_variations()` function generates Date of Birth variations that cover **ALL 6 required categories** for maximum score (1.0).

## Required Categories (6 Total)

The validator requires at least one DOB variation in each of these categories:

1. **±1 day**: Date within 1 day of seed DOB
   - Example: Seed `1990-06-15` → `1990-06-14` or `1990-06-16`

2. **±3 days**: Date within 3 days of seed DOB
   - Example: Seed `1990-06-15` → `1990-06-12` or `1990-06-18`

3. **±30 days**: Date within 30 days of seed DOB
   - Example: Seed `1990-06-15` → `1990-05-16` or `1990-07-15`

4. **±90 days**: Date within 90 days of seed DOB
   - Example: Seed `1990-06-15` → `1990-03-17` or `1990-09-13`

5. **±365 days**: Date within 365 days of seed DOB
   - Example: Seed `1990-06-15` → `1989-06-15` or `1991-06-15`

6. **Year+Month only**: Format `YYYY-MM` (no day), must match year and month of seed
   - Example: Seed `1990-06-15` → `1990-06`

## Scoring

The validator calculates score as:
```
score = len(found_categories) / 6
```

- **Perfect score (1.0)**: All 6 categories covered
- **Partial score**: Some categories missing (e.g., 5/6 = 0.833)

## Function Usage

```python
from generate_and_test_variations import generate_perfect_dob_variations

seed_dob = "1990-06-15"
variation_count = 9

dob_variations = generate_perfect_dob_variations(seed_dob, variation_count)
# Returns: ['1990-06-14', '1990-06-12', '1990-05-16', '1990-03-17', 
#           '1989-06-15', '1990-06', '1990-06-16', '1990-06-18', '1990-07-15']
```

## Features

1. **Automatic format normalization**: Handles formats like `1985-3-13` → `1985-03-13`
2. **Guaranteed category coverage**: Always includes at least one variation from each category
3. **Flexible count**: Generates exactly the requested number of variations
4. **No duplicates**: All variations are unique

## Format Requirements

- **Full dates**: `YYYY-MM-DD` format (e.g., `1990-06-15`)
- **Year+Month**: `YYYY-MM` format (e.g., `1990-06`)
- **Input normalization**: Accepts formats like `1985-3-13` and normalizes to `1985-03-13`

## Example Output

For seed DOB `1990-06-15` with 9 variations:

```
1. 1990-06-14  (±1 day)
2. 1990-06-12  (±3 days)
3. 1990-05-16  (±30 days)
4. 1990-03-17  (±90 days)
5. 1989-06-15  (±365 days)
6. 1990-06     (Year+Month only)
7. 1990-06-16  (additional ±1 day)
8. 1990-06-18  (additional ±3 days)
9. 1990-07-15  (additional ±30 days)
```

**Result**: ✅ All 6 categories covered → Score: 1.0

