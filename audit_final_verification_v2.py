import pandas as pd
import numpy as np
import hashlib

# Load Stage 2.3 frozen data
cands = pd.read_parquet('data/interim/phase3/stage2_3/ifct_match_candidates.parquet')
disamb = pd.read_parquet('data/interim/phase3/stage2_3/disambiguated_ingredients.parquet')

print('=== STAGE 2.3 FROZEN DATA - AUTHORITATIVE COUNTS ===')
print(f'Total candidates: {len(cands)}')
print(f'Total disambiguated: {len(disamb)}')
print(f'Unique recipes: {cands["recipe_id"].nunique()}')
print(f'Unique primary_ingredient: {cands["primary_ingredient"].nunique()}')
print(f'Unique ifct_food_code: {cands["ifct_food_code"].nunique()}')

# Review unit keys
# Current key (primary_ingredient, ifct_food_code)
review_units_current = cands.groupby(['primary_ingredient', 'ifct_food_code']).agg(
    recipe_count=('recipe_id', 'nunique'),
    candidate_count=('recipe_id', 'count'),
    match_method=('match_method', 'first'),
    preparation_state=('preparation_state', 'first'),
    similarity=('similarity_score', 'max')
).reset_index()
print(f'\nUnique (primary_ingredient, ifct_food_code) pairs: {len(review_units_current)}')

# Corrected key (primary_ingredient, preparation_state, ifct_food_code)
review_units_corrected = cands.groupby(['primary_ingredient', 'preparation_state', 'ifct_food_code']).agg(
    recipe_count=('recipe_id', 'nunique'),
    candidate_count=('recipe_id', 'count'),
    match_method=('match_method', 'first'),
    similarity=('similarity_score', 'max')
).reset_index()
print(f'Unique (primary_ingredient, preparation_state, ifct_food_code) triples: {len(review_units_corrected)}')

# Check for duplicates in corrected key
dup_check = review_units_corrected.duplicated(subset=['primary_ingredient', 'preparation_state', 'ifct_food_code']).sum()
print(f'Duplicates in corrected key: {dup_check}')

# Preparation state distribution
print(f'\nPreparation state distribution in candidates:')
print(cands['preparation_state'].value_counts().to_dict())

# 1. PRIORITY BAND CALCULATION FOR CORRECTED KEY
def compute_priority_score(row):
    score = 0.0
    method_weights = {'EXACT': 40, 'SYNONYM': 30, 'TOKEN_EQUIVALENT': 20, 'TOKEN_SIMILARITY': 10, 'FUZZY': 0}
    score += method_weights.get(row.get('match_method', ''), 0)
    
    prep_weights = {'FRESH': 30, 'RAW': 30, 'NOT_SPECIFIED': 15, 'DRIED': 5, 'POWDERED': 5, 'GROUND': 5, 
                    'ROASTED': 5, 'FRIED': 5, 'BOILED': 5, 'COOKED': 5, 'SPROUTED': 5, 
                    'FERMENTED': 5, 'PICKLED': 5, 'SOAKED': 10, 'BLANCHED': 5, 'MARINATED': 5, 
                    'FRIED': 5, 'UNKNOWN': 5}
    prep_state = row.get('preparation_state', row.get('prep_state', 'NOT_SPECIFIED'))
    score += prep_weights.get(prep_state, 0)
    
    score += min(row['recipe_count'] * 2, 20)
    score += row['similarity'] * 10
    return round(score, 2)

# Compute priority scores for corrected review units
review_units_corrected['priority_score'] = review_units_corrected.apply(compute_priority_score, axis=1)
bins = [0, 19, 39, 59, 79, 100]
labels = ['Low (0-19)', 'Standard (20-39)', 'Medium (40-59)', 'High (60-79)', 'Critical (80-100)']
review_units_corrected['priority_band'] = pd.cut(review_units_corrected['priority_score'], bins=bins, labels=labels, right=True)

band_counts_corrected = review_units_corrected['priority_band'].value_counts().sort_index()
print('\n=== AUTHORITATIVE PRIORITY BANDS (CORRECTED KEY) ===')
print(band_counts_corrected)
print(f'Sum: {band_counts_corrected.sum()}')
print(f'Total corrected review units: {len(review_units_corrected)}')

# Also compute for current key for comparison
review_units_current = cands.groupby(['primary_ingredient', 'ifct_food_code']).agg(
    recipe_count=('recipe_id', 'nunique'),
    candidate_count=('recipe_id', 'count'),
    match_method=('match_method', 'first'),
    preparation_state=('preparation_state', 'first'),
    similarity=('similarity_score', 'max')
).reset_index()

