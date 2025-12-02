# Optimized Prompt for Maximum Scoring

This document contains the prompt used in `gemini_generator_new.py` that is optimized for maximum scoring based on the exact scoring mechanism in `rewards.py`.

## Scoring Formula

```
FINAL SCORE = (Name Quality × 0.20) + (DOB Score × 0.10) + (Address Score × 0.70)
```

## Key Components

### 1. Name Quality (20% of total score)
- **Similarity Distribution**: 60% weight within name quality
  - Phonetic: Light (0.80-1.00), Medium (0.60-0.79), Far (0.30-0.59)
  - Orthographic: Light (0.70-1.00), Medium (0.50-0.69), Far (0.20-0.49)
- **Count**: 15% weight - Must have EXACTLY N variations
- **Uniqueness**: 10% weight - All variations must be unique
- **Length**: 15% weight - Variations must be 60-140% of original length
- **Rule Compliance**: 20% weight - EXACTLY N variations must follow rules

### 2. DOB Score (10% of total score)
- **MUST include at least ONE variation in EACH of these 6 categories:**
  - ±1 day from seed DOB
  - ±3 days from seed DOB
  - ±30 days from seed DOB
  - ±90 days from seed DOB
  - ±365 days from seed DOB
  - Year+Month only (format: YYYY-MM, no day)
- **Missing any category = 0% for DOB component (loses 10% of total score!)**

### 3. Address Score (70% of total score - MOST IMPORTANT!)
- **Format Validation**: Address must be 30-300 chars, 20+ letters, 2+ commas, 1+ digit
- **Region Match**: Country/city must match seed address
- **API Validation**: Address must be geocodable on OpenStreetMap
- **ANY failure = 0% for address component (loses 70% of total score!)**

## Prompt Structure

The prompt is built dynamically based on:
- Original identity (name, DOB, address)
- Query template requirements (variation count, similarity distributions, rules)
- Specific examples for each rule type
- Detailed instructions for each scoring component

## Usage

```python
from gemini_generator_new import build_optimized_prompt, parse_query_template

# Parse query template
requirements = parse_query_template(query_template)

# Build prompt
prompt = build_optimized_prompt(name, dob, address, requirements)

# Use with Gemini API
variations = generate_with_gemini(name, dob, address, query_template, api_key)
```

## Testing

Run the test script to see the complete scoring breakdown:

```bash
export GEMINI_API_KEY=YOUR_API_KEY
python3 test_complete_scoring_single.py
```

This will show:
- Name Quality Score (20% weight)
- DOB Score (10% weight)
- Address Score (70% weight)
- Final Score calculation

## Key Features

1. **Explicit Scoring Formula**: Shows the exact formula used by rewards.py
2. **Component Weights**: Clearly shows that address is 70% of the score
3. **DOB Categories**: Explicitly lists all 6 required DOB categories
4. **Address Requirements**: Detailed format, region, and API validation requirements
5. **Rule Examples**: Provides name-specific examples for each rule type
6. **Similarity Distribution**: Shows exact counts for each similarity level

