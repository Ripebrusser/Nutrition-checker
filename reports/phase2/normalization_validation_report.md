# Stage 1 - Ingredient Normalization Validation Report

**Date:** 2026-11-16T20:09:22.787376
**Input:** 6,865 recipes from `data/processed/recipes.parquet`
**Output:** `data/interim/phase2/normalized_ingredients.parquet`
**Synonym Dictionary:** `data/interim/phase2/ingredient_synonyms.csv`

## Summary Statistics

| Metric | Value |
|--------|-------|
| Total recipes processed | 6865 |
| Total ingredient lines (raw + en) | 168602 |
| Unique original expressions | 27288 |
| Unique normalized expressions | 26210 |
| Synonym mappings applied | 74929 |
| Unique synonyms applied | 144 |
| Expressions without synonym match | 16773 |
| Expressions with distinction flags | 0 |
| Synonym dictionary size | 264 |

## Transformation Counts

| Transformation | Count |
|----------------|-------|
| lowercase | 168602 |
| whitespace_normalize | 168602 |
| punctuation_normalize | 168602 |
| synonym_multiword:sunflower oil->sunflower oil | 4962 |
| synonym_word:garlic->garlic | 4888 |
| synonym_multiword:turmeric powder->turmeric powder | 4214 |
| synonym_word:onion->onion (bulb) | 3850 |
| unicode_nfc | 3784 |
| synonym_word:ginger->ginger | 3249 |
| synonym_multiword:cumin seeds->cumin seeds | 2880 |
| synonym_word:sugar->sugar (white) | 2838 |
| synonym_multiword:curry leaves->curry leaves | 2382 |
| synonym_word:lemon->lemon | 2269 |
| synonym_multiword:mustard seeds->mustard seeds | 2217 |
| synonym_word:milk->milk (cow) | 2045 |
| synonym_word:ghee->ghee | 1983 |
| synonym_word:tomato->tomato | 1887 |
| synonym_word:asafoetida->asafoetida | 1880 |
| synonym_multiword:black pepper->black pepper | 1812 |
| synonym_word:butter->butter | 1737 |
| synonym_multiword:coriander powder->coriander powder | 1638 |
| synonym_word:curd->curd | 1497 |
| synonym_multiword:cumin powder->cumin powder | 1435 |
| synonym_multiword:fresh coconut->fresh coconut kernel | 1396 |
| synonym_multiword:urad dal->black gram (split) | 1074 |
| synonym_multiword:cinnamon stick->cinnamon (stick) | 1068 |
| synonym_word:corn->corn (fresh) | 936 |
| synonym_word:jaggery->jaggery | 920 |
| synonym_word:cream->cream | 896 |
| synonym_multiword:tej patta->bay leaf | 860 |
| synonym_word:mango->mango (ripe) | 814 |
| synonym_multiword:mint leaves->mint leaves | 772 |
| synonym_word:carrot->carrot | 733 |
| synonym_word:cashew->cashew | 711 |
| synonym_multiword:fennel seeds->fennel seeds | 685 |
| synonym_word:honey->honey | 638 |
| synonym_multiword:fenugreek seeds->fenugreek seeds | 622 |
| synonym_multiword:chana dal->bengal gram (split) | 622 |
| synonym_multiword:green peas->green peas (fresh) | 543 |
| synonym_multiword:mustard oil->mustard oil | 516 |
| synonym_word:paneer->paneer | 506 |
| synonym_word:badam->almond | 488 |
| synonym_multiword:carom seeds->carom seeds | 482 |
| synonym_multiword:moong dal->green gram (split) | 422 |
| synonym_word:potato->potato | 403 |
| synonym_multiword:cinnamon powder->cinnamon powder | 402 |
| synonym_multiword:coconut oil->coconut oil | 377 |
| synonym_multiword:arhar dal->pigeon pea | 358 |
| synonym_word:cabbage->cabbage | 335 |
| synonym_multiword:brown sugar->brown sugar | 303 |
| synonym_word:sooji->semolina (fine) | 302 |
| synonym_word:cucumber->cucumber | 300 |
| synonym_multiword:poppy seeds->poppy seeds | 293 |
| synonym_word:orange->orange | 285 |
| synonym_word:brinjal->eggplant | 278 |
| synonym_multiword:dried fenugreek leaves->kasuri methi | 274 |
| synonym_multiword:spring onion greens->onion (spring) | 264 |
| synonym_word:cauliflower->cauliflower | 258 |
| synonym_multiword:spring onion->onion (spring) | 242 |
| synonym_word:nutmeg->nutmeg | 229 |
| synonym_multiword:fenugreek leaves->fenugreek leaves | 208 |
| synonym_multiword:black cardamom->cardamom (black) | 206 |
| synonym_multiword:kabuli chana->chickpea (kabuli) | 172 |
| synonym_word:apple->apple | 172 |
| synonym_word:kaddu->pumpkin | 166 |
| synonym_word:beetroot->beetroot | 159 |
| synonym_multiword:nigella seeds->nigella seeds | 146 |
| synonym_multiword:masoor dal->red lentil (split) | 142 |
| synonym_word:ragi->finger millet | 139 |
| synonym_word:almond->almond | 131 |
| synonym_word:maida->wheat flour (refined) | 124 |
| synonym_multiword:bottle gourd->bottle gourd | 120 |
| synonym_word:bhindi->okra | 116 |
| synonym_word:mace->mace | 112 |
| synonym_word:pomegranate->pomegranate | 112 |
| synonym_multiword:kala chana->chickpea (desi) | 112 |
| synonym_word:buttermilk->buttermilk | 110 |
| synonym_multiword:moong sprouts->green gram (sprouted) | 104 |
| synonym_multiword:raw banana->banana (raw/plantain) | 104 |
| synonym_multiword:red chili powder->red chili powder | 89 |
| synonym_word:jowar->sorghum | 89 |
| synonym_word:bajra->pearl millet | 86 |
| synonym_word:khoya->khoya | 80 |
| synonym_word:yam->yam | 79 |
| synonym_word:banana->banana (ripe) | 79 |
| synonym_word:quinoa->quinoa | 76 |
| synonym_multiword:sweet potato->sweet potato | 73 |
| synonym_word:papaya->papaya (ripe) | 70 |
| synonym_multiword:green chili->green chili | 68 |
| synonym_word:jackfruit->jackfruit (ripe) | 65 |
| synonym_word:capsicum->capsicum (bell pepper) | 58 |
| synonym_multiword:ridge gourd->ridge gourd | 56 |
| synonym_word:watermelon->watermelon | 56 |
| synonym_multiword:gingelly oil->gingelly oil | 54 |
| synonym_multiword:coriander seeds->coriander seeds | 53 |
| synonym_word:pumpkin->pumpkin | 53 |
| synonym_word:atta->wheat flour (whole) | 52 |
| synonym_multiword:white pepper->white pepper | 50 |
| synonym_word:yogurt->yogurt | 48 |
| synonym_multiword:bay leaf->bay leaf | 47 |
| synonym_multiword:sesame oil->sesame oil | 39 |
| synonym_multiword:coriander leaves->coriander leaves | 39 |
| synonym_multiword:black sesame seeds->sesame seeds (black) | 35 |
| fraction_1_2 | 34 |
| synonym_word:lime->lime | 33 |
| synonym_word:rava->semolina (fine) | 31 |
| synonym_word:radish->radish | 31 |
| synonym_word:chana->bengal gram (whole) | 28 |
| synonym_multiword:red chili->red chili (fresh) | 25 |
| synonym_word:guava->guava | 24 |
| synonym_word:rajgira->amaranth leaves | 23 |
| synonym_multiword:coconut water->coconut water | 22 |
| synonym_word:jeera->cumin seeds | 22 |
| synonym_word:chenna->chenna | 18 |
| synonym_word:date->date | 18 |
| synonym_multiword:badi elaichi->cardamom (black) | 16 |
| synonym_multiword:peanut oil->peanut oil | 16 |
| synonym_word:clove->clove | 16 |
| synonym_word:mooli->radish | 16 |
| synonym_multiword:raw mango->mango (raw) | 15 |
| fraction_1_4 | 14 |
| synonym_multiword:kasuri methi->kasuri methi | 13 |
| synonym_word:aloo->potato | 12 |
| synonym_multiword:hari mirch->green chili | 12 |
| synonym_word:suran->elephant foot yam | 11 |
| synonym_word:okra->okra | 11 |
| synonym_word:kalonji->nigella seeds | 11 |
| synonym_multiword:tur dal->pigeon pea | 10 |
| synonym_word:gur->jaggery | 8 |
| synonym_multiword:toor dal->pigeon pea | 6 |
| synonym_word:pistachio->pistachio | 6 |
| synonym_multiword:groundnut oil->groundnut oil | 6 |
| synonym_multiword:khus khus->poppy seeds | 5 |
| synonym_multiword:ash gourd->ash gourd | 5 |
| synonym_word:moong->green gram (whole) | 4 |
| synonym_word:peanut->peanut (raw) | 4 |
| synonym_multiword:fresh turmeric->turmeric (fresh) | 4 |
| synonym_word:pudina->mint leaves | 4 |
| synonym_word:elaichi->cardamom (green) | 3 |
| synonym_word:cilantro->coriander leaves | 3 |
| fraction_1_3 | 2 |
| synonym_multiword:green cardamom->cardamom (green) | 2 |
| synonym_multiword:white sesame seeds->sesame seeds (white) | 2 |
| fraction_3_4 | 2 |
| synonym_word:pista->pistachio | 2 |
| synonym_word:mawa->khoya | 2 |
| synonym_word:urad->black gram (whole) | 2 |
| synonym_word:chawal->rice (raw) | 2 |
| synonym_word:fig->fig (dried) | 2 |
| synonym_multiword:jeera powder->cumin powder | 2 |
| synonym_multiword:kashmiri red chili powder->kashmiri red chili powder | 1 |
| synonym_word:arbi->taro root | 1 |

