# Anuvaad INDB 2024.11 — Semantic Audit Report

**Project:** AI for Nutrition & Diet Planning  
**Phase:** 1 — Dataset Validation and Preprocessing (Targeted Audit)  
**Date:** 2026-11-15  
**Auditor:** Lead Data Engineer

---

## 1. Dataset Identity & Purpose

| Field | Value |
|-------|-------|
| **File** | `datasets/Anuvaad_INDB_2024.11.xlsx` |
| **Sheet** | `Sheet1` (single sheet) |
| **Rows** | 1,014 |
| **Columns** | 82 (3 identifiers + 39 per-100g nutrients + 1 serving unit + 39 per-serving nutrients) |
| **MD5 Hash** | `f4db8039b33a6de9d6f602ee372aebab` |
| **Provenance** | Anuvaad / ICMR-NIN Indian Food Composition Database (INDB) 2024.11 release |
| **Licence** | Academic/research use; redistribution terms not explicitly stated in file |

**Stated Purpose (inferred):** Composition database for Indian prepared foods, beverages, and recipes — not raw ingredients.

---

## 2. Sheet-by-Sheet Analysis

### 2.1 Sheet: `Sheet1` (Only Sheet)

| Attribute | Detail |
|-----------|--------|
| **Row count** | 1,014 |
| **Column count** | 82 |
| **Identifier columns** | `food_code` (str), `food_name` (str), `primarysource` (str) |
| **Per-100g nutrient columns** | 39 (all `float64`) |
| **Serving unit column** | `servings_unit` (str, 97 null) |
| **Per-serving nutrient columns** | 39 (all `float64`, 82 rows entirely null) |
| **Primary key** | `food_code` — verified unique (1,014/1,014) |
| **Food name uniqueness** | Verified unique (1,014/1,014) |

**Column Groups:**
```
Identifiers (3):     food_code, food_name, primarysource
Per-100g (39):       energy_kj, energy_kcal, carb_g, protein_g, fat_g, freesugar_g, fibre_g,
                     sfa_mg, mufa_mg, pufa_mg, cholesterol_mg,
                     calcium_mg, phosphorus_mg, magnesium_mg, sodium_mg, potassium_mg,
                     iron_mg, copper_mg, selenium_ug, chromium_mg, manganese_mg,
                     molybdenum_mg, zinc_mg,
                     vita_ug, vite_mg, vitd2_ug, vitd3_ug, vitk1_ug, vitk2_ug,
                     folate_ug, vitb1_mg, vitb2_mg, vitb3_mg, vitb5_mg, vitb6_mg,
                     vitb7_ug, vitb9_ug, vitc_mg, carotenoids_ug
Serving info (1):    servings_unit
Per-serving (39):    unit_serving_energy_kj, unit_serving_energy_kcal, unit_serving_carb_g,
                     unit_serving_protein_g, unit_serving_fat_g, unit_serving_freesugar_g,
                     unit_serving_fibre_g, unit_serving_sfa_mg, unit_serving_mufa_mg,
                     unit_serving_pufa_mg, unit_serving_cholesterol_mg,
                     unit_serving_calcium_mg, unit_serving_phosphorus_mg,
                     unit_serving_magnesium_mg, unit_serving_sodium_mg,
                     unit_serving_potassium_mg, unit_serving_iron_mg,
                     unit_serving_copper_mg, unit_serving_selenium_ug,
                     unit_serving_chromium_mg, unit_serving_manganese_mg,
                     unit_serving_molybdenum_mg, unit_serving_zinc_mg,
                     unit_serving_vita_ug, unit_serving_vite_mg,
                     unit_serving_vitd2_ug, unit_serving_vitd3_ug,
                     unit_serving_vitk1_ug, unit_serving_vitk2_ug,
                     unit_serving_folate_ug, unit_serving_vitb1_mg,
                     unit_serving_vitb2_mg, unit_serving_vitb3_mg,
                     unit_serving_vitb5_mg, unit_serving_vitb6_mg,
                     unit_serving_vitb7_ug, unit_serving_vitb9_ug,
                     unit_serving_vitc_mg, unit_serving_carotenoids_ug
```

---

