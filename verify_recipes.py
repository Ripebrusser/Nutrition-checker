import pandas as pd
df = pd.read_parquet('data/processed/recipes.parquet')
print(f'Recipes: {len(df)} rows, {df["recipe_id"].nunique()} unique IDs')
print(f'Columns: {list(df.columns)}')

# Check missing ingredients count
if 'missing_ingredients' in df.columns:
    missing = df['missing_ingredients'].sum()
    print(f'Missing ingredients: {missing}')

# Check condiments flagged
if 'condiment_flag' in df.columns:
    condiments = df['condiment_flag'].sum()
    print(f'Condiments flagged: {condiments}')