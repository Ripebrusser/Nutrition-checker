import pandas as pd
from src.ingredients.ingredient_parser import IngredientParser

norm_df = pd.read_parquet('data/interim/phase2/normalized_ingredients.parquet')
parser = IngredientParser()

# Test the actual main loop logic for recipe 1 en records
en_r1 = norm_df[(norm_df['recipe_id'] == 1) & (norm_df['flags'].str.contains('source:ingredients_en'))]
print(f'Recipe 1 en records in normalized: {len(en_r1)}')

# Simulate the exact main loop for recipe 1 en records
en_r1 = norm_df[(norm_df['recipe_id'] == 1) & (norm_df['flags'].str.contains('source:ingredients_en'))]
parsed_records = []

for _, row in en_r1.iterrows():
    parsed = IngredientParser().parse(row['normalized_ingredient'])
    source_field = 'ingredients_raw' if 'source:ingredients_raw' in row['flags'] else 'ingredients_en'
    print(f'Source field assigned: {source_field}')
    
    # Create a minimal record like the main loop does
    from src.ingredients.ingredient_parser import ParsedIngredient
    parsed = IngredientParser().parse(row['normalized_ingredient'])
    parsed.recipe_id = row['recipe_id']
    parsed.source_field = source_field
    parsed.original_line = row['source_line']
    parsed.original_ingredient = row['source_ingredient']
    parsed.normalized_ingredient = row['normalized_ingredient']
    if row['flags']:
        parsed.flags.extend(row['flags'].split('; '))
    
    # Check the to_dict output
    d = parsed.to_dict()
    print(f'to_dict source_field: {d["source_field"]}')
    print(f'to_dict normalized_ingredient: {d["normalized_ingredient"][:60]}')
    print(f'to_dict flags: {d["flags"]}')
    print()

print('All en records for recipe 1 parsed successfully')