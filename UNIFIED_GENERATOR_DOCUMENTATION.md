# Unified Generator - Complete Documentation

## Table of Contents
1. [Overview](#overview)
2. [End-to-End Flow](#end-to-end-flow)
3. [How It Matches rewards.py](#how-it-matches-rewardspy)
4. [Detailed Step-by-Step Process](#detailed-step-by-step-process)
5. [Strategy Details](#strategy-details)
6. [Examples](#examples)

---

## Overview

The **Unified Generator** generates name variations (Light, Medium, Far) that match the validator's (`rewards.py`) expectations. It uses **51 different strategies** to generate variations and categorizes them using the same phonetic similarity algorithms as the validator.

### Key Principles

1. **Part-Based Categorization**: Categorizes first and last names separately (matching rewards.py)
2. **No Combined Scores**: Doesn't calculate combined scores for categorization - just ensures enough Light/Medium/Far for each part
3. **51 Strategies**: Uses comprehensive transformation strategies to generate diverse variations
4. **Phonetic Matching**: Uses the same `calculate_phonetic_similarity` function as rewards.py

---

## End-to-End Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    INPUT: Full Name                             │
│                    "John Smith"                                │
│                    Distribution: 4 Light, 8 Medium, 3 Far     │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: Split into Parts                                      │
│  - First name: "John"                                          │
│  - Last name: "Smith"                                          │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: Generate First Name Variations                         │
│  - Use 51 strategies to generate candidates                    │
│  - Request: 12 Light, 24 Medium, 9 Far (3x target)            │
│  - Output: Many candidate variations                           │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: Categorize First Name Variations                       │
│  - Score each: calculate_phonetic_similarity("John", var)     │
│  - Categorize:                                                │
│    • Light: score >= 0.8                                       │
│    • Medium: 0.6 <= score <= 0.79                              │
│    • Far: 0.3 <= score <= 0.59                                 │
│  - Store: first_light, first_medium, first_far                │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 4: Generate Last Name Variations                          │
│  - Use 51 strategies to generate candidates                    │
│  - Request: 12 Light, 24 Medium, 9 Far (3x target)            │
│  - Output: Many candidate variations                           │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 5: Categorize Last Name Variations                        │
│  - Score each: calculate_phonetic_similarity("Smith", var)    │
│  - Categorize:                                                │
│    • Light: score >= 0.8                                       │
│    • Medium: 0.6 <= score <= 0.79                              │
│    • Far: 0.3 <= score <= 0.59                                 │
│  - Store: last_light, last_medium, last_far                   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 6: Build Lists with Correct Distribution                 │
│  - first_name_list = [4 Light, 8 Medium, 3 Far]               │
│  - last_name_list = [4 Light, 8 Medium, 3 Far]                 │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 7: Combine into Full Names                                │
│  - Combine first_name_list × last_name_list                     │
│  - Ensure no duplicates                                        │
│  - Output: 15 full name variations                             │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    OUTPUT: Full Name Variations                 │
│  ['Jon Smaith', 'Jokn Smeith', 'Jomn Smiith', ...]             │
│  When rewards.py splits these, it will see:                    │
│  - First names: 4 Light, 8 Medium, 3 Far                       │
│  - Last names: 4 Light, 8 Medium, 3 Far                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## How It Matches rewards.py

### rewards.py Approach

When `rewards.py` receives variations, it:

1. **Splits full names into parts**:
   ```python
   first_name_variations = ['Jon', 'Jokn', 'Jomn', ...]
   last_name_variations = ['Smaith', 'Smeith', 'Smiith', ...]
   ```

2. **Calls `calculate_part_score()` for first name**:
   - Scores each variation: `calculate_phonetic_similarity("John", var)`
   - Categorizes each: Light (>=0.8), Medium (0.6-0.79), Far (0.3-0.59)
   - Checks distribution
   - Returns overall `first_name_score` (e.g., 0.5840)

3. **Calls `calculate_part_score()` for last name**:
   - Scores each variation: `calculate_phonetic_similarity("Smith", var)`
   - Categorizes each: Light (>=0.8), Medium (0.6-0.79), Far (0.3-0.59)
   - Checks distribution
   - Returns overall `last_name_score` (e.g., 0.6646)

4. **Combines overall part scores**:
   ```python
   base_score = (first_name_score × first_weight) + (last_name_score × last_weight)
   base_score = (0.5840 × 0.40) + (0.6646 × 0.60) = 0.6325
   ```

### Unified Generator Approach

The unified generator **matches this exactly**:

1. **Generates variations for each part separately**
2. **Categorizes each part separately** using the same scoring function
3. **Ensures correct distribution** for each part
4. **Combines them** so when rewards.py splits them back, it sees the right distribution

### Key Match Points

| Aspect | rewards.py | Unified Generator | Match? |
|--------|------------|-------------------|--------|
| Scoring Function | `calculate_phonetic_similarity()` | `calculate_phonetic_similarity()` | ✅ Same |
| Categorization | Light (>=0.8), Medium (0.6-0.79), Far (0.3-0.59) | Light (>=0.8), Medium (0.6-0.79), Far (0.3-0.59) | ✅ Same |
| Part Processing | Each part separately | Each part separately | ✅ Same |
| Distribution Check | Checks distribution for each part | Ensures distribution for each part | ✅ Same |
| Score Combination | Combines overall part scores | N/A (generation only) | ✅ N/A |

---

## Detailed Step-by-Step Process

### Step 1: Input Processing

**Function**: `generate_full_name_variations()`

```python
Input:
  full_name = "John Smith"
  light_count = 4
  medium_count = 8
  far_count = 3

Process:
  1. Split: first_name = "John", last_name = "Smith"
  2. Calculate target counts for generation (3x to ensure enough)
     - Request: 12 Light, 24 Medium, 9 Far for each part
```

### Step 2: Generate First Name Variations

**Function**: `generate_variations_unified()`

```python
Input:
  original = "John"
  light_count = 12
  medium_count = 24
  far_count = 9

Process:
  1. Use 51 strategies to generate candidate variations
  2. Recursively generate variations (max_depth = 5)
  3. For each candidate:
     - Calculate phonetic score
     - Categorize: Light/Medium/Far
     - Add to appropriate list
  4. Return: {'light': [...], 'medium': [...], 'far': [...]}

Output Example:
  {
    'light': ['Jon', 'Jaohn', 'Jeohn', ...],
    'medium': ['Jokn', 'Jomn', 'Johm', ...],
    'far': ['Johyn', 'Johny', 'Jown', ...]
  }
```

### Step 3: Categorize First Name Variations

**Function**: Inside `generate_full_name_variations()`

```python
Input:
  first_results = {'light': [...], 'medium': [...], 'far': [...]}

Process:
  1. For each variation in all lists:
     score = calculate_phonetic_similarity("John", var)
     
     if score >= 0.8:
         first_light.append(var)
     elif 0.6 <= score <= 0.79:
         first_medium.append(var)
     elif 0.3 <= score <= 0.59:
         first_far.append(var)

  2. Ensure we have enough:
     first_light = first_light[:max(light_count, 5)]
     first_medium = first_medium[:max(medium_count, 5)]
     first_far = first_far[:max(far_count, 5)]

Output:
  first_light = ['Jon', 'Jaohn', 'Jeohn', 'Jiohn', 'Joohn']
  first_medium = ['Jokn', 'Jomn', 'Johm', 'Jhon', 'Jonh', 'Jhohn', 'Jonhn', 'Johkn']
  first_far = ['Johyn', 'Johny', 'Jown', 'Joyn', 'Jokn']
```

### Step 4: Generate Last Name Variations

**Same process as Step 2, but for "Smith"**

```python
Output:
  {
    'light': ['Smaith', 'Smeith', 'Smiith', ...],
    'medium': ['Smit', 'Smitah', 'Smiteh', ...],
    'far': ['Smth', 'Samith', 'Semith', ...]
  }
```

### Step 5: Categorize Last Name Variations

**Same process as Step 3, but for "Smith"**

```python
Output:
  last_light = ['Smaith', 'Smeith', 'Smiith', 'Smoith']
  last_medium = ['Smit', 'Smitah', 'Smiteh', 'Smitih', 'Smitoh', 'Smituh', 'Snith', 'Smits']
  last_far = ['Smth', 'Samith', 'Semith']
```

### Step 6: Build Lists with Correct Distribution

**Function**: Inside `generate_full_name_variations()`

```python
Process:
  1. Build first_name_list:
     first_name_list = []
     first_name_list.extend(first_light[:light_count])      # 4 Light
     first_name_list.extend(first_medium[:medium_count])   # 8 Medium
     first_name_list.extend(first_far[:far_count])         # 3 Far
     
     Result: ['Jon', 'Jaohn', 'Jeohn', 'Jiohn',  # 4 Light
              'Jokn', 'Jomn', 'Johm', 'Jhon', 'Jonh', 'Jhohn', 'Jonhn', 'Johkn',  # 8 Medium
              'Johyn', 'Johny', 'Jown']  # 3 Far

  2. Build last_name_list:
     last_name_list = []
     last_name_list.extend(last_light[:light_count])      # 4 Light
     last_name_list.extend(last_medium[:medium_count])    # 8 Medium
     last_name_list.extend(last_far[:far_count])           # 3 Far
     
     Result: ['Smaith', 'Smeith', 'Smiith', 'Smoith',  # 4 Light
              'Smit', 'Smitah', 'Smiteh', 'Smitih', 'Smitoh', 'Smituh', 'Snith', 'Smits',  # 8 Medium
              'Smth', 'Samith', 'Semith']  # 3 Far
```

### Step 7: Combine into Full Names

**Function**: Inside `generate_full_name_variations()`

```python
Process:
  1. Combine first_name_list × last_name_list:
     for i in range(15):  # light_count + medium_count + far_count
         first_idx = i % len(first_name_list)
         last_idx = i % len(last_name_list)
         combined = f"{first_name_list[first_idx]} {last_name_list[last_idx]}"
         variations.append(combined)

  2. Avoid duplicates:
     - Track seen combinations
     - Try next last name if duplicate found

Output:
  variations = [
    'Jon Smaith',      # Light + Light
    'Jaohn Smeith',    # Light + Light
    'Jeohn Smiith',    # Light + Light
    'Jiohn Smoith',    # Light + Light
    'Jokn Smit',       # Medium + Medium
    'Jomn Smitah',     # Medium + Medium
    'Johm Smiteh',     # Medium + Medium
    'Jhon Smitih',     # Medium + Medium
    'Jonh Smitoh',     # Medium + Medium
    'Jhohn Smituh',    # Medium + Medium
    'Jonhn Snith',     # Medium + Medium
    'Johkn Smits',     # Medium + Medium
    'Johyn Smth',      # Far + Far
    'Johny Samith',    # Far + Far
    'Jown Semith'      # Far + Far
  ]
```

### Step 8: When rewards.py Processes These

```python
# rewards.py receives:
variations = ['Jon Smaith', 'Jaohn Smeith', ...]

# Step 1: Split into parts
first_name_variations = ['Jon', 'Jaohn', 'Jeohn', 'Jiohn', 'Jokn', 'Jomn', ...]
last_name_variations = ['Smaith', 'Smeith', 'Smiith', 'Smoith', 'Smit', 'Smitah', ...]

# Step 2: Categorize first names
first_light = ['Jon', 'Jaohn', 'Jeohn', 'Jiohn']      # 4 ✅
first_medium = ['Jokn', 'Jomn', 'Johm', 'Jhon', 'Jonh', 'Jhohn', 'Jonhn', 'Johkn']  # 8 ✅
first_far = ['Johyn', 'Johny', 'Jown']                # 3 ✅

# Step 3: Categorize last names
last_light = ['Smaith', 'Smeith', 'Smiith', 'Smoith']  # 4 ✅
last_medium = ['Smit', 'Smitah', 'Smiteh', 'Smitih', 'Smitoh', 'Smituh', 'Snith', 'Smits']  # 8 ✅
last_far = ['Smth', 'Samith', 'Semith']                # 3 ✅

# Step 4: Calculate overall part scores
first_name_score = calculate_part_score("John", first_name_variations, ...)
last_name_score = calculate_part_score("Smith", last_name_variations, ...)

# Step 5: Combine
base_score = (first_name_score × first_weight) + (last_name_score × last_weight)
```

**Result**: ✅ Distribution matches! rewards.py sees exactly what we intended.

---

## Strategy Details

The generator uses **51 strategies** to generate variations:

### Category 1: Letter Removal (Strategies 1, 8, 9, 10, 19, 20)
- Remove single letters
- Remove 2-6 letters in various combinations
- Remove middle letters (keep first and last)

### Category 2: Letter Insertion (Strategies 2, 7, 11, 14, 15, 18, 21, 22, 39)
- Add vowels at different positions
- Add all letters at all positions
- Insert vowel combinations
- Insert letter pairs
- Insert 3-letter combinations
- Insert consonant-vowel pairs

### Category 3: Letter Replacement (Strategies 3, 4, 13, 16, 23, 37, 40, 43)
- Change vowels
- Change consonants
- Replace with all possible letters
- Replace with phonetic equivalents
- Replace with similar-looking letters
- Replace multiple consecutive letters

### Category 4: Letter Swapping (Strategies 5, 6, 6b, 26, 36)
- Swap adjacent letters
- Swap non-adjacent letters
- Swap any two letters
- Swap 3 letters (rotate)
- Move letter to different position

### Category 5: Letter Duplication (Strategies 10, 24, 25, 48)
- Double letters
- Duplicate letters at different positions
- Remove duplicate letters
- Duplicate word segments

### Category 6: Pattern-Based (Strategies 27, 28, 29, 30, 31, 32, 33, 34, 35, 41, 42, 44, 45, 46, 47, 49, 50)
- Reverse substring
- Insert/remove/replace common letter pairs
- Add/remove prefixes and suffixes
- Split and insert letter
- Insert letter clusters
- Cyclic shift
- Mirror pattern
- Interleave letters
- Remove every other letter
- Replace vowels with 'y' or 'w'
- Add silent letters

### Category 7: Case Changes (Strategy 12)
- Change letter case

### Recursive Generation

The generator uses **recursive depth** (max_depth = 5) to generate variations of variations:

```
Original: "John"
  Depth 1: Generate variations
    - "Jon" (remove 'h')
    - "Jaohn" (add 'a')
    - ...
  Depth 2: Generate variations of variations
    - "Jon" → "Jno" (swap)
    - "Jaohn" → "Jaoahn" (add 'a')
    - ...
  Depth 3-5: Continue recursively
```

This ensures maximum diversity in generated variations.

---

## Examples

### Example 1: "John Smith" - 4 Light, 8 Medium, 3 Far

**Input**:
```python
full_name = "John Smith"
light_count = 4
medium_count = 8
far_count = 3
```

**Generated Variations**:
```
1.  Jon Smaith      (Light + Light)
2.  Jaohn Smeith    (Light + Light)
3.  Jeohn Smiith    (Light + Light)
4.  Jiohn Smoith    (Light + Light)
5.  Jokn Smit       (Medium + Medium)
6.  Jomn Smitah     (Medium + Medium)
7.  Johm Smiteh     (Medium + Medium)
8.  Jhon Smitih     (Medium + Medium)
9.  Jonh Smitoh     (Medium + Medium)
10. Jhohn Smituh    (Medium + Medium)
11. Jonhn Snith     (Medium + Medium)
12. Johkn Smits     (Medium + Medium)
13. Johyn Smth      (Far + Far)
14. Johny Samith    (Far + Far)
15. Jown Semith     (Far + Far)
```

**When rewards.py processes**:
- First names: 4 Light, 8 Medium, 3 Far ✅
- Last names: 4 Light, 8 Medium, 3 Far ✅

### Example 2: "Mary Johnson" - 3 Light, 5 Medium, 2 Far

**Input**:
```python
full_name = "Mary Johnson"
light_count = 3
medium_count = 5
far_count = 2
```

**Process**:
1. Generate variations for "Mary" → categorize
2. Generate variations for "Johnson" → categorize
3. Build lists: [3 Light, 5 Medium, 2 Far] for each part
4. Combine: 10 full name variations

**Result**: When rewards.py splits them, it sees:
- First names: 3 Light, 5 Medium, 2 Far ✅
- Last names: 3 Light, 5 Medium, 2 Far ✅

---

## Key Functions

### `generate_full_name_variations()`
Main entry point for generating full name variations.

**Parameters**:
- `full_name`: Full name (e.g., "John Smith")
- `light_count`: Number of Light variations needed
- `medium_count`: Number of Medium variations needed
- `far_count`: Number of Far variations needed
- `verbose`: Print progress (default: True)

**Returns**: List of full name variations

### `generate_variations_unified()`
Generates variations for a single name part using 51 strategies.

**Parameters**:
- `original`: Original name part (e.g., "John")
- `light_count`: Target Light variations
- `medium_count`: Target Medium variations
- `far_count`: Target Far variations
- `verbose`: Print progress (default: False)

**Returns**: Dictionary with 'light', 'medium', 'far' lists

### `calculate_phonetic_similarity()`
Calculates phonetic similarity score (from rewards.py).

**Parameters**:
- `original`: Original name
- `variation`: Variation to score

**Returns**: Score between 0.0 and 1.0

**Categorization**:
- Light: >= 0.8
- Medium: 0.6 - 0.79
- Far: 0.3 - 0.59
- Too Far: < 0.3

---

## Summary

The unified generator:

1. ✅ **Matches rewards.py's approach**: Categorizes each part separately
2. ✅ **Uses same scoring**: `calculate_phonetic_similarity()` function
3. ✅ **Ensures correct distribution**: Each part has the right Light/Medium/Far count
4. ✅ **Uses 51 strategies**: Comprehensive variation generation
5. ✅ **No combined scores**: Just ensures enough of each category for each part
6. ✅ **Works end-to-end**: From input to output that rewards.py can process correctly

When rewards.py receives the generated variations, it will:
- Split them into parts
- Categorize each part separately
- See the correct distribution
- Calculate scores correctly

**The generator is designed to match rewards.py's expectations perfectly!**

