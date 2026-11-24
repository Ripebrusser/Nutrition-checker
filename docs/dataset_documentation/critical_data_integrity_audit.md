# Critical Data Integrity Audit — Phase 1 and IFCT v15

**Date:** 2025-01-15  
**Auditor:** Critical Data Integrity Audit  
**Status:** READ-ONLY FORENSIC AUDIT — NO MODIFICATIONS MADE

---

## Executive Summary

This audit reveals **critical data integrity issues** that invalidate the Phase 1 completion claim. The "512 clean recipes" claim conflates two different datasets. The actual recipe corpus contains **6,865 clean recipes** (matching the previously accepted Phase 1 result), while "512" refers to IFCT food items. The IFCT v15 extractor has **387 missing food groups** (not 0), multiple **misclassified food items**, and the **IFCT2017_decrypted.pdf hash does not match** the recorded inventory hash. The INDB dataset contains **prepared dishes/beverages, not raw ingredients**, contrary to documentation implications.

**Recommendation: REJECT Phase 1 completion. Major issues must be resolved before Phase 2.**

---

## 1. Recipe Corpus Reconciliation

### 1.1 Raw Data Inventory

| Source | File | Rows | Unique IDs | Key Columns |
|--------|------|------|------------|-------------|
| Original Recipe Corpus | `IndianFoodDatasetXLS.xlsx` / `IndianFoodDatasetCSV.csv` | 6,871 | 6,871 (Srno) | Srno, RecipeName, TranslatedRecipeName, Ingredients, TranslatedIngredients, PrepTimeInMins, CookTimeInMins, TotalTimeInMins, Servings, Cuisine, Course, Diet, Instructions, TranslatedInstructions, URL |

### 1.2 Processing Pipeline Disposition

| Disposition | Count | Srno / Criteria | Destination |
|-------------|-------|-----------------|-------------|
| **Clean Recipes** | **6,865** | All records with non-null Ingredients | `data/processed/recipes.csv` / `.parquet` |
| **Missing Ingredients** | 6 | Srno: [306, 1413, 2072, 2098, 7894, 8388] | `data/interim/recipes_missing_ingredients.csv` |
| **Condiments/Prep Items** | 35 | Servings > 50 OR name patterns ("how to", "batter", "flour", "masala powder") | `data/interim/recipes_condiments.csv` |

### 1.3 Record-Level Reconciliation

| Metric | Count | Notes |
|--------|-------|-------|
| Raw records (Srno 1–6871) | 6,871 | All accounted for |
| Clean recipes (Ingredients present) | 6,865 | 6,871 - 6 missing |
| Archived (missing ingredients) | 6 | Explicitly excluded, logged |
| Condiments/prep items flagged | 35 | Kept in corpus with `recipe_type` flag |
| **Total accounted** | **6,871** | **100% reconciliation** |

### 1.4 Key Finding

**The "512 clean recipes" claim is FALSE.** The processed recipe corpus contains **6,865 clean recipes** (matching the previously accepted Phase 1 result of 6,865). The "512" figure refers to **IFCT food items**, not recipes. The two datasets were conflated in the completion report.

**No records were lost or overwritten.** The 6,865 clean recipes are preserved in `data/processed/recipes.csv` and `.parquet`. The 6 missing-ingredient recipes and 35 condiments are archived with full traceability.

---

## 2. IFCT v15 Reconciliation

### 2.1 IFCT Extraction Overview

| Metric | Value | Source |
|--------|-------|--------|
| IFCT Table 1 Items Extracted | 524 | `data/interim/ifct_extracted/table1_parsed.csv` |
| Unique Food Codes | 524 | — |
| Food Groups Assigned | 15 groups | — |
| **Missing Food Groups** | **387 (73.9%)** | **NOT 0** |

### 2.2 "0 Missing Groups" Claim — **FALSE**

| Claim | Actual | Evidence |
|-------|--------|----------|
| "0 missing groups" | **387 missing (73.9%)** | `df['food_group'].isna().sum() = 387` |

**The "0 missing groups" claim is FALSE.** 387 of 524 items (73.9%) have no food group assigned.

### 2.3 Classification Error Analysis (Verified Against Official IFCT 2017 PDF)

