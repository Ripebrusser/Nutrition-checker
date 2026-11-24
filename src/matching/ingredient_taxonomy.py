"""Ingredient Taxonomy - Category definitions and classification logic."""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Set
import re


class MatchCategory(Enum):
    """Ingredient matching category taxonomy."""
    EXACT_IDENTITY = "EXACT_IDENTITY"
    VERIFIED_SYNONYM = "VERIFIED_SYNONYM"
    TRANSLITERATION = "TRANSLITERATION"
    REGIONAL_VARIANT = "REGIONAL_VARIANT"
    INGREDIENT_VARIETY = "INGREDIENT_VARIETY"
    SPECIES_DISTINCTION = "SPECIES_DISTINCTION"
    PREPARATION_STATE = "PREPARATION_STATE"
    EDIBLE_PART = "EDIBLE_PART"
    COMPOSITE_INGREDIENT = "COMPOSITE_INGREDIENT"
    AMBIGUOUS = "AMBIGUOUS"
    ABSENT_FROM_IFCT = "ABSENT_FROM_IFCT"


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
class TaxonomyCategory:
    """Taxonomy category definition."""
    category: MatchCategory
    auto_accept: bool
    requires_review: bool
    evidence_required: str
    description: str
    examples: list


# Taxonomy category definitions
TAXONOMY_CATEGORIES = {
    MatchCategory.EXACT_IDENTITY: TaxonomyCategory(
        category=MatchCategory.EXACT_IDENTITY,
        auto_accept=True,
        requires_review=False,
        evidence_required="Exact string equality on normalized food_name",
        description="Normalized ingredient string exactly equals IFCT food_name",
        examples=["onion (bulb) ↔ IFCT 'onion (bulb)'", "cumin seeds ↔ IFCT 'cumin seeds'"]
    ),
    MatchCategory.VERIFIED_SYNONYM: TaxonomyCategory(
        category=MatchCategory.VERIFIED_SYNONYM,
        auto_accept=True,
        requires_review=False,
        evidence_required="Synonym dictionary entry with confidence ≥ 0.95",
        description="Verified synonym in dictionary with confidence ≥ 0.95",
        examples=["toor dal → pigeon pea", "jeera → cumin seeds", "haldi → turmeric powder"]
    ),
    MatchCategory.TRANSLITERATION: TaxonomyCategory(
        category=MatchCategory.TRANSLITERATION,
        auto_accept=True,
        requires_review=False,
        evidence_required="Devanagari/transliteration match in synonym dictionary (conf ≥ 0.90)",
        description="Verified Hindi-English transliteration match",
        examples=["हल्दी → turmeric powder", "जीरा → cumin seeds", "हल्दी → turmeric powder"]
    ),
    MatchCategory.REGIONAL_VARIANT: TaxonomyCategory(
        category=MatchCategory.REGIONAL_VARIANT,
        auto_accept=True,
        requires_review=False,
        evidence_required="Regional name in synonym dictionary (conf ≥ 0.90)",
        description="Regional name variant in synonym dictionary",
        examples=["arhar dal → pigeon pea", "tuvar dal → pigeon pea", "kala chana → chickpea (desi)"]
    ),
    MatchCategory.INGREDIENT_VARIETY: TaxonomyCategory(
        category=MatchCategory.INGREDIENT_VARIETY,
        auto_accept=False,
        requires_review=True,
        evidence_required="Same species, different cultivar/variety name",
        description="Same species, different cultivar/variety with potentially different nutrient profile",
        examples=["basmati rice vs sona masuri rice", "green gram vs moong dal"]
    ),
    MatchCategory.SPECIES_DISTINCTION: TaxonomyCategory(
        category=MatchCategory.SPECIES_DISTINCTION,
        auto_accept=False,
        requires_review=True,
        evidence_required="Scientific name verification",
        description="Different species (same/different genus) with different nutrient profiles",
        examples=["bengal gram vs chickpea", "green gram vs black gram"]
    ),
    MatchCategory.PREPARATION_STATE: TaxonomyCategory(
        category=MatchCategory.PREPARATION_STATE,
        auto_accept=False,
        requires_review=True,
        evidence_required="Preparation descriptor in ingredient text",
        description="Fresh vs dried, raw vs cooked, whole vs processed",
        examples=["fresh coconut vs dried coconut", "raw onion vs fried onion", "whole wheat vs refined wheat flour"]
    ),
    MatchCategory.EDIBLE_PART: TaxonomyCategory(
        category=MatchCategory.EDIBLE_PART,
        auto_accept=False,
        requires_review=True,
        evidence_required="Explicit edible part descriptor in ingredient text",
        description="Different edible parts of same food",
        examples=["coconut water vs coconut kernel", "orange juice vs orange fruit", "chicken breast vs chicken liver"]
    ),
    MatchCategory.COMPOSITE_INGREDIENT: TaxonomyCategory(
        category=MatchCategory.COMPOSITE_INGREDIENT,
        auto_accept=False,
        requires_review=True,
        evidence_required="Multi-component ingredient or prepared mixture",
        description="Multi-component ingredients or prepared mixtures",
        examples=["ginger garlic paste", "onion tomato paste", "garam masala", "curry powder"]
    ),
    MatchCategory.AMBIGUOUS: TaxonomyCategory(
        category=MatchCategory.AMBIGUOUS,
        auto_accept=False,
        requires_review=True,
        evidence_required="Human disambiguation required",
        description="Generic/ambiguous name mapping to multiple IFCT entries",
        examples=["dal (any pulse)", "rice (any variety)", "oil (any type)", "dalia (broken wheat/rice/millet)"]
    ),
    MatchCategory.ABSENT_FROM_IFCT: TaxonomyCategory(
        category=MatchCategory.ABSENT_FROM_IFCT,
        auto_accept=False,
        requires_review=True,
        evidence_required="No candidate in IFCT 528 foods with similarity ≥ 0.50",
        description="Ingredient absent from IFCT 528 foods",
        examples=["quinoa", "chia seeds", "kale", "zucchini", "broccoli", "avocado", "blueberry"]
    ),
}


