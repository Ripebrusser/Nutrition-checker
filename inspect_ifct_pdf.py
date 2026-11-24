import pdfplumber
import fitz  # pymupdf

pdf_path = "data/raw/nutrition/IFCT_2017/IFCT2017.pdf"

# Using PyMuPDF for quick page count and TOC
doc = fitz.open(pdf_path)
print(f"=== PDF Info (PyMuPDF) ===")
print(f"Pages: {doc.page_count}")
print(f"Metadata: {doc.metadata}")

# Check for table of contents / bookmarks
toc = doc.get_toc()
print(f"\n=== Table of Contents ({len(toc)} entries) ===")
for entry in toc[:50]:
    level, title, page = entry
    indent = "  " * (level - 1)
    print(f"{indent}{title} -> page {page}")

doc.close()

# Using pdfplumber to examine first few pages
print("\n=== First 10 Pages Text Preview (pdfplumber) ===")
with pdfplumber.open(pdf_path) as pdf:
    for i, page in enumerate(pdf.pages[:10]):
        text = page.extract_text()
        if text:
            print(f"\n--- Page {i+1} ---")
            print(text[:500])
        else:
            print(f"\n--- Page {i+1} --- (no text extracted)")

# Look for food composition tables - check pages around where tables might start
print("\n=== Searching for table headers / food codes ===")
with pdfplumber.open(pdf_path) as pdf:
    for i, page in enumerate(pdf.pages):
        text = page.extract_text()
        if text and ('Food Code' in text or 'Food code' in text or 'FOOD CODE' in text):
            print(f"Page {i+1}: Found 'Food Code' reference")
            print(text[:300])
            print("...")
        if text and ('Energy' in text and 'Protein' in text and 'Fat' in text and 'Carbohydrate' in text):
            # Check if this looks like a nutrient table header
            lines = text.split('\n')
            for line in lines:
                if 'Energy' in line and 'Protein' in line:
                    print(f"Page {i+1}: Potential nutrient table header")
                    print(line[:200])
                    break