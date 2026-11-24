#!/usr/bin/env python3
"""
Final verification after G013 correction
"""

import pandas as pd
from pathlib import Path

# Load corrected files
candidate_csv = pd.read_csv('data/interim/ifct_final_candidate/ifct_table1_candidate.csv')
candidate_parquet = pd.read_parquet('data/interim/ifct_final_candidate/ifct_table1_candidate.parquet')
remediation_log = pd.read_csv('data/interim/ifct_final_candidate/ifct_remediation_log.csv')

print("=== FINAL VERIFICATION AFTER G013 CORRECTION ===\n")

# 1. 528 unique records
print(f"1. Unique codes: {candidate_csv['food_code'].nunique()} (expected 528) {'✅' if candidate_csv['food_code'].nunique() == 528 else '❌'}")

# 2. G013 corrected
g013 = candidate_csv[candidate_csv['food_code'] == 'G013'].iloc[0]
print(f"\n2. G013 status:")
print(f"   Group: {g013['food_group']} (expected CONDIMENTS AND SPICES-FRESH) {'✅' if g013['food_group'] == 'CONDIMENTS AND SPICES-FRESH' else '❌'}")
print(f"   Method: {g013['extraction_method']} (expected manual) {'✅' if g013['extraction_method'] == 'manual' else '❌'}")
print(f"   Status: {g013['verification_status']} (expected verified_pdf) {'✅' if g013['verification_status'] == 'verified_pdf' else '❌'}")
print(f"   Manual: {g013['manual_recovery']} (expected True) {'✅' if g013['manual_recovery'] == True else '❌'}")

# 3. Nutrient values preserved for G013
nutrient_cols = ['moisture_g', 'protein_g', 'fat_g', 'ash_g', 'fibre_total_g', 
                 'fibre_insoluble_g', 'fibre_soluble_g', 'carb_available_g', 'energy_kj',
                 'regions', 'food_name', 'source_page']
print(f"\n3. G013 nutrient fields:")
for col in nutrient_cols:
    if col in candidate_csv.columns:
        val = g013[col]
        print(f"   {col}: {val}")

# 4. CSV/Parquet parity
parity_issues = 0
for col in candidate_csv.columns:
    if col in candidate_parquet.columns:
        for code in candidate_csv['food_code']:
            csv_val = candidate_csv[candidate_csv['food_code'] == code][col].values[0]
            parq_val = candidate_parquet[candidate_parquet['food_code'] == code][col].values[0]
            csv_s = str(csv_val) if pd.notna(csv_val) else ''
            parq_s = str(parq_val) if pd.notna(parq_val) else ''
            if csv_s != parq_s:
                parity_issues += 1
                print(f"   MISMATCH: {code}.{col}: CSV='{csv_s}' vs Parquet='{parq_s}'")
print(f"\n4. CSV/Parquet parity: {parity_issues} mismatches {'✅' if parity_issues == 0 else '❌'}")

# 5. No other record changed - check remediation log
print(f"\n5. Remediation log entries: {len(remediation_log)}")
g013_logs = remediation_log[remediation_log['food_code'] == 'G013']
print(f"   G013 log entries: {len(g013_logs)}")
for _, row in g013_logs.iterrows():
    print(f"     {row['field']}: '{row['previous_value']}' -> '{row['corrected_value']}' (p{row['pdf_page']})")

# 6. All 4 manual recoveries correct
print(f"\n6. Manual recoveries:")
for code in ['D001', 'E004', 'G013', 'H005']:
    row = candidate_csv[candidate_csv['food_code'] == code].iloc[0]
    pdf_group = {'D001': 'OTHER VEGETABLES', 'E004': 'FRUITS', 'G013': 'CONDIMENTS AND SPICES-FRESH', 'H005': 'NUTS AND OILSEEDS'}[code]
    match = row['food_group'] == pdf_group
    print(f"   {code}: {row['food_group']} (PDF: {pdf_group}) {'✅' if match else '❌'}")

# 7. Total unique codes
print(f"\n7. Total unique codes: {candidate_csv['food_code'].nunique()} {'✅' if candidate_csv['food_code'].nunique() == 528 else '❌'}")

print("\n=== ALL VERIFICATIONS COMPLETE ===")