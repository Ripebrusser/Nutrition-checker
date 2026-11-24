import pandas as pd

parquet_df = pd.read_parquet("data/interim/phase2/parsed_recipe_ingredients.parquet")
csv_df = pd.read_csv("data/interim/phase2/parsed_recipe_ingredients.csv")

print(f"Parquet shape: {parquet_df.shape}, CSV shape: {csv_df.shape}")
print(f"Columns match: {list(parquet_df.columns) == list(csv_df.columns)}")

# Check each column for differences
for col in parquet_df.columns:
    p = parquet_df[col]
    c = csv_df[col]
    
    if p.dtype != c.dtype:
        print(f"Column {col}: dtype mismatch - parquet={p.dtype}, csv={c.dtype}")
        continue
    
    # Check for NA differences
    p_na = p.isna()
    c_na = c.isna()
    if not p_na.equals(c_na):
        diff_count = (p_na != c_na).sum()
        print(f"Column {col}: NA mask differs in {diff_count} rows")
        # Show examples
        diff_idx = (p_na != c_na)
        if diff_idx.any():
            print(f"  Examples: parquet_na={p_na[diff_idx].iloc[0]}, csv_na={c_na[diff_idx].iloc[0]}")
    
    # Check value differences for non-NA
    if p.dtype == 'object':
        p_vals = p.fillna('__NA__')
        c_vals = c.fillna('__NA__')
        if not (p_vals == c_vals).all():
            diff = (p_vals != c_vals).sum()
            print(f"Column {col}: {diff} value differences")
            diff_idx = (p_vals != c_vals)
            if diff_idx.any():
                print(f"  Example: parquet='{p[diff_idx].iloc[0]}', csv='{c[diff_idx].iloc[0]}'")
        else:
            diff = (p != c).sum()
            if diff > 0:
                print(f"Column {col}: {diff} numeric differences")