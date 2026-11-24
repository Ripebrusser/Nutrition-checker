import pandas as pd
cands = pd.read_parquet('data/interim/phase3/ifct_match_candidates.parquet')

# Find ingredient with most candidates
cands_per = cands.groupby('matched_ingredient_name').size().sort_values(ascending=False)
print('Top 20 ingredients by candidate count:')
for ing, cnt in cands_per.head(20).items():
    print(f'  {cnt}: {ing}')

# Check the max
max_ing = cands_per.index[0]
max_cands = cands[cands['matched_ingredient_name'] == max_ing]
print(f'\nMax candidate ingredient: {max_ing}')
print(f'  Total candidates: {len(max_cands)}')
print(f'  Unique IFCT codes: {max_cands["ifct_food_code"].nunique()}')
print(f'  Match methods: {max_cands["match_method"].value_counts().to_dict()}')
print(f'  Similarity scores: min={max_cands["similarity_score"].min():.3f}, max={max_cands["similarity_score"].max():.3f}')
print(f'  Sample IFCT codes: {max_cands["ifct_food_code"].unique()[:10]}')

# Check what tokens this ingredient has
from src.matching.candidate_generator import CandidateGenerator
import pandas as pd
ifct_df = pd.read_parquet('data/interim/ifct_final_candidate/ifct_table1_candidate.parquet')
gen = CandidateGenerator(ifct_df, {}, {})
tokens = gen._tokenize(max_ing)
print(f'\nTokens for "{max_ing}": {tokens}')

# Check token index for each token
for token in tokens:
    if token in gen.token_index:
        print(f'  Token "{token}" -> {len(gen.token_index[token])} IFCT foods')
    else:
        print(f'  Token "{token}" -> NOT IN INDEX')