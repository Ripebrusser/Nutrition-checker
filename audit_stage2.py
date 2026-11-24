"""Independent Audit of Stage 2 Outputs"""

import pandas as pd
import numpy as np
import hashlib

print("="*80)
print("STAGE 2 INDEPENDENT AUDIT")
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

hashes = {}
for name, path in frozen_files.items():
    with open(path, 'rb') as f:
        h = hashlib.sha256(f.read()).hexdigest()
    hashes[name] = h
    print(f"  {name}: {h}")

# ============================================================
# 2. INPUT DATA ANALYSIS
# ============================================================
print("\n2. INPUT DATA ANALYSIS")
print("-"*40)

# Load parsed ingredients (Stage 2 input)
parsed = pd.read_parquet('data/interim/phase2/parsed_recipe_ingredients.parquet')
print(f"  Parsed ingredient records: {len(parsed)}")
print(f"  Unique recipe_ids: {parsed['recipe_id'].nunique()}")

# Check for ingredient_record_id - does it exist?
if 'ingredient_record_id' in parsed.columns:
    print(f"  Unique ingredient_record_ids: {parsed['ingredient_record_id'].nunique()}")
else:
    print("  No ingredient_record_id column found")
    # Create synthetic record ID from index
    parsed['ingredient_record_id'] = parsed.index

# Unique normalized ingredient expressions
unique_normalized = parsed['normalized_ingredient'].nunique()
print(f"  Unique normalized_ingredient expressions: {unique_normalized}")

# Unique ingredient_name expressions
unique_ingredient_name = parsed['ingredient_name'].nunique()
print(f"  Unique ingredient_name expressions: {unique_ingredient_name}")

# Source field breakdown
print(f"  Source field breakdown:")
print(f"    ingredients_raw: {(parsed['source_field'] == 'ingredients_raw').sum()}")
print(f"    ingredients_en: {(parsed['source_field'] == 'ingredients_en').sum()}")

# Check if raw and English represent same canonical ingredients
# Look at source_reconciliation
print(f"  Source reconciliation breakdown:")
print(parsed['source_reconciliation'].value_counts().to_dict())

# ============================================================
# 3. OUTPUT DATA ANALYSIS
# ============================================================
print("\n3. OUTPUT DATA ANALYSIS")
print("-"*40)

candidates = pd.read_parquet('data/interim/phase3/ifct_match_candidates.parquet')
print(f"  Candidate records: {len(candidates)}")

# Unique source ingredients in candidates
unique_matched_ingredient_name = candidates['matched_ingredient_name'].nunique()
unique_matched_normalized = candidates['normalized_ingredient'].nunique()
print(f"  Unique matched ingredient_name: {unique_matched_ingredient_name}")
print(f"  Unique matched normalized_ingredient: {unique_matched_normalized}")

# Unique IFCT food codes
unique_ifct_codes = candidates['ifct_food_code'].nunique()
print(f"  Unique IFCT food codes: {unique_ifct_codes}")

# Unique recipes with candidates
unique_recipes_with_candidates = candidates['recipe_id'].nunique()
print(f"  Unique recipes with candidates: {unique_recipes_with_candidates}")

# Duplicate candidate records (same recipe_id + matched_ingredient_name + ifct_food_code)
dup_key = candidates.duplicated(subset=['recipe_id', 'matched_ingredient_name', 'ifct_food_code']).sum()
print(f"  Duplicate candidate records (same recipe+ingredient+ifct): {dup_key}")

# Candidates per ingredient
cands_per_ingredient = candidates.groupby('matched_ingredient_name').size()
print(f"  Candidates per ingredient:")
print(f"    Mean: {cands_per_ingredient.mean():.2f}")
print(f"    Median: {cands_per_ingredient.median()}")
print(f"    Max: {cands_per_ingredient.max()}")
print(f"    Min: {cands_per_ingredient.min()}")

# Candidate count distribution
dist = cands_per_ingredient.value_counts().sort_index()
print(f"  Candidate count distribution:")
for cnt, freq in dist.items():
    print(f"    {cnt} candidate(s): {freq} ingredients")

# Check for invalid IFCT codes
valid_ifct_codes = set(pd.read_parquet('data/interim/ifct_final_candidate/ifct_table1_candidate.parquet')['food_code'])
invalid_codes = set(candidates['ifct_food_code'].unique()) - valid_ifct_codes
print(f"  Invalid/nonexistent IFCT codes: {len(invalid_codes)}")
if invalid_codes:
    print(f"    {invalid_codes}")

