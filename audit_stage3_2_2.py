import pandas as pd
import numpy as np

# Load Stage 2.3 frozen data
cands = pd.read_parquet('data/interim/phase3/stage2_3/ifct_match_candidates.parquet')
disamb = pd.read_parquet('data/interim/phase3/stage2_3/disambiguated_ingredients.parquet')

print('=== STAGE 2.3 FROZEN DATA - SOURCE RECONCILIATION ===')
print(f'Total candidates: {len(cands)}')
print(f'Total disambiguated: {len(disamb)}')
print(f'Unique recipes: {cands["recipe_id"].nunique()}')
print(f'Unique primary_ingredient: {cands["primary_ingredient"].nunique()}')
print(f'Unique ifct_food_code: {cands["ifct_food_code"].nunique()}')

# 1. REVIEW UNIT KEYS
print('\n=== REVIEW UNIT KEYS ===')
# Current key (primary_ingredient, ifct_food_code)
review_units_current = cands.groupby(['primary_ingredient', 'ifct_food_code']).agg(
    recipe_count=('recipe_id', 'nunique'),
    candidate_count=('recipe_id', 'count'),
    match_method=('match_method', 'first'),
    preparation_state=('preparation_state', 'first'),
    similarity=('similarity_score', 'max')
).reset_index()
print(f'Unique (primary_ingredient, ifct_food_code) pairs: {len(review_units_current)}')

# Corrected key (primary_ingredient, preparation_state, ifct_food_code)
# Use preparation_state from candidates directly (already has it)
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

# Check preparation_state values in candidates
print(f'\nPreparation state distribution in candidates:')
print(cands['preparation_state'].value_counts().to_dict())

# Check preparation_state in disambiguated
print(f'\nPreparation state in disambiguated:')
print(disamb['preparation_state'].value_counts().to_dict())

# 2. PRIORITY BAND CALCULATION
print('\n=== PRIORITY BAND CALCULATION ===')

def compute_priority_score(row):
    score = 0.0
    method_weights = {'EXACT': 40, 'SYNONYM': 30, 'TOKEN_EQUIVALENT': 20, 'TOKEN_SIMILARITY': 10, 'FUZZY': 0}
    score += method_weights.get(row.get('match_method', ''), 0)
    
    prep_weights = {'FRESH': 30, 'RAW': 30, 'NOT_SPECIFIED': 15, 'DRIED': 5, 'POWDERED': 5, 'GROUND': 5, 
                    'ROASTED': 5, 'FRIED': 5, 'BOILED': 5, 'COOKED': 5, 'SPROUTED': 5, 
                    'FERMENTED': 5, 'PICKLED': 5, 'SOAKED': 10, 'BLANCHED': 5, 'MARINATED': 5, 
                    'FRIED': 5, 'UNKNOWN': 5}
    # Handle both 'preparation_state' and 'prep_state' column names
    prep_state = row.get('preparation_state', row.get('prep_state', 'NOT_SPECIFIED'))
    score += prep_weights.get(prep_state, 0)
    
    score += min(row['recipe_count'] * 2, 20)
    score += row['similarity'] * 10
    return round(score, 2)

# Compute for current key review units
review_units_current['priority_score'] = review_units_current.apply(compute_priority_score, axis=1)
bins = [0, 19, 39, 59, 79, 100]
labels = ['Low (0-19)', 'Standard (20-39)', 'Medium (40-59)', 'High (60-79)', 'Critical (80-100)']
review_units_current['priority_band'] = pd.cut(review_units_current['priority_score'], bins=bins, labels=labels, right=True)

band_counts_current = review_units_current['priority_band'].value_counts().sort_index()
print('\nPriority band counts (current key):')
print(band_counts_current)
print(f'Sum: {band_counts_current.sum()}')

# Now for corrected key - need to compute priority scores
review_units_corrected['priority_score'] = review_units_corrected.apply(compute_priority_score, axis=1)
review_units_corrected['priority_band'] = pd.cut(review_units_corrected['priority_score'], bins=bins, labels=labels, right=True)