## 3. Record-Level Classification

### 3.1 Food Code Prefixes & Source Groups

| Prefix | Source Label | Count | Description |
|--------|--------------|-------|-------------|
| **ASC** | `asc_manual` | 490 | Prepared dishes, beverages, sauces, snacks, sandwiches, Western & Indian items |
| **BFP** | `bfp_manual` | 376 | Breakfast Food Preparations — traditional Indian breakfast/lunch dishes |
| **OSR** | `open_source_recipes` | 148 | Open-source recipes — juices, desserts, snacks, traditional preparations |

**Total:** 1,014 records

### 3.2 Semantic Content — All Records Are Prepared Foods

**No raw food ingredients exist in this dataset.** Every record represents a **prepared dish, beverage, or recipe** as consumed.

#### ASC (490) — Examples:
- Beverages: `Hot tea (Garam Chai)`, `Instant coffee`, `Lemonade`, `Mango milkshake`, `Sweet Lassi`
- Sandwiches: `Cheese and chilli sandwich`, `Chicken sandwich`, `Peanut and tomato sandwich`
- Sauces: `White sauce (thin/medium/thick)`, `Cheese sauce`, `Mayonnaise`, `Mustard sauce`
- Snacks: `Samosa`, `Pakora`, `Cutlet`, `Biscuit`, `Cake`, `Pastry`
- Main dishes: `Butter chicken`, `Mutton biryani`, `Vegetable pulao`, `Dal makhani`

#### BFP (376) — Examples:
- Breakfast: `Semolina upma (Suji/Rava upma)`, `Vegetable poha`, `Moong dal cheela`, `Plain omelette`
- Traditional: `Idli`, `Masala dosa`, `Plain parantha/paratha`, `Poori`, `Chapati/Roti`
- Porridges: `Rice upma`, `Vermicelli porridge`, `Cracked wheat porridge`
- Beverages: `Kashmiri tea (Kehwa)`, `Jal jeera`, `Sattu drink`

#### OSR (148) — Examples:
- Juices/Drinks: `Woodapple juice (Bel ka sharbat)`, `Thandai`, `Nannari sharbat`
- Desserts: `Black rice kheer`, `Coconut kheer`, `Mango malpua`, `Amaranth ladoo`, `Besan halwa`
- Snacks: `Finger millet biscuit`, `Jowar dosa`, `Putharekulu`

### 3.3 Evidence Against Raw Ingredient Interpretation

| Search Pattern | Matches Found | Nature of Matches |
|----------------|---------------|-------------------|
| `raw ` | 3 | `Raw mango drink`, `Raw turnip with coconut`, `Raw papaya with coconut` — all prepared |
| `dry ` | 3 | `Dry washed urad`, `Dry potato`, `Dry mango chutney` — processed/prepared |
| `whole ` | 3 | `Whole moong`, `Whole masoor`, `Whole moth` — listed as dals (prepared) |
| `flour` / `atta` / `besan` / `rava` | 15+ | All in prepared dishes (burfi, ladoo, chilla, dosa, kheer, upma) |
| `dal` / `lentil` / `bean` / `chickpea` | 20+ | All in curries, pulao, stuffed breads, soups |
| `rice` / `wheat` / `millet` | 25+ | All in prepared forms (boiled rice, lemon rice, upma, dosa, ladoo, biscuit) |

**Conclusion:** Zero records represent raw agricultural commodities or unprocessed food ingredients.

---

## 4. Nutrient Units & Measurement Basis

### 4.1 Per-100g Columns (39 nutrients)

