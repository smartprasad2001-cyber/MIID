"""
Maximize Orthographic Similarity - Brute Force Generator

This script reverse engineers rewards.py's orthographic similarity calculation
and uses brute force to generate name variations that achieve maximum orthographic scores.

Focus: ONLY orthographic similarity (Levenshtein distance), NOT phonetic similarity.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'MIID', 'validator'))

import Levenshtein
from typing import List, Set, Tuple, Dict, Optional, Any
import itertools
import random
import string

# Import exact function from rewards.py
from reward import calculate_orthographic_similarity

# Import rule evaluator functions for filtering and checking
from rule_evaluator import (
    evaluate_rule_compliance,
    has_double_letters,
    has_diff_adjacent_consonants
)

# Orthographic boundaries from rewards.py (lines 773-777)
ORTHOGRAPHIC_BOUNDARIES = {
    "Light": (0.70, 1.00),   # High similarity range
    "Medium": (0.50, 0.69),  # Moderate similarity range
    "Far": (0.20, 0.49)      # Low similarity range
}


class OrthographicBruteForceGenerator:
    """
    Brute force generator for maximizing orthographic similarity.
    Uses reverse engineering of rewards.py's Levenshtein-based calculation.
    """
    
    def __init__(self, original_name: str, target_distribution: Dict[str, float] = None, rule_based: Dict[str, Any] = None):
        """
        Initialize generator for a given original name.
        
        Args:
            original_name: Original name to generate variations for
            target_distribution: Target distribution, e.g., {"Light": 0.2, "Medium": 0.6, "Far": 0.2}
            rule_based: Dictionary with rule compliance requirements:
                - "selected_rules": List of rule names
                - "rule_percentage": Percentage (0-100) of variations that should follow rules
        """
        self.original_name = original_name.strip()
        self.target_distribution = target_distribution or {"Light": 0.2, "Medium": 0.6, "Far": 0.2}
        self.rule_based = rule_based or {}
        
        # Filter possible rules
        target_rules = self.rule_based.get("selected_rules", []) if self.rule_based else []
        self.possible_rules = self._filter_possible_rules(target_rules)
        
        # Rule percentage (convert to 0.0-1.0)
        rule_percentage = self.rule_based.get("rule_percentage", 30) if self.rule_based else 0
        if isinstance(rule_percentage, int):
            self.rule_percentage = rule_percentage / 100.0
        elif isinstance(rule_percentage, float):
            self.rule_percentage = rule_percentage if rule_percentage <= 1.0 else rule_percentage / 100.0
        else:
            self.rule_percentage = 0.0
        
        # Character substitution maps for similar-looking characters
        self.similar_chars = {
            'a': ['a', 'e', 'o', 'u', 'à', 'á', 'â', 'ã', 'ä', 'å'],
            'e': ['e', 'a', 'i', 'é', 'è', 'ê', 'ë'],
            'i': ['i', 'e', 'y', 'í', 'ì', 'î', 'ï'],
            'o': ['o', 'a', 'u', 'ó', 'ò', 'ô', 'õ', 'ö'],
            'u': ['u', 'o', 'v', 'ú', 'ù', 'û', 'ü'],
            'c': ['c', 'k', 's', 'ç'],
            'k': ['k', 'c', 'q'],
            's': ['s', 'c', 'z', 'ß'],
            'z': ['z', 's'],
            'b': ['b', 'p', 'd'],
            'd': ['d', 'b', 't'],
            'p': ['p', 'b'],
            't': ['t', 'd'],
            'f': ['f', 'ph'],
            'ph': ['ph', 'f'],
            'g': ['g', 'j'],
            'j': ['j', 'g', 'y'],
            'm': ['m', 'n'],
            'n': ['n', 'm'],
            'r': ['r', 'l'],
            'l': ['l', 'r'],
            'v': ['v', 'w', 'u'],
            'w': ['w', 'v'],
            'x': ['x', 'ks'],
            'y': ['y', 'i', 'j'],
        }
        
        # Common character pairs that look similar
        self.visual_similar = [
            ('rn', 'm'), ('cl', 'd'), ('ij', 'y'), ('vv', 'w'),
            ('ii', 'y'), ('nn', 'm'), ('ll', 'i'), ('tt', 't'),
        ]
        
        # Cache for generated variations
        self.generated_variations = {}
        self.scored_variations = {}
    
    def calculate_orthographic_score(self, variation: str) -> float:
        """
        Calculate orthographic similarity using EXACT same method as rewards.py.
        
        Formula: 1.0 - (Levenshtein_distance / max_length)
        
        Args:
            variation: Variation to score
            
        Returns:
            Orthographic similarity score (0.0 to 1.0)
        """
        return calculate_orthographic_similarity(self.original_name, variation)
    
    def categorize_score(self, score: float) -> str:
        """
        Categorize a score into Light, Medium, or Far.
        
        Args:
            score: Orthographic similarity score
            
        Returns:
            Category name: "Light", "Medium", "Far", or "Below" (if < 0.20)
        """
        if score >= 0.70:
            return "Light"
        elif score >= 0.50:
            return "Medium"
        elif score >= 0.20:
            return "Far"
        else:
            return "Below"
    
    def _filter_possible_rules(self, target_rules: List[str]) -> List[str]:
        """
        Filter out rules that are impossible for the given name structure.
        
        Args:
            target_rules: List of rule names to check
            
        Returns:
            List of rules that CAN be applied to this name
        """
        possible_rules = []
        name_parts = self.original_name.split()
        
        for rule in target_rules:
            # Rule: Name parts permutations / initials (require multi-part name)
            if rule in ('name_parts_permutations', 'initial_only_first_name', 
                       'shorten_name_to_initials', 'shorten_name_to_abbreviations'):
                if len(name_parts) < 2:
                    continue  # Skip - single-part name can't use this rule
            
            # Rule: Space removal/replacement (requires a space)
            if rule in ('replace_spaces_with_random_special_characters', 'remove_all_spaces'):
                if ' ' not in self.original_name:
                    continue  # Skip - no spaces in name
            
            # Rule: Double letter replacement (requires double letters)
            if rule == 'replace_double_letters_with_single_letter':
                if not has_double_letters(self.original_name):
                    continue  # Skip - no double letters
            
            # Rule: Adjacent consonant swap (requires swappable consonants)
            if rule == 'swap_adjacent_consonants':
                if not has_diff_adjacent_consonants(self.original_name):
                    continue  # Skip - no swappable consonants
            
            possible_rules.append(rule)
        
        return possible_rules
    
    def generate_single_char_substitution(self, word: str, max_variations: int = 100) -> Set[str]:
        """
        Generate variations by substituting single characters with similar-looking ones.
        
        Strategy: Replace each character with visually similar alternatives.
        """
        variations = set()
        word_lower = word.lower()
        
        for i, char in enumerate(word_lower):
            if char in self.similar_chars:
                for replacement in self.similar_chars[char]:
                    if replacement != char:
                        new_word = word[:i] + replacement + word[i+1:]
                        if new_word != word:
                            variations.add(new_word)
                            if len(variations) >= max_variations:
                                return variations
        
        return variations
    
    def generate_char_insertion(self, word: str, max_variations: int = 50) -> Set[str]:
        """
        Generate variations by inserting characters.
        
        Strategy: Insert similar-looking characters at various positions.
        """
        variations = set()
        word_lower = word.lower()
        
        # Insert at each position
        for i in range(len(word) + 1):
            # Try inserting similar characters to adjacent ones
            if i > 0 and word_lower[i-1] in self.similar_chars:
                for char in self.similar_chars[word_lower[i-1]]:
                    new_word = word[:i] + char + word[i:]
                    if new_word != word:
                        variations.add(new_word)
            
            # Try inserting common characters
            for char in ['a', 'e', 'i', 'o', 'u', 'h', 'y']:
                new_word = word[:i] + char + word[i:]
                if new_word != word:
                    variations.add(new_word)
            
            if len(variations) >= max_variations:
                break
        
        return variations
    
    def generate_char_deletion(self, word: str, max_variations: int = 30) -> Set[str]:
        """
        Generate variations by deleting characters.
        
        Strategy: Remove characters that might be redundant or silent.
        """
        variations = set()
        
        # Delete each character
        for i in range(len(word)):
            new_word = word[:i] + word[i+1:]
            if new_word and new_word != word:
                variations.add(new_word)
            
            if len(variations) >= max_variations:
                break
        
        return variations
    
    def generate_char_transposition(self, word: str, max_variations: int = 30) -> Set[str]:
        """
        Generate variations by transposing adjacent characters.
        
        Strategy: Swap adjacent characters (common typing errors).
        """
        variations = set()
        
        for i in range(len(word) - 1):
            chars = list(word)
            chars[i], chars[i+1] = chars[i+1], chars[i]
            new_word = ''.join(chars)
            if new_word != word:
                variations.add(new_word)
            
            if len(variations) >= max_variations:
                break
        
        return variations
    
    def generate_double_char_variations(self, word: str, max_variations: int = 50) -> Set[str]:
        """
        Generate variations by manipulating double characters.
        
        Strategy: Add/remove double letters, or replace with similar patterns.
        """
        variations = set()
        word_lower = word.lower()
        
        # Find double characters
        for i in range(len(word) - 1):
            if word_lower[i] == word_lower[i+1]:
                # Remove one of the doubles
                new_word = word[:i] + word[i+1:]
                if new_word != word:
                    variations.add(new_word)
                
                # Replace with similar pattern
                char = word_lower[i]
                if char in self.similar_chars:
                    for replacement in self.similar_chars[char]:
                        new_word = word[:i] + replacement + word[i+1:]
                        if new_word != word:
                            variations.add(new_word)
        
        # Add double characters where single exists
        for i in range(len(word)):
            char = word_lower[i]
            if char in string.ascii_lowercase:
                new_word = word[:i] + char + word[i:]
                if new_word != word:
                    variations.add(new_word)
        
        return variations
    
    def generate_visual_similar_replacements(self, word: str, max_variations: int = 50) -> Set[str]:
        """
        Generate variations using visually similar character patterns.
        
        Strategy: Replace patterns like "rn" with "m", "cl" with "d", etc.
        """
        variations = set()
        word_lower = word.lower()
        
        for pattern, replacement in self.visual_similar:
            if pattern in word_lower:
                new_word = word_lower.replace(pattern, replacement)
                if new_word != word_lower:
                    variations.add(new_word)
            
            if replacement in word_lower:
                new_word = word_lower.replace(replacement, pattern)
                if new_word != word_lower:
                    variations.add(new_word)
        
        return variations
    
    # ============================================================================
    # RULE-BASED GENERATION FUNCTIONS
    # ============================================================================
    
    def _apply_double_letter_replacement(self, word: str, max_variations: int = 50) -> Set[str]:
        """Generate variations by replacing double letters with single letters."""
        variations = set()
        word_lower = word.lower()
        
        for i in range(len(word) - 1):
            if word_lower[i] == word_lower[i+1] and word_lower[i].isalpha():
                # Remove one of the double letters
                new_word = word[:i] + word[i+1:]
                if new_word != word:
                    variations.add(new_word)
                    if len(variations) >= max_variations:
                        break
        
        return variations
    
    def _apply_consonant_swap(self, word: str, max_variations: int = 50) -> Set[str]:
        """Generate variations by swapping adjacent consonants."""
        variations = set()
        vowels = "aeiou"
        word_lower = word.lower()
        
        for i in range(len(word) - 1):
            char1 = word_lower[i]
            char2 = word_lower[i+1]
            
            # Check if both are different consonants
            if (char1.isalpha() and char1 not in vowels and
                char2.isalpha() and char2 not in vowels and
                char1 != char2):
                
                # Swap them
                new_word = word[:i] + word[i+1] + word[i] + word[i+2:]
                if new_word != word:
                    variations.add(new_word)
                    if len(variations) >= max_variations:
                        break
        
        return variations
    
    def _apply_letter_deletion(self, word: str, max_variations: int = 50, aggression: int = 1) -> Set[str]:
        """
        Generate variations by deleting letters.
        
        Args:
            word: Original word
            max_variations: Maximum variations to generate
            aggression: Number of letters to delete (1=Light, 2=Medium, 3+=Far)
        """
        variations = set()
        
        if aggression == 1:
            # Light: Delete 1 letter
            for i in range(len(word)):
                if word[i].isalpha():
                    new_word = word[:i] + word[i+1:]
                    if new_word and new_word != word:
                        variations.add(new_word)
                        if len(variations) >= max_variations:
                            break
        elif aggression == 2:
            # Medium: Delete 2 letters
            for i in range(len(word)):
                for j in range(i+1, len(word)):
                    if word[i].isalpha() and word[j].isalpha():
                        new_word = word[:i] + word[i+1:j] + word[j+1:]
                        if new_word and new_word != word and len(new_word) > 0:
                            variations.add(new_word)
                            if len(variations) >= max_variations:
                                return variations
        else:
            # Far: Delete 3+ letters
            for i in range(len(word)):
                for j in range(i+1, len(word)):
                    for k in range(j+1, min(j+4, len(word))):  # Limit to avoid explosion
                        if word[i].isalpha() and word[j].isalpha() and word[k].isalpha():
                            new_word = word[:i] + word[i+1:j] + word[j+1:k] + word[k+1:]
                            if new_word and new_word != word and len(new_word) > 0:
                                variations.add(new_word)
                                if len(variations) >= max_variations:
                                    return variations
        
        return variations
    
    def _apply_vowel_deletion(self, word: str, max_variations: int = 50) -> Set[str]:
        """Generate variations by deleting one vowel."""
        variations = set()
        vowels = "aeiou"
        word_lower = word.lower()
        
        for i in range(len(word)):
            if word_lower[i] in vowels:
                new_word = word[:i] + word[i+1:]
                if new_word and new_word != word:
                    variations.add(new_word)
                    if len(variations) >= max_variations:
                        break
        
        return variations
    
    def _apply_consonant_deletion(self, word: str, max_variations: int = 50) -> Set[str]:
        """Generate variations by deleting one consonant."""
        variations = set()
        vowels = "aeiou"
        word_lower = word.lower()
        
        for i in range(len(word)):
            if word_lower[i].isalpha() and word_lower[i] not in vowels:
                new_word = word[:i] + word[i+1:]
                if new_word and new_word != word:
                    variations.add(new_word)
                    if len(variations) >= max_variations:
                        break
        
        return variations
    
    def _apply_vowel_replacement(self, word: str, max_variations: int = 50) -> Set[str]:
        """Generate variations by replacing vowels with different vowels."""
        variations = set()
        vowels = "aeiou"
        word_lower = word.lower()
        
        for i in range(len(word)):
            if word_lower[i] in vowels:
                for replacement in vowels:
                    if replacement != word_lower[i]:
                        new_word = word[:i] + replacement + word[i+1:]
                        if new_word != word:
                            variations.add(new_word)
                            if len(variations) >= max_variations:
                                return variations
        
        return variations
    
    def _apply_consonant_replacement(self, word: str, max_variations: int = 50) -> Set[str]:
        """Generate variations by replacing consonants with different consonants."""
        variations = set()
        vowels = "aeiou"
        consonants = "bcdfghjklmnpqrstvwxyz"
        word_lower = word.lower()
        
        for i in range(len(word)):
            if word_lower[i].isalpha() and word_lower[i] not in vowels:
                for replacement in consonants:
                    if replacement != word_lower[i]:
                        new_word = word[:i] + replacement + word[i+1:]
                        if new_word != word:
                            variations.add(new_word)
                            if len(variations) >= max_variations:
                                return variations
        
        return variations
    
    def _apply_letter_swap(self, word: str, max_variations: int = 50, aggression: int = 1) -> Set[str]:
        """
        Generate variations by swapping letters.
        
        Args:
            word: Original word
            max_variations: Maximum variations to generate
            aggression: Number of swaps (1=Light, 2=Medium, 3+=Far)
        """
        variations = set()
        
        if aggression == 1:
            # Light: Swap 1 pair of adjacent letters
            for i in range(len(word) - 1):
                if word[i] != word[i+1]:
                    new_word = word[:i] + word[i+1] + word[i] + word[i+2:]
                    if new_word != word:
                        variations.add(new_word)
                        if len(variations) >= max_variations:
                            break
        elif aggression == 2:
            # Medium: Swap 2 pairs of letters (can be non-adjacent)
            for i in range(len(word) - 1):
                for j in range(i+2, len(word) - 1):
                    if word[i] != word[i+1] and word[j] != word[j+1]:
                        # Swap first pair
                        temp = word[:i] + word[i+1] + word[i] + word[i+2:j] + word[j+1] + word[j] + word[j+2:]
                        if temp != word:
                            variations.add(temp)
                            if len(variations) >= max_variations:
                                return variations
        else:
            # Far: Swap multiple pairs or non-adjacent letters
            for i in range(len(word)):
                for j in range(i+2, len(word)):
                    # Swap non-adjacent letters
                    new_word = word[:i] + word[j] + word[i+1:j] + word[i] + word[j+1:]
                    if new_word != word:
                        variations.add(new_word)
                        if len(variations) >= max_variations:
                            return variations
        
        return variations
    
    def _apply_letter_insertion(self, word: str, max_variations: int = 50, aggression: int = 1) -> Set[str]:
        """
        Generate variations by inserting letters.
        
        Args:
            word: Original word
            max_variations: Maximum variations to generate
            aggression: Number of letters to insert (1=Light, 2=Medium, 3+=Far)
        """
        variations = set()
        all_letters = string.ascii_lowercase
        
        if aggression == 1:
            # Light: Insert 1 letter
            for i in range(len(word) + 1):
                for letter in all_letters:
                    new_word = word[:i] + letter + word[i:]
                    if new_word != word:
                        variations.add(new_word)
                        if len(variations) >= max_variations:
                            return variations
        elif aggression == 2:
            # Medium: Insert 2 letters
            for i in range(len(word) + 1):
                for letter1 in all_letters[:13]:  # Limit to avoid explosion
                    for letter2 in all_letters[:13]:
                        new_word = word[:i] + letter1 + letter2 + word[i:]
                        if new_word != word:
                            variations.add(new_word)
                            if len(variations) >= max_variations:
                                return variations
        else:
            # Far: Insert 3+ letters
            for i in range(len(word) + 1):
                for letter1 in all_letters[:10]:
                    for letter2 in all_letters[:10]:
                        for letter3 in all_letters[:10]:
                            new_word = word[:i] + letter1 + letter2 + letter3 + word[i:]
                            if new_word != word:
                                variations.add(new_word)
                                if len(variations) >= max_variations:
                                    return variations
        
        return variations
    
    def _apply_letter_duplication(self, word: str, max_variations: int = 50) -> Set[str]:
        """Generate variations by duplicating a letter."""
        variations = set()
        
        for i in range(len(word)):
            if word[i].isalpha():
                new_word = word[:i] + word[i] + word[i:]
                if new_word != word:
                    variations.add(new_word)
                    if len(variations) >= max_variations:
                        break
        
        return variations
    
    def _apply_space_removal(self, word: str, max_variations: int = 50) -> Set[str]:
        """Generate variations by removing all spaces."""
        variations = set()
        if ' ' in word:
            new_word = word.replace(' ', '')
            if new_word != word:
                variations.add(new_word)
        return variations
    
    def _apply_space_replacement(self, word: str, max_variations: int = 50) -> Set[str]:
        """Generate variations by replacing spaces with special characters."""
        variations = set()
        special_chars = ['_', '-', '.', '']
        
        if ' ' in word:
            for char in special_chars:
                new_word = word.replace(' ', char)
                if new_word != word:
                    variations.add(new_word)
                    if len(variations) >= max_variations:
                        break
        
        return variations
    
    def _apply_first_name_initial(self, word: str, max_variations: int = 50) -> Set[str]:
        """Generate variations by converting first name to initial."""
        variations = set()
        parts = word.split()
        
        if len(parts) >= 2:
            # First name initial with last name
            new_word = parts[0][0] + ". " + " ".join(parts[1:])
            if new_word != word:
                variations.add(new_word)
            # Alternative: no space after dot
            new_word2 = parts[0][0] + "." + " ".join(parts[1:])
            if new_word2 != word and new_word2 != new_word:
                variations.add(new_word2)
        
        return variations
    
    def _apply_initials(self, word: str, max_variations: int = 50) -> Set[str]:
        """Generate variations by converting name to initials."""
        variations = set()
        parts = word.split()
        
        if len(parts) >= 2:
            # With dots and spaces: "J. S."
            new_word = ". ".join([p[0] for p in parts]) + "."
            if new_word != word:
                variations.add(new_word)
            # With dots no spaces: "J.S."
            new_word2 = ".".join([p[0] for p in parts]) + "."
            if new_word2 != word and new_word2 != new_word:
                variations.add(new_word2)
            # No dots: "JS"
            new_word3 = "".join([p[0] for p in parts])
            if new_word3 != word and new_word3 != new_word and new_word3 != new_word2:
                variations.add(new_word3)
        
        return variations
    
    def _apply_abbreviation(self, word: str, max_variations: int = 50) -> Set[str]:
        """Generate variations by abbreviating name parts."""
        variations = set()
        parts = word.split()
        
        if len(parts) >= 2:
            # Abbreviate first name
            if len(parts[0]) > 2:
                abbrev = parts[0][:2] + " " + " ".join(parts[1:])
                if abbrev != word:
                    variations.add(abbrev)
            # Abbreviate last name
            if len(parts[-1]) > 2:
                abbrev = " ".join(parts[:-1]) + " " + parts[-1][:2]
                if abbrev != word:
                    variations.add(abbrev)
        
        return variations
    
    def _apply_name_permutation(self, word: str, max_variations: int = 50) -> Set[str]:
        """Generate variations by permuting name parts."""
        variations = set()
        parts = word.split()
        
        if len(parts) >= 2:
            # Generate all permutations
            from itertools import permutations
            for perm in permutations(parts):
                new_word = " ".join(perm)
                if new_word != word:
                    variations.add(new_word)
                    if len(variations) >= max_variations:
                        break
        
        return variations
    
    def _apply_special_character_replacement(self, word: str, max_variations: int = 50) -> Set[str]:
        """Generate variations by replacing special characters with different special characters."""
        variations = set()
        special_chars = '!@#$%^&*()_+-=[]{}|;:,.<>?'
        
        for i in range(len(word)):
            if word[i] in special_chars:
                for replacement in special_chars:
                    if replacement != word[i]:
                        new_word = word[:i] + replacement + word[i+1:]
                        if new_word != word:
                            variations.add(new_word)
                            if len(variations) >= max_variations:
                                return variations
        
        return variations
    
    def _apply_special_character_removal(self, word: str, max_variations: int = 50) -> Set[str]:
        """Generate variations by removing special characters."""
        variations = set()
        special_chars = '!@#$%^&*()_+-=[]{}|;:,.<>?'
        
        for i in range(len(word)):
            if word[i] in special_chars:
                new_word = word[:i] + word[i+1:]
                if new_word and new_word != word:
                    variations.add(new_word)
                    if len(variations) >= max_variations:
                        break
        
        return variations
    
    def _apply_title_removal(self, word: str, max_variations: int = 50) -> Set[str]:
        """Generate variations by removing title prefix."""
        variations = set()
        titles = ["Mr.", "Mrs.", "Ms.", "Mr", "Mrs", "Ms", "Miss", "Dr.", "Dr",
                  "Prof.", "Prof", "Sir", "Lady", "Lord", "Dame", "Master", "Mistress",
                  "Rev.", "Hon.", "Capt.", "Col.", "Lt.", "Sgt.", "Maj."]
        
        word_lower = word.lower()
        for title in titles:
            title_lower = title.lower()
            if word_lower.startswith(title_lower + " "):
                # Remove title
                new_word = word[len(title):].strip()
                if new_word and new_word != word:
                    variations.add(new_word)
                    if len(variations) >= max_variations:
                        break
        
        return variations
    
    def _apply_title_addition(self, word: str, max_variations: int = 50) -> Set[str]:
        """Generate variations by adding title prefix."""
        variations = set()
        titles = ["Mr.", "Mrs.", "Ms.", "Mr", "Mrs", "Ms", "Miss", "Dr.", "Dr",
                  "Prof.", "Prof", "Sir", "Lady", "Lord", "Dame", "Master", "Mistress",
                  "Rev.", "Hon.", "Capt.", "Col.", "Lt.", "Sgt.", "Maj."]
        
        for title in titles:
            new_word = f"{title} {word}"
            if new_word != word:
                variations.add(new_word)
                if len(variations) >= max_variations:
                    break
        
        return variations
    
    def _apply_suffix_addition(self, word: str, max_variations: int = 50) -> Set[str]:
        """Generate variations by adding suffix."""
        variations = set()
        suffixes = ["Jr.", "Sr.", "III", "IV", "V", "PhD", "MD", "Esq.", "Jr", "Sr"]
        
        for suffix in suffixes:
            new_word = f"{word} {suffix}"
            if new_word != word:
                variations.add(new_word)
                if len(variations) >= max_variations:
                    break
        
        return variations
    
    def _apply_syllable_swap(self, word: str, max_variations: int = 50) -> Set[str]:
        """Generate variations by swapping adjacent syllables (simplified to adjacent letter swap)."""
        # Simplified: same as letter swap since syllable detection is complex
        return self._apply_letter_swap(word, max_variations)
    
    def generate_rule_compliant_variations(self, word: str, rules: List[str], max_per_rule: int = 100, aggression: int = 1) -> Set[str]:
        """
        Generate variations that follow specific rules.
        
        Args:
            word: Original word
            rules: List of rule names to apply
            max_per_rule: Maximum variations per rule
            aggression: Aggression level (1=Light, 2=Medium, 3+=Far)
            
        Returns:
            Set of rule-compliant variations
        """
        variations = set()
        
        rule_generators = {
            "replace_double_letters_with_single_letter": self._apply_double_letter_replacement,
            "swap_adjacent_consonants": self._apply_consonant_swap,
            "delete_random_letter": lambda w, m: self._apply_letter_deletion(w, m, aggression),
            "remove_random_vowel": self._apply_vowel_deletion,
            "remove_random_consonant": self._apply_consonant_deletion,
            "replace_random_vowel_with_random_vowel": self._apply_vowel_replacement,
            "replace_random_consonant_with_random_consonant": self._apply_consonant_replacement,
            "replace_random_special_character_with_random_special_character": self._apply_special_character_replacement,
            "swap_random_letter": lambda w, m: self._apply_letter_swap(w, m, aggression),
            "swap_adjacent_syllables": self._apply_syllable_swap,
            "insert_random_letter": lambda w, m: self._apply_letter_insertion(w, m, aggression),
            "duplicate_random_letter_as_double_letter": self._apply_letter_duplication,
            "remove_all_spaces": self._apply_space_removal,
            "replace_spaces_with_random_special_characters": self._apply_space_replacement,
            "remove_random_special_character": self._apply_special_character_removal,
            "remove_title": self._apply_title_removal,
            "add_random_leading_title": self._apply_title_addition,
            "add_random_trailing_title": self._apply_suffix_addition,
            "initial_only_first_name": self._apply_first_name_initial,
            "shorten_name_to_initials": self._apply_initials,
            "shorten_name_to_abbreviations": self._apply_abbreviation,
            "name_parts_permutations": self._apply_name_permutation,
        }
        
        for rule in rules:
            if rule in rule_generators:
                rule_variations = rule_generators[rule](word, max_per_rule)
                variations.update(rule_variations)
        
        return variations
    
    def generate_rule_compliant_variations_with_scores(
        self,
        max_per_rule: int = 100
    ) -> Dict[str, List[Tuple[str, float, str]]]:
        """
        Generate rule-compliant variations and score them for orthographic similarity.
        
        Returns:
            Dictionary mapping rule_name -> [(variation, orthographic_score, category), ...]
        """
        rule_compliant_scored = {}
        
        for rule in self.possible_rules:
            # Generate variations following this rule
            rule_variations = self.generate_rule_compliant_variations(
                self.original_name,
                [rule],
                max_per_rule
            )
            
            # Score each variation for orthographic similarity
            scored_variations = []
            for var in rule_variations:
                score = self.calculate_orthographic_score(var)
                category = self.categorize_score(score)
                scored_variations.append((var, score, category))
            
            # Sort by score (descending) to prioritize high-similarity variations
            scored_variations.sort(key=lambda x: x[1], reverse=True)
            
            rule_compliant_scored[rule] = scored_variations
        
        return rule_compliant_scored
    
    def generate_rule_compliant_by_category(
        self,
        category: str,
        rules: List[str],
        max_per_rule: int = 50
    ) -> List[Tuple[str, float, str]]:
        """
        Generate rule-compliant variations targeting a specific orthographic category.
        
        Strategy:
        - Light: Use single-letter operations (delete/insert/swap 1 letter)
        - Medium: Use rules that naturally produce medium similarity (space removal, vowel replacement)
        - Far: Use rules that naturally produce far similarity (initials, abbreviations, permutations)
        
        Args:
            category: Target category ("Light", "Medium", or "Far")
            rules: List of rule names to apply
            max_per_rule: Maximum variations per rule
            
        Returns:
            List of (variation, score, category) tuples
        """
        target_range = {
            "Light": (0.70, 1.00),
            "Medium": (0.50, 0.69),
            "Far": (0.20, 0.49)
        }[category]
        
        variations = []
        
        # For Light: Use single-letter operations (aggression=1)
        # For Medium/Far: Use rules that naturally produce those similarity levels
        if category == "Light":
            # Light: Single-letter operations
            aggression = 1
            rule_variations = self.generate_rule_compliant_variations(
                self.original_name,
                rules,
                max_per_rule,
                aggression=aggression
            )
        elif category == "Medium":
            # Medium: Use rules that produce moderate changes
            # Filter rules to those that can produce Medium similarity
            medium_rules = [
                r for r in rules if r in [
                    "remove_all_spaces",
                    "replace_spaces_with_random_special_characters",
                    "replace_random_vowel_with_random_vowel",
                    "replace_random_consonant_with_random_consonant",
                    "duplicate_random_letter_as_double_letter"
                ]
            ]
            if not medium_rules:
                # Fallback: Use single-letter operations but filter for Medium scores
                medium_rules = rules
            
            rule_variations = self.generate_rule_compliant_variations(
                self.original_name,
                medium_rules if medium_rules else rules,
                max_per_rule,
                aggression=1
            )
        else:  # Far
            # Far: Use rules that produce large changes
            far_rules = [
                r for r in rules if r in [
                    "shorten_name_to_initials",
                    "shorten_name_to_abbreviations",
                    "name_parts_permutations",
                    "initial_only_first_name"
                ]
            ]
            if not far_rules:
                # Fallback: Use single-letter operations but filter for Far scores
                far_rules = rules
            
            rule_variations = self.generate_rule_compliant_variations(
                self.original_name,
                far_rules if far_rules else rules,
                max_per_rule,
                aggression=1
            )
        
        # Score and filter by target range
        for var in rule_variations:
            score = self.calculate_orthographic_score(var)
            if target_range[0] <= score <= target_range[1]:
                variations.append((var, score, category))
        
        # Sort by score (descending for Light, closest to middle for Medium/Far)
        if category == "Light":
            variations.sort(key=lambda x: x[1], reverse=True)
        elif category == "Medium":
            variations.sort(key=lambda x: abs(x[1] - 0.60))
        else:  # Far
            variations.sort(key=lambda x: abs(x[1] - 0.35))
        
        return variations
    
    def generate_all_strategies_comprehensive(self, word: str, max_candidates: int = 2000000, max_depth: int = 6) -> Set[str]:
        """
        Generate variations using ALL 50 strategies from unified_generator.py.
        This is a comprehensive brute force approach to find Far variations.
        """
        candidates = set()
        tested = set()
        
        vowels = ['a', 'e', 'i', 'o', 'u', 'y']
        all_letters = 'abcdefghijklmnopqrstuvwxyz'
        consonants = 'bcdfghjklmnpqrstvwxyz'
        
        def add_candidate(var: str):
            """Helper to add candidate if valid."""
            if var and var != word and var not in tested and len(var) > 0:
                if len(var) >= 1 and len(var) <= len(word) + 5:
                    tested.add(var)
                    candidates.add(var)
                    return True
            return False
        
        def generate_level(w: str, depth: int = 0):
            """Recursively generate variations using all strategies."""
            if depth >= max_depth or len(candidates) >= max_candidates:
                return
            
            # Strategy 1: Remove single letters
            for i in range(len(w)):
                var = w[:i] + w[i+1:]
                if add_candidate(var) and depth < max_depth - 1:
                    generate_level(var, depth + 1)
            
            # Strategy 2: Add vowels at different positions
            for pos in range(len(w) + 1):
                for v in vowels:
                    var = w[:pos] + v + w[pos:]
                    if add_candidate(var) and depth < max_depth - 1:
                        generate_level(var, depth + 1)
            
            # Strategy 3: Change vowels
            for i, char in enumerate(w):
                if char.lower() in vowels:
                    for v in vowels:
                        if v != char.lower():
                            var = w[:i] + v + w[i+1:]
                            if add_candidate(var) and depth < max_depth - 1:
                                generate_level(var, depth + 1)
            
            # Strategy 4: Change consonants (all consonants)
            for i, char in enumerate(w):
                if char.lower() in consonants:
                    for c in consonants:
                        if c != char.lower():
                            var = w[:i] + c + w[i+1:]
                            if add_candidate(var) and depth < max_depth - 1:
                                generate_level(var, depth + 1)
            
            # Strategy 5: Swap adjacent letters
            for i in range(len(w) - 1):
                var = w[:i] + w[i+1] + w[i] + w[i+2:]
                if add_candidate(var) and depth < max_depth - 1:
                    generate_level(var, depth + 1)
            
            # Strategy 6: Swap non-adjacent letters
            for i in range(len(w)):
                for j in range(i+2, len(w)):
                    var = w[:i] + w[j] + w[i+1:j] + w[i] + w[j+1:]
                    if add_candidate(var) and depth < max_depth - 1:
                        generate_level(var, depth + 1)
            
            # Strategy 7: Add ALL letters at ALL positions
            for pos in range(len(w) + 1):
                for letter in all_letters:
                    var = w[:pos] + letter + w[pos:]
                    if add_candidate(var) and depth < max_depth - 1:
                        generate_level(var, depth + 1)
            
            # Strategy 8: Remove multiple letters (2 letters)
            if len(w) > 3:
                for i in range(len(w)):
                    for j in range(i+1, len(w)):
                        var = w[:i] + w[i+1:j] + w[j+1:]
                        if add_candidate(var) and depth < max_depth - 1:
                            generate_level(var, depth + 1)
            
            # Strategy 9: Remove 3 letters
            if len(w) > 4:
                for i in range(len(w)):
                    for j in range(i+1, len(w)):
                        for k in range(j+1, len(w)):
                            var = w[:i] + w[i+1:j] + w[j+1:k] + w[k+1:]
                            if add_candidate(var) and depth < max_depth - 1:
                                generate_level(var, depth + 1)
            
            # Strategy 10: Remove 4 letters
            if len(w) > 5:
                for i in range(len(w)):
                    for j in range(i+1, len(w)):
                        for k in range(j+1, len(w)):
                            for l in range(k+1, len(w)):
                                var = w[:i] + w[i+1:j] + w[j+1:k] + w[k+1:l] + w[l+1:]
                                if add_candidate(var) and len(candidates) < max_candidates:
                                    if depth < max_depth - 1:
                                        generate_level(var, depth + 1)
            
            # Strategy 11: Insert vowel combinations
            vowel_combos = ['ae', 'ai', 'ao', 'au', 'ea', 'ei', 'eo', 'eu', 'ia', 'ie', 'io', 'iu', 
                          'oa', 'oe', 'oi', 'ou', 'ua', 'ue', 'ui', 'uo', 'aa', 'ee', 'ii', 'oo', 'uu']
            for pos in range(len(w) + 1):
                for combo in vowel_combos:
                    var = w[:pos] + combo + w[pos:]
                    if add_candidate(var) and depth < max_depth - 1:
                        generate_level(var, depth + 1)
            
            # Strategy 12: Try ALL letter pairs
            for pos in range(len(w) + 1):
                for letter1 in all_letters[:13]:  # Limit to avoid explosion
                    for letter2 in all_letters[:13]:
                        var = w[:pos] + letter1 + letter2 + w[pos:]
                        if add_candidate(var) and len(candidates) < max_candidates:
                            if depth < max_depth - 1:
                                generate_level(var, depth + 1)
            
            # Strategy 13: Replace with ALL possible letters
            for i in range(len(w)):
                for letter in all_letters:
                    if letter != w[i].lower():
                        var = w[:i] + letter + w[i+1:]
                        if add_candidate(var) and depth < max_depth - 1:
                            generate_level(var, depth + 1)
            
            # Strategy 19: Remove 5 letters (for Far variations)
            if len(w) > 6:
                for i in range(len(w)):
                    for j in range(i+1, min(i+3, len(w))):
                        for k in range(j+1, min(j+3, len(w))):
                            for l in range(k+1, min(k+3, len(w))):
                                for m in range(l+1, min(l+3, len(w))):
                                    var = w[:i] + w[i+1:j] + w[j+1:k] + w[k+1:l] + w[l+1:m] + w[m+1:]
                                    if add_candidate(var) and len(candidates) < max_candidates:
                                        if depth < max_depth - 1:
                                            generate_level(var, depth + 1)
            
            # Strategy 20: Remove 6 letters (for Far variations)
            if len(w) > 7:
                for i in range(len(w)):
                    for j in range(i+1, min(i+2, len(w))):
                        for k in range(j+1, min(j+2, len(w))):
                            for l in range(k+1, min(k+2, len(w))):
                                for m in range(l+1, min(l+2, len(w))):
                                    for n in range(m+1, min(m+2, len(w))):
                                        var = w[:i] + w[i+1:j] + w[j+1:k] + w[k+1:l] + w[l+1:m] + w[m+1:n] + w[n+1:]
                                        if add_candidate(var) and len(candidates) < max_candidates:
                                            if depth < max_depth - 1:
                                                generate_level(var, depth + 1)
            
            # Strategy 23: Replace with phonetic equivalents
            phonetic_equivalents = {
                'a': ['e', 'i', 'o'], 'e': ['a', 'i', 'y'], 'i': ['e', 'y', 'a'],
                'o': ['a', 'u'], 'u': ['o', 'a'], 'y': ['i', 'e'],
                'b': ['p', 'v'], 'p': ['b', 'f'], 'v': ['b', 'f', 'w'],
                'd': ['t', 'th'], 't': ['d', 'th'], 'g': ['k', 'j'], 'k': ['g', 'c', 'q'],
                's': ['z', 'c', 'x'], 'z': ['s', 'x'], 'c': ['s', 'k', 'q'],
                'f': ['v', 'ph'], 'm': ['n', 'mn'], 'n': ['m', 'ng'],
                'l': ['r', 'll'], 'r': ['l', 'rr'], 'w': ['v', 'u'], 'h': [''],
                'x': ['ks', 'z'], 'q': ['k', 'c'], 'j': ['g', 'y']
            }
            for i, char in enumerate(w):
                base_char = char.lower()
                if base_char in phonetic_equivalents:
                    for equiv in phonetic_equivalents[base_char]:
                        if equiv:
                            var = w[:i] + equiv + w[i+1:]
                            if add_candidate(var) and depth < max_depth - 1:
                                generate_level(var, depth + 1)
            
            # Strategy 24: Duplicate letters
            for i in range(len(w)):
                var = w[:i] + w[i] + w[i] + w[i+1:]
                if add_candidate(var) and depth < max_depth - 1:
                    generate_level(var, depth + 1)
            
            # Strategy 25: Remove duplicate letters
            for i in range(len(w) - 1):
                if w[i] == w[i+1]:
                    var = w[:i] + w[i+1:]
                    if add_candidate(var) and depth < max_depth - 1:
                        generate_level(var, depth + 1)
            
            # Strategy 26: Swap 3 letters (rotate)
            if len(w) >= 3:
                for i in range(len(w) - 2):
                    var = w[:i] + w[i+1] + w[i+2] + w[i] + w[i+3:]
                    if add_candidate(var) and depth < max_depth - 1:
                        generate_level(var, depth + 1)
            
            # Strategy 27: Reverse substring
            for i in range(len(w) - 1):
                for j in range(i+2, min(i+5, len(w)+1)):
                    var = w[:i] + w[i:j][::-1] + w[j:]
                    if add_candidate(var) and depth < max_depth - 1:
                        generate_level(var, depth + 1)
            
            # Strategy 28: Insert common letter pairs
            common_pairs = ['th', 'sh', 'ch', 'ph', 'ck', 'ng', 'st', 'tr', 'br', 'cr', 'dr', 'fr', 'gr', 'pr']
            for pos in range(len(w) + 1):
                for pair in common_pairs:
                    var = w[:pos] + pair + w[pos:]
                    if add_candidate(var) and depth < max_depth - 1:
                        generate_level(var, depth + 1)
            
            # Strategy 29: Remove common letter pairs
            for i in range(len(w) - 1):
                pair = w[i:i+2]
                if pair in common_pairs:
                    var = w[:i] + w[i+2:]
                    if add_candidate(var) and depth < max_depth - 1:
                        generate_level(var, depth + 1)
            
            # Strategy 30: Replace common letter pairs
            for i in range(len(w) - 1):
                pair = w[i:i+2]
                for replacement_pair in common_pairs:
                    if replacement_pair != pair:
                        var = w[:i] + replacement_pair + w[i+2:]
                        if add_candidate(var) and depth < max_depth - 1:
                            generate_level(var, depth + 1)
            
            # Strategy 31: Add prefix
            common_prefixes = ['a', 'e', 'i', 'o', 'u', 'y', 're', 'un', 'in', 'de']
            for prefix in common_prefixes:
                var = prefix + w
                if add_candidate(var) and depth < max_depth - 1:
                    generate_level(var, depth + 1)
            
            # Strategy 32: Add suffix
            common_suffixes = ['a', 'e', 'i', 'o', 'u', 'y', 's', 'es', 'ed', 'er', 'ing']
            for suffix in common_suffixes:
                var = w + suffix
                if add_candidate(var) and depth < max_depth - 1:
                    generate_level(var, depth + 1)
            
            # Strategy 35: Split and insert letter
            if len(w) > 2:
                mid = len(w) // 2
                for letter in all_letters[:13]:
                    var = w[:mid] + letter + w[mid:]
                    if add_candidate(var) and depth < max_depth - 1:
                        generate_level(var, depth + 1)
            
            # Strategy 36: Move letter to different position
            for i in range(len(w)):
                for j in range(len(w) + 1):
                    if j != i and j != i + 1:
                        var = w[:i] + w[i+1:j] + w[i] + w[j:]
                        if add_candidate(var) and depth < max_depth - 1:
                            generate_level(var, depth + 1)
            
            # Strategy 37: Replace with double letter
            for i in range(len(w)):
                for letter in all_letters[:13]:
                    var = w[:i] + letter + letter + w[i+1:]
                    if add_candidate(var) and depth < max_depth - 1:
                        generate_level(var, depth + 1)
            
            # Strategy 38: Remove middle letters (keep first and last)
            if len(w) > 3:
                for i in range(1, len(w) - 1):
                    for j in range(i+1, len(w) - 1):
                        var = w[0] + w[i+1:j] + w[-1]
                        if add_candidate(var) and depth < max_depth - 1:
                            generate_level(var, depth + 1)
            
            # Strategy 43: Replace with similar-looking letters
            visual_similar = {
                'a': ['o', 'e'], 'e': ['a', 'c'], 'i': ['l', '1'], 'o': ['a', '0'],
                'c': ['e', 'o'], 'g': ['q', '9'], 'l': ['i', '1'], 
                's': ['5', 'z'], 'z': ['2', 's'], 'b': ['6', 'p'], 'p': ['b', 'q'],
                'q': ['g', 'p'], 'd': ['b', 'p'], 'm': ['n', 'w'], 'n': ['m', 'h'],
                'w': ['m', 'v'], 'v': ['w', 'u'], 'u': ['v', 'n']
            }
            for i, char in enumerate(w):
                base_char = char.lower()
                if base_char in visual_similar:
                    for similar in visual_similar[base_char]:
                        var = w[:i] + similar + w[i+1:]
                        if add_candidate(var) and depth < max_depth - 1:
                            generate_level(var, depth + 1)
            
            # Strategy 44: Cyclic shift
            if len(w) > 1:
                for shift in range(1, min(4, len(w))):
                    var = w[shift:] + w[:shift]
                    if add_candidate(var) and depth < max_depth - 1:
                        generate_level(var, depth + 1)
            
            # Strategy 47: Remove every other letter (for Far variations)
            if len(w) > 2:
                var = ''.join(w[i] for i in range(0, len(w), 2))
                if add_candidate(var) and depth < max_depth - 1:
                    generate_level(var, depth + 1)
                var = ''.join(w[i] for i in range(1, len(w), 2))
                if add_candidate(var) and depth < max_depth - 1:
                    generate_level(var, depth + 1)
            
            # Strategy 48: Duplicate word segments
            if len(w) > 2:
                for i in range(1, len(w)):
                    segment = w[:i]
                    var = segment + segment + w[i:]
                    if add_candidate(var) and depth < max_depth - 1:
                        generate_level(var, depth + 1)
            
            # Strategy 49: Replace vowels with 'y' or 'w'
            for i, char in enumerate(w):
                if char.lower() in vowels:
                    for replacement in ['y', 'w']:
                        var = w[:i] + replacement + w[i+1:]
                        if add_candidate(var) and depth < max_depth - 1:
                            generate_level(var, depth + 1)
        
        # Start generation
        generate_level(word, depth=0)
        return candidates
    
    def generate_all_variations(self, max_candidates: int = 10000) -> Dict[str, List[Tuple[str, float]]]:
        """
        Generate all possible variations and categorize them by similarity level.
        
        Returns:
            Dictionary mapping category to list of (variation, score) tuples
        """
        print(f"🔍 Generating variations for: '{self.original_name}'")
        print(f"   Target distribution: {self.target_distribution}")
        print()
        
        # Generate variations using all strategies
        all_variations = set()
        
        print("   Strategy 1: Single character substitution...")
        all_variations.update(self.generate_single_char_substitution(self.original_name, max_candidates // 6))
        print(f"      Generated: {len(all_variations)} variations")
        
        print("   Strategy 2: Character insertion...")
        all_variations.update(self.generate_char_insertion(self.original_name, max_candidates // 6))
        print(f"      Generated: {len(all_variations)} variations")
        
        print("   Strategy 3: Character deletion...")
        all_variations.update(self.generate_char_deletion(self.original_name, max_candidates // 6))
        print(f"      Generated: {len(all_variations)} variations")
        
        print("   Strategy 4: Character transposition...")
        all_variations.update(self.generate_char_transposition(self.original_name, max_candidates // 6))
        print(f"      Generated: {len(all_variations)} variations")
        
        print("   Strategy 5: Double character variations...")
        all_variations.update(self.generate_double_char_variations(self.original_name, max_candidates // 6))
        print(f"      Generated: {len(all_variations)} variations")
        
        print("   Strategy 6: Visual similar replacements...")
        all_variations.update(self.generate_visual_similar_replacements(self.original_name, max_candidates // 6))
        print(f"      Generated: {len(all_variations)} variations")
        
        print("   Strategy 7: Comprehensive all-strategies generation (50 strategies, depth 6)...")
        comprehensive_vars = self.generate_all_strategies_comprehensive(
            self.original_name, 
            max_candidates=max_candidates, 
            max_depth=6
        )
        all_variations.update(comprehensive_vars)
        print(f"      Generated: {len(all_variations)} total variations")
        
        # Remove original and empty strings
        all_variations.discard(self.original_name)
        all_variations.discard("")
        
        print()
        print(f"   Total unique variations generated: {len(all_variations)}")
        print("   Calculating orthographic scores...")
        
        # Score all variations
        scored_variations = []
        for var in all_variations:
            score = self.calculate_orthographic_score(var)
            category = self.categorize_score(score)
            scored_variations.append((var, score, category))
        
        # Sort by score (descending)
        scored_variations.sort(key=lambda x: x[1], reverse=True)
        
        # Group by category
        categorized = {
            "Light": [],
            "Medium": [],
            "Far": [],
            "Below": []
        }
        
        for var, score, category in scored_variations:
            categorized[category].append((var, score))
        
        print()
        print(f"   Categorized variations:")
        print(f"      Light (0.70-1.00):   {len(categorized['Light'])} variations")
        print(f"      Medium (0.50-0.69):  {len(categorized['Medium'])} variations")
        print(f"      Far (0.20-0.49):     {len(categorized['Far'])} variations")
        print(f"      Below threshold:     {len(categorized['Below'])} variations")
        print()
        
        return categorized
    
    def select_optimal_combination(self, categorized: Dict[str, List[Tuple[str, float]]], 
                                   total_count: int) -> List[str]:
        """
        Select optimal combination of variations to match target distribution.
        
        Uses brute force to try different combinations and find the best match.
        Handles cases where categories are missing (e.g., very short names).
        
        Args:
            categorized: Dictionary of categorized variations
            total_count: Total number of variations needed
            
        Returns:
            List of selected variation strings
        """
        print(f"🎯 Selecting optimal combination for {total_count} variations...")
        print(f"   Target distribution: {self.target_distribution}")
        
        # Calculate target counts
        target_counts = {
            "Light": int(self.target_distribution.get("Light", 0.0) * total_count),
            "Medium": int(self.target_distribution.get("Medium", 0.0) * total_count),
            "Far": int(self.target_distribution.get("Far", 0.0) * total_count)
        }
        
        print(f"   Target counts: Light={target_counts['Light']}, Medium={target_counts['Medium']}, Far={target_counts['Far']}")
        print()
        
        # Check available counts
        available_counts = {
            "Light": len(categorized["Light"]),
            "Medium": len(categorized["Medium"]),
            "Far": len(categorized["Far"])
        }
        
        # If a category is missing, redistribute proportionally
        if available_counts["Light"] < target_counts["Light"]:
            shortfall = target_counts["Light"] - available_counts["Light"]
            print(f"   ⚠️  Warning: Only {available_counts['Light']} Light variations available (need {target_counts['Light']})")
            print(f"   🔄 Redistributing {shortfall} slots to Medium/Far proportionally...")
            
            # Redistribute to Medium and Far based on their target ratios
            medium_ratio = target_counts["Medium"] / (target_counts["Medium"] + target_counts["Far"]) if (target_counts["Medium"] + target_counts["Far"]) > 0 else 0.6
            far_ratio = target_counts["Far"] / (target_counts["Medium"] + target_counts["Far"]) if (target_counts["Medium"] + target_counts["Far"]) > 0 else 0.2
            
            target_counts["Light"] = available_counts["Light"]  # Use what's available
            target_counts["Medium"] += int(shortfall * medium_ratio)
            target_counts["Far"] += shortfall - int(shortfall * medium_ratio)
            
            print(f"   📊 Adjusted targets: Light={target_counts['Light']}, Medium={target_counts['Medium']}, Far={target_counts['Far']}")
        
        # Select variations from each category
        selected = []
        
        # Light variations (prioritize highest scores)
        if target_counts["Light"] > 0:
            light_candidates = categorized["Light"][:target_counts["Light"] * 2]  # Get more candidates
            if len(light_candidates) >= target_counts["Light"]:
                selected.extend([var for var, _ in light_candidates[:target_counts["Light"]]])
            else:
                selected.extend([var for var, _ in light_candidates])
        
        # Medium variations (prioritize scores closest to 0.60)
        if target_counts["Medium"] > 0:
            medium_candidates = categorized["Medium"].copy()
            # Sort by closeness to 0.60 (middle of Medium range)
            medium_candidates.sort(key=lambda x: abs(x[1] - 0.60))
            if len(medium_candidates) >= target_counts["Medium"]:
                selected.extend([var for var, _ in medium_candidates[:target_counts["Medium"]]])
            else:
                selected.extend([var for var, _ in medium_candidates])
                if len(medium_candidates) < target_counts["Medium"]:
                    print(f"   ⚠️  Warning: Only {len(medium_candidates)} Medium variations available (need {target_counts['Medium']})")
        
        # Far variations (prioritize scores closest to 0.35)
        if target_counts["Far"] > 0:
            far_candidates = categorized["Far"].copy()
            # Sort by closeness to 0.35 (middle of Far range)
            far_candidates.sort(key=lambda x: abs(x[1] - 0.35))
            if len(far_candidates) >= target_counts["Far"]:
                selected.extend([var for var, _ in far_candidates[:target_counts["Far"]]])
            else:
                selected.extend([var for var, _ in far_candidates])
                if len(far_candidates) < target_counts["Far"]:
                    print(f"   ⚠️  Warning: Only {len(far_candidates)} Far variations available (need {target_counts['Far']})")
        
        # If we still don't have enough, use brute force to find best combination
        if len(selected) < total_count:
            print(f"   🔄 Using brute force to optimize distribution for {total_count - len(selected)} remaining slots...")
            
            # Collect all available candidates
            all_candidates = (
                [(var, score, "Light") for var, score in categorized["Light"]] +
                [(var, score, "Medium") for var, score in categorized["Medium"]] +
                [(var, score, "Far") for var, score in categorized["Far"]]
            )
            
            # Remove duplicates (keep first occurrence)
            seen = set()
            unique_candidates = []
            for var, score, cat in all_candidates:
                if var not in seen:
                    seen.add(var)
                    unique_candidates.append((var, score, cat))
            
            # Try multiple combinations to find best distribution match
            best_combination = None
            best_quality = -1
            attempts = min(5000, max(100, len(unique_candidates) * 10))
            
            for _ in range(attempts):
                # Randomly sample enough variations
                sample_size = min(total_count, len(unique_candidates))
                combo = random.sample(unique_candidates, sample_size)
                combo_vars = [var for var, _, _ in combo]
                
                # Calculate distribution quality
                scores = [self.calculate_orthographic_score(var) for var in combo_vars]
                quality = self._calculate_distribution_quality(scores, self.target_distribution)
                
                if quality > best_quality:
                    best_quality = quality
                    best_combination = combo_vars
            
            if best_combination:
                # Use the best combination, but ensure we have exactly total_count
                if len(selected) > 0:
                    # Combine selected with best combination, avoiding duplicates
                    combined = selected.copy()
                    for var in best_combination:
                        if var not in combined and len(combined) < total_count:
                            combined.append(var)
                    selected = combined[:total_count]
                else:
                    selected = best_combination[:total_count]
        
        # Final check: ensure we have exactly total_count
        if len(selected) < total_count:
            # Fill remaining slots from any available category
            all_remaining = (
                [(var, score) for var, score in categorized["Light"] if var not in selected] +
                [(var, score) for var, score in categorized["Medium"] if var not in selected] +
                [(var, score) for var, score in categorized["Far"] if var not in selected]
            )
            
            needed = total_count - len(selected)
            for var, _ in all_remaining[:needed]:
                selected.append(var)
        
        print(f"   ✅ Selected {len(selected)} variations")
        print()
        
        return selected[:total_count]  # Ensure we don't exceed total_count
    
    def select_optimal_combination_with_rules(
        self,
        categorized: Dict[str, List[Tuple[str, float]]],
        rule_compliant_scored: Dict[str, List[Tuple[str, float, str]]],
        total_count: int
    ) -> List[str]:
        """
        Select optimal combination meeting BOTH constraints:
        1. Orthographic distribution (Light/Medium/Far)
        2. Rule compliance percentage
        
        ENHANCED: Uses category-targeted rule generation to distribute rule compliance.
        
        Args:
            categorized: Non-rule variations by orthographic category
            rule_compliant_scored: Rule-compliant variations with scores (legacy, may be empty)
            total_count: Total number of variations needed
            
        Returns:
            List of selected variation strings
        """
        print(f"🎯 Selecting optimal combination with rule compliance for {total_count} variations...")
        print(f"   Target distribution: {self.target_distribution}")
        print(f"   Rule percentage: {self.rule_percentage * 100:.1f}%")
        print(f"   Possible rules: {self.possible_rules}")
        
        # Calculate targets
        target_rule_count = max(1, int(total_count * self.rule_percentage))
        target_orthographic = {
            "Light": int(self.target_distribution.get("Light", 0.0) * total_count),
            "Medium": int(self.target_distribution.get("Medium", 0.0) * total_count),
            "Far": int(self.target_distribution.get("Far", 0.0) * total_count)
        }
        
        print(f"   Target rule-compliant: {target_rule_count} variations")
        print(f"   Target orthographic: Light={target_orthographic['Light']}, Medium={target_orthographic['Medium']}, Far={target_orthographic['Far']}")
        print()
        
        # Generate rule-compliant variations for EACH category using aggression levels
        print(f"   🔧 Generating category-targeted rule-compliant variations...")
        rule_compliant_by_category = {}
        for category in ["Light", "Medium", "Far"]:
            rule_compliant_by_category[category] = self.generate_rule_compliant_by_category(
                category=category,
                rules=self.possible_rules,
                max_per_rule=50
            )
            print(f"      {category}: {len(rule_compliant_by_category[category])} rule-compliant variations")
        print()
        
        selected = []
        rule_count = 0
        rule_count_by_category = {"Light": 0, "Medium": 0, "Far": 0}
        selected_by_category = {"Light": 0, "Medium": 0, "Far": 0}
        
        # Phase 1: Fill each category with rule-compliant variations (priority)
        for category in ["Light", "Medium", "Far"]:
            needed = target_orthographic[category]
            selected_in_category = 0
            available_rule_compliant = rule_compliant_by_category[category]
            
            # Take as many rule-compliant as possible (up to target_rule_count)
            rule_taken = min(
                needed,
                len(available_rule_compliant),
                target_rule_count - rule_count
            )
            
            # Add rule-compliant variations
            for var, score, cat in available_rule_compliant[:rule_taken]:
                selected.append(var)
                rule_count += 1
                selected_in_category += 1
                rule_count_by_category[category] += 1
                selected_by_category[category] += 1
            
            # Fill remaining slots with non-rule-compliant variations
            remaining = needed - selected_in_category
            if remaining > 0:
                non_rule_in_category = [
                    (v, s) for v, s in categorized[category] 
                    if v not in selected
                ]
                for var, score in non_rule_in_category[:remaining]:
                    selected.append(var)
                    selected_in_category += 1
                    selected_by_category[category] += 1
        
        # Phase 2: If we need more rule-compliant, add from any category
        if rule_count < target_rule_count:
            print(f"   ⚠️  Only {rule_count} rule-compliant variations selected (need {target_rule_count})")
            print(f"   🔄 Adding more rule-compliant variations from any category...")
            
            for category in ["Light", "Medium", "Far"]:
                if rule_count >= target_rule_count:
                    break
                
                available = rule_compliant_by_category[category]
                for var, score, cat in available:
                    if var not in selected and rule_count < target_rule_count and len(selected) < total_count:
                        selected.append(var)
                        rule_count += 1
                        rule_count_by_category[category] += 1
                        selected_by_category[category] += 1
                        if rule_count >= target_rule_count:
                            break
        
        # Phase 3: Fill remaining slots to reach total_count
        if len(selected) < total_count:
            all_remaining = (
                [(v, s) for v, s in categorized["Light"] if v not in selected] +
                [(v, s) for v, s in categorized["Medium"] if v not in selected] +
                [(v, s) for v, s in categorized["Far"] if v not in selected]
            )
            needed = total_count - len(selected)
            for var, _ in all_remaining[:needed]:
                selected.append(var)
        
        print(f"   ✅ Selected {len(selected)} variations")
        print(f"   Rule-compliant: {rule_count} ({rule_count/len(selected)*100:.1f}%)")
        print(f"   Rule-compliant by category: Light={rule_count_by_category['Light']}, Medium={rule_count_by_category['Medium']}, Far={rule_count_by_category['Far']}")
        print(f"   Total by category: Light={selected_by_category['Light']}, Medium={selected_by_category['Medium']}, Far={selected_by_category['Far']}")
        print()
        
        return selected[:total_count]
    
    def _calculate_distribution_quality(self, scores: List[float], targets: Dict[str, float]) -> float:
        """
        Calculate distribution quality (same logic as rewards.py).
        
        This is used to evaluate how well a combination matches the target distribution.
        """
        quality = 0.0
        total_matched = 0
        
        for level, (lower, upper) in ORTHOGRAPHIC_BOUNDARIES.items():
            target_percentage = targets.get(level, 0.0)
            if target_percentage == 0.0:
                continue
            
            # Count scores in this range
            count = sum(1 for score in scores if lower <= score <= upper)
            target_count = int(target_percentage * len(scores))
            
            if target_count > 0:
                match_ratio = count / target_count
                if match_ratio <= 1.0:
                    match_quality = match_ratio
                else:
                    match_quality = 1.0 - (1.0 / (1.0 + match_ratio - 1.0))  # Diminishing returns
                quality += target_percentage * match_quality
                total_matched += count
        
        # Penalize unmatched variations
        unmatched = len(scores) - total_matched
        if unmatched > 0:
            penalty = 0.1 * (unmatched / len(scores))
            quality = max(0.0, quality - penalty)
        
        return quality
    
    def generate_optimal_variations(self, variation_count: int = 15) -> Tuple[List[str], Dict]:
        """
        Main method: Generate optimal variations matching target distribution.
        Supports rule compliance if rule_based parameter is provided.
        
        Args:
            variation_count: Total number of variations to generate
            
        Returns:
            Tuple of (list of variations, detailed metrics)
        """
        print("=" * 80)
        print("ORTHOGRAPHIC SIMILARITY MAXIMIZATION (BRUTE FORCE)")
        if self.possible_rules:
            print(f"WITH RULE COMPLIANCE ({len(self.possible_rules)} rules, {self.rule_percentage*100:.0f}%)")
        print("=" * 80)
        print()
        
        # Step 1: Generate rule-compliant variations (if rules specified)
        rule_compliant_scored = {}
        if self.possible_rules:
            print(f"🔧 Generating rule-compliant variations for {len(self.possible_rules)} rules...")
            rule_compliant_scored = self.generate_rule_compliant_variations_with_scores(max_per_rule=100)
            total_rule_variations = sum(len(v) for v in rule_compliant_scored.values())
            print(f"   Generated {total_rule_variations} rule-compliant variations")
            print()
        
        # Step 2: Generate all orthographic variations
        categorized = self.generate_all_variations(max_candidates=10000)
        
        # Step 3: Select optimal combination (with or without rules)
        if rule_compliant_scored:
            selected = self.select_optimal_combination_with_rules(
                categorized,
                rule_compliant_scored,
                variation_count
            )
        else:
            selected = self.select_optimal_combination(categorized, variation_count)
        
        # Calculate final metrics
        final_scores = [self.calculate_orthographic_score(var) for var in selected]
        final_categories = {cat: [] for cat in ["Light", "Medium", "Far", "Below"]}
        
        for var, score in zip(selected, final_scores):
            category = self.categorize_score(score)
            final_categories[category].append((var, score))
        
        # Calculate distribution
        actual_distribution = {
            "Light": len(final_categories["Light"]) / len(selected) if selected else 0.0,
            "Medium": len(final_categories["Medium"]) / len(selected) if selected else 0.0,
            "Far": len(final_categories["Far"]) / len(selected) if selected else 0.0
        }
        
        # Calculate quality score
        quality_score = self._calculate_distribution_quality(final_scores, self.target_distribution)
        
        # Calculate rule compliance metrics
        rule_compliance_metrics = {}
        if self.possible_rules:
            from rule_evaluator import evaluate_rule_compliance
            compliant_variations_by_rule, compliance_ratio = evaluate_rule_compliance(
                self.original_name,
                selected,
                self.possible_rules
            )
            
            # Count rule-compliant variations
            all_compliant_variations = set()
            for rule, variations_list in compliant_variations_by_rule.items():
                all_compliant_variations.update(variations_list)
            
            rule_compliance_metrics = {
                "possible_rules": self.possible_rules,
                "rule_percentage_target": self.rule_percentage * 100,
                "rule_compliant_count": len(all_compliant_variations),
                "rule_compliant_percentage": len(all_compliant_variations) / len(selected) * 100 if selected else 0.0,
                "compliant_variations_by_rule": {k: len(v) for k, v in compliant_variations_by_rule.items()},
                "compliance_ratio": compliance_ratio
            }
        
        metrics = {
            "original_name": self.original_name,
            "variation_count": len(selected),
            "target_distribution": self.target_distribution,
            "actual_distribution": actual_distribution,
            "quality_score": quality_score,
            "average_score": sum(final_scores) / len(final_scores) if final_scores else 0.0,
            "min_score": min(final_scores) if final_scores else 0.0,
            "max_score": max(final_scores) if final_scores else 0.0,
            "categorized_variations": final_categories,
            "all_scores": final_scores,
            "rule_compliance": rule_compliance_metrics if rule_compliance_metrics else None
        }
        
        print("=" * 80)
        print("RESULTS")
        print("=" * 80)
        print(f"Original Name: {self.original_name}")
        print(f"Variations Generated: {len(selected)}")
        print()
        print("Distribution:")
        print(f"  Target:  Light={self.target_distribution.get('Light', 0):.1%}, "
              f"Medium={self.target_distribution.get('Medium', 0):.1%}, "
              f"Far={self.target_distribution.get('Far', 0):.1%}")
        print(f"  Actual:  Light={actual_distribution['Light']:.1%}, "
              f"Medium={actual_distribution['Medium']:.1%}, "
              f"Far={actual_distribution['Far']:.1%}")
        print()
        print(f"Quality Score: {quality_score:.4f}")
        print(f"Average Orthographic Score: {metrics['average_score']:.4f}")
        print(f"Score Range: {metrics['min_score']:.4f} - {metrics['max_score']:.4f}")
        
        # Print rule compliance info
        if rule_compliance_metrics:
            print()
            print("Rule Compliance:")
            print(f"  Target: {rule_compliance_metrics['rule_percentage_target']:.1f}%")
            print(f"  Actual: {rule_compliance_metrics['rule_compliant_percentage']:.1f}% ({rule_compliance_metrics['rule_compliant_count']} variations)")
            print(f"  Rules satisfied: {rule_compliance_metrics['compliant_variations_by_rule']}")
        
        print()
        print("Selected Variations:")
        for i, (var, score) in enumerate(zip(selected, final_scores), 1):
            category = self.categorize_score(score)
            print(f"  {i:2d}. {var:30s} | Score: {score:.4f} | {category}")
        print()
        print("=" * 80)
        
        return selected, metrics


def generate_full_name_variations(first_name: str, last_name: str, 
                                  target_distribution: Dict[str, float],
                                  variation_count: int = 15) -> Tuple[List[Tuple[str, str]], Dict]:
    """
    Generate variations for full name (first + last) and calculate scores separately.
    
    This matches rewards.py's approach of scoring first and last names separately.
    """
    print("=" * 80)
    print("FULL NAME ORTHOGRAPHIC SIMILARITY MAXIMIZATION")
    print("=" * 80)
    print()
    print(f"First Name: '{first_name}'")
    print(f"Last Name: '{last_name}'")
    print(f"Target Distribution: {target_distribution}")
    print(f"Variation Count: {variation_count}")
    print()
    
    # Generate variations for first name
    print("🔍 Generating FIRST NAME variations...")
    print("-" * 80)
    first_generator = OrthographicBruteForceGenerator(first_name, target_distribution)
    first_categorized = first_generator.generate_all_variations(max_candidates=5000)
    
    # Calculate target counts for first name
    first_target_counts = {
        "Light": int(target_distribution.get("Light", 0.0) * variation_count),
        "Medium": int(target_distribution.get("Medium", 0.0) * variation_count),
        "Far": int(target_distribution.get("Far", 0.0) * variation_count)
    }
    
    # Select first name variations
    first_selected = first_generator.select_optimal_combination(first_categorized, variation_count)
    first_scores = [first_generator.calculate_orthographic_score(var) for var in first_selected]
    
    print()
    print("🔍 Generating LAST NAME variations...")
    print("-" * 80)
    last_generator = OrthographicBruteForceGenerator(last_name, target_distribution)
    last_categorized = last_generator.generate_all_variations(max_candidates=5000)
    
    # Calculate target counts for last name
    last_target_counts = {
        "Light": int(target_distribution.get("Light", 0.0) * variation_count),
        "Medium": int(target_distribution.get("Medium", 0.0) * variation_count),
        "Far": int(target_distribution.get("Far", 0.0) * variation_count)
    }
    
    # Select last name variations
    last_selected = last_generator.select_optimal_combination(last_categorized, variation_count)
    last_scores = [last_generator.calculate_orthographic_score(var) for var in last_selected]
    
    # Combine first and last name variations
    # Match variations by category to maintain distribution when combined
    # Calculate full name scores to ensure combined distribution matches target
    from MIID.validator.reward import calculate_orthographic_similarity
    
    original_full_name = f"{first_name} {last_name}"
    
    # Generate all possible combinations and score them
    all_combinations = []
    for fv in first_selected:
        for lv in last_selected:
            full_var = f"{fv} {lv}"
            score = calculate_orthographic_similarity(original_full_name, full_var)
            all_combinations.append((fv, lv, score))
    
    # Categorize combinations by full name score
    combined_categorized = {
        "Light": [],
        "Medium": [],
        "Far": []
    }
    
    for fv, lv, score in all_combinations:
        if score >= 0.7:
            combined_categorized["Light"].append((fv, lv, score))
        elif score >= 0.5:
            combined_categorized["Medium"].append((fv, lv, score))
        else:
            combined_categorized["Far"].append((fv, lv, score))
    
    # Select optimal combination to match target distribution
    combined_target_counts = {
        "Light": int(target_distribution.get("Light", 0.0) * variation_count),
        "Medium": int(target_distribution.get("Medium", 0.0) * variation_count),
        "Far": int(target_distribution.get("Far", 0.0) * variation_count)
    }
    
    combined_variations = []
    
    # Select from each category
    if combined_target_counts["Light"] > 0:
        light_combos = sorted(combined_categorized["Light"], key=lambda x: x[2], reverse=True)
        combined_variations.extend([(fv, lv) for fv, lv, _ in light_combos[:combined_target_counts["Light"]]])
    
    if combined_target_counts["Medium"] > 0:
        medium_combos = sorted(combined_categorized["Medium"], key=lambda x: abs(x[2] - 0.60))
        combined_variations.extend([(fv, lv) for fv, lv, _ in medium_combos[:combined_target_counts["Medium"]]])
    
    if combined_target_counts["Far"] > 0:
        far_combos = sorted(combined_categorized["Far"], key=lambda x: abs(x[2] - 0.35))
        combined_variations.extend([(fv, lv) for fv, lv, _ in far_combos[:combined_target_counts["Far"]]])
    
    # Ensure we have exactly variation_count
    if len(combined_variations) < variation_count:
        # Fill remaining slots from any category
        remaining = []
        for fv, lv, score in all_combinations:
            if (fv, lv) not in combined_variations:
                remaining.append((fv, lv, score))
        
        remaining.sort(key=lambda x: abs(x[2] - 0.60))  # Sort by closeness to medium
        needed = variation_count - len(combined_variations)
        combined_variations.extend([(fv, lv) for fv, lv, _ in remaining[:needed]])
    
    combined_variations = combined_variations[:variation_count]
    
    # Calculate detailed scores
    print()
    print("=" * 80)
    print("DETAILED SCORING RESULTS")
    print("=" * 80)
    print()
    
    # First name metrics
    first_categories = {"Light": [], "Medium": [], "Far": [], "Below": []}
    for var, score in zip(first_selected, first_scores):
        category = first_generator.categorize_score(score)
        first_categories[category].append((var, score))
    
    first_distribution = {
        "Light": len(first_categories["Light"]) / len(first_selected) if first_selected else 0.0,
        "Medium": len(first_categories["Medium"]) / len(first_selected) if first_selected else 0.0,
        "Far": len(first_categories["Far"]) / len(first_selected) if first_selected else 0.0
    }
    
    first_quality = first_generator._calculate_distribution_quality(first_scores, target_distribution)
    
    # Last name metrics
    last_categories = {"Light": [], "Medium": [], "Far": [], "Below": []}
    for var, score in zip(last_selected, last_scores):
        category = last_generator.categorize_score(score)
        last_categories[category].append((var, score))
    
    last_distribution = {
        "Light": len(last_categories["Light"]) / len(last_selected) if last_selected else 0.0,
        "Medium": len(last_categories["Medium"]) / len(last_selected) if last_selected else 0.0,
        "Far": len(last_categories["Far"]) / len(last_selected) if last_selected else 0.0
    }
    
    last_quality = last_generator._calculate_distribution_quality(last_scores, target_distribution)
    
    # Print detailed results
    print("FIRST NAME SCORES:")
    print("-" * 80)
    print(f"Original: '{first_name}'")
    print(f"Variations Generated: {len(first_selected)}")
    print()
    print("Distribution:")
    print(f"  Target:  Light={target_distribution.get('Light', 0):.1%}, "
          f"Medium={target_distribution.get('Medium', 0):.1%}, "
          f"Far={target_distribution.get('Far', 0):.1%}")
    print(f"  Actual:  Light={first_distribution['Light']:.1%}, "
          f"Medium={first_distribution['Medium']:.1%}, "
          f"Far={first_distribution['Far']:.1%}")
    print()
    print(f"Quality Score: {first_quality:.4f}")
    print(f"Average Orthographic Score: {sum(first_scores) / len(first_scores):.4f}")
    print(f"Score Range: {min(first_scores):.4f} - {max(first_scores):.4f}")
    print()
    print("First Name Variations (with scores):")
    for i, (var, score) in enumerate(zip(first_selected, first_scores), 1):
        category = first_generator.categorize_score(score)
        print(f"  {i:2d}. {var:30s} | Score: {score:.4f} | {category}")
    print()
    
    print("LAST NAME SCORES:")
    print("-" * 80)
    print(f"Original: '{last_name}'")
    print(f"Variations Generated: {len(last_selected)}")
    print()
    print("Distribution:")
    print(f"  Target:  Light={target_distribution.get('Light', 0):.1%}, "
          f"Medium={target_distribution.get('Medium', 0):.1%}, "
          f"Far={target_distribution.get('Far', 0):.1%}")
    print(f"  Actual:  Light={last_distribution['Light']:.1%}, "
          f"Medium={last_distribution['Medium']:.1%}, "
          f"Far={last_distribution['Far']:.1%}")
    print()
    print(f"Quality Score: {last_quality:.4f}")
    print(f"Average Orthographic Score: {sum(last_scores) / len(last_scores):.4f}")
    print(f"Score Range: {min(last_scores):.4f} - {max(last_scores):.4f}")
    print()
    print("Last Name Variations (with scores):")
    for i, (var, score) in enumerate(zip(last_selected, last_scores), 1):
        category = last_generator.categorize_score(score)
        print(f"  {i:2d}. {var:30s} | Score: {score:.4f} | {category}")
    print()
    
    print("COMBINED FULL NAME VARIATIONS:")
    print("-" * 80)
    for i, (first_var, last_var) in enumerate(combined_variations, 1):
        first_score = first_generator.calculate_orthographic_score(first_var)
        last_score = last_generator.calculate_orthographic_score(last_var)
        full_name = f"{first_var} {last_var}"
        print(f"  {i:2d}. {full_name:40s} | First: {first_score:.4f} | Last: {last_score:.4f}")
    print()
    
    # Calculate combined similarity score (matching rewards.py logic)
    # In rewards.py: similarity_score = (phonetic_quality + orthographic_quality) / 2
    # Since we're only doing orthographic, similarity_score = orthographic_quality for each part
    first_name_similarity_score = first_quality  # Orthographic quality (no phonetic in our case)
    last_name_similarity_score = last_quality    # Orthographic quality (no phonetic in our case)
    
    # Combine first and last name using weights from rewards.py
    # first_name_weight = 0.3, last_name_weight = 0.7
    combined_similarity_score = (0.3 * first_name_similarity_score) + (0.7 * last_name_similarity_score)
    
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"First Name Orthographic Quality:  {first_quality:.4f}")
    print(f"Last Name Orthographic Quality:    {last_quality:.4f}")
    print()
    print(f"First Name Similarity Score:      {first_name_similarity_score:.4f}")
    print(f"Last Name Similarity Score:        {last_name_similarity_score:.4f}")
    print(f"Combined Similarity Score:         {combined_similarity_score:.4f}")
    print(f"  (First: {first_name_similarity_score:.4f} × 0.3 + Last: {last_name_similarity_score:.4f} × 0.7)")
    print()
    print(f"First Name Average Orthographic:   {sum(first_scores) / len(first_scores):.4f}")
    print(f"Last Name Average Orthographic:    {sum(last_scores) / len(last_scores):.4f}")
    print(f"Combined Average Orthographic:     {(sum(first_scores) + sum(last_scores)) / (len(first_scores) + len(last_scores)):.4f}")
    print()
    
    # Calculate combined similarity score
    first_name_similarity_score = first_quality
    last_name_similarity_score = last_quality
    combined_similarity_score = (0.3 * first_name_similarity_score) + (0.7 * last_name_similarity_score)
    
    metrics = {
            "first_name": {
                "original": first_name,
                "variations": first_selected,
                "scores": first_scores,
                "distribution": first_distribution,
                "quality_score": first_quality,
                "similarity_score": first_name_similarity_score,
                "average_score": sum(first_scores) / len(first_scores) if first_scores else 0.0,
                "min_score": min(first_scores) if first_scores else 0.0,
                "max_score": max(first_scores) if first_scores else 0.0,
                "categorized": first_categories
            },
            "last_name": {
                "original": last_name,
                "variations": last_selected,
                "scores": last_scores,
                "distribution": last_distribution,
                "quality_score": last_quality,
                "similarity_score": last_name_similarity_score,
                "average_score": sum(last_scores) / len(last_scores) if last_scores else 0.0,
                "min_score": min(last_scores) if last_scores else 0.0,
                "max_score": max(last_scores) if last_scores else 0.0,
                "categorized": last_categories
            },
            "combined": {
                "variations": combined_variations,
                "count": len(combined_variations),
                "similarity_score": combined_similarity_score
            }
        }
    
    return combined_variations, metrics


def generate_dob_variations(seed_dob: str, count: int) -> List[str]:
    """
    Generate DOB variations that cover ALL required categories for maximum score.
    
    Required categories (6 total):
    1. ±1 day
    2. ±3 days
    3. ±30 days
    4. ±90 days
    5. ±365 days
    6. Year+Month variation (using complete date format)
    
    Args:
        seed_dob: Seed date of birth in YYYY-MM-DD format
        count: Total number of variations to generate (will ensure all 6 categories are covered)
    
    Returns:
        List of DOB variations covering all 6 categories, all in YYYY-MM-DD format
    """
    from datetime import datetime, timedelta
    
    dob_variations = []
    
    try:
        # Parse seed DOB
        seed_date = datetime.strptime(seed_dob, "%Y-%m-%d")
        
        # Category 1: ±1 day (at least 1 variation)
        for days in [-1, 1]:
            var_date = seed_date + timedelta(days=days)
            dob_variations.append(var_date.strftime("%Y-%m-%d"))
        
        # Category 2: ±3 days (at least 1 variation)
        for days in [-3, 3]:
            var_date = seed_date + timedelta(days=days)
            dob_variations.append(var_date.strftime("%Y-%m-%d"))
        
        # Category 3: ±30 days (at least 1 variation)
        for days in [-30, 30]:
            var_date = seed_date + timedelta(days=days)
            dob_variations.append(var_date.strftime("%Y-%m-%d"))
        
        # Category 4: ±90 days (at least 1 variation)
        for days in [-90, 90]:
            var_date = seed_date + timedelta(days=days)
            dob_variations.append(var_date.strftime("%Y-%m-%d"))
        
        # Category 5: ±365 days (at least 1 variation)
        for days in [-365, 365]:
            var_date = seed_date + timedelta(days=days)
            dob_variations.append(var_date.strftime("%Y-%m-%d"))
        
        # Category 6: Year+Month variation
        # Validator requires YYYY-MM format (without day) for "Year+Month only" category
        # This is the only format that gets recognized as "Year+Month only"
        year_month_only = seed_date.strftime("%Y-%m")  # YYYY-MM format for validator recognition
        
        # Build a prioritized list ensuring all 6 categories are covered
        category_reps = [
            (seed_date + timedelta(days=-1)).strftime("%Y-%m-%d"),  # ±1 day
            (seed_date + timedelta(days=-3)).strftime("%Y-%m-%d"),  # ±3 days
            (seed_date + timedelta(days=-30)).strftime("%Y-%m-%d"),  # ±30 days
            (seed_date + timedelta(days=-90)).strftime("%Y-%m-%d"),  # ±90 days
            (seed_date + timedelta(days=-365)).strftime("%Y-%m-%d"),  # ±365 days
            year_month_only  # Year+Month only (YYYY-MM format for validator)
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
                (seed_date + timedelta(days=-730)).strftime("%Y-%m-%d"),  # ±2 years
                (seed_date + timedelta(days=730)).strftime("%Y-%m-%d"),
            ]
            
            for i in range(additional_needed):
                if i < len(additional_variations):
                    final_variations.append(additional_variations[i])
                else:
                    # If we run out, repeat year-month format
                    final_variations.append(year_month_only)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_variations = []
        for dob in final_variations:
            if dob not in seen:
                seen.add(dob)
                unique_variations.append(dob)
        
        # Ensure year-month is included (add at the end if somehow missing)
        if year_month_only not in unique_variations:
            unique_variations.append(year_month_only)
        
        # Return exactly the requested count, but ensure all 6 categories are represented
        return unique_variations[:count]
        
    except ValueError as e:
        print(f"⚠️  Error parsing DOB '{seed_dob}': {e}")
        # Return default variations if parsing fails
        default_dob = "1985-03-15"
        if seed_dob != default_dob:
            return generate_dob_variations(default_dob, count)
        else:
            # Last resort: generate simple variations
            return [f"{1985 + i % 5}-03-{15 + i % 10}" for i in range(count)]
    except Exception as e:
        print(f"⚠️  Unexpected error generating DOB variations: {e}")
        # Return default variations
        return [f"{1985 + i % 5}-03-{15 + i % 10}" for i in range(count)]


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
            # Year-Month format - convert to complete date using 1st day
            year = parts[0]
            month = parts[1].zfill(2)
            return f"{year}-{month}-01"
        else:
            return dob  # Return as-is if format is unexpected
    except:
        return dob  # Return as-is if parsing fails


def main():
    """Example usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Maximize orthographic similarity using brute force")
    parser.add_argument("name", help="Original name (full name like 'John Smith' or single name)")
    parser.add_argument("--count", type=int, default=15, help="Number of variations to generate (default: 15)")
    parser.add_argument("--light", type=float, default=0.2, help="Target percentage for Light (default: 0.2)")
    parser.add_argument("--medium", type=float, default=0.6, help="Target percentage for Medium (default: 0.6)")
    parser.add_argument("--far", type=float, default=0.2, help="Target percentage for Far (default: 0.2)")
    parser.add_argument("--full-name", action="store_true", help="Treat as full name (first + last)")
    parser.add_argument("--rules", nargs="+", help="Rule names to apply (e.g., replace_double_letters_with_single_letter swap_adjacent_consonants)")
    parser.add_argument("--rule-percentage", type=int, default=30, help="Percentage of variations that should follow rules (default: 30)")
    
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
    
    # Check if it's a full name
    name_parts = args.name.strip().split()
    if len(name_parts) >= 2 or args.full_name:
        if len(name_parts) >= 2:
            first_name = name_parts[0]
            last_name = " ".join(name_parts[1:])
        else:
            print("⚠️  Full name mode but only one word provided. Using as first name.")
            first_name = name_parts[0]
            last_name = name_parts[0]  # Use same for both
        
        # Generate full name variations
        variations, metrics = generate_full_name_variations(
            first_name, last_name, target_distribution, args.count
        )
        
        print(f"\n✅ Generated {len(variations)} full name variations")
        print(f"   First Name Quality: {metrics['first_name']['quality_score']:.4f}")
        print(f"   Last Name Quality:  {metrics['last_name']['quality_score']:.4f}")
    else:
        # Single name
        # Parse rule-based parameters if provided
        rule_based = None
        if args.rules:
            rule_based = {
                "selected_rules": args.rules,
                "rule_percentage": args.rule_percentage
            }
        
        generator = OrthographicBruteForceGenerator(args.name, target_distribution, rule_based)
        variations, metrics = generator.generate_optimal_variations(args.count)
        
        print(f"\n✅ Generated {len(variations)} variations")
        print(f"   Quality Score: {metrics['quality_score']:.4f}")
        print(f"   Average Score: {metrics['average_score']:.4f}")


if __name__ == "__main__":
    main()

