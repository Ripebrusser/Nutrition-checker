import pandas as pd
cands = pd.read_parquet('data/interim/phase3/ifct_match_candidates.parquet')
# Find rows with parenthetical text in matched_ingredient_name
paren = cands[cands['matched_ingredient_name'].str.contains(r'\(.*\)', na=False)]
print(f'Candidates with parentheses in matched name: {len(paren)}')
print()
for _, row in paren.head(20).iterrows():
    print(f'  {repr(row["matched_ingredient_name"])} -> {row["ifct_food_name"]} | {row["match_method"]} | review={row["requires_review"]}')