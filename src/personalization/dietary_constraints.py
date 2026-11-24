"""Dietary Constraints Engine - Evaluate recipes against user dietary preferences and restrictions."""

from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

from ..personalization.profile_models import DietaryPreference


class ConstraintResult(Enum):
    """Result of dietary constraint evaluation."""
    PASS = "PASS"           # Recipe passes constraint
    FAIL = "FAIL"           # Recipe fails constraint (hard block)
    UNVERIFIED = "UNVERIFIED"  # Cannot verify (missing ingredient info)


@dataclass
class ConstraintEvaluation:
    """Single constraint evaluation result."""
    constraint_type: str
    constraint_name: str
    result: ConstraintResult
    reason: str
    matched_items: List[str] = field(default_factory=list)
    severity: str = "HARD"  # HARD, SOFT, ADVISORY


@dataclass
class RecipeDietaryEvaluation:
    """Complete dietary evaluation for a recipe."""
    recipe_id: int
    recipe_name: str
    overall_result: ConstraintResult
    evaluations: List[ConstraintEvaluation] = field(default_factory=list)
    hard_fails: List[ConstraintEvaluation] = field(default_factory=list)
    soft_fails: List[ConstraintEvaluation] = field(default_factory=list)
    unverified: List[ConstraintEvaluation] = field(default_factory=list)
    passes: List[ConstraintEvaluation] = field(default_factory=list)
    
    @property
    def is_suitable(self) -> bool:
        """True if no hard failures."""
        return len(self.hard_fails) == 0
    
    @property
    def has_unverified(self) -> bool:
        return len(self.unverified) > 0
    
    def to_dict(self) -> Dict:
        return {
            "recipe_id": self.recipe_id,
            "recipe_name": self.recipe_name,
            "overall_result": self.overall_result.value,
            "is_suitable": self.is_suitable,
            "has_unverified": self.has_unverified,
            "evaluations": [
                {
                    "constraint_type": e.constraint_type,
                    "constraint_name": e.constraint_name,
                    "result": e.result.value,
                    "reason": e.reason,
                    "matched_items": e.matched_items,
                    "severity": e.severity,
                }
                for e in self.evaluations
            ],
            "summary": {
                "passes": len(self.passes),
                "hard_fails": len(self.hard_fails),
                "soft_fails": len(self.soft_fails),
                "unverified": len(self.unverified),
            }
        }


