# Rule Compliance Documentation

## Overview

Rule compliance is a scoring component in the MIID validator that evaluates how well name variations follow specific transformation rules. These rules represent common obfuscation techniques used in sanctions evasion, such as character replacements, swaps, removals, and formatting changes.

**Current Status**: Rule compliance score is currently showing **0.000** in test outputs, indicating that the orthographic generator is not producing rule-compliant variations.

---

## 1. How Rule Compliance is Used in Query Templates

### 1.1 Query Generation Process

When the validator generates a query, it includes rule-based requirements in the prompt sent to miners:

```python
# From query_generator.py
rule_template, rule_metadata = get_rule_template_and_metadata(rule_percentage)

labels = {
    "variation_count": variation_count,
    "phonetic_similarity": phonetic_similarity,
    "orthographic_similarity": orthographic_similarity,
    "rule_based": {**(rule_metadata or {}), "percentage": rule_percentage},
}
```

### 1.2 Rule Template Format

The query template includes instructions like:

```
Generate 15 variations of {name}, ensuring phonetic similarity: 100% Medium, 
and orthographic similarity: 100% Medium, and also include 30% of variations 
that follow: Additionally, generate variations that perform these transformations: 
Replace double letters with a single letter, Swap adjacent consonants, 
and Delete a random letter.
```

### 1.3 Rule Selection

Rules are randomly selected from 6 categories:

1. **Character Replacement**
   - `replace_spaces_with_random_special_characters`
   - `replace_double_letters_with_single_letter`
   - `replace_random_vowel_with_random_vowel`
   - `replace_random_consonant_with_random_consonant`

2. **Character Swapping**
   - `swap_adjacent_consonants`
   - `swap_adjacent_syllables`
   - `swap_random_letter`

3. **Character Removal**
   - `delete_random_letter`
   - `remove_random_vowel`
   - `remove_random_consonant`
   - `remove_all_spaces`

4. **Character Insertion**
   - `duplicate_random_letter_as_double_letter`
   - `insert_random_letter`
   - `add_random_leading_title`
   - `add_random_trailing_title`

5. **Name Formatting**
   - `initial_only_first_name`
   - `shorten_name_to_initials`
   - `shorten_name_to_abbreviations`

6. **Structure Change**
   - `name_parts_permutations`

**Selection**: 1-3 rules are randomly selected per query.

**Rule Percentage**: Default is 30%, meaning 30% of variations should follow the selected rules.

---

## 2. What the Validator Needs (rule_based Metadata)

### 2.1 Rule-Based Metadata Structure

The validator expects a `rule_based` dictionary in the query labels:

```python
rule_based = {
    "rule_percentage": 30,  # Percentage of variations that should follow rules
    "selected_rules": [     # List of rule names to check
        "replace_double_letters_with_single_letter",
        "swap_adjacent_consonants",
        "delete_random_letter"
    ],
    "rule_descriptions": {   # Human-readable descriptions
        "replace_double_letters_with_single_letter": "Replace double letters with a single letter",
        "swap_adjacent_consonants": "Swap adjacent consonants",
        "delete_random_letter": "Delete a random letter"
    }
}
```

### 2.2 How Metadata is Passed to Scoring

The `rule_based` metadata is passed to `calculate_variation_quality()`:

```python
def calculate_variation_quality(
    original_name: str,
    variations: List[str],
    phonetic_similarity: Dict[str, float] = None,
    orthographic_similarity: Dict[str, float] = None,
    expected_count: int = 10,
    rule_based: Dict[str, Any] = None  # Rule-based metadata
) -> Tuple[float, Dict]:
```

### 2.3 Rule Applicability Filtering

The validator automatically filters out rules that are impossible for a given name:

- **Multi-part name required**: `name_parts_permutations`, `initial_only_first_name`, `shorten_name_to_initials`, `shorten_name_to_abbreviations`
- **Space required**: `replace_spaces_with_random_special_characters`, `remove_all_spaces`
- **Double letters required**: `replace_double_letters_with_single_letter`
- **Swappable consonants required**: `swap_adjacent_consonants`

If no rules are applicable, the validator:
- Sets `rule_compliance_weight = 0.0`
- Uses only the base score (similarity, count, uniqueness, length)
- Returns a rule compliance score of `1.0` (no penalty)

---

## 3. How Scoring is Done for Rule Compliance

### 3.1 Scoring Formula

Rule compliance is integrated into the final quality score using a weighted combination:

