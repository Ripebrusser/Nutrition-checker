"""Stage 2.3: Auto-Acceptance Safety Corrections Pipeline."""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.matching.name_disambiguation import disambiguate_ingredient_batch
from src.matching.candidate_generator import CandidateGenerator
from src.matching.ingredient_taxonomy import HOUSEHOLD_MEASUREMENTS_RAW

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


def generate_candidates_for_row(generator, row, disambiguated_row):
    """Generate candidates for a single row."""
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
    
    # Convert candidates to records
    candidate_records = []
    for cand in candidates:
        candidate_records.append({
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
            'requires_review': cand.requires_review,
            'acceptance_evidence': cand.evidence.get('acceptance_decision', {})
        })
    
    return candidate_records


def apply_global_multi_code_check(candidates_df):
    """Apply global multi-code ambiguity check ONLY on candidates that would be auto-accepted."""
    logger.info("Applying global multi-code ambiguity check on auto-accept candidates...")
    
    # First, identify candidates that would be auto-accepted based on other criteria
    # (prep state, match method, provenance, etc.)
    # We simulate the acceptance gate but only for multi-code check purposes
    
    # For multi-code ambiguity, we only care about primary ingredients that have
    # multiple IFCT codes among candidates that pass all OTHER criteria
    # (prep state, match method, provenance, prep_compat threshold)
    
    # First, identify candidates that pass all checks EXCEPT multi-code
    def would_auto_accept_except_multi(row):
        """Check if candidate would be auto-accepted ignoring multi-code ambiguity."""
        # Check match method
        if row['match_method'] not in {'EXACT', 'SYNONYM'}:
            return False
        
        # Check prep state
        prep_state = row['preparation_state']
        if prep_state not in {'RAW', 'FRESH'}:
            return False
        
        # Check prep_state_compat
        if row.get('prep_state_compat', 0) < 0.8:
            return False
        
        # Check provenance
        ev = row.get('evidence', {})
        if not ev or not isinstance(ev, dict) or len(ev) == 0:
            return False
        
        # Check required fields
        required = ['ifct_food_code', 'ifct_food_name', 'ifct_food_group', 'match_method', 'similarity_score']
        for field in ['ifct_food_code', 'ifct_food_name', 'ifct_food_group', 'match_method', 'similarity_score']:
            if pd.isna(row.get(field)):
                return False
        
        # Method-specific
        if row['match_method'] == 'SYNONYM':
            ev = row.get('evidence', {})
            if isinstance(ev, dict):
                match_source = ev.get('acceptance_decision', {}).get('evidence', {}).get('match_source', ev.get('match_source', ''))
                if match_source == 'token_match':
                    return False
                conf = ev.get('confidence', ev.get('acceptance_decision', {}).get('evidence', {}).get('confidence', 1.0))
                if conf < 0.95:
                    return False
        
        # NOT_SPECIFIED check
        prep_state = row['preparation_state']
        if prep_state not in {'RAW', 'FRESH'}:
            return False
        
        return True
    
    # Identify candidates that would be auto-accepted
    would_accept = candidates_df.apply(would_auto_accept_except_multi, axis=1)
    potential_auto = candidates_df[would_accept].copy()
    
    logger.info(f"Candidates passing all checks except multi-code: {len(potential_auto)}")
    
    # Check multi-code ambiguity among these potential auto-accepts
    if len(potential_auto) > 0:
        multi_ifct = potential_auto.groupby('primary_ingredient')['ifct_food_code'].nunique()
        ambiguous_ingredients = set(multi_ifct[multi_ifct > 1].index)
        
        logger.info(f"Found {len(ambiguous_ingredients)} primary ingredients with multi-code ambiguity among auto-accept candidates")
        
        # Flag all candidates (not just potential auto) for these ingredients
        mask = candidates_df['primary_ingredient'].isin(ambiguous_ingredients)
        candidates_df.loc[mask, 'requires_review'] = True
        
        # Update evidence
        ingredient_to_codes = candidates_df.groupby('primary_ingredient')['ifct_food_code'].apply(set).to_dict()
        
        def update_row(row):
            if row['primary_ingredient'] in ambiguous_ingredients:
                row['requires_review'] = True
                ev = row['evidence']
                if isinstance(ev, dict):
                    if 'acceptance_decision' not in ev:
                        ev['acceptance_decision'] = {}
                    acc = ev['acceptance_decision']
                    if 'rejection_reasons' not in acc:
                        acc['rejection_reasons'] = []
                    if 'MULTIPLE_IFCT_CODE_AMBIGUITY' not in acc.get('rejection_reasons', []):
                        acc['rejection_reasons'].append('MULTIPLE_IFCT_CODE_AMBIGUITY')
                    ingredient = row['primary_ingredient']
                    if ingredient in ingredient_to_codes:
                        codes = ingredient_to_codes.get(ingredient, set())
                        ev = row['evidence']
                        if isinstance(ev, dict):
                            if 'acceptance_decision' not in ev:
                                ev['acceptance_decision'] = {}
                            ev['acceptance_decision']['competing_codes'] = sorted(list(ingredient_to_codes.get(ingredient, set())))
            return row
        
        candidates_df = candidates_df.apply(lambda r: update_row(r), axis=1)
    
    return candidates_df


