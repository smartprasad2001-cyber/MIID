# Cheat Detection System Documentation

## Overview

The `cheat_detection.py` module is a comprehensive anti-cheating system that analyzes miner responses to detect various forms of cheating, collusion, and manipulation. It operates **after** the initial reward calculation and applies penalties to miners who exhibit suspicious patterns.

### Key Capabilities

1. **Cross-Miner Collusion Detection**: Identifies miners with suspiciously similar variation sets
2. **Exact Copy Detection**: Catches miners submitting identical or near-identical responses
3. **Special Character Abuse**: Detects excessive use of non-standard characters
4. **Address Duplication**: Finds duplicate addresses within a miner and across miners
5. **Cheat Corpus Matching**: Compares submissions against known cheat lists

---

## Table of Contents

1. [Normalization Functions](#normalization-functions)
2. [Cheat Corpus Detection](#cheat-corpus-detection)
3. [Similarity Metrics](#similarity-metrics)
4. [Main Detection Function](#main-detection-function)
5. [Integration with Reward System](#integration-with-reward-system)
6. [Complete Examples](#complete-examples)

---

## Normalization Functions

### 1. `normalize_variation(text: str, aggressive: bool = True) -> str`

**Purpose**: Creates a canonical form of any string for robust comparison.

**Process**:
- Converts to lowercase
- Removes all spaces
- If `aggressive=True`: Applies leetspeak mapping and removes all non-letters

**Example**:

```python
from MIID.validator.cheat_detection import normalize_variation

# Basic normalization
normalize_variation("John Smith", aggressive=False)
# Returns: "johnsmith"

# Aggressive normalization (applies leetspeak mapping)
normalize_variation("J0hn Sm!th", aggressive=True)
# Returns: "johnsmith" (0→o, !→i, spaces removed)

normalize_variation("M@ry J@ne", aggressive=True)
# Returns: "maryjane" (@→a)

# Different variations that normalize to the same string
normalize_variation("John-Smith", aggressive=True)  # "johnsmith"
normalize_variation("John_Smith", aggressive=True)  # "johnsmith"
normalize_variation("John Smith", aggressive=True)  # "johnsmith"
```

**Use Case**: Used to detect when miners submit the same variation with different formatting.

---

### 2. `remove_disallowed_unicode(text: str) -> str`

**Purpose**: Strips out unwanted Unicode characters while preserving legitimate text.

**Keeps**:
- All letters (any language)
- Diacritic marks
- ASCII digits and spaces

**Removes**:
- Emoji (😀, 🎉, etc.)
- Currency symbols (£, €, ¥, etc.)
- Math operators (∑, ∫, etc.)
- Phonetic extensions and Latin Extended-D block

**Example**:

```python
from MIID.validator.cheat_detection import remove_disallowed_unicode

remove_disallowed_unicode("John Smith 😀")
# Returns: "John Smith "

remove_disallowed_unicode("123 Main St. £500")
# Returns: "123 Main St. 500"

remove_disallowed_unicode("Mary's Café")
# Returns: "Mary's Café" (diacritics preserved)
```

---

### 3. `normalize_address_for_deduplication(addr: str) -> str`

**Purpose**: Very aggressive normalization specifically for address deduplication and cross-miner comparison.

**Process**:
1. Removes disallowed Unicode
2. Applies NFKD normalization and removes diacritics
3. Transliterates all non-ASCII to ASCII (Arabic, Cyrillic, etc.)
4. Extracts unique words
5. **Sorts all letters alphabetically** (this is the key difference!)

**Example**:

```python
from MIID.validator.cheat_detection import normalize_address_for_deduplication

# Same address in different formats
normalize_address_for_deduplication("123 Main Street, New York")
# Returns: "adeeghikmnorstttwxy" (sorted letters from unique words)

normalize_address_for_deduplication("123 Main St., New York, NY")
# Returns: "adeeghikmnorstttwxy" (same - duplicates detected!)

# Different languages transliterated
normalize_address_for_deduplication("ул. Ленина, 10, Москва")  # Russian
# Returns: sorted letters from transliterated version

# Addresses that are semantically the same
normalize_address_for_deduplication("123 Main St")
normalize_address_for_deduplication("Main Street 123")
# Both normalize to similar sorted letter strings (may match if words overlap)
```

**Important**: This is **much more aggressive** than the `normalize_address` function in `rewards.py`. This is intentional - it's designed to catch sophisticated cheating attempts where addresses are rewritten but mean the same thing.

---

## Cheat Corpus Detection

### `load_cheat_corpus(paths: List[str]) -> Dict[str, Set[str]]`

**Purpose**: Loads known cheat lists from files and creates a normalized lookup table.

**Example**:

**File: `known_cheats.json`**
```json
{
  "John Smith": ["John Smith", "Jon Smith", "John Smyth"],
  "Mary Johnson": ["Mary Johnson", "Marie Johnson", "Mary Jonson"]
}
```

**Usage**:

```python
from MIID.validator.cheat_detection import load_cheat_corpus, corpus_overlap_score

# Load cheat corpus
cheat_corpus = load_cheat_corpus(["known_cheats.json"])

# Check a miner's variations
miner_variations = {
    "John Smith": ["John Smith", "Jon Smith", "Johnny Smith", "John Smyth"]
}

# Calculate overlap
overlap = corpus_overlap_score(miner_variations, cheat_corpus)
# Returns: 0.75 (3 out of 4 variations match the cheat corpus)
```

**Real-World Scenario**:
- A cheat list gets leaked and shared among miners
- All miners using that list will have high overlap scores
- This helps identify coordinated cheating

---

## Similarity Metrics

### `overlap_coefficient(a: Set[str], b: Set[str]) -> float`

**Formula**: `|a ∩ b| / min(|a|, |b|)`

**Example**:

```python
from MIID.validator.cheat_detection import overlap_coefficient, build_normalized_set

miner1_variations = ["John Smith", "Jon Smith", "Johnny Smith"]
miner2_variations = ["John Smith", "Jon Smith", "Jane Doe"]

set1 = build_normalized_set(miner1_variations)
# {"johnsmith", "jonsmith", "johnnysmith"}

set2 = build_normalized_set(miner2_variations)
# {"johnsmith", "jonsmith", "janedoe"}

overlap = overlap_coefficient(set1, set2)
# Returns: 2/3 = 0.667 (2 common, min size is 3)
```

### `jaccard(a: Set[str], b: Set[str]) -> float`

**Formula**: `|a ∩ b| / |a ∪ b|`

**Example**:

```python
from MIID.validator.cheat_detection import jaccard

set1 = {"a", "b", "c"}
set2 = {"a", "b", "d"}

jaccard(set1, set2)
# Returns: 2/4 = 0.5 (2 common, 4 unique total)
```

**When to Use**:
- **Overlap Coefficient**: Better when one set is much larger (measures "how much of the smaller set is covered")
- **Jaccard**: Better for symmetric comparison (measures "how similar are these sets overall")

---

## Main Detection Function

### `detect_cheating_patterns(responses, uids, rewards, seed_names) -> Dict`

**Input Format**:

```python
# responses: List[Dict[str, List[List[str]]]]
# Each miner's response is a dict: name -> list of [name_var, dob_var, address_var]

responses = [
    {
        "John Smith": [
            ["John Smith", "1990-01-01", "123 Main St"],
            ["Jon Smith", "1990-01-01", "123 Main Street"],
            ["Johnny Smith", "1990-01-01", "456 Oak Ave"]
        ],
        "Mary Johnson": [
            ["Mary Johnson", "1985-05-15", "789 Pine Rd"],
            ["Marie Johnson", "1985-05-15", "789 Pine Road"]
        ]
    },
    # ... more miners
]

uids = [1, 2, 3, ...]  # Miner IDs
rewards = np.array([0.85, 0.92, 0.78, ...])  # Current reward scores
seed_names = ["John Smith", "Mary Johnson"]  # Seed names requested
```

**Output**:

```python
{
    "duplication_penalties": np.array([0.0, 0.5, 0.0, ...]),  # Per-miner penalties
    "signature_penalties": np.array([0.0, 0.8, 0.0, ...]),
    "collusion_penalties": np.array([0.0, 0.75, 0.0, ...]),
    "special_char_penalties": np.array([0.0, 0.3, 0.0, ...]),
    "address_duplication_penalties": np.array([0.0, 0.2, 0.0, ...]),
    "special_char_counts": np.array([0, 5, 0, ...]),
    "total_variations_counts": np.array([20, 20, 20, ...]),
    "special_char_ratios": np.array([0.0, 0.25, 0.0, ...])
}
```

---

## Detection Mechanisms

### 1. Special Character Abuse Detection

**Process**:
- Counts special characters in each name variation (excluding common punctuation like `.`, `-`, `'`)
- If a variation has >2 special characters, it's flagged
- If >50% of variations have excessive special chars, penalty is applied

**Example**:

```python
# Miner with excessive special characters
miner_variations = {
    "John Smith": [
        ["J0hn$m!th", "1990-01-01", "123 Main St"],      # 3 special chars
        ["J@hn#Sm!th", "1990-01-01", "123 Main St"],     # 4 special chars
        ["J0hn$m!th@", "1990-01-01", "123 Main St"],     # 5 special chars
        ["John Smith", "1990-01-01", "123 Main St"],      # 0 special chars
        ["Jon Smith", "1990-01-01", "123 Main St"]       # 0 special chars
    ]
}

# 3 out of 5 variations have >2 special chars = 60% ratio
# Penalty: (0.60 - 0.50) / 0.50 = 0.20 (20% penalty)
```

---

### 2. Within-Miner Address Duplication

**Process**:
- Collects all addresses from a miner across all names
- Normalizes each address using `normalize_address_for_deduplication`
- Counts duplicates: `duplicate_count = len(all_addresses) - len(set(all_addresses))`
- Penalty: `min(duplicate_ratio * 0.2, 0.2)`

**Example**:

```python
# Miner reusing the same address
miner_response = {
    "John Smith": [
        ["John Smith", "1990-01-01", "123 Main St, New York"],
        ["Jon Smith", "1990-01-01", "123 Main Street, New York"],  # Duplicate!
        ["Johnny Smith", "1990-01-01", "123 Main St, NY"]         # Duplicate!
    ],
    "Mary Johnson": [
        ["Mary Johnson", "1985-05-15", "123 Main St, New York"]   # Duplicate!
    ]
}

# All 4 addresses normalize to the same string
# duplicate_count = 4 - 1 = 3
# duplicate_ratio = 3/4 = 0.75
# Penalty = min(0.75 * 0.2, 0.2) = 0.15 (15% penalty)
```

---

### 3. Cross-Miner Name Similarity (Collusion Detection)

**Process**:
- Builds normalized sets for each miner: `{name -> Set[normalized_variations]}`
- Compares all pairs of miners using overlap/Jaccard coefficients
- If similarity exceeds thresholds, applies penalties

**Example**:

```python
# Two miners with suspiciously similar variations
miner1 = {
    "John Smith": ["John Smith", "Jon Smith", "Johnny Smith"]
}
miner2 = {
    "John Smith": ["John Smith", "Jon Smith", "Johnny Smith"]  # Identical!
}

# After normalization:
# miner1_set = {"johnsmith", "jonsmith", "johnnysmith"}
# miner2_set = {"johnsmith", "jonsmith", "johnnysmith"}

# Overlap = 3/3 = 1.0 (100% overlap!)
# Jaccard = 3/3 = 1.0 (100% similarity!)

# Since overlap > 0.95, both miners get duplication_penalty = 0.5 (50%)
```

**Thresholds**:
- **Strict mode**: Overlap > 0.75 OR Jaccard > 0.70
- **Relaxed mode**: Overlap > 0.80 OR Jaccard > 0.70
- **Global check**: Overlap > 0.95 OR Jaccard > 0.90 → 50% penalty

---

### 4. Exact Signature Matching

**Process**:
- Creates a stable hash signature for each miner's complete response
- Groups miners by signature
- If multiple miners share the same signature and have reward > 0, they get penalized

**Example**:

```python
# Three miners submit identical responses
miner1_response = {
    "John Smith": [["John Smith", "1990-01-01", "123 Main St"]],
    "Mary Johnson": [["Mary Johnson", "1985-05-15", "456 Oak Ave"]]
}
miner2_response = {
    "John Smith": [["John Smith", "1990-01-01", "123 Main St"]],
    "Mary Johnson": [["Mary Johnson", "1985-05-15", "456 Oak Ave"]]
}
miner3_response = {
    "John Smith": [["John Smith", "1990-01-01", "123 Main St"]],
    "Mary Johnson": [["Mary Johnson", "1985-05-15", "456 Oak Ave"]]
}

# All three have the same hash signature
# signature_penalties = [0.8, 0.8, 0.8] (80% penalty for all)
```

---

### 5. Cross-Miner Address Similarity

**Process**:
- Normalizes addresses using `normalize_address_for_deduplication`
- Compares address sets between miners for each common name
- If overlap > 0.8 or Jaccard > 0.7, applies penalty

**Example**:

```python
# Two miners using the same addresses
miner1 = {
    "John Smith": [
        ["John Smith", "1990-01-01", "123 Main St, New York"],
        ["Jon Smith", "1990-01-01", "456 Oak Ave, Boston"]
    ]
}
miner2 = {
    "John Smith": [
        ["John Smith", "1990-01-01", "123 Main Street, NY"],      # Same as miner1
        ["Jon Smith", "1990-01-01", "456 Oak Avenue, Boston"]     # Same as miner1
    ]
}

# After normalization, both have the same address sets
# Overlap = 1.0, Jaccard = 1.0
# Since overlap > 0.8, both get address_duplication_penalty = 0.6 (60%)
```

---

### 6. Reward Bucket Collusion

**Process**:
- Groups miners by exact reward value (rounded to 4 decimal places)
- If a group has >5 miners with identical rewards and reward < 0.95, flags as collusion

**Example**:

```python
# 6 miners all have reward = 0.8234
rewards = np.array([0.8234, 0.8234, 0.8234, 0.8234, 0.8234, 0.8234, 0.9123, ...])

# Group of 6 miners with identical reward < 0.95
# collusion_penalties = [0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.0, ...]
```

---

## Integration with Reward System

### How It's Called

In `reward.py`, the cheat detection runs **after** initial reward calculation:

```python
# 1. Calculate initial rewards based on quality
rewards = calculate_initial_rewards(...)

# 2. Run cheat detection
cheating_results = detect_cheating_patterns(
    responses=response_dicts,
    uids=uids,
    rewards=rewards,  # Uses current rewards for grouping
    seed_names=seed_names
)

# 3. Apply penalties
for i in range(num_miners):
    total_penalty = (
        cheating_results["duplication_penalties"][i] +
        cheating_results["signature_penalties"][i] +
        cheating_results["collusion_penalties"][i] +
        cheating_results["special_char_penalties"][i] +
        cheating_results["address_duplication_penalties"][i]
    )
    total_penalty = min(total_penalty, 1.0)  # Cap at 100%
    
    # Apply penalty multiplicatively
    final_reward = rewards[i] * (1.0 - total_penalty)
```

### Penalty Application

**Multiplicative Penalty Model**:
- If a miner has reward = 0.90 and total penalty = 0.30 (30%)
- Final reward = 0.90 × (1.0 - 0.30) = 0.90 × 0.70 = **0.63**

**Penalty Caps**:
- Individual penalties can exceed 1.0, but `total_penalty` is capped at 1.0
- This means a miner can lose **up to 100%** of their reward

---

## Complete Examples

### Example 1: Honest Miner (No Penalties)

```python
# Miner submits legitimate, unique variations
honest_miner = {
    "John Smith": [
        ["John Smith", "1990-01-01", "123 Main St, New York"],
        ["Jon Smith", "1990-01-01", "456 Oak Ave, Boston"],
        ["Johnny Smith", "1990-01-01", "789 Pine Rd, Chicago"]
    ],
    "Mary Johnson": [
        ["Mary Johnson", "1985-05-15", "321 Elm St, Seattle"],
        ["Marie Johnson", "1985-05-15", "654 Maple Dr, Portland"]
    ]
}

# Results:
# - No duplicate addresses (all unique)
# - No excessive special characters
# - Variations are unique compared to other miners
# - No exact signature match with others

# Penalties: All zeros
# Final reward: Unchanged
```

---

### Example 2: Miner with Duplicate Addresses

```python
# Miner reuses the same address for multiple variations
duplicate_address_miner = {
    "John Smith": [
        ["John Smith", "1990-01-01", "123 Main St, New York"],
        ["Jon Smith", "1990-01-01", "123 Main Street, NY"],      # Duplicate
        ["Johnny Smith", "1990-01-01", "123 Main St, New York"]  # Duplicate
    ],
    "Mary Johnson": [
        ["Mary Johnson", "1985-05-15", "123 Main St, New York"]  # Duplicate
    ]
}

# Analysis:
# - 4 addresses total
# - All normalize to the same string
# - duplicate_count = 4 - 1 = 3
# - duplicate_ratio = 3/4 = 0.75
# - address_duplication_penalty = min(0.75 * 0.2, 0.2) = 0.15

# If initial reward = 0.85:
# Final reward = 0.85 × (1.0 - 0.15) = 0.85 × 0.85 = 0.7225
```

---

### Example 3: Two Miners Colluding

```python
# Miner 1
miner1 = {
    "John Smith": [
        ["John Smith", "1990-01-01", "123 Main St"],
        ["Jon Smith", "1990-01-01", "456 Oak Ave"]
    ]
}

# Miner 2 (copying from Miner 1)
miner2 = {
    "John Smith": [
        ["John Smith", "1990-01-01", "123 Main St"],      # Same as miner1
        ["Jon Smith", "1990-01-01", "456 Oak Ave"]        # Same as miner1
    ]
}

# Analysis:
# - Normalized sets are identical
# - Overlap = 1.0, Jaccard = 1.0
# - Both exceed thresholds (overlap > 0.95)
# - duplication_penalties = [0.5, 0.5] (50% each)

# If both had initial reward = 0.90:
# Final reward = 0.90 × (1.0 - 0.5) = 0.45 for both
```

---

### Example 4: Miner Using Cheat Corpus

```python
# Known cheat list
cheat_corpus = {
    "john smith": {
        "johnsmith", "jonsmith", "johnnysmith", "johsmith"
    }
}

# Miner using the cheat list
miner = {
    "John Smith": [
        "John Smith",    # In corpus
        "Jon Smith",     # In corpus
        "Johnny Smith",  # In corpus
        "Jane Doe"       # Not in corpus
    ]
}

# Analysis:
# - 3 out of 4 variations match corpus
# - corpus_overlap_score = 0.75
# - This would be flagged in a corpus-based check
# - (Note: corpus checking is separate from detect_cheating_patterns)
```

---

### Example 5: Miner with Special Character Abuse

```python
# Miner using excessive special characters
special_char_miner = {
    "John Smith": [
        ["J0hn$m!th", "1990-01-01", "123 Main St"],      # 3 special chars
        ["J@hn#Sm!th", "1990-01-01", "123 Main St"],     # 4 special chars
        ["J0hn$m!th@", "1990-01-01", "123 Main St"],     # 5 special chars
        ["J0hn$m!th#", "1990-01-01", "123 Main St"],     # 5 special chars
        ["John Smith", "1990-01-01", "123 Main St"]     # 0 special chars
    ]
}

# Analysis:
# - 4 out of 5 variations have >2 special chars
# - special_char_ratio = 4/5 = 0.80
# - Penalty = (0.80 - 0.50) / 0.50 = 0.60 (60%)
# - special_char_penalties = 0.60

# If initial reward = 0.85:
# Final reward = 0.85 × (1.0 - 0.60) = 0.85 × 0.40 = 0.34
```

---

### Example 6: Multiple Cheating Patterns Combined

```python
# Miner with multiple issues
bad_miner = {
    "John Smith": [
        ["J0hn$m!th", "1990-01-01", "123 Main St"],           # Special chars
        ["J@hn#Sm!th", "1990-01-01", "123 Main Street"],      # Special chars + duplicate address
        ["J0hn$m!th@", "1990-01-01", "123 Main St, NY"]      # Special chars + duplicate address
    ]
}

# Also colludes with another miner (same variations)

# Penalties:
# - special_char_penalty = 0.60 (3/3 have special chars)
# - address_duplication_penalty = 0.20 (all addresses are duplicates)
# - duplication_penalty = 0.50 (colluding with another miner)
# - Total = 0.60 + 0.20 + 0.50 = 1.30 → capped at 1.0

# If initial reward = 0.90:
# Final reward = 0.90 × (1.0 - 1.0) = 0.0 (100% penalty - miner gets nothing)
```

---

## Key Differences: `cheat_detection.py` vs `rewards.py`

| Aspect | `rewards.py` | `cheat_detection.py` |
|--------|-------------|---------------------|
| **Purpose** | Calculate quality-based rewards | Detect cheating and collusion |
| **Normalization** | Simple: lowercase, spaces, separators | Aggressive: transliteration, letter sorting |
| **Scope** | Per-miner, per-name | Cross-miner, global |
| **Address Normalization** | Preserves word order | Sorts letters alphabetically |
| **Duplicate Detection** | Within a miner's variations for a name | Across all miners, all names |
| **Penalty Type** | Quality/completeness penalties | Cheating/collusion penalties |

**Why Two Systems?**

- **`rewards.py`**: Fair scoring - "Did the miner provide good variations?"
- **`cheat_detection.py`**: Security - "Is the miner cheating or colluding?"

The aggressive normalization in `cheat_detection.py` is necessary to catch sophisticated cheating where addresses are rewritten but semantically identical.

---

## Best Practices for Miners

To avoid penalties, miners should:

1. ✅ **Use unique addresses** - Don't reuse the same address across variations
2. ✅ **Avoid excessive special characters** - Use normal punctuation only
3. ✅ **Generate original variations** - Don't copy from other miners
4. ✅ **Use diverse formats** - Vary address formats naturally
5. ✅ **Avoid exact matches** - Don't submit identical responses as other miners

---

## Summary

The cheat detection system is a multi-layered defense against various forms of cheating:

- **Within-miner checks**: Duplicate addresses, special character abuse
- **Cross-miner checks**: Collusion, exact copying, address sharing
- **Pattern detection**: Reward bucket analysis, signature matching
- **Aggressive normalization**: Catches sophisticated rewriting attempts

All penalties are applied **multiplicatively** to the initial reward, ensuring cheaters receive significantly reduced or zero rewards.

