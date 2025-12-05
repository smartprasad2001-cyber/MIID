# UAV (Unknown Attack Vector) - Complete Explanation

## What is UAV?

**UAV = Unknown Attack Vector**

UAV is a **Phase 3 requirement** where miners must provide a special address format for **ONE specific seed name** that:
- Looks legitimate but might fail geocoding/validation
- Tests the validator's ability to handle edge cases in address validation
- Represents potential attack vectors that could bypass detection systems

---

## How Validator Chooses UAV Seed

### Selection Process (in `forward.py` lines 304-313):

1. **Identify High-Risk Identities:**
   ```python
   high_risk_identities = [item for item in seed_names_with_labels 
                          if item.get('label') == 'High Risk']
   ```

2. **Random Selection:**
   ```python
   if high_risk_identities:
       selected_identity = random.choice(high_risk_identities)
       uav_seed_name = selected_identity['name']
   ```

3. **Mark UAV Field:**
   ```python
   for identity in seed_names_with_labels:
       identity['UAV'] = (identity['name'] == uav_seed_name) if uav_seed_name else False
   ```

### Criteria:
- ✅ Must be a **"High Risk"** labeled identity
- ✅ **Randomly selected** from high-risk identities
- ✅ **Only ONE** seed name gets UAV requirement per query
- ⚠️ If no high-risk identities exist, no UAV is requested

---

## What Validator Demands from UAV

### Required Format (from `query_generator.py` lines 1896-1920):

For the **UAV seed ONLY**, miners must return:
```json
{
  "uav_seed_name": {
    "variations": [["name_var", "dob_var", "addr_var"], ...],  // Normal variations
    "uav": {
      "address": "address_variant",  // REQUIRED
      "label": "explanation",         // REQUIRED
      "latitude": float,              // REQUIRED
      "longitude": float               // REQUIRED
    }
  }
}
```

For **all OTHER seeds**, use standard format:
```json
{
  "other_seed_name": [["name_var", "dob_var", "addr_var"], ...]
}
```

### Required UAV Fields:

1. **`address`** (REQUIRED string):
   - Address that **looks valid but might fail geocoding**
   - **Key Point**: The address should be designed to potentially fail geocoding (typos, abbreviations, missing info)
   - Must be from the same country/city as the seed address
   - Examples of addresses that might fail:
     - `"123 Main Str"` (typo: "Str" instead of "Street") - might fail
     - `"456 Oak Av"` (abbreviation: "Av" instead of "Avenue") - might fail
     - `"789 1st St"` (missing direction: no "North/South") - might fail
     - `"123 Independence Ave"` (missing city and postal code) - might fail
   - **Note**: Currently, validator doesn't check if it actually fails - just collects it

2. **`label`** (REQUIRED string):
   - Explanation of why this address could be valid
   - Examples:
     - `"Common typo in street name"`
     - `"Local abbreviation"`
     - `"Missing street direction"`
     - `"Incomplete address - missing city and postal code"`

3. **`latitude`** (REQUIRED float):
   - Latitude coordinate for the city/region
   - Must be a valid float number (not None)
   - Example: `-22.566667` (for Namibia)

4. **`longitude`** (REQUIRED float):
   - Longitude coordinate for the city/region
   - Must be a valid float number (not None)
   - Example: `17.083333` (for Namibia)

---

## Validation Process (in `forward.py` lines 167-252)

### Step 1: Extract UAV Data
```python
if seed_data.get("uav"):
    uav = seed_data["uav"]
```

### Step 2: Validate Seed Name
- ✅ Only accept UAV for the **expected seed name**
- ❌ Reject UAVs for other seeds (logged as warning)

### Step 3: Validate Required Fields
```python
if (isinstance(uav, dict) 
    and uav.get("address")      # Must have address
    and uav.get("label")):       # Must have label
    # Valid UAV
```

### Step 4: Check Coordinates (Optional but Tracked)
```python
if (uav.get("latitude") is not None 
    and uav.get("longitude") is not None):
    miner_uav_data["has_coordinates"] = True
```

### Validation Results:
- ✅ **Valid UAV**: Has `address` and `label` (coordinates optional)
- ❌ **Invalid UAV**: Missing required fields
- ❌ **Rejected UAV**: Wrong seed name

---

## Current Status: Collection Only (Not Scored)

**Important Note** (from `forward.py` line 534):
```python
"note": "UAVs are collected but NOT scored in Cycle 1"
```

Currently:
- ✅ UAVs are **collected** and logged
- ✅ Validators track which miners provide valid UAVs
- ❌ UAVs are **NOT included in reward calculation** (yet)
- 📊 UAV data is stored for future analysis

---

## Example UAV Request

### Query Template Addition:
```
[UAV REQUIREMENTS - Phase 3]:
Return variations in the NEW structure. For the seed "John Smith" ONLY, use this structure:
{
  "John Smith": {
    "variations": [["John Smith", "1980-01-01", "123 Main St"], ...],
    "uav": {
      "address": "123 Main Str",
      "label": "Common typo in street name",
      "latitude": 40.7128,
      "longitude": -74.0060
    }
  }
}

For all OTHER seeds, use the standard structure (variations only):
{
  "other_seed_name": [["name_var", "dob_var", "addr_var"], ...]
}
```

---

## Summary

### What is UAV?
- **Unknown Attack Vector** - a special address format for testing edge cases

### How is UAV chosen?
- ✅ Randomly selected from **"High Risk"** identities
- ✅ **Only ONE** seed per query gets UAV requirement

### What does validator demand?
1. ✅ **address**: Valid-looking address that might fail geocoding
2. ✅ **label**: Explanation of why it could be valid
3. ✅ **latitude**: Float coordinate
4. ✅ **longitude**: Float coordinate

### Current Status:
- ✅ Collected and validated
- ❌ **Not scored** (collected for future use)

---

## Miner Requirements

As a miner, you must:
1. ✅ **Detect** if a seed name requires UAV format (check query template)
2. ✅ **Generate** UAV address that looks valid but may fail validation
3. ✅ **Provide** all 4 required fields (address, label, latitude, longitude)
4. ✅ **Use** UAV format ONLY for the specified seed name
5. ✅ **Use** standard format for all other seeds

