"""Stage 2.2: Ingredient Name Disambiguation and Preparation-State Handling Pipeline."""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.matching.name_disambiguation import (
    IngredientNameDisambiguator,
    PreparationState,
    AliasType,
    disambiguate_ingredient_batch
)
from src.matching.candidate_generator import CandidateGenerator
from src.matching.ingredient_taxonomy import HOUSEHOLD_MEASUREMENTS_RAW, HOUSEHOLD_DB

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_data():
    """Load all required input data."""
    logger.info("Loading input data...")
    
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


def generate_candidates_with_disambiguation(generator, parsed_df, disambiguated_df):
    """Generate candidates using disambiguated primary ingredients and aliases."""
    candidates_list = []
    
    # Merge disambiguated info with parsed data
    # We need to match on recipe_id and normalized_ingredient
    merged = parsed_df.merge(
        disambiguated_df[['recipe_id', 'normalized_ingredient', 'primary_ingredient', 
                          'parenthetical_text', 'extracted_aliases', 'preparation_state',
                          'preparation_confidence', 'ambiguity_flags', 'alias_extraction_status',
                          'parentheses_balanced']],
        on=['recipe_id', 'normalized_ingredient'],
        how='left'
    )
    
    for _, row in merged.iterrows():
        # Use primary_ingredient for matching (cleaned, no parentheticals)
        primary = row.get('primary_ingredient', '')
        if not primary or pd.isna(primary):
            primary = row.get('ingredient_name', '')
        if not primary or pd.isna(primary):
            primary = row['normalized_ingredient']
        
        parsed_data = {
            'quantity': row.get('quantity'),
            'unit': row.get('unit'),
            'preparation': row.get('preparation'),
            'size_descriptor': row.get('size_descriptor'),
            'disambiguated_preparation': row.get('preparation_state'),
            'preparation_confidence': row.get('preparation_confidence'),
            'ambiguity_flags': row.get('ambiguity_flags', []),
            'extracted_aliases': row.get('extracted_aliases', []),
        }
        
        ingredient_name = row.get('ingredient_name', primary)
        source_field = row.get('source_field', 'ingredients_raw')
        recipe_id = row['recipe_id']
        original_ingredient = row.get('original_ingredient', row['normalized_ingredient'])
        normalized_ingredient = row['normalized_ingredient']
        source_line = row.get('original_line', '')
        
        # Generate candidates using the primary ingredient
        candidates = generator.generate_candidates(
            normalized_ingredient=primary,
            parsed_data=parsed_data,
            ingredient_name=ingredient_name,
            source_field=source_field
        )
        
        # Filter candidates based on preparation state compatibility
        candidates = filter_candidates_by_preparation(candidates, parsed_data)
        
        # Convert candidates to records
        for cand in candidates:
            candidates_list.append({
                'recipe_id': recipe_id,
                'original_ingredient': original_ingredient,
                'normalized_ingredient': normalized_ingredient,
                'primary_ingredient': primary,
                'parenthetical_text': row.get('parenthetical_text', ''),
                'extracted_aliases': str(row.get('extracted_aliases', [])),
                'preparation_state': row.get('preparation_state', ''),
                'preparation_confidence': row.get('preparation_confidence', 0.0),
                'ambiguity_flags': str(row.get('ambiguity_flags', [])),
                'alias_extraction_status': row.get('alias_extraction_status', ''),
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


def filter_candidates_by_preparation(candidates, parsed_data):
    """Filter or adjust candidates based on preparation state compatibility."""
    prep_state = parsed_data.get('disambiguated_preparation')
    prep_confidence = parsed_data.get('preparation_confidence', 0.0)
    
    if not prep_state or prep_state == 'NOT_SPECIFIED' or prep_state == PreparationState.NOT_SPECIFIED:
        return candidates
    
    # Map preparation state to IFCT compatibility
    # IFCT Table 1 is raw basis - so RAW/FRESH are compatible, others need review
    compatible_states = {PreparationState.RAW, PreparationState.FRESH}
    incompatible_states = {
        PreparationState.COOKED, PreparationState.BOILED, PreparationState.FRIED,
        PreparationState.ROASTED, PreparationState.DRIED, PreparationState.POWDERED,
        PreparationState.GROUND, PreparationState.FERMENTED, PreparationState.PICKLED
    }
    
    for cand in candidates:
        ifct_name = cand.ifct_food_name.lower()
        
        # Check if IFCT entry has preparation indicator
        ifct_is_raw = any(w in ifct_name for w in ['raw', 'fresh'])
        ifct_is_processed = any(w in ifct_name for w in ['cooked', 'boiled', 'fried', 'roasted', 'dried', 'powder', 'ground'])
        
        if prep_state in compatible_states:
            # Recipe wants raw/fresh - IFCT raw entries are compatible
            if ifct_is_raw:
                cand.prep_state_compat = max(cand.prep_state_compat, 1.0)
            elif ifct_is_processed:
                cand.prep_state_compat = min(cand.prep_state_compat, 0.3)
                cand.requires_review = True
                if 'preparation_state' not in str(cand.evidence):
                    cand.evidence['prep_state_warning'] = f'Recipe specifies {prep_state.value}, IFCT entry may be processed'
        elif prep_state in incompatible_states:
            # Recipe specifies preparation - IFCT raw entries may not match
            if ifct_is_raw:
                cand.prep_state_compat = min(cand.prep_state_compat, 0.4)
                cand.requires_review = True
                if 'preparation_state' not in str(cand.evidence):
                    cand.evidence['prep_state_warning'] = f'Recipe specifies {prep_state.value}, IFCT entry is raw basis'
            elif ifct_is_processed:
                cand.prep_state_compat = max(cand.prep_state_compat, 0.7)
    
    return candidates


def main():
    logger.info("="*60)
    logger.info("STAGE 2.2 - INGREDIENT NAME DISAMBIGUATION & PREP-STATE HANDLING")
    logger.info("="*60)
    
    # Load data
    parsed_df, ifct_df, syn_df, hh_df = load_data()
    
    # Disambiguate ingredient names
    logger.info("Disambiguating ingredient names...")
    disambiguated_df = disambiguate_ingredient_batch(parsed_df)
    
    # Save disambiguated output
    output_dir = Path("data/interim/phase3/stage2_2")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    disambiguated_df.to_parquet(output_dir / "disambiguated_ingredients.parquet", index=False)
    disambiguated_df.to_csv(output_dir / "disambiguated_ingredients.csv", index=False)
    logger.info(f"Saved disambiguated ingredients: {len(disambiguated_df)} records")
    
    # Create candidate generator
    logger.info("Creating candidate generator...")
    generator = create_candidate_generator(ifct_df, syn_df, hh_df)
    
    # Generate candidates using disambiguated primary ingredients
    logger.info("Generating candidates with disambiguation...")
    candidates_df = generate_candidates_with_disambiguation(generator, parsed_df, disambiguated_df)
    logger.info(f"Generated {len(candidates_df)} candidate matches")
    
    # Save candidates
    candidates_df.to_parquet(output_dir / "ifct_match_candidates.parquet", index=False)
    candidates_df.to_csv(output_dir / "ifct_match_candidates.csv", index=False)
    logger.info(f"Saved match candidates: {len(candidates_df)} records")
    
    # Find unmatched ingredients
    matched_names = set(candidates_df['primary_ingredient'].unique()) if len(candidates_df) > 0 else set()
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
    
    logger.info("Stage 2.2 complete.")


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    main()