#!/usr/bin/env python3
"""
Test script to verify Gemini integration for miner variations.

This script tests:
1. Gemini API key is set
2. Gemini connection works
3. Query template parsing works
4. Gemini prompt generation works
5. Gemini can generate variations (optional - uses API quota)
"""

import os
import json
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from MIID.validator.gemini_generator import (
    parse_query_template_for_gemini,
    build_gemini_prompt,
    generate_variations_with_gemini
)
from MIID.protocol import IdentitySynapse

def test_api_key():
    """Test if API key is set."""
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        print(f"✅ GEMINI_API_KEY is set (length: {len(api_key)} chars)")
        print(f"   Key starts with: {api_key[:10]}...")
        return True
    else:
        print("❌ GEMINI_API_KEY is not set")
        print("   Set it with: export GEMINI_API_KEY=your_key")
        return False

def test_query_parsing():
    """Test query template parsing."""
    print("\n" + "="*80)
    print("Testing Query Template Parsing")
    print("="*80)
    
    # Example query template
    query_template = """
    Generate 15 variations for the name {name}.
    
    Approximately 24% of variations should follow these rules:
    - Replace spaces with special characters
    
    Phonetic similarity distribution:
    - Light: 40%
    - Medium: 35%
    - Far: 25%
    
    Orthographic similarity distribution:
    - Light: 30%
    - Medium: 40%
    - Far: 30%
    """
    
    requirements = parse_query_template_for_gemini(query_template)
    
    print(f"\n📋 Parsed Requirements:")
    print(f"   Variation count: {requirements['variation_count']}")
    print(f"   Rule percentage: {requirements['rule_percentage']*100:.0f}%")
    print(f"   Rules: {requirements['rules']}")
    print(f"   Phonetic similarity: {requirements.get('phonetic_similarity', {})}")
    print(f"   Orthographic similarity: {requirements.get('orthographic_similarity', {})}")
    
    assert requirements['variation_count'] == 15, "Variation count should be 15"
    assert requirements['rule_percentage'] == 0.24, "Rule percentage should be 24%"
    assert 'replace_spaces_with_special_characters' in requirements['rules'], "Should have replace_spaces rule"
    
    print("✅ Query template parsing works correctly!")
    return True

def test_prompt_generation():
    """Test Gemini prompt generation."""
    print("\n" + "="*80)
    print("Testing Gemini Prompt Generation")
    print("="*80)
    
    requirements = {
        'variation_count': 15,
        'rule_percentage': 0.24,
        'rules': ['replace_spaces_with_special_characters'],
        'phonetic_similarity': {'Light': 0.40, 'Medium': 0.35, 'Far': 0.25},
        'orthographic_similarity': {'Light': 0.30, 'Medium': 0.40, 'Far': 0.30},
        'uav_seed_name': None
    }
    
    prompt = build_gemini_prompt(
        name="John Smith",
        dob="1990-01-15",
        address="123 Main St, New York, NY 10001, USA",
        requirements=requirements,
        is_uav_seed=False
    )
    
    print(f"\n📝 Generated Prompt (first 500 chars):")
    print(prompt[:500] + "...")
    print(f"\n   Full prompt length: {len(prompt)} characters")
    
    # Check key elements
    assert "John Smith" in prompt, "Should contain original name"
    assert "15 variations" in prompt or "EXACTLY 15" in prompt, "Should specify variation count"
    assert "phonetic" in prompt.lower(), "Should mention phonetic similarity"
    assert "orthographic" in prompt.lower(), "Should mention orthographic similarity"
    assert "JSON" in prompt, "Should specify JSON output format"
    
    print("✅ Prompt generation works correctly!")
    return True

def test_gemini_connection():
    """Test Gemini API connection."""
    print("\n" + "="*80)
    print("Testing Gemini API Connection")
    print("="*80)
    
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("❌ GEMINI_API_KEY not set")
            return False
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        
        # Simple test query
        response = model.generate_content(
            "Say 'Hello, Gemini integration works!'",
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=50,
                temperature=0.1,
            )
        )
        
        print(f"✅ Gemini connection successful!")
        print(f"   Response: {response.text.strip()}")
        return True
        
    except ImportError:
        print("❌ google-generativeai not installed")
        print("   Install with: pip install google-generativeai")
        return False
    except Exception as e:
        print(f"❌ Gemini connection failed: {e}")
        return False

def test_full_generation():
    """Test full variation generation (uses API quota)."""
    print("\n" + "="*80)
    print("Testing Full Variation Generation (uses API quota)")
    print("="*80)
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not set - skipping full test")
        return False
    
    # Create a test synapse
    query_template = """
    Generate 5 variations for the name {name}.
    
    Phonetic similarity distribution:
    - Light: 40%
    - Medium: 35%
    - Far: 25%
    """
    
    synapse = IdentitySynapse(
        identity=[["John Smith", "1990-01-15", "123 Main St, New York, NY 10001, USA"]],
        query_template=query_template,
        timeout=120.0
    )
    
    try:
        print("🔄 Generating variations with Gemini...")
        variations = generate_variations_with_gemini(
            synapse,
            gemini_api_key=api_key,
            gemini_model="gemini-2.0-flash-exp"
        )
        
        print(f"\n✅ Generated variations:")
        for name, var_list in variations.items():
            if isinstance(var_list, dict):
                # UAV structure
                print(f"   {name}: {len(var_list.get('variations', []))} variations + UAV")
                if var_list.get('uav'):
                    print(f"      UAV: {var_list['uav'].get('address', 'N/A')}")
            else:
                print(f"   {name}: {len(var_list)} variations")
                # Show first variation as example
                if var_list:
                    print(f"      Example: {var_list[0]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Full generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("="*80)
    print("Gemini Integration Test Suite")
    print("="*80)
    
    results = []
    
    # Test 1: API Key
    results.append(("API Key Check", test_api_key()))
    
    # Test 2: Query Parsing
    try:
        results.append(("Query Parsing", test_query_parsing()))
    except Exception as e:
        print(f"❌ Query parsing test failed: {e}")
        results.append(("Query Parsing", False))
    
    # Test 3: Prompt Generation
    try:
        results.append(("Prompt Generation", test_prompt_generation()))
    except Exception as e:
        print(f"❌ Prompt generation test failed: {e}")
        results.append(("Prompt Generation", False))
    
    # Test 4: Gemini Connection
    results.append(("Gemini Connection", test_gemini_connection()))
    
    # Test 5: Full Generation (optional - uses quota)
    print("\n" + "="*80)
    response = input("Run full generation test? (uses API quota) [y/N]: ").strip().lower()
    if response == 'y':
        results.append(("Full Generation", test_full_generation()))
    else:
        print("⏭️  Skipping full generation test")
        results.append(("Full Generation", None))
    
    # Summary
    print("\n" + "="*80)
    print("Test Summary")
    print("="*80)
    for test_name, result in results:
        if result is None:
            status = "⏭️  SKIPPED"
        elif result:
            status = "✅ PASSED"
        else:
            status = "❌ FAILED"
        print(f"   {test_name}: {status}")
    
    all_passed = all(r for r in results if r is not None)
    if all_passed:
        print("\n🎉 All tests passed! Gemini integration is ready to use.")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")

if __name__ == "__main__":
    main()

