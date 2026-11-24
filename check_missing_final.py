import pandas as pd

df = pd.read_csv('data/interim/ifct_extracted/table1_parsed.csv')
print('Current extracted:')
print(f'  Total items: {len(df)}')
print(f'Unique codes: {df["food_code"].nunique()}')
print('Food groups:', df['food_group'].value_counts().to_dict())

missing = ['D001', 'E004', 'G013', 'H005', 'M001', 'M002', 'M003', 'M004', 'M005', 'M006', 'M007', 'N001', 'N002', 'N003', 'N004', 'N005', 'N006', 'T001', 'T002', 'T003', 'T004', 'T005', 'T006', 'T007', 'T008', 'T009', 'T010', 'T011', 'T011', 'T012', 'T013', 'T014']

for code in ['D001', 'E004', 'G013', 'H005', 'M001', 'M002', 'M003', 'M004', 'M005', 'M006', 'M007', 'N001', 'N002', 'N003', 'N004', 'N005', 'N006', 'T001', 'T002', 'T003', 'T004', 'T005', 'T006', 'T007', 'T008', 'T009', 'T010', 'T011', 'T012', 'T013', 'T014']:
    row = df[df['food_code'] == code]
    if len(row) > 0:
        r = row.iloc[0]
        print(f'{code}: FOUND - group={r["food_group"]} name={r["food_name"]}')
    else:
        print(f'{code}: MISSING')