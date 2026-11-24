import pandas as pd

# Load normalized ingredients
norm = pd.read_parquet('data/interim/phase2/normalized_ingredients.parquet')
print(f"Shape: {norm.shape}")
print(f"Columns: {list(norm.columns)}")
print(f"Recipe IDs: {norm['recipe_id'].nunique()}")

# Check source distribution
print("\nSource distribution:")
print(norm['flags'].str.contains('source:ingredients_raw').sum(), "raw")
print(norm['flags'].str.contains('source:ingredients_en').sum(), "en")

# Sample records
print("\nSample records:")
for i in range(min(20, len(norm))):
    row = norm.iloc[i]
    print(f"  Recipe {row['recipe_id']} | {row['source_ingredient'][:80]} -> {row['normalized_ingredient'][:80]}")

# Check for duplicates within same recipe+source
print("\nDuplicate check within recipe+source+ingredient:")
dupes = norm.duplicated(subset=['recipe_id', 'source_ingredient', 'flags']).sum()
print(f"Duplicates: {dupes}")

# Check raw vs en for same recipe
print("\nChecking raw vs en for same recipe:")
for recipe_id in norm['recipe_id'].unique()[:5]:
    recipe_data = norm[norm['recipe_id'] == recipe_id]
    raw_ings = set(recipe_data[recipe_data['flags'].str.contains('source:ingredients_raw')]['source_ingredient'])
    en_ings = set(recipe_data[recipe_data['flags'].str.contains('source:ingredients_en')]['source_ingredient'])
    print(f"  Recipe {recipe_id}: raw={len(raw_ings)}, en={len(en_ings)}")
    if raw_ings != en_ings:
        print(f"    Raw only: {raw_ings - en_ings}")
        print(f"    En only: {en_ings - raw_ings}")