import pandas as pd

# Load Stage 2.3 data
cands = pd.read_parquet('data/interim/phase3/stage2_3/ifct_match_candidates.parquet')
disamb = pd.read_parquet('data/interim/phase3/stage2_3/disambiguated_ingredients.parquet')

print('=== STAGE 2.3 DATA VERIFICATION ===')
print(f'Total candidates: {len(cands)}')
print(f'Total disambiguated: {len(disamb)}')
print(f'Unique recipes: {cands["recipe_id"].nunique()}')
print(f'Unique primary_ingredient: {cands["primary_ingredient"].nunique()}')
print(f'Unique ifct_food_code: {cands["ifct_food_code"].nunique()}')

# Check review units count
review_units = cands.groupby(['primary_ingredient', 'ifct_food_code']).agg(
    recipe_count=('recipe_id', 'nunique'),
    candidate_count=('recipe_id', 'count'),
    match_method=('match_method', 'first'),
    prep_state=('preparation_state', 'first'),
    similarity=('similarity_score', 'max')
).reset_index()
print(f'Unique (primary_ingredient, ifct_food_code) pairs: {len(review_units)}')

# Check auto-accepted
auto = cands[cands['requires_review'] == False]
print(f'Auto-accepted: {len(auto)}')
print(f'  Methods: {auto["match_method"].value_counts().to_dict()}')
print(f'  Prep states: {auto["preparation_state"].value_counts().to_dict()}')

# Check review units by match method
ru_method = review_units.groupby('match_method').size()
print(f'Review units by method: {ru_method.to_dict()}')

# Check by prep state
ru_prep = review_units.groupby('prep_state').size()
print(f'Review units by prep: {ru_prep.to_dict()}')

# Check multi-code ambiguity
multi = review_units.groupby('primary_ingredient')['ifct_food_code'].nunique()
multi_count = (multi > 1).sum()
print(f'Primary ingredients with multiple IFCT codes: {multi_count}')

# Check how many unique primary ingredients
print(f'Unique primary ingredients: {review_units["primary_ingredient"].nunique()}')

# Check auto-accepted review units
auto_ru = review_units.merge(auto[['primary_ingredient', 'ifct_food_code']].drop_duplicates(), 
                              on=['primary_ingredient', 'ifct_food_code'])
print(f'Auto-accepted review units: {len(auto_ru)}')

# Check 4 auto-accepted candidates details
auto_detail = auto[['primary_ingredient', 'ifct_food_code', 'match_method', 'preparation_state', 'similarity_score']].drop_duplicates()
print('Auto-accepted unique pairs:')
print(auto_detail.to_string())