| Nutrient Group | Columns | Unit | Basis |
|----------------|---------|------|-------|
| Energy | `energy_kj`, `energy_kcal` | kJ, kcal | Per 100g **edible portion of prepared dish** |
| Macronutrients | `carb_g`, `protein_g`, `fat_g`, `freesugar_g`, `fibre_g` | g | Per 100g prepared dish |
| Fatty Acids | `sfa_mg`, `mufa_mg`, `pufa_mg`, `cholesterol_mg` | mg | Per 100g prepared dish |
| Minerals | `calcium_mg`, `phosphorus_mg`, `magnesium_mg`, `sodium_mg`, `potassium_mg`, `iron_mg`, `copper_mg`, `zinc_mg` | mg | Per 100g prepared dish |
| Trace Minerals | `selenium_ug`, `chromium_mg`, `manganese_mg`, `molybdenum_mg` | µg/mg | Per 100g prepared dish |
| Vitamins | `vita_ug`, `vite_mg`, `vitd2_ug`, `vitd3_ug`, `vitk1_ug`, `vitk2_ug`, `folate_ug`, `vitb1_mg`, `vitb2_mg`, `vitb3_mg`, `vitb5_mg`, `vitb6_mg`, `vitb7_ug`, `vitb9_ug`, `vitc_mg` | µg/mg | Per 100g prepared dish |
| Phytonutrients | `carotenoids_ug` | µg | Per 100g prepared dish |

### 4.2 Per-Serving Columns (39 nutrients)

| Column Prefix | Unit | Basis |
|---------------|------|-------|
| `unit_serving_*` | Same as per-100g | Per **defined serving unit** (variable) |

### 4.3 Serving Units (125 distinct values)

Top serving units:
| Unit | Count | Example Foods |
|------|-------|---------------|
| bowl | 269 | Upma, poha, dal, kheer, soup |
| plate | 72 | Rice dishes, biryani, chowmein |
| piece | 57 | Idli, dosa, parantha, poori, biscuit, cutlet |
| biscuit | 29 | Cookies, biscuits |
| tall glass | 21 | Milkshakes, juices, lassi |
| triangle | 21 | Sandwiches (cut) |
| tablespoon | 21 | Chutneys, sauces |
| cup | 19 | Beverages, porridge |
| slice | 19 | Cake, bread, pizza |
| soup bowl | 18 | Soups, consommés |
| glass | 15 | Juices, sharbat |
| small bowl | 15 | Side dishes, chutneys |
| sandwich | 14 | Whole sandwiches |
| parantha | 13 | Paranthas |
| egg | 12 | Egg preparations |
| cookie | 12 | Cookies |
| cutlet | 11 | Cutlets |
| poori | 10 | Pooris |

### 4.4 Implied Serving Weights (Derived)

Per-serving values are mathematically consistent with per-100g values:
```
per_serving_nutrient = per_100g_nutrient × (serving_weight_g / 100)
```

Verified for energy, protein, fat, carbohydrate — **zero inconsistencies** in 50-record sample.

**Example implied serving weights:**
| Food | Serving Unit | Implied Weight |
|------|--------------|----------------|
| Hot tea | tea cup | 210 g |
| Instant coffee | tea cup | 450 g |
| Semolina upma | bowl | 106 g |
| Plain parantha | parantha | 56 g |
| Idli | idli | 25 g |
| Mixed dal | bowl | 298 g |
| Saffron biscuit | biscuit | 11 g |

---

## 5. The 82 Records Missing Per-Serving Data

| Attribute | Detail |
|-----------|--------|
| **Count** | 82 (8.1% of dataset) |
| **Primary Source** | `asc_manual`: 57, `bfp_manual`: 24, `open_source_recipes`: 1 |
| **Prefix** | ASC: 57, BFP: 24, OSR: 1 |
| **Serving Unit** | **All 82 have null `servings_unit`** |
| **Food Types** | Sauces (white, cheese, egg, mushroom, mustard, brown, mayonnaise, dressings), Pastries (short crust, choux, flaky), Cakes (sponge, glace icing), Glazes, Icings |

**Reason:** These items lack a natural "serving unit" (no standard bowl/plate/piece). They are ingredient-like preparations (sauces, batters, pastry doughs) meant to be used *in* other recipes.

---

## 6. Comparison with Documented INDB Methodology

### 6.1 Expected INDB Structure (per ICMR-NIN documentation)

The Indian Food Composition Database (INDB / IFCT) traditionally provides:
- **Raw food ingredients** (cereals, pulses, vegetables, fruits, meats, dairy, etc.)
- **Per 100g edible portion** of raw commodity
- **Standardised food codes** (e.g., FCT codes, NIN codes)
- **~1,600+ raw foods** in IFCT-2017

### 6.2 Actual Anuvaad_INDB_2024.11 Content

