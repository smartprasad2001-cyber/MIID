# Rule Compliance Test Results - 15 Sanctioned Names

## Test Configuration

- **Names Tested**: 15 names from `Sanctioned_list.json`
- **Variations per Name**: 15
- **Target Distribution**: Light (20%), Medium (60%), Far (20%)
- **Target Rule Compliance**: 30%
- **Rules Tested**: 13 rules
  - swap_adjacent_consonants
  - replace_double_letters_with_single_letter
  - remove_all_spaces
  - replace_spaces_with_random_special_characters
  - delete_random_letter
  - replace_random_vowel_with_random_vowel
  - replace_random_consonant_with_random_consonant
  - swap_random_letter
  - insert_random_letter
  - duplicate_random_letter_as_double_letter
  - initial_only_first_name
  - shorten_name_to_initials
  - name_parts_permutations

## Overall Results

| Metric | Value |
|--------|-------|
| **Average Rule Compliance Score** | 0.1994 (19.94%) |
| **Average Compliance Ratio** | 25.78% |
| **Target Compliance** | 30% |
| **Achievement** | 85.9% of target |

## Per-Name Breakdown

| Name | Rule Score | Compliance % | Status |
|------|------------|--------------|--------|
| Asma Al-Akhras | 0.2500 | 26.67% | ✅ |
| Akhmed Dudaev | 0.1667 | 26.67% | ✅ |
| Leonid Pasechnik | 0.1667 | 26.67% | ✅ |
| Anna Molchanova | 0.2308 | 26.67% | ✅ |
| Yelena MIZULINA | 0.1364 | 20.00% | ⚠️ |
| Yuriy Hovtvin | 0.2500 | 26.67% | ✅ |
| Ivan Nareiko | 0.1818 | 26.67% | ✅ |
| Anastasiya Eshstrut | 0.2500 | 26.67% | ✅ |
| Maria Butina | 0.1818 | 26.67% | ✅ |
| Varee KRATUMPORN | 0.2308 | 26.67% | ✅ |
| Zeinab Jammeh | 0.2500 | 26.67% | ✅ |
| Yu Hsiang PAO | 0.2500 | 26.67% | ✅ |
| Alexey Chubarov | 0.1250 | 20.00% | ⚠️ |
| Ilya Medvedovskiy | 0.1667 | 26.67% | ✅ |
| Umar Ahmad Umar Ahmad Hajj | 0.1538 | 26.67% | ✅ |

## Key Findings

1. **Consistent Performance**: Most names (13/15) achieved 26.67% compliance, which is close to the 30% target.

2. **Rule Distribution**: 
   - Most rule-compliant variations came from:
     - `insert_random_letter` (most common)
     - `shorten_name_to_initials`
     - `name_parts_permutations`
   - Some rules had 0 matches for certain names (likely due to name structure constraints)

3. **Orthographic Distribution**: All names successfully met the target distribution (20% Light, 60% Medium, 20% Far).

4. **Challenges**:
   - 2 names (Yelena MIZULINA, Alexey Chubarov) achieved only 20% compliance
   - Some rules are difficult to apply to certain name structures (e.g., double letters, spaces, multi-part names)

## Recommendations

1. **Rule Selection**: The generator successfully filters out impossible rules based on name structure.

2. **Category-Targeted Generation**: The generator uses category-targeted rule generation to distribute rule compliance across Light, Medium, and Far categories.

3. **Improvement Opportunities**:
   - Increase rule compliance for names with fewer applicable rules
   - Better distribution of rule-compliant variations across Medium category (currently mostly in Light)

## Test Method

The test uses:
- `OrthographicBruteForceGenerator` from `maximize_orthographic_similarity.py`
- `calculate_rule_compliance_score` from `MIID/validator/reward.py`
- `evaluate_rule_compliance` from `MIID/validator/rule_evaluator.py`

All functions match the validator's scoring system, ensuring consistency with actual validator behavior.

