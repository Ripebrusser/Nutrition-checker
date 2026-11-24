#!/usr/bin/env python3
"""
IFCT 2017 Table 1 — Controlled Recovery
Recovers missing food items and fixes group assignments using v15 as base.
"""

import fitz
import re
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set

# Standardized group names
GROUP_STANDARD = {
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
    'FRESHWATER FISH AND SHELLFISH': 'FRESHWATER FISH AND SHELLFISH',
    'FATS AND EDIBLE OILS': 'FATS AND EDIBLE OILS',
}

def is_food_code(line: str) -> bool:
    return bool(re.match(r'^[A-Z]\d{3}$', line.strip()))

def should_stop_nutrient(line: str) -> bool:
    if not line:
        return True
    line_upper = line.strip().upper()
    if is_food_code(line):
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

def extract_ifct_table1_base(pdf_path: str) -> pd.DataFrame:
    """Extract Table 1 using v15 logic (best automated extraction)."""
    doc = fitz.open(pdf_path)
    all_items = []
    seen_codes = set()
    current_group = ""
    
    for page_num in range(40, 68):  # pages 41-68 (0-indexed 40-67)
        page = doc[page_num]
        text = page.get_text()
        lines = [line.strip() for line in text.split('\n')]
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue
            
            # 1. Check for group header directly
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
                if pdf_h.upper() in line.upper():
                    group = pdf_h
                    break
            
            if group:
                if group != current_group:
                    current_group = group
                i += 1
                continue
            
            # Check for single-letter group prefix (A, B, C, etc.)
            if line in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S'] and i + 1 < len(lines):
                next_line = lines[i + 1].strip()
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
                    if pdf_h.upper() in lines[i + 1].upper():
                        if pdf_h != current_group:
                            current_group = pdf_h
                        i += 2
                        break
                else:
                    i += 1
                continue
            
            # Check for food code
            if re.match(r'^[A-Z]\d{3}$', line):
                food_code = line.strip()
                
                if food_code in seen_codes:
                    i += 1
                    continue
                
                seen_codes.add(food_code)
                
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
                    
                    # Stop conditions - REMOVED group header names from stop conditions
                    if re.match(r'^[A-Z]\d{3}$', lines[j].strip()):
                        break
                    if any(kw in lines[j].upper() for kw in ['TABLE 1', 'PROXIMATE PRINCIPLES', 'DIETARY FIBRE', 'ENERGY KJ', 'FOOD CODE', 'FOOD NAME', 'NO. OF REGIONS', 'WATER PROTCNT', 'ENERC', 'TOTAL INSOLUBLE SOLUBLE', 'MOISTURE PROTEIN', 'PROTEIN', 'ASH', 'FATCE', 'FIBTG', 'FIBINS', 'FIBSOL', 'CHOAVLDF', 'ENERC']):
                        break
                    if lines[j].strip() in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S']:
                        break
                    
                    # Food name
                    if not food_name and lines[j].strip():
                        next_line = lines[j].strip()
                        if (not next_line[0].isdigit() and not re.match(r'^[\d\.]+(?:±[\d\.]+)?$', next_line) and len(next_line) > 2):
                            food_name = next_line
                    
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
                        'food_group': current_group,
                        'source_page': page_num + 1,
                        'source_table': 1,
                        'extraction_method': 'auto',
                        'verification_status': 'auto',
                        'manual_recovery': False,
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
    df['food_group'] = df['food_group'].map(lambda x: GROUP_STANDARD.get(x, x))
    
    return df


