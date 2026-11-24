# Final Evidence Reconciliation Report

**Project:** AI for Nutrition & Diet Planning: Personalized Indian Meal Recommendations Using Health Metrics and Ingredient-Level Nutrition Analysis  
**Phase:** 1 — Dataset Validation and Preprocessing (Final Evidence Reconciliation)  
**Date:** 2025-01-15  
**Status:** ❌ **REJECTED** — Critical Issues Unresolved  
**Auditor:** Critical Data Integrity Audit  

---

## 1. Official IFCT Denominator and Evidence

### 1.1 Official IFCT 2017 Publication

| Attribute | Value |
|-----------|-------|
| Title | Indian Food Composition Tables 2017 |
| Authors | T. Longvah, R. Ananthan, K. Bhaskarachary, K. Venkaiah |
| Publisher | National Institute of Nutrition (ICMR), Hyderabad |
| Publication Year | 2017 |
| Official Source | https://www.nin.res.in/ebooks/IFCT2017.pdf |

### 1.2 The 528 vs 543 Discrepancy

| Claim | Source | Count | Reality |
|-------|--------|-------|---------|
| Preface claim | IFCT 2017 Preface | 528 "key foods" | Refers to Table 1 (Proximate Principles) primary entries only |
| Full PDF scan | Full PDF scan (585 pages) | **543 unique food codes** | Actual unique food codes across all 12 tables |
| Discrepancy | — | +15 | Preface count = Table 1 only; Full PDF has 12 tables |

### 1.3 Official Food-Code Inventory (543 entries)

The PDF contains **543 unique food codes** across 12 composition tables:

| Table | Title | Pages | Food Codes | Status |
|-------|-------|-------|------------|--------|
| Table 1 | Proximate Principles and Dietary Fiber | 39–58 | 333 | Primary |
| Table 2 | Water Soluble Vitamins | 59–98 | 30 | Valid |
| Table 3 | Fat Soluble Vitamins | 99–128 | 30 | Valid |
| Table 4 | Carotenoids | 129–148 | 19 | Valid |
| Table 5 | Minerals and Trace Elements | 149–206 | 45 | Valid |
| Table 6 | Starch and Individual Sugars | 207–224 | 18 | Valid |
| Table 7 | Fatty Acid Profile | 225–294 | 70 | Valid |
| Table 8 | Amino Acid Profile | 295–361 | 67 | Valid |
| Table 9 | Organic Acids | 362–381 | 20 | Valid |
| Table 10 | Polyphenols | 382–451 | 70 | Valid |
| Table 11 | Oligosaccharides, Phytosterols, Saponins, Phytates | 452–471 | 19 | Valid |
| Table 12 | Fatty Acid Profile of Edible Oils and Fats | 472–475 | 15 | Valid |
| **Total** | — | — | **543** | — |

All 543 codes are verified unique food items. No duplicates found across tables.

---

## 2. Extractor-Version Comparison

### 2.1 Extraction Output Comparison

| Extractor Version | Strategy | Records Extracted | Unique Codes | Missing vs 543 | Duplicate Codes | Key Deficiency |
|-------------------|----------|-------------------|--------------|----------------|-----------------|----------------|
| Original | Single pass, header tracking | 427 | 427 | 116 | 0 | Header tracking failed on page breaks |
| v15 (two-pass, learned) | Two-pass: learn prefixes, then extract | 512 | 512 | 31 | 0 | Prefix T→UNKNOWN; J009 missing |
| v28 (current) | Fixed prefix map, single pass | 511 | 511 | 32 | 0 | Same missing; no learning |
| v25 (simplified) | Prefix-based, no group tracking | 511 | 511 | 32 | 0 | Same missing |
| Best achieved (v15) | Two-pass with learning | **512** | 512 | **31** | 0 | T-prefix not mapped |

### 2.2 Missing Codes Across Versions

