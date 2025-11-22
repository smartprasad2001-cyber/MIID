# Why There Are Warnings About UAV Format

## The Issue

You're seeing warnings like:
```
WARNING | Gemini returned UAV format for non-UAV seed 'Gregory Dimitry'. Extracting variations only.
```

## Why This Happens

1. **Query Template Contains UAV Instructions**: The validator's query template includes UAV requirements that mention the UAV format structure. Gemini sees this format example and sometimes applies it to ALL seeds, not just the UAV seed.

2. **Gemini's Behavior**: Gemini models can be overly helpful - when they see a format example in the instructions, they sometimes apply it universally, even when told it's only for specific cases.

3. **Not Actually a Problem**: The code correctly handles this by:
   - Detecting when Gemini returns UAV format for non-UAV seeds
   - Extracting only the `variations` list from the UAV structure
   - Converting it to the standard format (list of arrays)
   - The miner still works correctly!

## The Fix

I've made three improvements:

### 1. Changed Log Level from WARNING to DEBUG
```python
# Before:
bt.logging.warning(f"Gemini returned UAV format for non-UAV seed '{name}'. Extracting variations only.")

# After:
bt.logging.debug(f"Gemini returned UAV format for non-UAV seed '{name}'. Extracting variations only.")
```

**Why**: This is not an error - the code handles it correctly. It's just informational, so DEBUG level is more appropriate.

### 2. Made UAV Instructions More Explicit
```python
uav_instructions = f"""
UAV REQUIREMENTS (Phase 3) - CRITICAL - FOR THIS SEED ONLY:
⚠️  IMPORTANT: This seed "{name}" is the ONLY seed that requires UAV format. 
All other seeds use standard format.
...
"""
```

**Why**: Makes it crystal clear that UAV format is ONLY for the specific seed.

### 3. Added Explicit "Don't Use UAV" Instructions for Non-UAV Seeds
```python
output_format = """
...
- ⚠️  CRITICAL: Use STANDARD format (list of arrays), NOT UAV format with {"variations": ..., "uav": ...}
- ⚠️  UAV format is ONLY for the specific UAV seed mentioned in query template - this is NOT that seed
"""
```

**Why**: Explicitly tells Gemini NOT to use UAV format for non-UAV seeds.

## Results

- ✅ **Before**: Warnings appeared for every non-UAV seed
- ✅ **After**: 
  - Warnings changed to DEBUG level (won't show in normal operation)
  - More explicit instructions to prevent the issue
  - Code still handles it correctly if it happens

## Summary

**The warnings are harmless** - the code correctly extracts variations from UAV format when Gemini returns it for non-UAV seeds. The fixes:
1. Reduce log noise (DEBUG instead of WARNING)
2. Make instructions clearer to prevent the issue
3. Ensure correct behavior regardless

The miner works correctly either way! 🎉

