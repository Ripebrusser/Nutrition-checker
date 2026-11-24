import pandas as pd
norm_df = pd.read_parquet('data/interim/phase2/normalized_ingredients.parquet')

# Check the source field assignment in the parsing loop
en_records = norm_df[norm_df['flags'].str.contains('source:ingredients_en')].head(3)
for _, row in en_records.iterrows():
    source_field = 'ingredients_raw' if 'source:ingredients_raw' in row['flags'] else 'ingredients_en'
    print(f'Flags: {row["flags"][:80]}')
    print(f'Source field assigned: {source_field}')
    print()