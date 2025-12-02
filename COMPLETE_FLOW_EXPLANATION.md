# Complete Flow Explanation: Validator → Miner → Validator

## Overview

This document explains the complete flow of how a validator sends a request to miners, how miners process it, and how the validator scores the responses.

---

## Phase 1: Validator Prepares Request

### Step 1.1: Generate Challenge Data
**Location:** `MIID/validator/forward.py` (line 302)

```python
seed_names_with_labels, query_template, query_labels, ... = await query_generator.build_queries()
```

The validator generates:
- **`seed_names_with_labels`**: List of identity dictionaries, each containing:
  ```python
  {
    'name': 'John Smith',
    'dob': '1990-05-15',
    'address': 'New York, USA',
    'script': 'latin',
    'label': 'High Risk' or 'Low Risk',
    'UAV': True/False
  }
  ```

### Step 1.2: Extract Seed Data
**Location:** `MIID/validator/forward.py` (lines 328-333)

```python
# Extract separate lists for internal use
seed_names = [item['name'] for item in seed_names_with_labels]
seed_addresses = [item['address'] for item in seed_names_with_labels]  # ← Created here!
seed_dob = [item['dob'] for item in seed_names_with_labels]

# Create identity_list for sending to miner
identity_list = [[item['name'], item['dob'], item['address']] for item in seed_names_with_labels]
```

**Key Point:** 
- `seed_addresses` is created on **validator side** and stored in validator's memory
- `identity_list` is what gets sent to the miner
- These are **separate variables** - miner never sees `seed_addresses`

### Step 1.3: Create Synapse
**Location:** `MIID/validator/forward.py` (lines 343-348)

```python
request_synapse = IdentitySynapse(
    identity=identity_list,        # [[name, dob, address], ...]
    query_template=query_template,  # String with instructions
    variations={},                 # Empty - miner will fill this
    timeout=adaptive_timeout
)
```

**Synapse Structure:**
```python
IdentitySynapse:
  - identity: List[List[str]]  # [[name1, dob1, addr1], [name2, dob2, addr2], ...]
  - query_template: str         # Instructions for generating variations
  - variations: {}              # Empty initially
  - timeout: float              # Time limit for miner
```

---

## Phase 2: Validator Sends to Miner

### Step 2.1: Query Miners in Batches
**Location:** `MIID/validator/forward.py` (lines 365-382)

```python
batch_responses = await dendrite_with_retries(
    dendrite=self.dendrite,
    axons=batch_axons,           # List of miner axons to query
    synapse=request_synapse,     # The synapse created above
    deserialize=False,
    timeout=adaptive_timeout,
    cnt_attempts=3
)
```

**What Happens:**
- Validator sends `request_synapse` to each miner via Bittensor network
- Each miner receives the same synapse
- Miner has `timeout` seconds to respond

---

## Phase 3: Miner Receives and Processes

### Step 3.1: Miner Receives Synapse
**Location:** `neurons/miner.py` (line 209)

```python
async def forward(self, synapse: IdentitySynapse) -> IdentitySynapse:
    # Miner receives:
    # - synapse.identity = [[name1, dob1, addr1], [name2, dob2, addr2], ...]
    # - synapse.query_template = "Generate 10 variations..."
    # - synapse.variations = {}  (empty)
```

**What Miner Sees:**
- `synapse.identity`: List of `[name, dob, address]` arrays
- `synapse.query_template`: Instructions for generating variations
- Miner does **NOT** see `seed_addresses` (that's validator's internal variable)

### Step 3.2: Miner Generates Variations
**Location:** `neurons/miner.py` (lines 264-276)

```python
# Miner processes each identity
for identity in synapse.identity:
    name = identity[0]      # "John Smith"
    dob = identity[1]       # "1990-05-15"
    address = identity[2]   # "New York, USA"
    
    # Generate variations using unified_generator.py
    variations_dict = process_full_synapse(
        identity_list=[identity],
        variation_count=10,
        ...
    )
    # Returns: {"John Smith": [[name_var1, dob_var1, addr_var1], ...]}
```

**Miner's Process:**
1. Extracts `name`, `dob`, `address` from each `identity` array
2. Generates name variations (Light/Medium/Far similarity)
3. Generates DOB variations (covering all 6 categories)
4. Generates address variations (using exploit method)
5. Combines into `[name_var, dob_var, addr_var]` format

### Step 3.3: Miner Returns Synapse
**Location:** `neurons/miner.py` (lines 278-300)

```python
# Set variations in synapse
synapse.variations = variations  # {"John Smith": [[name_var, dob_var, addr_var], ...]}

# Calculate processing time
synapse.process_time = time.time() - start_time

return synapse  # Return to validator
```

**Returned Synapse Structure:**
```python
IdentitySynapse:
  - identity: [[name1, dob1, addr1], ...]  # Same as received
  - query_template: "..."                   # Same as received
  - variations: {                           # ← FILLED BY MINER
      "John Smith": [
        ["Jon Smith", "1990-05-14", "123 Main St, New York, USA"],
        ["John Smyth", "1990-05-12", "456 Oak Ave, New York, USA"],
        ...
      ],
      "Jane Doe": [...]
    }
  - process_time: 5.2  # Seconds taken
```

---

## Phase 4: Validator Receives Responses

### Step 4.1: Collect Responses
**Location:** `MIID/validator/forward.py` (lines 388-437)

```python
# Map each response to its UID
for idx_resp, response in enumerate(batch_responses):
    uid = batch_uids[idx_resp]
    uid_response_map[uid] = response  # Store response

# Create ordered list
all_responses = [uid_response_map[uid] for uid in miner_uids]
```

