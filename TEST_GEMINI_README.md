# End-to-End Production Test with Gemini

This script simulates the complete validator-to-miner flow using Gemini-2.5-pro.

## Setup

1. **Export Gemini API Key:**
   ```bash
   export GEMINI_API_KEY=your_api_key_here
   ```

2. **Install dependencies:**
   ```bash
   pip install google-generativeai
   ```

## Usage

```bash
python3 test_gemini_production.py
```

## What It Does

1. **Mocks Validator Query Generation:**
   - Generates random query parameters (variation_count, phonetic_similarity, etc.)
   - Creates test identities with names, DOB, and addresses
   - Builds query template matching real validator format

2. **Sends to Gemini:**
   - Uses `gemini-2.5-pro` model
   - Sends precise prompts for name, DOB, and address variations
   - Parses JSON response

3. **Scores with rewards.py:**
   - Sends variations to `get_name_variation_rewards()`
   - Gets detailed metrics

4. **Displays Results:**
   - Shows all scoring metrics in the format:
     - Final score
     - Names
     - Basic Quality Score
     - Similarity Score
     - Phonetic Similarity
     - Orthographic Similarity
     - Count Score
     - Uniqueness Score
     - Length Score
     - Rule Compliance Score
     - Address Score
     - DOB Score
     - All penalties

## Output Format

The script displays results in the exact format shown:

```
Final score
0.956

Names
0.779

Basic Quality Score
0.775

Similarity Score
0.644

Phonetic Similarity
0.450

Orthographic Similarity
0.765

Count Score
0.966

Uniqueness Score
0.999

Length Score
0.964

Rule Compliance Score
0.673

Address Score
1.000

DOB Score
1.000

Completeness Multiplier
1.000

Extra names penalty
0.000

Missing names penalty
0.000

Post Penalty
0.000

Address Penalty
0.000

Collusion Penalty
0.000

Duplication Penalty
0.000

Signature Copy Penalty
0.000

Special Chars Penalty
0.000
```

## Test Identities

Default test identities:
- John Smith (DOB: 1985-03-15, Address: New York, United States)
- Maria Garcia (DOB: 1990-07-22, Address: Madrid, Spain)

You can modify these in the `create_test_identities()` method.





