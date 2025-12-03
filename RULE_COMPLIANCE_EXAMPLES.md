# Rule Compliance Examples - Weights and Scoring

This document provides concrete examples of how rule compliance weights work and how they affect final scores.

---

## Example 1: Perfect Rule Compliance

### Setup
- **Original Name**: "John Smith"
- **Total Variations**: 15
- **Target Rules**: `["replace_double_letters_with_single_letter", "swap_adjacent_consonants"]`
- **Target Percentage**: 30% (5 out of 15 variations)
- **Base Score** (similarity, count, uniqueness, length): 0.85

### Variations Generated
```
1. "John Smth"      ✅ Rule 1 (double letter removed)
2. "Jon Smith"      ✅ Rule 2 (adjacent consonants swapped)
3. "Jhon Smith"    ✅ Rule 2 (adjacent consonants swapped)
4. "John Smit"      ✅ Rule 1 (double letter removed)
5. "Jon Smth"       ✅ Both rules
6. "John Smyth"     ❌ No rule
7. "Jon Smyth"      ❌ No rule
8. "Jhon Smyth"     ❌ No rule
9. "John Smithe"    ❌ No rule
10. "Jon Smithe"     ❌ No rule
11. "Jhon Smithe"    ❌ No rule
12. "John Smithh"    ❌ No rule
13. "Jon Smithh"     ❌ No rule
14. "Jhon Smithh"    ❌ No rule
15. "John Smiht"     ❌ No rule
```

### Rule Compliance Calculation

**Step 1: Count Compliant Variations**
- Rule 1 compliant: 3 variations ("John Smth", "John Smit", "Jon Smth")
- Rule 2 compliant: 3 variations ("Jon Smith", "Jhon Smith", "Jon Smth")
- **Unique compliant variations**: 5 (variations 1-5)
- **Expected**: 5 (30% of 15)
- **Actual/Expected ratio**: 5/5 = 1.0

**Step 2: Quantity Score**
```python
ratio = 5/5 = 1.0
quantity_score = 1.0  # Perfect match
```

**Step 3: Diversity Factor**
- Rules satisfied: 2 out of 2
- Diversity factor = 2/2 = 1.0

**Step 4: Rule Compliance Score**
```python
rule_compliance_score = quantity_score × diversity_factor
rule_compliance_score = 1.0 × 1.0 = 1.0
```

### Final Quality Score Calculation

**Component Weights**:
- Base weight: 80% (0.8)
- Rule compliance weight: 20% (0.2)

**Calculation**:
```python
base_score = 0.85
rule_compliance_score = 1.0

final_score = (0.8 × 0.85) + (0.2 × 1.0)
final_score = 0.68 + 0.20
final_score = 0.88
```

**Result**: ✅ **Final Score: 0.88** (improved from 0.85 base score)

---

## Example 2: Partial Rule Compliance (All from One Rule)

### Setup
- **Original Name**: "John Smith"
- **Total Variations**: 15
- **Target Rules**: `["replace_double_letters_with_single_letter", "swap_adjacent_consonants"]`
- **Target Percentage**: 30% (5 out of 15 variations)
- **Base Score**: 0.85

### Variations Generated
```
1. "John Smth"      ✅ Rule 1
2. "John Smit"      ✅ Rule 1
3. "John Smi"       ✅ Rule 1
4. "Jon Smth"       ✅ Rule 1
5. "Jhon Smth"      ✅ Rule 1
6. "John Smyth"     ❌ No rule
7. "Jon Smyth"      ❌ No rule
... (10 more non-rule variations)
```

### Rule Compliance Calculation

**Step 1: Count Compliant Variations**
- Rule 1 compliant: 5 variations
- Rule 2 compliant: 0 variations
- **Unique compliant variations**: 5
- **Expected**: 5
- **Actual/Expected ratio**: 5/5 = 1.0

**Step 2: Quantity Score**
```python
quantity_score = 1.0  # Perfect quantity
```

**Step 3: Diversity Factor**
- Rules satisfied: 1 out of 2
- Diversity factor = 1/2 = 0.5

**Step 4: Rule Compliance Score**
```python
rule_compliance_score = 1.0 × 0.5 = 0.5
```

### Final Quality Score Calculation

