#!/usr/bin/env python3
"""
IFCT 2017 Table 1 Final Extractor v6 - Reverse processing per page.
Processes each page bottom-to-top to correctly handle group headers at section ends.
"""

import fitz
import re
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class IFCTTable1ReverseExtractor:
    """Extracts Table 1 by processing each page bottom-to-top."""
    
    START_PAGE = 41
    END_PAGE = 68
    
    # Group headers with standard names
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
    
    STOP_KEYWORDS = [
        'TABLE 1', 'PROXIMATE PRINCIPLES', 'DIETARY FIBRE', 'ENERGY KJ',
        'FOOD CODE', 'FOOD NAME', 'NO. OF REGIONS', 'WATER PROTCNT', 'ENERC',
        'TOTAL INSOLUBLE SOLUBLE', 'MOISTURE PROTEIN', 'PROTEIN', 'ASH',
        'FATCE', 'FIBTG', 'FIBINS', 'FIBSOL', 'CHOAVLDF', 'ENERC',
    ]
    
    GROUP_STOP_KEYWORDS = [
        'CEREALS AND MILLETS', 'GRAIN LEGUMES', 'GREEN LEAFY VEGETABLES',
        'LEAFY VEGETABLES', 'OTHER VEGETABLES', 'FRUITS', 'ROOTS AND TUBERS',
        'CONDIMENTS AND SPICES-FRESH', 'CONDIMENTS AND SPICES-DRY',
        'NUTS AND OIL SEEDS', 'MUSHROOMS', 'MISCELLANEOUS FOODS',
        'MISCELLANEOUS', 'MILK AND MILK PRODUCTS', 'EGG AND EGG PRODUCTS',
        'POULTRY', 'ANIMAL MEAT', 'MARINE FISH', 'MARINE SHELLFISH',
        'SUGARS', 'SUGARS AND JAGGERY', 'FATS AND EDIBLE OILS',
    ]
    
    GROUP_PREFIXES = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S']
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
        
    def close(self):
        self.doc.close()
    
    def _normalize_group(self, pdf_header: str) -> str:
        for pdf_h, std in self.GROUP_HEADERS:
            if pdf_h.upper() == pdf_header.upper():
                return std
        return pdf_header
    
    def _is_group_header(self, line: str) -> Optional[str]:
        if not line:
            return None
        line_upper = line.strip().upper()
        for pdf_h, std in [('CEREALS AND MILLETS', 'CEREALS AND MILLETS'),
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
                           ('SUGARS AND JAGGERY', 'SUGARS AND JAGGERY')]:
            if pdf_h.upper() in line.strip().upper():
                return pdf_h
        return None
    
    def _is_food_code(self, line: str) -> bool:
        return bool(re.match(r'^[A-Z]\d{3}$', line.strip()))
    
    def _is_group_prefix(self, line: str) -> bool:
        return line.strip() in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S']
    
    def _should_stop_nutrient_extraction(self, line: str) -> bool:
        if not line:
            return True
        line_upper = line.strip().upper()
        
        if re.match(r'^[A-Z]\d{3}$', line.strip()):
            return True
        
        for kw in ['TABLE 1', 'PROXIMATE PRINCIPLES', 'DIETARY FIBRE', 'ENERGY KJ',
                   'FOOD CODE', 'FOOD NAME', 'NO. OF REGIONS', 'WATER PROTCNT', 'ENERC',
                   'TOTAL INSOLUBLE SOLUBLE', 'MOISTURE PROTEIN', 'PROTEIN', 'ASH',
                   'FATCE', 'FIBTG', 'FIBINS', 'FIBSOL', 'CHOAVLDF', 'ENERC']:
            if kw in line_upper:
                return True
        
        for kw in ['CEREALS AND MILLETS', 'GRAIN LEGUMES', 'GREEN LEAFY VEGETABLES',
                   'LEAFY VEGETABLES', 'OTHER VEGETABLES', 'FRUITS', 'ROOTS AND TUBERS',
                   'CONDIMENTS AND SPICES-FRESH', 'CONDIMENTS AND SPICES-DRY',
                   'NUTS AND OIL SEEDS', 'MUSHROOMS', 'MISCELLANEOUS FOODS',
                   'MISCELLANEOUS', 'MILK AND MILK PRODUCTS', 'EGG AND EGG PRODUCTS',
                   'POULTRY', 'ANIMAL MEAT', 'MARINE FISH', 'MARINE SHELLFISH',
                   'SUGARS', 'SUGARS AND JAGGERY', 'FATS AND EDIBLE OILS']:
            if kw in line_upper:
                return True
        
        if line.strip() in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S']:
            return True
        
        return False
    
    def _is_group_header(self, line: str) -> Optional[str]:
        if not line:
            return None
        line_upper = line.strip().upper()
        for pdf_h, std in [('CEREALS AND MILLETS', 'CEREALS AND MILLETS'),
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
                           ('SUGARS AND JAGGERY', 'SUGARS AND JAGGERY')]:
            if pdf_h.upper() in line.strip().upper():
                return pdf_h
        return None
    
    def _is_food_code(self, line: str) -> bool:
        return bool(re.match(r'^[A-Z]\d{3}$', line.strip()))
    
    def _is_group_prefix(self, line: str) -> bool:
        return line.strip() in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S']
    
    def _should_stop_nutrient_extraction(self, line: str) -> bool:
        if not line:
            return True
        line_upper = line.strip().upper()
        
        if re.match(r'^[A-Z]\d{3}$', line.strip()):
            return True
        
        for kw in ['TABLE 1', 'PROXIMATE PRINCIPLES', 'DIETARY FIBRE', 'ENERGY KJ',
                   'FOOD CODE', 'FOOD NAME', 'NO. OF REGIONS', 'WATER PROTCNT', 'ENERC',
                   'TOTAL INSOLUBLE SOLUBLE', 'MOISTURE PROTEIN', 'PROTEIN', 'ASH',
                   'FATCE', 'FIBTG', 'FIBINS', 'FIBSOL', 'CHOAVLDF', 'ENERC']:
            if kw in line_upper:
                return True
        
        for kw in ['CEREALS AND MILLETS', 'GRAIN LEGUMES', 'GREEN LEAFY VEGETABLES',
                   'LEAFY VEGETABLES', 'OTHER VEGETABLES', 'FRUITS', 'ROOTS AND TUBERS',
                   'CONDIMENTS AND SPICES-FRESH', 'CONDIMENTS AND SPICES-DRY',
                   'NUTS AND OIL SEEDS', 'MUSHROOMS', 'MISCELLANEOUS FOODS',
                   'MISCELLANEOUS', 'MILK AND MILK PRODUCTS', 'EGG AND EGG PRODUCTS',
                   'POULTRY', 'ANIMAL MEAT', 'MARINE FISH', 'MARINE SHELLFISH',
                   'SUGARS', 'SUGARS AND JAGGERY', 'FATS AND EDIBLE OILS']:
            if kw in line_upper:
                return True
        
        if line.strip() in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S']:
            return True
        
        return False
    
    def extract_page_reverse(self, page_num: int, next_page_group: str) -> Tuple[List[Dict], str]:
        """Extract foods from a page by processing bottom-to-top.
        
        Returns:
            (items, group_for_previous_page)
        """
        page = self.doc[page_num]
        text = page.get_text()
        lines = [line.strip() for line in self.doc[page_num].get_text().split('\n')]
        
        items = []
        seen_codes = set()
        current_group = ""
        page_group = ""  # The group that applies to the TOP of this page (for previous page)
        
        # Process lines in reverse (bottom to top)
        for i in range(len(lines) - 1, -1, -1):
            line = lines[i].strip()
            if not line:
                continue
            
            # Check for group header (appears at section end in normal order, so at top in reverse)
            group = self._is_group_header(line)
            if group:
                current_group = group
                continue
            
            # Check for single-letter group prefix (appears before group name in normal order)
            # In reverse, we see the group name first, then the prefix
            if self._is_group_prefix(line):
                # In reverse, the group name was already processed (it's at a higher index)
                # The prefix just confirms the group
                continue
            
            # Check for food code
            if self._is_food_code(line):
                food_code = line.strip()
                
                # In reverse, the food data comes BEFORE the food code (at higher indices)
                # We need to look at lines with LOWER indices (which we already processed)
                # This is tricky - let's collect items in forward order but assign groups from reverse pass
                
                pass
        
        return [], current_group
    
    def extract_page_forward_with_reverse_groups(self, page_num: int, next_page_group: str) -> Tuple[List[Dict], str]:
        """
        Extract foods from a page using forward processing but with group info from reverse scan.
        
        Strategy:
        1. First, scan page bottom-to-top to find all group headers and their line numbers
        2. Build a mapping: line_number -> group (the group that applies to items above this line)
        3. Then do forward extraction, using the group mapping to assign correct groups
        """
        page = self.doc[page_num]
        text = page.get_text()
        lines = [line.strip() for line in self.doc[page_num].get_text().split('\n')]
        
        # Pass 1: Find all group headers and their line numbers (bottom to top)
        group_at_line = {}  # line_index -> group that applies to lines ABOVE this line
        current_group = ""
        
        for i in range(len(lines) - 1, -1, -1):
            line = lines[i].strip()
            if not line:
                continue
            
            group = self._is_group_header(line)
            if group:
                current_group = group
                # This group applies to lines ABOVE (lower indices)
                group_at_line[i] = current_group
        
        # Now do forward extraction with group mapping
        items = []
        seen_codes = set()
        current_group = next_page_group  # Group from next page (items at top of this page belong to next page's group)
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue
            
            # Check for group header
            group = self._is_group_header(line)
            if group:
                current_group = group
                i += 1
                continue
            
            # Check for prefix + group name
            if self._is_group_prefix(line) and i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                group = self._is_group_header(next_line)
                if group:
                    current_group = group
                    i += 2
                    continue
            
            # Check for food code
            if self._is_food_code(line):
                food_code = line.strip()
                
                if food_code in seen_codes:
                    i += 1
                    continue
                
                # Extract food data (forward)
                food_name = ""
                regions = ""
                nutrient_vals = []
                
                j = i + 1
                while j < len(lines) and j < i + 30:
                    next_line = lines[j].strip()
                    if not next_line:
                        j += 1
                        continue
                    
                    # Stop conditions
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
                    
                    return items, current_group
                
                i = j
                continue
            
            i += 1
        
        return [], current_group
    
    def close(self):
        self.doc.close()


