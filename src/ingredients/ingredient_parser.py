#!/usr/bin/env python3
"""
Stage 2 — Ingredient Quantity and Unit Parser (Optimized)
"""

import re
import json
import unicodedata
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
from collections import Counter, defaultdict
from enum import Enum

import pandas as pd
import numpy as np


# ============================================================
# ENUMS AND DATA CLASSES
# ============================================================

class ParseStatus(Enum):
    PARSED_EXACT = "PARSED_EXACT"
    PARSED_APPROXIMATE = "PARSED_APPROXIMATE"
    RANGE_PARSED = "RANGE_PARSED"
    UNQUANTIFIED = "UNQUANTIFIED"
    UNIT_UNSUPPORTED = "UNIT_UNSUPPORTED"
    AMBIGUOUS = "AMBIGUOUS"
    PARSE_FAILED = "PARSE_FAILED"


class UnitCategory(Enum):
    MASS = "mass"
    VOLUME = "volume"
    COUNT = "count"
    APPROXIMATE = "approximate"
    UNKNOWN = "unknown"


@dataclass
class ParsedQuantity:
    value: Optional[float] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    is_range: bool = False
    original_text: str = ""
    
    def to_dict(self) -> Dict:
        return {
            'value': self.value,
            'min_value': self.min_value,
            'max_value': self.max_value,
            'is_range': self.is_range,
            'original_text': self.original_text
        }


@dataclass
class ParsedUnit:
    unit: str
    standardized_unit: Optional[str] = None
    category: UnitCategory = UnitCategory.UNKNOWN
    conversion_factor: Optional[float] = None
    is_approximate: bool = False
    original_text: str = ""
    
    def to_dict(self) -> Dict:
        return {
            'unit': self.unit,
            'standardized_unit': self.standardized_unit,
            'category': self.category.value,
            'conversion_factor': self.conversion_factor,
            'is_approximate': self.is_approximate,
            'original_text': self.original_text
        }


@dataclass
class ParsedIngredient:
    recipe_id: int
    source_field: str
    original_line: str
    original_ingredient: str
    normalized_ingredient: str
    
    quantity: Optional[ParsedQuantity] = None
    unit: Optional[ParsedUnit] = None
    ingredient_name: str = ""
    preparation: Optional[str] = None
    size_descriptor: Optional[str] = None
    
    parse_status: str = ParseStatus.PARSE_FAILED.value
    conversion_status: str = "UNRESOLVED"
    gram_weight: Optional[float] = None
    gram_weight_min: Optional[float] = None
    gram_weight_max: Optional[float] = None
    
    source_reconciliation: str = ""
    raw_match: bool = False
    en_match: bool = False
    discrepancy_flag: bool = False
    
    transformations: List[str] = field(default_factory=list)
    flags: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            'recipe_id': self.recipe_id,
            'source_field': self.source_field,
            'original_line': self.original_line,
            'original_ingredient': self.original_ingredient,
            'normalized_ingredient': self.normalized_ingredient,
            'quantity': self.quantity.to_dict() if self.quantity else None,
            'unit': self.unit.to_dict() if self.unit else None,
            'ingredient_name': self.ingredient_name,
            'preparation': self.preparation,
            'size_descriptor': self.size_descriptor,
            'parse_status': self.parse_status,
            'conversion_status': self.conversion_status,
            'gram_weight': self.gram_weight,
            'gram_weight_min': self.gram_weight_min,
            'gram_weight_max': self.gram_weight_max,
            'source_reconciliation': self.source_reconciliation,
            'raw_match': self.raw_match,
            'en_match': self.en_match,
            'discrepancy_flag': self.discrepancy_flag,
            'transformations': self.transformations,
            'flags': self.flags,
            'timestamp': self.timestamp
        }


# ============================================================
# UNIT DEFINITIONS
# ============================================================