class IngredientTaxonomy:
    """Ingredient taxonomy classifier."""

    def __init__(self):
        self.categories = TAXONOMY_CATEGORIES
        self._compile_patterns()

    def _compile_patterns(self):
        """Compile regex patterns for category detection."""
        self.prep_patterns = {
            'raw': re.compile(r'\b(raw|fresh|uncooked)\b', re.IGNORECASE),
            'cooked': re.compile(r'\b(cooked|boiled|fried|roasted|steamed|baked|grilled)\b', re.IGNORECASE),
            'dried': re.compile(r'\b(dried|dry|dehydrated|powder)\b', re.IGNORECASE),
            'fresh': re.compile(r'\b(fresh)\b', re.IGNORECASE),
            'chopped': re.compile(r'\b(chopped|diced|sliced|minced|grated|crushed|mashed|peeled)\b', re.IGNORECASE),
        }

        self.edible_part_patterns = {
            'seed': re.compile(r'\b(seed|seeds)\b', re.IGNORECASE),
            'leaf': re.compile(r'\b(leaf|leaves)\b', re.IGNORECASE),
            'root': re.compile(r'\b(root|roots)\b', re.IGNORECASE),
            'stem': re.compile(r'\b(stem|stems)\b', re.IGNORECASE),
            'flower': re.compile(r'\b(flower|flowers)\b', re.IGNORECASE),
            'fruit': re.compile(r'\b(fruit|fruits)\b', re.IGNORECASE),
            'seed': re.compile(r'\b(seed|seeds)\b', re.IGNORECASE),
            'peel': re.compile(r'\b(peel|skin|rind)\b', re.IGNORECASE),
            'pulp': re.compile(r'\b(pulp)\b', re.IGNORECASE),
            'juice': re.compile(r'\b(juice)\b', re.IGNORECASE),
            'water': re.compile(r'\b(water)\b', re.IGNORECASE),
            'milk': re.compile(r'\b(milk)\b', re.IGNORECASE),
            'oil': re.compile(r'\b(oil)\b', re.IGNORECASE),
            'paste': re.compile(r'\b(paste)\b', re.IGNORECASE),
            'powder': re.compile(r'\b(powder)\b', re.IGNORECASE),
            'flour': re.compile(r'\b(flour)\b', re.IGNORECASE),
            'seed': re.compile(r'\b(seed|seeds)\b', re.IGNORECASE),
            'nut': re.compile(r'\b(nut|nuts)\b', re.IGNORECASE),
            'kernel': re.compile(r'\b(kernel)\b', re.IGNORECASE),
            'flesh': re.compile(r'\b(flesh)\b', re.IGNORECASE),
            'peel': re.compile(r'\b(peel|skin|rind)\b', re.IGNORECASE),
            'seed': re.compile(r'\b(seed|seeds)\b', re.IGNORECASE),
            'leaf': re.compile(r'\b(leaf|leaves)\b', re.IGNORECASE),
            'root': re.compile(r'\b(root|roots)\b', re.IGNORECASE),
        }

        self.composite_patterns = [
            re.compile(r'\b(paste|masala|powder|batter|chutney|pickle|sauce|curry)\b', re.IGNORECASE),
            re.compile(r'\b(ginger\s+garlic|onion\s+tomato|ginger\s+chili)\s+(paste|masala)\b', re.IGNORECASE),
        ]

        self.ambiguous_terms = {
            'dal', 'rice', 'oil', 'milk', 'salt', 'sugar', 'flour', 'atta', 'maida', 'besan',
            'dalia', 'rava', 'suji', 'poha', 'sevai', 'vermicelli', 'noodles',
            'bread', 'roti', 'chapati', 'paratha', 'naan', 'kulcha',
            'curry', 'masala', 'gravy', 'sauce', 'chutney', 'pickle',
            'salad', 'soup', 'stew', 'biryani', 'pulao', 'khichdi',
            'papad', 'papadum', 'fry', 'pakora', 'vada', 'bhaji',
            'chutney', 'raita', 'dip', 'spread', 'jam', 'jam', 'jelly',
            'ketchup', 'sauce', 'mayonnaise', 'mayo', 'mustard',
        }

    def classify(self, normalized_ingredient: str, parsed_data: dict) -> list:
        """
        Classify ingredient into taxonomy categories.
        Returns list of applicable categories (can be multiple).
        """
        categories = []
        ingredient_lower = normalized_ingredient.lower()

        # Check for exact identity (will be handled by exact match)
        # Check for verified synonym (handled by synonym matching)
        # Check for transliteration (handled separately)

        # Check preparation state
        prep_state = self._detect_prep_state(normalized_ingredient)
        if prep_state:
            categories.append(MatchCategory.PREPARATION_STATE)

        # Check edible part
        edible_part = self._detect_edible_part(normalized_ingredient)
        if edible_part:
            categories.append(MatchCategory.EDIBLE_PART)

        # Check composite ingredient
        if self._is_composite(normalized_ingredient):
            categories.append(MatchCategory.COMPOSITE_INGREDIENT)

        # Check ambiguous
        if self._is_ambiguous(normalized_ingredient):
            categories.append(MatchCategory.AMBIGUOUS)

        # Check preparation state from parsed data
        prep_from_parsed = parsed_data.get('preparation')
        if prep_state:
            categories.append(MatchCategory.PREPARATION_STATE)

        # Check edible part from parsed data
        # (would need more sophisticated parsing)

        return categories

    def _detect_prep_state(self, text: str) -> str:
        """Detect preparation state from text."""
        text_lower = text.lower()
        if self.prep_patterns['cooked'].search(text_lower):
            return 'cooked'
        elif self.prep_patterns['fried'].search(text_lower):
            return 'fried'
        elif self.prep_patterns['roasted'].search(text_lower):
            return 'roasted'
        elif self.prep_patterns['steamed'].search(text_lower):
            return 'steamed'
        elif self.prep_patterns['boiled'].search(text_lower):
            return 'boiled'
        elif self.prep_patterns['raw'].search(text_lower):
            return 'raw'
        elif self.prep_patterns['fresh'].search(text_lower):
            return 'fresh'
        elif self.prep_patterns['dried'].search(text_lower):
            return 'dried'
        elif self.prep_patterns['chopped'].search(text_lower):
            return 'chopped'
        return 'unknown'

    def _detect_edible_part(self, text: str) -> list:
        """Detect edible part mentions."""
        parts = []
        for part, pattern in self.edible_part_patterns.items():
            if pattern.search(text):
                parts.append(part)
        return parts

    def _is_composite(self, text: str) -> bool:
        """Check if ingredient is a composite/prepared mixture."""
        text_lower = text.lower()
        for pattern in self.composite_patterns:
            if pattern.search(text_lower):
                return True
        return False

    def _is_ambiguous(self, text: str) -> bool:
        """Check if ingredient name is ambiguous."""
        text_lower = text.lower().strip()
        return text_lower in self.ambiguous_terms

    def get_category_info(self, category: MatchCategory) -> dict:
        """Get category information."""
        if category in self.categories:
            cat = self.categories[category]
            return {
                'category': category.value,
                'auto_accept': cat.auto_accept,
                'requires_review': cat.requires_review,
                'evidence_required': cat.evidence_required,
                'description': cat.description,
                'examples': cat.examples
            }
        return {}