| Aspect | Expected (Raw IFCT) | Actual (This Workbook) |
|--------|---------------------|------------------------|
| **Food Type** | Raw commodities | Prepared dishes/recipes |
| **Coverage** | ~1,600 raw foods | 1,014 prepared items |
| **Food Codes** | FCT/NIN standard | ASC/BFP/OSR custom prefixes |
| **Measurement** | Per 100g raw edible | Per 100g prepared as consumed |
| **Use Case** | Ingredient-level calculation | Ready-to-eat dish lookup |
| **Serving Data** | Rarely included | 92% have per-serving values |

**Critical Finding:** This workbook is **not** the standard IFCT raw-food composition table. It is a **derived recipe/prepared-food composition dataset** built on top of (or alongside) the raw IFCT data.

---

## 7. Food-Code Interpretation

| Code | Pattern | Meaning |
|------|---------|---------|
| `ASC###` | `asc_manual` source | Anuvaad Standard Collection? — prepared dishes, beverages, Western items |
| `BFP###` | `bfp_manual` source | Breakfast Food Preparations — traditional Indian meals |
| `OSR###` | `open_source_recipes` source | Open Source Recipes — community/contributed recipes |

**These are NOT interchangeable with IFCT/FCT food codes.** They are internal Anuvaad identifiers for prepared dishes.

---

## 8. Can This Serve as Primary Ingredient-Level Nutrient Reference?

### **NO — Categorically Not Suitable**

| Requirement for Ingredient-Level Reference | This Dataset | Verdict |
|--------------------------------------------|--------------|---------|
| Raw food ingredients (rice, wheat, dal, vegetables, meats) | **Absent** | ❌ |
| Per 100g raw edible portion | Per 100g **prepared** dish | ❌ |
| Decomposable into ingredients | Pre-composed recipes | ❌ |
| Standard food codes (IFCT/FCT) | Custom ASC/BFP/OSR | ❌ |
| Usable for recipe nutrition calculation (ingredient × weight) | No ingredient weights | ❌ |

**This dataset provides:** Nutrition facts for **ready-to-eat dishes** (like a restaurant menu nutrition label).

**This dataset cannot provide:** Nutrition for **raw ingredients** needed to compute recipe nutrition from ingredient lists.

---

## 9. Missing Resources & Unresolved Questions

### 9.1 Missing: Raw-Food Composition Table
The actual **ICMR-NIN IFCT-2017 / INDB raw food composition data** (1,600+ raw ingredients, per 100g raw edible portion) is **not present** in the provided datasets.

**Required for Phase 2:** A raw-ingredient composition table with:
- Standard IFCT food codes
- Per 100g raw edible portion values
- All 39+ nutrients
- Edible portion / waste factors

### 9.2 Unresolved Questions

| Question | Impact |
|----------|--------|
| What is the exact relationship between Anuvaad ASC/BFP/OSR and ICMR-NIN IFCT? | Determines if raw IFCT data can be sourced from same authority |
| Are ASC/BFP/OSR recipes calculated from IFCT raw ingredients? | If yes, reverse-engineering may be possible |
| What are the edible portion / yield factors for each prepared dish? | Needed to convert between raw and prepared |
| Is there a separate raw-food workbook in the Anuvaad distribution? | Must be located before Phase 2 |
| Licence terms for redistribution of Anuvaad data? | Legal clearance needed |

### 9.3 USDA FoodData Central — Suitability for Supplementary Matching

| Criterion | Assessment |
|-----------|------------|
| **Coverage** | 87,990 US foods — comprehensive but wrong food supply |
| **Units** | Same SI units (kcal, g, mg, µg) — compatible |
| **Food Matching** | **High risk** — US varieties ≠ Indian varieties (e.g., "Rice, white, long-grain, regular, raw" vs Indian sona masoori/basmati) |
| **Nutrient Profile** | Different fortification, soil composition, processing |
| **Matching Rules Required** | 1. **Manual curation only** — no automatic name/code matching<br>2. **Explicit mapping table** — recipe ingredient → FDC fdc_id with confidence<br>3. **Gap-fill only** — use only when Indian raw ingredient absent from IFCT<br>4. **Document every substitution** — ingredient, FDC code, nutrient differences, confidence |
| **Verdict** | **Conditionally approved** for gap-fill only with strict manual mapping |

