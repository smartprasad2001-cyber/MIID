# Orthographic Similarity Generator - How It Works

## Overview

The `maximize_orthographic_similarity.py` script is a brute-force generator that creates name variations with maximum orthographic similarity scores. It reverse-engineers the `rewards.py` orthographic similarity calculation and uses multiple strategies to generate variations that match target distributions.

## Core Concept

**Orthographic Similarity** measures how visually similar two names are based on spelling, using the **Levenshtein distance** algorithm.

### Formula
```
Orthographic Score = 1.0 - (Levenshtein_distance / max_length)
```

Where:
- `Levenshtein_distance`: Minimum number of single-character edits (insertions, deletions, substitutions) needed to transform one string into another
- `max_length`: Maximum length of the two strings
- Result: Score between 0.0 (completely different) and 1.0 (identical)

### Categories

Variations are categorized by their orthographic score:

- **Light** (0.70 - 1.00): High similarity - very close to original
- **Medium** (0.50 - 0.69): Moderate similarity - noticeable differences
- **Far** (0.20 - 0.49): Low similarity - significant differences
- **Below** (< 0.20): Too different (usually rejected)

## Architecture

### Main Class: `OrthographicBruteForceGenerator`

The generator is initialized with:
- `original_name`: The name to generate variations for
- `target_distribution`: Desired ratio of Light/Medium/Far (e.g., `{"Light": 0.2, "Medium": 0.6, "Far": 0.2}`)
- `rule_based`: Optional rule compliance requirements

## Generation Strategies

The generator uses **50+ different strategies** to create variations:

### 1. Basic Character Operations

#### Single Character Substitution
- Replaces each character with visually similar alternatives
- Example: `a → e, o, u, à, á, â, ã, ä, å`
- Similarity map includes:
  - Vowels: `a, e, i, o, u` with accented variants
  - Consonants: `c↔k↔s`, `b↔p↔d`, `m↔n`, `r↔l`, etc.

#### Character Insertion
- Inserts similar-looking characters at various positions
- Tries inserting vowels (`a, e, i, o, u, h, y`) and similar characters to adjacent ones

#### Character Deletion
- Removes characters that might be redundant or silent
- Can delete 1, 2, 3+ letters depending on target category

#### Character Transposition
- Swaps adjacent characters (common typing errors)
- Example: `John` → `Jhon`, `Jonh`

### 2. Advanced Pattern Manipulations

#### Double Character Variations
- Removes one of double letters: `Smith` → `Smit`
- Adds double letters: `John` → `Johhn`
- Replaces doubles with similar patterns

#### Visual Similar Replacements
- Replaces character patterns that look similar:
  - `rn` ↔ `m` (e.g., `burn` ↔ `bum`)
  - `cl` ↔ `d`
  - `ij` ↔ `y`
  - `vv` ↔ `w`
  - `ii` ↔ `y`

### 3. Comprehensive Multi-Strategy Generation

The `generate_all_strategies_comprehensive()` function uses **recursive depth-first generation** with up to 6 levels of depth, applying 50+ strategies:

1. **Remove letters** (1-6 letters)
2. **Add vowels** at different positions
3. **Change vowels** to other vowels
4. **Change consonants** to other consonants
5. **Swap adjacent letters**
6. **Swap non-adjacent letters**
7. **Insert ALL letters** at ALL positions
8. **Remove multiple letters** (2-6 letters)
9. **Insert vowel combinations** (`ae`, `ai`, `ao`, etc.)
10. **Insert letter pairs**
11. **Replace with phonetic equivalents** (`ph` ↔ `f`, `c` ↔ `k`, etc.)
12. **Duplicate letters**
13. **Remove duplicate letters**
14. **Rotate letters** (3-letter rotation)
15. **Reverse substrings**
16. **Insert common letter pairs** (`th`, `sh`, `ch`, `ph`, etc.)
17. **Add prefixes/suffixes**
18. **Split and insert letters**
19. **Move letters** to different positions
20. **Replace with similar-looking letters** (visual similarity)
21. **Cyclic shift** characters
22. **Remove every other letter** (for Far variations)
23. **Duplicate word segments**
24. **Replace vowels with 'y' or 'w'**
25. And 25+ more strategies...

### 4. Rule-Based Generation

The generator supports **22 different rule-based transformations**:

#### Letter Manipulation Rules
- `replace_double_letters_with_single_letter`: `Smith` → `Smit`
- `swap_adjacent_consonants`: `John` → `Jhon`
- `delete_random_letter`: `John` → `Jon`, `Jhn`
- `delete_random_vowel`: `John` → `Jhn`
- `delete_random_consonant`: `John` → `Jon`
- `replace_random_vowel_with_random_vowel`: `John` → `Jahn`, `Jehn`
- `replace_random_consonant_with_random_consonant`: `John` → `Jonn`, `Jokn`
- `swap_random_letter`: `John` → `Jhon`, `Jonh`
- `insert_random_letter`: `John` → `Johon`, `Johan`
- `duplicate_random_letter_as_double_letter`: `John` → `Johhn`

