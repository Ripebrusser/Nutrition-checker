"""Stage 2 Candidate Generation Pipeline - Main execution script."""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.matching.ingredient_taxonomy import taxonomy
from src.matching.candidate_generator import CandidateGenerator
from src.matching.matching_rules import MatchingRules
from src.matching.matching_confidence import ConfidenceScorer
from src.matching.provenance import ProvenanceTracker
from src.matching.ingredient_taxonomy import HOUSEHOLD_MEASUREMENTS_RAW, HOUSEHOLD_DB

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_data():
    """Load all required input data."""
    logger.info("Loading input data...")
    
    # Use parsed ingredients which have parsed quantity/unit/preparation and ingredient_name
    parsed_df = pd.read_parquet('data/interim/phase2/parsed_recipe_ingredients.parquet')
    logger.info(f"Loaded {len(parsed_df)} parsed ingredients")
    
    ifct_df = pd.read_parquet('data/interim/ifct_final_candidate/ifct_table1_candidate.parquet')
    logger.info(f"Loaded IFCT: {len(ifct_df)} records")
    
    syn_df = pd.read_csv('data/interim/phase2/ingredient_synonyms.csv')
    logger.info(f"Loaded {len(syn_df)} synonym entries")
    
    hh_df = pd.read_csv('data/interim/phase2/household_measurements.csv')
    logger.info(f"Loaded {len(hh_df)} household measurements")
    
    return parsed_df, ifct_df, syn_df, hh_df


def create_candidate_generator(ifct_df, syn_df, hh_df):
    """Create candidate generator with loaded data."""
    # Build synonym dict
    synonym_dict = {}
    for _, row in syn_df.iterrows():
        key = row['synonym_key'] if 'synonym_key' in row else row['synonym']
        entry = {
            'canonical_name': row['canonical_name'],
            'synonym': row['synonym'],
            'category': row['category'],
            'evidence': row['evidence'],
            'confidence': row['confidence'],
            'excludes': str(row['excludes']).split(';') if pd.notna(row['excludes']) else []
        }
        synonym_dict[key.lower().strip()] = entry
    
    # Build household DB
    household_db = {}
    for _, row in hh_df.iterrows():
        key = (row['ingredient_name'].lower().strip(), row['household_unit'].lower().strip())
        if key not in household_db or row['confidence'] > household_db[key]['confidence']:
            household_db[key] = {
                'mass_g': row['equivalent_mass_g'],
                'source': row['source'],
                'confidence': row['confidence']
            }
    
    return CandidateGenerator(ifct_df, synonym_dict, household_db)


def generate_candidates_batch(generator, parsed_df):
    """Generate candidates for all parsed ingredients."""
    candidates_list = []
    
    for _, row in parsed_df.iterrows():
        # Use ingredient_name for matching (cleaner than normalized_ingredient)
        ingredient_name = row.get('ingredient_name', '')
        if not ingredient_name or pd.isna(ingredient_name):
            ingredient_name = row['normalized_ingredient']
        
        # Normalize the ingredient name for matching
        # Remove quantity/unit remnants that might be in ingredient_name
        matching_text = ingredient_name.strip()
        
        parsed_data = {
            'quantity': row.get('quantity'),
            'unit': row.get('unit'),
            'preparation': row.get('preparation'),
            'size_descriptor': row.get('size_descriptor')
        }
        source_field = row.get('source_field', 'ingredients_raw')
        recipe_id = row['recipe_id']
        original_ingredient = row.get('original_ingredient', row['normalized_ingredient'])
        normalized_ingredient = row['normalized_ingredient']
        source_line = row.get('original_line', '')
        
        # Generate candidates using the generator
        candidates = generator.generate_candidates(
            normalized_ingredient=matching_text,
            parsed_data=parsed_data,
            ingredient_name=ingredient_name,
            source_field=source_field
        )
        
        # Convert candidates to records
        for cand in candidates:
            candidates_list.append({
                'recipe_id': recipe_id,
                'original_ingredient': original_ingredient,
                'normalized_ingredient': normalized_ingredient,
                'matched_ingredient_name': matching_text,
                'source_field': source_field,
                'ifct_food_code': cand.ifct_food_code,
                'ifct_food_name': cand.ifct_food_name,
                'ifct_food_group': cand.ifct_food_group,
                'match_method': cand.match_method,
                'similarity_score': cand.similarity_score,
                'evidence': cand.evidence,
                'food_group_compat': cand.food_group_compat,
                'prep_state_compat': cand.prep_state_compat,
                'taxonomy_category': cand.taxonomy_category,
                'provisional_confidence': cand.provisional_confidence,
                'requires_review': cand.requires_review
            })
    
    return pd.DataFrame(candidates_list)


def main():
    logger.info("="*60)
    logger.info("STAGE 2 - IFCT INGREDIENT CANDIDATE GENERATION")
    logger.info("="*60)
    
    # Load data
    parsed_df, ifct_df, syn_df, hh_df = load_data()
    
    # Create candidate generator
    logger.info("Creating candidate generator...")
    generator = create_candidate_generator(ifct_df, syn_df, hh_df)
    
    # Generate candidates
    logger.info("Generating candidates for all ingredients...")
    candidates_df = generate_candidates_batch(generator, parsed_df)
    logger.info(f"Generated {len(candidates_df)} candidate matches")
    
    # Save outputs
    output_dir = Path("data/interim/phase3")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    candidates_df.to_parquet(output_dir / "ifct_match_candidates.parquet", index=False)
    candidates_df.to_csv(output_dir / "ifct_match_candidates.csv", index=False)
    logger.info(f"Saved match candidates: {len(candidates_df)} records")
    
    # Find unmatched ingredients (ingredients with no candidates)
    # Use matched_ingredient_name for comparison
    matched_names = set(candidates_df['matched_ingredient_name'].unique()) if len(candidates_df) > 0 else set()
    all_names = set(parsed_df['ingredient_name'].dropna().unique())
    unmatched_names = all_names - matched_names
    
    unmatched_df = parsed_df[parsed_df['ingredient_name'].isin(unmatched_names)]
    unmatched_df.to_parquet(output_dir / "unmatched_ingredients.parquet", index=False)
    unmatched_df.to_csv(output_dir / "unmatched_ingredients.csv", index=False)
    logger.info(f"Unmatched ingredients: {len(unmatched_df)} records ({len(unmatched_names)} unique)")
    
    # Household measurements
    hh_rows = []
    for item in HOUSEHOLD_MEASUREMENTS_RAW:
        ingredient, unit, mass, source, confidence, verification = item
        hh_rows.append({
            'ingredient_name': ingredient,
            'household_unit': unit,
            'equivalent_mass_g': mass,
            'source': source,
            'confidence': confidence,
            'verification_status': verification
        })
    pd.DataFrame(hh_rows).to_csv(output_dir / "household_measurements.csv", index=False)
    
    logger.info("Stage 2 complete.")


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    main()