class DietClassifier:
    """Classify recipes into dietary categories based on ingredients."""
    
    # Non-vegetarian ingredients (core)
    NON_VEG_INGREDIENTS = {
        # Meats
        "chicken", "mutton", "lamb", "goat", "beef", "pork", "venison",
        "duck", "quail", "turkey", "rabbit",
        # Organ meats
        "liver", "kidney", "heart", "brain", "tongue", "tripe",
        # Seafood
        "fish", "prawn", "shrimp", "crab", "lobster", "mussel", "clam",
        "oyster", "scallop", "squid", "octopus",
        # Processed meats
        "bacon", "ham", "salami", "sausage", "pepperoni", "chorizo",
        # Eggs are handled separately for eggetarian classification
    }
    
    # Vegetarian but not vegan
    VEGETARIAN_NON_VEGAN = {
        "milk", "curd", "yogurt", "yoghurt", "butter", "ghee", "cream",
        "cheese", "paneer", "khoya", "mawa", "condensed milk",
        "whey", "casein", "lassi", "buttermilk", "dahi",
    }
    
    # Egg ingredients (for eggetarian)
    EGG_INGREDIENTS = {"egg", "eggs", "egg white", "egg yolk", "omelette", "mayonnaise"}
    
    # Jain-restricted ingredients (root vegetables, fermented, certain others)
    JAIN_RESTRICTED = {
        # Root vegetables
        "onion", "garlic", "potato", "carrot", "radish", "beetroot",
        "ginger", "turmeric", "yam", "colocasia", "turnip", "parsnip",
        "sweet potato", "taro", "cassava",
        # Fermented
        "yeast", "vinegar", "alcohol", "wine", "beer", "fermented",
        # Certain others
        "mushroom", "honey", "gelatin",
        # Multi-seeded fruits (some traditions)
        "fig", "pomegranate",  # sometimes restricted
    }
    
    # Common allergens
    ALLERGENS = {
        "peanut": ["peanut", "groundnut", "peanut butter", "peanut oil"],
        "tree_nut": ["almond", "cashew", "walnut", "pistachio", "hazelnut", 
                     "macadamia", "pecan", "brazil nut", "pine nut", "nut"],
        "milk": ["milk", "curd", "yogurt", "yoghurt", "butter", "ghee", "cream",
                 "cheese", "paneer", "khoya", "whey", "casein", "lassi"],
        "egg": ["egg", "eggs", "egg white", "egg yolk", "mayonnaise", "omelette"],
        "wheat": ["wheat", "atta", "maida", "flour", "bread", "roti", "chapati",
                  "naan", "paratha", "puri", "biscuit", "cookie", "cake", "semolina",
                  "suji", "rava", "sevai", "vermicelli", "pasta", "noodles"],
        "soy": ["soy", "soya", "tofu", "tempeh", "soy sauce", "soy milk", "edamame"],
        "fish": ["fish", "salmon", "tuna", "mackerel", "sardine", "anchovy"],
        "shellfish": ["prawn", "shrimp", "crab", "lobster", "mussel", "clam", "oyster", "scallop"],
        "sesame": ["sesame", "til", "tahini", "sesame oil", "gingelly oil"],
        "mustard": ["mustard", "sarson", "mustard seeds", "mustard oil"],
        "celery": ["celery", "ajwain", "celery seed"],
    }
    
    def __init__(self):
        # Normalize all ingredient sets to lowercase
        self.non_veg = {ing.lower() for ing in self.NON_VEG_INGREDIENTS}
        self.veg_non_vegan = {ing.lower() for ing in self.VEGETARIAN_NON_VEGAN}
        self.egg_ingredients = {ing.lower() for ing in self.EGG_INGREDIENTS}
        self.jain_restricted = {ing.lower() for ing in self.JAIN_RESTRICTED}
        self.allergens = {k: {v.lower() for v in vs} for k, vs in self.ALLERGENS.items()}
    
    def classify_recipe(self, ingredients: List[str]) -> Dict[str, Any]:
        """
        Classify a recipe based on its ingredients.
        
        Returns:
            Dict with classification results
        """
        normalized = [ing.lower().strip() for ing in ingredients if ing]
        ingredient_set = set(normalized)
        
        # Check non-vegetarian
        non_veg_found = ingredient_set & self.non_veg
        is_non_veg = len(non_veg_found) > 0
        
        # Check vegetarian non-vegan
        dairy_found = ingredient_set & self.veg_non_vegan
        
        # Check eggs
        egg_found = ingredient_set & self.egg_ingredients
        
        # Check Jain restrictions
        jain_found = ingredient_set & self.jain_restricted
        
        # Determine classification
        if is_non_veg:
            diet_type = "NON_VEGETARIAN"
        elif egg_found and not dairy_found:
            diet_type = "EGGETARIAN"
        elif dairy_found:
            diet_type = "VEGETARIAN"
        else:
            diet_type = "VEGAN"
        
        # Jain compliance
        jain_compliant = len(jain_found) == 0
        
        return {
            "diet_type": diet_type,
            "is_vegetarian": diet_type in ("VEGETARIAN", "VEGAN", "EGGETARIAN"),
            "is_vegan": diet_type == "VEGAN",
            "is_eggetarian": diet_type == "EGGETARIAN",
            "is_non_veg": is_non_veg,
            "non_veg_ingredients": sorted(non_veg_found),
            "dairy_ingredients": sorted(dairy_found),
            "egg_ingredients": sorted(egg_found),
            "jain_compliant": jain_compliant,
            "jain_restricted_ingredients": sorted(jain_found),
            "total_ingredients": len(ingredient_set),
        }


