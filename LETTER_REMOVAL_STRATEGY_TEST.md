# Letter Removal Strategy Test Results

## Key Finding: Validator Scores FIRST and LAST Names SEPARATELY!

The validator calculates phonetic similarity for **first name** and **last name** separately, then combines them. This means you need to vary **BOTH** parts to get the right distribution!

---

## Test Results

### Strategy: Remove Letters from Last Name Only

**Variations Tested:**
- "Jon Smith" (remove 'h' from first name)
- "John Smithe" (add 'e' to last name)
- "John Smit" (remove 1 from end)
- "John Smth" (remove 'i' from middle)
- "John Smyth" (change 'i' to 'y')
- "John Smitt" (add 't' to end)
- "John Smih" (remove 't' from middle)
- "John Smi" (remove 2 from end)

**Problem:**
- **First Name Distribution**: All 8 are "John" or "Jon" → **100% Light** (target: 20% Light, 60% Medium, 20% Far)
- **Last Name Distribution**: Some are 0.0000 ("Smih", "Smi") → **Too Low**, penalized

**Result**: Similarity Score = **0.0000** ❌

---

## Working Patterns Found

### For LAST NAME Only:

| Category | Pattern | Example | Score Range |
|----------|---------|---------|-------------|
| **Light** | Remove 0 letters | "Smith" | 1.0000 |
| **Light** | Add letter to end | "Smithe" | 1.0000 |
| **Medium** | Remove 1 from end | "Smit" | 0.58-0.75 |
| **Medium** | Remove 1 from middle | "Smth" | 0.61-0.67 |
| **Medium** | Change vowel | "Smyth" | 0.61-0.67 |
| **Far** | Remove 2 from end | "Smi" | 0.31-0.45 |
| **Far** | Remove 2 from middle | "Smt" | 0.31-0.45 |

### For FIRST NAME:

| Category | Pattern | Example | Score Range |
|----------|---------|---------|-------------|
| **Light** | Original | "John" | 1.0000 |
| **Light** | Remove letter from middle | "Jon" | 1.0000 |
| **Medium** | ??? | Need to test | 0.6-0.8 |
| **Far** | ??? | Need to test | 0.3-0.6 |

**⚠️ Problem**: Removing letters from first name often gives 0.0000 (too different)!

---

## Why the Strategy Partially Works

✅ **Last Name**: Letter removal from end/middle of last name works well
- Remove 1 letter → Medium (0.6-0.8)
- Remove 2 letters → Far (0.3-0.6)

❌ **First Name**: Letter removal from first name is unpredictable
- Most removals give 0.0000 (too different)
- Only "Jon" (remove 'h' from middle) works and gives 1.0000 (Light)

---

## The Real Challenge

To "deceive" the validator, you need to:

1. **Vary FIRST name** to get distribution: 20% Light, 60% Medium, 20% Far
2. **Vary LAST name** to get distribution: 20% Light, 60% Medium, 20% Far
3. **Both distributions must match simultaneously!**

**Current Problem:**
- All first names are "John" or "Jon" → 100% Light (wrong!)
- Some last names are "Smih" or "Smi" → 0.0000 (penalized!)

---

## Recommendations

### Option 1: Vary First Name More
- Need to find ways to create Medium (0.6-0.8) and Far (0.3-0.6) first names
- Examples to test:
  - "Jhon" (swap letters) → Test if Medium
  - "Joh" (remove 1 from end) → Test if Medium/Far
  - "Jo" (remove 2 from end) → Test if Far

### Option 2: Use Different Strategies
- Instead of just removing letters, try:
  - Swapping letters: "John" → "Jhon"
  - Changing vowels: "John" → "Jahn"
  - Adding letters: "John" → "Johne"
  - Removing from different positions

### Option 3: Accept Limitations
- The letter removal strategy works for **last names** but not for **first names**
- May need to use Gemini or other methods to generate first name variations

---

## Test Code

```python
from MIID.validator.reward import calculate_phonetic_similarity

name = "John Smith"
first_original = "John"
last_original = "Smith"

# Test first name variations
first_variations = ["Jhon", "Joh", "Jo", "Jahn", "Johne"]
for var in first_variations:
    score = calculate_phonetic_similarity(first_original, var)
    print(f"'{var}' → {score:.4f}")

# Test last name variations (these work!)
last_variations = ["Smit", "Smth", "Smyth", "Smi", "Smt"]
for var in last_variations:
    score = calculate_phonetic_similarity(last_original, var)
    print(f"'{var}' → {score:.4f}")
```

---

## Conclusion

✅ **Letter removal from LAST NAME works well** for controlling similarity
❌ **Letter removal from FIRST NAME is unreliable** (most give 0.0000)
⚠️ **Need to vary BOTH first and last names** to get correct distribution
🎯 **Strategy is partially viable** but needs refinement for first names

