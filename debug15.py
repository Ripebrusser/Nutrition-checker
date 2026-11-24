import pandas as pd
from src.ingredients.ingredient_parser import IngredientParser

norm_df = pd.read_parquet('data/interim/phase2/normalized_ingredients.parquet')
parser = IngredientParser()

# Simulate the EXACT main parsing loop
parsed_records = []
for i, (_, row) in enumerate(norm_df.iterrows()):
    if i % 50000 == 0:
        print(f'Processing record {i}')
    
    parsed = parser.parse(row['normalized_ingredient'])
    source_field = 'ingredients_raw' if 'source:ingredients_raw' in row['flags'] else 'ingredients_en'
    
    # We're not actually creating the ParsedIngredient object here, just counting
    if i < 20:
        source_field = 'ingredients_raw' if 'source:ingredients_raw' in row['flags'] else 'ingredients_en'
        if i < 20:
            print(f'Record {i}: source_field={source_field}, recipe_id={row["recipe_id"]}')

print('Done')