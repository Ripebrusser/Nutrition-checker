import pandas as pd
parsed = pd.read_parquet('data/interim/phase2/parsed_recipe_ingredients.parquet')
# Find rows with jeera or cumin
jeera_rows = parsed[parsed['ingredient_name'].str.contains('jeera|cumin', case=False, na=False)]
print('Rows with jeera/cumin:')
for _, row in jeera_rows.head(10).iterrows():
    print('  ingredient_name: ' + repr(row['ingredient_name']))
    print('  normalized_ingredient: ' + repr(row['normalized_ingredient']))
    print()