def main():
    logger.info("="*60)
    logger.info("STAGE 2.3 - AUTO-ACCEPTANCE SAFETY CORRECTIONS")
    logger.info("="*60)
    
    # Load data
    parsed_df, ifct_df, syn_df, hh_df = load_data()
    
    # Disambiguate ingredient names
    logger.info("Disambiguating ingredient names...")
    disambiguated_df = disambiguate_ingredient_batch(parsed_df)
    
    # Save disambiguated output
    output_dir = Path("data/interim/phase3/stage2_3")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    disambiguated_df.to_parquet(output_dir / "disambiguated_ingredients.parquet", index=False)
    disambiguated_df.to_csv(output_dir / "disambiguated_ingredients.csv", index=False)
    logger.info(f"Saved disambiguated ingredients: {len(disambiguated_df)} records")
    
    # Create candidate generator
    logger.info("Creating candidate generator...")
    generator = create_candidate_generator(ifct_df, syn_df, hh_df)
    
    # Merge disambiguated info with parsed data
    logger.info("Merging disambiguation data...")
    merged = parsed_df.merge(
        disambiguated_df[['recipe_id', 'normalized_ingredient', 'primary_ingredient', 
                          'parenthetical_text', 'extracted_aliases', 'preparation_state',
                          'preparation_confidence', 'ambiguity_flags', 'alias_extraction_status',
                          'parentheses_balanced']],
        on=['recipe_id', 'normalized_ingredient'],
        how='left'
    )
    
    # Generate candidates for all rows (first pass)
    logger.info("Generating candidates (first pass)...")
    all_candidate_records = []
    
    for _, row in merged.iterrows():
        # Get corresponding disambiguated row
        disamb_row = disambiguated_df[
            (disambiguated_df['recipe_id'] == row['recipe_id']) & 
            (disambiguated_df['normalized_ingredient'] == row['normalized_ingredient'])
        ]
        disamb_row = disamb_row.iloc[0] if len(disamb_row) > 0 else None
        
        candidate_records = generate_candidates_for_row(generator, row, disamb_row)
        all_candidate_records.extend(candidate_records)
    
    logger.info(f"Generated {len(all_candidate_records)} candidate records (first pass)")
    
    # Convert to DataFrame
    candidates_df = pd.DataFrame(all_candidate_records)
    logger.info(f"First pass complete: {len(candidates_df)} candidate records")
    
    # Global multi-code ambiguity check
    candidates_df = apply_global_multi_code_check(candidates_df)
    
    # Save candidates
    output_dir = Path("data/interim/phase3/stage2_3")
    output_dir.mkdir(parents=True, exist_ok=True)
    
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
    
    # Log acceptance stats
    auto_accept = candidates_df[candidates_df['requires_review'] == False]
    logger.info(f"Auto-accepted: {len(auto_accept)} ({len(auto_accept)/len(candidates_df)*100:.1f}%)")
    logger.info(f"Requires review: {len(candidates_df) - len(auto_accept)}")
    
    by_method = candidates_df[candidates_df['requires_review'] == False]['match_method'].value_counts()
    logger.info(f"Auto-accept by method: {by_method.to_dict()}")
    
    by_prep = candidates_df[candidates_df['requires_review'] == False]['preparation_state'].value_counts()
    logger.info(f"Auto-accept by preparation state: {by_prep.to_dict()}")
    
    logger.info("Stage 2.3 complete.")


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    main()