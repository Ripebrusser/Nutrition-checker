import pandas as pd
from src.ingredients.ingredient_parser import _has_source_flag

# Load parsed data
parsed_df = pd.read_parquet('data/interim/phase2/parsed_recipe_ingredients.parquet')

# Add source columns
parsed_df['_is_raw'] = parsed_df['flags'].apply(lambda f: _has_source_flag(f, 'source:ingredients_raw'))
parsed_df['_is_en'] = parsed_df['flags'].apply(lambda f: _has_source_flag(f, 'source:ingredients_en'))

# Check recipe 1 groups
r1 = parsed_df[parsed_df['recipe_id'] == 1]
print('Recipe 1 records:', len(r1))
print('Raw:', (r1['source_field'] == 'ingredients_raw').sum())
print('En:', (r1['source_field'] == 'ingredients_en').sum())

# Group by normalized_ingredient
grouped = r1.groupby('normalized_ingredient').agg(
    has_raw=('_is_raw', 'any'),
    has_en=('_is_en', 'any'),
    count=('recipe_id', 'count')
).reset_index()

print(f'\nGroups for recipe 1: {len(grouped)}')
print('Groups with both raw and en:')
both = grouped[(grouped['has_raw'] == True) & (grouped['has_en'] == True)]
print(f'  Count: {len(both)}')
for _, row in both.iterrows():
    print(f'  {row["normalized_ingredient"][:60]}: raw={row["has_raw"]}, en={row["has_en"]}')

print('\nRaw only groups:')
raw_only = grouped[(grouped['has_raw'] == True) & (grouped['has_en'] == False)]
print(f'  Count: {len(raw_only)}')
for _, row in raw_only.head(10).iterrows():
    print(f'  {row["normalized_ingredient"][:60]}')

print('\nEn only groups:')
en_only = grouped[(grouped['has_raw'] == False) & (grouped['has_en'] == True)]
print(f'  Count: {len(en_only)}')
for _, row in en_only.head(10).iterrows():
    print(f'  {row["normalized_ingredient"][:60]}')