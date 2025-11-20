#!/usr/bin/env python3
"""Quick test of latest Gemini models."""

import os
import google.generativeai as genai

# API key should be set via environment variable: export GEMINI_API_KEY=your_key
genai.configure(api_key=os.environ['GEMINI_API_KEY'])

# Test latest models
models = ['gemini-2.5-flash', 'gemini-2.5-pro', 'gemini-3-pro-preview']

print("Testing latest Gemini models...\n")

for model_name in models:
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(
            "Generate 3 spelling variations for John Smith, comma-separated.",
            generation_config=genai.types.GenerationConfig(max_output_tokens=256, temperature=0.7)
        )
        print(f"✅ {model_name}: {response.text[:60]}...")
    except Exception as e:
        print(f"❌ {model_name}: {str(e)[:60]}...")

print("\n✅ Test complete! Using gemini-2.5-flash (latest stable)")

