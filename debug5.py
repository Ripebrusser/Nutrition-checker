import pandas as pd
parsed_df = pd.read_parquet('data/interim/phase2/parsed_recipe_ingredients.parquet')

r1 = parsed_df[parsed_df['recipe_id'] == 1]
raw = r1[r1['source_field'] == 'ingredients_raw']
en = r1[r1['source_field'] == 'ingredients_en']

print('Parsed Raw:')
for _, r in raw.iterrows():
    print(f'  {r["normalized_ingredient"]}')
print()
print('Parsed En:')
for _, r in en.iterrows():
    print(f'  {r["normalized_ingredient"]}')