class AllergenFilter:
    """Filter recipes based on user allergies."""
    
    def __init__(self, classifier: Optional[DietClassifier] = None):
        self.classifier = classifier or DietClassifier()
    
    def check_allergens(
        self,
        ingredients: List[str],
        user_allergies: List[str]
    ) -> List[ConstraintEvaluation]:
        """
        Check recipe ingredients against user allergies.
        
        Returns:
            List of ConstraintEvaluation for each allergen
        """
        evaluations = []
        normalized = [ing.lower().strip() for ing in ingredients if ing]
        ingredient_set = set(normalized)
        
        # Normalize user allergies
        user_allergies_norm = [a.lower().strip() for a in user_allergies]
        
        for allergen in user_allergies_norm:
            # Get allergen ingredient patterns
            allergen_patterns = self.classifier.allergens.get(allergen, {allergen})
            
            # Check for matches
            matches = []
            for pattern in allergen_patterns:
                # Check exact match
                if pattern in ingredient_set:
                    matches.append(pattern)
                # Check partial match (for compound ingredients)
                for ing in ingredient_set:
                    if pattern in ing or ing in pattern:
                        matches.append(ing)
            
            if matches:
                evaluations.append(ConstraintEvaluation(
                    constraint_type="ALLERGEN",
                    constraint_name=f"Allergen: {allergen}",
                    result=ConstraintResult.FAIL,
                    reason=f"Recipe contains {allergen}: {', '.join(matches)}",
                    matched_items=sorted(matches),
                    severity="HARD"
                ))
            else:
                evaluations.append(ConstraintEvaluation(
                    constraint_type="ALLERGEN",
                    constraint_name=f"Allergen: {allergen}",
                    result=ConstraintResult.PASS,
                    reason=f"No {allergen} detected",
                    matched_items=[],
                    severity="HARD"
                ))
        
        return evaluations
    
    def has_allergen(self, ingredients: List[str], allergen: str) -> bool:
        """Quick check if recipe contains a specific allergen."""
        evals = self.check_allergens(ingredients, [allergen])
        return any(e.result == ConstraintResult.FAIL for e in evals)


class IngredientExclusionFilter:
    """Filter recipes based on user ingredient exclusions."""
    
    def __init__(self):
        pass
    
    def check_exclusions(
        self,
        ingredients: List[str],
        exclusions: List[str],
        severity: str = "HARD"
    ) -> List[ConstraintEvaluation]:
        """
        Check recipe ingredients against user exclusions.
        
        Args:
            ingredients: Recipe ingredients
            exclusions: User's excluded ingredients
            severity: "HARD" (block) or "SOFT" (warn)
            
        Returns:
            List of ConstraintEvaluation
        """
        evaluations = []
        normalized = [ing.lower().strip() for ing in ingredients if ing]
        ingredient_set = set(normalized)
        
        for exclusion in exclusions:
            exclusion_norm = exclusion.lower().strip()
            
            # Check for matches (exact and partial)
            matches = []
            for ing in ingredient_set:
                if exclusion_norm == ing or exclusion_norm in ing or ing in exclusion_norm:
                    matches.append(ing)
            
            if matches:
                evaluations.append(ConstraintEvaluation(
                    constraint_type="EXCLUSION",
                    constraint_name=f"Excluded ingredient: {exclusion}",
                    result=ConstraintResult.FAIL,
                    reason=f"Recipe contains excluded ingredient: {', '.join(matches)}",
                    matched_items=sorted(matches),
                    severity=severity
                ))
            else:
                evaluations.append(ConstraintEvaluation(
                    constraint_type="EXCLUSION",
                    constraint_name=f"Excluded ingredient: {exclusion}",
                    result=ConstraintResult.PASS,
                    reason=f"Excluded ingredient '{exclusion}' not found",
                    matched_items=[],
                    severity=severity
                ))
        
        return evaluations


class DietaryPreferenceFilter:
    """Filter recipes based on dietary preference (veg/non-veg/vegan/etc.)."""
    
    def __init__(self, classifier: Optional[DietClassifier] = None):
        self.classifier = classifier or DietClassifier()
    
    def check_preference(
        self,
        ingredients: List[str],
        preference: str  # DietaryPreference value
    ) -> List[ConstraintEvaluation]:
        """
        Check if recipe matches user's dietary preference.
        """
        evaluations = []
        classification = self.classifier.classify_recipe(ingredients)
        recipe_type = classification["diet_type"]
        
        # Map preferences to allowed types
        preference_map = {
            "VEGAN": ["VEGAN"],
            "VEGETARIAN": ["VEGAN", "VEGETARIAN"],
            "EGGETARIAN": ["VEGAN", "VEGETARIAN", "EGGETARIAN"],
            "JAIN": ["VEGAN", "VEGETARIAN"],  # Jain is stricter vegetarian
            "NON_VEGETARIAN": ["VEGAN", "VEGETARIAN", "EGGETARIAN", "NON_VEGETARIAN"],
            "OMNIVORE": ["VEGAN", "VEGETARIAN", "EGGETARIAN", "NON_VEGETARIAN"],
        }
        
        allowed_types = preference_map.get(preference.upper(), ["VEGAN", "VEGETARIAN", "EGGETARIAN", "NON_VEGETARIAN"])
        
        if recipe_type in allowed_types:
            evaluations.append(ConstraintEvaluation(
                constraint_type="DIETARY_PREFERENCE",
                constraint_name=f"Dietary preference: {preference}",
                result=ConstraintResult.PASS,
                reason=f"Recipe is {recipe_type}, allowed for {preference}",
                matched_items=[recipe_type],
                severity="HARD"
            ))
        else:
            evaluations.append(ConstraintEvaluation(
                constraint_type="DIETARY_PREFERENCE",
                constraint_name=f"Dietary preference: {preference}",
                result=ConstraintResult.FAIL,
                reason=f"Recipe is {recipe_type}, not compatible with {preference}",
                matched_items=[recipe_type],
                severity="HARD"
            ))
        
        return evaluations


