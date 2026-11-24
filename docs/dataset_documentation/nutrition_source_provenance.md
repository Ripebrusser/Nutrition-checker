# Nutrition Data Source Provenance & Licensing

**Project:** AI for Nutrition & Diet Planning  
**Phase:** 2 — Raw Food Composition Data Acquisition and Verification  
**Date:** 2026-11-15

---

## 1. Source Inventory

| # | Source | Type | Access Method | Licence Status |
|---|--------|------|---------------|----------------|
| 1 | **IFCT 2017** (Indian Food Composition Tables) | Primary raw-food composition | Official PDF download from NIN | © ICMR-NIN; academic use permitted; redistribution requires permission |
| 2 | **INDB 2024.11** (Anuvaad) | Prepared dish composition | Local XLSX file | Academic use assumed; redistribution unclear |
| 3 | **USDA FoodData Central** | Supplementary composition | CSV download from USDA | Public domain (US Govt work) |
| 4 | **UK Food Composition Tables** | Referenced by INDB | Not acquired | Crown copyright; check OGL |
| 5 | **IFCT 2004** | Referenced by INDB | Not acquired | ICMR-NIN; similar terms to IFCT 2017 |

---

## 2. IFCT 2017 — Detailed Provenance

### 2.1 Official Publication
- **Title:** Indian Food Composition Tables 2017
- **Authors:** T. Longvah, R. Ananthan, K. Bhaskarachary, K. Venkaiah
- **Publisher:** National Institute of Nutrition (ICMR), Hyderabad
- **Year:** 2017
- **ISBN:** Not stated in PDF
- **Pages:** 585
- **Official URL:** https://www.nin.res.in/ebooks/IFCT2017.pdf

### 2.2 Copyright Notice (from PDF)
> Copyright © 2017 by National Institute of Nutrition  
> Indian Council of Medical Research  
> Department of Health Research  
> Ministry of Health and Family Welfare, Government of India  
> Jamai Osmania (PO), Hyderabad – 500 007, Telangana State, INDIA

> Citation of this book should be given as—  
> Longvah, T., Ananthan, R., Bhaskarachary, K. and Venkaiah, K. (2017). Indian Food Composition Tables 2017, National Institute of Nutrition, Indian Council of Medical Research, Hyderabad, Telangana, India.

### 2.3 Permissions Analysis

| Use Case | Permitted? | Basis |
|----------|------------|-------|
| Academic research (internal) | ✅ Yes | Government publication for public health |
| Local storage for research | ✅ Yes | Fair dealing / research exception |
| Academic publication (with citation) | ✅ Yes | Standard academic practice |
| Public GitHub repository (data files) | ❌ No / Unclear | Copyright notice prohibits reproduction without permission |
| Embedded in distributable application | ❌ No / Unclear | Commercial/distribution rights not granted |
| Sharing extracted CSV with collaborators | ⚠️ Case-by-case | Private sharing for research may be fair dealing |

### 2.4 Recommended Compliance Actions
1. **Do not commit** extracted IFCT data files to public Git repositories
2. **Add to .gitignore:** `data/interim/ifct_extracted/*.csv`, `data/processed/ifct_food_composition/`
3. **Document citation** in all outputs: "Source: Longvah et al. (2017), IFCT 2017, NIN/ICMR"
4. **Seek written permission** from NIN/ICMR if public redistribution is needed
5. **Consider** using only aggregated/derived statistics in public outputs, not raw tables

---

## 3. INDB 2024.11 (Anuvaad) — Provenance

### 3.1 Source Details
- **File:** `Anuvaad_INDB_2024.11.xlsx`
- **Source:** Anuvaad platform / ICMR-NIN INDB
- **Content:** 1,014 prepared dishes/beverages with per-100g and per-serving nutrients
- **Primary Sources Cited in File:** `asc_manual`, `bfp_manual`, `open_source_recipes`, `fct_2017`, `ifct_2017`, `usda`, `calculated`

