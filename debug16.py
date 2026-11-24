import pandas as pd
from src.ingredients.ingredient_parser import IngredientParser

norm_df = pd.read_parquet('data/interim/phase2/normalized_ingredients.parquet')
parser = IngredientParser()

# Replicate the EXACT main parsing loop with debugging
parsed_records = []
en_count = 0
raw_count = 0

for i, (_, row) in enumerate(norm_df.iterrows()):
    if i % 50000 == 0:
        print(f'Processing record {i}')
    
    parsed = parser.parse(row['normalized_ingredient'])
    source_field = 'ingredients_raw' if 'source:ingredients_raw' in row['flags'] else 'ingredients_en'
    
    # Create a simple dict instead of ParsedIngredient object to isolate the issue
    record = {
        'recipe_id': row['recipe_id'],
        'source_field': source_field,
        'original_line': row['source_line'],
        'original_ingredient': row['source_ingredient'],
        'normalized_ingredient': row['normalized_ingredient'],
        'flags': row['flags'].split('; ') if row['flags'] else [],
    }
    
    if source_field == 'ingredients_en':
        en_count += 1
    else:
        raw_count += 1
    
    if i < 20:
        print(f'Record {i}: source_field={source_field}, recipe_id={row["recipe_id"]}')

print(f'Total processed: {i+1}')
print(f'Raw count: {raw_count}')
print(f'En count: {en_count}')

# Now test creating the actual ParsedIngredient objects
from src.ingredients.ingredient_parser import ParsedIngredient
from datetime import datetime

parsed_records = []
for i, (_, row) in enumerate(norm_df.iterrows()):
    parsed = __import__('src.ingredients.ingredient_parser', fromlist=['IngredientParser']).IngredientParser().parse(row['normalized_ingredient'])
    source_field = 'ingredients_raw' if 'source:ingredients_raw' in row['flags'] else 'ingredients_en'
    
    parsed.recipe_id = row['recipe_id']
    parsed.source_field = source_field
    parsed.original_line = row['source_line']
    parsed.original_ingredient = row['source_ingredient']
    parsed.normalized_ingredient = row['normalized_ingredient']
    if row['flags']:
        parsed.flags.extend(row['flags'].split('; '))
    
    # Convert to dict immediately to see if there's an issue
    d = parsed.to_dict()
    parsed_records.append(d)
    
    if i < 20:
        print(f'Record {i}: source_field={d["source_field"]}, recipe_id={d["recipe_id"]}')

print(f'\nTotal parsed records: {len(parsed_records)}')
print(f'En count: {sum(1 for r in parsed_records if r["source_field"] == "ingredients_en")}')
print(f'Raw count: {sum(1 for r in parsed_records if r["source_field"] == "ingredients_raw")}')

# Convert to DataFrame
parsed_df = pd.DataFrame(parsed_records)
print(f'DataFrame shape: {parsed_df.shape}')
print(f'DataFrame en count: {(parsed_df["source_field"] == "ingredients_en").sum()}')
print(f'DataFrame raw count: {(parsed_df["source_field"] == "ingredients_raw").sum()}')