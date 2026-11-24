"""Main Matcher Orchestrator - Orchestrates the matching pipeline."""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import pandas as pd
import logging

from .ingredient_taxonomy import taxonomy, classify_ingredient, MatchCategory
from .candidate_generator import CandidateGenerator, Candidate
from .matching_rules import MatchStatus, MatchingRules
from .matching_confidence import ConfidenceScorer, compute_match_score
from .provenance import ProvenanceTracker, provenance_tracker

logger = logging.getLogger(__name__)


@dataclass
class MatchResult:
    """Final match result for an ingredient."""
    match_id: str
    input_record_id: str
    recipe_id: int
    original_ingredient: str
    normalized_ingredient: str
    source_field: str
    ifct_food_code: str
    ifct_food_name: str
    ifct_food_group: str
    match_status: str
    match_method: str
    similarity_score: float
    confidence_level: str
    evidence: dict
    requires_review: bool
    gram_weight: Optional[float] = None
    gram_weight_min: Optional[float] = None
    gram_weight_max: Optional[float] = None
    conversion_status: str = "UNRESOLVED"
    provenance_id: str = ""
    review_status: str = "PENDING"
    reviewer_notes: str = ""
    timestamp: str = ""


class IngredientMatcher:
    """Main orchestrator for ingredient matching pipeline."""
    
    def __init__(self, 
                 ifct_path: str = "data/interim/ifct_final_candidate/ifct_table1_candidate.parquet",
                 synonym_path: str = "data/interim/phase2/ingredient_synonyms.csv",
                 household_path: str = "data/interim/phase2/household_measurements.csv"):
        
        self.ifct_path = ifct_path
        self.synonym_path = synonym_path
        self.household_path = household_path
        
        # Initialize components
        self.candidate_generator = None
        self._initialize_components()
        
    def _initialize_components(self):
        """Initialize all matching components."""
        from .candidate_generator import CandidateGenerator
        from .matching_confidence import ConfidenceScorer
        
        self.candidate_generator = CandidateGenerator(
            ifct_path="data/interim/ifct_final_candidate/ifct_table1_candidate.parquet",
            synonym_path="data/interim/phase2/ingredient_synonyms.csv",
            household_path="data/interim/phase2/household_measurements.csv"
        )
        
        self.confidence_scorer = ConfidenceScorer()
        self.provenance_tracker = None  # Will be initialized when needed
    
    def match_ingredient(self, 
                         normalized_ingredient: str,
                         parsed_data: dict,
                         ingredient_name: str,
                         source_field: str,
                         recipe_id: int,
                         original_ingredient: str,
                         source_line: str) -> dict:
        """
        Match a single normalized ingredient to IFCT.
        
        Returns a match result dictionary.
        """
        # Generate candidates
        candidates = self.candidate_generator.generate_candidates(
            normalized_ingredient=normalized_ingredient,
            parsed_data=parsed_data,
            ingredient_name=ingredient_name,
            source_field=source_field
        )
        
        # Select best candidate
        best_candidate = self._select_best_candidate(candidates)
        
        # Build result
        result = {
            'recipe_id': recipe_id,
            'original_ingredient': original_ingredient,
            'normalized_ingredient': normalized_ingredient,
            'source_field': source_field,
            'ifct_food_code': '',
            'ifct_food_name': '',
            'ifct_food_group': '',
            'match_status': 'UNMATCHED',
            'match_method': 'NONE',
            'similarity_score': 0.0,
            'confidence_level': 'LOW',
            'evidence': {},
            'requires_review': True,
            'gram_weight': None,
            'gram_weight_min': None,
            'gram_weight_max': None,
            'conversion_status': 'UNRESOLVED',
            'provenance_id': '',
            'review_status': 'PENDING',
            'reviewer_notes': '',
            'timestamp': datetime.now().isoformat()
        }
        
        if best_candidate:
            result.update({
                'ifct_food_code': best_candidate.ifct_food_code,
                'ifct_food_name': best_candidate.ifct_food_name,
                'ifct_food_group': best_candidate.ifct_food_group,
                'match_status': best_candidate.match_method,
                'match_method': best_candidate.match_method,
                'similarity_score': best_candidate.similarity_score,
                'confidence_level': best_candidate.provisional_confidence,
                'evidence': best_candidate.evidence,
                'requires_review': best_candidate.requires_review,
                'gram_weight': best_candidate.gram_weight,
                'gram_weight_min': best_candidate.gram_weight_min,
                'gram_weight_max': best_candidate.gram_weight_max,
                'conversion_status': best_candidate.conversion_status,
            })
        
        return result
    
    def _select_best_candidate(self, candidates: List) -> Optional[object]:
        """Select the best candidate from the list."""
        if not candidates:
            return None
        
        # Sort by similarity score descending
        sorted_candidates = sorted(candidates, key=lambda c: c.similarity_score, reverse=True)
        
        # Return top candidate
        return sorted_candidates[0] if sorted_candidates else None
    
    def match_batch(self, ingredients_df: pd.DataFrame) -> pd.DataFrame:
        """
        Match a batch of ingredients.
        
        Args:
            ingredients_df: DataFrame with columns from parsed_recipe_ingredients
            
        Returns:
            DataFrame with match results
        """
        results = []
        
        for _, row in ingredients_df.iterrows():
            # Parse quantity/unit from the parsed data
            parsed_data = {
                'quantity': row.get('quantity'),
                'unit': row.get('unit'),
                'preparation': row.get('preparation'),
                'size_descriptor': row.get('size_descriptor')
            }
            
            result = self.match_ingredient(
                normalized_ingredient=row['normalized_ingredient'],
                parsed_data=parsed_data,
                ingredient_name=row.get('ingredient_name', ''),
                source_field=row['source_field'],
                recipe_id=row['recipe_id'],
                original_ingredient=row['original_ingredient'],
                source_line=row['source_line']
            )
            results.append(result)
        
        return pd.DataFrame(results)
    
    def match_recipe_ingredients(self, recipe_ids: List[int] = None) -> pd.DataFrame:
        """
        Match ingredients for specific recipes or all recipes.
        """
        # Load normalized ingredients
        norm_df = pd.read_parquet('data/interim/phase2/normalized_ingredients.parquet')
        
        if recipe_ids:
            norm_df = norm_df[norm_df['recipe_id'].isin(recipe_ids)]
        
        # Process in batches for memory efficiency
        batch_size = 10000
        results = []
        
        for i in range(0, len(norm_df), 10000):
            batch = norm_df.iloc[i:i+10000]
            batch_results = self._process_batch(norm_df.iloc[i:i+10000])
            # ... process batch
            
        return pd.DataFrame()


