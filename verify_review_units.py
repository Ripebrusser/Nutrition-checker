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

# Check review units count
review_units = cands.groupby(['primary_ingredient', 'ifct_food_code']).agg(
    recipe_count=('recipe_id', 'nunique'),
    candidate_count=('recipe_id', 'count'),
    match_method=('match_method', 'first'),
    prep_state=('preparation_state', 'first'),
    similarity=('similarity_score', 'max')
).reset_index()
print(f'Unique (primary_ingredient, ifct_food_code) pairs: {len(review_units)}')

# Check auto-accepted
auto = cands[cands['requires_review'] == False]
print(f'Auto-accepted candidates: {len(auto)}')
print(f'  Methods: {auto["match_method"].value_counts().to_dict()}')
print(f'  Prep states: {auto["preparation_state"].value_counts().to_dict()}')

# Check auto-accepted review units
auto_ru = review_units.merge(auto[['primary_ingredient', 'ifct_food_code']].drop_duplicates(), 
                              on=['primary_ingredient', 'ifct_food_code'])
print(f'Auto-accepted review units: {len(auto_ru)}')
print(auto_ru[['primary_ingredient', 'ifct_food_code', 'match_method', 'prep_state']].to_string())

# Check auto-accepted candidates details
auto_detail = auto[['primary_ingredient', 'ifct_food_code', 'match_method', 'preparation_state', 'similarity_score', 'recipe_id']].drop_duplicates()
print(f'\nAuto-accepted candidates ({len(auto)}):')
print(auto_detail.to_string())

# Check review units by match method
ru_method = review_units.groupby('match_method').size()
print(f'\nReview units by method: {ru_method.to_dict()}')

# Check by prep state
ru_prep = review_units.groupby('prep_state').size()
print(f'Review units by prep: {ru_prep.to_dict()}')

# Check multi-code ambiguity
multi = review_units.groupby('primary_ingredient')['ifct_food_code'].nunique()
multi_count = (multi > 1).sum()
print(f'\nPrimary ingredients with multiple IFCT codes: {multi_count}')

# Check how many unique primary ingredients
print(f'Unique primary ingredients: {review_units["primary_ingredient"].nunique()}')

# Now compute priority scores for all review units
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

review_units['priority_score'] = review_units.apply(compute_priority_score, axis=1)

# Check priority bands
bins = [0, 19, 39, 59, 79, 100]
labels = ['Low (0-19)', 'Standard (20-39)', 'Medium (40-59)', 'High (60-79)', 'Critical (80-100)']
review_units['priority_band'] = pd.cut(review_units['priority_score'], bins=bins, labels=labels, right=True)

band_counts = review_units['priority_band'].value_counts().sort_index()
print('\nPriority band counts:')
print(band_counts)

# By match method and priority band
print('\nBy match method and priority band:')
cross = pd.crosstab(review_units['match_method'], review_units['priority_band'], margins=True)
print(cross)

# Check specific numbers from priority report
print('\n=== COMPARISON WITH PRIORITY REPORT ===')
print(f'Critical (80-100): {len(review_units[review_units["priority_score"] >= 80])} (report: 46)')
print(f'High (60-79): {len(review_units[(review_units["priority_score"] >= 60) & (review_units["priority_score"] < 80)])} (report: 237)')
print(f'Medium (40-59): {len(review_units[(review_units["priority_score"] >= 40) & (review_units["priority_score"] < 60)])} (report: 1,284)')
print(f'Standard (20-39): {len(review_units[(review_units["priority_score"] >= 20) & (review_units["priority_score"] < 40)])} (report: 2,898)')
print(f'Low (0-19): {len(review_units[review_units["priority_score"] < 20])} (report: 2,700)')

# Check auto-accepted
auto = cands[cands['requires_review'] == False]
print(f'\nAuto-accepted candidates: {len(auto)}')
print(f'Auto-accepted review units: {len(auto_ru)}')

# Check auto-accepted details
auto_ru = review_units.merge(auto[['primary_ingredient', 'ifct_food_code']].drop_duplicates(), 
                              on=['primary_ingredient', 'ifct_food_code'])
print(f'\nAuto-accepted review units: {len(auto_ru)}')
for _, row in auto_ru.iterrows():
    print(f'  {row["primary_ingredient"]} -> {row["ifct_food_code"]} ({row["match_method"]}, {row["prep_state"]})')

# Check critical band items
critical = review_units[review_units['priority_score'] >= 80]
print(f'\nCritical items ({len(critical)}):')
for _, row in critical.iterrows():
    print(f'  {row["primary_ingredient"]} -> {row["ifct_food_code"]} ({row["match_method"]}, {row["prep_state"]}, recipes={row["recipe_count"]}, sim={row["similarity"]}, score={row["priority_score"]})')

# Check high items
high = review_units[(review_units['priority_score'] >= 60) & (review_units['priority_score'] < 80)]
print(f'\nHigh items ({len(high)}):')
for _, row in high.iterrows():
    print(f'  {row["primary_ingredient"]} -> {row["ifct_food_code"]} ({row["match_method"]}, {row["prep_state"]}, recipes={row["recipe_count"]}, sim={row["similarity"]}, score={row["priority_score"]})')

# Check multi-code ambiguity more carefully
multi = review_units.groupby('primary_ingredient')['ifct_food_code'].nunique()
multi_ingredients = multi[multi > 1].index.tolist()
print(f'\nMulti-code ingredients: {len(multi_ingredients)}')

# Check how many of the multi-code ingredients are in each priority band
for band in ['Critical (80-100)', 'High (60-79)', 'Medium (40-59)', 'Standard (20-39)', 'Low (0-19)']:
    band_ru = review_units[review_units['priority_band'] == band]
    multi_in_band = band_ru[band_ru['primary_ingredient'].isin(multi_ingredients)]
    print(f'{band}: {len(multi_in_band)} multi-code ingredients, {len(band_ru)} total units')

# Check auto-accepted - are they in the review units?
print('\n=== AUTO-ACCEPTED VERIFICATION ===')
print(f'Auto-accepted candidates: {len(auto)}')
auto_unique = auto[['primary_ingredient', 'ifct_food_code', 'match_method', 'preparation_state']].drop_duplicates()
print(f'Unique auto-accepted pairs: {len(auto_unique)}')
print(auto_unique.to_string())

# Check if the 4 auto-accepted candidates map to 3 or 4 review units
auto_ru = review_units.merge(auto[['primary_ingredient', 'ifct_food_code']].drop_duplicates(), 
                              on=['primary_ingredient', 'ifct_food_code'])
print(f'Auto-accepted review units: {len(auto_ru)}')
print(auto_ru[['primary_ingredient', 'ifct_food_code', 'match_method', 'prep_state', 'priority_score']].to_string())

# Check the 4th auto-accepted candidate
print('\nAll 4 auto-accepted candidates:')
for _, row in auto.iterrows():
    print(f'  recipe_id={row["recipe_id"]}: {row["primary_ingredient"]} -> {row["ifct_food_code"]} ({row["match_method"]}, {row["preparation_state"]})')

# Check how many unique (primary, ifct) pairs in auto
auto_pairs = auto[['primary_ingredient', 'ifct_food_code']].drop_duplicates()
print(f'\nUnique (primary, ifct) pairs in auto: {len(auto_pairs)}')
print(auto_pairs.to_string())