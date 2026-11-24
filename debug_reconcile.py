import pandas as pd

# Load parsed data
parsed_df = pd.read_parquet('data/interim/phase2/parsed_recipe_ingredients.parquet')
print(f"Parsed DF shape: {parsed_df.shape}")
print(f"Columns: {list(parsed_df.columns)}")

# Check a specific recipe
recipe_id = 1
recipe_data = pd.read_parquet('data/interim/phase2/parsed_recipe_ingredients.parquet')
recipe_data = recipe_data[recipe_data['recipe_id'] == recipe_id]
print(f"\nRecipe {recipe_id}: {len(recipe_data)} records")

# Check source distribution
raw = recipe_data[recipe_data['flags'].str.contains('source:ingredients_raw', na=False)]
en = recipe_data[recipe_data['flags'].str.contains('source:ingredients_en', na=False)]
print(f"Raw: {len(raw)}, En: {len(en)}")

print("\nRaw ingredients:")
for _, r in raw.iterrows():
    print(f"  {r['normalized_ingredient'][:80]}")

print("\nEn ingredients:")
for _, r in en.iterrows():
    print(f"  {r['normalized_ingredient'][:80]}")

# Check if normalized_ingredient column exists and has values
print(f"\nColumns: {list(pd.read_parquet('data/interim/phase2/parsed_recipe_ingredients.parquet').columns)}")