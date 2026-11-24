import pandas as pd

parsed_df = pd.read_parquet('data/interim/phase2/parsed_recipe_ingredients.parquet')
print('Columns:', list(parsed_df.columns))
print(f'Records: {len(parsed_df)}')
print()

# Check sample rows
for _, row in parsed_df.head(10).iterrows():
    print(f"recipe_id: {row.get('recipe_id', 'N/A')}")
    print(f"source_field: {row.get('source_field', 'N/A')}")
    print(f"source_ingredient: {row.get('source_ingredient', 'N/A')}")
    print(f"normalized_ingredient: {row.get('normalized_ingredient', 'N/A')}")
    print(f"ingredient_name: {row.get('ingredient_name', 'N/A')}")
    print(f"quantity: {row.get('quantity', 'N/A')}")
    print(f"unit: {row.get('unit', 'N/A')}")
    print(f"preparation: {row.get('preparation', 'N/A')}")
    print(f"size_descriptor: {row.get('size_descriptor', 'N/A')}")
    print(f"gram_weight: {row.get('gram_weight', 'N/A')}")
    print(f"conversion_status: {row.get('conversion_status', 'N/A')}")
    print(f"source_reconciliation: {row.get('source_reconciliation', 'N/A')}")
    print("---")

# Check unique source_field values
print(f"\nsource_field values: {parsed_df['source_field'].value_counts().to_dict()}")