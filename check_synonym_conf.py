import pandas as pd
syn_df = pd.read_csv('data/interim/phase2/ingredient_synonyms.csv')
print('Synonym confidence distribution:')
print(syn_df['confidence'].value_counts().sort_index())
print()
print('Confidence >= 0.95:')
high = syn_df[syn_df['confidence'] >= 0.95]
print(f'  Count: {len(high)}')
print('  Categories:', high['category'].value_counts().to_dict())
print()
print('Confidence < 0.95:')
low = syn_df[syn_df['confidence'] < 0.95]
print(f'  Count: {len(low)}')
for _, row in low.iterrows():
    print(f'  {row["synonym"]} -> {row["canonical_name"]} (conf: {row["confidence"]})')