band_counts_corrected = review_units_corrected['priority_band'].value_counts().sort_index()
print('\nPriority band counts (corrected key):')
print(band_counts_corrected)
print(f'Sum: {band_counts_corrected.sum()}')
print(f'Total corrected review units: {len(review_units_corrected)}')

# Check the difference
print(f'\nDifference in review unit counts: {len(review_units_corrected)} - {len(review_units_current)} = {len(review_units_corrected) - len(review_units_current)}')

# 3. AUTOACCEPT VERIFICATION
print('\n=== AUTOACCEPT VERIFICATION ===')
cands_auto = cands[cands['requires_review'] == False]
print(f'Auto-accepted candidates: {len(cands[cands["requires_review"] == False])}')
print(f'Methods: {cands[cands["requires_review"] == False]["match_method"].value_counts().to_dict()}')
print(f'Prep states: {cands[cands["requires_review"] == False]["preparation_state"].value_counts().to_dict()}')

# Check all auto-accepted candidates
auto = cands[cands['requires_review'] == False]
print('\nAll auto-accepted candidates:')
for _, row in auto.iterrows():
    print(f'  recipe_id={row["recipe_id"]}: {row["primary_ingredient"]} -> {row["ifct_food_code"]} ({row["match_method"]}, {row["preparation_state"]})')

# Check unique (primary, ifct) pairs
auto_pairs = auto[['primary_ingredient', 'ifct_food_code']].drop_duplicates()
print(f'\nUnique (primary, ifct) pairs in auto: {len(auto_pairs)}')
print(auto_pairs.to_string())

# Check unique (primary, prep, ifct) in auto
auto_triples = auto[['primary_ingredient', 'preparation_state', 'ifct_food_code']].drop_duplicates()
print(f'\nUnique (primary, prep, ifct) triples in auto: {len(auto_triples)}')
print(auto_triples.to_string())

# Check auto-accepted review units with current key
auto_ru_current = review_units_current.merge(auto[['primary_ingredient', 'ifct_food_code']].drop_duplicates(), 
                              on=['primary_ingredient', 'ifct_food_code'])
print(f'\nAuto-accepted review units (current key): {len(auto_ru_current)}')

# Auto-accepted review units with corrected key
auto_ru_corrected = review_units_corrected.merge(auto[['primary_ingredient', 'ifct_food_code']].drop_duplicates(), 
                              on=['primary_ingredient', 'ifct_food_code'])
print(f'Auto-accepted review units (corrected key): {len(auto_ru_corrected)}')
print(auto_ru_corrected[['primary_ingredient', 'preparation_state', 'ifct_food_code', 'match_method', 'priority_score']].to_string())

# Check auto-accepted with corrected key - detail
print('\nAuto-accepted review units (corrected key) detail:')
for _, row in auto_ru_corrected.iterrows():
    print(f'  {row["primary_ingredient"]} | {row["preparation_state"]} -> {row["ifct_food_code"]} ({row["match_method"]}, score={row["priority_score"]})')

# 3. SAMPLING VERIFICATION
print('\n=== SAMPLING VERIFICATION ===')
# Count review units by match method (current key)
ru_method = review_units_current.groupby('match_method').size()
print(f'Review units by match method: {ru_method.to_dict()}')

# Count by priority band (current key)
ru_priority = review_units_current.groupby('priority_band').size()
print(f'Review units by priority band: {ru_priority.to_dict()}')

# For corrected key, need to compute priority bands
review_units_corrected['priority_score'] = review_units_corrected.apply(compute_priority_score, axis=1)
bins = [0, 19, 39, 59, 79, 100]
labels = ['Low (0-19)', 'Standard (20-39)', 'Medium (40-59)', 'High (60-79)', 'Critical (80-100)']
review_units_corrected['priority_band'] = pd.cut(review_units_corrected['priority_score'], bins=bins, labels=labels, right=True)

