import pandas as pd

# Check outputs
cands = pd.read_parquet('data/interim/phase3/ifct_match_candidates.parquet')
print('Match candidates:')
print(f'  Records: {len(cands)}')
print(f'  Columns: {list(cands.columns)}')
print(f'  Unique recipes: {cands["recipe_id"].nunique()}')
print(f'  Unique ingredients: {cands["normalized_ingredient"].nunique()}')
print(f'  Match methods: {cands["match_method"].value_counts().to_dict()}')
print(f'  Confidence levels: {cands["provisional_confidence"].value_counts().to_dict()}')
print(f'  IFCT food groups: {cands["ifct_food_group"].nunique()}')
print()

unmatched = pd.read_parquet('data/interim/phase3/unmatched_ingredients.parquet')
print('Unmatched ingredients:')
print(f'  Records: {len(unmatched)}')
print(f'  Unique: {unmatched["normalized_ingredient"].nunique()}')
print()

# Check household measurements
hh = pd.read_csv('data/interim/phase3/household_measurements.csv')
print('Household measurements:')
print(f'  Records: {len(hh)}')