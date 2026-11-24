import pandas as pd
import time
norm_df = pd.read_parquet('data/interim/phase2/normalized_ingredients.parquet')

# Check if there's any filtering in the main loop by counting iterations
from src.ingredients.ingredient_parser import IngredientParser
parser = IngredientParser()

# Check if there's any filtering in the main loop by counting iterations
count = 0
start = time.time()
for _, row in norm_df.iterrows():
    if count % 50000 == 0:
        print(f'Processed {count} records')
    count += 1
print(f'Total iterations: {count}')
print(f'Time: {time.time() - start:.2f}s')

# Now check what the actual parsing loop produces
from src.ingredients.ingredient_parser import IngredientParser
parser = IngredientParser()

parsed_records = []
for i, (_, row) in enumerate(norm_df.iterrows()):
    if i % 50000 == 0:
        print(f'Parsed {i} records')
    parsed = __import__('src.ingredients.ingredient_parser', fromlist=['IngredientParser']).IngredientParser().parse(row['normalized_ingredient'])
    # We're not actually appending here, just checking if it runs
    if i == len(norm_df) - 1:
        print(f'Last record processed: {i}')

print('Done iterating')