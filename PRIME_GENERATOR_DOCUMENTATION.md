# Prime Generator Documentation

## Overview

The `prime_generator.py` script is a unified name variation generator that creates Light, Medium, and Far similarity variations for full names (first + last) and validates them using the actual validator's `rewards.py` scoring system.

## Purpose

This script is designed to:
1. **Generate name variations** that match specific phonetic similarity ranges (Light: 1.0, Medium: 0.6-0.79, Far: 0.3-0.59)
2. **Use algorithm weights** to intelligently target specific score ranges
3. **Test variations** with the actual validator scoring system to verify they achieve the desired scores
4. **Handle full names** by processing first and last names separately (as the validator does)

## How It Works

### Core Concept

The validator uses **three phonetic algorithms** (Soundex, Metaphone, NYSIIS) with **deterministic weights** to calculate similarity scores. The script leverages this knowledge to generate variations that target specific score ranges:

- **Light (1.0)**: All 3 algorithms match → `weight1 + weight2 + weight3 = 1.0`
- **Medium (0.6-0.79)**: 2 out of 3 algorithms match → `weight1 + weight2 ≈ 0.6-0.79`
- **Far (0.3-0.59)**: 1 out of 3 algorithms match → `weight1 ≈ 0.3-0.59`

### Algorithm Selection

The validator uses `random.seed(hash(original_name) % 10000)` to deterministically select which 3 algorithms to use and their weights. The script uses `get_weights_for_name()` to get these exact weights for any given name.

### Generation Strategy

1. **Get Algorithm Weights**: For each name, determine which algorithms are selected and their weights
2. **Generate Candidates**: Use 50+ strategies to generate candidate variations (letter removal, insertion, swapping, etc.)
3. **Filter by Target Range**: Check each candidate against the target score range:
   - **Light**: All 3 algorithm codes must match
   - **Medium**: 2 out of 3 algorithm codes must match (or specific combinations)
   - **Far**: 1 out of 3 algorithm codes must match (or lower scores)
4. **Recursive Search**: If not enough variations found, increase depth and candidate limits, then search again
5. **Combine First/Last**: Generate variations for first and last names separately, then combine them

## Key Functions

### `get_algorithm_codes(name: str) -> dict`
Gets the Soundex, Metaphone, and NYSIIS codes for a name.

**Example:**
```python
codes = get_algorithm_codes("John")
# Returns: {'soundex': 'J500', 'metaphone': 'JN', 'nysiis': 'JAN'}
```

### `calculate_score_with_weights(original, variation, selected_algorithms, weights) -> float`
Calculates phonetic similarity score using specific algorithms and their weights.

**How it works:**
- For each algorithm, checks if the codes match (1.0) or don't match (0.0)
- Multiplies match result by the algorithm's weight
- Sums all weighted matches to get final score

**Example:**
```python
# If weights are [0.3, 0.4, 0.3] for [soundex, metaphone, nysiis]
# And "John" vs "Jon" matches soundex and metaphone:
score = (1.0 * 0.3) + (1.0 * 0.4) + (0.0 * 0.3) = 0.7  # Medium range
```

### `generate_candidates(original, max_depth=10, max_candidates=10000000) -> List[str]`
Generates candidate variations using 50+ strategies recursively.

**Strategies include:**
- Letter removal (single, multiple, combinations)
- Letter insertion (vowels, consonants, pairs, clusters)
- Letter swapping (adjacent, non-adjacent, rotations)
- Letter replacement (phonetic equivalents, visual similarity)
- Prefix/suffix operations
- Pattern-based modifications (double letters, silent patterns, etc.)

**Recursive approach:**
- Each generated variation becomes a new starting point
- Continues until `max_depth` is reached or `max_candidates` limit is hit
- No early stopping - tries all possible combinations

### `generate_light_variations(original, count, verbose=False) -> List[str]`
Generates Light variations (score = 1.0) where all 3 algorithms match.

**Strategy:**
1. Get target codes for all 3 algorithms
2. Generate candidates recursively
3. Check each candidate: all 3 codes must match
4. If not enough found, increase depth and try again

**Example:**
```python
# For "John" (J500, JN, JAN)
# Find variations that produce: J500, JN, JAN
# Examples: "Jon", "Jhon", "Jahn" (if they match all 3)
```

### `generate_medium_variations(original, count, verbose=False) -> List[str]`
Generates Medium variations (score 0.6-0.79) where 2 out of 3 algorithms match.

**Strategy:**
1. Get algorithm weights
2. Calculate which 2-algorithm combinations give Medium range scores
3. Generate candidates and check if they match those specific combinations
4. Filter to ensure score is strictly in 0.6-0.79 range

**Example:**
```python
# If weights are [0.3, 0.4, 0.3]
# Target: Match soundex + metaphone = 0.3 + 0.4 = 0.7 (Medium)
# Find variations where soundex AND metaphone match, but nysiis doesn't
```

### `generate_far_variations(original, count, verbose=False) -> List[str]`
Generates Far variations (score 0.3-0.59) where 1 out of 3 algorithms match.

**Strategy:**
1. Get algorithm weights
2. Calculate which single algorithm gives Far range score
3. Generate candidates and check if they match only that algorithm
4. Filter to ensure score is strictly in 0.3-0.59 range

**Example:**
```python
# If weights are [0.3, 0.4, 0.3]
# Target: Match only metaphone = 0.4 (Far)
# Find variations where only metaphone matches
```

