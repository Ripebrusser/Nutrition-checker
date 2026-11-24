import pandas as pd

# Check normalized ingredients
norm_df = pd.read_parquet('data/interim/phase2/normalized_ingredients.parquet')
print('Normalized ingredients (sample):')
for ing in norm_df['normalized_ingredient'].unique()[:50]:
    print(f'  {ing}')

print(f'\nTotal unique: {norm_df["normalized_ingredient"].nunique()}')

# Check if any match synonym keys
syn_df = pd.read_csv('data/interim/phase2/ingredient_synonyms.csv')
syn_keys = set(syn_df['synonym'].str.lower().str.strip()) if 'synonym' in syn_df.columns else set()
if 'synonym_key' in syn_df.columns:
    syn_keys = set(syn_df['synonym_key'].str.lower().str.strip())

norm_ingredients = set(norm_df['normalized_ingredient'].str.lower().str.strip())

print(f'\nSynonym keys: {len(syn_keys)}')
print(f'Normalized ingredients: {len(norm_ingredients)}')

# Find overlap
overlap = syn_keys & norm_ingredients
print(f'\nOverlap: {len(overlap)}')
for ing in list(overlap)[:20]:
    print(f'  {ing}')

# Check some specific synonym keys
test_keys = ['toor dal', 'jeera', 'haldi', 'onion', 'garlic', 'tomato', 'rice', 'dal']
print('\nTest keys in normalized ingredients:')
for key in test_keys:
    if key in norm_ingredients:
        print(f'  {key}: FOUND')
    else:
        # Check partial
        matches = [n for n in norm_ingredients if key in n or n in key]
        if matches:
            print(f'  {key}: PARTIAL -> {matches[:3]}')
        else:
            print(f'  {key}: NOT FOUND')