review_units_current['priority_score'] = review_units_current.apply(compute_priority_score, axis=1)
bins = [0, 19, 39, 59, 79, 100]
labels = ['Low (0-19)', 'Standard (20-39)', 'Medium (40-59)', 'High (60-79)', 'Critical (80-100)']
review_units_current['priority_band'] = pd.cut(review_units_current['priority_score'], bins=bins, labels=labels, right=True)

band_counts_current = review_units_current['priority_band'].value_counts().sort_index()
print('\n=== PRIORITY BANDS (CURRENT KEY - 7,165 units) ===')
print(band_counts_current)
print(f'Sum: {band_counts_current.sum()}')

# 2. AUTOACCEPT VERIFICATION
print('\n=== AUTOACCEPT VERIFICATION ===')
auto = cands[cands['requires_review'] == False]
print(f'Auto-accepted candidates: {len(auto)}')
print(f'Methods: {auto["match_method"].value_counts().to_dict()}')
print(f'Prep states: {auto["preparation_state"].value_counts().to_dict()}')

print('\nAll auto-accepted candidates:')
for _, row in auto.iterrows():
    print(f'  recipe_id={row["recipe_id"]}: {row["primary_ingredient"]} -> {row["ifct_food_code"]} ({row["match_method"]}, {row["preparation_state"]})')

auto_pairs = auto[['primary_ingredient', 'ifct_food_code']].drop_duplicates()
print(f'\nUnique (primary, ifct) pairs in auto: {len(auto_pairs)}')

auto_triples = auto[['primary_ingredient', 'preparation_state', 'ifct_food_code']].drop_duplicates()
print(f'Unique (primary, prep, ifct) triples in auto: {len(auto_triples)}')

# Auto-accepted review units (current key)
auto_ru_current = cands[cands['requires_review'] == False].groupby(['primary_ingredient', 'ifct_food_code']).size().reset_index(name='count')
print(f'\nAuto-accepted review units (current key): {len(auto_ru_current)}')

# Auto-accepted review units (corrected key)
auto_ru_corrected = cands[cands['requires_review'] == False].groupby(['primary_ingredient', 'preparation_state', 'ifct_food_code']).size().reset_index(name='count')
print(f'Auto-accepted review units (corrected key): {len(auto_ru_corrected)}')

# Check auto-accepted with corrected key - detail
auto_ru_corrected_detail = cands[cands['requires_review'] == False].groupby(['primary_ingredient', 'preparation_state', 'ifct_food_code']).agg(
    match_method=('match_method', 'first'),
    similarity_score=('similarity_score', 'max'),
    recipe_ids=('recipe_id', lambda x: list(x.unique()))
).reset_index()
print('\nAuto-accepted review units (corrected key) detail:')
for _, row in auto_ru_corrected_detail.iterrows():
    print(f'  {row["primary_ingredient"]} | {row["preparation_state"]} -> {row["ifct_food_code"]} ({row["match_method"]})')

# Check auto-accepted with NOT_SPECIFIED prep
auto_not_spec = auto[auto['preparation_state'] == 'NOT_SPECIFIED']
print(f'\nAuto-accepted with NOT_SPECIFIED prep: {len(auto_not_spec)}')

# 3. SAMPLING VERIFICATION
print('\n=== SAMPLING VERIFICATION ===')
# Count review units by match method (corrected key)
ru_method_corrected = cands.groupby(['primary_ingredient', 'preparation_state', 'ifct_food_code', 'match_method']).size().reset_index(name='count')
ru_method_counts = ru_method_corrected.groupby('match_method').size()
print(f'Review units by match method (corrected): {ru_method_counts.to_dict()}')

# Count by priority band (corrected key)
review_units_corrected['priority_score'] = review_units_corrected.apply(compute_priority_score, axis=1)
bins = [0, 19, 39, 59, 79, 100]
labels = ['Low (0-19)', 'Standard (20-39)', 'Medium (40-59)', 'High (60-79)', 'Critical (80-100)']
review_units_corrected['priority_band'] = pd.cut(review_units_corrected['priority_score'], bins=bins, labels=labels, right=True)

ru_priority_corrected = review_units_corrected.groupby('priority_band').size()
print(f'\nReview units by priority band (corrected): {ru_priority_corrected.to_dict()}')

# TOKEN_SIMILARITY population
token_sim_corrected = review_units_corrected[review_units_corrected['match_method'] == 'TOKEN_SIMILARITY']
token_sim_corrected_count = len(token_sim_corrected)
print(f'\nTOKEN_SIMILARITY population (corrected): {token_sim_corrected_count}')
print(f'10% sample: {token_sim_corrected_count * 0.1:.0f}')

# 4. WORKLOAD VERIFICATION
print('\n=== WORKLOAD VERIFICATION ===')
def time_per_unit(band):
    if band == 'Critical (80-100)': return 8
    elif band == 'High (60-79)': return 10
    elif band == 'Medium (40-59)': return 12
    elif band == 'Standard (20-39)': return 15
    elif band == 'Low (0-19)': return 10
    return 10

