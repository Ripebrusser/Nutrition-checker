import pandas as pd
import fitz

# 1. Check CSV vs Parquet mismatches in detail
print("=== CSV vs Parquet Mismatch Details ===")
csv_df = pd.read_csv('data/interim/ifct_verified/ifct_table1_verified.csv')
parquet_df = pd.read_parquet('data/interim/ifct_verified/ifct_table1_verified.parquet')

for col in ['regions', 'fibre_total_g', 'fibre_insoluble_g', 'fibre_soluble_g']:
    csv_vals = csv_df[col].astype(str).sort_values().reset_index(drop=True)
    parquet_vals = parquet_df[col].astype(str).sort_values().reset_index(drop=True)
    diff = csv_vals != parquet_vals
    if diff.any():
        print(f"\n{col} mismatches: {diff.sum()}")
        # Show first few
        for i in csv_vals[diff].index[:5]:
            c = csv_df.iloc[i]['food_code']
            csv_v = csv_df.iloc[i][col]
            parq_v = parquet_df[parquet_df['food_code'] == c][col].values[0]
            print(f"  {c}: CSV='{csv_v}' vs Parquet='{parq_v}'")

# 2. Check T-prefix items in PDF - are they really there?
print("\n=== T-prefix Items in PDF Verification ===")
pdf_path = "data/raw/nutrition/IFCT_2017/IFCT2017_decrypted.pdf"
doc = fitz.open(pdf_path)

# Page 68 is index 67
page = doc[67]
text = page.get_text()
print(f"Page 68 text length: {len(text)}")
print("=== Page 68 Full Text ===")
print(text[:5000])
print("...")
print(text[-2000:])

# Search for T001-T014
import re
for i in range(1, 15):
    code = f'T{i:03d}'
    if code in text:
        print(f"Found {code} on page 68")
    else:
        print(f"NOT FOUND {code} on page 68")

# Also check pages 67-68 (0-indexed 66-67) for freshwater fish section
for page_num in [66, 67]:
    page = doc[page_num]
    text = page.get_text()
    print(f"\n=== Page {page_num+1} (searching for T codes) ===")
    for i in range(1, 15):
        code = f'T{i:03d}'
        if code in text:
            print(f"  Found {code}")

doc.close()

# 3. Check S001-S010 on page 68 - are they freshwater or marine?
print("\n=== S-prefix Items on Page 68 ===")
doc = fitz.open(pdf_path)
page = doc[67]
text = page.get_text()
# Find S codes
s_codes = re.findall(r'S\d{3}', text)
print(f"S codes on page 68: {sorted(set(s_codes))}")

# Check context around each S code
for code in sorted(set(s_codes)):
    idx = text.find(code)
    if idx >= 0:
        context = text[max(0,idx-100):idx+200]
        print(f"\n{code} context:")
        print(context[:300])
doc.close()

# 4. Check G-prefix group headers in PDF
print("\n=== G-prefix Section Headers ===")
doc = fitz.open(pdf_path)
for page_num in [52, 53, 54]:  # pages 53-55
    page = doc[page_num]
    text = page.get_text()
    print(f"\nPage {page_num+1}:")
    lines = text.split('\n')
    for i, line in enumerate(lines):
        line_upper = line.strip().upper()
        if 'CONDIMENT' in line_upper or 'SPICE' in line_upper:
            print(f"  Line {i}: {line.strip()}")
doc.close()

# 5. Check L-prefix (Milk) section
print("\n=== L-prefix (Milk) Section ===")
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

# 6. Check N-prefix (Poultry) section pages 58-59
print("\n=== N-prefix (Poultry) Section ===")
doc = fitz.open(pdf_path)
for page_num in [57, 58]:  # pages 58-59
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

# 7. Check R-prefix section
print("\n=== R-prefix Section ===")
doc = fitz.open(pdf_path)
for page_num in [66, 67]:  # pages 67-68
    page = doc[page_num]
    text = page.get_text()
    print(f"Page {page_num+1}:")
    lines = text.split('\n')
    for i, line in enumerate(lines):
        line_upper = line.strip().upper()
        if 'SHELLFISH' in line_upper or 'CLAM' in line_upper or 'OCTOPUS' in line_upper or 'SQUID' in line_upper:
            print(f"  Line {i}: {line.strip()}")
        if re.match(r'^R\d{3}$', line.strip()):
            print(f"  Line {i}: FOOD CODE {line.strip()}")
doc.close()