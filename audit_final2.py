import pandas as pd
import fitz
import re

# Verify CSV/Parquet mismatch is just representation
print("=== CSV/Parquet Actual Value Check ===")
csv_df = pd.read_csv('data/interim/ifct_verified/ifct_table1_verified.csv')
parquet_df = pd.read_parquet('data/interim/ifct_verified/ifct_table1_verified.parquet')

for col in ['regions', 'fibre_total_g', 'fibre_insoluble_g', 'fibre_soluble_g']:
    # Compare by food_code
    mismatches = 0
    for code in csv_df['food_code']:
        csv_v = csv_df[csv_df['food_code'] == code][col].values[0]
        parq_v = parquet_df[parquet_df['food_code'] == code][col].values[0]
        # Normalize: both NaN -> same, both empty -> same
        csv_s = str(csv_v) if pd.notna(csv_v) else ''
        parq_s = str(parq_v) if pd.notna(parq_v) else ''
        if csv_s != parq_s:
            mismatches += 1
            if mismatches <= 3:
                print(f"  {code}: CSV='{csv_s}' vs Parquet='{parq_s}'")
    print(f"{col}: {mismatches} actual mismatches out of 542")

# Check the authoritative PDF code count vs recovery
print("\n=== Authoritative PDF Code Count ===")
pdf_path = "data/raw/nutrition/IFCT_2017/IFCT2017_decrypted.pdf"
doc = fitz.open(pdf_path)
all_codes = set()
for page_num in range(38, 68):
    page = doc[page_num]
    text = page.get_text()
    codes = re.findall(r'[A-Z]\d{3}', text)
    for c in codes:
        all_codes.add(c)
print(f"Total unique codes in PDF pages 39-68: {len(all_codes)}")

# Count by prefix
from collections import Counter
prefix_counts = Counter([c[0] for c in all_codes])
for p in sorted(prefix_counts):
    print(f"  {p}: {prefix_counts[p]}")

doc.close()

# Recovery codes by prefix
recovery_codes = set(csv_df['food_code'].values)
rec_prefix_counts = Counter([c[0] for c in recovery_codes])
print(f"\nRecovery codes by prefix:")
for p in sorted(rec_prefix_counts):
    print(f"  {p}: {rec_prefix_counts[p]}")

# Extra codes in recovery not in PDF
extra = recovery_codes - all_codes
print(f"\nExtra codes in recovery (not in PDF): {sorted(extra)}")

# Missing codes from PDF not in recovery
missing = all_codes - recovery_codes
print(f"Missing codes from PDF: {sorted(missing)}")

# Check J009 specifically
print(f"\nJ009 in PDF: {'J009' in all_codes}")
print(f"J009 in recovery: {'J009' in recovery_codes}")

# Check what J codes exist
j_codes = [c for c in all_codes if c.startswith('J')]
print(f"J codes in PDF: {sorted(j_codes)}")
j_codes_rec = [c for c in recovery_codes if c.startswith('J')]
print(f"J codes in recovery: {sorted(j_codes_rec)}")