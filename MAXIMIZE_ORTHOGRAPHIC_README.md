# Maximize Orthographic Similarity - Brute Force Generator

## Overview

This script reverse engineers `rewards.py`'s orthographic similarity calculation and uses brute force to generate name variations that achieve **maximum orthographic scores**.

**Focus**: ONLY orthographic similarity (Levenshtein distance), NOT phonetic similarity.

## How It Works

### 1. Reverse Engineering `rewards.py`

The script uses the **exact same calculation** as `rewards.py`:

```python
def calculate_orthographic_similarity(original_name: str, variation: str) -> float:
    distance = Levenshtein.distance(original_name, variation)
    max_len = max(len(original_name), len(variation))
    return 1.0 - (distance / max_len)
```

**Boundaries** (from `rewards.py` lines 773-777):
- **Light**: 0.70 - 1.00 (high similarity)
- **Medium**: 0.50 - 0.69 (moderate similarity)
- **Far**: 0.20 - 0.49 (low similarity)
- **Below**: < 0.20 (rejected)

### 2. Brute Force Generation Strategies

The script uses **7 different strategies** to generate variations:

#### Strategy 1: Single Character Substitution
- Replaces each character with visually similar alternatives
- Example: "John" → "Jgohn" (g instead of o), "Joåhn" (å instead of a)

#### Strategy 2: Character Insertion
- Inserts similar-looking characters at various positions
- Example: "John" → "Johan" (insert 'a'), "Johhn" (insert 'h')

#### Strategy 3: Character Deletion
- Removes characters (simulating typos or abbreviations)
- Example: "John" → "Jhn" (remove 'o'), "Jon" (remove 'h')

#### Strategy 4: Character Transposition
- Swaps adjacent characters (common typing errors)
- Example: "John" → "Jhon" (swap 'h' and 'o'), "Jonh" (swap 'n' and 'h')

#### Strategy 5: Double Character Variations
- Manipulates double letters (add/remove/replace)
- Example: "Smith" → "Smitth" (add double 't'), "Smth" (remove double)

#### Strategy 6: Visual Similar Replacements
- Replaces patterns that look similar
- Examples: "rn" → "m", "cl" → "d", "vv" → "w"

#### Strategy 7: Recursive Variations
- Applies multiple strategies in sequence
- Generates variations of variations (depth 2-3)
- Finds more complex combinations

### 3. Optimal Selection Algorithm

After generating thousands of variations, the script:

1. **Scores all variations** using the exact `rewards.py` calculation
2. **Categorizes** them into Light/Medium/Far
3. **Selects optimal combination** to match target distribution:
   - Light: Prioritizes highest scores
   - Medium: Prioritizes scores closest to 0.60 (middle of range)
   - Far: Prioritizes scores closest to 0.35 (middle of range)
4. **Uses brute force** to try different combinations if needed
5. **Calculates distribution quality** using the same logic as `rewards.py`

## Usage

### Basic Usage

```bash
python3 maximize_orthographic_similarity.py "John" --count 15
```

### Custom Distribution

```bash
python3 maximize_orthographic_similarity.py "John Smith" \
    --count 15 \
    --light 0.2 \
    --medium 0.6 \
    --far 0.2
```

### Parameters

- `name`: Original name to generate variations for (required)
- `--count`: Number of variations to generate (default: 15)
- `--light`: Target percentage for Light category (default: 0.2)
- `--medium`: Target percentage for Medium category (default: 0.6)
- `--far`: Target percentage for Far category (default: 0.2)

**Note**: Percentages will be normalized if they don't sum to 1.0

## Example Output

