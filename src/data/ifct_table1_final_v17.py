#!/usr/bin/env python3
"""
IFCT 2017 Table 1 Final Extractor v17 - Reverse page processing (bottom-to-top).
Group headers appear at section ENDS, so process bottom-to-top to assign correct groups.
"""

import fitz
import re
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional

def extract_ifct_table1(pdf_path: str, output_dir: Path) -> pd.DataFrame:
    """Extract Table 1 by processing each page bottom-to-top."""
    
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
    
    def is_group_header(line: str) -> Optional[str]:
        if not line:
            return None
        line_upper = line.strip().upper()
        for pdf_h, std in [
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
        ]:
            if pdf_h.upper() in line.strip().upper():
                return pdf_h
        return None
    
    def is_food_code(line: str) -> bool:
        return bool(re.match(r'^[A-Z]\d{3}$', line.strip()))
    
    def is_group_prefix(line: str) -> bool:
        return line.strip() in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S']
    
    def should_stop_nutrient(line: str) -> bool:
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
        if line.strip() in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S']:
            return True
        return False
    
    def is_group_header(line: str) -> Optional[str]:
        if not line:
            return None
        line_upper = line.strip().upper()
        for pdf_h, std in [
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
        ]:
            if pdf_h.upper() in line.strip().upper():
                return pdf_h
        return None
    
    def is_food_code(line: str) -> bool:
        return bool(re.match(r'^[A-Z]\d{3}$', line.strip()))
    
    def is_group_prefix(line: str) -> bool:
        return line.strip() in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S']
    
    def should_stop_nutrient(line: str) -> bool:
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
        if line.strip() in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S']:
            return True
        return False
    
    doc = fitz.open(pdf_path)
    all_items = []
    seen_codes = set()
    # The group that applies to the TOP of the next page (items at top of next page belong to this group)
    next_page_group = ""
    
    for page_num in range(67, 39, -1):  # pages 68-41, bottom to top (0-indexed 67-40)
        page = doc[page_num]
        text = page.get_text()
        lines = [line.strip() for line in text.split('\n')]
        
        page_num_1 = page_num + 1
        print(f"\n=== PAGE {page_num+1} (next_page_group: '{next_page_group}') ===")
        
        # Process page bottom-to-top
        current_group = next_page_group  # Group for items at bottom of this page
        items_on_page = []
        seen_on_page = set()
        
        # Process lines bottom-to-top
        for idx in range(len(lines) - 1, -1, -1):
            line = lines[idx].strip()
            if not line:
                continue
            
            # Check for group header (appears at section end in normal order, so at top in reverse)
            group = None
            for pdf_h, std in [
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
            ]:
                if pdf_h.upper() in lines[idx].upper():
                    current_group = pdf_h
                    break
            
            # Check for single-letter group prefix (appears before group name in normal order)
            if lines[idx].strip() in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S']:
                # In reverse, the group name comes BEFORE the prefix, so we already processed it
                continue
            
            # Check for food code
            if re.match(r'^[A-Z]\d{3}$', lines[idx].strip()):
                food_code = lines[idx].strip()
                
                if food_code in seen_codes:
                    continue
                
                # Extract food data by looking at lines BELOW (higher indices) which we already processed
                # In reverse, food data comes AFTER the food code (at higher indices)
                # But we process bottom-to-top, so we haven't seen the food data yet
                # This is the fundamental problem with reverse processing
                pass
        
        # Reverse processing is complex for nutrient extraction.
        # Let's use a different approach: forward pass with per-page group header pre-scan
        
    doc.close()
    return pd.DataFrame()  # placeholder