# Missing candidate evidence
missing_evidence = candidates['evidence'].isna().sum()
print(f"  Missing evidence: {missing_evidence}")

# Missing source provenance
missing_source = candidates['source_field'].isna().sum()
print(f"  Missing source_field: {missing_source}")

# ============================================================
# 4. METHOD COUNT AUDIT
# ============================================================
print("\n4. MATCH METHOD AUDIT")
print("-"*40)

method_counts = candidates['match_method'].value_counts()
print(f"  Method counts:")
for method, count in method_counts.items():
    print(f"    {method}: {count}")

# Check if methods are mutually exclusive per (recipe_id, matched_ingredient_name)
method_per_ingredient = candidates.groupby(['recipe_id', 'matched_ingredient_name'])['match_method'].nunique()
overlapping = (method_per_ingredient > 1).sum()
print(f"  Ingredients with multiple methods: {overlapping}")

if overlapping > 0:
    # Show examples
    multi_method = candidates.groupby(['recipe_id', 'matched_ingredient_name'])['match_method'].apply(set).reset_index()
    multi_method = multi_method[multi_method['match_method'].apply(len) > 1]
    print(f"  Examples of overlapping methods:")
    for _, row in multi_method.head(5).iterrows():
        print(f"    Recipe {row['recipe_id']}, '{row['matched_ingredient_name']}': {row['match_method']}")

# ============================================================
# 5. CONFIDENCE CLASSIFICATION AUDIT
# ============================================================
print("\n5. CONFIDENCE CLASSIFICATION AUDIT")
print("-"*40)

conf_counts = candidates['provisional_confidence'].value_counts()
print(f"  Confidence counts:")
for conf, count in conf_counts.items():
    print(f"    {conf}: {count}")

# Check classification logic
# HIGH should be EXACT or SYNONYM with high confidence
high_exact = candidates[(candidates['provisional_confidence'] == 'HIGH') & (candidates['match_method'] == 'EXACT')].shape[0]
high_syn = candidates[(candidates['provisional_confidence'] == 'HIGH') & (candidates['match_method'] == 'SYNONYM')].shape[0]
high_token = candidates[(candidates['provisional_confidence'] == 'HIGH') & (candidates['match_method'] == 'TOKEN_SIMILARITY')].shape[0]
print(f"  HIGH confidence breakdown:")
print(f"    EXACT: {high_exact}")
print(f"    SYNONYM: {high_syn}")
print(f"    TOKEN_SIMILARITY: {high_token}")

# Check requires_review flag
review_counts = candidates['requires_review'].value_counts()
print(f"  Requires review:")
for val, count in review_counts.items():
    print(f"    {val}: {count}")

# ============================================================
# 6. UNMATCHED ANALYSIS
# ============================================================
print("\n6. UNMATCHED ANALYSIS")
print("-"*40)

unmatched = pd.read_parquet('data/interim/phase3/unmatched_ingredients.parquet')
print(f"  Unmatched records: {len(unmatched)}")
print(f"  Unique unmatched ingredient_name: {unmatched['ingredient_name'].nunique()}")
print(f"  Unique unmatched normalized_ingredient: {unmatched['normalized_ingredient'].nunique()}")

# Reconcile counts
total_records = len(parsed)
total_unique_ingredient_name = parsed['ingredient_name'].nunique()
matched_records = len(candidates)  # But this is candidate records, not ingredient records
matched_unique_ingredient_name = candidates['matched_ingredient_name'].nunique()
unmatched_records = len(unmatched)
unmatched_unique_ingredient_name = unmatched['ingredient_name'].nunique()

print(f"\n  COUNT RECONCILIATION:")
print(f"    Total ingredient records: {total_records}")
print(f"    Total unique ingredient_name: {total_unique_ingredient_name}")
print(f"    Unique ingredient_name with candidates: {matched_unique_ingredient_name}")
print(f"    Unique ingredient_name without candidates: {unmatched_unique_ingredient_name}")
print(f"    Sum unique (matched + unmatched): {matched_unique_ingredient_name + unmatched_unique_ingredient_name}")

# Records with/without candidates - need to map back to parsed records
# An ingredient record has candidates if its ingredient_name appears in candidates
matched_ingredient_names_set = set(candidates['matched_ingredient_name'].unique())
parsed['has_candidates'] = parsed['ingredient_name'].isin(matched_ingredient_names_set)

