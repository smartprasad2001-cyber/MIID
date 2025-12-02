# How Similarity is Calculated

## Overview

The validator calculates similarity in **two steps**:
1. **Individual Similarity**: Calculate phonetic similarity for each variation (0.0-1.0)
2. **Distribution Matching**: Check if variations match the required distribution (Light/Medium/Far)

## Step 1: Phonetic Similarity Calculation

### Algorithm
Uses **3 phonetic algorithms** (Soundex, Metaphone, NYSIIS) with randomized selection and weights:

```python
def calculate_phonetic_similarity(original_name, variation):
    # 1. Select 3 algorithms randomly (but deterministically based on original_name)
    algorithms = ["soundex", "metaphone", "nysiis"]
    selected = random.sample(algorithms, k=3)  # All 3 are selected
    
    # 2. Generate random weights for each algorithm
    weights = [random.random() for each algorithm]
    weights = normalize(weights)  # Sum to 1.0
    
    # 3. Calculate weighted score
    score = 0.0
    for algo, weight in zip(selected, weights):
        if algo(original_name) == algo(variation):
            score += weight  # Algorithm matches = add weight
        # else: score += 0
    
    return score  # 0.0 (no match) to 1.0 (all algorithms match)
```

### Examples:
- "John" vs "Jon": All 3 algorithms match → **1.0000**
- "John" vs "Jhon": 1-2 algorithms match → **0.5690**
- "John" vs "Joh": No algorithms match → **0.0000**

### Key Points:
- **Binary matching**: Each algorithm returns 1 (match) or 0 (no match)
- **Weighted average**: Final score = weighted sum of algorithm matches
- **Deterministic per name**: Same name always uses same algorithms/weights in one run

## Step 2: Distribution Matching

### Boundaries:
- **Light**: 0.8 - 1.0 (high similarity)
- **Medium**: 0.6 - 0.8 (moderate similarity)
- **Far**: 0.3 - 0.6 (low similarity)
- **Too Low**: < 0.3 (penalized)

### Process:

1. **Calculate phonetic similarity** for each variation
2. **Categorize** each score into Light/Medium/Far
3. **Count** how many fall into each category
4. **Compare** against target distribution (e.g., 20% Light, 60% Medium, 20% Far)
5. **Calculate match quality** for each level:
   ```python
   match_ratio = actual_count / target_count
   
   if match_ratio <= 1.0:
       match_quality = match_ratio  # Linear: 0.5 count = 0.5 quality
   else:
       match_quality = 1.0 - exp(-(match_ratio - 1.0))  # Diminishing returns
   ```
6. **Sum weighted match quality**:
   ```python
   similarity_score = sum(
       target_percentage * match_quality 
       for each level (Light, Medium, Far)
   )
   ```
7. **Apply penalty** for unmatched variations:
   ```python
   unmatched = total - matched
   penalty = 0.1 * (unmatched / total)
   similarity_score = max(0.0, similarity_score - penalty)
   ```

### Example Calculation:

**Target**: 20% Light (1-2), 60% Medium (4-5), 20% Far (1-2) for 8 variations

**Actual scores**: [1.0, 0.7, 0.7, 0.7, 0.7, 0.4, 0.4, 0.4]
- Light (0.8-1.0): 1 variation (target: 1-2)
- Medium (0.6-0.8): 4 variations (target: 4-5)
- Far (0.3-0.6): 3 variations (target: 1-2)

**Calculation**:
- Light: 1/2 = 0.5 match_quality → 0.2 × 0.5 = **0.10**
- Medium: 4/5 = 0.8 match_quality → 0.6 × 0.8 = **0.48**
- Far: 3/2 = 1.5 match_ratio → 1.0 - exp(-0.5) = 0.39 match_quality → 0.2 × 0.39 = **0.078**
- Total: 0.10 + 0.48 + 0.078 = **0.658**

**Penalty**: 0 unmatched → no penalty

**Final similarity score**: **0.658**

## Why Similarity Score is 0.0

The similarity score becomes 0.0 when:

1. **Distribution doesn't match**: If actual distribution is very different from target
2. **Too many unmatched**: Penalty reduces score below 0
3. **Minimum threshold**: If similarity_score < 0.2, it's multiplied by 0.1 (keeps only 10%)

### Current Issue:
- We have: Light 1, Medium 4, Far 3 (for 8 variations)
- Target: Light 1-2, Medium 4-5, Far 1-2
- Problem: **3 Far variations is too many** (target is 1-2)
- This causes Far match_quality to be low, reducing overall score

## Solution

To fix similarity score:
1. **Generate exactly 1-2 Far variations** (not 3)
2. **Ensure distribution matches exactly** for both first name AND last name separately
3. **Avoid variations with < 0.3 similarity** (they're penalized)