```python
# From reward.py
rule_compliance_weight = 0.20  # 20% weight
base_weight = 1.0 - rule_compliance_weight  # 80% weight

final_score = (base_weight * base_score) + (rule_compliance_weight * rule_compliance_score)
```

**Components**:
- **Base Score** (80%): Similarity, count, uniqueness, length scores
- **Rule Compliance Score** (20%): Rule compliance score

### 3.2 Rule Compliance Score Calculation

The rule compliance score is calculated in `calculate_rule_compliance_score()`:

#### Step 1: Evaluate Rule Compliance

```python
compliant_variations_by_rule, compliance_ratio = evaluate_rule_compliance(
    original_name, 
    variations, 
    target_rules
)
```

This returns:
- `compliant_variations_by_rule`: Dict mapping each rule to list of compliant variations
- `compliance_ratio`: Ratio of variations that matched any rule

#### Step 2: Calculate Quantity Score

```python
expected_compliant_count = max(1, int(len(variations) * target_percentage))
overall_compliant_count = len(rules_satisfied_by_variation)

ratio_of_actual_to_expected = overall_compliant_count / expected_compliant_count

if ratio_of_actual_to_expected <= 0.0:
    quantity_score = 0.0
elif ratio_of_actual_to_expected <= 1.0:  # At or below target
    quantity_score = ratio_of_actual_to_expected
else:  # Above target - apply a gentler penalty
    quantity_score = max(0.5, 1.5 - 0.5 * ratio_of_actual_to_expected)
```

**Example**:
- Target: 30% of 15 variations = 4.5 → 5 expected
- Actual: 3 compliant variations
- Ratio: 3/5 = 0.6
- Quantity Score: 0.6

#### Step 3: Calculate Rule Diversity Factor

```python
num_target_rules_met = len(satisfied_effective_rules)
effective_rules_count = len(compliant_variations_by_rule)

rule_diversity_factor = num_target_rules_met / effective_rules_count
```

**Example**:
- Target rules: 3 rules
- Effective rules (after filtering): 2 rules
- Rules satisfied: 1 rule
- Diversity Factor: 1/2 = 0.5

#### Step 4: Final Rule Compliance Score

```python
final_score = quantity_score * rule_diversity_factor
```

**Example**:
- Quantity Score: 0.6
- Diversity Factor: 0.5
- Final Score: 0.6 × 0.5 = **0.3**

### 3.3 Special Cases

#### No Rules Applicable

If no rules are applicable to the name structure:
- Returns score of `1.0` (no penalty)
- Sets `rule_compliance_weight = 0.0`
- Final score uses only base score

#### No Compliant Variations

If no variations comply with any rule:
- `quantity_score = 0.0`
- `rule_diversity_factor = 0.0`
- Final score: `0.0`

#### All Variations Compliant

If all variations comply (over-target):
- `ratio_of_actual_to_expected > 1.0`
- `quantity_score = max(0.5, 1.5 - 0.5 * ratio)`
- Example: 10/5 = 2.0 → `1.5 - 0.5 * 2.0 = 0.5`

---

## 4. Detailed Metrics Returned

The rule compliance calculation returns detailed metrics:

```python
{
    "compliant_variations_by_rule": {
        "replace_double_letters_with_single_letter": ["John Smth", "Jane Do"],
        "swap_adjacent_consonants": ["John Smth"]
    },
    "rules_satisfied_by_variation": {
        "John Smth": ["replace_double_letters_with_single_letter", "swap_adjacent_consonants"],
        "Jane Do": ["replace_double_letters_with_single_letter"]
    },
    "compliance_ratio_overall_variations": 0.133,  # 2/15
    "overall_compliant_unique_variations_count": 2,
    "expected_compliant_variations_count": 5,
    "quantity_score": 0.4,  # 2/5
    "rule_diversity_factor": 0.5,  # 1/2 rules satisfied
    "num_target_rules_met": 1,
    "total_target_rules": 3,
    "score": 0.2  # 0.4 × 0.5
}
```

---

## 5. Integration with Overall Scoring

### 5.1 Final Quality Score Formula

```python
# Step 1: Calculate base score (similarity, count, uniqueness, length)
base_score = (first_name_weight * first_name_score) + (last_name_weight * last_name_score)

# Step 2: Calculate rule compliance score
rule_compliance_score = calculate_rule_compliance_score(...)

# Step 3: Combine with weights
final_score = (0.8 * base_score) + (0.2 * rule_compliance_score)
```

### 5.2 Impact on Final Reward

