import camelot
import json

pdf_path = "data/raw/nutrition/IFCT_2017/IFCT2017_decrypted.pdf"

# Try stream flavor
pages = "41-68"

print(f"Extracting tables from pages {pages} with stream flavor...")
tables = camelot.read_pdf(pdf_path, pages=pages, flavor='stream')

print(f"Found {tables.n} tables")

all_data = []
for i, table in enumerate(tables):
    df = table.df
    print(f"\n--- Table {i+1} (Page {table.page}) ---")
    print(f"  Shape: {df.shape}")
    print(f"  Accuracy: {table.accuracy}")
    print(f"  Header: {df.iloc[0].tolist()}")
    print(f"  First 5 rows:")
    print(df.head(5).to_string())
    
    all_data.append({
        "page": table.page,
        "shape": list(df.shape),
        "accuracy": table.accuracy,
        "header": df.iloc[0].tolist(),
        "data": df.iloc[1:].values.tolist()
    })

# Save
with open("data/interim/ifct_extracted/table1_camelot_stream.json", "w") as f:
    json.dump(all_data, f, indent=2)

print(f"\nSaved {len(all_data)} tables to data/interim/ifct_extracted/table1_camelot_stream.json")