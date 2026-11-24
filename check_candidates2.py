import pandas as pd
cands = pd.read_parquet('data/interim/phase3/ifct_match_candidates.parquet')

# Per recipe-ingredient record
print('Per recipe-ingredient record:')
print(f'  Total candidate records: {len(cands)}')
pairs = cands.groupby(['recipe_id', 'matched_ingredient_name']).ngroups
print(f'  Unique (recipe_id, matched_ingredient_name) pairs: {pairs}')
print(f'  Mean candidates per recipe-ingredient: {len(cands) / pairs:.1f}')

# Per unique ingredient_name
print('\nPer unique ingredient_name:')
unique_ings = cands['matched_ingredient_name'].nunique()
print(f'  Unique ingredient_names with candidates: {unique_ings}')
cands_per_ing = cands.groupby('matched_ingredient_name')['ifct_food_code'].nunique()
print(f'  Mean unique IFCT codes per ingredient: {cands_per_ing.mean():.1f}')
print(f'  Max unique IFCT codes per ingredient: {cands_per_ing.max()}')
print(f'  Min unique IFCT codes per ingredient: {cands_per_ing.min()}')

# Check HIGH confidence TOKEN_SIMILARITY
high_token = cands[(cands['provisional_confidence'] == 'HIGH') & (cands['match_method'] == 'TOKEN_SIMILARITY')]
print(f'\nHIGH confidence TOKEN_SIMILARITY: {len(high_token)}')
print(f'  Similarity scores: {high_token["similarity_score"].describe()}')

# Check SYNONYM confidence
syn = cands[cands['match_method'] == 'SYNONYM']
print(f'\nSYNONYM confidence distribution:')
print(syn['provisional_confidence'].value_counts())
print(f'  requires_review: {syn["requires_review"].value_counts().to_dict()}')

# Check EXACT confidence
exact = cands[cands['match_method'] == 'EXACT']
print(f'\nEXACT confidence distribution:')
print(exact['provisional_confidence'].value_counts())
print(f'  requires_review: {exact["requires_review"].value_counts().to_dict()}')