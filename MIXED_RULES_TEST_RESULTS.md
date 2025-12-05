# Mixed Rules Test Results

## Test Results Summary

### Rule Compliance Distribution Achieved:
- **Light**: 3 rule-compliant variations ✅
- **Medium**: 0 rule-compliant variations ❌
- **Far**: 1 rule-compliant variation ✅
- **Total**: 4 rule-compliant (26.7% of 15) - **Close to 30% target!**

### Orthographic Distribution:
- **Light**: 3/3 (20%) ✅
- **Medium**: 9/9 (60%) ✅
- **Far**: 3/3 (20%) ✅

## Rule Analysis

### Rules That Produce Light (0.70-1.00):
- `delete_random_letter` → Score: 0.90+
- `insert_random_letter` → Score: 0.90+
- `swap_random_letter` → Score: 0.90+
- `remove_all_spaces` → Score: 0.90
- `replace_spaces_with_random_special_characters` → Score: 0.90
- `replace_random_vowel_with_random_vowel` → Score: 0.90
- `replace_random_consonant_with_random_consonant` → Score: 0.90

### Rules That Produce Far (0.20-0.49):
- `shorten_name_to_initials` → Score: 0.20-0.30 ✅
- `name_parts_permutations` → Score: 0.00-0.20 ✅

### Rules That Produce Medium (0.50-0.69):
- **NONE FOUND** ❌

## Key Finding

**There are NO rules that naturally produce Medium similarity (0.50-0.69).**

All tested rules either:
1. Make minimal changes → Light category (0.70-1.00)
2. Make large changes → Far category (0.20-0.49)

## Current Performance

✅ **Achieved:**
- 26.7% rule compliance (4 out of 15) - close to 30% target
- Rule compliance distributed across Light and Far categories
- Perfect orthographic distribution maintained

❌ **Limitation:**
- Cannot achieve rule compliance in Medium category
- Medium variations must be non-rule-compliant

## Recommendation

**Accept the current distribution:**
- Light: 3 rule-compliant (from delete/insert/swap/space rules)
- Medium: 0 rule-compliant (no rules produce Medium similarity)
- Far: 1 rule-compliant (from initials/permutations)
- **Total: 4 rule-compliant (26.7%)**

This is the best achievable with current rule set. The 26.7% is close to the 30% target and demonstrates that rule compliance CAN be distributed across categories (Light + Far), even if Medium is not achievable.

## Alternative Approach

If you need Medium rule-compliant variations, you would need to:
1. **Create new rules** that produce Medium similarity
2. **Modify existing rules** to produce Medium variations (but validator checks are strict)
3. **Accept that Medium will always be non-rule-compliant**

