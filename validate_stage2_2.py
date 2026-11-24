import pandas as pd

print("=== VALIDATING STAGE 2.2 OUTPUTS ===\n")

# Load new outputs
cands = pd.read_parquet('data/interim/phase3/stage2_2/ifct_match_candidates.parquet')
unmatched = pd.read_parquet('data/interim/phase3/stage2_2/unmatched_ingredients.parquet')
disambiguated = pd.read_parquet('data/interim/phase3/stage2_2/disambiguated_ingredients.parquet')

print(f"Candidate records: {len(cands)}")
print(f"Unmatched records: {len(unmatched)}")
print(f"Disambiguated records: {len(disambiguated)}")
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

# Preparation state distribution
print("Preparation state distribution:")
print(cands['preparation_state'].value_counts())
print()

# Primary ingredient stats
print("Unique primary ingredients:", cands['primary_ingredient'].nunique())
print("Unique normalized ingredients:", cands['normalized_ingredient'].nunique())

# Check EXACT vs TOKEN_EQUIVALENT vs TOKEN_SIMILARITY HIGH
print("\nHIGH confidence breakdown by method:")
high = cands[cands['provisional_confidence'] == 'HIGH']
print(high['match_method'].value_counts())
print()

# TOKEN_EQUIVALENT details
token_eq = cands[cands['match_method'] == 'TOKEN_EQUIVALENT']
print(f"TOKEN_EQUIVALENT count: {len(token_eq)}")
print(f"  Unique ingredients: {token_eq['primary_ingredient'].nunique()}")
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

# Check preparation state compatibility
print("Prep state compatibility distribution:")
print(cands['prep_state_compat'].value_counts().head(10))
print()

# Count reconciliation
parsed = pd.read_parquet('data/interim/phase2/parsed_recipe_ingredients.parquet')
total_records = len(parsed)
total_unique_name = parsed['ingredient_name'].nunique()
matched_unique_name = cands['primary_ingredient'].nunique()
unmatched_unique_name = unmatched['ingredient_name'].nunique()

print(f"\nCOUNT RECONCILIATION:")
print(f"  Total ingredient records: {total_records}")
print(f"  Total unique ingredient_name: {total_unique_name}")
print(f"  Unique primary_ingredient with candidates: {matched_unique_name}")
print(f"  Unique ingredient_name without candidates: {unmatched_unique_name}")

# Record-level
matched_names_set = set(cands['primary_ingredient'].unique())
parsed['has_cands'] = parsed['ingredient_name'].isin(matched_names_set)
rec_with = parsed['has_cands'].sum()
rec_without = (~parsed['has_cands']).sum()
print(f"  Records with candidates: {rec_with} ({rec_with/total_records*100:.1f}%)")
print(f"  Records without candidates: {rec_without} ({rec_without/total_records*100:.1f}%)")

# Check IFCT codes
ifct = pd.read_parquet('data/interim/ifct_final_candidate/ifct_table1_candidate.parquet')
valid_codes = set(ifct['food_code'])
invalid = set(cands['ifct_food_code'].unique()) - valid_codes
print(f"\nInvalid IFCT codes: {len(invalid)}")
if invalid:
    print(f"  {invalid}")

# Check duplicates
dups = cands.duplicated(subset=['recipe_id', 'primary_ingredient', 'ifct_food_code']).sum()
print(f"Duplicate candidates (recipe+ingredient+IFCT): {dups}")

# Check disambiguation stats
print(f"\nDISAMBIGUATION STATS:")
print(f"  Records with parentheses: {disambiguated['parentheses_balanced'].sum() + (~disambiguated['parentheses_balanced']).sum()}")
print(f"  Balanced parentheses: {disambiguated['parentheses_balanced'].sum()}")
print(f"  Unbalanced parentheses: {(~disambiguated['parentheses_balanced']).sum()}")
print(f"  Preparation detected: {(disambiguated['preparation_state'] != 'NOT_SPECIFIED').sum()}")
print(f"  Alias extraction status:")
print(disambiguated['alias_extraction_status'].value_counts())
print(f"  Ambiguity flags sample:")
# Flatten flags
all_flags = []
for flags_str in disambiguated['ambiguity_flags'].dropna():
    if flags_str and flags_str != '[]':
        try:
            flags = eval(flags_str)
            all_flags.extend(flags)
        except:
            pass
from collections import Counter
print(Counter(all_flags).most_common(10))