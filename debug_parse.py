import pandas as pd
import sys

# Load normalized ingredients
norm_df = pd.read_parquet('data/interim/phase2/normalized_ingredients.parquet')
print(f"Loaded {len(norm_df)} records for {norm_df['recipe_id'].nunique()} recipes")

# Check first row
row = norm_df.iloc[0]
print(f"Row: recipe_id={row['recipe_id']}, flags={row['flags']}")
print(f"Normalized: {row['normalized_ingredient'][:100]}")

# Test parser directly
sys.path.insert(0, 'src/ingredients')
from ingredient_parser import IngredientParser

parser = IngredientParser()
text = norm_df.iloc[0]['normalized_ingredient']
print(f"Input text: {text}")

# Test parse_quantity
from ingredient_parser import ParsedQuantity, ParsedUnit
qty, remaining = parser.parse_quantity(text)
print(f"Quantity: {qty}, remaining: {remaining[:100]}")

# Test extract_unit
unit, remaining = parser.extract_unit(text)
print(f"Unit: {unit}, remaining: {remaining[:100]}")

# Test full parse
parsed = parser.parse(text)
print(f"Parsed: name={parsed.ingredient_name}, qty={parsed.quantity}, unit={parsed.unit}, status={parsed.parse_status}")