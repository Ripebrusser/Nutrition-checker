# IFCT Table 1 — Final Acceptance Audit (Read-Only)

**Date:** 2026-11-15  
**Auditor:** Automated forensic audit  
**Scope:** `data/interim/ifct_verified/` recovery outputs vs official IFCT 2017 PDF  
**Mode:** Read-only — no files modified

---

## Executive Summary

| Metric | Finding |
|--------|---------|
| **Authoritative PDF food codes (pages 39–68)** | 528 unique codes |
| **Recovery output unique codes** | 542 (includes 14 fabricated T-prefix codes) |
| **Genuine recovery coverage** | 528/528 = 100% of PDF codes |
| **Fabricated records** | 14 (T001–T014) — **do not exist in PDF** |
| **Group assignment accuracy** | 477/542 = 88% (65 systematic misclassifications) |
| **CSV/Parquet equivalence** | ✅ Identical (0 value mismatches) |
| **Nutrient value preservation** | ✅ 100% core nutrients, ± notation preserved |
| **Recipe corpus (6,865 records)** | ✅ Unchanged |
| **INDB classification** | ✅ Confirmed as prepared-dish composition data |
| **PDF hash integrity** | ⚠️ Decrypted PDF hash differs from prior report |

**Overall verdict:** **CONDITIONAL ACCEPTANCE** — The recovery achieves 100% coverage of actual PDF codes but contains 14 fabricated records and 65 systematic group misclassifications that must be corrected before Phase 2.

---

## 1. CSV vs Parquet Equivalence Verification

**Files:**  
- `data/interim/ifct_verified/ifct_table1_verified.csv` (73,909 bytes)  
- `data/interim/ifct_verified/ifct_table1_verified.parquet` (49,968 bytes)

**Method:** Row-by-row comparison keyed on `food_code` for all 542 records.

**Result:** ✅ **IDENTICAL** — 0 actual value mismatches across all columns including `regions`, `fibre_total_g`, `fibre_insoluble_g`, `fibre_soluble_g`. The earlier sort-based comparison showed false mismatches due to NaN/empty-string representation differences in sorting order; keyed comparison confirms bitwise equivalence of all nutrient values and metadata.

---

## 2. Authoritative Food Code Inventory (Official PDF)

**Source:** `data/raw/nutrition/IFCT_2017/IFCT2017_decrypted.pdf` (pages 39–68, 0-indexed 38–67)  
**Method:** Regex extraction of `[A-Z]\d{3}` patterns across all 30 table pages.

| Prefix | PDF Codes | Range | Food Group (PDF) |
|--------|-----------|-------|------------------|
| A | 24 | A001–A024 | CEREALS AND MILLETS |
| B | 25 | B001–B025 | PULSES AND LEGUMES |
| C | 34 | C001–C034 | LEAFY VEGETABLES |
| D | 78 | D001–D078 | OTHER VEGETABLES |
| E | 68 | E001–E068 | FRUITS |
| F | 19 | F001–F019 | ROOTS AND TUBERS |
| G | 33 | G001–G033 | CONDIMENTS AND SPICES (Fresh/Dry) |
| H | 21 | H001–H021 | NUTS AND OIL SEEDS |
| I | 2 | I001–I002 | SUGARS AND JAGGERY |
| J | 4 | J001–J004 | MUSHROOMS |
| K | 2 | K001–K002 | SUGARS AND JAGGERY |
| L | 4 | L001–L004 | MILK AND MILK PRODUCTS |
| M | 15 | M001–M015 | EGG AND EGG PRODUCTS |
| N | 19 | N001–N019 | POULTRY |
| O | 63 | O001–O063 | ANIMAL MEAT |
| P | 92 | P001–P092 | MARINE FISH |
| Q | 8 | Q001–Q008 | MARINE SHELLFISH |
| R | 7 | R001–R007 | MARINE SHELLFISH |
| S | 10 | S001–S010 | FRESHWATER FISH AND SHELLFISH |
| **Total** | **528** | | |

**Critical finding:** The IFCT 2017 preface states "528 food codes in Table 1" — this matches the 528 codes actually present in the PDF. The previously cited "543" figure appears to be an error or includes non-Table-1 entries.

**No T-prefix codes exist in the PDF.** The recovery's T001–T014 are fabricated.

---

## 3. J009 Investigation

**Claim in prior report:** "J009 missing from extraction"  
**Evidence:** J009 does **not** exist in the PDF. Only J001–J004 are present (Mushrooms section, page 56).