records_with_candidates = parsed['has_candidates'].sum()
records_without_candidates = (~parsed['has_candidates']).sum()
print(f"    Ingredient records with candidates: {records_with_candidates}")
print(f"    Ingredient records without candidates: {records_without_candidates}")
print(f"    Sum records: {records_with_candidates + records_without_candidates}")

# Percentages
print(f"\n  PERCENTAGES:")
print(f"    Unmatched records / total records: {records_without_candidates/total_records*100:.1f}%")
print(f"    Matched records / total records: {records_with_candidates/total_records*100:.1f}%")
print(f"    Unmatched unique / total unique: {unmatched_unique_ingredient_name/total_unique_ingredient_name*100:.1f}%")
print(f"    Matched unique / total unique: {matched_unique_ingredient_name/total_unique_ingredient_name*100:.1f}%")

# ============================================================
# 7. NEGATIVE CONTROL AUDIT
# ============================================================
print("\n7. NEGATIVE CONTROL AUDIT")
print("-"*40)

# Read the negative control report
with open('reports/phase3/stage2_negative_control_report.md', 'r') as f:
    nc_report = f.read()

# Parse the summary table
print("  Report content check:")
if "36/40 test cases behave correctly (90%)" in nc_report:
    print("    Found: 36/40 = 90% claim")
if "Total Tests" in nc_report:
    print("    Found test summary table")

# ============================================================
# 8. TEST ACCOUNTING
# ============================================================
print("\n8. TEST ACCOUNTING")
print("-"*40)

# Run tests and count
import subprocess
result = subprocess.run(['py', '-m', 'pytest', 'tests/', '-v', '--tb=no', '-q'], 
                       capture_output=True, text=True, timeout=120)
output = result.stdout

# Count tests
lines = output.strip().split('\n')
passed = sum(1 for l in lines if 'PASSED' in l)
failed = sum(1 for l in lines if 'FAILED' in l)
skipped = sum(1 for l in lines if 'SKIPPED' in l)
print(f"  Test run results:")
print(f"    Passed: {passed}")
print(f"    Failed: {failed}")
print(f"    Skipped: {skipped}")
print(f"    Total: {passed + failed + skipped}")

# List failed tests
for l in lines:
    if 'FAILED' in l:
        print(f"    FAIL: {l.strip()}")

# ============================================================
# 9. SAVE AUDIT RESULTS
# ============================================================
print("\n9. AUDIT COMPLETE")
print("-"*40)

# Save detailed results to file
audit_data = {
    'frozen_hashes': hashes,
    'total_parsed_records': int(total_records),
    'unique_recipe_ids': int(parsed['recipe_id'].nunique()),
    'unique_ingredient_record_ids': int(parsed['ingredient_record_id'].nunique()),
    'unique_normalized_expressions': int(unique_normalized),
    'unique_ingredient_name_expressions': int(total_unique_ingredient_name),
    'unique_with_candidates': int(matched_unique_ingredient_name),
    'unique_without_candidates': int(unmatched_unique_ingredient_name),
    'records_with_candidates': int(records_with_candidates),
    'records_without_candidates': int(records_without_candidates),
    'candidate_records': int(len(candidates)),
    'unique_ifct_codes_matched': int(unique_ifct_codes),
    'duplicate_candidates': int(dup_key),
    'invalid_ifct_codes': len(invalid_codes),
    'missing_evidence': int(missing_evidence),
    'method_counts': method_counts.to_dict(),
    'overlapping_methods': int(overlapping),
    'confidence_counts': conf_counts.to_dict(),
    'high_breakdown': {'EXACT': int(high_exact), 'SYNONYM': int(high_syn), 'TOKEN_SIMILARITY': int(high_token)},
    'review_counts': review_counts.to_dict(),
    'unmatched_records': int(unmatched_records),
    'unmatched_unique': int(unmatched_unique_ingredient_name),
    'pct_unmatched_records': records_without_candidates/total_records*100,
    'pct_matched_records': records_with_candidates/total_records*100,
    'pct_unmatched_unique': unmatched_unique_ingredient_name/total_unique_ingredient_name*100,
    'pct_matched_unique': matched_unique_ingredient_name/total_unique_ingredient_name*100,
    'test_passed': passed,
    'test_failed': failed,
    'test_skipped': skipped,
}

import json
with open('reports/phase3/stage2_audit_data.json', 'w') as f:
    json.dump(audit_data, f, indent=2)

print("  Audit data saved to reports/phase3/stage2_audit_data.json")