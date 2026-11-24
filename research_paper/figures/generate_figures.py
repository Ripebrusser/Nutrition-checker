#!/usr/bin/env python3
"""Regenerate every figure in the paper from the authoritative project artifacts.

Sources (read-only):
  reports/phase5/experiments/results/baseline_experiments.json
  reports/phase5/experiments/results/content_based_experiments.json
  data/interim/phase2/parsed_recipe_ingredients.parquet   (parse status counts)
  data/interim/ifct_final_candidate/ifct_table1_candidate.parquet

Run:  py research_paper/figures/generate_figures.py
"""

import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "DejaVu Serif"],
    "font.size": 7,
    "axes.labelsize": 7,
    "axes.titlesize": 7.5,
    "xtick.labelsize": 6.5,
    "ytick.labelsize": 6.5,
    "legend.fontsize": 6,
    "axes.linewidth": 0.6,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "savefig.dpi": 600,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.02,
    "pdf.fonttype": 42,
})

GREY = "#5a5a5a"
BLUE = "#2b6cb0"
ORANGE = "#c05621"
GREEN = "#2f7d32"
RED = "#b02318"


def load(name):
    with open(os.path.join(ROOT, "reports/phase5/experiments/results", name)) as fh:
        return json.load(fh)


base = load("baseline_experiments.json")
content = load("content_based_experiments.json")

METHODS = ["Random", "Cuisine match", "Jaccard", "TF-IDF"]
P5 = [base["random"]["metrics"]["precision@5"]["mean"],
      base["cuisine_match"]["metrics"]["precision@5"]["mean"],
      base["jaccard"]["metrics"]["precision@5"]["mean"],
      content["tfidf_only"]["metrics"]["precision@5"]["mean"]]
R5 = [base["random"]["metrics"]["recall@5"]["mean"],
      base["cuisine_match"]["metrics"]["recall@5"]["mean"],
      base["jaccard"]["metrics"]["recall@5"]["mean"],
      content["tfidf_only"]["metrics"]["recall@5"]["mean"]]
DIV = [base["random"]["metrics"]["diversity"]["mean"],
       base["cuisine_match"]["metrics"]["diversity"]["mean"],
       base["jaccard"]["metrics"]["diversity"]["mean"],
       content["tfidf_only"]["metrics"]["diversity"]["mean"]]
COV = [base["random"]["metrics"]["coverage"],
       base["cuisine_match"]["metrics"]["coverage"],
       base["jaccard"]["metrics"]["coverage"],
       content["tfidf_only"]["metrics"]["coverage"]]
LAT = [base["random"]["time_seconds"] / 50 * 1000,
       base["cuisine_match"]["time_seconds"] / 50 * 1000,
       base["jaccard"]["time_seconds"] / 50 * 1000,
       180.0]  # TF-IDF per-query latency as reported in the Phase 5.3 correction

P_AT_K = {
    "Random": [base["random"]["metrics"][f"precision@{k}"]["mean"] for k in (5, 10, 20)],
    "Cuisine match": [base["cuisine_match"]["metrics"][f"precision@{k}"]["mean"] for k in (5, 10, 20)],
    "Jaccard": [base["jaccard"]["metrics"][f"precision@{k}"]["mean"] for k in (5, 10, 20)],
    "TF-IDF": [content["tfidf_only"]["metrics"][f"precision@{k}"]["mean"] for k in (5, 10, 20)],
}


def save(fig, name):
    path = os.path.join(HERE, name)
    fig.savefig(path)
    plt.close(fig)
    print("wrote", path)


# ----------------------------------------------------------------------
# Fig. 1  System architecture (schematic; box contents are paper facts)
# ----------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(3.5, 3.55))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")


def box(x, y, w, h, text, fs=5.9, fc="#f2f2f2"):
    ax.add_patch(Rectangle((x, y), w, h, facecolor=fc, edgecolor="#333333", linewidth=0.6))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, linespacing=1.35)


