#!/usr/bin/env python3
"""
Complete Scoring Test with Validator Mock
=========================================

This script:
1. Loads names and DOB from orthographic_15_names_15_variations.json
2. Loads addresses from validated_address_cache_new.json (15 countries, 15 addresses each)
3. Combines them into the proper format
4. Scores with rewards.py using validator mock
5. Displays final score and all detailed metrics
"""

import sys
import os
import json
import random
import logging
from typing import List, Dict, Any, Tuple
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f'test_complete_scoring_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)
logger = logging.getLogger(__name__)

# Add MIID/validator to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'MIID', 'validator'))

# Import rewards
from reward import get_name_variation_rewards
import numpy as np

# Import MockSelf from test_orthographic_scoring
from test_orthographic_scoring import MockSelf

# Import format_detailed_metrics and update it
from test_orthographic_scoring import format_detailed_metrics as format_detailed_metrics_base

def format_detailed_metrics(metrics: Dict[str, Any]) -> str:
    """Format detailed metrics with fix for name_metrics structure"""
    # Fix the Names section to use final_score instead of quality_score
    if "name_metrics" in metrics:
        # Temporarily replace name_metrics to fix the formatting
        original_name_metrics = metrics["name_metrics"]
        fixed_name_metrics = {}
        for name, nm in original_name_metrics.items():
            fixed_nm = nm.copy()
            # Add quality_score if it doesn't exist but final_score does
            if "quality_score" not in fixed_nm and "final_score" in fixed_nm:
                fixed_nm["quality_score"] = fixed_nm["final_score"]
            
            # Fix detailed_metrics structure - extract from first_name and last_name
            if "detailed_metrics" not in fixed_nm:
                # Build detailed_metrics from first_name and last_name metrics
                detailed_metrics = {
                    "similarity": {"phonetic": 0.0, "orthographic": 0.0, "combined": 0.0},
                    "count": {"score": 0.0},
                    "uniqueness": {"score": 0.0},
                    "length": {"score": 0.0}
                }
                
                # Extract from first_name
                if "first_name" in nm and "metrics" in nm["first_name"]:
                    fm = nm["first_name"]["metrics"]
                    if "similarity" in fm:
                        detailed_metrics["similarity"]["phonetic"] = fm["similarity"].get("phonetic", 0.0)
                        detailed_metrics["similarity"]["orthographic"] = fm["similarity"].get("orthographic", 0.0)
                        detailed_metrics["similarity"]["combined"] = fm["similarity"].get("combined", 0.0)
                    if "count" in fm and "score" in fm["count"]:
                        detailed_metrics["count"]["score"] = fm["count"]["score"]
                    if "uniqueness" in fm and "score" in fm["uniqueness"]:
                        detailed_metrics["uniqueness"]["score"] = fm["uniqueness"]["score"]
                    if "length" in fm and "score" in fm["length"]:
                        detailed_metrics["length"]["score"] = fm["length"]["score"]
                
                # Average with last_name if available
                if "last_name" in nm and "metrics" in nm["last_name"]:
                    lm = nm["last_name"]["metrics"]
                    if "similarity" in lm:
                        detailed_metrics["similarity"]["phonetic"] = (
                            detailed_metrics["similarity"]["phonetic"] + lm["similarity"].get("phonetic", 0.0)
                        ) / 2
                        detailed_metrics["similarity"]["orthographic"] = (
                            detailed_metrics["similarity"]["orthographic"] + lm["similarity"].get("orthographic", 0.0)
                        ) / 2
                        detailed_metrics["similarity"]["combined"] = (
                            detailed_metrics["similarity"]["combined"] + lm["similarity"].get("combined", 0.0)
                        ) / 2
                    if "count" in lm and "score" in lm["count"]:
                        detailed_metrics["count"]["score"] = (
                            detailed_metrics["count"]["score"] + lm["count"]["score"]
                        ) / 2
                    if "uniqueness" in lm and "score" in lm["uniqueness"]:
                        detailed_metrics["uniqueness"]["score"] = (
                            detailed_metrics["uniqueness"]["score"] + lm["uniqueness"]["score"]
                        ) / 2
                    if "length" in lm and "score" in lm["length"]:
                        detailed_metrics["length"]["score"] = (
                            detailed_metrics["length"]["score"] + lm["length"]["score"]
                        ) / 2
                
                fixed_nm["detailed_metrics"] = detailed_metrics
            
            fixed_name_metrics[name] = fixed_nm
        metrics["name_metrics"] = fixed_name_metrics
    
    # Use the base formatting function
    return format_detailed_metrics_base(metrics)


