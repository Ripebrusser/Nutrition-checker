import json

# Load the raw chunks
with open("data/interim/ifct_extracted/table1_raw_chunks.json", "r") as f:
    chunks = json.load(f)

# Search for food group headers in the raw data
print("=== Searching for food group headers in raw chunks ===")
found_groups = set()
for chunk in chunks:
    for row in chunk['data']:
        for val in row:
            if isinstance(val, str):
                val_clean = val.strip().upper()
                # Look for known group patterns
                if any(kw in val_clean for kw in ['CEREAL', 'PULSE', 'LEGUME', 'VEGETABLE', 'FRUIT', 
                                                   'ROOT', 'TUBER', 'NUT', 'OILSEED', 'CONDIMENT', 
                                                   'SPICE', 'MUSHROOM', 'EGG', 'POULTRY', 'MEAT', 
                                                   'FISH', 'SHELLFISH', 'MILK', 'FAT', 'OIL', 
                                                   'SUGAR', 'JAGGERY', 'HONEY', 'MISCELLANEOUS']):
                    if len(val.strip()) < 60:
                        found_groups.add(val.strip())

print("Found food group headers:")
for g in sorted(found_groups):
    print(f"  '{g}'")

# Also check for the exact headers in the PDF
print("\n=== Checking for exact matches to known groups ===")
known_groups = {
    'CEREALS AND MILLETS',
    'PULSES AND LEGUMES',
    'LEAFY VEGETABLES',
    'OTHER VEGETABLES',
    'FRUITS',
    'ROOTS AND TUBERS',
    'NUTS AND OILSEEDS',
    'CONDIMENTS AND SPICES-FRESH',
    'CONDIMENTS AND SPICES-DRY',
    'MUSHROOMS',
    'EGG AND EGG PRODUCTS',
    'POULTRY',
    'ANIMAL MEAT',
    'MARINE FISH',
    'MARINE SHELLFISH',
    'MILK AND MILK PRODUCTS',
    'FATS AND EDIBLE OILS',
    'SUGARS AND JAGGERY',
    'MISCELLANEOUS',
}

for group in known_groups:
    found = False
    for chunk in chunks:
        for row in chunk['data']:
            for val in row:
                if isinstance(val, str) and val.strip().upper() == group:
                    found = True
                    break
        if found:
            break
    status = "FOUND" if found else "MISSING"
    print(f"  {group}: {status}")

# Check for NaN food names
print("\n=== Checking for NaN food names ===")
with open("data/interim/ifct_extracted/table1_parsed.csv", "r") as f:
    import csv
    reader = csv.DictReader(f)
    nan_names = 0
    for row in reader:
        if not row['food_name'] or row['food_name'] == 'NaN':
            nan_names += 1
            print(f"  NaN name: food_code={row['food_code']}, group={row['food_group']}, page={row['source_page']}")
    print(f"Total NaN food names: {nan_names}")