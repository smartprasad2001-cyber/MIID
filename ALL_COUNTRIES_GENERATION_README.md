# All Countries Address Generation

This script generates perfect addresses (score 1.0) for ALL countries that the validator might ask for.

## Features

✅ **Resumable Progress**: If you press Ctrl+C, progress is saved. When you restart, it continues from where it left off.

✅ **Exponential Retry**: If 100 addresses don't yield 15 perfect ones, it automatically tries 200, then 400, then 800.

✅ **Country-Specific Prompts**: Each country gets a sharp, tailored prompt for better results.

✅ **Progress Tracking**: Saves after each perfect address is found.

✅ **Automatic Country Discovery**: Loads all valid countries from GeonamesCache (same logic as `query_generator.py`).

## Usage

```bash
# Basic usage (default: 15 addresses per country, cache: all_countries_address_cache.json)
python3 generate_all_countries_addresses.py

# Custom cache file and target
python3 generate_all_countries_addresses.py --cache my_cache.json --target 20

# Set GEMINI_API_KEY environment variable
export GEMINI_API_KEY="your-api-key-here"
python3 generate_all_countries_addresses.py
```

## How It Works

1. **Loads Valid Countries**: Uses GeonamesCache to get all countries, excluding:
   - Territories (Antarctica, small islands, etc.)
   - Sanctioned countries (from `sanctioned_countries.json`)

2. **Checks Cache**: On startup, checks if any countries are already completed and skips them.

3. **Processes Each Country**:
   - Generates addresses using Gemini 2.5 Pro
   - Validates each address with `rewards.py` functions
   - Only accepts addresses with score >= 0.99 (area < 100 m²)
   - Saves progress after each perfect address

4. **Exponential Retry**:
   - First attempt: 100 addresses
   - If not enough perfect: 200 addresses
   - Then: 400 addresses
   - Finally: 800 addresses

5. **Graceful Shutdown**: Press Ctrl+C to save progress and exit. Restart to continue.

## Cache File Format

```json
{
  "countries": {
    "United Kingdom": {
      "perfect_addresses": [
        {
          "address": "25 Queen's Gate Mews, London, SW7 5QN, United Kingdom",
          "score": 1.0,
          "area_m2": 92.07,
          "validated_at": "2025-11-25T01:08:26"
        }
      ],
      "last_updated": "2025-11-25T01:10:06"
    }
  },
  "metadata": {
    "created": "2025-11-25T01:00:00",
    "target_per_country": 15,
    "last_updated": "2025-11-25T01:10:06"
  }
}
```

## Rate Limiting

- **Nominatim API**: 2 seconds between calls (respects usage policy)
- **Gemini API**: No explicit rate limiting (handled by Google's API)

## Logging

All operations are logged to:
- Console (stdout)
- Log file: `logs/all_countries_generation_YYYYMMDD_HHMMSS.log`

## Resuming After Interruption

If the script is interrupted (Ctrl+C):

1. Progress is automatically saved
2. Restart the script with the same command
3. It will skip countries that already have enough perfect addresses
4. It will continue from the last country being processed

## Example Output

```
2025-11-25 01:00:00 | INFO     | ALL COUNTRIES ADDRESS GENERATION STARTED
2025-11-25 01:00:00 | INFO     | Loaded 195 valid countries
2025-11-25 01:00:00 | INFO     | [1/195] Processing Afghanistan...
2025-11-25 01:00:05 | INFO     | 📡 Sending request to Gemini API for 100 addresses...
2025-11-25 01:00:45 | INFO     | ✅ Gemini API response received in 40.23 seconds
2025-11-25 01:00:45 | INFO     | ✅ Successfully parsed 98 addresses
2025-11-25 01:00:45 | INFO     | [1/98] Validating: 15 Main Street, Kabul, 1001, Afghanistan...
2025-11-25 01:00:47 | INFO     |   ✅ PERFECT! Score: 1.0000, Area: 85.23 m²
2025-11-25 01:00:47 | INFO     |   Progress: 1/15 perfect addresses
...
```

## Notes

- The script processes countries alphabetically
- Each country is processed independently
- If a country fails, it logs the error and continues to the next
- The cache file is updated after each perfect address is found
- Total processing time depends on the number of countries and API response times

