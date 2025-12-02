# How Names and DOBs are Calculated in unified_generator.py

## Overview

The `unified_generator.py` uses **algorithmic generation** (NOT Gemini) for both names and DOBs. It's completely deterministic and based on phonetic similarity algorithms and date arithmetic.

---

## 🔤 NAME GENERATION

### Process Flow:

1. **Split Full Name**: 
   - Splits "John Smith" → first_name="John", last_name="Smith"

2. **Generate Variations Separately**:
   - Generates Light/Medium/Far variations for **first name** separately
   - Generates Light/Medium/Far variations for **last name** separately
   - Then combines them: `first_variation + " " + last_variation`

3. **Three Similarity Levels**:

#### **Light Variations** (High similarity, score ~1.0)
- Uses **phonetic algorithms** to find perfect matches:
  - `soundex()` - Soundex algorithm
  - `metaphone()` - Metaphone algorithm  
  - `nysiis()` - NYSIIS algorithm
- **Requirement**: ALL three algorithms must match the original
- **Example**: "John" → "Jon", "Jhon" (all algorithms produce same code)

#### **Medium Variations** (Medium similarity, score 0.6-0.79)
- Uses `calculate_phonetic_similarity()` from `rewards.py`
- **Requirement**: Score must be in range 0.6-0.79
- Generates candidates recursively and filters by score

#### **Far Variations** (Low similarity, score 0.3-0.59)
- Uses `calculate_phonetic_similarity()` from `rewards.py`
- **Requirement**: Score must be in range 0.3-0.59
- Generates candidates recursively and filters by score

### Candidate Generation (`generate_candidates()`)

Uses **50+ strategies** to generate candidate variations recursively:

1. Remove single letters
2. Add vowels at different positions
3. Change vowels
4. Change consonants (similar-sounding)
5. Swap adjacent letters
6. Swap non-adjacent letters
7. Add letters at all positions
8. Remove multiple letters (2, 3, 4, 5, 6 letters)
9. Double letters
10. Insert vowel combinations
11. Insert letter pairs
12. Replace with phonetic equivalents
13. ... and 40+ more strategies

**Recursive Depth**: Up to 6-7 levels deep (generates variations of variations)

**Example Flow**:
```
"John" 
  → Remove 'h': "Jon" (test if matches Light/Medium/Far)
  → Add 'a': "Johan" (test if matches)
  → Change 'o' to 'a': "Jahn" (test if matches)
  → ... continues recursively
```

---

## 📅 DOB GENERATION

### Process: `generate_perfect_dob_variations()`

**Uses simple date arithmetic** (NOT Gemini, NOT random)

### Required Categories (6 total):

1. **±1 day**: `seed_date ± 1 day`
2. **±3 days**: `seed_date ± 3 days`
3. **±30 days**: `seed_date ± 30 days`
4. **±90 days**: `seed_date ± 90 days`
5. **±365 days**: `seed_date ± 365 days`
6. **Year+Month only**: `YYYY-MM` format (no day)

### Algorithm:

```python
seed_dob = "1990-01-15"
seed_date = datetime.strptime(seed_dob, "%Y-%m-%d")

# Category 1: ±1 day
var1 = seed_date + timedelta(days=-1)  # "1990-01-14"
var2 = seed_date + timedelta(days=1)   # "1990-01-16"

# Category 2: ±3 days
var3 = seed_date + timedelta(days=-3)  # "1990-01-12"
var4 = seed_date + timedelta(days=3)   # "1990-01-18"

# ... and so on for all 6 categories

# Category 6: Year+Month only
var6 = seed_date.strftime("%Y-%m")     # "1990-01"
```

### Example Output:

For seed `"1990-01-15"`:
```
1. 1990-01-14  (±1 day)
2. 1990-01-16  (±1 day)
3. 1990-01-12  (±3 days)
4. 1990-01-18  (±3 days)
5. 1989-12-16  (±30 days)
6. 1990-02-14  (±30 days)
7. 1989-10-17  (±90 days)
8. 1990-04-15  (±90 days)
9. 1989-01-15  (±365 days)
10. 1991-01-15 (±365 days)
11. 1990-01    (Year+Month only)
```

---

## 🔄 Key Differences from test_complete_scoring.py

| Feature | unified_generator.py | test_complete_scoring.py |
|---------|---------------------|-------------------------|
| **Names** | Algorithmic (phonetic matching) | Gemini API |
| **DOBs** | Date arithmetic (6 categories) | Simple date math (±1-5 days) |
| **Speed** | Fast (no API calls) | Slow (API calls) |
| **Quality** | High (targets specific score ranges) | Variable (depends on Gemini) |
| **Deterministic** | Yes (same input = same output) | No (LLM randomness) |

---

## 📊 Why Scores Might Be Low

### Names:
- **Light variations** require ALL 3 phonetic algorithms to match (very strict)
- **Medium/Far variations** must fall in exact score ranges (0.6-0.79 or 0.3-0.59)
- If not enough candidates found, returns fewer variations → lower count score

### DOBs:
- Must cover all 6 categories for maximum score
- If `variation_count < 6`, some categories might be missing
- Year+Month format is critical (must be included)

---

## 🎯 Recommendations

1. **For Names**: The algorithmic approach is actually better than Gemini for scoring because it targets exact similarity ranges
2. **For DOBs**: The 6-category approach is correct and should score well
3. **If scores are low**: Check if enough variations are being generated (count vs. expected)

