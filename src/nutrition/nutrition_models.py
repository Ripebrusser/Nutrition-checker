"""Nutrition Data Models - Typed data contracts for the nutrition calculation engine."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Literal
from enum import Enum
import pandas as pd


class MappingStatus(Enum):
    """Status of ingredient-to-IFCT mapping."""
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    AMBIGUOUS = "AMBIGUOUS"
    UNMATCHED = "UNMATCHED"
    CANDIDATE = "CANDIDATE"  # Not yet reviewed


class CalculationStatus(Enum):
    """Status of nutrient calculation for an ingredient."""
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    MISSING_WEIGHT = "MISSING_WEIGHT"
    MISSING_MAPPING = "MISSING_MAPPING"
    MISSING_NUTRIENTS = "MISSING_NUTRIENTS"
    INVALID_INPUT = "INVALID_INPUT"


class RecipeCalculationStatus(Enum):
    """Overall recipe nutrition calculation status."""
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    NO_MAPPED_INGREDIENTS = "NO_MAPPED_INGREDIENTS"
    UNAVAILABLE = "UNAVAILABLE"


@dataclass
class NutrientValue:
    """Nutrient value with metadata."""
    value: float
    unit: str
    per_100g: bool = True
    source: str = ""
    confidence: float = 1.0
    note: str = ""


@dataclass
class IngredientNutrition:
    """Nutrient profile for a single ingredient (legacy/internal)."""
    recipe_id: int
    ingredient_record_id: str
    original_ingredient: str
    normalized_ingredient: str
    ifct_food_code: str
    ifct_food_name: str
    ifct_food_group: str
    match_status: str
    
    # Weight information
    gross_weight_g: Optional[float] = None
    edible_weight_g: Optional[float] = None


@dataclass
class IFCTNutrientRecord:
    """IFCT nutrient record per 100g edible portion."""
    food_code: str
    food_name: str
    food_group: str
    moisture_g: Optional[float] = None
    protein_g: Optional[float] = None
    ash_g: Optional[float] = None
    fat_g: Optional[float] = None
    fibre_total_g: Optional[float] = None
    fibre_insoluble_g: Optional[float] = None
    fibre_soluble_g: Optional[float] = None
    carb_available_g: Optional[float] = None
    energy_kj: Optional[float] = None
    source_page: Optional[int] = None
    source_table: Optional[int] = None
    verification_status: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'food_code': self.food_code,
            'food_name': self.food_name,
            'food_group': self.food_group,
            'moisture_g': self.moisture_g,
            'protein_g': self.protein_g,
            'ash_g': self.ash_g,
            'fat_g': self.fat_g,
            'fibre_total_g': self.fibre_total_g,
            'fibre_insoluble_g': self.fibre_insoluble_g,
            'fibre_soluble_g': self.fibre_soluble_g,
            'carb_available_g': self.carb_available_g,
            'energy_kj': self.energy_kj,
            'source_page': self.source_page,
            'source_table': self.source_table,
            'verification_status': self.verification_status,
        }
    
    @property
    def nutrient_fields(self) -> List[str]:
        return ['moisture_g', 'protein_g', 'ash_g', 'fat_g', 'fibre_total_g', 
                'fibre_insoluble_g', 'fibre_soluble_g', 'carb_available_g', 'energy_kj']
    
    def get_nutrient(self, nutrient: str) -> Optional[float]:
        return getattr(self, nutrient, None)
    
    def has_nutrient(self, nutrient: str) -> bool:
        val = getattr(self, nutrient, None)
        return val is not None and not pd.isna(val)


@dataclass
class ApprovedMapping:
    """Verified ingredient-to-IFCT mapping decision."""
    recipe_id: int
    ingredient_record_id: str
    original_ingredient: str
    normalized_ingredient: str
    ifct_food_code: str
    ifct_food_name: str
    ifct_food_group: str
    mapping_status: MappingStatus
    preparation_state: str
    reviewer_id: str
    review_timestamp: str
    confidence: float
    evidence: str
    notes: str = ""
    
    def is_usable(self) -> bool:
        return self.mapping_status == MappingStatus.APPROVED


@dataclass
class IngredientWeightInfo:
    """Weight information for an ingredient."""
    recipe_id: int
    ingredient_record_id: str
    original_ingredient: str
    normalized_ingredient: str
    quantity: Optional[float] = None
    unit: Optional[str] = None
    gram_weight: Optional[float] = None
    gram_weight_min: Optional[float] = None
    gram_weight_max: Optional[float] = None
    conversion_status: str = "UNRESOLVED"
    household_conversion_source: Optional[str] = None
    household_conversion_confidence: Optional[float] = None
    is_edible_weight: bool = False  # True if weight already represents edible portion
    edible_portion_factor: Optional[float] = None
    edible_portion_source: Optional[str] = None
    preparation_state: str = "NOT_SPECIFIED"
    
    @property
    def has_resolved_weight(self) -> bool:
        return self.gram_weight is not None and not pd.isna(self.gram_weight) and self.gram_weight > 0
    
    @property
    def has_range_weight(self) -> bool:
        return (self.gram_weight_min is not None and not pd.isna(self.gram_weight_min) and
                self.gram_weight_max is not None and not pd.isna(self.gram_weight_max) and
                self.gram_weight_min < self.gram_weight_max)


@dataclass
class IngredientNutritionInput:
    """Input contract for ingredient nutrition calculation."""
    recipe_id: int
    ingredient_record_id: str
    original_ingredient: str
    normalized_ingredient: str
    ifct_food_code: str
    ifct_food_name: str
    ifct_food_group: str
    mapping_status: MappingStatus
    preparation_state: str
    edible_weight_g: Optional[float] = None
    nutrient_values: Optional[Dict[str, float]] = None
    source_provenance: str = ""


@dataclass
class IngredientNutritionOutput:
    """Output contract for ingredient nutrition calculation."""
    recipe_id: int
    ingredient_record_id: str
    ifct_food_code: str
    ifct_food_name: str
    ifct_food_group: str
    edible_weight_g: Optional[float]
    calculated_nutrients: Dict[str, float] = field(default_factory=dict)
    missing_nutrients: List[str] = field(default_factory=list)
    mapping_status: MappingStatus = MappingStatus.UNMATCHED
    calculation_status: CalculationStatus = CalculationStatus.INVALID_INPUT
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def has_calculations(self) -> bool:
        return len(self.calculated_nutrients) > 0
    
    @property
    def nutrient_completeness(self) -> float:
        """Proportion of standard nutrients that have values."""
        standard_nutrients = ['moisture_g', 'protein_g', 'ash_g', 'fat_g', 
                              'fibre_total_g', 'fibre_insoluble_g', 'fibre_soluble_g',
                              'carb_available_g', 'energy_kj']
        if not standard_nutrients:
            return 0.0
        present = sum(1 for n in standard_nutrients if n in self.calculated_nutrients)
        return present / len(standard_nutrients)


@dataclass
class RecipeNutritionOutput:
    """Output contract for recipe-level nutrition aggregation."""
    recipe_id: int
    total_nutrients: Dict[str, float] = field(default_factory=dict)
    nutrient_completeness: Dict[str, float] = field(default_factory=dict)
    ingredient_mapping_coverage: float = 0.0
    gram_weight_coverage: float = 0.0
    mapped_ingredient_count: int = 0
    total_ingredient_count: int = 0
    unresolved_ingredient_count: int = 0
    calculation_status: RecipeCalculationStatus = RecipeCalculationStatus.UNAVAILABLE
    ingredient_details: List[IngredientNutritionOutput] = field(default_factory=list)
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def has_any_nutrition(self) -> bool:
        return len(self.total_nutrients) > 0
    
    @property
    def overall_completeness(self) -> float:
        if not self.nutrient_completeness:
            return 0.0
        return sum(self.nutrient_completeness.values()) / len(self.nutrient_completeness)


@dataclass
class NutrientCalculationResult:
    """Complete result of a nutrient calculation run."""
    recipe_outputs: List[RecipeNutritionOutput] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


NUTRIENT_NAMES = [
    'moisture_g', 'protein_g', 'ash_g', 'fat_g', 
    'fibre_total_g', 'fibre_insoluble_g', 'fibre_soluble_g',
    'carb_available_g', 'energy_kj'
]

NUTRIENT_UNITS = {
    'moisture_g': 'g',
    'protein_g': 'g',
    'ash_g': 'g',
    'fat_g': 'g',
    'fibre_total_g': 'g',
    'fibre_insoluble_g': 'g',
    'fibre_soluble_g': 'g',
    'carb_available_g': 'g',
    'energy_kj': 'kJ',
}