Rule compliance affects the final reward through the quality score:

```
Identity Quality = (Names × 0.2) + (DOB × 0.1) + (Address × 0.7)

Where Names = final_score (which includes rule compliance)
```

**Example**:
- Base score: 0.8
- Rule compliance: 0.0 (no compliant variations)
- Final score: (0.8 × 0.8) + (0.2 × 0.0) = **0.64**
- Names component: 0.64 × 0.2 = **0.128**

---

## 6. Why Rule Compliance is Currently 0.000

### 6.1 Current Generator Behavior

The orthographic generator (`maximize_orthographic_similarity.py`) focuses on:
- Character substitutions
- Insertions/deletions
- Transpositions
- Visual similar replacements

**It does NOT implement rule-based transformations** like:
- Replacing double letters with single letters
- Swapping adjacent consonants
- Removing all spaces
- Converting to initials

### 6.2 How to Fix

To achieve rule compliance, the generator needs to:

1. **Detect rule requirements** from the query (if provided)
2. **Generate rule-compliant variations** for the target percentage
3. **Mix rule-compliant and non-rule-compliant variations**

**Example Implementation**:
```python
def generate_rule_compliant_variation(original_name: str, rule: str) -> str:
    if rule == "replace_double_letters_with_single_letter":
        # Find double letters and replace with single
        for i in range(len(original_name) - 1):
            if original_name[i] == original_name[i+1]:
                return original_name[:i] + original_name[i+1:]
    elif rule == "swap_adjacent_consonants":
        # Find adjacent consonants and swap
        # ... implementation
    # ... other rules
    return original_name
```

---

## 7. Examples

### Example 1: Perfect Rule Compliance

**Original Name**: "John Smith"  
**Target Rules**: `["replace_double_letters_with_single_letter", "swap_adjacent_consonants"]`  
**Target Percentage**: 30% (5 out of 15 variations)

**Variations**:
- Rule-compliant (5): "John Smth", "Jon Smith", "John Smit", "Jhon Smith", "John Smih"
- Non-rule-compliant (10): "John Smyth", "Jon Smyth", etc.

**Calculation**:
- Compliant count: 5
- Expected: 5
- Ratio: 5/5 = 1.0
- Quantity Score: 1.0
- Rules satisfied: 2/2
- Diversity Factor: 1.0
- **Rule Compliance Score: 1.0**

### Example 2: Partial Rule Compliance

**Original Name**: "John Smith"  
**Target Rules**: `["replace_double_letters_with_single_letter", "swap_adjacent_consonants"]`  
**Target Percentage**: 30% (5 out of 15 variations)

**Variations**:
- Rule-compliant (2): "John Smth", "Jon Smith"
- Non-rule-compliant (13): "John Smyth", etc.

**Calculation**:
- Compliant count: 2
- Expected: 5
- Ratio: 2/5 = 0.4
- Quantity Score: 0.4
- Rules satisfied: 1/2 (only double letter replacement)
- Diversity Factor: 0.5
- **Rule Compliance Score: 0.2**

### Example 3: No Rule Compliance

**Original Name**: "John Smith"  
**Target Rules**: `["replace_double_letters_with_single_letter"]`  
**Target Percentage**: 30% (5 out of 15 variations)

**Variations**:
- Rule-compliant (0): None
- Non-rule-compliant (15): All variations

**Calculation**:
- Compliant count: 0
- Expected: 5
- Ratio: 0/5 = 0.0
- Quantity Score: 0.0
- **Rule Compliance Score: 0.0**

---

## 8. Summary

### Key Points

1. **Rule compliance is 20% of the quality score** (combined with 80% base score)
2. **Rules are randomly selected** (1-3 rules per query, 30% target percentage)
3. **Rules are filtered** for applicability (e.g., no double letters → skip double letter rule)
4. **Scoring combines quantity and diversity**:
   - Quantity: How many variations comply vs. expected
   - Diversity: How many different rules are satisfied
5. **Current generator doesn't implement rules**, resulting in 0.000 score

### Impact on Final Reward

- **Without rule compliance**: Names component reduced by up to 20%
- **With perfect rule compliance**: Full quality score maintained
- **Example**: Base score 0.8 → Final score 0.64 (without rules) vs. 0.8 (with rules)

### Next Steps

To improve rule compliance scores:
1. Implement rule-based transformation functions
2. Detect rule requirements from query metadata
3. Generate rule-compliant variations for target percentage
4. Mix rule-compliant and non-rule-compliant variations appropriately

