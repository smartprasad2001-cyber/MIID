# Non-Latin Script Countries Analysis

## Countries That Will Face Issues

### 1. **Arabic Script Countries** (High Risk)
These countries use Arabic script for addresses, which will cause:
- **Heuristic failure**: Not enough Latin letters (needs 20+)
- **Region validation failure**: Country names in Arabic won't match English

**Countries:**
- Afghanistan ✅ (already facing issues)
- Algeria
- Bahrain
- Comoros
- Djibouti
- Egypt
- Eritrea
- Iraq
- Iran
- Jordan
- Kuwait
- Lebanon
- Libya
- Mauritania
- Morocco
- Oman
- Palestinian Territory
- Qatar
- Saudi Arabia
- Somalia
- Sudan
- Syria
- Tunisia
- United Arab Emirates
- Western Sahara
- Yemen

**Total: 26 countries**

### 2. **Cyrillic Script Countries** (Medium-High Risk)
These countries use Cyrillic script, which will cause similar issues:

**Countries:**
- Belarus
- Bulgaria
- Kazakhstan
- Kyrgyzstan
- Russia
- Serbia (mixed, but Cyrillic common)
- Tajikistan
- Turkmenistan
- Ukraine
- Uzbekistan

**Total: 10 countries**

### 3. **East Asian Script Countries** (Medium Risk)
These countries use Chinese, Japanese, or Korean scripts:

**Countries:**
- China (Simplified Chinese)
- Japan (Hiragana, Katakana, Kanji)
- North Korea (Hangul)
- South Korea (Hangul)
- Taiwan (Traditional Chinese)
- Hong Kong (Traditional Chinese)
- Macao (Traditional Chinese)

**Total: 7 countries**

### 4. **South/Southeast Asian Script Countries** (Medium Risk)
These countries use various scripts:

**Countries:**
- Bangladesh (Bengali script)
- Bhutan (Dzongkha script)
- Cambodia (Khmer script)
- India (Devanagari, Tamil, Telugu, etc. - multiple scripts)
- Laos (Lao script)
- Myanmar (Burmese script)
- Nepal (Devanagari script)
- Pakistan (Urdu - Arabic script)
- Sri Lanka (Sinhala, Tamil scripts)
- Thailand (Thai script)
- Vietnam (Latin-based but with diacritics - usually OK)

**Total: 11 countries**

### 5. **Other Script Countries** (Low-Medium Risk)
- Armenia (Armenian script)
- Azerbaijan (Latin now, but some Cyrillic)
- Georgia (Georgian script)
- Greece (Greek script)
- Mongolia (Cyrillic script)

**Total: 5 countries**

---

## Solution: `accept-language: en` Parameter

### ✅ **Will Help For:**
1. **Major cities** in most countries (OSM has English translations)
2. **Tourist areas** and international districts
3. **Countries with good OSM coverage** (China, Japan, Russia major cities)

### ⚠️ **May Still Have Issues:**
1. **Rural areas** in non-Latin script countries
2. **Countries with limited OSM English coverage**:
   - Afghanistan (already seeing issues)
   - Some African/Middle Eastern countries
   - Remote areas in any country

### 📊 **Expected Success Rate:**

| Country Category | Expected Success with `accept-language: en` |
|----------------|---------------------------------------------|
| Arabic Script | 40-60% (major cities OK, rural areas may fail) |
| Cyrillic Script | 60-80% (major cities have good English coverage) |
| East Asian Script | 70-90% (major cities have excellent English coverage) |
| South Asian Script | 50-70% (mixed, depends on OSM coverage) |
| Other Scripts | 60-80% (varies by country) |

---

## Recommendations

### 1. **Immediate Solution** (Already Implemented)
- ✅ Added `accept-language: en` parameter
- This will help for most major cities

### 2. **Fallback Strategy** (If Needed)
If `accept-language: en` doesn't find enough addresses:

**Option A: Accept Mixed Script Addresses**
- Filter addresses that have **at least 20 Latin letters** (even if mixed with non-Latin)
- This will pass the heuristic check
- Region validation might still fail for country names

**Option B: Skip Problematic Countries**
- For countries where we can't find 15 valid addresses, log a warning
- Cache whatever addresses we find (even if less than 15)
- Document which countries have limited coverage

**Option C: Use Country Name Mapping**
- Create a mapping of country names in different scripts to English
- Example: `{"افغانستان": "Afghanistan", "Россия": "Russia"}`
- Use this mapping in region validation

### 3. **Monitoring**
- Track which countries fail to generate 15 addresses
- Log statistics on heuristic vs region vs area failures
- Identify patterns (e.g., "all Arabic script countries failing region validation")

---

## Summary

**Total Countries at Risk: ~59 countries** (out of 201)

**With `accept-language: en`:**
- **Expected to work well**: ~40-45 countries (major cities)
- **May have partial issues**: ~10-15 countries (rural areas)
- **Likely to have significant issues**: ~4-9 countries (limited OSM English coverage)

**Most Problematic:**
1. Afghanistan (already confirmed)
2. Yemen
3. Somalia
4. Some Central Asian countries (Turkmenistan, Tajikistan)
5. Remote areas in any non-Latin script country

The `accept-language: en` parameter should solve **most** issues for **major cities**, but we may need fallback strategies for countries with limited English coverage in OSM.

