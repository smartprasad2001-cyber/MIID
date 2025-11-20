#!/usr/bin/env python3
"""
Simple test script to verify Gemini integration locally.
This tests the Gemini API connection and name variation generation
without connecting to the Bittensor network.
"""

import os
import sys
import asyncio
from MIID.protocol import IdentitySynapse

# Try to import google.generativeai
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    print("ERROR: google-generativeai not installed. Run: pip install google-generativeai")
    sys.exit(1)


def test_gemini_connection(api_key: str, model_name: str = "gemini-2.0-flash-exp"):
    """Test basic Gemini API connection."""
    print(f"\n{'='*60}")
    print("Testing Gemini API Connection")
    print(f"{'='*60}")
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        
        # Simple test query
        test_prompt = "Say 'Hello, Gemini is working!' in one sentence."
        print(f"\nSending test query to {model_name}...")
        response = model.generate_content(test_prompt)
        
        print(f"✅ Connection successful!")
        print(f"Response: {response.text}")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False


def test_name_variation(api_key: str, model_name: str = "gemini-2.0-flash-exp"):
    """Test name variation generation similar to what the miner does."""
    print(f"\n{'='*60}")
    print("Testing Name Variation Generation")
    print(f"{'='*60}")
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        
        # Create a prompt similar to what the miner uses
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
        
        print(f"\nGenerating variations for: {test_name}")
        print("Sending request to Gemini...")
        
        response = model.generate_content(
            context_prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=1024,
                temperature=0.7,
            )
        )
        
        print(f"✅ Generation successful!")
        print(f"\nRaw response:")
        print(f"{response.text}")
        print(f"\n{'='*60}")
        return True, response.text
        
    except Exception as e:
        print(f"❌ Generation failed: {str(e)}")
        return False, None


async def test_miner_forward_function(api_key: str, model_name: str = "gemini-2.0-flash-exp"):
    """Test the actual miner forward function in mock mode."""
    print(f"\n{'='*60}")
    print("Testing Miner Forward Function (Mock Mode)")
    print(f"{'='*60}")
    
    try:
        # Import here to avoid issues if not available
        from neurons.miner import Miner
        import bittensor as bt
        
        # Create a mock config
        class MockConfig:
            class neuron:
                llm_provider = "gemini"
                gemini_api_key = api_key
                gemini_model_name = model_name
                model_name = model_name
                ollama_url = "http://127.0.0.1:11434"
            
            class logging:
                logging_dir = "./test_logs"
                debug = True
            
            class wallet:
                name = "test"
                hotkey = "test"
            
            class subtensor:
                network = "mock"
                chain_endpoint = "mock"
            
            class axon:
                port = 8091
            
            netuid = 1
            mock = True
        
        config = MockConfig()
        
        print("\nInitializing miner in mock mode...")
        miner = Miner(config=config)
        
        # Create a test synapse
        test_synapse = IdentitySynapse(
            identity=[["John Smith", "1990-01-01", "123 Main St"]],
            query_template="Generate 5 spelling variations for the name: {name}",
            timeout=60.0
        )
        
        print("\nCalling miner forward function...")
        result = await miner.forward(test_synapse)
        
        print(f"✅ Forward function successful!")
        print(f"\nResult variations:")
        if result.variations:
            for name, variations in result.variations.items():
                print(f"  {name}: {len(variations)} variations")
                for i, var in enumerate(variations[:3], 1):  # Show first 3
                    print(f"    {i}. {var}")
        else:
            print("  No variations returned")
        
        print(f"\n{'='*60}")
        return True
        
    except Exception as e:
        print(f"❌ Forward function test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function."""
    print("\n" + "="*60)
    print("Gemini Integration Local Test")
    print("="*60)
    
    # Get API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        api_key = input("\nEnter your Gemini API key (or set GEMINI_API_KEY env var): ").strip()
        if not api_key:
            print("ERROR: API key is required!")
            sys.exit(1)
    
    # Get model name (optional)
    model_name = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-exp')
    print(f"\nUsing model: {model_name}")
    
    # Test 1: Basic connection
    if not test_gemini_connection(api_key, model_name):
        print("\n❌ Basic connection test failed. Please check your API key.")
        sys.exit(1)
    
    # Test 2: Name variation generation
    success, response = test_name_variation(api_key, model_name)
    if not success:
        print("\n❌ Name variation test failed.")
        sys.exit(1)
    
    # Test 3: Full miner forward function (optional, requires mock setup)
    print("\n" + "="*60)
    run_full_test = input("\nRun full miner forward function test? (y/n): ").strip().lower()
    if run_full_test == 'y':
        try:
            result = asyncio.run(test_miner_forward_function(api_key, model_name))
            if result:
                print("\n✅ All tests passed!")
            else:
                print("\n⚠️  Full test had issues, but basic functionality works.")
        except Exception as e:
            print(f"\n⚠️  Full test failed: {str(e)}")
            print("But basic Gemini connection works! You can proceed with --mock mode.")
    else:
        print("\nSkipping full miner test.")
    
    print("\n" + "="*60)
    print("✅ Local testing complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Run miner in mock mode: python neurons/miner.py --mock --neuron.llm_provider gemini --neuron.gemini_api_key YOUR_KEY")
    print("2. Or set env var: export GEMINI_API_KEY=your_key")
    print("3. Then run: python neurons/miner.py --mock --neuron.llm_provider gemini")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()

