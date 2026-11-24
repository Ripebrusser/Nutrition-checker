import fitz
import re

# Check page 56 (0-indexed 55) structure in detail
pdf_path = "data/raw/nutrition/IFCT_2017/IFCT2017_decrypted.pdf"
doc = fitz.open(pdf_path)
page = doc[55]  # page 56
text = page.get_text()
lines = text.split('\n')

print("=== Page 56 (0-indexed 55) Full Structure ===")
for i, line in enumerate(lines):
    line_upper = line.strip().upper()
    if any(kw in line_upper for kw in ['SUGAR', 'JAGGERY', 'MUSHROOM', 'I001', 'I002', 'J001', 'J002', 'J003', 'J004']):
        print(f"Line {i}: {line.strip()}")
    if re.match(r'^[IJ]\d{3}$', line.strip()):
        print(f"Line {i}: FOOD CODE {line.strip()}")

import re
doc.close()