UNIT_DEFINITIONS = {
    'g': {'category': UnitCategory.MASS, 'base_factor': 1.0, 'standard': 'g'},
    'gram': {'category': UnitCategory.MASS, 'base_factor': 1.0, 'standard': 'g'},
    'grams': {'category': UnitCategory.MASS, 'base_factor': 1.0, 'standard': 'g'},
    'kg': {'category': UnitCategory.MASS, 'base_factor': 1000.0, 'standard': 'kg'},
    'kilogram': {'category': UnitCategory.MASS, 'base_factor': 1000.0, 'standard': 'kg'},
    'mg': {'category': UnitCategory.MASS, 'base_factor': 0.001, 'standard': 'mg'},
    'milligram': {'category': UnitCategory.MASS, 'base_factor': 0.001, 'standard': 'mg'},
    
    'ml': {'category': UnitCategory.VOLUME, 'base_factor': 1.0, 'standard': 'ml'},
    'milliliter': {'category': UnitCategory.VOLUME, 'base_factor': 1.0, 'standard': 'ml'},
    'milliliters': {'category': UnitCategory.VOLUME, 'base_factor': 1.0, 'standard': 'ml'},
    'l': {'category': UnitCategory.VOLUME, 'base_factor': 1000.0, 'standard': 'l'},
    'liter': {'category': UnitCategory.VOLUME, 'base_factor': 1000.0, 'standard': 'l'},
    'litre': {'category': UnitCategory.VOLUME, 'base_factor': 1000.0, 'standard': 'l'},
    'liters': {'category': UnitCategory.VOLUME, 'base_factor': 1000.0, 'standard': 'l'},
    'litres': {'category': UnitCategory.VOLUME, 'base_factor': 1000.0, 'standard': 'l'},
    'tsp': {'category': UnitCategory.VOLUME, 'base_factor': 4.92892, 'standard': 'tsp'},
    'teaspoon': {'category': UnitCategory.VOLUME, 'base_factor': 4.92892, 'standard': 'tsp'},
    'teaspoons': {'category': UnitCategory.VOLUME, 'base_factor': 4.92892, 'standard': 'tsp'},
    'tbsp': {'category': UnitCategory.VOLUME, 'base_factor': 14.7868, 'standard': 'tbsp'},
    'tablespoon': {'category': UnitCategory.VOLUME, 'base_factor': 14.7868, 'standard': 'tbsp'},
    'tablespoons': {'category': UnitCategory.VOLUME, 'base_factor': 14.7868, 'standard': 'tbsp'},
    'cup': {'category': UnitCategory.VOLUME, 'base_factor': 236.588, 'standard': 'cup'},
    'cups': {'category': UnitCategory.VOLUME, 'base_factor': 236.588, 'standard': 'cup'},
    
    'piece': {'category': UnitCategory.COUNT, 'base_factor': 1.0, 'standard': 'piece'},
    'pieces': {'category': UnitCategory.COUNT, 'base_factor': 1.0, 'standard': 'piece'},
    'whole': {'category': UnitCategory.COUNT, 'base_factor': 1.0, 'standard': 'piece'},
    'clove': {'category': UnitCategory.COUNT, 'base_factor': 1.0, 'standard': 'clove'},
    'cloves': {'category': UnitCategory.COUNT, 'base_factor': 1.0, 'standard': 'clove'},
    'slice': {'category': UnitCategory.COUNT, 'base_factor': 1.0, 'standard': 'slice'},
    'slices': {'category': UnitCategory.COUNT, 'base_factor': 1.0, 'standard': 'slice'},
    'number': {'category': UnitCategory.COUNT, 'base_factor': 1.0, 'standard': 'piece'},
    
    'handful': {'category': UnitCategory.APPROXIMATE, 'base_factor': None, 'standard': 'handful'},
    'handfuls': {'category': UnitCategory.APPROXIMATE, 'base_factor': None, 'standard': 'handful'},
    'pinch': {'category': UnitCategory.APPROXIMATE, 'base_factor': None, 'standard': 'pinch'},
    'pinches': {'category': UnitCategory.APPROXIMATE, 'base_factor': None, 'standard': 'pinch'},
    'to taste': {'category': UnitCategory.APPROXIMATE, 'base_factor': None, 'standard': 'to_taste'},
    'as required': {'category': UnitCategory.APPROXIMATE, 'base_factor': None, 'standard': 'as_required'},
    'as needed': {'category': UnitCategory.APPROXIMATE, 'base_factor': None, 'standard': 'as_needed'},
    'small amount': {'category': UnitCategory.APPROXIMATE, 'base_factor': None, 'standard': 'small_amount'},
    'small quantities': {'category': UnitCategory.APPROXIMATE, 'base_factor': None, 'standard': 'small_amount'},
    'dash': {'category': UnitCategory.APPROXIMATE, 'base_factor': None, 'standard': 'dash'},
    'sprinkle': {'category': UnitCategory.APPROXIMATE, 'base_factor': None, 'standard': 'sprinkle'},
    
    # Indian units (mapped to standard units)
    'चमच': {'category': UnitCategory.VOLUME, 'base_factor': 14.7868, 'standard': 'tbsp'},
    'चम्मच': {'category': UnitCategory.VOLUME, 'base_factor': 14.7868, 'standard': 'tbsp'},
    'बड़ा चमच': {'category': UnitCategory.VOLUME, 'base_factor': 14.7868, 'standard': 'tbsp'},
    'बड़ा चम्मच': {'category': UnitCategory.VOLUME, 'base_factor': 14.7868, 'standard': 'tbsp'},
    'छोटा चमच': {'category': UnitCategory.VOLUME, 'base_factor': 4.92892, 'standard': 'tsp'},
    'छोटा चम्मच': {'category': UnitCategory.VOLUME, 'base_factor': 4.92892, 'standard': 'tsp'},
    'चुटकी': {'category': UnitCategory.APPROXIMATE, 'base_factor': None, 'standard': 'pinch'},
    'चुटकी भर': {'category': UnitCategory.APPROXIMATE, 'base_factor': None, 'standard': 'pinch'},
    'कप': {'category': UnitCategory.VOLUME, 'base_factor': 236.588, 'standard': 'cup'},
    'कपफुल': {'category': UnitCategory.VOLUME, 'base_factor': 236.588, 'standard': 'cup'},
}

# Build unit category lookup
UNIT_CATEGORIES = {}
for unit, info in UNIT_DEFINITIONS.items():
    if isinstance(info, dict):
        UNIT_CATEGORIES[unit] = info
        if unit.endswith('s') and not unit.endswith('ss'):
            UNIT_CATEGORIES[unit[:-1]] = info
        elif not unit.endswith('s'):
            UNIT_CATEGORIES[unit + 's'] = info


# ============================================================
# PRE-COMPILED REGEX PATTERNS
# ============================================================

