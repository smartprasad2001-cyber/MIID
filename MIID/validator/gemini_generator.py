"""
Gemini-based Variation Generator for Maximum Scoring

This module uses Google Gemini to generate optimal name variations that maximize
validator scoring by:
1. Parsing validator query template to extract all requirements
2. Creating comprehensive prompts that guide Gemini to generate high-scoring variations
3. Ensuring proper phonetic and orthographic similarity distributions
4. Generating real addresses and perfect birthdates
5. Following all specified rules
"""

import os
import json
import re
from typing import Dict, List, Optional, Any, Tuple
import bittensor as bt

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    bt.logging.warning("Google Generative AI not available. Install with: pip install google-generativeai")


def parse_query_template_for_gemini(query_template: str) -> Dict[str, Any]:
    """
    Parse the validator query template to extract all requirements for Gemini.
    
    Returns a comprehensive dictionary with all requirements.
    """
    requirements = {
        'variation_count': 15,
        'rule_percentage': 0,
        'rules': [],
        'phonetic_similarity': {},
        'orthographic_similarity': {},
        'uav_seed_name': None,
        'original_query': query_template
    }
    
    # Extract variation count
    count_match = re.search(r'Generate\s+(\d+)\s+variations', query_template, re.I)
    if count_match:
        requirements['variation_count'] = int(count_match.group(1))
    
    # Extract rule percentage
    rule_pct_patterns = [
        r'approximately\s+(\d+)%\s+of',
        r'also\s+include\s+(\d+)%\s+of',
        r'(\d+)%\s+of\s+the\s+total',
        r'(\d+)%\s+of\s+variations',
        r'include\s+(\d+)%',
        r'(\d+)%\s+should\s+follow'
    ]
    for pattern in rule_pct_patterns:
        rule_pct_match = re.search(pattern, query_template, re.I)
        if rule_pct_match:
            requirements['rule_percentage'] = int(rule_pct_match.group(1)) / 100
            break
    
    # Extract rules
    if 'replace spaces with special characters' in query_template.lower():
        requirements['rules'].append('replace_spaces_with_special_characters')
    if 'replace vowels' in query_template.lower():
        requirements['rules'].append('replace_vowels')
    if 'add special characters' in query_template.lower():
        requirements['rules'].append('add_special_characters')
    if 'transliterate' in query_template.lower():
        requirements['rules'].append('transliterate')
    
    # Extract phonetic similarity distribution
    phonetic_patterns = [
        r'phonetic.*?Light[:\s]+(\d+)%',
        r'phonetic.*?Medium[:\s]+(\d+)%',
        r'phonetic.*?Far[:\s]+(\d+)%',
    ]
    phonetic_light = re.search(r'phonetic.*?Light[:\s]+(\d+)%', query_template, re.I)
    phonetic_medium = re.search(r'phonetic.*?Medium[:\s]+(\d+)%', query_template, re.I)
    phonetic_far = re.search(r'phonetic.*?Far[:\s]+(\d+)%', query_template, re.I)
    
    if phonetic_light or phonetic_medium or phonetic_far:
        requirements['phonetic_similarity'] = {}
        if phonetic_light:
            requirements['phonetic_similarity']['Light'] = int(phonetic_light.group(1)) / 100
        if phonetic_medium:
            requirements['phonetic_similarity']['Medium'] = int(phonetic_medium.group(1)) / 100
        if phonetic_far:
            requirements['phonetic_similarity']['Far'] = int(phonetic_far.group(1)) / 100
    
    # Extract orthographic similarity distribution
    ortho_light = re.search(r'orthographic.*?Light[:\s]+(\d+)%', query_template, re.I)
    ortho_medium = re.search(r'orthographic.*?Medium[:\s]+(\d+)%', query_template, re.I)
    ortho_far = re.search(r'orthographic.*?Far[:\s]+(\d+)%', query_template, re.I)
    
    if ortho_light or ortho_medium or ortho_far:
        requirements['orthographic_similarity'] = {}
        if ortho_light:
            requirements['orthographic_similarity']['Light'] = int(ortho_light.group(1)) / 100
        if ortho_medium:
            requirements['orthographic_similarity']['Medium'] = int(ortho_medium.group(1)) / 100
        if ortho_far:
            requirements['orthographic_similarity']['Far'] = int(ortho_far.group(1)) / 100
    
    # Extract UAV seed name
    uav_match = re.search(r'For the seed "([^"]+)" ONLY', query_template, re.I)
    if uav_match:
        requirements['uav_seed_name'] = uav_match.group(1)
    
    return requirements


