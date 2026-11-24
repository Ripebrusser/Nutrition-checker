import pandas as pd
df = pd.read_csv('data/interim/ifct_verified/ifct_food_code_inventory.csv')
print(f'Inventory: {len(df)} records')
print(f'Unique codes: {df["food_code"].nunique()}')
print(f'Groups: {df["food_group"].nunique()}')
print(f'Methods: {df["extraction_method"].value_counts().to_dict()}')
print(f'Verification: {df["verification_status"].value_counts().to_dict()}')
print(f'Manual recovery: {df["manual_recovery"].sum()}')