### 3.2 Licence Status
- **No explicit licence** in the file or accompanying documentation
- **Anuvaad platform** (https://anuvaad.in) is an ICMR-NIN initiative
- **Assumption:** Academic/research use permitted as part of ICMR ecosystem
- **Redistribution:** Unknown — do not redistribute without confirmation

### 3.3 Relationship to IFCT
- INDB **references** IFCT 2017 as a source (`primarysource` = `ifct_2017` for some items)
- INDB contains **prepared dishes**, not raw ingredients
- INDB food codes (`ASC###`, `BFP###`, `OSR###`) are **not interchangeable** with IFCT codes (`A001`, `B001`, etc.)

---

## 4. USDA FoodData Central — Provenance

### 4.1 Source Details
- **Source:** USDA Agricultural Research Service
- **Files:** `food.csv`, `nutrient.csv`, `food_nutrient.csv`, `measure_unit.csv`, `food_portion.csv`
- **Download Date:** 2026-11-15 (from USDA FDC download portal)
- **Version:** FDC 2024 (latest at download time)

### 4.2 Licence
- **Public Domain** (US Government work, 17 USC § 105)
- **No copyright** — free to use, modify, redistribute
- **Citation:** "U.S. Department of Agriculture, Agricultural Research Service. FoodData Central, 2024."

### 4.3 Usage Constraints for This Project
- **Only for gap-filling** when Indian raw ingredient absent from IFCT
- **Manual mapping required** — no automatic name/code matching
- **Document every mapping** with confidence score
- **Verify units** — USDA uses same SI units but different food descriptors

---

## 5. NHANES 2019-2020 — Provenance

### 5.1 Source Details
- **Source:** CDC National Center for Health Statistics
- **Files:** BMX, DEMO, DIQ, DR1TOT, PAQ (XPT format)
- **Survey Cycle:** 2019-2020
- **Status:** **Excluded from core pipeline** — US population survey data

### 5.2 Licence
- **Public Domain** (CDC/US Government work)
- **No restrictions** on use or redistribution

---

## 6. Unofficial ifct2017 GitHub Repository

### 6.1 Source
- **URL:** https://github.com/nodef/ifct2017
- **Description:** Community-extracted structured version of IFCT 2017
- **Status:** **Unofficial** — not endorsed by NIN/ICMR

### 6.2 Usage Policy
- **Reference only** — may help identify missing food names or verify extraction
- **Do not use as primary source** — always verify against official PDF
- **Licence:** Unknown (check repository LICENSE file)

---

## 6.3 UK Food Composition Tables (McCance & Widdowson)

### Referenced by INDB as a source
- **Publisher:** Public Health England / Food Standards Agency
- **Licence:** Open Government Licence v3.0 (OGL) — permits reuse with attribution
- **Status:** Not acquired; only referenced by INDB

---

## 7. Summary: Permitted vs Restricted

| Source | Internal Research | Academic Publication | Public Redistribution | Commercial Use |
|--------|-------------------|----------------------|----------------------|----------------|
| IFCT 2017 | ✅ | ✅ (with citation) | ❌ (permission needed) | ❌ |
| INDB 2024.11 | ✅ (assumed) | ⚠️ (verify) | ❌ (verify) | ❌ |
| USDA FDC | ✅ | ✅ | ✅ | ✅ |
| NHANES | ✅ | ✅ | ✅ | ✅ |
| UK FCT | ✅ | ✅ | ✅ (OGL) | ✅ |
| ifct2017 (GitHub) | ⚠️ (verify only) | ❌ | ❌ | ❌ |

---

## 8. Project Compliance Checklist

- [x] IFCT 2017 PDF downloaded from official source
- [x] File hash recorded (MD5: `ef7664ce5d9ae114de6f34aafdf4ca9d`)
- [x] Copyright notice documented
- [x] Citation format established
- [x] Raw extracted data marked as **internal only** (not for public repo)
- [x] `.gitignore` updated for extracted data files
- [ ] Written permission request drafted for ICMR/NIN (if public release planned)
- [x] USDA FDC usage documented as gap-fill only
- [x] INDB usage documented as prepared-dish reference only
- [x] NHANES documented as excluded from core pipeline

---

## 9. Recommended Attribution for Outputs

### In Code/Documentation:
```
Nutrient data sourced from:
- Indian Food Composition Tables 2017 (Longvah et al., 2017), NIN/ICMR
- Anuvaad INDB 2024.11 (ICMR-NIN)
- USDA FoodData Central (USDA ARS) — gap-fill only
```

### In Publications:
> Nutrient composition data for Indian raw foods were obtained from the Indian Food Composition Tables 2017 (Longvah T, Ananthan R, Bhaskarachary K, Venkaiah K. Indian Food Composition Tables 2017. National Institute of Nutrition, Indian Council of Medical Research, Hyderabad, 2017). Prepared dish compositions were referenced from the Anuvaad Indian Nutrition Database 2024.11. Supplementary values for ingredients not covered in Indian databases were sourced from USDA FoodData Central (manual gap-fill with documented mappings).

---

*End of Provenance Document*