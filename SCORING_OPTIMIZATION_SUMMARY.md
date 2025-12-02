# Scoring Optimization Summary

## Objective
Achieve 0.8 average score using exact synapse from logs with Gemini 2.5 Flash-Lite.

## Current Status
- **Average Score**: 0.2775 (Target: 0.8)
- **Best Score**: 0.4977 (cesar taylor)
- **Scores ≥ 0.8**: 0/15
- **Scores ≥ 0.6**: 0/15

## Issues Identified

### 1. Rule Compliance (20% weight) - CRITICAL
- **Current**: 0-3 variations follow rules (need 5 out of 8)
- **Required**: 5 out of 8 variations (60%) must follow:
  - `shorten_name_to_initials`: Convert name to initials (e.g., "John Smith" → "J.S.")
  - `swap_random_letter`: Swap adjacent letters (e.g., "John" → "Jhon")
- **Impact**: Missing rules = 0% for this component (loses 20% weight)

### 2. Similarity Distribution (60% weight) - CRITICAL
- **Current**: Many names have 0.0000 similarity score
- **Required**:
  - Phonetic: 20% Light (0.80-1.00), 60% Medium (0.60-0.79), 20% Far (0.30-0.59)
  - Orthographic: 30% Light (0.70-1.00), 40% Medium (0.50-0.69), 30% Far (0.20-0.49)
- **Impact**: This is 60% of the total score - most important component

### 3. Uniqueness (10% weight)
- **Current**: Some names have identical variations (e.g., "alfred boulay" all identical)
- **Required**: All variations must be unique (combined similarity < 0.99)
- **Impact**: Identical variations = 0% uniqueness (loses 10% weight)

### 4. Count (15% weight)
- **Current**: Generally correct (8 variations)
- **Status**: ✅ Working

### 5. Length (15% weight)
- **Current**: Generally within range
- **Status**: ✅ Working

## Changes Made

### 1. Rule Parsing Fixes
- Added parsing for "Convert {name} to initials" → `shorten_name_to_initials`
- Added parsing for "Swap random adjacent letters" → `swap_random_letter`
- Fixed rule_count calculation: `math.ceil()` instead of `int()` (5 out of 8 instead of 4)

### 2. Prompt Enhancements
- Added explicit execution plans showing which variations should follow which rules
- Added detailed rule definitions with name-specific examples
- Added unified execution plan combining rules and similarity distributions
- Added explicit similarity distribution plans with variation indices

### 3. Prompt Structure
- Clear separation between rule-compliant (variations 1-5) and non-rule-compliant (variations 6-8)
- Explicit instructions for each similarity category with Levenshtein distance calculations
- Stronger warnings about uniqueness and rule compliance

## Next Steps for Optimization

### 1. Rule Compliance
- **Issue**: Gemini is not applying rules to 5 variations
- **Solution**: 
  - Make rule instructions even more explicit
  - Provide concrete examples for each name
  - Add validation checks in the prompt

### 2. Similarity Distribution
- **Issue**: Variations don't match required similarity ranges
- **Solution**:
  - Provide more specific examples of variations that fall into each category
  - Add Levenshtein distance examples for each name
  - Test variations mentally before generating

### 3. Uniqueness
- **Issue**: Some names have identical variations
- **Solution**:
  - Add stronger warnings about uniqueness
  - Provide examples of diverse variations
  - Emphasize varying both first and last name parts

### 4. Testing Strategy
- Run tests on individual names to identify specific issues
- Analyze which names score highest and replicate their patterns
- Iteratively refine the prompt based on test results

## Test Command
```bash
export GEMINI_API_KEY=YOUR_API_KEY
python3 test_exact_synapse_scoring.py
```

## Files Modified
- `MIID/validator/gemini_generator.py`: Enhanced prompt with explicit instructions
- `test_exact_synapse_scoring.py`: Test script for exact synapse scoring

## Key Metrics
- **Rule Compliance**: 0-3/8 (need 5/8) - 20% weight
- **Similarity**: 0.0000-0.3423 (need 0.8+) - 60% weight
- **Uniqueness**: 0.1250-0.7143 (need 1.0) - 10% weight
- **Count**: ✅ 8/8 - 15% weight
- **Length**: ✅ Generally good - 15% weight

## Conclusion
The prompt has been significantly enhanced, but Gemini still struggles with:
1. Applying rules to 5 out of 8 variations
2. Matching similarity distributions exactly
3. Ensuring uniqueness for all variations

Further prompt engineering and testing are needed to reach the 0.8 target.

