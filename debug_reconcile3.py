import pandas as pd

# Load the canonical output
canonical_df = pd.read_parquet('data/interim/phase2/parsed_recipe_ingredients.parquet')
print(f"Shape: {canonical_df.shape}")
print(f"Columns: {list(canonical_df.columns)}")
print(f"Source reconciliation values: {canonical_df['source_reconciliation'].value_counts()}")
print(f"Has raw: {canonical_df['raw_match'].sum()}")
print(f"Has en: {canonical_df['en_match'].sum()}")
print(f"Has raw col: {'has_raw' in canonical_df.columns}")
print(f"Has en col: {'has_en' in canonical_df.columns}")

# Check a specific recipe
recipe_id = 1
recipe_data = canonical_df[canonical_df['recipe_id'] == recipe_id]
print(f"\nRecipe {recipe_id}: {len(recipe_data)} records")
print(f"Reconciliation: {recipe_data['source_reconciliation'].value_counts()}")
print(f"Raw match: {recipe_data['raw_match'].sum()}")
print(f"En match: {recipe_data['en_match'].sum()}")
print(f"Flags sample: {recipe_data['flags'].iloc[0] if len(recipe_data) > 0 else 'empty'}")

# Check raw vs en in parsed_df
parsed_df = pd.read_parquet('data/interim/phase2/parsed_recipe_ingredients.parquet')
# Wait, we need the pre-reconciliation data
# Let's check the normalized_ingredients instead
norm_df = pd.read_parquet('data/interim/phase2/normalized_ingredients.parquet')
recipe_raw = norm_df[(norm_df['recipe_id'] == 1) & (norm_df['flags'].str.contains('source:ingredients_raw'))]
recipe_en = norm_df[(norm_df['recipe_id'] == 1) & (norm_df['flags'].str.contains('source:ingredients_en'))]
print(f"\nRecipe 1 raw: {len(recipe_raw)}, en: {len(recipe_en)}")
print(f"Raw normalized: {recipe_raw['normalized_ingredient'].tolist()}")
print(f"En normalized: {recipe_en['normalized_ingredient'].tolist()}")