import re

# Test the nutrient regex
pattern = r'[\d\.]+(?:±[\d\.]+)?'
test_strings = ['76.51±0.20', '13.28±0.29', '0.81±0.04', '9.15±0.14', '564±3']

for s in ['76.51±0.20', '13.28±0.29', '0.81±0.04', '9.15±0.14', '564±3']:
    matches = re.findall(r'[\d\.]+(?:±[\d\.]+)?', s)
    print(f'{s}: {re.findall(r"[\d\.]+(?:±[\d\.]+)?", s)}')