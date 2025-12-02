#!/usr/bin/env python3
"""
End-to-End Production Test with Gemini
======================================

This script:
1. Mocks validator query generation
2. Sends query to Gemini-2.5-pro
3. Parses Gemini response
4. Scores with rewards.py
5. Displays detailed results
"""

import sys
import os
import json
import random
import asyncio
import logging
from typing import List, Dict, Any, Tuple
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f'test_gemini_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)
logger = logging.getLogger(__name__)

# Add MIID/validator to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'MIID', 'validator'))

# Import Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    print("❌ google.generativeai not available. Install with: pip install google-generativeai")
    GEMINI_AVAILABLE = False
    sys.exit(1)

# Import rewards
from reward import get_name_variation_rewards
import numpy as np


class MockValidator:
    """Mock validator that generates queries like the real validator"""
    
    DEFAULT_VARIATION_COUNT = 15
    
    def __init__(self):
        self.query_generator = None
    
    def generate_query_parameters(self) -> Dict[str, Any]:
        """Generate query parameters like the real validator"""
        logger.info("="*80)
        logger.info("GENERATING QUERY PARAMETERS")
        logger.info("="*80)
        
        # 1. Variation count
        variation_count = random.randint(6, self.DEFAULT_VARIATION_COUNT)
        logger.info(f"Variation count: {variation_count}")
        
        # 2. Phonetic similarity (weighted selection)
        phonetic_configs_with_weights = [
            ({"Light": 0.3, "Medium": 0.4, "Far": 0.3}, 0.25),
            ({"Light": 0.2, "Medium": 0.6, "Far": 0.2}, 0.20),
            ({"Light": 0.1, "Medium": 0.3, "Far": 0.6}, 0.15),
            ({"Light": 0.5, "Medium": 0.5}, 0.12),
            ({"Light": 0.1, "Medium": 0.5, "Far": 0.4}, 0.10),
            ({"Medium": 1.0}, 0.08),
            ({"Light": 0.7, "Medium": 0.3}, 0.05),
            ({"Far": 1.0}, 0.03),
            ({"Light": 1.0}, 0.02),
        ]
        
        weights = [w for _, w in phonetic_configs_with_weights]
        selected = random.choices(
            phonetic_configs_with_weights,
            weights=weights,
            k=1
        )[0]
        phonetic_similarity = selected[0]
        logger.info(f"Phonetic similarity: {phonetic_similarity}")
        
        # 3. Orthographic similarity (same approach)
        orthographic_configs_with_weights = [
            ({"Light": 0.3, "Medium": 0.4, "Far": 0.3}, 0.25),
            ({"Light": 0.2, "Medium": 0.6, "Far": 0.2}, 0.20),
            ({"Light": 0.1, "Medium": 0.3, "Far": 0.6}, 0.15),
            ({"Light": 0.5, "Medium": 0.5}, 0.12),
            ({"Light": 0.1, "Medium": 0.5, "Far": 0.4}, 0.10),
            ({"Medium": 1.0}, 0.08),
            ({"Light": 0.7, "Medium": 0.3}, 0.05),
            ({"Far": 1.0}, 0.03),
            ({"Light": 1.0}, 0.02),
        ]
        
        weights = [w for _, w in orthographic_configs_with_weights]
        selected = random.choices(
            orthographic_configs_with_weights,
            weights=weights,
            k=1
        )[0]
        orthographic_similarity = selected[0]
        logger.info(f"Orthographic similarity: {orthographic_similarity}")
        
        # 4. Rule percentage
        rule_percentage = random.randint(10, 60)
        logger.info(f"Rule percentage: {rule_percentage}%")
        
        params = {
            "variation_count": variation_count,
            "phonetic_similarity": phonetic_similarity,
            "orthographic_similarity": orthographic_similarity,
            "rule_percentage": rule_percentage
        }
        
        logger.info("="*80)
        logger.info("QUERY PARAMETERS GENERATED")
        logger.info("="*80)
        logger.info(json.dumps(params, indent=2))
        
        return params
    
    def create_test_identities(self, count: int = 15) -> List[Dict[str, str]]:
        """Create test identities from Sanctioned_list.json"""
        logger.info("="*80)
        logger.info("LOADING IDENTITIES FROM SANCTIONED_LIST.JSON")
        logger.info("="*80)
        
        sanctioned_file = os.path.join(os.path.dirname(__file__), 'MIID', 'validator', 'Sanctioned_list.json')
        
        if not os.path.exists(sanctioned_file):
            logger.error(f"❌ Sanctioned_list.json not found at {sanctioned_file}")
            print(f"❌ Sanctioned_list.json not found at {sanctioned_file}")
            # Fallback to default identities
            return [
                {
                    "name": "John Smith",
                    "dob": "1985-03-15",
                    "address": "New York, United States"
                },
                {
                    "name": "Maria Garcia",
                    "dob": "1990-07-22",
                    "address": "Madrid, Spain"
                }
            ]
        
        try:
            with open(sanctioned_file, 'r', encoding='utf-8') as f:
                sanctioned_data = json.load(f)
            
            logger.info(f"Loaded {len(sanctioned_data)} entries from sanctioned list")
            print(f"Loaded {len(sanctioned_data)} entries from sanctioned list")
            
            # Select random 15 entries (or all if less than 15)
            selected = random.sample(sanctioned_data, min(count, len(sanctioned_data)))
            
            identities = []
            for entry in selected:
                first_name = entry.get('FirstName', '')
                last_name = entry.get('LastName', '')
                full_name = f"{first_name} {last_name}".strip()
                
                # Format DOB (convert from "1975-8-11" to "1975-08-11")
                dob_raw = entry.get('DOB', '')
                dob_parts = dob_raw.split('-')
                if len(dob_parts) == 3:
                    year, month, day = dob_parts
                    dob = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                else:
                    dob = dob_raw
                
                # Get address from country
                country = entry.get('Country_Residence', 'Unknown')
                address = f"{country}"
                
                identities.append({
                    "name": full_name,
                    "dob": dob,
                    "address": address
                })
            
            logger.info(f"Selected {len(identities)} identities:")
            print(f"Selected {len(identities)} identities:")
            for i, identity in enumerate(identities, 1):
                logger.info(f"  {i}. {identity['name']} (DOB: {identity['dob']}, Address: {identity['address']})")
                print(f"  {i}. {identity['name']} (DOB: {identity['dob']}, Address: {identity['address']})")
            
            logger.info("="*80)
            print()
            
            return identities
            
        except Exception as e:
            logger.error(f"❌ Error loading sanctioned list: {e}")
            import traceback
            logger.error(traceback.format_exc())
            print(f"❌ Error loading sanctioned list: {e}")
            # Fallback to default
            return [
                {
                    "name": "John Smith",
                    "dob": "1985-03-15",
                    "address": "New York, United States"
                }
            ]
    
    def build_query_template(self, params: Dict[str, Any]) -> str:
        """Build query template like the real validator"""
        logger.info("="*80)
        logger.info("BUILDING QUERY TEMPLATE")
        logger.info("="*80)
        
        variation_count = params["variation_count"]
        phonetic = params["phonetic_similarity"]
        orthographic = params["orthographic_similarity"]
        rule_pct = params["rule_percentage"]
        
        logger.info(f"Template parameters:")
        logger.info(f"  Variation count: {variation_count}")
        logger.info(f"  Phonetic: {phonetic}")
        logger.info(f"  Orthographic: {orthographic}")
        logger.info(f"  Rule percentage: {rule_pct}%")
        
        # Build query template
        query = f"""Generate {variation_count} name variations for the identity below.

REQUIREMENTS:
1. PHONETIC SIMILARITY DISTRIBUTION:
   - Light (high similarity): {phonetic.get('Light', 0)*100:.0f}%
   - Medium (moderate similarity): {phonetic.get('Medium', 0)*100:.0f}%
   - Far (low similarity): {phonetic.get('Far', 0)*100:.0f}%

2. ORTHOGRAPHIC SIMILARITY DISTRIBUTION:
   - Light (high similarity): {orthographic.get('Light', 0)*100:.0f}%
   - Medium (moderate similarity): {orthographic.get('Medium', 0)*100:.0f}%
   - Far (low similarity): {orthographic.get('Far', 0)*100:.0f}%

3. RULE COMPLIANCE: {rule_pct}% of variations must follow transformation rules
   (e.g., character substitutions, transliterations, common misspellings)

4. NAME VARIATIONS:
   - Each variation must be a valid name (no numbers, special chars except hyphens/apostrophes)
   - Variations should sound similar to the original (phonetic similarity)
   - Variations should look similar to the original (orthographic similarity)
   - Follow the exact distribution percentages above

5. DOB VARIATIONS:
   - Generate AT LEAST one variation in EACH category:
     * ±1 day from seed DOB
     * ±3 days from seed DOB
     * ±30 days from seed DOB
     * ±90 days from seed DOB
     * ±365 days from seed DOB
     * Year+Month only (no day, format: YYYY-MM)
   - Each variation must have a different DOB
   - DOB format: YYYY-MM-DD (or YYYY-MM for year+month only)

6. ADDRESS VARIATIONS:
   - Generate unique, realistic addresses within the specified country/city
   - Each variation must have a different address
   - Addresses should be valid format (street, city, country)
   - Use realistic street names, numbers, and locations

OUTPUT FORMAT (JSON):
{{
  "{{name}}": [
    ["name_variation_1", "dob_variation_1", "address_variation_1"],
    ["name_variation_2", "dob_variation_2", "address_variation_2"],
    ...
    ["name_variation_{variation_count}", "dob_variation_{variation_count}", "address_variation_{variation_count}"]
  ]
}}

CRITICAL REQUIREMENTS:
1. Return ONLY valid JSON - no markdown code blocks, no explanations, no text before/after
2. Each variation must be exactly: ["name", "dob", "address"] as a 3-element list
3. Name format: Only letters, hyphens, apostrophes - NO numbers or special characters
4. DOB format: YYYY-MM-DD (or YYYY-MM for year+month only)
5. Address format: Realistic address string (e.g., "123 Main St, New York, United States")
6. Exact count: Generate EXACTLY {variation_count} variations (no more, no less)
7. Follow similarity distributions EXACTLY as specified above
8. Each variation must have UNIQUE name, DOB, and address (no duplicates)

EXAMPLE OUTPUT:
{{
  "John Smith": [
    ["Jon Smith", "1985-03-14", "124 Main Street, New York, United States"],
    ["John Smyth", "1985-03-16", "125 Oak Avenue, New York, United States"],
    ["Jhon Smith", "1985-03-12", "126 Elm Road, New York, United States"]
  ]
}}
"""
        
        logger.info(f"Query template length: {len(query)} characters")
        logger.info("="*80)
        
        return query


