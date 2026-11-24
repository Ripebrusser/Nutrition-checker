"""Matching Confidence - Scoring, thresholds, and calibration."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from typing import Dict, List, Optional, Tuple, Any

from .ingredient_taxonomy import MatchCategory, MatchStatus
from .matching_rules import MatchStatus


class ConfidenceLevel(Enum):
    """Confidence level for matches."""
    HIGH = "HIGH"       # Auto-accept
    MEDIUM = "MEDIUM"   # Review required
    LOW = "LOW"         # Review required
    UNMATCHED = "UNMATCHED"


@dataclass
class ConfidenceThresholds:
    """Confidence thresholds for match classification."""
    # Auto-accept thresholds
    EXACT_THRESHOLD: float = 1.0
    SYNONYM_THRESHOLD: float = 0.95
    TRANSLITERATION_THRESHOLD: float = 0.90
    REGIONAL_THRESHOLD: float = 0.90
    
    # Review thresholds
    HIGH_CONFIDENCE_THRESHOLD: float = 0.85
    REVIEW_THRESHOLD: float = 0.70
    AMBIGUOUS_THRESHOLD: float = 0.50
    
    # Weights for composite scoring
    WEIGHT_EXACT_MATCH: float = 1.0
    WEIGHT_SYNONYM_CONF: float = 0.95
    WEIGHT_TOKEN_SIM: float = 0.70
    WEIGHT_FOOD_GROUP: float = 0.15
    WEIGHT_PREP_STATE: float = 0.10


@dataclass
class ConfidenceScore:
    """Composite confidence score breakdown."""
    exact_match: float = 0.0
    synonym_conf: float = 0.0
    token_similarity: float = 0.0
    food_group_compat: float = 0.0
    prep_state_compat: float = 0.0
    composite_score: float = 0.0
    confidence_level: str = "LOW"
    match_status: str = "UNMATCHED"
    requires_review: bool = True


class ConfidenceScorer:
    """Compute confidence scores for candidate matches."""
    
    # Scoring weights (initial values, to be calibrated)
    WEIGHTS = {
        'exact_match': 1.0,
        'synonym_conf': 0.95,
        'token_sim': 0.70,
        'food_group': 0.15,
        'prep_state': 0.10,
    }
    
    # Thresholds
    THRESHOLDS = {
        'EXACT': 1.0,
        'SYNONYM': 0.95,
        'TRANSLITERATION': 0.90,
        'REGIONAL': 0.90,
        'HIGH_CONFIDENCE': 0.85,
        'REVIEW': 0.70,
        'AMBIGUOUS': 0.50,
    }
    
    # Confidence levels
    CONFIDENCE_LEVELS = {
        'HIGH': (0.90, 1.0),
        'MEDIUM': (0.70, 0.89),
        'LOW': (0.50, 0.69),
        'UNMATCHED': (0.0, 0.49)
    }
    
    @classmethod
    def compute_score(cls, 
                      exact_match: bool,
                      synonym_conf: float,
                      token_similarity: float,
                      food_group_compat: float,
                      prep_state_compat: float) -> Tuple[float, str, str]:
        """
        Compute composite confidence score.
        
        Returns:
            (composite_score, confidence_level, match_status)
        """
        score = (
            cls.WEIGHTS['exact_match'] * (1.0 if exact_match else 0.0) +
            cls.WEIGHTS['synonym_conf'] * synonym_conf +
            cls.WEIGHTS['token_sim'] * token_similarity +
            cls.WEIGHTS['food_group'] * food_group_compat +
            cls.WEIGHTS['prep_state'] * prep_state_compat
        )
        
        # Determine confidence level and match status
        if exact_match:
            return score, "HIGH", "EXACT_MATCH"
        elif synonym_conf >= 0.95:
            return score, "HIGH", "SYNONYM_MATCH"
        elif score >= 0.90:
            return score, "HIGH", "TRANSLITERATION_MATCH"
        elif score >= 0.85:
            return score, "MEDIUM", "HIGH_CONFIDENCE_MATCH"
        elif score >= 0.70:
            return score, "MEDIUM", "REVIEW_REQUIRED"
        elif score >= 0.50:
            return score, "LOW", "AMBIGUOUS_MATCH"
        else:
            return score, "LOW", "UNMATCHED"

    @classmethod
    def compute_token_similarity(cls, text1: str, text2: str) -> float:
        """Compute Jaccard similarity on normalized tokens."""
        tokens1 = set(cls._tokenize(text1))
        tokens2 = set(cls._tokenize(text2))
        
        if not tokens1 or not tokens2:
            return 0.0
        
        intersection = len(tokens1 & tokens2)
        union = len(tokens1 | tokens2)
        
        if union == 0:
            return 0.0
        return intersection / union
    
    @staticmethod
    def _tokenize(text: str) -> set:
        """Tokenize text into normalized tokens."""
        import re
        text = text.lower().strip()
        # Remove parentheses content
        text = re.sub(r'\([^)]*\)', '', text)
        # Split on non-word characters
        tokens = re.findall(r'\b\w+\b', text.lower())
        # Filter stopwords and short tokens
        stopwords = {'and', 'or', 'of', 'the', 'a', 'an', 'in', 'on', 'for', 'with', 'to', 'from', 'by', 'raw', 'fresh', 'dried', 'cooked', 'boiled', 'fried', 'roasted', 'steamed', 'baked', 'grilled', 'chopped', 'sliced', 'diced', 'minced', 'grated', 'ground', 'powder', 'powdered', 'fresh', 'dried', 'raw', 'cooked', 'boiled', 'fried', 'roasted', 'steamed', 'baked', 'grilled'}
        return {t for t in tokens if len(t) > 2 and t not in stopwords}

    @classmethod
    def compute_food_group_compat(cls, group1: str, group2: str) -> float:
        """Compute food group compatibility."""
        if group1 == group2:
            return 1.0
        # Related groups
        related_groups = {
            ('VEGETABLES', 'LEAFY VEGETABLES'): 0.5,
            ('VEGETABLES', 'OTHER VEGETABLES'): 0.5,
            ('FRUITS', 'FRUITS'): 1.0,
            ('NUTS AND OILSEEDS', 'NUTS AND OILSEEDS'): 1.0,
            ('PULSES AND LEGUMES', 'PULSES AND LEGUMES'): 1.0,
            ('CEREALS AND MILLETS', 'CEREALS AND MILLETS'): 1.0,
            ('MARINE FISH', 'MARINE FISH'): 1.0,
            ('MARINE SHELLFISH', 'MARINE SHELLFISH'): 1.0,
            ('ANIMAL MEAT', 'ANIMAL MEAT'): 1.0,
            ('POULTRY', 'POULTRY'): 1.0,
            ('MILK AND MILK PRODUCTS', 'MILK AND MILK PRODUCTS'): 1.0,
            ('EGG AND EGG PRODUCTS', 'EGG AND EGG PRODUCTS'): 1.0,
            ('POULTRY', 'POULTRY'): 1.0,
            ('ANIMAL MEAT', 'ANIMAL MEAT'): 1.0,
            ('MARINE FISH', 'MARINE FISH'): 1.0,
            ('MARINE SHELLFISH', 'MARINE SHELLFISH'): 1.0,
            ('FRESHWATER FISH AND SHELLFISH', 'FRESHWATER FISH AND SHELLFISH'): 1.0,
            ('SUGARS AND JAGGERY', 'SUGARS AND JAGGERY'): 1.0,
            ('FATS AND EDIBLE OILS', 'FATS AND EDIBLE OILS'): 1.0,
        }
        key = (group1, group2) if group1 <= group2 else (group2, group1)
        return 0.5 if group1 != group2 and (group1, group2) in cls.FOOD_GROUP_COMPAT else 0.0


def compute_match_score(exact_match: bool,
                        synonym_conf: float,
                        token_similarity: float,
                        food_group_compat: float,
                        prep_state_compat: float) -> Tuple[float, str, str]:
    """
    Compute composite match score and determine status.
    
    Returns:
        (composite_score, confidence_level, match_status)
    """
    from .matching_confidence import ConfidenceScorer
    return ConfidenceScorer.compute_score(
        exact_match, synonym_conf, token_similarity,
        food_group_compat, prep_state_compat
    )


def classify_match_status(score: float) -> Tuple[str, str]:
    """Classify match based on composite score."""
    if score >= 0.95:
        return "HIGH", "EXACT_MATCH" if score == 1.0 else "SYNONYM_MATCH"
    elif score >= 0.85:
        return "HIGH", "HIGH_CONFIDENCE_MATCH"
    elif score >= 0.70:
        return "MEDIUM", "REVIEW_REQUIRED"
    elif score >= 0.50:
        return "LOW", "AMBIGUOUS_MATCH"
    else:
        return "LOW", "UNMATCHED"