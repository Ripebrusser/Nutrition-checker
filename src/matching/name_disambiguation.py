"""Ingredient Name Disambiguation - Parenthetical extraction and preparation-state handling."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set
from enum import Enum
import re
import logging
import pandas as pd

logger = logging.getLogger(__name__)


class PreparationState(Enum):
    """Preparation state taxonomy."""
    RAW = "RAW"
    FRESH = "FRESH"
    DRIED = "DRIED"
    ROASTED = "ROASTED"
    FRIED = "FRIED"
    BOILED = "BOILED"
    COOKED = "COOKED"
    FERMENTED = "FERMENTED"
    SPROUTED = "SPROUTED"
    POWDERED = "POWDERED"
    GROUND = "GROUND"
    PICKLED = "PICKLED"
    BLANCHED = "BLANCHED"
    SOAKED = "SOAKED"
    MARINATED = "MARINATED"
    UNKNOWN = "UNKNOWN"
    NOT_SPECIFIED = "NOT_SPECIFIED"


class AliasType(Enum):
    """Type of parenthetical alias."""
    SYNONYM = "SYNONYM"           # e.g., "cumin seeds (jeera)"
    HINDI_NAME = "HINDI_NAME"     # e.g., "cumin seeds (जीरा)"
    ALTERNATE_NAME = "ALTERNATE_NAME"  # e.g., "pigeon pea (toor dal)"
    PREPARATION = "PREPARATION"   # e.g., "onion (bulb) - thinly sliced"
    QUANTITY = "QUANTITY"         # e.g., "rice (1 cup)"
    SIZE = "SIZE"                 # e.g., "potato (large)"
    EDIBLE_PART = "EDIBLE_PART"   # e.g., "coconut (kernel)"
    VARIETY = "VARIETY"           # e.g., "rice (basmati)"
    EXPLANATORY = "EXPLANATORY"   # e.g., "amchur (dry mango powder)"
    UNCLASSIFIED = "UNCLASSIFIED"


@dataclass
class ExtractedAlias:
    """An extracted parenthetical alias."""
    text: str
    alias_type: AliasType
    confidence: float
    start_pos: int
    end_pos: int


@dataclass
class DisambiguatedIngredient:
    """Result of ingredient name disambiguation."""
    original_ingredient: str
    normalized_ingredient: str
    primary_ingredient: str
    parenthetical_text: str
    extracted_aliases: List[ExtractedAlias]
    parentheses_balanced: bool
    alias_extraction_status: str
    preparation_state: PreparationState
    preparation_confidence: float
    ambiguity_flags: List[str]
    source_recipe_id: int
    source_field: str
    
    def to_dict(self) -> dict:
        return {
            'original_ingredient': self.original_ingredient,
            'normalized_ingredient': self.normalized_ingredient,
            'primary_ingredient': self.primary_ingredient,
            'parenthetical_text': self.parenthetical_text,
            'extracted_aliases': [
                {
                    'text': a.text,
                    'type': a.alias_type.value,
                    'confidence': a.confidence,
                    'start_pos': a.start_pos,
                    'end_pos': a.end_pos
                }
                for a in self.extracted_aliases
            ],
            'parentheses_balanced': self.parentheses_balanced,
            'alias_extraction_status': self.alias_extraction_status,
            'preparation_state': self.preparation_state.value,
            'preparation_confidence': self.preparation_confidence,
            'ambiguity_flags': self.ambiguity_flags,
            'recipe_id': self.source_recipe_id,
            'source_field': self.source_field
        }


# Patterns for classification
PREPARATION_KEYWORDS = {
    PreparationState.RAW: ['raw', 'uncooked'],
    PreparationState.FRESH: ['fresh'],
    PreparationState.DRIED: ['dried', 'dry', 'dehydrated', 'sun-dried', 'sundried'],
    PreparationState.ROASTED: ['roasted', 'roast', 'bhuna'],
    PreparationState.FRIED: ['fried', 'fry', 'talna'],
    PreparationState.BOILED: ['boiled', 'boil', 'ubla'],
    PreparationState.COOKED: ['cooked', 'cook', 'pakka'],
    PreparationState.FERMENTED: ['fermented', 'ferment', 'khamir'],
    PreparationState.SPROUTED: ['sprouted', 'sprout', 'ankurit'],
    PreparationState.POWDERED: ['powdered', 'powder', 'pisi', 'pisii'],
    PreparationState.GROUND: ['ground', 'grind', 'pisa'],
    PreparationState.PICKLED: ['pickled', 'pickle', 'achar'],
    PreparationState.BLANCHED: ['blanched', 'blanch'],
    PreparationState.SOAKED: ['soaked', 'soak', 'bhigo'],
    PreparationState.MARINATED: ['marinated', 'marinate'],
}

EDIBLE_PART_KEYWORDS = {
    'kernel', 'seed', 'seeds', 'leaf', 'leaves', 'root', 'roots', 'stem', 'stems',
    'flower', 'flowers', 'fruit', 'fruits', 'peel', 'skin', 'rind', 'pulp',
    'juice', 'water', 'milk', 'oil', 'paste', 'powder', 'flour', 'nut', 'nuts',
    'flesh', 'bulb', 'clove', 'cloves'
}

VARIETY_KEYWORDS = {
    'basmati', 'sona masuri', 'sona masoori', 'brown', 'white', 'red', 'black',
    'green', 'yellow', 'whole', 'split', 'long grain', 'short grain', 'medium',
    'kabuli', 'desi', 'local', 'hybrid', 'improved', 'traditional', 'organic'
}

QUANTITY_PATTERN = re.compile(r'\d+(?:\.\d+)?\s*(?:cup|cups|tbsp|tsp|tablespoon|teaspoon|piece|pieces|clove|cloves|slice|slices|g|gram|grams|kg|ml|l|liter|litre)', re.IGNORECASE)
SIZE_PATTERN = re.compile(r'\b(small|medium|large|big|tiny|huge|mini)\b', re.IGNORECASE)

# Known Hindi/English alias pairs (from synonym dictionary)
HINDI_ALIAS_PATTERNS = [
    (r'\b(jeera|zeera)\b', 'cumin seeds', AliasType.HINDI_NAME),
    (r'\b(haldi)\b', 'turmeric powder', AliasType.HINDI_NAME),
    (r'\b(dhania)\b', 'coriander', AliasType.HINDI_NAME),
    (r'\b(besan)\b', 'chickpea flour', AliasType.HINDI_NAME),
    (r'\b(atta)\b', 'wheat flour', AliasType.HINDI_NAME),
    (r'\b(maida)\b', 'refined wheat flour', AliasType.HINDI_NAME),
    (r'\b(suji|rava)\b', 'semolina', AliasType.HINDI_NAME),
    (r'\b(kala chana)\b', 'chickpea (desi)', AliasType.HINDI_NAME),
    (r'\b(kabuli chana)\b', 'chickpea (kabuli)', AliasType.HINDI_NAME),
    (r'\b(toor dal|arhar dal|tuvar dal)\b', 'pigeon pea', AliasType.HINDI_NAME),
    (r'\b(moong dal|hari moong)\b', 'green gram', AliasType.HINDI_NAME),
    (r'\b(urad dal|maah ki dal)\b', 'black gram', AliasType.HINDI_NAME),
    (r'\b(chana dal)\b', 'bengal gram', AliasType.HINDI_NAME),
    (r'\b(masoor dal)\b', 'red lentil', AliasType.HINDI_NAME),
    (r'\b(hing|heeng)\b', 'asafoetida', AliasType.HINDI_NAME),
    (r'\b(saunf)\b', 'fennel seeds', AliasType.HINDI_NAME),
    (r'\b(methi)\b', 'fenugreek', AliasType.HINDI_NAME),
    (r'\b(ajwain)\b', 'carom seeds', AliasType.HINDI_NAME),
    (r'\b(kalonji)\b', 'nigella seeds', AliasType.HINDI_NAME),
    (r'\b(elaichi|elaichi)\b', 'cardamom', AliasType.HINDI_NAME),
    (r'\b(lal mirch)\b', 'red chili', AliasType.HINDI_NAME),
    (r'\b(hari mirch)\b', 'green chili', AliasType.HINDI_NAME),
    (r'\b(adrak)\b', 'ginger', AliasType.HINDI_NAME),
    (r'\b(lehsun|lassan)\b', 'garlic', AliasType.HINDI_NAME),
    (r'\b(pyaaz|pyaaj)\b', 'onion', AliasType.HINDI_NAME),
    (r'\b(tamatar)\b', 'tomato', AliasType.HINDI_NAME),
    (r'\b(gajar)\b', 'carrot', AliasType.HINDI_NAME),
    (r'\b(gobhi)\b', 'cauliflower', AliasType.HINDI_NAME),
    (r'\b(palak)\b', 'spinach', AliasType.HINDI_NAME),
    (r'\b(methi patta)\b', 'fenugreek leaves', AliasType.HINDI_NAME),
    (r'\b(pudina)\b', 'mint leaves', AliasType.HINDI_NAME),
    (r'\b(kadi patta)\b', 'curry leaves', AliasType.HINDI_NAME),
]


def check_parentheses_balance(text: str) -> Tuple[bool, List[Tuple[int, int]]]:
    """Check if parentheses are balanced and return positions of matched pairs."""
    stack = []
    pairs = []
    for i, char in enumerate(text):
        if char == '(':
            stack.append(i)
        elif char == ')':
            if stack:
                start = stack.pop()
                pairs.append((start, i))
            else:
                return False, pairs
    return len(stack) == 0, pairs


def extract_parenthetical_content(text: str) -> List[Tuple[str, int, int]]:
    """Extract parenthetical content with positions.
    
    For nested parentheses, only extract the outermost level to avoid duplicates.
    Also handles unbalanced parentheses.
    """
    results = []
    stack = []
    outer_pairs = []
    
    for i, char in enumerate(text):
        if char == '(':
            stack.append(i)
        elif char == ')':
            if stack:
                start = stack.pop()
                if not stack:  # Only record when we're back to outermost level
                    outer_pairs.append((start, i))
    
    # Add outermost pairs
    for start, end in outer_pairs:
        content = text[start+1:end]
        results.append((content, start, end))
    
    # Handle unclosed parentheses - treat everything from opening paren to end as content
    # But only for unclosed outermost parentheses
    for start in stack:
        content = text[start+1:]
        results.append((content, start, len(text)))
    
    return results


def classify_alias(content: str, context: str = "") -> Tuple[AliasType, float]:
    """Classify the type of parenthetical alias with mutually exclusive types.
    
    Priority order (highest to lowest):
    1. QUANTITY - explicit measurements
    2. SIZE - size descriptors
    3. PREPARATION - explicit preparation/cooking terms
    4. HINDI_NAME - known Hindi/English alias pairs
    5. EDIBLE_PART - anatomical parts
    6. VARIETY - cultivar/variety names
    7. QUANTITY (loose) - loose quantity mentions
    7. ALTERNATE_NAME - explicit "or/aka" synonyms
    8. SYNONYM - short alternative names
    8. EXPLANATORY - explanatory/descriptive text
    9. UNCLASSIFIED - everything else
    
    This ensures mutually exclusive classification with clear priority.
    """
    content_lower = content.lower().strip()
    
    # 1. QUANTITY - explicit measurements (highest priority)
    if QUANTITY_PATTERN.search(content):
        return AliasType.QUANTITY, 0.95
    
    # 2. SIZE - size descriptors
    if SIZE_PATTERN.search(content):
        return AliasType.SIZE, 0.9
    
    # 3. PREPARATION - explicit preparation/cooking terms
    for prep_state, keywords in PREPARATION_KEYWORDS.items():
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', content_lower):
                return AliasType.PREPARATION, 0.9
    
    # 4. HINDI_NAME - known Hindi/English alias pairs (high confidence)
    for pattern, canonical, alias_type in HINDI_ALIAS_PATTERNS:
        if re.search(pattern, content_lower):
            return AliasType.HINDI_NAME, 0.95
    
    # 5. EDIBLE_PART - anatomical parts
    for part in EDIBLE_PART_KEYWORDS:
        if re.search(r'\b' + re.escape(part) + r'\b', content_lower):
            return AliasType.EDIBLE_PART, 0.85
    
    # 6. VARIETY - cultivar/variety names
    for variety in VARIETY_KEYWORDS:
        if re.search(r'\b' + re.escape(variety) + r'\b', content_lower):
            return AliasType.VARIETY, 0.85
    
    # 7. ALTERNATE_NAME - explicit "or/aka" synonyms
    if any(kw in content_lower for kw in ['or', 'aka', 'also known as', 'known as']):
        return AliasType.ALTERNATE_NAME, 0.7
    
    # 8. SYNONYM - short alternative names (2-3 words, alphabetic)
    words = content_lower.split()
    if (re.search(r'[a-z]', content_lower) and 
        len(content_lower) > 1 and
        len(words) <= 3 and
        all(re.search(r'[a-z]', w) for w in words) and
        not any(kw in content_lower for kw in ['dry', 'fresh', 'ripe', 'raw', 'powder', 'powdered', 'split', 'whole', 'bulb', 'stalk', 'seed'])):
        return AliasType.SYNONYM, 0.6
    
    # 9. EXPLANATORY - explanatory/descriptive text (contains prep-like words but not as primary)
    if any(kw in content_lower for kw in ['dry', 'fresh', 'ripe', 'raw', 'powder', 'powdered', 'split', 'whole', 'bulb', 'stalk', 'seed']):
        return AliasType.EXPLANATORY, 0.7
    
    # 10. UNCLASSIFIED - everything else
    return AliasType.UNCLASSIFIED, 0.3


def detect_preparation_state(text: str) -> Tuple[PreparationState, float]:
    """Detect preparation state from text."""
    text_lower = text.lower()
    
    # Check for explicit preparation states (highest confidence)
    for prep_state, keywords in PREPARATION_KEYWORDS.items():
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
                return prep_state, 0.9
    
    # Check for preparation in parenthetical (already extracted)
    # This is handled by the alias extraction
    
    return PreparationState.NOT_SPECIFIED, 0.5


class IngredientNameDisambiguator:
    """Disambiguate ingredient names by extracting parenthetical aliases and preparation states."""
    
    def __init__(self):
        self.stats = {
            'total': 0,
            'with_parentheses': 0,
            'balanced': 0,
            'unbalanced': 0,
            'aliases_extracted': 0,
            'preparation_detected': 0
        }
    
    def disambiguate(self, 
                     original_ingredient: str,
                     normalized_ingredient: str,
                     ingredient_name: str,
                     recipe_id: int,
                     source_field: str) -> DisambiguatedIngredient:
        """
        Disambiguate an ingredient name.
        
        Args:
            original_ingredient: Original text from recipe
            normalized_ingredient: Full normalized text (with quantities/units)
            ingredient_name: Extracted ingredient name (from parser, quantities/units removed)
            recipe_id: Recipe ID
            source_field: 'ingredients_raw' or 'ingredients_en'
            
        Returns:
            DisambiguatedIngredient object
        """
        self.stats['total'] += 1
        
        # Check if ingredient_name has truncated parentheses (unbalanced with no closing)
        # If so, fall back to normalized_ingredient for parenthetical extraction
        use_normalized_for_parens = False
        if ingredient_name and not pd.isna(ingredient_name):
            balanced, _ = check_parentheses_balance(ingredient_name)
            if not balanced and '(' in ingredient_name and ')' not in ingredient_name:
                # Likely truncated - use normalized_ingredient
                use_normalized_for_parens = True
        
        # Use ingredient_name for primary text (has quantities/units removed)
        # Use normalized_ingredient for parenthetical extraction if ingredient_name is truncated
        text_for_parens = normalized_ingredient if use_normalized_for_parens else (
            ingredient_name if ingredient_name and not pd.isna(ingredient_name) else normalized_ingredient
        )
        text = ingredient_name if ingredient_name and not pd.isna(ingredient_name) else normalized_ingredient
        
        # Also keep normalized_ingredient for preparation detection
        full_text = normalized_ingredient
        
        # Check parentheses balance on text_for_parens (used for extraction)
        balanced, pairs = check_parentheses_balance(text_for_parens)
        if '(' in text_for_parens or ')' in text_for_parens:
            self.stats['with_parentheses'] += 1
            if balanced:
                self.stats['balanced'] += 1
            else:
                self.stats['unbalanced'] += 1
        
        # Extract parenthetical content from text_for_parens
        parentheticals = extract_parenthetical_content(text_for_parens)
        
        # Classify each parenthetical
        aliases = []
        for content, start, end in parentheticals:
            alias_type, confidence = classify_alias(content, text)
            aliases.append(ExtractedAlias(
                text=content,
                alias_type=alias_type,
                confidence=confidence,
                start_pos=start,
                end_pos=end
            ))
            self.stats['aliases_extracted'] += 1
        
        # Determine primary ingredient by removing parentheticals and cleaning
        primary = self._extract_primary_ingredient(text, text_for_parens, parentheticals, use_normalized_for_parens)
        
        # Detect preparation state from aliases, primary text, and full normalized text
        prep_state, prep_confidence = self._detect_preparation(text, aliases, normalized_ingredient)
        if prep_state != PreparationState.NOT_SPECIFIED:
            self.stats['preparation_detected'] += 1
        
        # Identify ambiguity flags
        ambiguity_flags = self._identify_ambiguity(primary, aliases, balanced)
        
        # Determine extraction status
        if not parentheticals:
            extraction_status = "NO_PARENTHESES"
        elif balanced and all(a.confidence >= 0.7 for a in aliases):
            extraction_status = "SUCCESS"
        elif not balanced:
            extraction_status = "UNBALANCED_PARENTHESES"
        elif any(a.confidence < 0.7 for a in aliases):
            extraction_status = "LOW_CONFIDENCE_ALIASES"
        else:
            extraction_status = "PARTIAL"
        
        return DisambiguatedIngredient(
            original_ingredient=original_ingredient,
            normalized_ingredient=normalized_ingredient,
            primary_ingredient=primary,
            parenthetical_text=', '.join([a.text for a in aliases]),
            extracted_aliases=aliases,
            parentheses_balanced=balanced,
            alias_extraction_status=extraction_status,
            preparation_state=prep_state,
            preparation_confidence=prep_confidence,
            ambiguity_flags=ambiguity_flags,
            source_recipe_id=recipe_id,
            source_field=source_field
        )
    
    def _extract_primary_ingredient(self, text: str, text_for_parens: str, parentheticals: List[Tuple[str, int, int]], use_normalized: bool) -> str:
        """Extract primary ingredient name by removing parentheticals."""
        # Use text_for_parens for removing parentheticals (has balanced parentheses)
        # Then clean the result
        source_text = text_for_parens if use_normalized else text
        
        if not parentheticals:
            primary = self._clean_ingredient_text(source_text, remove_leading_qty=use_normalized)
            return primary
        
        # Remove parenthetical content from source_text
        result = []
        last_end = 0
        for content, start, end in parentheticals:
            result.append(source_text[last_end:start])
            last_end = end + 1
        result.append(source_text[last_end:])
        
        primary = ''.join(result)
        return self._clean_ingredient_text(primary, remove_leading_qty=use_normalized)
    
    def _clean_ingredient_text(self, text: str, remove_leading_qty: bool = False) -> str:
        """Clean ingredient text: remove prep words, punctuation, parentheses remnants.
        
        Args:
            text: Text to clean
            remove_leading_qty: If True, also remove leading quantities and units
        """
        if remove_leading_qty:
            # Remove leading quantities and units
            text = re.sub(r'^[\d\s\-\/\.\u00BC\u00BD\u00BE\u2150-\u215E]+', '', text)
            # Remove leading units (cup, tbsp, tsp, etc.) - include plurals
            text = re.sub(r'^(cup|cups|tbsp|tsp|tablespoon|tablespoons|teaspoon|teaspoons|piece|pieces|clove|cloves|slice|slices)\s+', '', text, flags=re.IGNORECASE)
        
        # Remove trailing prep words (the parser may leave some)
        text = re.sub(r'\s*[,\-]\s*(chopped|diced|sliced|minced|grated|crushed|mashed|peeled|boiled|fried|roasted|steamed|baked|grilled|raw|fresh|dried|dry|powdered|powder|soaked|marinated|fermented|pickled|blanched)\s*$', '', text, flags=re.IGNORECASE)
        # Remove trailing size descriptors
        text = re.sub(r'\s*[,\-]\s*(small|medium|large|big|tiny|huge|mini)\s*$', '', text, flags=re.IGNORECASE)
        # Remove parentheses remnants
        text = re.sub(r'\s*\([^)]*\)', '', text)
        # Clean punctuation
        text = re.sub(r'[\s\-,\.\(\)\[\]]+$', '', text)
        text = re.sub(r'^[\s\-,\.\(\)\[\]]+', '', text)
        # Collapse whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _detect_preparation(self, text: str, aliases: List[ExtractedAlias], full_text: str = "") -> Tuple[PreparationState, float]:
        """Detect preparation state from text, aliases, and full normalized text."""
        # Check aliases first (higher confidence)
        for alias in aliases:
            if alias.alias_type == AliasType.PREPARATION:
                for prep_state, keywords in PREPARATION_KEYWORDS.items():
                    for kw in keywords:
                        if kw in alias.text.lower():
                            return prep_state, alias.confidence
        
        # Check full normalized text (has preparation words that parser may have removed)
        if full_text:
            full_lower = full_text.lower()
            for prep_state, keywords in PREPARATION_KEYWORDS.items():
                for kw in keywords:
                    if re.search(r'\b' + re.escape(kw) + r'\b', full_lower):
                        return prep_state, 0.85
        
        # Check remaining text
        return detect_preparation_state(text)
    
    def _identify_ambiguity(self, primary: str, aliases: List[ExtractedAlias], balanced: bool) -> List[str]:
        """Identify ambiguity flags."""
        flags = []
        
        if not balanced:
            flags.append("UNBALANCED_PARENTHESES")
        
        if not primary or len(primary.strip()) < 2:
            flags.append("EMPTY_PRIMARY_NAME")
        
        # Check for multiple synonym aliases
        synonym_aliases = [a for a in aliases if a.alias_type in (AliasType.SYNONYM, AliasType.HINDI_NAME, AliasType.ALTERNATE_NAME)]
        if len(synonym_aliases) > 1:
            flags.append("MULTIPLE_SYNONYMS")
        
        # Check for conflicting preparation aliases
        prep_aliases = [a for a in aliases if a.alias_type == AliasType.PREPARATION]
        if len(prep_aliases) > 1:
            flags.append("CONFLICTING_PREPARATION")
        
        # Check for generic ambiguous terms
        primary_lower = primary.lower().strip()
        ambiguous_terms = {'dal', 'rice', 'oil', 'milk', 'salt', 'sugar', 'flour', 'atta', 'maida', 'besan',
                          'dalia', 'rava', 'suji', 'poha', 'sevai', 'vermicelli', 'noodles',
                          'bread', 'roti', 'chapati', 'paratha', 'naan', 'kulcha',
                          'curry', 'masala', 'gravy', 'sauce', 'chutney', 'pickle'}
        if primary_lower in ambiguous_terms:
            flags.append("GENERIC_AMBIGUOUS_TERM")
        
        # Check for composite ingredients
        if any(kw in primary_lower for kw in ['paste', 'masala', 'powder', 'batter', 'chutney', 'pickle', 'sauce', 'curry']):
            flags.append("COMPOSITE_INGREDIENT")
        
        return flags


def disambiguate_ingredient_batch(parsed_df: pd.DataFrame) -> pd.DataFrame:
    """Disambiguate a batch of parsed ingredients."""
    disambiguator = IngredientNameDisambiguator()
    results = []
    
    for _, row in parsed_df.iterrows():
        disambiguated = disambiguator.disambiguate(
            original_ingredient=row.get('original_ingredient', row['normalized_ingredient']),
            normalized_ingredient=row['normalized_ingredient'],
            ingredient_name=row.get('ingredient_name', ''),
            recipe_id=row['recipe_id'],
            source_field=row.get('source_field', 'ingredients_raw')
        )
        results.append(disambiguated.to_dict())
    
    logger.info(f"Disambiguation stats: {disambiguator.stats}")
    return pd.DataFrame(results)


if __name__ == "__main__":
    import pandas as pd
    logging.basicConfig(level=logging.INFO)
    
    # Test with parsed ingredients
    parsed = pd.read_parquet('data/interim/phase2/parsed_recipe_ingredients.parquet')
    disambiguated = disambiguate_ingredient_batch(parsed.head(100))
    
    print("Sample disambiguated ingredients:")
    for _, row in disambiguated.head(20).iterrows():
        print(f"  Original: {row['original_ingredient'][:80]}")
        print(f"  Primary:  {row['primary_ingredient']}")
        print(f"  Aliases:  {row['parenthetical_text']}")
        print(f"  Prep:     {row['preparation_state']} (conf: {row['preparation_confidence']})")
        print(f"  Flags:    {row['ambiguity_flags']}")
        print(f"  Status:   {row['alias_extraction_status']}")
        print()