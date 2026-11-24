#!/usr/bin/env python3
"""
IFCT 2017 Extractor using PyMuPDF (fitz) for text-based extraction.
This extracts food composition data directly from PDF text, which is more reliable
than camelot for this PDF's table structure.
"""

import fitz
import re
import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

class IFCTPyMuPDFExtractor:
    """Extracts IFCT 2017 food composition tables using PyMuPDF text extraction."""
    
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
    
    # Table 1 nutrient columns (full table)
    TABLE1_FULL_COLUMNS = [
        'moisture_g', 'protein_g', 'ash_g', 'fat_g',
        'fibre_total_g', 'fibre_insoluble_g', 'fibre_soluble_g',
        'carb_available_g', 'energy_kj'
    ]
    
    # Table 1 reduced columns (no fibre, no carb)
    TABLE1_REDUCED_COLUMNS = [
        'moisture_g', 'protein_g', 'ash_g', 'fat_g', 'energy_kj'
    ]
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
        self.parsed_data = {}
        
    def close(self):
        self.doc.close()
        
    def _is_food_code(self, val: str) -> bool:
        """Check if a string is a food code (Letter + 3 digits)."""
        if not isinstance(val, str):
            return False
        val = val.strip()
        return bool(re.match(r'^[A-Z]\d{3}$', val))
    
    def _is_food_group_header(self, text: str) -> Optional[str]:
        """Check if text is a known food group header."""
        text_clean = text.strip().upper()
        if text_clean in self.FOOD_GROUP_HEADERS:
            return text.strip()
        return None
    
    def extract_table1_from_text(self) -> pd.DataFrame:
        """Extract Table 1 (Proximate Principles) from PDF text."""
        start_page, end_page = self.TABLE_PAGES[1]
        
        all_rows = []
        current_food_group = ""
        seen_codes = set()
        
        # Food code pattern
        food_code_pattern = re.compile(r'^([A-Z]\d{3})$')
        
        for page_num in range(start_page - 1, end_page):  # 0-indexed
            page = self.doc[page_num]
            text = page.get_text()
            lines = text.split('\n')
            
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                
                # Check for food group header
                group = self._is_food_group_header(line)
                if group:
                    current_food_group = group
                    i += 1
                    continue
                
                # Check for food code
                if food_code_pattern.match(line):
                    food_code = line.strip()
                    
                    # Skip if already seen (deduplication)
                    if food_code in seen_codes:
                        i += 1
                        continue
                    seen_codes.add(food_code)
                    
                    # Next lines should be: food_name, regions, then nutrients
                    food_name = ""
                    regions = ""
                    
                    # Look ahead for food name and regions
                    j = i + 1
                    while j < len(lines) and j < i + 5:
                        next_line = lines[j].strip()
                        if next_line:
                            if not food_name and next_line and not self._is_food_code(next_line):
                                food_name = next_line
                            elif food_name and not regions and next_line.isdigit():
                                regions = next_line
                                break
                        j += 1
                    
                    # Now collect nutrient values from subsequent lines
                    # Nutrients can span multiple lines
                    nutrient_vals = []
                    k = j
                    while k < len(lines) and k < j + 20:
                        line_k = lines[k].strip()
                        if not line_k:
                            k += 1
                            continue
                        # Check if this line starts a new food code
                        if food_code_pattern.match(line_k):
                            break
                        # Check if it's a food group header
                        if self._is_food_group_header(line_k):
                            break
                        # Check for nutrient values (numbers with optional ±)
                        # Pattern: number with optional ± and number
                        val_matches = re.findall(r'[\d\.]+(?:±[\d\.]+)?', line_k)
                        if val_matches:
                            nutrient_vals.extend(val_matches)
                        k += 1
                    
                    # Determine table type by number of nutrient values
                    if len(nutrient_vals) >= 9:
                        # Full table with fibre breakdown
                        parsed_row = {
                            'food_code': line.strip(),
                            'food_name': '',
                            'regions': '',
                            'food_group': current_food_group,
                            'source_page': page_num + 1,
                            'source_table': 1,
                        }
                        # We'll fill food_name and regions from context
                        # For now, use the collected nutrient values
                        # The order is: moisture, protein, ash, fat, fibre_total, fibre_insol, fibre_sol, carb, energy
                        if len(nutrient_vals) >= 9:
                            parsed_row['moisture_g'] = nutrient_vals[0]
                            parsed_row['protein_g'] = nutrient_vals[1]
                            parsed_row['ash_g'] = nutrient_vals[2]
                            parsed_row['fat_g'] = nutrient_vals[3]
                            parsed_row['fibre_total_g'] = nutrient_vals[4]
                            parsed_row['fibre_insoluble_g'] = nutrient_vals[4] if len(nutrient_vals) < 6 else nutrient_vals[5]
                            parsed_row['fibre_soluble_g'] = nutrient_vals[5] if len(nutrient_vals) < 7 else nutrient_vals[6]
                            parsed_row['carb_available_g'] = nutrient_vals[6] if len(nutrient_vals) < 8 else nutrient_vals[7]
                            parsed_row['energy_kj'] = nutrient_vals[8] if len(nutrient_vals) > 8 else nutrient_vals[8]
                        all_rows.append(parsed_row)
                    
                    elif len(nutrient_vals) >= 5:
                        # Reduced table
                        parsed_row = {
                            'food_code': line.strip(),
                            'food_name': '',
                            'regions': '',
                            'food_group': current_food_group,
                            'source_page': page_num + 1,
                            'source_table': 1,
                        }
                        if len(nutrient_vals) >= 5:
                            parsed_row['moisture_g'] = nutrient_vals[0]
                            parsed_row['protein_g'] = nutrient_vals[1]
                            parsed_row['ash_g'] = nutrient_vals[2]
                            parsed_row['fat_g'] = nutrient_vals[3]
                            parsed_row['energy_kj'] = nutrient_vals[4]
                        all_rows.append(parsed_row)
                    
                    i = j
                    continue
                
                i += 1
        
        # Post-process: fill in food names and regions by re-scanning with more context
        # This is a simplified version - in practice we'd want a more robust parser
        return pd.DataFrame(all_rows)
    
    def extract_table1_hybrid(self) -> pd.DataFrame:
        """
        Hybrid approach: Use camelot for table structure, PyMuPDF for missing rows.
        """
        # First, get camelot extraction
        import camelot
        start_page, end_page = self.TABLE_PAGES[1]
        pages = f"{start_page}-{end_page}"
        tables = camelot.read_pdf(self.pdf_path, pages=f"{start_page}-{end_page}", flavor='stream')
        
        # Parse camelot results
        camelot_rows = []
        seen_codes = set()
        
        for table in tables:
            df = table.df
            data = df.iloc[1:].values.tolist()  # Skip header
            page = table.page
            
            current_food_group = ""
            
            for row in data:
                # Skip header rows
                row_str = ' '.join([str(v) for v in row]).upper()
                header_keywords = ['WATER', 'PROTCNT', 'ASH', 'FATCE', 'FIBTG', 'FIBINS', 'FIBSOL', 
                                  'CHOAVLDF', 'ENERC', 'DIETARY', 'FIBRE', 'MOISTURE', 'PROTEIN',
                                  'TOTAL', 'INSOLUBLE', 'SOLUBLE', 'CARBOHYDRATE', 'ENERGY',
                                  'FOOD CODE', 'FOOD NAME', 'REGIONS', 'FOOD GROUP']
                if any(kw in row_str for kw in header_keywords):
                    continue
                
                # Check for food group header
                for val in row:
                    if isinstance(val, str):
                        val_clean = val.strip().upper()
                        if val_clean in self.FOOD_GROUP_HEADERS:
                            current_food_group = val.strip()
                            break
                
                # Find food code
                food_code = None
                food_name = None
                regions = None
                fc_idx = -1
                
                for col_idx, val in enumerate(row):
                    if isinstance(val, str) and re.match(r'^[A-Z]\d{3}$', val.strip()):
                        food_code = val.strip()
                        fc_idx = col_idx
                        if col_idx + 1 < len(row):
                            next_val = row[col_idx + 1]
                            if isinstance(next_val, str) and len(next_val.strip()) > 2:
                                food_name = next_val.strip()
                        if col_idx + 2 < len(row):
                            reg_val = row[col_idx + 2]
                            if isinstance(reg_val, str) and reg_val.strip().isdigit():
                                regions = reg_val.strip()
                        break
                
                if not food_code:
                    continue
                
                if food_code in seen_codes:
                    continue
                seen_codes.add(food_code)
                
                # Extract numeric values from nutrient columns
                nutrient_start = fc_idx + 3
                numeric_vals = []
                for i in range(nutrient_start, len(row)):
                    val = row[i]
                    if isinstance(val, str):
                        val_clean = val.strip()
                        if re.match(r'^[\d\.]+(?:±[\d\.]+)?$', val_clean):
                            numeric_vals.append(val_clean)
                
                if len(numeric_vals) < 5:
                    continue
                
                parsed_row = {
                    'food_code': food_code,
                    'food_name': food_name,
                    'regions': regions,
                    'food_group': current_food_group,
                    'source_page': page,
                    'source_table': 1,
                }
                
                if len(numeric_vals) >= 9:
                    parsed_row.update({
                        'moisture_g': numeric_vals[0],
                        'protein_g': numeric_vals[1],
                        'ash_g': numeric_vals[2],
                        'fat_g': numeric_vals[3],
                        'fibre_total_g': numeric_vals[4],
                        'fibre_insoluble_g': numeric_vals[5],
                        'fibre_soluble_g': numeric_vals[6],
                        'carb_available_g': numeric_vals[7],
                        'energy_kj': numeric_vals[8],
                    })
                elif len(numeric_vals) >= 5:
                    parsed_row.update({
                        'moisture_g': numeric_vals[0],
                        'protein_g': numeric_vals[1],
                        'ash_g': numeric_vals[2],
                        'fat_g': numeric_vals[3],
                        'energy_kj': numeric_vals[4],
                    })
                else:
                    continue
                
                camelot_rows.append(parsed_row)
        
        # Now supplement with PyMuPDF text extraction for missing codes
        # Get all codes from camelot
        camelot_codes = {r['food_code'] for r in camelot_rows}
        
        # Extract from PyMuPDF text for missing codes
        pymupdf_rows = self._extract_missing_from_text(camelot_codes)
        
        # Combine
        all_rows = camelot_rows + pymupdf_rows
        
        df = pd.DataFrame(all_rows)
        if len(df) > 0:
            df = df.drop_duplicates(subset='food_code', keep='first').reset_index(drop=True)
        
        return df
    
    def _extract_missing_from_text(self, existing_codes: set) -> List[Dict]:
        """Extract food items from PyMuPDF text that are missing from camelot extraction."""
        start_page, end_page = self.TABLE_PAGES[1]
        missing_rows = []
        current_food_group = ""
        seen_in_this_pass = set()
        
        food_code_pattern = re.compile(r'^([A-Z]\d{3})$')
        
        for page_num in range(start_page - 1, end_page):
            page = self.doc[page_num]
            text = page.get_text()
            lines = text.split('\n')
            
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                
                # Check for food group header
                group = self._is_food_group_header(line)
                if group:
                    current_food_group = group
                    i += 1
                    continue
                
                # Check for food code
                if food_code_pattern.match(line):
                    food_code = line.strip()
                    
                    # Skip if already in existing or already processed in this pass
                    if food_code in existing_codes or food_code in seen_in_this_pass:
                        i += 1
                        continue
                    seen_in_this_pass.add(food_code)
                    
                    # Extract food name, regions, nutrients from subsequent lines
                    food_name = ""
                    regions = ""
                    nutrient_vals = []
                    
                    j = i + 1
                    # Collect up to 30 lines after food code
                    while j < len(lines) and j < i + 30:
                        next_line = lines[j].strip()
                        if not next_line:
                            j += 1
                            continue
                        
                        # Stop if we hit another food code
                        if food_code_pattern.match(next_line):
                            break
                        # Stop if food group header
                        if self._is_food_group_header(next_line):
                            break
                        
                        # Try to parse as food name (first non-empty, non-numeric line)
                        if not food_name and next_line:
                            # Food name typically doesn't start with digit
                            if not next_line[0].isdigit() and not re.match(r'^[\d\.]+(?:±[\d\.]+)?$', next_line):
                                food_name = next_line
                        
                        # Try to parse as regions (single digit)
                        elif not regions and next_line.isdigit() and len(next_line) <= 2:
                            regions = next_line
                        
                        # Try to parse nutrient values
                        val_matches = re.findall(r'[\d\.]+(?:±[\d\.]+)?', next_line)
                        if val_matches:
                            nutrient_vals.extend(val_matches)
                        
                        j += 1
                    
                    if len(nutrient_vals) >= 5:
                        parsed_row = {
                            'food_code': line.strip(),
                            'food_name': food_name,
                            'regions': regions,
                            'food_group': current_food_group,
                            'source_page': i + 1,  # approximate
                            'source_table': 1,
                        }
                        
                        if len(nutrient_vals) >= 9:
                            parsed_row.update({
                                'moisture_g': nutrient_vals[0],
                                'protein_g': nutrient_vals[1],
                                'ash_g': nutrient_vals[2],
                                'fat_g': nutrient_vals[3],
                                'fibre_total_g': nutrient_vals[4],
                                'fibre_insoluble_g': nutrient_vals[5],
                                'fibre_soluble_g': nutrient_vals[6],
                                'carb_available_g': nutrient_vals[7],
                                'energy_kj': nutrient_vals[8],
                            })
                        elif len(nutrient_vals) >= 5:
                            parsed_row.update({
                                'moisture_g': nutrient_vals[0],
                                'protein_g': nutrient_vals[1],
                                'ash_g': nutrient_vals[2],
                                'fat_g': nutrient_vals[3],
                                'energy_kj': nutrient_vals[4],
                            })
                        
                        missing_rows.append(parsed_row)
                    
                    i = j
                    continue
                
                i += 1
        
        return missing_rows
    
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
    
    extractor = IFCTPyMuPDFExtractor(pdf_path)
    
    print("=" * 60)
    print("EXTRACTING TABLE 1: Proximate Principles and Dietary Fiber (Hybrid)")
    print("=" * 60)
    
    try:
        table1_df = extractor.extract_table1_hybrid()
        extractor.save_parsed_data(table1_df, 1, output_dir)
        
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
    finally:
        extractor.close()


if __name__ == "__main__":
    main()