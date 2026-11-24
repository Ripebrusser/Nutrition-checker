import pandas as pd

df = pd.read_excel('datasets/Anuvaad_INDB_2024.11.xlsx', sheet_name='Sheet1')

# Verify unit consistency: per-serving should equal per-100g * (serving_g / 100)
# Check a few nutrients beyond energy
non_missing = df.dropna(subset=['unit_serving_energy_kcal'])

print('=== Unit Consistency Check (Protein) ===')
consistent = 0
inconsistent = 0
for _, r in non_missing.head(50).iterrows():
    if r['protein_g'] > 0:
        implied_g = (r['unit_serving_protein_g'] / r['protein_g']) * 100
        energy_implied_g = (r['unit_serving_energy_kcal'] / r['energy_kcal']) * 100
        if abs(implied_g - energy_implied_g) < 1.0:
            consistent += 1
        else:
            inconsistent += 1
            print('  INCONSISTENT: {} - protein implied: {:.1f}g, energy implied: {:.1f}g'.format(
                r['food_name'], implied_g, energy_implied_g))

print('Consistent: {}, Inconsistent: {}'.format(consistent, inconsistent))

# Check fat
print('\n=== Unit Consistency Check (Fat) ===')
consistent = 0
inconsistent = 0
for _, r in non_missing.head(50).iterrows():
    if r['fat_g'] > 0:
        implied_g = (r['unit_serving_fat_g'] / r['fat_g']) * 100
        energy_implied_g = (r['unit_serving_energy_kcal'] / r['energy_kcal']) * 100
        if abs(implied_g - energy_implied_g) < 1.0:
            consistent += 1
        else:
            inconsistent += 1
            print('  INCONSISTENT: {} - fat implied: {:.1f}g, energy implied: {:.1f}g'.format(
                r['food_name'], implied_g, energy_implied_g))

print('Consistent: {}, Inconsistent: {}'.format(consistent, inconsistent))

# Check carb
print('\n=== Unit Consistency Check (Carb) ===')
consistent = 0
inconsistent = 0
for _, r in non_missing.head(50).iterrows():
    if r['carb_g'] > 0:
        implied_g = (r['unit_serving_carb_g'] / r['carb_g']) * 100
        energy_implied_g = (r['unit_serving_energy_kcal'] / r['energy_kcal']) * 100
        if abs(implied_g - energy_implied_g) < 1.0:
            consistent += 1
        else:
            inconsistent += 1
            print('  INCONSISTENT: {} - carb implied: {:.1f}g, energy implied: {:.1f}g'.format(
                r['food_name'], implied_g, energy_implied_g))

print('Consistent: {}, Inconsistent: {}'.format(consistent, inconsistent))