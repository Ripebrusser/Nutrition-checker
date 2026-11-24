import pandas as pd

# Check normalized data for en records
norm_df = pd.read_parquet('data/interim/phase2/normalized_ingredients.parquet')
en_r1 = norm_df[(norm_df['recipe_id'] == 1) & (norm_df['flags'].str.contains('source:ingredients_en'))]
print(f'Normalized en records for recipe 1: {len(en_r1)}')
for _, r in en_r1.iterrows():
    print(f'  {r["normalized_ingredient"]}')

# Check parsed output
parsed_df = pd.read_parquet('data/interim/phase2/parsed_recipe_ingredients.parquet')
en_parsed = parsed_df[(parsed_df['recipe_id'] == 1) & (parsed_df['source_field'] == 'ingredients_en')]
print(f'Parsed en records for recipe 1: {len(parsed_df[(parsed_df["recipe_id"]==1) & (parsed_df["source_field"]=="ingredients_en")])}')
for _, r in parsed_df[(parsed_df['recipe_id']==1) & (parsed_df['source_field']=='ingredients_en')].iterrows():
    print(f'  {r["normalized_ingredient"][:80]}')