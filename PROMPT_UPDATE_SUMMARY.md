# Gemini Prompt Updates Based on Validator Scoring

## Summary

Updated the Gemini prompt to accurately reflect how the validator (`rewards.py`) actually scores miner output.

## Key Updates

### 1. ✅ Uniqueness Calculation (10% weight)
**Before**: Generic description
**After**: Exact validator logic
- Validator checks pairwise: `combined_similarity = (phonetic * 0.7) + (orthographic * 0.3)`
- If `combined_similarity > 0.99`, variations are considered duplicates
- `uniqueness_score = unique_count / total_count`
- If all variations identical → `uniqueness_score = 0` (loses 10% weight)

### 2. ✅ Length Calculation (15% weight)
**Before**: Simple 60-140% range
**After**: Exact validator formula
- Adaptive thresholds: `min_ratio = 0.6` if `len <= 5`, else `0.7`
- Validator calculates: `length_ratio = min(var_len / original_len, original_len / var_len)`
- Validator calculates: `length_score = length_ratio * (1.0 - min(1.0, absolute_diff / original_len))`
- Short names (≤5 chars) are more forgiving

### 3. ✅ Count Tolerance (15% weight)
**Before**: Generic "20-40% tolerance"
**After**: Exact adaptive tolerance formula
- `base_tolerance = 0.2` (20%)
- `tolerance = base_tolerance + (0.05 * (expected_count // 10))`
- Max tolerance = 0.4 (40%)
- Within tolerance = 1.0, outside = `exp(-deviation / expected_count)`

### 4. ✅ Phonetic Similarity (60% weight)
**Before**: Generic description
**After**: Exact algorithm details
- Validator uses randomized subset of: Soundex, Metaphone, NYSIIS
- Algorithm selection is deterministic per name (same algorithms used each time)
- Boundaries: Light (0.80-1.00), Medium (0.60-0.79), Far (0.30-0.59)

### 5. ✅ Orthographic Similarity (60% weight)
**Before**: Generic description
**After**: Exact formula
- Validator uses: `score = 1.0 - (distance / max_length)` where distance is Levenshtein
- Boundaries: Light (0.70-1.00), Medium (0.50-0.69), Far (0.20-0.49)
- Distribution matching: Validator counts variations in each range

## Impact

The prompt now provides Gemini with:
1. **Exact scoring formulas** - No guessing about how validator calculates scores
2. **Precise boundaries** - Knows exact similarity ranges for each category
3. **Adaptive thresholds** - Understands how tolerance changes with count
4. **Pairwise uniqueness** - Knows how validator checks for duplicate variations
5. **Algorithm details** - Understands which phonetic algorithms are used

## Expected Results

- Better distribution matching for similarity scores
- More accurate variation counts
- Improved uniqueness (fewer identical variations)
- Better length compliance
- Higher overall scores

## Status

✅ **All updates applied** - Prompt now matches validator's exact scoring mechanism

