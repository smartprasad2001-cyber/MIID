# Mainnet Readiness Checklist - Gemini Integration

## Scoring Components Verification

### 1. NAME QUALITY SCORING (20% weight)

#### ✅ Similarity Score (60% of name quality)
- **Phonetic Similarity**: ⚠️ Needs improvement
  - Current: ~0.19-0.32
  - Target: Match distribution exactly
  - Status: Prompt updated with phonetic algorithm guidance
  - Action: Test and refine based on actual validator behavior

- **Orthographic Similarity**: ⚠️ Needs improvement
  - Current: ~0.14-0.85
  - Target: Match distribution exactly
  - Status: Prompt updated with Levenshtein distance calculations
  - Action: Ensure variations fall into correct distance ranges

#### ✅ Count Score (15% of name quality)
- **Status**: ✅ PERFECT (0.993-1.0)
- **Action**: No changes needed

#### ✅ Uniqueness Score (10% of name quality)
- **Current**: ~0.60
- **Target**: 1.0
- **Status**: Prompt emphasizes uniqueness requirements
- **Action**: Ensure variations have combined similarity < 0.99

#### ✅ Length Score (15% of name quality)
- **Current**: ~0.73
- **Target**: 1.0
- **Status**: Prompt specifies 60-140% range
- **Action**: Verify all variations are within range

#### ⚠️ Rule Compliance Score (20% of name quality)
- **Current**: 0.0 ❌
- **Target**: 1.0
- **Status**: Prompt updated with explicit rule instructions
- **Action**: CRITICAL - Must apply rules to specified count

### 2. ADDRESS SCORING (70% weight)

#### ✅ Looks Like Address (Format Validation)
- **Status**: ✅ PERFECT (0.647-1.0)
- **Action**: No changes needed

#### ⚠️ Address Region Match
- **Current**: 0.0 (validator bug)
- **Status**: Identified as validator-side issue
- **Action**: Monitor validator fix, but not a Gemini issue

#### ✅ Address API Call
- **Status**: ✅ EXCELLENT (0.9-1.0 when passing)
- **Action**: No changes needed

### 3. DOB SCORING (10% weight)

#### ✅ DOB Score
- **Status**: ✅ PERFECT (0.778-1.0)
- **Action**: No changes needed

### 4. COMPLETENESS MULTIPLIER

#### ✅ Extra Names Penalty
- **How it works**: Penalty for variations beyond requested count
- **Status**: ✅ Covered - Gemini generates exact count
- **Action**: No changes needed

#### ✅ Missing Names Penalty
- **How it works**: 20% penalty per missing name (up to 90% max)
- **Status**: ✅ Covered - Gemini generates for all seed names
- **Action**: Verify all seed names have variations

### 5. PENALTIES (Applied after scoring)

#### ✅ Post Penalty
- **How it works**: Penalty for post-processing issues
- **Status**: ✅ Covered - Output is clean JSON
- **Action**: Ensure JSON parsing is robust

#### ✅ Address Penalty
- **How it works**: Penalty for address-related issues
- **Status**: ✅ Covered - Addresses pass format validation
- **Action**: Monitor for any address validation failures

#### ✅ Collusion Penalty
- **How it works**: Detects if miners have similar responses
- **Status**: ✅ Covered - Gemini generates unique variations
- **Action**: Ensure variations are sufficiently diverse

#### ✅ Duplication Penalty
- **How it works**: Penalty for duplicate variations within miner
- **Status**: ✅ Covered - Prompt emphasizes uniqueness
- **Action**: Verify no duplicate variations

#### ✅ Signature Copy Penalty
- **How it works**: Penalty for exact copies of seed names
- **Status**: ✅ Covered - Gemini generates variations, not copies
- **Action**: Ensure no exact seed name copies

#### ✅ Special Chars Penalty
- **How it works**: Penalty for excessive special characters
- **Status**: ⚠️ Needs verification
- **Action**: Ensure special chars only in rule-compliant variations

## Critical Issues to Fix Before Mainnet

### 🔴 HIGH PRIORITY

1. **Rule Compliance (20% weight)**: Currently 0.0
   - **Impact**: Loses 20% of name quality score
   - **Fix**: Ensure rules are explicitly applied to specified count
   - **Status**: Prompt updated, needs testing

