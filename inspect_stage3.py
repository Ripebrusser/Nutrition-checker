import pandas as pd

# Inspect Stage 2.3 outputs
cands = pd.read_parquet('data/interim/phase3/stage2_3/ifct_match_candidates.parquet')
disamb = pd.read_parquet('data/interim/phase3/stage2_3/disambiguated_ingredients.parquet')
unmatched = pd.read_parquet('data/interim/phase3/stage2_3/unmatched_ingredients.parquet')

print('=== CANDIDATES ===')
print(f'Records: {len(cands)}')
print(f'Columns: {list(cands.columns)}')
print()

print('=== DISAMBIGUATED ===')
print(f'Records: {len(disamb)}')
print(f'Columns: {list(disamb.columns)}')
print()

print('=== UNMATCHED ===')
print(f'Records: {len(unmatched)}')
print(f'Columns: {list(unmatched.columns)}')
print()

# Unique counts
print('=== UNIQUE COUNTS ===')
print(f'Unique primary_ingredient: {cands["primary_ingredient"].nunique()}')
print(f'Unique ifct_food_code: {cands["ifct_food_code"].nunique()}')
print(f'Unique recipe_id: {cands["recipe_id"].nunique()}')
print(f'Match methods: {cands["match_method"].value_counts().to_dict()}')
print(f'Prep states: {cands["preparation_state"].value_counts().head(10).to_dict()}')
print(f'Requires review: {cands["requires_review"].value_counts().to_dict()}')

# Review units
print()
print('=== REVIEW UNITS ===')
review_units = cands.groupby(['primary_ingredient', 'ifct_food_code']).agg(
    recipe_count=('recipe_id', 'nunique'),
    candidate_count=('recipe_id', 'count'),
    match_method=('match_method', 'first'),
    prep_state=('preparation_state', 'first'),
    similarity=('similarity_score', 'max')
).reset_index()
print(f'Unique (primary_ingredient, ifct_food_code) pairs: {len(review_units)}')
print()
print('By match method:')
print(review_units['match_method'].value_counts().to_dict())
print()
print('By prep state:')
print(review_units['prep_state'].value_counts().head(10).to_dict())
print()
print('Requires review:')
print(review_units.groupby('match_method').size().to_dict())

# Look at auto-accepted
auto = cands[cands['requires_review'] == False]
print(f'\nAuto-accepted: {len(auto)}')
if len(auto) > 0:
    print(auto[['primary_ingredient', 'ifct_food_code', 'match_method', 'preparation_state', 'similarity_score']].to_string())