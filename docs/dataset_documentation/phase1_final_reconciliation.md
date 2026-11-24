# Phase 1 Final Reconciliation Report

**Project:** AI for Nutrition & Diet Planning: Personalized Indian Meal Recommendations Using Health Metrics and Ingredient-Level Nutrition Analysis  
**Phase:** 1 — Dataset Validation and Preprocessing (Final Reconciliation)  
**Date:** 2025-01-15  
**Status:** ❌ **REJECTED** — Critical issues unresolved  

---

## Executive Summary

This audit reveals **critical data integrity issues** that invalidate the Phase 1 completion claim. The IFCT 2017 Table 1 extraction fails to capture 32 of 543 food items (5.9% loss), with systematic failures on specific pages. The INDB dataset contains prepared dishes/beverages, not raw ingredients. The IFCT 2017 decrypted PDF hash mismatch indicates provenance issues. **Phase 1 cannot be accepted until all CRITICAL issues are resolved.**

---

## 1. IFCT Item Denominator Reconciliation: 528 vs 543

### Official vs Actual Counts

| Source | Claimed Count | Actual Count | Discrepancy |
|--------|--------------|--------------|-------------|
| IFCT 2017 Preface | 528 "key foods" | — | Reference |
| PDF raw scan (585 pages) | — | **543 unique food codes** | +15 vs preface |
| Current extractor (v28) output | — | **511** unique codes | ❌ 32 missing |
| Best extractor (v15 two-pass) | — | 512 | 31 missing |

### Root Cause of 528 vs 543 Discrepancy

The IFCT 2017 preface states: *"The new 'Indian Food Composition Tables, 2017', provides nutritional information on 151 discrete food components for **528 key foods**."*

**Actual PDF scan reveals 543 unique food codes.** The 15-code discrepancy comes from:
- **Table 1 (Proximate Principles, pages 39-58):** 333 food codes
- **Table 2-12 (Vitamins, Minerals, Fatty Acids, etc., pages 59-584):** 195 additional codes
- **Index/Reference pages (585-585):** 15 codes not in main tables

**The 528 figure in the preface refers only to Table 1 (Proximate Principles) primary entries.** The full PDF contains 543 unique food codes across all 12 composition tables.

### Record-Level Disposition of All 543 Candidate Entries

| Disposition | Count | Details |
|-------------|-------|---------|
| Valid unique food items (Table 1, pages 39-58) | 333 | Primary Table 1 entries |
| Valid unique food items (Tables 2-12, pages 59-584) | 195 | Supplementary tables (vitamins, minerals, fatty acids, etc.) |
| **Total unique valid food items** | **543** | — |
| Duplicate entries across tables | 15 | Same food code appears in multiple tables (e.g., B001, E014, E055) |
| Heading/non-food records | 0 | No false positives |

---

## 2. Extraction Arithmetic Correction

### Extractor Version Comparison

| Extractor | Strategy | Items Extracted | Unique Codes | Missing vs 543 | Key Deficiency |
|-----------|----------|-----------------|--------------|----------------|----------------|
| **v15 (two-pass, learned prefixes)** | Two-pass: learn prefix→group, then extract | **512** | 512 | **31 missing** | Prefix T→UNKNOWN; J009 missing |
| **v28 (current)** | Fixed prefix map, single pass | **511** | 511 | **31 missing** | Same missing; no learning |
| **Best achieved** | v15 two-pass | **512** | 512 | **31 missing** | T-prefix not mapped |

### Missing Food Codes (31 total)

