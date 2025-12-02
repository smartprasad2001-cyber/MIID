# How Orthographic Similarity is Calculated

## Formula

```python
def calculate_orthographic_similarity(original_name: str, variation: str) -> float:
    distance = Levenshtein.distance(original_name, variation)
    max_len = max(len(original_name), len(variation))
    score = 1.0 - (distance / max_len)
    return score
```

## Step-by-Step

1. **Calculate Levenshtein Distance**: Number of single-character edits (insertions, deletions, substitutions) needed to transform one string into another.

2. **Get Maximum Length**: `max(len(original), len(variation))`

3. **Calculate Score**: `1.0 - (distance / max_len)`

## Examples

| Original | Variation | Distance | Max Len | Score | Calculation |
|----------|-----------|----------|---------|-------|--------------|
| "John" | "Jon" | 1 | 4 | 0.7500 | 1 - 1/4 = 0.75 |
| "John" | "Jhn" | 1 | 4 | 0.7500 | 1 - 1/4 = 0.75 |
| "John" | "Johan" | 1 | 5 | 0.8000 | 1 - 1/5 = 0.80 |
| "Smith" | "Smaith" | 1 | 6 | 0.8333 | 1 - 1/6 = 0.83 |
| "Rodriguez" | "Rodriguez" | 0 | 9 | 1.0000 | 1 - 0/9 = 1.00 |
| "Rodriguez" | "Rodrigue" | 1 | 9 | 0.8889 | 1 - 1/9 = 0.89 |
| "Rodriguez" | "Rodrigu" | 2 | 9 | 0.7778 | 1 - 2/9 = 0.78 |
| "Christopher" | "Chraistopher" | 1 | 12 | 0.9167 | 1 - 1/12 = 0.92 |

## Score Ranges (Boundaries)

The validator uses these ranges to categorize variations:

- **Light**: 0.70 - 1.00 (High similarity)
- **Medium**: 0.50 - 0.69 (Moderate similarity)
- **Far**: 0.20 - 0.49 (Low similarity)

## Why Scores Are Low

### Problem: Distribution Mismatch

Even though **individual orthographic scores are high** (0.75-0.83), the **aggregated score is low** (0.1963) because:

1. **All variations fall in Light range** (0.70-1.00)
2. **Target distribution requires**:
   - 20% Light (0.70-1.00)
   - 60% Medium (0.50-0.69)
   - 20% Far (0.20-0.49)

3. **Result**: 100% in Light vs 20% target = **huge mismatch**

4. **Distribution quality calculation** penalizes this mismatch:
   ```python
   # If target is 20% Light but we have 100% Light:
   match_ratio = 100% / 20% = 5.0 (way too many!)
   match_quality = 1.0 - exp(-(5.0 - 1.0)) ≈ 0.02 (very low)
   quality = 0.20 * 0.02 = 0.004 (almost zero)
   ```

## The Real Issue

The unified generator creates variations that are **too similar orthographically**:
- Most variations: 1-2 character differences
- Scores: 0.75-0.83 (all in Light range)
- Need variations with: 3-5 character differences for Medium, 5+ for Far

## Solution

To get better orthographic scores, the generator needs to create variations with:
- **Medium range (0.50-0.69)**: 3-4 character differences for 9-char names
- **Far range (0.20-0.49)**: 5+ character differences for 9-char names

**Example for "Rodriguez" (9 chars):**
- Light (0.70-1.00): 0-2 char differences → "Rodriguez", "Rodrigue", "Rodrigu"
- Medium (0.50-0.69): 3-4 char differences → "Rodrig", "Rodrigz", "Rodrige"
- Far (0.20-0.49): 5+ char differences → "Rodri", "Rodrigu", "Rodrig"

## Current Behavior

The unified generator prioritizes **phonetic similarity** (which is high), but doesn't control **orthographic similarity** ranges, so all variations end up in the Light range.

