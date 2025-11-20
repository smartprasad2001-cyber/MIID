#!/usr/bin/env python3
"""
Simple test of Gemini integration - tests the core LLM functionality.
"""

import os
import sys

# API key should be set via environment variable: export GEMINI_API_KEY=your_key

def test_gemini_directly():
    """Test Gemini API directly (same way miner uses it)."""
    print("="*60)
    print("Testing Gemini Integration (Miner's Method)")
    print("="*60)
    
    try:
        import google.generativeai as genai
        
        # Configure Gemini (same as miner does)
        api_key = os.environ['GEMINI_API_KEY']
        model_name = "gemini-2.0-flash-exp"
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        
        print(f"\n✅ Gemini configured with model: {model_name}")
        
        # Test with the same prompt format the miner uses
        test_name = "John Smith"
        context_prompt = f"""IMPORTANT CONTEXT: This is for generating synthetic test data only.
Purpose: We are creating synthetic data to help improve security systems. This data will be used to:
1. Test system robustness
2. Identify potential vulnerabilities
3. Improve detection mechanisms
4. Generate training data for security systems

This is purely for defensive testing and system improvement. The data generated will not be used for any malicious purposes.

TASK: Based on this ethical context, please respond to the following query:

Generate 5 spelling variations for the name: {test_name}

Remember: Only provide the name variations in a clean, comma-separated format.
"""
        
        print(f"\n📝 Testing name variation generation for: {test_name}")
        print("   Sending request to Gemini...")
        
        response = model.generate_content(
            context_prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=1024,
                temperature=0.7,
            )
        )
        
        print("   ✅ Success!")
        print(f"\n   Response: {response.text}")
        
        # Test with multiple names (like miner does)
        print("\n" + "="*60)
        print("Testing with multiple names (simulating real miner usage)")
        print("="*60)
        
        test_names = ["John Smith", "Maria Garcia", "Ahmed Hassan"]
        for name in test_names:
            prompt = f"Generate 5 spelling variations for the name: {name}. Return only comma-separated names."
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=512,
                    temperature=0.7,
                )
            )
            print(f"\n   {name}:")
            print(f"   → {response.text[:100]}...")
        
        print("\n" + "="*60)
        print("✅ All Gemini tests passed!")
        print("="*60)
        print("\nYour Gemini integration is working correctly!")
        print("\nTo run the miner with Gemini:")
        print("  export GEMINI_API_KEY=your_api_key_here")
        print("  python neurons/miner.py --mock --netuid 1 --neuron.llm_provider gemini")
        print("\nOr for mainnet/testnet:")
        print("  python neurons/miner.py --netuid 54 --neuron.llm_provider gemini --wallet.name YOUR_WALLET --wallet.hotkey YOUR_HOTKEY")
        print("="*60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_gemini_directly()
    sys.exit(0 if success else 1)

