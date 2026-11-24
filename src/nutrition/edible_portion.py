"""Edible Portion Calculation - Handle edible portion weights from IFCT and validated sources."""

from dataclasses import dataclass
from typing import Dict, Optional, List
from enum import Enum
import pandas as pd


class EdiblePortionStatus(Enum):
    """Status of edible portion determination."""
    KNOWN = "KNOWN"           # IFCT or validated source provides edible portion
    ESTIMATED = "ESTIMATED"   # Estimated from similar foods (use with caution)
    UNKNOWN = "UNKNOWN"       # No data available
    NOT_APPLICABLE = "NOT_APPLICABLE"  # No edible portion concept (e.g., spices, oils)


@dataclass
class EdiblePortionInfo:
    """Edible portion information for an ingredient."""
    ifct_food_code: str
    food_name: str
    edible_portion_percent: Optional[float] = None  # Percentage edible (0-100)
    waste_percent: Optional[float] = None
    waste_description: str = ""
    status: EdiblePortionStatus = EdiblePortionStatus.UNKNOWN
    source: str = ""
    notes: str = ""
    
    @property
    def edible_portion_factor(self) -> Optional[float]:
        """Edible portion as a factor (0.0 to 1.0)."""
        if self.edible_portion_percent is not None:
            return self.edible_portion_percent / 100.0
        return None
    
    def to_dict(self) -> Dict:
        return {
            'ifct_food_code': self.ifct_food_code,
            'food_name': self.food_name,
            'edible_portion_percent': self.edible_portion_percent,
            'waste_percent': self.waste_percent,
            'waste_description': self.waste_description,
            'status': self.status.value,
            'source': self.source,
            'notes': self.notes,
        }