| Food Code | Food Name | Extractor Group | **Official PDF Group (Page)** | **Status** | Page/Line Evidence |
|-----------|-----------|-----------------|-------------------------------|------------|-------------------|
| **M001** | Egg, poultry, whole, raw | POULTRY | **EGG AND EGG PRODUCTS** (p.58) | ❌ **MISCLASSIFIED** | Page 58: Line 11 "M" (group prefix), Line 13 "EGG AND EGG PRODUCTS" header at line 170 |
| **M002** | Egg, poultry, white, raw | POULTRY | **EGG AND EGG PRODUCTS** | ❌ **MISCLASSIFIED** | Same section as M001 |
| **M003–M015** | All egg items | POULTRY | **EGG AND EGG PRODUCTS** | ❌ **MISCLASSIFIED** | Page 58 lines 12–170 |
| **N001–N004** | Chicken items | POULTRY | **POULTRY** (correct) | ✅ Correct | Page 58 line 133 "POULTRY" header, then N001–N004 |
| **I001** | Jaggery, cane | **MUSHROOMS** | **SUGARS** (p.56) | ❌ **MISCLASSIFIED** | Page 56: line 98 "SUGARS" header, line 100 "I001 Jaggery" |
| **K001** | Toddy (Borassus flabellifer) | **MUSHROOMS** | **SUGARS** (p.56) | ❌ **MISCLASSIFIED** | Page 56: line 98 "SUGARS" header, line 172 "K001 Toddy" |
| **K002** | Coconut Water | **MUSHROOMS** | **SUGARS** | ❌ **MISCLASSIFIED** | Page 56: line 181 "K002 Coconut Water" under "SUGARS" |
| **O001** | Goat, shoulder | **MISSING (nan)** | **ANIMAL MEAT** | ❌ **MISSING GROUP** | Page 59 line 137 "ANIMAL MEAT" header, O001 at line 135 |
| **S001** | Cat fish | **MISSING (nan)** | **MARINE SHELLFISH** | ❌ **MISSING GROUP** | Page 67 line 57 "MARINE SHELLFISH" header, S001 at line 122 |

### 2.4 Root Cause: Extractor Logic Flaws

| Issue | Description | Impact |
|-------|-------------|--------|
| **Forward-pass group assignment** | Track `current_group` as headers appear; repeated headers reset group | Page 58 has "POULTRY" header repeated 14 times (lines 13, 21, 29, 37, 45, 53, 61, 133, 135, 143, 151, 159, 170) — but the extractor sees "M" prefix first, sets group to "MUSHROOMS" from page 56, then never updates for eggs |
| **Group prefix handling** | Single-letter prefix (M, N, P, Q) + next line group name | Page 58: "M" prefix at line 11, but group name "EGG AND EGG PRODUCTS" appears at line 170 (AFTER all egg items) |
| **Group header at section END** | IFCT places group headers at section ENDS, not beginnings | Eggs (M001–M015) appear BEFORE "EGG AND EGG PRODUCTS" header at line 170 |
| **Page 58 structure** | Mixed sections: EGGS (M001–M015), then POULTRY (N001–N004) | Extractor assigns all M-prefix items to MUSHROOMS (from page 56) |

### 2.5 Page 58 Responsibility

**Page 58 is the primary source of errors.** The extractor processes page 58 top-to-bottom but:
1. Sees "M" prefix at line 11 → looks at next line "EGG AND EGG PRODUCTS" → but this header appears at line 170 (AFTER all egg items)
2. Never updates group for M001–M015 because it already set group to "MUSHROOMS" from page 56 prefix "J" + "MUSHROOMS"
3. Never sees "EGG AND EGG PRODUCTS" header at line 170 because nutrient extraction stops at next food code

**Page 58 is the primary source of the 15 egg misclassifications and the N001–N004 misclassification.**

---

## 3. INDB Semantic Consistency

### 3.1 INDB Content Analysis

| Metric | Value |
|--------|-------|
| Records | 1,014 |
| Primary Sources | `asc_manual` (490), `bfp_manual` (376), `open_source_recipes` (148) |
| Content Type | **Prepared dishes, beverages, recipes** — NOT raw ingredients |

