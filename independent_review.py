#!/usr/bin/env python3
"""
Independent Acceptance Review — Evidence-based audit
No remediation scripts, no prior reports as proof. Source PDF only.
"""

import pandas as pd
import fitz
import re
import hashlib
from pathlib import Path

print("="*70)
print("INDEPENDENT ACCEPTANCE REVIEW — IFCT TABLE 1")
print("="*70)

# ============================================================
# LOAD ALL ARTIFACTS
# ============================================================
candidate_csv = pd.read_csv('data/interim/ifct_final_candidate/ifct_table1_candidate.csv')
candidate_parquet = pd.read_parquet('data/interim/ifct_final_candidate/ifct_table1_candidate.parquet')
remediation_log = pd.read_csv('data/interim/ifct_final_candidate/ifct_remediation_log.csv')
source_recovery = pd.read_csv('data/interim/ifct_verified/ifct_table1_verified.csv')  # forensic source
recipes = pd.read_parquet('data/processed/recipes.parquet')

print(f"\nCandidate CSV: {len(candidate_csv)} records, {candidate_csv['food_code'].nunique()} unique")
print(f"Candidate Parquet: {len(candidate_parquet)} records, {candidate_parquet['food_code'].nunique()} unique")
print(f"Remediation log: {len(remediation_log)} entries")
print(f"Source recovery (forensic): {len(source_recovery)} records, {source_recovery['food_code'].nunique()} unique")
print(f"Recipe corpus: {len(recipes)} records, {recipes['recipe_id'].nunique()} unique")

# ============================================================
# 1. RECONCILE CHANGE LOG
# ============================================================
print("\n" + "="*70)
print("1. CHANGE LOG RECONCILIATION")
print("="*70)

# Analyze remediation log
print(f"\nRemediation log columns: {list(remediation_log.columns)}")
print(f"Total entries: {len(remediation_log)}")

# Group by operation type
if 'field' in remediation_log.columns:
    field_counts = remediation_log['field'].value_counts()
    print(f"\nField types: {field_counts.to_dict()}")

if 'food_code' in remediation_log.columns:
    codes_in_log = remediation_log['food_code'].nunique()
    print(f"Unique codes affected: {codes_in_log}")
    # Count operations per code
    ops_per_code = remediation_log['food_code'].value_counts()
    multi_op = ops_per_code[ops_per_code > 1]
    if len(multi_op) > 0:
        print(f"Codes with multiple operations: {len(multi_op)}")
        for code, count in multi_op.items():
            ops = remediation_log[remediation_log['food_code'] == code]
            print(f"  {code}: {count} ops - fields: {ops['field'].tolist()}")

# Build record-level accounting by comparing source vs candidate
print("\n--- Record-level accounting (Source vs Candidate) ---")
source_codes = set(source_recovery['food_code'])
cand_codes = set(candidate_csv['food_code'])

removed = source_codes - cand_codes
added = cand_codes - source_codes
common = source_codes & cand_codes

print(f"Removed codes: {sorted(removed)} ({len(removed)})")
print(f"Added codes: {sorted(added)} ({len(added)})")
print(f"Common codes: {len(common)}")

# For common codes, check what changed
changes_detail = []
for code in sorted(common):
    src_row = source_recovery[source_recovery['food_code'] == code].iloc[0]
    cand_row = candidate_csv[candidate_csv['food_code'] == code].iloc[0]
    
    row_changes = []
    for col in ['food_group', 'extraction_method', 'verification_status', 'manual_recovery']:
        if col in src_row and col in cand_row:
            src_val = src_row[col]
            cand_val = cand_row[col]
            if str(src_val) != str(cand_val):
                row_changes.append({
                    'field': col,
                    'previous': src_val,
                    'final': cand_val
                })
    
    # Check nutrient columns
    for col in ['moisture_g', 'protein_g', 'fat_g', 'ash_g', 'fibre_total_g', 
                'fibre_insoluble_g', 'fibre_soluble_g', 'carb_available_g', 'energy_kj',
                'regions', 'food_name', 'source_page']:
        if col in src_row and col in cand_row:
            src_val = src_row[col]
            cand_val = cand_row[col]
            if str(src_val) != str(cand_val):
                row_changes.append({
                    'field': col,
                    'previous': src_val,
                    'final': cand_val
                })
    
    if row_changes:
        changes_detail.append({
            'food_code': code,
            'changes': row_changes
        })

