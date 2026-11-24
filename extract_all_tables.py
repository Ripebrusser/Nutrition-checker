import camelot
import json
from pathlib import Path

pdf_path = "data/raw/nutrition/IFCT_2017/IFCT2017_decrypted.pdf"
output_dir = Path("data/interim/ifct_extracted")
output_dir.mkdir(parents=True, exist_ok=True)

# Table page ranges from TOC
TABLE_PAGES = {
    1: (41, 68),      # Proximate Principles and Dietary Fiber
    2: (71, 98),      # Water Soluble Vitamins
    3: (99, 128),     # Fat Soluble Vitamins
    4: (129, 148),    # Carotenoids
    5: (149, 206),    # Minerals and Trace Elements
    6: (207, 224),    # Starch and Individual Sugars
    7: (225, 294),    # Fatty Acid Profile
    8: (295, 361),    # Amino Acid Profile
    9: (362, 381),    # Organic Acids
    10: (382, 451),   # Polyphenols
    11: (452, 471),   # Oligosaccharides, Phytosterols, Saponins, Phytates
    12: (472, 475),   # Fatty acid Profile of Edible Oils and Fats
}

TABLE_NAMES = {
    1: "Proximate Principles and Dietary Fiber",
    2: "Water Soluble Vitamins",
    3: "Fat Soluble Vitamins",
    4: "Carotenoids",
    5: "Minerals and Trace Elements",
    6: "Starch and Individual Sugars",
    7: "Fatty Acid Profile",
    8: "Amino Acid Profile",
    9: "Organic Acids",
    10: "Polyphenols",
    11: "Oligosaccharides, Phytosterols, Saponins, Phytates",
    12: "Fatty acid Profile of Edible Oils and Fats",
}

def extract_table(table_num: int):
    start_page, end_page = TABLE_PAGES[table_num]
    pages = f"{start_page}-{end_page}"
    
    print(f"\n{'='*60}")
    print(f"EXTRACTING TABLE {table_num}: {TABLE_NAMES[table_num]} (pages {pages})")
    print(f"{'='*60}")
    
    tables = camelot.read_pdf(pdf_path, pages=pages, flavor='stream')
    print(f"Found {tables.n} table chunks")
    
    results = []
    for i, table in enumerate(tables):
        df = table.df
        results.append({
            "table_num": table_num,
            "chunk_index": i,
            "page": table.page,
            "accuracy": table.accuracy,
            "shape": list(df.shape),
            "header": df.iloc[0].tolist() if len(df) > 0 else [],
            "data": df.iloc[1:].values.tolist() if len(df) > 1 else []
        })
        if i < 3:  # Print first 3 chunks
            print(f"  Chunk {i}: Page {table.page}, Shape {df.shape}, Accuracy {table.accuracy:.2f}%")
    
    # Save raw chunks
    output_file = output_dir / f"table{table_num}_raw_chunks.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Saved to {output_file}")
    
    return results

def main():
    all_results = {}
    for table_num in range(1, 13):
        try:
            all_results[table_num] = extract_table(table_num)
        except Exception as e:
            print(f"Error extracting Table {table_num}: {e}")
            all_results[table_num] = []
    
    # Summary
    print(f"\n{'='*60}")
    print("EXTRACTION SUMMARY")
    print(f"{'='*60}")
    total_chunks = 0
    for table_num, chunks in all_results.items():
        print(f"Table {table_num} ({TABLE_NAMES[table_num]}): {len(chunks)} chunks")
        total_chunks += len(chunks)
    print(f"Total chunks: {total_chunks}")

if __name__ == "__main__":
    main()