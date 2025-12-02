#!/usr/bin/env python3
"""
Complete scoring test: Generate names/DOBs, attach perfect addresses, and get full score breakdown
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from typing import List, Dict, Any

# Suppress bittensor argument parsing
_saved_argv = sys.argv
sys.argv = [sys.argv[0]]

# Add MIID validator to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'MIID', 'validator'))

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    print("ERROR: google-generativeai not installed")
    GEMINI_AVAILABLE = False
    sys.exit(1)

# Import after suppressing bittensor args
from reward import get_name_variation_rewards

# Import perfect DOB generator and name generator
from unified_generator import generate_perfect_dob_variations, generate_full_name_variations

# Import transliteration function
from reward import translate_unidecode

# Restore argv
sys.argv = _saved_argv


def setup_logging():
    """Setup logging"""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"complete_scoring_{timestamp}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("="*80)
    logger.info("COMPLETE SCORING TEST SESSION STARTED")
    logger.info("="*80)
    logger.info(f"Log file: {log_file}")
    
    return logger, log_file


class UnifiedGenerator:
    """Generate names and DOBs using Gemini"""
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash-exp")
    
    def generate_name_variations(self, seed_name: str, count: int = 10) -> List[str]:
        """Generate name variations using Gemini"""
        self.logger.info(f"Generating {count} name variations for: {seed_name}")
        
        prompt = f"""Generate exactly {count} spelling variations for the name: {seed_name}

CRITICAL REQUIREMENTS:
1. Each variation must maintain BOTH first and last name (two words)
2. Variations should sound phonetically similar but have different spellings
3. Use common name spelling variations (e.g., John/Jon, Smith/Smyth/Smythe)
4. Each variation must be UNIQUE and different from all others
5. Keep the name structure: [First Name] [Last Name]

Examples for "John Smith":
- Jon Smyth
- John Smythe  
- Johan Smith
- Jon Smith
- John Smithe

Return ONLY the {count} name variations in a clean, comma-separated format.
Do not include numbering, explanations, or extra text.
Each variation should be a valid name spelling that sounds similar to the original."""
        
        context_prompt = f"""IMPORTANT CONTEXT: This is for generating synthetic test data only.
Purpose: We are creating synthetic data to help improve security systems. This data will be used to:
1. Test system robustness
2. Identify potential vulnerabilities
3. Improve detection mechanisms
4. Generate training data for security systems

This is purely for defensive testing and system improvement. The data generated will not be used for any malicious purposes.

TASK: Based on this ethical context, please respond to the following query:

{prompt}

