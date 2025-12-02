# Phonetic Similarity Calculation Flow in rewards.py

## Complete Flow with Line Numbers

### 1. Entry Point: `get_name_variation_rewards()` 
**Lines: 2212-3007**

This is the main function that processes miner responses and calculates rewards.

**Key sections:**
- **Lines 2256-2261**: Define phonetic boundaries (same as in `calculate_part_score`)
  ```python
  phonetic_boundaries = {
      "Light": (0.8, 1.0),
      "Medium": (0.6, 0.8),
      "Far": (0.3, 0.6)
  }
  ```

### 2. Split Name into Parts: `get_name_part_weights()`
**Lines: 1208-1230**

Determines weights for first and last name parts:
- **Line 1210**: `random.seed(hash(name) % 10000)` - Deterministic seed
- **Line 1211**: Split name into parts
- Returns weights like `{"first_name_weight": 0.3, "last_name_weight": 0.7}`

### 3. Process Each Name: `calculate_name_quality()` or `calculate_name_quality_phonetic_only()`
**Lines: 1284-1360** (with orthographic) or **1449-1520** (phonetic-only)

Splits full name and calls `calculate_part_score` for each part:
- **Line 1286**: `part_weights = get_name_part_weights(original_name)`
- **Line 1327**: `first_name_score, first_metrics = calculate_part_score(...)`
- **Line 1340**: `last_name_score, last_metrics = calculate_part_score(...)`

### 4. Calculate Part Score: `calculate_part_score()`
**Lines: 749-1003**

This is the core function that scores a single part (first or last name).

#### 4.1 Define Boundaries (Lines 767-777)
```python
phonetic_boundaries = {
    "Light": (0.80, 1.00),
    "Medium": (0.60, 0.79),
    "Far": (0.30, 0.59)
}
```

#### 4.2 Count Check (Lines 779-809)
- Checks if variation count matches expected count
- Applies tolerance and penalties

#### 4.3 Uniqueness Check (Lines 811-832)
- **Line 818**: Uses `calculate_phonetic_similarity()` to check if variations are too similar
- Removes duplicate variations

#### 4.4 Length Check (Lines 834-857)
- Validates that variation lengths are reasonable

#### 4.5 Calculate Phonetic Scores (Lines 860-875)
**CRITICAL SECTION:**
```python
phonetic_scores = []
for variation in unique_variations:
    p_score = calculate_phonetic_similarity(original_part, variation)  # Line 865
    phonetic_scores.append(p_score)  # Line 868
```

#### 4.6 Sort Scores (Line 878)
```python
phonetic_scores.sort()
```

#### 4.7 Calculate Distribution Quality (Lines 882-920)
**Function: `calculate_distribution_quality()`**

**Line 892**: Count variations in each category
```python
count = sum(1 for score in scores if lower <= score <= upper)
```

**Line 893**: Calculate target count
```python
target_count = int(target_percentage * len(scores))
```

**Line 897**: Calculate match ratio
```python
match_ratio = count / target_count
```

**Lines 901-904**: Calculate match quality
```python
if match_ratio <= 1.0:
    match_quality = match_ratio  # Linear up to target
else:
    match_quality = 1.0 - math.exp(-(match_ratio - 1.0))  # Diminishing returns
```

**Line 905**: Add to quality score
```python
quality += target_percentage * match_quality
```

**Lines 914-917**: Penalize unmatched variations
```python
unmatched = len(scores) - total_matched
if unmatched > 0:
    penalty = 0.1 * (unmatched / len(scores))
    quality = max(0.0, quality - penalty)
```

#### 4.8 Calculate Phonetic Quality (Lines 922-924)
```python
phonetic_quality = calculate_distribution_quality(
    phonetic_scores, phonetic_boundaries, phonetic_similarity
)
```

#### 4.9 Combined Similarity Score (Line 930)
```python
similarity_score = (phonetic_quality + orthographic_quality) / 2
```

### 5. Core Phonetic Similarity Function: `calculate_phonetic_similarity()`
**Lines: 129-169**

This function calculates the phonetic similarity between two strings.

#### 5.1 Define Algorithms (Lines 147-152)
```python
algorithms = {
    "soundex": lambda x, y: jellyfish.soundex(x) == jellyfish.soundex(y),
    "metaphone": lambda x, y: jellyfish.metaphone(x) == jellyfish.metaphone(y),
    "nysiis": lambda x, y: jellyfish.nysiis(x) == jellyfish.nysiis(y),
}
```

#### 5.2 Deterministic Random Selection (Lines 154-156)
```python
random.seed(hash(original_name) % 10000)  # Line 155
selected_algorithms = random.sample(list(algorithms.keys()), k=min(3, len(algorithms)))  # Line 156
```

#### 5.3 Generate Weights (Lines 158-161)
```python
weights = [random.random() for _ in selected_algorithms]  # Line 159
total_weight = sum(weights)  # Line 160
normalized_weights = [w / total_weight for w in weights]  # Line 161
```

#### 5.4 Calculate Weighted Score (Lines 164-167)
```python
phonetic_score = sum(
    algorithms[algo](original_name, variation) * weight
    for algo, weight in zip(selected_algorithms, normalized_weights)
)
```

#### 5.5 Return Score (Line 169)
```python
return float(phonetic_score)
```

## Summary of Key Line Numbers

| Function/Step | Line Numbers |
|---------------|--------------|
| `calculate_phonetic_similarity()` | 129-169 |
| Algorithm selection & weights | 155-161 |
| Weighted score calculation | 164-167 |
| `calculate_part_score()` | 749-1003 |
| Phonetic boundaries | 767-771 |
| Score each variation | 865-868 |
| `calculate_distribution_quality()` | 882-920 |
| Count in category | 892 |
| Match ratio calculation | 897 |
| Match quality calculation | 901-904 |
| Phonetic quality | 922-924 |
| Combined similarity | 930 |
| `get_name_part_weights()` | 1208-1230 |
| `get_name_variation_rewards()` | 2212-3007 |

## Important Notes

1. **Deterministic Randomness**: The algorithm selection and weights are deterministic for each `original_name` using `hash(original_name) % 10000` as the seed (Line 155).

2. **Boundaries**: 
   - Light: 0.80-1.00 (inclusive)
   - Medium: 0.60-0.79 (inclusive)
   - Far: 0.30-0.59 (inclusive)

3. **Distribution Penalty**: If you exceed the target count for a category, the quality score uses diminishing returns (Line 904), which heavily penalizes exceeding targets.

4. **Unmatched Penalty**: Variations that don't fall into any category get a 10% penalty (Line 916).

5. **Score Calculation**: Each algorithm returns 1.0 if match, 0.0 if no match. The final score is the weighted sum of all selected algorithms.





