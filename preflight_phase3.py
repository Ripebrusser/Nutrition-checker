import pandas as pd

# Check canonical ingredient records for source traceability
df = pd.read_parquet('data/interim/phase2/parsed_recipe_ingredients.parquet')

print('=== CANONICAL INGREDIENT INTEGRITY ===')
print(f'Total canonical records: {len(df)}')
print(f'Unique recipes: {df["recipe_id"].nunique()}')
print(f'Unique normalized ingredients: {df["normalized_ingredient"].nunique()}')
print()

# Check source traceability
print('=== SOURCE TRACEABILITY ===')
print('Source field distribution:')
print(df['source_field'].value_counts())
print()

# Check if original text is preserved
print('Original ingredient text preservation:')
sample = df.head(5)
for _, row in sample.iterrows():
    print(f'  Original: {row["original_ingredient"][:80]}')
    print(f'  Normalized: {row["normalized_ingredient"][:80]}')
    print(f'  Source: {row["source_field"]}')
    print()

# Check recipe IDs stability
print(f'Unique recipe IDs: {df["recipe_id"].nunique()}')
print(f'Total records: {len(df)}')
print(f'Duplicates on (recipe_id, normalized_ingredient): {df.duplicated(subset=["recipe_id", "normalized_ingredient"]).sum()}')
print()

# Check flags column
print('Flags column sample:')
print(df['flags'].head(10).tolist())
print()

# Check if both raw and en are preserved in canonical
canonical = df[df['source_reconciliation'] == 'canonical']
print(f'Canonical records: {len(canonical)}')
print('Canonical source_field distribution:')
print(df[df['source_reconciliation'] == 'canonical']['source_field'].value_counts())
print()

# Check if original text is preserved in canonical
print('Sample canonical records:')
for _, row in df[df['source_reconciliation'] == 'canonical'].head(5).iterrows():
    print(f'  Recipe {row["recipe_id"]}: {row["original_ingredient"][:80]} -> {row["normalized_ingredient"][:80]}')