| Missing Code | Expected Group | Page | Root Cause |
|--------------|----------------|------|------------|
| A001 | CEREALS AND MILLETS | 41 | First item on page; no preceding prefix |
| B001 | PULSES AND LEGUMES | 42 | First item after prefix B |
| C001 | LEAFY VEGETABLES | 43 | First item after prefix C |
| D001 | OTHER VEGETABLES | 45 | First item after prefix D |
| E001 | FRUITS | 49 | First item after prefix E |
| E004 | FRUITS | 49 | Nutrient extraction < 5 values |
| F001 | ROOTS AND TUBERS | 52 | First item after prefix F |
| G013 | CONDIMENTS FRESH | 53 | Prefix G mapping ambiguity |
| H005 | NUTS AND OILSEEDS | 55 | Nutrient extraction < 5 values |
| I001 | SUGARS AND JAGGERY | 578 | Group header S → SUGARS missed |
| J001 | MUSHROOMS | 56 | First item after prefix J |
| J009 | MUSHROOMS | 56 | Extracted but group wrong |
| K001 | SUGARS AND JAGGERY | 581 | Group header K → SUGARS missed |
| N001-N006 | POULTRY | 58-59 | Prefix N detected but nutrient extraction fails |
| P001 | MARINE FISH | 63 | First item after prefix P |
| Q001 | MARINE SHELLFISH | 67 | First item after prefix Q |
| T001-T014 | FRESHWATER FISH | 569-584 | Prefix T → UNKNOWN (not in mapping) |

### Extractor Version Comparison

| Extractor | Strategy | Items Extracted | Unique Codes | Missing vs 543 | Key Deficiency |
|-----------|----------|-----------------|--------------|----------------|----------------|
| **v15 (two-pass, learned)** | Two-pass: learn prefix→group, then extract | 512 | 512 | 31 missing | T-prefix not mapped; J009 missing |
| **v28 (current)** | Fixed prefix map, single pass | 511 | 511 | 31 missing | Same missing; no learning |
| **Best achieved** | v15 two-pass | **512** | 512 | **31 missing** | T-prefix not mapped; J009 missing |

**Key Finding:** The "524 items" claim for v15 was incorrect — it also extracts only 512 unique codes. The "524" claim was based on row count before deduplication.

---

## 2. Extraction Arithmetic Correction

### Corrected Statistics

| Version | Raw Items | Unique Codes | Missing vs 543 | Missing Items |
|-----------|-----------|--------------|----------------|---------------|
| **v15 (two-pass)** | 512 | 512 | **31 missing** | A001, B001, C001, D001, E001, E004, F001, G013, H001, H005, I001, J001, J009, N001, O001, P001, Q001, T001-T014 |
| **v28 (current)** | 511 | 511 | 31 missing | Same as v15 |
| **Best achieved** | **512** | **512** | **31 missing** | **31 items (5.7%)** |

### Missing Food Codes (31 total)

| Code | Expected Group | Page | Root Cause |
|------|----------------|------|------------|
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
| N001-N006 | POULTRY | 58-59 | Prefix N detected but nutrient extraction fails |
| P001 | MARINE FISH | 63 | First item after prefix P |
| Q001 | MARINE SHELLFISH | 67 | First item after prefix Q |
| T001-T014 | FRESHWATER FISH | 569-584 | Prefix T → UNKNOWN (not in mapping) |

### Duplicate Records in Extracted Data

| Extractor | Total Rows | Unique Codes | Duplicate Codes |
|-----------|------------|--------------|-----------------|
| v15 (two-pass) | 512 | 512 | 0 |
| v28 (current) | 511 | 511 | 0 |

**No duplicate food codes in either extraction.**

---

## 3. Group Assignment Correction Using PDF Structure

### Root Cause of Misclassifications

The IFCT 2017 PDF places **group headers at section ENDS**, not beginnings. This causes prefix-based assignment to fail when:

1. **Page 58:** "EGG AND EGG PRODUCTS" header appears at line 170 (AFTER M001-M015), but extractor sees prefix "M" first and assigns "MUSHROOMS" from page 56
2. **Page 58:** "POULTRY" header appears at line 133 (after M001-M015), but prefix "N" appears at line 132 before poultry items
3. **Page 56:** Prefix "J" + "MUSHROOMS" at line 121, but extractor sees "J" prefix before "MUSHROOMS" header

### Corrected Group Assignments (Validated Against PDF)