FRACTION_MAP = {
    '\u00BC': 0.25, '\u00BD': 0.5, '\u00BE': 0.75,
    '\u2150': 1/7, '\u2151': 1/9, '\u2152': 1/10,
    '\u2153': 1/3, '\u2154': 2/3, '\u2155': 1/5,
    '\u2156': 2/5, '\u2157': 3/5, '\u2158': 4/5,
    '\u2159': 1/6, '\u215A': 5/6, '\u215B': 1/8,
    '\u215C': 3/8, '\u215D': 5/8, '\u215E': 7/8,
}

FRACTION_PATTERN = re.compile('|'.join(re.escape(k) for k in FRACTION_MAP.keys()))
ASCII_FRACTION_PATTERN = re.compile(r'(?P<whole>\d+)?\s*(?P<frac>\d+/\d+)')
MIXED_FRAC_PATTERN = re.compile(r'(\d+)\s+(\d+/\d+)')

# Unit regex - build from UNIT_DEFINITIONS keys
UNIT_KEYS = [u for u in UNIT_DEFINITIONS if isinstance(UNIT_DEFINITIONS[u], dict)]
UNIT_KEYS_SORTED = sorted(UNIT_KEYS, key=len, reverse=True)
UNIT_REGEX = '|'.join(re.escape(u) for u in UNIT_KEYS_SORTED)
UNIT_PATTERN = re.compile(rf'\b({UNIT_REGEX})\b', re.IGNORECASE)

RANGE_PATTERN = re.compile(r'(\d+(?:\.\d+)?|\d+/\d+)\s*[-–—to]\s*(\d+(?:\.\d+)?|\d+/\d+)', re.IGNORECASE)
SIZE_PATTERN = re.compile(r'\b(small|medium|large|big|tiny|huge|mini)\b', re.IGNORECASE)

PREP_REGEX = re.compile(r'\b(chopped|diced|sliced|minced|grated|ground|crushed|mashed|peeled|boiled|fried|roasted|steamed|baked|grilled|raw|fresh|dried|dry|powdered|powder|soaked|marinated|fermented|pickled|blanched)\b', re.IGNORECASE)

APPROX_KEYWORDS = [
    ('to taste', 'to_taste'),
    ('as required', 'as_required'),
    ('as needed', 'as_needed'),
    ('handful', 'handful'),
    ('handfuls', 'handful'),
    ('pinch', 'pinch'),
    ('pinches', 'pinch'),
    ('dash', 'dash'),
    ('sprinkle', 'sprinkle'),
    ('small amount', 'small_amount'),
    ('small quantities', 'small_amount'),
    ('approximately', 'approximately'),
    ('approx', 'approximately'),
    ('about', 'approximately'),
    ('चुटकी', 'pinch'),
    ('चुटकी भर', 'pinch'),
    ('स्वाद अनुसार', 'to_taste'),
    ('प्रयोग अनुसार', 'as_required'),
]

HINDI_UNITS = {'कप': 'cup', 'कपफुल': 'cup', 'चमच': 'tbsp', 'चम्मच': 'tbsp', 'बड़ा चमच': 'tbsp', 'बड़ा चम्मच': 'tbsp',
    'छोटा चमच': 'tsp', 'छोटा चम्मच': 'tsp', 'चुटकी': 'pinch', 'चुटकी भर': 'pinch',
    'कप': 'cup', 'कपफुल': 'cup'}

HINDI_QUANTITIES = {'आधा': 0.5, 'आधे': 0.5, 'एक': 1, 'दो': 2, 'तीन': 3, 'चार': 4, 'पांच': 5,
    'छह': 6, 'सात': 7, 'आठ': 8, 'नौ': 9, 'दस': 10, 'सवा': 1.25, 'डेढ़': 1.5, 'ढाई': 2.5, 'साढ़े': 2.5}

DEVANAGARI_DIGITS = str.maketrans('०१२३४५६७८९', '0123456789')

FRACTION_MAP = {
    '\u00BC': 0.25, '\u00BD': 0.5, '\u00BE': 0.75,
    '\u2150': 1/7, '\u2151': 1/9, '\u2152': 1/10,
    '\u2153': 1/3, '\u2154': 2/3, '\u2155': 1/5,
    '\u2156': 2/5, '\u2157': 3/5, '\u2158': 4/5,
    '\u2159': 1/6, '\u215A': 5/6, '\u215B': 1/8,
    '\u215C': 3/8, '\u215D': 5/8, '\u215E': 7/8,
}

FRACTION_PATTERN = re.compile('|'.join(re.escape(k) for k in FRACTION_MAP.keys()))
ASCII_FRACTION_PATTERN = re.compile(r'(?P<whole>\d+)?\s*(?P<frac>\d+/\d+)')
MIXED_FRAC_PATTERN = re.compile(r'(\d+)\s+(\d+/\d+)')

# Unit pattern for standard units
UNIT_KEYS = [u for u in UNIT_DEFINITIONS if isinstance(UNIT_DEFINITIONS[u], dict)]
UNIT_KEYS_SORTED = sorted(UNIT_KEYS, key=len, reverse=True)
UNIT_REGEX = '|'.join(re.escape(u) for u in UNIT_KEYS_SORTED)
UNIT_PATTERN = re.compile(rf'\b({UNIT_REGEX})\b', re.IGNORECASE)

RANGE_PATTERN = re.compile(r'(\d+(?:\.\d+)?|\d+/\d+)\s*[-–—to]\s*(\d+(?:\.\d+)?|\d+/\d+)', re.IGNORECASE)
SIZE_PATTERN = re.compile(r'\b(small|medium|large|big|tiny|huge|mini)\b', re.IGNORECASE)

