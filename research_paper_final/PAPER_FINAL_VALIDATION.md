# Final validation report

Deliverable directory: `research_paper_final/` (the original project tree is unmodified).

## 1. Deliverables

| File | Status |
|---|---|
| `IEEE_Final_Research_Paper.tex` | canonical source |
| `IEEE_Final_Research_Paper.pdf` | compiled output, 6 pages |
| `references.bib` | 15 entries, every one cited |
| `figures/` | `generate_figures.py`, 9 PNGs (600 dpi), `figure_data_summary.json` |
| `tables/` | `tab1_datasets.tex`, `tab2_preprocessing.tex`, `tab3_results.tex`, `tab4_clustering.tex` |
| `PAPER_EVIDENCE_AUDIT.md` | claim → artifact → value traceability |
| `PAPER_FINAL_VALIDATION.md` | this report |

## 2. Required counts

| Requirement | Target | Actual |
|---|---|---|
| Pages | exactly 6 | **6** |
| Authors | 6, 3 + 3 layout | **6** (Author One–Six, tabular 3 + 3) |
| References | exactly 15, all cited | **15** entries, **15** cited, **0** uncited |
| Numbered sections | 8 headings total | **6** `\section` + Abstract + References = **8** |
| Figures | 4 diagrams + graphs | **7**, all captioned and cited |
| Tables | 4 | **4**, all captioned and cited |
| Equations | consistent with the code | **11**, all render |

Sections present: Abstract, Introduction, Related Work, Dataset and Methodology,
Experimental Setup, Results and Discussion, Conclusion, References. Absent by design:
Acknowledgment, Problem Statement, Objectives, Literature Survey, System Design,
Future Work, standalone Limitations, Appendix.

Prose body (excluding captions, tables, equations, references): 2,878 words.
Distribution: Introduction 269, Related Work 260, remainder across Sections III–VI.

## 3. Compilation

- Toolchain: Tectonic 0.17.0 (XeTeX engine, BibTeX run automatically).
- Command: `tectonic IEEE_Final_Research_Paper.tex`
- Result: **success**, exit status 0.
- Warnings: **none** — no overfull/underfull box warnings, no undefined references
  (`??` count in the PDF text = 0), no missing citations, no missing figures.
- Fonts: TeXGyreTermesX / NewTX (IEEEtran defaults). No font size, margin or column
  width was changed to fit; the only layout adjustments are float placement fractions
  in the preamble (`\dbltopfraction`, `\topfraction`, `\textfraction`, `topnumber`,
  `dbltopnumber`) and `\footnotesize` inside table bodies.

## 4. Visual inspection

All six pages were rendered (95–100 dpi) and inspected:

- Title block: six authors in two rows of three, department/institution/city/country/email
  placeholders intact, no overlap with the abstract rule.
- Page 1: title, authors, abstract, index terms, Section I start; no orphan headings.
- Page 2: Tables I and II side by side at column tops; both fit inside the measure
  (Table I was rebuilt with a `p{3.0cm}` third column to stop over-wrapping).
- Page 3: Figs. 1 and 2 full width at top; Eq. (3) on one line; no overflow.
- Page 4: Table III, Eq. (11) split cleanly; columns end flush at the baseline.
- Page 5: Figs. 3, 4, 5 and Table IV interleaved with text; no float stranded from its
  citation.
- Page 6: Fig. 6, Conclusion, References; both columns run to the bottom margin.
- Every page's lowest text block is at y = 718.7 pt of a 792 pt page (bottom margin
  respected); no column ends early except where a float occupies its top.

## 5. Metrics verified against project artifacts

Verified and reproduced (details in `PAPER_EVIDENCE_AUDIT.md`): 6,865 recipes; 90,862
parsed rows; 13,049 names; parse split 54,903 / 29,980 / 1,673 / 4,306; 1,299 rows with
mass; 88.6 % preparation state missing; IFCT 528 / 18 / 9; 222 of 528 fibre+carb missing;
180 of 528 edible-portion factors; INDB 1,014 × 86; 119,474 candidate pairs; 63,244
unmatched; 0 approved mappings; splits 4,783 / 1,025 / 1,025 over 63 cuisines; 42 nutrition
tests; P@5 0.128 / 0.904 / 0.548 / 0.996; R@5 0.000593 / 0.011273 / 0.004591 / 0.015665;
Div@10 0.958 / 0.824 / 0.773 / 0.869; Cov@20 0.254 / 0.225 / 0.220 / 0.234; latency
110.4 / 390.0 / 208.1 / 180 ms; five clustering rows; 20 inspected queries, 47
cuisine-crossing items, 16 queries with generic terms.

## 6. Disclosed limitations of the paper (stated inside the paper)

1. **Proxy relevance is circular and permissive.** `ρ ≥ 0.3` is satisfied by metadata
   agreement alone (0.5), so P@5 ≈ 1 measures metadata agreement, not dietary usefulness.
2. **The composite's reliability term was never measured.** It is held at 1.0 for every
   method and cannot affect the ordering; the reported Φ is bookkeeping, not validated
   utility.
3. **Four weight configurations produced identical metrics** — a software defect (the
   weights are literals in `recommend()`), so no sensitivity claim is made.
4. **Queries are the first 50 test recipes**, not a random sample, and coverage is
   computed over the first 100 catalogue recipes rather than over the same 50 queries.
5. **No nutrition values are reported.** Zero approved IFCT mappings and 1.43 % mass
   coverage mean the engine returns `NO_MAPPED_INGREDIENTS`; abstention is the result.
6. **No human, user-study or clinical evaluation was performed**, and the corpus is
   scraped with no explicit licence.
7. **The `tfidf_only` configuration is a misnomer**: TF-IDF is fitted and used by the
   clustering study, but it is not an input to the deployed ranking score.

## 7. Deviations from the figure request

The request listed four diagrams (architecture, preprocessing pipeline, matching and
nutrition workflow, recommendation methodology) and graphs for model comparison,
diversity/coverage, parsing outcomes, nutrition coverage and clustering. To hold the hard
six-page limit without shrinking type or margins, the paper carries **seven** figures:

| Paper figure | Content |
|---|---|
| Fig. 1 | System architecture (composition and recommendation paths) |
| Fig. 2 | Ingredient parsing outcomes |
| Fig. 3 | Ingredient-to-IFCT matching and nutrition workflow |
| Fig. 4 | Method comparison: P@5, R@5, precision vs. cut-off |
| Fig. 5 | Diversity@10 and coverage@20 against the requirement |
| Fig. 6 | Clustering diagnostics vs. k |
| Fig. 7 | Nutrition coverage of the four engine inputs |

Not carried as separate diagrams, because they cost more than the page budget allowed and
their content is fully specified elsewhere: the **preprocessing pipeline** strip (stage
list in Section III-B plus Table II's outcome counts) and the **recommendation methodology**
strip (Eq. (4) scoring, Fig. 1 path B, and Table III). Adding either pushed the build to
seven pages in testing; both attempts were reverted. Their source PNGs remain in
`figures/` (`fig2_preprocessing.png`, `fig4_recommendation.png`) and can be reinstated as
full-width figures if a seventh page, or one longer paper, is acceptable. All other
requested graphs are present.

## 8. What was and was not checked

Checked: compilation (clean), page count, page geometry and bottom-margin usage on every
page, section/reference/float/equation consistency by automated scan of the source and
extracted PDF text, and a visual pass over all six rendered pages.

Not checked: no proofreading pass by a second reader, no IEEE PDF eXpress conformance
check, no validation of the nutrient values (there are none in the paper), and no
re-generation of the underlying experiments (the paper reports them as recorded).