print(f"\nCodes with changes: {len(changes_detail)}")
for c in changes_detail:
    print(f"\n  {c['food_code']}:")
    for ch in c['changes']:
        print(f"    {ch['field']}: '{ch['previous']}' -> '{ch['final']}'")

# ============================================================
# 2. VERIFY H-CODE STANDARDIZATIONS
# ============================================================
print("\n" + "="*70)
print("2. H-CODE STANDARDIZATION VERIFICATION")
print("="*70)

# Get H codes from PDF
pdf_path = "data/raw/nutrition/IFCT_2017/IFCT2017_decrypted.pdf"
doc = fitz.open(pdf_path)
page = doc[55]  # page 56 (0-indexed 55) - wait, H is page 55 (0-indexed 54)
# Let's check all pages for H section
for page_num in [54, 55]:  # pages 55, 56
    page = doc[page_num]
    text = page.get_text()
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if 'NUTS' in line.strip().upper() or 'OIL' in line.strip().upper():
            print(f"Page {page_num+1}, Line {i}: {line.strip()}")
        if re.match(r'^H\d{3}$', line.strip()):
            print(f"Page {page_num+1}, Line {i}: FOOD CODE {line.strip()}")
doc.close()

# Check candidate H codes
h_codes = sorted([c for c in candidate_csv['food_code'] if c.startswith('H')])
print(f"\nCandidate H-codes: {h_codes} ({len(h_codes)})")

for code in h_codes:
    row = candidate_csv[candidate_csv['food_code'] == code].iloc[0]
    src_row = source_recovery[source_recovery['food_code'] == code].iloc[0]
    print(f"  {code}: candidate='{row['food_group']}', source='{src_row['food_group']}'")
    # Check nutrients unchanged
    for col in ['moisture_g', 'protein_g', 'fat_g', 'ash_g', 'energy_kj']:
        if row[col] != src_row[col]:
            print(f"    NUTRIENT CHANGED: {col}: '{src_row[col]}' -> '{row[col]}'")

# ============================================================
# 3. INDEPENDENT FOOD GROUP VALIDATION (ALL 528)
# ============================================================
print("\n" + "="*70)
print("3. INDEPENDENT FOOD GROUP VALIDATION (ALL 528)")
print("="*70)

# Build PDF section map by scanning PDF pages 39-68
doc = fitz.open(pdf_path)
pdf_groups = {}

for page_num in range(38, 68):
    page = doc[page_num]
    text = page.get_text()
    lines = text.split('\n')
    
    current_section = None
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        line_upper = line_stripped.upper()
        
        # Detect section headers (exact matching)
        if line_upper == 'CEREALS AND MILLETS':
            current_section = 'CEREALS AND MILLETS'
        elif line_upper in ['GRAIN LEGUMES', 'PULSES AND LEGUMES']:
            current_section = 'PULSES AND LEGUMES'
        elif line_upper == 'GREEN LEAFY VEGETABLES':
            current_section = 'LEAFY VEGETABLES'
        elif line_upper == 'LEAFY VEGETABLES' and 'GREEN' not in line_upper:
            current_section = 'LEAFY VEGETABLES'
        elif line_upper == 'OTHER VEGETABLES':
            current_section = 'OTHER VEGETABLES'
        elif line_upper == 'FRUITS':
            current_section = 'FRUITS'
        elif line_upper == 'ROOTS AND TUBERS':
            current_section = 'ROOTS AND TUBERS'
        elif line_upper == 'CONDIMENTS AND SPICES-FRESH':
            current_section = 'CONDIMENTS AND SPICES-FRESH'
        elif line_upper == 'CONDIMENTS AND SPICES-DRY':
            current_section = 'CONDIMENTS AND SPICES-DRY'
        elif 'NUTS AND OIL' in line_upper and 'SEED' in line_upper:
            current_section = 'NUTS AND OIL SEEDS'
        elif line_upper == 'MUSHROOMS':
            current_section = 'MUSHROOMS'
        elif line_upper == 'MILK AND MILK PRODUCTS':
            current_section = 'MILK AND MILK PRODUCTS'
        elif line_upper == 'EGG AND EGG PRODUCTS':
            current_section = 'EGG AND EGG PRODUCTS'
        elif line_upper == 'POULTRY':
            current_section = 'POULTRY'
        elif line_upper == 'ANIMAL MEAT':
            current_section = 'ANIMAL MEAT'
        elif line_upper == 'MARINE FISH':
            current_section = 'MARINE FISH'
        elif line_upper == 'MARINE SHELLFISH':
            current_section = 'MARINE SHELLFISH'
        elif line_upper == 'FRESHWATER FISH AND SHELLFISH':
            current_section = 'FRESHWATER FISH AND SHELLFISH'
        elif line_upper in ['SUGARS', 'SUGARS AND JAGGERY']:
            current_section = 'SUGARS AND JAGGERY'
        
        # Detect food codes
        if re.match(r'^[A-Z]\d{3}$', line_stripped):
            code = line_stripped
            if current_section and code not in pdf_groups:
                pdf_groups[code] = (current_section, page_num + 1)