```python
base_score = 0.85
rule_compliance_score = 0.5

final_score = (0.8 × 0.85) + (0.2 × 0.5)
final_score = 0.68 + 0.10
final_score = 0.78
```

**Result**: ⚠️ **Final Score: 0.78** (reduced from 0.85 due to low diversity)

---

## Example 3: Under-Target Rule Compliance

### Setup
- **Original Name**: "John Smith"
- **Total Variations**: 15
- **Target Rules**: `["replace_double_letters_with_single_letter", "swap_adjacent_consonants"]`
- **Target Percentage**: 30% (5 out of 15 variations)
- **Base Score**: 0.85

### Variations Generated
```
1. "John Smth"      ✅ Rule 1
2. "Jon Smith"      ✅ Rule 2
3. "John Smyth"     ❌ No rule
... (12 more non-rule variations)
```

### Rule Compliance Calculation

**Step 1: Count Compliant Variations**
- Rule 1 compliant: 1 variation
- Rule 2 compliant: 1 variation
- **Unique compliant variations**: 2
- **Expected**: 5
- **Actual/Expected ratio**: 2/5 = 0.4

**Step 2: Quantity Score**
```python
ratio = 2/5 = 0.4
quantity_score = 0.4  # Linear penalty for under-target
```

**Step 3: Diversity Factor**
- Rules satisfied: 2 out of 2
- Diversity factor = 2/2 = 1.0

**Step 4: Rule Compliance Score**
```python
rule_compliance_score = 0.4 × 1.0 = 0.4
```

### Final Quality Score Calculation

```python
base_score = 0.85
rule_compliance_score = 0.4

final_score = (0.8 × 0.85) + (0.2 × 0.4)
final_score = 0.68 + 0.08
final_score = 0.76
```

**Result**: ⚠️ **Final Score: 0.76** (penalized for insufficient rule compliance)

---

## Example 4: No Rule Compliance

### Setup
- **Original Name**: "John Smith"
- **Total Variations**: 15
- **Target Rules**: `["replace_double_letters_with_single_letter", "swap_adjacent_consonants"]`
- **Target Percentage**: 30% (5 out of 15 variations)
- **Base Score**: 0.85

### Variations Generated
```
All 15 variations are orthographic/phonetic variations but NONE follow the target rules:
1. "John Smyth"
2. "Jon Smyth"
3. "Jhon Smyth"
... (all non-rule variations)
```

### Rule Compliance Calculation

**Step 1: Count Compliant Variations**
- Rule 1 compliant: 0 variations
- Rule 2 compliant: 0 variations
- **Unique compliant variations**: 0
- **Expected**: 5
- **Actual/Expected ratio**: 0/5 = 0.0

**Step 2: Quantity Score**
```python
quantity_score = 0.0
```

**Step 3: Diversity Factor**
- Rules satisfied: 0 out of 2
- Diversity factor = 0/2 = 0.0

**Step 4: Rule Compliance Score**
```python
rule_compliance_score = 0.0 × 0.0 = 0.0
```

### Final Quality Score Calculation

```python
base_score = 0.85
rule_compliance_score = 0.0

final_score = (0.8 × 0.85) + (0.2 × 0.0)
final_score = 0.68 + 0.00
final_score = 0.68
```

**Result**: ❌ **Final Score: 0.68** (lost 20% of potential score)

---

## Example 5: Over-Target Rule Compliance (Penalty)

### Setup
- **Original Name**: "John Smith"
- **Total Variations**: 15
- **Target Rules**: `["replace_double_letters_with_single_letter", "swap_adjacent_consonants"]`
- **Target Percentage**: 30% (5 out of 15 variations)
- **Base Score**: 0.85

### Variations Generated
```
1-10. All rule-compliant variations (10 total)
11-15. Non-rule variations (5 total)
```

### Rule Compliance Calculation

**Step 1: Count Compliant Variations**
- **Unique compliant variations**: 10
- **Expected**: 5
- **Actual/Expected ratio**: 10/5 = 2.0

**Step 2: Quantity Score**
```python
ratio = 2.0  # Over-target
quantity_score = max(0.5, 1.5 - 0.5 × 2.0)
quantity_score = max(0.5, 0.5)
quantity_score = 0.5  # Capped penalty
```

**Step 3: Diversity Factor**
- Rules satisfied: 2 out of 2
- Diversity factor = 1.0

