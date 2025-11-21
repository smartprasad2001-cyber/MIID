# End-to-End Flow: Validator Request → Miner Response

## Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    1. VALIDATOR SENDS REQUEST                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
         ┌─────────────────────────────────────┐
         │  IdentitySynapse Object:            │
         │  {                                  │
         │    identity: [                      │
         │      ["John Doe", "1990-05-15",     │
         │       "New York, USA"],             │
         │      ["Sarah Smith", "1985-03-20",  │
         │       "Los Angeles, USA"]           │
         │    ],                               │
         │    query_template: "...",           │
         │    timeout: 360.0,                  │
         │    variations: null                 │
         │  }                                  │
         └─────────────────────────────────────┘
                              │
                              ▼ (Bittensor Network)
┌─────────────────────────────────────────────────────────────────┐
│                  2. MINER RECEIVES REQUEST                       │
│                      neurons/miner.py                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
         ┌─────────────────────────────────────┐
         │  async def forward(synapse):        │
         │    - Validate validator             │
         │    - Log request details            │
         │    - Route to clean generator       │
         └─────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│             3. ROUTE TO VARIATION GENERATOR                      │
│              variation_generator_clean.py                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
         ┌─────────────────────────────────────┐
         │  def generate_variations(synapse):  │
         │    - Parse query template           │
         │    - Extract requirements           │
         └─────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   4. PARSE QUERY TEMPLATE                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
         ┌─────────────────────────────────────┐
         │  Requirements Extracted:            │
         │  - variation_count: 15              │
         │  - rule_percentage: 45%             │
         │  - rules: [                         │
         │      'replace_spaces_with_...',     │
         │      'delete_random_letter'         │
         │    ]                                │
         │  - phonetic_similarity: Medium      │
         │  - orthographic_similarity: Medium  │
         └─────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│             5. GENERATE VARIATIONS (For Each Name)               │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┴─────────────────────┐
        │                                           │
        ▼                                           ▼
┌──────────────────┐                    ┌──────────────────┐
│ A. NAME VARS     │                    │ B. DOB VARS      │
│                  │                    │                  │
│ Rule-based (6):  │                    │ ±1, ±3, ±30,    │
│ - John_Doe       │                    │ ±90, ±365 days  │
│ - ohn Doe        │                    │ Year+month only │
│ ...              │                    │ Random fills    │
│                  │                    │                  │
│ Non-rule (9):    │                    │ Total: 15       │
│ - Jon Doe        │                    └──────────────────┘
│ - Johhn Doe      │
│ ...              │                              │
│ (name_variations │                              │
│  .py algorithm)  │                              │
│                  │                              │
│ Total: 15        │                              │
└──────────────────┘                              │
        │                                           │
        └──────────────────┬───────────────────────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │ C. ADDRESS VARS  │
                  │                  │
                  │ Random streets   │
                  │ Same city/country│
                  │ Unique addresses │
                  │                  │
                  │ Total: 15        │
                  └──────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                  6. COMBINE INTO FORMAT                          │
└─────────────────────────────────────────────────────────────────┘
                           │
                           ▼
         ┌─────────────────────────────────────┐
         │  Combined Variations:               │
         │  {                                  │
         │    "John Doe": [                    │
         │      ["John_Doe", "1990-05-16",     │
         │       "123 Main St, New York..."],  │
         │      ["ohn Doe", "1990-05-14",      │
         │       "456 Oak Ave, New York..."],  │
         │      ... (15 total)                 │
         │    ],                                │
         │    "Sarah Smith": [                 │
         │      ... (15 total)                 │
         │    ]                                │
         │  }                                  │
         └─────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   7. RETURN TO MINER                             │
│                  neurons/miner.py                                │
└─────────────────────────────────────────────────────────────────┘
                           │
                           ▼
         ┌─────────────────────────────────────┐
         │  synapse.variations = variations    │
         │  synapse.process_time = elapsed     │
         │  return synapse                     │
         └─────────────────────────────────────┘
                           │
                           ▼ (Bittensor Network)
┌─────────────────────────────────────────────────────────────────┐
│                 8. VALIDATOR RECEIVES RESPONSE                   │
└─────────────────────────────────────────────────────────────────┘
                           │
                           ▼
         ┌─────────────────────────────────────┐
         │  Validator Processing:              │
         │  - Score variations (reward.py)     │
         │  - Check quality                    │
         │  - Check uniqueness                 │
         │  - Check rule compliance            │
         │  - Update miner rewards             │
         └─────────────────────────────────────┘
```

## Detailed Step-by-Step

### Step 1: Validator Creates Request
```python
# Validator creates IdentitySynapse
synapse = IdentitySynapse(
    identity=[
        ["John Doe", "1990-05-15", "New York, USA"],
        ["Sarah Smith", "1985-03-20", "Los Angeles, USA"]
    ],
    query_template="Generate 15 variations...",
    timeout=360.0,
    variations=None  # Empty - miner fills this
)
```

### Step 2: Miner Receives via Bittensor
```python
# neurons/miner.py
async def forward(self, synapse: IdentitySynapse):
    # Validate validator (whitelist check)
    # Log request
    # Route to clean generator
    variations = generate_variations_clean(synapse)
    synapse.variations = variations
    return synapse
```

### Step 3: Clean Generator Processes
```python
# variation_generator_clean.py
def generate_variations(synapse):
    # Parse query template
    requirements = parse_query_template(synapse.query_template)
    
    # For each identity
    for identity in synapse.identity:
        name, dob, address = identity[0], identity[1], identity[2]
        
        # Generate variations
        name_vars = generate_name_variations_clean(...)
        dob_vars = generate_dob_variations(...)
        address_vars = generate_address_variations(...)
        
        # Combine: [name_var, dob_var, address_var]
        combined = [[nv, dv, av] for nv, dv, av in zip(name_vars, dob_vars, address_vars)]
        all_variations[name] = combined
    
    return all_variations  # Dict[str, List[List[str]]]
```

### Step 4: Algorithm Details

**Name Variations:**
- **Rule-based (45%)**: Uses rule functions (replace spaces, delete letter, etc.)
- **Non-rule (55%)**: Uses `name_variations.py` - simple transformation algorithm

**DOB Variations:**
- Covers all required categories: ±1, ±3, ±30, ±90, ±365 days, year+month
- Random variations to fill count

**Address Variations:**
- Random street numbers and names
- Maintains same city/country
- Ensures uniqueness

### Step 5: Response Format
```python
{
    "John Doe": [
        ["John_Doe", "1990-05-16", "123 Main St, New York, USA"],
        ["ohn Doe", "1990-05-14", "456 Oak Ave, New York, USA"],
        # ... 15 total
    ],
    "Sarah Smith": [
        # ... 15 total
    ]
}
```

### Step 6: Validator Scores
- Validator receives `synapse.variations`
- Runs through `reward.py` scoring logic
- Updates miner rewards based on quality

## Key Technologies Used

✅ **Bittensor Network**: Validator ↔ Miner communication
✅ **variation_generator_clean.py**: Main variation generation logic
✅ **name_variations.py**: Simple algorithm for non-rule names
✅ **Rule functions**: Apply transformations (spaces, delete letter, etc.)

## What's NOT Used

❌ **Ollama**: Skipped in initialization
❌ **Gemini**: Skipped in initialization
❌ **LLM APIs**: No external API calls needed
❌ **Complex algorithms**: Just simple transformations

## Processing Speed

- **Fast**: No LLM API latency
- **Local**: All processing happens locally
- **Efficient**: Simple algorithm execution
- **Scalable**: Can handle many requests quickly

