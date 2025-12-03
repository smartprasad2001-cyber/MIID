# Rule Compliance Flexibility - Any Percentage, Any Number of Rules

## Overview

The `maximize_orthographic_similarity.py` generator now **fully matches** the query generator's rule compliance system. It handles:

✅ **Any percentage** (0-100%) - integer format matching query_generator  
✅ **Any number of rules** (1, 2, 3, 4, 5, etc.) - not limited to 1-3  
✅ **Exact structure** - matches `query_generator.py` metadata format  
✅ **Percentage allocation** - works exactly like the validator expects

---

## How Query Generator Works

### Rule Selection

The query generator uses `get_rule_template_and_metadata()` which:
- Randomly selects **1-3 rules** by default
- But can accept **any number of rules** if provided
- Rules are selected from all available rule categories

### Rule Percentage

- **Format**: Integer (0-100), not float
- **Meaning**: Percentage of variations that should comply with **at least one** of the selected rules
- **Not per-rule**: The percentage applies to the **total pool** of rules, not individually

### Metadata Structure

```python
rule_based = {
    "rule_percentage": 30,        # Integer 0-100
    "percentage": 30,              # Also stored (query_generator uses both)
    "selected_rules": [            # List - can be any length
        "replace_double_letters_with_single_letter",
        "swap_adjacent_consonants",
        "delete_random_letter"
    ],
    "rule_descriptions": {         # Optional descriptions
        "replace_double_letters_with_single_letter": "Replace double letters with a single letter",
        "swap_adjacent_consonants": "Swap adjacent consonants",
        "delete_random_letter": "Delete a random letter"
    }
}
```

---

## How Our Implementation Matches

### 1. Accepts Any Percentage (0-100)

```python
# Integer format (matching query_generator)
rule_based = {
    "rule_percentage": 30,  # 30%
    "percentage": 30         # Also accepts this key
}

# Or float format (converted internally)
rule_based = {
    "rule_percentage": 0.30  # Also works, converted to 30%
}
```

**Examples**:
- `0%` - No rule compliance required
- `30%` - Default, 30% of variations should follow rules
- `50%` - Half of variations should follow rules
- `100%` - All variations must follow rules

### 2. Accepts Any Number of Rules

```python
# 1 rule
rule_based = {
    "selected_rules": ["replace_double_letters_with_single_letter"]
}

# 2 rules
rule_based = {
    "selected_rules": [
        "replace_double_letters_with_single_letter",
        "swap_adjacent_consonants"
    ]
}

# 5 rules (works perfectly!)
rule_based = {
    "selected_rules": [
        "replace_double_letters_with_single_letter",
        "swap_adjacent_consonants",
        "delete_random_letter",
        "remove_random_vowel",
        "insert_random_letter"
    ]
}
```

### 3. Percentage Allocation Logic

**Key Point**: The percentage applies to **ALL rules combined**, not per rule.

**Example**: 3 rules, 30% target
- **NOT**: Rule 1 gets 10%, Rule 2 gets 10%, Rule 3 gets 10%
- **ACTUAL**: 30% of variations should comply with **at least one** of the 3 rules

**How it works**:
1. Generate variations following any of the target rules
2. Count unique variations that satisfy **at least one** rule
3. Ensure that count meets the percentage target (e.g., 5 out of 15 for 30%)

### 4. Rule Diversity Factor

When multiple rules are provided, the validator rewards **rule diversity**:
- **More rules satisfied** = Higher diversity factor
- **Diversity factor** = `rules_satisfied / total_rules`
- **Final score** = `quantity_score × diversity_factor`

**Example**:
- 3 rules provided
- 2 rules satisfied by variations
- Diversity factor = 2/3 = 0.67

---

## Usage Examples

### Example 1: Single Rule, 30% Target

```python
rule_based = {
    "selected_rules": ["replace_double_letters_with_single_letter"],
    "rule_percentage": 30
}

# Result: 30% of variations (5 out of 15) should follow the double letter rule
```

### Example 2: Multiple Rules, 30% Target

```python
rule_based = {
    "selected_rules": [
        "replace_double_letters_with_single_letter",
        "swap_adjacent_consonants",
        "delete_random_letter"
    ],
    "rule_percentage": 30
}

# Result: 30% of variations (5 out of 15) should comply with at least one of the 3 rules
# Diversity: Higher score if variations satisfy multiple different rules
```

### Example 3: Many Rules, 50% Target

