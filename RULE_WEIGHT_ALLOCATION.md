# Rule Weight Allocation - How 30% Target is Distributed

## Key Answer

**The 30% target percentage is NOT distributed across individual rules. It's a single target for ALL rules combined.**

When you have 2 rules and 30% target:
- **30% means**: 30% of variations should comply with **at least one** of the 2 rules
- **You can pick any rule(s)** to satisfy the 30% - all from one rule, or split between both
- **No per-rule weights** - individual rules don't have separate percentage targets

---

## How It Works

### Step 1: Count Unique Compliant Variations

The validator counts **unique variations that satisfy ANY of the target rules**:

```python
# From reward.py line 2938-2939
overall_compliant_count = len(rules_satisfied_by_variation)  # Unique variations
expected_compliant_count = max(1, int(len(variations) * target_percentage))
```

**Key Point**: A variation can satisfy multiple rules, but it's only counted **once** in `overall_compliant_count`.

### Step 2: Calculate Quantity Score

```python
ratio_of_actual_to_expected = overall_compliant_count / expected_compliant_count

if ratio_of_actual_to_expected <= 1.0:
    quantity_score = ratio_of_actual_to_expected
else:
    quantity_score = max(0.5, 1.5 - 0.5 * ratio_of_actual_to_expected)
```

### Step 3: Calculate Diversity Factor

```python
# Count how many different rules were satisfied (at least once)
satisfied_effective_rules = set()
for rule_name, compliant_vars_for_rule_list in compliant_variations_by_rule.items():
    if compliant_vars_for_rule_list:  # Rule was satisfied by at least one variation
        satisfied_effective_rules.add(rule_name)

num_target_rules_met = len(satisfied_effective_rules)
effective_rules_count = len(compliant_variations_by_rule)

rule_diversity_factor = num_target_rules_met / effective_rules_count
```

**Key Point**: Diversity rewards satisfying **multiple different rules**, not how many variations per rule.

### Step 4: Final Score

```python
final_score = quantity_score * rule_diversity_factor
```

---

## Examples

### Example 1: 2 Rules, 30% Target, All from One Rule

**Setup**:
- Total variations: 15
- Target rules: `["replace_double_letters_with_single_letter", "swap_adjacent_consonants"]`
- Target percentage: 30% → Expected: 5 variations

**Variations**:
- Rule 1 compliant: 5 variations ("John Smth", "Jon Smith", "Jhon Smith", "John Smit", "Jhon Smit")
- Rule 2 compliant: 0 variations
- Total unique compliant: 5

**Calculation**:
- Quantity Score: 5/5 = **1.0** ✅
- Rules satisfied: 1 out of 2
- Diversity Factor: 1/2 = **0.5**
- **Final Score: 1.0 × 0.5 = 0.5**

**Result**: You get full quantity score but lose 50% on diversity.

---

### Example 2: 2 Rules, 30% Target, Split Between Both Rules

**Setup**:
- Total variations: 15
- Target rules: `["replace_double_letters_with_single_letter", "swap_adjacent_consonants"]`
- Target percentage: 30% → Expected: 5 variations

**Variations**:
- Rule 1 compliant: 3 variations ("John Smth", "Jon Smith", "Jhon Smith")
- Rule 2 compliant: 2 variations ("John Smth", "Jon Smth") - Note: "John Smth" satisfies both!
- Total unique compliant: 4 (one variation satisfies both rules)

**Calculation**:
- Quantity Score: 4/5 = **0.8** ⚠️ (slightly below target)
- Rules satisfied: 2 out of 2
- Diversity Factor: 2/2 = **1.0** ✅
- **Final Score: 0.8 × 1.0 = 0.8**

**Result**: You get full diversity score but lose 20% on quantity.

---

### Example 3: 2 Rules, 30% Target, Perfect Distribution

**Setup**:
- Total variations: 15
- Target rules: `["replace_double_letters_with_single_letter", "swap_adjacent_consonants"]`
- Target percentage: 30% → Expected: 5 variations

**Variations**:
- Rule 1 compliant: 3 variations ("John Smth", "Jon Smith", "Jhon Smith")
- Rule 2 compliant: 3 variations ("John Smth", "Jon Smth", "Jhon Smth") - Note: "John Smth" satisfies both!
- Total unique compliant: 5

**Calculation**:
- Quantity Score: 5/5 = **1.0** ✅
- Rules satisfied: 2 out of 2
- Diversity Factor: 2/2 = **1.0** ✅
- **Final Score: 1.0 × 1.0 = 1.0** 🎯

