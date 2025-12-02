"""
Exact Match Generator - Matches rewards.py exactly

This script generates name variations using the exact same approach as rewards.py:
1. Gets deterministic weights for algorithms (based on name hash)
2. Generates variations using 51 strategies
3. Scores each variation using the same weighted algorithm approach as rewards.py
4. Categorizes into Light/Medium/Far based on exact score ranges
5. Combines first and last name variations ensuring correct distribution
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'MIID', 'validator'))

import random
import jellyfish
from typing import List, Dict, Tuple, Set

# Import from rewards.py
from reward import get_name_part_weights

# Import variation generation from unified_generator
from unified_generator import generate_candidates


def get_algorithm_weights(original_name: str) -> Tuple[List[str], Dict[str, float]]:
    """
    Get algorithm weights exactly as rewards.py's calculate_phonetic_similarity() does.
    
    This matches calculate_phonetic_similarity() in rewards.py EXACTLY:
    - Seeds random with SHA-256 hash (for cross-machine consistency)
    - Selects 3 algorithms randomly
    - Generates random weights that sum to 1.0
    
    Returns:
        (selected_algorithms, weights_dict)
    """
    # Deterministically seed the random selection based on the original name
    # This matches rewards.py EXACTLY (uses SHA-256 for cross-machine consistency)
    import hashlib
    stable_seed = int(hashlib.sha256(original_name.encode()).hexdigest(), 16) % 10000
    random.seed(stable_seed)
    
    # Available algorithms (same as rewards.py)
    available_algorithms = ["soundex", "metaphone", "nysiis"]
    
    # Select 3 algorithms randomly (same as rewards.py line 156)
    selected_algorithms = random.sample(available_algorithms, k=min(3, len(available_algorithms)))
    
    # Generate random weights that sum to 1.0 (same as rewards.py lines 159-161)
    weights = [random.random() for _ in selected_algorithms]
    total_weight = sum(weights)
    normalized_weights = [w / total_weight for w in weights]
    
    # Create weights dictionary
    weights_dict = {algo: weight for algo, weight in zip(selected_algorithms, normalized_weights)}
    
    return selected_algorithms, weights_dict


def calculate_phonetic_score_exact(original: str, variation: str, selected_algorithms: List[str], weights_dict: Dict[str, float]) -> float:
    """
    Calculate phonetic score exactly as rewards.py does.
    
    Uses the same algorithms and weights as calculate_phonetic_similarity().
    """
    algorithms = {
        "soundex": lambda x, y: 1.0 if jellyfish.soundex(x) == jellyfish.soundex(y) else 0.0,
        "metaphone": lambda x, y: 1.0 if jellyfish.metaphone(x) == jellyfish.metaphone(y) else 0.0,
        "nysiis": lambda x, y: 1.0 if jellyfish.nysiis(x) == jellyfish.nysiis(y) else 0.0,
    }
    
    # Calculate weighted score exactly as rewards.py
    phonetic_score = sum(
        algorithms[algo](original, variation) * weights_dict[algo]
        for algo in selected_algorithms
    )
    
    return float(phonetic_score)


def categorize_by_score(score: float) -> str:
    """
    Categorize variation based on score (exactly as rewards.py does).
    
    rewards.py boundaries (inclusive on both ends):
    - Light: (0.8, 1.0) -> 0.8 <= score <= 1.0
    - Medium: (0.6, 0.8) -> 0.6 <= score <= 0.8
    - Far: (0.3, 0.6) -> 0.3 <= score <= 0.6
    
    Note: A score of exactly 0.8 matches Light, a score of exactly 0.6 matches Medium
    """
    if 0.8 <= score <= 1.0:
        return "Light"
    elif 0.6 <= score <= 0.8:
        return "Medium"
    elif 0.3 <= score <= 0.6:
        return "Far"
    else:
        return "Too Far"


def generate_variations_for_part(
    original: str,
    light_count: int,
    medium_count: int,
    far_count: int,
    selected_algorithms: List[str],
    weights_dict: Dict[str, float],
    max_depth: int = 5,
    max_candidates: int = 50000  # Generate more candidates to ensure we have enough Medium
) -> Dict[str, List[str]]:
    """
    Generate variations for a single name part (first or last).
    
    Uses 51 strategies from unified_generator and scores each variation
    using the exact same method as rewards.py.
    
    If Medium variations are not found, increases recursion depth and candidate limits.
    """
    # Start with initial limits
    current_depth = max_depth
    current_max_candidates = max_candidates
    
    # We need at least medium_count * 3 Medium variations to have enough after re-scoring
    target_medium = medium_count * 3
    
    light_variations = []
    medium_variations = []
    far_variations = []
    seen = set()
    
    # Keep increasing depth and candidates until we find enough Medium variations
    # Use rewards.py scoring from the start to ensure consistency
    from reward import calculate_phonetic_similarity as rewards_phonetic
    
    max_attempts = 10  # Try up to 10 times with increasing limits
    attempt = 0
    
    while len(medium_variations) < target_medium and attempt < max_attempts:
        attempt += 1
        
        # Increase limits for each attempt - be very aggressive
        if attempt > 1:
            current_depth = min(current_depth + 3, 15)  # Increase depth by 3, max 15
            current_max_candidates = min(int(current_max_candidates * 2.5), 2000000)  # 2.5x candidates, max 2M
        
        # Generate candidate variations using 51 strategies
        candidates = generate_candidates(original, max_depth=current_depth, max_candidates=current_max_candidates)
        
        # Score and categorize each candidate using rewards.py scoring
        for var in candidates:
            if var == original or var in seen:
                continue
            seen.add(var)
            
            # Use rewards.py scoring directly to ensure consistency
            score = rewards_phonetic(original, var)
            
            # Categorize using rewards.py boundaries
            if 0.8 <= score <= 1.0:
                category = "Light"
            elif 0.6 <= score <= 0.8:
                category = "Medium"
            elif 0.3 <= score <= 0.6:
                category = "Far"
            else:
                continue  # Skip variations that are too far
            
            # Collect variations - prioritize Medium
            if category == "Medium":
                if var not in medium_variations:
                    medium_variations.append(var)
                    # Stop if we have enough Medium
                    if len(medium_variations) >= target_medium:
                        break
            elif category == "Light":
                if var not in light_variations:
                    light_variations.append(var)
            elif category == "Far":
                if var not in far_variations:
                    far_variations.append(var)
        
        # If we found enough Medium, break
        if len(medium_variations) >= target_medium:
            break
    
    # Continue collecting Light and Far even after we have enough Medium
    # This ensures we have enough of all categories
    for var in seen:
        if var == original:
            continue
        score = rewards_phonetic(original, var)
        if 0.8 <= score <= 1.0:
            if var not in light_variations:
                light_variations.append(var)
        elif 0.3 <= score <= 0.6:
            if var not in far_variations:
                far_variations.append(var)
    
    # Return all variations we found (we'll re-score with rewards.py later)
    return {
        'light': light_variations,
        'medium': medium_variations,
        'far': far_variations
    }


def generate_full_name_variations_exact(
    full_name: str,
    light_count: int = None,
    medium_count: int = None,
    far_count: int = None,
    expected_count: int = 15,
    phonetic_similarity: Dict[str, float] = None,
    verbose: bool = True
) -> List[str]:
    """
    Generate full name variations exactly as rewards.py expects.
    
    Process:
    1. Split into first and last name
    2. Get algorithm weights for each part (deterministic)
    3. Generate variations for each part using 51 strategies
    4. Score and categorize each variation using exact rewards.py method
    5. Build lists with correct distribution
    6. Combine into full names
    
    Args:
        full_name: Full name to generate variations for
        light_count: Number of Light variations (if None, calculated from phonetic_similarity)
        medium_count: Number of Medium variations (if None, calculated from phonetic_similarity)
        far_count: Number of Far variations (if None, calculated from phonetic_similarity)
        expected_count: Total number of variations expected (default: 15)
        phonetic_similarity: Dict with Light, Medium, Far percentages (default: {"Light": 0.3, "Medium": 0.5, "Far": 0.2})
        verbose: Whether to print progress
    """
    # Default phonetic_similarity if not provided
    if phonetic_similarity is None:
        phonetic_similarity = {"Light": 0.3, "Medium": 0.5, "Far": 0.2}
    
    # Calculate counts from percentages if not provided
    if light_count is None:
        light_count = int(phonetic_similarity.get("Light", 0.3) * expected_count)
    if medium_count is None:
        medium_count = int(phonetic_similarity.get("Medium", 0.5) * expected_count)
    if far_count is None:
        far_count = int(phonetic_similarity.get("Far", 0.2) * expected_count)
    
    # Ensure total matches expected_count
    total = light_count + medium_count + far_count
    if total < expected_count:
        # Add to Medium if we're short
        medium_count += (expected_count - total)
    elif total > expected_count:
        # Remove from Medium if we're over
        medium_count = max(0, medium_count - (total - expected_count))
    # Split name
    name_parts = full_name.split()
    if len(name_parts) < 2:
        first_name = full_name
        last_name = None
    else:
        first_name = name_parts[0]
        last_name = name_parts[-1]
    
    if verbose:
        print(f"Generating variations for '{full_name}':")
        print(f"  First name: '{first_name}'")
        if last_name:
            print(f"  Last name: '{last_name}'")
        print()
    
    # Get algorithm weights for first name (deterministic)
    first_selected, first_weights = get_algorithm_weights(first_name)
    if verbose:
        print(f"First name algorithms: {first_selected}")
        print(f"First name weights: {first_weights}")
        print()
    
    # Generate first name variations
    if verbose:
        print(f"Generating first name variations...")
    first_results = generate_variations_for_part(
        first_name,
        light_count,
        medium_count,
        far_count,
        first_selected,
        first_weights
    )
    
    # Re-score and categorize first name variations (ensure exact match)
    first_light = []
    first_medium = []
    first_far = []
    
    all_first = list(set(first_results['light'] + first_results['medium'] + first_results['far']))
    for var in all_first:
        score = calculate_phonetic_score_exact(first_name, var, first_selected, first_weights)
        category = categorize_by_score(score)
        
        if category == "Light" and var not in first_light:
            first_light.append(var)
        elif category == "Medium" and var not in first_medium:
            first_medium.append(var)
        elif category == "Far" and var not in first_far:
            first_far.append(var)
    
    # If not enough Far, use variations close to Far range
    if len(first_far) < far_count:
        # Try Light variations close to Far (0.75-0.8)
        for var in first_light:
            if len(first_far) >= far_count:
                break
            score = calculate_phonetic_score_exact(first_name, var, first_selected, first_weights)
            if 0.75 <= score < 0.8:  # Close to Medium, but we'll use as Far if needed
                if var not in first_far:
                    first_far.append(var)
                    if var in first_light:
                        first_light.remove(var)
    
    # If still not enough Far, use any variation with score < 0.8
    if len(first_far) < far_count:
        for var in all_first:
            if len(first_far) >= far_count:
                break
            if var in first_light or var in first_medium:
                continue
            score = calculate_phonetic_score_exact(first_name, var, first_selected, first_weights)
            if score < 0.8 and var not in first_far:
                first_far.append(var)
    
    if verbose:
        print(f"  First name: {len(first_light)} Light, {len(first_medium)} Medium, {len(first_far)} Far")
        print()
    
    # Generate last name variations
    if last_name:
        # Get algorithm weights for last name (deterministic)
        last_selected, last_weights = get_algorithm_weights(last_name)
        if verbose:
            print(f"Last name algorithms: {last_selected}")
            print(f"Last name weights: {last_weights}")
            print()
        
        if verbose:
            print(f"Generating last name variations...")
        last_results = generate_variations_for_part(
            last_name,
            light_count,
            medium_count,
            far_count,
            last_selected,
            last_weights
        )
        
        # Re-score and categorize last name variations
        last_light = []
        last_medium = []
        last_far = []
        
        all_last = list(set(last_results['light'] + last_results['medium'] + last_results['far']))
        for var in all_last:
            score = calculate_phonetic_score_exact(last_name, var, last_selected, last_weights)
            category = categorize_by_score(score)
            
            if category == "Light" and var not in last_light:
                last_light.append(var)
            elif category == "Medium" and var not in last_medium:
                last_medium.append(var)
            elif category == "Far" and var not in last_far:
                last_far.append(var)
        
        # If not enough Far, use variations close to Far range
        if len(last_far) < far_count:
            for var in all_last:
                if len(last_far) >= far_count:
                    break
                if var in last_light or var in last_medium:
                    continue
                score = calculate_phonetic_score_exact(last_name, var, last_selected, last_weights)
                if score < 0.8 and var not in last_far:
                    last_far.append(var)
        
        if verbose:
            print(f"  Last name: {len(last_light)} Light, {len(last_medium)} Medium, {len(last_far)} Far")
            print()
    else:
        # Single name case
        last_light = [first_name] * (light_count * 3)
        last_medium = [first_name] * (medium_count * 3)
        last_far = [first_name] * (far_count * 3)
    
    # Build lists with correct distribution
    # IMPORTANT: We need EXACTLY light_count Light, medium_count Medium, far_count Far
    # This is critical - rewards.py penalizes heavily if we exceed the target
    first_name_list = []
    
    # Take exactly what we need from each category (no more, no less)
    first_name_list.extend(first_light[:light_count])
    
    # For Medium: take EXACTLY medium_count, not more
    first_name_list.extend(first_medium[:medium_count])
    needed_medium = medium_count - min(len(first_medium), medium_count)
    
    if needed_medium > 0:
        # Use Light variations close to Medium range (0.75-0.8)
        for var in first_light:
            if needed_medium <= 0:
                break
            if var in first_name_list:  # Skip if already added
                continue
            score = calculate_phonetic_score_exact(first_name, var, first_selected, first_weights)
            if 0.75 <= score < 0.8:
                first_name_list.append(var)
                needed_medium -= 1
        
        # If still needed, use any Light variations
        if needed_medium > 0:
            for var in first_light:
                if needed_medium <= 0:
                    break
                if var not in first_name_list:
                    first_name_list.append(var)
                    needed_medium -= 1
        
        # If still needed, use Far variations close to Medium (0.6-0.65)
        if needed_medium > 0:
            for var in first_far:
                if needed_medium <= 0:
                    break
                score = calculate_phonetic_score_exact(first_name, var, first_selected, first_weights)
                if 0.6 <= score < 0.65:
                    first_name_list.append(var)
                    needed_medium -= 1
        
        # If still needed, use any available variations
        if needed_medium > 0:
            all_available = [v for v in (first_light + first_medium + first_far) if v not in first_name_list]
            first_name_list.extend(all_available[:needed_medium])
    
    # Add Far variations
    first_name_list.extend(first_far[:far_count])
    
    # Ensure we have exactly the right count
    while len(first_name_list) < (light_count + medium_count + far_count):
        all_available = first_light + first_medium + first_far
        for var in all_available:
            if var not in first_name_list:
                first_name_list.append(var)
                break
        if len(first_name_list) >= (light_count + medium_count + far_count):
            break
    
    # Build last name list with correct distribution
    # IMPORTANT: We need EXACTLY light_count Light, medium_count Medium, far_count Far
    last_name_list = []
    last_name_list.extend(last_light[:light_count])
    
    # For Medium: take EXACTLY medium_count, not more
    last_name_list.extend(last_medium[:medium_count])
    needed_medium = medium_count - min(len(last_medium), medium_count)
    
    if needed_medium > 0:
        # Fill with Light variations that are close to Medium (0.75-0.8)
        for var in last_light:
            if needed_medium <= 0:
                break
            if var in last_name_list:  # Skip if already added as Light
                continue
            score = calculate_phonetic_score_exact(last_name, var, last_selected, last_weights)
            if 0.75 <= score < 0.8:
                last_name_list.append(var)
                needed_medium -= 1
        
        # If still needed, use any Light variations
        if needed_medium > 0:
            for var in last_light:
                if needed_medium <= 0:
                    break
                if var not in last_name_list:
                    last_name_list.append(var)
                    needed_medium -= 1
        
        # If still needed, use Far variations close to Medium (0.6-0.65)
        if needed_medium > 0:
            for var in last_far:
                if needed_medium <= 0:
                    break
                score = calculate_phonetic_score_exact(last_name, var, last_selected, last_weights)
                if 0.6 <= score < 0.65:
                    last_name_list.append(var)
                    needed_medium -= 1
    
    # Add Far variations
    last_name_list.extend(last_far[:far_count])
    
    # Ensure we have exactly the right count
    while len(first_name_list) < (light_count + medium_count + far_count):
        all_available = first_light + first_medium + first_far
        for var in all_available:
            if var not in first_name_list:
                first_name_list.append(var)
                break
        if len(first_name_list) >= (light_count + medium_count + far_count):
            break
    
    while len(last_name_list) < (light_count + medium_count + far_count):
        all_available = last_light + last_medium + last_far
        for var in all_available:
            if var not in last_name_list:
                last_name_list.append(var)
                break
        if len(last_name_list) >= (light_count + medium_count + far_count):
            break
    
    # IMPORTANT: Re-score and re-categorize using rewards.py's calculate_phonetic_similarity
    # to ensure the distribution matches exactly what rewards.py will see
    from reward import calculate_phonetic_similarity as rewards_phonetic
    
    # Re-categorize first name list using rewards.py scoring
    first_light_final = []
    first_medium_final = []
    first_far_final = []
    
    for var in first_name_list:
        score = rewards_phonetic(first_name, var)
        if 0.8 <= score <= 1.0:
            first_light_final.append(var)
        elif 0.6 <= score <= 0.8:
            first_medium_final.append(var)
        elif 0.3 <= score <= 0.6:
            first_far_final.append(var)
    
    # Re-categorize last name list using rewards.py scoring
    last_light_final = []
    last_medium_final = []
    last_far_final = []
    
    for var in last_name_list:
        score = rewards_phonetic(last_name, var)
        if 0.8 <= score <= 1.0:
            last_light_final.append(var)
        elif 0.6 <= score <= 0.8:
            last_medium_final.append(var)
        elif 0.3 <= score <= 0.6:
            last_far_final.append(var)
    
    # Build final lists with EXACT distribution
    # CRITICAL: Take EXACTLY light_count Light, medium_count Medium, far_count Far
    # No more, no less - rewards.py penalizes heavily if we exceed targets
    
    first_name_list_final = []
    # Take exactly light_count Light (no more!)
    first_name_list_final.extend(first_light_final[:light_count])
    # Take exactly medium_count Medium (no more!)
    first_name_list_final.extend(first_medium_final[:medium_count])
    # Take exactly far_count Far (no more!)
    first_name_list_final.extend(first_far_final[:far_count])
    
    # If we don't have enough Medium, we need to fill from other categories
    # But we must ensure the final distribution matches when rewards.py scores them
    if len(first_medium_final) < medium_count:
        needed_medium = medium_count - len(first_medium_final)
        # Try to find Light variations that score close to Medium (0.75-0.8)
        for var in first_light_final:
            if needed_medium <= 0:
                break
            if var in first_name_list_final:
                continue
            score = rewards_phonetic(first_name, var)
            if 0.75 <= score < 0.8:  # Close to Medium
                # Insert in Medium section
                first_name_list_final.insert(light_count + len(first_medium_final), var)
                needed_medium -= 1
    
    # Ensure we have exactly the right total count
    while len(first_name_list_final) < (light_count + medium_count + far_count):
        all_first = first_light_final + first_medium_final + first_far_final
        for var in all_first:
            if var not in first_name_list_final:
                first_name_list_final.append(var)
                break
    
    last_name_list_final = []
    # Take exactly light_count Light (no more!)
    last_name_list_final.extend(last_light_final[:light_count])
    # Take exactly medium_count Medium (no more!) - THIS IS THE KEY FIX
    last_name_list_final.extend(last_medium_final[:medium_count])  # Only take 7, not 8!
    # Take exactly far_count Far (no more!)
    last_name_list_final.extend(last_far_final[:far_count])
    
    # If we don't have enough Medium, fill from other categories
    if len(last_medium_final) < medium_count:
        needed_medium = medium_count - len(last_medium_final)
        for var in last_light_final:
            if needed_medium <= 0:
                break
            if var in last_name_list_final:
                continue
            score = rewards_phonetic(last_name, var)
            if 0.75 <= score < 0.8:  # Close to Medium
                last_name_list_final.insert(light_count + len(last_medium_final), var)
                needed_medium -= 1
    
    # Ensure we have exactly the right total count
    while len(last_name_list_final) < (light_count + medium_count + far_count):
        all_last = last_light_final + last_medium_final + last_far_final
        for var in all_last:
            if var not in last_name_list_final:
                last_name_list_final.append(var)
                break
    
    # CRITICAL: Final verification - Re-score ALL variations using rewards.py
    # and build lists with EXACTLY the right distribution
    # We need to ensure that when rewards.py scores them, we have exactly:
    # - light_count Light (0.8 <= score <= 1.0)
    # - medium_count Medium (0.6 <= score <= 0.8)  <- EXACTLY 7, not 8!
    # - far_count Far (0.3 <= score <= 0.6)
    
    # Get ALL available variations and score them with rewards.py
    all_first_variations = list(set(first_light + first_medium + first_far))
    all_last_variations = list(set(last_light + last_medium + last_far))
    
    # Score all first name variations with rewards.py
    first_scored = [(var, rewards_phonetic(first_name, var)) for var in all_first_variations]
    first_scored.sort(key=lambda x: x[1], reverse=True)  # Sort by score
    
    # Categorize first name variations
    first_light_final = [var for var, score in first_scored if 0.8 <= score <= 1.0]
    first_medium_final = [var for var, score in first_scored if 0.6 <= score <= 0.8]
    first_far_final = [var for var, score in first_scored if 0.3 <= score <= 0.6]
    
    # Score all last name variations with rewards.py
    last_scored = [(var, rewards_phonetic(last_name, var)) for var in all_last_variations]
    last_scored.sort(key=lambda x: x[1], reverse=True)  # Sort by score
    
    # Categorize last name variations
    last_light_final = [var for var, score in last_scored if 0.8 <= score <= 1.0]
    last_medium_final = [var for var, score in last_scored if 0.6 <= score <= 0.8]
    last_far_final = [var for var, score in last_scored if 0.3 <= score <= 0.6]
    
    # Build final lists with EXACTLY the right counts (no more, no less!)
    # CRITICAL: Take exactly medium_count Medium variations, not more!
    first_verified = []
    first_verified.extend(first_light_final[:light_count])  # Exactly 4
    first_verified.extend(first_medium_final[:medium_count])  # Exactly 7, NOT 8!
    first_verified.extend(first_far_final[:far_count])  # Exactly 3
    
    last_verified = []
    last_verified.extend(last_light_final[:light_count])  # Exactly 4
    last_verified.extend(last_medium_final[:medium_count])  # Exactly 7, NOT 8!
    last_verified.extend(last_far_final[:far_count])  # Exactly 3
    
    # Verify we have exactly the right counts
    if len(first_verified) != (light_count + medium_count + far_count):
        # Fill gaps if needed (shouldn't happen if we have enough variations)
        needed = (light_count + medium_count + far_count) - len(first_verified)
        all_first = first_light_final + first_medium_final + first_far_final
        for var in all_first:
            if var not in first_verified and needed > 0:
                first_verified.append(var)
                needed -= 1
    
    if len(last_verified) != (light_count + medium_count + far_count):
        # Fill gaps if needed
        needed = (light_count + medium_count + far_count) - len(last_verified)
        all_last = last_light_final + last_medium_final + last_far_final
        for var in all_last:
            if var not in last_verified and needed > 0:
                last_verified.append(var)
                needed -= 1
    
    # CRITICAL: Final verification - Re-score the combined variations
    # to ensure the distribution matches exactly what rewards.py will see
    variations = []
    seen = set()
    
    # Build combinations ensuring each position has the right category
    # Structure: [Light×Light, Light×Light, ..., Medium×Medium, Medium×Medium, ..., Far×Far, ...]
    
    # Light combinations (positions 0 to light_count-1)
    for i in range(light_count):
        if i < len(first_verified) and i < len(last_verified):
            combined = f"{first_verified[i]} {last_verified[i]}"
            if combined not in seen:
                variations.append(combined)
                seen.add(combined)
    
    # Medium combinations (positions light_count to light_count+medium_count-1)
    for i in range(medium_count):
        first_idx = light_count + i
        last_idx = light_count + i
        if first_idx < len(first_verified) and last_idx < len(last_verified):
            combined = f"{first_verified[first_idx]} {last_verified[last_idx]}"
            if combined not in seen:
                variations.append(combined)
                seen.add(combined)
    
    # Far combinations (positions light_count+medium_count to end)
    for i in range(far_count):
        first_idx = light_count + medium_count + i
        last_idx = light_count + medium_count + i
        if first_idx < len(first_verified) and last_idx < len(last_verified):
            combined = f"{first_verified[first_idx]} {last_verified[last_idx]}"
            if combined not in seen:
                variations.append(combined)
                seen.add(combined)
    
    # Final verification: Re-score the final variations to ensure exact distribution
    # This is the last check before returning
    if len(variations) == (light_count + medium_count + far_count):
        # Re-score to verify distribution
        final_first_scores = [rewards_phonetic(first_name, v.split()[0]) for v in variations]
        final_last_scores = [rewards_phonetic(last_name, v.split()[-1]) for v in variations]
        
        final_first_light = sum(1 for s in final_first_scores if 0.8 <= s <= 1.0)
        final_first_medium = sum(1 for s in final_first_scores if 0.6 <= s <= 0.8)
        final_first_far = sum(1 for s in final_first_scores if 0.3 <= s <= 0.6)
        
        final_last_light = sum(1 for s in final_last_scores if 0.8 <= s <= 1.0)
        final_last_medium = sum(1 for s in final_last_scores if 0.6 <= s <= 0.8)
        final_last_far = sum(1 for s in final_last_scores if 0.3 <= s <= 0.6)
        
        # If distribution doesn't match, rebuild with correct distribution
        if (final_first_medium != medium_count or final_last_medium != medium_count or
            final_first_light != light_count or final_last_light != light_count or
            final_first_far != far_count or final_last_far != far_count):
            
            # Rebuild variations ensuring exact distribution
            variations = []
            seen = set()
            
            # Get all variations sorted by score
            first_all_scored = sorted([(var, rewards_phonetic(first_name, var)) for var in all_first_variations], 
                                     key=lambda x: x[1], reverse=True)
            last_all_scored = sorted([(var, rewards_phonetic(last_name, var)) for var in all_last_variations], 
                                    key=lambda x: x[1], reverse=True)
            
            # Build lists with exact distribution
            first_final_list = []
            last_final_list = []
            
            # Add Light
            first_final_list.extend([var for var, score in first_all_scored if 0.8 <= score <= 1.0][:light_count])
            last_final_list.extend([var for var, score in last_all_scored if 0.8 <= score <= 1.0][:light_count])
            
            # Add Medium - EXACTLY medium_count, not more!
            first_final_list.extend([var for var, score in first_all_scored if 0.6 <= score <= 0.8][:medium_count])
            last_final_list.extend([var for var, score in last_all_scored if 0.6 <= score <= 0.8][:medium_count])
            
            # Add Far
            first_final_list.extend([var for var, score in first_all_scored if 0.3 <= score <= 0.6][:far_count])
            last_final_list.extend([var for var, score in last_all_scored if 0.3 <= score <= 0.6][:far_count])
            
            # Fill to exact count if needed
            while len(first_final_list) < (light_count + medium_count + far_count):
                for var, score in first_all_scored:
                    if var not in first_final_list:
                        first_final_list.append(var)
                        break
            
            while len(last_final_list) < (light_count + medium_count + far_count):
                for var, score in last_all_scored:
                    if var not in last_final_list:
                        last_final_list.append(var)
                        break
            
            # Combine
            for i in range(light_count + medium_count + far_count):
                first_idx = i % len(first_final_list) if first_final_list else 0
                last_idx = i % len(last_final_list) if last_final_list else 0
                combined = f"{first_final_list[first_idx]} {last_final_list[last_idx]}"
                if combined not in seen:
                    variations.append(combined)
                    seen.add(combined)
                    if len(variations) >= (light_count + medium_count + far_count):
                        break
    first_parts = [v.split()[0] for v in variations]
    last_parts = [v.split()[-1] for v in variations]
    
    # Re-score with rewards.py
    first_rescored = [(var, rewards_phonetic(first_name, var)) for var in first_parts]
    last_rescored = [(var, rewards_phonetic(last_name, var)) for var in last_parts]
    
    # Check distribution
    first_light_actual = sum(1 for _, score in first_rescored if 0.8 <= score <= 1.0)
    first_medium_actual = sum(1 for _, score in first_rescored if 0.6 <= score <= 0.8)
    first_far_actual = sum(1 for _, score in first_rescored if 0.3 <= score <= 0.6)
    
    last_light_actual = sum(1 for _, score in last_rescored if 0.8 <= score <= 1.0)
    last_medium_actual = sum(1 for _, score in last_rescored if 0.6 <= score <= 0.8)
    last_far_actual = sum(1 for _, score in last_rescored if 0.3 <= score <= 0.6)
    
    # If distribution doesn't match, rebuild with exact counts
    if (first_light_actual != light_count or first_medium_actual != medium_count or first_far_actual != far_count or
        last_light_actual != light_count or last_medium_actual != medium_count or last_far_actual != far_count):
        
        # Rebuild first name list with exact distribution
        first_rebuilt = []
        first_rebuilt.extend(first_light_final[:light_count])
        first_rebuilt.extend(first_medium_final[:medium_count])
        first_rebuilt.extend(first_far_final[:far_count])
        
        # Rebuild last name list with exact distribution
        last_rebuilt = []
        last_rebuilt.extend(last_light_final[:light_count])
        last_rebuilt.extend(last_medium_final[:medium_count])
        last_rebuilt.extend(last_far_final[:far_count])
        
        # Rebuild variations
        variations = []
        seen = set()
        
        for i in range(light_count):
            if i < len(first_rebuilt) and i < len(last_rebuilt):
                combined = f"{first_rebuilt[i]} {last_rebuilt[i]}"
                if combined not in seen:
                    variations.append(combined)
                    seen.add(combined)
        
        for i in range(medium_count):
            first_idx = light_count + i
            last_idx = light_count + i
            if first_idx < len(first_rebuilt) and last_idx < len(last_rebuilt):
                combined = f"{first_rebuilt[first_idx]} {last_rebuilt[last_idx]}"
                if combined not in seen:
                    variations.append(combined)
                    seen.add(combined)
        
        for i in range(far_count):
            first_idx = light_count + medium_count + i
            last_idx = light_count + medium_count + i
            if first_idx < len(first_rebuilt) and last_idx < len(last_rebuilt):
                combined = f"{first_rebuilt[first_idx]} {last_rebuilt[last_idx]}"
                if combined not in seen:
                    variations.append(combined)
                    seen.add(combined)
    
    # Ensure exact count
    variations = variations[:(light_count + medium_count + far_count)]
    
    return variations


if __name__ == "__main__":
    # Test with "John Smith"
    full_name = "John Smith"
    
    # Use default phonetic_similarity to calculate correct counts
    phonetic_similarity = {"Light": 0.3, "Medium": 0.5, "Far": 0.2}
    expected_count = 15
    
    light_count = int(phonetic_similarity["Light"] * expected_count)  # 4
    medium_count = int(phonetic_similarity["Medium"] * expected_count)  # 7 (not 8!)
    far_count = int(phonetic_similarity["Far"] * expected_count)  # 3
    
    print("="*80)
    print("EXACT MATCH GENERATOR - Testing with 'John Smith'")
    print("="*80)
    print(f"Target distribution: {light_count} Light, {medium_count} Medium, {far_count} Far")
    print(f"(Based on phonetic_similarity: {phonetic_similarity})")
    print()
    
    variations = generate_full_name_variations_exact(
        full_name=full_name,
        light_count=light_count,
        medium_count=medium_count,
        far_count=far_count,
        expected_count=expected_count,
        phonetic_similarity=phonetic_similarity,
        verbose=True
    )
    
    print()
    print("="*80)
    print("GENERATED VARIATIONS")
    print("="*80)
    for i, var in enumerate(variations, 1):
        print(f"{i:2d}. {var}")
    
    print()
    print("="*80)
    print("VERIFYING WITH REWARDS.PY")
    print("="*80)
    
    # Verify using rewards.py
    from reward import calculate_phonetic_similarity
    
    first_name = "John"
    last_name = "Smith"
    
    first_name_variations = [v.split()[0] for v in variations]
    last_name_variations = [v.split()[-1] for v in variations]
    
    first_light = []
    first_medium = []
    first_far = []
    
    for var in first_name_variations:
        score = calculate_phonetic_similarity(first_name, var)
        if score >= 0.8:
            first_light.append((var, score))
        elif 0.6 <= score <= 0.79:
            first_medium.append((var, score))
        elif 0.3 <= score <= 0.59:
            first_far.append((var, score))
    
    last_light = []
    last_medium = []
    last_far = []
    
    for var in last_name_variations:
        score = calculate_phonetic_similarity(last_name, var)
        if score >= 0.8:
            last_light.append((var, score))
        elif 0.6 <= score <= 0.79:
            last_medium.append((var, score))
        elif 0.3 <= score <= 0.59:
            last_far.append((var, score))
    
    print(f"First name distribution: {len(first_light)} Light, {len(first_medium)} Medium, {len(first_far)} Far")
    print(f"Target: {light_count} Light, {medium_count} Medium, {far_count} Far")
    print()
    print(f"Last name distribution: {len(last_light)} Light, {len(last_medium)} Medium, {len(last_far)} Far")
    print(f"Target: {light_count} Light, {medium_count} Medium, {far_count} Far")
    print()
    
    first_match = (len(first_light) == light_count and 
                   len(first_medium) == medium_count and 
                   len(first_far) == far_count)
    last_match = (len(last_light) == light_count and 
                  len(last_medium) == medium_count and 
                  len(last_far) == far_count)
    
    if first_match and last_match:
        print("✅ PERFECT MATCH!")
    else:
        print("❌ Doesn't match exactly")
        if not first_match:
            print(f"   First name: Light {len(first_light)}/{light_count}, Medium {len(first_medium)}/{medium_count}, Far {len(first_far)}/{far_count}")
        if not last_match:
            print(f"   Last name: Light {len(last_light)}/{light_count}, Medium {len(last_medium)}/{medium_count}, Far {len(last_far)}/{far_count}")
    
    print("="*80)

