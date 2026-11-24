import pdfplumber
import json

pdf_path = "data/raw/nutrition/IFCT_2017/IFCT2017.pdf"

# Table 1 spans pages 41-68 (0-indexed: 40-67)
# Let's extract all tables from these pages
all_table_data = []

with pdfplumber.open(pdf_path) as pdf:
    for i in range(40, 68):  # Table 1 pages
        page = pdf.pages[i]
        tables = page.extract_tables()
        if tables:
            for t_idx, table in enumerate(tables):
                if table and len(table) > 1:
                    # Clean the table data
                    cleaned_table = []
                    for row in table:
                        cleaned_row = [cell.strip() if cell else "" for cell in row]
                        cleaned_table.append(cleaned_row)
                    
                    all_table_data.append({
                        "page": i + 1,
                        "table_index": t_idx,
                        "rows": len(cleaned_table),
                        "cols": len(cleaned_table[0]) if cleaned_table else 0,
                        "header": cleaned_table[0] if cleaned_table else [],
                        "data": cleaned_table[1:] if len(cleaned_table) > 1 else []
                    })
                    
                    # Print first few rows
                    print(f"\n--- Page {i+1}, Table {t_idx} ---")
                    print(f"  Dimensions: {len(cleaned_table)} rows x {len(cleaned_table[0]) if cleaned_table else 0} cols")
                    print(f"  Header: {cleaned_table[0] if cleaned_table else 'N/A'}")
                    for row in cleaned_table[1:4]:
                        print(f"  Row: {row}")

# Save all extracted table data
with open("data/interim/ifct_extracted/table1_raw.json", "w") as f:
    json.dump(all_table_data, f, indent=2)

print(f"\n\nTotal table chunks extracted: {len(all_table_data)}")
print("Saved to data/interim/ifct_extracted/table1_raw.json")