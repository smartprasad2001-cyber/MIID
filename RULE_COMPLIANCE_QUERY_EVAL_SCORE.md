# Rule Compliance: Query, Evaluation, and Scoring

## Overview

This document explains the complete flow of rule compliance in the MIID validator:
1. **Query Generation** - How rules are included in queries sent to miners
2. **Rule Evaluation** - How variations are checked against rules
3. **Scoring** - How rule compliance is scored and integrated into rewards

---

## Part 1: Query Generation

### Step 1: Rule Selection

**Location**: `MIID/validator/rule_extractor.py`

The query generator randomly selects 1-3 rules from available rule categories:

```python
def get_rule_template_and_metadata(rule_percentage: int = 30) -> Tuple[str, Dict[str, Any]]:
    # Select 1-3 random rules
    n_rules = random.randint(1, 3)
    selected_rules = get_random_rules(n_rules)
    
    # Format rules into natural language
    rule_template = format_rules_for_query(selected_rules)
    
    # Create metadata
    metadata = {
        "rule_percentage": rule_percentage,  # e.g., 30
        "selected_rules": selected_rules,    # e.g., ["replace_double_letters_with_single_letter", "swap_adjacent_consonants"]
        "rule_descriptions": {rule: get_rule_description(rule) for rule in selected_rules}
    }
    
    return rule_template, metadata
```

**Example Output**:
```python
rule_template = "Additionally, generate variations that: Replace double letters with a single letter, and Swap adjacent consonants."
metadata = {
    "rule_percentage": 30,
    "selected_rules": ["replace_double_letters_with_single_letter", "swap_adjacent_consonants"],
    "rule_descriptions": {
        "replace_double_letters_with_single_letter": "Replace double letters with a single letter",
        "swap_adjacent_consonants": "Swap adjacent consonants"
    }
}
```

### Step 2: Query Template Generation

**Location**: `MIID/validator/query_generator.py` → `generate_complex_query()`

The query generator creates a natural-language prompt that includes:

1. **Variation count** (e.g., 15 variations)
2. **Phonetic similarity** requirements (e.g., 60% Medium)
3. **Orthographic similarity** requirements (e.g., 60% Medium)
4. **Rule compliance** requirements (e.g., 30% should follow rules)

**Query Template Example**:
```
Generate exactly 15 variations of a target identity represented by {name}.
Ensure the generated variations reflect:
- Phonetic similarity (sound-alike names) based on: 60% Medium
- Orthographic similarity (visual similarity) based on: 60% Medium
Make sure approximately 30% of all generated variations follow the rule-based transformations below (as a group, not per rule):
Additionally, generate variations that: Replace double letters with a single letter, and Swap adjacent consonants.
```

**Key Points**:
- Rule percentage applies to **ALL rules combined** (not per rule)
- Rules are described in natural language
- The query is sent to miners via LLM (Ollama/Gemini)

### Step 3: Labels/Metadata Storage

**Location**: `MIID/validator/query_generator.py` → `generate_complex_query()`

The query generator stores metadata in `labels`:

```python
labels = {
    "variation_count": 15,
    "phonetic_similarity": {"Medium": 0.6, "Light": 0.2, "Far": 0.2},
    "orthographic_similarity": {"Medium": 0.6, "Light": 0.2, "Far": 0.2},
    "rule_based": {
        "rule_percentage": 30,
        "percentage": 30,  # Duplicate for compatibility
        "selected_rules": ["replace_double_letters_with_single_letter", "swap_adjacent_consonants"],
        "rule_descriptions": {
            "replace_double_letters_with_single_letter": "Replace double letters with a single letter",
            "swap_adjacent_consonants": "Swap adjacent consonants"
        }
    }
}
```

This metadata is used later for evaluation and scoring.

---

## Part 2: Rule Evaluation

### Step 1: Filter Impossible Rules

**Location**: `MIID/validator/rule_evaluator.py` → `evaluate_rule_compliance()`

Before evaluation, rules that are impossible for the name structure are filtered out:

```python
effective_rules = []
for rule in rules:
    # Rule: Name parts permutations / initials (require multi-part name)
    if rule in ('name_parts_permutations', 'initial_only_first_name', ...) and len(original_name.split()) < 2:
        continue  # Skip - single-part name can't use this rule
    
    # Rule: Space removal/replacement (requires a space)
    if rule in ('replace_spaces_with_random_special_characters', 'remove_all_spaces') and ' ' not in original_name:
        continue  # Skip - no spaces in name
    
    # Rule: Double letter replacement (requires double letters)
    if rule == 'replace_double_letters_with_single_letter' and not has_double_letters(original_name):
        continue  # Skip - no double letters
    
    # Rule: Adjacent consonant swap (requires swappable consonants)
    if rule == 'swap_adjacent_consonants' and not has_diff_adjacent_consonants(original_name):
        continue  # Skip - no swappable consonants
    
    effective_rules.append(rule)
```

**Example**:
- Original name: `"John"` (single word, no double letters)
- Target rules: `["replace_double_letters_with_single_letter", "swap_adjacent_consonants", "name_parts_permutations"]`
- Effective rules: `["swap_adjacent_consonants"]` (only one possible)

### Step 2: Check Each Variation Against Rules

**Location**: `MIID/validator/rule_evaluator.py` → `evaluate_rule_compliance()`

For each variation, check if it complies with any effective rule:

```python
compliant_variations = {rule: [] for rule in effective_rules}
all_compliant_variations = set()

for variation in variations:
    for rule in effective_rules:
        if rule in RULE_EVALUATORS:
            if RULE_EVALUATORS[rule](original_name, variation):
                compliant_variations[rule].append(variation)
                all_compliant_variations.add(variation)
```

**Example**:
- Original: `"John Smith"`
- Variation 1: `"Jhon Smith"` → ✅ Complies with `swap_adjacent_consonants`
- Variation 2: `"Jon Smith"` → ✅ Complies with `delete_random_letter`
- Variation 3: `"John Smyth"` → ❌ No rule compliance

**Result**:
```python
compliant_variations = {
    "swap_adjacent_consonants": ["Jhon Smith"],
    "delete_random_letter": ["Jon Smith"]
}
all_compliant_variations = {"Jhon Smith", "Jon Smith"}
compliance_ratio = 2 / 15 = 0.133  # 2 out of 15 variations comply
```

### Step 3: Rule Evaluator Functions

**Location**: `MIID/validator/rule_evaluator.py`

Each rule has a dedicated evaluator function:

#### Example 1: Double Letter Replacement
```python
def is_double_letter_replaced(original: str, variation: str) -> bool:
    """Check if a double letter in the original is replaced with a single letter"""
    original_lower = original.lower()
    
    # Early exit if no double letters
    if not any(original_lower[i] == original_lower[i+1] for i in range(len(original_lower) - 1)):
        return False
    
    variation_lower = variation.lower()
    if len(variation_lower) != len(original_lower) - 1:
        return False
    
    # Check if removing one double letter creates the variation
    for i in range(len(original_lower) - 1):
        if original_lower[i] == original_lower[i+1] and original_lower[i].isalpha():
            candidate = original_lower[:i] + original_lower[i+1:]
            if candidate == variation_lower:
                return True
    
    return False
```

**Example**:
- Original: `"John"` → No double letters → Returns `False`
- Original: `"William"` → Has `"ll"` → Check if variation is `"Wilam"` → Returns `True`

#### Example 2: Consonant Swap
```python
def is_adjacent_consonants_swapped(original: str, variation: str) -> bool:
    """Check if two adjacent consonants are swapped"""
    original_lower = original.lower()
    variation_lower = variation.lower()
    
    if len(original_lower) != len(variation_lower) or original_lower == variation_lower:
        return False
    
    # Check each pair of adjacent consonants
    for i in range(len(original_lower) - 1):
        if is_consonant(original_lower[i]) and is_consonant(original_lower[i+1]):
            test_str = list(original_lower)
            test_str[i], test_str[i+1] = test_str[i+1], test_str[i]
            if "".join(test_str) == variation_lower:
                return True
    
    return False
```

**Example**:
- Original: `"John"` → Swap `"h"` and `"n"` → `"Jhon"` → Returns `True`
- Original: `"John"` → Variation: `"Jon"` → Different length → Returns `False`

---

## Part 3: Scoring

