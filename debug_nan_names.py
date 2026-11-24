import json

with open("data/interim/ifct_extracted/table1_raw_chunks.json", "r") as f:
    chunks = json.load(f)

# Find the rows with NaN food names - food codes: A002, C012, C014, C015, C016, C017, C024, D052, D070, D071, E065
nan_codes = ['A002', 'C012', 'C014', 'C015', 'C016', 'C017', 'C024', 'D052', 'D070', 'D071', 'E065']

print("=== Debugging NaN food names ===")
for chunk in chunks:
    for row in chunk['data']:
        for val in row:
            if isinstance(val, str) and val.strip() in nan_codes:
                print(f"\nFound {val.strip()} on page {chunk['page']}:")
                print(f"  Full row: {row}")
                # Find the food name column (usually next to food code)
                for i, v in enumerate(row):
                    if v and str(v).strip() == val.strip():
                        print(f"  Food code at index {i}")
                        if i + 1 < len(row):
                            print(f"  Next column (index {i+1}): '{row[i+1]}'")
                        if i + 2 < len(row):
                            print(f"  Column {i+2}: '{row[i+2]}'")
                        break