2. **Similarity Distribution (60% weight)**: Currently ~0.35
   - **Impact**: Biggest component of name quality
   - **Fix**: Improve distribution matching
   - **Status**: Prompt updated, needs iterative refinement

### 🟡 MEDIUM PRIORITY

3. **Uniqueness (10% weight)**: Currently ~0.60
   - **Impact**: Moderate impact on score
   - **Fix**: Ensure variations are more diverse
   - **Status**: Prompt emphasizes uniqueness

4. **Length (15% weight)**: Currently ~0.73
   - **Impact**: Moderate impact on score
   - **Fix**: Verify all variations in 60-140% range
   - **Status**: Prompt specifies range

### 🟢 LOW PRIORITY

5. **Region Validation**: Currently 0.0 (validator bug)
   - **Impact**: Affects all miners, not just Gemini
   - **Fix**: Wait for validator fix
   - **Status**: Documented, not a Gemini issue

## Testing Checklist

### Pre-Mainnet Tests

- [ ] Test with multiple seed names (single and multi-part)
- [ ] Test with different similarity distributions
- [ ] Test with different rule requirements
- [ ] Test with different variation counts
- [ ] Test with different countries/cities for addresses
- [ ] Test with different DOB formats
- [ ] Test edge cases (very short names, very long names)
- [ ] Test with special characters in rules
- [ ] Test uniqueness (no duplicates)
- [ ] Test length compliance (all in 60-140% range)
- [ ] Test rule compliance (rules applied correctly)
- [ ] Test address format (all pass validation)
- [ ] Test address API (geocodable addresses)
- [ ] Test DOB categories (all 6 categories covered)
- [ ] Test completeness (all seed names have variations)
- [ ] Test JSON output (valid, parseable)
- [ ] Test penalty avoidance (no collusion, duplication, etc.)

## Expected Scores After Fixes

### Optimistic Scenario
- Similarity: 0.90 (60% weight) = 0.54
- Count: 1.0 (15% weight) = 0.15
- Uniqueness: 0.95 (10% weight) = 0.095
- Length: 0.95 (15% weight) = 0.1425
- Rules: 0.90 (20% weight) = 0.18
- **Name Quality**: ~1.11 (capped at 1.0)

- Address: 0.90 (70% weight) = 0.63
- DOB: 1.0 (10% weight) = 0.10
- **Identity Quality**: 0.83

- Completeness: 0.95
- **Final Score**: ~0.79

### Realistic Scenario
- Similarity: 0.70 (60% weight) = 0.42
- Count: 1.0 (15% weight) = 0.15
- Uniqueness: 0.80 (10% weight) = 0.08
- Length: 0.85 (15% weight) = 0.1275
- Rules: 0.70 (20% weight) = 0.14
- **Name Quality**: ~0.92

- Address: 0.85 (70% weight) = 0.595
- DOB: 1.0 (10% weight) = 0.10
- **Identity Quality**: ~0.72

- Completeness: 0.90
- **Final Score**: ~0.65

## Recommendations

1. **Before Mainnet**:
   - Fix rule compliance (critical - 20% weight)
   - Improve similarity distribution matching
   - Test extensively with various scenarios
   - Monitor for any penalty triggers

2. **Post-Mainnet**:
   - Monitor actual scores
   - Iteratively refine prompt based on results
   - Adjust for validator behavior patterns
   - Optimize for maximum scores

3. **Ongoing**:
   - Track penalty rates
   - Monitor address API success rates
   - Track similarity distribution accuracy
   - Ensure rule compliance

## Status Summary

| Component | Status | Score | Priority |
|-----------|--------|-------|----------|
| Count | ✅ Perfect | 1.0 | ✅ |
| Address Format | ✅ Perfect | 1.0 | ✅ |
| DOB Categories | ✅ Perfect | 1.0 | ✅ |
| Address API | ✅ Excellent | 0.9-1.0 | ✅ |
| Similarity | ⚠️ Needs Work | 0.35 | 🔴 |
| Uniqueness | ⚠️ Needs Work | 0.60 | 🟡 |
| Length | ⚠️ Needs Work | 0.73 | 🟡 |
| Rules | ❌ Critical | 0.0 | 🔴 |
| Region Match | ⚠️ Validator Bug | 0.0 | 🟢 |
| Penalties | ✅ Covered | 0.0 | ✅ |

**Overall Readiness**: ⚠️ **NOT READY** - Need to fix rule compliance and improve similarity before mainnet.