### Step 1: Calculate Rule Compliance Score

**Location**: `MIID/validator/reward.py` → `calculate_rule_compliance_score()`

The scoring function calculates how well variations meet rule compliance requirements:

```python
def calculate_rule_compliance_score(
    original_name: str,
    variations: List[str],
    target_rules: List[str],
    target_percentage: float = 0.3  # 30%
) -> Tuple[float, Dict]:
```

### Step 2: Evaluate Compliance

```python
# Get compliant variations by rule
compliant_variations_by_rule, compliance_ratio = evaluate_rule_compliance(
    original_name, 
    variations, 
    target_rules
)

# Map each variation to rules it satisfies
rules_satisfied_by_variation = {}
for rule, rule_compliant_variations_list in compliant_variations_by_rule.items():
    for variation in rule_compliant_variations_list:
        if variation not in rules_satisfied_by_variation:
            rules_satisfied_by_variation[variation] = []
        rules_satisfied_by_variation[variation].append(rule)
```

**Example**:
```python
compliant_variations_by_rule = {
    "swap_adjacent_consonants": ["Jhon Smith", "Jhon Smyth"],
    "delete_random_letter": ["Jon Smith"]
}
rules_satisfied_by_variation = {
    "Jhon Smith": ["swap_adjacent_consonants"],
    "Jhon Smyth": ["swap_adjacent_consonants"],
    "Jon Smith": ["delete_random_letter"]
}
overall_compliant_count = 3  # 3 unique variations comply
```

### Step 3: Calculate Quantity Score

**Formula**: How many variations comply vs. expected count

```python
expected_compliant_count = max(1, int(len(variations) * target_percentage))
# Example: 15 variations * 0.30 = 4.5 → 5 expected

ratio_of_actual_to_expected = overall_compliant_count / expected_compliant_count
# Example: 3 / 5 = 0.60

quantity_score = 0.0
if ratio_of_actual_to_expected <= 0.0:
    quantity_score = 0.0
elif ratio_of_actual_to_expected <= 1.0:  # At or below target
    quantity_score = ratio_of_actual_to_expected  # Linear: 0.60 → 0.60
else:  # Above target - apply penalty
    quantity_score = max(0.5, 1.5 - 0.5 * ratio_of_actual_to_expected)
    # Example: 2.0 ratio → 1.5 - 0.5*2.0 = 0.5
```

**Scoring Examples**:
- **0 compliant** (expected 5): `ratio = 0/5 = 0.0` → `quantity_score = 0.0`
- **3 compliant** (expected 5): `ratio = 3/5 = 0.6` → `quantity_score = 0.6`
- **5 compliant** (expected 5): `ratio = 5/5 = 1.0` → `quantity_score = 1.0`
- **10 compliant** (expected 5): `ratio = 10/5 = 2.0` → `quantity_score = 0.5` (penalty)

### Step 4: Calculate Rule Diversity Factor

**Formula**: How many different rules are satisfied

```python
# Count how many target rules were satisfied by at least one variation
satisfied_effective_rules = set()
for rule_name, compliant_vars_for_rule_list in compliant_variations_by_rule.items():
    if compliant_vars_for_rule_list:  # Rule was satisfied
        satisfied_effective_rules.add(rule_name)

num_target_rules_met = len(satisfied_effective_rules)
effective_rules_count = len(compliant_variations_by_rule)

if effective_rules_count > 0:
    rule_diversity_factor = num_target_rules_met / effective_rules_count
else:
    rule_diversity_factor = 1.0  # No rules possible = perfect score
```

**Examples**:
- **2 rules targeted, 2 satisfied**: `diversity = 2/2 = 1.0` ✅
- **2 rules targeted, 1 satisfied**: `diversity = 1/2 = 0.5` ⚠️
- **2 rules targeted, 0 satisfied**: `diversity = 0/2 = 0.0` ❌

### Step 5: Final Rule Compliance Score

**Formula**: `final_score = quantity_score × rule_diversity_factor`

```python
final_score = quantity_score * rule_diversity_factor
```

**Examples**:
- **Quantity: 0.6, Diversity: 1.0**: `score = 0.6 × 1.0 = 0.6`
- **Quantity: 1.0, Diversity: 0.5**: `score = 1.0 × 0.5 = 0.5`
- **Quantity: 0.8, Diversity: 1.0**: `score = 0.8 × 1.0 = 0.8`

