# Strategy: Adding Rule Compliance to Orthographic Generator

## Overview

The goal is to integrate rule compliance into `maximize_orthographic_similarity.py` so that generated variations can:
1. **Maintain orthographic similarity distribution** (Light/Medium/Far)
2. **Follow specific transformation rules** (e.g., replace double letters, swap consonants)
3. **Meet rule percentage targets** (e.g., 30% of variations should follow rules)

## Current State

### What Exists:
- ✅ **Rule evaluators** (`rule_evaluator.py`) - Functions to CHECK if variations follow rules
- ✅ **Rule definitions** (`rule_extractor.py`) - List of all available rules
- ✅ **Orthographic generator** (`maximize_orthographic_similarity.py`) - Generates variations by similarity

### What's Missing:
- ❌ **Rule-based generation functions** - Functions to GENERATE variations following specific rules
- ❌ **Rule compliance integration** - Logic to ensure percentage of variations follow rules
- ❌ **Dual-constraint optimization** - Balancing orthographic similarity + rule compliance

---

## Strategy: Three-Phase Approach

### Phase 1: Rule-Based Generation Functions

**Goal**: Create functions that GENERATE variations following specific rules (not just check them).

**Implementation**:
```python
class OrthographicBruteForceGenerator:
    def generate_rule_compliant_variations(
        self, 
        word: str, 
        rules: List[str],
        max_per_rule: int = 50
    ) -> Set[str]:
        """
        Generate variations that follow specific rules.
        
        Args:
            word: Original word
            rules: List of rule names to apply
            max_per_rule: Maximum variations per rule
            
        Returns:
            Set of rule-compliant variations
        """
        variations = set()
        
        for rule in rules:
            if rule == "replace_double_letters_with_single_letter":
                variations.update(self._apply_double_letter_replacement(word, max_per_rule))
            elif rule == "swap_adjacent_consonants":
                variations.update(self._apply_consonant_swap(word, max_per_rule))
            elif rule == "delete_random_letter":
                variations.update(self._apply_letter_deletion(word, max_per_rule))
            # ... etc for all rules
        
        return variations
```

**Key Functions Needed**:
1. `_apply_double_letter_replacement()` - Replace "ll" → "l", "ee" → "e", etc.
2. `_apply_consonant_swap()` - Swap adjacent consonants: "John" → "Jhon"
3. `_apply_letter_deletion()` - Remove one letter: "John" → "Jon", "Jhn", "Joh"
4. `_apply_vowel_replacement()` - Replace vowels: "John" → "Jahn", "Jehn"
5. `_apply_space_replacement()` - Replace spaces with special chars: "John Smith" → "John_Smith"
6. `_apply_initial_conversion()` - Convert to initials: "John Smith" → "J. Smith"
7. ... (one function per rule)

---

### Phase 2: Dual-Constraint Selection

**Goal**: Select variations that meet BOTH orthographic similarity AND rule compliance requirements.

**Implementation**:
```python
def select_optimal_combination_with_rules(
    self,
    categorized: Dict[str, List[Tuple[str, float]]],  # By orthographic category
    rule_compliant_variations: Set[str],              # Rule-compliant variations
    total_count: int,
    rule_percentage: float = 0.30
) -> List[str]:
    """
    Select variations meeting both constraints:
    1. Orthographic distribution (Light/Medium/Far)
    2. Rule compliance percentage
    """
    # Calculate targets
    target_rule_count = int(total_count * rule_percentage)
    target_orthographic = {
        "Light": int(self.target_distribution["Light"] * total_count),
        "Medium": int(self.target_distribution["Medium"] * total_count),
        "Far": int(self.target_distribution["Far"] * total_count)
    }
    
    # Strategy: Two-pool approach
    # Pool 1: Rule-compliant variations (meet both constraints)
    # Pool 2: Non-rule-compliant variations (meet orthographic only)
    
    # Step 1: Score all rule-compliant variations
    rule_compliant_scored = []
    for var in rule_compliant_variations:
        score = self.calculate_orthographic_score(var)
        category = self.categorize_score(score)
        rule_compliant_scored.append((var, score, category))
    
    # Step 2: Select rule-compliant variations that also meet orthographic targets
    selected = []
    rule_count = 0
    
    # Prioritize rule-compliant variations that match orthographic categories
    for category in ["Light", "Medium", "Far"]:
        needed = target_orthographic[category]
        rule_compliant_in_category = [
            (v, s) for v, s, c in rule_compliant_scored 
            if c == category
        ]
        
        # Take rule-compliant variations first
        for var, score in rule_compliant_in_category[:needed]:
            if var not in selected and rule_count < target_rule_count:
                selected.append(var)
                rule_count += 1
    
    # Step 3: Fill remaining orthographic slots with non-rule-compliant variations
    # ... (existing logic)
    
    return selected
```

