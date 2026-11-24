"""Ingredient Mapping Interface - Strict interface for verified IFCT mappings only."""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import pandas as pd
import hashlib
import json
from pathlib import Path

from .nutrition_models import (
    MappingStatus, ApprovedMapping, IFCTNutrientRecord,
    IngredientWeightInfo, IngredientNutritionInput
)


class MappingDecision(Enum):
    """Mapping decision from review."""
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    AMBIGUOUS = "AMBIGUOUS"
    DEFER = "DEFER"


@dataclass
class MappingReviewRecord:
    """Single mapping review decision record."""
    recipe_id: int
    ingredient_record_id: str
    original_ingredient: str
    normalized_ingredient: str
    ifct_food_code: str
    ifct_food_name: str
    ifct_food_group: str
    decision: MappingDecision
    reviewer_id: str
    timestamp: str
    confidence: float
    evidence: str
    preparation_state: str
    notes: str = ""
    
    def to_approved_mapping(self) -> Optional[ApprovedMapping]:
        if self.decision != MappingDecision.APPROVE:
            return None
        return ApprovedMapping(
            recipe_id=self.recipe_id,
            ingredient_record_id=self.ingredient_record_id,
            original_ingredient=self.original_ingredient,
            normalized_ingredient=self.normalized_ingredient,
            ifct_food_code=self.ifct_food_code,
            ifct_food_name=self.ifct_food_name,
            ifct_food_group=self.ifct_food_group,
            mapping_status=MappingStatus.APPROVED,
            preparation_state=self.preparation_state,
            reviewer_id=self.reviewer_id,
            review_timestamp=self.timestamp,
            confidence=self.confidence,
            evidence=self.evidence,
            notes=self.notes,
        )


class ApprovedMappingStore:
    """Strict store for approved ingredient-to-IFCT mappings only."""
    
    def __init__(self):
        self._mappings: Dict[str, ApprovedMapping] = {}  # key: (recipe_id, ingredient_record_id)
        self._by_recipe: Dict[int, List[ApprovedMapping]] = {}
        self._by_ifct_code: Dict[str, List[ApprovedMapping]] = {}
        self._decision_log: List[MappingReviewRecord] = []
    
    def _make_key(self, recipe_id: int, ingredient_record_id: str) -> str:
        return f"{recipe_id}:{ingredient_record_id}"
    
    def add_mapping(self, mapping: ApprovedMapping) -> bool:
        """Add an approved mapping. Returns True if added, False if duplicate with different data."""
        key = self._make_key(mapping.recipe_id, mapping.ingredient_record_id)
        
        if key in self._mappings:
            existing = self._mappings[key]
            if existing.ifct_food_code != mapping.ifct_food_code:
                raise ValueError(
                    f"Duplicate mapping for {key} with different IFCT code: "
                    f"existing={existing.ifct_food_code}, new={mapping.ifct_food_code}"
                )
            return False  # Already exists with same data
        
        if mapping.mapping_status != MappingStatus.APPROVED:
            raise ValueError(f"Only APPROVED mappings can be added, got {mapping.mapping_status}")
        
        self._mappings[key] = mapping
        self._by_recipe.setdefault(mapping.recipe_id, []).append(mapping)
        self._by_ifct_code.setdefault(mapping.ifct_food_code, []).append(mapping)
        return True
    
    def add_review_decision(self, decision: MappingReviewRecord) -> Optional[ApprovedMapping]:
        """Process a review decision. Returns ApprovedMapping if approved, None otherwise."""
        if decision.decision == MappingDecision.APPROVE:
            approved = decision.to_approved_mapping()
            if approved:
                self.add_mapping(approved)
                self._decision_log.append(decision)
                return approved
        elif decision.decision == MappingDecision.REJECT:
            # Log rejection but don't store as usable mapping
            self._decision_log.append(decision)
        elif decision.decision in (MappingDecision.AMBIGUOUS, MappingDecision.DEFER):
            self._decision_log.append(decision)
        return None
    
    def get_mapping(self, recipe_id: int, ingredient_record_id: str) -> Optional[ApprovedMapping]:
        """Get approved mapping for a specific ingredient record."""
        key = self._make_key(recipe_id, ingredient_record_id)
        return self._mappings.get(key)
    
    def get_mappings_for_recipe(self, recipe_id: int) -> List[ApprovedMapping]:
        """Get all approved mappings for a recipe."""
        return self._by_recipe.get(recipe_id, [])
    
    def get_mappings_for_ifct(self, ifct_food_code: str) -> List[ApprovedMapping]:
        """Get all approved mappings using a specific IFCT food code."""
        return self._by_ifct_code.get(ifct_food_code, [])
    
    def has_approved_mapping(self, recipe_id: int, ingredient_record_id: str) -> bool:
        """Check if an approved mapping exists."""
        key = self._make_key(recipe_id, ingredient_record_id)
        return key in self._mappings
    
    def get_all_mappings(self) -> List[ApprovedMapping]:
        """Get all approved mappings."""
        return list(self._mappings.values())
    
    def get_decision_log(self) -> List[MappingReviewRecord]:
        """Get all review decisions."""
        return self._decision_log.copy()
    
    def stats(self) -> Dict[str, Any]:
        """Get store statistics."""
        decisions = self._decision_log
        return {
            'total_approved': len(self._mappings),
            'total_reviewed': len(decisions),
            'approved_count': sum(1 for d in decisions if d.decision == MappingDecision.APPROVE),
            'rejected_count': sum(1 for d in decisions if d.decision == MappingDecision.REJECT),
            'ambiguous_count': sum(1 for d in decisions if d.decision == MappingDecision.AMBIGUOUS),
            'deferred_count': sum(1 for d in decisions if d.decision == MappingDecision.DEFER),
            'unique_recipes': len(self._by_recipe),
            'unique_ifct_codes': len(self._by_ifct_code),
        }


