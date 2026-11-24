import fitz
import re

doc = fitz.open('data/raw/nutrition/IFCT_2017/IFCT2017_decrypted.pdf')
page = doc[40]  # page 41
text = page.get_text()
lines = [line.strip() for line in text.split('\n')]

# Check for group headers
headers = [
    'CEREALS AND MILLETS', 'GRAIN LEGUMES', 'GREEN LEAFY VEGETABLES',
    'LEAFY VEGETABLES', 'OTHER VEGETABLES', 'FRUITS', 'ROOTS AND TUBERS',
    'CONDIMENTS AND SPICES-FRESH', 'CONDIMENTS AND SPICES-DRY',
    'NUTS AND OIL SEEDS', 'MUSHROOMS', 'MISCELLANEOUS FOODS', 'MISCELLANEOUS',
    'MILK AND MILK PRODUCTS', 'EGG AND EGG PRODUCTS', 'POULTRY',
    'ANIMAL MEAT', 'MARINE FISH', 'MARINE SHELLFISH',
    'SUGARS', 'SUGARS AND JAGGERY'
]

print("=== PAGE 41 lines (first 50) ===")
for i, line in enumerate(lines[:50]):
    if line.strip():
        print(f'{i:3}: "{line}"')
        
        # Check for group headers
        for h in ['CEREALS AND MILLETS', 'GRAIN LEGUMES', 'GREEN LEAFY VEGETABLES',
                  'LEAFY VEGETABLES', 'OTHER VEGETABLES', 'FRUITS', 'ROOTS AND TUBERS',
                  'CONDIMENTS AND SPICES-FRESH', 'CONDIMENTS AND SPICES-DRY',
                  'NUTS AND OIL SEEDS', 'MUSHROOMS', 'MISCELLANEOUS FOODS', 'MISCELLANEOUS',
                  'MILK AND MILK PRODUCTS', 'EGG AND EGG PRODUCTS', 'POULTRY',
                  'ANIMAL MEAT', 'MARINE FISH', 'MARINE SHELLFISH',
                  'SUGARS', 'SUGARS AND JAGGERY']:
            if h.upper() in line.upper():
                print(f'  >>> MATCH: {h}')