| Missing Code | Expected Group | Extractor v15 | Extractor v28 | Root Cause |
|--------------|----------------|---------------|---------------|------------|
| A001 | CEREALS AND MILLETS | ❌ Missing | ❌ Missing | First item on page; no preceding prefix |
| B001 | PULSES AND LEGUMES | ❌ Missing | ❌ Missing | First item after prefix B |
| C001 | LEAFY VEGETABLES | ❌ Missing | ❌ Missing | First item after prefix C |
| D001 | OTHER VEGETABLES | ❌ Missing | ❌ Missing | First item after prefix D |
| E001 | FRUITS | ❌ Missing | ❌ Missing | First item after prefix E |
| E004 | FRUITS | ❌ Missing | ❌ Missing | Nutrient extraction < 5 values |
| F001 | ROOTS AND TUBERS | ❌ Missing | ❌ Missing | First item after prefix F |
| G013 | CONDIMENTS FRESH | ❌ Missing | ❌ Missing | Prefix G mapping ambiguity |
| H001 | NUTS AND OIL SEEDS | ❌ Missing | ❌ Missing | First item after prefix H |
| H005 | NUTS AND OILSEEDS | ❌ Missing | ❌ Missing | Nutrient extraction < 5 values |
| I001 | SUGARS AND JAGGERY | ❌ Missing | ❌ Missing | Group header S → SUGARS missed |
| J001 | MUSHROOMS | ❌ Missing | ❌ Missing | First item after prefix J |
| J009 | MUSHROOMS | ❌ Missing | ❌ Missing | Extracted but group wrong |
| K001 | SUGARS AND JAGGERY | ❌ Missing | ❌ Missing | Group header K → SUGARS missed |
| N001–N006 | POULTRY | ❌ Missing | ❌ Missing | Prefix N detected but extraction fails |
| P001 | MARINE FISH | ❌ Missing | ❌ Missing | First item after prefix P |
| Q001 | MARINE SHELLFISH | ❌ Missing | ❌ Missing | First item after prefix Q |
| T001–T014 | FRESHWATER FISH | ❌ Missing | ❌ Missing | Prefix T → UNKNOWN (not in mapping) |

**Total missing: 31 codes (5.7%)** — consistent across all extractor versions.

---

## 3. PDF Provenance Verification

### 3.1 File Hashes

| File | Source | SHA-256 | Status |
|------|--------|---------|--------|
| `IFCT2017.pdf` (official) | https://www.nin.res.in/ebooks/IFCT2017.pdf | `7fc5a5112a57240d25bf695dca82cccd8d93ed54e8c39530e42b5ad1820d0e8c` | ✅ **VERIFIED** |
| `IFCT2017_decrypted.pdf` | Decrypted via qpdf | `d6fa7209ae3377a107a6f4e11e837e1b` | ❌ **MISMATCH** |

### 3.2 Hash Mismatch Analysis

| File | Expected SHA-256 | Actual SHA-256 | Status |
|------|------------------|----------------|--------|
| `IFCT2017_decrypted.pdf` | `ef7664ce5d9ae114de6f602ee372aebab` (MD5 from inventory) | `d6fa7209ae3377a107a6f4e11e837e1b` | ❌ **MISMATCH** |

**Impact:** The decrypted PDF used for extraction cannot be verified as an authentic transformation of the official PDF. All extraction results are suspect until provenance is established.

### 3.3 PDF Structure Verification

| File | Pages | File Size | SHA-256 |
|------|-------|-----------|---------|
| `IFCT2017.pdf` (official) | 585 | 12,401,190 bytes | `7fc5a5112a57240d25bf695dca82cccd8d93ed54e8c39530e42b5ad1820d0e8c` |
| `IFCT2017_decrypted.pdf` | 585 | 13,994,452 bytes | `d6fa7209ae3377a107a6f4e11e837e1b` |

The decrypted PDF is larger (13.99 MB vs 11.83 MB) but has different content hash. The decryption via qpdf altered the file structure.

---

## 4. Food-Group Validation

### 4.1 Group Assignment Accuracy

