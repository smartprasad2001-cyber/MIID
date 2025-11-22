# How to Run Gemini Integration Tests

## Quick Start

Run the full test (recommended):
```bash
python3 test_gemini_full.py
```

## Test Options

### Option 1: Full Test (Recommended)
```bash
python3 test_gemini_full.py
```
- Runs all tests automatically
- Includes actual Gemini API calls
- Shows generated variations
- No user input required

### Option 2: Interactive Test
```bash
python3 test_gemini_integration.py
```
- Runs basic tests automatically
- Asks if you want to run full generation test
- Type 'y' to run full generation, 'n' to skip

## Prerequisites

1. **Set Gemini API Key:**
   ```bash
   export GEMINI_API_KEY=your_api_key_here
   ```
   
   Or add to `~/.zshrc` or `~/.bashrc`:
   ```bash
   echo 'export GEMINI_API_KEY=your_api_key_here' >> ~/.zshrc
   source ~/.zshrc
   ```

2. **Install dependencies:**
   ```bash
   pip install google-generativeai
   ```

## What the Tests Do

1. **API Key Check** - Verifies GEMINI_API_KEY is set
2. **Query Parsing** - Tests parsing of validator query templates
3. **Prompt Generation** - Tests building comprehensive Gemini prompts
4. **Gemini Connection** - Tests API connectivity
5. **Full Generation** - Tests actual variation generation (uses API quota)

## Expected Output

When successful, you should see:
```
✅ GEMINI_API_KEY is set
✅ Parsed: 5 variations
✅ Generated prompt (3520 characters)
✅ GENERATION SUCCESSFUL!

📝 John Smith: 5 variations
   1. Name: Jon Smith
      DOB:  1991-01-14
      Addr: 456 Oak Ave, New York, NY 10002, USA
   ...
```

## Troubleshooting

**If API key is not set:**
```bash
export GEMINI_API_KEY=your_key_here
```

**If google-generativeai is not installed:**
```bash
pip install google-generativeai
```

**If you get connection errors:**
- Check your internet connection
- Verify the API key is correct
- Check if you have API quota remaining

