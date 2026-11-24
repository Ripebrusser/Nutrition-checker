import fitz
import re

doc = fitz.open('data/raw/nutrition/IFCT_2017/IFCT2017.pdf')

# Check page 42 (index 41) for D001
page = doc[41]  # Page 42
text = page.get_text()

print('=== PAGE 42 ===')
for i, line in enumerate(text.split('\n')):
    line_stripped = line.strip()
    if 'D001' in line:
        print(f'Line: {repr(line)}')
        print(f'Stripped: {repr(line.strip())}')
        print(f'Match: {re.match(r"^[A-Z]\\d{3}$", line.strip())}')
        break

# Check if D001 is in the lines list
lines_list = [line.strip() for line in text.split('\n')]
for line in lines_list:
    if line == 'D001':
        print('Found D001 in lines list')
        break
else:
    print('D001 NOT FOUND in lines list')

# Check all food codes on this page
food_codes = [line for line in [l.strip() for l in text.split('\n')] if re.match(r'^[A-Z]\d{3}$', line.strip())]
print(f'Page 42 food codes: {food_codes}')

doc.close()