**Result**: Perfect score! You met the 30% target AND satisfied both rules.

---

### Example 4: 2 Rules, 30% Target, Over-Target

**Setup**:
- Total variations: 15
- Target rules: `["replace_double_letters_with_single_letter", "swap_adjacent_consonants"]`
- Target percentage: 30% → Expected: 5 variations

**Variations**:
- Rule 1 compliant: 8 variations
- Rule 2 compliant: 2 variations
- Total unique compliant: 10

**Calculation**:
- Ratio: 10/5 = 2.0
- Quantity Score: max(0.5, 1.5 - 0.5 × 2.0) = max(0.5, 0.5) = **0.5** ⚠️
- Rules satisfied: 2 out of 2
- Diversity Factor: 2/2 = **1.0** ✅
- **Final Score: 0.5 × 1.0 = 0.5**

**Result**: Over-target is penalized! You get capped at 0.5 for quantity score.

---

## Important Points

### 1. No Per-Rule Weights

**Individual rules do NOT have separate percentage targets.**

- ❌ **NOT**: Rule 1 gets 15%, Rule 2 gets 15% = 30% total
- ✅ **ACTUAL**: Any combination that totals 30% of variations satisfying at least one rule

### 2. Variations Can Satisfy Multiple Rules

A single variation can satisfy multiple rules simultaneously:

```python
# Variation "John Smth" might satisfy:
# - replace_double_letters_with_single_letter (if original was "John Smithh")
# - swap_adjacent_consonants (if "th" was swapped)
```

But it's only counted **once** in the quantity score.

### 3. Diversity Rewards Rule Coverage

The diversity factor encourages satisfying **multiple different rules**:

- 1 rule satisfied: Diversity = 0.5 (if 2 rules total)
- 2 rules satisfied: Diversity = 1.0 (if 2 rules total)

**Strategy**: To maximize score, satisfy the 30% target AND cover multiple rules.

### 4. Over-Target is Penalized

If you exceed the target percentage, quantity score is capped:

```python
if ratio > 1.0:
    quantity_score = max(0.5, 1.5 - 0.5 * ratio)
```

**Example**: 10/5 = 2.0 → Score = 0.5 (50% penalty)

---

## Strategy for Miners

### Optimal Strategy

1. **Meet the 30% target exactly** (or slightly above, but not too much)
2. **Distribute across multiple rules** to maximize diversity
3. **Avoid over-target** (penalty kicks in)

### Example Optimal Distribution

**2 Rules, 30% Target (5 out of 15 variations)**:

- Rule 1: 3 variations
- Rule 2: 3 variations
- Overlap: 1 variation (satisfies both)
- **Total unique: 5** ✅
- **Both rules satisfied** ✅
- **Score: 1.0** 🎯

### Suboptimal Strategies

**All from one rule**:
- Quantity: ✅
- Diversity: ❌ (0.5 factor)
- **Score: 0.5**

**Over-target**:
- Quantity: ❌ (capped at 0.5)
- Diversity: ✅
- **Score: 0.5**

---

## Code Reference

### Key Function: `calculate_rule_compliance_score`

```python
# Line 2938-2940
overall_compliant_count = len(rules_satisfied_by_variation)  # Unique variations
expected_compliant_count = max(1, int(len(variations) * target_percentage))
```

**This counts unique variations, not per-rule counts.**

### Key Function: `evaluate_rule_compliance`

```python
# Line 488-496
for variation in variations:
    for rule in effective_rules:
        if RULE_EVALUATORS[rule](original_name, variation):
            compliant_variations[rule].append(variation)
            all_compliant_variations.add(variation)  # Set - no duplicates
```

**A variation can be added to multiple rule lists, but the set ensures unique counting.**

---

## Summary

| Question | Answer |
|----------|--------|
| **Are weights distributed across rules?** | ❌ No - 30% is a single target for ALL rules combined |
| **Can I pick any rule to satisfy 30%?** | ✅ Yes - all from one rule, or split between rules |
| **Do individual rules have weights?** | ❌ No - no per-rule percentage targets |
| **What happens if I exceed 30%?** | ⚠️ Penalty - quantity score capped at 0.5 |
| **What's the best strategy?** | ✅ Meet 30% target AND satisfy multiple rules for diversity |

**Bottom Line**: The 30% target is a **pool** that can be satisfied by any combination of the target rules. Diversity factor rewards covering multiple rules, but there's no requirement to split the 30% evenly.

