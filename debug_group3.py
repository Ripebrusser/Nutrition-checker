import fitz

doc = fitz.open('data/raw/nutrition/IFCT_2017/IFCT2017_decrypted.pdf')

# Check page 55 lines around the NUTS header
page = doc[54]
text = page.get_text()
lines = [line.strip() for line in text.split('\n')]

# Print lines 65-80
for i in range(65, 85):
    if i < len(lines):
        line = lines[i]
        if line.strip():
            print(f'{i:3}: "{line}"')

doc.close()