# Count review units by priority band (corrected key)
band_counts = review_units_corrected['priority_band'].value_counts().sort_index()
print('\nPriority band counts (corrected):')
print(band_counts)

# Time per unit
time_map = {
    'Critical (80-100)': 8,
    'High (60-79)': 10,
    'Medium (40-59)': 12,
    'Standard (20-39)': 15,
    'Low (0-19)': 10
}

review_units_corrected['time_min'] = review_units_corrected['priority_band'].map(time_map)
primary_minutes = review_units_corrected['time_min'].sum()
primary_hours = review_units_corrected['time_min'].sum() / 60
print(f'\nPrimary review minutes: {primary_minutes}')
print(f'Primary review hours: {primary_hours:.1f}')

# Audit overhead
audit_hours = primary_hours * 0.2
print(f'Audit hours (20%): {audit_hours:.1f}')

# Adjudication
adjudication_hours = len(review_units_corrected) * 0.01 * 30 / 60
print(f'Adjudication hours (1% * 30 min): {adjudication_hours:.1f}')

# Calibration
calibration_hours = 8 * 5
print(f'Calibration hours: {calibration_hours}')

total_hours = primary_hours + primary_hours * 0.2 + (len(review_units_corrected) * 0.01 * 30 / 60) + 40
print(f'Total hours: {total_hours:.1f}')

# 4. KEY VERIFICATION
print('\n=== KEY VERIFICATION ===')
dup_check = review_units_corrected.duplicated(subset=['primary_ingredient', 'preparation_state', 'ifct_food_code']).sum()
print(f'Duplicates in corrected key: {dup_check}')

null_prep = cands['preparation_state'].isna().sum()
print(f'Null preparation_state in candidates: {null_prep}')

not_spec = (cands['preparation_state'] == 'NOT_SPECIFIED').sum()
print(f'NOT_SPECIFIED units in candidates: {not_spec}')

# Distinct preparation states
print(f'\nDistinct preparation states: {cands["preparation_state"].nunique()}')
print(cands['preparation_state'].value_counts().to_dict())

# Check multi-prep ingredients
multi_prep = cands.groupby(['primary_ingredient', 'ifct_food_code'])['preparation_state'].nunique()
multi_prep_count = (multi_prep > 1).sum()
print(f'Ingredients with multiple prep states for same IFCT: {multi_prep_count}')

# Show examples
print('\nExamples of ingredients with multiple prep states:')
multi_prep_ingredients = multi_prep[multi_prep > 1].index.tolist()
for ing in multi_prep_ingredients[:10]:
    # ing is a tuple (primary_ingredient, ifct_food_code)
    ingredient_name = ing[0]
    states = cands.loc[cands['primary_ingredient'] == ingredient_name, 'preparation_state'].unique()
    print(f'  {ingredient_name}: {list(states)}')

# 5. WORKLOAD RECALCULATION
print('\n=== WORKLOAD RECALCULATION ===')
# Time per unit by priority band
time_map = {
    'Critical (80-100)': 8,
    'High (60-79)': 10,
    'Medium (40-59)': 12,
    'Standard (20-39)': 15,
    'Low (0-19)': 10
}

# Count review units by priority band (corrected key)
band_counts = review_units_corrected['priority_band'].value_counts().sort_index()
print('\nPriority band counts (corrected):')
print(band_counts)

# Time per unit
time_map = {
    'Critical (80-100)': 8,
    'High (60-79)': 10,
    'Medium (40-59)': 12,
    'Standard (20-39)': 15,
    'Low (0-19)': 10
}

review_units_corrected['time_min'] = review_units_corrected['priority_band'].map(time_map)
primary_minutes = review_units_corrected['time_min'].sum()
primary_hours = review_units_corrected['time_min'].sum() / 60
print(f'Primary review minutes: {primary_minutes}')
print(f'Primary review hours: {primary_hours:.1f}')

# Audit overhead
audit_hours = primary_hours * 0.2
print(f'Audit hours (20%): {audit_hours:.1f}')

# Adjudication
adjudication_hours = len(review_units_corrected) * 0.01 * 30 / 60
print(f'Adjudication hours (1% * 30 min): {adjudication_hours:.1f}')

# Calibration
calibration_hours = 40
print(f'Calibration hours: {calibration_hours}')

total_hours = primary_hours + primary_hours * 0.2 + len(review_units_corrected) * 0.01 * 30 / 60 + 40
print(f'Total hours: {total_hours:.1f}')

# 8. BLOCKER REGISTER CONSOLIDATION
print('\n=== BLOCKER REGISTER ===')
# We'll create this in the final report
print('See blocker register in separate file')

print('\n=== RECONCILIATION COMPLETE ===')