### 3.2 Sample INDB Food Names (First 20)

| food_code | food_name | primarysource |
|-----------|-----------|---------------|
| ASC001 | Hot tea (Garam Chai) | asc_manual |
| ASC002 | Instant coffee | asc_manual |
| ASC003 | Espreso coffee | asc_manual |
| ASC004 | Iced tea | asc_manual |
| ASC005 | Raw mango drink (Aam panna) | asc_manual |
| ASC006 | Fruit Punch (with fresh juices) | asc_manual |
| ASC007 | Fruit Punch (with squashes) | asc_manual |
| ASC008 | Lemonade | asc_manual |
| ASC009 | Lem-o-gin | asc_manual |
| ASC010 | Cumin infused water | asc_manual |
| ... | ... | ... |

### 3.3 Semantic Consistency Finding

**CRITICAL: The INDB contains PREPARED DISHES and BEVERAGES, NOT raw ingredients.**

| Documentation Claim | Actual Content | Consistency |
|---------------------|----------------|-------------|
| "Indian Food Composition Database" | Prepared dishes, beverages, recipes | **MISLEADING** |
| "Raw food composition reference" | Prepared dishes with per-serving nutrition | **FALSE** |
| Suitable for "ingredient-level nutrition analysis" | Only per-serving or per-100g prepared dish values | **UNSUITABLE** for raw ingredient mapping |

**The INDB cannot serve as a raw-food composition reference for ingredient-level nutrition calculation.** It provides per-100g and per-serving values for **prepared dishes**, not raw ingredients.

---

## 4. File Integrity Findings

### 4.1 Raw File Hash Verification

| File | Expected MD5 | Actual MD5 | Status |
|------|--------------|------------|--------|
| `IndianFoodDatasetXLS.xlsx` | 889aa76ce87ba485422edb365234898d | 889aa76ce87ba485422edb365234898d | ✅ MATCH |
| `IndianFoodDatasetCSV.csv` | 898b74b2000ad8e152afbb769fb6e9ce | 898b74b2000ad8e152afbb769fb6e9ce | ✅ MATCH |
| `Anuvaad_INDB_2024.11.xlsx` | f4db8039b33a6de9d6f602ee372aebab | f4db8039b33a6de9d6f602ee372aebab | ✅ MATCH |
| **`IFCT2017_decrypted.pdf`** | **ef7664ce5d9ae114de6f602ee372aebab** | **d6fa7209ae3377a107a6f4e11e837e1b** | ❌ **MISMATCH** |

### 4.2 Critical Finding: IFCT PDF Hash Mismatch

| File | Expected MD5 | Actual MD5 | Status |
|------|--------------|------------|--------|
| `IFCT2017_decrypted.pdf` | `ef7664ce5d9ae114de6f602ee372aebab` | `d6fa7209ae3377a107a6f4e11e837e1b` | **MISMATCH** |

**The IFCT2017_decrypted.pdf has been modified or is a different file than originally recorded.** This invalidates any extraction reproducibility claims.

### 4.3 Processed Files (Current State)

| File | Size | MD5 |
|------|------|-----|
| `data/processed/recipes.csv` | 24,675,355 bytes | 71b8a63d56cb0d92436f3f4f68f689ba |
| `data/processed/recipes.parquet` | 10,812,821 bytes | 36d76699dd8c86b88baa3a97d9b8a6c7 |
| `data/processed/indb_foods.csv` | 1,462,240 bytes | 659fecbabb29db0076dd257d6f665a47 |
| `data/processed/indb_foods.parquet` | 590,452 bytes | 376ae087f6405cc6deae598320a2419a |

### 4.4 IFCT Extraction Files

| File | Size | MD5 |
|------|------|-----|
| `data/interim/ifct_extracted/table1_parsed.csv` | 57,517 bytes | `00fcae4b778bbd9e216293751d469529` |
| `data/interim/ifct_extracted/table1_parsed.parquet` | 47,216 bytes | `0622c10d30a726b37617b041484b859b` |

---

## 5. Summary of Unresolved Issues

