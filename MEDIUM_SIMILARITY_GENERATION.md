# Medium Similarity Generation Strategy

## Overview

We can now generate **Medium similarity variations (0.6-0.8 range, targeting ~0.7)** by using the **known weights** for each seed/name and strategically finding variations where specific algorithms match/don't match.

## How It Works

### Step 1: Get Weights for the Name

For any name, we can calculate the exact weights using:
```python
selected_algorithms, weights = get_weights_for_name("John")
```

Example for "John":
- Metaphone: 36.5% (0.3646)
- Soundex: 31.1% (0.3111)
- NYSIIS: 32.4% (0.3243)

### Step 2: Calculate Target Score

To get a Medium score (~0.7), we need:
```
Score = (weight1 × match1) + (weight2 × match2) + (weight3 × match3)
```

Where `match` is 1.0 if algorithm matches, 0.0 if it doesn't.

### Step 3: Find Match Patterns

For "John" with weights [0.3646, 0.3111, 0.3243], to get ~0.6757:

**Pattern 1: Match Metaphone + Soundex, miss NYSIIS**
- Metaphone matches: 0.3646 ✓
- Soundex matches: 0.3111 ✓
- NYSIIS doesn't match: 0.0000 ✗
- **Total: 0.6757** (Medium!)

**Pattern 2: Match Soundex + NYSIIS, miss Metaphone**
- Metaphone doesn't match: 0.0000 ✗
- Soundex matches: 0.3111 ✓
- NYSIIS matches: 0.3243 ✓
- **Total: 0.6354** (Medium!)

### Step 4: Generate Variations

We generate candidate variations using:
1. Remove letters
2. Add vowels
3. Change vowels
4. Change consonants
5. Swap adjacent letters
6. Add common letters
7. Remove multiple letters

### Step 5: Test and Filter

For each candidate:
1. Test which algorithms match
2. Calculate score using weights
3. Keep if score is in 0.6-0.8 range

## Examples

### Example 1: "John"

**Weights:**
- Metaphone: 36.5%
- Soundex: 31.1%
- NYSIIS: 32.4%

**Medium Variations (score ~0.6757):**
- "Jown" → Metaphone ✓, Soundex ✓, NYSIIS ✗ = 0.6757
- "Joyn" → Metaphone ✓, Soundex ✓, NYSIIS ✗ = 0.6757
- "Johyn" → Metaphone ✓, Soundex ✓, NYSIIS ✗ = 0.6757

**Medium Variations (score ~0.6354):**
- "Jhon" → Metaphone ✗, Soundex ✓, NYSIIS ✓ = 0.6354
- "Jomn" → Metaphone ✗, Soundex ✓, NYSIIS ✓ = 0.6354
- "Johm" → Metaphone ✗, Soundex ✓, NYSIIS ✓ = 0.6354

### Example 2: "Christopher"

**Weights:**
- Soundex: 49.6% (highest!)
- NYSIIS: 27.1%
- Metaphone: 23.3%

**Medium Variations (score ~0.7293):**
- "Chrstopher" → NYSIIS ✗, Soundex ✓, Metaphone ✓ = 0.7293
- "Christpher" → NYSIIS ✗, Soundex ✓, Metaphone ✓ = 0.7293
- "Christophr" → NYSIIS ✗, Soundex ✓, Metaphone ✓ = 0.7293

## Key Insights

1. **Weights are deterministic** - Same name always has same weights
2. **We can predict scores** - By knowing which algorithms match
3. **Different names have different weights** - "John" vs "Christopher" have different distributions
4. **We can target specific scores** - By finding variations with the right match pattern

## Strategy for Different Weight Distributions

### If Soundex has highest weight (e.g., 50%):
- Match Soundex + one other algorithm → ~0.7-0.8
- Match only Soundex → ~0.5 (too low, not Medium)

### If weights are balanced (e.g., 33% each):
- Match any 2 algorithms → ~0.66 (Medium)
- Match all 3 → 1.0 (Light)

### If one weight is very low (e.g., 20%):
- Need to match the two higher-weighted algorithms
- Missing the low-weight one doesn't hurt much

## Usage

```python
from generate_medium_variations import find_medium_variations

# Generate 15 Medium variations for any word
variations = find_medium_variations("John", target_score=0.7, count=15, tolerance=0.1)

# Each variation is a tuple: (variation, score, match_pattern)
for var, score, pattern in variations:
    print(f"{var} → {score:.4f}")
    print(f"  Match pattern: {pattern}")
```

## Benefits

✅ **Predictable** - We know exactly which algorithms will be used and their weights
✅ **Targeted** - We can generate variations that hit specific score ranges
✅ **Efficient** - We test candidates and filter by score, not random guessing
✅ **Scalable** - Works for any word, any weight distribution

## Next Steps

1. **Integrate into smart generator** - Use this for Medium variations
2. **Extend to Far similarity** - Similar approach for 0.3-0.6 range
3. **Combine with Light generator** - Use both for complete distribution matching

