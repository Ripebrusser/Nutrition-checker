"""Independent Audit of Stage 2.2 Outputs"""

import pandas as pd
import numpy as np
import hashlib
import json

print("="*80)
print("STAGE 2.2 INDEPENDENT AUDIT")
print("="*80)

# ============================================================
# 1. FROZEN INPUT INTEGRITY
# ============================================================
print("\n1. FROZEN INPUT INTEGRITY")
print("-"*40)

frozen_files = {
    'normalized_ingredients': 'data/interim/phase2/normalized_ingredients.parquet',
    'parsed_recipe_ingredients': 'data/interim/phase2/parsed_recipe_ingredients.parquet',
    'ingredient_synonyms': 'data/interim/phase2/ingredient_synonyms.csv',
    'household_measurements': 'data/interim/phase2/household_measurements.csv',
    'ifct_table1_candidate': 'data/interim/ifct_final_candidate/ifct_table1_candidate.parquet',
}

frozen_hashes = {}
for name, path in frozen_files.items():
    with open(path, 'rb') as f:
        h = hashlib.sha256(f.read()).hexdigest()
    frozen_hashes[name] = h
    print(f"  {name}: {h}")

# ============================================================
# 2. OUTPUT FILE HASHES AND SCHEMAS
# ============================================================
print("\n2. OUTPUT FILE INSPECTION")
print("-"*40)

output_files = {
    'disambiguated': 'data/interim/phase3/stage2_2/disambiguated_ingredients.parquet',
    'candidates': 'data/interim/phase3/stage2_2/ifct_match_candidates.parquet',
    'unmatched': 'data/interim/phase3/stage2_2/unmatched_ingredients.parquet',
    'household': 'data/interim/phase3/stage2_2/household_measurements.csv',
}

output_hashes = {}
for name, path in output_files.items():
    with open(path, 'rb') as f:
        h = hashlib.sha256(f.read()).hexdigest()
    output_hashes[name] = h
    print(f"  {name}: {h}")

# Load data
print("\nLoading data...")
disamb = pd.read_parquet(output_files['disambiguated'])
cands = pd.read_parquet(output_files['candidates'])
unmatched = pd.read_parquet(output_files['unmatched'])

print(f"\nDisambiguated: {len(disamb)} rows, {len(disamb.columns)} cols")
print(f"Candidates: {len(cands)} rows, {len(cands.columns)} cols")
print(f"Unmatched: {len(unmatched)} rows, {len(unmatched.columns)} cols")

# Schemas
print("\n=== CANDIDATES SCHEMA ===")
for col in cands.columns:
    dtype = cands[col].dtype
    nulls = cands[col].isna().sum()
    print(f"  {col}: {dtype} (nulls: {nulls})")

print("\n=== DISAMBIGUATED SCHEMA ===")
for col in disamb.columns:
    dtype = disamb[col].dtype
    nulls = disamb[col].isna().sum()
    print(f"  {col}: {dtype} (nulls: {nulls})")

# ============================================================
# 3. RECORD COVERAGE RECONCILIATION
# ============================================================
print("\n3. RECORD COVERAGE RECONCILIATION")
print("-"*40)

# Input records
parsed = pd.read_parquet(frozen_files['parsed_recipe_ingredients'])
total_input_records = len(parsed)
print(f"Total input records (parsed): {total_input_records}")

# Unique identifiers
print(f"Unique recipe_ids: {parsed['recipe_id'].nunique()}")
print(f"Unique ingredient_name: {parsed['ingredient_name'].nunique()}")
print(f"Unique normalized_ingredient: {parsed['normalized_ingredient'].nunique()}")

# Candidate coverage
cand_primary_ingredients = set(cands['primary_ingredient'].unique())
cand_normalized = set(cands['normalized_ingredient'].unique())
print(f"\nUnique primary_ingredient in candidates: {len(cand_primary_ingredients)}")
print(f"Unique normalized_ingredient in candidates: {len(cand_normalized)}")

# Unmatched coverage
unmatched_ingredients = set(unmatched['ingredient_name'].unique())
unmatched_normalized = set(unmatched['normalized_ingredient'].unique())
print(f"Unique ingredient_name in unmatched: {len(unmatched_ingredients)}")
print(f"Unique normalized_ingredient in unmatched: {len(unmatched_normalized)}")

# Check partitioning
all_parsed_names = set(parsed['ingredient_name'].unique())
print(f"\nAll unique ingredient_name in parsed: {len(all_parsed_names)}")
print(f"Matched + Unmatched unique names: {len(cand_primary_ingredients) + len(unmatched_ingredients)}")
print(f"Overlap (matched & unmatched names): {len(cand_primary_ingredients & unmatched_ingredients)}")