ru_priority_corrected = review_units_corrected.groupby('priority_band').size()
print(f'\nPriority band counts (corrected key):')
print(ru_priority_corrected)
print(f'Sum: {ru_priority_corrected.sum()}')

# TOKEN_SIMILARITY population
token_sim = review_units_corrected[review_units_corrected['match_method'] == 'TOKEN_SIMILARITY']
print(f'\nTOKEN_SIMILARITY review units (corrected): {len(token_sim)}')
print(f'By priority band:')
print(token_sim.groupby('priority_band').size().to_dict())

# 4. AUTOACCEPT DETAIL
print('\n=== AUTOACCEPT DETAIL ===')
auto = cands[cands['requires_review'] == False]
print(f'Auto-accepted candidates: {len(auto)}')
print(f'Unique (primary, ifct) pairs: {auto[["primary_ingredient", "ifct_food_code"]].drop_duplicates().shape[0]}')
print(f'Unique (primary, prep, ifct) triples: {auto[["primary_ingredient", "preparation_state", "ifct_food_code"]].drop_duplicates().shape[0]}')

print('\nAll auto-accepted candidates:')
for _, row in auto.iterrows():
    print(f'  recipe_id={row["recipe_id"]}: {row["primary_ingredient"]} -> {row["ifct_food_code"]} ({row["match_method"]}, {row["preparation_state"]})')

# Check if NOT_SPECIFIED auto-accepted
auto_not_spec = auto[auto['preparation_state'] == 'NOT_SPECIFIED']
print(f'\nAuto-accepted with NOT_SPECIFIED prep: {len(auto_not_spec)}')
if len(auto_not_spec) > 0:
    for _, row in auto_not_spec.iterrows():
        print(f'  {row["primary_ingredient"]} -> {row["ifct_food_code"]} ({row["match_method"]})')

# 5. SAMPLING VERIFICATION
print('\n=== SAMPLING VERIFICATION ===')
# Count review units by match method and priority band for corrected key
review_units_corrected['priority_score'] = review_units_corrected.apply(compute_priority_score, axis=1)
bins = [0, 19, 39, 59, 79, 100]
labels = ['Low (0-19)', 'Standard (20-39)', 'Medium (40-59)', 'High (60-79)', 'Critical (80-100)']
review_units_corrected['priority_band'] = pd.cut(review_units_corrected['priority_score'], bins=bins, labels=labels, right=True)

# Population by stratum for corrected key
strata_pop = {}
for method in ['EXACT', 'SYNONYM', 'TOKEN_EQUIVALENT', 'TOKEN_SIMILARITY', 'FUZZY']:
    for band in ['Critical (80-100)', 'High (60-79)', 'Medium (40-59)', 'Standard (20-39)', 'Low (0-19)']:
        count = len(review_units_corrected[(review_units_corrected['match_method'] == method) & (review_units_corrected['priority_band'] == band)])
        if count > 0:
            strata_pop[f'{method}_{band}'] = count

# TOKEN_SIMILARITY total
token_sim_total = len(review_units_corrected[review_units_corrected['match_method'] == 'TOKEN_SIMILARITY'])
print(f'\nTOKEN_SIMILARITY total population (corrected): {token_sim_total}')
print(f'10% sample: {token_sim_total * 0.1:.0f}')

# Check if 695 is correct
print(f'Previous claim: 695 samples for TOKEN_SIMILARITY')
print(f'Actual 10%: {token_sim_total * 0.1:.0f}')

# 5. WORKLOAD VERIFICATION
print('\n=== WORKLOAD VERIFICATION ===')
# Compute time per unit based on priority bands
def time_per_unit(band):
    if band == 'Critical (80-100)': return 8
    elif band == 'High (60-79)': return 10
    elif band == 'Medium (40-59)': return 12
    elif band == 'Standard (20-39)': return 15
    elif band == 'Low (0-19)': return 10
    return 10

