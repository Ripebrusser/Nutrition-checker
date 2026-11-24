import pandas as pd
from src.ingredients.ingredient_parser import _has_source_flag

parsed_df = pd.read_parquet('data/interim/phase2/parsed_recipe_ingredients.parquet')

r1 = parsed_df[parsed_df['recipe_id'] == 1]
raw = r1[r1['source_field'] == 'ingredients_raw']
en = r1[r1['source_field'] == 'ingredients_en']

print(f'Raw count: {len(raw)}, En count: {len(en)}')
print()

for _, r in r1.iterrows():
    is_raw = _has_source_flag(r['flags'], 'source:ingredients_raw')
    is_en = _has_source_flag(r['flags'], 'source:ingredients_en')
    print(f'Source: {r["source_field"]}, _is_raw: {is_raw}, _is_en: {is_en}, flags: {r["flags"]}')