import pandas as pd

# Check recipe IDs in canonical output
canonical_df = pd.read_parquet('data/interim/phase2/parsed_recipe_ingredients.parquet')
print(f"Canonical recipes: {canonical_df['recipe_id'].nunique()} unique IDs")
print(f"Recipe IDs range: {canonical_df['recipe_id'].min()} to {canonical_df['recipe_id'].max()}")

# Check original recipes
recipes_df = pd.read_parquet('data/processed/recipes.parquet')
print(f"\nOriginal recipes: {recipes_df['recipe_id'].nunique()} unique IDs")
print(f"Recipe IDs range: {recipes_df['recipe_id'].min()} to {recipes_df['recipe_id'].max()}")

# Check which recipes are missing
canonical_ids = set(canonical_df['recipe_id'].unique())
original_ids = set(pd.read_parquet('data/processed/recipes.parquet')['recipe_id'].unique())

print(f"\nCanonical IDs count: {len(canonical_ids)}")
print(f"Original IDs count: {len(original_ids)}")
print(f"Original IDs not in canonical: {original_ids - canonical_ids}")
print(f"Canonical IDs not in original: {canonical_ids - original_ids}")

# Check if recipe IDs are sequential
print(f"\nOriginal IDs sample: {sorted(list(original_ids))[:20]}")
print(f"Canonical IDs sample: {sorted(list(canonical_ids))[:20]}")

# Check if all original recipes have at least one canonical ingredient
recipes_with_canonical = set(canonical_df['recipe_id'].unique())
missing_recipes = original_ids - recipes_with_canonical
print(f"\nRecipes missing from canonical: {len(missing_recipes)}")
if missing_recipes:
    print(f"Missing: {sorted(missing_recipes)[:20]}")