doc.close()

print(f"PDF section assignments found: {len(pdf_groups)}")

# Map PDF section names to standardized group names
pdf_to_std = {
    'CEREALS AND MILLETS': 'CEREALS AND MILLETS',
    'PULSES AND LEGUMES': 'PULSES AND LEGUMES',
    'LEAFY VEGETABLES': 'LEAFY VEGETABLES',
    'OTHER VEGETABLES': 'OTHER VEGETABLES',
    'FRUITS': 'FRUITS',
    'ROOTS AND TUBERS': 'ROOTS AND TUBERS',
    'CONDIMENTS AND SPICES-FRESH': 'CONDIMENTS AND SPICES-FRESH',
    'CONDIMENTS AND SPICES-DRY': 'CONDIMENTS AND SPICES-DRY',
    'NUTS AND OIL SEEDS': 'NUTS AND OILSEEDS',  # standardized
    'MUSHROOMS': 'MUSHROOMS',
    'MILK AND MILK PRODUCTS': 'MILK AND MILK PRODUCTS',
    'EGG AND EGG PRODUCTS': 'EGG AND EGG PRODUCTS',
    'POULTRY': 'POULTRY',
    'ANIMAL MEAT': 'ANIMAL MEAT',
    'MARINE FISH': 'MARINE FISH',
    'MARINE SHELLFISH': 'MARINE SHELLFISH',
    'FRESHWATER FISH AND SHELLFISH': 'FRESHWATER FISH AND SHELLFISH',
    'SUGARS AND JAGGERY': 'SUGARS AND JAGGERY',
}

# Validate each candidate record
validation_results = []
for _, row in candidate_csv.iterrows():
    code = row['food_code']
    candidate_group = row['food_group']
    pdf_info = pdf_groups.get(code)
    
    if pdf_info:
        pdf_section, pdf_page = pdf_info
        expected_group = pdf_to_std.get(pdf_section, pdf_section)
        status = 'PASS' if candidate_group == expected_group else 'FAIL'
    else:
        pdf_section = 'NOT_FOUND'
        pdf_page = None
        expected_group = 'UNKNOWN'
        status = 'UNRESOLVED'
    
    validation_results.append({
        'food_code': code,
        'food_name': row['food_name'],
        'candidate_group': candidate_group,
        'pdf_section': pdf_section,
        'pdf_page': pdf_page,
        'expected_group': expected_group,
        'status': status
    })

val_df = pd.DataFrame(validation_results)
pass_count = (val_df['status'] == 'PASS').sum()
fail_count = (val_df['status'] == 'FAIL').sum()
unresolved_count = (val_df['status'] == 'UNRESOLVED').sum()

print(f"\nValidation Results: PASS={pass_count}, FAIL={fail_count}, UNRESOLVED={unresolved_count}")

if fail_count > 0:
    print("\nFAILURES:")
    for _, r in val_df[val_df['status'] == 'FAIL'].iterrows():
        print(f"  {r['food_code']}: candidate='{r['candidate_group']}', PDF='{r['pdf_section']}' ({r['expected_group']}), page={r['pdf_page']}")

if unresolved_count > 0:
    print("\nUNRESOLVED:")
    for _, r in val_df[val_df['status'] == 'UNRESOLVED'].iterrows():
        print(f"  {r['food_code']}: candidate='{r['candidate_group']}', not found in PDF")

# Save validation file
val_df.to_csv('data/interim/ifct_final_candidate/ifct_independent_group_validation.csv', index=False)
print(f"\nSaved: data/interim/ifct_final_candidate/ifct_independent_group_validation.csv")

# ============================================================
# 4. DATA INTEGRITY CHECKS
# ============================================================
print("\n" + "="*70)
print("4. DATA INTEGRITY CHECKS")
print("="*70)

# 4.1 Exactly 528 unique codes
print(f"4.1 Unique codes: {candidate_csv['food_code'].nunique()} (expected 528)")
assert candidate_csv['food_code'].nunique() == 528