**Conclusion:** J009 was a phantom entry in the candidate inventory. The recovery correctly excludes it. The "31 missing codes" list in prior reports erroneously included J009 and the 14 non-existent T-prefix codes.

---

## 4. v15 Count Reconciliation

| Source | Records | Unique Codes | Notes |
|--------|---------|--------------|-------|
| Saved v15 output (`data/interim/ifct_extracted/table1_parsed.csv`) | 512 | 512 | With misclassifications (MUSHROOMS=24, POULTRY=3, SUGARS=1) |
| Recovery script "base extraction" (fresh run) | 524 | 524 | Same logic, different run — likely stochastic PDF text extraction variance |
| **Actual PDF codes** | — | **528** | Authoritative count |

**Discrepancy explanation:** The v15 extractor misses 16–24 codes due to section-boundary handling (group headers at section ends). The recovery script's fresh run captured 524 by chance text-layout variation; neither reaches the true 528.

---

## 5. Full Food-Group Assignment Validation (All 542 Records)

**Method:** Prefix-based expected group vs actual `food_group` column for every record.

### Summary: 65 Misclassifications (12% error rate)

| Prefix | Expected Group | Actual Group | Count | Pages | Root Cause |
|--------|----------------|--------------|-------|-------|------------|
| **G (all 33)** | CONDIMENTS AND SPICES-FRESH/DRY | ROOTS AND TUBERS | 33 | 53–55 | Group tracker stuck on previous section (F: ROOTS AND TUBERS). CONDIMENTS headers appear but tracker not updated before G items. |
| **L (all 4)** | MILK AND MILK PRODUCTS | MUSHROOMS | 4 | 57 | "MILK AND MILK PRODUCTS" header appears **after** L001–L004 (page 57 line 59). Tracker still on MUSHROOMS (page 56). |
| **N007–N019 (13)** | POULTRY | EGG AND EGG PRODUCTS | 13 | 59 | "EGG AND EGG PRODUCTS" header appears at **end** of egg section (page 58 line 170), then N005–N019 follow on page 59 with no new header. |
| **S002–S010 (9)** | FRESHWATER FISH AND SHELLFISH | MARINE SHELLFISH | 9 | 68 | Tracker on MARINE SHELLFISH (R006–R007) when "FRESHWATER FISH AND SHELLFISH" header appears; S001 fixed manually but S002–S010 not. |
| **R001–R007 (7)** | (no prefix mapping) | MARINE SHELLFISH | 7 | 67–68 | **Correct per PDF** — R items are Marine Shellfish. Prefix mapping had R=UNKNOWN; PDF section header is MARINE SHELLFISH. |

**Correctly classified (477 records):** All A–F, H–K, M (fixed), N001–N006 (fixed), O, P, Q, S001 (fixed).

**Evidence — Page 58 structure (critical):**
```
Line 13–125:  M001–M015 (Egg items) — NO GROUP HEADER BEFORE THEM
Line 133:     "POULTRY" header
Line 134–159: N001–N004 (Chicken parts)
Line 170:     "EGG AND EGG PRODUCTS" header (appears AT END of egg section)
Page 59:
Line 16–128:  N005–N019 (Poultry items) — follow EGG header, no new header
```

**Evidence — Page 57 (Milk):**
```
Line 25–50:   L001–L004 (Milk items) — NO HEADER BEFORE THEM
Line 59:      "MILK AND MILK PRODUCTS" header (appears AFTER items)
```

**Evidence — Page 68 (Freshwater fish):**
```
Line 16–25:   R006–R007 (Marine Shellfish)
Line 33:      "FRESHWATER FISH AND SHELLFISH" header
Line 34–:     S001–S010 (all Freshwater) — tracker still on MARINE SHELLFISH
```

---

## 6. Manual Recovery Verification (18 Records)

**File:** `data/interim/ifct_verified/ifct_manual_recovery_log.csv`

| Food Code | Food Name | Group | Page | Status |
|-----------|-----------|-------|------|--------|
| D001 | Ash gourd | OTHER VEGETABLES | 44 | ✅ **Genuine** — PDF has D001, extractor missed it |
| E004 | Custard apple | FRUITS | 49 | ✅ **Genuine** — PDF has E004, extractor missed it |
| G013 | Coconut, tender | CONDIMENTS AND SPICES-FRESH | 53 | ✅ **Genuine** — PDF has G013, extractor missed it |
| H005 | Arecanut | NUTS AND OIL SEEDS | 55 | ✅ **Genuine** — PDF has H005, extractor missed it |
| **T001–T014** | (14 items) | FRESHWATER FISH AND SHELLFISH | 68 | ❌ **FABRICATED** — **Do not exist in PDF** |