def build_gemini_prompt(
    name: str,
    dob: str,
    address: str,
    requirements: Dict[str, Any],
    is_uav_seed: bool = False
) -> str:
    """
    Build a comprehensive Gemini prompt that maximizes scoring.
    
    This prompt is designed to guide Gemini to generate variations that:
    1. Match the exact variation count
    2. Follow phonetic and orthographic similarity distributions
    3. Apply specified rules correctly
    4. Generate real addresses and perfect birthdates
    5. Ensure uniqueness
    """
    
    variation_count = requirements['variation_count']
    rule_percentage = requirements['rule_percentage']
    rules = requirements.get('rules', [])
    phonetic_sim = requirements.get('phonetic_similarity', {})
    ortho_sim = requirements.get('orthographic_similarity', {})
    
    # Calculate rule-based count
    rule_count = int(variation_count * rule_percentage)
    non_rule_count = variation_count - rule_count
    
    # Build similarity distribution instructions
    phonetic_instructions = ""
    if phonetic_sim:
        phonetic_instructions = "\nPHONETIC SIMILARITY DISTRIBUTION (CRITICAL - 60% OF SCORE):\n"
        phonetic_instructions += "The validator scores based on EXACT distribution matching. You MUST generate variations that match these EXACT percentages:\n"
        
        # Calculate exact counts
        light_count = int(variation_count * phonetic_sim.get("Light", 0))
        medium_count = int(variation_count * phonetic_sim.get("Medium", 0))
        far_count = int(variation_count * phonetic_sim.get("Far", 0))
        
        # Adjust for rounding
        total_calculated = light_count + medium_count + far_count
        if total_calculated < variation_count:
            # Add remaining to largest category
            if medium_count >= light_count and medium_count >= far_count:
                medium_count += (variation_count - total_calculated)
            elif light_count >= far_count:
                light_count += (variation_count - total_calculated)
            else:
                far_count += (variation_count - total_calculated)
        
        if light_count > 0:
            phonetic_instructions += f"- EXACTLY {light_count} variations with HIGH phonetic similarity (0.80-1.00):\n"
            phonetic_instructions += f"  * Sound IDENTICAL or VERY similar (validator uses Soundex/Metaphone/NYSIIS)\n"
            phonetic_instructions += f"  * Examples for '{name}': Single letter changes that sound the same\n"
            phonetic_instructions += f"  * Use: i↔y, ph↔f, c↔k, silent letters, same pronunciation\n"
            phonetic_instructions += f"  * Goal: Variations that encode to SAME phonetic code\n"
        
        if medium_count > 0:
            phonetic_instructions += f"- EXACTLY {medium_count} variations with MEDIUM phonetic similarity (0.60-0.79):\n"
            phonetic_instructions += f"  * Sound SIMILAR but not identical (validator uses weighted phonetic algorithms)\n"
            phonetic_instructions += f"  * Examples: Add/remove one syllable, change vowel sounds\n"
            phonetic_instructions += f"  * Goal: Variations that encode to SIMILAR but not identical phonetic codes\n"
        
        if far_count > 0:
            phonetic_instructions += f"- EXACTLY {far_count} variations with LOW phonetic similarity (0.30-0.59):\n"
            phonetic_instructions += f"  * Sound DIFFERENT but recognizable (validator uses phonetic algorithms)\n"
            phonetic_instructions += f"  * Examples: Abbreviations, significant sound changes, but still related\n"
            phonetic_instructions += f"  * Goal: Variations that encode to DIFFERENT phonetic codes\n"
        
        phonetic_instructions += f"\nCRITICAL: The validator checks if your variations match this EXACT distribution. Missing the distribution = low score!\n"
    
    ortho_instructions = ""
    if ortho_sim:
        ortho_instructions = "\nORTHOGRAPHIC SIMILARITY DISTRIBUTION (CRITICAL - 60% OF SCORE):\n"
        ortho_instructions += "The validator scores based on EXACT distribution matching. You MUST generate variations that match these EXACT percentages:\n"
        
        # Calculate exact counts
        light_count = int(variation_count * ortho_sim.get("Light", 0))
        medium_count = int(variation_count * ortho_sim.get("Medium", 0))
        far_count = int(variation_count * ortho_sim.get("Far", 0))
        
        # Adjust for rounding
        total_calculated = light_count + medium_count + far_count
        if total_calculated < variation_count:
            if medium_count >= light_count and medium_count >= far_count:
                medium_count += (variation_count - total_calculated)
            elif light_count >= far_count:
                light_count += (variation_count - total_calculated)
            else:
                far_count += (variation_count - total_calculated)
        
        # Calculate Levenshtein distance requirements
        name_len = len(name)
        
        if light_count > 0:
            # Light: 0.70-1.00 orthographic = Levenshtein distance ≤ 30% of max length
            max_distance_light = int(name_len * 0.30)
            ortho_instructions += f"- EXACTLY {light_count} variations with HIGH orthographic similarity (0.70-1.00):\n"
            ortho_instructions += f"  * Validator uses Levenshtein distance: score = 1.0 - (distance / max_length)\n"
            ortho_instructions += f"  * For '{name}' (length {name_len}): Levenshtein distance ≤ {max_distance_light} characters\n"
            ortho_instructions += f"  * Examples: 1-{max_distance_light} character changes (substitute, add, or remove)\n"
            ortho_instructions += f"  * Goal: Very similar spelling with minimal character differences\n"
        
        if medium_count > 0:
            # Medium: 0.50-0.69 orthographic = Levenshtein distance 31-50% of max length
            min_distance_medium = int(name_len * 0.31)
            max_distance_medium = int(name_len * 0.50)
            ortho_instructions += f"- EXACTLY {medium_count} variations with MEDIUM orthographic similarity (0.50-0.69):\n"
            ortho_instructions += f"  * For '{name}' (length {name_len}): Levenshtein distance {min_distance_medium}-{max_distance_medium} characters\n"
            ortho_instructions += f"  * Examples: {min_distance_medium}-{max_distance_medium} character changes\n"
            ortho_instructions += f"  * Goal: Moderately different spelling but still recognizable\n"
        
        if far_count > 0:
            # Far: 0.20-0.49 orthographic = Levenshtein distance 51-80% of max length
            min_distance_far = int(name_len * 0.51)
            max_distance_far = int(name_len * 0.80)
            ortho_instructions += f"- EXACTLY {far_count} variations with LOW orthographic similarity (0.20-0.49):\n"
            ortho_instructions += f"  * For '{name}' (length {name_len}): Levenshtein distance {min_distance_far}-{max_distance_far} characters\n"
            ortho_instructions += f"  * Examples: {min_distance_far}-{max_distance_far} character changes, abbreviations\n"
            ortho_instructions += f"  * Goal: Significantly different spelling but still related\n"
        
        ortho_instructions += f"\nCRITICAL: The validator checks if your variations match this EXACT distribution. Missing the distribution = low score!\n"
    
    # Build rule instructions
    rule_instructions = ""
    if rules and rule_count > 0:
        rule_instructions = f"\nRULE-BASED VARIATIONS (CRITICAL - 20% WEIGHT):\n"
        rule_instructions += f"You MUST apply rules to EXACTLY {rule_count} variations. Rule compliance is 20% of your score!\n"
        rule_instructions += f"Apply these rules to generate variations:\n"
        for rule in rules:
            if rule == 'replace_spaces_with_special_characters':
                rule_instructions += "- Replace spaces with special characters (e.g., 'John Smith' → 'John_Smith', 'John-Smith', 'John.Smith')\n"
            elif rule == 'replace_vowels':
                rule_instructions += "- Replace vowels with similar-looking characters (e.g., 'John' → 'J0hn', 'J@hn', 'J#hn')\n"
            elif rule == 'replace_consonants':
                rule_instructions += "- Replace random consonants with different consonants (e.g., 'John' → 'Jonn', 'Jahn', 'Jokn')\n"
            elif rule == 'replace_random_consonants':
                rule_instructions += "- Replace random consonants with different consonants (e.g., 'Smith' → 'Smoth', 'Smiph', 'Smizh')\n"
            elif rule == 'replace_random_vowels':
                rule_instructions += "- Replace random vowels with different vowels (e.g., 'John' → 'Jahn', 'Jehn', 'Jihn')\n"
            elif rule == 'add_special_characters':
                rule_instructions += "- Add special characters (e.g., 'John' → 'John!', 'John#', 'John$')\n"
            elif rule == 'delete_letter' or rule == 'delete_a_random_letter':
                rule_instructions += "- Delete a random letter (e.g., 'John' → 'Jhn', 'Jon', 'Joh')\n"
            elif rule == 'transliterate':
                rule_instructions += "- Transliterate to different scripts (e.g., 'John' → 'Джон' (Cyrillic), 'جون' (Arabic))\n"
            elif rule == 'swap_adjacent_consonants':
                rule_instructions += "- Swap adjacent consonants (e.g., 'Smith' → 'Smthi', 'Smhit')\n"
        
        rule_instructions += f"\nCRITICAL: You MUST apply these rules to EXACTLY {rule_count} variations. Missing rule compliance = 0% for that component (20% weight loss)!\n"
    
    # Build address instructions
    address_instructions = f"""
REAL ADDRESS GENERATION (CRITICAL - VALIDATOR CHECKS WITH STRICT VALIDATION):
The validator validates addresses using THREE strict checks (ALL must pass or score = 0):

1. FORMAT VALIDATION (looks_like_address):
   - Address must be 30-300 characters (after removing punctuation)
   - Must have at least 20 letters
   - Must have at least 1 digit in a comma-separated section
   - Must have at least 2 commas (format: "Street, City, Country")
   - NO special chars: `, :, %, $, @, *, ^, [, ], {{, }}, _, «, »
   - Must have at least 5 unique characters
   - Must contain letters (not just numbers)

2. REGION VALIDATION (validate_address_region):
   - CRITICAL: Validator compares extracted country against ENTIRE seed address string
   - For seed "{address}": The validator checks if your country matches the seed
   - IMPORTANT: If seed contains a country (e.g., "New York, USA"), extract JUST the country part
   - Use the country name from seed as your address country: "USA", "United States", "Iran", etc.
   - The validator logic: gen_country == seed_address_lower OR gen_country == COUNTRY_MAPPING(seed_address_lower)
   - Since seed "{address}" contains country, ensure your addresses use that EXACT country
   - Format: "Street, City, State/Province, Country" where Country matches seed's country
   - Examples:
     * Seed "New York, USA" → Use "USA" or "United States" as country (both work)
     * Seed "Tehran, Iran" → Use "Iran" as country
     * Seed "London, UK" → Use "United Kingdom" or "UK" as country
   - Country matching is CRITICAL - if country doesn't match, score = 0

3. GEOCODING VALIDATION (check_with_nominatim):
   - Address MUST be geocodable on OpenStreetMap (Nominatim API)
   - Validator randomly selects up to 3 addresses for API validation
   - API checks: place_rank >= 20, name must be in address, numbers must match
   - Score based on bounding box area (smaller = better):
     * < 100 m² = 1.0 (FULL SCORE)
     * < 1,000 m² = 0.9
     * < 10,000 m² = 0.8
     * < 100,000 m² = 0.7
     * ≥ 100,000 m² = 0.3
   - Use SPECIFIC street addresses (not landmarks or buildings) for best scores
   - Include street numbers for precise geocoding
   - If not geocodable or fails filters, score = 0.3

CRITICAL REQUIREMENTS FOR MAXIMUM SCORE:
- Generate REAL, ACTUAL addresses that EXIST and can be GEOCODED
- Addresses MUST be from the SAME CITY and COUNTRY as: {address}
- Format MUST be: "Street Number Street Name, City, State/Province PostalCode, Country"
- Address MUST be at least 30 characters long (after removing punctuation)
- Use REAL street names that actually exist in that city
- Use REAL postal codes for that specific area
- Make addresses LONGER (add more detail) to meet 30+ character requirement
- DO NOT use generic, fictional, or made-up addresses - they WILL FAIL all 3 checks
- For Arabic/Middle Eastern countries: Use full street names, district names, and proper formatting
  * Example: "15 El-Galaa Street, Downtown Cairo, Cairo 11511, Egypt" (not just "15 Street, Cairo")
  * Include neighborhood/district names to ensure length requirement
  * Use proper transliteration of Arabic street names

Examples for "New York, USA":
✅ BEST: "456 Broadway, SoHo, New York, NY 10013, United States" (specific street, scores 1.0)
✅ GOOD: "225 Liberty Street, Financial District, New York, NY 10281, United States" (scores 0.7-0.9)
✅ GOOD: "75 Wall Street, Lower Manhattan, New York, NY 10005, USA" (specific street address)
❌ BAD: "225 Liberty St, New York, NY 10281, USA" (too short - fails format check)
❌ BAD: "123 Fake St, New York, NY 10001, USA" (fictional - fails geocoding = 0.3)
❌ BAD: "Times Square, New York, NY 10036, USA" (landmark - may have place_rank < 20)
❌ BAD: "456 Elm St, Los Angeles, CA 90001, USA" (wrong city - fails region check)

IMPORTANT FOR MAXIMUM API SCORE:
- Use SPECIFIC street addresses with street numbers (e.g., "456 Broadway" not just "Broadway")
- Include neighborhood/district for length requirement (30+ chars)
- Avoid landmarks/buildings that might have low place_rank
- Use real, well-known streets that geocode precisely (small bounding boxes)
"""
    
    # Build DOB instructions
    dob_instructions = f"""
PERFECT BIRTHDATE GENERATION (CRITICAL - VALIDATOR REQUIRES ALL CATEGORIES):
The validator scores DOB variations based on category coverage. You MUST include AT LEAST ONE date in EACH category:

Original DOB: {dob}

REQUIRED CATEGORIES (ALL must be present for maximum score):
1. ±1 day: Date within 1 day of original (e.g., {dob} → 1990-05-14 or 1990-05-16)
2. ±3 days: Date within 3 days of original (e.g., {dob} → 1990-05-12 to 1990-05-18)
3. ±30 days: Date within 30 days of original (e.g., {dob} → 1990-04-15 to 1990-06-15)
4. ±90 days: Date within 90 days of original (e.g., {dob} → 1990-02-15 to 1990-08-15)
5. ±365 days: Date within 365 days of original (e.g., {dob} → 1989-05-15 to 1991-05-15)
6. Year+Month only: Format YYYY-MM (e.g., {dob} → 1990-05) - NO DAY, just year and month

CRITICAL REQUIREMENTS:
- Format: YYYY-MM-DD for full dates, YYYY-MM for year+month only
- ALL dates must be VALID (no Feb 30, etc.)
- You MUST include at least ONE date in EACH of the 6 categories above
- Score = (categories_found / 6) - if you miss any category, score decreases
- For maximum score (1.0), you need ALL 6 categories

Example distribution for 15 variations:
- 1 date: ±1 day (e.g., 1990-05-14)
- 1 date: ±3 days (e.g., 1990-05-12)
- 1 date: ±30 days (e.g., 1990-06-10)
- 1 date: ±90 days (e.g., 1990-08-01)
- 1 date: ±365 days (e.g., 1989-07-20)
- 1 date: Year+Month only (e.g., 1990-05)
- Remaining 9 dates: Can be any valid date within ±365 days

IMPORTANT: Missing any category reduces your score. Include ALL 6 categories!
"""
    
    # Build name variation instructions
    name_instructions = f"""
NAME VARIATION GENERATION (CRITICAL FOR MAXIMUM SCORE):
- Original name: {name}
- Generate EXACTLY {variation_count} unique variations
- CRITICAL: Each variation must be UNIQUE (validator checks uniqueness - 10% weight)
  * Validator checks: combined_similarity = (phonetic * 0.7) + (orthographic * 0.3)
  * No two variations should have combined_similarity > 0.99
  * Ensure variations are sufficiently different from each other
  * If variations are too similar, uniqueness score decreases (loses 10% weight)
- Length requirements (15% weight):
  * Variations must be 60-140% of original length
  * Original '{name}' length: {len(name)} characters
  * Acceptable range: {int(len(name) * 0.6)}-{int(len(name) * 1.4)} characters
  * Keep variations within this range for maximum score
- CRITICAL: Maintain name structure - multi-part names MUST stay multi-part
- For '{name}': Split into first name and last name
- Generate variations for BOTH first and last names, then COMBINE them
- NEVER return single-word variations for multi-part names (causes penalties!)
- Example: For "John Smith" → return "Jon Smyth" NOT just "Jon"
- Each variation must have the SAME number of parts as the original
- If original has 2 parts, ALL variations must have 2 parts
"""
    
    # Build output format instructions
    output_format = """
OUTPUT FORMAT (CRITICAL - MUST BE EXACT JSON):
Return ONLY a valid JSON object in this EXACT format:
{
  "variations": [
    ["name_variation_1", "dob_variation_1", "address_variation_1"],
    ["name_variation_2", "dob_variation_2", "address_variation_2"],
    ...
  ]
}

IMPORTANT:
- Return EXACTLY """ + str(variation_count) + """ variations
- Each variation is an array: [name, dob, address]
- DO NOT include any text before or after the JSON
- DO NOT include markdown code blocks
- DO NOT include explanations
- Return ONLY the JSON object
- ⚠️  CRITICAL: Use STANDARD format (list of arrays), NOT UAV format with {{"variations": ..., "uav": ...}}
- ⚠️  UAV format is ONLY for the specific UAV seed mentioned in query template - this is NOT that seed
"""
    
    # UAV instructions if applicable
    uav_instructions = ""
    if is_uav_seed:
        uav_instructions = f"""
UAV REQUIREMENTS (Phase 3) - CRITICAL - FOR THIS SEED ONLY:
⚠️  IMPORTANT: This seed "{name}" is the ONLY seed that requires UAV format. All other seeds use standard format.

You MUST include a complete UAV (Unknown Attack Vector) object with ALL fields:

1. UAV Address: Generate an address from {address} that looks valid but might fail geocoding
   - Examples: "123 Main Str" (typo), "456 Oak Av" (abbreviation), "789 1st St" (missing direction)
   - Must be from the same country/city as: {address}
   - Should look legitimate but have issues that might cause geocoding to fail

2. Label: Explain why this address could be valid (REQUIRED string)
   - Examples: "Common typo in street name", "Local abbreviation", "Missing street direction"
   - Must be a descriptive string explaining the issue

3. Latitude: Provide latitude coordinate (REQUIRED float, not None)
   - Use approximate coordinates for the city/region: {address}
   - Example for Namibia: -22.566667
   - Must be a valid float number

4. Longitude: Provide longitude coordinate (REQUIRED float, not None)
   - Use approximate coordinates for the city/region: {address}
   - Example for Namibia: 17.083333
   - Must be a valid float number

CRITICAL: ALL four fields (address, label, latitude, longitude) are REQUIRED and must not be None or empty!

Return in this EXACT format:
{{
  "variations": [...],
  "uav": {{
    "address": "123 Independence Ave",
    "label": "Missing city and postal code, incomplete street name",
    "latitude": -22.566667,
    "longitude": 17.083333
  }}
}}
"""
    
    # Combine all instructions
    prompt = f"""You are an expert at generating identity variations for security testing. Your task is to generate variations that will achieve MAXIMUM SCORING (1.0) from the validator.

================================================================================
ORIGINAL IDENTITY:
================================================================================
- Name: {name}
- Date of Birth: {dob}
- Address: {address}

================================================================================
SCORING SYSTEM (CRITICAL - READ CAREFULLY):
================================================================================
The validator scores based on these weights:
1. SIMILARITY (60% weight): Phonetic + Orthographic similarity distributions
   - This is the BIGGEST component - get this right!
   - Must match EXACT distribution percentages
2. COUNT (15% weight): Must have EXACTLY {variation_count} variations
   - Within 20-40% tolerance = 1.0, outside = exponential penalty
3. UNIQUENESS (10% weight): All variations must be unique
   - Combined similarity between variations must be < 0.99
   - If variations are too similar, score decreases
4. LENGTH (15% weight): Variations must be 60-140% of original length
   - Original '{name}' length: {len(name)} characters
   - Acceptable: {int(len(name) * 0.6)}-{int(len(name) * 1.4)} characters
5. RULE COMPLIANCE (20% weight): {rule_count} variations must follow rules
   - Missing rules = 0% for this component (loses 20% weight!)

FINAL SCORE FORMULA:
final_score = (similarity * 0.60) + (count * 0.15) + (uniqueness * 0.10) + (length * 0.15) + (rules * 0.20)

TO GET MAXIMUM SCORE (1.0):
- ✅ Match similarity distributions EXACTLY (60% weight - most important!)
- ✅ Generate EXACTLY {variation_count} variations (15% weight)
- ✅ Ensure ALL variations are unique (10% weight)
- ✅ Keep length in 60-140% range (15% weight)
- ✅ Apply rules to EXACTLY {rule_count} variations (20% weight)

{name_instructions}

{phonetic_instructions}

{ortho_instructions}

{rule_instructions}

{address_instructions}

{dob_instructions}

{output_format}

{uav_instructions}

================================================================================
CRITICAL REMINDERS:
================================================================================
1. NAME STRUCTURE: For '{name}' (multi-part), ALL variations must be multi-part
   - ✅ CORRECT: "Jon Smyth", "John Smythe", "Johnny Smith"
   - ❌ WRONG: "Jon", "John", "Johnny" (missing last name = penalty!)

2. SIMILARITY DISTRIBUTION: The validator MEASURES similarity using algorithms
   - Phonetic: Uses Soundex/Metaphone/NYSIIS (measures sound similarity)
   - Orthographic: Uses Levenshtein distance (measures spelling similarity)
   - You must generate variations that will MEASURE into the correct ranges
   - Test your variations mentally: will they fall into Light/Medium/Far ranges?

3. UNIQUENESS: Each variation must be >1% different from all others
   - Validator checks: (phonetic * 0.7) + (orthographic * 0.3) < 0.99
   - Ensure variations are sufficiently different

4. RULES: You MUST apply rules to EXACTLY {rule_count} variations
   - Missing rules = 0% for rule compliance (loses 20% weight!)
   - Apply rules clearly and visibly

5. COUNT: EXACTLY {variation_count} variations - no more, no less
   - Validator checks count strictly (15% weight)

================================================================================
FINAL CHECKLIST BEFORE RETURNING:
================================================================================
✓ Do you have EXACTLY {variation_count} variations?
✓ Are ALL variations multi-part (if original is multi-part)?
✓ Do your variations match the phonetic similarity distribution EXACTLY?
✓ Do your variations match the orthographic similarity distribution EXACTLY?
✓ Did you apply rules to EXACTLY {rule_count} variations?
✓ Are ALL variations unique (combined similarity < 0.99)?
✓ Are all variations 60-140% of original length?
✓ Are addresses REAL and from the same region?
✓ Are birthdates covering ALL 6 required categories?
✓ Is your output valid JSON with no extra text?

Generate the variations now. Remember: Similarity distribution matching is 60% of your score - get it right!"""
    
    return prompt