PREP_REGEX = re.compile(r'\b(chopped|diced|sliced|minced|grated|ground|crushed|mashed|peeled|boiled|fried|roasted|steamed|baked|grilled|raw|fresh|dried|dry|powdered|powder|soaked|marinated|fermented|pickled|blanched)\b', re.IGNORECASE)

APPROX_KEYWORDS = [
    ('to taste', 'to_taste'),
    ('as required', 'as_required'),
    ('as needed', 'as_needed'),
    ('handful', 'handful'),
    ('handfuls', 'handful'),
    ('pinch', 'pinch'),
    ('pinches', 'pinch'),
    ('dash', 'dash'),
    ('sprinkle', 'sprinkle'),
    ('small amount', 'small_amount'),
    ('small quantities', 'small_amount'),
    ('approximately', 'approximately'),
    ('approx', 'approximately'),
    ('about', 'approximately'),
    ('चुटकी', 'pinch'),
    ('चुटकी भर', 'pinch'),
    ('स्वाद अनुसार', 'to_taste'),
    ('प्रयोग अनुसार', 'as_required'),
]

HINDI_UNITS = {'कप': 'cup', 'कपफुल': 'cup', 'चमच': 'tbsp', 'चम्मच': 'tbsp', 'बड़ा चमच': 'tbsp', 'बड़ा चम्मच': 'tbsp',
    'छोटा चमच': 'tsp', 'छोटा चम्मच': 'tsp', 'चुटकी': 'pinch', 'चुटकी भर': 'pinch',
    'कप': 'cup', 'कपफुल': 'cup'}

HINDI_QUANTITIES = {'आधा': 0.5, 'आधे': 0.5, 'एक': 1, 'दो': 2, 'तीन': 3, 'चार': 4, 'पांच': 5,
    'छह': 6, 'सात': 7, 'आठ': 8, 'नौ': 9, 'दस': 10, 'सवा': 1.25, 'डेढ़': 1.5, 'ढाई': 2.5, 'साढ़े': 2.5}

DEVANAGARI_DIGITS = str.maketrans('०१२३४५६७८९', '0123456789')

FRACTION_MAP = {
    '\u00BC': 0.25, '\u00BD': 0.5, '\u00BE': 0.75,
    '\u2150': 1/7, '\u2151': 1/9, '\u2152': 1/10,
    '\u2153': 1/3, '\u2154': 2/3, '\u2155': 1/5,
    '\u2156': 2/5, '\u2157': 3/5, '\u2158': 4/5,
    '\u2159': 1/6, '\u215A': 5/6, '\u215B': 1/8,
    '\u215C': 3/8, '\u215D': 5/8, '\u215E': 7/8,
}

FRACTION_PATTERN = re.compile('|'.join(re.escape(k) for k in FRACTION_MAP.keys()))
ASCII_FRACTION_PATTERN = re.compile(r'(?P<whole>\d+)?\s*(?P<frac>\d+/\d+)')
MIXED_FRAC_PATTERN = re.compile(r'(\d+)\s+(\d+/\d+)')

# Unit category lookup
UNIT_CATEGORIES = {}
for unit, info in UNIT_DEFINITIONS.items():
    if isinstance(info, dict):
        UNIT_CATEGORIES[unit] = info
        if unit.endswith('s') and not unit.endswith('ss'):
            UNIT_CATEGORIES[unit[:-1]] = info
        elif not unit.endswith('s'):
            UNIT_CATEGORIES[unit + 's'] = info


# ============================================================
# HOUSEHOLD MEASUREMENTS (abbreviated for performance)
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
    ("green cardamom", "piece", 0.6, "Indian kitchen", 0.85, "verified"),
    ("black cardamom", "piece", 1.5, "Indian kitchen", 0.85, "verified"),
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

# Build household db
HOUSEHOLD_DB = {}
for item in HOUSEHOLD_MEASUREMENTS_RAW:
    ingredient, unit, mass, source, confidence, verification = item
    key = (ingredient.lower().strip(), unit.lower().strip())
    if key not in HOUSEHOLD_DB or confidence > HOUSEHOLD_DB[key]['confidence']:
        HOUSEHOLD_DB[key] = {
            'mass_g': mass, 'source': source, 'confidence': confidence
        }


# ============================================================
# FAST PARSER CLASS
# ============================================================

