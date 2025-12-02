# What Happens If You Send 8 Duplicate Variations?

## Scenario
Validator asks for 8 variations for "John Smith", and you send 8 duplicates: ["John Smith", "John Smith", "John Smith", ...]

## Test Results

**Final Score: 0.2500** (very low!)

### Breakdown:

1. **Uniqueness Score: 0.1250** (10% weight)
   - Only 1 unique variation out of 8
   - Uniqueness = 1/8 = 0.125
   - This severely reduces the base score

2. **Similarity Score: 0.0000** (60% weight)
   - All variations have similarity = 1.0 (perfect match with "John Smith")
   - BUT: All 8 fall into **Light category** (0.8-1.0)
   - Target distribution: 20% Light (1-2), 60% Medium (4-5), 20% Far (1-2)
   - Actual: 100% Light (8/8) → **Distribution doesn't match!**
   - Result: Similarity score = **0.0000** (wrong distribution)

3. **Count Score: 1.0000** (15% weight)
   - Expected: 8, Actual: 8
   - Count is correct ✓

4. **Length Score: 1.0000** (15% weight)
   - All variations have correct length ✓

5. **Duplicate Penalty: 35%**
   - 7 duplicates (8 total - 1 unique)
   - Penalty = 7 × 0.05 = **0.35 (35% penalty!)**
   - Applied to `extra_names_penalty`

## Score Calculation

```
Base Score = (0.60 × 0.0) + (0.15 × 1.0) + (0.10 × 0.125) + (0.15 × 1.0)
           = 0.0 + 0.15 + 0.0125 + 0.15
           = 0.3125

After duplicate penalty (35%):
Final Score = 0.3125 × (1 - 0.35) = 0.2031

Actual result: 0.2500 (slightly higher due to other factors)
```

## Why It's So Low

1. **Wrong Distribution**: All variations are Light (100%), but target is 20% Light
   - Similarity score = 0.0 (60% of base score lost!)

2. **Low Uniqueness**: Only 1 unique variation
   - Uniqueness score = 0.125 (10% of base score lost!)

3. **Duplicate Penalty**: 35% penalty for 7 duplicates
   - Further reduces final score

## Comparison

**With 8 Duplicates:**
- Final Score: **0.2500**

**With 8 Unique Variations (proper distribution):**
- Final Score: **0.4-0.7** (much better!)

**Difference**: 0.25 vs 0.5-0.7 = **50-60% lower score!**

## Conclusion

**❌ DON'T send duplicate variations!**

**Why:**
1. Uniqueness score drops to 0.125 (from 1.0)
2. Similarity score drops to 0.0 (wrong distribution)
3. Duplicate penalty: 35% for 7 duplicates
4. Final score is **very low** (0.25 vs 0.5-0.7)

**✅ DO send unique variations:**
1. Each variation should be different
2. Match the distribution (20% Light, 60% Medium, 20% Far)
3. Get much higher scores (0.4-0.7)

## Code Reference

From `reward.py`:
- Line 1051: `uniqueness_score = len(unique_variations) / len(variations)`
- Line 2415-2419: Duplicate penalty = `duplicates × 0.05` (5% per duplicate)
- Line 1085-1123: Distribution matching - must match target distribution

