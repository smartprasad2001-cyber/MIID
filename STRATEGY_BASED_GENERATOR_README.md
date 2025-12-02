# Strategy-Based Generator

## Overview

This generator ensures **all 25 strategies are used** before exhausting recursion limits, providing maximum diversity in generated variations.

## Key Features

1. **Systematic Strategy Cycling**: Cycles through all 25 strategies in order
2. **Per-Strategy Limits**: Each strategy has its own recursion limits
3. **Maximum Diversity**: Ensures variations come from different strategies, not just the first few
4. **Adaptive Limits**: Adjusts limits based on name length/complexity

## How It Works

### Strategy Cycle

1. **Start with Strategy 1**: Remove single letters
2. **Apply with recursion limits**: Each strategy gets a limited recursion depth
3. **Move to Strategy 2**: Add vowels at different positions
4. **Continue through all 25 strategies**: Even if early strategies find variations
5. **Cycle back**: If needed, go through all strategies again

### Example Flow

```
Round 1, Strategy 1/25: strategy_remove_single_letter
  Found 0/6 candidates, checked 115/750000
Round 2, Strategy 2/25: strategy_add_vowels
  Found 0/6 candidates, checked 1922/750000
Round 3, Strategy 3/25: strategy_change_vowels
  Found 0/6 candidates, checked 2167/750000
...
Round 25, Strategy 25/25: strategy_cyclic_shift
  Found 0/6 candidates, checked 36097/750000
Round 26, Strategy 1/25: strategy_remove_single_letter (cycle back)
  ...
```

## All 25 Strategies

1. Remove single letters
2. Add vowels at different positions
3. Change vowels
4. Change consonants
5. Swap adjacent letters
6. Swap non-adjacent letters
7. Add letters at all positions
8. Remove multiple letters (2 letters)
9. Remove 3 letters
10. Double letters
11. Insert vowel combinations
12. Insert letter pairs
13. Replace with all possible letters
14. Replace with phonetic equivalents
15. Duplicate letters at positions
16. Remove duplicate letters
17. Swap 3 letters (rotate)
18. Reverse substring
19. Insert common letter pairs
20. Add prefix
21. Add suffix
22. Split and insert letter
23. Move letter to different position
24. Replace with double letter
25. Cyclic shift (rotate letters)

## Usage

```python
from strategy_based_generator import generate_full_name_variations_strategy_based

variations = generate_full_name_variations_strategy_based(
    "Sebastian Martinez",
    light_count=2,
    medium_count=6,
    far_count=2,
    verbose=True
)
```

## Advantages Over Unified Generator

1. **Maximum Diversity**: Variations come from all strategies, not just the first few
2. **Predictable**: Always cycles through all strategies in order
3. **Fair Distribution**: No strategy is skipped even if early ones find variations
4. **Better Coverage**: Ensures all transformation types are explored

## Adaptive Limits

Based on name length:
- **Short names (< 8 chars)**: 500k candidates, depth 3
- **Medium names (8-11 chars)**: 750k candidates, depth 3
- **Long names (≥ 12 chars)**: 1M candidates, depth 4

## Files

- `strategy_based_generator.py`: Main generator script
- `test_strategy_based.py`: Test script
- `STRATEGY_BASED_GENERATOR_README.md`: This file

## Notes

- This generator prioritizes **diversity** over **speed**
- It may be slower than `unified_generator.py` but provides more varied results
- All strategies are guaranteed to be used at least once
- If limits are exhausted for one strategy, it moves to the next (doesn't stop)