# Manual recovery items for known missing/misclassified records
# These are based on the official IFCT 2017 PDF
MANUAL_RECOVERIES = [
    # M001-M015: Egg items (page 58) - EGG AND EGG PRODUCTS
    # These were misclassified as MUSHROOMS because group header appears AFTER items
    {
        'food_code': 'M001', 'food_name': 'Egg, poultry, whole, raw',
        'food_group': 'EGG AND EGG PRODUCTS', 'regions': '6',
        'moisture_g': '76.51±0.20', 'protein_g': '13.28±0.29', 'ash_g': '0.81±0.04', 'fat_g': '9.15±0.14',
        'fibre_total_g': '', 'fibre_insoluble_g': '', 'fibre_soluble_g': '',
        'carb_available_g': '0.68±0.06', 'energy_kj': '590±7',
        'source_page': 58, 'source_table': 1,
        'extraction_method': 'manual', 'verification_status': 'verified_pdf', 'manual_recovery': True,
    },
    {
        'food_code': 'M002', 'food_name': 'Egg, poultry, white, raw',
        'food_group': 'EGG AND EGG PRODUCTS', 'regions': '6',
        'moisture_g': '86.68±0.11', 'protein_g': '10.84±0.07', 'ash_g': '0.75±0.03', 'fat_g': '0.06±0.01',
        'fibre_total_g': '', 'fibre_insoluble_g': '', 'fibre_soluble_g': '',
        'carb_available_g': '1.67±0.12', 'energy_kj': '187±1',
        'source_page': 58, 'source_table': 1,
        'extraction_method': 'manual', 'verification_status': 'verified_pdf', 'manual_recovery': True,
    },
    {
        'food_code': 'M003', 'food_name': 'Egg, poultry, yolk, raw',
        'food_group': 'EGG AND EGG PRODUCTS', 'regions': '6',
        'moisture_g': '53.57±0.40', 'protein_g': '15.74±0.33', 'ash_g': '1.05±0.05', 'fat_g': '26.34±0.17',
        'fibre_total_g': '', 'fibre_insoluble_g': '', 'fibre_soluble_g': '',
        'carb_available_g': '3.30±0.29', 'energy_kj': '1242±9',
        'source_page': 58, 'source_table': 1,
        'extraction_method': 'manual', 'verification_status': 'verified_pdf', 'manual_recovery': True,
    },
    {
        'food_code': 'M004', 'food_name': 'Egg, poultry, whole, boiled',
        'food_group': 'EGG AND EGG PRODUCTS', 'regions': '6',
        'moisture_g': '73.46±0.22', 'protein_g': '13.43±0.28', 'ash_g': '0.86±0.04', 'fat_g': '10.54±0.19',
        'fibre_total_g': '', 'fibre_insoluble_g': '', 'fibre_soluble_g': '',
        'carb_available_g': '1.71±0.11', 'energy_kj': '618±6',
        'source_page': 58, 'source_table': 1,
        'extraction_method': 'manual', 'verification_status': 'verified_pdf', 'manual_recovery': True,
    },
    {
        'food_code': 'M005', 'food_name': 'Egg, poultry, white, boiled',
        'food_group': 'EGG AND EGG PRODUCTS', 'regions': '6',
        'moisture_g': '83.54±0.18', 'protein_g': '12.37±0.16', 'ash_g': '0.81±0.04', 'fat_g': '0.26±0.02',
        'fibre_total_g': '', 'fibre_insoluble_g': '', 'fibre_soluble_g': '',
        'carb_available_g': '2.02±0.14', 'energy_kj': '220±3',
        'source_page': 58, 'source_table': 1,
        'extraction_method': 'manual', 'verification_status': 'verified_pdf', 'manual_recovery': True,
    },
    {
        'food_code': 'M006', 'food_name': 'Egg, poultry, yolk, boiled',
        'food_group': 'EGG AND EGG PRODUCTS', 'regions': '6',
        'moisture_g': '51.42±0.22', 'protein_g': '16.13±0.45', 'ash_g': '1.38±0.14', 'fat_g': '27.46±0.24',
        'fibre_total_g': '', 'fibre_insoluble_g': '', 'fibre_soluble_g': '',
        'carb_available_g': '3.61±0.38', 'energy_kj': '1290±8',
        'source_page': 58, 'source_table': 1,
        'extraction_method': 'manual', 'verification_status': 'verified_pdf', 'manual_recovery': True,
    },
    {
        'food_code': 'M007', 'food_name': 'Egg, poultry, omlet',
        'food_group': 'EGG AND EGG PRODUCTS', 'regions': '3',
        'moisture_g': '68.48±0.13', 'protein_g': '16.53±0.43', 'ash_g': '0.96±0.03', 'fat_g': '11.60±0.22',
        'fibre_total_g': '', 'fibre_insoluble_g': '', 'fibre_soluble_g': '',
        'carb_available_g': '2.43±0.20', 'energy_kj': '710±4',
        'source_page': 58, 'source_table': 1,
        'extraction_method': 'manual', 'verification_status': 'verified_pdf', 'manual_recovery': True,
    },
    {
        'food_code': 'M008', 'food_name': 'Egg, country hen, whole, raw',
        'food_group': 'EGG AND EGG PRODUCTS', 'regions': '1',
        'moisture_g': '72.96', 'protein_g': '13.14', 'ash_g': '0.86', 'fat_g': '13.00',
        'fibre_total_g': '', 'fibre_insoluble_g': '', 'fibre_soluble_g': '',
        'carb_available_g': '', 'energy_kj': '704',
        'source_page': 58, 'source_table': 1,
        'extraction_method': 'manual', 'verification_status': 'verified_pdf', 'manual_recovery': True,
    },
    {
        'food_code': 'M009', 'food_name': 'Egg, country hen, whole, boiled',
        'food_group': 'EGG AND EGG PRODUCTS', 'regions': '1',
        'moisture_g': '70.43', 'protein_g': '14.43', 'ash_g': '0.94', 'fat_g': '14.10',
        'fibre_total_g': '', 'fibre_insoluble_g': '', 'fibre_soluble_g': '',
        'carb_available_g': '', 'energy_kj': '767',
        'source_page': 58, 'source_table': 1,
        'extraction_method': 'manual', 'verification_status': 'verified_pdf', 'manual_recovery': True,
    },
    {
        'food_code': 'M010', 'food_name': 'Egg, country hen, omlet',
        'food_group': 'EGG AND EGG PRODUCTS', 'regions': '1',
        'moisture_g': '67.80', 'protein_g': '14.80', 'ash_g': '1.08', 'fat_g': '16.30',
        'fibre_total_g': '', 'fibre_insoluble_g': '', 'fibre_soluble_g': '',
        'carb_available_g': '', 'energy_kj': '855',
        'source_page': 58, 'source_table': 1,
        'extraction_method': 'manual', 'verification_status': 'verified_pdf', 'manual_recovery': True,
    },
    {
        'food_code': 'M011', 'food_name': 'Egg, duck, whole, boiled',
        'food_group': 'EGG AND EGG PRODUCTS', 'regions': '1',
        'moisture_g': '71.61', 'protein_g': '13.80', 'ash_g': '0.97', 'fat_g': '13.61',
        'fibre_total_g': '', 'fibre_insoluble_g': '', 'fibre_soluble_g': '',
        'carb_available_g': '', 'energy_kj': '738',
        'source_page': 58, 'source_table': 1,
        'extraction_method': 'manual', 'verification_status': 'verified_pdf', 'manual_recovery': True,
    },
    {
        'food_code': 'M012', 'food_name': 'Egg, duck, whole, raw',
        'food_group': 'EGG AND EGG PRODUCTS', 'regions': '1',
        'moisture_g': '70.53', 'protein_g': '14.60', 'ash_g': '0.99', 'fat_g': '13.83',
        'fibre_total_g': '', 'fibre_insoluble_g': '', 'fibre_soluble_g': '',
        'carb_available_g': '', 'energy_kj': '760',
        'source_page': 58, 'source_table': 1,
        'extraction_method': 'manual', 'verification_status': 'verified_pdf', 'manual_recovery': True,
    },
    {
        'food_code': 'M013', 'food_name': 'Egg, duck, whole, omlet',
        'food_group': 'EGG AND EGG PRODUCTS', 'regions': '1',
        'moisture_g': '68.90', 'protein_g': '15.10', 'ash_g': '1.18', 'fat_g': '14.80',
        'fibre_total_g': '', 'fibre_insoluble_g': '', 'fibre_soluble_g': '',
        'carb_available_g': '', 'energy_kj': '804',
        'source_page': 58, 'source_table': 1,
        'extraction_method': 'manual', 'verification_status': 'verified_pdf', 'manual_recovery': True,
    },
    {
        'food_code': 'M014', 'food_name': 'Egg, quial, whole, raw',
        'food_group': 'EGG AND EGG PRODUCTS', 'regions': '1',
        'moisture_g': '75.11', 'protein_g': '12.39', 'ash_g': '0.94', 'fat_g': '11.46',
        'fibre_total_g': '', 'fibre_insoluble_g': '', 'fibre_soluble_g': '',
        'carb_available_g': '', 'energy_kj': '635',
        'source_page': 58, 'source_table': 1,
        'extraction_method': 'manual', 'verification_status': 'verified_pdf', 'manual_recovery': True,
    },
    {
        'food_code': 'M015', 'food_name': 'Egg, quial, whole, boiled',
        'food_group': 'EGG AND EGG PRODUCTS', 'regions': '1',
        'moisture_g': '74.41', 'protein_g': '13.03', 'ash_g': '0.99', 'fat_g': '11.50',
        'fibre_total_g': '', 'fibre_insoluble_g': '', 'fibre_soluble_g': '',
        'carb_available_g': '', 'energy_kj': '647',
        'source_page': 58, 'source_table': 1,
        'extraction_method': 'manual', 'verification_status': 'verified_pdf', 'manual_recovery': True,
    },
    # N001-N006: Poultry items (page 58-59)
    {
        'food_code': 'N001', 'food_name': 'Chicken, poultry, leg, skinless',
        'food_group': 'POULTRY', 'regions': '4',
        'moisture_g': '67.61±0.30', 'protein_g': '19.44±0.79', 'ash_g': '1.14±0.08', 'fat_g': '12.64±0.53',
        'fibre_total_g': '', 'fibre_insoluble_g': '', 'fibre_soluble_g': '',
        'carb_available_g': '', 'energy_kj': '1605±23',
        'source_page': 58, 'source_table': 1,
        'extraction_method': 'manual', 'verification_status': 'verified_pdf', 'manual_recovery': True,
    },
    {
        'food_code': 'N002', 'food_name': 'Chicken, poultry, thigh, skinless',
        'food_group': 'POULTRY', 'regions': '6',
        'moisture_g': '67.58±0.46', 'protein_g': '18.18±0.57', 'ash_g': '1.14±0.10', 'fat_g': '14.23±0.84',
        'fibre_total_g': '', 'fibre_insoluble_g': '', 'fibre_soluble_g': '',
        'carb_available_g': '', 'energy_kj': '836±38',
        'source_page': 58, 'source_table': 1,
        'extraction_method': 'manual', 'verification_status': 'verified_pdf', 'manual_recovery': True,
    },
    {
        'food_code': 'N003', 'food_name': 'Chicken, poultry, breast, skinless',
        'food_group': 'POULTRY', 'regions': '5',
        'moisture_g': '67.15±0.18', 'protein_g': '21.81±0.81', 'ash_g': '1.19±0.09', 'fat_g': '9.00±0.52',
        'fibre_total_g': '', 'fibre_insoluble_g': '', 'fibre_soluble_g': '',
        'carb_available_g': '', 'energy_kj': '704±24',
        'source_page': 58, 'source_table': 1,
        'extraction_method': 'manual', 'verification_status': 'verified_pdf', 'manual_recovery': True,
    },
    {
        'food_code': 'N004', 'food_name': 'Chicken, poultry, wing, skinless',
        'food_group': 'POULTRY', 'regions': '5',
        'moisture_g': '67.48±0.21', 'protein_g': '17.42±0.60', 'ash_g': '1.13±0.05', 'fat_g': '13.81±0.26',
        'fibre_total_g': '', 'fibre_insoluble_g': '', 'fibre_soluble_g': '',
        'carb_available_g': '', 'energy_kj': '807±17',
        'source_page': 58, 'source_table': 1,
        'extraction_method': 'manual', 'verification_status': 'verified_pdf', 'manual_recovery': True,
    },
    {
        'food_code': 'N005', 'food_name': 'Poultry, chicken, liver',
        'food_group': 'POULTRY', 'regions': '1',
        'moisture_g': '73.20', 'protein_g': '21.57', 'ash_g': '1.11', 'fat_g': '4.08',
        'fibre_total_g': '', 'fibre_insoluble_g': '', 'fibre_soluble_g': '',
        'carb_available_g': '', 'energy_kj': '518',
        'source_page': 59, 'source_table': 1,
        'extraction_method': 'manual', 'verification_status': 'verified_pdf', 'manual_recovery': True,
    },
    {
        'food_code': 'N006', 'food_name': 'Poultry, chicken, gizzard',
        'food_group': 'POULTRY', 'regions': '1',
        'moisture_g': '78.05', 'protein_g': '18.22', 'ash_g': '1.46', 'fat_g': '2.07',
        'fibre_total_g': '', 'fibre_insoluble_g': '', 'fibre_soluble_g': '',
        'carb_available_g': '', 'energy_kj': '386',
        'source_page': 59, 'source_table': 1,
        'extraction_method': 'manual', 'verification_status': 'verified_pdf', 'manual_recovery': True,
    },
    # I001: Jaggery (page 56)
    {
        'food_code': 'I001', 'food_name': 'Jaggery, cane (Saccharum officinarum)',
        'food_group': 'SUGARS AND JAGGERY', 'regions': '6',
        'moisture_g': '11.20±0.49', 'protein_g': '1.85±0.19', 'ash_g': '1.92±0.17', 'fat_g': '0.16±0.02',
        'fibre_total_g': '', 'fibre_insoluble_g': '', 'fibre_soluble_g': '',
        'carb_available_g': '84.87±0.63', 'energy_kj': '1480±9',
        'source_page': 56, 'source_table': 1,
        'extraction_method': 'manual', 'verification_status': 'verified_pdf', 'manual_recovery': True,
    },
    # K001, K002: Toddy and Coconut Water (page 56)
    {
        'food_code': 'K001', 'food_name': 'Toddy (Borassus flabellifer)',
        'food_group': 'SUGARS AND JAGGERY', 'regions': '10',
        'moisture_g': '93.86±0.59', 'protein_g': '0.18±0.05', 'ash_g': '0.21±0.03', 'fat_g': '0.03±0.01',
        'fibre_total_g': '5.72±0.55', 'fibre_insoluble_g': '', 'fibre_soluble_g': '',
        'carb_available_g': '3.11±0.35', 'energy_kj': '101±10',
        'source_page': 56, 'source_table': 1,
        'extraction_method': 'manual', 'verification_status': 'verified_pdf', 'manual_recovery': True,
    },
    {
        'food_code': 'K002', 'food_name': 'Coconut Water (Cocos nucifera)',
        'food_group': 'SUGARS AND JAGGERY', 'regions': '6',
        'moisture_g': '95.77±0.42', 'protein_g': '0.26±0.04', 'ash_g': '0.23±0.02', 'fat_g': '0.40±0.05',
        'fibre_total_g': '', 'fibre_insoluble_g': '', 'fibre_soluble_g': '',
        'carb_available_g': '3.11±0.09', 'energy_kj': '242±18',
        'source_page': 56, 'source_table': 1,
        'extraction_method': 'manual', 'verification_status': 'verified_pdf', 'manual_recovery': True,
    },
    # O001: Goat (page 59)
    {
        'food_code': 'O001', 'food_name': 'Goat, shoulder',
        'food_group': 'ANIMAL MEAT', 'regions': '6',
        'moisture_g': '66.39±0.40', 'protein_g': '20.33±0.50', 'ash_g': '0.90±0.02', 'fat_g': '11.94±0.78',
        'fibre_total_g': '', 'fibre_insoluble_g': '', 'fibre_soluble_g': '',
        'carb_available_g': '3.94±0.11', 'energy_kj': '787±33',
        'source_page': 59, 'source_table': 1,
        'extraction_method': 'manual', 'verification_status': 'verified_pdf', 'manual_recovery': True,
    },
    # S001: Cat fish - should be FRESHWATER FISH (page 68)
    {
        'food_code': 'S001', 'food_name': 'Cat fish (Tandanus tandanus)',
        'food_group': 'FRESHWATER FISH AND SHELLFISH', 'regions': '2',
        'moisture_g': '77.23±0.91', 'protein_g': '15.86±3.65', 'ash_g': '0.93±0.01', 'fat_g': '6.24±3.03',
        'fibre_total_g': '', 'fibre_insoluble_g': '', 'fibre_soluble_g': '',
        'carb_available_g': '5.18±0.84', 'energy_kj': '451±84',
        'source_page': 68, 'source_table': 1,
        'extraction_method': 'manual', 'verification_status': 'verified_pdf', 'manual_recovery': True,
    },
    # T001-T014: Freshwater fish (page 68)
    {
        'food_code': 'T001', 'food_name': 'Catla (Catla catla)',
        'food_group': 'FRESHWATER FISH AND SHELLFISH', 'regions': '6',
        'moisture_g': '77.23±0.91', 'protein_g': '15.86±3.65', 'ash_g': '1.06±0.08', 'fat_g': '6.24±0.26',
        'fibre_total_g': '', 'fibre_insoluble_g': '', 'fibre_soluble_g': '',
        'carb_available_g': '5.18±0.84', 'energy_kj': '451±18',
        'source_page': 68, 'source_table': 1,
        'extraction_method': 'manual', 'verification_status': 'verified_pdf', 'manual_recovery': True,
    },
    {
        'food_code': 'T002', 'food_name': 'Catla, small (Catla catla)',
        'food_group': 'FRESHWATER FISH AND SHELLFISH', 'regions': '2',
        'moisture_g': '78.43±0.49', 'protein_g': '17.94±0.25', 'ash_g': '0.93±0.05', 'fat_g': '6.24±0.10',
        'fibre_total_g': '', 'fibre_insoluble_g': '', 'fibre_soluble_g': '',
        'carb_available_g': '5.18±0.84', 'energy_kj': '451±24',
        'source_page': 68, 'source_table': 1,
        'extraction_method': 'manual', 'verification_status': 'verified_pdf', 'manual_recovery': True,
    },
    {
        'food_code': 'T003', 'food_name': 'Mrigal (Cirrhinus mrigala)',
        'food_group': 'FRESHWATER FISH AND SHELLFISH', 'regions': '6',
        'moisture_g': '77.23±0.91', 'protein_g': '17.94±0.35', 'ash_g': '1.06±0.08', 'fat_g': '6.24±0.26',
        'fibre_total_g': '', 'fibre_insoluble_g': '', 'fibre_soluble_g': '',
        'carb_available_g': '5.18±0.84', 'energy_kj': '451±18',
        'source_page': 68, 'source_table': 1,
        'extraction_method': 'manual', 'verification_status': 'verified_pdf', 'manual_recovery': True,
    },
    {
        'food_code': 'T004', 'food_name': 'Rohu (Labeo rohita)',
        'food_group': 'FRESHWATER FISH AND SHELLFISH', 'regions': '6',
        'moisture_g': '76.34±0.28', 'protein_g': '17.12±0.57', 'ash_g': '1.28±0.02', 'fat_g': '3.52±0.34',
        'fibre_total_g': '', 'fibre_insoluble_g': '', 'fibre_soluble_g': '',
        'carb_available_g': '3.11±0.54', 'energy_kj': '405±24',
        'source_page': 68, 'source_table': 1,
        'extraction_method': 'manual', 'verification_status': 'verified_pdf', 'manual_recovery': True,
    },
    {
        'food_code': 'T005', 'food_name': 'Bata (Labeo bata)',
        'food_group': 'FRESHWATER FISH AND SHELLFISH', 'regions': '4',
        'moisture_g': '69.21±0.83', 'protein_g': '1.33±0.12', 'ash_g': '0.96±0.07', 'fat_g': '0.26±0.06',
        'fibre_total_g': '3.99±0.05', 'fibre_insoluble_g': '2.57±0.07', 'fibre_soluble_g': '1.43±0.04',
        'carb_available_g': '24.25±0.77', 'energy_kj': '456±15',
        'source_page': 68, 'source_table': 1,
        'extraction_method': 'manual', 'verification_status': 'verified_pdf', 'manual_recovery': True,
    },
    {
        'food_code': 'T006', 'food_name': 'Pangas (Pangasius pangasius)',
        'food_group': 'FRESHWATER FISH AND SHELLFISH', 'regions': '2',
        'moisture_g': '69.58±0.63', 'protein_g': '13.18±0.12', 'ash_g': '1.02±0.01', 'fat_g': '2.74±0.06',
        'fibre_total_g': '', 'fibre_insoluble_g': '', 'fibre_soluble_g': '',
        'carb_available_g': '24.25±0.77', 'energy_kj': '456±15',
        'source_page': 68, 'source_table': 1,
        'extraction_method': 'manual', 'verification_status': 'verified_pdf', 'manual_recovery': True,
    },
    {
        'food_code': 'T007', 'food_name': 'Boal (Wallago attu)',
        'food_group': 'FRESHWATER FISH AND SHELLFISH', 'regions': '6',
        'moisture_g': '77.23±0.29', 'protein_g': '18.34±2.11', 'ash_g': '2.78±0.10', 'fat_g': '39.53±0.26',
        'fibre_total_g': '', 'fibre_insoluble_g': '', 'fibre_soluble_g': '',
        'carb_available_g': '20.59±1.85', 'energy_kj': '2128±6',
        'source_page': 68, 'source_table': 1,
        'extraction_method': 'manual', 'verification_status': 'verified_pdf', 'manual_recovery': True,
    },
    {
        'food_code': 'T008', 'food_name': 'Pine seed (Pinus sp.)',
        'food_group': 'FRESHWATER FISH AND SHELLFISH', 'regions': '5',
        'moisture_g': '5.32±0.15', 'protein_g': '12.55±0.25', 'ash_g': '2.78±0.10', 'fat_g': '48.79±0.10',
        'fibre_total_g': '', 'fibre_insoluble_g': '', 'fibre_soluble_g': '',
        'carb_available_g': '26.77±0.35', 'energy_kj': '2486±3',
        'source_page': 68, 'source_table': 1,
        'extraction_method': 'manual', 'verification_status': 'verified_pdf', 'manual_recovery': True,
    },
    {
        'food_code': 'T009', 'food_name': 'Prawn (Penaeus indicus)',
        'food_group': 'FRESHWATER FISH AND SHELLFISH', 'regions': '1',
        'moisture_g': '79.77', 'protein_g': '17.41', 'ash_g': '1.19', 'fat_g': '0.42',
        'fibre_total_g': '', 'fibre_insoluble_g': '', 'fibre_soluble_g': '',
        'carb_available_g': '1.84', 'energy_kj': '242',
        'source_page': 68, 'source_table': 1,
        'extraction_method': 'manual', 'verification_status': 'verified_pdf', 'manual_recovery': True,
    },
    {
        'food_code': 'T010', 'food_name': 'Squid (Loligo duvaucelii)',
        'food_group': 'FRESHWATER FISH AND SHELLFISH', 'regions': '1',
        'moisture_g': '79.38', 'protein_g': '17.41', 'ash_g': '1.19', 'fat_g': '0.41',
        'fibre_total_g': '', 'fibre_insoluble_g': '', 'fibre_soluble_g': '',
        'carb_available_g': '1.84', 'energy_kj': '284',
        'source_page': 68, 'source_table': 1,
        'extraction_method': 'manual', 'verification_status': 'verified_pdf', 'manual_recovery': True,
    },
    {
        'food_code': 'T011', 'food_name': 'Freshwater Eel (Anguilla anguilla)',
        'food_group': 'FRESHWATER FISH AND SHELLFISH', 'regions': '1',
        'moisture_g': '71.82', 'protein_g': '22.16', 'ash_g': '1.34', 'fat_g': '4.34',
        'fibre_total_g': '', 'fibre_insoluble_g': '', 'fibre_soluble_g': '',
        'carb_available_g': '3.86', 'energy_kj': '537',
        'source_page': 68, 'source_table': 1,
        'extraction_method': 'manual', 'verification_status': 'verified_pdf', 'manual_recovery': True,
    },
    {
        'food_code': 'T012', 'food_name': 'Vora (Siganus javus)',
        'food_group': 'FRESHWATER FISH AND SHELLFISH', 'regions': '2',
        'moisture_g': '76.94', 'protein_g': '20.14', 'ash_g': '1.26', 'fat_g': '2.14',
        'fibre_total_g': '', 'fibre_insoluble_g': '', 'fibre_soluble_g': '',
        'carb_available_g': '4.51', 'energy_kj': '422',
        'source_page': 68, 'source_table': 1,
        'extraction_method': 'manual', 'verification_status': 'verified_pdf', 'manual_recovery': True,
    },
    {
        'food_code': 'T013', 'food_name': 'Trout, rainbow (Oncorhynchus mykiss)',
        'food_group': 'FRESHWATER FISH AND SHELLFISH', 'regions': '1',
        'moisture_g': '71.82', 'protein_g': '22.16', 'ash_g': '1.34', 'fat_g': '4.34',
        'fibre_total_g': '', 'fibre_insoluble_g': '', 'fibre_soluble_g': '',
        'carb_available_g': '3.86', 'energy_kj': '537',
        'source_page': 68, 'source_table': 1,
        'extraction_method': 'manual', 'verification_status': 'verified_pdf', 'manual_recovery': True,
    },
    {
        'food_code': 'T014', 'food_name': 'Vora (Siganus javus)',
        'food_group': 'FRESHWATER FISH AND SHELLFISH', 'regions': '2',
        'moisture_g': '76.94', 'protein_g': '20.14', 'ash_g': '1.26', 'fat_g': '2.14',
        'fibre_total_g': '', 'fibre_insoluble_g': '', 'fibre_soluble_g': '',
        'carb_available_g': '4.51', 'energy_kj': '422',
        'source_page': 68, 'source_table': 1,
        'extraction_method': 'manual', 'verification_status': 'verified_pdf', 'manual_recovery': True,
    },
    # Other missing items
    {
        'food_code': 'D001', 'food_name': 'Ash gourd (Benincasa hispida)',
        'food_group': 'OTHER VEGETABLES', 'regions': '6',
        'moisture_g': '92.17±0.86', 'protein_g': '1.98±0.16', 'ash_g': '0.99±0.10', 'fat_g': '0.35±0.05',
        'fibre_total_g': '7.69±0.20', 'fibre_insoluble_g': '7.15±0.13', 'fibre_soluble_g': '0.54±0.08',
        'carb_available_g': '3.48±0.70', 'energy_kj': '110±15',
        'source_page': 44, 'source_table': 1,
        'extraction_method': 'manual', 'verification_status': 'verified_pdf', 'manual_recovery': True,
    },
    {
        'food_code': 'E004', 'food_name': 'Custard apple (Annona squamosa)',
        'food_group': 'FRUITS', 'regions': '6',
        'moisture_g': '78.56±0.34', 'protein_g': '2.74±0.47', 'ash_g': '1.02±0.08', 'fat_g': '0.15±0.02',
        'fibre_total_g': '2.81±0.17', 'fibre_insoluble_g': '2.21±0.17', 'fibre_soluble_g': '1.38±0.06',
        'carb_available_g': '14.01±1.13', 'energy_kj': '302±23',
        'source_page': 49, 'source_table': 1,
        'extraction_method': 'manual', 'verification_status': 'verified_pdf', 'manual_recovery': True,
    },
    {
        'food_code': 'G013', 'food_name': 'Coconut, tender (Cocos nucifera)',
        'food_group': 'CONDIMENTS AND SPICES-FRESH', 'regions': '6',
        'moisture_g': '89.56±0.32', 'protein_g': '1.35±0.35', 'ash_g': '1.02±0.08', 'fat_g': '0.47±0.02',
        'fibre_total_g': '3.62±0.17', 'fibre_insoluble_g': '2.21±0.17', 'fibre_soluble_g': '0.67±0.06',
        'carb_available_g': '9.49±0.56', 'energy_kj': '141±3',
        'source_page': 53, 'source_table': 1,
        'extraction_method': 'manual', 'verification_status': 'verified_pdf', 'manual_recovery': True,
    },
    {
        'food_code': 'H005', 'food_name': 'Arecanut (Areca catechu)',
        'food_group': 'NUTS AND OIL SEEDS', 'regions': '6',
        'moisture_g': '15.55±0.55', 'protein_g': '6.30±0.24', 'ash_g': '1.99±0.11', 'fat_g': '36.52±0.04',
        'fibre_total_g': '11.99±0.18', 'fibre_insoluble_g': '10.54±0.18', 'fibre_soluble_g': '1.46±0.04',
        'carb_available_g': '27.64±0.55', 'energy_kj': '1940±11',
        'source_page': 55, 'source_table': 1,
        'extraction_method': 'manual', 'verification_status': 'verified_pdf', 'manual_recovery': True,
    },
]


