import pandas as pd
import numpy as np

# Load Stage 2.3 data
cands = pd.read_parquet('data/interim/phase3/stage2_3/ifct_match_candidates.parquet')
disamb = pd.read_parquet('data/interim/phase3/stage2_3/disambiguated_ingredients.parquet')

print('=== STAGE 2.3 DATA VERIFICATION ===')
print(f'Total candidates: {len(cands)}')
print(f'Total disambiguated: {len(disamb)}')
print(f'Unique recipes: {cands["recipe_id"].nunique()}')
print(f'Unique primary_ingredient: {cands["primary_ingredient"].nunique()}')
print(f'Unique ifct_food_code: {cands["ifct_food_code"].nunique()}')

# Check review units count with different keys
# Current key (primary_ingredient, ifct_food_code)
review_units_current = cands.groupby(['primary_ingredient', 'ifct_food_code']).agg(
    recipe_count=('recipe_id', 'nunique'),
    candidate_count=('recipe_id', 'count'),
    match_method=('match_method', 'first'),
    prep_state=('preparation_state', 'first'),
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

# Check auto-accepted
auto = cands[cands['requires_review'] == False]
print(f'\nAuto-accepted candidates: {len(auto)}')
print(f'  Methods: {auto["match_method"].value_counts().to_dict()}')
print(f'  Prep states: {auto["preparation_state"].value_counts().to_dict()}')

# Check auto-accepted review units (current key)
auto_ru_current = review_units_current.merge(auto[['primary_ingredient', 'ifct_food_code']].drop_duplicates(), 
                              on=['primary_ingredient', 'ifct_food_code'])
print(f'\nAuto-accepted review units (current key): {len(auto_ru_current)}')

# Check auto-accepted review units (corrected key)
auto_ru_corrected = review_units_corrected.merge(auto[['primary_ingredient', 'ifct_food_code']].drop_duplicates(), 
                              on=['primary_ingredient', 'ifct_food_code'])
print(f'Auto-accepted review units (corrected key): {len(auto_ru_corrected)}')

# Check auto-accepted candidates details
auto_detail = auto[['primary_ingredient', 'ifct_food_code', 'match_method', 'preparation_state', 'similarity_score', 'recipe_id']].drop_duplicates()
print(f'\nAuto-accepted unique pairs: {len(auto[["primary_ingredient", "ifct_food_code"]].drop_duplicates())}')
print(auto_detail.to_string())

# Check review units by match method
ru_method = review_units_current.groupby('match_method').size()
print(f'\nReview units by method: {ru_method.to_dict()}')

# Check by prep state
ru_prep = review_units_current.groupby('prep_state').size()
print(f'Review units by prep: {ru_prep.to_dict()}')

# Check multi-code ambiguity
multi = review_units_current.groupby('primary_ingredient')['ifct_food_code'].nunique()
multi_count = (multi > 1).sum()
print(f'\nPrimary ingredients with multiple IFCT codes: {multi_count}')

# Check how many unique primary ingredients
print(f'Unique primary ingredients: {review_units_current["primary_ingredient"].nunique()}')

# Now compute priority scores for all review units (current key)
def compute_priority_score(row):
    score = 0.0
    method_weights = {'EXACT': 40, 'SYNONYM': 30, 'TOKEN_EQUIVALENT': 20, 'TOKEN_SIMILARITY': 10, 'FUZZY': 0}
    score += method_weights.get(row['match_method'], 0)
    
    prep_weights = {'FRESH': 30, 'RAW': 30, 'NOT_SPECIFIED': 15, 'DRIED': 5, 'POWDERED': 5, 'GROUND': 5, 
                    'ROASTED': 5, 'FRIED': 5, 'BOILED': 5, 'COOKED': 5, 'SPROUTED': 5, 
                    'FERMENTED': 5, 'PICKLED': 5, 'SOAKED': 10, 'BLANCHED': 5, 'MARINATED': 5, 
                    'FRIED': 5, 'UNKNOWN': 5}
    score += prep_weights.get(row['prep_state'], 0)
    
    score += min(row['recipe_count'] * 2, 20)
    score += row['similarity'] * 10
    return round(score, 2)

review_units_current['priority_score'] = review_units_current.apply(compute_priority_score, axis=1)

# Check priority bands
bins = [0, 19, 39, 59, 79, 100]
labels = ['Low (0-19)', 'Standard (20-39)', 'Medium (40-59)', 'High (60-79)', 'Critical (80-100)']
review_units_current['priority_band'] = pd.cut(review_units_current['priority_score'], bins=bins, labels=labels, right=True)

band_counts = review_units_current['priority_band'].value_counts().sort_index()
print('\nPriority band counts (current key):')
print(band_counts)

# By match method and priority band
print('\nBy match method and priority band:')
cross = pd.crosstab(review_units_current['match_method'], review_units_current['priority_band'], margins=True)
print(cross)

# Check specific numbers from priority report
print('\n=== COMPARISON WITH PRIORITY REPORT ===')
print(f'Critical (80-100): {len(review_units_current[review_units_current["priority_score"] >= 80])} (report: 46)')
print(f'High (60-79): {len(review_units_current[(review_units_current["priority_score"] >= 60) & (review_units_current["priority_score"] < 80)])} (report: 237)')
print(f'Medium (40-59): {len(review_units_current[(review_units_current["priority_score"] >= 40) & (review_units_current["priority_score"] < 60)])} (report: 1,284)')
print(f'Standard (20-39): {len(review_units_current[(review_units_current["priority_score"] >= 20) & (review_units_current["priority_score"] < 40)])} (report: 2,898)')
print(f'Low (0-19): {len(review_units_current[review_units_current["priority_score"] < 20])} (report: 2,700)')

# Check auto-accepted
auto = cands[cands['requires_review'] == False]
print(f'\nAuto-accepted candidates: {len(auto)}')
print(f'Auto-accepted review units (current key): {len(auto_ru_current)}')

# Check RAW EXACT candidates
raw_exact = cands[(cands['match_method'] == 'EXACT') & (cands['preparation_state'] == 'RAW')]
print(f'\nRAW EXACT candidates: {len(raw_exact)}')

# Check FRESH EXACT candidates
fresh_exact = cands[(cands['match_method'] == 'EXACT') & (cands['preparation_state'] == 'FRESH')]
print(f'FRESH EXACT candidates: {len(fresh_exact)}')

# Check FRESH EXACT review units
fresh_exact_ru = review_units_current[(review_units_current['match_method'] == 'EXACT') & (review_units_current['preparation_state'] == 'FRESH')]
print(f'FRESH EXACT review units: {len(fresh_exact_ru)}')

# Check RAW EXACT review units
raw_exact_ru = review_units_current[(review_units_current['match_method'] == 'EXACT') & (review_units_current['preparation_state'] == 'RAW')]
print(f'RAW EXACT review units: {len(raw_exact_ru)}')

# Check FRESH EXACT auto-accepted
fresh_exact_auto = cands[(cands['match_method'] == 'EXACT') & (cands['preparation_state'] == 'FRESH') & (cands['requires_review'] == False)]
print(f'FRESH EXACT auto-accepted: {len(fresh_exact_auto)}')

# Check all auto-accepted
print('\nAll auto-accepted candidates:')
for _, row in auto.iterrows():
    print(f'  recipe_id={row["recipe_id"]}: {row["primary_ingredient"]} -> {row["ifct_food_code"]} ({row["match_method"]}, {row["preparation_state"]})')