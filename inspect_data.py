import pandas as pd

# Check IFCT candidate dataset
ifct = pd.read_parquet('data/interim/ifct_final_candidate/ifct_table1_candidate.parquet')
print('IFCT candidate:')
print(f'  Records: {len(ifct)}')
print(f'  Columns: {list(ifct.columns)}')
print(f'  Food groups: {ifct["food_group"].nunique()}')
print(f'  Unique food codes: {ifct["food_code"].nunique()}')
print()

# Check parsed recipe ingredients
parsed = pd.read_parquet('data/interim/phase2/parsed_recipe_ingredients.parquet')
print(f'Parsed recipe ingredients: {len(parsed)}')
print(f'  Unique recipes: {parsed["recipe_id"].nunique()}')
print(f'  Unique normalized ingredients: {parsed["normalized_ingredient"].nunique()}')
print(f'  Source reconciliation: {parsed["source_reconciliation"].value_counts().to_dict()}')
print()

# Check synonym dictionary
syn = pd.read_csv('data/interim/phase2/ingredient_synonyms.csv')
print(f'Synonym dictionary: {len(syn)} entries')
print(f'  Categories: {syn["category"].value_counts().to_dict()}')
print()

# Check household measurements
hh = pd.read_csv('data/interim/phase2/household_measurements.csv')
print(f'Household measurements: {len(hh)}')
print(f'  Units: {hh["household_unit"].unique()}')
print()

# Check IFCT food groups
ifct = pd.read_parquet('data/interim/ifct_final_candidate/ifct_table1_candidate.parquet')
print('IFCT food groups:')
print(ifct['food_group'].value_counts())