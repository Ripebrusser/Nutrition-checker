import fitz

doc = fitz.open('data/raw/nutrition/IFCT_2017/IFCT2017_decrypted.pdf')
for i in range(len(doc)):
    page = doc[i]
    text = page.get_text()
    if 'All values are expressed per 100g edible portion' in text:
        print(f'Page {i+1}: Found "All values are expressed per 100g edible portion"')
        break