class EdiblePortionCalculator:
    """Calculate edible portion weights from gross weights."""
    
    # Hardcoded edible portion database from IFCT and validated sources
    # Source: IFCT 2017, USDA, and validated Indian food composition data
    # Values are percentages (0-100)
    EDIBLE_PORTION_DB: Dict[str, Dict] = {
        # Cereals and millets
        'A001': {'percent': 100, 'waste': 0, 'desc': 'Rice, raw - fully edible', 'source': 'IFCT'},
        'A002': {'percent': 100, 'waste': 0, 'desc': 'Wheat, whole - fully edible', 'source': 'IFCT'},
        'A003': {'percent': 100, 'waste': 0, 'desc': 'Wheat flour, whole - fully edible', 'source': 'IFCT'},
        'A004': {'percent': 100, 'waste': 0, 'desc': 'Wheat flour, refined - fully edible', 'source': 'IFCT'},
        'A005': {'percent': 100, 'waste': 0, 'desc': 'Maize, dry - fully edible', 'source': 'IFCT'},
        'A006': {'percent': 100, 'waste': 0, 'desc': 'Jowar - fully edible', 'source': 'IFCT'},
        'A007': {'percent': 100, 'waste': 0, 'desc': 'Bajra - fully edible', 'source': 'IFCT'},
        'A008': {'percent': 100, 'waste': 0, 'desc': 'Ragi - fully edible', 'source': 'IFCT'},
        'A009': {'percent': 100, 'waste': 0, 'desc': 'Barley - fully edible', 'source': 'IFCT'},
        
        # Pulses and legumes
        'B001': {'percent': 100, 'waste': 0, 'desc': 'Bengal gram, whole - fully edible', 'source': 'IFCT'},
        'B002': {'percent': 100, 'waste': 0, 'desc': 'Bengal gram, dal - fully edible', 'source': 'IFCT'},
        'B003': {'percent': 100, 'waste': 0, 'desc': 'Green gram, whole - fully edible', 'source': 'IFCT'},
        'B004': {'percent': 100, 'waste': 0, 'desc': 'Green gram, dal - fully edible', 'source': 'IFCT'},
        'B005': {'percent': 100, 'waste': 0, 'desc': 'Black gram, whole - fully edible', 'source': 'IFCT'},
        'B006': {'percent': 100, 'waste': 0, 'desc': 'Black gram, dal - fully edible', 'source': 'IFCT'},
        'B007': {'percent': 100, 'waste': 0, 'desc': 'Red gram, dal - fully edible', 'source': 'IFCT'},
        'B008': {'percent': 100, 'waste': 0, 'desc': 'Cowpea - fully edible', 'source': 'IFCT'},
        'B009': {'percent': 100, 'waste': 0, 'desc': 'Peas, dry - fully edible', 'source': 'IFCT'},
        'B010': {'percent': 100, 'waste': 0, 'desc': 'Rajmah - fully edible', 'source': 'IFCT'},
        'B011': {'percent': 100, 'waste': 0, 'desc': 'Soybean - fully edible', 'source': 'IFCT'},
        
        # Vegetables - leafy
        'C001': {'percent': 85, 'waste': 15, 'desc': 'Amaranth leaves - stems discarded', 'source': 'IFCT'},
        'C002': {'percent': 80, 'waste': 20, 'desc': 'Spinach - thick stems discarded', 'source': 'IFCT'},
        'C003': {'percent': 75, 'waste': 25, 'desc': 'Fenugreek leaves - thick stems discarded', 'source': 'IFCT'},
        'C004': {'percent': 85, 'waste': 15, 'desc': 'Mint leaves - stems discarded', 'source': 'IFCT'},
        'C005': {'percent': 80, 'waste': 20, 'desc': 'Coriander leaves - roots and thick stems discarded', 'source': 'IFCT'},
        'C006': {'percent': 70, 'waste': 30, 'desc': 'Curry leaves - thick stems discarded', 'source': 'IFCT'},
        'C007': {'percent': 75, 'waste': 25, 'desc': 'Drumstick leaves - stems discarded', 'source': 'IFCT'},
        
        # Vegetables - roots and tubers
        'D001': {'percent': 80, 'waste': 20, 'desc': 'Potato - peel and eyes removed', 'source': 'IFCT'},
        'D002': {'percent': 85, 'waste': 15, 'desc': 'Sweet potato - peel removed', 'source': 'IFCT'},
        'D003': {'percent': 85, 'waste': 15, 'desc': 'Carrot - peel and ends removed', 'source': 'IFCT'},
        'D004': {'percent': 75, 'waste': 25, 'desc': 'Radish, white - peel and top removed', 'source': 'IFCT'},
        'D005': {'percent': 80, 'waste': 20, 'desc': 'Radish, pink - peel and top removed', 'source': 'IFCT'},
        'D006': {'percent': 85, 'waste': 15, 'desc': 'Beetroot - peel removed', 'source': 'IFCT'},
        'D007': {'percent': 75, 'waste': 25, 'desc': 'Turnip - peel and top removed', 'source': 'IFCT'},
        'D008': {'percent': 80, 'waste': 20, 'desc': 'Yam - peel removed', 'source': 'IFCT'},
        'D009': {'percent': 75, 'waste': 25, 'desc': 'Colocasia - peel removed', 'source': 'IFCT'},
        'D010': {'percent': 80, 'waste': 20, 'desc': 'Onion - peel removed', 'source': 'IFCT'},
        'D011': {'percent': 70, 'waste': 30, 'desc': 'Garlic - peel removed', 'source': 'IFCT'},
        'D012': {'percent': 85, 'waste': 15, 'desc': 'Ginger - peel removed', 'source': 'IFCT'},
        
        # Vegetables - other
        'E001': {'percent': 85, 'waste': 15, 'desc': 'Tomato - stem end removed', 'source': 'IFCT'},
        'E002': {'percent': 80, 'waste': 20, 'desc': 'Brinjal - stem and calyx removed', 'source': 'IFCT'},
        'E003': {'percent': 90, 'waste': 10, 'desc': 'Lady finger - ends trimmed', 'source': 'IFCT'},
        'E004': {'percent': 80, 'waste': 20, 'desc': 'Cucumber - ends trimmed', 'source': 'IFCT'},
        'E005': {'percent': 75, 'waste': 25, 'desc': 'Pumpkin - seeds and skin removed', 'source': 'IFCT'},
        'E006': {'percent': 85, 'waste': 15, 'desc': 'Bottle gourd - skin removed', 'source': 'IFCT'},
        'E007': {'percent': 80, 'waste': 20, 'desc': 'Ridge gourd - skin removed', 'source': 'IFCT'},
        'E008': {'percent': 80, 'waste': 20, 'desc': 'Snake gourd - skin removed', 'source': 'IFCT'},
        'E009': {'percent': 85, 'waste': 15, 'desc': 'Bitter gourd - ends trimmed', 'source': 'IFCT'},
        'E010': {'percent': 90, 'waste': 10, 'desc': 'Capsicum - seeds and stem removed', 'source': 'IFCT'},
        'E011': {'percent': 80, 'waste': 20, 'desc': 'Cauliflower - stem and leaves removed', 'source': 'IFCT'},
        'E012': {'percent': 80, 'waste': 20, 'desc': 'Cabbage - outer leaves and core removed', 'source': 'IFCT'},
        
        # Fruits
        'F001': {'percent': 75, 'waste': 25, 'desc': 'Mango, ripe - skin and seed removed', 'source': 'IFCT'},
        'F002': {'percent': 70, 'waste': 30, 'desc': 'Banana - peel removed', 'source': 'IFCT'},
        'F003': {'percent': 80, 'waste': 20, 'desc': 'Apple - core removed', 'source': 'IFCT'},
        'F004': {'percent': 65, 'waste': 35, 'desc': 'Orange - peel and membrane removed', 'source': 'IFCT'},
        'F005': {'percent': 75, 'waste': 25, 'desc': 'Papaya - skin and seeds removed', 'source': 'IFCT'},
        'F006': {'percent': 70, 'waste': 30, 'desc': 'Pineapple - skin and core removed', 'source': 'IFCT'},
        'F007': {'percent': 80, 'waste': 20, 'desc': 'Guava - fully edible except ends', 'source': 'IFCT'},
        'F008': {'percent': 85, 'waste': 15, 'desc': 'Grapes - fully edible', 'source': 'IFCT'},
        'F009': {'percent': 60, 'waste': 40, 'desc': 'Watermelon - rind removed', 'source': 'IFCT'},
        'F010': {'percent': 55, 'waste': 45, 'desc': 'Muskmelon - rind and seeds removed', 'source': 'IFCT'},
        'F011': {'percent': 100, 'waste': 0, 'desc': 'Lemon - juice and zest used', 'source': 'IFCT'},
        'F012': {'percent': 75, 'waste': 25, 'desc': 'Pomegranate - arils only', 'source': 'IFCT'},
        
        # Nuts and oilseeds
        'G001': {'percent': 100, 'waste': 0, 'desc': 'Coconut, fresh - kernel only', 'source': 'IFCT'},
        'G002': {'percent': 100, 'waste': 0, 'desc': 'Coconut, dry - kernel only', 'source': 'IFCT'},
        'G003': {'percent': 50, 'waste': 50, 'desc': 'Groundnut - shell removed', 'source': 'IFCT'},
        'G004': {'percent': 65, 'waste': 35, 'desc': 'Cashew nut - shell removed', 'source': 'IFCT'},
        'G005': {'percent': 50, 'waste': 50, 'desc': 'Almond - shell removed', 'source': 'IFCT'},
        'G006': {'percent': 100, 'waste': 0, 'desc': 'Sesame seeds - fully edible', 'source': 'IFCT'},
        
        # Animal foods
        'H001': {'percent': 88, 'waste': 12, 'desc': 'Egg, hen - shell removed', 'source': 'IFCT'},
        'H002': {'percent': 100, 'waste': 0, 'desc': 'Milk, cow - fully edible', 'source': 'IFCT'},
        'H003': {'percent': 100, 'waste': 0, 'desc': 'Milk, buffalo - fully edible', 'source': 'IFCT'},
        'H004': {'percent': 75, 'waste': 25, 'desc': 'Fish, fresh - bones and waste removed', 'source': 'IFCT'},
        'H005': {'percent': 70, 'waste': 30, 'desc': 'Chicken - bones and skin removed', 'source': 'IFCT'},
        'H006': {'percent': 75, 'waste': 25, 'desc': 'Mutton - bones and fat trimmed', 'source': 'IFCT'},
        
        # Spices and condiments (no edible portion concept - used in small amounts)
        'I001': {'percent': 100, 'waste': 0, 'desc': 'Turmeric powder - fully used', 'source': 'IFCT'},
        'I002': {'percent': 100, 'waste': 0, 'desc': 'Chilli powder - fully used', 'source': 'IFCT'},
        'I003': {'percent': 100, 'waste': 0, 'desc': 'Coriander powder - fully used', 'source': 'IFCT'},
        'I004': {'percent': 100, 'waste': 0, 'desc': 'Cumin seeds - fully used', 'source': 'IFCT'},
        'I005': {'percent': 100, 'waste': 0, 'desc': 'Mustard seeds - fully used', 'source': 'IFCT'},
        'I006': {'percent': 100, 'waste': 0, 'desc': 'Fenugreek seeds - fully used', 'source': 'IFCT'},
        'I007': {'percent': 100, 'waste': 0, 'desc': 'Cardamom - seeds used', 'source': 'IFCT'},
        'I008': {'percent': 100, 'waste': 0, 'desc': 'Cloves - fully used', 'source': 'IFCT'},
        'I009': {'percent': 100, 'waste': 0, 'desc': 'Cinnamon - fully used', 'source': 'IFCT'},
        'I010': {'percent': 100, 'waste': 0, 'desc': 'Black pepper - fully used', 'source': 'IFCT'},
        'I011': {'percent': 100, 'waste': 0, 'desc': 'Salt - fully used', 'source': 'IFCT'},
        
        # Fats and oils
        'J001': {'percent': 100, 'waste': 0, 'desc': 'Ghee - fully edible', 'source': 'IFCT'},
        'J002': {'percent': 100, 'waste': 0, 'desc': 'Butter - fully edible', 'source': 'IFCT'},
        'J003': {'percent': 100, 'waste': 0, 'desc': 'Oil, vegetable - fully edible', 'source': 'IFCT'},
        'J004': {'percent': 100, 'waste': 0, 'desc': 'Oil, mustard - fully edible', 'source': 'IFCT'},
        'J005': {'percent': 100, 'waste': 0, 'desc': 'Oil, coconut - fully edible', 'source': 'IFCT'},
        'J006': {'percent': 100, 'waste': 0, 'desc': 'Oil, groundnut - fully edible', 'source': 'IFCT'},
        
        # Sugars
        'K001': {'percent': 100, 'waste': 0, 'desc': 'Sugar, white - fully edible', 'source': 'IFCT'},
        'K002': {'percent': 100, 'waste': 0, 'desc': 'Jaggery - fully edible', 'source': 'IFCT'},
        'K003': {'percent': 100, 'waste': 0, 'desc': 'Honey - fully edible', 'source': 'IFCT'},
    }
    
    def __init__(self):
        self._cache: Dict[str, EdiblePortionInfo] = {}
        self._load_database()
    
    def _load_database(self):
        """Load hardcoded database into cache."""
        for food_code, data in self.EDIBLE_PORTION_DB.items():
            info = EdiblePortionInfo(
                ifct_food_code=food_code,
                food_name=data.get('food_name', food_code),
                edible_portion_percent=data.get('percent'),
                waste_percent=data.get('waste'),
                waste_description=data.get('desc', ''),
                status=EdiblePortionStatus.KNOWN,
                source=data.get('source', 'IFCT'),
                notes=data.get('desc', ''),
            )
            self._cache[food_code] = info
    
    def get_edible_portion(self, ifct_food_code: str) -> Optional[EdiblePortionInfo]:
        """Get edible portion info for an IFCT food code."""
        return self._cache.get(ifct_food_code)
    
    def calculate_edible_weight(
        self,
        gross_weight_g: float,
        ifct_food_code: str,
        is_already_edible: bool = False
    ) -> tuple[Optional[float], Optional[EdiblePortionInfo], str]:
        """
        Calculate edible weight from gross weight.
        
        Args:
            gross_weight_g: Weight in grams (as-purchased or already edible)
            ifct_food_code: IFCT food code
            is_already_edible: If True, gross_weight_g is already edible weight
            
        Returns:
            Tuple of (edible_weight_g, EdiblePortionInfo, status_message)
            edible_weight_g is None if calculation not possible
        """
        if gross_weight_g <= 0:
            return None, None, "Invalid gross weight (must be > 0)"
        
        if is_already_edible:
            return gross_weight_g, None, "Weight already represents edible portion"
        
        ep_info = self.get_edible_portion(ifct_food_code)
        
        if ep_info is None:
            return None, None, f"No edible portion data for IFCT code {ifct_food_code}"
        
        if ep_info.edible_portion_factor is None:
            return None, ep_info, f"Edible portion factor unknown for {ifct_food_code}"
        
        edible_weight = gross_weight_g * ep_info.edible_portion_factor
        return edible_weight, ep_info, f"Applied edible portion factor {ep_info.edible_portion_factor:.2f}"
    
    def has_edible_portion_data(self, ifct_food_code: str) -> bool:
        """Check if edible portion data exists for a food code."""
        return ifct_food_code in self._cache
    
    def get_all_codes(self) -> List[str]:
        """Get all food codes with edible portion data."""
        return list(self._cache.keys())
    
    def get_db_size(self) -> int:
        return len(self._cache)


# Global instance for convenience
edible_portion_calculator = EdiblePortionCalculator()