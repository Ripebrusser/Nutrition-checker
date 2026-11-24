import fitz
import re

doc = fitz.open('data/raw/nutrition/IFCT_2017/IFCT2017_decrypted.pdf')

# Check page 57
page = doc[56]
text = page.get_text()
lines = [line.strip() for line in text.split('\n')]

print('=== PAGE 57 ===')
for i, line in enumerate(lines):
    if line.strip():
        if re.match(r'^[A-Z]\d{3}$', line.strip()) or any(h in line.upper() for h in ['MILK', 'EGG', 'POULTRY', 'ANIMAL', 'MEAT', 'EGG']):
            print(f'{i:3}: {line}')

doc.close()