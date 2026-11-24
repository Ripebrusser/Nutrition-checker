import pandas as pd

df = pd.read_parquet('data/interim/phase2/parsed_recipe_ingredients.parquet')

print('=== CANONICAL INGREDIENT INTEGRITY ===')
print(f'Total canonical records: {len(df)}')
print(f'Unique recipes: {df["recipe_id"].nunique()}')
print(f'Unique normalized ingredients: {df["normalized_ingredient"].nunique()}')
print()

print('Source field distribution:')
print(df['source_field'].value_counts())
print()

# Check if original text is preserved in canonical records
canonical = df[df['source_reconciliation'] == 'canonical']
print(f'Canonical records: {len(canonical)}')
print('Canonical source_field distribution:')
print(canonical['source_field'].value_counts())
print()

# Check if original text is preserved in canonical records
print('Sample canonical records:')
for _, row in df[df['source_reconciliation'] == 'canonical'].head(5).iterrows():
    print(f'  Recipe {row["recipe_id"]}: {row["original_ingredient"][:80]} -> {row["normalized_ingredient"][:80]}')
    print(f'  Source: {row["source_field"]}')
    print()

# Check if original text is preserved in canonical records
print('Original text preservation in canonical:')
for _, row in df[df['source_reconciliation'] == 'canonical'].head(3).iterrows():
    print(f'  Original: {row["original_ingredient"][:100]}')
    print(f'  Normalized: {row["normalized_ingredient"][:80]}')
    print()

# Check if recipe IDs and ingredient record IDs are stable
print(f'Total records: {len(df)}')
print(f'Unique recipes: {df["recipe_id"].nunique()}')
print(f'Unique normalized ingredients: {df["normalized_ingredient"].nunique()}')
print(f'Duplicates on (recipe_id, normalized_ingredient): {df.duplicated(subset=["recipe_id", "normalized_ingredient"]).sum()}')