def arrow(x1, y1, x2, y2, style="-|>", ls="-", color="#333333"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style,
                                 mutation_scale=7, linewidth=0.6, color=color,
                                 linestyle=ls, shrinkA=0, shrinkB=0))


# main column
mx, mw = 0.03, 0.585
box(mx, 0.855, mw, 0.115, "Recipe corpus\n(IndianFoodDatasetX: 6,865 recipes)", fs=6)
box(mx, 0.665, mw, 0.145, "Ingredient normalisation and\nquantity parsing\n(90,862 records; 13,049 names)")
box(mx, 0.475, mw, 0.145, "Ingredient-to-IFCT candidate\nmatching (119,474 candidate pairs)")
box(mx, 0.285, mw, 0.145, "Human review / approval gate\n(0 approved mappings)")
box(mx, 0.095, mw, 0.145, "TF-IDF + metadata features\n(2,000 terms) -> ranking with\ndietary filters and targets", fs=5.7)

for y0, y1 in [(0.855, 0.810), (0.665, 0.620), (0.475, 0.430), (0.285, 0.240)]:
    arrow(mx + mw / 2, y0, mx + mw / 2, y1)

# side inputs feeding the main column
sx, sw = 0.665, 0.325
box(sx, 0.475, sw, 0.145, "IFCT 2017\n528 foods, 9 nutrients\nper 100 g edible", fs=5.6, fc="#eaf0f6")
box(sx, 0.095, sw, 0.145, "ICMR-NIN 2020 RDA\n+ Mifflin-St Jeor BMR\n-> energy/macro targets", fs=5.5, fc="#eaf0f6")

arrow(sx, 0.5475, mx + mw, 0.5475)
arrow(sx, 0.1675, mx + mw, 0.1675)

ax.text(0.5, 0.020, "Nutrition layer returns UNAVAILABLE while approved mappings = 0",
        ha="center", va="center", fontsize=5.4, style="italic", color=RED)
save(fig, "fig1_architecture.png")

# ----------------------------------------------------------------------
# Fig. 2  Parsing status and pipeline coverage (wide, two panels)
# ----------------------------------------------------------------------
fig, (a, b) = plt.subplots(1, 2, figsize=(7.05, 2.05), gridspec_kw={"width_ratios": [1.15, 1]})

status = ["Exact", "Approximate", "Range", "Unquantified"]
counts = [54903, 29980, 1673, 4306]
bars = a.bar(status, counts, color=BLUE, edgecolor="black", linewidth=0.4, width=0.62)
a.set_ylabel("Ingredient records")
a.set_title("(a) Quantity-parsing outcome (90,862 records)")
a.set_ylim(0, 63000)
a.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, p: f"{v/1000:.0f}k"))
for bar, v in zip(bars, counts):
    a.text(bar.get_x() + bar.get_width() / 2, v + 900, f"{v:,}", ha="center", va="bottom", fontsize=5.6)
a.tick_params(axis="x", length=0)

cov_labels = ["Approved\nIFCT\nmappings", "Resolved\ngram\nweights", "Edible\nportion\ncodes", "IFCT\nfibre/carb\npresent"]
cov_vals = [0.0, 1299 / 90862 * 100, 180 / 528 * 100, 306 / 528 * 100]
cols = [RED, ORANGE, ORANGE, ORANGE]
bars = b.bar(cov_labels, cov_vals, color=cols, edgecolor="black", linewidth=0.4, width=0.58)
b.set_ylabel("Coverage (%)")
b.set_title("(b) Nutrition-pipeline coverage")
b.set_ylim(0, 72)
for bar, v in zip(bars, cov_vals):
    b.text(bar.get_x() + bar.get_width() / 2, v + 1.4,
           ("0.0%" if v == 0 else f"{v:.1f}%"), ha="center", va="bottom", fontsize=5.9)
b.tick_params(axis="x", length=0, labelsize=5.6)

fig.tight_layout(w_pad=1.6)
save(fig, "fig2_pipeline_coverage.png")