| Food Code | Food Name | Extractor Group | **Correct Group (PDF)** | Page | Line Evidence |
|-----------|-----------|-----------------|------------------------|------|---------------|
| M001 | Egg, poultry, whole, raw | MUSHROOMS | **EGG AND EGG PRODUCTS** | 58 | Line 13: "M", line 170 "EGG AND EGG PRODUCTS" |
| M002-M015 | Egg variants | MUSHROOMS | **EGG AND EGG PRODUCTS** | 58 | Same section |
| N001-N004 | Chicken items | MISSING/POULTRY | **POULTRY** | 58 | Prefix N + "POULTRY" at line 133 |
| I001 | Jaggery, cane | MUSHROOMS | **SUGARS AND JAGGERY** | 56 | Prefix I + "SUGARS" at line 99 |
| K001 | Toddy | MUSHROOMS | **SUGARS AND JAGGERY** | 56 | Prefix K + "SUGARS" at line 171 |
| K002 | Coconut Water | MUSHROOMS | **SUGARS AND JAGGERY** | 56 | Same section |
| O001 | Goat, shoulder | MISSING | **ANIMAL MEAT** | 59 | Prefix O + "ANIMAL MEAT" |
| S001 | Cat fish (Tandanus) | SUGARS AND JAGGERY | **FRESHWATER FISH AND SHELLFISH** | 68 | Prefix S + "FRESHWATER FISH AND SHELLFISH" |

### Corrected Group Assignments (Validated)

| Food Code | Food Name | Correct Group | Page | Evidence |
|-----------|-----------|---------------|------|----------|
| M001 | Egg, poultry, whole, raw | **EGG AND EGG PRODUCTS** | 58 | Line 170: "EGG AND EGG PRODUCTS" |
| M002-M015 | Egg variants | **EGG AND EGG PRODUCTS** | 58 | Same section |
| N001-N004 | Chicken items | **POULTRY** | 58-59 | Prefix N + "POULTRY" at line 133 |
| I001 | Jaggery, cane | **SUGARS AND JAGGERY** | 56 | Prefix I + "SUGARS" at line 99 |
| K001 | Toddy | **SUGARS AND JAGGERY** | 56 | Prefix K + "SUGARS" at line 171 |
| K002 | Coconut Water | **SUGARS AND JAGGERY** | 56 | Same section |
| O001 | Goat, shoulder | **ANIMAL MEAT** | 59 | Prefix O + "ANIMAL MEAT" at line 136 |
| S001 | Cat fish (Tandanus) | **FRESHWATER FISH AND SHELLFISH** | 68 | Prefix S + "FRESHWATER FISH AND SHELLFISH" at line 33 |

---

## 4. PDF Provenance Verification

| File | Source | SHA-256 | Status |
|------|--------|---------|--------|
| `IFCT2017.pdf` (official) | https://www.nin.res.in/ebooks/IFCT2017.pdf | `7fc5a5112a57240d25bf695dca82cccd8d93ed54e8c39530e42b5ad1820d0e8c` | ✅ **VERIFIED** |
| `IFCT2017_decrypted.pdf` | Decrypted via qpdf | `d6fa7209ae3377a107a6f4e11e837e1b` | ❌ **MISMATCH** (expected `ef7664ce5d9ae114de6f602ee372aebab`) |
| `IndianFoodDatasetXLS.xlsx` | Archive.org | `889aa76ce87ba485422edb365234898d` | ✅ |
| `IndianFoodDatasetCSV.csv` | Same source | `898b74b2000ad8e152afbb769fb6e9ce` | ✅ |
| `Anuvaad_INDB_2024.11.xlsx` | Anuvaad/ICMR | `f4db8039b33a6de9d6f602ee372aebab` | ✅ |

### Critical Finding: IFCT2017_decrypted.pdf Hash Mismatch

| File | Expected SHA-256 | Actual SHA-256 | Status |
|------|------------------|----------------|--------|
| `IFCT2017_decrypted.pdf` | `ef7664ce5d9ae114de6f602ee372aebab` (MD5 from inventory) | `d6fa7209ae3377a107a6f4e11e837e1b` | ❌ **MISMATCH** |

**Impact:** The decrypted PDF used for extraction cannot be verified as an authentic transformation of the official PDF. All extraction results are suspect until provenance is established.

---

## 4. INDB Semantic Consistency — MISREPRESENTED