### Step 6: Integration into Overall Quality Score

**Location**: `MIID/validator/reward.py` → `calculate_variation_quality()`

The rule compliance score is combined with orthographic/phonetic similarity scores:

```python
# Calculate base score (orthographic + phonetic similarity)
base_score = calculate_orthographic_and_phonetic_quality(...)

# Calculate rule compliance score
rule_compliance_score, rule_metrics = calculate_rule_compliance_score(
    original_name,
    variations,
    target_rules,
    target_percentage
)

# Combine using weights
rule_compliance_weight = MIID_REWARD_WEIGHTS["rule_compliance_weight"]  # e.g., 0.2
base_weight = 1.0 - rule_compliance_weight  # e.g., 0.8

final_score = (base_weight * base_score) + (rule_compliance_weight * rule_compliance_score)
```

**Example**:
- `base_score = 0.85` (orthographic/phonetic quality)
- `rule_compliance_score = 0.60`
- `base_weight = 0.8`, `rule_compliance_weight = 0.2`
- `final_score = (0.8 × 0.85) + (0.2 × 0.60) = 0.68 + 0.12 = 0.80`

---

## Complete Flow Example

### Input:
- **Original name**: `"John Smith"`
- **Variations**: 15 variations
- **Target rules**: `["replace_double_letters_with_single_letter", "swap_adjacent_consonants"]`
- **Target percentage**: 30% (5 out of 15 should comply)

### Step 1: Filter Rules
- `"replace_double_letters_with_single_letter"` → ❌ No double letters in "John Smith"
- `"swap_adjacent_consonants"` → ✅ Possible (e.g., "Jhon Smith")
- **Effective rules**: `["swap_adjacent_consonants"]`

### Step 2: Evaluate Variations
```
Variation 1: "Jhon Smith" → ✅ Complies with swap_adjacent_consonants
Variation 2: "Jon Smith" → ❌ No rule compliance
Variation 3: "Jhon Smyth" → ✅ Complies with swap_adjacent_consonants
...
Variation 15: "John Smyth" → ❌ No rule compliance
```

**Result**:
- `compliant_variations_by_rule = {"swap_adjacent_consonants": ["Jhon Smith", "Jhon Smyth", ...]}`
- `overall_compliant_count = 3` (3 variations comply)

### Step 3: Calculate Scores
- **Expected**: `max(1, int(15 × 0.30)) = 5`
- **Actual**: `3`
- **Ratio**: `3 / 5 = 0.6`
- **Quantity score**: `0.6`
- **Diversity**: `1 / 1 = 1.0` (1 rule satisfied out of 1 effective)
- **Final rule compliance score**: `0.6 × 1.0 = 0.6`

### Step 4: Combine with Base Score
- **Base score** (orthographic/phonetic): `0.85`
- **Rule compliance score**: `0.60`
- **Final quality score**: `(0.8 × 0.85) + (0.2 × 0.60) = 0.80`

---

## Key Takeaways

1. **Query Generation**:
   - Randomly selects 1-3 rules
   - Includes rule percentage (e.g., 30%) in query
   - Rules described in natural language

2. **Rule Evaluation**:
   - Filters impossible rules (based on name structure)
   - Checks each variation against effective rules
   - Returns compliant variations by rule

3. **Scoring**:
   - **Quantity score**: How many variations comply vs. expected
   - **Diversity factor**: How many different rules are satisfied
   - **Final score**: `quantity_score × diversity_factor`
   - **Integration**: Combined with orthographic/phonetic scores using weights

4. **Special Cases**:
   - **No rules possible**: Returns score of `1.0` (not penalized)
   - **Above target**: Penalty applied (max 0.5 if 2x+ expected)
   - **Multiple rules**: Rewards diversity (satisfying multiple rules)

---

## Configuration

**Weights** (in `MIID/utils/config.py`):
```python
MIID_REWARD_WEIGHTS = {
    "rule_compliance_weight": 0.2,  # 20% weight for rule compliance
    # ... other weights
}
```

**Default Rule Percentage**: 30% (can be configured per query)

