#!/usr/bin/env python3
"""
Test the latest Gemini model and list available models.
"""

import os
import sys

# Set API key
# API key should be set via environment variable: export GEMINI_API_KEY=your_key

def list_available_models():
    """List all available Gemini models."""
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=os.environ['GEMINI_API_KEY'])
        
        print("="*60)
        print("Available Gemini Models")
        print("="*60)
        
        # List models
        models = genai.list_models()
        
        # Filter for generation models
        generation_models = [m for m in models if 'generateContent' in m.supported_generation_methods]
        
        print(f"\nFound {len(generation_models)} generation models:\n")
        
        model_names = []
        for model in generation_models:
            name = model.name.replace('models/', '')
            model_names.append(name)
            print(f"  - {name}")
            if hasattr(model, 'display_name'):
                print(f"    Display Name: {model.display_name}")
        
        print("\n" + "="*60)
        
        # Try to identify the latest models
        latest_models = [m for m in model_names if '3' in m or '2.5' in m or '2.0' in m]
        if latest_models:
            print("\nLatest models (by version):")
            for m in sorted(latest_models, reverse=True):
                print(f"  - {m}")
        
        return model_names
        
    except Exception as e:
        print(f"Error listing models: {str(e)}")
        return []

def test_model(model_name):
    """Test a specific Gemini model."""
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=os.environ['GEMINI_API_KEY'])
        model = genai.GenerativeModel(model_name)
        
        print(f"\n{'='*60}")
        print(f"Testing Model: {model_name}")
        print(f"{'='*60}")
        
        # Test 1: Simple query
        print("\n1. Testing simple query...")
        response = model.generate_content("Say 'Hello, I am working!' in one sentence.")
        print(f"   ✅ Response: {response.text}")
        
        # Test 2: Name variation (what miner does)
        print("\n2. Testing name variation generation...")
        test_name = "John Smith"
        prompt = f"""Generate 5 spelling variations for the name: {test_name}. 
Return only comma-separated names, no numbering or extra text."""
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=512,
                temperature=0.7,
            )
        )
        print(f"   ✅ Variations for {test_name}:")
        print(f"   {response.text}")
        
        # Test 3: Multiple names
        print("\n3. Testing with multiple names...")
        names = ["Maria Garcia", "Ahmed Hassan"]
        for name in names:
            prompt = f"Generate 3 spelling variations for: {name}. Comma-separated only."
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=256,
                    temperature=0.7,
                )
            )
            print(f"   {name}: {response.text[:80]}")
        
        print(f"\n{'='*60}")
        print(f"✅ Model {model_name} is working correctly!")
        print(f"{'='*60}\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error testing {model_name}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function."""
    print("\n" + "="*60)
    print("Testing Latest Gemini Models")
    print("="*60)
    
    # List available models
    models = list_available_models()
    
    if not models:
        print("\n⚠️  Could not list models. Trying common model names...")
        models = [
            'gemini-3-pro',
            'gemini-3-flash',
            'gemini-2.5-flash',
            'gemini-2.0-flash-exp',
            'gemini-1.5-pro',
            'gemini-1.5-flash'
        ]
    
    # Test the latest models first
    test_models = [
        'gemini-3-pro',
        'gemini-3-flash', 
        'gemini-2.5-flash',
        'gemini-2.0-flash-exp'
    ]
    
    print("\n" + "="*60)
    print("Testing Latest Models")
    print("="*60)
    
    working_model = None
    for model_name in test_models:
        try:
            if test_model(model_name):
                working_model = model_name
                print(f"\n✅ Successfully tested: {model_name}")
                break
        except Exception as e:
            print(f"\n⚠️  {model_name} not available: {str(e)}")
            continue
    
    if working_model:
        print("\n" + "="*60)
        print("RECOMMENDATION")
        print("="*60)
        print(f"\n✅ Use model: {working_model}")
        print(f"\nTo use this model in your miner, run:")
        print(f"  python neurons/miner.py \\")
        print(f"    --netuid 322 \\")
        print(f"    --subtensor.network test \\")
        print(f"    --wallet.name abc \\")
        print(f"    --wallet.hotkey abc \\")
        print(f"    --neuron.llm_provider gemini \\")
        print(f"    --neuron.gemini_api_key YOUR_API_KEY \\")
        print(f"    --neuron.gemini_model_name {working_model} \\")
        print(f"    --logging.debug")
        print("="*60 + "\n")
    else:
        print("\n⚠️  Could not find a working latest model. Using default: gemini-2.0-flash-exp")
    
    return working_model or 'gemini-2.0-flash-exp'

if __name__ == "__main__":
    latest_model = main()
    sys.exit(0)

