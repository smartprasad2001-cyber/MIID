#!/usr/bin/env python3
"""
Quick test of miner's Gemini integration without full startup.
"""

import os
import asyncio
import sys

# Set API key
os.environ['GEMINI_API_KEY'] = 'AIzaSyC5bJ82CRL65UqWj4Tx04AmtofX19eRF5o'

async def test_miner_gemini():
    """Test the miner's Get_Respond_LLM method with Gemini."""
    print("="*60)
    print("Testing Miner's Gemini Integration")
    print("="*60)
    
    try:
        # Import miner
        from neurons.miner import Miner
        import bittensor as bt
        import argparse
        
        # Create proper config using the miner's config system
        parser = argparse.ArgumentParser()
        Miner.add_args(parser)
        bt.wallet.add_args(parser)
        bt.subtensor.add_args(parser)
        bt.logging.add_args(parser)
        bt.axon.add_args(parser)
        
        # Set mock mode and Gemini settings
        args = parser.parse_args([
            '--mock',
            '--netuid', '1',
            '--neuron.llm_provider', 'gemini',
            '--neuron.gemini_api_key', os.environ['GEMINI_API_KEY'],
            '--wallet.name', 'test',
            '--wallet.hotkey', 'test',
            '--logging.debug'
        ])
        
        config = Miner.config()
        config.merge(bt.config(parser))
        
        # Override with our args
        config.mock = True
        config.netuid = 1
        config.neuron.llm_provider = "gemini"
        config.neuron.gemini_api_key = os.environ['GEMINI_API_KEY']
        config.wallet.name = "test"
        config.wallet.hotkey = "test"
        
        print("\n1. Initializing miner...")
        miner = Miner(config=config)
        print("   ✅ Miner initialized successfully!")
        
        print("\n2. Testing Get_Respond_LLM with Gemini...")
        test_prompt = "Generate 5 spelling variations for the name: John Smith"
        response = miner.Get_Respond_LLM(test_prompt)
        print("   ✅ LLM query successful!")
        print(f"\n   Response: {response}")
        
        print("\n3. Testing full forward function...")
        from MIID.protocol import IdentitySynapse
        
        synapse = IdentitySynapse(
            identity=[["John Smith", "1990-01-01", "123 Main St"]],
            query_template="Generate 5 spelling variations for the name: {name}",
            timeout=60.0
        )
        
        result = await miner.forward(synapse)
        print("   ✅ Forward function successful!")
        
        if result.variations:
            print(f"\n   Generated variations for {len(result.variations)} name(s):")
            for name, variations in result.variations.items():
                print(f"   - {name}: {len(variations)} variations")
                for i, var in enumerate(variations[:3], 1):
                    print(f"     {i}. {var[0]}")  # Show just the name variation
        else:
            print("   ⚠️  No variations returned")
        
        print("\n" + "="*60)
        print("✅ All tests passed! Gemini integration works!")
        print("="*60)
        print("\nYou can now run the miner with:")
        print("  export GEMINI_API_KEY=AIzaSyC5bJ82CRL65UqWj4Tx04AmtofX19eRF5o")
        print("  python neurons/miner.py --mock --netuid 1 --neuron.llm_provider gemini")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_miner_gemini())
    sys.exit(0 if success else 1)