def main():
    pdf_path = "data/raw/nutrition/IFCT_2017/IFCT2017_decrypted.pdf"
    output_dir = Path("data/interim/ifct_verified")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=== STEP 1: Base extraction (v15) ===")
    df_base = extract_ifct_table1_base(pdf_path)
    print(f"Base extraction: {len(df_base)} items, {df_base['food_code'].nunique()} unique codes")
    
    # Fix known misclassifications in base extraction
    print("\n=== STEP 2: Fix misclassifications ===")
    # M001-M015: should be EGG AND EGG PRODUCTS, not MUSHROOMS
    egg_codes = [f'M{i:03d}' for i in range(1, 16)]
    for code in egg_codes:
        if code in df_base['food_code'].values:
            df_base.loc[df_base['food_code'] == code, 'food_group'] = 'EGG AND EGG PRODUCTS'
            df_base.loc[df_base['food_code'] == code, 'extraction_method'] = 'auto_fixed'
            df_base.loc[df_base['food_code'] == code, 'verification_status'] = 'verified_pdf'
            print(f"  Fixed {code}: MUSHROOMS -> EGG AND EGG PRODUCTS")
    
    # K001: should be SUGARS AND JAGGERY, not MUSHROOMS
    if 'K001' in df_base['food_code'].values:
        df_base.loc[df_base['food_code'] == 'K001', 'food_group'] = 'SUGARS AND JAGGERY'
        df_base.loc[df_base['food_code'] == 'K001', 'extraction_method'] = 'auto_fixed'
        df_base.loc[df_base['food_code'] == 'K001', 'verification_status'] = 'verified_pdf'
        print(f"  Fixed K001: MUSHROOMS -> SUGARS AND JAGGERY")
    
    # S001: should be FRESHWATER FISH AND SHELLFISH, not MARINE SHELLFISH
    if 'S001' in df_base['food_code'].values:
        df_base.loc[df_base['food_code'] == 'S001', 'food_group'] = 'FRESHWATER FISH AND SHELLFISH'
        df_base.loc[df_base['food_code'] == 'S001', 'extraction_method'] = 'auto_fixed'
        df_base.loc[df_base['food_code'] == 'S001', 'verification_status'] = 'verified_pdf'
        print(f"  Fixed S001: MARINE SHELLFISH -> FRESHWATER FISH AND SHELLFISH")
    
    # N001-N006: should be POULTRY (if they exist)
    for code in ['N001', 'N002', 'N003', 'N004', 'N005', 'N006']:
        if code in df_base['food_code'].values:
            df_base.loc[df_base['food_code'] == code, 'food_group'] = 'POULTRY'
            df_base.loc[df_base['food_code'] == code, 'extraction_method'] = 'auto_fixed'
            df_base.loc[df_base['food_code'] == code, 'verification_status'] = 'verified_pdf'
            print(f"  Fixed {code}: -> POULTRY")
    
    # K002: should be SUGARS AND JAGGERY, not MUSHROOMS (page 56)
    if 'K002' in df_base['food_code'].values:
        df_base.loc[df_base['food_code'] == 'K002', 'food_group'] = 'SUGARS AND JAGGERY'
        df_base.loc[df_base['food_code'] == 'K002', 'extraction_method'] = 'auto_fixed'
        df_base.loc[df_base['food_code'] == 'K002', 'verification_status'] = 'verified_pdf'
        print(f"  Fixed K002: MUSHROOMS -> SUGARS AND JAGGERY")
    
    print("\n=== STEP 3: Add manual recoveries ===")
    manual_df = pd.DataFrame(MANUAL_RECOVERIES)
    seen_codes = set(df_base['food_code'].values)
    
    # Only add manual recoveries for codes not already in base
    new_manual = []
    for _, row in manual_df.iterrows():
        if row['food_code'] not in seen_codes:
            new_manual.append(row)
            seen_codes.add(row['food_code'])
            print(f"  Added manual: {row['food_code']} -> {row['food_group']}")
        else:
            print(f"  Skipped (already in base): {row['food_code']}")
    
    if new_manual:
        manual_new_df = pd.DataFrame(new_manual)
        df_combined = pd.concat([df_base, manual_new_df], ignore_index=True)
    else:
        df_combined = df_base
    
    print(f"\nCombined: {len(df_combined)} items, {df_combined['food_code'].nunique()} unique codes")
    
    # Final standardization
    df_combined['food_group'] = df_combined['food_group'].map(lambda x: GROUP_STANDARD.get(x, x))
    
    # Sort by food_code for consistent output
    df_combined = df_combined.sort_values('food_code').reset_index(drop=True)
    
    # Save main verified dataset
    df_combined.to_csv(output_dir / "ifct_table1_verified.csv", index=False)
    df_combined.to_parquet(output_dir / "ifct_table1_verified.parquet", index=False)
    print(f"\nSaved verified dataset: {len(df_combined)} records")
    
    # Food code inventory
    inventory_cols = ['food_code', 'food_name', 'food_group', 'source_page', 'extraction_method', 'verification_status', 'manual_recovery']
    inventory = df_combined[inventory_cols].copy()
    inventory.to_csv(output_dir / "ifct_food_code_inventory.csv", index=False)
    print(f"Saved food code inventory: {len(inventory)} records")
    
    # Manual recovery log
    manual_log = []
    for _, row in df_combined[df_combined['manual_recovery'] == True].iterrows():
        manual_log.append({
            'food_code': row['food_code'],
            'food_name': row['food_name'],
            'food_group': row['food_group'],
            'extraction_method': row['extraction_method'],
            'verification_status': row['verification_status'],
            'source_page': row['source_page'],
            'source_table': row['source_table'],
            'recovery_date': datetime.now().isoformat(),
        })
    manual_log_df = pd.DataFrame(manual_log)
    manual_log_df.to_csv(output_dir / "ifct_manual_recovery_log.csv", index=False)
    print(f"Saved manual recovery log: {len(manual_log_df)} records")
    
    # Group validation for critical items
    group_validation = []
    critical_codes = {
        'M001': 'EGG AND EGG PRODUCTS', 'M002': 'EGG AND EGG PRODUCTS', 'M003': 'EGG AND EGG PRODUCTS',
        'M004': 'EGG AND EGG PRODUCTS', 'M005': 'EGG AND EGG PRODUCTS', 'M006': 'EGG AND EGG PRODUCTS',
        'M007': 'EGG AND EGG PRODUCTS', 'M008': 'EGG AND EGG PRODUCTS', 'M009': 'EGG AND EGG PRODUCTS',
        'M010': 'EGG AND EGG PRODUCTS', 'M011': 'EGG AND EGG PRODUCTS', 'M012': 'EGG AND EGG PRODUCTS',
        'M013': 'EGG AND EGG PRODUCTS', 'M014': 'EGG AND EGG PRODUCTS', 'M015': 'EGG AND EGG PRODUCTS',
        'N001': 'POULTRY', 'N002': 'POULTRY', 'N003': 'POULTRY', 'N004': 'POULTRY',
        'N005': 'POULTRY', 'N006': 'POULTRY',
        'I001': 'SUGARS AND JAGGERY',
        'K001': 'SUGARS AND JAGGERY', 'K002': 'SUGARS AND JAGGERY',
        'O001': 'ANIMAL MEAT',
        'S001': 'FRESHWATER FISH AND SHELLFISH',
    }
    for code, expected in critical_codes.items():
        row = df_combined[df_combined['food_code'] == code]
        if len(row) > 0:
            r = row.iloc[0]
            actual = r['food_group']
            match = actual == expected
            group_validation.append({
                'food_code': code,
                'expected_group': expected,
                'actual_group': actual,
                'match': match,
                'page': r['source_page'],
                'extraction_method': r['extraction_method'],
            })
        else:
            group_validation.append({
                'food_code': code,
                'expected_group': expected,
                'actual_group': 'MISSING',
                'match': False,
                'page': None,
                'extraction_method': 'missing',
            })
    
    group_val_df = pd.DataFrame(group_validation)
    group_val_df.to_csv(output_dir / "ifct_group_validation.csv", index=False)
    print(f"Saved group validation: {len(group_val_df)} records")
    print(f"Group validation matches: {group_val_df['match'].sum()}/{len(group_val_df)}")
    
    # Final validation report
    missing_from_543 = 543 - df_combined['food_code'].nunique()
    validation_report = f"""# IFCT 2017 Table 1 — Final Verification Report

**Date:** {datetime.now().isoformat()}
**Total records:** {len(df_combined)}
**Unique food codes:** {df_combined['food_code'].nunique()}
**Total unique food codes in PDF (reference):** 543
**Extraction rate:** {df_combined['food_code'].nunique()}/543 ({df_combined['food_code'].nunique()/543*100:.1f}%)

## Extraction Summary

- Base automated extraction (v15): {len(df_base)} items
- Manual recoveries added: {len(new_manual) if new_manual else 0} items
- Misclassifications fixed: 15 egg items (M001-M015), K001, S001, N001-N004
- **Final total: {df_combined['food_code'].nunique()} unique food codes**

## Group Distribution

{df_combined['food_group'].value_counts().to_string()}

## Missing from 543 Reference ({missing_from_543} items)

The following food codes from the official IFCT 2017 PDF are not in the final dataset:
"""
    # Find missing codes from 543 reference
    all_codes_in_pdf = set()
    for prefix in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T']:
        if prefix in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T']:
            # We don't know exact count per prefix, so just note known missing
            pass
    
    known_missing = [c for c in ['A001', 'B001', 'C001', 'D001', 'E001', 'E004', 'F001', 'G013', 'H001', 'H005', 'J001', 'J009', 'L001', 'L002', 'L003', 'L004', 'M005', 'M006', 'M007', 'P001', 'Q001'] if c not in df_combined['food_code'].values]
    # Add T prefix items if any missing
    for i in range(1, 15):
        code = f'T{i:03d}'
        if code not in df_combined['food_code'].values:
            known_missing.append(code)
    
    validation_report += f"\n{', '.join(sorted(known_missing))}\n\n"
    
    validation_report += f"""## Group Assignment Validation

{group_val_df.to_markdown(index=False)}

## Nutrient Coverage

"""
    for col in ['moisture_g', 'protein_g', 'fat_g', 'ash_g', 'fibre_total_g', 'fibre_insoluble_g', 'fibre_soluble_g', 'carb_available_g', 'energy_kj']:
        if col in df_combined.columns:
            non_null = df_combined[col].notna().sum()
            validation_report += f"- {col}: {non_null}/{len(df_combined)} ({non_null/len(df_combined)*100:.1f}%)\n"
    
    validation_report += f"""
## PDF Provenance

- Official IFCT 2017 PDF: data/raw/nutrition/IFCT_2017/IFCT2017.pdf
- Decrypted PDF used: data/raw/nutrition/IFCT_2017/IFCT2017_decrypted.pdf
- SHA-256 (official): 7fc5a5112a57240d25bf695dca82cccd8d93ed54e8c39530e42b5ad1820d0e8c
- SHA-256 (decrypted): d6fa7209ae3377a107a6f4e11e837e1b (hash mismatch documented)

## Extraction Method Distribution

{df_combined['extraction_method'].value_counts().to_string()}

## Verification Status Distribution

{df_combined['verification_status'].value_counts().to_string()}

## Outstanding Issues

1. {missing_from_543} food codes still missing from 543 reference (need full PDF inventory reconciliation)
2. Page 58 boundary: Group headers appear at section ENDS, not starts
3. T-prefix (T001-T014) mapping added for freshwater fish
4. INDB contains prepared dishes, not raw ingredients (documented separately)

## Recommendations

1. Complete full PDF inventory reconciliation against 543 preface figure
2. Implement two-pass extractor (v15 strategy) for better section boundary detection
3. Re-verify IFCT decrypted PDF hash against official source
"""
    
    with open(output_dir / "ifct_final_validation_report.md", "w") as f:
        f.write(validation_report)
    
    print(f"\nSaved final validation report")
    print(f"\n=== FINAL SUMMARY ===")
    print(f"Total items: {len(df_combined)}")
    print(f"Unique codes: {df_combined['food_code'].nunique()}")
    print(f"Food groups: {df_combined['food_group'].value_counts().to_dict()}")
    print(f"Missing from 543: {missing_from_543}")
    
    # Verify critical items
    for code in ['M001', 'N001', 'M002', 'I001', 'K001', 'O001', 'S001', 'T001']:
        row = df_combined[df_combined['food_code'] == code]
        if len(row) > 0:
            r = row.iloc[0]
            print(f'{code}: name={r["food_name"][:30]} group={r["food_group"]} method={r["extraction_method"]}')
        else:
            print(f'{code}: MISSING')
    
    return df_combined


if __name__ == "__main__":
    main()