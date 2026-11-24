import re

# Test the regex
test = 'B001'
pattern = r'^[A-Z]\d{3}$'
print(f'Match: {re.match(pattern, test)}')
print(f'Fullmatch: {re.fullmatch(r"^[A-Z]\d{3}$", "B001")}')

# Check if there's a BOM or invisible char
s = 'B001'
print(f'Bytes: {s.encode()}')
print(f'Ord: {[ord(c) for c in s]}')