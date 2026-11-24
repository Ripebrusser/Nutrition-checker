#!/usr/bin/env python3
"""
IFCT 2017 Table 1 Extractor v2 - Two-pass extractor with pre-scanned group mapping.
"""

import fitz
import re
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

class IFCTTable1ExtractorV2:
    """Extracts Table 1 with two-pass approach: group mapping then food extraction."""
    
    START_PAGE = 41
    END_PAGE = 68
    
    # All known food group headers (standardized)
    FOOD_GROUP_HEADERS = [
        'CEREALS AND MILLETS',
        'LEAFY VEGETABLES',
        'OTHER VEGETABLES',
        'FRUITS',
        'ROOTS AND TUBERS',
        'CONDIMENTS AND SPICES-FRESH',
        'CONDIMENTS AND SPICES-DRY',
        'MUSHROOMS',
        'MISCELLANEOUS',
        'MILK AND MILK PRODUCTS',
        'EGG AND EGG PRODUCTS',
        'POULTRY',
        'ANIMAL MEAT',
        'MARINE FISH',
        'MARINE SHELLFISH',
    ]
    
    GROUP_NAME_MAP = {
        'GREEN LEAFY VEGETABLES': 'LEAFY VEGETABLES',
        'MISCELLANEOUS FOODS': 'MISCELLANEOUS',
    }
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
        self.food_code_pattern = re.compile(r'^([A-Z]\d{3})$')
        self.page_groups = {}  # page_num -> group name
        
    def close(self):
        self.doc.close()
    
    def _normalize_group(self, group: str) -> str:
        group_map = {
            'GREEN LEAFY VEGETABLES': 'LEAFY VEGETABLES',
            'MISCELLANEOUS FOODS': 'MISCELLANEOUS',
        }
        return group_map.get(group, group)
    
    def _is_group_header(self, text: str) -> Optional[str]:
        if not isinstance(text, str):
            return None
        text_upper = text.strip().upper()
        for header in [
            'CEREALS AND MILLETS',
            'GREEN LEAFY VEGETABLES',
            'LEAFY VEGETABLES',
            'OTHER VEGETABLES',
            'FRUITS',
            'ROOTS AND TUBERS',
            'CONDIMENTS AND SPICES-FRESH',
            'CONDIMENTS AND SPICES-DRY',
            'MUSHROOMS',
            'MISCELLANEOUS FOODS',
            'MISCELLANEOUS',
            'MILK AND MILK PRODUCTS',
            'EGG AND EGG PRODUCTS',
            'POULTRY',
            'ANIMAL MEAT',
            'MARINE FISH',
            'MARINE SHELLFISH',
        ]:
            if header in text.upper():
                return header
        return None
    
    def _normalize_group_name(self, group: str) -> str:
        group_map = {
            'GREEN LEAFY VEGETABLES': 'LEAFY VEGETABLES',
            'MISCELLANEOUS FOODS': 'MISCELLANEOUS',
        }
        return group_map.get(group, group)
    
    def scan_page_groups(self) -> Dict[int, str]:
        """First pass: determine food group for each page."""
        page_groups = {}
        
        for page_num in range(self.START_PAGE - 1, self.END_PAGE):
            page = self.doc[page_num]
            text = page.get_text()
            lines = [line.strip() for line in text.split('\n')]
            
            found_group = None
            for line in lines:
                line_upper = line.upper()
                for header in [
                    'CEREALS AND MILLETS',
                    'GREEN LEAFY VEGETABLES',
                    'LEAFY VEGETABLES',
                    'OTHER VEGETABLES',
                    'FRUITS',
                    'ROOTS AND TUBERS',
                    'CONDIMENTS AND SPICES-FRESH',
                    'CONDIMENTS AND SPICES-DRY',
                    'MUSHROOMS',
                    'MISCELLANEOUS FOODS',
                    'MISCELLANEOUS',
                    'MILK AND MILK PRODUCTS',
                    'EGG AND EGG PRODUCTS',
                    'POULTRY',
                    'ANIMAL MEAT',
                    'MARINE FISH',
                    'MARINE SHELLFISH',
                ]:
                    if header in line.upper():
                        normalized = self._normalize_header(header)
                        page_groups[page_num + 1] = normalized  # 1-indexed page
                        break
                if page_num + 1 in [p for p in page_groups]:
                    break
            
            # If no header found on this page, we'll infer later
            if page_num + 1 not in [p for p in page_groups]:
                pass
        
        return page_groups
    
    def _normalize_header(self, header: str) -> str:
        group_map = {
            'GREEN LEAFY VEGETABLES': 'LEAFY VEGETABLES',
            'MISCELLANEOUS FOODS': 'MISCELLANEOUS',
        }
        return group_map.get(header, header)
    
    def infer_page_groups(self, detected_groups: Dict[int, str]) -> Dict[int, str]:
        """Infer groups for pages without explicit headers by forward/backward fill."""
        all_pages = {}
        
        # First, fill in detected groups
        for page_num in range(self.START_PAGE, self.END_PAGE + 1):
            if page_num in detected_groups:
                all_pages[page_num] = detected_groups[page_num]
        
        # Forward fill: propagate last known group forward
        current_group = None
        for page_num in range(self.START_PAGE, self.END_PAGE + 1):
            if page_num in all_pages:
                current_group = all_pages[page_num]
            elif current_group is not None:
                all_pages[page_num] = current_group
        
        # Backward fill for any remaining pages at the start
        current_group = None
        for page_num in range(self.END_PAGE, self.START_PAGE - 1, -1):
            if page_num in all_pages:
                current_group = all_pages[page_num]
            elif current_group is not None:
                all_pages[page_num] = current_group
        
        return all_pages
    
    def extract_foods(self, page_groups: Dict[int, str]) -> pd.DataFrame:
        """Extract food items using known page groups."""
        all_items = []
        seen_codes = set()
        
        for page_num in range(self.START_PAGE - 1, self.END_PAGE):
            page = self.doc[page_num]
            text = page.get_text()
            lines = [line.strip() for line in text.split('\n')]
            
            # Get group for this page
            page_num_1 = page_num + 1
            current_group = page_groups.get(page_num + 1, "")
            
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                
                # Check for food code
                if re.match(r'^[A-Z]\d{3}$', line):
                    food_code = line.strip()
                    
                    # Skip if already seen
                    if food_code in seen_codes:
                        i += 1
                        continue
                    
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
                            'food_group': page_groups.get(page_num + 1, ""),
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
    pdf_path = "data/raw/nutrition/IFCT_2017/IFCT2017_decrypted.pdf"
    output_dir = Path("data/interim/ifct_extracted")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    extractor = IFCTTable1ExtractorV2(pdf_path)
    
    print("=" * 60)
    print("EXTRACTING TABLE 1: Proximate Principles and Dietary Fiber (v2)")
    print("=" * 60)
    
    try:
        # Pass 1: Scan for group headers
        print("\nPass 1: Scanning page groups...")
        detected_groups = extractor.scan_page_groups()
        print(f"Detected groups on {len(extractor.page_groups)} pages")
        for page, group in sorted(extractor.page_groups.items()):
            print(f"  Page {page}: {group}")
        
        # Infer groups for all pages
        page_groups = extractor.infer_page_groups(extractor.page_groups)
        print(f"\nInferred groups for {len(page_groups)} pages:")
        for page in range(extractor.START_PAGE, extractor.END_PAGE + 1):
            print(f"  Page {page}: {page_groups.get(page, 'UNKNOWN')}")
        
        # Pass 2: Extract foods
        print("\nPass 2: Extracting foods...")
        df = extractor.extract_foods(page_groups)
        
        print(f"\nExtracted {len(df)} food items")
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
    main()