# Why Some Names Have Low Orthographic Quality Scores

## Root Cause Analysis

After investigation, the low quality scores (0.3400) are **caused by rule compliance constraints**, not the names themselves.

## Key Finding

**Without rules**: All names achieve quality score **1.0000** (perfect)  
**With rules (30% compliance)**: Some names drop to **0.3400**

## Example: Akhmed Dudaev

### Without Rules
- **Quality Score**: 1.0000
- **Score Range**: 0.3846 - 0.9286
- **Distribution**: Perfect 20/60/20 match
- **All variations**: Within valid boundaries (0.20-1.00)

### With Rules (30% compliance)
- **Quality Score**: 0.3400 ⚠️
- **Score Range**: 0.2308 - 0.9286
- **Distribution**: Still shows 20/60/20, but quality is low
- **Issue**: Rule-compliant variations may not match distribution as well

## Why This Happens

### 1. **Rule Compliance Priority**
When rules are required, the selection algorithm:
1. **First** selects rule-compliant variations (to meet 30% target)
2. **Then** fills remaining slots to match distribution

This two-phase approach can compromise distribution quality.

### 2. **Limited Rule-Compliant Options**
For some names, rule-compliant variations are:
- **Concentrated in Light category** (most rules produce high-similarity variations)
- **Sparse in Medium/Far categories** (fewer rule-compliant options)
- **May have edge-case scores** (e.g., 0.2308, very close to Far boundary)

### 3. **Quality Score Calculation**
The quality score penalizes:
- **Unmatched variations** (outside 0.20-1.00 range): 0.1 penalty per unmatched
- **Poor distribution match**: Lower match_ratio = lower quality
- **Edge scores**: Variations at category boundaries may not contribute optimally

## Specific Issues for Low-Scoring Names

### Names with 0.3400 Quality:
1. **Akhmed Dudaev**
2. **Yuriy Hovtvin**
3. **Zeinab Jammeh**
4. **Yu Hsiang PAO**
5. **Umar Ahmad Umar Ahmad Hajj**

### Common Characteristics:
- **Short names** or **unusual name structures**
- **Limited rule-compliant variations** in Medium/Far categories
- **Rule-compliant variations** mostly in Light category
- **Far variations** may have scores very close to 0.20 boundary

## Example Breakdown: Akhmed Dudaev (With Rules)

```
Selected Variations:
   1. dAkhmed Dudaev                 | Score: 0.9286 | Light (rule-compliant)
   2. Akhmed Dudaevv                 | Score: 0.9286 | Light (rule-compliant)
   3. qAkhmed Dudaev                 | Score: 0.9286 | Light (rule-compliant)
   4-12. Medium variations           | Score: 0.6923 | Medium
   13. Dudaev Akhmed                  | Score: 0.2308 | Far (rule-compliant, very low!)
   14-15. Far variations              | Score: 0.47-0.47 | Far
```

**Problem**: The Far variation at 0.2308 is:
- Rule-compliant (name_parts_permutations)
- Within Far range (0.20-0.49) but at the very edge
- May not contribute optimally to quality score

## Quality Score Formula

```python
quality = 0.0
for each category (Light, Medium, Far):
    count = variations in category
    target_count = target_percentage * total
    match_ratio = count / target_count
    if match_ratio <= 1.0:
        match_quality = match_ratio
    else:
        match_quality = 1.0 - (1.0 / (1.0 + match_ratio - 1.0))
    quality += target_percentage * match_quality

# Penalty for unmatched
unmatched = total - total_matched
penalty = 0.1 * (unmatched / total)
quality = max(0.0, quality - penalty)
```

## Why 0.3400 Specifically?

**ROOT CAUSE IDENTIFIED**: The quality score is 0.3400 because **Medium variations have scores of 0.6923**, which falls **between the Medium and Light boundaries**!

### The Problem:
- **Medium range**: 0.50 - 0.69
- **Light range**: 0.70 - 1.00
- **Actual Medium scores**: 0.6923 (9 variations)

**0.6923 > 0.69** (Medium upper bound) but **0.6923 < 0.70** (Light lower bound)

Result: **9 variations are "unmatched"** (fall in the gap between categories)

### Quality Calculation:
```
Light:   3/3 variations  → contribution: 0.2000
Medium:  0/9 variations  → contribution: 0.0000 (all unmatched!)
Far:     3/3 variations  → contribution: 0.2000
Unmatched: 9 variations → penalty: 0.0600

Total: 0.2000 + 0.0000 + 0.2000 - 0.0600 = 0.3400
```

### Why This Happens:
When rules are applied, the selection algorithm:
1. Selects rule-compliant variations (often in Light category)
2. Fills Medium slots with variations that score **just above 0.69**
3. These variations fall in the **gap between Medium (0.69) and Light (0.70)**
4. They're counted as "unmatched" and penalized

## Solutions

### 1. **Improve Category-Targeted Rule Generation**
- Generate more rule-compliant variations for Medium/Far categories
- Use higher aggression levels for Far category rules

### 2. **Better Selection Algorithm**
- Balance rule compliance and distribution quality
- Avoid selecting edge-case variations when better options exist

### 3. **Rule Filtering**
- Skip rules that produce only edge-case variations
- Prioritize rules that work well across all categories

## Summary

**Low scores (0.3400) are caused by:**

### Primary Issue: Boundary Gap
- ✅ **Medium variations score 0.6923**, which is **above Medium upper bound (0.69)** but **below Light lower bound (0.70)**
- ✅ These variations are **unmatched** and penalized (9 variations × 0.1 penalty = 0.06 reduction)
- ✅ This happens when rule compliance forces selection of variations that don't fit category boundaries perfectly

### Secondary Issues:
- ✅ Rule compliance constraints limit available variations
- ✅ Selection algorithm prioritizes rules over perfect boundary matching
- ✅ Some names have fewer rule-compliant options in Medium category

### The Math:
```
Quality = Light contribution (0.20) + Medium contribution (0.00) + Far contribution (0.20) - Penalty (0.06)
        = 0.40 - 0.06
        = 0.34
```

**Recommendation**: 
1. Adjust selection algorithm to avoid scores in the 0.69-0.70 gap
2. Filter out variations with scores between category boundaries
3. Use more aggressive Medium category targeting for rule-compliant variations

