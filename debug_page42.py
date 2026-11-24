import fitz

doc = fitz.open('data/raw/nutrition/IFCT_2017/IFCT2017_decrypted.pdf')

# Check page 42 (GRAIN LEGUMES)
page = doc[41]
text = page.get_text()
lines = [line.strip() for line in text.split('\n')]

for i, line in enumerate(lines[:100]):
    if line.strip():
        print(f'{i:3}: "{line}"')

doc.close()