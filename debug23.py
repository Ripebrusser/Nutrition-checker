import pandas as pd
df = pd.read_parquet('data/interim/phase2/parsed_recipe_ingredients.parquet')
en_df = df[df['source_field'] == 'ingredients_en']
print(f'Total en records: {len(en_df)}')
print(f'Unique recipes with en: {en_df[\"recipe_id\"].nunique()}')

en_recipes = en_df['recipe_id'].value_counts()
print('Top 20 recipes with en records:')
print(en_recipes.head(20))

r1 = df[df['recipe_id'] == 1]
print(f'\nRecipe 1 total: {len(df[df[\"recipe_id\"]==1])}')
print(f'Recipe 1 source_field:')
print(df[df['recipe_id']==1]['source_field'].value_counts())