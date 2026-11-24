import pandas as pd

# Load canonical output
canonical_df = pd.read_parquet('data/interim/phase2/parsed_recipe_ingredients.parquet')
print(f"Shape: {canonical_df.shape}")
print(f"Recipes: {canonical_df['recipe_id'].nunique()}")

# Check reconciliation distribution
print(f"\nReconciliation:")
print(canonical_df['source_reconciliation'].value_counts())

print(f"\nDiscrepancy flag: {canonical_df['discrepancy_flag'].sum()}")

print(f"\nRaw match: {canonical_df['raw_match'].sum()}")
print(f"En match: {canonical_df['en_match'].sum()}")

# Check a few recipes
for recipe_id in [1, 2, 3]:
    recipe_data = canonical_df[canonical_df['recipe_id'] == recipe_id]
    print(f"\nRecipe {recipe_id}: {len(recipe_data)} records")
    print(f"  Reconciliation: {recipe_data['source_reconciliation'].value_counts().to_dict()}")
    print(f"  Raw match: {recipe_data['raw_match'].sum()}, En match: {recipe_data['en_match'].sum()}")
    print(f"  Discrepancy: {recipe_data['discrepancy_flag'].sum()}")

# Check conversion status
print(f"\nConversion status:")
print(canonical_df['conversion_status'].value_counts())

print(f"\nParse status:")
print(canonical_df['parse_status'].value_counts())

# Check gram weight resolution
gw = canonical_df['gram_weight'].notna().sum()
gw_range = canonical_df['gram_weight_min'].notna().sum()
print(f"\nGram weight resolved: {canonical_df['gram_weight'].notna().sum()} (exact), {canonical_df['gram_weight_min'].notna().sum()} (range)")

# Check sample parsed ingredients
print("\nSample parsed ingredients:")
for _, row in canonical_df.head(20).iterrows():
    qty = row.get('quantity', {})
    unit = row.get('unit', {})
    print(f"  {row['ingredient_name'][:40]}: qty={qty.get('value') if isinstance(qty, dict) else qty}, unit={unit.get('standardized_unit') if isinstance(unit, dict) else unit}, status={row['parse_status']}, gw={row.get('gram_weight')}")

# Check unparsed
print("\nUnparsed samples:")
unparsed = canonical_df[canonical_df['parse_status'] == 'UNQUANTIFIED'].head(10)
for _, row in unparsed.iterrows():
    print(f"  {row['normalized_ingredient'][:80]} -> {row['parse_status']}")

# Check flags
print("\nFlags sample:")
for _, row in canonical_df.head(10).iterrows():
    print(f"  {row['ingredient_name'][:40]}: {row['flags']}")