# Global taxonomy instance
taxonomy = IngredientTaxonomy()


def classify_ingredient(normalized_ingredient: str, parsed_data: dict = None) -> list:
    """Classify ingredient into taxonomy categories."""
    if parsed_data is None:
        parsed_data = {}
    return taxonomy.classify(normalized_ingredient, parsed_data)


def get_category_info(category: MatchCategory) -> dict:
    """Get category information."""
    return taxonomy.get_category_info(category)


# ============================================================
# HOUSEHOLD MEASUREMENTS RAW DATA
# ============================================================

HOUSEHOLD_MEASUREMENTS_RAW = [
    ("basmati rice (raw)", "cup", 195.0, "USDA", 0.95, "verified"),
    ("rice (raw)", "cup", 195.0, "USDA", 0.85, "verified"),
    ("wheat flour (whole)", "cup", 120.0, "USDA", 0.95, "verified"),
    ("wheat flour (refined)", "cup", 125.0, "USDA", 0.95, "verified"),
    ("chickpea flour (besan)", "cup", 92.0, "USDA", 0.95, "verified"),
    ("rice flour", "cup", 158.0, "USDA", 0.90, "verified"),
    ("semolina (coarse)", "cup", 167.0, "USDA", 0.90, "verified"),
    ("sugar (white)", "cup", 200.0, "USDA", 0.99, "verified"),
    ("brown sugar", "cup", 220.0, "USDA", 0.95, "verified"),
    ("jaggery", "cup", 180.0, "Indian kitchen", 0.85, "verified"),
    ("mustard oil", "tablespoon", 13.5, "USDA", 0.95, "verified"),
    ("coconut oil", "tablespoon", 13.6, "USDA", 0.95, "verified"),
    ("groundnut oil", "tablespoon", 13.5, "USDA", 0.95, "verified"),
    ("sesame oil", "tablespoon", 13.6, "USDA", 0.95, "verified"),
    ("sunflower oil", "tablespoon", 13.6, "USDA", 0.95, "verified"),
    ("ghee", "tablespoon", 12.8, "USDA", 0.95, "verified"),
    ("butter", "tablespoon", 14.2, "USDA", 0.99, "verified"),
    ("cumin seeds", "tablespoon", 6.0, "USDA", 0.90, "verified"),
    ("cumin powder", "tablespoon", 6.0, "USDA", 0.90, "verified"),
    ("coriander seeds", "tablespoon", 5.0, "USDA", 0.90, "verified"),
    ("coriander powder", "tablespoon", 5.0, "USDA", 0.90, "verified"),
    ("turmeric powder", "tablespoon", 9.0, "USDA", 0.90, "verified"),
    ("red chili powder", "tablespoon", 7.5, "USDA", 0.90, "verified"),
    ("black pepper", "tablespoon", 7.0, "USDA", 0.90, "verified"),
    ("mustard seeds", "tablespoon", 11.0, "USDA", 0.90, "verified"),
    ("fenugreek seeds", "tablespoon", 11.0, "USDA", 0.90, "verified"),
    ("kasuri methi", "tablespoon", 3.0, "USDA", 0.85, "verified"),
    ("fennel seeds", "tablespoon", 5.5, "USDA", 0.90, "verified"),
    ("carom seeds", "tablespoon", 11.0, "USDA", 0.85, "verified"),
    ("nigella seeds", "tablespoon", 9.0, "USDA", 0.85, "verified"),
    ("asafoetida", "teaspoon", 2.0, "Indian kitchen", 0.80, "verified"),
    ("bay leaf", "piece", 0.5, "USDA", 0.80, "verified"),
    ("cinnamon (stick)", "piece", 5.0, "USDA", 0.85, "verified"),
    ("cinnamon powder", "tablespoon", 7.5, "USDA", 0.90, "verified"),
    ("clove", "piece", 0.2, "USDA", 0.85, "verified"),
    ("cardamom (green)", "piece", 0.6, "Indian kitchen", 0.85, "verified"),
    ("cardamom (black)", "piece", 1.5, "Indian kitchen", 0.85, "verified"),
    ("nutmeg", "teaspoon", 2.2, "USDA", 0.90, "verified"),
    ("mace", "teaspoon", 2.0, "USDA", 0.85, "verified"),
    ("poppy seeds", "tablespoon", 9.0, "USDA", 0.85, "verified"),
    ("white sesame seeds", "tablespoon", 9.0, "USDA", 0.90, "verified"),
    ("black sesame seeds", "tablespoon", 9.0, "USDA", 0.90, "verified"),
    ("onion (bulb)", "cup", 160.0, "USDA", 0.95, "verified"),
    ("garlic", "clove", 3.0, "USDA", 0.99, "verified"),
    ("ginger", "tablespoon", 6.0, "USDA", 0.90, "verified"),
    ("tomato", "piece", 123.0, "USDA", 0.95, "verified"),
    ("green chili", "piece", 7.0, "Indian kitchen", 0.90, "verified"),
    ("red chili (fresh)", "piece", 5.0, "Indian kitchen", 0.85, "verified"),
    ("green peas (fresh)", "cup", 145.0, "USDA", 0.95, "verified"),
    ("carrot", "cup", 128.0, "USDA", 0.95, "verified"),
    ("cauliflower", "cup", 100.0, "USDA", 0.95, "verified"),
    ("cabbage", "cup", 89.0, "USDA", 0.95, "verified"),
    ("potato", "piece", 173.0, "USDA", 0.95, "verified"),
    ("sweet potato", "piece", 130.0, "USDA", 0.95, "verified"),
    ("mango (ripe)", "piece", 200.0, "USDA", 0.90, "verified"),
    ("banana (ripe)", "piece", 118.0, "USDA", 0.95, "verified"),
    ("apple", "piece", 182.0, "USDA", 0.95, "verified"),
    ("pigeon pea (toor dal)", "cup", 200.0, "USDA", 0.95, "verified"),
    ("green gram (split) (moong dal)", "cup", 195.0, "USDA", 0.95, "verified"),
    ("black gram (split) (urad dal)", "cup", 195.0, "USDA", 0.95, "verified"),
    ("bengal gram (split) (chana dal)", "cup", 190.0, "USDA", 0.95, "verified"),
    ("chickpea (kabuli)", "cup", 164.0, "USDA", 0.95, "verified"),
    ("red lentil (split) (masoor dal)", "cup", 195.0, "USDA", 0.95, "verified"),
    ("cashew", "cup", 137.0, "USDA", 0.95, "verified"),
    ("almond", "cup", 143.0, "USDA", 0.95, "verified"),
    ("peanut (raw)", "cup", 146.0, "USDA", 0.95, "verified"),
    ("fresh coconut kernel", "cup", 80.0, "USDA", 0.90, "verified"),
    ("dried coconut", "cup", 93.0, "USDA", 0.95, "verified"),
]

# Build household DB
HOUSEHOLD_DB = {}
for item in HOUSEHOLD_MEASUREMENTS_RAW:
    ingredient, unit, mass, source, confidence, verification = item
    key = (ingredient.lower().strip(), unit.lower().strip())
    if key not in HOUSEHOLD_DB or confidence > HOUSEHOLD_DB[key]['confidence']:
        HOUSEHOLD_DB[key] = {
            'mass_g': mass,
            'source': source,
            'confidence': confidence
        }

HOUSEHOLD_MEASUREMENTS_RAW = HOUSEHOLD_MEASUREMENTS_RAW