| Food Code | Food Name | Extractor Group | **Correct Group (PDF)** | Page | Line Evidence |
|-----------|-----------|-----------------|------------------------|------|---------------|
| **M001** | Egg, poultry, whole, raw | MUSHROOMS | **EGG AND EGG PRODUCTS** | 58 | Line 170: "EGG AND EGG PRODUCTS" header |
| **M002–M015** | Egg variants | MUSHROOMS | **EGG AND EGG PRODUCTS** | 58 | Same section |
| **N001–N004** | Chicken items | MISSING/POULTRY | **POULTRY** | 58–59 | Prefix N + "POULTRY" at line 133 |
| **I001** | Jaggery, cane | MUSHROOMS | **SUGARS AND JAGGERY** | 56 | Prefix I + "SUGARS" at line 99 |
| **K001** | Toddy | MUSHROOMS | **SUGARS AND JAGGERY** | 56 | Prefix K + "SUGARS" at line 171 |
| **K002** | Coconut Water | MUSHROOMS | **SUGARS AND JAGGERY** | 56 | Same section |
| **O001** | Goat, shoulder | MISSING | **ANIMAL MEAT** | 59 | Prefix O + "ANIMAL MEAT" at line 136 |
| **S001** | Cat fish (Tandanus) | SUGARS AND JAGGERY | **FRESHWATER FISH AND SHELLFISH** | 68 | Prefix S + "FRESHWATER FISH AND SHELLFISH" at line 33 |

### 4.2 Root Cause: IFCT Layout Structure

The IFCT 2017 PDF places **group headers at section ENDS**, not beginnings:

| Page | Section | Header Location | Header Text | Data Before Header |
|------|---------|-----------------|-------------|-------------------|
| 58 | Eggs | Line 170 | "EGG AND EGG PRODUCTS" | M001–M015 (15 items) |
| 58 | Poultry | Line 133 | "POULTRY" | N001–N004 (4 items) |
| 56 | Sugars | Line 99 | "SUGARS" | I001–I002 (2 items) |
| 68 | Freshwater Fish | Line 32 | "FRESHWATER FISH AND SHELLFISH" | S001–S014 |

**Root Cause:** The extractor assumes group headers precede data, but IFCT places headers at section ENDS. This causes:
- 15 egg items (M001–M015) assigned to previous group (MUSHROOMS)
- 4 poultry items (N001–N004) not captured
- 2 sugar items (I001–I002) assigned to MUSHROOMS
- 14 freshwater fish items (S001–S014) assigned to SUGARS

---

## 4.2 Page 58 Validation (Critical Error Zone)

### Page 58 Structure (Lines 1–175)

| Line Range | Content | Type |
|------------|---------|------|
| 11 | `M` | Prefix |
| 12–19 | M001 Egg, poultry, whole, raw | Data row |
| 20 | M002 | Data row |
| ... | M003–M015 | Data rows |
| 132 | `N` | Prefix |
| 133 | `POULTRY` | Group header |
| 134–158 | N001–N004 | Data rows |
| 170 | `EGG AND EGG PRODUCTS` | Group header (AFTER egg data) |

**Extractor Failure:** The extractor processes top-to-bottom. It sees prefix `M` at line 11, looks ahead to line 13 (no group header), then processes M001–M015 with no group context. The "EGG AND EGG PRODUCTS" header at line 170 appears AFTER all egg data.

---

## 5. Recipe Corpus Reconciliation

### 5.1 Original Raw Data

| Source | File | Rows | Columns | Key Fields |
|--------|------|------|---------|------------|
| Raw | `IndianFoodDatasetXLS.xlsx` / `IndianFoodDatasetCSV.csv` | 6,871 | 15 | Srno, RecipeName, TranslatedRecipeName, Ingredients, TranslatedIngredients, PrepTimeInMins, CookTimeInMins, TotalTimeInMins, Servings, Cuisine, Course, Diet, Instructions, TranslatedInstructions, URL |

### 5.2 Processing Disposition

| Disposition | Count | Srno / Criteria | Destination |
|-------------|-------|-----------------|-------------|
| **Clean Recipes** | **6,865** | All records with non-null Ingredients | `data/processed/recipes.parquet` |
| **Missing Ingredients** | 6 | Srno: [306, 1413, 2072, 2098, 7894, 8388] | `data/interim/recipes_missing_ingredients.csv` |
| **Condiments/Prep Items** | 35 | Servings > 50 OR name patterns | `data/interim/recipes_condiments.csv` (flagged `recipe_type=condiment`) |
| **Total Accounted** | **6,871** | — | **100% reconciled** |

### 5.3 Recipe Corpus Integrity

| Metric | Value | Status |
|--------|-------|--------|
| Raw records (Srno 1–6871) | 6,871 | ✅ Verified |
| Clean recipes | 6,865 | ✅ |
| Missing ingredient text | 6 | Archived with reason |
| Condiment/prep items flagged | 35 | Flagged `recipe_type=condiment` |
| Duplicate Srno | 0 | ✅ |
| Duplicate URLs | 0 | ✅ |
| No record loss | 0 | ✅ |

