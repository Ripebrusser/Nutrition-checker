import pandas as pd
parsed = pd.read_parquet('data/interim/phase2/parsed_recipe_ingredients.parquet')

# Check ingredient_name for parentheses
print("=== Parsed ingredient_name with parentheses ===")
paren = parsed[parsed['ingredient_name'].str.contains(r'\(.*\)', na=False)]
print(f'Count: {len(paren)}')
for _, row in paren.head(20).iterrows():
    print(f'  {repr(row["ingredient_name"])} | normalized: {repr(row["normalized_ingredient"])} | prep: {row["preparation"]}')

print()
print("=== Normalized ingredient with parentheses ===")
paren2 = parsed[parsed['normalized_ingredient'].str.contains(r'\(.*\)', na=False)]
print(f'Count: {len(paren2)}')
for _, row in paren2.head(20).iterrows():
    print(f'  {repr(row["normalized_ingredient"])} | ingredient_name: {repr(row["ingredient_name"])}')