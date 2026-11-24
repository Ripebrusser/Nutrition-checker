import pandas as pd

df = pd.read_excel('datasets/Anuvaad_INDB_2024.11.xlsx', sheet_name='Sheet1')

# Check all nutrient column names and infer units
print('=== NUTRIENT COLUMNS (per 100g) ===')
nutrient_100g = [c for c in df.columns if not c.startswith('unit_serving_') and c not in ['food_code', 'food_name', 'primarysource', 'servings_unit']]
for col in nutrient_100g:
    print('  {}'.format(col))

print('\n=== NUTRIENT COLUMNS (per serving) ===')
nutrient_serving = [c for c in df.columns if c.startswith('unit_serving_')]
for col in nutrient_serving:
    print('  {}'.format(col))

# Check if per-serving = per-100g * (serving_size_in_g / 100)
# For items with both, calculate implied serving size in grams
non_missing = df.dropna(subset=['unit_serving_energy_kcal'])
print('\n=== Implied Serving Size (g) from Energy ===')
for _, r in non_missing.head(20).iterrows():
    if r['energy_kcal'] > 0:
        implied_g = (r['unit_serving_energy_kcal'] / r['energy_kcal']) * 100
        print('  {} ({}): {}g per serving (unit: {})'.format(r['food_name'], r['food_code'], round(implied_g, 1), r['servings_unit']))

# Check a few more
print('\n=== More implied serving sizes ===')
for _, r in non_missing.sample(20, random_state=42).iterrows():
    if r['energy_kcal'] > 0:
        implied_g = (r['unit_serving_energy_kcal'] / r['energy_kcal']) * 100
        print('  {} ({}): {}g per serving (unit: {})'.format(r['food_name'], r['food_code'], round(implied_g, 1), r['servings_unit']))