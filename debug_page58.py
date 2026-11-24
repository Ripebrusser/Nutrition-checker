import fitz
import re

doc = fitz.open('data/raw/nutrition/IFCT_2017/IFCT2017.pdf')
page = doc[57]  # Page 58
text = page.get_text()
lines = [line.strip() for line in text.split('\n')]

# Simulate the v25 extractor logic exactly
lines_list = [line.strip() for line in text.split('\n')]
print(f'Page 58 has {len(lines)} lines')

# Simulate the v25 extractor logic exactly
seen_codes = set()
current_group = ''
i = 0
while i < len(lines):
    line = lines[i].strip()
    if not line:
        i += 1
        continue
    
    # Check for group header
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
        print(f'Line {i}: GROUP HEADER -> {group}')
        current_group = group
        i += 1
        continue
    
    # Check for single-letter group prefix
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
            ('FRESHWATER FISH AND SHELLFISH', 'FRESHWATER FISH AND SHELLFISH'),
            ('FATS AND EDIBLE OILS', 'FATS AND EDIBLE OILS'),
        ]:
            if pdf_h.upper() in lines[i + 1].upper():
                current_group = pdf_h
                print(f'  Line {i}: PREFIX "{line}" + "{lines[i+1]}" -> {pdf_h}')
                i += 2
                break
        else:
            i += 1
        continue
    
    # Check for food code
    if re.match(r'^[A-Z]\d{3}$', line):
        food_code = line.strip()
        print(f'Found food code at line {i}: {food_code}')
        
        if food_code in seen_codes:
            i += 1
            continue
        
        seen_codes.add(food_code)
        
        # Extract food data (forward)
        food_name = ''
        regions = ''
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
                               'CEREALS AND MILLETS', 'GRAIN LEGUMES', 'GREEN LEAFY VEGETABLES', 'LEAFY VEGETABLES', 'OTHER VEGETABLES', 'FRUITS', 'ROOTS AND TUBERS', 'CONDIMENTS AND SPICES-FRESH', 'CONDIMENTS AND SPICES-DRY', 'NUTS AND OIL SEEDS', 'MUSHROOMS', 'MISCELLANEOUS FOODS', 'MISCELLANEOUS', 'MILK AND MILK PRODUCTS', 'EGG AND EGG PRODUCTS', 'POULTRY', 'ANIMAL MEAT', 'MARINE FISH', 'MARINE SHELLFISH', 'SUGARS', 'SUGARS AND JAGGERY', 'FRESHWATER FISH AND SHELLFISH', 'FATS AND EDIBLE OILS']):
                break
            if next_line in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S']:
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
            print(f'  Extracted {food_code}: name={food_name}, group=?, nutrients={len(nutrient_vals)}')
        
        i = j
        continue
    
    i += 1

print(f'Total extracted: {len(seen_codes)}')
print(f'Codes found: {sorted(seen_codes)}')