### `generate_full_name_variations(full_name, light_count, medium_count, far_count, verbose=True) -> List[str]`
Generates variations for a full name by processing first and last names separately.

**Process:**
1. Split name into first and last name
2. Generate Light/Medium/Far variations for first name
3. Generate Light/Medium/Far variations for last name
4. Combine them: `first_light[i] + " " + last_light[i]`

**Why separate?**
The validator scores first and last names independently, so both must meet the target distribution.

### `test_with_rewards(full_name, variations, expected_count, light_count, medium_count, far_count)`
Tests generated variations using the actual validator's `rewards.py` scoring system.

**What it does:**
1. Calculates target distribution percentages
2. Calls `calculate_variation_quality()` from `rewards.py`
3. Displays detailed metrics:
   - Final score and base score
   - First name and last name scores
   - Similarity scores (phonetic, orthographic, combined)
   - Count, uniqueness, and length scores

## Usage Example

```python
from prime_generator import generate_full_name_variations, test_with_rewards

# Generate variations for "John Smith"
# Target: 3 Light, 5 Medium, 2 Far
variations = generate_full_name_variations(
    "John Smith",
    light_count=3,
    medium_count=5,
    far_count=2,
    verbose=True
)

# Test with validator scoring
final_score, base_score, detailed_metrics = test_with_rewards(
    "John Smith",
    variations,
    expected_count=10,
    light_count=3,
    medium_count=5,
    far_count=2
)

print(f"Final score: {final_score:.4f}")
```

## Key Features

### 1. **Intelligent Algorithm Matching**
- Uses known algorithm weights to target specific score ranges
- For Medium: Matches 2 out of 3 algorithms
- For Far: Matches 1 out of 3 algorithms
- For Light: Matches all 3 algorithms

### 2. **Recursive Generation**
- Starts with depth 1, increases if not enough variations found
- Each variation becomes a new starting point
- Continues until enough variations are found or max depth reached

### 3. **50+ Generation Strategies**
- Letter removal (single, multiple, combinations)
- Letter insertion (vowels, consonants, pairs, clusters)
- Letter swapping (adjacent, non-adjacent, rotations)
- Letter replacement (phonetic equivalents, visual similarity)
- Prefix/suffix operations
- Pattern-based modifications

### 4. **Strict Range Filtering**
- Light: Only variations with score = 1.0
- Medium: Only variations with score 0.6-0.79
- Far: Only variations with score 0.3-0.59
- Ensures generated variations match validator's distribution requirements

### 5. **Separate First/Last Name Processing**
- Generates variations for first and last names independently
- Combines them to create full name variations
- Both parts must individually meet target distribution

### 6. **Validator Integration**
- Uses actual `rewards.py` functions for scoring
- Verifies that generated variations achieve target scores
- Provides detailed metrics for debugging

## Performance Considerations

### Recursive Depth
- Starts at depth 1, increases up to depth 10
- Each depth level exponentially increases candidate count
- Early stopping when enough variations found

### Candidate Limits
- Initial: 100,000-500,000 candidates
- Maximum: 10,000,000 candidates
- Increases by 2x each recursion level

### Generation Multipliers
- Light: 200x more candidates (harder to find perfect matches)
- Medium: 200x more candidates
- Far: 200x more candidates

## Limitations

1. **Computational Cost**: Generating millions of candidates can be slow for difficult names
2. **Memory Usage**: Storing large candidate sets requires significant memory
3. **Perfect Matches**: Some names may not have enough Light variations (all 3 algorithms matching)
4. **Name Length**: Very short names (< 3 letters) have limited variation possibilities

## Troubleshooting

### Not Finding Enough Variations

**Problem**: Script can't find enough Light/Medium/Far variations

**Solutions**:
1. Increase `max_depth` (currently up to 10)
2. Increase `max_candidates` (currently up to 10,000,000)
3. Check if name is too short or too unique
4. Verify algorithm weights are correct using `get_weights_for_name()`

### Low Similarity Scores

**Problem**: Generated variations don't achieve target similarity scores

**Solutions**:
1. Ensure using `calculate_phonetic_similarity()` from `rewards.py` (not custom function)
2. Verify algorithm weights match validator's selection
3. Check that variations are being filtered to strict ranges (0.6-0.79 for Medium, 0.3-0.59 for Far)

### Memory Issues

**Problem**: Script runs out of memory

**Solutions**:
1. Reduce `max_candidates` limit
2. Reduce `max_depth`
3. Process names one at a time instead of batch processing

## Integration with Validator

This script is designed to work with the MIID subnet validator:

1. **Uses Validator Functions**: Imports and uses `calculate_variation_quality()`, `calculate_phonetic_similarity()` from `rewards.py`
2. **Matches Validator Logic**: Replicates the validator's algorithm selection and weighting
3. **Validates Output**: Tests generated variations with actual validator scoring
4. **Distribution Matching**: Ensures generated variations match validator's Light/Medium/Far distribution requirements

## Future Improvements

1. **Parallel Processing**: Generate candidates in parallel for faster execution
2. **Caching**: Cache algorithm codes and weights for repeated names
3. **Smart Pruning**: Early pruning of candidates that can't reach target ranges
4. **Adaptive Strategies**: Select generation strategies based on name characteristics
5. **Batch Processing**: Process multiple names simultaneously

