import pandas as pd

print("=== VALIDATING STAGE 2.3 OUTPUTS ===\n")

# Load new outputs
cands = pd.read_parquet('data/interim/phase3/stage2_3/ifct_match_candidates.parquet')
unmatched = pd.read_parquet('data/interim/phase3/stage2_3/unmatched_ingredients.parquet')
disambiguated = pd.read_parquet('data/interim/phase3/stage2_3/disambiguated_ingredients.parquet')

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

# Auto-accepted
auto = cands[cands['requires_review'] == False]
print(f"Auto-accepted: {len(auto)}")
if len(auto) > 0:
    print("By method:")
    print(auto['match_method'].value_counts())
    print()
    print("By preparation state:")
    print(auto['preparation_state'].value_counts())
    print()

# Check EXACT auto-accepted
exact_auto = cands[(cands['match_method'] == 'EXACT') & (cands['requires_review'] == False)]
print(f"EXACT auto-accepted: {len(exact_auto)}")
if len(exact_auto) > 0:
    print("Prep states:")
    print(exact_auto['preparation_state'].value_counts())
    print()

# Check SYNONYM auto-accepted
syn_auto = cands[(cands['match_method'] == 'SYNONYM') & (cands['requires_review'] == False)]
print(f"SYNONYM auto-accepted: {len(syn_auto)}")
if len(syn_auto) > 0:
    print("Prep states:")
    print(syn_auto['preparation_state'].value_counts())
    print()

# Check non-raw auto-accepted
non_raw_auto = auto[~auto['preparation_state'].isin(['RAW', 'FRESH', 'NOT_SPECIFIED', 'UNKNOWN'])]
print(f"Non-raw auto-accepted: {len(non_raw_auto)}")
if len(non_raw_auto) > 0:
    print(non_raw_auto[['primary_ingredient', 'ifct_food_name', 'preparation_state', 'match_method']].head(20))
    print()

# Check multi-code ambiguity
print("Multi-code ambiguity check:")
multi_ifct = cands.groupby('primary_ingredient')['ifct_food_code'].nunique()
multi = multi_ifct[multi_ifct > 1]
print(f"Primary ingredients with multiple IFCT codes: {len(multi)}")
if len(multi) > 0:
    print(multi.head(10))
    print()

# Check IFCT codes with multiple primary ingredients
multi_src = cands.groupby('ifct_food_code')['primary_ingredient'].nunique()
multi_src = multi_src[multi_src > 1]
print(f"IFCT codes with multiple primary ingredients: {len(multi_src)}")
if len(multi_src) > 0:
    print(multi_src.head(10))
    print()

# Preparation state distribution
print("Preparation state distribution (auto-accepted):")
if len(auto) > 0:
    print(auto['preparation_state'].value_counts())
else:
    print("None")

print("\nPreparation state distribution (all candidates):")
print(cands['preparation_state'].value_counts().head(20))

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

# Check duplicates
dups = cands.duplicated(subset=['recipe_id', 'primary_ingredient', 'ifct_food_code']).sum()
print(f"Duplicate candidates (recipe+primary+IFCT): {dups}")

# Check acceptance evidence
print("\nAcceptance decision evidence sample:")
for _, row in cands.head(5).iterrows():
    ev = row['evidence']
    if isinstance(ev, dict) and 'acceptance_decision' in ev:
        print(f"  {row['primary_ingredient']}: {ev['acceptance_decision']}")

# Check RAW candidates that should be auto-accepted
print("\nChecking RAW EXACT candidates:")
raw_exact = cands[(cands['match_method'] == 'EXACT') & (cands['preparation_state'] == 'RAW')]
print(f"RAW EXACT candidates: {len(raw_exact)}")
if len(raw_exact) > 0:
    print("Sample:")
    for _, row in raw_exact.head(10).iterrows():
        ev = row['evidence']
        acc = ev.get('acceptance_decision', {}) if isinstance(ev, dict) else {}
        print(f"  {row['primary_ingredient']} -> {row['ifct_food_name']} | auto_accept: {acc.get('auto_accept')} | reasons: {acc.get('reasons')}")

# Check IFCT coverage
matched_ifct_codes = cands['ifct_food_code'].nunique()
total_ifct_codes = ifct['food_code'].nunique()
print(f"\nIFCT coverage: {matched_ifct_codes}/{total_ifct_codes} ({matched_ifct_codes/total_ifct_codes*100:.1f}%)")

# Unmatched IFCT codes by food group
matched_ifct = ifct[ifct['food_code'].isin(cands['ifct_food_code'].unique())]
unmatched_ifct = ifct[~ifct['food_code'].isin(cands['ifct_food_code'].unique())]
print("\nUnmatched IFCT codes by food group:")
print(unmatched_ifct['food_group'].value_counts())

print("\nCandidate counts by IFCT food group:")
print(cands['ifct_food_group'].value_counts().head(20))