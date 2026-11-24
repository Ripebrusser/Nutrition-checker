#!/usr/bin/env python3
"""
IFCT 2017 Extractor - Extracts food composition tables from the official PDF.
Uses camelot-py with stream flavor for table extraction.
"""

import camelot
import pandas as pd
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

class IFCTExtractor:
    """Extracts and parses IFCT 2017 food composition tables."""
    
    # Table page ranges (1-indexed, from TOC)
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
    
    # Known food group headers (exact matches from the PDF)
    FOOD_GROUP_HEADERS = {
        'CEREALS AND MILLETS',
        'PULSES AND LEGUMES',
        'LEAFY VEGETABLES',
        'OTHER VEGETABLES',
        'FRUITS',
        'ROOTS AND TUBERS',
        'NUTS AND OILSEEDS',
        'CONDIMENTS AND SPICES-FRESH',
        'CONDIMENTS AND SPICES-DRY',
        'MUSHROOMS',
        'EGG AND EGG PRODUCTS',
        'POULTRY',
        'ANIMAL MEAT',
        'MARINE FISH',
        'MARINE SHELLFISH',
        'MILK AND MILK PRODUCTS',
        'FATS AND EDIBLE OILS',
        'SUGARS AND JAGGERY',
        'MISCELLANEOUS',
    }
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.parsed_data = {}
        
    def extract_table(self, table_num: int, flavor: str = 'stream') -> List[Dict]:
        """Extract a specific table by number."""
        if table_num not in self.TABLE_PAGES:
            raise ValueError(f"Unknown table number: {table_num}")
        
        start_page, end_page = self.TABLE_PAGES[table_num]
        pages = f"{start_page}-{end_page}"
        
        print(f"Extracting Table {table_num} from pages {pages}...")
        tables = camelot.read_pdf(self.pdf_path, pages=pages, flavor=flavor)
        
        print(f"  Found {tables.n} table chunks")
        
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
        
        return results
    
    def extract_all_tables(self, flavor: str = 'stream') -> Dict[int, List[Dict]]:
        """Extract all 12 tables."""
        all_results = {}
        for table_num in range(1, 13):
            try:
                all_results[table_num] = self.extract_table(table_num, flavor)
            except Exception as e:
                print(f"Error extracting Table {table_num}: {e}")
                all_results[table_num] = []
        return all_results
    
    def _is_food_code(self, val: str) -> bool:
        """Check if a string is a food code (Letter + 3 digits)."""
        if not isinstance(val, str):
            return False
        val = val.strip()
        return bool(re.match(r'^[A-Z]\d{3}$', val))
    
    def _is_header_row(self, row: List[str]) -> bool:
        """Check if a row is a header/metadata row."""
        row_str = ' '.join([str(v) for v in row]).upper()
        header_keywords = ['WATER', 'PROTCNT', 'ASH', 'FATCE', 'FIBTG', 'FIBINS', 'FIBSOL', 
                          'CHOAVLDF', 'ENERC', 'DIETARY', 'FIBRE', 'MOISTURE', 'PROTEIN',
                          'TOTAL', 'INSOLUBLE', 'SOLUBLE', 'CARBOHYDRATE', 'ENERGY',
                          'FOOD CODE', 'FOOD NAME', 'REGIONS', 'FOOD GROUP']
        return any(kw in row_str for kw in header_keywords)
    
    def _is_food_group_header(self, row: List[str]) -> Optional[str]:
        """Check if row is a known food group header."""
        for val in row:
            if isinstance(val, str):
                val_clean = val.strip().upper()
                if val_clean in self.FOOD_GROUP_HEADERS:
                    return val.strip()
        return None
    
    def _extract_numeric_values(self, row: List[str], start_idx: int) -> List[str]:
        """Extract numeric values from row starting at given column index."""
        numeric_vals = []
        for i in range(start_idx, len(row)):
            val = row[i]
            if isinstance(val, str):
                val_clean = val.strip()
                if re.match(r'^[\d\.]+(?:±[\d\.]+)?$', val_clean):
                    numeric_vals.append(val_clean)
        return numeric_vals
    
    def parse_table1(self, chunks: List[Dict]) -> pd.DataFrame:
        """Parse Table 1 (Proximate Principles) chunks into a unified DataFrame."""
        all_rows = []
        current_food_group = ""
        seen_codes = set()  # For deduplication
        
        for chunk in chunks:
            data = chunk['data']
            page = chunk['page']
            
            for row_idx, row in enumerate(data):
                # Skip header rows
                if self._is_header_row(row):
                    continue
                
                # Check for food group header (must be exact match)
                group = self._is_food_group_header(row)
                if group:
                    current_food_group = group
                    continue
                
                # Find food code column index
                food_code = None
                food_name = None
                regions = None
                fc_idx = -1
                
                for col_idx, val in enumerate(row):
                    if self._is_food_code(val):
                        food_code = val.strip()
                        fc_idx = col_idx
                        # Food name is usually next column
                        if col_idx + 1 < len(row):
                            next_val = row[col_idx + 1]
                            if isinstance(next_val, str) and len(next_val.strip()) > 2:
                                food_name = next_val.strip()
                        # Regions is usually next after food name
                        if col_idx + 2 < len(row):
                            reg_val = row[col_idx + 2]
                            if isinstance(reg_val, str) and reg_val.strip().isdigit():
                                regions = reg_val.strip()
                        break
                
                if not food_code:
                    continue
                
                # Deduplicate: skip if we've already seen this food code
                if food_code in seen_codes:
                    continue
                seen_codes.add(food_code)
                
                # Determine nutrient column start index (after regions)
                # Structure: [food_code, food_name, regions, nutrient1, nutrient2, ...]
                nutrient_start = fc_idx + 3
                
                # Extract numeric values from nutrient columns only
                numeric_vals = []
                for i in range(nutrient_start, len(row)):
                    val = row[i]
                    if isinstance(val, str):
                        val_clean = val.strip()
                        if re.match(r'^[\d\.]+(?:±[\d\.]+)?$', val_clean):
                            numeric_vals.append(val_clean)
                
                if not food_code or not numeric_vals:
                    continue
                
                # Find food name (between food_code and regions)
                food_name = None
                if fc_idx + 1 < len(row):
                    next_val = row[fc_idx + 1]
                    if isinstance(next_val, str) and len(next_val.strip()) > 2:
                        food_name = next_val.strip()
                regions = None
                if fc_idx + 2 < len(row):
                    reg_val = row[fc_idx + 2]
                    if isinstance(reg_val, str) and reg_val.strip().isdigit():
                        regions = reg_val.strip()
                
                # Extract numeric values from nutrient columns only
                numeric_vals = []
                for i in range(fc_idx + 3, len(row)):
                    val = row[i]
                    if isinstance(val, str):
                        val_clean = val.strip()
                        if re.match(r'^[\d\.]+(?:±[\d\.]+)?$', val_clean):
                            numeric_vals.append(val_clean)
                
                if len(numeric_vals) < 5:
                    continue
                
                # Determine table type by number of nutrient values
                # Full table (with fibre breakdown): moisture, protein, ash, fat, fibre_total, fibre_insol, fibre_sol, carb, energy = 9 values
                # Reduced table (no fibre, no carb): moisture, protein, ash, fat, energy = 5 values
                
                parsed_row = {
                    'food_code': food_code,
                    'food_name': food_name if food_code in seen_codes else None,  # Will set below
                    'regions': regions,
                    'food_group': current_food_group,
                    'source_page': chunk['page'],
                    'source_table': 1,
                }
                
                # Map nutrients based on number of numeric values
                # Full table (with fibre breakdown): moisture, protein, ash, fat, fibre_total, fibre_insol, fibre_sol, carb, energy = 9 values
                # Reduced table (no fibre, no carb): moisture, protein, ash, fat, energy = 5 values
                
                if len(numeric_vals) >= 9:
                    parsed_row = {
                        'food_code': food_code,
                        'food_name': food_name,
                        'regions': regions,
                        'food_group': current_food_group,
                        'source_page': chunk['page'],
                        'source_table': 1,
                        'moisture_g': numeric_vals[0],
                        'protein_g': numeric_vals[1],
                        'ash_g': numeric_vals[2],
                        'fat_g': numeric_vals[3],
                        'fibre_total_g': numeric_vals[4],
                        'fibre_insoluble_g': numeric_vals[5],
                        'fibre_soluble_g': numeric_vals[6],
                        'carb_available_g': numeric_vals[7],
                        'energy_kj': numeric_vals[8],
                    }
                elif len(numeric_vals) == 8:
                    parsed_row = {
                        'food_code': food_code,
                        'food_name': food_name,
                        'regions': regions,
                        'food_group': current_food_group,
                        'source_page': chunk['page'],
                        'source_table': 1,
                        'moisture_g': numeric_vals[0],
                        'protein_g': numeric_vals[1],
                        'ash_g': numeric_vals[2],
                        'fat_g': numeric_vals[3],
                        'fibre_total_g': numeric_vals[4],
                        'carb_available_g': numeric_vals[5],
                        'energy_kj': numeric_vals[6] if len(numeric_vals) > 6 else None,
                    }
                elif len(numeric_vals) == 7:
                    parsed_row = {
                        'food_code': food_code,
                        'food_name': food_name,
                        'regions': regions,
                        'food_group': current_food_group,
                        'source_page': chunk['page'],
                        'source_table': 1,
                        'moisture_g': numeric_vals[0],
                        'protein_g': numeric_vals[1],
                        'ash_g': numeric_vals[2],
                        'fat_g': numeric_vals[3],
                        'fibre_total_g': numeric_vals[4],
                        'carb_available_g': numeric_vals[5],
                        'energy_kj': numeric_vals[6],
                    }
                elif len(numeric_vals) >= 5:
                    # Reduced table (no fibre, no carb) - eggs, poultry, meat, fish
                    parsed_row = {
                        'food_code': food_code,
                        'food_name': food_name,
                        'regions': regions,
                        'food_group': current_food_group,
                        'source_page': chunk['page'],
                        'source_table': 1,
                        'moisture_g': numeric_vals[0],
                        'protein_g': numeric_vals[1],
                        'ash_g': numeric_vals[2],
                        'fat_g': numeric_vals[3],
                        'energy_kj': numeric_vals[4] if len(numeric_vals) > 4 else None,
                    }
                else:
                    continue
                
                # Check for duplicate food code (camelot sometimes extracts same row twice)
                # We'll deduplicate later
                
                all_rows.append(parsed_row)
        
        # Create DataFrame and deduplicate by food_code (keep first occurrence)
        df = pd.DataFrame(all_rows)
        if len(df) > 0:
            df = df.drop_duplicates(subset='food_code', keep='first').reset_index(drop=True)
        
        return df
    
    def save_raw_chunks(self, chunks: List[Dict], table_num: int, output_dir: Path):
        """Save raw extracted chunks for verification."""
        output_file = output_dir / f"table{table_num}_raw_chunks.json"
        with open(output_file, 'w') as f:
            json.dump(chunks, f, indent=2)
        print(f"Saved raw chunks to {output_file}")
    
    def save_parsed_data(self, df: pd.DataFrame, table_num: int, output_dir: Path):
        """Save parsed data as CSV and Parquet."""
        csv_file = output_dir / f"table{table_num}_parsed.csv"
        parquet_file = output_dir / f"table{table_num}_parsed.parquet"
        df.to_csv(csv_file, index=False)
        df.to_parquet(parquet_file, index=False)
        print(f"Saved parsed Table {table_num} to {csv_file} and {parquet_file} ({len(df)} rows)")