#### Space Manipulation Rules
- `remove_all_spaces`: `John Smith` → `JohnSmith`
- `replace_spaces_with_random_special_characters`: `John Smith` → `John-Smith`, `John_Smith`

#### Special Character Rules
- `remove_random_special_character`: Removes special characters if present

#### Title/Suffix Rules
- `remove_title`: `Mr. John` → `John`
- `add_random_leading_title`: `John` → `Mr. John`, `Dr. John`
- `add_random_trailing_title`: `John` → `John Jr.`, `John Sr.`

#### Name Structure Rules
- `initial_only_first_name`: `John Smith` → `J. Smith`
- `shorten_name_to_initials`: `John Smith` → `J. S.`
- `shorten_name_to_abbreviations`: `John` → `Jn.`, `Jhn.`
- `name_parts_permutations`: `John Smith` → `Smith John`

### 5. Category-Targeted Rule Generation

The generator can target specific orthographic categories when applying rules:

- **Light (0.70-1.00)**: Uses single-letter operations (`aggression=1`)
  - Delete 1 letter
  - Insert 1 letter
  - Swap 1 pair of letters

- **Medium (0.50-0.69)**: Uses rules that naturally produce moderate changes
  - Space removal/replacement
  - Vowel/consonant replacement
  - Letter duplication

- **Far (0.20-0.49)**: Uses rules that produce large changes
  - Initials/abbreviations
  - Name permutations
  - Multiple letter deletions

## Generation Workflow

### Step 1: Generate All Variations

```python
categorized = generator.generate_all_variations(max_candidates=10000)
```

This generates variations using:
1. Single character substitution
2. Character insertion
3. Character deletion
4. Character transposition
5. Double character variations
6. Visual similar replacements
7. Comprehensive 50-strategy generation (recursive, depth 6)

All variations are then:
- Scored using `calculate_orthographic_similarity()` (same as `rewards.py`)
- Categorized into Light/Medium/Far/Below
- Stored in a dictionary by category

### Step 2: Generate Rule-Compliant Variations (if rules specified)

```python
rule_compliant_scored = generator.generate_rule_compliant_variations_with_scores()
```

For each rule:
1. Generate variations following that rule
2. Score each variation for orthographic similarity
3. Categorize by Light/Medium/Far
4. Sort by score (descending)

### Step 3: Category-Targeted Rule Generation

```python
rule_compliant_by_category = {
    "Light": generator.generate_rule_compliant_by_category("Light", rules),
    "Medium": generator.generate_rule_compliant_by_category("Medium", rules),
    "Far": generator.generate_rule_compliant_by_category("Far", rules)
}
```

This ensures rule-compliant variations are distributed across all categories, not just Light.

### Step 4: Select Optimal Combination

#### Without Rules:
```python
selected = generator.select_optimal_combination(categorized, variation_count)
```

Algorithm:
1. Calculate target counts for each category based on distribution
2. Select highest-scoring variations from Light category
3. Select variations closest to 0.60 from Medium category
4. Select variations closest to 0.35 from Far category
5. If needed, use brute force to find best combination matching distribution

#### With Rules:
```python
selected = generator.select_optimal_combination_with_rules(
    categorized, rule_compliant_scored, variation_count
)
```

Algorithm (3-phase approach):

**Phase 1: Fill each category with rule-compliant variations (priority)**
- For each category (Light, Medium, Far):
  - Take as many rule-compliant variations as possible (up to target rule count)
  - Fill remaining slots with non-rule-compliant variations

**Phase 2: Add more rule-compliant if needed**
- If rule compliance percentage not met, add rule-compliant variations from any category

**Phase 3: Fill remaining slots**
- Add non-rule-compliant variations to reach `variation_count`

## Key Features

### 1. Exact Scoring Match

The generator uses the **exact same scoring function** as `rewards.py`:
```python
from reward import calculate_orthographic_similarity
score = calculate_orthographic_similarity(original_name, variation)
```

This ensures generated variations will score identically in the validator.

### 2. Distribution Matching

The generator tries to match the target distribution as closely as possible:
- Calculates target counts: `target_count = distribution_percentage * total_count`
- Selects variations from each category to match targets
- Uses brute force optimization if needed to find best combination

### 3. Rule Compliance Distribution

When rules are specified:
- Generates rule-compliant variations for **each category** (Light, Medium, Far)
- Distributes rule compliance across categories (not just Light)
- Uses `aggression` parameter to control how many changes are made:
  - `aggression=1`: Light changes (1 letter operation)
  - `aggression=2`: Medium changes (2 letter operations)
  - `aggression=3+`: Far changes (3+ letter operations)