# Current key workload
review_units_current['time_min'] = review_units_current['priority_band'].apply(time_per_unit)
total_hours_current = (review_units_current['time_min'].sum() / 60).round(1)
print(f'\nPrimary review hours (current key): {total_hours_current}')

# Corrected key workload
review_units_corrected['time_min'] = review_units_corrected['priority_band'].apply(time_per_unit)
total_hours_corrected = (review_units_corrected['time_min'].sum() / 60).round(1)
print(f'Primary review hours (corrected key): {total_hours_corrected}')

# Audit overhead
primary_hours = total_hours_corrected
audit_hours = primary_hours * 0.2  # 20% audit
adjudication_hours = 50  # from report
calibration_hours = 8 * 5  # 8 reviewers * 5 hrs
total_hours = primary_hours + primary_hours * 0.2 + 50 + 40
print(f'\nTotal workload (corrected): {total_hours:.1f} hours')

# 6. KEY VERIFICATION
print('\n=== KEY VERIFICATION ===')
# Check corrected key for duplicates
dup_check = review_units_corrected.duplicated(subset=['primary_ingredient', 'preparation_state', 'ifct_food_code']).sum()
print(f'Duplicates in corrected key: {dup_check}')

# Check null preparation_state
null_prep = review_units_corrected['preparation_state'].isna().sum()
print(f'Null preparation_state: {null_prep}')

# Check NOT_SPECIFIED handling
not_spec = (review_units_corrected['preparation_state'] == 'NOT_SPECIFIED').sum()
print(f'NOT_SPECIFIED units: {not_spec}')

# Check distinct preparation states
print(f'\nDistinct preparation states: {review_units_corrected["preparation_state"].nunique()}')
print(review_units_corrected['preparation_state'].value_counts().to_dict())

# Check if any unit has multiple preparation states for same (ingredient, IFCT)
multi_prep = review_units_corrected.groupby(['primary_ingredient', 'ifct_food_code'])['preparation_state'].nunique()
multi_prep_count = (multi_prep > 1).sum()
print(f'Ingredients with multiple prep states for same IFCT: {multi_prep_count}')

# Check if any unit has multiple preparation states for same (ingredient, IFCT)
multi_prep = review_units_corrected.groupby(['primary_ingredient', 'ifct_food_code'])['preparation_state'].nunique()
multi_prep_count = (multi_prep > 1).sum()
print(f'Ingredients with multiple prep states for same IFCT: {multi_prep_count}')

# Show examples
print('\nExamples of ingredients with multiple prep states:')
multi_prep_ingredients = multi_prep[multi_prep > 1].index.tolist()
for ing in multi_prep_ingredients[:10]:
    states = review_units_corrected[review_units_corrected['primary_ingredient'] == ing]['preparation_state'].tolist()
    print(f'  {ing}: {states}')

# 6. WORKLOAD RECALCULATION
print('\n=== WORKLOAD RECALCULATION ===')
# Time per unit by priority band
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

# Audit: 20% of primary
audit_hours = primary_hours * 0.2
print(f'Audit hours (20%): {audit_hours:.1f}')

# Adjudication: 1% of units * 30 min
adjudication_hours = len(review_units_corrected) * 0.01 * 30 / 60
print(f'Adjudication hours (1% * 30 min): {adjudication_hours:.1f}')

# Calibration: 8 reviewers * 5 hours
calibration_hours = 40
print(f'Calibration hours: {calibration_hours}')

total = primary_hours + primary_hours * 0.2 + (len(review_units_corrected) * 0.01 * 30 / 60) + 40
print(f'Total hours: {total:.1f}')

# Compare with reported
print(f'\nReported total: 2080 hours')
print(f'Actual calculated: {total:.1f} hours')

# 8. BLOCKER REGISTER CONSOLIDATION
print('\n=== BLOCKER REGISTER ===')
# We'll create this in the final report
print('See blocker register in separate file')

print('\n=== RECONCILIATION COMPLETE ===')