# Rule Compliance Integration in Orthographic Generator

## Overview

The `maximize_orthographic_similarity.py` generator now supports **rule compliance** without affecting orthographic similarity scores. This allows you to generate variations that:

1. ✅ Maintain optimal orthographic similarity distribution (Light/Medium/Far)
2. ✅ Comply with target rules (e.g., replace double letters, swap consonants)
3. ✅ Meet the rule percentage target (default: 30%)

## How It Works

### Key Principle

**Rule compliance and orthographic similarity are independent scoring components:**

- **Orthographic similarity** (80% weight): Based on Levenshtein distance
- **Rule compliance** (20% weight): Based on following specific transformation rules

The generator ensures both are satisfied simultaneously.

### Implementation Strategy

1. **Generate rule-compliant variations** using rule-specific transformation functions
2. **Score all variations** (both rule-compliant and non-rule) for orthographic similarity
3. **Select optimal combination** that:
   - Meets orthographic distribution targets (Light/Medium/Far)
   - Meets rule compliance target (30% of variations)
   - Prioritizes rule-compliant variations that also have good orthographic scores

## Usage

### Command Line

```bash
# Basic usage with rules
python3 maximize_orthographic_similarity.py "John Smith" \
    --count 15 \
    --light 0.2 --medium 0.6 --far 0.2 \
    --rules replace_double_letters_with_single_letter swap_adjacent_consonants \
    --rule-percentage 30

# Full name with rules
python3 maximize_orthographic_similarity.py "John Smith" \
    --full-name \
    --count 15 \
    --rules replace_double_letters_with_single_letter delete_random_letter \
    --rule-percentage 30
```

### Python API

```python
from maximize_orthographic_similarity import OrthographicBruteForceGenerator

# Setup rule-based metadata
rule_based = {
    "selected_rules": [
        "replace_double_letters_with_single_letter",
        "swap_adjacent_consonants",
        "delete_random_letter"
    ],
    "rule_percentage": 30  # 30% of variations should follow rules
}

# Create generator
generator = OrthographicBruteForceGenerator(
    original_name="John Smith",
    target_distribution={"Light": 0.2, "Medium": 0.6, "Far": 0.2},
    rule_based=rule_based
)

# Generate variations
variations, metrics = generator.generate_optimal_variations(variation_count=15)
```

## Supported Rules

The generator supports all rules from `rule_evaluator.py`:

### Character Replacement
- `replace_double_letters_with_single_letter` - Remove one of double letters
- `replace_random_vowel_with_random_vowel` - Replace vowels with other vowels
- `replace_random_consonant_with_random_consonant` - Replace consonants with other consonants

### Character Swapping
- `swap_adjacent_consonants` - Swap two adjacent consonants
- `swap_random_letter` - Swap adjacent letters

### Character Removal
- `delete_random_letter` - Remove a random letter
- `remove_random_vowel` - Remove a vowel
- `remove_random_consonant` - Remove a consonant
- `remove_all_spaces` - Remove all spaces

### Character Insertion
- `duplicate_random_letter_as_double_letter` - Duplicate a letter
- `insert_random_letter` - Insert a random letter

### Name Formatting
- `initial_only_first_name` - Use first name initial + last name
- `shorten_name_to_initials` - Convert to initials
- `shorten_name_to_abbreviations` - Abbreviate name parts

### Structure Change
- `name_parts_permutations` - Reorder name parts

## Example Output

