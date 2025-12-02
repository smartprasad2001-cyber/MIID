# Universal Letter Removal Strategy for All Names

## Goal
Create a universal strategy that works for **any name** to generate:
- **Light** (0.8-1.0): Keep original
- **Medium** (0.6-0.8): Remove letters strategically
- **Far** (0.3-0.6): Remove more letters strategically

---

## Universal Strategy

### LIGHT (0.8-1.0) - Keep Original
```
Strategy: Keep the name exactly as it is
Example: "John Smith" → "John Smith" (1.0000)
```

### MEDIUM (0.6-0.8) - Try in Order

**Priority 1: Remove 1 letter from MIDDLE of last name**
```
Algorithm:
  1. Find middle position: mid_pos = len(last_name) // 2
  2. Remove letter at mid_pos: last_name[:mid_pos] + last_name[mid_pos+1:]
  3. Check if score is 0.6-0.8

Examples:
  "John Smith" → "John Smth" (0.7600) ✓
  "Sarah Brown" → "Sarah Brwn" (0.7666) ✓
```

**Priority 2: Change a vowel in last name**
```
Algorithm:
  1. Find first vowel in last name
  2. Replace with different vowel (a→e, e→i, i→o, o→u, u→a)
  3. Check if score is 0.6-0.8

Examples:
  "Michael Davis" → "Michael Devis" (0.6797) ✓
```

**Priority 3: Remove 1 letter from END (if name >= 5 chars)**
```
Algorithm:
  1. If len(last_name) >= 5: remove last letter
  2. Check if score is 0.6-0.8

Examples:
  "Robert Williams" → "Robert William" (0.9123) - Actually Light!
  "Michael Davis" → "Michael Davi" (0.8382) - Actually Light!
```

**⚠️ Note**: Removing from end is **unreliable** - often gives Light or Far instead of Medium!

---

### FAR (0.3-0.6) - Try in Order

**Priority 1: Remove 2 letters from MIDDLE of last name**
```
Algorithm:
  1. Find middle position: mid_pos = len(last_name) // 2
  2. Remove 2 letters around middle: last_name[:mid_pos-1] + last_name[mid_pos+1:]
  3. Check if score is 0.3-0.6

Examples:
  "David Miller" → "David Mier" (0.4231) ✓
  "Jennifer Wilson" → "Jennifer Wion" (0.3133) ✓
```

**Priority 2: Remove 2 letters from END of last name**
```
Algorithm:
  1. Remove last 2 letters: last_name[:-2]
  2. Check if score is 0.3-0.6

Examples:
  "Mary Johnson" → "Mary Johns" (0.3170) ✓
  "Sarah Brown" → "Sarah Bro" (0.5462) ✓
  "Michael Davis" → "Michael Dav" (0.5461) ✓
```

**Priority 3: Remove 1 letter from MIDDLE (fallback)**
```
Algorithm:
  1. Remove 1 letter from middle (same as Medium Priority 1)
  2. Some names give Far instead of Medium

Examples:
  "Michael Davis" → "Michael Dais" (0.3631) ✓
```

---

## Implementation Code

```python
def generate_medium_variation(full_name):
    """Generate Medium similarity variation (0.6-0.8)"""
    parts = full_name.split()
    if len(parts) < 2:
        return None
    
    first = parts[0]
    last = parts[1]
    
    # Strategy 1: Remove 1 letter from middle
    if len(last) >= 4:
        mid_pos = len(last) // 2
        var = f"{first} {last[:mid_pos] + last[mid_pos+1:]}"
        score = calculate_phonetic_similarity(full_name, var)
        if 0.6 <= score < 0.8:
            return var
    
    # Strategy 2: Change vowel
    vowels = ['a', 'e', 'i', 'o', 'u']
    for i, char in enumerate(last):
        if char.lower() in vowels:
            for v in vowels:
                if v != char.lower():
                    var = f"{first} {last[:i] + v + last[i+1:]}"
                    score = calculate_phonetic_similarity(full_name, var)
                    if 0.6 <= score < 0.8:
                        return var
    
    # Fallback: Remove 1 from end (unreliable but better than nothing)
    if len(last) > 1:
        return f"{first} {last[:-1]}"
    
    return None

def generate_far_variation(full_name):
    """Generate Far similarity variation (0.3-0.6)"""
    parts = full_name.split()
    if len(parts) < 2:
        return None
    
    first = parts[0]
    last = parts[1]
    
    # Strategy 1: Remove 2 letters from middle
    if len(last) >= 5:
        mid_pos = len(last) // 2
        var = f"{first} {last[:mid_pos-1] + last[mid_pos+1:]}"
        score = calculate_phonetic_similarity(full_name, var)
        if 0.3 <= score < 0.6:
            return var
    
    # Strategy 2: Remove 2 letters from end
    if len(last) >= 4:
        var = f"{first} {last[:-2]}"
        score = calculate_phonetic_similarity(full_name, var)
        if 0.3 <= score < 0.6:
            return var
    
    # Fallback: Remove 1 from middle
    if len(last) >= 4:
        mid_pos = len(last) // 2
        var = f"{first} {last[:mid_pos] + last[mid_pos+1:]}"
        score = calculate_phonetic_similarity(full_name, var)
        if 0.3 <= score < 0.6:
            return var
    
    # Last resort: Remove 2 from end anyway
    if len(last) >= 3:
        return f"{first} {last[:-2]}"
    
    return None
```

---

## Success Rates (Tested on 7 Names)

- **Medium Variations**: 2/7 (28.6%) - **Challenging!**
- **Far Variations**: 5/7 (71.4%) - **Works well!**

---

## Key Insights

1. **Removing from MIDDLE is more reliable** than removing from END
2. **Medium is harder to achieve** than Far (phonetic algorithms are sensitive)
3. **Vowel changes can work** for Medium but are name-dependent
4. **Removing 2 letters from middle** is the most reliable for Far
5. **Removing from end** often gives unexpected results (Light or Too Low)

---

## Recommendations

### For Maximum Reliability:

1. **Light**: Always keep original (100% success)

2. **Medium**: 
   - Primary: Remove 1 letter from middle
   - Secondary: Change vowel
   - Fallback: Remove 1 from end (accept that some will be Light/Far)

3. **Far**:
   - Primary: Remove 2 letters from middle
   - Secondary: Remove 2 letters from end
   - Fallback: Remove 1 from middle (some names give Far)

### For Production Use:

Since Medium is challenging, consider:
- Using Gemini for Medium variations (more reliable)
- Using letter removal for Far variations (works well)
- Accepting that some Medium attempts will be Light/Far (validator will still score them, just not optimally)

---

## Example Usage

```python
name = "John Smith"

# Light (keep original)
light_var = name  # "John Smith"

# Medium (remove 1 from middle)
medium_var = generate_medium_variation(name)  # "John Smth"

# Far (remove 2 from middle)
far_var = generate_far_variation(name)  # "John Smi" or "John Sth"
```

---

## Limitations

1. **Not 100% reliable**: Phonetic similarity depends on the specific name
2. **Medium is hardest**: Only ~30% success rate
3. **Name-dependent**: Some names respond differently to the same strategy
4. **First name not varied**: Strategy only works on last name (first name needs separate handling)

---

## Next Steps

1. Test with more diverse names (international, longer names)
2. Combine with first name variation strategies
3. Consider hybrid approach: letter removal for Far, Gemini for Medium
4. Test with actual validator scoring to verify distribution matching

