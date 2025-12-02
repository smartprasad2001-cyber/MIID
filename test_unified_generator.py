#!/usr/bin/env python3
"""
Test the unified generator alone - generate names and DOBs
"""

import os
import sys
import logging

# Suppress bittensor argument parsing
_saved_argv = sys.argv
sys.argv = [sys.argv[0]]

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'MIID', 'validator'))

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    print("ERROR: google-generativeai not installed")
    GEMINI_AVAILABLE = False
    sys.exit(1)

sys.argv = _saved_argv

# Import the generator
from test_complete_scoring import UnifiedGenerator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

def main():
    """Test unified generator"""
    logger.info("="*80)
    logger.info("TESTING UNIFIED GENERATOR")
    logger.info("="*80)
    
    # Check API key
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        logger.error("GEMINI_API_KEY environment variable not set")
        return
    
    # Create generator
    generator = UnifiedGenerator(logger=logger)
    
    # Test names
    seed_names = ["John Smith", "Maria Garcia", "Ahmed Hassan"]
    
    logger.info("\n" + "="*80)
    logger.info("TESTING NAME GENERATION")
    logger.info("="*80)
    
    all_name_variations = {}
    for seed_name in seed_names:
        logger.info(f"\nGenerating variations for: {seed_name}")
        name_vars = generator.generate_name_variations(seed_name, 10)
        all_name_variations[seed_name] = name_vars
        
        logger.info(f"✅ Generated {len(name_vars)} variations:")
        for i, var in enumerate(name_vars, 1):
            logger.info(f"  {i}. {var}")
    
    # Test DOBs
    seed_dobs = ["1990-01-15", "1985-06-22", "1992-11-08"]
    
    logger.info("\n" + "="*80)
    logger.info("TESTING DOB GENERATION")
    logger.info("="*80)
    
    all_dob_variations = {}
    for seed_dob in seed_dobs:
        logger.info(f"\nGenerating variations for: {seed_dob}")
        dob_vars = generator.generate_dob_variations(seed_dob, 10)
        all_dob_variations[seed_dob] = dob_vars
        
        logger.info(f"✅ Generated {len(dob_vars)} variations:")
        for i, var in enumerate(dob_vars, 1):
            logger.info(f"  {i}. {var}")
    
    # Summary
    logger.info("\n" + "="*80)
    logger.info("SUMMARY")
    logger.info("="*80)
    logger.info(f"Names tested: {len(seed_names)}")
    logger.info(f"DOBs tested: {len(seed_dobs)}")
    logger.info(f"Total name variations: {sum(len(v) for v in all_name_variations.values())}")
    logger.info(f"Total DOB variations: {sum(len(v) for v in all_dob_variations.values())}")
    logger.info("="*80)

if __name__ == "__main__":
    main()