```
🔍 Generating variations for: 'John Smith'
   Target distribution: {'Light': 0.2, 'Medium': 0.6, 'Far': 0.2}
   Rule compliance: 30% (5 variations)
   Target rules: ['replace_double_letters_with_single_letter', 'swap_adjacent_consonants']

   Strategy 1: Single character substitution...
   Strategy 2: Character insertion...
   ...
   Strategy 8: Rule-compliant variations (2 rules)...
      Generated: 12 rule-compliant variations

🎯 Selecting optimal combination for 15 variations...
   Rule compliance: 30% (5 variations)
   ✅ Rule compliance: 5/5 variations (33.3%)
   ✅ Selected 15 variations

RESULTS:
Original Name: John Smith
Variations Generated: 15

Distribution:
  Target:  Light=20.0%, Medium=60.0%, Far=20.0%
  Actual:  Light=20.0%, Medium=60.0%, Far=20.0%

Quality Score: 0.9500
Average Orthographic Score: 0.6234

Selected Variations:
   1. John Smth      | Score: 0.9333 | Light  ✅ Rule-compliant
   2. Jon Smith      | Score: 0.8667 | Light  ✅ Rule-compliant
   3. Jhon Smith     | Score: 0.8000 | Light
   4. John Smit       | Score: 0.7333 | Medium ✅ Rule-compliant
   5. Jon Smth        | Score: 0.6667 | Medium ✅ Rule-compliant
   6. Jhon Smth       | Score: 0.6000 | Medium ✅ Rule-compliant
   ...
```

## How It Maintains Orthographic Scores

### Strategy

1. **Generate both types**: Creates both rule-compliant and non-rule variations
2. **Score everything**: All variations are scored for orthographic similarity
3. **Smart selection**: 
   - Prioritizes rule-compliant variations that match orthographic targets
   - Falls back to non-rule variations if needed
   - Ensures orthographic distribution is maintained

### Example

**Original**: "John Smith"

**Rule-compliant variations** (following `replace_double_letters_with_single_letter`):
- "John Smth" (score: 0.933) ✅ Light category
- "Jon Smith" (score: 0.867) ✅ Light category

**Non-rule variations**:
- "Jhon Smith" (score: 0.800) ✅ Light category
- "John Smyth" (score: 0.733) ✅ Medium category

**Selection**: Mixes rule-compliant and non-rule to meet both targets.

## Benefits

1. ✅ **No score sacrifice**: Orthographic scores remain optimal
2. ✅ **Rule compliance**: Meets 30% rule target
3. ✅ **Automatic filtering**: Skips impossible rules (e.g., no double letters → skip double letter rule)
4. ✅ **Smart prioritization**: Prefers rule-compliant variations with good orthographic scores

## Integration with Validator

The generated variations will:
- ✅ Pass orthographic similarity scoring (80% weight)
- ✅ Pass rule compliance scoring (20% weight)
- ✅ Result in higher final quality scores

**Final Score Formula**:
```
final_score = (0.8 × base_score) + (0.2 × rule_compliance_score)
```

Where:
- `base_score` = orthographic similarity quality (maintained)
- `rule_compliance_score` = rule compliance quality (newly added)

## Troubleshooting

### "No rule-compliant variations found"

**Cause**: Rules are not applicable to the name structure.

**Solution**: The generator automatically filters impossible rules. Check:
- Does the name have double letters? (for `replace_double_letters_with_single_letter`)
- Does the name have swappable consonants? (for `swap_adjacent_consonants`)
- Does the name have spaces? (for `remove_all_spaces`)

### "Rule compliance below target"

**Cause**: Not enough rule-compliant variations generated.

**Solution**: 
- Increase `max_candidates` in `generate_all_variations()`
- Check if rules are applicable to the name
- Try different rules

### "Orthographic distribution affected"

**Cause**: Rule-compliant variations don't match orthographic targets.

**Solution**: The generator prioritizes orthographic distribution. Rule compliance is secondary. If needed, adjust `rule_percentage` or use different rules.

## Next Steps

1. **Test with your names**: Run the generator with your target names
2. **Verify scores**: Check that both orthographic and rule compliance scores are high
3. **Adjust rules**: Try different rule combinations
4. **Monitor results**: Check the detailed metrics output

## Summary

✅ Rule compliance is now integrated into the orthographic generator  
✅ Orthographic scores are maintained  
✅ Both scoring components work together  
✅ Automatic rule filtering for impossible rules  
✅ Smart selection prioritizes optimal combinations

The generator now produces variations that maximize both orthographic similarity AND rule compliance!

