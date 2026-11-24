import pandas as pd
parsed_df = pd.read_parquet('data/interim/phase2/parsed_recipe_ingredients.parquet')

def _has_source_flag(flags, source):
    if isinstance(flags, list):
        return any(source in f for f in flags)
    elif isinstance(flags, str):
        return source in flags
    return False

# Check the flags column for recipe 1
r1 = parsed_df[parsed_df['recipe_id'] == 1]
raw = r1[r1['source_field'] == 'ingredients_raw']
en = r1[r1['source_field'] == 'ingredients_en']

print('Raw flags sample:')
print(raw['flags'].iloc[0] if len(raw) > 0 else 'none')
print()
print('En flags sample:')
print(en['flags'].iloc[0] if len(en) > 0 else 'none')
print()

# Test the flag detection
for _, r in parsed_df[parsed_df['recipe_id'] == 1].head(5).iterrows():
    is_raw = _has_source_flag(r['flags'], 'source:ingredients_raw')
    is_en = _has_source_flag(r['flags'], 'source:ingredients_en')
    print(f'Source: {r["source_field"]}, _is_raw: {is_raw}, _is_en: {is_en}')