def main():
    pdf_path = "data/raw/nutrition/IFCT_2017/IFCT2017_decrypted.pdf"
    output_dir = Path("data/interim/ifct_extracted")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    extractor = IFCTExtractor(pdf_path)
    
    # Extract Table 1 first
    print("=" * 60)
    print("EXTRACTING TABLE 1: Proximate Principles and Dietary Fiber")
    print("=" * 60)
    
    table1_chunks = extractor.extract_table(1, flavor='stream')
    extractor.save_raw_chunks(table1_chunks, 1, output_dir)
    
    # Parse Table 1
    table1_df = extractor.parse_table1(table1_chunks)
    extractor.save_parsed_data(table1_df, 1, output_dir)
    
    # Print summary
    print(f"\nTable 1 parsed: {len(table1_df)} food items")
    if len(table1_df) > 0:
        print(f"Columns: {list(table1_df.columns)}")
        print(f"Sample rows:")
        print(table1_df.head(15).to_string())
        print(f"\nFood groups: {table1_df['food_group'].value_counts().to_dict()}")
        print(f"Nutrient coverage:")
        for col in ['moisture_g', 'protein_g', 'fat_g', 'ash_g', 'fibre_total_g', 'fibre_insoluble_g', 'fibre_soluble_g', 'carb_available_g', 'energy_kj']:
            if col in table1_df.columns:
                non_null = table1_df[col].notna().sum()
                print(f"  {col}: {non_null}/{len(table1_df)} ({non_null/len(table1_df)*100:.1f}%)")


if __name__ == "__main__":
    main()