**Step 4: Rule Compliance Score**
```python
rule_compliance_score = 0.5 × 1.0 = 0.5
```

### Final Quality Score Calculation

```python
base_score = 0.85
rule_compliance_score = 0.5

final_score = (0.8 × 0.85) + (0.2 × 0.5)
final_score = 0.68 + 0.10
final_score = 0.78
```

**Result**: ⚠️ **Final Score: 0.78** (penalized for over-target compliance)

---

## Example 6: No Rules Applicable (Special Case)

### Setup
- **Original Name**: "John" (single word, no double letters, no spaces)
- **Target Rules**: `["replace_double_letters_with_single_letter", "swap_adjacent_consonants"]`
- **Base Score**: 0.85

### Rule Applicability Check

The validator filters out impossible rules:
- `replace_double_letters_with_single_letter`: ❌ No double letters in "John"
- `swap_adjacent_consonants`: ❌ No swappable adjacent consonants

**Result**: No effective rules → `rule_compliance_weight = 0.0`

### Final Quality Score Calculation

```python
base_score = 0.85
rule_compliance_weight = 0.0  # Adjusted to 0
base_weight = 1.0  # Adjusted to 1.0

final_score = (1.0 × 0.85) + (0.0 × rule_compliance_score)
final_score = 0.85
```

**Result**: ✅ **Final Score: 0.85** (no penalty, uses only base score)

---

## Summary Table

| Scenario | Base Score | Rule Compliance | Quantity | Diversity | Final Score | Impact |
|----------|-----------|----------------|----------|-----------|-------------|--------|
| **Perfect** | 0.85 | 1.0 | 1.0 | 1.0 | **0.88** | +0.03 ✅ |
| **One Rule Only** | 0.85 | 0.5 | 1.0 | 0.5 | **0.78** | -0.07 ⚠️ |
| **Under-Target** | 0.85 | 0.4 | 0.4 | 1.0 | **0.76** | -0.09 ⚠️ |
| **No Compliance** | 0.85 | 0.0 | 0.0 | 0.0 | **0.68** | -0.17 ❌ |
| **Over-Target** | 0.85 | 0.5 | 0.5 | 1.0 | **0.78** | -0.07 ⚠️ |
| **No Rules Applicable** | 0.85 | N/A | N/A | N/A | **0.85** | No change ✅ |

---

## Key Formulas

### 1. Rule Compliance Score
```python
rule_compliance_score = quantity_score × rule_diversity_factor
```

### 2. Quantity Score
```python
ratio = actual_compliant / expected_compliant

if ratio <= 0.0:
    quantity_score = 0.0
elif ratio <= 1.0:
    quantity_score = ratio  # Linear up to target
else:
    quantity_score = max(0.5, 1.5 - 0.5 × ratio)  # Penalty for over-target
```

### 3. Diversity Factor
```python
diversity_factor = rules_satisfied / total_effective_rules
```

### 4. Final Quality Score
```python
final_score = (base_weight × base_score) + (rule_compliance_weight × rule_compliance_score)

Where:
- base_weight = 0.8 (80%)
- rule_compliance_weight = 0.2 (20%)
```

---

## Optimal Strategy

To maximize your score:

1. ✅ **Meet the 30% target exactly** (or slightly above, but not too much)
2. ✅ **Distribute across multiple rules** to maximize diversity
3. ✅ **Avoid over-target** (penalty kicks in at 2× target)
4. ✅ **Ensure variations actually comply** with the rules (not just similar)

**Example Optimal Distribution**:
- 2 rules, 30% target (5 out of 15)
- Rule 1: 3 variations
- Rule 2: 3 variations
- Overlap: 1 variation (satisfies both)
- **Total unique: 5** ✅
- **Both rules satisfied** ✅
- **Score: 1.0** 🎯

---

## Impact on Final Reward

Rule compliance affects the **Names component** of the final reward:

```
Identity Quality = (Names × 0.2) + (DOB × 0.1) + (Address × 0.7)

Where Names = final_score (which includes rule compliance)
```

**Example Impact**:
- Without rule compliance: Names = 0.68 → Component = 0.136
- With perfect rule compliance: Names = 0.88 → Component = 0.176
- **Difference**: +0.04 in Names component → **+0.008 in final Identity Quality**

This may seem small, but it compounds with other scoring factors and can affect ranking!