### 4. Rule Filtering

Before generating, the generator filters out impossible rules:
- `name_parts_permutations`: Requires multi-part name (skipped for single names)
- `remove_all_spaces`: Requires spaces in name (skipped if no spaces)
- `replace_double_letters`: Requires double letters (skipped if none)
- `swap_adjacent_consonants`: Requires swappable consonants (skipped if none)

### 5. Comprehensive Strategy Coverage

The generator uses **50+ strategies** with recursive depth-first search:
- Starts with original name
- Applies all strategies at depth 0
- Recursively applies strategies to generated variations (up to depth 6)
- This creates millions of potential variations

### 6. Quality Optimization

The generator uses a quality score to evaluate combinations:
```python
quality = _calculate_distribution_quality(scores, target_distribution)
```

This measures how well a combination matches the target distribution, allowing brute force optimization to find the best set of variations.

## Example Workflow

### Input
```python
generator = OrthographicBruteForceGenerator(
    original_name="John Smith",
    target_distribution={"Light": 0.2, "Medium": 0.6, "Far": 0.2},
    rule_based={
        "selected_rules": ["swap_adjacent_consonants", "remove_all_spaces"],
        "rule_percentage": 30
    }
)
```

### Process
1. **Generate all variations** (10,000+ candidates)
   - Single char substitution: `John` → `Jahn`, `Jehn`, `Jonn`, etc.
   - Char insertion: `John` → `Johon`, `Johan`, `Johhn`, etc.
   - Char deletion: `John` → `Jon`, `Jhn`, `Joh`, etc.
   - Transposition: `John` → `Jhon`, `Jonh`
   - Comprehensive strategies: 50+ strategies, depth 6

2. **Score and categorize**
   - Light: `Jhon` (0.95), `Jahn` (0.88), `Johhn` (0.82), ...
   - Medium: `Jon` (0.67), `Johan` (0.60), `Jhohn` (0.55), ...
   - Far: `J. S.` (0.35), `Jhn` (0.42), `J. Smith` (0.28), ...

3. **Generate rule-compliant variations**
   - `swap_adjacent_consonants`: `John Smith` → `Jhon Smith` (Light)
   - `remove_all_spaces`: `John Smith` → `JohnSmith` (Medium)
   - Category-targeted: Generate rule-compliant for Light, Medium, Far

4. **Select optimal combination** (15 variations)
   - Target: 3 Light, 9 Medium, 3 Far
   - Target rule-compliant: 5 variations (30%)
   - Phase 1: Fill each category with rule-compliant (priority)
   - Phase 2: Add more rule-compliant if needed
   - Phase 3: Fill remaining with non-rule-compliant

### Output
```python
variations = [
    "Jhon Smith",      # Light, rule-compliant (swap consonants)
    "Jahn Smith",      # Light
    "Johhn Smith",     # Light
    "JohnSmith",       # Medium, rule-compliant (remove spaces)
    "Jon Smith",       # Medium
    "Johan Smith",     # Medium
    # ... 9 more variations
]
```

## Performance Considerations

### Computational Complexity

- **Basic strategies**: O(n) to O(n²) per strategy
- **Comprehensive generation**: O(n^d) where d = depth (up to 6)
- **Brute force optimization**: Up to 5,000 random combinations tested

### Optimization Techniques

1. **Early termination**: Stops when enough variations found
2. **Caching**: Stores generated variations to avoid duplicates
3. **Limits**: `max_candidates` and `max_variations` parameters prevent explosion
4. **Filtering**: Removes impossible rules before generation
5. **Smart selection**: Prioritizes high-quality variations

## Integration with Validator

The generator is designed to work seamlessly with the validator:

1. **Same scoring function**: Uses `calculate_orthographic_similarity()` from `rewards.py`
2. **Same boundaries**: Uses `ORTHOGRAPHIC_BOUNDARIES` from `rewards.py`
3. **Same categorization**: Light (0.70-1.00), Medium (0.50-0.69), Far (0.20-0.49)
4. **Rule compliance**: Uses `evaluate_rule_compliance()` from `rule_evaluator.py`

This ensures that variations generated by this script will score identically when validated by the validator.

## Summary

The orthographic generator is a comprehensive brute-force system that:

1. **Generates millions of variations** using 50+ strategies
2. **Scores each variation** using the exact same method as the validator
3. **Categorizes by similarity** (Light/Medium/Far)
4. **Matches target distribution** as closely as possible
5. **Supports rule compliance** with category-targeted generation
6. **Optimizes selection** to find the best combination

The result is a set of name variations that maximize orthographic similarity scores while meeting distribution and rule compliance requirements.

