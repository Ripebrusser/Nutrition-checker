"""Matching Rules - Hierarchy, classification logic, evidence requirements."""

from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field

from .ingredient_taxonomy import MatchCategory, MatchStatus, classify_ingredient, taxonomy


class MatchMethod(Enum):
    """Candidate generation method."""
    EXACT = "EXACT"
    SYNONYM = "SYNONYM"
    TRANSLITERATION = "TRANSLITERATION"
    REGIONAL = "REGIONAL"
    TOKEN_SIMILARITY = "TOKEN_SIMILARITY"
    FUZZY = "FUZZY"
    FOOD_GROUP_FILTER = "FOOD_GROUP_FILTER"


class MatchStatus(Enum):
    """Matching status enum."""
    EXACT_MATCH = "EXACT_MATCH"
    SYNONYM_MATCH = "SYNONYM_MATCH"
    TRANSLITERATION_MATCH = "TRANSLITERATION_MATCH"
    REGIONAL_VARIANT = "REGIONAL_VARIANT"
    HIGH_CONFIDENCE_MATCH = "HIGH_CONFIDENCE_MATCH"
    PREP_STATE_COMPATIBLE = "PREP_STATE_COMPATIBLE"
    PREP_STATE_MISMATCH = "PREP_STATE_MISMATCH"
    EDIBLE_PART_COMPATIBLE = "EDIBLE_PART_COMPATIBLE"
    EDIBLE_PART_MISMATCH = "EDIBLE_PART_MISMATCH"
    VARIETY_MATCH = "VARIETY_MATCH"
    SPECIES_MATCH = "SPECIES_MATCH"
    COMPOSITE_DECOMPOSED = "COMPOSITE_DECOMPOSED"
    COMPOSITE_REVIEW_REQUIRED = "COMPOSITE_REVIEW_REQUIRED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    AMBIGUOUS_MATCH = "AMBIGUOUS_MATCH"
    UNMATCHED = "UNMATCHED"
    NOT_APPLICABLE = "NOT_APPLICABLE"


@dataclass
class MatchEvidence:
    """Evidence supporting a match."""
    method: str
    score: float
    details: Dict = field(default_factory=dict)
    source: str = ""


@dataclass
class MatchResult:
    """Result of matching an ingredient."""
    ifct_food_code: str
    ifct_food_name: str
    ifct_food_group: str
    match_status: str
    match_method: str
    similarity_score: float
    confidence_level: str  # HIGH, MEDIUM, LOW, UNMATCHED
    evidence: Dict = field(default_factory=dict)
    requires_review: bool = True
    taxonomy_category: str = ""
    prep_state_compat: float = 0.5
    edible_part_compat: float = 0.5
    food_group_compat: float = 0.5
    evidence_details: Dict = field(default_factory=dict)
    candidate_alternatives: List[Dict] = field(default_factory=list)