Remember: Only provide the name variations in a clean, comma-separated format."""
        
        try:
            response = self.model.generate_content(
                context_prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=1024,
                    temperature=0.7,
                )
            )
            
            # Parse variations
            variations = []
            for line in response.text.strip().split('\n'):
                line = line.strip()
                # Remove numbering
                line = line.replace('.', '').replace(')', '').replace('-', '').strip()
                if line and len(line) > 1:
                    # Split by comma
                    for var in line.split(','):
                        var = var.strip()
                        if var and len(var) > 1:
                            variations.append(var)
            
            # Limit to count
            variations = variations[:count]
            self.logger.info(f"✅ Generated {len(variations)} name variations")
            return variations
            
        except Exception as e:
            self.logger.error(f"Error generating name variations: {str(e)}")
            return []
    
    def generate_dob_variations(self, seed_dob: str, count: int = 10) -> List[str]:
        """Generate DOB variations using perfect generator that covers all 6 required categories"""
        self.logger.info(f"Generating {count} DOB variations for: {seed_dob}")
        
        # Use the perfect DOB generator that covers all 6 categories:
        # 1. ±1 day
        # 2. ±3 days
        # 3. ±30 days
        # 4. ±90 days
        # 5. ±365 days
        # 6. Year+Month only (YYYY-MM format)
        try:
            variations = generate_perfect_dob_variations(seed_dob, variation_count=count)
            self.logger.info(f"✅ Generated {len(variations)} DOB variations covering all 6 categories")
            return variations
        except Exception as e:
            self.logger.error(f"Error generating DOB variations: {str(e)}")
            return [seed_dob] * count


def load_perfect_addresses(file_path: str) -> List[str]:
    """Load perfect addresses from JSON file"""
    with open(file_path, 'r') as f:
        data = json.load(f)
        return data.get('perfect_addresses', [])


def create_miner_response(
    seed_names: List[str],
    seed_dobs: List[str],
    perfect_addresses: List[str],
    generator: UnifiedGenerator,
    seed_script: List[str],
    variations_per_name: int = 10
) -> Dict[str, List[List[str]]]:
    """Create a miner response format with name/DOB variations and perfect addresses"""
    logger = logging.getLogger(__name__)
    logger.info("Creating miner response...")
    
    variations = {}
    
    for i, (seed_name, seed_dob) in enumerate(zip(seed_names, seed_dobs)):
        logger.info(f"Processing identity {i+1}/{len(seed_names)}: {seed_name}")
        
        # CRITICAL FIX: For non-Latin scripts, transliterate the seed name FIRST, then generate variations
        # This ensures variations have proper phonetic/orthographic similarity with the transliterated seed
        script = seed_script[i] if i < len(seed_script) else "latin"
        if script != "latin":
            logger.info(f"  Transliterating seed name from {script} to Latin script...")
            transliterated_seed = translate_unidecode(seed_name)
            logger.info(f"  Transliterated '{seed_name}' to '{transliterated_seed}'")
            # Use transliterated name for variation generation
            name_to_vary = transliterated_seed
        else:
            name_to_vary = seed_name
        
        # Generate name variations using unified generator (algorithmic, no API calls)
        # Calculate distribution: 20% Light, 60% Medium, 20% Far
        light_count = max(1, int(variations_per_name * 0.2))
        medium_count = max(1, int(variations_per_name * 0.6))
        far_count = max(1, int(variations_per_name * 0.2))
        # Adjust to ensure total equals variations_per_name
        total = light_count + medium_count + far_count
        if total < variations_per_name:
            medium_count += (variations_per_name - total)
        elif total > variations_per_name:
            medium_count -= (total - variations_per_name)
        
        name_vars = generate_full_name_variations(
            name_to_vary,  # Use transliterated name if non-Latin
            light_count=light_count,
            medium_count=medium_count,
            far_count=far_count,
            verbose=False
        )
        if not name_vars or len(name_vars) < variations_per_name:
            # Fallback: repeat if needed
            while len(name_vars) < variations_per_name:
                name_vars.extend(name_vars[:variations_per_name - len(name_vars)])
            name_vars = name_vars[:variations_per_name]
        
        # Variations are already in Latin script (generated from transliterated name)
        if script != "latin":
            logger.info(f"  ✅ Generated {len(name_vars)} variations in Latin script (example: '{name_vars[0] if name_vars else 'N/A'}')")
        
        # Generate DOB variations
        dob_vars = generator.generate_dob_variations(seed_dob, variations_per_name)
        if not dob_vars:
            dob_vars = [seed_dob] * variations_per_name
        
        # Use perfect addresses (cycle if needed)
        address_vars = []
        for j in range(variations_per_name):
            addr_idx = (i * variations_per_name + j) % len(perfect_addresses)
            address_vars.append(perfect_addresses[addr_idx])
        
        # Create variations: [name_var, dob_var, address_var]
        name_variations = []
        for name_var, dob_var, addr_var in zip(name_vars, dob_vars, address_vars):
            name_variations.append([name_var, dob_var, addr_var])
        
        variations[seed_name] = name_variations
        logger.info(f"  Created {len(name_variations)} variations for {seed_name}")
    
    return variations


def format_score_display(detailed_metrics: Dict[str, Any]) -> str:
    """Format the detailed score breakdown"""
    output = []
    output.append("="*80)
    output.append("FINAL SCORE BREAKDOWN")
    output.append("="*80)
    
    # Final score
    final_score = detailed_metrics.get('final_reward', 0.0)
    output.append(f"\nFinal score\n{final_score:.3f}")
    
    # Names section
    output.append("\nNames")
    name_metrics = detailed_metrics.get('name_metrics', {})
    if name_metrics:
        # Extract metrics from nested structure
        # Each name_metrics[name] contains: first_name, last_name, base_score, final_score, rule_compliance
        all_final_scores = []
        all_base_scores = []
        all_phonetic = []
        all_orthographic = []
        all_similarity = []
        all_count = []
        all_uniqueness = []
        all_length = []
        all_rule = []
        
        for name, metrics in name_metrics.items():
            # Final score (overall quality for this name)
            final_score = metrics.get('final_score', 0.0)
            all_final_scores.append(final_score)
            
            # Base score
            base_score = metrics.get('base_score', 0.0)
            all_base_scores.append(base_score)
            
            # Extract from first_name metrics
            first_name = metrics.get('first_name', {})
            first_metrics = first_name.get('metrics', {})
            
            # Similarity metrics
            similarity = first_metrics.get('similarity', {})
            phonetic = similarity.get('phonetic', 0.0)
            orthographic = similarity.get('orthographic', 0.0)
            combined = similarity.get('combined', 0.0)
            
            all_phonetic.append(phonetic)
            all_orthographic.append(orthographic)
            all_similarity.append(combined)
            
            # Count metrics
            count_metrics = first_metrics.get('count', {})
            count_score = count_metrics.get('score', 0.0)
            all_count.append(count_score)
            
            # Uniqueness metrics
            uniqueness_metrics = first_metrics.get('uniqueness', {})
            uniqueness_score = uniqueness_metrics.get('score', 0.0)
            all_uniqueness.append(uniqueness_score)
            
            # Length metrics
            length_metrics = first_metrics.get('length', {})
            length_score = length_metrics.get('score', 0.0)
            all_length.append(length_score)
            
            # Rule compliance
            rule_compliance = metrics.get('rule_compliance', {})
            rule_score = rule_compliance.get('score', 0.0) if rule_compliance else 0.0
            all_rule.append(rule_score)
        
        # Calculate averages
        avg_final = sum(all_final_scores) / len(all_final_scores) if all_final_scores else 0.0
        avg_base = sum(all_base_scores) / len(all_base_scores) if all_base_scores else 0.0
        avg_phonetic = sum(all_phonetic) / len(all_phonetic) if all_phonetic else 0.0
        avg_orthographic = sum(all_orthographic) / len(all_orthographic) if all_orthographic else 0.0
        avg_similarity = sum(all_similarity) / len(all_similarity) if all_similarity else 0.0
        avg_count = sum(all_count) / len(all_count) if all_count else 0.0
        avg_uniqueness = sum(all_uniqueness) / len(all_uniqueness) if all_uniqueness else 0.0
        avg_length = sum(all_length) / len(all_length) if all_length else 0.0
        avg_rule = sum(all_rule) / len(all_rule) if all_rule else 0.0
        
        output.append(f"{avg_final:.3f}")
        
        # Basic Quality Score (base_score)
        output.append("\nBasic Quality Score")
        output.append(f"{avg_base:.3f}")
        
        # Similarity Score
        output.append("\nSimilarity Score")
        output.append(f"{avg_similarity:.3f}")
        
        # Phonetic Similarity
        output.append("\nPhonetic Similarity")
        output.append(f"{avg_phonetic:.3f}")
        
        # Orthographic Similarity
        output.append("\nOrthographic Similarity")
        output.append(f"{avg_orthographic:.3f}")
        
        # Count Score
        output.append("\nCount Score")
        output.append(f"{avg_count:.3f}")
        
        # Uniqueness Score
        output.append("\nUniqueness Score")
        output.append(f"{avg_uniqueness:.3f}")
        
        # Length Score
        output.append("\nLength Score")
        output.append(f"{avg_length:.3f}")
        
        # Rule Compliance Score
        output.append("\nRule Compliance Score")
        output.append(f"{avg_rule:.3f}")
    else:
        # No name metrics
        output.append("0.000")
        output.append("\nBasic Quality Score\n0.000")
        output.append("\nSimilarity Score\n0.000")
        output.append("\nPhonetic Similarity\n0.000")
        output.append("\nOrthographic Similarity\n0.000")
        output.append("\nCount Score\n0.000")
        output.append("\nUniqueness Score\n0.000")
        output.append("\nLength Score\n0.000")
        output.append("\nRule Compliance Score\n0.000")
    
    # Address Score
    address_grading = detailed_metrics.get('address_grading', {})
    address_score = address_grading.get('overall_score', 0.0)
    output.append("\nAddress Score")
    output.append(f"{address_score:.3f}")
    
    # Address sub-scores
    addr_breakdown = address_grading.get('detailed_breakdown', {})
    output.append("\nLooks Like Address")
    looks_like = 1.0 if address_grading.get('heuristic_perfect', False) else 0.0
    output.append(f"{looks_like:.3f}")
    
    output.append("\nAddress Region Match")
    region_matches = address_grading.get('region_matches', 0)
    total_addresses = address_grading.get('total_addresses', 1)
    region_score = region_matches / total_addresses if total_addresses > 0 else 0.0
    output.append(f"{region_score:.3f}")
    
    output.append("\nAddress API call")
    api_result = address_grading.get('api_result', 'FAILED')
    api_score = 1.0 if api_result == 'SUCCESS' else 0.0
    output.append(f"{api_score:.3f}")
    
    # DOB Score
    dob_grading = detailed_metrics.get('dob_grading', {})
    dob_score = dob_grading.get('overall_score', 0.0)
    output.append("\nDOB Score")
    output.append(f"{dob_score:.3f}")
    
    # Completeness Multiplier
    completeness = detailed_metrics.get('completeness_multiplier', 1.0)
    output.append("\nCompleteness Multiplier")
    output.append(f"{completeness:.3f}")
    
    # Penalties
    penalties = detailed_metrics.get('penalties', {})
    output.append("\nExtra names penalty")
    output.append(f"{penalties.get('extra_names', 0.0):.3f}")
    
    output.append("\nMissing names penalty")
    output.append(f"{penalties.get('missing_names', 0.0):.3f}")
    
    output.append("\nPost Penalty")
    output.append(f"{penalties.get('total_penalty', 0.0):.3f}")
    
    output.append("\nAddress Penalty")
    output.append(f"{penalties.get('insufficient_addresses', 0.0):.3f}")
    
    output.append("\nCollusion Penalty")
    output.append(f"{penalties.get('collusion_penalty', 0.0):.3f}")
    
    output.append("\nDuplication Penalty")
    output.append(f"{penalties.get('duplication_penalty', 0.0):.3f}")
    
    output.append("\nSignature Copy Penalty")
    output.append(f"{penalties.get('signature_copy_penalty', 0.0):.3f}")
    
    output.append("\nSpecial Chars Penalty")
    output.append(f"{penalties.get('special_chars_penalty', 0.0):.3f}")
    
    output.append("="*80)
    
    return "\n".join(output)


def main():
    """Main function"""
    logger, log_file = setup_logging()
    
    # Load perfect addresses
    address_file = "uk_perfect_addresses.json"
    if not os.path.exists(address_file):
        logger.error(f"Address file not found: {address_file}")
        return
    
    logger.info(f"Loading perfect addresses from: {address_file}")
    perfect_addresses = load_perfect_addresses(address_file)
    logger.info(f"✅ Loaded {len(perfect_addresses)} perfect addresses")
    
    # Load names from both sanctioned lists
    transliteration_file = os.path.join(os.path.dirname(__file__), 'MIID', 'validator', 'Sanctioned_Transliteration.json')
    sanctioned_file = os.path.join(os.path.dirname(__file__), 'MIID', 'validator', 'Sanctioned_list.json')
    
    with open(transliteration_file, 'r', encoding='utf-8') as f:
        transliteration_data = json.load(f)
    
    with open(sanctioned_file, 'r', encoding='utf-8') as f:
        sanctioned_data = json.load(f)
    
    logger.info(f"Loaded {len(transliteration_data)} entries from Sanctioned_Transliteration")
    logger.info(f"Loaded {len(sanctioned_data)} entries from Sanctioned_list")
    
    # Select 8 from transliteration list (non-Latin scripts) and 7 from sanctioned list (Latin)
    selected_transliteration = transliteration_data[:8]
    selected_sanctioned = sanctioned_data[:7]
    
    seed_names = []
    seed_dobs = []
    seed_addresses = []
    seed_script = []
    
    # Add names from transliteration list (non-Latin scripts)
    for entry in selected_transliteration:
        first = entry.get('FirstName', '')
        last = entry.get('LastName', '')
        full_name = f"{first} {last}".strip()
        seed_names.append(full_name)
        seed_dobs.append(entry.get('DOB', '1990-01-01'))
        seed_addresses.append(entry.get('Country_Residence', 'United Kingdom'))
        seed_script.append(entry.get('Script', 'latin'))
    
    # Add names from sanctioned list (Latin script)
    for entry in selected_sanctioned:
        first = entry.get('FirstName', '')
        last = entry.get('LastName', '')
        full_name = f"{first} {last}".strip()
        seed_names.append(full_name)
        seed_dobs.append(entry.get('DOB', '1990-01-01'))
        seed_addresses.append(entry.get('Country_Residence', 'United Kingdom'))
        seed_script.append('latin')  # Sanctioned_list entries are Latin
    
    logger.info(f"Selected {len(seed_names)} names from sanctioned list:")
    for i, (name, dob, country, script) in enumerate(zip(seed_names, seed_dobs, seed_addresses, seed_script), 1):
        logger.info(f"  {i:2}. {name:40} | DOB: {dob:12} | Country: {country:20} | Script: {script}")
    
    logger.info(f"Seed names: {seed_names}")
    logger.info(f"Seed DOBs: {seed_dobs}")
    
    # Create generator
    generator = UnifiedGenerator(logger=logger)
    
    # Generate miner response
    logger.info("Generating name and DOB variations...")
    variations = create_miner_response(
        seed_names=seed_names,
        seed_dobs=seed_dobs,
        perfect_addresses=perfect_addresses,
        generator=generator,
        seed_script=seed_script,
        variations_per_name=10
    )
    
    logger.info(f"✅ Created variations for {len(variations)} names")
    
    # Create mock validator (get_name_variation_rewards needs self)
    class MockNeuron:
        burn_fraction = 0.40
        top_miner_cap = 10
        quality_threshold = 0.5
        decay_rate = 0.1
        blend_factor = 0.5
    
    class MockConfig:
        def __init__(self):
            self.neuron = MockNeuron()
    
    class MockValidator:
        def __init__(self):
            self.uid = 101
            self.config = MockConfig()
    
    validator = MockValidator()
    
    # Prepare response format - need to wrap in object or use correct format
    # The function checks: response.variations if hasattr else {}
    # So we need to create an object with .variations attribute
    class ResponseWrapper:
        def __init__(self, variations_dict):
            self.variations = variations_dict
    
    responses = [ResponseWrapper(variations)]
    uids = [501]
    
    logger.info("Calculating rewards...")
    logger.info("="*80)
    
    # Call get_name_variation_rewards (it's a method, so pass self)
    rewards, updated_uids, detailed_metrics = get_name_variation_rewards(
        validator,
        seed_names=seed_names,
        seed_dob=seed_dobs,
        seed_addresses=seed_addresses,
        seed_script=seed_script,
        responses=responses,
        uids=uids,
        variation_count=10
    )
    
    logger.info("="*80)
    logger.info("✅ Reward calculation complete!")
    
    # Display results
    if detailed_metrics and len(detailed_metrics) > 0:
        score_display = format_score_display(detailed_metrics[0])
        logger.info("\n" + score_display)
        print("\n" + score_display)
    
    logger.info(f"\nFinal reward: {rewards[0]:.3f}")
    logger.info(f"UID: {updated_uids[0]}")
    logger.info(f"Log file: {log_file}")
    logger.info("="*80)
    logger.info("SESSION COMPLETED")
    logger.info("="*80)


if __name__ == "__main__":
    main()

