import pandas as pd
norm_df = pd.read_parquet('data/interim/phase2/normalized_ingredients.parquet')

# Check how many en records exist for recipe 1 in normalized data
en_r1 = norm_df[(norm_df['recipe_id'] == 1) & (norm_df['flags'].str.contains('source:ingredients_en'))]
print(f'Normalized en records for recipe 1: {len(en_r1)}')

# Check parsed output for recipe 1 en records
parsed_df = pd.read_parquet('data/interim/phase2/parsed_recipe_ingredients.parquet')
en_parsed = parsed_df[(parsed_df['recipe_id'] == 1) & (parsed_df['source_field'] == 'ingredients_en')]
print(f'Parsed en records for recipe 1: {len(en_parsed)}')

# Check all en records in parsed
print(f'Total parsed en records: {(parsed_df["source_field"] == "ingredients_en").sum()}')
print(f'Total en in normalized: {norm_df["flags"].str.contains("source:ingredients_en").sum()}')

# Check if en records are being dropped during parsing
# Let's trace through the parsing loop for recipe 1 en records
en_r1 = norm_df[(norm_df['recipe_id'] == 1) & (norm_df['flags'].str.contains('source:ingredients_en'))]
print()
print('Recipe 1 en normalized ingredients:')
for _, r in en_r1.iterrows():
    print(f'  {r["normalized_ingredient"]}')