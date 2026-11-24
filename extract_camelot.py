import camelot
import json

pdf_path = "data/raw/nutrition/IFCT_2017/IFCT2017.pdf"

# Try to extract tables from Table 1 pages (41-68)
# Camelot uses 1-indexed pages
pages = "41-68"

print(f"Extracting tables from pages {pages}...")
tables = camelot.read_pdf(pdf_path, pages=pages, flavor='lattice')

print(f"Found {tables.n} tables")

all_data = []
for i, table in enumerate(tables):
    df = table.df
    print(f"\n--- Table {i+1} (Page {table.page}) ---")
    print(f"  Shape: {df.shape}")
    print(f"  Header: {df.iloc[0].tolist()}")
    print(f"  First 3 rows:")
    print(df.head(3).to_string())
    
    all_data.append({
        "page": table.page,
        "shape": df.shape,
        "header": df.iloc[0].tolist(),
        "data": df.iloc[1:].values.tolist()
    })

# Save
with open("data/interim/ifct_extracted/table1_camelot.json", "w") as f:
    json.dump(all_data, f, indent=2)

print(f"\nSaved {len(all_data)} tables to data/interim/ifct_extracted/table1_camelot.json")