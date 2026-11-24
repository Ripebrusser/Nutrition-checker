import pandas as pd
norm_df = pd.read_parquet('data/interim/phase2/normalized_ingredients.parquet')

# Check recipe 1 - compare raw vs en normalized_ingredient for same ingredients
r1 = norm_df[norm_df['recipe_id'] == 1]
raw = r1[r1['flags'].str.contains('source:ingredients_raw')]
en = r1[r1['flags'].str.contains('source:ingredients_en')]

print('Raw normalized ingredients:')
for _, r in raw.iterrows():
    print(f'  {r["normalized_ingredient"]}')
print()
print('En normalized ingredients:')
for _, r in en.iterrows():
    print(f'  {r["normalized_ingredient"]}')