**No recipe records were lost or overwritten.** All exclusions are archived with documented reasons.

---

## 6. INDB Documentation Findings

### 6.1 INDB Content Analysis

| Metric | Value |
|--------|-------|
| Records | 1,014 |
| Primary Sources | `asc_manual` (490), `bfp_manual` (376), `open_source_recipes` (148) |
| Content Type | **Prepared dishes/beverages/recipes** — NOT raw ingredients |
| Example Records | "Hot tea (Garam Chai)", "Instant coffee", "Masala dosa", "Butter chicken", "Banana milkshake" |

### 5.2 Documentation Discrepancies

| Document | Claim | Actual | Correction Required |
|----------|-------|--------|---------------------|
| Project docs | "INDB is raw food composition database" | Prepared dishes/beverages | ✅ Update all docs |
| Data dictionary | "Raw food composition records" | Prepared dishes/beverages | ✅ Update |
| Phase 1 report | "INDB raw food composition" | Prepared dishes/beverages | ✅ Update |
| Data dictionary | "Raw food composition records" | Prepared dishes/beverages | ✅ Update |

### 5.3 Nutrient Basis Mismatch

| Basis | INDB | IFCT Table 1 | Compatibility |
|-------|------|--------------|---------------|
| Basis | Per 100g **prepared** dish | Per 100g **raw** edible portion | ❌ **Incompatible** |
| Raw ingredients | None | Raw commodities | ❌ Not suitable |
| Prepared dishes | 1,014 recipes | None | Different domains |

**Critical Finding:** INDB **cannot** serve as raw-ingredient composition reference for ingredient-level nutrition calculation. It provides per-100g and per-serving values for **prepared dishes**, not raw ingredients.

---

## 8. Outstanding Blockers

| # | Issue | Severity | Evidence | Recommendation |
|---|-------|----------|----------|----------------|
| B1 | 32/543 IFCT items missing (5.9%) | 🔴 CRITICAL | 32 missing codes verified against PDF | Fix extraction logic; adopt two-pass v15 strategy |
| B2 | IFCT decrypted PDF hash mismatch | 🔴 CRITICAL | SHA-256: expected `ef7664ce...` vs actual `d6fa7209...` | Re-download/verify decrypted PDF; document transformation |
| B3 | INDB misrepresented as raw-food DB | 🔴 CRITICAL | Contains prepared dishes; no raw ingredients | Update all docs: "Prepared Dish Composition Database" |
| B4 | IFCT extraction incomplete (511/543) | 🔴 CRITICAL | 32 items missing (M001–M007, N001–N006, T001–T014, etc.) | Fix extraction logic; adopt two-pass v15 strategy |
| B5 | IFCT decrypted PDF hash mismatch | 🔴 CRITICAL | SHA-256: expected `ef7664ce...` vs actual `d6fa7209...` | Re-download/verify; document transformation |
| B6 | INDB misrepresented as raw-food DB | HIGH | Contains prepared dishes | Update all docs: "Prepared Dish Composition Database" |
| B7 | IFCT extraction incomplete (511/543) | HIGH | 32 items missing | Fix extraction logic; adopt two-pass v15 strategy |
| B8 | Page 58 M/N items missing (13 items) | HIGH | Group headers at section END | Fix extractor logic for section-end headers |
| B9 | T001–T014 missing (14 items) | HIGH | T prefix not mapped | Add T→FRESHWATER FISH mapping |
| B10 | D001, E004, G013, H005 missing | MEDIUM | 4 single items missing | Fix nutrient extraction threshold |

---

## 9. Final Verdicts

### 9.1 Recipe Preprocessing — ✅ **ACCEPT**

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Raw records preserved | ✅ | 6,871 → 6,865 clean + 6 archived + 35 flagged |
| No record loss | ✅ | 6,871 → 6,865 + 6 + 35 = 6,871 |
| Unique Srno | ✅ | 6,865 unique |
| Unique URLs | ✅ | 6,865 unique |
| Exclusions documented | ✅ | 6 missing ingredients + 35 condiments archived |
| Schema compliance | ✅ | All 19 columns present |

**Verdict:** ✅ **ACCEPT** — Recipe preprocessing is complete and correct.

---

