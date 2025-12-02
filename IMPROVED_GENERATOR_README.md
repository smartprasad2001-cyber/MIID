# Improved Address Generator

This is an improved address generation pipeline that uses Gemini to generate candidate addresses and validates them using the exact same functions from `MIID/validator/reward.py`.

## Features

- **Uses your exact validator logic**: Imports functions directly from `reward.py` (looks_like_address, validate_address_region, check_with_nominatim)
- **Robust validation**: Two-phase approach - Gemini proposes, validator verifies
- **Incremental retry**: Increases batch size on each attempt (120 → 240 → 360 → ...)
- **Rate limiting**: 2-second delay between Nominatim API calls
- **Detailed logging**: All operations logged to console and file
- **Perfect address filtering**: Only accepts addresses with score ≥ 0.99

## Setup

1. **Install dependencies**:
   ```bash
   pip install google-generativeai requests
   ```

2. **Create the master prompt** (if not already created):
   ```bash
   python3 update_prompt.py
   ```

   Optionally add country-specific guidance:
   ```bash
   python3 update_prompt.py --extra "For the United Kingdom, prefer Oxford Walton Street, Manchester Northern Quarter backstreets, etc."
   ```

3. **Set your Gemini API key**:
   ```bash
   export GEMINI_API_KEY="your_api_key_here"
   ```

## Usage

### Basic usage:
```bash
python3 improved_generate_addresses.py --country "United Kingdom" --target 15 --output uk_perfect.json
```

### Options:
- `--country`: Required. Country name (e.g., "United Kingdom", "United States")
- `--target`: Number of perfect addresses to generate (default: 15)
- `--output`: Output JSON file path (optional, prints to stdout if not provided)
- `--validator-uid`: Validator UID for API calls (default: 101)
- `--miner-uid`: Miner UID for API calls (default: 501)

### Example:
```bash
export GEMINI_API_KEY="AIzaSyAy6_C3olzlDKGS7Y2VDtgzgXm3zYzRxaU"
python3 improved_generate_addresses.py --country "United Kingdom" --target 15 --output uk_perfect.json
```

## How It Works

1. **Loads master prompt** from `master_prompt.txt` (created by `update_prompt.py`)
2. **Generates candidates** using Gemini 2.5 Pro (low temperature: 0.25 for realistic patterns)
3. **Validates each candidate** using:
   - `looks_like_address()` - Heuristic check
   - `validate_address_region()` - Region match check
   - `check_with_nominatim()` - API validation with area check
4. **Collects perfect addresses** (score ≥ 0.99) until target is reached
5. **Incremental retry**: If not enough perfect addresses found, increases batch size and retries (up to 6 attempts)

## Output Format

The script outputs a JSON file with:
```json
{
  "country": "United Kingdom",
  "perfect_addresses": [
    "1 Walton Street, Oxford, OX1 2HG, United Kingdom",
    ...
  ],
  "count": 15,
  "stats": {
    "attempts": 2,
    "candidates_tested": 45,
    "perfect_found": 15
  },
  "timestamp": "2025-11-25T01:00:00Z"
}
```

## Key Differences from Previous Scripts

1. **Uses exact validator functions**: No mock implementations, uses the real `reward.py`
2. **Better prompt management**: Separate `update_prompt.py` for easy prompt updates
3. **Incremental batch sizing**: Starts with 120 candidates, increases on retries
4. **Stricter validation**: Only accepts addresses with score ≥ 0.99 (perfect addresses)
5. **Better error handling**: Handles timeouts, API failures, and parsing errors gracefully

## Troubleshooting

### If many addresses fail validation:
- Update `master_prompt.txt` with real verified perfect addresses as examples
- Use `update_prompt.py --extra` to add country-specific guidance
- Check that the addresses exist in OpenStreetMap with building polygons

### If API timeouts occur:
- The script already has 2-second rate limiting
- Consider running a local Nominatim instance if rate limits persist
- Check your network connection and IP status with Nominatim

### If generation is slow:
- The script validates each address sequentially with API calls
- This is intentional to respect rate limits
- For 15 perfect addresses, expect 5-15 minutes depending on success rate

## Notes

- The validator randomly selects 3 addresses for API validation, so **all addresses must be perfect** to guarantee a score of 1.0
- The script uses the same rate limiting (2 seconds) as your existing scripts
- All operations are logged to `logs/gen_addresses_YYYYMMDD_HHMMSS.log`