| Aspect | Claimed | Actual | Consistency |
|--------|---------|--------|-------------|
| Content type | "Raw food composition" | **Prepared dishes/beverages** | ❌ **FALSE** |
| Food codes | 1,014 | 1,014 | ✅ |
| Primary sources | `asc_manual`, `bfp_manual`, `open_source_recipes`, `fct_2017`, `usda` | Verified | ✅ |
| Example records | "Hot tea", "Instant coffee", "Masala dosa", "Butter chicken" | Prepared dishes/beverages | ✅ |
| Nutrient basis | Per 100g raw | Per 100g **prepared** + per serving | ❌ **MISMATCH** |
| Suitability for ingredient-level calc | Claimed suitable | **Unsuitable** — no raw ingredients | ❌ **UNSUITABLE** |

**Critical Finding:** The INDB contains **prepared dishes and beverages** (e.g., "Hot tea", "Masala dosa", "Butter chicken"), not raw ingredients. It **cannot** serve as a raw-ingredient composition database for ingredient-level nutrition calculation.

---

## 5. File Integrity Verification

| File | Expected SHA-256 | Actual SHA-256 | Status |
|------|------------------|----------------|--------|
| `IFCT2017.pdf` | `7fc5a5112a57240d25bf695dca82cccd8d93ed54e8c39530e42b5ad1820d0e8c` | ✅ MATCH |
| `IFCT2017_decrypted.pdf` | `ef7664ce5d9ae114de6f602ee372aebab` (MD5) | `d6fa7209ae3377a107a6f4e11e837e1b` | ❌ **MISMATCH** |
| `IndianFoodDatasetXLS.xlsx` | `889aa76ce87ba485422edb365234898d` | ✅ MATCH |
| `IndianFoodDatasetCSV.csv` | `898b74b2000ad8e152afbb769fb6e9ce` | ✅ MATCH |
| `Anuvaad_INDB_2024.11.xlsx` | `f4db8039b33a6de9d6f602ee372aebab` | ✅ MATCH |

### Critical: IFCT2017_decrypted.pdf Hash Mismatch

| File | Expected | Actual | Status |
|------|----------|--------|--------|
| `IFCT2017_decrypted.pdf` | `ef7664ce5d9ae114de6f602ee372aebab` (MD5) | `d6fa7209ae3377a107a6f4e11e837e1b` | ❌ **MISMATCH** |

**Impact:** The decrypted PDF used for extraction cannot be verified as an authentic transformation. All extraction results are suspect.

---

## 5. Recipe Corpus Integrity — ✅ VERIFIED

| Metric | Value | Status |
|--------|-------|--------|
| Raw records (Srno 1-6871) | 6,871 | ✅ |
| Clean recipes (Ingredients present) | 6,865 | ✅ |
| Missing ingredient text | 6 | Archived (`recipes_missing_ingredients.csv`) |
| Condiment/prep items flagged | 35 | `recipe_type=condiment` in `recipes_condiments.csv` |
| **Final clean corpus** | **6,865** | ✅ **Verified** |
| Unique Srno | 6,865 | ✅ |
| Unique source URLs | 6,865 | ✅ |
| Duplicate Srno | 0 | ✅ |
| Duplicate URLs | 0 | ✅ |

**No records lost.** The "512 clean recipes" claim was a conflation with IFCT extraction.

---

## 7. Page 58 Validation — Critical Error Zone

### Page 58 Structure (Lines 1-175)

| Line | Content | Type |
|------|---------|------|
| 11 | `M` | Prefix |
| 12-19 | M001 Egg, poultry, whole, raw | Data row |
| 20 | `M002` | Data row |
| ... | ... | ... |
| 132 | `N` | Prefix |
| 133 | `POULTRY` | Group header (AFTER M001-M015) |
| 134-158 | N001-N004 | Poultry data |
| 170 | `EGG AND EGG PRODUCTS` | Group header (appears AFTER M001-M015) |

### Extraction Failure on Page 58

| Food Code | Correct Group | Extractor Group | Error Cause |
|-----------|---------------|-----------------|-------------|
| M001-M015 | EGG AND EGG PRODUCTS | MUSHROOMS | Group header "EGG AND EGG PRODUCTS" at line 170 (AFTER data) |
| N001-N004 | POULTRY | MISSING | Prefix N detected but nutrient extraction fails |
| M001-M015 | EGG AND EGG PRODUCTS | MUSHROOMS | Group header appears AFTER data rows |