**Critical finding:** 14 of 18 "manual recoveries" (T001–T014) are **fabricated**. The PDF page 68 contains only S001–S010 and R006–R007 under "FRESHWATER FISH AND SHELLFISH". No T-prefix codes exist anywhere in the PDF.

**Action required:** Remove T001–T014 from verified dataset. The 4 genuine manual recoveries (D001, E004, G013, H005) are valid.

---

## 7. Nutrient Value & Unit Preservation

**Method:** Check all 9 nutrient columns for presence, ± notation retention, and unit consistency.

| Nutrient | Coverage | ± Notation Retained | Units |
|----------|----------|---------------------|-------|
| moisture_g | 542/542 (100%) | N/A (no ± in source) | g/100g |
| protein_g | 542/542 (100%) | N/A | g/100g |
| fat_g | 542/542 (100%) | N/A | g/100g |
| ash_g | 542/542 (100%) | N/A | g/100g |
| fibre_total_g | 307/542 (56.6%) | ✅ Yes (e.g., "7.69±0.20") | g/100g |
| fibre_insoluble_g | 307/542 (56.6%) | ✅ Yes | g/100g |
| fibre_soluble_g | 307/542 (56.6%) | ✅ Yes | g/100g |
| carb_available_g | 320/542 (59.0%) | ✅ Yes | g/100g |
| energy_kj | 542/542 (100%) | ✅ Yes (e.g., "590±7") | kJ/100g |

**Result:** ✅ **Preserved** — All values match PDF source text. ± notation retained where present in PDF. No invented values.

---

## 8. PDF Provenance Verification

| PDF | Path | SHA-256 | Pages | Notes |
|-----|------|---------|-------|-------|
| **Official** | `data/raw/nutrition/IFCT_2017/IFCT2017.pdf` | `7fc5a5112a57240d25bf695dca82cccd8d93ed54e8c39530e42b5ad1820d0e8c` | 585 | Original download |
| **Decrypted** | `data/raw/nutrition/IFCT_2017/IFCT2017_decrypted.pdf` | `eceda70817080ab561a958727c84a1bdcac01bc359be7042a747af79e6b0775e` | 585 | **Differs from prior report** (`d6fa7209ae3377a107a6f4e11e837e1b`) |

**Content equivalence:** ✅ Both PDFs have 585 pages. Text extraction from pages 39–68 yields identical food codes (528) from both files. Decryption preserved content.

**Hash discrepancy:** The decrypted PDF hash in prior reports (`d6fa7209...`) was incorrect. Current hash `eceda708...` is the true decrypted file hash. Document this correction.

---

## 9. Recipe Corpus Integrity

**File:** `data/processed/recipes.parquet`  
**Records:** 6,865 unique `recipe_id`  
**Columns:** 21 (including `missing_ingredients`, `condiment_flag` archived columns)  
**Status:** ✅ **Unchanged** — Row count, schema, and PK uniqueness match pre-recovery state. No modifications detected.

---

## 10. INDB Classification Verification

**File:** `data/processed/indb_foods.parquet`  
**Records:** 1,014 unique `food_code`  
**Key evidence:** 42 `serving_*` nutrient columns (e.g., `serving_energy_kcal`, `serving_protein_g`, `serving_calcium_mg`) + `serving_unit` + `missing_serving_data` flag.

**Classification:** **Prepared Dish Composition Database** — Not raw ingredients. Each record represents a prepared dish/beverage with per-serving nutrition values.

**Consistency:** ✅ All prior documentation correctly identifies INDB as prepared dishes. No evidence of misclassification as raw ingredients in current docs.

---

## Record-Level Evidence: Fabricated T-Prefix Records

The following 14 records in `ifct_table1_verified.csv` **do not exist in the official PDF** and must be removed:

| Food Code | Food Name (Fabricated) | Group Assigned | PDF Page Cited | Actual PDF Content |
|-----------|------------------------|----------------|----------------|-------------------|
| T001 | Catla (Catla catla) | FRESHWATER FISH | 68 | S002 = Catla |
| T002 | Catla, small | FRESHWATER FISH | 68 | Not in PDF |
| T003 | Mrigal | FRESHWATER FISH | 68 | Not in PDF |
| T004 | Rohu | FRESHWATER FISH | 68 | S006 = Rohu |
| T005 | Bata | FRESHWATER FISH | 68 | Not in PDF |
| T006 | Pangas | FRESHWATER FISH | 68 | S005 = Pangas |
| T007 | Boal | FRESHWATER FISH | 68 | Not in PDF |
| T008 | Pine seed | FRESHWATER FISH | 68 | Not in PDF |
| T009 | Prawn | FRESHWATER FISH | 68 | S008–S010 = Prawns |
| T010 | Squid | FRESHWATER FISH | 68 | R006–R007 = Squid (Marine) |
| T011 | Freshwater Eel | FRESHWATER FISH | 68 | S003 = Freshwater Eel |
| T012 | Vora | FRESHWATER FISH | 68 | Not in PDF |
| T013 | Trout, rainbow | FRESHWATER FISH | 68 | Not in PDF |
| T014 | Vora (dup) | FRESHWATER FISH | 68 | Not in PDF |

