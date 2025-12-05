#!/usr/bin/env python3
"""
Visual demonstration of how the generator distributes rule-compliant variations.
Shows the step-by-step logic with examples.
"""

def demonstrate_distribution_logic():
    """Show how the algorithm works with different scenarios."""
    
    print("=" * 80)
    print("GENERATOR DISTRIBUTION LOGIC - STEP BY STEP")
    print("=" * 80)
    print()
    
    # Scenario 1: Ideal case (rule-compliant available in all categories)
    print("SCENARIO 1: Rule-compliant variations available in ALL categories")
    print("-" * 80)
    print("Target: 3 Light, 9 Medium, 3 Far | 4 rule-compliant")
    print()
    
    # Simulated available rule-compliant variations
    rule_compliant_available = {
        "Light": ["var1", "var2", "var3"],      # 3 available
        "Medium": ["var4", "var5", "var6"],     # 3 available
        "Far": ["var7", "var8"]                 # 2 available
    }
    
    selected = []
    rule_count = 0
    target_rule_count = 4
    target_orthographic = {"Light": 3, "Medium": 9, "Far": 3}
    
    print("Phase 1: Fill each category with rule-compliant (priority)")
    print()
    
    for category in ["Light", "Medium", "Far"]:
        needed = target_orthographic[category]
        print(f"  {category} (need {needed}):")
        
        # Try to fill with rule-compliant
        available = rule_compliant_available.get(category, [])
        rule_taken = min(needed, len(available), target_rule_count - rule_count)
        
        if rule_taken > 0:
            for i in range(rule_taken):
                var = available[i]
                selected.append((var, category, "RULE"))
                rule_count += 1
                print(f"    ✅ Added {var} (rule-compliant, {category})")
        
        # Fill remaining with non-rule
        remaining = needed - rule_taken
        if remaining > 0:
            for i in range(remaining):
                var = f"non_rule_{category}_{i+1}"
                selected.append((var, category, "non-rule"))
                print(f"    ✅ Added {var} (non-rule, {category})")
        print()
    
    print(f"Result: {rule_count} rule-compliant out of {len(selected)} total")
    print()
    print("Distribution:")
    light_count = sum(1 for _, cat, _ in selected if cat == "Light")
    medium_count = sum(1 for _, cat, _ in selected if cat == "Medium")
    far_count = sum(1 for _, cat, _ in selected if cat == "Far")
    print(f"  Light: {light_count} (target: 3)")
    print(f"  Medium: {medium_count} (target: 9)")
    print(f"  Far: {far_count} (target: 3)")
    print()
    
    # Scenario 2: Rule-compliant only in Light
    print("=" * 80)
    print("SCENARIO 2: Rule-compliant variations ONLY in Light (CURRENT PROBLEM)")
    print("-" * 80)
    print("Target: 3 Light, 9 Medium, 3 Far | 4 rule-compliant")
    print()
    
    rule_compliant_available = {
        "Light": ["var1", "var2", "var3", "var4", "var5"],  # 5 available
        "Medium": [],                                       # 0 available
        "Far": []                                           # 0 available
    }
    
    selected = []
    rule_count = 0
    
    print("Phase 1: Fill each category with rule-compliant (priority)")
    print()
    
    for category in ["Light", "Medium", "Far"]:
        needed = target_orthographic[category]
        print(f"  {category} (need {needed}):")
        
        # Try to fill with rule-compliant
        available = rule_compliant_available.get(category, [])
        rule_taken = min(needed, len(available), target_rule_count - rule_count)
        
        if rule_taken > 0:
            for i in range(rule_taken):
                var = available[i]
                selected.append((var, category, "RULE"))
                rule_count += 1
                print(f"    ✅ Added {var} (rule-compliant, {category})")
        
        # Fill remaining with non-rule
        remaining = needed - rule_taken
        if remaining > 0:
            for i in range(remaining):
                var = f"non_rule_{category}_{i+1}"
                selected.append((var, category, "non-rule"))
                print(f"    ✅ Added {var} (non-rule, {category})")
        print()
    
    print(f"Phase 2: Need more rule-compliant? Current: {rule_count}, Target: {target_rule_count}")
    if rule_count < target_rule_count:
        print(f"  ⚠️  Only {rule_count} rule-compliant found (need {target_rule_count})")
        print(f"  🔄 Trying to add more from any category...")
        
        # Check if we can add more from Light without breaking distribution
        remaining_light_rule = [v for v in rule_compliant_available["Light"] 
                                if v not in [s[0] for s in selected]]
        
        if remaining_light_rule and rule_count < target_rule_count:
            # But adding more Light would break distribution!
            print(f"  ❌ Cannot add more - would break Light distribution (already have 3)")
            print(f"  ❌ Result: Only {rule_count} rule-compliant instead of {target_rule_count}")
    
    print()
    print("Result:")
    light_count = sum(1 for _, cat, _ in selected if cat == "Light")
    medium_count = sum(1 for _, cat, _ in selected if cat == "Medium")
    far_count = sum(1 for _, cat, _ in selected if cat == "Far")
    print(f"  Light: {light_count} (target: 3)")
    print(f"  Medium: {medium_count} (target: 9)")
    print(f"  Far: {far_count} (target: 3)")
    print(f"  Rule-compliant: {rule_count} (target: {target_rule_count}) ❌")
    print()
    
    # Scenario 3: Example 1 from user
    print("=" * 80)
    print("SCENARIO 3: Example 1 - Distributed Rule-Compliant")
    print("-" * 80)
    print("Target: 3 Light, 9 Medium, 3 Far | 4 rule-compliant")
    print("Desired: 1 rule in Light, 2 in Medium, 1 in Far")
    print()
    
    rule_compliant_available = {
        "Light": ["var1"],      # Need 1
        "Medium": ["var2", "var3"],  # Need 2
        "Far": ["var4"]         # Need 1
    }
    
    selected = []
    rule_count = 0
    
    for category in ["Light", "Medium", "Far"]:
        needed = target_orthographic[category]
        print(f"  {category} (need {needed}):")
        
        available = rule_compliant_available.get(category, [])
        rule_taken = min(needed, len(available), target_rule_count - rule_count)
        
        if rule_taken > 0:
            for i in range(rule_taken):
                var = available[i]
                selected.append((var, category, "RULE"))
                rule_count += 1
                print(f"    ✅ Added {var} (rule-compliant)")
        
        remaining = needed - rule_taken
        if remaining > 0:
            for i in range(remaining):
                var = f"non_rule_{category}_{i+1}"
                selected.append((var, category, "non-rule"))
                print(f"    ✅ Added {var} (non-rule)")
        print()
    
    print(f"✅ Perfect! {rule_count} rule-compliant distributed across categories")
    print()
    print("Final Distribution:")
    print("  Light: 3 total (1 rule-compliant, 2 non-rule)")
    print("  Medium: 9 total (2 rule-compliant, 7 non-rule)")
    print("  Far: 3 total (1 rule-compliant, 2 non-rule)")
    print(f"  Total rule-compliant: {rule_count} ✅")
    print()
    print("=" * 80)

if __name__ == "__main__":
    demonstrate_distribution_logic()

