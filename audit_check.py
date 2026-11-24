import pandas as pd

df = pd.read_excel('datasets/Anuvaad_INDB_2024.11.xlsx', sheet_name='Sheet1')

items_to_check = ['Hot tea (Garam Chai)', 'Instant coffee', 'Semolina upma (Suji/Rava upma)', 
                  'Plain parantha/paratha', 'Idli', 'Mixed dal']

for item in items_to_check:
    row = df[df['food_name'] == item]
    if len(row) > 0:
        r = row.iloc[0]
        print('\n=== {} ({}) ==='.format(item, r["food_code"]))
        print('  servings_unit: {}'.format(r["servings_unit"]))
        print('  energy_kcal (per 100g): {:.2f}'.format(r["energy_kcal"]))
        print('  protein_g (per 100g): {:.2f}'.format(r["protein_g"]))
        print('  carb_g (per 100g): {:.2f}'.format(r["carb_g"]))
        print('  fat_g (per 100g): {:.2f}'.format(r["fat_g"]))
        if pd.notna(r['unit_serving_energy_kcal']):
            print('  unit_serving_energy_kcal: {:.2f}'.format(r["unit_serving_energy_kcal"]))
            print('  unit_serving_protein_g: {:.2f}'.format(r["unit_serving_protein_g"]))
            print('  unit_serving_carb_g: {:.2f}'.format(r["unit_serving_carb_g"]))
            print('  unit_serving_fat_g: {:.2f}'.format(r["unit_serving_fat_g"]))
        else:
            print('  MISSING per-serving data')