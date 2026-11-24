import pandas as pd
import fitz
import re

# Load current extracted data
df = pd.read_csv('data/interim/ifct_extracted/table1_parsed.csv')
print('Current extracted:')
print(f'  Total items: {len(df)}')
print(f'Unique codes: {df["food_code"].nunique()}')

# Get all codes from PDF
import fitz
doc = fitz.open('data/raw/nutrition/IFCT_2017/IFCT2017.pdf')
all_codes = set()
for page_num in range(585):
    page = doc[page_num]
    text = page.get_text()
    for line in text.split('\n'):
        line_stripped = line.strip()
        if re.match(r'^[A-Z]\d{3}$', line.strip()):
            all_codes.add(line.strip())
doc.close()

# Load v25 output
df_v25 = pd.read_csv('data/interim/ifct_extracted/table1_parsed.csv')
v25_codes = set(df['food_code'].tolist())

all_codes = set()
import fitz
doc = fitz.open('data/raw/nutrition/IFCT_2017/IFCT2017.pdf')
for page_num in range(585):
    page = doc[page_num]
    text = page.get_text()
    for line in text.split('\n'):
        line_stripped = line.strip()
        if re.match(r'^[A-Z]\d{3}$', line.strip()):
            all_codes.add(line.strip())

v25_codes = set(df['food_code'].tolist())
missing = sorted(all_codes - v25_codes)
print('Missing from v25:', sorted(all_codes - v25_codes))
print(f'Missing count: {len(missing)}')