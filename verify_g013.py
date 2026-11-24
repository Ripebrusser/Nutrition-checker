import fitz
import re

pdf_path = "data/raw/nutrition/IFCT_2017/IFCT2017_decrypted.pdf"
doc = fitz.open(pdf_path)
page = doc[53]  # page 54 (0-indexed 53)
text = page.get_text()
lines = text.split('\n')

print("=== Page 54 (0-indexed 53) - Full Context ===")
for i, line in enumerate(lines):
    line_stripped = line.strip()
    if 'CONDIMENT' in line_stripped.upper() or 'SPICE' in line_stripped.upper() or 'G013' in line_stripped or 'G012' in line_stripped or 'G014' in line_stripped:
        print(f"Line {i}: {line_stripped}")
    if re.match(r'^G\d{3}$', line_stripped):
        print(f"Line {i}: FOOD CODE {line_stripped}")

import re
doc.close()