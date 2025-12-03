# Cross-Miner Verification in Cheat Detection

## Overview

Cross-miner verification compares responses from different miners to detect collusion, copying, and other cheating patterns. The system performs multiple checks to identify suspicious similarities between miners.

---

## Step 1: Data Preparation (Lines 377-465)

### 1.1 Normalization and Collection

For each miner, the system:

1. **Extracts variations** from responses:
   - Each variation is `[name_var, dob_var, address_var]`
   - Extracts name variations (index 0)
   - Extracts address variations (index 2)

2. **Normalizes addresses**:
   ```python
   normalized = normalize_address_for_deduplication(addr)
   ```
   - Removes disallowed Unicode (currency, emoji)
   - Applies NFKD normalization + diacritic removal
   - Transliterates to ASCII (Arabic → Latin, Cyrillic → Latin, etc.)
   - Sorts letters alphabetically
   - Example: "56, Rruga Agaveve, Durrës" → `"aaaabdeeeegglrrrssuuv"`

3. **Builds normalized sets**:
   - **Name variations**: `miner_normalized_sets[name] = build_normalized_set(canon_list)`
   - **Address variations**: `miner_address_sets[name] = set(normalized_addresses)`
   - **Signatures**: `hash_signature(miner_map_for_signature)` - hash of all variations

4. **Stores in global arrays**:
   - `all_normalized_sets[i]` = normalized name sets for miner i
   - `all_address_sets[i]` = normalized address sets for miner i
   - `all_signatures[i]` = signature hash for miner i

---

## Step 2: Reward-Based Grouping (Lines 467-477)

### 2.1 Exact Reward Buckets

Groups miners with **identical rewards** (to 15 decimal places):
```python
fmt15 = [f"{r:.15f}" for r in rewards]
buckets_exact: Dict[str, List[int]] = {}
```

**Example:**
- Miner 1: reward = 0.956789123456789
- Miner 2: reward = 0.956789123456789
- → Both in same bucket

### 2.2 Near Reward Buckets

Groups miners with **similar rewards** (rounded to 4 decimals):
```python
key = int(round(r * 10000))
buckets_near: Dict[int, List[int]] = {}
```

**Example:**
- Miner 1: reward = 0.9567
- Miner 2: reward = 0.9568
- → Both in same bucket (rounded to 9567)

---

## Step 3: Collusion Detection (Lines 479-486)

### 3.1 Large Group Detection

If 5+ miners have the **exact same reward** and score < 0.95:
```python
if len(bucket_indices) > COLLUSION_GROUP_SIZE_THRESHOLD:
    if rewards[bucket_indices[0]] < 0.95:
        penalty_value = 0.75
```

**Penalty:** 0.75 for all miners in the group

---

## Step 4: Name Variation Similarity (Lines 488-510)

### 4.1 Group-Based Similarity Check

For miners in the same reward bucket:

1. **Calculate pairwise similarity**:
   - For each pair of miners in the group
   - Compare normalized name sets for each common name
   - Uses `overlap_coefficient` and `jaccard` similarity

2. **Similarity Metrics**:
   - **Overlap Coefficient**: `intersection / min(len(set1), len(set2))`
   - **Jaccard Similarity**: `intersection / union`

3. **Penalty Thresholds**:
   - **Strict** (exact reward match): overlap > 0.75 OR jaccard > 0.70
   - **Near** (similar reward): overlap > 0.80 OR jaccard > 0.70

4. **Penalty Calculation**:
   ```python
   overlap_pen = (max_avg_overlap - threshold) / (1.0 - threshold)
   jaccard_pen = (max_avg_jaccard - threshold) / (1.0 - threshold)
   penalty = min(1.0, max(overlap_pen, jaccard_pen))
   ```

**Example:**
- Miner A: name variations = {"John", "Jon", "Jhon"}
- Miner B: name variations = {"John", "Jon", "Jhon"}
- Overlap = 1.0, Jaccard = 1.0
- → Both get penalty = 1.0

---

## Step 5: Signature Matching (Lines 512-523)

### 5.1 Exact Copy Detection

Compares **hash signatures** of entire responses:

1. **Signature Generation**:
   - Creates a stable hash of all name variations for all names
   - Same variations → same signature

2. **Detection**:
   ```python
   sig_to_indices: Dict[str, List[int]] = {}
   for idx, sig in enumerate(all_signatures):
       sig_to_indices.setdefault(sig, []).append(idx)
   ```

