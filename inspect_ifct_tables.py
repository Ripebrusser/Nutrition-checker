import pdfplumber

pdf_path = "data/raw/nutrition/IFCT_2017/IFCT2017.pdf"

# Table 1: Proximate Principles and Dietary Fiber - starts at page 39 (TOC) = PDF page 41
# Let's examine pages 41-68 (Table 1)
print("=== TABLE 1: Proximate Principles and Dietary Fiber (pages 41-68) ===")
with pdfplumber.open(pdf_path) as pdf:
    for i in range(40, 68):  # 0-indexed
        page = pdf.pages[i]
        text = page.extract_text()
        if text:
            lines = text.split('\n')
            # Print first few lines of each page
            print(f"\n--- Page {i+1} ---")
            for line in lines[:5]:
                print(f"  {line}")
            # Check for tables
            tables = page.extract_tables()
            if tables:
                print(f"  TABLES FOUND: {len(tables)}")
                for t_idx, table in enumerate(tables):
                    print(f"    Table {t_idx}: {len(table)} rows x {len(table[0]) if table else 0} cols")
                    if table:
                        print(f"      Header: {table[0]}")
                        if len(table) > 1:
                            print(f"      Row 1: {table[1]}")
                        if len(table) > 2:
                            print(f"      Row 2: {table[2]}")

# Table 2: Water Soluble Vitamins - starts at page 69 (TOC) = PDF page 71
print("\n\n=== TABLE 2: Water Soluble Vitamins (pages 71-98) ===")
with pdfplumber.open(pdf_path) as pdf:
    for i in range(70, 98):
        page = pdf.pages[i]
        tables = page.extract_tables()
        if tables:
            print(f"\n--- Page {i+1} --- TABLES: {len(tables)}")
            for t_idx, table in enumerate(tables):
                if table:
                    print(f"    Table {t_idx}: {len(table)} rows x {len(table[0])} cols")
                    print(f"      Header: {table[0]}")
                    if len(table) > 1:
                        print(f"      Row 1: {table[1]}")

# Let's also check the Index pages to understand food codes
print("\n\n=== INDEX PAGES (around page 550+) ===")
with pdfplumber.open(pdf_path) as pdf:
    for i in range(549, 585):
        page = pdf.pages[i]
        text = page.extract_text()
        if text and ('Food Code' in text or 'Food code' in text or 'Code' in text):
            print(f"\n--- Page {i+1} ---")
            print(text[:500])