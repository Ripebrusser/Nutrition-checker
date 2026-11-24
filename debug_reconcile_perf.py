import pandas as pd
import time

# Load parsed data
norm_df = pd.read_parquet('data/interim/phase2/normalized_ingredients.parquet')
print(f"Loaded {len(norm_df)} records")

# Test just the parsing part
from src.ingredients.ingredient_parser import IngredientParser
parser = IngredientParser()

# Test with first 1000 records
test_df = pd.read_parquet('data/interim/phase2/normalized_ingredients.parquet').head(1000)
print(f"Testing with {len(test_df)} records")

start = time.time()
parsed_records = []
for _, row in test_df.iterrows():
    parsed = parser.parse(row['normalized_ingredient'])
    parsed.recipe_id = row['recipe_id']
    parsed.source_field = 'ingredients_raw' if 'source:ingredients_raw' in row['flags'] else 'ingredients_en'
    parsed.original_line = row['source_line']
    parsed.original_ingredient = row['source_ingredient']
    parsed.normalized_ingredient = row['normalized_ingredient']
    if row['flags']:
        parsed.flags.extend(row['flags'].split('; '))
    parsed_records.append(parsed)

print(f"Parsed {len(parsed_records)} records in {time.time() - start:.2f}s")

parsed_data = [p.to_dict() for p in parsed_records]
parsed_df = pd.DataFrame(parsed_data)
print(f"Parsed DF shape: {parsed_df.shape}")

# Test reconciliation with small sample
from src.ingredients.ingredient_parser import reconcile_sources
start = time.time()
canonical_df = reconcile_sources(parsed_df)
print(f"Reconciliation took {time.time() - start:.2f}s")
print(f"Canonical shape: {canonical_df.shape}")