def create_matcher(ifct_path: str = None,
                   synonym_path: str = None,
                   household_path: str = None) -> 'IngredientMatcher':
    """Factory function to create matcher."""
    return IngredientMatcher(
        ifct_path or "data/interim/ifct_final_candidate/ifct_table1_candidate.parquet",
        synonym_path or "data/interim/phase2/ingredient_synonyms.csv",
        household_path or "data/interim/phase2/household_measurements.csv"
    )


def main():
    """Main entry point for batch matching."""
    import argparse
    
    parser = argparse.ArgumentParser(description='IFCT Ingredient Matcher')
    parser.add_argument('--ifct', default='data/interim/ifct_final_candidate/ifct_table1_candidate.parquet')
    parser.add_argument('--synonyms', default='data/interim/phase2/ingredient_synonyms.csv')
    parser.add_argument('--household', default='data/interim/phase2/household_measurements.csv')
    parser.add_argument('--output', default='data/interim/phase3/ifct_match_candidates.parquet')
    parser.add_argument('--batch-size', type=int, default=10000)
    parser.add_argument('--recipe-ids', nargs='+', type=int, help='Specific recipe IDs to process')
    
    args = parser.parse_args()
    
    matcher = create_matcher(args.ifct, args.synonyms, args.household)
    
    if args.recipe_ids:
        result = matcher.match_recipe_ingredients(args.recipe_ids)
    else:
        result = matcher.match_recipe_ingredients()
    
    # Save outputs
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_parquet(args.output)
    result.to_csv(args.output.replace('.parquet', '.csv'), index=False)
    
    print(f"Saved {len(result)} matches to {args.output}")


if __name__ == "__main__":
    main()