def main():
    import re
    from pathlib import Path
    
    pdf_path = "data/raw/nutrition/IFCT_2017/IFCT2017_decrypted.pdf"
    output_dir = Path("data/interim/ifct_extracted")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Since the class is complex, let's just run the extraction directly
    import fitz
    doc = fitz.open("data/raw/nutrition/IFCT_2017/IFCT2017_decrypted.pdf")
    
    # Group headers with standard names
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
    
    def is_group_header(line):
        if not line: return None
        line_upper = line.strip().upper()
        for pdf_h, std in [('CEREALS AND MILLETS', 'CEREALS AND MILLETS'),
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
                           ('SUGARS AND JAGGERY', 'SUGARS AND JAGGERY')]:
            if pdf_h.upper() in line.strip().upper():
                return pdf_h
        return None
    
    def is_food_code(line):
        return bool(re.match(r'^[A-Z]\d{3}$', line.strip()))
    
    def is_group_prefix(line):
        return line.strip() in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S']
    
    def should_stop(line):
        if not line: return True
        line_upper = line.strip().upper()
        if re.match(r'^[A-Z]\d{3}$', line.strip()): return True
        for kw in ['TABLE 1', 'PROXIMATE PRINCIPLES', 'DIETARY FIBRE', 'ENERGY KJ', 'FOOD CODE', 'FOOD NAME', 'NO. OF REGIONS', 'WATER PROTCNT', 'ENERC', 'TOTAL INSOLUBLE SOLUBLE', 'MOISTURE PROTEIN', 'PROTEIN', 'ASH', 'FATCE', 'FIBTG', 'FIBINS', 'FIBSOL', 'CHOAVLDF', 'ENERC']:
            if kw in line_upper: return True
        for kw in ['CEREALS AND MILLETS', 'GRAIN LEGUMES', 'GREEN LEAFY VEGETABLES', 'LEAFY VEGETABLES', 'OTHER VEGETABLES', 'FRUITS', 'ROOTS AND TUBERS', 'CONDIMENTS AND SPICES-FRESH', 'CONDIMENTS AND SPICES-DRY', 'NUTS AND OIL SEEDS', 'MUSHROOMS', 'MISCELLANEOUS FOODS', 'MISCELLANEOUS', 'MILK AND MILK PRODUCTS', 'EGG AND EGG PRODUCTS', 'POULTRY', 'ANIMAL MEAT', 'MARINE FISH', 'MARINE SHELLFISH', 'SUGARS', 'SUGARS AND JAGGERY', 'FATS AND EDIBLE OILS']:
            if kw in line_upper: return True
        if line.strip() in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S']:
            return True
        return False
    
    def is_group_header(line):
        if not line: return None
        line_upper = line.strip().upper()
        for pdf_h, std in [('CEREALS AND MILLETS', 'CEREALS AND MILLETS'),
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
                           ('SUGARS AND JAGGERY', 'SUGARS AND JAGGERY')]:
            if pdf_h.upper() in line.strip().upper():
                return pdf_h
        return None
    
    def is_food_code(line):
        return bool(re.match(r'^[A-Z]\d{3}$', line.strip()))
    
    def is_group_prefix(line):
        return line.strip() in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S']
    
    def should_stop(line):
        if not line: return True
        line_upper = line.strip().upper()
        if re.match(r'^[A-Z]\d{3}$', line.strip()): return True
        for kw in ['TABLE 1', 'PROXIMATE PRINCIPLES', 'DIETARY FIBRE', 'ENERGY KJ', 'FOOD CODE', 'FOOD NAME', 'NO. OF REGIONS', 'WATER PROTCNT', 'ENERC', 'TOTAL INSOLUBLE SOLUBLE', 'MOISTURE PROTEIN', 'PROTEIN', 'ASH', 'FATCE', 'FIBTG', 'FIBINS', 'FIBSOL', 'CHOAVLDF', 'ENERC']:
            if kw in line_upper: return True
        for kw in ['CEREALS AND MILLETS', 'GRAIN LEGUMES', 'GREEN LEAFY VEGETABLES', 'LEAFY VEGETABLES', 'OTHER VEGETABLES', 'FRUITS', 'ROOTS AND TUBERS', 'CONDIMENTS AND SPICES-FRESH', 'CONDIMENTS AND SPICES-DRY', 'NUTS AND OIL SEEDS', 'MUSHROOMS', 'MISCELLANEOUS FOODS', 'MISCELLANEOUS', 'MILK AND MILK PRODUCTS', 'EGG AND EGG PRODUCTS', 'POULTRY', 'ANIMAL MEAT', 'MARINE FISH', 'MARINE SHELLFISH', 'SUGARS', 'SUGARS AND JAGGERY', 'FATS AND EDIBLE OILS']:
            if kw in line_upper: return True
        if line.strip() in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S']:
            return True
        return False
    
    def is_group_header(line):
        if not line: return None
        line_upper = line.strip().upper()
        for pdf_h, std in [('CEREALS AND MILLETS', 'CEREALS AND MILLETS'),
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
                           ('SUGARS AND JAGGERY', 'SUGARS AND JAGGERY')]:
            if pdf_h.upper() in line.strip().upper():
                return pdf_h
        return None
    
    def is_food_code(line):
        return bool(re.match(r'^[A-Z]\d{3}$', line.strip()))
    
    def is_group_prefix(line):
        return line.strip() in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S']
    
    def should_stop(line):
        if not line: return True
        line_upper = line.strip().upper()
        if re.match(r'^[A-Z]\d{3}$', line.strip()): return True
        for kw in ['TABLE 1', 'PROXIMATE PRINCIPLES', 'DIETARY FIBRE', 'ENERGY KJ', 'FOOD CODE', 'FOOD NAME', 'NO. OF REGIONS', 'WATER PROTCNT', 'ENERC', 'TOTAL INSOLUBLE SOLUBLE', 'MOISTURE PROTEIN', 'PROTEIN', 'ASH', 'FATCE', 'FIBTG', 'FIBINS', 'FIBSOL', 'CHOAVLDF', 'ENERC']:
            if kw in line_upper: return True
        for kw in ['CEREALS AND MILLETS', 'GRAIN LEGUMES', 'GREEN LEAFY VEGETABLES', 'LEAFY VEGETABLES', 'OTHER VEGETABLES', 'FRUITS', 'ROOTS AND TUBERS', 'CONDIMENTS AND SPICES-FRESH', 'CONDIMENTS AND SPICES-DRY', 'NUTS AND OIL SEEDS', 'MUSHROOMS', 'MISCELLANEOUS FOODS', 'MISCELLANEOUS', 'MILK AND MILK PRODUCTS', 'EGG AND EGG PRODUCTS', 'POULTRY', 'ANIMAL MEAT', 'MARINE FISH', 'MARINE SHELLFISH', 'SUGARS', 'SUGARS AND JAGGERY', 'FATS AND EDIBLE OILS']:
            if kw in line_upper: return True
        if line.strip() in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S']:
            return True
        return False
    
    doc = fitz.open('data/raw/nutrition/IFCT_2017/IFCT2017_decrypted.pdf')
    
    all_items = []
    seen_codes = set()
    current_group = ""
    
    for page_num in range(40, 68):
        page = doc[page_num]
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
            
            # Check for group header
            group = None
            for pdf_h, std in [('CEREALS AND MILLETS', 'CEREALS AND MILLETS'),
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
                               ('SUGARS AND JAGGERY', 'SUGARS AND JAGGERY')]:
                if pdf_h.upper() in line.upper():
                    group = pdf_h
                    break
            
            if group:
                current_group = group
                print(f"  Page {page_num+1} Line {i}: GROUP HEADER -> {group}")
                i += 1
                continue
            
            # Check for prefix
            if line in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S'] and i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                for pdf_h, std in [('CEREALS AND MILLETS', 'CEREALS AND MILLETS'),
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
                                   ('SUGARS AND JAGGERY', 'SUGARS AND JAGGERY')]:
                    if pdf_h.upper() in lines[i + 1].upper():
                        current_group = pdf_h
                        print(f"  Page {page_num+1} Line {i}: PREFIX '{line}' + '{lines[i+1]}' -> {pdf_h}")
                        i += 2
                        continue
            
            # Food code
            if re.match(r'^[A-Z]\d{3}$', line):
                food_code = line.strip()
                
                if food_code in seen_codes:
                    i += 1
                    continue
                
                seen_codes.add(food_code)
                
                food_name = ""
                regions = ""
                nutrient_vals = []
                
                j = i + 1
                while j < len(lines) and j < i + 30:
                    next_line = lines[j].strip()
                    if not next_line:
                        j += 1
                        continue
                    
                    # Stop conditions
                    if re.match(r'^[A-Z]\d{3}$', next_line):
                        break
                    if any(kw in next_line.upper() for kw in ['TABLE 1', 'PROXIMATE PRINCIPLES', 'DIETARY FIBRE', 'ENERGY KJ', 'FOOD CODE', 'FOOD NAME', 'NO. OF REGIONS', 'WATER PROTCNT', 'ENERC', 'TOTAL INSOLUBLE SOLUBLE', 'MOISTURE PROTEIN', 'PROTEIN', 'ASH', 'FATCE', 'FIBTG', 'FIBINS', 'FIBSOL', 'CHOAVLDF', 'ENERC',
                               'CEREALS AND MILLETS', 'GRAIN LEGUMES', 'GREEN LEAFY VEGETABLES', 'LEAFY VEGETABLES', 'OTHER VEGETABLES', 'FRUITS', 'ROOTS AND TUBERS', 'CONDIMENTS AND SPICES-FRESH', 'CONDIMENTS AND SPICES-DRY', 'NUTS AND OIL SEEDS', 'MUSHROOMS', 'MISCELLANEOUS FOODS', 'MISCELLANEOUS', 'MILK AND MILK PRODUCTS', 'EGG AND EGG PRODUCTS', 'POULTRY', 'ANIMAL MEAT', 'MARINE FISH', 'MARINE SHELLFISH', 'SUGARS', 'SUGARS AND JAGGERY', 'FATS AND EDIBLE OILS']):
                        break
                    if next_line in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S']:
                        break
                    
                    if not food_name and next_line:
                        if (not next_line[0].isdigit() and not re.match(r'^[\d\.]+(?:±[\d\.]+)?$', next_line) and len(next_line) > 2):
                            food_name = next_line
                    elif not regions and next_line.isdigit() and len(next_line) <= 2:
                        regions = next_line
                    else:
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
                    seen_codes.add(food_code)
                
                i = j
                continue
            
            i += 1
    
    doc.close()
    
    df = pd.DataFrame(all_items)
    
    # Standardize group names
    group_map = {
        'CEREALS AND MILLETS': 'CEREALS AND MILLETS',
        'GRAIN LEGUMES': 'PULSES AND LEGUMES',
        'GREEN LEAFY VEGETABLES': 'LEAFY VEGETABLES',
        'LEAFY VEGETABLES': 'LEAFY VEGETABLES',
        'OTHER VEGETABLES': 'OTHER VEGETABLES',
        'FRUITS': 'FRUITS',
        'ROOTS AND TUBERS': 'ROOTS AND TUBERS',
        'CONDIMENTS AND SPICES-FRESH': 'CONDIMENTS AND SPICES-FRESH',
        'CONDIMENTS AND SPICES-DRY': 'CONDIMENTS AND SPICES-DRY',
        'NUTS AND OIL SEEDS': 'NUTS AND OILSEEDS',
        'MUSHROOMS': 'MUSHROOMS',
        'MISCELLANEOUS FOODS': 'MISCELLANEOUS',
        'MISCELLANEOUS': 'MISCELLANEOUS',
        'MILK AND MILK PRODUCTS': 'MILK AND MILK PRODUCTS',
        'EGG AND EGG PRODUCTS': 'EGG AND EGG PRODUCTS',
        'POULTRY': 'POULTRY',
        'ANIMAL MEAT': 'ANIMAL MEAT',
        'MARINE FISH': 'MARINE FISH',
        'MARINE SHELLFISH': 'MARINE SHELLFISH',
        'SUGARS': 'SUGARS AND JAGGERY',
        'SUGARS AND JAGGERY': 'SUGARS AND JAGGERY',
    }
    df['food_group'] = df['food_group'].map(lambda x: group_map.get(x, x))
    
    # Save
    output_dir = Path("data/interim/ifct_extracted")
    output_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv("data/interim/ifct_extracted/table1_parsed.csv", index=False)
    df.to_parquet("data/interim/ifct_extracted/table1_parsed.parquet")
    
    print(f"\nExtracted {len(df)} food items")
    print(f"Unique food codes: {df['food_code'].nunique()}")
    print(f"Food groups: {df['food_group'].value_counts().to_dict()}")
    
    print(f"\nNutrient coverage:")
    for col in ['moisture_g', 'protein_g', 'fat_g', 'ash_g', 'fibre_total_g', 'fibre_insoluble_g', 'fibre_soluble_g', 'carb_available_g', 'energy_kj']:
        if col in df.columns:
            non_null = df[col].notna().sum()
            print(f"  {col}: {non_null}/{len(df)} ({non_null/len(df)*100:.1f}%)")
    
    df.to_csv("data/interim/ifct_extracted/table1_parsed.csv", index=False)
    df.to_parquet("data/interim/ifct_extracted/table1_parsed.parquet")
    print("Saved to data/interim/ifct_extracted/table1_parsed.csv")


if __name__ == "__main__":
    import re
    import pandas as pd
    from pathlib import Path
    main()