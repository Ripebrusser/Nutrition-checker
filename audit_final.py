import pandas as pd
import hashlib
import fitz
from pathlib import Path

# 1. Verify CSV and Parquet identical
print("=== 1. CSV vs Parquet Verification ===")
csv_df = pd.read_csv('data/interim/ifct_verified/ifct_table1_verified.csv')
parquet_df = pd.read_parquet('data/interim/ifct_verified/ifct_table1_verified.parquet')

print(f"CSV rows: {len(csv_df)}, Parquet rows: {len(parquet_df)}")
print(f"CSV unique codes: {csv_df['food_code'].nunique()}, Parquet unique codes: {parquet_df['food_code'].nunique()}")

# Check food codes match
csv_codes = set(csv_df['food_code'].sort_values().values)
parquet_codes = set(parquet_df['food_code'].sort_values().values)
print(f"Codes identical: {csv_codes == parquet_codes}")

# Check nutrient values match for common columns
common_cols = [c for c in csv_df.columns if c in parquet_df.columns]
for col in common_cols:
    if col in ['food_code', 'food_name', 'regions', 'food_group', 'source_page', 'source_table', 'extraction_method', 'verification_status', 'manual_recovery']:
        csv_vals = csv_df[col].sort_values().reset_index(drop=True)
        parquet_vals = parquet_df[col].sort_values().reset_index(drop=True)
        match = csv_vals.equals(parquet_vals)
        if not match:
            print(f"  MISMATCH in {col}")
    else:
        # Numeric columns - compare as strings to avoid float precision
        csv_vals = csv_df[col].astype(str).sort_values().reset_index(drop=True)
        parquet_vals = parquet_df[col].astype(str).sort_values().reset_index(drop=True)
        match = csv_vals.equals(parquet_vals)
        if not match:
            print(f"  MISMATCH in {col}")

print("CSV/Parquet verification complete")

# 2. Authoritative food codes from PDF
print("\n=== 2. PDF Food Code Inventory ===")
pdf_path = "data/raw/nutrition/IFCT_2017/IFCT2017_decrypted.pdf"
doc = fitz.open(pdf_path)
print(f"PDF pages: {len(doc)}")

all_pdf_codes = set()
for page_num in range(38, 68):  # pages 39-68 (0-indexed 38-67)
    page = doc[page_num]
    text = page.get_text()
    import re
    codes = re.findall(r'[A-Z]\d{3}', text)
    for c in codes:
        all_pdf_codes.add(c)

print(f"Unique food codes found in PDF pages 39-68: {len(all_pdf_codes)}")
print(f"Codes: {sorted(all_pdf_codes)}")

# Check which codes in recovery not in PDF, and vice versa
recovery_codes = set(csv_df['food_code'].values)
print(f"\nRecovery codes not in PDF: {recovery_codes - all_pdf_codes}")
print(f"PDF codes not in recovery: {all_pdf_codes - recovery_codes}")

doc.close()

# 3. Investigate J009
print("\n=== 3. J009 Investigation ===")
print(f"J009 in PDF codes: {'J009' in all_pdf_codes}")
print(f"J009 in recovery: {'J009' in recovery_codes}")

# Search for J009 specifically in PDF
doc = fitz.open(pdf_path)
for page_num in range(38, 68):
    page = doc[page_num]
    text = page.get_text()
    if 'J009' in text:
        print(f"J009 found on page {page_num+1}")
        # Show context
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if 'J009' in line:
                print(f"  Line {i}: {line.strip()}")
                if i > 0: print(f"  Line {i-1}: {lines[i-1].strip()}")
                if i < len(lines)-1: print(f"  Line {i+1}: {lines[i+1].strip()}")
doc.close()

# 4. Reconcile v15 counts
print("\n=== 4. v15 Count Reconciliation ===")
# Check v15 output
v15_csv = 'data/interim/ifct_extracted/table1_parsed.csv'
if Path(v15_csv).exists():
    v15_df = pd.read_csv(v15_csv)
    print(f"v15 output rows: {len(v15_df)}, unique codes: {v15_df['food_code'].nunique()}")
    print(f"v15 groups: {v15_df['food_group'].value_counts().to_dict()}")
else:
    print("v15 output not found")

