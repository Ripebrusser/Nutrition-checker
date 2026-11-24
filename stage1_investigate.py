import pandas as pd
import fitz
import re

print("=== STAGE 1 INVESTIGATION ===\n")

# Load current recovery
csv_df = pd.read_csv('data/interim/ifct_verified/ifct_table1_verified.csv')
print(f"Current recovery: {len(csv_df)} records, {csv_df['food_code'].nunique()} unique codes")

# 1. Reconcile 65 vs 66 misclassifications
print("\n=== 1. Misclassification Count Reconciliation ===")

# Expected group by prefix (from PDF section headers)
prefix_to_group = {
    'A': 'CEREALS AND MILLETS',
    'B': 'PULSES AND LEGUMES',
    'C': 'LEAFY VEGETABLES',
    'D': 'OTHER VEGETABLES',
    'E': 'FRUITS',
    'F': 'ROOTS AND TUBERS',
    'G': 'CONDIMENTS AND SPICES-FRESH',  # Need to check Fresh vs Dry per page
    'H': 'NUTS AND OIL SEEDS',
    'I': 'SUGARS AND JAGGERY',
    'J': 'MUSHROOMS',
    'K': 'SUGARS AND JAGGERY',
    'L': 'MILK AND MILK PRODUCTS',
    'M': 'EGG AND EGG PRODUCTS',
    'N': 'POULTRY',
    'O': 'ANIMAL MEAT',
    'P': 'MARINE FISH',
    'Q': 'MARINE SHELLFISH',
    'R': 'MARINE SHELLFISH',  # PDF shows R under MARINE SHELLFISH
    'S': 'FRESHWATER FISH AND SHELLFISH',
    'T': 'FRESHWATER FISH AND SHELLFISH',  # But T doesn't exist in PDF
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

print(f"Total mismatches by prefix mapping: {len(mismatches)}")

# Group by expected vs actual
from collections import Counter
mismatch_types = Counter([(m['expected'], m['actual']) for m in mismatches])
for (exp, act), cnt in mismatch_types.most_common():
    codes = [m['food_code'] for m in mismatches if m['expected']==exp and m['actual']==act]
    print(f"  {exp} -> {act}: {cnt} records (e.g., {codes[:5]})")

# 2. Check G013 specifically
print("\n=== 2. G013 Status ===")
g013_row = csv_df[csv_df['food_code'] == 'G013']
if len(g013_row) > 0:
    r = g013_row.iloc[0]
    print(f"  G013 in recovery: group={r['food_group']}, method={r['extraction_method']}, page={r['source_page']}")
    # Is G013 in G001-G033 range?
    print(f"  G013 in G001-G033 range: Yes")
else:
    print("  G013 NOT in recovery")

# Check all G codes in recovery
g_codes = sorted([c for c in csv_df['food_code'] if c.startswith('G')])
print(f"  G codes in recovery: {g_codes}")
print(f"  Count: {len(g_codes)}")

# 3. Verify 4 genuine manual recoveries in PDF
print("\n=== 3. Manual Recovery PDF Verification ===")
pdf_path = "data/raw/nutrition/IFCT_2017/IFCT2017_decrypted.pdf"
doc = fitz.open(pdf_path)

genuine_codes = ['D001', 'E004', 'G013', 'H005']
for code in genuine_codes:
    found = False
    for page_num in range(38, 68):
        page = doc[page_num]
        text = page.get_text()
        if code in text:
            # Show context
            idx = text.find(code)
            context = text[max(0,idx-200):idx+300]
            print(f"  {code}: FOUND on page {page_num+1}")
            print(f"    Context: ...{context[:200]}...")
            found = True
            break
    if not found:
        print(f"  {code}: NOT FOUND in PDF pages 39-68")

doc.close()

# 4. Confirm T001-T014 absent
print("\n=== 4. T-Prefix Verification ===")
doc = fitz.open(pdf_path)
t_found = []
for page_num in range(38, 68):
    page = doc[page_num]
    text = page.get_text()
    for i in range(1, 15):
        code = f'T{i:03d}'
        if code in text:
            t_found.append((code, page_num+1))
if t_found:
    for code, pg in t_found:
        print(f"  {code}: FOUND on page {pg}")
else:
    print("  T001-T014: NOT FOUND in PDF pages 39-68")
doc.close()

# 5. Exact authoritative inventory
print("\n=== 5. Authoritative Inventory (528 codes) ===")
doc = fitz.open(pdf_path)
all_codes = set()
code_to_page = {}
for page_num in range(38, 68):
    page = doc[page_num]
    text = page.get_text()
    codes = re.findall(r'[A-Z]\d{3}', text)
    for c in codes:
        all_codes.add(c)
        if c not in code_to_page:
            code_to_page[c] = page_num + 1

print(f"Total unique codes in PDF: {len(all_codes)}")
from collections import Counter
prefix_counts = Counter([c[0] for c in all_codes])
for p in sorted(prefix_counts):
    codes_in_prefix = sorted([c for c in all_codes if c.startswith(p)])
    print(f"  {p}: {prefix_counts[p]} codes ({codes_in_prefix[0]}–{codes_in_prefix[-1]})")

doc.close()

# 6. Check which codes in recovery are NOT in PDF (fabricated)
print("\n=== 6. Fabricated Records in Recovery ===")
recovery_codes = set(csv_df['food_code'].values)
pdf_codes = set(all_codes)
extra = recovery_codes - pdf_codes
print(f"Codes in recovery but NOT in PDF: {sorted(extra)}")

# 7. Check which PDF codes are missing from recovery
missing = pdf_codes - recovery_codes
print(f"Codes in PDF but missing from recovery: {sorted(missing)}")

# 8. Detailed G-section analysis (Fresh vs Dry)
print("\n=== 7. G-Section Detailed Analysis ===")
doc = fitz.open(pdf_path)
for page_num in [52, 53, 54]:  # pages 53, 54, 55
    page = doc[page_num]
    text = page.get_text()
    print(f"\nPage {page_num+1}:")
    lines = text.split('\n')
    for i, line in enumerate(lines):
        line_upper = line.strip().upper()
        if 'CONDIMENT' in line_upper or 'SPICE' in line_upper:
            print(f"  Line {i}: {line.strip()}")
        if re.match(r'^G\d{3}$', line.strip()):
            print(f"  Line {i}: FOOD CODE {line.strip()}")
doc.close()

# 9. Detailed L-section analysis
print("\n=== 8. L-Section (Milk) Analysis ===")
doc = fitz.open(pdf_path)
for page_num in [56]:  # page 57
    page = doc[page_num]
    text = page.get_text()
    print(f"Page {page_num+1}:")
    lines = text.split('\n')
    for i, line in enumerate(lines):
        line_upper = line.strip().upper()
        if 'MILK' in line_upper:
            print(f"  Line {i}: {line.strip()}")
        if re.match(r'^L\d{3}$', line.strip()):
            print(f"  Line {i}: FOOD CODE {line.strip()}")
doc.close()

# 10. Detailed N-section analysis
print("\n=== 9. N-Section (Poultry) Analysis ===")
doc = fitz.open(pdf_path)
for page_num in [57, 58]:  # pages 58, 59
    page = doc[page_num]
    text = page.get_text()
    print(f"Page {page_num+1}:")
    lines = text.split('\n')
    for i, line in enumerate(lines):
        line_upper = line.strip().upper()
        if 'POULTRY' in line_upper or 'EGG' in line_upper:
            print(f"  Line {i}: {line.strip()}")
        if re.match(r'^N\d{3}$', line.strip()):
            print(f"  Line {i}: FOOD CODE {line.strip()}")
doc.close()

# 11. Detailed S/R section analysis
print("\n=== 10. S/R Section (Freshwater/Marine) Analysis ===")
doc = fitz.open(pdf_path)
for page_num in [66, 67]:  # pages 67, 68
    page = doc[page_num]
    text = page.get_text()
    print(f"Page {page_num+1}:")
    lines = text.split('\n')
    for i, line in enumerate(lines):
        line_upper = line.strip().upper()
        if 'SHELLFISH' in line_upper or 'FRESHWATER' in line_upper or 'MARINE' in line_upper:
            print(f"  Line {i}: {line.strip()}")
        if re.match(r'^[RS]\d{3}$', line.strip()):
            print(f"  Line {i}: FOOD CODE {line.strip()}")
doc.close()

print("\n=== STAGE 1 INVESTIGATION COMPLETE ===")