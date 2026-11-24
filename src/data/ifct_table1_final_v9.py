#!/usr/bin/env python3
"""
IFCT 2017 Table 1 Final Extractor v9 - Proper lookahead group assignment.
For each food item, find the next group header AFTER it (lookahead).
"""

import fitz
import re
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional

def extract_ifct_table1(pdf_path: str, output_dir: Path) -> pd.DataFrame:
    """Extract Table 1 using lookahead group assignment."""
    
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
    
    def is_group_header(line: str) -> Optional[str]:
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
    
    def is_group_header(line: str) -> Optional[str]:
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
    
    doc = fitz.open(pdf_path)
    all_items = []
    seen_codes = set()
    
    for page_num in range(40, 68):  # pages 41-68 (0-indexed 40-67)
        page = doc[page_num]
        text = page.get_text()
        lines = [line.strip() for line in text.split('\n')]
        
        page_num_1 = page_num + 1
        print(f"\n=== PAGE {page_num+1} ===")
        
        # Pass 1: Find all group header line indices
        group_headers = []  # list of (line_index, group_name)
        
        for idx, line in enumerate(lines):
            line_stripped = line.strip()
            if not line_stripped:
                continue
            
            # Check for direct group header
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
                    group_headers.append((idx, pdf_h))
                    break
            
            # Check for prefix + group name
            if line in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S'] and idx + 1 < len(lines):
                next_line = lines[idx + 1].strip()
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
                    if pdf_h.upper() in lines[idx + 1].upper():
                        group_headers.append((idx + 1, pdf_h))
                        break
        
        # Sort group headers by line index
        group_headers.sort(key=lambda x: x[0])
        
        # For each food code, find the next group header AFTER it
        group_lines = [gh[0] for gh in group_headers]
        group_names = [gh[1] for gh in group_headers]
        
        print(f"\n=== PAGE {page_num+1} ===")
        print(f"  Group headers at lines: {group_headers}")
        
        # Extract foods
        seen_codes = set()
        page_items = []
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue
            
            # Check for food code
            if re.match(r'^[A-Z]\d{3}$', line):
                food_code = line.strip()
                
                if food_code in seen_codes:
                    i += 1
                    continue
                
                # Find the next group header AFTER this food code's line
                food_group = ""
                for gh_line, gh_name in zip(group_lines, group_names):
                    if gh_line > i:
                        food_group = gh_name
                        break
                
                if not food_group:
                    food_group = ""
                
                food_code = lines[i].strip()
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
                    if re.match(r'^[A-Z]\d{3}$', lines[j].strip()):
                        break
                    if any(kw in lines[j].upper() for kw in ['TABLE 1', 'PROXIMATE PRINCIPLES', 'DIETARY FIBRE', 'ENERGY KJ', 'FOOD CODE', 'FOOD NAME', 'NO. OF REGIONS', 'WATER PROTCNT', 'ENERC', 'TOTAL INSOLUBLE SOLUBLE', 'MOISTURE PROTEIN', 'PROTEIN', 'ASH', 'FATCE', 'FIBTG', 'FIBINS', 'FIBSOL', 'CHOAVLDF', 'ENERC',
                               'CEREALS AND MILLETS', 'GRAIN LEGUMES', 'GREEN LEAFY VEGETABLES', 'LEAFY VEGETABLES', 'OTHER VEGETABLES', 'FRUITS', 'ROOTS AND TUBERS', 'CONDIMENTS AND SPICES-FRESH', 'CONDIMENTS AND SPICES-DRY', 'NUTS AND OIL SEEDS', 'MUSHROOMS', 'MISCELLANEOUS FOODS', 'MISCELLANEOUS', 'MILK AND MILK PRODUCTS', 'EGG AND EGG PRODUCTS', 'POULTRY', 'ANIMAL MEAT', 'MARINE FISH', 'MARINE SHELLFISH', 'SUGARS', 'SUGARS AND JAGGERY', 'FATS AND EDIBLE OILS']):
                        break
                    if lines[j].strip() in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S']:
                        break
                    
                    # Food name
                    if not food_name and lines[j].strip():
                        next_line = lines[j].strip()
                        if (not next_line[0].isdigit() and not re.match(r'^[\d\.]+(?:±[\d\.]+)?$', next_line) and len(next_line) > 2):
                            food_name = lines[j].strip()
                    
                    # Regions
                    elif not regions and lines[j].strip().isdigit() and len(lines[j].strip()) <= 2:
                        regions = lines[j].strip()
                    
                    # Nutrient values
                    val_matches = re.findall(r'[\d\.]+(?:±[\d\.]+)?', lines[j].strip())
                    if val_matches:
                        nutrient_vals.extend(val_matches)
                    
                    j += 1
                
                if len(nutrient_vals) >= 5:
                    item = {
                        'food_code': lines[i].strip(),
                        'food_name': food_name if food_name else None,
                        'regions': regions if regions else None,
                        'food_group': food_group,
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
    
    # Final verification
    print("\n=== FINAL VERIFICATION ===")
    df = pd.read_csv("data/interim/ifct_extracted/table1_parsed.csv")
    print(f"Total items: {len(df)}")
    print(f"Unique codes: {df['food_code'].nunique()}")
    print(f"Food groups: {df['food_group'].value_counts().to_dict()}")
    print(f"Missing names: {df['food_name'].isna().sum()}")
    print(f"Missing groups: {df['food_group'].isna().sum()}")
    
    # Check specific items
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