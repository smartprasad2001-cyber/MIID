#!/usr/bin/env python3
"""
Test Orthographic Scoring with Validator Mock
=============================================

This script:
1. Generates variations using maximize_orthographic_similarity.py
2. Formats them for rewards.py
3. Scores with actual rewards.py functions
4. Displays all detailed metrics in the exact format
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
        logging.FileHandler(f'test_orthographic_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)
logger = logging.getLogger(__name__)

# Add MIID/validator to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'MIID', 'validator'))

# Import rewards
from reward import get_name_variation_rewards
import numpy as np

# Import the orthographic generator
from maximize_orthographic_similarity import OrthographicBruteForceGenerator, generate_full_name_variations


class MockSelf:
    """Mock validator self object"""
    def __init__(self):
        self.uid = 1
        self.config = MockConfig()


class MockConfig:
    """Mock config object"""
    def __init__(self):
        self.neuron = MockNeuronConfig()


class MockNeuronConfig:
    """Mock neuron config"""
    def __init__(self):
        self.burn_fraction = 0.40
        self.top_miner_cap = 1
        self.quality_threshold = 0.0
        self.decay_rate = 0.0
        self.blend_factor = 0.0


def format_variations_for_rewards(combined_variations: List[Tuple[str, str]], 
                                  seed_dob: str, 
                                  seed_address: str) -> Dict[str, List[List[str]]]:
    """
    Format variations from orthographic generator into rewards.py format.
    
    Format: {name: [[name_var, dob_var, address_var], ...]}
    """
    formatted = {}
    
    for first_var, last_var in combined_variations:
        full_name = f"{first_var} {last_var}"
        
        # Generate DOB variations (simple variations)
        dob_variations = generate_dob_variations(seed_dob, len(combined_variations))
        
        # Generate address variations (simple variations)
        address_variations = generate_address_variations(seed_address, len(combined_variations))
        
        # Use the original seed name as the key
        seed_name = " ".join([first_var.split()[0] if " " in first_var else first_var,
                              last_var.split()[0] if " " in last_var else last_var])
        
        # For simplicity, use first variation's original name parts
        # We'll use the first combined variation to determine the seed name
        if not formatted:
            # Extract original from first variation (this is a bit of a hack)
            # In practice, we'd pass the original name separately
            pass
    
    # Actually, we need to know the original name
    # Let's restructure this
    return formatted


def normalize_dob_format(dob: str) -> str:
    """
    Normalize DOB format to YYYY-MM-DD.
    Handles formats like: YYYY-M-D, YYYY-MM-D, YYYY-M-DD, YYYY-MM-DD
    """
    try:
        parts = dob.split('-')
        if len(parts) == 3:
            year = parts[0]
            month = parts[1].zfill(2)  # Pad to 2 digits
            day = parts[2].zfill(2)  # Pad to 2 digits
            return f"{year}-{month}-{day}"
        elif len(parts) == 2:
            # Year-Month format
            year = parts[0]
            month = parts[1].zfill(2)
            return f"{year}-{month}"
        else:
            return dob  # Return as-is if format is unexpected
    except:
        return dob  # Return as-is if parsing fails

def generate_dob_variations(seed_dob: str, count: int) -> List[str]:
    """
    Generate DOB variations that cover ALL required categories for maximum score.
    
    Required categories (6 total):
    1. ±1 day
    2. ±3 days
    3. ±30 days
    4. ±90 days
    5. ±365 days
    6. Year+Month only (YYYY-MM format)
    
    Args:
        seed_dob: Seed date of birth in YYYY-MM-DD format
        count: Total number of variations to generate (will ensure all 6 categories are covered)
    
    Returns:
        List of DOB variations covering all 6 categories
    """
    from datetime import datetime, timedelta
    
    dob_variations = []
    
    try:
        # Normalize DOB format first
        normalized_dob = normalize_dob_format(seed_dob)
        
        # Parse seed DOB
        seed_date = datetime.strptime(normalized_dob, "%Y-%m-%d")
        
        # Category 1: ±1 day (at least 1 variation)
        # Generate both +1 and -1 day
        for days in [-1, 1]:
            var_date = seed_date + timedelta(days=days)
            dob_variations.append(var_date.strftime("%Y-%m-%d"))
        
        # Category 2: ±3 days (at least 1 variation)
        # Generate both +3 and -3 days
        for days in [-3, 3]:
            var_date = seed_date + timedelta(days=days)
            dob_variations.append(var_date.strftime("%Y-%m-%d"))
        
        # Category 3: ±30 days (at least 1 variation)
        # Generate both +30 and -30 days
        for days in [-30, 30]:
            var_date = seed_date + timedelta(days=days)
            dob_variations.append(var_date.strftime("%Y-%m-%d"))
        
        # Category 4: ±90 days (at least 1 variation)
        # Generate both +90 and -90 days
        for days in [-90, 90]:
            var_date = seed_date + timedelta(days=days)
            dob_variations.append(var_date.strftime("%Y-%m-%d"))
        
        # Category 5: ±365 days (at least 1 variation)
        # Generate both +365 and -365 days
        for days in [-365, 365]:
            var_date = seed_date + timedelta(days=days)
            dob_variations.append(var_date.strftime("%Y-%m-%d"))
        
        # Category 6: Year+Month variation (using complete date format)
        # Use a date in the same month but different day to represent year+month category
        # This ensures we always have YYYY-MM-DD format
        # Use the 1st day of the month to represent year+month category
        year_month_day = seed_date.replace(day=1).strftime("%Y-%m-%d")
        
        # Build a prioritized list ensuring all 6 categories are covered
        # Priority: Ensure at least 1 from each category, then fill remaining slots
        
        # Create category representatives (one from each category)
        category_reps = [
            (seed_date + timedelta(days=-1)).strftime("%Y-%m-%d"),  # ±1 day
            (seed_date + timedelta(days=-3)).strftime("%Y-%m-%d"),  # ±3 days
            (seed_date + timedelta(days=-30)).strftime("%Y-%m-%d"),  # ±30 days
            (seed_date + timedelta(days=-90)).strftime("%Y-%m-%d"),  # ±90 days
            (seed_date + timedelta(days=-365)).strftime("%Y-%m-%d"),  # ±365 days
            year_month_day  # Year+Month (using complete date format)
        ]
        
        # Start with category representatives (ensures all 6 categories)
        final_variations = category_reps.copy()
        
        # If more variations are needed, add additional ones from each category
        if count > len(final_variations):
            additional_needed = count - len(final_variations)
            
            # Additional variations from each category
            additional_variations = [
                (seed_date + timedelta(days=1)).strftime("%Y-%m-%d"),  # ±1 day (positive)
                (seed_date + timedelta(days=3)).strftime("%Y-%m-%d"),  # ±3 days (positive)
                (seed_date + timedelta(days=30)).strftime("%Y-%m-%d"),  # ±30 days (positive)
                (seed_date + timedelta(days=90)).strftime("%Y-%m-%d"),  # ±90 days (positive)
                (seed_date + timedelta(days=365)).strftime("%Y-%m-%d"),  # ±365 days (positive)
                # More variations from different offsets
                (seed_date + timedelta(days=-2)).strftime("%Y-%m-%d"),
                (seed_date + timedelta(days=2)).strftime("%Y-%m-%d"),
                (seed_date + timedelta(days=-7)).strftime("%Y-%m-%d"),
                (seed_date + timedelta(days=7)).strftime("%Y-%m-%d"),
                (seed_date + timedelta(days=-15)).strftime("%Y-%m-%d"),
                (seed_date + timedelta(days=15)).strftime("%Y-%m-%d"),
                (seed_date + timedelta(days=-45)).strftime("%Y-%m-%d"),
                (seed_date + timedelta(days=45)).strftime("%Y-%m-%d"),
                (seed_date + timedelta(days=-60)).strftime("%Y-%m-%d"),
                (seed_date + timedelta(days=60)).strftime("%Y-%m-%d"),
                (seed_date + timedelta(days=-120)).strftime("%Y-%m-%d"),
                (seed_date + timedelta(days=120)).strftime("%Y-%m-%d"),
                (seed_date + timedelta(days=-180)).strftime("%Y-%m-%d"),
                (seed_date + timedelta(days=180)).strftime("%Y-%m-%d"),
                (seed_date + timedelta(days=-270)).strftime("%Y-%m-%d"),
                (seed_date + timedelta(days=270)).strftime("%Y-%m-%d"),
            ]
            
            # Add additional variations up to the requested count
            for i in range(additional_needed):
                if i < len(additional_variations):
                    final_variations.append(additional_variations[i])
                else:
                    # If we run out, repeat year-month format (using complete date)
                    final_variations.append(year_month_day)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_variations = []
        for dob in final_variations:
            if dob not in seen:
                seen.add(dob)
                unique_variations.append(dob)
        
        # Ensure year-month is included (add at the end if somehow missing)
        if year_month_day not in unique_variations:
            unique_variations.append(year_month_day)
        
        # Return exactly the requested count, but ensure all 6 categories are represented
        return unique_variations[:count]
        
    except ValueError as e:
        # If seed DOB format is invalid, return empty list
        logger.error(f"Error parsing seed DOB '{seed_dob}': {e}")
        return []
    except Exception as e:
        logger.error(f"Error generating DOB variations for '{seed_dob}': {e}")
        return []


def generate_address_variations(seed_address: str, count: int) -> List[str]:
    """Generate simple address variations"""
    # For now, return the same address
    # In production, would use address cache or generate realistic variations
    return [seed_address] * count


def format_detailed_metrics(metrics: Dict[str, Any]) -> str:
    """Format detailed metrics in the exact format specified"""
    lines = []
    
    # Final score
    if "final_reward" in metrics:
        lines.append("Final score")
        lines.append(f"{metrics['final_reward']:.3f}")
        lines.append("")
    elif "post_penalty_reward" in metrics:
        lines.append("Final score")
        lines.append(f"{metrics['post_penalty_reward']:.3f}")
        lines.append("")
    
    # Names
    if "name_metrics" in metrics:
        lines.append("Names")
        total_name_score = 0.0
        count = 0
        for name, name_metrics in metrics["name_metrics"].items():
            if "quality_score" in name_metrics:
                total_name_score += name_metrics["quality_score"]
                count += 1
        if count > 0:
            lines.append(f"{total_name_score / count:.3f}")
        else:
            lines.append("0.000")
        lines.append("")
    
    # Basic Quality Score
    if "average_quality" in metrics:
        lines.append("Basic Quality Score")
        lines.append(f"{metrics['average_quality']:.3f}")
        lines.append("")
    
    # Similarity Score
    similarity_scores = []
    if "name_metrics" in metrics:
        for name_metrics in metrics["name_metrics"].values():
            if "detailed_metrics" in name_metrics:
                dm = name_metrics["detailed_metrics"]
                if "similarity" in dm:
                    if isinstance(dm["similarity"], dict):
                        if "combined" in dm["similarity"]:
                            similarity_scores.append(float(dm["similarity"]["combined"]))
                        elif "score" in dm["similarity"]:
                            similarity_scores.append(float(dm["similarity"]["score"]))
    if similarity_scores:
        lines.append("Similarity Score")
        lines.append(f"{sum(similarity_scores) / len(similarity_scores):.3f}")
        lines.append("")
    else:
        lines.append("Similarity Score")
        lines.append("0.000")
        lines.append("")
    
    # Phonetic Similarity
    phonetic_scores = []
    if "name_metrics" in metrics:
        for name_metrics in metrics["name_metrics"].values():
            if "detailed_metrics" in name_metrics:
                dm = name_metrics["detailed_metrics"]
                if "similarity" in dm and isinstance(dm["similarity"], dict):
                    if "phonetic" in dm["similarity"]:
                        phonetic_scores.append(float(dm["similarity"]["phonetic"]))
    if phonetic_scores:
        lines.append("Phonetic Similarity")
        lines.append(f"{sum(phonetic_scores) / len(phonetic_scores):.3f}")
        lines.append("")
    else:
        lines.append("Phonetic Similarity")
        lines.append("0.000")
        lines.append("")
    
    # Orthographic Similarity
    orthographic_scores = []
    if "name_metrics" in metrics:
        for name_metrics in metrics["name_metrics"].values():
            if "detailed_metrics" in name_metrics:
                dm = name_metrics["detailed_metrics"]
                if "similarity" in dm and isinstance(dm["similarity"], dict):
                    if "orthographic" in dm["similarity"]:
                        orthographic_scores.append(float(dm["similarity"]["orthographic"]))
    if orthographic_scores:
        lines.append("Orthographic Similarity")
        lines.append(f"{sum(orthographic_scores) / len(orthographic_scores):.3f}")
        lines.append("")
    else:
        lines.append("Orthographic Similarity")
        lines.append("0.000")
        lines.append("")
    
    # Count Score
    count_scores = []
    if "name_metrics" in metrics:
        for name_metrics in metrics["name_metrics"].values():
            if "detailed_metrics" in name_metrics:
                dm = name_metrics["detailed_metrics"]
                if "count" in dm and "score" in dm["count"]:
                    count_scores.append(float(dm["count"]["score"]))
    if count_scores:
        lines.append("Count Score")
        lines.append(f"{sum(count_scores) / len(count_scores):.3f}")
        lines.append("")
    else:
        lines.append("Count Score")
        lines.append("0.000")
        lines.append("")
    
    # Uniqueness Score
    uniqueness_scores = []
    if "name_metrics" in metrics:
        for name_metrics in metrics["name_metrics"].values():
            if "detailed_metrics" in name_metrics:
                dm = name_metrics["detailed_metrics"]
                if "uniqueness" in dm and "score" in dm["uniqueness"]:
                    uniqueness_scores.append(float(dm["uniqueness"]["score"]))
    if uniqueness_scores:
        lines.append("Uniqueness Score")
        lines.append(f"{sum(uniqueness_scores) / len(uniqueness_scores):.3f}")
        lines.append("")
    else:
        lines.append("Uniqueness Score")
        lines.append("0.000")
        lines.append("")
    
    # Length Score
    length_scores = []
    if "name_metrics" in metrics:
        for name_metrics in metrics["name_metrics"].values():
            if "detailed_metrics" in name_metrics:
                dm = name_metrics["detailed_metrics"]
                if "length" in dm and "score" in dm["length"]:
                    length_scores.append(float(dm["length"]["score"]))
    if length_scores:
        lines.append("Length Score")
        lines.append(f"{sum(length_scores) / len(length_scores):.3f}")
        lines.append("")
    else:
        lines.append("Length Score")
        lines.append("0.000")
        lines.append("")
    
    # Rule Compliance Score
    rule_scores = []
    if "name_metrics" in metrics:
        for name_metrics in metrics["name_metrics"].values():
            if "rule_compliance" in name_metrics:
                rc = name_metrics["rule_compliance"]
                if isinstance(rc, dict):
                    if "score" in rc:
                        rule_scores.append(float(rc["score"]))
                    elif "compliance_score" in rc:
                        rule_scores.append(float(rc["compliance_score"]))
                elif isinstance(rc, (int, float)):
                    rule_scores.append(float(rc))
    if rule_scores:
        lines.append("Rule Compliance Score")
        lines.append(f"{sum(rule_scores) / len(rule_scores):.3f}")
        lines.append("")
    elif "rule_compliance" in metrics:
        rc = metrics["rule_compliance"]
        if isinstance(rc, dict) and "score" in rc:
            lines.append("Rule Compliance Score")
            lines.append(f"{rc['score']:.3f}")
            lines.append("")
        elif isinstance(rc, (int, float)):
            lines.append("Rule Compliance Score")
            lines.append(f"{float(rc):.3f}")
            lines.append("")
    else:
        lines.append("Rule Compliance Score")
        lines.append("0.000")
        lines.append("")
    
    # Address Score
    if "address_grading" in metrics:
        addr_grading = metrics["address_grading"]
        if isinstance(addr_grading, dict) and "overall_score" in addr_grading:
            lines.append("Address Score")
            lines.append(f"{addr_grading['overall_score']:.3f}")
            lines.append("")
        elif isinstance(addr_grading, (int, float)):
            lines.append("Address Score")
            lines.append(f"{float(addr_grading):.3f}")
            lines.append("")
    elif "address_score" in metrics:
        lines.append("Address Score")
        lines.append(f"{metrics['address_score']:.3f}")
        lines.append("")
    else:
        lines.append("Address Score")
        lines.append("0.000")
        lines.append("")
    
    # Looks Like Address
    if "address_grading" in metrics and isinstance(metrics["address_grading"], dict):
        addr_breakdown = metrics["address_grading"].get("detailed_breakdown", {})
        heuristic_perfect = addr_breakdown.get("heuristic_perfect", False)
        lines.append("Looks Like Address")
        lines.append(f"{1.0 if heuristic_perfect else 0.0:.3f}")
        lines.append("")
    else:
        lines.append("Looks Like Address")
        lines.append("0.000")
        lines.append("")
    
    # Address Regain Match (region match)
    if "address_grading" in metrics and isinstance(metrics["address_grading"], dict):
        addr_breakdown = metrics["address_grading"].get("detailed_breakdown", {})
        region_matches = addr_breakdown.get("region_matches", 0)
        total_addresses = addr_breakdown.get("total_addresses", 1)
        region_score = region_matches / total_addresses if total_addresses > 0 else 0.0
        lines.append("Address Regain Match")
        lines.append(f"{region_score:.3f}")
        lines.append("")
    else:
        lines.append("Address Regain Match")
        lines.append("0.000")
        lines.append("")
    
    # Address API call
    if "address_grading" in metrics and isinstance(metrics["address_grading"], dict):
        addr_breakdown = metrics["address_grading"].get("detailed_breakdown", {})
        api_validation = addr_breakdown.get("api_validation", {})
        api_result_score = api_validation.get("api_result_score", 0.0)
        if isinstance(api_result_score, (int, float)):
            lines.append("Address API call")
            lines.append(f"{float(api_result_score):.3f}")
            lines.append("")
        else:
            lines.append("Address API call")
            lines.append("0.000")
            lines.append("")
    else:
        lines.append("Address API call")
        lines.append("0.000")
        lines.append("")
    
    # DOB Score
    if "dob_grading" in metrics:
        dob_grading = metrics["dob_grading"]
        if isinstance(dob_grading, dict) and "overall_score" in dob_grading:
            lines.append("DOB Score")
            lines.append(f"{dob_grading['overall_score']:.3f}")
            lines.append("")
        elif isinstance(dob_grading, (int, float)):
            lines.append("DOB Score")
            lines.append(f"{float(dob_grading):.3f}")
            lines.append("")
    elif "dob_score" in metrics:
        lines.append("DOB Score")
        lines.append(f"{metrics['dob_score']:.3f}")
        lines.append("")
    else:
        lines.append("DOB Score")
        lines.append("0.000")
        lines.append("")
    
    # Completeness Multiplier
    if "completeness_multiplier" in metrics:
        lines.append("Completeness Multiplier")
        lines.append(f"{metrics['completeness_multiplier']:.3f}")
        lines.append("")
    else:
        lines.append("Completeness Multiplier")
        lines.append("1.000")
        lines.append("")
    
    # Penalties
    penalties = metrics.get("penalties", {})
    
    # Extra names penalty
    lines.append("Extra names penalty")
    lines.append(f"{penalties.get('extra_names', 0.0):.3f}")
    lines.append("")
    
    # Missing names penalty
    lines.append("Missing names penalty")
    lines.append(f"{penalties.get('missing_names', 0.0):.3f}")
    lines.append("")
    
    # Post Penalty
    if "post_penalty_reward" in metrics:
        lines.append("Post Penalty")
        lines.append(f"{metrics['post_penalty_reward']:.3f}")
        lines.append("")
    elif "final_reward" in metrics:
        lines.append("Post Penalty")
        lines.append(f"{metrics['final_reward']:.3f}")
        lines.append("")
    else:
        lines.append("Post Penalty")
        lines.append("0.000")
        lines.append("")
    
    # Address Penalty
    lines.append("Address Penalty")
    lines.append(f"{penalties.get('insufficient_addresses', 0.0):.3f}")
    lines.append("")
    
    # Collusion Penalty
    lines.append("Collusion Penalty")
    lines.append(f"{penalties.get('collusion', 0.0):.3f}")
    lines.append("")
    
    # Duplication Penalty
    lines.append("Duplication Penalty")
    lines.append(f"{penalties.get('duplication', 0.0):.3f}")
    lines.append("")
    
    # Signature Copy Penalty
    lines.append("Signature Copy Penalty")
    lines.append(f"{penalties.get('signature_copy', 0.0):.3f}")
    lines.append("")
    
    # Special Chars Penalty
    lines.append("Special Chars Penalty")
    lines.append(f"{penalties.get('numbers_in_names', 0.0):.3f}")
    lines.append("")
    
    return "\n".join(lines)


def main():
    """Main function to test orthographic scoring"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test orthographic variations with validator mock")
    parser.add_argument("name", help="Full name (e.g., 'John Smith')")
    parser.add_argument("--count", type=int, default=15, help="Number of variations (default: 15)")
    parser.add_argument("--light", type=float, default=0.2, help="Target Light percentage (default: 0.2)")
    parser.add_argument("--medium", type=float, default=0.6, help="Target Medium percentage (default: 0.6)")
    parser.add_argument("--far", type=float, default=0.2, help="Target Far percentage (default: 0.2)")
    parser.add_argument("--dob", type=str, default="1985-03-15", help="Seed DOB (default: 1985-03-15)")
    parser.add_argument("--address", type=str, default="New York, United States", help="Seed address")
    
    args = parser.parse_args()
    
    # Normalize percentages
    total = args.light + args.medium + args.far
    if total != 1.0:
        print(f"⚠️  Percentages sum to {total}, normalizing...")
        args.light /= total
        args.medium /= total
        args.far /= total
    
    target_distribution = {
        "Light": args.light,
        "Medium": args.medium,
        "Far": args.far
    }
    
    print("=" * 80)
    print("ORTHOGRAPHIC VARIATION SCORING TEST")
    print("=" * 80)
    print()
    print(f"Original Name: {args.name}")
    print(f"Variation Count: {args.count}")
    print(f"Target Distribution: {target_distribution}")
    print(f"Seed DOB: {args.dob}")
    print(f"Seed Address: {args.address}")
    print()
    
    # Split name into first and last
    name_parts = args.name.strip().split()
    if len(name_parts) < 2:
        print("❌ Error: Please provide full name (first and last)")
        return
    
    first_name = name_parts[0]
    last_name = " ".join(name_parts[1:])
    
    # Generate variations
    print("🔍 Generating variations...")
    print()
    combined_variations, gen_metrics = generate_full_name_variations(
        first_name, last_name, target_distribution, args.count
    )
    
    print()
    print("=" * 80)
    print("FORMATTING FOR REWARDS.PY")
    print("=" * 80)
    print()
    
    # Format variations for rewards.py
    # Format: {seed_name: [[name_var, dob_var, address_var], ...]}
    seed_name = args.name
    formatted_variations = {seed_name: []}
    
    # Generate DOB and address variations
    dob_variations = generate_dob_variations(args.dob, args.count)
    address_variations = generate_address_variations(args.address, args.count)
    
    # Combine into format: [[name_var, dob_var, address_var], ...]
    for i, (first_var, last_var) in enumerate(combined_variations):
        full_name_var = f"{first_var} {last_var}"
        dob_var = dob_variations[i] if i < len(dob_variations) else args.dob
        addr_var = address_variations[i] if i < len(address_variations) else args.address
        formatted_variations[seed_name].append([full_name_var, dob_var, addr_var])
    
    logger.info(f"Formatted {len(formatted_variations[seed_name])} variations for rewards.py")
    logger.info(f"Sample variation: {formatted_variations[seed_name][0] if formatted_variations[seed_name] else 'None'}")
    logger.info(f"Seed name: '{seed_name}' (type: {type(seed_name)}, len: {len(seed_name)})")
    logger.info(f"Variations keys: {list(formatted_variations.keys())}")
    for key in formatted_variations.keys():
        logger.info(f"  Key: '{key}' (type: {type(key)}, len: {len(key)})")
    
    # Debug: Print first few variations
    for i, var in enumerate(formatted_variations[seed_name][:3]):
        logger.info(f"  Variation {i+1}: {var}")
    
    # Ensure seed_name matches exactly (strip whitespace)
    seed_name = seed_name.strip()
    if seed_name not in formatted_variations:
        logger.warning(f"⚠️  Seed name '{seed_name}' not in variations keys! Adding it...")
        # Re-key the variations with the exact seed_name
        if formatted_variations:
            old_key = list(formatted_variations.keys())[0]
            formatted_variations[seed_name] = formatted_variations.pop(old_key)
    
    # Create MockResponse object (rewards.py expects response.variations)
    class MockResponse:
        def __init__(self, variations_dict):
            self.variations = variations_dict
    
    responses = [MockResponse(formatted_variations)]
    
    # Final verification
    logger.info(f"Final seed_name: '{seed_name}'")
    logger.info(f"Final variations keys: {list(responses[0].variations.keys())}")
    logger.info(f"Seed name in variations: {seed_name in responses[0].variations}")
    
    # Create mock validator
    mock_self = MockSelf()
    
    # Generate query parameters
    variation_count = args.count
    phonetic_similarity = {"Light": 0.2, "Medium": 0.6, "Far": 0.2}  # Default
    orthographic_similarity = target_distribution
    
    print()
    print("=" * 80)
    print("SCORING WITH REWARDS.PY")
    print("=" * 80)
    print()
    
    # Call rewards.py
    try:
        logger.info("="*80)
        logger.info("CALLING REWARDS.PY")
        logger.info("="*80)
        logger.info(f"Seed names: {[seed_name]}")
        logger.info(f"Seed DOB: {[args.dob]}")
        logger.info(f"Seed addresses: {[args.address]}")
        logger.info(f"Responses type: {type(responses)}")
        logger.info(f"Responses length: {len(responses)}")
        if responses:
            logger.info(f"First response type: {type(responses[0])}")
            if hasattr(responses[0], 'variations'):
                logger.info(f"First response variations type: {type(responses[0].variations)}")
                logger.info(f"First response variations keys: {list(responses[0].variations.keys())}")
                logger.info(f"First response variations count: {len(responses[0].variations.get(seed_name, []))}")
        
        rewards, uids, detailed_metrics = get_name_variation_rewards(
            mock_self,
            seed_names=[seed_name],
            seed_dob=[args.dob],
            seed_addresses=[args.address],
            seed_script=["latin"],
            responses=responses,
            uids=[1],
            variation_count=variation_count,
            phonetic_similarity=phonetic_similarity,
            orthographic_similarity=orthographic_similarity,
            rule_based=None
        )
        
        logger.info(f"✅ Scoring complete. Reward: {rewards[0]:.6f}")
        logger.info(f"   Detailed metrics keys: {list(detailed_metrics[0].keys()) if detailed_metrics else 'None'}")
        if detailed_metrics and len(detailed_metrics) > 0:
            logger.info(f"   Name metrics keys: {list(detailed_metrics[0].get('name_metrics', {}).keys())}")
        
        # Format and display results
        print()
        print("=" * 80)
        print("DETAILED SCORING RESULTS")
        print("=" * 80)
        print()
        
        if detailed_metrics and len(detailed_metrics) > 0:
            # Debug: Print full metrics structure
            logger.info("=" * 80)
            logger.info("FULL METRICS STRUCTURE")
            logger.info("=" * 80)
            logger.info(json.dumps(detailed_metrics[0], indent=2, default=str))
            logger.info("=" * 80)
            
            formatted_output = format_detailed_metrics(detailed_metrics[0])
            print(formatted_output)
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
        
    except Exception as e:
        logger.error(f"❌ Error during scoring: {e}")
        import traceback
        logger.error(traceback.format_exc())
        print(f"❌ Error: {e}")
        print("Check logs for details")


if __name__ == "__main__":
    main()

