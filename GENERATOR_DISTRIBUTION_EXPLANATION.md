# How the Generator Distributes Rule-Compliant Variations

## Algorithm Overview

The `select_optimal_combination_with_rules` method works in **3 phases**:

### Phase 1: Fill Each Category with Rule-Compliant Variations (Priority)
**Lines 1370-1400**: For each category (Light → Medium → Far):
1. **First priority**: Try to fill with rule-compliant variations that match this category
2. **Second priority**: Fill remaining slots with non-rule-compliant variations

### Phase 2: Add More Rule-Compliant Variations (If Needed)
**Lines 1402-1416**: If we haven't reached the target rule count (e.g., 4-5):
- Add more rule-compliant variations from ANY category
- This can cause slight imbalance in orthographic distribution

### Phase 3: Fill Remaining Slots
**Lines 1418-1427**: Fill any remaining slots to reach exactly 15 variations

---

## Example Walkthroughs

### Example 1: Ideal Distribution
**Target**: 3 Light, 9 Medium, 3 Far | 4 rule-compliant

**Phase 1 - Light (need 3)**:
- Finds 1 rule-compliant variation in Light → ✅ Add it (rule_count=1)
- Fills remaining 2 slots with non-rule variations → ✅ Add 2

**Phase 1 - Medium (need 9)**:
- Finds 2 rule-compliant variations in Medium → ✅ Add them (rule_count=3)
- Fills remaining 7 slots with non-rule variations → ✅ Add 7

**Phase 1 - Far (need 3)**:
- Finds 1 rule-compliant variation in Far → ✅ Add it (rule_count=4)
- Fills remaining 2 slots with non-rule variations → ✅ Add 2

**Result**: ✅ Perfect! 4 rule-compliant, distribution matches

---

### Example 2: Rule-Compliant Concentrated in Light/Medium
**Target**: 3 Light, 9 Medium, 3 Far | 4 rule-compliant

**Phase 1 - Light (need 3)**:
- Finds 2 rule-compliant variations in Light → ✅ Add them (rule_count=2)
- Fills remaining 1 slot with non-rule → ✅ Add 1

**Phase 1 - Medium (need 9)**:
- Finds 2 rule-compliant variations in Medium → ✅ Add them (rule_count=4)
- Fills remaining 7 slots with non-rule → ✅ Add 7

**Phase 1 - Far (need 3)**:
- Finds 0 rule-compliant variations in Far → ⚠️ None available
- Fills all 3 slots with non-rule → ✅ Add 3

**Result**: ✅ Perfect! 4 rule-compliant, distribution matches

---

### Example 3: All Rule-Compliant in Medium
**Target**: 3 Light, 9 Medium, 3 Far | 4 rule-compliant

**Phase 1 - Light (need 3)**:
- Finds 0 rule-compliant variations in Light → ⚠️ None available
- Fills all 3 slots with non-rule → ✅ Add 3

**Phase 1 - Medium (need 9)**:
- Finds 4 rule-compliant variations in Medium → ✅ Add them (rule_count=4)
- Fills remaining 5 slots with non-rule → ✅ Add 5

**Phase 1 - Far (need 3)**:
- Finds 0 rule-compliant variations in Far → ⚠️ None available
- Fills all 3 slots with non-rule → ✅ Add 3

**Result**: ✅ Perfect! 4 rule-compliant, distribution matches

---

## Current Problem

### What Actually Happens (Based on Test Results)

**Target**: 3 Light, 9 Medium, 3 Far | 4 rule-compliant

**Phase 1 - Light (need 3)**:
- Finds 3 rule-compliant variations in Light → ✅ Add all 3 (rule_count=3)
- Fills remaining 0 slots → ✅ Done

**Phase 1 - Medium (need 9)**:
- Finds 0 rule-compliant variations in Medium → ⚠️ **None available!**
- Fills all 9 slots with non-rule → ✅ Add 9

**Phase 1 - Far (need 3)**:
- Finds 0 rule-compliant variations in Far → ⚠️ **None available!**
- Fills all 3 slots with non-rule → ✅ Add 3

**Phase 2 - Add More Rule-Compliant**:
- Only 3 rule-compliant found (need 4) → ⚠️ Tries to add more
- But all remaining rule-compliant variations are in Light category
- Adding them would break the orthographic distribution
- **Result**: Only 3 rule-compliant (20%) instead of 4 (30%)

---

## Why This Happens

The rule generation functions (`_apply_letter_deletion`, `_apply_letter_insertion`, `_apply_letter_swap`) only make **minimal changes**:
- Delete 1 letter → Still very similar (Light category)
- Insert 1 letter → Still very similar (Light category)
- Swap 2 letters → Still very similar (Light category)

**To get rule-compliant variations in Medium/Far, we need:**
1. **More aggressive rule applications**: Delete 2-3 letters, insert multiple letters
2. **Combine multiple rules**: Delete + swap, insert + delete
3. **Apply rules to longer names**: More changes = lower similarity

---

## Code Logic Summary

```python
# Phase 1: For each category (Light, Medium, Far)
for category in ["Light", "Medium", "Far"]:
    needed = target_orthographic[category]  # e.g., 3 for Light
    
    # Try to fill with rule-compliant variations in this category
    for rule_compliant_var in rule_compliant_variations:
        if var_category == category and rule_count < target_rule_count:
            selected.append(var)  # ✅ Rule-compliant added
            rule_count += 1
    
    # Fill remaining slots with non-rule variations
    remaining = needed - selected_in_category
    for non_rule_var in non_rule_variations[category]:
        if remaining > 0:
            selected.append(var)  # ✅ Non-rule added
            remaining -= 1

# Phase 2: If we need more rule-compliant variations
if rule_count < target_rule_count:
    # Add from any category (may cause slight imbalance)
    for rule_compliant_var in remaining_rule_compliant:
        if rule_count < target_rule_count:
            selected.append(var)  # ✅ Rule-compliant added (any category)
            rule_count += 1
```

---

## Conclusion

**The generator CAN distribute rule-compliant variations across categories** (as shown in Examples 1-3), but **currently it can't** because:
- Rule-compliant variations only exist in Light category
- No rule-compliant variations are available in Medium/Far categories

**Solution**: Modify rule generation to produce variations that can fall into Medium/Far categories by making more aggressive changes.

