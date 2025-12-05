# Rule Compliance Implementation Strategy

## Core Strategy

**Goal**: Generate variations that:
1. ✅ Follow possible rules (filter impossible ones first)
2. ✅ Meet orthographic similarity requirements (Light/Medium/Far)
3. ✅ Meet rule percentage target (e.g., 30% of 15 = ~5 variations)
4. ✅ Don't compromise orthographic scores

---

## Step-by-Step Implementation

### Step 1: Filter Impossible Rules (Pre-check)

**Before generating any variations**, check which rules are possible for the given name:

```python
def filter_possible_rules(original_name: str, target_rules: List[str]) -> List[str]:
    """
    Filter out rules that are impossible for the given name structure.
    
    Returns:
        List of rules that CAN be applied to this name
    """
    possible_rules = []
    
    for rule in target_rules:
        # Rule: Name parts permutations / initials (require multi-part name)
        if rule in ('name_parts_permutations', 'initial_only_first_name', 
                    'shorten_name_to_initials', 'shorten_name_to_abbreviations'):
            if len(original_name.split()) < 2:
                continue  # Skip - single-part name can't use this rule
        
        # Rule: Space removal/replacement (requires a space)
        if rule in ('replace_spaces_with_random_special_characters', 'remove_all_spaces'):
            if ' ' not in original_name:
                continue  # Skip - no spaces in name
        
        # Rule: Double letter replacement (requires double letters)
        if rule == 'replace_double_letters_with_single_letter':
            if not has_double_letters(original_name):
                continue  # Skip - no double letters
        
        # Rule: Adjacent consonant swap (requires swappable consonants)
        if rule == 'swap_adjacent_consonants':
            if not has_diff_adjacent_consonants(original_name):
                continue  # Skip - no swappable consonants
        
        possible_rules.append(rule)
    
    return possible_rules
```

**Example**:
- Original: `"John"` (single word, no double letters)
- Target rules: `["replace_double_letters_with_single_letter", "swap_adjacent_consonants", "name_parts_permutations"]`
- Possible rules: `["swap_adjacent_consonants"]` ✅

---

### Step 2: Generate Rule-Compliant Variations (With Orthographic Scoring)

**Generate variations that follow rules AND maintain orthographic similarity**:

```python
def generate_rule_compliant_variations_with_scores(
    self,
    original_name: str,
    possible_rules: List[str],
    target_distribution: Dict[str, float],
    max_per_rule: int = 100
) -> Dict[str, List[Tuple[str, float, str]]]:
    """
    Generate rule-compliant variations and score them for orthographic similarity.
    
    Returns:
        Dictionary mapping rule_name -> [(variation, orthographic_score, category), ...]
    """
    rule_compliant_scored = {}
    
    for rule in possible_rules:
        # Generate variations following this rule
        rule_variations = self.generate_rule_compliant_variations(
            original_name,
            [rule],
            max_per_rule
        )
        
        # Score each variation for orthographic similarity
        scored_variations = []
        for var in rule_variations:
            score = self.calculate_orthographic_score(var)
            category = self.categorize_score(score)  # Light/Medium/Far
            scored_variations.append((var, score, category))
        
        # Sort by score (descending) to prioritize high-similarity variations
        scored_variations.sort(key=lambda x: x[1], reverse=True)
        
        rule_compliant_scored[rule] = scored_variations
    
    return rule_compliant_scored
```

**Key Point**: Each rule-compliant variation is **also scored** for orthographic similarity!

**Example Output**:
```python
rule_compliant_scored = {
    "swap_adjacent_consonants": [
        ("Jhon Smith", 0.85, "Light"),    # High orthographic score ✅
        ("Jhon Smyth", 0.72, "Medium"),  # Medium orthographic score ✅
        ("Jhon Smth", 0.45, "Far")       # Lower orthographic score ⚠️
    ],
    "delete_random_letter": [
        ("Jon Smith", 0.88, "Light"),    # High orthographic score ✅
        ("Jhn Smith", 0.65, "Medium"),   # Medium orthographic score ✅
    ]
}
```

---

### Step 3: Select Optimal Mix (Dual Constraint)

