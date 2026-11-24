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

line = 'NUTS AND OIL SEEDS'
line_upper = line.upper()

for h in headers:
    if h.upper() in line_upper:
        print('MATCH: ' + h)
        break
else:
    print('NO MATCH')

# Check exact match
print('Exact match: ' + str(line == 'NUTS AND OIL SEEDS'))