# ----------------------------------------------------------------------
# Fig. 3  Precision@5 and Recall@5
# ----------------------------------------------------------------------
fig, (a, b) = plt.subplots(2, 1, figsize=(3.45, 2.75))
x = np.arange(len(METHODS))
short = ["Random", "Cuisine", "Jaccard", "TF-IDF"]

for ax, vals, label, title, ymax, fmt in [
        (a, P5, "Precision@5", "(a) Precision@5", 1.14, "{:.3f}"),
        (b, R5, "Recall@5", "(b) Recall@5", 0.020, "{:.4f}")]:
    bars = ax.bar(x, vals, color=[GREY, ORANGE, GREEN, BLUE], edgecolor="black", linewidth=0.4, width=0.6)
    ax.set_xticks(x)
    ax.set_xticklabels(short)
    ax.set_ylabel(label)
    ax.set_title(title, loc="left")
    ax.set_ylim(0, ymax)
    ax.tick_params(axis="x", length=0)
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, v + ymax * 0.025, fmt.format(v),
                ha="center", va="bottom", fontsize=5.6)

b.axhline(0.02, color=RED, linestyle="--", linewidth=0.7)
b.text(3.42, 0.0208, "threshold 0.02", color=RED, fontsize=5.2, ha="right", va="bottom")
fig.tight_layout(h_pad=1.0)
save(fig, "fig3_precision_recall.png")

# ----------------------------------------------------------------------
# Fig. 4  Precision@k by method
# ----------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(3.45, 2.1))
ks = ["5", "10", "20"]
x = np.arange(len(ks))
w = 0.19
for i, (name, vals) in enumerate(P_AT_K.items()):
    ax.bar(x + (i - 1.5) * w, vals, w, label=name,
           color=[GREY, ORANGE, GREEN, BLUE][i], edgecolor="black", linewidth=0.35)
ax.set_xticks(x)
ax.set_xticklabels([f"k = {k}" for k in ks])
ax.set_ylabel("Precision@k")
ax.set_ylim(0, 1.02)
ax.legend(ncol=4, frameon=False, handlelength=0.9, columnspacing=1.1,
          loc="lower center", bbox_to_anchor=(0.5, 1.01))
fig.tight_layout()
save(fig, "fig4_precision_at_k.png")

# ----------------------------------------------------------------------
# Fig. 5  Diversity and coverage against the stated thresholds
# ----------------------------------------------------------------------
fig, (a, b) = plt.subplots(2, 1, figsize=(3.45, 2.7))
x = np.arange(len(METHODS))
bars = a.bar(x, DIV, color=[GREY, ORANGE, GREEN, BLUE], edgecolor="black", linewidth=0.4, width=0.6)
a.set_xticks(x)
a.set_xticklabels(short)
a.set_ylabel("Diversity@10")
a.set_ylim(0, 1.12)
a.set_title("(a) Intra-list diversity", loc="left")
a.tick_params(axis="x", length=0)
for bar, v in zip(bars, DIV):
    a.text(bar.get_x() + bar.get_width() / 2, v + 0.02, f"{v:.3f}", ha="center", va="bottom", fontsize=5.6)

bars = b.bar(x, [c * 100 for c in COV], color=[GREY, ORANGE, GREEN, BLUE],
             edgecolor="black", linewidth=0.4, width=0.6)
b.axhline(50, color=RED, linestyle="--", linewidth=0.7)
b.text(3.42, 51.5, "requirement 50%", color=RED, fontsize=5.2, ha="right", va="bottom")
b.set_xticks(x)
b.set_xticklabels(short)
b.set_ylabel("Coverage@20 (%)")
b.set_ylim(0, 62)
b.set_title("(b) Catalogue coverage", loc="left")
b.tick_params(axis="x", length=0)
for bar, v in zip(bars, COV):
    b.text(bar.get_x() + bar.get_width() / 2, v * 100 + 1.0, f"{v*100:.1f}%",
           ha="center", va="bottom", fontsize=5.6)
fig.tight_layout(h_pad=1.0)
save(fig, "fig5_diversity_coverage.png")

print("summary:", dict(zip(METHODS, zip(P5, R5, DIV, COV, LAT))))