class MatchingRules:
    """Matching rules and hierarchy implementation."""
    
    # Confidence thresholds
    EXACT_THRESHOLD = 1.0
    SYNONYM_THRESHOLD = 0.95
    TRANSLITERATION_THRESHOLD = 0.90
    REGIONAL_THRESHOLD = 0.90
    HIGH_CONFIDENCE_THRESHOLD = 0.85
    REVIEW_THRESHOLD = 0.70
    AMBIGUOUS_THRESHOLD = 0.50
    
    # Food group compatibility matrix
    FOOD_GROUP_COMPAT = {
        # Same group = 1.0
        # Related groups = 0.5
        # Unrelated = 0.0
        ('CEREALS AND MILLETS', 'CEREALS AND MILLETS'): 1.0,
        ('PULSES AND LEGUMES', 'PULSES AND LEGUMES'): 1.0,
        ('LEAFY VEGETABLES', 'LEAFY VEGETABLES'): 1.0,
        ('OTHER VEGETABLES', 'OTHER VEGETABLES'): 1.0,
        ('FRUITS', 'FRUITS'): 1.0,
        ('ROOTS AND TUBERS', 'ROOTS AND TUBERS'): 1.0,
        ('CONDIMENTS AND SPICES-FRESH', 'CONDIMENTS AND SPICES-FRESH'): 1.0,
        ('CONDIMENTS AND SPICES-DRY', 'CONDIMENTS AND SPICES-DRY'): 1.0,
        ('NUTS AND OILSEEDS', 'NUTS AND OILSEEDS'): 1.0,
        ('MUSHROOMS', 'MUSHROOMS'): 1.0,
        ('MILK AND MILK PRODUCTS', 'MILK AND MILK PRODUCTS'): 1.0,
        ('EGG AND EGG PRODUCTS', 'EGG AND EGG PRODUCTS'): 1.0,
        ('POULTRY', 'POULTRY'): 1.0,
        ('ANIMAL MEAT', 'ANIMAL MEAT'): 1.0,
        ('MARINE FISH', 'MARINE FISH'): 1.0,
        ('MARINE SHELLFISH', 'MARINE SHELLFISH'): 1.0,
        ('FRESHWATER FISH AND SHELLFISH', 'FRESHWATER FISH AND SHELLFISH'): 1.0,
        ('SUGARS AND JAGGERY', 'SUGARS AND JAGGERY'): 1.0,
        ('FATS AND EDIBLE OILS', 'FATS AND EDIBLE OILS'): 1.0,
        
        # Cross-group compatibilities
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
        ('FRESHWATER FISH AND SHELLFISH', 'FRESHWATER FISH AND SHELLFISH'): 1.0,
        ('MARINE SHELLFISH', 'MARINE SHELLFISH'): 1.0,
        ('MARINE FISH', 'MARINE FISH'): 1.0,
        ('MUSHROOMS', 'MUSHROOMS'): 1.0,
        ('CONDIMENTS AND SPICES-FRESH', 'CONDIMENTS AND SPICES-FRESH'): 1.0,
        ('CONDIMENTS AND SPICES-DRY', 'CONDIMENTS AND SPICES-DRY'): 1.0,
        ('NUTS AND OILSEEDS', 'NUTS AND OILSEEDS'): 1.0,
        ('ROOTS AND TUBERS', 'ROOTS AND TUBERS'): 1.0,
        ('LEAFY VEGETABLES', 'LEAFY VEGETABLES'): 1.0,
        ('OTHER VEGETABLES', 'OTHER VEGETABLES'): 1.0,
        ('FRUITS', 'FRUITS'): 1.0,
        ('MILK AND MILK PRODUCTS', 'MILK AND MILK PRODUCTS'): 1.0,
        ('EGG AND EGG PRODUCTS', 'EGG AND EGG PRODUCTS'): 1.0,
        ('POULTRY', 'POULTRY'): 1.0,
        ('ANIMAL MEAT', 'ANIMAL MEAT'): 1.0,
        ('MARINE FISH', 'MARINE FISH'): 1.0,
        ('MARINE SHELLFISH', 'MARINE SHELLFISH'): 1.0,
        ('FRESHWATER FISH AND SHELLFISH', 'FRESHWATER FISH AND SHELLFISH'): 1.0,
        ('SUGARS AND JAGGERY', 'SUGARS AND JAGGERY'): 1.0,
        ('FATS AND EDIBLE OILS', 'FATS AND EDIBLE OILS'): 1.0,
        
        # Cross-group (lower compatibility)
        ('CEREALS AND MILLETS', 'PULSES AND LEGUMES'): 0.3,
        ('VEGETABLES', 'FRUITS'): 0.2,
        ('MEAT', 'FISH'): 0.2,
        ('DAIRY', 'MEAT'): 0.1,
    }
    
    @classmethod
    def get_food_group_compat(cls, group1: str, group2: str) -> float:
        """Get food group compatibility score."""
        if group1 == group2:
            return 1.0
        key = (group1, group2)
        if key in cls.FOOD_GROUP_COMPAT:
            return cls.FOOD_GROUP_COMPAT[key]
        key = (group2, group1)
        if key in cls.FOOD_GROUP_COMPAT:
            return cls.FOOD_GROUP_COMPAT[key]
        return 0.0


def classify_match(ingredient_text: str, ifct_record: dict, 
                   parsed_data: dict, taxonomy_category: str) -> dict:
    """
    Classify a match based on evidence.
    Returns match result with status and evidence.
    """
    # This would be implemented with the full matching logic
    pass


def get_match_hierarchy() -> list:
    """Return the matching hierarchy in priority order."""
    return [
        ('EXACT_MATCH', 1.0, 'auto'),
        ('SYNONYM_MATCH', 0.95, 'synonym_dict'),
        ('TRANSLITERATION_MATCH', 0.90, 'transliteration_map'),
        ('REGIONAL_VARIANT', 0.90, 'synonym_dict'),
        ('HIGH_CONFIDENCE_MATCH', 0.85, 'review'),
        ('PREP_STATE_COMPATIBLE', 0.80, 'review'),
        ('EDIBLE_PART_COMPATIBLE', 0.80, 'review'),
        ('VARIETY_MATCH', 0.80, 'review'),
        ('SPECIES_MATCH', 0.80, 'review'),
        ('PREP_STATE_COMPATIBLE', 0.80, 'review'),
        ('EDIBLE_PART_COMPATIBLE', 0.80, 'review'),
        ('VARIETY_MATCH', 0.80, 'review'),
        ('SPECIES_MATCH', 0.75, 'review'),
        ('COMPOSITE_DECOMPOSED', 0.70, 'review'),
        ('REVIEW_REQUIRED', 0.70, 'review'),
        ('AMBIGUOUS_MATCH', 0.50, 'review'),
        ('UNMATCHED', 0.0, None),
    ]