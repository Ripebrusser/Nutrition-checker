import pandas as pd
cands = pd.read_parquet('data/interim/phase3/ifct_match_candidates.parquet')
# Find cumin seeds matches
cumin = cands[cands['matched_ingredient_name'].str.contains('cumin', case=False, na=False)]
print('Cumin matches:')
for _, row in cumin.head(20).iterrows():
    print('  ' + repr(row['matched_ingredient_name']) + ' -> ' + row['ifct_food_name'] + ' | ' + row['match_method'] + ' | review=' + str(row['requires_review']))