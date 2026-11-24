import pandas as pd

norm_df = pd.read_parquet('data/interim/phase2/normalized_ingredients.parquet')

# Check recipe 1 in normalized data
recipe1 = norm_df[norm_df['recipe_id'] == 1]
raw_items = recipe1[recipe1['flags'].str.contains('source:ingredients_raw')]
en_items = recipe1[recipe1['flags'].str.contains('source:ingredients_en')]
print('Normalized Recipe 1:')
print(f'Raw: {len(raw_items)}, En: {len(en_items)}')

# Check parsed output
parsed_df = pd.read_parquet('data/interim/phase2/parsed_recipe_ingredients.parquet')
recipe1_parsed = parsed_df[parsed_df['recipe_id'] == 1]
print(f'Parsed Recipe 1: {len(recipe1_parsed)} items')
for _, r in recipe1_parsed.iterrows():
    print(f'  {r["source_field"]}: {r["normalized_ingredient"][:80]}')