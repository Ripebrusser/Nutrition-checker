import fitz  # pymupdf
import os

pdf_path = "data/raw/nutrition/IFCT_2017/IFCT2017.pdf"
output_path = "data/raw/nutrition/IFCT_2017/IFCT2017_decrypted.pdf"

doc = fitz.open(pdf_path)
print(f"Original encryption: {doc.is_encrypted}")
print(f"Permissions: {doc.permissions}")

# Try to save without encryption
doc.save(output_path, garbage=4, deflate=True, encryption=fitz.PDF_ENCRYPT_NONE)
print(f"Saved decrypted version to {output_path}")

doc.close()

# Verify
doc2 = fitz.open(output_path)
print(f"New encryption: {doc2.is_encrypted}")
print(f"Pages: {doc2.page_count}")
doc2.close()