#!/usr/bin/env python3
"""
Test the latest available Gemini models.
"""

import os
import sys

os.environ['GEMINI_API_KEY'] = 'AIzaSyC5bJ82CRL65UqWj4Tx04AmtofX19eRF5o'

def test_model(model_name):
    """Test a specific Gemini model."""
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=os.environ['GEMINI_API_KEY'])
        model = genai.GenerativeModel(model_name)
        
        print(f"\n{'='*60}")
        print(f"Testing: {model_name}")
        print(f"{'='*60}")
        
        # Test name variation (what miner does)
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
        
        print(f"✅ Success!")
        print(f"Variations for {test_name}:")
        print(f"  {response.text}")
        
        # Test with another name
        test_name2 = "Maria Garcia"
        prompt2 = f"Generate 3 spelling variations for: {test_name2}. Comma-separated only."
        response2 = model.generate_content(
            prompt2,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=256,
                temperature=0.7,
            )
        )
        print(f"\nVariations for {test_name2}:")
        print(f"  {response2.text}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    """Test latest models."""
    print("\n" + "="*60)
    print("Testing Latest Gemini Models")
    print("="*60)
    
    # Latest models to test
    models_to_test = [
        'gemini-3-pro-preview',  # Latest preview
        'gemini-2.5-pro',        # Latest stable pro
        'gemini-2.5-flash',      # Latest stable flash
    ]
    
    working_models = []
    
    for model_name in models_to_test:
        if test_model(model_name):
            working_models.append(model_name)
            print(f"\n✅ {model_name} is working!")
        else:
            print(f"\n⚠️  {model_name} failed")
        print()
    
    if working_models:
        # Recommend the best one (prefer stable over preview, flash over pro for speed)
        recommended = None
        if 'gemini-2.5-flash' in working_models:
            recommended = 'gemini-2.5-flash'
        elif 'gemini-2.5-pro' in working_models:
            recommended = 'gemini-2.5-pro'
        elif 'gemini-3-pro-preview' in working_models:
            recommended = 'gemini-3-pro-preview'
        
        print("="*60)
        print("RECOMMENDATION")
        print("="*60)
        print(f"\n✅ Recommended model: {recommended}")
        print(f"\nWorking models: {', '.join(working_models)}")
        print(f"\nTo use {recommended} in your miner:")
        print(f"  python neurons/miner.py \\")
        print(f"    --netuid 322 \\")
        print(f"    --subtensor.network test \\")
        print(f"    --wallet.name abc \\")
        print(f"    --wallet.hotkey abc \\")
        print(f"    --neuron.llm_provider gemini \\")
        print(f"    --neuron.gemini_api_key AIzaSyC5bJ82CRL65UqWj4Tx04AmtofX19eRF5o \\")
        print(f"    --neuron.gemini_model_name {recommended} \\")
        print(f"    --logging.debug")
        print("="*60 + "\n")
        
        return recommended
    else:
        print("\n❌ No models worked!")
        return None

if __name__ == "__main__":
    recommended = main()
    sys.exit(0 if recommended else 1)

