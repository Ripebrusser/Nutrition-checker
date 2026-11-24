#!/usr/bin/env python3
"""
IFCT 2017 Table 1 Final Extractor v4 - Fixed nutrient extraction stop conditions.
Properly stops at group prefixes and headers during nutrient extraction.
"""

import fitz
import re
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional

class IFCTTable1FinalExtractor:
    """Extracts Table 1 with proper group header detection and nutrient extraction."""
    
    START_PAGE = 41
    END_PAGE = 68
    
    # Group headers as they appear in the PDF (with standard names)
    GROUP_HEADERS = [
        ('CEREALS AND MILLETS', 'CEREALS AND MILLETS'),
        ('GRAIN LEGUMES', 'PULSES AND LEGUMES'),
        ('GREEN LEAFY VEGETABLES', 'LEAFY VEGETABLES'),
        ('LEAFY VEGETABLES', 'LEAFY VEGETABLES'),
        ('OTHER VEGETABLES', 'OTHER VEGETABLES'),
        ('FRUITS', 'FRUITS'),
        ('ROOTS AND TUBERS', 'ROOTS AND TUBERS'),
        ('CONDIMENTS AND SPICES-FRESH', 'CONDIMENTS AND SPICES-FRESH'),
        ('CONDIMENTS AND SPICES-DRY', 'CONDIMENTS AND SPICES-DRY'),
        ('NUTS AND OIL SEEDS', 'NUTS AND OILSEEDS'),
        ('MUSHROOMS', 'MUSHROOMS'),
        ('MISCELLANEOUS FOODS', 'MISCELLANEOUS'),
        ('MISCELLANEOUS', 'MISCELLANEOUS'),
        ('MILK AND MILK PRODUCTS', 'MILK AND MILK PRODUCTS'),
        ('EGG AND EGG PRODUCTS', 'EGG AND EGG PRODUCTS'),
        ('POULTRY', 'POULTRY'),
        ('ANIMAL MEAT', 'ANIMAL MEAT'),
        ('MARINE FISH', 'MARINE FISH'),
        ('MARINE SHELLFISH', 'MARINE SHELLFISH'),
        ('SUGARS', 'SUGARS AND JAGGERY'),
        ('SUGARS AND JAGGERY', 'SUGARS AND JAGGERY'),
    ]
    
    GROUP_PREFIXES = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S']
    
    # Stop keywords for nutrient extraction
    STOP_KEYWORDS = [
        'TABLE 1', 'PROXIMATE PRINCIPLES', 'DIETARY FIBRE', 'ENERGY KJ',
        'FOOD CODE', 'FOOD NAME', 'NO. OF REGIONS', 'WATER PROTCNT', 'ENERC',
        'TOTAL INSOLUBLE SOLUBLE', 'MOISTURE PROTEIN', 'PROTEIN', 'ASH',
        'FATCE', 'FIBTG', 'FIBINS', 'FIBSOL', 'CHOAVLDF', 'ENERC',
        'TOTAL INSOLUBLE SOLUBLE', 'MOISTURE PROTEIN',
    ]
    
    # Group header keywords that should stop nutrient extraction
    GROUP_STOP_KEYWORDS = [
        'CEREALS AND MILLETS', 'GRAIN LEGUMES', 'GREEN LEAFY VEGETABLES',
        'LEAFY VEGETABLES', 'OTHER VEGETABLES', 'FRUITS', 'ROOTS AND TUBERS',
        'CONDIMENTS AND SPICES-FRESH', 'CONDIMENTS AND SPICES-DRY',
        'NUTS AND OIL SEEDS', 'MUSHROOMS', 'MISCELLANEOUS FOODS',
        'MISCELLANEOUS', 'MILK AND MILK PRODUCTS', 'EGG AND EGG PRODUCTS',
        'POULTRY', 'ANIMAL MEAT', 'MARINE FISH', 'MARINE SHELLFISH',
        'SUGARS', 'SUGARS AND JAGGERY', 'FATS AND EDIBLE OILS',
    ]
    
    # Group prefix letters
    GROUP_PREFIXES = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S']
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
        
    def close(self):
        self.doc.close()
    
    def _normalize_group(self, pdf_header: str) -> str:
        """Map PDF header to standard name."""
        for pdf_h, std in self.GROUP_HEADERS:
            if pdf_h.upper() == pdf_header.upper():
                return std
        return pdf_header
    
    def _is_group_header(self, line: str) -> Optional[str]:
        if not line:
            return None
        line_upper = line.strip().upper()
        for pdf_h, std in self.GROUP_HEADERS:
            if pdf_h.upper() in line_upper:
                return pdf_h
        return None
    
    def _is_food_code(self, line: str) -> bool:
        return bool(re.match(r'^[A-Z]\d{3}$', line.strip()))
    
    def _is_group_prefix(self, line: str) -> bool:
        return line.strip() in self.GROUP_PREFIXES
    
    def _should_stop_nutrient_extraction(self, line: str) -> bool:
        """Check if nutrient extraction should stop at this line."""
        if not line:
            return True
        line_upper = line.strip().upper()
        
        # Stop at food code
        if re.match(r'^[A-Z]\d{3}$', line.strip()):
            return True
        
        # Stop at table headers/footers
        for kw in self.STOP_KEYWORDS:
            if kw in line_upper:
                return True
        
        # Stop at group headers
        for kw in self.GROUP_STOP_KEYWORDS:
            if kw in line_upper:
                return True
        
        # Stop at single letter prefixes (A, B, C, etc.)
        if line.strip() in self.GROUP_PREFIXES:
            return True
        
        return False
    
    def _is_group_header(self, line: str) -> Optional[str]:
        if not line:
            return None
        line_upper = line.strip().upper()
        for pdf_h, std in self.GROUP_HEADERS:
            if pdf_h.upper() in line_upper:
                return pdf_h
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
            print(f"\n=== PAGE {page_num_1} (group: '{current_group}') ===")
            
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                if not line:
                    i += 1
                    continue
                
                # Check for group header directly
                group = self._is_group_header(line)
                if group:
                    current_group = group
                    print(f"  Page {page_num+1} Line {i}: GROUP HEADER -> {group}")
                    i += 1
                    continue
                
                # Check for single-letter group prefix (A, B, C, etc.)
                if self._is_group_prefix(line) and i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    group = self._is_group_header(next_line)
                    if group:
                        current_group = group
                        print(f"  Page {page_num+1} Line {i}: PREFIX '{line}' + '{next_line}' -> {group}")
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
                    while j < len(lines) and j < i + 30:
                        next_line = lines[j].strip()
                        if not next_line:
                            j += 1
                            continue
                        
                        # Stop nutrient extraction at appropriate boundaries
                        if self._should_stop_nutrient_extraction(next_line):
                            break
                        
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
    
    extractor = IFCTTable1FinalExtractor(pdf_path)
    
    try:
        df = extractor.extract()
        
        print(f"\nExtracted {len(df)} food items")
        print(f"Unique food codes: {df['food_code'].nunique()}")
        print(f"Food groups: {df['food_group'].value_counts().to_dict()}")
        print(f"Nutrient coverage:")
        for col in ['moisture_g', 'protein_g', 'fat_g', 'ash_g', 'fibre_total_g', 'fibre_insoluble_g', 'fibre_soluble_g', 'carb_available_g', 'energy_kj']:
            if col in df.columns:
                non_null = df[col].notna().sum()
                print(f"  {col}: {non_null}/{len(df)} ({non_null/len(df)*100:.1f}%)")
        
        # Standardize group names
        group_map = {pdf: std for pdf, std in extractor.GROUP_HEADERS}
        df['food_group'] = df['food_group'].map(lambda x: group_map.get(x, x))
        
        print(f"\nStandardized food groups: {df['food_group'].value_counts().to_dict()}")
        
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