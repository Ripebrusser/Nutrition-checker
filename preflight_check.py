import pandas as pd

# Check parsed recipe ingredients
df = pd.read_parquet('data/interim/phase2/parsed_recipe_ingredients.parquet')
print('Parsed recipe ingredients:')
print(f'  Total records: {len(df)}')
print(f'  Unique recipes: {df["recipe_id"].nunique()}')
print(f'  Source reconciliation: {df["source_reconciliation"].value_counts().to_dict()}')
print(f'  Parse status: {df["parse_status"].value_counts().to_dict()}')
print(f'  Conversion status: {df["conversion_status"].value_counts().to_dict()}')
print(f'  Gram weight resolved: {df["gram_weight"].notna().sum()}')
print()

# Check IFCT candidate
ifct = pd.read_parquet('data/interim/ifct_final_candidate/ifct_table1_candidate.parquet')
print(f'IFCT candidate records: {len(ifct)}')
print(f'IFCT unique food codes: {ifct["food_code"].nunique()}')
print(f'IFCT food groups: {ifct["food_group"].nunique()}')
print()

# Check INDB
indb = pd.read_parquet('data/processed/indb_foods.parquet')
print(f'INDB records: {len(indb)}')
print(f'INDB unique food codes: {indb["food_code"].nunique()}')

# Check recipes
recipes = pd.read_parquet('data/processed/recipes.parquet')
print(f'Recipes: {len(recipes)}')
print(f'Unique recipe IDs: {recipes["recipe_id"].nunique()}')