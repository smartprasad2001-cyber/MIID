# How Medium Similarity is Calculated

## Question: Do I "Shut Down" Algorithms?

**Answer: NO!** I don't shut down or disable algorithms. I simply **test** which algorithms naturally match or don't match for each variation.

## How It Actually Works

### Step 1: Generate Candidate Variations

I generate variations by modifying the original word:
- Add letters: "John" → "Jaohn"
- Remove letters: "John" → "Jon"
- Change letters: "John" → "Jhon"
- Swap letters: "John" → "Jhon"

### Step 2: Test Each Variation Against ALL Algorithms

For each candidate variation, I test it against **all three algorithms**:

```python
# Test "Jhon" against "John"
soundex_match = soundex("Jhon") == soundex("John")    # True (J500 == J500)
metaphone_match = metaphone("Jhon") == metaphone("John")  # False (JHN != JN)
nysiis_match = nysiis("Jhon") == nysiis("John")      # True (JAN == JAN)
```

### Step 3: Calculate Score Based on Matches

The score is calculated as:
```
score = (weight1 × match1) + (weight2 × match2) + (weight3 × match3)
```

Where:
- `match` = 1.0 if algorithm matches, 0.0 if it doesn't
- `weight` = the weight for that algorithm (from the seed)

### Step 4: Categorize by Score

- **Light (0.8-1.0)**: All 3 algorithms match → score = 1.0
- **Medium (0.6-0.8)**: 2 algorithms match → score = sum of 2 weights
- **Far (0.3-0.6)**: 0-1 algorithms match → score = sum of 0-1 weights

## Example: "John" → "Jhon"

### Original: "John"
- Soundex: J500
- Metaphone: JN
- NYSIIS: JAN

### Variation: "Jhon"
- Soundex: J500 ✓ (matches!)
- Metaphone: JHN ✗ (doesn't match - naturally different!)
- NYSIIS: JAN ✓ (matches!)

### Why Metaphone Doesn't Match

The variation "Jhon" naturally breaks the Metaphone code:
- "John" → Metaphone: JN
- "Jhon" → Metaphone: JHN

This happens because:
- The letter swap (o↔h) changes the phonetic structure
- Metaphone is sensitive to letter order and position
- I don't control this - it's how the algorithm works!

### Score Calculation

If weights are:
- Metaphone: 30.8% (0.3078)
- Soundex: 3.0% (0.0299)
- NYSIIS: 66.2% (0.6624)

Score = 0.0 × 0.3078 + 1.0 × 0.0299 + 1.0 × 0.6624
     = 0.0000 + 0.0299 + 0.6624
     = **0.6922** (Medium!)

## Key Points

### 1. I Don't Control Which Algorithms Match

- I generate variations by modifying letters
- I test which algorithms match
- Some match, some don't - **naturally**
- I don't "shut down" or disable algorithms

### 2. Algorithms Match or Don't Match Based on Their Rules

- **Soundex**: Matches if first letter + similar consonants match
- **Metaphone**: Matches if phonetic structure is similar
- **NYSIIS**: Matches if name structure is similar

Each algorithm has its own rules, and variations naturally break some rules while keeping others.

### 3. Medium Score = 2 Algorithms Match

For Medium similarity:
- 2 algorithms match → contribute their weights
- 1 algorithm doesn't match → contributes 0
- Score = weight1 + weight2 (typically 0.6-0.8)

### 4. I Just Test and Filter

My process:
1. Generate many candidate variations
2. Test each against all 3 algorithms
3. Calculate score for each
4. Keep variations with scores in Medium range (0.6-0.8)
5. Sort by closeness to target (e.g., 0.7)

## Why Some Algorithms Don't Match

### Natural Reasons:

1. **Letter changes break phonetic codes**
   - "John" → "Jhon": Swapping letters changes Metaphone code

2. **Removing letters changes structure**
   - "John" → "Jon": Removing 'h' might keep Soundex but break NYSIIS

3. **Adding letters changes codes**
   - "John" → "Jaohn": Adding 'a' might break all codes

4. **Each algorithm is sensitive to different things**
   - Soundex: First letter + consonants
   - Metaphone: Phonetic structure
   - NYSIIS: Name structure

## Summary

**I don't shut down algorithms!**

What I do:
1. ✅ Generate candidate variations
2. ✅ Test each against ALL 3 algorithms
3. ✅ Calculate score based on which ones match
4. ✅ Keep variations with Medium scores (0.6-0.8)

The algorithms naturally match or don't match based on:
- How the variation modifies the original
- Each algorithm's specific rules
- The phonetic/structure similarity

**Medium score = 2 algorithms match, 1 doesn't (naturally!)**

