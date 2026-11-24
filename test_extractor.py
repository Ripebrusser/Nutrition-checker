import fitz
import re

doc = fitz.open('data/raw/nutrition/IFCT_2017/IFCT2017_decrypted.pdf')

# Test the extraction logic on page 55 only
page = doc[54]
text = page.get_text()
lines = [line.strip() for line in text.split('\n')]

GROUP_HEADERS = [
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

GROUP_PREFIXES = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S']

def is_group_header(line):
    if not line:
        return None
    line_upper = line.strip().upper()
    for header in GROUP_HEADERS:
        if header.upper() in line_upper:
            return header
    return None

def is_food_code(line):
    return bool(re.match(r'^[A-Z]\d{3}$', line.strip()))

def is_group_prefix(line):
    return line.strip() in GROUP_PREFIXES

GROUP_PREFIXES = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S']

# Simulate the extraction logic
page = fitz.open('data/raw/nutrition/IFCT_2017/IFCT2017_decrypted.pdf')[54]
text = page.get_text()
lines = [line.strip() for line in text.split('\n')]

current_group = ""
i = 0
while i < len(lines):
    line = lines[i].strip()
    
    # Check for group header directly
    group = None
    for h in ['CEREALS AND MILLETS', 'GRAIN LEGUMES', 'GREEN LEAFY VEGETABLES', 'LEAFY VEGETABLES', 'OTHER VEGETABLES', 'FRUITS', 'ROOTS AND TUBERS', 'CONDIMENTS AND SPICES-FRESH', 'CONDIMENTS AND SPICES-DRY', 'NUTS AND OIL SEEDS', 'MUSHROOMS', 'MISCELLANEOUS FOODS', 'MISCELLANEOUS', 'MILK AND MILK PRODUCTS', 'EGG AND EGG PRODUCTS', 'POULTRY', 'ANIMAL MEAT', 'MARINE FISH', 'MARINE SHELLFISH', 'SUGARS', 'SUGARS AND JAGGERY']:
        if h.upper() in line.upper():
            group = h
            break
    
    if group:
        print(f'Line {i}: GROUP HEADER -> {group}')
        current_group = group
        i += 1
        continue
    
    # Check for group prefix
    if line in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S'] and i + 1 < len(lines):
        next_line = lines[i + 1].strip()
        group = None
        for h in ['CEREALS AND MILLETS', 'GRAIN LEGUMES', 'GREEN LEAFY VEGETABLES', 'LEAFY VEGETABLES', 'OTHER VEGETABLES', 'FRUITS', 'ROOTS AND TUBERS', 'CONDIMENTS AND SPICES-FRESH', 'CONDIMENTS AND SPICES-DRY', 'NUTS AND OIL SEEDS', 'MUSHROOMS', 'MISCELLANEOUS FOODS', 'MISCELLANEOUS', 'MILK AND MILK PRODUCTS', 'EGG AND EGG PRODUCTS', 'POULTRY', 'ANIMAL MEAT', 'MARINE FISH', 'MARINE SHELLFISH', 'SUGARS', 'SUGARS AND JAGGERY']:
            if h.upper() in next_line.upper():
                group = h
                break
        if group:
            print(f'Line {i}: PREFIX {line} + next line GROUP HEADER -> {group}')
            current_group = group
            i += 2
            continue
    
    # Check for food code
    if re.match(r'^[A-Z]\d{3}$', line):
        print(f'Line {i}: FOOD CODE {line} (group: {current_group})')
        # Simulate extraction
        food_code = line
        # ... extract nutrients ...
        # For now just print
        print(f'  Would extract food: {food_code}')
    
    i += 1

print('Final group:', current_group)