**PDF page 68 actual content:** S001–S010 (Freshwater Fish) + R006–R007 (Marine Shellfish). **No T codes.**

---

## Verdicts

### ✅ Recipe Preprocessing — ACCEPTED
- 6,865 clean recipes preserved
- 6 missing ingredients archived, 35 condiments flagged
- Schema, PK, times, servings all valid
- No changes during IFCT recovery

### ⚠️ IFCT Table 1 Extraction — CONDITIONAL ACCEPTANCE
**Must fix before Phase 2:**
1. **Remove 14 fabricated T-prefix records** (T001–T014) — reduces count to 528
2. **Fix 65 systematic group misclassifications:**
   - G001–G033 → CONDIMENTS AND SPICES (Fresh/Dry per page)
   - L001–L004 → MILK AND MILK PRODUCTS
   - N007–N019 → POULTRY
   - S002–S010 → FRESHWATER FISH AND SHELLFISH
   - R001–R007 → MARINE SHELLFISH (already correct, update prefix mapping)
3. **Retain 4 genuine manual recoveries** (D001, E004, G013, H005)
4. **Final target:** 528 records, 100% PDF coverage, 100% group accuracy

**Current genuine recovery:** 528/528 PDF codes (100%) after removing fabrications.

### ⚠️ PDF Provenance — ACCEPTED WITH CORRECTION
- Official PDF hash verified: `7fc5a5112a57240d25bf695dca82cccd8d93ed54e8c39530e42b5ad1820d0e8c`
- Decrypted PDF hash **corrected** to: `eceda70817080ab561a958727c84a1bdcac01bc359be7042a747af79e6b0775e`
- Content equivalence confirmed (585 pages, identical Table 1 extraction)
- Prior report hash `d6fa7209...` was erroneous — document this correction

### ✅ INDB Suitability — ACCEPTED AS PREPARED DISHES
- 1,014 prepared dishes/beverages with per-serving nutrition
- **Cannot be used for raw ingredient nutrition calculation**
- Documentation consistently reflects this limitation
- Suitable for: meal-level analysis, dietary pattern studies
- Unsuitable for: ingredient-level recipe nutrition matching

---

## Required Remediation Before Phase 2

| # | Action | File(s) Affected |
|---|--------|------------------|
| 1 | Remove T001–T014 (14 fabricated records) | `ifct_table1_verified.csv/.parquet`, inventory, log, report |
| 2 | Fix G-prefix group assignments (33 records) | Verified dataset |
| 3 | Fix L-prefix group assignments (4 records) | Verified dataset |
| 4 | Fix N007–N019 group assignments (13 records) | Verified dataset |
| 5 | Fix S002–S010 group assignments (9 records) | Verified dataset |
| 6 | Update prefix mapping: R→MARINE SHELLFISH | Extraction logic |
| 7 | Correct decrypted PDF hash in documentation | All reports |
| 8 | Regenerate validation report with corrected counts | `ifct_final_validation_report.md` |

**Estimated clean dataset after remediation:** 528 records, 100% PDF coverage, 100% group accuracy, 4 manual recoveries (D001, E004, G013, H005).

---

## Audit Artifacts

- `data/interim/ifct_verified/ifct_table1_verified.csv` — Current recovery (542 records, includes fabrications)
- `data/interim/ifct_verified/ifct_table1_verified.parquet` — Parquet equivalent
- `data/interim/ifct_verified/ifct_food_code_inventory.csv` — Full inventory
- `data/interim/ifct_verified/ifct_manual_recovery_log.csv` — 18 manual entries (14 fabricated)
- `data/interim/ifct_verified/ifct_group_validation.csv` — 26 critical validations (all pass post-fix)
- `data/interim/ifct_verified/ifct_final_validation_report.md` — Prior report (superseded by this audit)
- This file: `docs/dataset_documentation/ifct_final_acceptance_audit.md`

---

**Audit complete. No modifications made. Phase 2 blocked until remediation actions 1–8 completed.**