# Record-level
# Which input records have candidates?
matched_names = cand_primary_ingredients
parsed['has_candidates'] = parsed['ingredient_name'].isin(matched_names)
records_with = parsed['has_candidates'].sum()
records_without = (~parsed['has_candidates']).sum()
print(f"\nInput records with candidates: {records_with} ({records_with/total_input_records*100:.1f}%)")
print(f"Input records without candidates: {records_without} ({records_without/total_input_records*100:.1f}%)")
print(f"Sum: {records_with + records_without}")

# Unmatched records check
unmatched_names = set(unmatched['ingredient_name'].unique())
parsed['is_unmatched'] = parsed['ingredient_name'].isin(unmatched_names)
unmatched_records = parsed['is_unmatched'].sum()
print(f"Records marked unmatched: {unmatched_records}")

# Neither
neither = parsed[~parsed['has_candidates'] & ~parsed['is_unmatched']]
print(f"Records in neither: {len(neither)}")

# Candidate rows per input record
cands_per_record = cands.groupby(['recipe_id', 'primary_ingredient']).size()
print(f"\nCandidate rows per (recipe, primary_ingredient):")
print(f"  Mean: {cands_per_record.mean():.2f}")
print(f"  Median: {cands_per_record.median()}")
print(f"  Max: {cands_per_record.max()}")
print(f"  Min: {cands_per_record.min()}")

# Unique ingredient-IFCT pairs
unique_pairs = cands[['primary_ingredient', 'ifct_food_code']].drop_duplicates()
print(f"\nUnique (primary_ingredient, IFCT) pairs: {len(unique_pairs)}")

# ============================================================
# 4. AUTO-ACCEPTANCE AUDIT
# ============================================================
print("\n4. AUTO-ACCEPTANCE AUDIT")
print("-"*40)

auto = cands[cands['requires_review'] == False]
print(f"Total auto-accepted (requires_review=False): {len(auto)}")

print("\nBy match_method:")
print(auto['match_method'].value_counts())

print("\nBy provisional_confidence:")
print(auto['provisional_confidence'].value_counts())

# Unique counts
print(f"\nUnique source ingredient names (original_ingredient): {auto['original_ingredient'].nunique()}")
print(f"Unique normalized ingredients: {auto['normalized_ingredient'].nunique()}")
print(f"Unique primary ingredients: {auto['primary_ingredient'].nunique()}")
print(f"Unique ingredient-IFCT pairs: {auto[['primary_ingredient', 'ifct_food_code']].drop_duplicates().shape[0]}")

# Check for source ingredients with multiple IFCT codes
multi_ifct = auto.groupby('primary_ingredient')['ifct_food_code'].nunique()
multi = multi_ifct[multi_ifct > 1]
print(f"\nPrimary ingredients with >1 auto-accepted IFCT code: {len(multi)}")
if len(multi) > 0:
    print(multi.head(10))

# Check for IFCT codes with multiple source ingredients
multi_src = auto.groupby('ifct_food_code')['primary_ingredient'].nunique()
multi_src = multi_src[multi_src > 1]
print(f"IFCT codes with >1 auto-accepted primary ingredient: {len(multi_src)}")
if len(multi_src) > 0:
    print(multi_src.head(10))

# SYNONYM auto-accepted details
syn_auto = auto[auto['match_method'] == 'SYNONYM']
print(f"\nSYNONYM auto-accepted: {len(syn_auto)}")
if len(syn_auto) > 0:
    print("Sample:")
    for _, row in syn_auto.head(10).iterrows():
        print(f"  {row['primary_ingredient']} -> {row['ifct_food_code']} ({row['ifct_food_name']})")
        print(f"    evidence: {row['evidence']}")

# Check preparation-state-incompatible auto-accepted
prep_incompat = auto[auto['prep_state_compat'] < 0.5]
print(f"\nAuto-accepted with prep_state_compat < 0.5: {len(prep_incompat)}")
if len(prep_incompat) > 0:
    for _, row in prep_incompat.head(10).iterrows():
        print(f"  {row['primary_ingredient']} -> {row['ifct_food_name']} | prep_compat: {row['prep_state_compat']} | prep_state: {row.get('preparation_state', 'N/A')}")

# Auto-accepted with missing provenance
missing_prov = auto[auto['evidence'].apply(lambda x: x == {} or x is None or (isinstance(x, dict) and len(x) == 0))]
print(f"\nAuto-accepted with empty evidence: {len(missing_prov)}")

# ============================================================
# 5. EXACT CLASSIFICATION AUDIT
# ============================================================
print("\n5. EXACT CLASSIFICATION AUDIT")
print("-"*40)

