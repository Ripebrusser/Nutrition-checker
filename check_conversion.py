import pandas as pd

df = pd.read_parquet('data/interim/phase2/parsed_recipe_ingredients.parquet')

print('=== CONVERSION READINESS ===')
print('Conversion status:')
print(df['conversion_status'].value_counts())
print()

# Check household resolved records
hh_resolved = df[df['conversion_status'] == 'RESOLVED_HOUSEHOLD']
print(f'RESOLVED_HOUSEHOLD records: {len(hh_resolved)}')

# Check if household resolved have gram_weight
hh_with_weight = hh_resolved[hh_resolved['gram_weight'].notna()]
print(f'Household resolved with gram_weight: {len(hh_with_weight)}')

# Check gram_weight_min/max
print(f'Gram weight min resolved: {df.loc[df["conversion_status"] == "RESOLVED_HOUSEHOLD", "gram_weight_min"].notna().sum()}')
print(f'Gram weight max resolved: {df.loc[df["conversion_status"] == "RESOLVED_HOUSEHOLD", "gram_weight_max"].notna().sum()}')

# Check the unit field
print()
print('Unit field sample:')
unit_sample = df['unit'].dropna().head(20)
for u in unit_sample:
    print(f'  {u}')

# Check unit field structure
df_unit = df[df['unit'].notna()]
unit_dict = df['unit'].apply(lambda x: x if isinstance(x, dict) else None)
has_cf = unit_dict.apply(lambda x: x.get('conversion_factor') if isinstance(x, dict) else None).notna().sum()
print(f'Records with unit: {len(df_unit)}')
print(f'Records with conversion_factor: {has_cf}')
print(f'Records without conversion_factor: {len(df_unit) - has_cf}')

# Check the household measurements mapping
hh = pd.read_csv('data/interim/phase2/household_measurements.csv')
print()
print('Household measurements count:', len(hh))
print('Units:', hh['household_unit'].unique())

# Check how many RESOLVED_HOUSEHOLD have gram_weight
hh_resolved = df[df['conversion_status'] == 'RESOLVED_HOUSEHOLD']
hh_with_weight = hh_resolved[hh_resolved['gram_weight'].notna()]
print(f'\nHousehold resolved with gram_weight: {len(hh_with_weight)}')

# Check the unit field structure
unit_dict = df['unit'].apply(lambda x: x if isinstance(x, dict) else None)
hh_unit = df[df['conversion_status'] == 'RESOLVED_HOUSEHOLD']['unit']
print('\nHousehold resolved unit field:')
print(hh_unit.value_counts())

# Check for unit conversion factors
for u in hh_unit.unique():
    if isinstance(u, dict):
        print(f'  Unit: {u}')
        break