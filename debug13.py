import pandas as pd
from src.ingredients.ingredient_parser import IngredientParser

norm_df = pd.read_parquet('data/interim/phase2/normalized_ingredients.parquet')
parser = IngredientParser()

# Simulate the parsing loop for just the first 1000 records to see what happens
test_df = norm_df.head(1000)
parsed_records = []
for _, row in test_df.iterrows():
    parsed = IngredientParser().parse(row['normalized_ingredient'])
    parsed.recipe_id = row['recipe_id']
    parsed.source_field = 'ingredients_raw' if 'source:ingredients_raw' in row['flags'] else 'ingredients_en'
    parsed.original_line = row['source_line']
    parsed.original_ingredient = row['source_ingredient']
    parsed.normalized_ingredient = row['normalized_ingredient']
    if row['flags']:
        parsed.flags.extend(row['flags'].split('; '))
    parsed_records.append(parsed)

# Convert to DataFrame
parsed_data = [p.to_dict() for p in parsed_records]
parsed_df = pd.DataFrame(parsed_data)

print(f'Test parsed records: {len(parsed_df)}')
print(f'Source field distribution:')
print(parsed_df['source_field'].value_counts())
print()

# Check recipe 1 in test parsed data
r1 = parsed_df[parsed_df['recipe_id'] == 1]
print(f'Recipe 1 records: {len(r1)}')
print(f'Source field distribution:')
print(r1['source_field'].value_counts())