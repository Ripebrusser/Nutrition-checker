import pandas as pd

# Check normalized data flags
norm_df = pd.read_parquet('data/interim/phase2/normalized_ingredients.parquet')
print('Normalized flags sample:')
print(norm_df['flags'].iloc[0])
print('Type:', type(norm_df['flags'].iloc[0]))
print()

# Check parsed data flags
parsed_df = pd.read_parquet('data/interim/phase2/parsed_recipe_ingredients.parquet')
print('Parsed flags sample:')
print(parsed_df['flags'].iloc[0])
print('Type:', type(parsed_df['flags'].iloc[0]))