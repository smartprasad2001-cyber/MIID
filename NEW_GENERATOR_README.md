# New Gemini Generator - Complete Scoring System

## Overview

This is a fresh start with a new generator script (`gemini_generator_new.py`) that uses the **exact scoring mechanism from `rewards.py`** to optimize for maximum scores.

## Files Created

1. **`gemini_generator_new.py`**: New generator script with optimized prompt
2. **`test_complete_scoring_single.py`**: Test script that shows complete scoring breakdown
3. **`PROMPT_FOR_MAXIMUM_SCORE.md`**: Documentation of the prompt structure

## Scoring Formula (from rewards.py)

```
FINAL SCORE = (Name Quality × 0.20) + (DOB Score × 0.10) + (Address Score × 0.70)
```

### Component Breakdown

1. **Name Quality (20% weight)**
   - Similarity Distribution: 60% weight (phonetic + orthographic)
   - Count: 15% weight
   - Uniqueness: 10% weight
   - Length: 15% weight
   - Rule Compliance: 20% weight

2. **DOB Score (10% weight)**
   - Must cover ALL 6 categories:
     - ±1 day
     - ±3 days
     - ±30 days
     - ±90 days
     - ±365 days
     - Year+Month only

3. **Address Score (70% weight - MOST IMPORTANT!)**
   - Format validation
   - Region match
   - API validation (OpenStreetMap geocoding)

## Usage

### Test with Single Name

```bash
export GEMINI_API_KEY=YOUR_API_KEY
python3 test_complete_scoring_single.py
```

This will:
- Generate variations using Gemini
- Score using exact `rewards.py` functions
- Show complete breakdown:
  - Name Quality Score (20%)
  - DOB Score (10%)
  - Address Score (70%)
  - Final Score

### Use in Code

```python
from gemini_generator_new import generate_with_gemini, parse_query_template

# Parse query template
query_template = """Generate exactly 8 variations..."""
requirements = parse_query_template(query_template)

# Generate variations
variations = generate_with_gemini(
    name="John Smith",
    dob="1990-06-15",
    address="New York, USA",
    query_template=query_template,
    api_key=os.getenv("GEMINI_API_KEY")
)
```

## Key Features

1. **Exact Scoring**: Uses `calculate_variation_quality`, `_grade_dob_variations`, and `_grade_address_variations` from `rewards.py`
2. **Optimized Prompt**: Shows exact scoring formula and component weights
3. **Address Focus**: Emphasizes that address is 70% of the score
4. **DOB Categories**: Explicitly lists all 6 required DOB categories
5. **Rule Examples**: Provides name-specific examples for each rule type

## Prompt Highlights

The prompt explicitly tells Gemini:

- **Final Score Formula**: Shows the exact formula used
- **Component Weights**: Address (70%), Name (20%), DOB (10%)
- **DOB Requirements**: All 6 categories must be covered
- **Address Requirements**: Format, region, and API validation details
- **Rule Examples**: Name-specific examples for each rule
- **Similarity Distribution**: Exact counts for each similarity level

## Next Steps

1. Test with single name to see scoring breakdown
2. Identify which component is failing
3. Refine prompt based on test results
4. Scale to multiple names once single name scores 0.8+

## Example Output

```
================================================================================
SCORING BREAKDOWN
================================================================================

1. NAME QUALITY SCORE (20% of total):
   Name Quality Score: 0.8500
   → Name Component (20% weight): 0.1700

2. DOB SCORE (10% of total):
   DOB Score: 1.0000
   → DOB Component (10% weight): 0.1000

3. ADDRESS SCORE (70% of total - MOST IMPORTANT!):
   Address Score: 0.9000
   → Address Component (70% weight): 0.6300

================================================================================
FINAL SCORE CALCULATION
================================================================================
Name Component (20%):  0.1700
DOB Component (10%):   0.1000
Address Component (70%): 0.6300
================================================================================
FINAL SCORE: 0.9000
================================================================================
```

## Files

- `gemini_generator_new.py`: Generator with optimized prompt
- `test_complete_scoring_single.py`: Single name test with full scoring
- `PROMPT_FOR_MAXIMUM_SCORE.md`: Prompt documentation

