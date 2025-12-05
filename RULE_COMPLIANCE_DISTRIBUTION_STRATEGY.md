# Strategy: Distributing Rule Compliance Across Orthographic Categories

## Problem Statement

**Current Issue:**
- Rule-compliant variations only exist in **Light** category (0.70-1.00 similarity)
- No rule-compliant variations in **Medium** (0.50-0.69) or **Far** (0.20-0.49) categories
- Cannot achieve 30% rule compliance while maintaining orthographic distribution

**Root Cause:**
- Simple rule applications (delete/insert/swap 1 letter) make minimal changes
- Minimal changes = high similarity = Light category only

---

## Strategy Overview

### Phase 1: Multi-Level Rule Application
Generate rule-compliant variations at different "aggression levels" to target different orthographic categories.

### Phase 2: Category-Aware Rule Generation
Modify rule generation functions to produce variations targeting specific similarity ranges.

### Phase 3: Smart Selection Algorithm
Enhance selection logic to prioritize rule-compliant variations that match target categories.

---

## Detailed Strategy

### 1. Multi-Level Rule Application

**Concept:** Apply rules with different "intensity" levels to target different similarity ranges.

#### Level 1: Light Category (0.70-1.00)
- **Single letter operations:** Delete 1 letter, insert 1 letter, swap 2 adjacent letters
- **Current behavior:** Already working ✅

#### Level 2: Medium Category (0.50-0.69)
- **Multiple letter operations:** Delete 2-3 letters, insert 2 letters, swap multiple letters
- **Combined operations:** Delete + swap, insert + delete
- **Target:** Reduce similarity to Medium range

#### Level 3: Far Category (0.20-0.49)
- **Aggressive operations:** Delete 3-4 letters, insert 3+ letters, multiple swaps
- **Multiple rule combinations:** Delete + insert + swap
- **Target:** Reduce similarity to Far range

### 2. Enhanced Rule Generation Functions

Modify existing rule functions to accept an "aggression" parameter:

```python
def _apply_letter_deletion(self, word: str, max_variations: int = 50, 
                          aggression: int = 1) -> Set[str]:
    """
    Generate variations by deleting letters.
    
    Args:
        aggression: Number of letters to delete (1=Light, 2-3=Medium, 3-4=Far)
    """
    variations = set()
    
    if aggression == 1:
        # Light: Delete 1 letter
        for i in range(len(word)):
            if word[i].isalpha():
                new_word = word[:i] + word[i+1:]
                if new_word and new_word != word:
                    variations.add(new_word)
    
    elif aggression == 2:
        # Medium: Delete 2 letters
        for i in range(len(word)):
            for j in range(i+1, len(word)):
                if word[i].isalpha() and word[j].isalpha():
                    new_word = word[:i] + word[i+1:j] + word[j+1:]
                    if new_word and new_word != word:
                        variations.add(new_word)
    
    elif aggression >= 3:
        # Far: Delete 3+ letters
        for i in range(len(word)):
            for j in range(i+1, len(word)):
                for k in range(j+1, len(word)):
                    if word[i].isalpha() and word[j].isalpha() and word[k].isalpha():
                        new_word = word[:i] + word[i+1:j] + word[j+1:k] + word[k+1:]
                        if new_word and new_word != word:
                            variations.add(new_word)
    
    return variations
```

### 3. Category-Targeted Rule Generation

Generate rule-compliant variations specifically for each category:

```python
def generate_rule_compliant_by_category(
    self,
    category: str,  # "Light", "Medium", or "Far"
    rules: List[str],
    max_per_rule: int = 100
) -> List[Tuple[str, float, str]]:
    """
    Generate rule-compliant variations targeting a specific orthographic category.
    
    Strategy:
    - Light: Use aggression=1 (minimal changes)
    - Medium: Use aggression=2-3 (moderate changes)
    - Far: Use aggression=3-4 (aggressive changes)
    """
    target_range = {
        "Light": (0.70, 1.00),
        "Medium": (0.50, 0.69),
        "Far": (0.20, 0.49)
    }[category]
    
    aggression_map = {
        "Light": 1,
        "Medium": 2,
        "Far": 3
    }
    
    aggression = aggression_map[category]
    variations = []
    
    for rule in rules:
        # Generate variations with appropriate aggression
        rule_variations = self._apply_rule_with_aggression(
            self.original_name,
            rule,
            aggression,
            max_per_rule
        )
        
        # Score and filter by target range
        for var in rule_variations:
            score = self.calculate_orthographic_score(var)
            if target_range[0] <= score <= target_range[1]:
                variations.append((var, score, category))
    
    return variations
```

