# Explanation: Rule-Based vs Non-Rule-Based Scoring

## How the Validator Scores Variations

The validator **separates** rule-based and non-rule-based variations:

1. **Rule-Based Variations** (like "j.s.", "j. Smith"):
   - ✅ **NOT scored for phonetic/orthographic similarity**
   - ✅ **ONLY scored for rule compliance** (20% weight)
   - ✅ This is CORRECT - they shouldn't sound like the original!

2. **Non-Rule-Based Variations** (like "Jon Smith", "John Smythe"):
   - ✅ **Scored for phonetic/orthographic similarity** (60% weight)
   - ✅ **Scored for count, uniqueness, length** (40% weight)
   - ✅ **NOT scored for rule compliance**

## Why "j. Smith" Has 0.0 Phonetic Similarity

The issue is that **"j. Smith" is NOT being recognized as rule-compliant**!

- "j. Smith" matches the rule `initial_only_first_name` (first name is an initial)
- But the query template only includes: `shorten_name_to_initials` and `swap_random_letter`
- Since `initial_only_first_name` is NOT in the query template, the validator doesn't recognize "j. Smith" as rule-compliant
- Therefore, it gets scored for phonetic similarity (where it fails with 0.0)

## The Fix

We need to ensure our manual rule application **only generates variations that match the rules specified in the query template**.

If the query template says "Convert to initials", we should generate "j.s." (which matches `shorten_name_to_initials`), NOT "j. Smith" (which matches `initial_only_first_name`).

## Code Reference

From `reward.py` lines 1258-1279:
```python
# Separate variations into rule-compliant and non-rule-compliant
non_rule_compliant_variations = [
    var for var in variations if var not in rule_compliant_variations
]

# Process NON-RULE-COMPLIANT variations for base quality score
for variation in non_rule_compliant_variations:
    # Only these are scored for phonetic/orthographic similarity
```

From `reward.py` lines 1362:
```python
final_score = (base_weight * base_score) + (rule_compliance_weight * rule_compliance_score)
```

So:
- `base_score` = phonetic/orthographic similarity (for non-rule variations only)
- `rule_compliance_score` = rule compliance (for rule-based variations only)

