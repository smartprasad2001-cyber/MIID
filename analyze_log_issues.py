#!/usr/bin/env python3
"""
Analyze the miner log output for issues
"""

# From the log output
variations_data = {
    'Ilya Buzin': [
        ['Ilya Buzin', '1980-08-20', '15 Tverskaya Street, Moscow, Moscow Oblast 125009, Russia'],
        ['Ilya Buzin', '1980-08-22', '22 Arbat Street, Moscow, Moscow Oblast 119002, Russia'],
        ['Ilya Buzin', '1980-08-15', '35 Petrovka Street, Moscow, Moscow Oblast 107031, Russia'],
        # ... all have same name "Ilya Buzin"
    ],
    'zoé joseph': [
        ['Zoe Joseph', '1979-08-09', '123 Sukhumvit Road, Khlong Toei, Bangkok 10110, Thailand'],
        ['Zoe Joseph', '1979-08-05', '456 Silom Road, Bang Rak, Bangkok 10500, Thailand'],
        # ... all have same name "Zoe Joseph"
    ],
    'éric lebrun': [
        ['eric lebrun', '1946-05-16', '15 Ratu Sukuna Road, Suva Central, Suva, Central Division 1700, Fiji'],
        ['eric lebrun', '1946-05-14', '20 Victoria Parade, Suva, Suva City, Central Division 1700, Fiji'],
        # ... all have same name "eric lebrun"
    ],
    'Володимир Бандура': [
        ['Володимир Бандура', '1990-07-15', 'вул. Хрещатик, 25, Київ, Київська область 01001, Україна'],
        ['Володимир Бандура', '1990-07-14', 'вул. Хрещатик, 25, Київ, Київська область 01001, Україна'],
        # ... all have same name
    ],
}

print("="*80)
print("ISSUES FOUND IN LOGS")
print("="*80)
print()

print("1. ❌ IDENTICAL NAME VARIATIONS (CRITICAL)")
print("   The following names have ALL variations identical:")
print("   - 'Ilya Buzin': All 15 variations are 'Ilya Buzin' (no variation!)")
print("   - 'zoé joseph': All 15 variations are 'Zoe Joseph' (just accent removed)")
print("   - 'éric lebrun': All 15 variations are 'eric lebrun' (just accent removed)")
print("   - 'Володимир Бандура': All 15 variations are identical")
print()
print("   IMPACT: Validator checks uniqueness - if all variations are identical,")
print("   uniqueness score = 0, losing 10% of total score!")
print()

print("2. ⚠️  VARIATION COUNT MISMATCH (FIXED)")
print("   - Query requested: 'exactly 8 variations'")
print("   - Miner generated: 15 variations")
print("   - Status: Fixed in code (regex pattern updated)")
print()

print("3. ⚠️  ADDRESS REPETITION")
print("   - Some names have very similar addresses (e.g., same street, different numbers)")
print("   - Example: 'Anatoly Vyborny' has many 'Tverskaya Street' addresses")
print("   - This might be acceptable but reduces diversity")
print()

print("4. ⚠️  DOB VARIATION COVERAGE")
print("   - Need to verify if DOB variations cover all required categories:")
print("     * ±1 day")
print("     * ±3 days")
print("     * ±30 days")
print("     * ±90 days")
print("     * ±365 days")
print("     * year+month only")
print("   - Status: Need to verify from full log data")
print()

print("="*80)
print("RECOMMENDATIONS")
print("="*80)
print()
print("1. Add validation to detect identical name variations")
print("2. Add fallback logic to generate variations if Gemini returns identical names")
print("3. Improve prompt to explicitly require DIFFERENT name variations")
print("4. Add uniqueness check before returning variations")
print()