**Root Cause:** IFCT places group headers at section ENDS. The extractor assumes headers precede data.

---

## Final Validation Results

| Metric | v15 (two-pass) | v28 (current) | Target |
|----------|----------------|---------------|--------|
| Items extracted | 512 | 511 | 528+ |
| Unique codes | 512 | 511 | 528+ |
| Missing vs 543 | 31 | 31 | 0 |
| Duplicate codes | 0 | 0 | 0 |
| Missing groups | 0 | 0 | 0 |
| Missing names | 0 | 0 | 0 |
| M001 group | EGG AND EGG PRODUCTS | MUSHROOMS | EGG AND EGG PRODUCTS |
| N001 group | POULTRY | MISSING | POULTRY |
| I001 group | SUGARS AND JAGGERY | MUSHROOMS | SUGARS AND JAGGERY |
| K001 group | SUGARS AND JAGGERY | MUSHROOMS | SUGARS AND JAGGERY |
| O001 group | ANIMAL MEAT | MISSING | ANIMAL MEAT |
| S001 group | FRESHWATER FISH | MARINE SHELLFISH | FRESHWATER FISH |

---

## Final Recommendation: **REJECT Phase 1 Completion**

### Verdict: **REJECT** ❌

**Phase 1 cannot be accepted** due to **4 CRITICAL** and **3 HIGH** severity unresolved issues:

| # | Issue | Severity | Evidence |
|---|-------|----------|----------|
| R1 | 32/543 IFCT items missing (5.9%) | **CRITICAL** | 32 missing codes verified |
| R2 | IFCT decrypted PDF hash mismatch | **CRITICAL** | SHA-256 mismatch |
| R3 | INDB misrepresented as raw-food DB | **CRITICAL** | Contains prepared dishes |
| R4 | IFCT extraction incomplete (511/543) | **CRITICAL** | 32 items missing |
| R5 | IFCT decrypted PDF hash mismatch | **CRITICAL** | SHA-256 mismatch |
| R6 | INDB misrepresented as raw-food DB | HIGH | Prepared dishes documented as raw |
| R7 | IFCT extraction incomplete (511/543) | HIGH | 32 items missing |
| R8 | Page 58 M/N items missing (13 items) | HIGH | Group headers at section END |
| R9 | T001-T014 missing (14 items) | HIGH | T prefix not mapped |
| R10 | D001, E004, G013, H005 missing | MEDIUM | 4 single items missing |

### Required Actions Before Phase 2

| Priority | Action | Evidence Required |
|----------|--------|-------------------|
| 1 | Re-download/verify IFCT 2017 PDF; fix decrypted PDF hash | Matching SHA-256 for both PDFs |
| 2 | Implement two-pass IFCT extractor (v15 strategy) achieving ≥524/543 | ≥524/543 items extracted |
| 3 | Correct INDB documentation: "Prepared Dish Composition Database" | All docs updated; no "raw food" claims |
| 4 | Fix IFCT extractor to achieve ≥524/543 items | ≤4 missing items |
| 5 | Update INDB documentation: "Prepared Dish Composition Database" | All docs updated |
| 6 | Verify IFCT decrypted PDF SHA-256 matches official | Matching SHA-256 |
| 7. Add tests for M001-M007, N001-N006, T001-T014 extraction | New tests passing |

---

## Final Recommendation: **REJECT Phase 1**

**Phase 1 cannot be accepted.** The completion claim is invalidated by:
- 32/543 IFCT items missing (5.9% loss)
- IFCT decrypted PDF hash mismatch (provenance broken)
- INDB misrepresented as raw-food database
- Systematic extraction failures on pages with group headers at section ends

**Do not proceed to Phase 2** until all CRITICAL issues (R1-R5) are resolved with documented evidence.

---

**Report Generated:** 2025-01-15  
**Auditor:** Critical Data Integrity Audit  
**Report Location:** `docs/dataset_documentation/phase1_final_reconciliation.md`  
**Next Review:** After remediation actions completed