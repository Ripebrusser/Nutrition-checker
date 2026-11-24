import pandas as pd
from src.matching.candidate_generator import CandidateGenerator

# Load data
ifct_df = pd.read_parquet('data/interim/ifct_final_candidate/ifct_table1_candidate.parquet')
syn_df = pd.read_csv('data/interim/phase2/ingredient_synonyms.csv')
hh_df = pd.read_csv('data/interim/phase2/household_measurements.csv')

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

# Create generator
gen = CandidateGenerator(ifct_df, synonym_dict, household_db)

# Test some synonyms
test_synonyms = ['jeera', 'haldi', 'toor dal', 'besan', 'atta', 'maida', 'suji', 'rava', 'kabuli chana', 'masoor dal']

for syn in test_synonyms:
    cands = gen.generate_candidates(
        normalized_ingredient=syn,
        parsed_data={},
        ingredient_name=syn,
        source_field='ingredients_raw'
    )
    print(f"\n{syn}: {len(cands)} candidates")
    for c in cands[:3]:
        print(f"  {c.ifct_food_code} | {c.ifct_food_name} | {c.match_method} | {c.similarity_score:.3f} | {c.provisional_confidence} | review={c.requires_review}")
        if c.evidence:
            print(f"    evidence: {c.evidence}")