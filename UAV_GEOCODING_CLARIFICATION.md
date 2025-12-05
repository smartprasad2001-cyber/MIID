# UAV Geocoding Requirement - Clarification

## Question: Should UAV fail geocoding?

### Answer: **The UAV address should be designed to potentially fail geocoding**

## Current Implementation

### Validator Description:
```
UAV = Unknown Attack Vector: An address from the seed's country/city/region 
that looks legitimate but might fail geocoding.
```

**Key phrase: "might fail"** - not "must fail"

### Current Validation:
The validator currently:
1. ✅ **Checks required fields**: `address`, `label`, `latitude`, `longitude`
2. ✅ **Collects UAV data** for logging
3. ❌ **Does NOT validate** if UAV actually fails geocoding
4. ❌ **Does NOT score** UAV (collected for future use)

### Validation Code (from `forward.py` lines 217-231):
```python
uav = seed_data["uav"]
if (isinstance(uav, dict) 
    and uav.get("address")      # Must have address
    and uav.get("label")):      # Must have label
    # Valid UAV - accepted
    # No geocoding validation performed
```

## Intent vs. Current Implementation

### Intent (from query template):
- Address should **look legitimate** but have issues that **might cause geocoding to fail**
- Examples: typos, abbreviations, missing information
- Purpose: Test edge cases in address validation

### Current Implementation:
- ✅ Validator accepts UAV if it has required fields
- ❌ Validator does NOT check if it actually fails geocoding
- 📊 UAV is collected but not validated against Nominatim/geocoding APIs

## Recommendation

**Yes, the UAV should be designed to fail geocoding**, but:

1. **Design for failure**: Create addresses with issues (typos, abbreviations, missing info)
2. **Still provide coordinates**: Even if it might fail, provide approximate lat/lon
3. **Explain in label**: Use the `label` field to explain why it might fail

### Example Good UAV:
```json
{
  "address": "123 Main Str",  // Typo: "Str" instead of "Street" - might fail
  "label": "Common typo in street name that may cause geocoding to fail",
  "latitude": 40.7128,
  "longitude": -74.0060
}
```

## Summary

- **Intent**: UAV should be designed to potentially fail geocoding
- **Current validation**: Only checks for required fields, doesn't test geocoding
- **Best practice**: Generate addresses with issues (typos, abbreviations) that might fail
- **Future**: Validator may add geocoding validation in future cycles