class JainComplianceFilter:
    """Check Jain dietary compliance."""
    
    def __init__(self, classifier: Optional[DietClassifier] = None):
        self.classifier = classifier or DietClassifier()
    
    def check_compliance(self, ingredients: List[str]) -> List[ConstraintEvaluation]:
        """Check Jain dietary compliance."""
        evaluations = []
        classification = self.classifier.classify_recipe(ingredients)
        
        if classification["jain_compliant"]:
            evaluations.append(ConstraintEvaluation(
                constraint_type="JAIN_COMPLIANCE",
                constraint_name="Jain dietary compliance",
                result=ConstraintResult.PASS,
                reason="Recipe contains no Jain-restricted ingredients",
                matched_items=[],
                severity="HARD"
            ))
        else:
            evaluations.append(ConstraintEvaluation(
                constraint_type="JAIN_COMPLIANCE",
                constraint_name="Jain dietary compliance",
                result=ConstraintResult.FAIL,
                reason=f"Recipe contains Jain-restricted ingredients: {', '.join(classification['jain_restricted_ingredients'])}",
                matched_items=classification["jain_restricted_ingredients"],
                severity="HARD"
            ))
        
        return evaluations


class DietaryConstraintEngine:
    """
    Main engine for evaluating recipes against user dietary constraints.
    
    Combines all filters: allergens, exclusions, preferences, Jain compliance.
    """
    
    def __init__(self):
        self.classifier = DietClassifier()
        self.allergen_filter = AllergenFilter(self.classifier)
        self.exclusion_filter = IngredientExclusionFilter()
        self.preference_filter = DietaryPreferenceFilter(self.classifier)
        self.jain_filter = JainComplianceFilter(self.classifier)
    
    def evaluate_recipe(
        self,
        recipe_id: int,
        recipe_name: str,
        ingredients: List[str],
        user_preference: str = "OMNIVORE",
        user_allergies: Optional[List[str]] = None,
        user_exclusions: Optional[List[str]] = None,
        check_jain: bool = False,
        exclusion_severity: str = "HARD"
    ) -> RecipeDietaryEvaluation:
        """
        Evaluate a recipe against all user dietary constraints.
        
        Args:
            recipe_id: Recipe identifier
            recipe_name: Recipe name
            ingredients: List of ingredient names
            user_preference: DietaryPreference value
            user_allergies: List of user allergies
            user_exclusions: List of excluded ingredients
            check_jain: Whether to check Jain compliance
            exclusion_severity: "HARD" or "SOFT" for exclusions
            
        Returns:
            RecipeDietaryEvaluation with complete results
        """
        all_evaluations = []
        
        # 1. Dietary preference check
        pref_evals = self.preference_filter.check_preference(ingredients, user_preference)
        all_evaluations.extend(pref_evals)
        
        # 2. Allergen check
        if user_allergies:
            allergen_evals = self.allergen_filter.check_allergens(ingredients, user_allergies)
            all_evaluations.extend(allergen_evals)
        
        # 3. Ingredient exclusions
        if user_exclusions:
            exclusion_evals = self.exclusion_filter.check_exclusions(
                ingredients, user_exclusions, severity=exclusion_severity
            )
            all_evaluations.extend(exclusion_evals)
        
        # 4. Jain compliance
        if check_jain:
            jain_evals = self.jain_filter.check_compliance(ingredients)
            all_evaluations.extend(jain_evals)
        
        # Categorize results
        hard_fails = [e for e in all_evaluations if e.result == ConstraintResult.FAIL and e.severity == "HARD"]
        soft_fails = [e for e in all_evaluations if e.result == ConstraintResult.FAIL and e.severity == "SOFT"]
        unverified = [e for e in all_evaluations if e.result == ConstraintResult.UNVERIFIED]
        passes = [e for e in all_evaluations if e.result == ConstraintResult.PASS]
        
        # Overall result
        if hard_fails:
            overall = ConstraintResult.FAIL
        elif unverified:
            overall = ConstraintResult.UNVERIFIED
        else:
            overall = ConstraintResult.PASS
        
        return RecipeDietaryEvaluation(
            recipe_id=recipe_id,
            recipe_name=recipe_name,
            overall_result=overall,
            evaluations=all_evaluations,
            hard_fails=hard_fails,
            soft_fails=soft_fails,
            unverified=unverified,
            passes=passes
        )
    
    def evaluate_batch(
        self,
        recipes: List[Dict],
        user_preference: str = "OMNIVORE",
        user_allergies: Optional[List[str]] = None,
        user_exclusions: Optional[List[str]] = None,
        check_jain: bool = False
    ) -> List[RecipeDietaryEvaluation]:
        """
        Evaluate multiple recipes.
        
        Args:
            recipes: List of dicts with recipe_id, recipe_name, ingredients
            
        Returns:
            List of RecipeDietaryEvaluation
        """
        results = []
        for recipe in recipes:
            eval_result = self.evaluate_recipe(
                recipe_id=recipe["recipe_id"],
                recipe_name=recipe.get("recipe_name", f"Recipe {recipe['recipe_id']}"),
                ingredients=recipe.get("ingredients", []),
                user_preference=user_preference,
                user_allergies=user_allergies,
                user_exclusions=user_exclusions,
                check_jain=check_jain
            )
            results.append(eval_result)
        return results
    
    def filter_suitable(
        self,
        recipes: List[Dict],
        user_preference: str = "OMNIVORE",
        user_allergies: Optional[List[str]] = None,
        user_exclusions: Optional[List[str]] = None,
        check_jain: bool = False,
        include_unverified: bool = False
    ) -> List[Dict]:
        """
        Filter recipes to only suitable ones.
        
        Args:
            include_unverified: If True, include UNVERIFIED recipes
            
        Returns:
            List of suitable recipe dicts with evaluation attached
        """
        evaluations = self.evaluate_batch(recipes, user_preference, user_allergies, user_exclusions, check_jain)
        
        suitable = []
        for recipe, eval_result in zip(recipes, evaluations):
            if eval_result.overall_result == ConstraintResult.PASS:
                recipe_copy = recipe.copy()
                recipe_copy["dietary_evaluation"] = eval_result.to_dict()
                suitable.append(recipe_copy)
            elif include_unverified and eval_result.overall_result == ConstraintResult.UNVERIFIED:
                recipe_copy = recipe.copy()
                recipe_copy["dietary_evaluation"] = eval_result.to_dict()
                suitable.append(recipe_copy)
        
        return suitable


# Convenience functions
def evaluate_recipe_dietary(
    recipe_id: int,
    recipe_name: str,
    ingredients: List[str],
    user_preference: str = "OMNIVORE",
    user_allergies: Optional[List[str]] = None,
    user_exclusions: Optional[List[str]] = None,
    check_jain: bool = False
) -> RecipeDietaryEvaluation:
    """Quick single recipe evaluation."""
    engine = DietaryConstraintEngine()
    return engine.evaluate_recipe(
        recipe_id=recipe_id,
        recipe_name=recipe_name,
        ingredients=ingredients,
        user_preference=user_preference,
        user_allergies=user_allergies,
        user_exclusions=user_exclusions,
        check_jain=check_jain
    )


def filter_recipes_by_diet(
    recipes: List[Dict],
    user_preference: str = "OMNIVORE",
    user_allergies: Optional[List[str]] = None,
    user_exclusions: Optional[List[str]] = None,
    check_jain: bool = False
) -> List[Dict]:
    """Filter recipes by dietary constraints."""
    engine = DietaryConstraintEngine()
    return engine.filter_suitable(
        recipes, user_preference, user_allergies, user_exclusions, check_jain
    )