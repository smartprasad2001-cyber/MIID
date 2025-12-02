# What Happens If You Send Same Variations for All Names?

## Scenario
You send the same 8 variations (e.g., "John Smith", "Sohn Smith", "Jon Smith", etc.) for ALL names in the synapse.

## What Happens

### 1. Each Name is Scored Separately

The validator scores **each name independently** against its original:

```python
# For "John Smith" with variations ["John Smith", "Sohn Smith", ...]
Score = 0.3904  # Good - variations match the original

# For "Jane Doe" with SAME variations ["John Smith", "Sohn Smith", ...]
Score = 0.2325  # BAD - variations don't match "Jane Doe"!

# For "Bob Johnson" with SAME variations ["John Smith", "Sohn Smith", ...]
Score = 0.2315  # BAD - variations don't match "Bob Johnson"!
```

### 2. Why Scores Are Low for Non-Matching Names

**Phonetic Similarity Calculation:**
- "John Smith" vs "John Smith" → **1.0000** (perfect match)
- "John Smith" vs "Jane Doe" → **0.0000** (no match - different names!)
- "John Smith" vs "Bob Johnson" → **0.0000** (no match - different names!)

**Result:**
- Similarity score = **0.0000** (no variations match the original name)
- Base score drops significantly
- Final score is **much lower** (0.23 vs 0.39)

### 3. Penalties Applied

#### Within a Single Name:
- **Duplicate variations**: 5% penalty per duplicate
  - Example: If "John Smith" appears twice in variations for "John Smith" → 5% penalty

#### Across Different Names (Same Miner):
- **No direct penalty** for using same variations across names
- **BUT**: Each name gets scored separately, so non-matching names get **low scores**
- This effectively penalizes you because your average score will be low

#### Across Different Miners:
- **Collusion detection**: If multiple miners send same variations → penalty up to 0.75
- **Duplication detection**: If variations are too similar → penalty
- **Signature detection**: If exact same pattern → penalty up to 0.8

### 4. Example Calculation

**Scenario**: 3 names, same 8 variations for all

```
Name 1: "John Smith" → Score: 0.3904 ✓
Name 2: "Jane Doe" → Score: 0.2325 ✗
Name 3: "Bob Johnson" → Score: 0.2315 ✗

Average Score: (0.3904 + 0.2325 + 0.2315) / 3 = 0.2848
```

**vs. Generating Proper Variations:**

```
Name 1: "John Smith" → Score: 0.3904 ✓
Name 2: "Jane Doe" → Score: 0.3904 ✓ (with proper "Jane Doe" variations)
Name 3: "Bob Johnson" → Score: 0.3904 ✓ (with proper "Bob Johnson" variations)

Average Score: 0.3904
```

**Difference**: 0.3904 vs 0.2848 = **27% lower score!**

## Conclusion

**❌ DON'T send the same variations for all names!**

**Why:**
1. Each name is scored separately against its original
2. Non-matching variations get **0.0 similarity** → **low scores**
3. Your average score will be **much lower**
4. You'll get penalized for collusion if other miners do the same

**✅ DO generate unique variations for each name:**
1. Each name gets variations that match its original
2. Each name scores well (0.4-0.7)
3. Average score is **much higher**
4. No collusion penalties

## Code Reference

From `reward.py`:
- Each name is scored separately: `calculate_variation_quality(original_name, variations)`
- Phonetic similarity is calculated per name: `calculate_phonetic_similarity(original_name, variation)`
- If variations don't match original → similarity = 0.0 → low score

