import fitz

doc = fitz.open('data/raw/nutrition/IFCT_2017/IFCT2017_decrypted.pdf')

# Check page 55 for group headers
page = doc[54]
text = page.get_text()
lines = [line.strip() for line in text.split('\n')]

headers = [
    'CEREALS AND MILLETS',
    'GRAIN LEGUMES',
    'GREEN LEAFY VEGETABLES',
    'LEAFY VEGETABLES',
    'OTHER VEGETABLES',
    'FRUITS',
    'ROOTS AND TUBERS',
    'CONDIMENTS AND SPICES-FRESH',
    'CONDIMENTS AND SPICES-DRY',
    'NUTS AND OIL SEEDS',
    'MUSHROOMS',
    'MISCELLANEOUS FOODS',
    'MISCELLANEOUS',
    'MILK AND MILK PRODUCTS',
    'EGG AND EGG PRODUCTS',
    'POULTRY',
    'ANIMAL MEAT',
    'MARINE FISH',
    'MARINE SHELLFISH',
    'SUGARS',
    'SUGARS AND JAGGERY',
]

for i, line in enumerate(lines):
    if line.strip():
        line_upper = line.upper()
        for h in headers:
            if h.upper() in line_upper:
                print(f'{i:3}: "{line}" -> MATCH: {h}')
                break

doc.close()