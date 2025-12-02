"""
Test Smart Phonetic Generator with Actual Rewards.py Scoring
"""

from smart_phonetic_generator import generate_smart_variations, predict_score
from MIID.validator.reward import calculate_variation_quality

# Test with multiple names
test_names = [
    "John Smith",
    "Mary Johnson",
    "Sarah Brown"
]

print("="*80)
print("TESTING SMART GENERATOR WITH ACTUAL REWARDS.PY SCORING")
print("="*80)

for name in test_names:
    print("\n" + "="*80)
    print(f"Testing: {name}")
    print("="*80)
    
    parts = name.split()
    first_original = parts[0]
    last_original = parts[1] if len(parts) > 1 else ""
    
    # Generate variations using smart generator
    variations = generate_smart_variations(name, light_count=2, medium_count=5, far_count=1)
    
    print(f"\nGenerated {len(variations)} variations:")
    print("-" * 80)
    
    # Show predicted scores
    first_scores = []
    last_scores = []
    
    for i, var in enumerate(variations, 1):
        var_parts = var.split()
        first_var = var_parts[0] if len(var_parts) > 0 else ""
        last_var = var_parts[1] if len(var_parts) > 1 else ""
        
        first_pred = predict_score(first_original, first_var)
        last_pred = predict_score(last_original, last_var)
        
        first_scores.append(first_pred)
        last_scores.append(last_pred)
        
        first_cat = "Light" if 0.8 <= first_pred <= 1.0 else "Medium" if 0.6 <= first_pred < 0.8 else "Far" if 0.3 <= first_pred < 0.6 else "Too Low"
        last_cat = "Light" if 0.8 <= last_pred <= 1.0 else "Medium" if 0.6 <= last_pred < 0.8 else "Far" if 0.3 <= last_pred < 0.6 else "Too Low"
        
        print(f"  {i}. {var:25s}")
        print(f"      First: {first_pred:.4f} ({first_cat:8s}), Last: {last_pred:.4f} ({last_cat:8s})")
    
    # Count predicted distribution
    first_light_pred = sum(1 for s in first_scores if 0.8 <= s <= 1.0)
    first_medium_pred = sum(1 for s in first_scores if 0.6 <= s < 0.8)
    first_far_pred = sum(1 for s in first_scores if 0.3 <= s < 0.6)
    
    last_light_pred = sum(1 for s in last_scores if 0.8 <= s <= 1.0)
    last_medium_pred = sum(1 for s in last_scores if 0.6 <= s < 0.8)
    last_far_pred = sum(1 for s in last_scores if 0.3 <= s < 0.6)
    
    print(f"\nPredicted Distribution:")
    print(f"  First: Light {first_light_pred}/8, Medium {first_medium_pred}/8, Far {first_far_pred}/8")
    print(f"  Last:  Light {last_light_pred}/8, Medium {last_medium_pred}/8, Far {last_far_pred}/8")
    
    # Score with actual rewards.py
    print(f"\nActual Scoring with rewards.py:")
    print("-" * 80)
    
    final_score, base_score, metrics = calculate_variation_quality(
        original_name=name,
        variations=variations,
        phonetic_similarity={'Light': 0.2, 'Medium': 0.6, 'Far': 0.2},
        orthographic_similarity={'Light': 0.3, 'Medium': 0.4, 'Far': 0.3},
        expected_count=8,
        rule_based=None
    )
    
    first_metrics = metrics.get('first_name', {}).get('metrics', {})
    last_metrics = metrics.get('last_name', {}).get('metrics', {})
    
    print(f"Final Score: {final_score:.4f}")
    print(f"Base Score: {base_score:.4f}")
    print()
    print("First Name Similarity Score: {:.4f}".format(
        first_metrics.get('similarity', {}).get('combined', 0)
    ))
    print("Last Name Similarity Score: {:.4f}".format(
        last_metrics.get('similarity', {}).get('combined', 0)
    ))
    
    # Compare predicted vs actual
    print(f"\nComparison:")
    print(f"  Predicted First Light: {first_light_pred}/8, Actual Similarity: {first_metrics.get('similarity', {}).get('combined', 0):.4f}")
    print(f"  Predicted Last Light:  {last_light_pred}/8, Actual Similarity: {last_metrics.get('similarity', {}).get('combined', 0):.4f}")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print("""
The smart generator uses reverse-engineered algorithms to predict scores.
This allows us to:
1. ✅ Test variations before sending to validator
2. ✅ Target specific score ranges (Light/Medium/Far)
3. ✅ Generate variations that match target distribution
4. ✅ Work on first and last names separately

The predictions should match the actual validator scores closely!
""")

