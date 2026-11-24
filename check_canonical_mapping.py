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

# Test canonical names that don't match IFCT directly
problem_canonicals = [
    'pigeon pea',
    'green gram (split)',
    'green gram (whole)',
    'green gram (sprouted)',
    'black gram (split)',
    'black gram (whole)',
    'bengal gram (split)',
    'bengal gram (whole)',
    'chickpea (kabuli)',
    'chickpea (desi)',
    'red lentil (split)',
    'red lentil (whole)',
    'horse gram',
    'moth bean',
    'rice (raw)',
    'rice (cooked)',
    'rice (parboiled)',
    'basmati rice',
    'sona masuri rice',
    'wheat flour (whole)',
    'wheat flour (refined)',
    'semolina (coarse)',
    'semolina (fine)',
    'finger millet',
    'pearl millet',
    'sorghum',
    'foxtail millet',
    'little millet',
    'barnyard millet',
    'kodo millet',
]

print("Best token matches for problematic canonical names:")
for canon in problem_canonicals:
    canon_norm = gen._normalize_text(canon)
    canon_tokens = set(gen._tokenize(canon_norm))
    
    best_match = None
    best_score = 0.0
    best_name = ""
    
    for food_code, food_tokens in gen.ifct_token_sets.items():
        if not food_tokens:
            continue
        intersection = len(canon_tokens & food_tokens)
        union = len(canon_tokens | food_tokens)
        if union > 0:
            jaccard = intersection / union
            if jaccard > best_score:
                best_score = jaccard
                best_match = food_code
                best_name = gen.ifct_lookup[food_code]['food_name']
    
    if best_score >= 0.3:
        print(f"  {canon} -> {best_match}: {best_name} (score: {best_score:.3f})")
    else:
        print(f"  {canon} -> NO GOOD MATCH (best: {best_score:.3f})")