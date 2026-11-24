# Report content checklist

Deliverables in this folder:

1. `ML_Project_Final_Report.docx` — editable report (Word, 53 pages).
2. `ML_Project_Final_Report.pdf` — exported PDF of the same document (53 pages).
3. `Report_Content_Checklist.md` — this file.

The PDF was exported from the DOCX by Microsoft Word (fields updated before export), so the two
files are the same document. The table of contents and the lists of figures and tables were
generated from live Word fields and therefore carry the page numbers of this build.

---

## 1. Preliminary pages — complete

| Item | Status |
|---|---|
| Cover page | Complete; title, degree, department, session, three student slots |
| Certificate | Complete; signature and approval blocks left as placeholders |
| Declaration | Complete; unsigned by design |
| Acknowledgement | Complete draft; editable |
| Abstract | Complete (~330 words) with keywords |
| Table of contents | Complete; chapters, sections and references with page numbers |
| List of figures | Complete; 12 entries with page numbers |
| List of tables | Complete; 14 entries with page numbers |
| Abbreviations and acronyms | Complete; 20 entries |

## 2. Chapters — all eight present

| Chapter | Title | Status |
|---|---|---|
| 1 | Introduction (background, problem, motivation, objectives, scope, contributions) | Complete |
| 2 | Literature Review (food recommenders, content-based methods, ingredient representation, Indian composition data, personalised nutrition, limitations, research gap) | Complete |
| 3 | Dataset Description and Analysis (four resources, fields, cleaning, missing values, limitations) | Complete, 3 tables |
| 4 | Methodology (12 pipeline stages, 4 equations, 4 figures, 2 tables) | Complete |
| 5 | Machine Learning and Recommendation System (features, TF-IDF, similarity, ranking, constraints, baselines, clustering, protocol, 7 equations, 2 tables) | Complete |
| 6 | System Design and Implementation (architecture, frontend, backend, database, ML and nutrition modules, authentication, planning, pages, stack) | Complete, 1 figure, 3 tables |
| 7 | Results and Discussion (preprocessing, mapping, nutrition availability, recommendation, configuration defect, clustering, testing, discussion, limitations) | Complete, 5 figures, 4 tables |
| 8 | Conclusion and Future Scope (summary, what the results establish, what remains incomplete, future work, concluding remarks) | Complete |
| — | References | Complete, 15 entries, all cited in the text |

## 3. Figures (12) and tables (14)

Figures: 4.1 system architecture · 4.2 normalisation and parsing workflow · 4.3 matching and
approval funnel · 4.4 nutrition calculation and abstention · 4.5 personalisation and meal
planning · 5.1 recommendation architecture · 6.1 application architecture · 7.1 parsing
outcomes · 7.2 nutrition data coverage · 7.3 precision and recall by method · 7.4 diversity and
coverage · 7.5 clustering diagnostics.

Tables: 3.1 data resources · 3.2 recipe fields · 3.3 missing data · 4.1 parsing outcomes ·
4.2 IFCT matching statistics · 5.1 rankers under comparison · 5.2 evaluation metrics · 6.1 backend
routers · 6.2 application pages · 6.3 technology stack · 7.1 recommendation performance ·
7.2 clustering · 7.3 test suites · 7.4 end-to-end journeys.

Every figure and table has a numbered caption and is cited from the text.

## 4. Numbers verified against project artefacts

6,865 recipes (from 6,871 raw) · 75 cuisines / 10 courses / 20 diet labels · 90,862 parsed rows ·
13,049 ingredient names · parsing outcomes 54,903 / 29,980 / 1,673 / 4,306 (60.4 / 33.0 / 1.8 /
4.7 %) · 1,299 rows with a resolved mass (1.43 %) · 88.6 % preparation state unspecified ·
IFCT 528 foods, 18 groups, 9 nutrient fields · 222 foods missing fibre and carbohydrate (42.0 %) ·
180 foods with an edible-portion factor (34.1 %) · INDB 1,014 × 86 · 119,474 candidate pairs ·
63,244 lines without a candidate · 7,992 pending review units · 0 approved mappings ·
splits 4,783 / 1,025 / 1,025 over 63 cuisines (32 dropped) · P@5 0.128 / 0.904 / 0.548 / 0.996 ·
R@5 0.00059 / 0.01127 / 0.00459 / 0.01566 · Div@10 0.958 / 0.824 / 0.773 / 0.869 ·
Cov@20 0.254 / 0.225 / 0.220 / 0.234 · latency 110.4 / 390.0 / 208.1 / 180 ms ·
clustering five rows (silhouette 0.0388–0.0469, Davies–Bouldin 3.187–4.214) ·
362 tests, 354 passed, 7 pre-existing failures, 2 timeouts (97.8 %) · 7 journeys, 55 steps.

## 5. Deliberate placeholders (not invented)

- Institution name, city, department name on the cover and certificate.
- Student names and roll numbers (three students).
- Guide name, Head of Department, internal and external examiner names, dates.
- These are the only blanks. No signature, approval, clinical validation or deployment claim is
  fabricated anywhere in the report.

## 6. Known limitations stated in the report

Zero approved ingredient-to-IFCT mappings; nutrition engine abstains; 98.6 % of parsed rows
without a resolved mass; 42.0 % of IFCT foods missing fibre and carbohydrate; proxy relevance is
circular and permissive; 50-query sample is the first 50 test recipes; coverage computed over a
different population; four ranking configurations are numerically identical because the ranker
hard-codes its weights; no human evaluation; local deployment only; corpus has no licence.

## 7. Items that could not be verified or provided

| Item | Note |
|---|---|
| Application screenshots | None exist in the repository; none were fabricated. Chapter 6 describes pages from the implemented routes and components. |
| Phase 7 aggregate test count | The phase-7 table lists the Phase 1 suite twice, so the row sum exceeds the stated 362 total. The report presents the suite-level figures and notes the discrepancy. |
| Endpoint count | 41 route handlers counted directly from the router modules (37) plus the entry point (4). |
| Frontend page count | 15 page components counted in `frontend/src/pages`; the phase-9 summary's "12 pages" is stale. |