class StrictMappingInterface:
    """
    Strict interface for ingredient-to-IFCT mappings.
    
    Rules:
    1. Only explicitly approved mappings can enter calculation
    2. Rejected mappings are never used
    3. Ambiguous mappings are never used automatically
    4. Unmatched ingredients remain unmatched
    5. Candidate similarity scores are not probabilities
    6. Preparation-state compatibility is enforced
    7. IFCT raw-food basis is respected
    """
    
    def __init__(self, approved_store: ApprovedMappingStore, ifct_data: pd.DataFrame):
        self.approved_store = approved_store
        self.ifct_data = ifct_data
        self._ifct_index = self._build_ifct_index()
    
    def _build_ifct_index(self) -> Dict[str, IFCTNutrientRecord]:
        """Build lookup index for IFCT records."""
        index = {}
        for _, row in self.ifct_data.iterrows():
            record = IFCTNutrientRecord(
                food_code=row['food_code'],
                food_name=row['food_name'],
                food_group=row['food_group'],
                moisture_g=self._parse_nutrient(row.get('moisture_g')),
                protein_g=self._parse_nutrient(row.get('protein_g')),
                ash_g=self._parse_nutrient(row.get('ash_g')),
                fat_g=self._parse_nutrient(row.get('fat_g')),
                fibre_total_g=self._parse_nutrient(row.get('fibre_total_g')),
                fibre_insoluble_g=self._parse_nutrient(row.get('fibre_insoluble_g')),
                fibre_soluble_g=self._parse_nutrient(row.get('fibre_soluble_g')),
                carb_available_g=self._parse_nutrient(row.get('carb_available_g')),
                energy_kj=self._parse_nutrient(row.get('energy_kj')),
                source_page=row.get('source_page'),
                source_table=row.get('source_table'),
                verification_status=row.get('verification_status', ''),
            )
            index[row['food_code']] = record
        return index
    
    def _parse_nutrient(self, value: Any) -> Optional[float]:
        """Parse nutrient value from string (may contain ± notation)."""
        if value is None or pd.isna(value):
            return None
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            # Handle "61.46±0.60" format - take the mean value
            if '±' in value:
                try:
                    return float(value.split('±')[0].strip())
                except ValueError:
                    return None
            try:
                return float(value)
            except ValueError:
                return None
        return None
    
    def get_approved_mapping(self, recipe_id: int, ingredient_record_id: str) -> Optional[ApprovedMapping]:
        """Get approved mapping for an ingredient. Returns None if not approved."""
        return self.approved_store.get_mapping(recipe_id, ingredient_record_id)
    
    def get_ifct_record(self, ifct_food_code: str) -> Optional[IFCTNutrientRecord]:
        """Get IFCT nutrient record by food code."""
        return self._ifct_index.get(ifct_food_code)
    
    def create_nutrition_input(
        self,
        recipe_id: int,
        ingredient_record_id: str,
        weight_info: IngredientWeightInfo
    ) -> Optional[IngredientNutritionInput]:
        """
        Create nutrition calculation input from approved mapping and weight info.
        Returns None if no approved mapping exists.
        """
        mapping = self.get_approved_mapping(recipe_id, ingredient_record_id)
        if not mapping:
            return None
        
        ifct_record = self.get_ifct_record(mapping.ifct_food_code)
        if not ifct_record:
            return None
        
        # Build nutrient values dict from IFCT record
        nutrient_values = {}
        for field in ifct_record.nutrient_fields:
            val = ifct_record.get_nutrient(field)
            if val is not None:
                nutrient_values[field] = val
        
        # Determine edible weight
        edible_weight = self._resolve_edible_weight(weight_info, mapping)
        
        return IngredientNutritionInput(
            recipe_id=recipe_id,
            ingredient_record_id=ingredient_record_id,
            original_ingredient=mapping.original_ingredient,
            normalized_ingredient=mapping.normalized_ingredient,
            ifct_food_code=mapping.ifct_food_code,
            ifct_food_name=mapping.ifct_food_name,
            ifct_food_group=mapping.ifct_food_group,
            mapping_status=mapping.mapping_status,
            preparation_state=mapping.preparation_state,
            edible_weight_g=edible_weight,
            nutrient_values=nutrient_values,
            source_provenance=f"mapping:{mapping.reviewer_id}:{mapping.review_timestamp};"
                              f"ifct:{ifct_record.verification_status};"
                              f"weight:{weight_info.conversion_status}"
        )
    
    def _resolve_edible_weight(
        self,
        weight_info: IngredientWeightInfo,
        mapping: ApprovedMapping
    ) -> Optional[float]:
        """
        Resolve edible weight from weight info.
        
        Rules:
        - If weight is already edible portion, use as-is
        - If weight is as-purchased, need validated edible portion factor
        - If no factor available, return None (missing)
        """
        if not weight_info.has_resolved_weight:
            return None
        
        gross_weight = weight_info.gram_weight
        
        # If already marked as edible weight, use directly
        if weight_info.is_edible_weight:
            return gross_weight
        
        # If edible portion factor provided, apply it
        if weight_info.edible_portion_factor is not None:
            if weight_info.edible_portion_factor <= 0 or weight_info.edible_portion_factor > 1:
                raise ValueError(f"Invalid edible portion factor: {weight_info.edible_portion_factor}")
            return gross_weight * weight_info.edible_portion_factor
        
        # No edible portion factor available - cannot determine edible weight
        return None
    
    def validate_preparation_compatibility(
        self,
        ingredient_prep_state: str,
        ifct_record: IFCTNutrientRecord
    ) -> tuple[bool, str]:
        """
        Validate preparation state compatibility with IFCT raw-food basis.
        
        IFCT data is primarily for raw foods. Cooked/prepared foods need
        explicit validation or separate IFCT entries.
        """
        prep_lower = ingredient_prep_state.lower()
        
        # Raw-compatible states
        raw_compatible = {'raw', 'fresh', 'not_specified', 'whole', 'uncooked'}
        # States that may be compatible with IFCT raw values
        possibly_compatible = {'powdered', 'dried', 'ground', 'flour'}
        # States requiring cooked IFCT entries (not in our dataset)
        cooked_states = {'cooked', 'boiled', 'fried', 'roasted', 'baked', 'steamed'}
        
        if prep_lower in raw_compatible:
            return True, "Preparation state compatible with IFCT raw food basis"
        elif prep_lower in possibly_compatible:
            return True, "Preparation state possibly compatible - review recommended"
        elif prep_lower in cooked_states:
            return False, f"Preparation state '{ingredient_prep_state}' requires cooked IFCT entry (not available)"
        else:
            return True, f"Unknown preparation state '{ingredient_prep_state}' - treated as possibly compatible"
    
    def get_mapping_coverage(self, recipe_ids: List[int]) -> Dict[str, Any]:
        """Get mapping coverage statistics for a set of recipes."""
        total_ingredients = 0
        mapped_ingredients = 0
        unmapped_ingredients = 0
        
        for recipe_id in recipe_ids:
            mappings = self.approved_store.get_mappings_for_recipe(recipe_id)
            mapped_ingredients += len(mappings)
            # Would need full ingredient list for accurate total
        
        return {
            'mapped_ingredients': mapped_ingredients,
            'recipes_with_mappings': len([r for r in recipe_ids 
                                           if self.approved_store.get_mappings_for_recipe(r)]),
        }


def load_approved_mappings_from_jsonl(path: Path) -> ApprovedMappingStore:
    """Load approved mappings from JSONL review decisions file."""
    store = ApprovedMappingStore()
    
    if not path.exists():
        return store
    
    with open(path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                decision = MappingReviewRecord(**data)
                store.add_review_decision(decision)
            except Exception as e:
                print(f"Warning: Failed to parse line {line_num} in {path}: {e}")
    
    return store


def save_approved_mappings_to_jsonl(store: ApprovedMappingStore, path: Path):
    """Save review decisions to JSONL file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        for decision in store.get_decision_log():
            f.write(json.dumps(decision.__dict__) + '\n')