```python
rule_based = {
    "selected_rules": [
        "replace_double_letters_with_single_letter",
        "swap_adjacent_consonants",
        "delete_random_letter",
        "remove_random_vowel",
        "insert_random_letter",
        "duplicate_random_letter_as_double_letter"
    ],
    "rule_percentage": 50
}

# Result: 50% of variations (8 out of 15) should comply with at least one of the 6 rules
# Diversity: Maximum score if all 6 rules are satisfied
```

### Example 4: 100% Rule Compliance

```python
rule_based = {
    "selected_rules": ["replace_double_letters_with_single_letter"],
    "rule_percentage": 100
}

# Result: ALL variations (15 out of 15) must follow the rule
```

### Example 5: 0% Rule Compliance (Disabled)

```python
rule_based = {
    "selected_rules": ["replace_double_letters_with_single_letter"],
    "rule_percentage": 0
}

# Result: Rule compliance is disabled, only orthographic similarity matters
```

---

## Command Line Examples

### Single Rule
```bash
python3 maximize_orthographic_similarity.py "John Smith" \
    --count 15 \
    --rules replace_double_letters_with_single_letter \
    --rule-percentage 30
```

### Multiple Rules (2)
```bash
python3 maximize_orthographic_similarity.py "John Smith" \
    --count 15 \
    --rules replace_double_letters_with_single_letter swap_adjacent_consonants \
    --rule-percentage 30
```

### Many Rules (5)
```bash
python3 maximize_orthographic_similarity.py "John Smith" \
    --count 15 \
    --rules replace_double_letters_with_single_letter swap_adjacent_consonants delete_random_letter remove_random_vowel insert_random_letter \
    --rule-percentage 50
```

### 100% Rule Compliance
```bash
python3 maximize_orthographic_similarity.py "John Smith" \
    --count 15 \
    --rules replace_double_letters_with_single_letter \
    --rule-percentage 100
```

---

## How It Works Internally

### Step 1: Accept Input (Any Format)

```python
# Handles both integer and float
rule_percentage = rule_based.get("rule_percentage") or rule_based.get("percentage", 30)
if isinstance(rule_percentage, int):
    self.rule_percentage = rule_percentage / 100.0  # Convert to 0.0-1.0
elif isinstance(rule_percentage, float):
    self.rule_percentage = rule_percentage if rule_percentage <= 1.0 else rule_percentage / 100.0
```

### Step 2: Generate Rule-Compliant Variations

```python
# Generates variations for ALL rules (any number)
for rule in self.target_rules:  # Can be 1, 2, 3, 5, 10, etc.
    variations.update(self.generate_rule_compliant_variations(word, [rule]))
```

### Step 3: Check Compliance (Any Rule)

```python
# A variation is compliant if it satisfies ANY of the target rules
for rule in self.target_rules:  # Check all rules
    if RULE_EVALUATORS[rule](original_name, variation):
        is_compliant = True
        break  # Only need to satisfy one rule
```

### Step 4: Select Optimal Mix

```python
# Calculate target count based on percentage
expected_rule_count = max(1, int(total_count * self.rule_percentage))

# Select variations that:
# 1. Meet orthographic distribution (Light/Medium/Far)
# 2. Meet rule compliance target (percentage)
# 3. Maximize rule diversity (satisfy multiple different rules)
```

---

## Key Differences from Query Generator

| Aspect | Query Generator | Our Implementation | Match? |
|--------|----------------|-------------------|--------|
| **Rule Selection** | Random 1-3 rules | Accepts any number | ✅ Yes |
| **Percentage Format** | Integer (0-100) | Integer (0-100) | ✅ Yes |
| **Percentage Meaning** | Pool of all rules | Pool of all rules | ✅ Yes |
| **Metadata Structure** | `rule_based` dict | `rule_based` dict | ✅ Yes |
| **Rule Descriptions** | Included | Included | ✅ Yes |
| **Diversity Factor** | Rewards multiple rules | Rewards multiple rules | ✅ Yes |

---

## Summary

✅ **Any percentage** (0-100): Works with any integer percentage  
✅ **Any number of rules** (1, 2, 3, 5, 10, etc.): Not limited to 1-3  
✅ **Exact structure**: Matches `query_generator.py` format exactly  
✅ **Percentage allocation**: Applies to all rules combined (pool)  
✅ **Rule diversity**: Rewards satisfying multiple different rules  
✅ **Flexible input**: Accepts both integer and float percentage formats  

The implementation is **fully compatible** with the query generator and validator's rule compliance system!