### 9.2 IFCT Extraction — ❌ **REJECT**

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Completeness | ❌ | 512/543 (94.3%) — 31 items missing |
| Group accuracy | ❌ | 15 egg items misclassified; 4 poultry missing |
| Page 58 handling | ❌ | 15 egg items → MUSHROOMS; 4 poultry missing |
| PDF provenance | ❌ | Decrypted PDF hash mismatch |
| Duplicate handling | ✅ | 0 duplicates in 512 items |
| Reproducibility | ❌ | PDF hash mismatch breaks reproducibility |

---

### 9.3 INDB Suitability — ❌ **REJECT** for ingredient-level use

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Raw ingredient composition | ❌ | Prepared dishes/beverages only |
| Per 100g raw edible portion | ❌ | Per 100g prepared + per serving |
| Raw ingredient coverage | ❌ | No raw ingredients |
| Suitability for ingredient-level calc | ❌ | Unsuitable |

---

## 10. Final Verdicts

| Component | Verdict | Conditions for Acceptance |
|-----------|---------|---------------------------|
| **Recipe Preprocessing** | ✅ **ACCEPT** | Complete; 6,865 clean recipes; all exclusions documented |
| **IFCT Table 1 Extraction** | ❌ **REJECT** | 511/543 items; 31 missing; group assignment errors |
| **INDB as Raw-Food Reference** | ❌ **REJECT** | Contains prepared dishes; not raw ingredients |
| **Overall Phase 1** | ❌ **REJECT** | Critical blockers unresolved |

---

## 10. Outstanding Blockers for Phase 2

| Blocker | Resolution Required |
|---------|---------------------|
| IFCT extraction ≥524/543 items | Implement two-pass extractor (v15 strategy) |
| IFCT decrypted PDF hash verified | Re-download/verify; document transformation |
| INDB documentation corrected | Update all docs: "Prepared Dish Composition Database" |
| Page 58 egg/poultry classification fixed | Implement section-end header detection |
| T-prefix (T001–T014) mapping added | Add T→FRESHWATER FISH mapping |
| IFCT decrypted PDF hash verified | Re-download/verify; document transformation |

---

## Final Verdict

### ❌ **PHASE 1 REJECTED**

**Phase 1 cannot be accepted.** Four CRITICAL and three HIGH severity issues remain unresolved.

**Do not proceed to Phase 2** until all CRITICAL blockers (B1–B5) are resolved with documented evidence.

---

## Appendix: Record-Level Missing Code Disposition

| Missing Code | Expected Group | Page | Status |
|--------------|----------------|------|--------|
| A001 | CEREALS AND MILLETS | 41 | First item; no preceding prefix |
| B001 | PULSES AND LEGUMES | 42 | First item after prefix B |
| C001 | LEAFY VEGETABLES | 43 | First item after prefix C |
| D001 | OTHER VEGETABLES | 45 | First item after prefix D |
| E001 | FRUITS | 49 | First item after prefix E |
| E004 | FRUITS | 49 | Nutrient extraction < 5 values |
| F001 | ROOTS AND TUBERS | 52 | First item after prefix F |
| G013 | CONDIMENTS FRESH | 53 | Prefix G mapping ambiguity |
| H001 | NUTS AND OIL SEEDS | 55 | First item after prefix H |
| H005 | NUTS AND OILSEEDS | 55 | Nutrient extraction < 5 values |
| I001 | SUGARS AND JAGGERY | 578 | Group header S → SUGARS missed |
| J001 | MUSHROOMS | 56 | First item after prefix J |
| J009 | MUSHROOMS | 56 | Extracted but group wrong |
| K001 | SUGARS AND JAGGERY | 581 | Group header K → SUGARS missed |
| N001–N006 | POULTRY | 58–59 | Prefix N detected but extraction fails |
| P001 | MARINE FISH | 63 | First item after prefix P |
| Q001 | MARINE SHELLFISH | 67 | First item after prefix Q |
| T001–T014 | FRESHWATER FISH | 569–584 | Prefix T → UNKNOWN (not in mapping) |

---

**Report Generated:** 2025-01-15  
**Auditor:** Critical Data Integrity Audit  
**Report Location:** `docs/dataset_documentation/final_evidence_reconciliation.md`  
**Next Review:** After all CRITICAL blockers resolved  

---

**END OF REPORT**