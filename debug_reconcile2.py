import pandas as pd
import sys
sys.path.insert(0, 'src/ingredients')
from ingredient_parser import IngredientParser

# Load and parse a small sample
norm_df = pd.read_parquet('data/interim/phase2/normalized_ingredients.parquet')
sample = norm_df.head(100)

parser = IngredientParser()
parsed_records = []

for _, row in sample.iterrows():
    parsed = parser.parse(row['normalized_ingredient'])
    parsed.recipe_id = row['recipe_id']
    parsed.source_field = 'ingredients_raw' if 'source:ingredients_raw' in row['flags'] else 'ingredients_en'
    parsed.original_line = row['source_line']
    parsed.original_ingredient = row['source_ingredient']
    parsed.normalized_ingredient = row['normalized_ingredient']
    if row['flags']:
        parsed.flags.extend(row['flags'].split('; '))
    parsed_records.append(parsed)

print(f"Parsed {len(parsed_records)} records")

# Convert to DataFrame
parsed_data = [p.to_dict() for p in parsed_records]
parsed_df = pd.DataFrame(parsed_data)
print(f"Parsed DF shape: {parsed_df.shape}")
print(f"Columns: {list(parsed_df.columns)}")
print(f"Recipe IDs: {parsed_df['recipe_id'].unique()[:5]}")
print(f"Source fields: {parsed_df['source_field'].unique()}")
print(f"Flags sample: {parsed_df['flags'].iloc[0] if len(parsed_df) > 0 else 'empty'}")

# Test reconciliation manually
recipe_id = 1
recipe_data = parsed_df[parsed_df['recipe_id'] == recipe_id].copy()
print(f"\nRecipe {recipe_id}: {len(recipe_data)} records")

raw_df = recipe_data[recipe_data['flags'].str.contains('source:ingredients_raw', na=False)].copy()
en_df = recipe_data[recipe_data['flags'].str.contains('source:ingredients_en', na=False)].copy()
print(f"Raw: {len(raw_df)}, En: {len(en_df)}")

if len(raw_df) > 0:
    print(f"Raw normalized: {raw_df['normalized_ingredient'].tolist()}")
if len(en_df) > 0:
    print(f"En normalized: {en_df['normalized_ingredient'].tolist()}")

# Try reconciliation
raw_by_norm = raw_df.set_index('normalized_ingredient')
en_by_norm = en_df.set_index('normalized_ingredient')
all_norms = set(raw_by_norm.index) | set(en_by_norm.index)
print(f"\nAll norms: {len(all_norms)}")
for norm_ing in list(all_norms)[:5]:
    print(f"  {norm_ing[:80]}")
    print(f"    raw_match: {norm_ing in raw_by_norm.index}, en_match: {norm_ing in en_by_norm.index}")