---

## 10. Audit Conclusion & Decision

### **DECISION: CONDITIONALLY APPROVED — BUT NOT FOR INGREDIENT-LEVEL CALCULATIONS**

| Use Case | Approved? | Conditions |
|----------|-----------|------------|
| **Primary ingredient-level nutrient reference** | ❌ **REJECTED** | Dataset contains prepared dishes, not raw ingredients |
| **Ready-to-eat dish nutrition lookup** | ✅ **APPROVED** | Use as-is for meal-level nutrition display |
| **Recipe nutrition via ingredient decomposition** | ❌ **REJECTED** | No ingredient weights or raw compositions |
| **Serving-size reference for Indian dishes** | ✅ **APPROVED** | 931 records have serving units & weights |
| **Gap-fill for missing raw ingredients** | ❌ **REJECTED** | Wrong measurement basis (prepared vs raw) |

### **Required Before Phase 2:**

1. **Obtain the actual ICMR-NIN IFCT raw-food composition table** (1,600+ raw ingredients, per 100g raw edible portion)
2. **Verify licence** for both IFCT raw data and Anuvaad prepared-food data
3. **Establish raw ↔ prepared mapping** (yield factors, recipe formulations) if Anuvaad recipes are derived from IFCT
4. **Do not proceed** with ingredient-level nutrition computation until raw-food table is secured

### **Immediate Actions:**

- [ ] Locate and ingest `IFCT-2017` or `INDB-Raw` raw food composition workbook
- [ ] Validate raw table: food codes, nutrients, units, edible portion factors
- [ ] Map Anuvaad ASC/BFP/OSR dishes to IFCT raw ingredients (if derivations exist)
- [ ] Only then build ingredient parser → nutrition calculator pipeline

---

## 11. Appendix: Record Examples by Category

### Beverages (ASC)
| Code | Name | Energy (kcal/100g) | Serving | kcal/Serving |
|------|------|-------------------|---------|-------------|
| ASC001 | Hot tea (Garam Chai) | 16.1 | tea cup | 34.0 |
| ASC002 | Instant coffee | 23.2 | tea cup | 104.2 |
| ASC021 | Sweet Lassi | 58.3 | tall glass | 258.0 |

### Traditional Breakfast (BFP)
| Code | Name | Energy (kcal/100g) | Serving | kcal/Serving |
|------|------|-------------------|---------|-------------|
| BFP039 | Semolina upma | 147.9 | bowl | 157.1 |
| BFP040 | Vermicelli upma | 152.3 | bowl | 161.9 |
| BFP153 | Appam | 137.5 | appam | 210.3 |

### Breads (ASC/BFP)
| Code | Name | Energy (kcal/100g) | Serving | kcal/Serving |
|------|------|-------------------|---------|-------------|
| ASC097 | Plain parantha | 298.3 | parantha | 166.3 |
| ASC107 | Poori | 274.1 | poori | 342.3 |
| ASC144 | Idli | 137.5 | idli | 34.5 |
| BFP153 | Appam | 137.5 | appam | 210.3 |

### Desserts/Sweets (OSR/ASC)
| Code | Name | Energy (kcal/100g) | Serving | kcal/Serving |
|------|------|-------------------|---------|-------------|
| OSR010 | Coconut kheer | 142.8 | bowl | 258.5 |
| ASC282 | Rice kheer | 128.4 | bowl | 232.6 |
| ASC340 | Gram flour burfi | 398.2 | piece | 119.5 |

### Sauces/Condiments (Missing Per-Serving)
| Code | Name | Energy (kcal/100g) | Serving Unit | Per-Serving |
|------|------|-------------------|--------------|-------------|
| ASC071 | White sauce (thin) | 89.2 | NULL | MISSING |
| ASC074 | Cheese sauce | 156.7 | NULL | MISSING |
| ASC266 | Mayonnaise | 680.4 | NULL | MISSING |

---

**End of Audit Report**  
**Next Step:** Secure raw-food composition table before Phase 2 commencement.