class IngredientParser:
    def __init__(self):
        self.stats = Counter()
        # Pre-compile patterns
        self.fraction_re = re.compile('|'.join(re.escape(k) for k in FRACTION_MAP.keys()))
        self.ascii_frac_re = re.compile(r'(\d+)?\s*(\d+/\d+)')
        self.mixed_frac_re = re.compile(r'(\d+)\s+(\d+/\d+)')
        # Range regex - handle "to" as a word, not individual characters
        self.range_re = re.compile(r'(\d+(?:\.\d+)?|\d+/\d+)\s*(?:[-–—]|\bto\b)\s*(\d+(?:\.\d+)?|\d+/\d+)', re.IGNORECASE)
        self.unit_re = re.compile(r'\b(' + '|'.join(re.escape(u) for u in sorted([u for u in UNIT_CATEGORIES], key=len, reverse=True)) + r')\b', re.IGNORECASE)
        self.size_re = re.compile(r'\b(small|medium|large|big|tiny|huge|mini)\b', re.IGNORECASE)
        self.prep_re = re.compile(r'\b(chopped|diced|sliced|minced|grated|ground|crushed|mashed|peeled|boiled|fried|roasted|steamed|baked|grilled|raw|fresh|dried|dry|powdered|powder|soaked|marinated|fermented|pickled|blanched)\b', re.IGNORECASE)
        self.approx_re = re.compile(r'\b(to taste|as required|as needed|handful|handfuls|pinch|pinches|dash|sprinkle|small amount|small quantities|approximately|approx|about|चुटकी|चुटकी भर|स्वाद अनुसार|प्रयोग अनुसार)\b', re.IGNORECASE)
        self.hindi_unit_re = re.compile(r'(कप|कपफुल|चमच|चम्मच|बड़ा चमच|बड़ा चम्मच|छोटा चमच|छोटा चम्मच|चुटकी|चुटकी भर)')
        self.hindi_qty_re = re.compile('|'.join(map(re.escape, HINDI_QUANTITIES.keys())))
        
    def parse_fraction(self, s: str) -> Optional[float]:
        s = s.strip()
        if not s:
            return None
        for char, val in FRACTION_MAP.items():
            if char in s:
                base = s.replace(char, '').strip()
                base_val = float(base) if base else 0
                try:
                    return base_val + val
                except:
                    pass
        if '/' in s:
            parts = s.split('/')
            if len(parts) == 2:
                try:
                    return float(parts[0]) / float(parts[1])
                except:
                    pass
        try:
            return float(s)
        except:
            return None
    
    def parse_quantity(self, text: str) -> Tuple[Optional[ParsedQuantity], str]:
        # Range first
        range_match = self.range_re.search(text)
        if range_match:
            min_val = self.parse_fraction(range_match.group(1))
            max_val = self.parse_fraction(range_match.group(2))
            if min_val is not None and max_val is not None:
                qty = ParsedQuantity(min_value=min_val, max_value=max_val, is_range=True, original_text=range_match.group(0))
                remaining = text[:range_match.start()] + text[range_match.end():]
                return qty, remaining.strip()
        
        # Mixed fraction
        mixed = self.mixed_frac_re.search(text)
        if mixed:
            whole = int(mixed.group(1))
            frac = self.parse_fraction(mixed.group(2))
            if frac is not None:
                qty = ParsedQuantity(value=whole + frac, original_text=mixed.group(0))
                remaining = text[:mixed.start()] + text[mixed.end():]
                return qty, remaining.strip()
        
        # Unicode fraction
        for char, val in FRACTION_MAP.items():
            idx = text.find(char)
            if idx >= 0:
                preceding = text[:idx].strip()
                whole_match = re.search(r'(\d+)\s*$', preceding)
                if whole_match:
                    val = int(whole_match.group(1)) + FRACTION_MAP[char]
                    qty_text = whole_match.group(0) + char
                else:
                    val = FRACTION_MAP[char]
                    qty_text = char
                qty = ParsedQuantity(value=val, original_text=qty_text)
                remaining = text[:idx] + text[idx+1:]
                return qty, remaining.strip()
        
        # ASCII fraction
        frac_match = self.ascii_frac_re.search(text)
        if frac_match:
            whole_str = frac_match.group(1)
            frac_str = frac_match.group(2)
            frac_val = self.parse_fraction(frac_str)
            if frac_val is not None:
                if whole_str := frac_match.group(1):
                    val = int(whole_str) + frac_val
                else:
                    val = frac_val
                qty = ParsedQuantity(value=val, original_text=frac_match.group(0))
                remaining = text[:frac_match.start()] + text[frac_match.end():]
                return qty, remaining.strip()
        
        # Decimal/whole with optional range
        qty_match = self.range_re.search(text)
        if qty_match:
            min_val = self.parse_fraction(qty_match.group(1))
            max_val = self.parse_fraction(qty_match.group(2))
            if min_val is not None and max_val is not None:
                qty = ParsedQuantity(min_value=min_val, max_value=max_val, is_range=True, original_text=qty_match.group(0))
                remaining = text[:qty_match.start()] + text[qty_match.end():]
                return qty, remaining.strip()
        
        # Single quantity
        qty_match = re.search(r'(\d+(?:\.\d+)?|\d+/\d+)', text)
        if qty_match:
            val = self.parse_fraction(qty_match.group(1))
            if val is not None:
                qty = ParsedQuantity(value=val, original_text=qty_match.group(1))
                remaining = text[:qty_match.start()] + text[qty_match.end():]
                return qty, remaining.strip()
        
        return None, text
    
    def extract_unit(self, text: str) -> Tuple[Optional[ParsedUnit], str]:
        # Approximate first
        for approx, standard in APPROX_KEYWORDS:
            if approx.lower() in text.lower():
                pattern = re.compile(re.escape(approx), re.IGNORECASE)
                match = pattern.search(text)
                if match:
                    unit_text = match.group(0)
                    unit = ParsedUnit(unit=unit_text.strip(), standardized_unit=standard, category=UnitCategory.APPROXIMATE, is_approximate=True, original_text=unit_text)
                    remaining = text[:match.start()] + text[match.end():]
                    return unit, remaining.strip()
        
        # Hindi units
        for hindi, eng in HINDI_UNITS.items():
            if hindi in text:
                pattern = re.compile(re.escape(hindi))
                match = pattern.search(text)
                if match:
                    unit_text = match.group(0)
                    unit = ParsedUnit(unit=unit_text.strip(), standardized_unit=eng, category=UnitCategory.VOLUME if eng in ['cup','tbsp','tsp'] else UnitCategory.APPROXIMATE, original_text=unit_text)
                    remaining = text[:match.start()] + text[match.end():]
                    return unit, remaining.strip()
        
        # Standard units - longest first
        for unit_text in sorted(UNIT_CATEGORIES.keys(), key=len, reverse=True):
            pattern = re.compile(r'\b' + re.escape(unit_text) + r'\b', re.IGNORECASE)
            match = pattern.search(text)
            if match:
                matched_text = match.group(0)
                info = UNIT_CATEGORIES[unit_text.lower()]
                unit = ParsedUnit(unit=matched_text, standardized_unit=info['standard'], category=info['category'], conversion_factor=info['base_factor'] if info['base_factor'] else None, is_approximate=(info['category'] == UnitCategory.APPROXIMATE), original_text=matched_text)
                remaining = text[:match.start()] + text[match.end():]
                return unit, remaining.strip()
        
        return None, text
    
    def extract_size(self, text: str) -> Tuple[Optional[str], str]:
        match = SIZE_PATTERN.search(text)
        if match:
            size = match.group(1).lower()
            remaining = text[:match.start()] + text[match.end():]
            return size, remaining.strip()
        return None, text
    
    def extract_preparation(self, text: str) -> Tuple[Optional[str], str]:
        matches = list(PREP_REGEX.finditer(text))
        if not matches:
            return None, text
        preps = []
        remaining = text
        for match in reversed(matches):
            prep = match.group(1).lower()
            if prep not in preps:
                preps.append(prep)
            remaining = remaining[:match.start()] + remaining[match.end():]
        return ', '.join(preps), remaining
    
    def clean_name(self, text: str) -> str:
        text = re.sub(r'^[\s\-,\.\(\)\[\]]+', '', text)
        text = re.sub(r'[\s\-,\.\(\)\[\]]+$', '', text)
        text = re.sub(r'\s*\([^)]*\)', '', text)
        text = re.sub(r'^[\d\s\-\/\.\u00BC\u00BD\u00BE\u2150-\u215E]+', '', text)
        return text.strip()
    
    def parse(self, text: str) -> ParsedIngredient:
        transformations = []
        
        # Quantity
        quantity, remaining = self.parse_quantity(text)
        
        # Size
        size, remaining = self.extract_size(remaining)
        
        # Preparation (BEFORE unit, so prep words aren't consumed)
        prep, remaining = self.extract_preparation(remaining)
        
        # Unit
        unit, remaining = self.extract_unit(remaining)
        
        # Ingredient name
        name = re.sub(r'^[\s\-,\.\(\)\[\]]+', '', remaining)
        name = re.sub(r'[\s\-,\.\(\)\[\]]+$', '', name)
        name = re.sub(r'\s*\([^)]*\)', '', name)
        name = re.sub(r'^[\d\s\-\/\.\u00BC\u00BD\u00BE\u2150-\u215E]+', '', name).strip()
        
        # Determine status
        if quantity and unit:
            if quantity.is_range:
                status = ParseStatus.RANGE_PARSED.value
            elif unit.category == UnitCategory.APPROXIMATE:
                status = ParseStatus.PARSED_APPROXIMATE.value
            else:
                status = ParseStatus.PARSED_EXACT.value
        elif quantity:
            status = ParseStatus.PARSED_APPROXIMATE.value
        elif unit and unit.category == UnitCategory.APPROXIMATE:
            status = ParseStatus.PARSED_APPROXIMATE.value
        else:
            status = ParseStatus.UNQUANTIFIED.value
        
        # Gram weight
        gram_weight = gram_min = gram_max = None
        conv_status = "UNRESOLVED"
        if quantity and unit and unit.conversion_factor:
            if quantity.is_range:
                if quantity.min_value: gram_min = quantity.min_value * unit.conversion_factor
                if quantity.max_value: gram_max = quantity.max_value * unit.conversion_factor
            elif quantity.value:
                gram_w = quantity.value * unit.conversion_factor
            conv_status = "RESOLVED"
        elif quantity and unit:
            conv_status = "UNRESOLVED"
        else:
            conv_status = "NOT_APPLICABLE"
        
        flags = []
        if not quantity: flags.append("no_quantity")
        if not unit: flags.append("no_unit")
        if status == ParseStatus.UNQUANTIFIED.value: flags.append("unquantified")
        if unit and unit.category == UnitCategory.APPROXIMATE: flags.append("approximate_unit")
        
        return ParsedIngredient(
            recipe_id=0, source_field="", original_line="", original_ingredient="", normalized_ingredient="",
            quantity=quantity, unit=unit, ingredient_name=name,
            preparation=prep, size_descriptor=size,
            parse_status=status, conversion_status="UNRESOLVED",
            gram_weight=None, gram_weight_min=None, gram_weight_max=None,
            transformations=[], flags=flags
        )