**Select variations that meet BOTH constraints**:

```python
def select_optimal_combination_with_rules(
    self,
    categorized: Dict[str, List[Tuple[str, float]]],  # Non-rule variations by orthographic category
    rule_compliant_scored: Dict[str, List[Tuple[str, float, str]]],  # Rule-compliant variations
    total_count: int,
    rule_percentage: float = 0.30,
    target_distribution: Dict[str, float] = None
) -> List[str]:
    """
    Select variations meeting BOTH:
    1. Orthographic distribution (Light/Medium/Far)
    2. Rule compliance percentage
    """
    target_rule_count = int(total_count * rule_percentage)  # e.g., 5 out of 15
    target_orthographic = {
        "Light": int(target_distribution["Light"] * total_count),
        "Medium": int(target_distribution["Medium"] * total_count),
        "Far": int(target_distribution["Far"] * total_count)
    }
    
    selected = []
    rule_count = 0
    
    # Strategy: Prioritize rule-compliant variations that ALSO match orthographic categories
    for category in ["Light", "Medium", "Far"]:
        needed = target_orthographic[category]
        selected_in_category = 0
        
        # First, try to fill with rule-compliant variations in this category
        for rule, scored_vars in rule_compliant_scored.items():
            for var, score, var_category in scored_vars:
                if (var_category == category and 
                    var not in selected and 
                    rule_count < target_rule_count and
                    selected_in_category < needed):
                    selected.append(var)
                    rule_count += 1
                    selected_in_category += 1
                    if rule_count >= target_rule_count:
                        break
            if rule_count >= target_rule_count:
                break
        
        # Fill remaining slots with non-rule-compliant variations
        remaining = needed - selected_in_category
        if remaining > 0:
            non_rule_in_category = [
                (v, s) for v, s in categorized[category] 
                if v not in selected
            ]
            for var, score in non_rule_in_category[:remaining]:
                selected.append(var)
                selected_in_category += 1
    
    return selected[:total_count]
```

**Key Strategy**:
1. ✅ **Prioritize rule-compliant variations** that match orthographic categories
2. ✅ **Fill remaining slots** with non-rule-compliant variations
3. ✅ **Maintain orthographic distribution** while meeting rule percentage

---

### Step 4: Complete Flow

```python
def generate_optimal_variations_with_rules(
    self,
    variation_count: int = 15,
    rule_based: Dict[str, Any] = None
) -> Tuple[List[str], Dict]:
    """
    Complete flow: Generate variations with rule compliance.
    """
    # Step 1: Filter impossible rules
    target_rules = rule_based.get("selected_rules", []) if rule_based else []
    possible_rules = filter_possible_rules(self.original_name, target_rules)
    
    print(f"   Target rules: {target_rules}")
    print(f"   Possible rules: {possible_rules}")
    
    # Step 2: Generate rule-compliant variations (with orthographic scores)
    rule_compliant_scored = {}
    if possible_rules:
        rule_compliant_scored = self.generate_rule_compliant_variations_with_scores(
            self.original_name,
            possible_rules,
            self.target_distribution,
            max_per_rule=100
        )
        print(f"   Generated rule-compliant variations: {sum(len(v) for v in rule_compliant_scored.values())}")
    
    # Step 3: Generate all orthographic variations (existing logic)
    categorized = self.generate_all_variations(max_candidates=10000)
    
    # Step 4: Select optimal mix (dual constraint)
    rule_percentage = rule_based.get("rule_percentage", 30) / 100.0 if rule_based else 0.0
    
    if rule_compliant_scored:
        selected = self.select_optimal_combination_with_rules(
            categorized,
            rule_compliant_scored,
            variation_count,
            rule_percentage,
            self.target_distribution
        )
    else:
        # No rules possible, use regular selection
        selected = self.select_optimal_combination(categorized, variation_count)
    
    # Step 5: Verify both constraints are met
    final_scores = [self.calculate_orthographic_score(var) for var in selected]
    final_categories = {cat: [] for cat in ["Light", "Medium", "Far"]}
    
    for var, score in zip(selected, final_scores):
        category = self.categorize_score(score)
        final_categories[category].append((var, score))
    
    # Verify rule compliance
    if rule_based and possible_rules:
        rule_compliance_score, rule_metrics = calculate_rule_compliance_score(
            self.original_name,
            selected,
            possible_rules,
            rule_percentage
        )
        print(f"   Rule compliance score: {rule_compliance_score:.2f}")
    
    return selected, metrics
```