def load_orthographic_data(json_file: str) -> Dict[str, Dict[str, Any]]:
    """Load names and DOB variations from orthographic JSON file"""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"✅ Loaded {len(data)} names from {json_file}")
        return data
    except Exception as e:
        logger.error(f"❌ Error loading {json_file}: {e}")
        return {}


def load_address_cache(json_file: str, num_countries: int = 15) -> Dict[str, List[str]]:
    """Load addresses from validated address cache, selecting countries with enough addresses"""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        
        addresses_dict = cache_data.get('addresses', {})
        
        # Filter countries that have at least 15 addresses
        valid_countries = {
            country: addrs for country, addrs in addresses_dict.items()
            if isinstance(addrs, list) and len(addrs) >= 15
        }
        
        logger.info(f"✅ Loaded address cache: {len(addresses_dict)} total countries")
        logger.info(f"   Countries with 15+ addresses: {len(valid_countries)}")
        
        # Select random countries (or first N if less than requested)
        selected_countries = list(valid_countries.keys())[:num_countries]
        
        # Extract 15 addresses from each selected country
        selected_addresses = {}
        for country in selected_countries:
            addrs = valid_countries[country][:15]  # Take first 15
            selected_addresses[country] = addrs
            logger.info(f"   {country}: {len(addrs)} addresses")
        
        logger.info(f"✅ Selected {len(selected_addresses)} countries with addresses")
        return selected_addresses
        
    except Exception as e:
        logger.error(f"❌ Error loading {json_file}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {}


def combine_data_for_rewards(
    orthographic_data: Dict[str, Dict[str, Any]],
    address_cache: Dict[str, List[str]]
) -> Tuple[List[str], List[str], List[str], Dict[str, List[List[str]]]]:
    """
    Combine orthographic names/DOB with addresses for rewards.py format.
    
    Returns:
        (seed_names, seed_dob, seed_addresses, responses)
    """
    seed_names = []
    seed_dob = []
    seed_addresses = []
    responses = {}  # {name: [[name_var, dob_var, address_var], ...]}
    
    # Get list of countries with addresses
    countries = list(address_cache.keys())
    
    for name, entry in orthographic_data.items():
        # Extract seed name
        seed_names.append(name)
        
        # Extract seed DOB (use first variation's DOB as seed, or generate from pattern)
        # Actually, we need the original seed DOB - let's use a default
        seed_dob.append("1985-03-15")  # Default seed DOB
        
        # Get a country for this name (cycle through available countries)
        country_idx = len(seed_names) - 1
        if country_idx < len(countries):
            country = countries[country_idx]
            seed_addresses.append(country)  # Use country name as seed address
        else:
            # Fallback to first country
            seed_addresses.append(countries[0])
        
        # Format variations: [[name_var, dob_var, address_var], ...]
        variations = []
        country_addresses = address_cache.get(seed_addresses[-1], [])
        
        # Ensure we have enough unique addresses
        if len(country_addresses) < len(entry['variations']):
            # Repeat addresses if needed, but try to minimize duplicates
            extended_addresses = country_addresses * ((len(entry['variations']) // len(country_addresses)) + 1)
            country_addresses = extended_addresses[:len(entry['variations'])]
        
        for i, var in enumerate(entry['variations']):
            full_name = var['full_name']
            dob = var['dob']
            
            # Get address from the country's address list (use index to ensure uniqueness)
            addr_idx = i % len(country_addresses) if country_addresses else 0
            address = country_addresses[addr_idx] if country_addresses else seed_addresses[-1]
            
            variations.append([full_name, dob, address])
        
        responses[name] = variations
    
    return seed_names, seed_dob, seed_addresses, responses


def main():
    """Main function"""
    print("=" * 80)
    print("COMPLETE SCORING TEST WITH VALIDATOR MOCK")
    print("=" * 80)
    print()
    
    # Load orthographic data
    print("Loading orthographic names and DOB variations...")
    orthographic_file = "orthographic_15_names_15_variations.json"
    orthographic_data = load_orthographic_data(orthographic_file)
    
    if not orthographic_data:
        print("❌ Failed to load orthographic data")
        return
    
    print(f"✅ Loaded {len(orthographic_data)} names")
    print()
    
    # Load address cache
    print("Loading addresses from validated address cache...")
    address_cache_file = "validated_address_cache_new.json"
    address_cache = load_address_cache(address_cache_file, num_countries=15)
    
    if not address_cache:
        print("❌ Failed to load address cache")
        return
    
    print(f"✅ Loaded addresses for {len(address_cache)} countries")
    print()
    
    # Combine data
    print("Combining names, DOB, and addresses...")
    seed_names, seed_dob, seed_addresses, responses = combine_data_for_rewards(
        orthographic_data, address_cache
    )
    
    print(f"✅ Prepared {len(seed_names)} identities")
    print(f"   Names: {len(seed_names)}")
    print(f"   DOB variations: {len(seed_dob)}")
    print(f"   Address variations: {len(seed_addresses)}")
    print()
    
    # Show sample
    print("Sample data:")
    sample_name = seed_names[0]
    print(f"  Name: {sample_name}")
    print(f"  Seed DOB: {seed_dob[0]}")
    print(f"  Seed Address: {seed_addresses[0]}")
    print(f"  Variations: {len(responses[sample_name])}")
    print(f"  Sample variation: {responses[sample_name][0]}")
    print()
    
    # Create mock validator
    mock_self = MockSelf()
    
    # Generate query parameters (matching typical validator queries)
    variation_count = 15
    phonetic_similarity = {"Light": 0.2, "Medium": 0.6, "Far": 0.2}
    orthographic_similarity = {"Light": 0.2, "Medium": 0.6, "Far": 0.2}
    
    # Format response for rewards.py (needs MockResponse objects)
    class MockResponse:
        def __init__(self, variations_dict):
            self.variations = variations_dict
    
    responses_list = [MockResponse(responses)]
    uids = [1]
    seed_script = ["latin"] * len(seed_names)
    
    print("=" * 80)
    print("SCORING WITH REWARDS.PY")
    print("=" * 80)
    print()
    
    # Call rewards.py
    try:
        logger.info("Calling get_name_variation_rewards...")
        logger.info(f"  Seed names: {len(seed_names)}")
        logger.info(f"  Seed DOB: {len(seed_dob)}")
        logger.info(f"  Seed addresses: {len(seed_addresses)}")
        logger.info(f"  Responses: {len(responses_list)}")
        logger.info(f"  Variation count: {variation_count}")
        
        rewards, updated_uids, detailed_metrics = get_name_variation_rewards(
            mock_self,
            seed_names=seed_names,
            seed_dob=seed_dob,
            seed_addresses=seed_addresses,
            seed_script=seed_script,
            responses=responses_list,
            uids=uids,
            variation_count=variation_count,
            phonetic_similarity=phonetic_similarity,
            orthographic_similarity=orthographic_similarity,
            rule_based=None
        )
        
        print("✅ Scoring complete!")
        print(f"   Final Reward: {rewards[0]:.6f}")
        print()
        
        # Format and display results
        print("=" * 80)
        print("DETAILED SCORING RESULTS")
        print("=" * 80)
        print()
        
        if detailed_metrics and len(detailed_metrics) > 0:
            formatted_output = format_detailed_metrics(detailed_metrics[0])
            print(formatted_output)
            
            # Also log it
            logger.info("=" * 80)
            logger.info("DETAILED SCORING RESULTS")
            logger.info("=" * 80)
            logger.info("")
            logger.info(formatted_output)
        else:
            print("⚠️  No detailed metrics available")
            logger.warning("No detailed metrics available")
        
        print("=" * 80)
        print("TEST COMPLETE")
        print("=" * 80)
        print(f"✅ Final Reward: {rewards[0]:.6f}")
        print()
        
        # Summary statistics
        if detailed_metrics and len(detailed_metrics) > 0:
            metrics = detailed_metrics[0]
            print("Summary Statistics:")
            print(f"  Average Quality: {metrics.get('average_quality', 0.0):.4f}")
            print(f"  Completeness Multiplier: {metrics.get('completeness_multiplier', 0.0):.4f}")
            print(f"  Final Reward: {metrics.get('final_reward', 0.0):.4f}")
            print()
        
    except Exception as e:
        logger.error(f"❌ Error during scoring: {e}")
        import traceback
        logger.error(traceback.format_exc())
        print(f"❌ Error: {e}")
        print("Check logs for details")


if __name__ == "__main__":
    main()

