# Rule Compliance Distribution: Limitation and Solution

## Problem Identified

**Current Issue:**
- Rules `delete_random_letter`, `insert_random_letter`, `swap_random_letter` **ONLY** produce Light category variations (0.70-1.00 similarity)
- Cannot achieve 30% rule compliance distributed across Light/Medium/Far categories
- Only achieving 20% rule compliance (3 out of 15 variations)

## Root Cause

### Validator Rule Checks Are Strict

The validator's rule evaluation functions are very specific:

1. **`is_letter_removed`**: Only accepts variations where **exactly 1 letter** is removed
   ```python
   if len(variation) != len(original) - 1:
       return False
   ```

2. **`is_random_letter_inserted`**: Only accepts variations where **exactly 1 letter** is inserted
   ```python
   if len(variation) != len(original) + 1:
       return False
   ```

3. **`is_letters_swapped`**: Only accepts variations where **exactly 2 adjacent letters** are swapped
   ```python
   if len(diffs) != 2 or abs(diffs[0] - diffs[1]) != 1:
       return False
   ```

### Why This Limits to Light Category

- **Single-letter operations** (delete 1, insert 1, swap 2) make **minimal changes**
- Minimal changes = **high orthographic similarity** = **Light category only** (0.70-1.00)
- **Cannot** produce Medium (0.50-0.69) or Far (0.20-0.49) variations with these rules

## Solution Strategy

### Option 1: Use Additional Rules (RECOMMENDED)

Use a **mix of rules** that naturally produce different similarity levels:

**Light Category Rules:**
- `delete_random_letter` ✅
- `insert_random_letter` ✅
- `swap_random_letter` ✅

**Medium Category Rules:**
- `remove_all_spaces` (removes spaces, moderate change)
- `replace_spaces_with_random_special_characters` (moderate change)
- `replace_random_vowel_with_random_vowel` (moderate change)
- `duplicate_random_letter_as_double_letter` (moderate change)

**Far Category Rules:**
- `shorten_name_to_initials` (large change)
- `shorten_name_to_abbreviations` (large change)
- `name_parts_permutations` (large change)
- `initial_only_first_name` (large change)

### Option 2: Accept Limitation

If you **must** use only these 3 rules:
- Accept that rule compliance will be **limited to Light category**
- Achieve 20% rule compliance (3 out of 15) instead of 30%
- All rule-compliant variations will be in Light category

### Option 3: Hybrid Approach

Use the 3 specified rules for Light category, and use other rules for Medium/Far:
- Light: `delete_random_letter`, `insert_random_letter`, `swap_random_letter`
- Medium: `remove_all_spaces`, `replace_spaces_with_random_special_characters`
- Far: `shorten_name_to_initials`, `name_parts_permutations`

## Implementation Status

✅ **Completed:**
- Added aggression parameter to rule functions
- Created category-targeted generation method
- Updated selection algorithm to distribute rule compliance

❌ **Limitation:**
- The 3 specific rules (`delete_random_letter`, `insert_random_letter`, `swap_random_letter`) can only produce Light variations
- Cannot produce Medium/Far variations with these rules alone

## Recommendation

**Use a mix of rules** to achieve 30% rule compliance distributed across categories:

```python
rules = [
    # Light category
    "delete_random_letter",
    "insert_random_letter", 
    "swap_random_letter",
    # Medium category
    "remove_all_spaces",
    "replace_spaces_with_random_special_characters",
    # Far category
    "shorten_name_to_initials",
    "name_parts_permutations"
]
```

This will allow:
- **Light**: 1-2 rule-compliant variations (from delete/insert/swap)
- **Medium**: 1-2 rule-compliant variations (from space rules)
- **Far**: 1 rule-compliant variation (from initials/permutations)
- **Total**: 4-5 rule-compliant (30% of 15)

## Next Steps

1. **If using only 3 rules**: Accept 20% rule compliance limitation
2. **If using mixed rules**: Update rule selection to include Medium/Far rules
3. **Test with mixed rules** to verify 30% rule compliance across categories