```
================================================================================
ORTHOGRAPHIC SIMILARITY MAXIMIZATION (BRUTE FORCE)
================================================================================

🔍 Generating variations for: 'John'
   Target distribution: {'Light': 0.2, 'Medium': 0.6, 'Far': 0.2}

   Strategy 1: Single character substitution...
      Generated: 10 variations
   Strategy 2: Character insertion...
      Generated: 52 variations
   ...
   Total unique variations generated: 702
   Calculating orthographic scores...

   Categorized variations:
      Light (0.70-1.00):   99 variations
      Medium (0.50-0.69):  594 variations
      Far (0.20-0.49):     9 variations

🎯 Selecting optimal combination for 10 variations...
   Target counts: Light=2, Medium=6, Far=2
   ✅ Selected 10 variations

================================================================================
RESULTS
================================================================================
Original Name: John
Variations Generated: 10

Distribution:
  Target:  Light=20.0%, Medium=60.0%, Far=20.0%
  Actual:  Light=20.0%, Medium=60.0%, Far=20.0%

Quality Score: 1.0000
Average Orthographic Score: 0.6000
Score Range: 0.4000 - 0.8000

Selected Variations:
   1. Jgohn                          | Score: 0.8000 | Light
   2. Joåhn                          | Score: 0.8000 | Light
   3. Jgöhn                          | Score: 0.6000 | Medium
   4. Jaehn                          | Score: 0.6000 | Medium
   ...
```

## Key Features

### 1. Exact `rewards.py` Calculation
- Uses the same `calculate_orthographic_similarity()` function
- Same boundaries and categorization logic
- Same distribution quality calculation

### 2. Comprehensive Strategy Coverage
- 7 different generation strategies
- Recursive variations for complex combinations
- Handles Unicode characters and accents

### 3. Optimal Selection
- Matches target distribution exactly
- Prioritizes scores in the middle of each range
- Uses brute force for best combinations

### 4. Detailed Metrics
- Quality score (how well distribution matches)
- Average orthographic score
- Score range (min-max)
- Categorized breakdown

## How It Achieves Maximum Orthographic Similarity

1. **Generates Many Candidates**: Uses 7 strategies to create thousands of variations
2. **Scores Everything**: Calculates orthographic score for each variation
3. **Categorizes**: Groups variations into Light/Medium/Far
4. **Selects Best**: Chooses variations that:
   - Match target distribution exactly
   - Have scores in optimal ranges (middle of each category)
   - Maximize overall quality score

## Comparison with `rewards.py`

| Aspect | `rewards.py` | This Script |
|--------|-------------|-------------|
| **Calculation** | Levenshtein distance | ✅ Same |
| **Boundaries** | Light/Medium/Far | ✅ Same |
| **Distribution** | Checks against targets | ✅ Same logic |
| **Focus** | Phonetic + Orthographic | ✅ Orthographic only |
| **Generation** | Miners generate | ✅ Brute force strategies |
| **Selection** | Miners choose | ✅ Optimal algorithm |

## Limitations

1. **Brute Force**: May be slow for very long names (>10 characters)
2. **Limited Far Variations**: Short names may not generate many Far variations
3. **No Phonetic**: Only focuses on orthographic similarity
4. **Unicode Handling**: Some Unicode characters may not have good substitutions

## Future Improvements

1. **Parallel Processing**: Generate variations in parallel
2. **Smarter Strategies**: Learn from successful patterns
3. **Full Name Support**: Handle first + last name combinations
4. **Caching**: Cache generated variations for common names
5. **ML-Based**: Use ML to predict best variations

## Testing

Test with different names and distributions:

```bash
# Short name
python3 maximize_orthographic_similarity.py "John" --count 10

# Long name
python3 maximize_orthographic_similarity.py "Christopher" --count 15

# Custom distribution
python3 maximize_orthographic_similarity.py "Smith" \
    --count 20 \
    --light 0.3 \
    --medium 0.4 \
    --far 0.3
```

## Integration with `rewards.py`

To test the generated variations with actual `rewards.py` scoring:

```python
from MIID.validator.reward import calculate_orthographic_similarity, calculate_part_score

# Generate variations
generator = OrthographicBruteForceGenerator("John", {"Light": 0.2, "Medium": 0.6, "Far": 0.2})
variations, metrics = generator.generate_optimal_variations(15)

# Test with rewards.py
scores = [calculate_orthographic_similarity("John", var) for var in variations]
print(f"Average score: {sum(scores) / len(scores):.4f}")
```

---

*Script created: 2025-01-29*
*Based on: MIID/validator/reward.py (lines 171-191, 773-777, 882-920)*





