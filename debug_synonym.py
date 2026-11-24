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

# Test some known synonyms
test_ingredients = ['toor dal', 'jeera', 'haldi', 'onion', 'garlic', 'tomato', 'rice', 'dal', 'cumin', 'turmeric']

for ing in test_ingredients:
    cands = gen.generate_candidates(
        normalized_ingredient=ing,
        parsed_data={},
        ingredient_name=ing,
        source_field='ingredients_raw'
    )
    print(f"\n{ing}: {len(cands)} candidates")
    for c in cands[:3]:
        print(f"  {c.ifct_food_code} | {c.ifct_food_name} | {c.match_method} | {c.similarity_score:.3f} | {c.provisional_confidence}")

# Check synonym lookup
print("\n\nSynonym lookup keys (sample):")
count = 0
for k in gen.synonym_lookup:
    if count < 20:
        print(f"  {k}: {gen.synonym_lookup[k]}")
        count += 1
    else:
        break

# Check exact lookup
print("\n\nExact lookup keys (sample):")
count = 0
for k in gen.exact_lookup:
    if count < 20:
        print(f"  {k}: {gen.exact_lookup[k]}")
        count += 1
    else:
        break

# Check a specific example - toor dal
print("\n\nTesting 'toor dal':")
norm_toor = gen._normalize_text('toor dal')
print(f"  Normalized: '{norm_toor}'")
print(f"  In exact_lookup: {norm_toor in gen.exact_lookup}")
print(f"  In synonym_lookup: {norm_toor in gen.synonym_lookup}")
print(f"  Synonym dict has: {'toor dal' in synonym_dict}")

# Check canonical names in IFCT
print("\n\nIFCT foods containing 'pigeon':")
for code, row in gen.ifct_lookup.items():
    if 'pigeon' in row['food_name'].lower() or 'toor' in row['food_name'].lower():
        print(f"  {code}: {row['food_name']}")

print("\n\nIFCT foods containing 'cumin':")
for code, row in gen.ifct_lookup.items():
    if 'cumin' in row['food_name'].lower():
        print(f"  {code}: {row['food_name']}")