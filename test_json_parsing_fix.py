#!/usr/bin/env python3
"""
Test improved JSON parsing for Gemini responses with explanatory text
"""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from MIID.validator.gemini_generator import generate_variations_with_gemini
from MIID.protocol import IdentitySynapse

def test_json_parsing_with_explanatory_text():
    """Test JSON parsing when Gemini includes explanatory text."""
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY environment variable not set")
        print("   Set it with: export GEMINI_API_KEY=your_key")
        sys.exit(1)
    
    print("="*80)
    print("TESTING IMPROVED JSON PARSING")
    print("="*80)
    print()
    
    # Test with Russian name that previously failed
    identity = [
        ["Виктория Родина", "1989-10-29", "Russia"]
    ]
    
    query_template = """Generate 7 variations of {name}. Ensure phonetic similarity is reflected in 70% of the variations using light-sound-alike transformations, and in 30% using medium-sound-alike transformations. Also ensure orthographic similarity by making 20% of the variations visually similar to the original name with light changes, 60% with medium changes, and 20% with far changes. Approximately 45% of the total 7 variations should follow these rule-based transformations: Additionally, generate variations that perform these transformations: Delete a random letter, and Replace random consonants with different consonants. The following address is the seed country/city to generate address variations for: {address}. Generate unique real addresses within the specified country/city for each variation.  The following date of birth is the seed DOB to generate variations for: {dob}."""
    
    synapse = IdentitySynapse(
        identity=identity,
        query_template=query_template,
        timeout=360.0
    )
    
    print("🔄 Testing with Russian name (previously failed)...")
    print()
    
    try:
        variations = generate_variations_with_gemini(
            synapse,
            gemini_api_key=api_key,
            gemini_model="gemini-2.5-flash-lite"
        )
        
        print("✅ Generation complete")
        print()
        
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Verify results
    print("="*80)
    print("RESULTS VERIFICATION")
    print("="*80)
    print()
    
    name = "Виктория Родина"
    if name not in variations:
        print(f"❌ {name}: Missing")
        return
    
    data = variations[name]
    print(f"✅ {name}:")
    print(f"   Type: {type(data).__name__}")
    
    if isinstance(data, list):
        print(f"   Format: Standard (List[List[str]])")
        print(f"   Variations: {len(data)}")
        if len(data) > 0:
            print(f"   First variation: {data[0]}")
    else:
        print(f"   ⚠️  Unexpected format: {type(data)}")
    
    print()
    print("="*80)
    print("✅ TEST COMPLETE")
    print("="*80)
    
    # Save results
    with open("test_json_parsing_fix_results.json", "w", encoding="utf-8") as f:
        json.dump(variations, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved to: test_json_parsing_fix_results.json")

if __name__ == "__main__":
    test_json_parsing_with_explanatory_text()

