import pandas as pd
cands = pd.read_parquet('data/interim/phase3/ifct_match_candidates.parquet')

# Find the 7011 Jaccard=1.0 TOKEN_SIMILARITY HIGH cases
high_token = cands[(cands['provisional_confidence'] == 'HIGH') & (cands['match_method'] == 'TOKEN_SIMILARITY') & (cands['similarity_score'] == 1.0)]
print(f'Count: {len(high_token)}')

# Show examples
for _, row in high_token.head(20).iterrows():
    print(f"  '{row['matched_ingredient_name']}' -> '{row['ifct_food_name']}' (score: {row['similarity_score']})")

# Check evidence for token details
print("\nEvidence examples:")
for _, row in high_token.head(5).iterrows():
    print(f"  Input: {row['matched_ingredient_name']}")
    print(f"  IFCT: {row['ifct_food_name']}")
    print(f"  Evidence: {row['evidence']}")
    print()