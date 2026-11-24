import pandas as pd
from src.ingredients.ingredient_parser import _has_source_flag

# Load the parsed data
parsed_df = pd.read_parquet('data/interim/phase2/parsed_recipe_ingredients.parquet')

# Add source columns
from src.ingredients.ingredient_parser import _has_source_flag
parsed_df['_is_raw'] = parsed_df['flags'].apply(lambda f: _has_source_flag(f, 'source:ingredients_raw'))
parsed_df['_is_en'] = parsed_df['flags'].apply(lambda f: _has_source_flag(f, 'source:ingredients_en'))

# Check recipe 1
r1 = parsed_df[parsed_df['recipe_id'] == 1]
raw = r1[r1['source_field'] == 'ingredients_raw']
en = r1[r1['source_field'] == 'ingredients_en']

print('Raw normalized_ingredient values:')
for _, r in parsed_df[parsed_df['source_field'] == 'ingredients_raw'].head(10).iterrows():
    print(f'  [{r["recipe_id"]}] {repr(r["normalized_ingredient"])}')
print()
print('En normalized_ingredient values:')
for _, r in parsed_df[parsed_df['source_field'] == 'ingredients_en'].head(10).iterrows():
    print(f'  [{r["recipe_id"]}] {repr(r["normalized_ingredient"])}')
print()

# Check for exact matches between raw and en
raw_norm = set(parsed_df[parsed_df['source_field'] == 'ingredients_raw']['normalized_ingredient'])
en_norm = set(parsed_df[parsed_df['source_field'] == 'ingredients_en']['normalized_ingredient'])

print(f'Raw unique normalized: {len(raw_norm)}')
print(f'En unique normalized: {len(en_norm)}')
print(f'Intersection: {len(raw_norm & en_norm)}')

# Check recipe 1 specifically
r1_raw = set(parsed_df[(parsed_df['recipe_id'] == 1) & (parsed_df['source_field'] == 'ingredients_raw')]['normalized_ingredient'])
r1_en = set(parsed_df[(parsed_df['recipe_id'] == 1) & (parsed_df['source_field'] == 'ingredients_en')]['normalized_ingredient'])
print(f'\nRecipe 1 raw: {len(r1_raw)}')
print(f'Recipe 1 en: {len(r1_en)}')
print(f'Recipe 1 intersection: {len(r1_raw & r1_en)}')
if r1_raw & r1_en:
    for item in r1_raw & r1_en:
        print(f'  Match: {repr(item)}')