def extract_ifct_table1_v10_fixed(pdf_path: str, output_dir: Path) -> pd.DataFrame:
    """Use the working v10 approach but fix the repeated header issue."""
    
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
    
    def is_group_header(line: str) -> Optional[str]:
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
    
    def is_food_code(line: str) -> bool:
        return bool(re.match(r'^[A-Z]\d{3}$', line.strip()))
    
    def is_group_prefix(line: str) -> bool:
        return line.strip() in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S']
    
    def should_stop_nutrient(line: str) -> bool:
        if not line: return True
        line_upper = line.strip().upper()
        if re.match(r'^[A-Z]\d{3}$', line.strip()): return True
        for kw in ['TABLE 1', 'PROXIMATE PRINCIPLES', 'DIETARY FIBRE', 'ENERGY KJ', 'FOOD CODE', 'FOOD NAME', 'NO. OF REGIONS', 'WATER PROTCNT', 'ENERC', 'TOTAL INSOLUBLE SOLUBLE', 'MOISTURE PROTEIN', 'PROTEIN', 'ASH', 'FATCE', 'FIBTG', 'FIBINS', 'FIBSOL', 'CHOAVLDF', 'ENERC']:
            if kw in line_upper: return True
        if line.strip() in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S']: return True
        return False
    
    def is_group_header(line: str) -> Optional[str]:
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
    
    def is_food_code(line: str) -> bool:
        return bool(re.match(r'^[A-Z]\d{3}$', line.strip()))
    
    def is_group_prefix(line: str) -> bool:
        return line.strip() in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S']
    
    def should_stop_nutrient(line: str) -> bool:
        if not line: return True
        line_upper = line.strip().upper()
        if re.match(r'^[A-Z]\d{3}$', line.strip()): return True
        for kw in ['TABLE 1', 'PROXIMATE PRINCIPLES', 'DIETARY FIBRE', 'ENERGY KJ', 'FOOD CODE', 'FOOD NAME', 'NO. OF REGIONS', 'WATER PROTCNT', 'ENERC', 'TOTAL INSOLUBLE SOLUBLE', 'MOISTURE PROTEIN', 'PROTEIN', 'ASH', 'FATCE', 'FIBTG', 'FIBINS', 'FIBSOL', 'CHOAVLDF', 'ENERC']:
            if kw in line_upper: return True
        if line.strip() in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S']: return True
        return False
    
    doc = fitz.open(pdf_path)
    all_items = []
    seen_codes = set()
    current_group = ""
    
    for page_num in range(40, 68):
        page = doc[page_num]
        text = page.get_text()
        lines = [line.strip() for line in text.split('\n')]
        
        page_num_1 = page_num + 1
        print(f"\n=== PAGE {page_num+1} (group: '{current_group}') ===")
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue
            
            # Check for group header directly
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
                # Only update if different from current group (avoid repeated headers)
                if group != current_group:
                    current_group = group
                    print(f"  Page {page_num+1} Line {i}: GROUP HEADER -> {group}")
                i += 1
                continue
            
            # Check for single-letter group prefix
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
                        if pdf_h != current_group:  # Only update if different
                            current_group = pdf_h
                            print(f"  Page {page_num+1} Line {i}: PREFIX '{line}' + '{lines[i+1]}' -> {pdf_h}")
                        i += 2
                        continue
            
            # Check for food code
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
                    
                    # Stop conditions - NO group header names
                    if re.match(r'^[A-Z]\d{3}$', lines[j].strip()):
                        break
                    if any(kw in lines[j].upper() for kw in ['TABLE 1', 'PROXIMATE PRINCIPLES', 'DIETARY FIBRE', 'ENERGY KJ', 'FOOD CODE', 'FOOD NAME', 'NO. OF REGIONS', 'WATER PROTCNT', 'ENERC', 'TOTAL INSOLUBLE SOLUBLE', 'MOISTURE PROTEIN', 'PROTEIN', 'ASH', 'FATCE', 'FIBTG', 'FIBINS', 'FIBSOL', 'CHOAVLDF', 'ENERC']):
                        break
                    if lines[j].strip() in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S']:
                        break
                    
                    if not food_name and lines[j].strip():
                        next_line = lines[j].strip()
                        if (not next_line[0].isdigit() and not re.match(r'^[\d\.]+(?:±[\d\.]+)?$', next_line) and len(next_line) > 2):
                            food_name = next_line
                    elif not regions and lines[j].strip().isdigit() and len(lines[j].strip()) <= 2:
                        regions = lines[j].strip()
                    else:
                        val_matches = re.findall(r'[\d\.]+(?:±[\d\.]+)?', lines[j].strip())
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
    
    return df


def main():
    pdf_path = "data/raw/nutrition/IFCT_2017/IFCT2017_decrypted.pdf"
    output_dir = Path("data/interim/ifct_extracted")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    df = extract_ifct_table1(pdf_path, Path("data/interim/ifct_extracted"))
    
    print("\n=== FINAL VERIFICATION ===")
    df = pd.read_csv("data/interim/ifct_extracted/table1_parsed.csv")
    print(f"Total items: {len(df)}")
    print(f"Unique codes: {df['food_code'].nunique()}")
    print(f"Food groups: {df['food_group'].value_counts().to_dict()}")
    print(f"Missing names: {df['food_name'].isna().sum()}")
    print(f"Missing groups: {df['food_group'].isna().sum()}")
    
    for code in ['M001', 'N001', 'M002', 'N001', 'I001', 'K001', 'O001', 'S001']:
        row = df[df['food_code'] == code]
        if len(row) > 0:
            r = row.iloc[0]
            print(f'{code}: name={r["food_name"]} group={r["food_group"]} moisture={r["moisture_g"]}')
        else:
            print(f'{code}: MISSING')


if __name__ == "__main__":
    import re
    import pandas as pd
    from pathlib import Path
    main()