#!/usr/bin/env python3
"""
Simple test: Give 15 names to unified generator and get output
"""

import os
import sys
import json
import random

# Flush output immediately
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

print("🔍 Starting script...", flush=True)

# Add paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("📦 Importing modules...", flush=True)

try:
    from unified_generator import (
        generate_full_name_variations,
        generate_perfect_dob_variations
    )
    print("✅ Imports successful", flush=True)
except Exception as e:
    print(f"❌ Import error: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

def load_sanctioned_names(count: int = 15):
    """Load names from sanctioned list file (already in Latin script)"""
    print(f"📂 Loading names from file...", flush=True)
    json_path = os.path.join(os.path.dirname(__file__), 'MIID', 'validator', 'Sanctioned_list.json')
    print(f"   Path: {json_path}", flush=True)
    
    if not os.path.exists(json_path):
        print(f"❌ File not found: {json_path}", flush=True)
        return []
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            all_names = json.load(f)
        print(f"   ✅ Loaded {len(all_names)} names from file", flush=True)
        
        # Select random names
        selected = random.sample(all_names, min(count, len(all_names)))
        print(f"   ✅ Selected {len(selected)} names", flush=True)
        
        # Convert to format expected by unified_generator (add Script field)
        for person in selected:
            person['Script'] = 'latin'  # All names in this list are already Latin
        
        return selected
    except Exception as e:
        print(f"❌ Error loading file: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return []

def main():
    print("="*80, flush=True)
    print("UNIFIED GENERATOR TEST - 15 NAMES", flush=True)
    print("="*80, flush=True)
    print(flush=True)
    
    # Load 15 names from Sanctioned_list.json (already in Latin script)
    print("📋 Loading 15 names from Sanctioned_list.json (Latin script)...", flush=True)
    sanctioned_names = load_sanctioned_names(15)
    
    if not sanctioned_names:
        print("❌ No names loaded. Exiting.", flush=True)
        return
    
    print(f"✅ Loaded {len(sanctioned_names)} names\n", flush=True)
    
    # Requirements
    variation_count = 15
    
    # Distribution: 30% Light, 50% Medium, 20% Far
    # Light range: phonetic (0.8-1.0), orthographic (0.7-1.0)
    # Medium range: phonetic (0.6-0.79), orthographic (0.50-0.69)
    # Far range: phonetic (0.3-0.6), orthographic (0.2-0.5)
    light_pct = 0.30
    medium_pct = 0.50
    far_pct = 0.20
    
    print(f"📋 Requirements:", flush=True)
    print(f"✅ Variation count: {variation_count}", flush=True)
    print(f"✅ Distribution: Light={light_pct:.0%}, Medium={medium_pct:.0%}, Far={far_pct:.0%}\n", flush=True)
    
    # Process each name
    all_results = {}
    
    for i, person in enumerate(sanctioned_names, 1):
        first_name = person.get('FirstName', '')
        last_name = person.get('LastName', '')
        full_name = f"{first_name} {last_name}".strip()
        dob = person.get('DOB', '1990-01-01')
        script = person.get('Script', 'latin')
        
        print(f"[{i}/15] Processing: {full_name} (script: {script})", flush=True)
        
        try:
            # Calculate counts for distribution: 30% Light, 50% Medium, 20% Far
            light_count = max(1, int(variation_count * light_pct))
            medium_count = max(1, int(variation_count * medium_pct))
            far_count = max(1, int(variation_count * far_pct))
            
            # Adjust to ensure total equals variation_count
            total = light_count + medium_count + far_count
            if total < variation_count:
                # Add remaining to medium
                medium_count += (variation_count - total)
            elif total > variation_count:
                # Remove excess from medium
                medium_count -= (total - variation_count)
            
            # Generate name variations using unified_generator
            print(f"      🔄 Generating name variations (Light={light_count}, Medium={medium_count}, Far={far_count})...", flush=True)
            name_variations = generate_full_name_variations(
                full_name,
                light_count=light_count,
                medium_count=medium_count,
                far_count=far_count,
                verbose=False
            )
            print(f"      ✅ Generated {len(name_variations)} name variations", flush=True)
            
            # Generate DOB variations using unified_generator
            print(f"      🔄 Generating DOB variations...", flush=True)
            dob_variations = generate_perfect_dob_variations(dob, variation_count=variation_count)
            print(f"      ✅ Generated {len(dob_variations)} DOB variations", flush=True)
            
            # Combine into structured format (address blank)
            structured_variations = []
            for j in range(variation_count):
                name_var = name_variations[j] if j < len(name_variations) else full_name
                dob_var = dob_variations[j] if j < len(dob_variations) else dob
                addr_var = ""  # Blank address
                structured_variations.append([name_var, dob_var, addr_var])
            
            all_results[full_name] = structured_variations
            
            print(f"   ✅ Generated {len(structured_variations)} variations", flush=True)
            print(f"   📝 Sample: {name_variations[0] if name_variations else 'N/A'} | {dob_variations[0] if dob_variations else 'N/A'}", flush=True)
            print(flush=True)
            
        except Exception as e:
            print(f"   ❌ Error: {e}", flush=True)
            import traceback
            traceback.print_exc()
            print(flush=True)
    
    # Save results
    output_file = "unified_generator_output.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "test_date": __import__('datetime').datetime.now().isoformat(),
            "total_names": len(all_results),
            "variations": all_results
        }, f, indent=2, ensure_ascii=False)
    
    print("="*80)
    print(f"✅ COMPLETE - Generated variations for {len(all_results)} names")
    print(f"💾 Results saved to {output_file}")
    print("="*80)

if __name__ == '__main__':
    main()

