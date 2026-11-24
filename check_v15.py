import pandas as pd
import fitz
import re

# Load v25 output
df_v25 = pd.read_csv('data/interim/ifct_extracted/table1_parsed.csv')
print('v25 output:')
print(f'  Total: {len(df_v25)}')
print(f'Unique: {df_v25["food_code"].nunique()}')

# Get all codes from PDF
import fitz
import re

doc = fitz.open('data/raw/nutrition/IFCT_2017/IFCT2017.pdf')
all_codes = set()
for page_num in range(585):
    page = doc[page_num]
    text = page.get_text()
    for line in text.split('\n'):
        line_stripped = line.strip()
        if re.match(r'^[A-Z]\d{3}$', line.strip()):
            all_codes.add(line.strip())

v25_codes = set(pd.read_csv('data/interim/ifct_extracted/table1_parsed.csv')['food_code'].tolist())
missing = sorted(all_codes - v25_codes)
print('Missing from v15:', sorted(missing))
print(f'Missing count: {len(missing)}')