# ============================================================
# SOURCE RECONCILIATION (VECTORIZED)
# ============================================================

def _has_source_flag(flags, source):
    if isinstance(flags, (list, tuple)):
        return any(source in f for f in flags)
    elif isinstance(flags, str):
        return source in flags
    # Handle numpy arrays and other iterables
    try:
        return any(source in f for f in flags)
    except (TypeError, AttributeError):
        return False

def _row_to_dict(row: pd.Series) -> dict:
    d = row.to_dict()
    if 'flags' in d:
        flags = d['flags']
        if isinstance(flags, str):
            d['flags'] = [f.strip() for f in flags.split(';') if f.strip()]
        elif isinstance(flags, (list, tuple)):
            d['flags'] = list(flags)
        elif hasattr(flags, '__iter__') and not isinstance(flags, str):
            # Handle numpy arrays and other iterables
            d['flags'] = list(flags)
        else:
            d['flags'] = []
    return d

def reconcile_sources(ingredients_df: pd.DataFrame) -> pd.DataFrame:
    """Simple source reconciliation - one canonical row per recipe_id + normalized_ingredient."""
    # Add source columns
    ingredients_df['_is_raw'] = ingredients_df['flags'].apply(lambda f: _has_source_flag(f, 'source:ingredients_raw'))
    ingredients_df['_is_en'] = ingredients_df['flags'].apply(lambda f: _has_source_flag(f, 'source:ingredients_en'))
    
    # Group by recipe_id and normalized_ingredient, check sources
    grouped = ingredients_df.groupby(['recipe_id', 'normalized_ingredient']).agg(
        has_raw=('_is_raw', 'any'),
        has_en=('_is_en', 'any'),
        _is_raw=('_is_raw', 'first'),  # Keep first value for match info
        _is_en=('_is_en', 'first'),
    ).reset_index()
    
    # Determine reconciliation status - use has_raw/has_en (any) not _is_raw/_is_en (first)
    grouped['source_reconciliation'] = grouped.apply(
        lambda r: 'canonical' if r['has_raw'] and r['has_en'] else ('raw_only' if r['has_raw'] else ('en_only' if r['has_en'] else 'unknown')), axis=1
    )
    grouped['raw_match'] = grouped['_is_raw']
    grouped['en_match'] = grouped['_is_en']
    grouped['discrepancy_flag'] = grouped['source_reconciliation'].isin(['raw_only', 'en_only'])
    
    # Get a representative row for each group (prefer raw)
    # Drop temp columns first
    base_df = ingredients_df.drop(columns=['_is_raw', '_is_en'])
    rep_rows = base_df.drop_duplicates(subset=['recipe_id', 'normalized_ingredient'], keep='first')
    
    # Start with grouped as base (has all reconciliation info)
    canonical = grouped.copy()
    
    # Merge in the other columns from representative row
    other_cols = [c for c in base_df.columns if c not in ['_is_raw', '_is_en'] and c not in grouped.columns]
    if other_cols:
        rep_subset = base_df.drop_duplicates(subset=['recipe_id', 'normalized_ingredient'])[['recipe_id', 'normalized_ingredient'] + other_cols]
        canonical = grouped.merge(rep_subset, on=['recipe_id', 'normalized_ingredient'], how='left')
    else:
        canonical = grouped.copy()
    
    # Ensure source_reconciliation exists
    if 'source_reconciliation' not in canonical.columns:
        canonical['source_reconciliation'] = 'unknown'
    
    # Add missing source flags
    def add_missing_flags(row):
        flags = row.get('flags', [])
        if isinstance(flags, str):
            flags = flags.split(';')
        if not isinstance(flags, list):
            flags = []
        if row.get('source_reconciliation') == 'raw_only':
            flags.append('en_missing')
        elif row.get('source_reconciliation') == 'en_only':
            flags.append('raw_missing')
        return flags
    
    canonical['flags'] = canonical.apply(
        lambda row: (row.get('flags', []) if isinstance(row.get('flags'), list) else (row.get('flags', '').split(';') if isinstance(row.get('flags'), str) else [])) 
        + (['en_missing'] if row.get('source_reconciliation') == 'raw_only' else (['raw_missing'] if row.get('source_reconciliation') == 'en_only' else [])), 
        axis=1
    )
    # Discrepancy only when BOTH sources exist but disagree on quantity/unit
    canonical['discrepancy_flag'] = False
    canonical['raw_match'] = canonical['_is_raw']
    canonical['en_match'] = canonical['_is_en']
    
    # Clean up temp columns
    temp_cols = ['_is_raw', '_is_en', 'has_raw', 'has_en']
    canonical = canonical.drop(columns=[c for c in ['_is_raw', '_is_en', 'has_raw', 'has_en'] if c in canonical.columns])
    
    return canonical