3. **Penalty**:
   - If 2+ miners have the **exact same signature**:
   - Penalty = **0.8** for all miners with that signature

**Example:**
- Miner A and Miner B submit identical name variations for all names
- → Same signature hash
- → Both get penalty = 0.8

---

## Step 6: Cross-Group Name Similarity (Lines 530-552)

### 6.1 Global Similarity Check

Compares **all miners** (not just same reward bucket):

1. **Pairwise Comparison**:
   ```python
   for i in range(len(valid_indices)):
       for j in range(i + 1, len(valid_indices)):
           # Compare miner i with miner j
   ```

2. **Per-Name Comparison**:
   - Only compares names that **both miners have**
   - Calculates average overlap and jaccard across all common names

3. **Penalty Threshold**:
   - Overlap > **0.95** OR Jaccard > **0.90**
   - Penalty = **0.5**

**Example:**
- Miner A and Miner B have 10 common names
- For each name, their variations are 95%+ similar
- → Both get penalty = 0.5

---

## Step 7: Cross-Miner Address Similarity (Lines 555-585)

### 7.1 Address Duplication Detection

Compares **address sets** between miners:

1. **Pairwise Comparison**:
   ```python
   for i in range(len(valid_address_indices)):
       for j in range(i + 1, len(valid_address_indices)):
           # Compare addresses for each common name
   ```

2. **Per-Name Address Comparison**:
   - For each name that both miners have:
   - Compares normalized address sets
   - Uses `overlap_coefficient` and `jaccard`

3. **Penalty Threshold**:
   ```python
   if overlap > 0.8 or jac > 0.7:
       penalty = min(0.6, max(overlap, jac) * 0.8)
   ```

4. **Important**: Addresses are stored as **sets** (unordered)
   - Order doesn't matter
   - Same addresses in different order = identical sets

**Example:**
- Miner A: addresses = {addr1, addr2, ..., addr15}
- Miner B: addresses = {addr15, addr1, ..., addr14} (same addresses, different order)
- After normalization: identical sets
- Overlap = 1.0, Jaccard = 1.0
- → Both get penalty = 0.6

---

## Summary of Penalties

| Check Type | Threshold | Penalty | Location |
|------------|-----------|---------|----------|
| **Collusion** | 5+ miners, same reward, score < 0.95 | 0.75 | Lines 479-486 |
| **Name Similarity (Strict)** | Overlap > 0.75 OR Jaccard > 0.70 | 0.0-1.0 (scaled) | Lines 488-510 |
| **Name Similarity (Near)** | Overlap > 0.80 OR Jaccard > 0.70 | 0.0-1.0 (scaled) | Lines 488-510 |
| **Signature Match** | Exact same signature | 0.8 | Lines 512-523 |
| **Cross-Group Name** | Overlap > 0.95 OR Jaccard > 0.90 | 0.5 | Lines 530-552 |
| **Address Similarity** | Overlap > 0.8 OR Jaccard > 0.7 | 0.0-0.6 (scaled) | Lines 555-585 |

---

## Key Insights

1. **Order Doesn't Matter**: Addresses and name variations are stored as sets, so order is irrelevant.

2. **Normalization is Aggressive**: 
   - Addresses are normalized to sorted letter strings
   - "56 Rruga Agaveve" and "56, Rruga Agaveve" → same normalized form

3. **Multiple Checks**: The system performs 6 different types of cross-miner checks, each with different thresholds.

4. **Penalties are Cumulative**: Multiple penalties can apply to the same miner (they take the maximum).

5. **Per-Name Comparison**: Address and name similarity are checked **per name**, then averaged.

---

## Example Scenario

**Miner A:**
- Name: "John Smith"
  - Variations: ["John", "Jon", "Jhon"]
  - Addresses: ["123 Main St", "456 Oak Ave", "789 Pine Rd"]

**Miner B:**
- Name: "John Smith"
  - Variations: ["John", "Jon", "Jhon"] (same)
  - Addresses: ["789 Pine Rd", "123 Main St", "456 Oak Ave"] (same, different order)

**Result:**
- Name similarity: Overlap = 1.0, Jaccard = 1.0 → Penalty = 0.5 (cross-group check)
- Address similarity: Overlap = 1.0, Jaccard = 1.0 → Penalty = 0.6 (address check)
- **Total penalty = max(0.5, 0.6) = 0.6**

Both miners are penalized for using identical variations and addresses.

