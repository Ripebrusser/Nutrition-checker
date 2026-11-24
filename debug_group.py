import fitz

doc = fitz.open('data/raw/nutrition/IFCT_2017/IFCT2017_decrypted.pdf')

# Check page 55 for NUTS AND OIL SEEDS
page = doc[54]
text = page.get_text()
lines = [line.strip() for line in text.split('\n')]

for i, line in enumerate(lines):
    if line.strip():
        line_upper = line.upper()
        if any(h in line_upper for h in ['NUTS', 'MUSHROOMS', 'SUGARS', 'MISCELLANEOUS', 'MILK', 'EGG', 'POULTRY', 'ANIMAL', 'MARINE', 'SHELLFISH', 'SUGARS', 'JAGGERY']):
            print(f'{i:3}: "{line}"')

doc.close()