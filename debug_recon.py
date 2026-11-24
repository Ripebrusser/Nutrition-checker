import pandas as pd
parsed_df = pd.read_parquet('data/interim/phase2/parsed_recipe_ingredients.parquet')

# Check recipe 1 in parsed data
recipe1 = parsed_df[parsed_df['recipe_id'] == 1]
print('Recipe 1 parsed:')
for _, row in recipe1.iterrows():
    print(f'  {row["source_field"]}: {row["normalized_ingredient"][:80]}')
print()

# Check if normalized_ingredient values match between raw and en
# Group by recipe_id and normalized_ingredient
grouped = parsed_df.groupby(['recipe_id', 'normalized_ingredient']).agg(
    sources=('source_field', lambda x: list(x.unique()))
).reset_index()

# Check for matches
both = grouped[grouped['sources'].apply(lambda x: 'ingredients_raw' in x and 'ingredients_en' in x)]
raw_only = grouped[grouped['sources'].apply(lambda x: 'ingredients_raw' in x and 'ingredients_en' not in x)]
en_only = grouped[grouped['sources'].apply(lambda x: 'ingredients_en' in x and 'ingredients_raw' not in x)]

print(f'Canonical (both): {len(both)}')
print(f'Raw only: {len(raw_only)}')
print(f'En only: {len(en_only)}')
print(f'Total groups: {len(grouped)}')

# Show some examples of matches
if len(both) > 0:
    print("\nExamples of canonical matches:")
    for _, row in both.head(5).iterrows():
        print(f"  Recipe {row['recipe_id']}: {row['normalized_ingredient'][:80]}")