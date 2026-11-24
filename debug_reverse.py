import fitz
import re

doc = fitz.open('data/raw/nutrition/IFCT_2017/IFCT2017_decrypted.pdf')

# Test reverse scan on page 58 (EGG AND EGG PRODUCTS / POULTRY)
page = doc[57]
text = page.get_text()
lines = [line.strip() for line in text.split('\n')]

# Reverse scan to find group headers
group_at_line = {}
current_group = ""

for idx in range(len(lines) - 1, -1, -1):
    line = lines[idx].strip()
    if not line:
        continue
    
    # Check for group header
    group = None
    for pdf_h, std in [('CEREALS AND MILLETS', 'CEREALS AND MILLETS'),
                       ('GRAIN LEGUMES', 'PULSES AND LEGUMES'),
                       ('GREEN LEAFY VEGETABLES', 'LEAFY VEGETABLES'),
                       ('LEAFY VEGETABLES', 'LEAFY VEGETABLES'),
                       ('OTHER VEGETABLES', 'OTHER VEGETABLES'),
                       ('FRUITS', 'FRUITS'),
                       ('ROOTS AND TUBERS', 'ROOTS AND TUBERS'),
                       ('CONDIMENTS AND SPICES-FRESH', 'CONDIMENTS AND SPICES-FRESH'),
                       ('CONDIMENTS AND SPICES-DRY', 'CONDIMENTS AND SPICES-DRY'),
                       ('NUTS AND OIL SEEDS', 'NUTS AND OILSEEDS'),
                       ('MUSHROOMS', 'MUSHROOMS'),
                       ('MISCELLANEOUS FOODS', 'MISCELLANEOUS'),
                       ('MISCELLANEOUS', 'MISCELLANEOUS'),
                       ('MILK AND MILK PRODUCTS', 'MILK AND MILK PRODUCTS'),
                       ('EGG AND EGG PRODUCTS', 'EGG AND EGG PRODUCTS'),
                       ('POULTRY', 'POULTRY'),
                       ('ANIMAL MEAT', 'ANIMAL MEAT'),
                       ('MARINE FISH', 'MARINE FISH'),
                       ('MARINE SHELLFISH', 'MARINE SHELLFISH'),
                       ('SUGARS', 'SUGARS AND JAGGERY'),
                       ('SUGARS AND JAGGERY', 'SUGARS AND JAGGERY')]:
        if pdf_h.upper() in lines[idx].upper():
            current_group = pdf_h
            break
    
    if current_group:
        group_at_line[idx] = current_group

# Print detected group headers
print("Group headers found (reverse scan):")
for idx, group in sorted(group_at_line.items()):
    print(f"  Line {idx}: {group}")

# Now check foods and their assigned groups
print("\nFoods and their assigned groups:")
for idx in range(len(lines)):
    line = lines[idx].strip()
    if re.match(r'^[A-Z]\d{3}$', line):
        # Find next group header after this food
        food_group = ""
        for j in range(idx + 1, len(lines)):
            if j in group_at_line:
                food_group = group_at_line[j]
                break
        print(f"Line {idx}: {line} -> group: '{food_group}'")

import re