---

### Phase 3: Integration & Optimization

**Goal**: Integrate rule compliance into the main generation flow.

**Modified Flow**:
```python
def generate_optimal_variations(
    self, 
    variation_count: int = 15,
    rule_based: Dict[str, Any] = None  # NEW parameter
) -> Tuple[List[str], Dict]:
    """
    Generate variations with rule compliance support.
    """
    # Step 1: Generate rule-compliant variations (if rules specified)
    rule_compliant_variations = set()
    if rule_based and rule_based.get("selected_rules"):
        rules = rule_based["selected_rules"]
        rule_percentage = rule_based.get("rule_percentage", 30) / 100.0
        
        print(f"   Generating rule-compliant variations for {len(rules)} rules...")
        rule_compliant_variations = self.generate_rule_compliant_variations(
            self.original_name, 
            rules,
            max_per_rule=100
        )
        print(f"      Generated {len(rule_compliant_variations)} rule-compliant variations")
    
    # Step 2: Generate all orthographic variations (existing logic)
    categorized = self.generate_all_variations(max_candidates=10000)
    
    # Step 3: Select optimal combination (with rule compliance)
    if rule_compliant_variations:
        selected = self.select_optimal_combination_with_rules(
            categorized,
            rule_compliant_variations,
            variation_count,
            rule_percentage
        )
    else:
        selected = self.select_optimal_combination(categorized, variation_count)
    
    # Step 4: Verify rule compliance
    if rule_based:
        rule_compliance_score, metrics = self.verify_rule_compliance(
            selected,
            rule_based["selected_rules"],
            rule_percentage
        )
    
    return selected, metrics
```

---

## Implementation Details

### Rule Generation Functions

Each rule needs a dedicated generation function:

#### Example 1: Double Letter Replacement
```python
def _apply_double_letter_replacement(self, word: str, max_variations: int = 50) -> Set[str]:
    """Generate variations by replacing double letters with single letters."""
    variations = set()
    word_lower = word.lower()
    
    for i in range(len(word) - 1):
        if word_lower[i] == word_lower[i+1] and word_lower[i].isalpha():
            # Remove one of the double letters
            new_word = word[:i] + word[i+1:]
            variations.add(new_word)
            
            if len(variations) >= max_variations:
                break
    
    return variations
```

#### Example 2: Consonant Swap
```python
def _apply_consonant_swap(self, word: str, max_variations: int = 50) -> Set[str]:
    """Generate variations by swapping adjacent consonants."""
    variations = set()
    vowels = "aeiou"
    word_lower = word.lower()
    
    for i in range(len(word) - 1):
        char1 = word_lower[i]
        char2 = word_lower[i+1]
        
        # Check if both are different consonants
        if (char1.isalpha() and char1 not in vowels and
            char2.isalpha() and char2 not in vowels and
            char1 != char2):
            
            # Swap them
            new_word = word[:i] + word[i+1] + word[i] + word[i+2:]
            variations.add(new_word)
            
            if len(variations) >= max_variations:
                break
    
    return variations
```

#### Example 3: Letter Deletion
```python
def _apply_letter_deletion(self, word: str, max_variations: int = 50) -> Set[str]:
    """Generate variations by deleting one letter."""
    variations = set()
    
    for i in range(len(word)):
        if word[i].isalpha():
            new_word = word[:i] + word[i+1:]
            if new_word:  # Don't create empty strings
                variations.add(new_word)
            
            if len(variations) >= max_variations:
                break
    
    return variations
```

### Rule Mapping

Create a mapping from rule names to generation functions:

