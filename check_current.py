import pandas as pd
df = pd.read_csv('data/interim/ifct_extracted/table1_parsed.csv')
print(f'Total rows: {len(df)}')
print(f'Unique codes: {df["food_code"].nunique()}')
print(f'Groups: {df["food_group"].value_counts().to_dict()}')