import fitz

doc = fitz.open('data/raw/nutrition/IFCT_2017/IFCT2017.pdf')
page = doc[41]  # Page 42
text = page.get_text()
lines = [line.strip() for line in text.split('\n')]

for i, line in enumerate(text.split('\n')):
    line_stripped = line.strip()
    if 'B001' in line:
        print(f'Line: {repr(line)}')
        print(f'Stripped: {repr(line.strip())}')
        import re
        print(f'Match: {re.match(r"^[A-Z]\\d{3}$", line.strip())}')
        break

doc.close()