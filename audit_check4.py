import pandas as pd

df = pd.read_excel('datasets/Anuvaad_INDB_2024.11.xlsx', sheet_name='Sheet1')

# Analyze each source group in detail
for source in ['asc_manual', 'bfp_manual', 'open_source_recipes']:
    subset = df[df['primarysource'] == source]
    print('\n=== {} ({} records) ==='.format(source, len(subset)))
    
    # Food code prefix
    subset['prefix'] = subset['food_code'].str[:3]
    print('Prefix distribution:')
    print(subset['prefix'].value_counts())
    
    # Sample food names
    print('Sample foods:')
    for name in subset['food_name'].head(15).tolist():
        print('  {}'.format(name))
    
    # Serving unit distribution
    print('Serving units (top 10):')
    print(subset['servings_unit'].value_counts().head(10))
    
    # Missing per-serving
    serving_cols = [c for c in df.columns if c.startswith('unit_serving_')]
    missing = subset[serving_cols].isnull().all(axis=1)
    print('Missing per-serving: {} ({:.1f}%)'.format(missing.sum(), missing.sum()/len(subset)*100))

# Check if there are ANY raw food items
# Look for items that might be raw ingredients
print('\n=== Search for potential raw ingredients ===')
raw_patterns = [
    'raw ', 'dry ', 'fresh ', 'whole ', 'uncooked ',
    'flour', 'atta', 'maida', 'besan', 'rava', 'suji',
    'dal ', 'lentil', 'bean', 'pea', 'chickpea',
    'rice ', 'wheat ', 'millet', 'ragi', 'jowar', 'bajra',
    'oil ', 'ghee ', 'butter ',
    'sugar', 'jaggery', 'honey',
    'salt', 'turmeric', 'chilli', 'cumin', 'coriander', 'mustard'
]

for pattern in raw_patterns:
    matches = df[df['food_name'].str.lower().str.contains(pattern, na=False)]
    if len(matches) > 0:
        # Check if any are truly raw (not prepared dishes)
        for _, r in matches.head(3).iterrows():
            print('  {} -> {}: {}'.format(pattern, r['food_code'], r['food_name']))