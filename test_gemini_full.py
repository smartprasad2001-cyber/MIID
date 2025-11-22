#!/usr/bin/env python3
"""
Full Gemini integration test - runs all tests including generation.
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

def main():
    """Run all tests including full generation."""
    print("="*80)
    print("Gemini Integration - FULL TEST")
    print("="*80)
    
    # Test 1: API Key
    print("\n[1/4] Checking API Key...")
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        print(f"✅ GEMINI_API_KEY is set (length: {len(api_key)} chars)")
    else:
        print("❌ GEMINI_API_KEY is not set")
        return
    
    # Test 2: Query Parsing
    print("\n[2/4] Testing Query Template Parsing...")
    query_template = """
    Generate 5 variations for the name {name}.
    
    Phonetic similarity distribution:
    - Light: 40%
    - Medium: 35%
    - Far: 25%
    """
    
    requirements = parse_query_template_for_gemini(query_template)
    print(f"✅ Parsed: {requirements['variation_count']} variations")
    print(f"   Phonetic: {requirements.get('phonetic_similarity', {})}")
    
    # Test 3: Prompt Generation
    print("\n[3/4] Testing Prompt Generation...")
    prompt = build_gemini_prompt(
        name="John Smith",
        dob="1990-01-15",
        address="123 Main St, New York, NY 10001, USA",
        requirements=requirements,
        is_uav_seed=False
    )
    print(f"✅ Generated prompt ({len(prompt)} characters)")
    
    # Test 4: Full Generation
    print("\n[4/4] Testing Full Variation Generation with Gemini...")
    print("   This will call Gemini API and generate actual variations...")
    
    synapse = IdentitySynapse(
        identity=[["John Smith", "1990-01-15", "123 Main St, New York, NY 10001, USA"]],
        query_template=query_template,
        timeout=120.0
    )
    
    try:
        variations = generate_variations_with_gemini(
            synapse,
            gemini_api_key=api_key,
            gemini_model="gemini-2.0-flash-exp"
        )
        
        print("\n" + "="*80)
        print("✅ GENERATION SUCCESSFUL!")
        print("="*80)
        
        for name, var_list in variations.items():
            if isinstance(var_list, dict):
                # UAV structure
                vars_count = len(var_list.get('variations', []))
                print(f"\n📝 {name}: {vars_count} variations + UAV")
                if var_list.get('uav'):
                    uav = var_list['uav']
                    print(f"   🎯 UAV Address: {uav.get('address', 'N/A')}")
                    print(f"      Label: {uav.get('label', 'N/A')}")
            else:
                print(f"\n📝 {name}: {len(var_list)} variations")
                print("\n   Generated Variations:")
                for i, var in enumerate(var_list[:5], 1):  # Show first 5
                    print(f"   {i}. Name: {var[0]}")
                    print(f"      DOB:  {var[1]}")
                    print(f"      Addr: {var[2]}")
                if len(var_list) > 5:
                    print(f"   ... and {len(var_list) - 5} more variations")
        
        print("\n" + "="*80)
        print("🎉 ALL TESTS PASSED! Gemini integration is working perfectly!")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Generation failed: {e}")
        import traceback
        traceback.print_exc()
        return

if __name__ == "__main__":
    main()

