#!/usr/bin/env python3
"""
Show where hash is used for random seeding and which algorithms are used in rewards.py
"""

print("="*80)
print("HASH AND ALGORITHMS IN rewards.py")
print("="*80)
print()

print("📍 Location: MIID/validator/reward.py")
print()

print("="*80)
print("1. HASH USED FOR RANDOM SEEDING")
print("="*80)
print()

print("Line 155: random.seed(hash(original_name) % 10000)")
print()
print("Code:")
print("  # Deterministically seed the random selection based on the original name")
print("  random.seed(hash(original_name) % 10000)")
print("  selected_algorithms = random.sample(list(algorithms.keys()), k=min(3, len(algorithms)))")
print("  weights = [random.random() for _ in selected_algorithms]")
print()

print("What it does:")
print("  - Uses hash(original_name) % 10000 as the random seed")
print("  - This ensures the same original_name always gets the same algorithm selection")
print("  - But different names get different algorithm selections")
print("  - The random state is GLOBAL, so calling it for different names changes the state")
print()

print("="*80)
print("2. ALGORITHMS DEFINED")
print("="*80)
print()

print("Lines 147-152: algorithms dictionary")
print()
print("Code:")
print("  algorithms = {")
print("      \"soundex\": lambda x, y: jellyfish.soundex(x) == jellyfish.soundex(y),")
print("      \"metaphone\": lambda x, y: jellyfish.metaphone(x) == jellyfish.metaphone(y),")
print("      \"nysiis\": lambda x, y: jellyfish.nysiis(x) == jellyfish.nysiis(y),")
print("  }")
print()

print("Available algorithms:")
print("  1. soundex   - Soundex phonetic algorithm")
print("  2. metaphone - Metaphone phonetic algorithm")
print("  3. nysiis    - NYSIIS phonetic algorithm")
print()

print("Line 156: Algorithm selection")
print("  selected_algorithms = random.sample(list(algorithms.keys()), k=min(3, len(algorithms)))")
print("  - Randomly selects 3 algorithms from the 3 available (so all 3 are always selected)")
print("  - But the WEIGHTS are randomized")
print()

print("="*80)
print("3. HOW IT WORKS")
print("="*80)
print()

print("Step 1: Seed random with hash(original_name) % 10000")
print("Step 2: Select 3 algorithms (all 3 are always selected)")
print("Step 3: Generate random weights for each algorithm")
print("Step 4: Normalize weights to sum to 1.0")
print("Step 5: Calculate score = sum(algorithm_match * weight)")
print()

print("Example:")
print("  For 'John':")
print("    hash('John') % 10000 = some number")
print("    random.seed(that_number)")
print("    selected_algorithms = ['soundex', 'metaphone', 'nysiis']")
print("    weights = [0.3, 0.4, 0.3] (random, but deterministic for 'John')")
print()
print("  For 'Smith':")
print("    hash('Smith') % 10000 = different number")
print("    random.seed(that_number)  ← THIS CHANGES GLOBAL RANDOM STATE!")
print("    selected_algorithms = ['soundex', 'metaphone', 'nysiis']")
print("    weights = [0.5, 0.2, 0.3] (different weights)")
print()

print("="*80)
print("4. THE PROBLEM")
print("="*80)
print()

print("Issue: random.seed() affects GLOBAL random state")
print()
print("When generating variations:")
print("  1. Generate for 'John' → random.seed(hash('John')) → calculates scores")
print("  2. Generate for 'Smith' → random.seed(hash('Smith')) → CHANGES global state")
print("  3. Verify 'John' variations → random.seed(hash('John')) → but state was changed!")
print()
print("Result: Scores can be inconsistent between generation and verification")
print()

print("="*80)
print("5. OTHER HASH USAGE")
print("="*80)
print()

print("Line 1210: random.seed(hash(name) % 10000)")
print("  - Used in get_name_part_weights() function")
print("  - Also uses hash for random seeding")
print()

print("="*80)





