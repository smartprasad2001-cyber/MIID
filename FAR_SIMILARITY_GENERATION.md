# Far Similarity Generation Strategy

## Overview

We can now generate **Far similarity variations (0.3-0.6 range, targeting ~0.4-0.5)** by using the **known weights** for each seed/name and strategically finding variations where **few algorithms match** (typically 0-1 algorithms).

## How It Works

### Step 1: Get Weights for the Name

For any name, we can calculate the exact weights using:
```python
selected_algorithms, weights = get_weights_for_name("Christopher")
```

Example for "Christopher":
- Soundex: 41.2% (0.4125)
- Metaphone: 35.4% (0.3537)
- NYSIIS: 23.4% (0.2338)

### Step 2: Calculate Target Score

To get a Far score (~0.4-0.5), we need:
```
Score = (weight1 × match1) + (weight2 × match2) + (weight3 × match3)
```

Where `match` is 1.0 if algorithm matches, 0.0 if it doesn't.

### Step 3: Find Match Patterns for Far

For Far similarity, we want **fewer matches** (typically 0-1 algorithms):

**Pattern 1: Match only the highest-weighted algorithm**
- For "Christopher": Match Soundex (41.2%), miss others
- **Total: 0.4125** (Far!)

**Pattern 2: Match only one medium-weighted algorithm**
- For "Elizabeth": Match Soundex (41.1%), miss others
- **Total: 0.4115** (Far!)

**Pattern 3: Match two lower-weighted algorithms**
- If weights are balanced, matching two lower ones might give ~0.3-0.4

### Step 4: Generate Variations (More Aggressive)

For Far similarity, we use more aggressive modification strategies:
1. Remove letters (single and multiple)
2. Remove 2-3 letters
3. Change vowels aggressively
4. Change consonants
5. Swap non-adjacent letters
6. Add letters in middle (breaks phonetic codes)
7. Change multiple letters

### Step 5: Test and Filter

For each candidate:
1. Test which algorithms match
2. Calculate score using weights
3. Keep if score is in 0.3-0.6 range

## Examples

### Example 1: "Christopher"

**Weights:**
- Soundex: 41.2%
- Metaphone: 35.4%
- NYSIIS: 23.4%

**Far Variations (score ~0.4125):**
- "Christoher" → Only Soundex ✓ = 0.4125
- "Christoper" → Only Soundex ✓ = 0.4125
- "Christophe" → Only Soundex ✓ = 0.4125

**Pattern:** Match only Soundex (highest weight), miss others

### Example 2: "Elizabeth"

**Weights:**
- Soundex: 41.1%
- NYSIIS: 38.9%
- Metaphone: 19.9%

**Far Variations (score ~0.4115):**
- "Elizabeh" → Only Soundex ✓ = 0.4115
- "Elzabeh" → Only Soundex ✓ = 0.4115
- "Elizbet" → Only Soundex ✓ = 0.4115

**Pattern:** Match only Soundex (highest weight), miss others

### Example 3: "John" (Edge Case)

**Weights:**
- NYSIIS: 73.3% (very high!)
- Metaphone: 17.4%
- Soundex: 9.3%

**Problem:** 
- If NYSIIS matches: 0.733 (too high, not Far)
- If NYSIIS doesn't match: 0.174 + 0.093 = 0.267 (too low, below 0.3)

**Solution:** For names with one very high weight (>70%), it's mathematically difficult to get into 0.3-0.6 range. We can:
1. Accept variations slightly outside range (0.25-0.35 or 0.65-0.75)
2. Use more aggressive modifications to break all algorithms
3. Focus on other names with better weight distributions

## Key Insights

1. **Far = Fewer Matches** - Typically match 0-1 algorithms
2. **Match Highest Weight** - If matching one algorithm, match the highest-weighted one for best score
3. **More Aggressive Modifications** - Need bigger changes to break phonetic codes
4. **Weight Distribution Matters** - Some names are easier than others

## Strategy for Different Weight Distributions

### If one weight is very high (>70%):
- Hard to get into 0.3-0.6 range
- May need to accept slightly outside range
- Or use very aggressive modifications

### If weights are balanced (30-40% each):
- Match only one algorithm → ~0.3-0.4 (Far)
- Match two algorithms → ~0.6-0.8 (Medium)
- Easy to target Far range

### If one weight is very low (<15%):
- Match only that one → too low (<0.3)
- Need to match it with another low one
- Or match the higher-weighted ones

## Usage

```python
from generate_far_variations import find_far_variations

# Generate 15 Far variations for any word
variations = find_far_variations("Christopher", target_score=0.45, count=15, tolerance=0.15)

# Each variation is a tuple: (variation, score, match_pattern)
for var, score, pattern in variations:
    print(f"{var} → {score:.4f}")
    print(f"  Match pattern: {pattern}")
```

## Benefits

✅ **Predictable** - We know exactly which algorithms will be used and their weights
✅ **Targeted** - We can generate variations that hit specific score ranges
✅ **Efficient** - We test candidates and filter by score
✅ **Scalable** - Works for most words (some edge cases exist)

## Comparison: Light vs Medium vs Far

| Category | Score Range | Typical Matches | Strategy |
|----------|-------------|-----------------|----------|
| **Light** | 0.8-1.0 | All 3 algorithms | Match all codes |
| **Medium** | 0.6-0.8 | 2 algorithms | Match 2, miss 1 |
| **Far** | 0.3-0.6 | 0-1 algorithms | Match 0-1, miss others |

## Next Steps

1. **Integrate into smart generator** - Use this for Far variations
2. **Combine with Light and Medium** - Use all three for complete distribution matching
3. **Handle edge cases** - Improve handling of names with extreme weight distributions

