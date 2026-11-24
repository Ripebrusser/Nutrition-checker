import pandas as pd

print("=== VALIDATING CORRECTED STAGE 2 OUTPUTS ===\n")

# Load new outputs
cands = pd.read_parquet('data/interim/phase3/ifct_match_candidates.parquet')
unmatched = pd.read_parquet('data/interim/phase3/unmatched_ingredients.parquet')

print(f"Candidate records: {len(cands)}")
print(f"Unmatched records: {len(unmatched)}")
print()

# Method counts
print("Match method counts:")
print(cands['match_method'].value_counts())
print()

# Confidence counts
print("Confidence counts:")
print(cands['provisional_confidence'].value_counts())
print()

# Review requirement
print("Requires review:")
print(cands['requires_review'].value_counts())
print()

# EXACT vs TOKEN_EQUIVALENT vs TOKEN_SIMILARITY HIGH
print("HIGH confidence breakdown by method:")
high = cands[cands['provisional_confidence'] == 'HIGH']
print(high['match_method'].value_counts())
print()

# TOKEN_EQUIVALENT details
token_eq = cands[cands['match_method'] == 'TOKEN_EQUIVALENT']
print(f"TOKEN_EQUIVALENT count: {len(token_eq)}")
print(f"  Unique ingredients: {token_eq['matched_ingredient_name'].nunique()}")
print(f"  All require_review: {token_eq['requires_review'].all()}")
print()

# SYNONYM auto-accept check
syn = cands[cands['match_method'] == 'SYNONYM']
print(f"SYNONYM count: {len(syn)}")
print(f"  requires_review=False: {(syn['requires_review'] == False).sum()}")
print(f"  requires_review=True: {(syn['requires_review'] == True).sum()}")
print(f"  Confidence distribution:")
print(syn['provisional_confidence'].value_counts())
print()

# EXACT auto-accept check
exact = cands[cands['match_method'] == 'EXACT']
print(f"EXACT count: {len(exact)}")
print(f"  requires_review=False: {(exact['requires_review'] == False).sum()}")
print(f"  requires_review=True: {(exact['requires_review'] == True).sum()}")
print()

# Total auto-accept (requires_review=False)
auto_accept = cands[cands['requires_review'] == False]
print(f"Total auto-accept (requires_review=False): {len(auto_accept)}")
print(f"  Methods: {auto_accept['match_method'].value_counts().to_dict()}")
print()

# Check Jaccard=1.0 cases
jaccard1 = cands[(cands['match_method'] == 'TOKEN_EQUIVALENT') & (cands['similarity_score'] >= 0.999)]
print(f"Jaccard=1.0 TOKEN_EQUIVALENT: {len(jaccard1)}")
print()

# Verify IFCT codes
ifct = pd.read_parquet('data/interim/ifct_final_candidate/ifct_table1_candidate.parquet')
valid_codes = set(ifct['food_code'])
invalid = set(cands['ifct_food_code'].unique()) - valid_codes
print(f"Invalid IFCT codes: {len(invalid)}")
if invalid:
    print(f"  {invalid}")

# Check duplicates
dups = cands.duplicated(subset=['recipe_id', 'matched_ingredient_name', 'ifct_food_code']).sum()
print(f"Duplicate candidates (recipe+ingredient+IFCT): {dups}")

# Count reconciliation
parsed = pd.read_parquet('data/interim/phase2/parsed_recipe_ingredients.parquet')
total_records = len(parsed)
total_unique_name = parsed['ingredient_name'].nunique()
matched_unique_name = cands['matched_ingredient_name'].nunique()
unmatched_unique_name = unmatched['ingredient_name'].nunique()

print(f"\nCOUNT RECONCILIATION:")
print(f"  Total ingredient records: {total_records}")
print(f"  Total unique ingredient_name: {total_unique_name}")
print(f"  Unique ingredient_name with candidates: {matched_unique_name}")
print(f"  Unique ingredient_name without candidates: {unmatched_unique_name}")
print(f"  Sum: {matched_unique_name + unmatched_unique_name}")

# Record-level
matched_names_set = set(cands['matched_ingredient_name'].unique())
parsed['has_cands'] = parsed['ingredient_name'].isin(matched_names_set)
rec_with = parsed['has_cands'].sum()
rec_without = (~parsed['has_cands']).sum()
print(f"  Records with candidates: {rec_with} ({rec_with/total_records*100:.1f}%)")
print(f"  Records without candidates: {rec_without} ({rec_without/total_records*100:.1f}%)")
print(f"  Sum: {rec_with + rec_without}")

# Unmatched at normalized_ingredient level
total_unique_norm = parsed['normalized_ingredient'].nunique()
unmatched_unique_norm = unmatched['normalized_ingredient'].nunique()
matched_unique_norm = total_unique_norm - unmatched_unique_norm
print(f"\n  Unique normalized_ingredient total: {total_unique_norm}")
print(f"  Unique normalized_ingredient matched: {matched_unique_norm}")
print(f"  Unique normalized_ingredient unmatched: {unmatched_unique_norm}")