class GeminiClient:
    """Client for Gemini API"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-pro"):
        if not GEMINI_AVAILABLE:
            raise ImportError("google.generativeai not available")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.model_name = model_name
    
    def generate_variations(self, identities: List[Dict[str, str]], query_template: str) -> Dict[str, List[List[str]]]:
        """Send query to Gemini and parse response"""
        logger.info("="*80)
        logger.info("GENERATING VARIATIONS WITH GEMINI")
        logger.info("="*80)
        logger.info(f"Model: {self.model_name}")
        logger.info(f"Total identities: {len(identities)}")
        logger.info("="*80)
        
        results = {}
        
        for idx, identity in enumerate(identities, 1):
            name = identity["name"]
            dob = identity["dob"]
            address = identity["address"]
            
            logger.info(f"\n[{idx}/{len(identities)}] Processing: {name}")
            logger.info("-" * 80)
            logger.info(f"DOB: {dob}")
            logger.info(f"Address: {address}")
            
            # Format query with identity details
            formatted_query = query_template.replace("{name}", name)
            formatted_query = formatted_query.replace("{dob}", dob)
            formatted_query = formatted_query.replace("{address}", address)
            
            logger.info(f"Formatted query length: {len(formatted_query)} characters")
            logger.info(f"Query preview (first 500 chars):\n{formatted_query[:500]}...")
            logger.info("-" * 80)
            
            try:
                logger.info(f"Calling Gemini API for {name}...")
                start_time = datetime.now()
                
                # Call Gemini
                response = self.model.generate_content(
                    formatted_query,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.7,
                        max_output_tokens=8192,
                    )
                )
                
                elapsed = (datetime.now() - start_time).total_seconds()
                logger.info(f"✅ Gemini API call completed in {elapsed:.2f} seconds")
                
                response_text = response.text.strip()
                logger.info(f"Response length: {len(response_text)} characters")
                logger.info(f"Response preview (first 500 chars):\n{response_text[:500]}...")
                
                # Clean response (remove markdown code blocks if present)
                if response_text.startswith("```json"):
                    response_text = response_text[7:]
                if response_text.startswith("```"):
                    response_text = response_text[3:]
                if response_text.endswith("```"):
                    response_text = response_text[:-3]
                response_text = response_text.strip()
                
                # Parse JSON
                try:
                    logger.info(f"Parsing JSON response for {name}...")
                    parsed = json.loads(response_text)
                    logger.info(f"Parsed JSON keys: {list(parsed.keys())}")
                    
                    if name in parsed:
                        variations = parsed[name]
                        logger.info(f"✅ Found {len(variations)} variations for {name}")
                        logger.info(f"First variation: {variations[0] if variations else 'None'}")
                        results[name] = variations
                    else:
                        logger.warning(f"⚠️  Name '{name}' not found in response")
                        logger.warning(f"   Available keys: {list(parsed.keys())}")
                        logger.warning(f"   Using first available key if any...")
                        if parsed:
                            first_key = list(parsed.keys())[0]
                            logger.warning(f"   Using key: {first_key}")
                            results[name] = parsed[first_key]
                        else:
                            results[name] = []
                            
                except json.JSONDecodeError as e:
                    logger.error(f"❌ JSON parse error: {e}")
                    logger.error(f"   Response (first 1000 chars): {response_text[:1000]}")
                    results[name] = []
                
            except Exception as e:
                logger.error(f"❌ Error calling Gemini for {name}: {e}")
                import traceback
                logger.error(traceback.format_exc())
                results[name] = []
        
        logger.info("="*80)
        logger.info("VARIATION GENERATION COMPLETE")
        logger.info("="*80)
        logger.info(f"Total identities processed: {len(identities)}")
        logger.info(f"Successful: {sum(1 for v in results.values() if v)}")
        logger.info(f"Failed: {sum(1 for v in results.values() if not v)}")
        for name, variations in results.items():
            logger.info(f"  {name}: {len(variations)} variations")
        logger.info("="*80)
        
        return results


def format_detailed_metrics(metrics: Dict[str, Any], indent: int = 0) -> str:
    """Format detailed metrics in the specified format"""
    lines = []
    prefix = " " * indent
    
    # Final score
    if "final_reward" in metrics:
        lines.append(f"{prefix}Final score")
        lines.append(f"{prefix}{metrics['final_reward']:.3f}")
        lines.append("")
    
    # Names
    if "name_metrics" in metrics:
        lines.append(f"{prefix}Names")
        total_name_score = 0.0
        count = 0
        for name, name_metrics in metrics["name_metrics"].items():
            if "quality_score" in name_metrics:
                total_name_score += name_metrics["quality_score"]
                count += 1
        if count > 0:
            lines.append(f"{prefix}{total_name_score / count:.3f}")
        lines.append("")
    
    # Basic Quality Score
    if "average_quality" in metrics:
        lines.append(f"{prefix}Basic Quality Score")
        lines.append(f"{prefix}{metrics['average_quality']:.3f}")
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
        lines.append(f"{prefix}Similarity Score")
        lines.append(f"{prefix}{sum(similarity_scores) / len(similarity_scores):.3f}")
        lines.append("")
    else:
        # Try to get from average_quality or other sources
        lines.append(f"{prefix}Similarity Score")
        lines.append(f"{prefix}0.000")
        lines.append("")
    
    # Phonetic Similarity
    if "name_metrics" in metrics:
        phonetic_scores = []
        for name_metrics in metrics["name_metrics"].values():
            if "detailed_metrics" in name_metrics:
                dm = name_metrics["detailed_metrics"]
                if "similarity" in dm and "phonetic" in dm["similarity"]:
                    phonetic_scores.append(dm["similarity"]["phonetic"])
        if phonetic_scores:
            lines.append(f"{prefix}Phonetic Similarity")
            lines.append(f"{prefix}{sum(phonetic_scores) / len(phonetic_scores):.3f}")
            lines.append("")
    
    # Orthographic Similarity
    if "name_metrics" in metrics:
        orthographic_scores = []
        for name_metrics in metrics["name_metrics"].values():
            if "detailed_metrics" in name_metrics:
                dm = name_metrics["detailed_metrics"]
                if "similarity" in dm and "orthographic" in dm["similarity"]:
                    orthographic_scores.append(dm["similarity"]["orthographic"])
        if orthographic_scores:
            lines.append(f"{prefix}Orthographic Similarity")
            lines.append(f"{prefix}{sum(orthographic_scores) / len(orthographic_scores):.3f}")
            lines.append("")
    
    # Count Score
    if "name_metrics" in metrics:
        count_scores = []
        for name_metrics in metrics["name_metrics"].values():
            if "detailed_metrics" in name_metrics:
                dm = name_metrics["detailed_metrics"]
                if "count" in dm and "score" in dm["count"]:
                    count_scores.append(dm["count"]["score"])
        if count_scores:
            lines.append(f"{prefix}Count Score")
            lines.append(f"{prefix}{sum(count_scores) / len(count_scores):.3f}")
            lines.append("")
    
    # Uniqueness Score
    if "name_metrics" in metrics:
        uniqueness_scores = []
        for name_metrics in metrics["name_metrics"].values():
            if "detailed_metrics" in name_metrics:
                dm = name_metrics["detailed_metrics"]
                if "uniqueness" in dm and "score" in dm["uniqueness"]:
                    uniqueness_scores.append(dm["uniqueness"]["score"])
        if uniqueness_scores:
            lines.append(f"{prefix}Uniqueness Score")
            lines.append(f"{prefix}{sum(uniqueness_scores) / len(uniqueness_scores):.3f}")
            lines.append("")
    
    # Length Score
    if "name_metrics" in metrics:
        length_scores = []
        for name_metrics in metrics["name_metrics"].values():
            if "detailed_metrics" in name_metrics:
                dm = name_metrics["detailed_metrics"]
                if "length" in dm and "score" in dm["length"]:
                    length_scores.append(dm["length"]["score"])
        if length_scores:
            lines.append(f"{prefix}Length Score")
            lines.append(f"{prefix}{sum(length_scores) / len(length_scores):.3f}")
            lines.append("")
    
    # Rule Compliance Score
    if "name_metrics" in metrics:
        rule_scores = []
        for name_metrics in metrics["name_metrics"].values():
            if "rule_compliance" in name_metrics:
                rc = name_metrics["rule_compliance"]
                # Handle both dict and numeric values
                if isinstance(rc, dict):
                    if "score" in rc:
                        rule_scores.append(float(rc["score"]))
                    elif "compliance_score" in rc:
                        rule_scores.append(float(rc["compliance_score"]))
                elif isinstance(rc, (int, float)):
                    rule_scores.append(float(rc))
        if rule_scores:
            lines.append(f"{prefix}Rule Compliance Score")
            lines.append(f"{prefix}{sum(rule_scores) / len(rule_scores):.3f}")
            lines.append("")
    elif "rule_compliance" in metrics:
        # Check if rule_compliance is at top level
        rc = metrics["rule_compliance"]
        if isinstance(rc, dict) and "score" in rc:
            lines.append(f"{prefix}Rule Compliance Score")
            lines.append(f"{prefix}{rc['score']:.3f}")
            lines.append("")
        elif isinstance(rc, (int, float)):
            lines.append(f"{prefix}Rule Compliance Score")
            lines.append(f"{prefix}{float(rc):.3f}")
            lines.append("")
    
    # Address Score
    if "address_grading" in metrics:
        addr_grading = metrics["address_grading"]
        if isinstance(addr_grading, dict):
            if "overall_score" in addr_grading:
                lines.append(f"{prefix}Address Score")
                lines.append(f"{prefix}{addr_grading['overall_score']:.3f}")
                lines.append("")
        elif isinstance(addr_grading, (int, float)):
            lines.append(f"{prefix}Address Score")
            lines.append(f"{prefix}{float(addr_grading):.3f}")
            lines.append("")
    elif "address_score" in metrics:
        lines.append(f"{prefix}Address Score")
        lines.append(f"{prefix}{metrics['address_score']:.3f}")
        lines.append("")
    
    # DOB Score
    if "dob_grading" in metrics:
        dob_grading = metrics["dob_grading"]
        if isinstance(dob_grading, dict):
            if "overall_score" in dob_grading:
                lines.append(f"{prefix}DOB Score")
                lines.append(f"{prefix}{dob_grading['overall_score']:.3f}")
                lines.append("")
        elif isinstance(dob_grading, (int, float)):
            lines.append(f"{prefix}DOB Score")
            lines.append(f"{prefix}{float(dob_grading):.3f}")
            lines.append("")
    elif "dob_score" in metrics:
        lines.append(f"{prefix}DOB Score")
        lines.append(f"{prefix}{metrics['dob_score']:.3f}")
        lines.append("")
    
    # Penalties
    if "penalties" in metrics:
        penalties = metrics["penalties"]
        lines.append(f"{prefix}Completeness Multiplier")
        if "completeness_multiplier" in metrics:
            lines.append(f"{prefix}{metrics['completeness_multiplier']:.3f}")
        lines.append("")
        
        lines.append(f"{prefix}Extra names penalty")
        lines.append(f"{prefix}{penalties.get('extra_names', 0.0):.3f}")
        lines.append("")
        
        lines.append(f"{prefix}Missing names penalty")
        lines.append(f"{prefix}{penalties.get('missing_names', 0.0):.3f}")
        lines.append("")
        
        lines.append(f"{prefix}Post Penalty")
        if "post_penalty_reward" in metrics:
            lines.append(f"{prefix}{metrics['post_penalty_reward']:.3f}")
        elif "final_reward" in metrics:
            # Use final_reward as post penalty if available
            lines.append(f"{prefix}{metrics['final_reward']:.3f}")
        else:
            lines.append(f"{prefix}0.000")
        lines.append("")
        
        lines.append(f"{prefix}Address Penalty")
        lines.append(f"{prefix}{penalties.get('insufficient_addresses', 0.0):.3f}")
        lines.append("")
        
        lines.append(f"{prefix}Collusion Penalty")
        lines.append(f"{prefix}{penalties.get('collusion', 0.0):.3f}")
        lines.append("")
        
        lines.append(f"{prefix}Duplication Penalty")
        lines.append(f"{prefix}{penalties.get('duplication', 0.0):.3f}")
        lines.append("")
        
        lines.append(f"{prefix}Signature Copy Penalty")
        lines.append(f"{prefix}{penalties.get('signature_copy', 0.0):.3f}")
        lines.append("")
        
        lines.append(f"{prefix}Special Chars Penalty")
        lines.append(f"{prefix}{penalties.get('numbers_in_names', 0.0):.3f}")
        lines.append("")
    
    return "\n".join(lines)


def main():
    """Main test function"""
    print("="*80)
    print("END-TO-END PRODUCTION TEST WITH GEMINI")
    print("="*80)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    logger.info("="*80)
    logger.info("END-TO-END PRODUCTION TEST WITH GEMINI")
    logger.info("="*80)
    logger.info(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("")
    
    # Get Gemini API key from environment
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY environment variable not set")
        print("   Export it: export GEMINI_API_KEY=your_key")
        logger.error("❌ GEMINI_API_KEY environment variable not set")
        logger.error("   Export it: export GEMINI_API_KEY=your_key")
        sys.exit(1)
    
    print("✅ Gemini API key found")
    logger.info("✅ Gemini API key found")
    logger.info("")
    
    # Initialize
    print("Initializing components...")
    logger.info("Initializing components...")
    validator = MockValidator()
    print("✅ MockValidator created")
    gemini = GeminiClient(api_key, model_name="gemini-2.5-pro")
    print("✅ GeminiClient created")
    logger.info("✅ Components initialized")
    logger.info("")
    print()
    
    # Generate query parameters
    print("Generating query parameters...")
    params = validator.generate_query_parameters()
    print(f"✅ Query parameters generated")
    logger.info("")
    print()
    
    # Create test identities from sanctioned list
    print("Loading identities from Sanctioned_list.json...")
    identities = validator.create_test_identities(count=15)
    print(f"✅ Loaded {len(identities)} identities")
    logger.info("")
    print()
    
    # Build query template
    print("Building query template...")
    query_template = validator.build_query_template(params)
    print(f"✅ Query template built ({len(query_template)} characters)")
    logger.info("")
    print()
    
    # Query Gemini
    print("Querying Gemini for variations...")
    print("(This may take 30-60 seconds per identity)")
    variations = gemini.generate_variations(identities, query_template)
    print(f"✅ Received variations for {len(variations)} identities")
    logger.info("")
    print()
    
    # Prepare for rewards.py
    print("="*80)
    print("PREPARING DATA FOR REWARDS.PY")
    print("="*80)
    logger.info("="*80)
    logger.info("PREPARING DATA FOR REWARDS.PY")
    logger.info("="*80)
    
    seed_names = [id["name"] for id in identities]
    seed_dob = [id["dob"] for id in identities]
    seed_addresses = [id["address"] for id in identities]
    seed_script = ["latin"] * len(identities)
    
    print(f"Seed names: {seed_names}")
    print(f"Seed DOB: {seed_dob}")
    print(f"Seed addresses: {seed_addresses}")
    print(f"Variations received: {list(variations.keys())}")
    for name, vars_list in variations.items():
        print(f"  {name}: {len(vars_list)} variations")
        if vars_list:
            print(f"    Sample: {vars_list[0]}")
    logger.info(f"Seed names: {seed_names}")
    logger.info(f"Seed DOB: {seed_dob}")
    logger.info(f"Seed addresses: {seed_addresses}")
    logger.info(f"Variations received: {list(variations.keys())}")
    for name, vars_list in variations.items():
        logger.info(f"  {name}: {len(vars_list)} variations")
        if vars_list:
            logger.info(f"    Sample: {vars_list[0]}")
    print()
    logger.info("")
    
    # Format response for rewards.py
    # rewards.py expects List[Dict[str, List[List[str]]]]
    # Each dict has name -> list of [name, dob, address] tuples
    class MockResponse:
        def __init__(self, variations_dict):
            self.variations = variations_dict
    
    responses = [MockResponse(variations)]  # List of response objects
    uids = [1]  # Mock UID
    
    logger.info(f"Formatted {len(responses)} response(s) for rewards.py")
    logger.info("")
    
    # Create mock self object for rewards.py
    class MockConfig:
        class MockNeuron:
            burn_fraction = 0.40
            top_miner_cap = 10
            quality_threshold = 0.5
            decay_rate = 0.1
            blend_factor = 0.5
    
        def __init__(self):
            self.neuron = self.MockNeuron()
    
    class MockSelf:
        def __init__(self):
            self.uid = 0  # Mock validator UID
            self.config = MockConfig()
    
    mock_self = MockSelf()
    
    # Call rewards.py
    print("="*80)
    print("SCORING WITH REWARDS.PY")
    print("="*80)
    print(f"Calling get_name_variation_rewards()...")
    print(f"  variation_count: {params['variation_count']}")
    print(f"  phonetic_similarity: {params['phonetic_similarity']}")
    print(f"  orthographic_similarity: {params['orthographic_similarity']}")
    print(f"  rule_percentage: {params['rule_percentage']}%")
    print()
    logger.info("="*80)
    logger.info("SCORING WITH REWARDS.PY")
    logger.info("="*80)
    logger.info(f"Calling get_name_variation_rewards()...")
    logger.info(f"  variation_count: {params['variation_count']}")
    logger.info(f"  phonetic_similarity: {params['phonetic_similarity']}")
    logger.info(f"  orthographic_similarity: {params['orthographic_similarity']}")
    logger.info(f"  rule_percentage: {params['rule_percentage']}%")
    logger.info("")
    
    try:
        rewards, updated_uids, detailed_metrics = get_name_variation_rewards(
            mock_self,
            seed_names,
            seed_dob,
            seed_addresses,
            seed_script,
            responses,
            uids,
            variation_count=params["variation_count"],
            phonetic_similarity=params["phonetic_similarity"],
            orthographic_similarity=params["orthographic_similarity"],
            rule_based={"rule_percentage": params["rule_percentage"]}
        )
        
        print("✅ Rewards calculation completed")
        print(f"Reward: {rewards[0]:.6f}")
        print(f"Detailed metrics available: {len(detailed_metrics) > 0}")
        if detailed_metrics:
            print(f"Metrics keys: {list(detailed_metrics[0].keys())}")
        print()
        logger.info("✅ Rewards calculation completed")
        logger.info(f"Reward: {rewards[0]:.6f}")
        logger.info(f"Detailed metrics keys: {list(detailed_metrics[0].keys()) if detailed_metrics else 'None'}")
        logger.info("")
        
    except Exception as e:
        print(f"❌ Error in rewards calculation: {e}")
        import traceback
        print(traceback.format_exc())
        logger.error(f"❌ Error in rewards calculation: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)
    
    # Display results
    print("\n" + "="*80)
    print("RESULTS")
    print("="*80)
    print()
    logger.info("="*80)
    logger.info("RESULTS")
    logger.info("="*80)
    logger.info("")
    
    # Display variations for each name
    print("="*80)
    print("VARIATIONS FROM GEMINI")
    print("="*80)
    print()
    logger.info("="*80)
    logger.info("VARIATIONS FROM GEMINI")
    logger.info("="*80)
    logger.info("")
    
    for name, vars_list in variations.items():
        print(f"Name: {name}")
        print(f"Total variations: {len(vars_list)}")
        print()
        logger.info(f"Name: {name}")
        logger.info(f"Total variations: {len(vars_list)}")
        logger.info("")
        
        for i, var in enumerate(vars_list, 1):
            var_str = f"  {i:2d}. Name: {var[0]:30s} | DOB: {var[1]:12s} | Address: {var[2]}"
            print(var_str)
            logger.info(var_str)
        print()
        logger.info("")
    
    # Display scoring metrics
    if detailed_metrics and len(detailed_metrics) > 0:
        metrics = detailed_metrics[0]
        formatted = format_detailed_metrics(metrics)
        print("="*80)
        print("SCORING METRICS")
        print("="*80)
        print()
        print(formatted)
        logger.info("="*80)
        logger.info("SCORING METRICS")
        logger.info("="*80)
        logger.info("")
        logger.info(formatted)
    else:
        print("⚠️  No detailed metrics available")
        logger.warning("No detailed metrics available")
    
    print()
    print(f"Final Reward: {rewards[0]:.6f}")
    print()
    logger.info(f"Final Reward: {rewards[0]:.6f}")
    logger.info("")
    logger.info("="*80)
    logger.info("TEST COMPLETE")
    logger.info("="*80)
    logger.info(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("")
    
    print("="*80)
    print("TEST COMPLETE")
    print("="*80)
    print(f"✅ Final Reward: {rewards[0]:.6f}")
    print(f"📝 Full logs saved to: test_gemini_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    print()


if __name__ == "__main__":
    main()

