import pandas as pd

df = pd.read_excel('datasets/Anuvaad_INDB_2024.11.xlsx', sheet_name='Sheet1')

# Check the 82 records missing per-serving data
serving_cols = [c for c in df.columns if c.startswith('unit_serving_')]
missing_serving = df[serving_cols].isnull().all(axis=1)
missing_df = df[missing_serving]

print('=== 82 Records Missing Per-Serving Data ===')
print('Primary source distribution:')
print(missing_df['primarysource'].value_counts())
print()

print('Food code prefix distribution:')
missing_df['prefix'] = missing_df['food_code'].str[:3]
print(missing_df['prefix'].value_counts())
print()

print('Sample missing records:')
for _, r in missing_df.head(20).iterrows():
    print('  {}: {} (source: {})'.format(r['food_code'], r['food_name'], r['primarysource']))
print()

# Check serving_unit for missing vs non-missing
print('=== Serving Unit Analysis ===')
print('Non-missing serving_unit values:')
non_missing = df[~missing_serving]
print(non_missing['servings_unit'].value_counts().head(20))
print()

print('Missing serving_unit values:')
print(missing_df['servings_unit'].value_counts().head(20))
print()

# Check if missing serving_unit correlates with missing per-serving
print('Missing serving_unit count:', missing_df['servings_unit'].isna().sum())
print('Non-missing serving_unit count:', non_missing['servings_unit'].isna().sum())