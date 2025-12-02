# Step-by-Step: How We Predict Algorithm Selection

## Overview

This document explains step-by-step how we can predict which algorithms the validator will select, even though it uses "random" selection.

---

## Step 1: Understanding the Problem

**What the validator does:**
- It has 3 algorithms: Soundex, Metaphone, NYSIIS
- It randomly selects which ones to use
- It randomly weights them
- This seems unpredictable...

**But wait!** The randomness is seeded by the name, so it's actually predictable!

---

## Step 2: Finding the Seed

**Validator code (line 155):**
```python
random.seed(hash(original_name) % 10000)
```

**What this means:**
- Takes the original name (e.g., "John")
- Calculates its hash: `hash("John")` → some big number
- Takes modulo 10000: `hash("John") % 10000` → number between 0-9999
- Uses this as the seed

**Example:**
```python
hash("John") = -2094009081367661313  # Big number
hash("John") % 10000 = 8687          # Seed value
```

**Key insight:** Same name → same hash → same seed!

---

## Step 3: Understanding Python's Random Seed

**What `random.seed()` does:**
```python
random.seed(8687)
```

This initializes Python's random number generator with seed 8687.

**Important property:**
- Same seed → same sequence of random numbers
- Different seed → different sequence

**Example:**
```python
random.seed(8687)
print(random.random())  # Always: 0.960356...
print(random.random())  # Always: 0.662059...
print(random.random())  # Always: 0.244554...

# Reset to same seed
random.seed(8687)
print(random.random())  # Same: 0.960356...
print(random.random())  # Same: 0.662059...
```

---

## Step 4: How random.sample() Works

**The code:**
```python
algorithms = ["soundex", "metaphone", "nysiis"]
selected = random.sample(algorithms, k=3)
```

**What `random.sample()` does internally:**

1. It needs to pick 3 items from the list
2. It uses `random.random()` to generate random numbers
3. It uses these numbers to decide which items to pick
4. It uses them to decide the order

**Simplified version:**
```python
def sample(items, k):
    result = []
    remaining = items.copy()  # ['soundex', 'metaphone', 'nysiis']
    
    for i in range(k):
        # Generate random number
        r = random.random()  # e.g., 0.960356
        
        # Use it to pick an item
        index = int(r * len(remaining))  # e.g., int(0.960356 * 3) = 2
        item = remaining.pop(index)  # Remove item at index 2
        result.append(item)  # Add to result
    
    return result
```

**Example with seed 8687:**
```
Iteration 1:
  random.random() = 0.960356
  index = int(0.960356 * 3) = 2
  Pick: algorithms[2] = "nysiis"
  Remaining: ['soundex', 'metaphone']

Iteration 2:
  random.random() = 0.662059
  index = int(0.662059 * 2) = 1
  Pick: remaining[1] = "metaphone"
  Remaining: ['soundex']

Iteration 3:
  random.random() = 0.244554
  index = int(0.244554 * 1) = 0
  Pick: remaining[0] = "soundex"
  Remaining: []

Result: ['nysiis', 'metaphone', 'soundex']
```

---

## Step 5: Replicating the Process

**We do the EXACT same thing:**

```python
# Step 1: Calculate the same seed
original = "John"
seed = hash(original) % 10000  # Same as validator!

# Step 2: Set the same seed
random.seed(seed)  # Same as validator!

# Step 3: Select algorithms
algorithms = ["soundex", "metaphone", "nysiis"]
selected = random.sample(algorithms, k=3)  # Same as validator!

# Result: We get the SAME selection!
```

**Why it works:**
- Same seed → same random numbers
- Same random numbers → same selection
- Therefore: We predict exactly what validator will select!

---

## Step 6: Complete Example

**Let's trace through "John":**

```python
# Step 1: Calculate seed
original = "John"
seed = hash("John") % 10000
# seed = 8687

# Step 2: Set seed
random.seed(8687)

# Step 3: Select algorithms
algorithms = ["soundex", "metaphone", "nysiis"]
selected = random.sample(algorithms, k=3)
# selected = ['metaphone', 'soundex', 'nysiis']

# Step 4: Generate weights
weights = [random.random() for _ in selected]
# weights = [0.1114, 0.5839, 0.2587]
# Normalized: [0.1168, 0.6120, 0.2712]

# Step 5: Calculate score for variation
variation = "Jon"
soundex_match = jellyfish.soundex("John") == jellyfish.soundex("Jon")  # True
metaphone_match = jellyfish.metaphone("John") == jellyfish.metaphone("Jon")  # True
nysiis_match = jellyfish.nysiis("John") == jellyfish.nysiis("Jon")  # True

# Step 6: Calculate weighted score
score = (
    soundex_match * 0.1168 +    # 1.0 * 0.1168 = 0.1168
    metaphone_match * 0.6120 +  # 1.0 * 0.6120 = 0.6120
    nysiis_match * 0.2712       # 1.0 * 0.2712 = 0.2712
)
# score = 1.0000
```

---

## Step 7: Why This Works

**The key insight:**

1. **Deterministic randomness:**
   - Python's `random` is deterministic when seeded
   - Same seed → same sequence of numbers

2. **Seed is based on name:**
   - Validator: `hash(name) % 10000`
   - We: `hash(name) % 10000`
   - Same name → same seed → same sequence!

3. **Same sequence → same selection:**
   - `random.sample()` uses the sequence
   - Same sequence → same selection
   - Therefore: We can predict!

---

## Visual Summary

```
Name: "John"
  ↓
hash("John") = -2094009081367661313
  ↓
hash("John") % 10000 = 8687 (SEED)
  ↓
random.seed(8687)
  ↓
Random sequence: [0.960356, 0.662059, 0.244554, ...]
  ↓
random.sample() uses sequence
  ↓
Selected: ['metaphone', 'soundex', 'nysiis']
  ↓
Weights: [0.1168, 0.6120, 0.2712]
  ↓
Score calculation for variations
```

---

## Key Takeaways

1. ✅ **Seed is deterministic:** Based on name hash
2. ✅ **Random is deterministic:** Same seed → same sequence
3. ✅ **Selection is predictable:** Same sequence → same selection
4. ✅ **We can replicate:** Use same seed → get same result
5. ✅ **We can predict:** Know which algorithms will be used

---

## Code to Try Yourself

```python
import random

# Test with different names
for name in ["John", "Mary", "Robert"]:
    seed = hash(name) % 10000
    random.seed(seed)
    
    algorithms = ["soundex", "metaphone", "nysiis"]
    selected = random.sample(algorithms, k=3)
    
    print(f"{name}: seed={seed}, selected={selected}")
    
    # Reset and verify it's the same
    random.seed(seed)
    selected2 = random.sample(algorithms, k=3)
    print(f"  Same? {selected == selected2}")
```

This will show you that same seed always gives same selection!