exact = cands[cands['match_method'] == 'EXACT']
print(f"Total EXACT candidates: {len(exact)}")
print(f"EXACT requires_review=False: {(exact['requires_review'] == False).sum()}")
print(f"EXACT requires_review=True: {(exact['requires_review'] == True).sum()}")
print(f"EXACT similarity_score distribution:")
print(exact['similarity_score'].describe())

# Sample manual inspection
print("\nSample EXACT matches (first 30):")
for _, row in exact.head(30).iterrows():
    print(f"  '{row['primary_ingredient']}' -> '{row['ifct_food_name']}' ({row['ifct_food_code']}) | prep: {row.get('preparation_state', 'N/A')} | compat: {row['prep_state_compat']}")

# ============================================================
# 6. PARENTHETICAL DISAMBIGUATION AUDIT
# ============================================================
print("\n6. PARENTHETICAL DISAMBIGUATION AUDIT")
print("-"*40)

# Records with parentheses
has_paren = disamb[disamb['parenthetical_text'] != '']
print(f"Records with parenthetical_text non-empty: {len(has_paren)}")

# Parentheses balanced
print(f"Parentheses balanced: {disamb['parentheses_balanced'].sum()}")
print(f"Parentheses unbalanced: {(~disamb['parentheses_balanced']).sum()}")

# Alias extraction status
print("\nAlias extraction status:")
print(disamb['alias_extraction_status'].value_counts())

# Sample with aliases
print("\nSample with extracted aliases (first 20):")
for _, row in has_paren.head(20).iterrows():
    print(f"  primary: '{row['primary_ingredient']}'")
    print(f"    paren_text: '{row['parenthetical_text']}'")
    print(f"    aliases: {row['extracted_aliases']}")
    print(f"    prep: {row['preparation_state']} (conf: {row['preparation_confidence']})")
    print(f"    status: {row['alias_extraction_status']}")
    print(f"    flags: {row['ambiguity_flags']}")
    print()

# Check for false alias extraction (preparation as synonym)
print("\nChecking for preparation-in-parentheses extracted as synonym...")
false_syn = disamb[
    (disamb['extracted_aliases'].apply(lambda x: 'PREPARATION' in str(x) or 'preparation' in str(x).lower())) &
    (disamb['extracted_aliases'].apply(lambda x: 'SYNONYM' in str(x) or 'HINDI_NAME' in str(x) or 'ALTERNATE_NAME' in str(x)))
]
print(f"Aliases classified as both preparation and synonym: {len(false_syn)}")

# Information lost during cleaning
print("\nChecking information loss...")
# Compare primary_ingredient to original normalized_ingredient
loss = disamb[disamb['primary_ingredient'] != disamb['normalized_ingredient']]
print(f"Records where primary != normalized_ingredient: {len(loss)}")
for _, row in loss.head(20).iterrows():
    print(f"  normalized: '{row['normalized_ingredient']}' -> primary: '{row['primary_ingredient']}'")

# ============================================================
# 7. PREPARATION-STATE AUDIT
# ============================================================
print("\n7. PREPARATION-STATE AUDIT")
print("-"*40)

print("Preparation state distribution (candidates):")
print(cands['preparation_state'].value_counts())

print("\nPreparation state distribution (disambiguated):")
print(disamb['preparation_state'].value_counts())

# Conflicting preparation states
print("\nChecking for conflicting preparation states...")
# In disambiguated, flags should have CONFLICTING_PREPARATION
conflict = disamb[disamb['ambiguity_flags'].apply(lambda x: 'CONFLICTING_PREPARATION' in str(x))]
print(f"Records with CONFLICTING_PREPARATION flag: {len(conflict)}")

# Compatibility decisions
print("\nPrep state compatibility distribution:")
print(cands['prep_state_compat'].value_counts().head(20))

# Check incompatible states that auto-accepted
incompat_auto = auto[auto['prep_state_compat'] < 0.5]
print(f"\nAuto-accepted with prep_state_compat < 0.5: {len(incompat_auto)}")

# Raw-basis assumptions
print("\nChecking raw-basis enforcement...")
raw_cands = cands[cands['preparation_state'] == 'RAW']
print(f"Candidates with preparation_state=RAW: {len(raw_cands)}")
print(f"  requires_review=False: {(raw_cands['requires_review'] == False).sum()}")

fresh_cands = cands[cands['preparation_state'] == 'FRESH']
print(f"Candidates with preparation_state=FRESH: {len(fresh_cands)}")
print(f"  requires_review=False: {(fresh_cands['requires_review'] == False).sum()}")

dried_cands = cands[cands['preparation_state'] == 'DRIED']
print(f"Candidates with preparation_state=DRIED: {len(dried_cands)}")
print(f"  requires_review=False: {(dried_cands['requires_review'] == False).sum()}")

