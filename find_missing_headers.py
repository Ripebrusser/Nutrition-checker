import json

with open("data/interim/ifct_extracted/table1_raw_chunks.json", "r") as f:
    chunks = json.load(f)

# Search for rows that might be group headers for missing groups
missing_groups = ['PULSES AND LEGUMES', 'LEAFY VEGETABLES', 'OTHER VEGETABLES', 
                  'FRUITS', 'ROOTS AND TUBERS', 'NUTS AND OILSEEDS',
                  'CONDIMENTS AND SPICES-FRESH', 'MUSHROOMS', 'POULTRY',
                  'MARINE SHELLFISH', 'FATS AND EDIBLE OILS', 'SUGARS AND JAGGERY',
                  'MISCELLANEOUS']

print("=== Searching for potential group header rows ===")
for chunk in chunks:
    for row in chunk['data']:
        row_str = ' '.join([str(v) for v in row if v]).strip()
        # Check if this row might be a group header for missing groups
        row_upper = row_str.upper()
        for mg in missing_groups:
            # Check for partial matches
            words = mg.split()
            if any(word in row_upper for word in words if len(word) > 3):
                # Check if it's a short row (likely a header)
                non_empty = [v for v in row if v and str(v).strip()]
                if len(non_empty) <= 3:
                    print(f"  Page {chunk['page']}: '{row_str}' (non-empty: {len(non_empty)})")

# Also look for PULSES specifically
print("\n=== Searching for PULSES ===")
for chunk in chunks:
    for row in chunk['data']:
        row_str = ' '.join([str(v) for v in row if v]).strip()
        if 'PULSE' in row_str.upper() or 'LEGUME' in row_str.upper():
            non_empty = [v for v in row if v and str(v).strip()]
            print(f"  Page {chunk['page']}: '{row_str}' (non-empty: {len(non_empty)})")

# Look for POULTRY
print("\n=== Searching for POULTRY ===")
for chunk in chunks:
    for row in chunk['data']:
        row_str = ' '.join([str(v) for v in row if v]).strip()
        if 'POULTRY' in row_str.upper():
            non_empty = [v for v in row if v and str(v).strip()]
            print(f"  Page {chunk['page']}: '{row_str}' (non-empty: {len(non_empty)})")

# Look for MUSHROOMS
print("\n=== Searching for MUSHROOMS ===")
for chunk in chunks:
    for row in chunk['data']:
        row_str = ' '.join([str(v) for v in row if v]).strip()
        if 'MUSHROOM' in row_str.upper():
            non_empty = [v for v in row if v and str(v).strip()]
            print(f"  Page {chunk['page']}: '{row_str}' (non-empty: {len(non_empty)})")

# Look for NUTS
print("\n=== Searching for NUTS/OILSEEDS ===")
for chunk in chunks:
    for row in chunk['data']:
        row_str = ' '.join([str(v) for v in row if v]).strip()
        if 'NUT' in row_str.upper() or 'OILSEED' in row_str.upper():
            non_empty = [v for v in row if v and str(v).strip()]
            print(f"  Page {chunk['page']}: '{row_str}' (non-empty: {len(non_empty)})")

# Look for FRUITS
print("\n=== Searching for FRUITS ===")
for chunk in chunks:
    for row in chunk['data']:
        row_str = ' '.join([str(v) for v in row if v]).strip()
        if 'FRUIT' in row_str.upper():
            non_empty = [v for v in row if v and str(v).strip()]
            print(f"  Page {chunk['page']}: '{row_str}' (non-empty: {len(non_empty)})")

# Look for VEGETABLES
print("\n=== Searching for VEGETABLES ===")
for chunk in chunks:
    for row in chunk['data']:
        row_str = ' '.join([str(v) for v in row if v]).strip()
        if 'VEGETABLE' in row_str.upper() or 'LEAFY' in row_str.upper() or 'ROOT' in row_str.upper() or 'TUBER' in row_str.upper():
            non_empty = [v for v in row if v and str(v).strip()]
            print(f"  Page {chunk['page']}: '{row_str}' (non-empty: {len(non_empty)})")