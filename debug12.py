import pandas as pd
from src.ingredients.ingredient_parser import IngredientParser

norm_df = pd.read_parquet('data/interim/phase2/normalized_ingredients.parquet')
parser = IngredientParser()

# Test parsing recipe 1 en records
en_r1 = norm_df[(norm_df['recipe_id'] == 1) & (norm_df['flags'].str.contains('source:ingredients_en'))]

print(f'Recipe 1 en records: {len(en_r1)}')
for _, row in en_r1.iterrows():
    text = row['normalized_ingredient']
    try:
        parsed = IngredientParser().parse(text)
        source_field = 'ingredients_raw' if 'source:ingredients_raw' in row['flags'] else 'ingredients_en'
        print(f'OK: {text[:60]} -> source_field={source_field}, ingredient_name={parsed.ingredient_name[:40]}')
    except Exception as e:
        print(f'ERROR: {text[:60]} -> {e}')
        import traceback
        traceback.print_exc()

print()
print('Testing raw records for comparison:')
raw_r1 = norm_df[(norm_df['recipe_id'] == 1) & (norm_df['flags'].str.contains('source:ingredients_raw'))]
for _, row in raw_r1.head(3).iterrows():
    text = row['normalized_ingredient']
    try:
        parsed = IngredientParser().parse(text)
        source_field = 'ingredients_raw' if 'source:ingredients_raw' in row['flags'] else 'ingredients_en'
        print(f'OK: {text[:60]} -> source_field={source_field}')
    except Exception as e:
        print(f'ERROR: {text[:60]} -> {e}')