# 4.2 Every code exists in official PDF
pdf_codes = set(pdf_groups.keys())
cand_codes = set(candidate_csv['food_code'])
not_in_pdf = cand_codes - pdf_codes
print(f"4.2 Codes in candidate but not PDF: {sorted(not_in_pdf)}")
assert len(not_in_pdf) == 0

# 4.3 No fabricated records (T-prefix)
t_codes = [c for c in cand_codes if c.startswith('T')]
print(f"4.3 T-prefix codes in candidate: {t_codes}")
assert len(t_codes) == 0

# 4.4 CSV/Parquet equality
print("4.4 CSV/Parquet parity check...")
parity_issues = []
for col in candidate_csv.columns:
    if col in candidate_parquet.columns:
        for code in candidate_csv['food_code']:
            csv_val = candidate_csv[candidate_csv['food_code'] == code][col].values[0]
            parq_val = candidate_parquet[candidate_parquet['food_code'] == code][col].values[0]
            csv_s = str(csv_val) if pd.notna(csv_val) else ''
            parq_s = str(parq_val) if pd.notna(parq_val) else ''
            if csv_s != parq_s:
                parity_issues.append((code, col, csv_s, parq_s))

print(f"   Parity mismatches: {len(parity_issues)}")
if parity_issues:
    for code, col, csv_v, parq_v in parity_issues[:5]:
        print(f"   {code}.{col}: CSV='{csv_v}' vs Parquet='{parq_v}'")

# 4.5 Nutrient preservation vs source
print("4.5 Nutrient preservation vs source recovery...")
nutrient_cols = ['moisture_g', 'protein_g', 'fat_g', 'ash_g', 'fibre_total_g', 
                 'fibre_insoluble_g', 'fibre_soluble_g', 'carb_available_g', 'energy_kj',
                 'regions', 'food_name', 'source_page']
nutrient_diffs = 0
for code in sorted(cand_codes & set(source_recovery['food_code'])):
    for col in nutrient_cols:
        if col in candidate_csv.columns and col in source_recovery.columns:
            c_val = candidate_csv[candidate_csv['food_code'] == code][col].values[0]
            s_val = source_recovery[source_recovery['food_code'] == code][col].values[0]
            c_s = str(c_val) if pd.notna(c_val) else ''
            s_s = str(s_val) if pd.notna(s_val) else ''
            if c_s != s_s:
                nutrient_diffs += 1
                if nutrient_diffs <= 5:
                    print(f"   DIFF: {code}.{col}: candidate='{c_s}' vs source='{s_s}'")

print(f"   Total nutrient/field differences vs source: {nutrient_diffs}")

# 4.6 Manual recoveries
print("\n4.6 Manual recovery verification:")
genuine = ['D001', 'E004', 'G013', 'H005']
for code in genuine:
    row = candidate_csv[candidate_csv['food_code'] == code]
    if len(row) == 0:
        print(f"  {code}: MISSING from candidate!")
    else:
        r = row.iloc[0]
        pdf_info = pdf_groups.get(code)
        if pdf_info:
            pdf_section, pdf_page = pdf_info
            expected = pdf_to_std.get(pdf_section, pdf_section)
            match = r['food_group'] == expected
            print(f"  {code}: candidate='{r['food_group']}', PDF_section='{pdf_section}' (page {pdf_page}), expected='{expected}', MATCH={match}")
        else:
            print(f"  {code}: candidate='{r['food_group']}', NOT FOUND in PDF scan")

# 4.7 T001-T014 absent
print(f"\n4.7 T001-T014 in candidate: {[c for c in cand_codes if c.startswith('T')]}")

# 4.8 Recipe corpus
print(f"\n4.8 Recipe corpus: {len(recipes)} records (expected 6865), PK unique: {recipes['recipe_id'].nunique()}")
assert len(recipes) == 6865
assert recipes['recipe_id'].nunique() == 6865

# 4.9 PDF hashes
print("\n4.9 PDF Provenance:")
for name, path in [("Official", "data/raw/nutrition/IFCT_2017/IFCT2017.pdf"),
                    ("Decrypted", "data/raw/nutrition/IFCT_2017/IFCT2017_decrypted.pdf")]:
    with open(path, 'rb') as f:
        sha256 = hashlib.sha256(f.read()).hexdigest()
    doc = fitz.open(path)
    print(f"   {name}: {sha256} ({len(doc)} pages)")
    doc.close()

print("\n" + "="*70)
print("INDEPENDENT REVIEW COMPLETE")
print("="*70)