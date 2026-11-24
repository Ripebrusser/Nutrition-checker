import pandas as pd
from src.ingredients.ingredient_parser import IngredientParser

norm_df = pd.read_parquet('data/interim/phase2/normalized_ingredients.parquet')
parser = IngredientParser()

# Simulate the FULL parsing loop with some debugging
print(f'Total normalized records: {len(norm_df)}')

en_count = 0
raw_count = 0
en_recipe1_count = 0
raw_recipe1_count = 0

for i, (_, row) in enumerate(norm_df.iterrows()):
    if i % 50000 == 0:
        print(f'Processing record {i}')
    
    parsed = IngredientParser().parse(row['normalized_ingredient'])
    source_field = 'ingredients_raw' if 'source:ingredients_raw' in row['flags'] else 'ingredients_en'
    
    if source_field == 'ingredients_en':
        en_count += 1
        if row['recipe_id'] == 1:
            en_recipe1_count += 1
    else:
        raw_count += 1
        if row['recipe_id'] == 1:
            raw_recipe1_count += 1

print(f'Total processed: {i+1}')
print(f'Raw count: {raw_count}')
print(f'En count: {en_count}')
print(f'Recipe 1 raw: {raw_recipe1_count}')
print(f'Recipe 1 en: {en_recipe1_count}')