```python
RULE_GENERATORS = {
    "replace_double_letters_with_single_letter": "_apply_double_letter_replacement",
    "swap_adjacent_consonants": "_apply_consonant_swap",
    "delete_random_letter": "_apply_letter_deletion",
    "remove_random_vowel": "_apply_vowel_deletion",
    "remove_random_consonant": "_apply_consonant_deletion",
    "replace_random_vowel_with_random_vowel": "_apply_vowel_replacement",
    "replace_random_consonant_with_random_consonant": "_apply_consonant_replacement",
    "swap_random_letter": "_apply_letter_swap",
    "insert_random_letter": "_apply_letter_insertion",
    "duplicate_random_letter_as_double_letter": "_apply_letter_duplication",
    "remove_all_spaces": "_apply_space_removal",
    "replace_spaces_with_random_special_characters": "_apply_space_replacement",
    "initial_only_first_name": "_apply_first_name_initial",
    "shorten_name_to_initials": "_apply_initials",
    "shorten_name_to_abbreviations": "_apply_abbreviation",
    "name_parts_permutations": "_apply_name_permutation",
}
```

---

## Challenges & Solutions

### Challenge 1: Rule Compliance vs Orthographic Similarity

**Problem**: A variation that follows a rule might not match the desired orthographic category.

**Solution**: 
- Generate many rule-compliant variations
- Score them all for orthographic similarity
- Select those that meet BOTH constraints
- Use non-rule-compliant variations to fill remaining slots

### Challenge 2: Rule Percentage Target

**Problem**: Need exactly X% of variations to follow rules.

**Solution**:
- Calculate target count: `int(total_count * rule_percentage)`
- Prioritize rule-compliant variations in selection
- Track rule compliance during selection
- Verify final compliance and adjust if needed

### Challenge 3: Multiple Rules

**Problem**: Multiple rules might generate overlapping variations.

**Solution**:
- Generate variations for each rule separately
- Combine into a single set (automatic deduplication)
- Track which rule(s) each variation satisfies
- Reward diversity (variations satisfying multiple rules)

---

## Testing Strategy

### Test Cases:

1. **Single Rule, 30% Target**
   ```python
   rule_based = {
       "selected_rules": ["replace_double_letters_with_single_letter"],
       "rule_percentage": 30
   }
   # Expected: 5 out of 15 variations should follow the rule
   ```

2. **Multiple Rules, 50% Target**
   ```python
   rule_based = {
       "selected_rules": [
           "replace_double_letters_with_single_letter",
           "swap_adjacent_consonants"
       ],
       "rule_percentage": 50
   }
   # Expected: 8 out of 15 variations should follow at least one rule
   ```

3. **100% Rule Compliance**
   ```python
   rule_based = {
       "selected_rules": ["delete_random_letter"],
       "rule_percentage": 100
   }
   # Expected: ALL 15 variations should follow the rule
   ```

4. **Orthographic + Rule Compliance**
   ```python
   # Should still maintain Light/Medium/Far distribution
   # While also meeting rule percentage
   ```

---

## Implementation Priority

### Phase 1 (High Priority):
1. ✅ Implement rule generation functions for top 5 rules:
   - `replace_double_letters_with_single_letter`
   - `swap_adjacent_consonants`
   - `delete_random_letter`
   - `remove_random_vowel`
   - `insert_random_letter`

### Phase 2 (Medium Priority):
2. ✅ Implement remaining rule generation functions
3. ✅ Integrate rule compliance into selection logic
4. ✅ Add rule compliance verification

### Phase 3 (Low Priority):
5. ✅ Optimize for rule diversity
6. ✅ Add rule compliance metrics to output
7. ✅ Handle edge cases (impossible rules, etc.)

---

## Expected Benefits

1. **Better Test Coverage**: Variations that follow known transformation patterns
2. **Validator Alignment**: Matches what the validator expects
3. **Flexibility**: Can generate with or without rule compliance
4. **Quality**: Variations are both similar AND follow realistic obfuscation patterns

---

## Next Steps

1. **Review this strategy** with the team
2. **Implement Phase 1** (top 5 rule functions)
3. **Test with sample names** and verify rule compliance
4. **Integrate into main generator** (Phase 2)
5. **Validate against validator** to ensure compatibility

