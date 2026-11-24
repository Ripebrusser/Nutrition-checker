#!/usr/bin/env python3
"""
Debug version of Table 1 extractor with verbose logging.
"""

import fitz
import re
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional

class IFCTTable1DebugExtractor:
    """Debug extractor with verbose logging."""
    
    START_PAGE = 41
    END_PAGE = 68
    
    GROUP_HEADERS = [
        'CEREALS AND MILLETS',
        'GRAIN LEGUMES',
        'GREEN LEAFY VEGETABLES',
        'LEAFY VEGETABLES',
        'OTHER VEGETABLES',
        'FRUITS',
        'ROOTS AND TUBERS',
        'CONDIMENTS AND SPICES-FRESH',
        'CONDIMENTS AND SPICES-DRY',
        'NUTS AND OIL SEEDS',
        'MUSHROOMS',
        'MISCELLANEOUS FOODS',
        'MISCELLANEOUS',
        'MILK AND MILK PRODUCTS',
        'EGG AND EGG PRODUCTS',
        'POULTRY',
        'ANIMAL MEAT',
        'MARINE FISH',
        'MARINE SHELLFISH',
        'SUGARS',
        'SUGARS AND JAGGERY',
    ]
    
    GROUP_PREFIXES = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S']
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
        
    def close(self):
        self.doc.close()
    
    def _is_group_header(self, line: str) -> Optional[str]:
        if not line:
            return None
        line_upper = line.strip().upper()
        for header in self.GROUP_HEADERS:
            if header.upper() in line_upper:
                return header
        return None
    
    def _is_food_code(self, line: str) -> bool:
        return bool(re.match(r'^[A-Z]\d{3}$', line.strip()))
    
    def _is_group_prefix(self, line: str) -> bool:
        return line.strip() in self.GROUP_PREFIXES
    
    def extract(self) -> pd.DataFrame:
        all_items = []
        seen_codes = set()
        current_group = ""
        
        for page_num in range(self.START_PAGE - 1, self.END_PAGE):
            page = self.doc[page_num]
            text = page.get_text()
            lines = [line.strip() for line in text.split('\n')]
            
            page_num_1 = page_num + 1
            print(f"\n=== PAGE {page_num_1} (current_group at start: '{current_group}') ===")
            
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                
                # Check for group header directly
                group = self._is_group_header(line)
                if group:
                    print(f"  Line {i}: GROUP HEADER '{line}' -> {group}")
                    current_group = group
                    i += 1
                    continue
                
                # Check for single-letter group prefix
                if self._is_group_prefix(line) and i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    group = self._is_group_header(next_line)
                    if group:
                        print(f"  Line {i}: PREFIX '{line}' + next line '{next_line}' -> GROUP HEADER: {group}")
                        current_group = group
                        i += 2
                        continue
                
                # Check for food code
                if self._is_food_code(line):
                    food_code = line.strip()
                    
                    if food_code in seen_codes:
                        i += 1
                        continue
                    seen_codes.add(food_code)
                    
                    # Extract food name, regions, nutrients
                    food_name = ""
                    regions = ""
                    nutrient_vals = []
                    
                    j = i + 1
                    while j < len(lines) and j < i + 25:
                        next_line = lines[j].strip()
                        if not next_line:
                            j += 1
                            continue
                        
                        # Stop conditions
                        if re.match(r'^[A-Z]\d{3}$', next_line):
                            break
                        if any(kw in next_line.upper() for kw in ['TABLE 1', 'PROXIMATE PRINCIPLES', 'DIETARY FIBRE', 'ENERGY KJ', 'FOOD CODE', 'FOOD NAME', 'NO. OF REGIONS', 'WATER PROTCNT', 'ENERC', 'TOTAL INSOLUBLE SOLUBLE', 'MOISTURE PROTEIN', 'TOTAL INSOLUBLE SOLUBLE', 'MOISTURE PROTEIN', 'PROTEIN', 'ASH', 'FATCE', 'FIBTG', 'FIBINS', 'FIBSOL', 'CHOAVLDF', 'ENERC']):
                            j += 1
                            continue
                        
                        # Food name
                        if not food_name and next_line:
                            if (not next_line[0].isdigit() and 
                                not re.match(r'^[\d\.]+(?:±[\d\.]+)?$', next_line) and
                                len(next_line) > 2):
                                food_name = next_line
                        
                        # Regions
                        elif not regions and next_line.isdigit() and len(next_line) <= 2:
                            regions = next_line
                        
                        # Nutrient values
                        val_matches = re.findall(r'[\d\.]+(?:±[\d\.]+)?', next_line)
                        if val_matches:
                            nutrient_vals.extend(val_matches)
                        
                        j += 1
                    
                    if len(nutrient_vals) >= 5:
                        item = {
                            'food_code': lines[i].strip(),
                            'food_name': food_name if food_name else None,
                            'regions': regions if regions else None,
                            'food_group': current_group,
                            'source_page': page_num + 1,
                            'source_table': 1,
                        }
                        
                        if len(nutrient_vals) >= 9:
                            item.update({
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
                            item.update({
                                'moisture_g': nutrient_vals[0],
                                'protein_g': nutrient_vals[1],
                                'ash_g': nutrient_vals[2],
                                'fat_g': nutrient_vals[3],
                                'energy_kj': nutrient_vals[4],
                            })
                        
                        all_items.append(item)
                    
                    i = j
                    continue
                
                i += 1
        
        return pd.DataFrame(all_items)
    
    def close(self):
        self.doc.close()


def main():
    import re
    from pathlib import Path
    
    pdf_path = "data/raw/nutrition/IFCT_2017/IFCT2017_decrypted.pdf"
    output_dir = Path("data/interim/ifct_extracted")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    extractor = IFCTTable1DebugExtractor(pdf_path)
    
    try:
        df = extractor.extract()
        
        print(f"\n\nExtracted {len(df)} food items")
        print(f"Unique food codes: {df['food_code'].nunique()}")
        print(f"Food groups: {df['food_group'].value_counts().to_dict()}")
        print(f"Nutrient coverage:")
        for col in ['moisture_g', 'protein_g', 'fat_g', 'ash_g', 'fibre_total_g', 'fibre_insoluble_g', 'fibre_soluble_g', 'carb_available_g', 'energy_kj']:
            if col in df.columns:
                non_null = df[col].notna().sum()
                print(f"  {col}: {non_null}/{len(df)} ({non_null/len(df)*100:.1f}%)")
        
        # Save
        output_dir = Path("data/interim/ifct_extracted")
        output_dir.mkdir(parents=True, exist_ok=True)
        csv_file = output_dir / "table1_parsed.csv"
        parquet_file = output_dir / "table1_parsed.parquet"
        df.to_csv(csv_file, index=False)
        df.to_parquet(parquet_file, index=False)
        print(f"\nSaved to {csv_file} and {parquet_file}")
        
    finally:
        extractor.close()


if __name__ == "__main__":
    import re
    from pathlib import Path
    import fitz
    main()