# 5. Validate ALL food-group assignments
print("\n=== 5. Full Group Assignment Validation ===")
# Expected group by prefix
prefix_to_group = {
    'A': 'CEREALS AND MILLETS',
    'B': 'PULSES AND LEGUMES',
    'C': 'LEAFY VEGETABLES',
    'D': 'OTHER VEGETABLES',
    'E': 'FRUITS',
    'F': 'ROOTS AND TUBERS',
    'G': 'CONDIMENTS AND SPICES-FRESH',  # G has both fresh and dry
    'H': 'NUTS AND OILSEEDS',
    'I': 'SUGARS AND JAGGERY',
    'J': 'MUSHROOMS',
    'K': 'SUGARS AND JAGGERY',
    'L': 'MILK AND MILK PRODUCTS',
    'M': 'EGG AND EGG PRODUCTS',
    'N': 'POULTRY',
    'O': 'ANIMAL MEAT',
    'P': 'MARINE FISH',
    'Q': 'MARINE SHELLFISH',
    'R': 'UNKNOWN',
    'S': 'FRESHWATER FISH AND SHELLFISH',
    'T': 'FRESHWATER FISH AND SHELLFISH',
}

# Check each record
mismatches = []
for _, row in csv_df.iterrows():
    code = row['food_code']
    prefix = code[0]
    expected = prefix_to_group.get(prefix, 'UNKNOWN')
    actual = row['food_group']
    if expected != actual:
        mismatches.append({
            'food_code': code,
            'food_name': row['food_name'],
            'prefix': prefix,
            'expected': expected,
            'actual': actual,
            'page': row['source_page'],
            'method': row['extraction_method']
        })

print(f"Total records: {len(csv_df)}")
print(f"Group mismatches: {len(mismatches)}")
if mismatches:
    for m in mismatches:
        print(f"  {m['food_code']} ({m['food_name'][:40]}): expected {m['expected']}, got {m['actual']} [page {m['page']}, {m['method']}]")

# 6. Verify 18 manual recoveries
print("\n=== 6. Manual Recovery Verification ===")
manual_log = pd.read_csv('data/interim/ifct_verified/ifct_manual_recovery_log.csv')
print(f"Manual recovery log entries: {len(manual_log)}")
for _, row in manual_log.iterrows():
    print(f"  {row['food_code']}: {row['food_name'][:50]} -> {row['food_group']} (page {row['source_page']})")

# 7. Nutrient values preservation
print("\n=== 7. Nutrient Values Check ===")
nutrient_cols = ['moisture_g', 'protein_g', 'fat_g', 'ash_g', 'fibre_total_g', 'fibre_insoluble_g', 'fibre_soluble_g', 'carb_available_g', 'energy_kj']
for col in nutrient_cols:
    if col in csv_df.columns:
        non_null = csv_df[col].notna().sum()
        print(f"  {col}: {non_null}/{len(csv_df)} ({non_null/len(csv_df)*100:.1f}%)")
        # Check for ± notation preservation
        if csv_df[col].dtype == 'object':
            with_pm = csv_df[col].astype(str).str.contains('±').sum()
            print(f"    ± notation: {with_pm}/{non_null}")

# 8. PDF hashes
print("\n=== 8. PDF Hash Verification ===")
official_pdf = "data/raw/nutrition/IFCT_2017/IFCT2017.pdf"
decrypted_pdf = "data/raw/nutrition/IFCT_2017/IFCT2017_decrypted.pdf"

for name, path in [("Official", official_pdf), ("Decrypted", decrypted_pdf)]:
    if Path(path).exists():
        with open(path, 'rb') as f:
            sha256 = hashlib.sha256(f.read()).hexdigest()
        doc = fitz.open(path)
        print(f"{name} PDF: {path}")
        print(f"  SHA-256: {sha256}")
        print(f"  Pages: {len(doc)}")
        doc.close()
    else:
        print(f"{name} PDF not found: {path}")

# 9. Recipe corpus
print("\n=== 9. Recipe Corpus Verification ===")
recipes = pd.read_parquet('data/processed/recipes.parquet')
print(f"Recipes: {len(recipes)} rows, {recipes['recipe_id'].nunique()} unique IDs")

# 10. INDB verification
print("\n=== 10. INDB Verification ===")
indb = pd.read_parquet('data/processed/indb_foods.parquet')
print(f"INDB: {len(indb)} rows, {indb['food_code'].nunique()} unique codes")
print(f"Columns: {list(indb.columns)}")
# Check if it has per_serving columns (indicates prepared dishes)
per_serving_cols = [c for c in indb.columns if 'per_serving' in c.lower() or 'serving' in c.lower()]
print(f"Per-serving columns: {per_serving_cols}")

print("\n=== AUDIT COMPLETE ===")