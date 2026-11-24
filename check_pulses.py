import pandas as pd
ifct = pd.read_parquet('data/interim/ifct_final_candidate/ifct_table1_candidate.parquet')
pulses = ifct[ifct['food_group'].str.contains('PULSE|LEGUME', case=False)]
print('Pulses and legumes in IFCT:')
for _, row in pulses.iterrows():
    print(f'  {row["food_code"]}: {row["food_name"]} ({row["food_group"]})')