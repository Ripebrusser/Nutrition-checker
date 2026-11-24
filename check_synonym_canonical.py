import pandas as pd
syn_df = pd.read_csv('data/interim/phase2/ingredient_synonyms.csv')

# Check canonical names that map to IFCT
print("All canonical names in synonym dict:")
for name in syn_df['canonical_name'].unique():
    print(f'  {name}')

print("\n\nSynonyms for pigeon pea:")
pigeon = syn_df[syn_df['canonical_name'] == 'pigeon pea']
for _, row in pigeon.iterrows():
    print(f'  {row["synonym"]} -> {row["canonical_name"]}')

print("\n\nSynonyms for red gram:")
red = syn_df[syn_df['canonical_name'].str.contains('red gram', case=False)]
for _, row in red.iterrows():
    print(f'  {row["synonym"]} -> {row["canonical_name"]}')

# Check if any canonical_name matches IFCT food names
ifct = pd.read_parquet('data/interim/ifct_final_candidate/ifct_table1_candidate.parquet')
ifct_names = set(ifct['food_name'].str.lower().str.strip())

print("\n\nCanonical names that match IFCT food names:")
for name in syn_df['canonical_name'].unique():
    if name.lower().strip() in ifct_names:
        print(f'  MATCH: {name}')

# Check partial matches
print("\n\nCanonical names with partial IFCT matches:")
for name in syn_df['canonical_name'].unique():
    for ifct_name in ifct_names:
        if name.lower() in ifct_name or ifct_name in name.lower():
            print(f'  PARTIAL: {name} <-> {ifct_name}')
            break