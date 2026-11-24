import pandas as pd
syn_df = pd.read_csv('data/interim/phase2/ingredient_synonyms.csv')

keys = set(syn_df['synonym'].unique())
canonicals = set(syn_df['canonical_name'].unique())
overlap = keys & canonicals
print('Synonym keys that are also canonical names:')
for o in sorted(overlap):
    print('  ' + o)

print()
print('Is cumin seeds a synonym key?', 'cumin seeds' in keys)
print('Is cumin seeds a canonical name?', 'cumin seeds' in canonicals)

jeera_row = syn_df[syn_df['synonym'] == 'jeera']
if len(jeera_row) > 0:
    c = jeera_row['canonical_name'].values[0]
    conf = jeera_row['confidence'].values[0]
    print('jeera -> ' + c + ' (conf: ' + str(conf) + ')')

mapping_keys = ['pigeon pea', 'chickpea (kabuli)', 'chickpea (desi)', 'red lentil (split)', 
                'red lentil (whole)', 'sorghum', 'pearl millet', 'finger millet', 
                'foxtail millet', 'little millet', 'barnyard millet', 'kodo millet', 
                'basmati rice', 'sona masuri rice', 'rice (raw)', 'rice (cooked)', 
                'rice (parboiled)', 'wheat flour (whole)', 'wheat flour (refined)', 
                'semolina (coarse)', 'semolina (fine)']
print()
print('Canonical names in mapping:')
for c in ['cumin seeds', 'turmeric powder', 'red chili powder', 'coriander powder', 'cumin powder']:
    in_mapping = c in mapping_keys
    print('  ' + c + ': in mapping = ' + str(in_mapping))

print()
print('High-confidence synonyms that should auto-accept:')
high_conf = syn_df[syn_df['confidence'] >= 0.95]
for _, row in high_conf.iterrows():
    canon = row['canonical_name']
    if canon in mapping_keys:
        print('  ' + row['synonym'] + ' -> ' + canon + ' (conf: ' + str(row['confidence']) + ')')