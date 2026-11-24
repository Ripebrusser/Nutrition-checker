import pandas as pd
from src.ingredients.ingredient_parser import IngredientParser, reconcile_sources, _has_source_flag

# Create the full parsed data like the main function does
norm_df = pd.read_parquet('data/interim/phase2/normalized_ingredients.parquet')
parser = IngredientParser()

parsed_records = []
for i, (_, row) in enumerate(norm_df.iterrows()):
    parsed = __import__('src.ingredients.ingredient_parser', fromlist=['IngredientParser']).IngredientParser().parse(row['normalized_ingredient'])
    source_field = 'ingredients_raw' if 'source:ingredients_raw' in row['flags'] else 'ingredients_en'
    
    parsed.recipe_id = row['recipe_id']
    parsed.source_field = source_field
    parsed.original_line = row['source_line']
    parsed.original_ingredient = row['source_ingredient']
    parsed.normalized_ingredient = row['normalized_ingredient']
    if row['flags']:
        parsed.flags.extend(row['flags'].split('; '))
    
    d = parsed.to_dict()
    parsed_records.append(d)

print(f'Total parsed records: {len(parsed_records)}')

# Convert to DataFrame
parsed_df = pd.DataFrame(parsed_records)
print(f'DataFrame shape: {parsed_df.shape}')
print(f'En count: {(parsed_df["source_field"] == "ingredients_en").sum()}')
print(f'Raw count: {(parsed_df["source_field"] == "ingredients_raw").sum()}')

# Now test the reconciliation step by step
# Step 1: Add source columns
parsed_df['_is_raw'] = parsed_df['flags'].apply(lambda f: _has_source_flag(f, 'source:ingredients_raw'))
parsed_df['_is_en'] = parsed_df['flags'].apply(lambda f: _has_source_flag(f, 'source:ingredients_en'))

# Check _is_raw and _is_en for recipe 1
r1 = parsed_df[parsed_df['recipe_id'] == 1]
print('Recipe 1 _is_raw:', r1['_is_raw'].sum())
print('Recipe 1 _is_en:', r1['_is_en'].sum())

# Group by recipe_id and normalized_ingredient
grouped = parsed_df.groupby(['recipe_id', 'normalized_ingredient']).agg(
    has_raw=('_is_raw', 'any'),
    has_en=('_is_en', 'any'),
    _is_raw=('_is_raw', 'first'),
    _is_en=('_is_en', 'first'),
).reset_index()

print(f'\nTotal groups: {len(grouped)}')

# Check reconciliation status
grouped['source_reconciliation'] = grouped.apply(
    lambda r: 'canonical' if r['has_raw'] and r['has_en'] else ('raw_only' if r['has_raw'] else ('en_only' if r['has_en'] else 'unknown')), axis=1
)

print('Reconciliation status distribution:')
print(grouped['source_reconciliation'].value_counts())

# Check for canonical matches
canonical_groups = grouped[grouped['source_reconciliation'] == 'canonical']
print(f'\nCanonical groups: {len(canonical_groups)}')

if len(canonical_groups) > 0:
    print('Sample canonical matches:')
    for _, r in canonical_groups.head(5).iterrows():
        print(f'  Recipe {r["recipe_id"]}: {r["normalized_ingredient"][:60]}')