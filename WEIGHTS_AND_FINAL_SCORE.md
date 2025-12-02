# How Weights Are Assigned and Final Score is Calculated

## Overview

This document explains:
1. How weights are assigned using randomness
2. How the final similarity score is calculated after testing all three algorithms

---

## Step 1: Weights Are Assigned Using Randomness

### The Process

**After algorithms are selected, weights are generated:**

```python
# Step 1: Select algorithms (uses some random numbers)
selected = random.sample(algorithms, k=3)
# Result: ['soundex', 'metaphone', 'nysiis']

# Step 2: Generate weights (uses MORE random numbers from same sequence)
weights = [random.random() for _ in selected]
# Result: [0.217263, 0.577492, 0.006431]

# Step 3: Normalize weights (so they sum to 1.0)
total = sum(weights)  # 0.801186
normalized = [w / total for w in weights]
# Result: [0.271177, 0.720796, 0.008027]
```

### Key Points

1. **Same random sequence**: After `random.sample()` uses some numbers, the next numbers in the sequence are used for weights
2. **Deterministic**: Same seed → same sequence → same weights
3. **Normalized**: Weights are normalized so they sum to 1.0

### Example

For "John" with seed 7858:
- Random numbers for weights: `[0.217263, 0.577492, 0.006431]`
- Normalized weights:
  - Soundex: 0.271177 (27.1%)
  - Metaphone: 0.720796 (72.1%)
  - NYSIIS: 0.008027 (0.8%)

**Note**: Metaphone has the highest weight (72.1%), so it contributes most to the score!

---

## Step 2: Testing Variation Against All Algorithms

### The Process

**Each algorithm is tested independently:**

```python
# Test Soundex
soundex_match = jellyfish.soundex("John") == jellyfish.soundex("Jon")
# "John" = J500, "Jon" = J500 → Match: True → Score: 1.0

# Test Metaphone
metaphone_match = jellyfish.metaphone("John") == jellyfish.metaphone("Jon")
# "John" = JN, "Jon" = JN → Match: True → Score: 1.0

# Test NYSIIS
nysiis_match = jellyfish.nysiis("John") == jellyfish.nysiis("Jon")
# "John" = JAN, "Jon" = JAN → Match: True → Score: 1.0
```

### Result

Each algorithm returns:
- **1.0** if they match
- **0.0** if they don't match

---

## Step 3: Calculate Final Similarity Score

### The Formula

```
Final Score = Σ(algorithm_match × weight)
```

**Where:**
- `algorithm_match` = 1.0 if algorithms match, 0.0 if they don't
- `weight` = normalized weight for that algorithm

### Example 1: "John" → "Jon" (All Match)

**Algorithm Results:**
- Soundex: ✅ Match → 1.0
- Metaphone: ✅ Match → 1.0
- NYSIIS: ✅ Match → 1.0

**Weights:**
- Soundex: 0.271177
- Metaphone: 0.720796
- NYSIIS: 0.008027

**Calculation:**
```
Final Score = (1.0 × 0.271177) + (1.0 × 0.720796) + (1.0 × 0.008027)
            = 0.271177 + 0.720796 + 0.008027
            = 1.000000
```

**Result: 1.0 (Perfect match!)**

---

### Example 2: "John" → "Jhon" (Some Match)

**Algorithm Results:**
- Soundex: ✅ Match → 1.0
- Metaphone: ❌ No Match → 0.0
- NYSIIS: ✅ Match → 1.0

**Weights:**
- Soundex: 0.271177
- Metaphone: 0.720796
- NYSIIS: 0.008027

**Calculation:**
```
Final Score = (1.0 × 0.271177) + (0.0 × 0.720796) + (1.0 × 0.008027)
            = 0.271177 + 0.000000 + 0.008027
            = 0.279204
```

**Result: 0.279204 (Medium similarity)**

**Note**: Even though 2 out of 3 algorithms match, the score is low because:
- Metaphone (which doesn't match) has the highest weight (72.1%)
- So its 0.0 contribution heavily reduces the score

---

## Visual Flow

```
Name: "John"
  ↓
Seed: hash("John") % 10000 = 7858
  ↓
random.seed(7858)
  ↓
Random Sequence: [0.960356, 0.662059, 0.244554, 0.217263, 0.577492, 0.006431, ...]
  ↓
Step 1: Use first 3 numbers for algorithm selection
  → random.sample() → ['soundex', 'metaphone', 'nysiis']
  ↓
Step 2: Use next 3 numbers for weights
  → [0.217263, 0.577492, 0.006431]
  → Normalized: [0.271177, 0.720796, 0.008027]
  ↓
Step 3: Test variation "Jon" against all algorithms
  → Soundex: Match (1.0)
  → Metaphone: Match (1.0)
  → NYSIIS: Match (1.0)
  ↓
Step 4: Calculate weighted sum
  → (1.0 × 0.271177) + (1.0 × 0.720796) + (1.0 × 0.008027)
  → = 1.000000
```

---

## Key Insights

1. **All 3 algorithms are always used** - The code selects `k=min(3, 3) = 3`

2. **Weights are random but deterministic** - Same seed → same weights

3. **Weights determine contribution** - Higher weight = more impact on final score

4. **Final score is weighted average** - Not simple average, but weighted by algorithm importance

5. **Order matters for weights** - The order algorithms are selected determines which weight they get

---

## Why This Matters

**For generating variations:**

- If an algorithm with high weight doesn't match → score drops significantly
- If an algorithm with low weight doesn't match → score drops slightly
- To get high score, variations must match algorithms with high weights

**Example:**
- If Metaphone (weight 0.72) doesn't match → lose 72% of score
- If NYSIIS (weight 0.008) doesn't match → lose only 0.8% of score

So it's more important to match algorithms with higher weights!

---

## Summary

1. ✅ **Weights are assigned** using random numbers from the seeded sequence
2. ✅ **All 3 algorithms are tested** independently (match = 1.0, no match = 0.0)
3. ✅ **Final score** = weighted sum of algorithm matches
4. ✅ **Higher weight** = more impact on final score
5. ✅ **Same seed** → same weights → predictable scores

