import pandas as pd
df = pd.read_parquet('data/interim/ifct_final_candidate/ifct_table1_candidate.parquet')
print('Shape:', df.shape)
print('Columns:', list(df.columns))
print()
print('Food groups:')
print(df['food_group'].value_counts())
print()
print('Food codes (first 20):')
print(df['food_code'].head(20).tolist())
print()
for code in ['A001', 'J001', 'N001', 'P001', 'Q001']:
    matches = df[df['food_code'] == code]
    print(f'  {code}: {len(matches)} matches')
    if len(matches) > 0:
        print(f'    {matches["food_name"].values}')