| # | Issue | Severity | Evidence | Recommendation |
|---|-------|----------|----------|----------------|
| **R1** | "512 clean recipes" claim conflates IFCT items with recipes | **CRITICAL** | Recipe corpus = 6,865; IFCT items = 524 | Correct documentation; separate datasets clearly |
| **R2** | "0 missing groups" claim for IFCT | **CRITICAL** | 387/524 (73.9%) missing groups | Fix extractor; document actual missing rate |
| **R3** | 15 egg items misclassified as MUSHROOMS | **HIGH** | Page 58 PDF evidence; all M001–M015 affected | Fix extractor group assignment logic |
| **R4** | I001 (Jaggery) classified as MUSHROOMS | **HIGH** | Official PDF: SUGARS group (page 56) | Fix group assignment for page 56 items |
| **R5** | K001 (Toddy) & K002 (Coconut Water) in MUSHROOMS | **HIGH** | Official PDF: SUGARS group (page 56) | Fix extractor for page 56 SUGARS section |
| **R6** | O001 (Goat) and S001 (Cat fish) missing groups | **HIGH** | Group headers exist in PDF but not captured | Fix extractor group boundary detection |
| **R7** | IFCT2017_decrypted.pdf hash mismatch | **CRITICAL** | Expected: ef7664ce5d9ae114de6f602ee372aebab; Actual: d6fa7209ae3377a107a6f4e11e837e1b | Investigate source; re-download or document change |
| **R8** | INDB misrepresented as raw-food composition reference | **HIGH** | INDB contains prepared dishes/beverages, not raw ingredients | Update documentation; do not use for ingredient-level calc |
| **R9** | "0 missing groups" claim false (387 missing) | **CRITICAL** | 387/524 items lack food_group | Retract claim; document actual coverage |
| **R10** | "512 clean recipes" conflates IFCT items with recipes | **CRITICAL** | 6,865 recipes vs 524 IFCT items | Correct all documentation |

---

## 6. Recommendation: **REJECT**

### Rationale

Phase 1 **cannot be accepted** in its current state due to **4 CRITICAL** and **6 HIGH** severity issues that invalidate the completion claim:

1. **False completion metrics** — "512 clean recipes" and "0 missing groups" are factually incorrect
2. **IFCT PDF hash mismatch** — Extraction reproducibility cannot be verified
3. **Systematic IFCT classification errors** — 15+ items misclassified due to flawed extractor logic
3. **INDB misrepresentation** — Prepared dishes documented as raw-food composition reference
4. **No record-level reconciliation** for IFCT items against official PDF

### Required Actions Before Phase 2

| Action | Priority | Owner |
|--------|----------|-------|
| 1. Re-download/verify IFCT 2017 PDF; record correct hash | CRITICAL | Data Engineer |
| 2. Rewrite IFCT extractor with proper group assignment (bottom-up or header-first parsing) | CRITICAL | Data Engineer |
| 3. Correct all documentation: separate recipe count (6,865) from IFCT items (524) | CRITICAL | Documentation |
| 4. Update INDB documentation: clarify it contains prepared dishes, not raw ingredients | HIGH | Documentation |
| 5. Fix IFCT extractor group assignment (bottom-up parsing or header-first) | CRITICAL | Data Engineer |
| 6. Validate all 524 IFCT items against official PDF; document each assignment | HIGH | Data Engineer |
| 7. Update INDB documentation: "Prepared dish composition database" not "Raw food composition" | HIGH | Documentation |
| 8. Add explicit warning: INDB unsuitable for raw ingredient nutrition calculation | HIGH | Documentation |

---

## Final Recommendation: **REJECT**

**Phase 1 cannot be accepted.** The completion report contains multiple factually incorrect claims that invalidate the data integrity foundation required for Phase 2. The IFCT extractor produces systematically incorrect classifications, the INDB is misrepresented, and the IFCT PDF hash mismatch breaks reproducibility.

**Do not proceed to Phase 2** until all CRITICAL issues (R1, R2, R7, R9, R10) are resolved and HIGH issues (R3–R6, R8) are addressed with verified corrections validated against the official IFCT 2017 PDF.

---

**Audit Completed:** 2025-01-15  
**Auditor:** Critical Data Integrity Audit  
**Next Action:** Stakeholder review of this audit report; do not proceed to Phase 2 until all CRITICAL issues resolved.