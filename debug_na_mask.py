import pandas as pd

parquet_df = pd.read_parquet("data/interim/phase2/parsed_recipe_ingredients.parquet")
csv_df = pd.read_csv("data/interim/phase2/parsed_recipe_ingredients.csv")

col = 'ingredient_name'
p = parquet_df[col].reset_index(drop=True)
c = csv_df[col].reset_index(drop=True)

p_na = p.isna()
c_na = c.isna()
c_empty = (c == '')

print(f"Parquet NA count: {p_na.sum()}")
print(f"CSV NA count: {c_na.sum()}")
print(f"CSV empty count: {(c == '').sum()}")

print(f"\nParquet NA sample: {p[p.isna()].head()}")
print(f"CSV NA sample: {c[c.isna()].head()}")
print(f"CSV empty sample: {c[c == ''].head()}")

# Check where they differ
p_na_mask = p.isna()
c_na_mask = c.isna() | (c == '')
print(f"\nNA mask match: {(p.isna() == c_na).all()}")

# Find mismatches
mismatch = (p.isna() != (c.isna() | (c == '')))
print(f"Mismatch count: {mismatch.sum()}")
if mismatch.any():
    idx = mismatch.idxmax()
    print(f"Mismatch at index {idx}: parquet_na={p.iloc[idx]}, csv_na={c.isna().iloc[idx]}, csv_empty={(c == '').iloc[idx]}")
    print(f"  parquet value: '{p.iloc[idx]}'")
    print(f"  csv value: '{c.iloc[idx]}'")
    print(f"  csv isna: {c.isna().iloc[idx]}, csv == '': {(c == '').iloc[idx]}")