## Synonym Dictionary Categories

| Category | Count |
|----------|-------|
| spice | 59 |
| vegetable_other | 32 |
| pulse | 28 |
| grain | 26 |
| vegetable_root_tuber | 24 |
| fruit | 22 |
| vegetable_leafy | 17 |
| dairy | 14 |
| nut | 14 |
| oil | 10 |
| sweetener | 7 |
| dried_fruit | 6 |
| fat | 5 |

## Representative Successful Examples

| Original | Normalized | Synonym Applied | Confidence |
|----------|------------|-----------------|------------|
| 1 Onion - thinly sliced | 1 onion (bulb) - thinly sliced | onion | 0.99 |
| 2 teaspoons Turmeric powder (Haldi) | 2 teaspoons turmeric powder (haldi) | turmeric powder | 0.99 |
| 2 teaspoons Cumin seeds (Jeera) | 2 teaspoons cumin seeds (jeera) | cumin seeds | 0.99 |
| 1 tablespoon Coriander Powder (Dhania) | 1 tablespoon coriander powder (dhania) | coriander powder | 0.99 |
| 1 tablespoon Amchur (Dry Mango Powder) | 1 tablespoon amchur (dry mango (ripe) powder) | mango | 0.99 |
| Sunflower Oil - as required | sunflower oil - as required | sunflower oil | 0.90 |
| 1 Onion - thinly sliced | 1 onion (bulb) - thinly sliced | onion | 0.99 |
| 2 teaspoons Turmeric powder (Haldi) | 2 teaspoons turmeric powder (haldi) | turmeric powder | 0.99 |
| 2 teaspoons Cumin seeds (Jeera) | 2 teaspoons cumin seeds (jeera) | cumin seeds | 0.99 |
| 1 tablespoon Coriander Powder (Dhania) | 1 tablespoon coriander powder (dhania) | coriander powder | 0.99 |
| 1 tablespoon Amchur (Dry Mango Powder) | 1 tablespoon amchur (dry mango (ripe) powder) | mango | 0.99 |
| Sunflower Oil - as required | sunflower oil - as required | sunflower oil | 0.90 |
| 1/2 teaspoon cumin seeds | 1/2 teaspoon cumin seeds | cumin seeds | 0.99 |
| 1 teaspoon white urad dal | 1 teaspoon white black gram (split) | urad dal | 0.99 |
| 2 teaspoon cashew - or peanuts | 2 teaspoon cashew - or peanuts | cashew | 0.99 |
| 1-1 / 2 tablespoon oil - 1/2 teaspoon asafoetida | 1-1 / 2 tablespoon oil - 1/2 teaspoon asafoetida | asafoetida | 0.99 |
| 1 Onion - sliced | 1 onion (bulb) - sliced | onion | 0.99 |
| 1/3 cup Green peas (Matar) | 1/3 cup green peas (fresh) (matar) | green peas | 0.99 |
| 1/4 teaspoon Asafoetida (hing) | 1/4 teaspoon asafoetida (hing) | asafoetida | 0.99 |
| 1 teaspoon Mustard seeds | 1 teaspoon mustard seeds | mustard seeds | 0.99 |

