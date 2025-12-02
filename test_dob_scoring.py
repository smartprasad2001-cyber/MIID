#!/usr/bin/env python3
"""
Test DOB variation generation and scoring to understand why score is low.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'MIID', 'validator'))

from unified_generator import generate_perfect_dob_variations
from reward import _grade_dob_variations
from datetime import datetime, timedelta

def test_dob_generation():
    """Test DOB generation and scoring."""
    
    print("="*80)
    print("Testing DOB Generation and Scoring")
    print("="*80)
    print()
    
    # Test with a sample DOB
    seed_dob = "1987-12-1"
    print(f"Seed DOB: {seed_dob}")
    print()
    
    # Generate variations
    print("Generating DOB variations...")
    dob_variations = generate_perfect_dob_variations(seed_dob, variation_count=15)
    print(f"Generated {len(dob_variations)} variations:")
    for i, dob in enumerate(dob_variations, 1):
        print(f"  {i}. {dob}")
    print()
    
    # Parse seed DOB
    seed_date = datetime.strptime(seed_dob, "%Y-%m-%d")
    print(f"Seed date: {seed_date.strftime('%Y-%m-%d')}")
    print()
    
    # Classify each variation
    print("="*80)
    print("Classification of Variations")
    print("="*80)
    
    categories = {
        "±1 day": [],
        "±3 days": [],
        "±30 days": [],
        "±90 days": [],
        "±365 days": [],
        "Year+Month only": []
    }
    
    for dob_var in dob_variations:
        try:
            # Try full date format first
            var_date = datetime.strptime(dob_var, "%Y-%m-%d")
            day_diff = abs((var_date - seed_date).days)
            
            if day_diff <= 1:
                category = "±1 day"
            elif day_diff <= 3:
                category = "±3 days"
            elif day_diff <= 30:
                category = "±30 days"
            elif day_diff <= 90:
                category = "±90 days"
            elif day_diff <= 365:
                category = "±365 days"
            else:
                category = "Outside range"
            
            categories[category].append(dob_var)
            print(f"  {dob_var:15} → {category:15} (diff: {day_diff} days)")
            
        except ValueError:
            # Try year-month only format
            try:
                year_month = datetime.strptime(dob_var, "%Y-%m")
                if (seed_date.year == year_month.year and 
                    seed_date.month == year_month.month):
                    category = "Year+Month only"
                    categories[category].append(dob_var)
                    print(f"  {dob_var:15} → {category:15} (YYYY-MM format)")
                else:
                    print(f"  {dob_var:15} → Invalid year-month")
            except ValueError:
                print(f"  {dob_var:15} → Invalid format")
    
    print()
    print("="*80)
    print("Category Coverage")
    print("="*80)
    
    found_ranges = set()
    for category, dobs in categories.items():
        if dobs:
            found_ranges.add(category)
            print(f"  ✅ {category:20} : {len(dobs)} variations")
        else:
            print(f"  ❌ {category:20} : 0 variations")
    
    print()
    total_ranges = 6
    found_count = len(found_ranges)
    score = found_count / total_ranges
    print(f"Found categories: {found_count}/{total_ranges}")
    print(f"DOB Score: {score:.3f}")
    print()
    
    # Test with actual scoring function
    print("="*80)
    print("Testing with _grade_dob_variations function")
    print("="*80)
    
    # Create variations dict in the format expected by _grade_dob_variations
    # Format: {"Name": [[name_var1, dob_var1, addr_var1], [name_var2, dob_var2, addr_var2], ...]}
    variations = {
        "TestName": [[f"Name{i}", dob, "Address"] for i, dob in enumerate(dob_variations)]
    }
    
    seed_dobs = [seed_dob]
    miner_metrics = {}
    
    result = _grade_dob_variations(variations, seed_dobs, miner_metrics)
    
    print(f"Overall Score: {result['overall_score']:.3f}")
    print(f"Found Ranges: {result['found_ranges']}")
    print(f"Total Ranges: {result['total_ranges']}")
    print()
    
    # Show detailed breakdown
    if "detailed_breakdown" in result:
        breakdown = result["detailed_breakdown"]
        if "category_classifications" in breakdown:
            for name, data in breakdown["category_classifications"].items():
                print(f"Name: {name}")
                print(f"  Score: {data.get('score', 0):.3f}")
                if "categories" in data:
                    print("  Categories found:")
                    for cat, dobs in data["categories"].items():
                        print(f"    {cat}: {len(dobs)} variations")
                print()

if __name__ == "__main__":
    test_dob_generation()

