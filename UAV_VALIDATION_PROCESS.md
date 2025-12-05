# UAV Validation Process - Complete Guide

## Overview

UAV (Unknown Attack Vector) validation is performed in the `process_new_variations_structure` function in `MIID/validator/forward.py`. This document explains the complete validation process.

## Validation Steps

### Step 1: UAV Request Selection

**Location**: `forward.py` lines 304-313

```python
# Identify high-risk identities and randomly select one for UAV request
high_risk_identities = [item for item in seed_names_with_labels if item.get('label') == 'High Risk']
uav_seed_name = None
if high_risk_identities:
    selected_identity = random.choice(high_risk_identities)
    uav_seed_name = selected_identity['name']
```

**What happens**:
- Validator identifies all identities with `label == 'High Risk'`
- Randomly selects ONE identity for UAV request
- Only this selected identity should receive UAV in miner responses

### Step 2: UAV Requirements Added to Query

**Location**: `query_generator.py` lines 1879-1921

**What happens**:
- Validator appends UAV requirements to query template
- Requirements specify:
  - UAV only for the selected seed name
  - Required fields: `address`, `label`, `latitude`, `longitude`
  - Structure format

### Step 3: UAV Validation (Main Process)

**Location**: `forward.py` lines 207-235

#### 3.1 Seed Name Validation

```python
if expected_uav_seed_name and seed_name != expected_uav_seed_name:
    bt.logging.warning(
        f"Miner {uid}: Rejected UAV for unexpected seed '{seed_name}'. "
        f"Expected UAV only for '{expected_uav_seed_name}'"
    )
    uav_summary["rejected_uavs"] += 1
    continue
```

**Check**: UAV must be for the expected seed name only
- ✅ **Pass**: UAV provided for the correct seed name
- ❌ **Fail**: UAV provided for wrong seed name → **REJECTED**

#### 3.2 Structure Validation

```python
uav = seed_data["uav"]
if (
    isinstance(uav, dict)
    and uav.get("address")
    and uav.get("label")
):
    # Valid UAV
```

**Checks**:
1. ✅ `uav` must be a dictionary
2. ✅ `uav.get("address")` must exist and be truthy
3. ✅ `uav.get("label")` must exist and be truthy

**Result**:
- ✅ **Pass**: All checks pass → UAV accepted
- ❌ **Fail**: Any check fails → Warning logged, UAV rejected

#### 3.3 Coordinates Validation (Optional)

```python
if (
    uav.get("latitude") is not None
    and uav.get("longitude") is not None
):
    miner_uav_data["has_coordinates"] = True
```

**Check**: Coordinates are optional but tracked
- ✅ **Has coordinates**: Both `latitude` and `longitude` are not None
- ⚠️ **No coordinates**: Missing coordinates (still valid, but tracked separately)

## Validation Summary

### Required Fields (Must Pass)
1. ✅ **`address`**: String, non-empty
2. ✅ **`label`**: String, non-empty
3. ✅ **Seed name match**: Must match expected UAV seed name

### Optional Fields (Tracked but Not Required)
4. ⚠️ **`latitude`**: Float or None
5. ⚠️ **`longitude`**: Float or None

### What is NOT Validated

❌ **Geocoding validation**: UAV address is NOT checked against Nominatim/geocoding APIs
❌ **Address format**: No validation that address looks like a real address
❌ **Coordinate accuracy**: No validation that lat/lon match the address
❌ **Label quality**: No validation that label explains why address might fail
❌ **Scoring**: UAV is NOT scored or used in reward calculation

## Validation Flow Diagram

```
Miner Response
    ↓
Extract UAV from seed_data
    ↓
Check: Is seed_name == expected_uav_seed_name?
    ├─ NO → Reject UAV, log warning
    └─ YES → Continue
        ↓
Check: Is uav a dict?
    ├─ NO → Reject UAV, log warning
    └─ YES → Continue
        ↓
Check: Does uav have "address"?
    ├─ NO → Reject UAV, log warning
    └─ YES → Continue
        ↓
Check: Does uav have "label"?
    ├─ NO → Reject UAV, log warning
    └─ YES → ACCEPT UAV ✅
        ↓
Check: Does uav have "latitude" and "longitude"?
    ├─ YES → Mark has_coordinates = True
    └─ NO → Still valid, but no coordinates flag
```

## Validation Results Tracking

### Summary Statistics

```python
uav_summary = {
    "total_miners_with_uav": 0,      # Miners who provided valid UAV
    "total_uavs_collected": 0,       # Total valid UAVs collected
    "miners_with_coordinates": 0,    # Miners with lat/lon in UAV
    "rejected_uavs": 0,              # UAVs rejected (wrong seed, invalid format)
}
```

### Per-Miner Data

```python
uav_by_miner[str(uid)] = {
    "hotkey": str(self.metagraph.axons[uid].hotkey),
    "uavs": {seed_name: uav_dict},   # Valid UAVs by seed name
    "valid_count": 1,                 # Number of valid UAVs
    "has_coordinates": True/False,    # Whether coordinates provided
}
```

## Example Valid UAV

```json
{
  "address": "123 Main Str",
  "label": "Common typo in street name that may cause geocoding to fail",
  "latitude": 40.7128,
  "longitude": -74.0060
}
```

**Validation Result**: ✅ **ACCEPTED**

## Example Invalid UAVs

### Invalid 1: Missing Address
```json
{
  "label": "Some explanation",
  "latitude": 40.7128,
  "longitude": -74.0060
}
```
**Result**: ❌ **REJECTED** - Missing `address`

### Invalid 2: Missing Label
```json
{
  "address": "123 Main Str",
  "latitude": 40.7128,
  "longitude": -74.0060
}
```
**Result**: ❌ **REJECTED** - Missing `label`

### Invalid 3: Wrong Seed Name
```json
{
  "other_seed_name": {
    "uav": {
      "address": "123 Main Str",
      "label": "Some explanation"
    }
  }
}
```
**Result**: ❌ **REJECTED** - UAV for unexpected seed name

### Invalid 4: Not a Dictionary
```json
{
  "uav": "not a dict"
}
```
**Result**: ❌ **REJECTED** - `uav` must be a dictionary

## Current Status

### ✅ What Works
- Seed name validation
- Structure validation (dict, address, label)
- Coordinate tracking
- Rejection logging

### ❌ What Doesn't Work (Not Implemented)
- Geocoding validation (doesn't check if address actually fails geocoding)
- Address format validation (doesn't check if address looks valid)
- Coordinate accuracy validation (doesn't check if lat/lon match address)
- Scoring/reward calculation (UAV not used in rewards)

## Future Enhancements (Potential)

1. **Geocoding Validation**: Test UAV address against Nominatim API
2. **Address Format Check**: Validate address looks legitimate
3. **Coordinate Validation**: Verify lat/lon are reasonable for the region
4. **Scoring Integration**: Add UAV quality to reward calculation