roasted_cands = cands[cands['preparation_state'] == 'ROASTED']
print(f"Candidates with preparation_state=ROASTED: {len(roasted_cands)}")
print(f"  requires_review=False: {(roasted_cands['requires_review'] == False).sum()}")

fried_cands = cands[cands['preparation_state'] == 'FRIED']
print(f"Candidates with preparation_state=FRIED: {len(fried_cands)}")
print(f"  requires_review=False: {(fried_cands['requires_review'] == False).sum()}")

boiled_cands = cands[cands['preparation_state'] == 'BOILED']
print(f"Candidates with preparation_state=BOILED: {len(boiled_cands)}")
print(f"  requires_review=False: {(boiled_cands['requires_review'] == False).sum()}")

cooked_cands = cands[cands['preparation_state'] == 'COOKED']
print(f"Candidates with preparation_state=COOKED: {len(cooked_cands)}")
print(f"  requires_review=False: {(cooked_cands['requires_review'] == False).sum()}")

powdered_cands = cands[cands['preparation_state'] == 'POWDERED']
print(f"Candidates with preparation_state=POWDERED: {len(powdered_cands)}")
print(f"  requires_review=False: {(powdered_cands['requires_review'] == False).sum()}")

ground_cands = cands[cands['preparation_state'] == 'GROUND']
print(f"Candidates with preparation_state=GROUND: {len(ground_cands)}")
print(f"  requires_review=False: {(ground_cands['requires_review'] == False).sum()}")

# ============================================================
# 8. NEGATIVE CONTROL AUDIT
# ============================================================
print("\n8. NEGATIVE CONTROL AUDIT")
print("-"*40)

# We need to re-run the negative controls to verify
print("See run_negative_controls.py output for detailed results")

# ============================================================
# 9. COVERAGE AND FOOD GROUP ANALYSIS
# ============================================================
print("\n9. COVERAGE AND FOOD GROUP ANALYSIS")
print("-"*40)

ifct = pd.read_parquet(frozen_files['ifct_table1_candidate'])
total_ifct_codes = ifct['food_code'].nunique()
matched_ifct_codes = cands['ifct_food_code'].nunique()
print(f"Total IFCT codes: {total_ifct_codes}")
print(f"Matched IFCT codes: {matched_ifct_codes}")
print(f"Unmatched IFCT codes: {total_ifct_codes - matched_ifct_codes}")

# By food group
print("\nMatched IFCT codes by food group:")
matched_ifct = ifct[ifct['food_code'].isin(cands['ifct_food_code'].unique())]
print(matched_ifct['food_group'].value_counts())

print("\nUnmatched IFCT codes by food group:")
unmatched_ifct = ifct[~ifct['food_code'].isin(cands['ifct_food_code'].unique())]
print(unmatched_ifct['food_group'].value_counts())

# Candidate counts by food group
print("\nCandidate counts by IFCT food group:")
print(cands['ifct_food_group'].value_counts().head(20))

# ============================================================
# 10. TEST ACCOUNTING
# ============================================================
print("\n10. TEST ACCOUNTING")
print("-"*40)

import subprocess
result = subprocess.run(['py', '-m', 'pytest', 'tests/', '-v', '--tb=no', '-q'], 
                       capture_output=True, text=True, timeout=120)
output = result.stdout
lines = output.strip().split('\n')

passed = 0
failed = 0
for l in lines:
    if 'PASSED' in l:
        passed += 1
    elif 'FAILED' in l:
        failed += 1

print(f"Passed: {passed}")
print(f"Failed: {failed}")
print(f"Total: {passed + failed}")

# ============================================================
# 11. SAVE AUDIT DATA
# ============================================================
print("\n11. SAVING AUDIT DATA")
print("-"*40)

audit_data = {
    'frozen_hashes': frozen_hashes,
    'output_hashes': output_hashes,
    'total_input_records': int(total_input_records),
    'candidate_records': int(len(cands)),
    'unmatched_records': int(len(unmatched)),
    'disambiguated_records': int(len(disamb)),
    'unique_primary_ingredients': int(len(cand_primary_ingredients)),
    'unique_ifct_codes_matched': int(matched_ifct_codes),
    'auto_accept_count': int(len(auto)),
    'auto_accept_by_method': auto['match_method'].value_counts().to_dict(),
    'exact_count': int(len(exact)),
    'records_with_candidates': int(records_with),
    'records_without_candidates': int(records_without),
    'test_passed': passed,
    'test_failed': failed,
}

with open('reports/phase3/stage2_2_audit_data.json', 'w') as f:
    json.dump(audit_data, f, indent=2)

print("Audit data saved to reports/phase3/stage2_2_audit_data.json")
print("\nAUDIT COMPLETE")