import json

# Load the raw chunks
with open("data/interim/ifct_extracted/table1_raw_chunks.json", "r") as f:
    chunks = json.load(f)

# Examine the first few chunks in detail
for i, chunk in enumerate(chunks[:5]):
    print(f"\n=== CHUNK {i} (Page {chunk['page']}) ===")
    print(f"Shape: {chunk['shape']}")
    print(f"Header: {chunk['header']}")
    print(f"Data rows: {len(chunk['data'])}")
    print("First 8 data rows:")
    for j, row in enumerate(chunk['data'][:8]):
        print(f"  Row {j}: {row}")

# Look at a chunk that has actual food data (Table 15, page 53)
print("\n\n=== CHUNK 15 (Page 53) - CONDIMENTS AND SPICES ===")
chunk = chunks[15]
print(f"Shape: {chunk['shape']}")
print(f"Header: {chunk['header']}")
print(f"Data rows: {len(chunk['data'])}")
for j, row in enumerate(chunk['data'][:10]):
    print(f"  Row {j}: {row}")

# Look at chunk 18 (mushrooms)
print("\n\n=== CHUNK 18 (Page 56) - MUSHROOMS ===")
chunk = chunks[18]
print(f"Shape: {chunk['shape']}")
print(f"Header: {chunk['header']}")
for j, row in enumerate(chunk['data'][:10]):
    print(f"  Row {j}: {row}")

# Look at chunk 20 (egg)
print("\n\n=== CHUNK 20 (Page 58) - EGG ===")
chunk = chunks[20]
print(f"Shape: {chunk['shape']}")
print(f"Header: {chunk['header']}")
for j, row in enumerate(chunk['data'][:10]):
    print(f"  Row {j}: {row}")

# Look at chunk 21 (poultry)
print("\n\n=== CHUNK 21 (Page 58) - POULTRY ===")
chunk = chunks[21]
print(f"Shape: {chunk['shape']}")
print(f"Header: {chunk['header']}")
for j, row in enumerate(chunk['data'][:10]):
    print(f"  Row {j}: {row}")