## Representative Unmatched / Unknown Expressions

- 6 karela (bitter gourd/ pavakkai) - deseeded
- salt - to taste
- 3 tablespoon gram flour (besan)
- 1 tablespoon red chilli powder
- 2-1/2 कप चावल - पका ले
- 3 टमाटर
- 3 छोटा चमच्च बीसी बेले भात पाउडर
- नमक - स्वाद अनुसार
- 1 छोटा चमच्च चना दाल
- 1/2 छोटा चमच्च जीरा
- 1 छोटा चमच्च सफ़ेद उरद दाल
- 1/2 छोटा चमच्च राइ
- 1 हरी मिर्च
- 1 सुखी लाल मिर्च
- 2 छोटा चमच्च काजू - या मूंगफली
- 1-1/2 बड़े चमच्च तेल - प्रयोग अनुसार
- 1/2 छोटा चमच्च हींग
- 2-1 / 2 cups rice - cooked
- 3 tomatoes
- 3 teaspoons bc belle bhat powder
- salt - as per taste
- 1 teaspoon chickpea lentils
- 1/2 teaspoon mustard
- 1 green chilli
- 1 dry red chilli
- 1-1/2 cups rice vermicelli noodles (thin)
- 1/2 cup carrots (gajjar) - chopped
- 2 green chillies
- 500 grams chicken
- 4 green chillies - slit

## Known Limitations

1. **Synonym coverage incomplete**: Many regional names, brand names, and compound ingredients not yet mapped.
2. **Quantity/unit not parsed**: This stage only normalizes ingredient names; quantities and units remain embedded.
3. **Preparation state ambiguous**: 'chopped onion' vs 'onion' not distinguished unless explicitly in synonym dict.
4. **Mixed language handling**: Hindi/English mixed text handled but transliteration variations may be missed.
5. **Compound ingredients**: Multi-word ingredients like 'ginger garlic paste' may not match single-word synonyms.
6. **No IFCT matching**: This stage only normalizes; IFCT matching is Stage 3.
7. **Provisional synonyms**: Some mappings have confidence < 0.9 and should be reviewed.
8. **Distinction preservation**: Explicit exclusion lists prevent over-merging but may miss edge cases.

## Reproducibility

All normalization is deterministic. Re-running with same inputs produces identical outputs.
Timestamp: 2026-11-16T20:09:22.858586
