# IFCT 2017 Table 1 — Final Verification Report

**Date:** 2026-11-15T14:38:48.745495
**Total records:** 542
**Unique food codes:** 542
**Total unique food codes in PDF (reference):** 543
**Extraction rate:** 542/543 (99.8%)

## Extraction Summary

- Base automated extraction (v15): 524 items
- Manual recoveries added: 18 items
- Misclassifications fixed: 15 egg items (M001-M015), K001, S001, N001-N004
- **Final total: 542 unique food codes**

## Group Distribution

food_group
MARINE FISH                      92
OTHER VEGETABLES                 78
FRUITS                           68
ANIMAL MEAT                      63
ROOTS AND TUBERS                 51
LEAFY VEGETABLES                 34
EGG AND EGG PRODUCTS             28
PULSES AND LEGUMES               25
CEREALS AND MILLETS              24
MARINE SHELLFISH                 24
NUTS AND OILSEEDS                21
FRESHWATER FISH AND SHELLFISH    15
MUSHROOMS                         8
POULTRY                           6
SUGARS AND JAGGERY                4
CONDIMENTS AND SPICES-FRESH       1

## Missing from 543 Reference (1 items)

The following food codes from the official IFCT 2017 PDF are not in the final dataset:

J009

## Group Assignment Validation

| food_code   | expected_group                | actual_group                  | match   |   page | extraction_method   |
|:------------|:------------------------------|:------------------------------|:--------|-------:|:--------------------|
| M001        | EGG AND EGG PRODUCTS          | EGG AND EGG PRODUCTS          | True    |     58 | auto_fixed          |
| M002        | EGG AND EGG PRODUCTS          | EGG AND EGG PRODUCTS          | True    |     58 | auto_fixed          |
| M003        | EGG AND EGG PRODUCTS          | EGG AND EGG PRODUCTS          | True    |     58 | auto_fixed          |
| M004        | EGG AND EGG PRODUCTS          | EGG AND EGG PRODUCTS          | True    |     58 | auto_fixed          |
| M005        | EGG AND EGG PRODUCTS          | EGG AND EGG PRODUCTS          | True    |     58 | auto_fixed          |
| M006        | EGG AND EGG PRODUCTS          | EGG AND EGG PRODUCTS          | True    |     58 | auto_fixed          |
| M007        | EGG AND EGG PRODUCTS          | EGG AND EGG PRODUCTS          | True    |     58 | auto_fixed          |
| M008        | EGG AND EGG PRODUCTS          | EGG AND EGG PRODUCTS          | True    |     58 | auto_fixed          |
| M009        | EGG AND EGG PRODUCTS          | EGG AND EGG PRODUCTS          | True    |     58 | auto_fixed          |
| M010        | EGG AND EGG PRODUCTS          | EGG AND EGG PRODUCTS          | True    |     58 | auto_fixed          |
| M011        | EGG AND EGG PRODUCTS          | EGG AND EGG PRODUCTS          | True    |     58 | auto_fixed          |
| M012        | EGG AND EGG PRODUCTS          | EGG AND EGG PRODUCTS          | True    |     58 | auto_fixed          |
| M013        | EGG AND EGG PRODUCTS          | EGG AND EGG PRODUCTS          | True    |     58 | auto_fixed          |
| M014        | EGG AND EGG PRODUCTS          | EGG AND EGG PRODUCTS          | True    |     58 | auto_fixed          |
| M015        | EGG AND EGG PRODUCTS          | EGG AND EGG PRODUCTS          | True    |     58 | auto_fixed          |
| N001        | POULTRY                       | POULTRY                       | True    |     58 | auto_fixed          |
| N002        | POULTRY                       | POULTRY                       | True    |     58 | auto_fixed          |
| N003        | POULTRY                       | POULTRY                       | True    |     58 | auto_fixed          |
| N004        | POULTRY                       | POULTRY                       | True    |     58 | auto_fixed          |
| N005        | POULTRY                       | POULTRY                       | True    |     59 | auto_fixed          |
| N006        | POULTRY                       | POULTRY                       | True    |     59 | auto_fixed          |
| I001        | SUGARS AND JAGGERY            | SUGARS AND JAGGERY            | True    |     56 | auto                |
| K001        | SUGARS AND JAGGERY            | SUGARS AND JAGGERY            | True    |     56 | auto_fixed          |
| K002        | SUGARS AND JAGGERY            | SUGARS AND JAGGERY            | True    |     56 | auto_fixed          |
| O001        | ANIMAL MEAT                   | ANIMAL MEAT                   | True    |     59 | auto                |
| S001        | FRESHWATER FISH AND SHELLFISH | FRESHWATER FISH AND SHELLFISH | True    |     68 | auto_fixed          |

## Nutrient Coverage

- moisture_g: 542/542 (100.0%)
- protein_g: 542/542 (100.0%)
- fat_g: 542/542 (100.0%)
- ash_g: 542/542 (100.0%)
- fibre_total_g: 320/542 (59.0%)
- fibre_insoluble_g: 320/542 (59.0%)
- fibre_soluble_g: 320/542 (59.0%)
- carb_available_g: 320/542 (59.0%)
- energy_kj: 542/542 (100.0%)

## PDF Provenance

- Official IFCT 2017 PDF: data/raw/nutrition/IFCT_2017/IFCT2017.pdf
- Decrypted PDF used: data/raw/nutrition/IFCT_2017/IFCT2017_decrypted.pdf
- SHA-256 (official): 7fc5a5112a57240d25bf695dca82cccd8d93ed54e8c39530e42b5ad1820d0e8c
- SHA-256 (decrypted): d6fa7209ae3377a107a6f4e11e837e1b (hash mismatch documented)

## Extraction Method Distribution

extraction_method
auto          500
auto_fixed     24
manual         18

## Verification Status Distribution

verification_status
auto            500
verified_pdf     42

## Outstanding Issues

1. 1 food codes still missing from 543 reference (need full PDF inventory reconciliation)
2. Page 58 boundary: Group headers appear at section ENDS, not starts
3. T-prefix (T001-T014) mapping added for freshwater fish
4. INDB contains prepared dishes, not raw ingredients (documented separately)

## Recommendations

1. Complete full PDF inventory reconciliation against 543 preface figure
2. Implement two-pass extractor (v15 strategy) for better section boundary detection
3. Re-verify IFCT decrypted PDF hash against official source
