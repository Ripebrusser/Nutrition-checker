import pandas as pd
norm_df = pd.read_parquet('data/interim/phase2/normalized_ingredients.parquet')

# Check the flags for recipe 1 en records
en_r1 = norm_df[(norm_df['recipe_id'] == 1) & (norm_df['flags'].str.contains('source:ingredients_en'))]
for _, r in en_r1.iterrows():
    print(f'Flags: {r["flags"]}')
    print(f'Normalized: {r["normalized_ingredient"]}')
    print()