# How Algorithms Return Codes (Not 0!)

## Common Misconception

**❌ WRONG:** "Soundex gives 0 when a word is fed to it"

**✅ CORRECT:** Soundex returns a **CODE** (like "J500"), and the "0" comes from the **comparison** (match/no match)

## How It Actually Works

### Step 1: Algorithms Return Codes

Each algorithm converts a word into a **code**:

```python
import jellyfish

# Soundex returns a code
soundex("John") = "J500"    # Not 0!
soundex("Jon") = "J500"     # Not 0!
soundex("Jhon") = "J500"    # Not 0!

# Metaphone returns a code
metaphone("John") = "JN"    # Not 0!
metaphone("Jon") = "JN"     # Not 0!
metaphone("Jhon") = "JHN"   # Not 0!

# NYSIIS returns a code
nysiis("John") = "JAN"      # Not 0!
nysiis("Jon") = "JAN"       # Not 0!
nysiis("Jhon") = "JAN"      # Not 0!
```

### Step 2: Compare Codes

The validator compares codes to see if they match:

```python
original = "John"
variation = "Jhon"

# Get codes
soundex_orig = soundex(original)    # "J500"
soundex_var = soundex(variation)     # "J500"

# Compare
soundex_match = (soundex_orig == soundex_var)  # True (codes match!)
```

### Step 3: Convert Match to 1.0 or 0.0

The match (True/False) is converted to a number:

```python
# If codes match
match = 1.0  # Contributes weight

# If codes don't match
match = 0.0  # Contributes 0
```

### Step 4: Calculate Score

The score is calculated using the match value:

```python
score = (match1 × weight1) + (match2 × weight2) + (match3 × weight3)

# Example:
# Soundex: codes match → match = 1.0 → contributes 0.3
# Metaphone: codes don't match → match = 0.0 → contributes 0.0
# NYSIIS: codes match → match = 1.0 → contributes 0.3
# Score = 0.3 + 0.0 + 0.3 = 0.6
```

## Complete Example

### Original: "John"
- Soundex: "J500"
- Metaphone: "JN"
- NYSIIS: "JAN"

### Variation: "Jhon"
- Soundex: "J500" ✓ (matches!)
- Metaphone: "JHN" ✗ (doesn't match!)
- NYSIIS: "JAN" ✓ (matches!)

### Score Calculation

If weights are [0.3, 0.4, 0.3]:

```
Soundex:   1.0 × 0.3 = 0.3000  (codes match → match = 1.0)
Metaphone: 0.0 × 0.4 = 0.0000  (codes don't match → match = 0.0)
NYSIIS:    1.0 × 0.3 = 0.3000  (codes match → match = 1.0)
─────────────────────────────────────────────────────────
Total:                           0.6000
```

## Key Points

### 1. Algorithms Return Codes, Not 0

- **Soundex**: Returns codes like "J500", "S530", "M600"
- **Metaphone**: Returns codes like "JN", "SM0", "MR"
- **NYSIIS**: Returns codes like "JAN", "SNAT", "MAR"

### 2. The "0" Comes from Comparison

- If codes match → match = 1.0 → contributes weight
- If codes don't match → match = 0.0 → contributes 0

### 3. The Process

```
Word → Algorithm → Code → Compare → Match (1.0 or 0.0) → Score
```

**Example:**
```
"John" → Soundex → "J500" → Compare with "J500" → Match = 1.0 → Contributes weight
"Jhon" → Metaphone → "JHN" → Compare with "JN" → Match = 0.0 → Contributes 0
```

## Why This Matters

### For Medium Similarity

When generating Medium variations:
- We don't "shut down" algorithms
- We generate variations that naturally produce different codes
- Some codes match (contribute weight)
- Some codes don't match (contribute 0)
- Score = sum of weights for matching algorithms

### Example: "Jhon" from "John"

- Soundex: "J500" == "J500" → Match = 1.0 → Contributes 0.3
- Metaphone: "JN" != "JHN" → Match = 0.0 → Contributes 0.0
- NYSIIS: "JAN" == "JAN" → Match = 1.0 → Contributes 0.3
- **Score = 0.6 (Medium!)**

The Metaphone code doesn't match because:
- The letter swap (o↔h) changes the phonetic structure
- "John" → "JN"
- "Jhon" → "JHN"
- This is **natural** - we don't control it!

## Summary

1. ✅ **Algorithms return CODES** (like "J500", "JN", "JAN")
2. ✅ **Codes are compared** to see if they match
3. ✅ **Match = 1.0** if codes match, **0.0** if they don't
4. ✅ **Score = sum of (match × weight)** for each algorithm
5. ✅ **The "0" comes from match = 0.0** (codes don't match), NOT from the algorithm returning 0

**Soundex doesn't "give 0" - it gives a code, and the 0 comes from the comparison!**

