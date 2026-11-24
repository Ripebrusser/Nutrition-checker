import pandas as pd
from src.ingredients.ingredient_parser import IngredientParser

norm_df = pd.read_parquet('data/interim/phase2/normalized_ingredients.parquet')
parser = IngredientParser()

# Simulate the EXACT main parsing loop with detailed debugging
parsed_records = []
en_count = 0
raw_count = 0

for i, (_, row) in enumerate(norm_df.iterrows()):
    if i % 50000 == 0:
        print(f'Processing record {i}')
    
    parsed = IngredientParser().parse(row['normalized_ingredient'])
    source_field = 'ingredients_raw' if 'source:ingredients_raw' in row['flags'] else 'ingredients_en'
    
    # Create a minimal record to track
    record = {
        'recipe_id': row['recipe_id'],
        'source_field': 'ingredients_raw' if 'source:ingredients_raw' in row['flags'] else 'ingredients_en',
    }
    
    if source_field == 'ingredients_en':
        en_count += 1
    else:
        raw_count += 1
    
    # Check recipe 1 en records specifically
    if row['recipe_id'] == 1 and source_field == 'ingredients_en':
        print(f'Recipe 1 en record: {row["normalized_ingredient"][:60]}')

print(f'Total processed: {len(norm_df)}')
print(f'Raw count: {raw_count}')
print(f'En count: {en_count}')

# Now test the actual ParsedIngredient creation
print("\n--- Testing ParsedIngredient creation ---")
from src.ingredients.ingredient_parser import ParsedIngredient
from src.ingredients.ingredient_parser import IngredientParser

parser = IngredientParser()
parsed_records = []

for i, (_, row) in enumerate(norm_df.head(20).iterrows()):
    parsed = IngredientParser().parse(row['normalized_ingredient'])
    source_field = 'ingredients_raw' if 'source:ingredients_raw' in row['flags'] else 'ingredients_en'
    
    parsed.recipe_id = row['recipe_id']
    parsed.source_field = source_field
    parsed.original_line = row['source_line']
    parsed.original_ingredient = row['source_ingredient']
    parsed.normalized_ingredient = row['normalized_ingredient']
    if row['flags']:
        parsed.flags.extend(row['flags'].split('; '))
    
    # Check the to_dict output
    d = parsed.to_dict()
    print(f'Record {i}: source_field={d["source_field"]}, recipe_id={d["recipe_id"]}, normalized={d["normalized_ingredient"][:50]}')

print(f'\nTotal test records: 20')