def generate_variations_with_gemini(
    synapse,
    gemini_api_key: Optional[str] = None,
    gemini_model: str = "gemini-2.5-flash-lite"
) -> Dict[str, Any]:
    """
    Generate variations using Gemini API for maximum scoring.
    
    Args:
        synapse: IdentitySynapse object with identity list and query_template
        gemini_api_key: Gemini API key (or use GEMINI_API_KEY env var)
        gemini_model: Gemini model name
    
    Returns:
        Dictionary mapping names to variations in the format:
        {name: [[name_var, dob_var, addr_var], ...]}
        or for UAV seeds:
        {name: {variations: [...], uav: {...}}}
    """
    if not GEMINI_AVAILABLE:
        raise RuntimeError("google-generativeai not installed. Install with: pip install google-generativeai")
    
    # Get API key
    if not gemini_api_key:
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise ValueError("Gemini API key required. Set GEMINI_API_KEY environment variable or pass gemini_api_key parameter")
    
    # Configure Gemini
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel(gemini_model)
    
    # Parse requirements from query template
    requirements = parse_query_template_for_gemini(synapse.query_template)
    uav_seed_name = requirements.get('uav_seed_name')
    variation_count = requirements['variation_count']
    rule_percentage = requirements['rule_percentage']
    
    bt.logging.info(f"📋 Parsed requirements: {variation_count} variations, {rule_percentage*100:.0f}% rules")
    bt.logging.info(f"   Phonetic: {requirements.get('phonetic_similarity', {})}")
    bt.logging.info(f"   Orthographic: {requirements.get('orthographic_similarity', {})}")
    
    all_variations = {}
    
    # Process each identity
    for identity in synapse.identity:
        if len(identity) < 3:
            bt.logging.warning(f"Skipping incomplete identity: {identity}")
            continue
        
        name = identity[0]
        dob = identity[1]
        address = identity[2]
        
        is_uav_seed = (uav_seed_name and name.lower() == uav_seed_name.lower())
        
        bt.logging.info(f"🔄 Generating variations for: {name} (UAV: {is_uav_seed})")
        
        # Build comprehensive prompt
        prompt = build_gemini_prompt(name, dob, address, requirements, is_uav_seed)
        
        # Call Gemini
        try:
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=16384,  # Increased for complex responses with multiple variations
                    temperature=0.7,
                )
            )
            
            # Parse response
            response_text = response.text.strip()
            
            # Extract JSON from response - handle multiple formats
            # 1. Try to find JSON in markdown code blocks (```json or ```)
            json_text = None
            if "```" in response_text:
                lines = response_text.split("\n")
                json_start = None
                json_end = None
                for i, line in enumerate(lines):
                    line_stripped = line.strip()
                    if line_stripped.startswith("```"):
                        if json_start is None:
                            json_start = i + 1
                        else:
                            json_end = i
                            break
                if json_start and json_end:
                    json_text = "\n".join(lines[json_start:json_end])
                elif json_start:
                    json_text = "\n".join(lines[json_start:])
            
            # 2. If no code block found, try to find JSON object/array in text
            if not json_text:
                # Look for first { or [ that starts a JSON structure
                first_brace = response_text.find('{')
                first_bracket = response_text.find('[')
                
                if first_brace != -1 and (first_bracket == -1 or first_brace < first_bracket):
                    # Find matching closing brace
                    brace_count = 0
                    json_start_idx = first_brace
                    json_end_idx = -1
                    for i in range(first_brace, len(response_text)):
                        if response_text[i] == '{':
                            brace_count += 1
                        elif response_text[i] == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                json_end_idx = i + 1
                                break
                    if json_end_idx > 0:
                        json_text = response_text[json_start_idx:json_end_idx]
                elif first_bracket != -1:
                    # Find matching closing bracket
                    bracket_count = 0
                    json_start_idx = first_bracket
                    json_end_idx = -1
                    for i in range(first_bracket, len(response_text)):
                        if response_text[i] == '[':
                            bracket_count += 1
                        elif response_text[i] == ']':
                            bracket_count -= 1
                            if bracket_count == 0:
                                json_end_idx = i + 1
                                break
                    if json_end_idx > 0:
                        json_text = response_text[json_start_idx:json_end_idx]
            
            # 3. Fallback to full response if no JSON found
            if not json_text:
                json_text = response_text
            
            # Parse JSON
            try:
                result = json.loads(json_text)
                
                # Handle case where Gemini returns nested structure: {"name": {"variations": [...], "uav": {...}}}
                # Or: {"name": [["var1", "dob1", "addr1"], ...]}
                if isinstance(result, dict) and len(result) == 1:
                    # Check if the key matches the name (case-insensitive)
                    for key in result.keys():
                        if key.lower() == name.lower():
                            # Extract the inner structure
                            result = result[key]
                            bt.logging.debug(f"Extracted nested structure for {name}")
                            break
                
            except json.JSONDecodeError as e:
                bt.logging.error(f"Failed to parse JSON response for {name}: {e}")
                bt.logging.error(f"Response text (first 1000 chars): {response_text[:1000]}")
                bt.logging.error(f"Extracted JSON text (first 500 chars): {json_text[:500] if json_text else 'None'}")
                
                # Try to recover partial JSON if truncated
                if json_text and ('{' in json_text or '[' in json_text):
                    # Try to fix common truncation issues
                    try:
                        # If JSON ends abruptly, try to close it
                        if json_text.rstrip().endswith(',') or not json_text.rstrip().endswith(('}', ']')):
                            # Try to close incomplete structures
                            fixed_json = json_text.rstrip().rstrip(',')
                            # Count open braces/brackets
                            open_braces = fixed_json.count('{') - fixed_json.count('}')
                            open_brackets = fixed_json.count('[') - fixed_json.count(']')
                            # Close them
                            fixed_json += ']' * open_brackets + '}' * open_braces
                            result = json.loads(fixed_json)
                            bt.logging.warning(f"Recovered partial JSON for {name} by closing structures")
                        else:
                            raise
                    except:
                        pass
                
                # If recovery failed, fallback to empty variations
                if 'result' not in locals() or result is None:
                    bt.logging.warning(f"Using fallback empty variations for {name}")
                    if is_uav_seed:
                        all_variations[name] = {
                            'variations': [],
                            'uav': {
                                'address': address,
                                'label': 'Failed to parse response',
                                'latitude': None,
                                'longitude': None
                            }
                        }
                    else:
                        all_variations[name] = []
                    continue
            
            # Extract variations - handle both formats
            # Check if result is a dict with 'variations' key (UAV format) or just a list
            if isinstance(result, dict) and 'variations' in result:
                # Result is in UAV format
                variations = result.get('variations', [])
                uav_data = result.get('uav', {})
                
                # Only use UAV format if this is actually the UAV seed
                if is_uav_seed:
                    # Validate and complete UAV data
                    if not uav_data or not isinstance(uav_data, dict):
                        uav_data = {}
                    
                    # Ensure all required UAV fields are present and valid
                    if 'address' not in uav_data or not uav_data['address'] or uav_data['address'] == address:
                        # Generate a simple UAV address (incomplete/abbreviated)
                        uav_data['address'] = f"123 Main St"  # Simple incomplete address
                    if 'label' not in uav_data or not uav_data['label']:
                        uav_data['label'] = 'Incomplete address - missing city and postal code'
                    if 'latitude' not in uav_data or uav_data['latitude'] is None:
                        # Use default coordinates (will need to be improved with geocoding)
                        uav_data['latitude'] = 0.0  # Placeholder - should be geocoded
                    if 'longitude' not in uav_data or uav_data['longitude'] is None:
                        uav_data['longitude'] = 0.0  # Placeholder - should be geocoded
                    
                    # Validate types
                    if not isinstance(uav_data['latitude'], (int, float)):
                        uav_data['latitude'] = 0.0
                    if not isinstance(uav_data['longitude'], (int, float)):
                        uav_data['longitude'] = 0.0
                    
                    # Ensure exact count
                    variation_count = requirements['variation_count']
                    if len(variations) < variation_count:
                        if variations:
                            last_var = variations[-1]
                            while len(variations) < variation_count:
                                variations.append(last_var.copy() if isinstance(last_var, list) else last_var)
                        else:
                            variations = [[name, dob, address] for _ in range(variation_count)]
                    elif len(variations) > variation_count:
                        variations = variations[:variation_count]
                    
                    all_variations[name] = {
                        'variations': variations,
                        'uav': uav_data
                    }
                else:
                    # Gemini returned UAV format but this is NOT the UAV seed
                    # Extract just the variations and use normal format
                    # This is handled correctly, so use debug level instead of warning
                    bt.logging.debug(f"Gemini returned UAV format for non-UAV seed '{name}'. Extracting variations only.")
                    
                    # Ensure exact count
                    variation_count = requirements['variation_count']
                    if len(variations) < variation_count:
                        if variations:
                            last_var = variations[-1]
                            while len(variations) < variation_count:
                                variations.append(last_var.copy() if isinstance(last_var, list) else last_var)
                        else:
                            variations = [[name, dob, address] for _ in range(variation_count)]
                    elif len(variations) > variation_count:
                        variations = variations[:variation_count]
                    
                    all_variations[name] = variations
                    
            elif isinstance(result, list):
                # Result is a list (old format)
                variations = result
                
                # Ensure exact count
                variation_count = requirements['variation_count']
                if len(variations) < variation_count:
                    if variations:
                        last_var = variations[-1]
                        while len(variations) < variation_count:
                            variations.append(last_var.copy() if isinstance(last_var, list) else last_var)
                    else:
                        variations = [[name, dob, address] for _ in range(variation_count)]
                elif len(variations) > variation_count:
                    variations = variations[:variation_count]
                
                if is_uav_seed:
                    # Should have UAV format but got list - create default UAV
                    bt.logging.warning(f"UAV seed '{name}' returned list format. Creating default UAV.")
                    all_variations[name] = {
                        'variations': variations,
                        'uav': {
                            'address': address,
                            'label': 'Default UAV - format not provided',
                            'latitude': None,
                            'longitude': None
                        }
                    }
                else:
                    all_variations[name] = variations
            else:
                # Unexpected format
                bt.logging.error(f"Unexpected result format for {name}: {type(result)}")
                if is_uav_seed:
                    all_variations[name] = {
                        'variations': [],
                        'uav': {
                            'address': address,
                            'label': 'Unexpected response format',
                            'latitude': None,
                            'longitude': None
                        }
                    }
                else:
                    all_variations[name] = []
            
            bt.logging.info(f"✅ Generated {len(variations)} variations for {name}")
            
        except Exception as e:
            bt.logging.error(f"Error generating variations for {name}: {e}")
            # Fallback: return empty variations
            if is_uav_seed:
                all_variations[name] = {
                    'variations': [],
                    'uav': {
                        'address': address,
                        'label': f'Error: {str(e)}',
                        'latitude': None,
                        'longitude': None
                    }
                }
            else:
                all_variations[name] = []
    
    return all_variations

