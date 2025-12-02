# How Similarity is Scored Based on Light/Medium/Far Distribution

## Overview

The similarity score is **NOT** just the average of individual phonetic similarities. Instead, it's based on how well your variations match the **target distribution** of Light/Medium/Far categories.

---

## Step-by-Step Process

### Step 1: Calculate Individual Phonetic Similarity

For each variation, calculate its phonetic similarity to the original name (0.0-1.0).

**Example:**
- Original: "John Smith"
- Variation: "Jon Smith" → Similarity: **1.0000**
- Variation: "John Smyth" → Similarity: **0.6844**
- Variation: "John Smt" → Similarity: **0.3083**

### Step 2: Categorize into Light/Medium/Far

Each variation is categorized based on its similarity score:

| Category | Score Range | Description |
|----------|-------------|-------------|
| **Light** | 0.8 - 1.0 | High similarity (sounds very similar) |
| **Medium** | 0.6 - 0.8 | Moderate similarity (sounds somewhat similar) |
| **Far** | 0.3 - 0.6 | Low similarity (sounds different but related) |
| **Too Low** | < 0.3 | Penalized (sounds too different) |

**Example:**
- "Jon Smith" (1.0000) → **Light**
- "John Smyth" (0.6844) → **Medium**
- "John Smt" (0.3083) → **Far**

### Step 3: Count Distribution

Count how many variations fall into each category.

**Example with 8 variations:**
```
Actual Distribution:
  Light:   2/8 variations
  Medium:  4/8 variations
  Far:     2/8 variations
```

### Step 4: Compare Against Target Distribution

The query template specifies the target distribution (e.g., "20% Light, 60% Medium, 20% Far").

**Example:**
```
Target Distribution (for 8 variations):
  Light:   1-2 variations (20% of 8)
  Medium:  4-5 variations (60% of 8)
  Far:     1-2 variations (20% of 8)
```

### Step 5: Calculate Match Quality for Each Category

For each category, calculate how well the actual count matches the target:

```
Match Quality = actual_count / target_count
```

**Special Rules:**
- If `match_ratio ≤ 1.0`: Quality = match_ratio (linear)
- If `match_ratio > 1.0`: Quality = 1.0 - e^(-(match_ratio - 1.0)) (diminishing returns)

**Example:**
```
Light Category:
  Actual: 2, Target: 1
  Match Ratio: 2/1 = 2.00
  Match Quality: 0.6321 (diminishing returns because we exceeded target)

Medium Category:
  Actual: 4, Target: 4
  Match Ratio: 4/4 = 1.00
  Match Quality: 1.0000 (perfect match!)

Far Category:
  Actual: 2, Target: 1
  Match Ratio: 2/1 = 2.00
  Match Quality: 0.6321 (diminishing returns)
```

### Step 6: Calculate Weighted Similarity Score

Multiply each category's match quality by its target percentage and sum:

```
Similarity Score = (Light% × Light_Match) + (Medium% × Medium_Match) + (Far% × Far_Match)
```

**Example:**
```
Similarity Score = (0.20 × 0.6321) + (0.60 × 1.0000) + (0.20 × 0.6321)
                 = 0.1264 + 0.6000 + 0.1264
                 = 0.8528
```

### Step 7: Apply Penalties

If any variations fall outside the Light/Medium/Far ranges (< 0.3), apply a penalty:

```
Penalty = 0.1 × (unmatched_count / total_count)
Final Score = max(0.0, similarity_score - penalty)
```

---

## Complete Example

### Scenario: 8 Variations for "John Smith"

**Target Distribution:** 20% Light, 60% Medium, 20% Far

**Variations and Their Scores:**
1. "Jon Smith" → 1.0000 (Light)
2. "John Smithe" → 1.0000 (Light)
3. "John Smyth" → 0.6844 (Medium)
4. "John Smitt" → 0.6240 (Medium)
5. "John Smit" → 0.6240 (Medium)
6. "Jon Smyth" → 0.6844 (Medium)
7. "John Smt" → 0.3083 (Far)
8. "John Smi" → 0.3083 (Far)

**Distribution:**
- Light: 2/8 (target: 1-2) → Match Quality: 0.6321
- Medium: 4/8 (target: 4-5) → Match Quality: 1.0000
- Far: 2/8 (target: 1-2) → Match Quality: 0.6321

**Final Similarity Score:**
```
0.20 × 0.6321 + 0.60 × 1.0000 + 0.20 × 0.6321 = 0.8528
```

---

## What Happens with Wrong Distribution?

### Example: All 8 Variations are Light

**Variations:**
- All 8 are "John Smith" or "Jon Smith" (all Light)

**Distribution:**
- Light: 8/8 (target: 1-2) → Match Quality: 0.9991 (but only 20% weight!)
- Medium: 0/8 (target: 4-5) → Match Quality: 0.0000
- Far: 0/8 (target: 1-2) → Match Quality: 0.0000

**Final Similarity Score:**
```
0.20 × 0.9991 + 0.60 × 0.0000 + 0.20 × 0.0000 = 0.1998
```

**Result:** Very low score (≈0.20) because distribution doesn't match!

---

## Key Takeaways

1. **Similarity score is based on distribution matching**, not just individual similarity scores.

2. **You MUST match the target distribution** (e.g., 20% Light, 60% Medium, 20% Far).

3. **Perfect match = high score**: If you have exactly the right distribution, you get a high similarity score (0.8-1.0).

4. **Wrong distribution = low score**: If all variations are Light, you get a very low score (≈0.2) even though individual similarities are high.

5. **Medium category is most important**: It usually has the highest weight (60%), so getting Medium right is crucial.

6. **Exceeding target has diminishing returns**: Having 2x the target Light variations doesn't give 2x the score.

---

## Formula Summary

```
For each category (Light, Medium, Far):
  match_ratio = actual_count / target_count
  if match_ratio ≤ 1.0:
    match_quality = match_ratio
  else:
    match_quality = 1.0 - e^(-(match_ratio - 1.0))

similarity_score = (Light% × Light_quality) + (Medium% × Medium_quality) + (Far% × Far_quality)

if unmatched_variations > 0:
  penalty = 0.1 × (unmatched / total)
  similarity_score = max(0.0, similarity_score - penalty)
```

---

## Impact on Final Score

The similarity score is used in the base score calculation:

```
Base Score = (0.60 × similarity) + (0.15 × count) + (0.10 × uniqueness) + (0.15 × length)
```

Since similarity has a **60% weight**, getting the distribution right is critical for a high overall score!

