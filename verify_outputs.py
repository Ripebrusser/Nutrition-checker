import pandas as pd
norm = pd.read_parquet('data/interim/phase2/normalized_ingredients.parquet')
syn = pd.read_csv('data/interim/phase2/ingredient_synonyms.csv')
print(f'Normalized ingredients: {len(norm)} records, {norm["recipe_id"].nunique()} unique recipes')
print(f'Synonym dictionary: {len(syn)} entries')
print(f'Unique synonyms applied: {norm[norm["synonym_applied"].notna()]["synonym_applied"].nunique()}')
print(f'Synonym dictionary categories: {syn["category"].value_counts().to_dict()}')

# Check CSV/Parquet parity
norm_csv = pd.read_csv('data/interim/phase2/normalized_ingredients.csv')
norm_parq = pd.read_parquet('data/interim/phase2/normalized_ingredients.parquet')
print(f'CSV/Parquet row count match: {len(norm_csv) == len(norm_parq)}')
print(f'Columns match: {list(norm_csv.columns) == list(norm_parq.columns)}')

# Check original text preserved
print(f'Original ingredient text preserved: {norm["source_ingredient"].notna().all()}')

# Check transformations recorded
print(f'Transformations recorded: {norm["transformations"].notna().all()}')

# Check flags
print(f'Flags recorded: {norm["flags"].notna().all()}')

# Check source tracking
has_raw = norm['flags'].str.contains('source:ingredients_raw').any()
has_en = norm['flags'].str.contains('source:ingredients_en').any()
print(f'Source tracking (raw): {has_raw}')
print(f'Source tracking (en): {has_en}')

# Check synonym tracking
applied = norm['synonym_applied'].notna().sum()
print(f'Synonym applications: {applied}')

# Check flags
has_no_match = norm['flags'].str.contains('no_synonym_match').any()
print(f'Has no_synonym_match flag: {has_no_match}')

# Check repro
grouped = norm.groupby(['recipe_id', 'source_ingredient'])['normalized_ingredient'].nunique()
inconsistent = grouped[grouped > 1]
print(f'Deterministic: {len(inconsistent) == 0}')

# Check CSV/Parquet parity
norm_csv = pd.read_csv('data/interim/phase2/normalized_ingredients.csv')
norm_parq = pd.read_parquet('data/interim/phase2/normalized_ingredients.parquet')
print(f'CSV/Parquet parity: {len(norm_csv) == len(norm_parq) and list(norm_csv.columns) == list(norm_parq.columns)}')