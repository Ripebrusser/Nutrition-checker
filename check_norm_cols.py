import pandas as pd

norm_df = pd.read_parquet('data/interim/phase2/normalized_ingredients.parquet')
print('Columns:', list(norm_df.columns))
print()

# Check sample rows
for _, row in norm_df.head(10).iterrows():
    print(f"normalized: {row['normalized_ingredient']}")
    print(f"ingredient_name: {row.get('ingredient_name', 'N/A')}")
    print(f"source_ingredient: {row.get('source_ingredient', 'N/A')}")
    print(f"source_line: {row.get('source_line', 'N/A')}")
    print(f"quantity: {row.get('quantity', 'N/A')}")
    print(f"unit: {row.get('unit', 'N/A')}")
    print(f"preparation: {row.get('preparation', 'N/A')}")
    print(f"flags: {row.get('flags', 'N/A')}")
    print("---")