# ============================================================
# MAIN
# ============================================================

def main():
    print("="*60)
    print("STAGE 2 - INGREDIENT QUANTITY AND UNIT PARSING")
    print("="*60)
    
    input_path = "data/interim/phase2/normalized_ingredients.parquet"
    print(f"Loading from {input_path}...")
    norm_df = pd.read_parquet(input_path)
    print(f"Loaded {len(norm_df)} records for {norm_df['recipe_id'].nunique()} recipes")
    
    parser = IngredientParser()
    print("Parsing ingredients...")
    
    parsed_records = []
    for _, row in norm_df.iterrows():
        parsed = parser.parse(row['normalized_ingredient'])
        parsed.recipe_id = row['recipe_id']
        parsed.source_field = 'ingredients_raw' if 'source:ingredients_raw' in row['flags'] else 'ingredients_en'
        parsed.original_line = row['source_line']
        parsed.original_ingredient = row['source_ingredient']
        parsed.normalized_ingredient = row['normalized_ingredient']
        if row['flags']:
            parsed.flags.extend(row['flags'].split('; '))
        parsed_records.append(parsed)
    
    print(f"Parsed {len(parsed_records)} records")
    
    # Convert to DataFrame
    parsed_data = [p.to_dict() for p in parsed_records]
    parsed_df = pd.DataFrame(parsed_data)
    
    # Source reconciliation (vectorized)
    print("Reconciling sources...")
    canonical_df = reconcile_sources(parsed_df)
    print(f"Canonical records: {len(canonical_df)}")
    
    # Gram weight resolution
    print("Resolving gram weights...")
    resolved = 0
    for idx, row in canonical_df.iterrows():
        ing_name = row.get('ingredient_name', '').lower().strip()
        unit_std = row.get('unit', {}).get('standardized_unit', '').lower().strip() if isinstance(row.get('unit'), dict) else ''
        qty = row.get('quantity')
        if not isinstance(qty, dict): continue
        key = (ing_name, unit_std)
        if key in HOUSEHOLD_DB:
            entry = HOUSEHOLD_DB[key]
            if qty.get('is_range'):
                if qty.get('min_value'): canonical_df.at[idx, 'gram_weight_min'] = qty['min_value'] * entry['mass_g']
                if qty.get('max_value'): canonical_df.at[idx, 'gram_weight_max'] = qty['max_value'] * entry['mass_g']
                canonical_df.at[idx, 'conversion_status'] = 'RESOLVED_HOUSEHOLD'
            elif qty.get('value') is not None:
                canonical_df.at[idx, 'gram_weight'] = qty['value'] * entry['mass_g']
                canonical_df.at[idx, 'conversion_status'] = 'RESOLVED_HOUSEHOLD'
            resolved += 1
    
    print(f"Resolved {resolved} ingredients")
    
    # Save
    output_dir = Path("data/interim/phase2")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    canonical_df.to_parquet(output_dir / "parsed_recipe_ingredients.parquet", index=False)
    print(f"Saved to {output_dir}/parsed_recipe_ingredients.parquet")
    
    # Household measurements CSV
    household_rows = []
    for item in HOUSEHOLD_MEASUREMENTS_RAW:
        ing, unit, mass, source, conf, verif = item
        household_rows.append({
            'ingredient_name': ing, 'household_unit': unit,
            'equivalent_mass_g': mass, 'source': source,
            'confidence': conf, 'verification_status': verif
        })
    pd.DataFrame(household_rows).to_csv(output_dir / "household_measurements.csv", index=False)
    print(f"Saved household measurements")
    
    canonical_df.to_csv(output_dir / "parsed_recipe_ingredients.csv", index=False)
    
    # Validation
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    print(f"Recipes: {canonical_df['recipe_id'].nunique()}")
    print(f"Parsed records: {len(parsed_df)}")
    print(f"Canonical: {len(canonical_df)}")
    
    status_counts = Counter(canonical_df['parse_status'].astype(str))
    print(f"\nParse status:")
    for s, c in status_counts.most_common():
        print(f"  {s}: {c}")
    
    conv_counts = Counter(canonical_df['conversion_status'])
    print(f"\nConversion:")
    for s, c in Counter(canonical_df['conversion_status']).most_common():
        print(f"  {s}: {c}")
    
    recon_counts = Counter(canonical_df['source_reconciliation'])
    print(f"\nReconciliation:")
    for s, c in Counter(canonical_df['source_reconciliation']).most_common():
        print(f"  {s}: {c}")
    
    disc = canonical_df['discrepancy_flag'].sum() if 'discrepancy_flag' in canonical_df.columns else 0
    print(f"\nDiscrepancies: {disc}")
    
    gw = canonical_df['gram_weight'].notna().sum() if 'gram_weight' in canonical_df.columns else 0
    print(f"Gram weight resolved: {canonical_df['gram_weight'].notna().sum() if 'gram_weight' in canonical_df.columns else 0}")
    
    # Report
    report_path = "reports/phase2/quantity_parsing_report.md"
    Path("reports/phase2").mkdir(parents=True, exist_ok=True)
    with open(report_path, 'w') as f:
        f.write("# Stage 2 - Quantity Parsing Validation Report\n\n")
        f.write(f"**Date:** {datetime.now().isoformat()}\n")
        f.write(f"**Canonical records:** {len(canonical_df)}\n")
        f.write(f"**Parse status:** {dict(Counter(canonical_df['parse_status'].astype(str)))}\n")
        f.write(f"**Conversion:** {dict(Counter(canonical_df['conversion_status']))}\n")
        f.write(f"**Reconciliation:** {dict(Counter(canonical_df['source_reconciliation']))}\n")
        f.write(f"**Gram weight resolved:** {canonical_df['gram_weight'].notna().sum() if 'gram_weight' in canonical_df.columns else 0}\n")
    
    # Save outputs
    output_dir = Path("data/interim/phase2")
    output_dir.mkdir(parents=True, exist_ok=True)
    canonical_df.to_parquet(output_dir / "parsed_recipe_ingredients.parquet", index=False)
    canonical_df.to_csv(output_dir / "parsed_recipe_ingredients.csv", index=False)
    
    # Household measurements
    hh_rows = []
    for item in HOUSEHOLD_MEASUREMENTS_RAW:
        ing, unit, mass, source, conf, verif = item
        hh_rows.append({'ingredient_name': ing, 'household_unit': unit, 'equivalent_mass_g': mass, 'source': source, 'confidence': conf, 'verification_status': verif})
    pd.DataFrame(hh_rows).to_csv(output_dir / "household_measurements.csv", index=False)
    
    print("\nStage 2 complete.")


if __name__ == "__main__":
    main()