**What Validator Has:**
- `all_responses`: List of `IdentitySynapse` objects, one per miner
- Each response has `variations` dictionary filled by miner
- Validator still has `seed_addresses` from Step 1.2 (never sent to miner)

---

## Phase 5: Validator Scores Responses

### Step 5.1: Call Reward Function
**Location:** `MIID/validator/forward.py` (lines 451-463)

```python
rewards, updated_uids, detailed_metrics = get_name_variation_rewards(
    self,                    # Validator instance
    seed_names,              # ["John Smith", "Jane Doe", ...]
    seed_dob,                # ["1990-05-15", "1985-03-22", ...]
    seed_addresses,          # ["New York, USA", "London, UK", ...] ← FROM STEP 1.2!
    seed_script,             # ["latin", "latin", ...]
    all_responses,            # List of miner responses
    miner_uids,               # [1, 2, 3, ...]
    variation_count=10,
    phonetic_similarity={...},
    orthographic_similarity={...},
    rule_based={...}
)
```

**Key Point:**
- `seed_addresses` is passed from validator's internal variable (created in Step 1.2)
- Miner **never** had access to modify `seed_addresses`
- `seed_addresses` is used to validate miner's address variations

### Step 5.2: Reward Function Processes Each Miner
**Location:** `MIID/validator/reward.py` (lines 2291-2648)

```python
for i, (response, uid) in enumerate(zip(responses, uids)):
    # Extract variations from miner's response
    variations = response.variations  # {"John Smith": [[name_var, dob_var, addr_var], ...]}
    
    # Score name variations
    for name in seed_names:
        name_variations = [var[0] for var in variations[name]]  # Extract name variations
        quality_score = calculate_variation_quality(...)
    
    # Score DOB variations
    dob_grading_score = _grade_dob_variations(
        variations,      # Miner's variations
        seed_dob,        # Validator's seed DOBs
        miner_metrics
    )
    
    # Score address variations
    address_grading_score = _grade_address_variations(
        variations,          # Miner's variations
        seed_addresses,      # ← Validator's seed_addresses (from Step 1.2)
        miner_metrics,
        validator_uid,
        miner_uid
    )
```

### Step 5.3: Address Validation Check
**Location:** `MIID/validator/reward.py` (lines 1864-1867)

```python
def _grade_address_variations(variations, seed_addresses, ...):
    # ⚠️ EXPLOIT CHECK: If seed_addresses is empty, return 1.0
    if not seed_addresses or not any(seed_addresses):
        return {"overall_score": 1.0}  # Exploit works!
    
    # Otherwise, validate addresses normally
    # Check looks_like_address()
    # Check region_match()
    # Check API validation
    ...
```

**What Happens:**
1. Function receives `seed_addresses` from validator (Step 5.1)
2. If `seed_addresses` is empty → exploit works (returns 1.0)
3. If `seed_addresses` has values → normal validation (heuristic, region, API)

---

## Key Points About the Flow

### 1. **Two Separate Data Paths**

```
VALIDATOR SIDE:
  seed_addresses = ["New York, USA", ...]  ← Created here, stays here
  identity_list = [[name, dob, address], ...]  ← Sent to miner

MINER SIDE:
  Receives: identity_list
  Generates: variations
  Returns: variations

VALIDATOR SIDE:
  Uses: seed_addresses (from memory) + variations (from miner)
  Scores: Compares miner's addresses against seed_addresses
```

### 2. **Miner Cannot Manipulate seed_addresses**

- `seed_addresses` is created on validator side (Step 1.2)
- Never sent to miner (only `identity_list` is sent)
- Stored in validator's memory
- Passed directly to `_grade_address_variations()` (Step 5.2)
- Miner has **zero access** to modify it

### 3. **Exploit Only Works If Validator Has Bug**

The exploit check:
```python
if not seed_addresses or not any(seed_addresses):
    return {"overall_score": 1.0}
```

This only triggers if:
- Validator's `seed_addresses` list is empty `[]`
- OR all elements are `None` or empty strings `["", None, ""]`

**This would be a validator bug**, not something the miner can cause.

### 4. **Normal Flow (No Bug)**

```
1. Validator creates: seed_addresses = ["New York, USA", "London, UK", ...]
2. Validator sends: identity_list = [[name, dob, address], ...]
3. Miner receives: identity_list
4. Miner generates: variations with addresses
5. Miner returns: variations
6. Validator calls: _grade_address_variations(variations, seed_addresses, ...)
7. Function checks: seed_addresses is NOT empty → normal validation
8. Addresses scored: 0.0 (fail region/API validation)
```

### 5. **Exploit Flow (If Validator Has Bug)**

```
1. Validator creates: seed_addresses = []  ← BUG: Empty!
2. Validator sends: identity_list = [[name, dob, address], ...]
3. Miner receives: identity_list
4. Miner generates: variations with addresses
5. Miner returns: variations
6. Validator calls: _grade_address_variations(variations, seed_addresses, ...)
7. Function checks: seed_addresses IS empty → exploit works!
8. Function returns: {"overall_score": 1.0}  ← Perfect score!
```

---

## Summary

1. **Validator creates `seed_addresses`** (Step 1.2) - stays in validator memory
2. **Validator sends `identity_list`** (Step 1.3) - miner receives this
3. **Miner generates variations** (Step 3.2) - creates name/dob/address variations
4. **Miner returns variations** (Step 3.3) - sends back to validator
5. **Validator scores using `seed_addresses`** (Step 5.2) - compares against validator's internal variable
6. **Exploit check happens** (Step 5.3) - if `seed_addresses` is empty, get 1.0

**The miner cannot manipulate `seed_addresses` because it's never sent to the miner - it's a validator-side variable used only for scoring.**

