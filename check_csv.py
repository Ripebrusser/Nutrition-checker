import pandas as pd
df = pd.read_csv('data/interim/ifct_extracted/table1_parsed.csv')
print('Shape:', df.shape)
print('Food groups:')
print(df['food_group'].value_counts())
print()
for code in ['A001', 'J001', 'N001', 'P001', 'Q001']:
    matches = df[df['food_code'] == code]
    print(f'  {code}: {len(matches)} matches')
    if len(matches) > 0:
        print(f'    {matches["food_name"].values}')