### 4. Enhanced Selection Algorithm

Modify `select_optimal_combination_with_rules` to:

1. **Generate rule-compliant variations for each category separately**
2. **Prioritize rule-compliant variations that match their target category**
3. **Fill remaining slots with non-rule variations**

```python
def select_optimal_combination_with_rules_enhanced(
    self,
    categorized: Dict[str, List[Tuple[str, float]]],
    total_count: int
) -> List[str]:
    """
    Enhanced selection that generates rule-compliant variations for each category.
    """
    target_rule_count = max(1, int(total_count * self.rule_percentage))
    target_orthographic = {
        "Light": int(self.target_distribution.get("Light", 0.0) * total_count),
        "Medium": int(self.target_distribution.get("Medium", 0.0) * total_count),
        "Far": int(self.target_distribution.get("Far", 0.0) * total_count)
    }
    
    # Generate rule-compliant variations for EACH category
    rule_compliant_by_category = {}
    for category in ["Light", "Medium", "Far"]:
        rule_compliant_by_category[category] = self.generate_rule_compliant_by_category(
            category=category,
            rules=self.possible_rules,
            max_per_rule=50
        )
    
    selected = []
    rule_count = 0
    rule_count_by_category = {"Light": 0, "Medium": 0, "Far": 0}
    
    # Phase 1: Fill each category with rule-compliant variations
    for category in ["Light", "Medium", "Far"]:
        needed = target_orthographic[category]
        available_rule_compliant = rule_compliant_by_category[category]
        
        # Take as many rule-compliant as possible (up to target_rule_count)
        rule_taken = min(
            needed,
            len(available_rule_compliant),
            target_rule_count - rule_count
        )
        
        # Add rule-compliant variations
        for var, score, cat in available_rule_compliant[:rule_taken]:
            selected.append(var)
            rule_count += 1
            rule_count_by_category[category] += 1
        
        # Fill remaining with non-rule variations
        remaining = needed - rule_taken
        if remaining > 0:
            non_rule_in_category = [
                (v, s) for v, s in categorized[category] 
                if v not in selected
            ]
            for var, score in non_rule_in_category[:remaining]:
                selected.append(var)
    
    # Phase 2: If we need more rule-compliant, add from any category
    if rule_count < target_rule_count:
        for category in ["Light", "Medium", "Far"]:
            if rule_count >= target_rule_count:
                break
            
            available = rule_compliant_by_category[category]
            for var, score, cat in available:
                if var not in selected and rule_count < target_rule_count:
                    selected.append(var)
                    rule_count += 1
                    rule_count_by_category[category] += 1
                    if rule_count >= target_rule_count:
                        break
    
    return selected[:total_count]
```

---

## Implementation Plan

### Step 1: Add Aggression Parameter to Rule Functions
- Modify `_apply_letter_deletion`, `_apply_letter_insertion`, `_apply_letter_swap`
- Add support for multiple letter operations

### Step 2: Create Category-Targeted Generation
- Implement `generate_rule_compliant_by_category` method
- Test that it produces variations in target categories

### Step 3: Update Selection Algorithm
- Replace `select_optimal_combination_with_rules` with enhanced version
- Ensure it distributes rule compliance across categories

### Step 4: Testing
- Verify rule-compliant variations exist in all categories
- Verify 30% rule compliance can be achieved
- Verify orthographic distribution is maintained

---

## Expected Results

### Before (Current):
- Rule-compliant: 3 Light, 0 Medium, 0 Far = 3 total (20%)
- Cannot achieve 30% rule compliance

### After (With Strategy):
- Rule-compliant: 1-2 Light, 2-3 Medium, 0-1 Far = 4-5 total (30%)
- Can achieve 30% rule compliance
- Maintains orthographic distribution

---

## Example Distribution

**Target:** 3 Light, 9 Medium, 3 Far | 4 rule-compliant

**After Implementation:**
- Light: 3 total (1 rule-compliant, 2 non-rule)
- Medium: 9 total (2 rule-compliant, 7 non-rule)
- Far: 3 total (1 rule-compliant, 2 non-rule)
- **Total rule-compliant: 4 (30%)** ✅

---

## Risk Mitigation

1. **Rule Validation:** Ensure aggressive rule applications still pass validator checks
2. **Quality Control:** Verify variations are still recognizable as name variations
3. **Performance:** Monitor generation time (more aggressive = more variations to generate)

---

## Next Steps

1. Implement aggression parameter in rule functions
2. Create category-targeted generation method
3. Update selection algorithm
4. Test with sanctioned names
5. Verify distribution across all categories