---

## Key Principles

### 1. **Filter First, Generate Second**
- ✅ Check which rules are possible BEFORE generating
- ❌ Don't waste time generating variations for impossible rules

### 2. **Score Rule-Compliant Variations**
- ✅ Every rule-compliant variation is scored for orthographic similarity
- ✅ This ensures rule compliance doesn't compromise orthographic quality

### 3. **Dual Constraint Selection**
- ✅ Prioritize rule-compliant variations that ALSO match orthographic categories
- ✅ Fill remaining slots with non-rule-compliant variations
- ✅ Maintain both orthographic distribution AND rule percentage

### 4. **Accommodate All Possible Rules**
- ✅ Generate variations for ALL possible rules (not just one)
- ✅ Reward diversity: variations satisfying multiple different rules
- ✅ Ensure all rules are represented in the final selection

---

## Example Flow

### Input:
- **Original**: `"John Smith"`
- **Variation count**: 15
- **Rule percentage**: 30% (5 variations)
- **Target rules**: `["replace_double_letters_with_single_letter", "swap_adjacent_consonants", "name_parts_permutations"]`
- **Orthographic distribution**: Light=20%, Medium=60%, Far=20%

### Step 1: Filter Rules
```
Target rules: ["replace_double_letters_with_single_letter", "swap_adjacent_consonants", "name_parts_permutations"]
Possible rules: ["swap_adjacent_consonants", "name_parts_permutations"]
  - "replace_double_letters_with_single_letter" → ❌ No double letters in "John Smith"
```

### Step 2: Generate Rule-Compliant Variations (With Scores)
```
Rule: "swap_adjacent_consonants"
  - "Jhon Smith" → Score: 0.85 (Light) ✅
  - "Jhon Smyth" → Score: 0.72 (Medium) ✅
  - "Jhon Smth" → Score: 0.45 (Far) ✅

Rule: "name_parts_permutations"
  - "Smith John" → Score: 0.75 (Light) ✅
  - "Smith J. John" → Score: 0.55 (Medium) ✅
```

### Step 3: Select Optimal Mix
```
Target orthographic: Light=3, Medium=9, Far=3
Target rule-compliant: 5 variations

Selection:
  Light (3 needed):
    - "Jhon Smith" (rule-compliant) ✅
    - "Smith John" (rule-compliant) ✅
    - [1 non-rule Light variation]
  
  Medium (9 needed):
    - "Jhon Smyth" (rule-compliant) ✅
    - "Smith J. John" (rule-compliant) ✅
    - [7 non-rule Medium variations]
  
  Far (3 needed):
    - "Jhon Smth" (rule-compliant) ✅
    - [2 non-rule Far variations]

Total: 15 variations
Rule-compliant: 5 variations (33%) ✅
Orthographic distribution: Light=3, Medium=9, Far=3 ✅
```

---

## Benefits of This Strategy

1. ✅ **No Orthographic Score Compromise**: Rule-compliant variations are scored and selected based on orthographic similarity
2. ✅ **All Rules Accommodated**: All possible rules are represented in the final selection
3. ✅ **Dual Constraint Satisfaction**: Both orthographic distribution AND rule percentage are met
4. ✅ **Efficient**: Filters impossible rules first, avoiding wasted generation
5. ✅ **Quality**: Prioritizes high-quality rule-compliant variations (high orthographic scores)

---

## Implementation Checklist

- [ ] Implement `filter_possible_rules()` function
- [ ] Implement `generate_rule_compliant_variations_with_scores()` function
- [ ] Implement `select_optimal_combination_with_rules()` function
- [ ] Integrate into main `generate_optimal_variations()` flow
- [ ] Test with various name structures and rule combinations
- [ ] Verify orthographic scores are maintained
- [ ] Verify rule compliance percentage is met
- [ ] Verify all possible rules are accommodated

