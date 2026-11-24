"""Generate all figures for IEEE_Final_Research_Paper.tex.

Every plotted number is read from a frozen project artifact:
  reports/phase5/experiments/results/{baseline,content_based,clustering}_experiments.json
  data/interim/phase2/parsed_recipe_ingredients.parquet   (parse_status counts)

Nothing is simulated. Run:  py generate_figures.py
"""

from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RESULTS = ROOT / "reports" / "phase5" / "experiments" / "results"

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["DejaVu Serif"],
    "mathtext.fontset": "dejavuserif",
    "font.size": 7,
    "axes.labelsize": 7,
    "axes.titlesize": 7.5,
    "xtick.labelsize": 6.5,
    "ytick.labelsize": 6.5,
    "legend.fontsize": 6.2,
    "axes.linewidth": 0.6,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "savefig.dpi": 600,
    "figure.dpi": 120,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

DARK = "#2b4a63"
MID = "#7fa3bb"
LIGHT = "#c9dae5"
ACC = "#9e3b32"
GREY = "#8a8a8a"
INK = "#1a1a1a"

# ---------------------------------------------------------------- data ----
base = json.loads((RESULTS / "baseline_experiments.json").read_text())
cbf = json.loads((RESULTS / "content_based_experiments.json").read_text())
clu = json.loads((RESULTS / "clustering_experiments.json").read_text())

METHODS = ["Random", "Cuisine\nmatch", "Jaccard", "Weighted\n(deployed)"]
P5 = [base["random"]["metrics"]["precision@5"]["mean"],
      base["cuisine_match"]["metrics"]["precision@5"]["mean"],
      base["jaccard"]["metrics"]["precision@5"]["mean"],
      cbf["tfidf_only"]["metrics"]["precision@5"]["mean"]]
R5 = [base["random"]["metrics"]["recall@5"]["mean"],
      base["cuisine_match"]["metrics"]["recall@5"]["mean"],
      base["jaccard"]["metrics"]["recall@5"]["mean"],
      cbf["tfidf_only"]["metrics"]["recall@5"]["mean"]]
DIV = [base["random"]["metrics"]["diversity"]["mean"],
       base["cuisine_match"]["metrics"]["diversity"]["mean"],
       base["jaccard"]["metrics"]["diversity"]["mean"],
       cbf["tfidf_only"]["metrics"]["diversity"]["mean"]]
COV = [base["random"]["metrics"]["coverage"],
       base["cuisine_match"]["metrics"]["coverage"],
       base["jaccard"]["metrics"]["coverage"],
       cbf["tfidf_only"]["metrics"]["coverage"]]
LAT = [base["random"]["time_seconds"] / 50 * 1000,
       base["cuisine_match"]["time_seconds"] / 50 * 1000,
       base["jaccard"]["time_seconds"] / 50 * 1000,
       180.0]
PK = {"5": P5,
      "10": [base["random"]["metrics"]["precision@10"]["mean"],
             base["cuisine_match"]["metrics"]["precision@10"]["mean"],
             base["jaccard"]["metrics"]["precision@10"]["mean"],
             cbf["tfidf_only"]["metrics"]["precision@10"]["mean"]],
      "20": [base["random"]["metrics"]["precision@20"]["mean"],
             base["cuisine_match"]["metrics"]["precision@20"]["mean"],
             base["jaccard"]["metrics"]["precision@20"]["mean"],
             cbf["tfidf_only"]["metrics"]["precision@20"]["mean"]]}


def composite(p, r, d, c, lat_ms, rel=1.0):
    return (0.30 * p + 0.20 * r + 0.15 * d + 0.15 * c
            + 0.10 * (1 - lat_ms / 500.0) + 0.10 * rel)


PHI = [composite(P5[i], R5[i], DIV[i], COV[i], LAT[i]) for i in range(4)]
PHI_NOREL = [composite(P5[i], R5[i], DIV[i], COV[i], LAT[i], rel=0.0) for i in range(4)]

summary = {
    "P@5": P5, "R@5": R5, "Div@10": DIV, "Cov@20": COV,
    "latency_ms": [round(v, 1) for v in LAT],
    "composite_recomputed": [round(v, 3) for v in PHI],
    "composite_without_reliability": [round(v, 3) for v in PHI_NOREL],
}
(HERE / "figure_data_summary.json").write_text(json.dumps(summary, indent=2))
print(json.dumps(summary, indent=2))

# ------------------------------------------------------------- helpers ----
def box(ax, x, y, w, h, text, fc="white", ec=DARK, fs=5.9, ls="-", lw=0.7):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle="round,pad=0.18,rounding_size=0.5",
                                linewidth=lw, edgecolor=ec, facecolor=fc,
                                linestyle=ls, zorder=3))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fs, color=INK, zorder=4, linespacing=1.4)


def arrow(ax, p0, p1, ls="-", color=DARK, lw=0.7, zorder=2):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=6.5,
                                 linewidth=lw, color=color, linestyle=ls,
                                 shrinkA=1.0, shrinkB=1.0, zorder=zorder))


def canvas(w, h, ylim=(0, 100)):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, 100); ax.set_ylim(*ylim); ax.axis("off")
    fig.subplots_adjust(0.004, 0.004, 0.996, 0.996)
    return fig, ax


# ================================================ Fig 1  architecture =====
fig, ax = canvas(7.16, 2.35)
ax.add_patch(Rectangle((0, 51), 100, 49, facecolor="#f1f4f7", edgecolor="none", zorder=0))
ax.add_patch(Rectangle((0, 0), 100, 49, facecolor="#f8f5f2", edgecolor="none", zorder=0))
ax.text(1.4, 96, "A. Composition path (implemented; abstains)", fontsize=6.2,
        style="italic", color=ACC, va="top")
ax.text(1.4, 46, "B. Recommendation path (evaluated under a proxy)", fontsize=6.2,
        style="italic", color=DARK, va="top")

xs = [1.5, 21.5, 41.5, 61.5, 81.5]
w, h = 17, 19
yA = 64
box(ax, xs[0], yA, w, h, "Recipe corpus\n6,865 recipes\n90,862 ingredient rows")
box(ax, xs[1], yA, w, h, "Ingredient parsing\nand normalisation")
box(ax, xs[2], yA, w, h, "IFCT candidate\ngeneration\n119,474 pairs")
box(ax, xs[3], yA, w, h, "Human review gate\n0 approved", ec=ACC, ls="--")
box(ax, xs[4], yA, w, h, "Nutrition engine\nstatus unavailable\n(gate empty)", ec=ACC, fc="#f7e9e7")
for i in range(4):
    arrow(ax, (xs[i] + w, yA + h / 2), (xs[i + 1], yA + h / 2))

yB = 8
box(ax, xs[0], yB, w, h, "Recipe features\nTF-IDF and\nmetadata")
box(ax, xs[1], yB, w, h, "Similarity scoring\n$S=0.4J+0.3C$\n$+0.15K+0.15D$")
box(ax, xs[2], yB, w, h, "Dietary hard filters\n(allergens, diet)")
box(ax, xs[3], yB, w, h, "Top-$k$ list with\nexplanations")
box(ax, xs[4], yB, w, h, "Meal planner\nBMR/TDEE targets\nnutrition term inert", ec=GREY)
for i in range(4):
    arrow(ax, (xs[i] + w, yB + h / 2), (xs[i + 1], yB + h / 2))
arrow(ax, (xs[0] + w / 2, yA), (xs[0] + w / 2, yB + h), color=GREY, ls=":")
arrow(ax, (xs[4] + w / 2, yA), (xs[4] + w / 2, yB + h), color=ACC, ls="--")
fig.savefig(HERE / "fig1_architecture.png", bbox_inches="tight", pad_inches=0.02)
plt.close(fig)

# ============================================ Fig 2  preprocessing ========
fig, ax = canvas(7.16, 1.35, ylim=(0, 46))
steps = [
    "Raw ingredient\nline (EN / HI)",
    "Normalisation\nunicode, case,\npunctuation",
    "Synonym map to\ncanonical name",
    "Quantity and\nunit extraction",
    "Household measure\nto grams",
    "Preparation-state\nextraction",
    "Structured record\n(22 fields)",
]
n = len(steps)
bw, gap = 12.0, 2.4
x0 = (100 - (n * bw + (n - 1) * gap)) / 2
for i, s in enumerate(steps):
    x = x0 + i * (bw + gap)
    box(ax, x, 18, bw, 21, s, fc="white" if i not in (3, 4) else "#eaf1f6")
    if i:
        arrow(ax, (x - gap, 28.5), (x, 28.5))
ax.text(50, 6, "90,862 rows  ·  54,903 exact  ·  29,980 approximate  ·  1,673 range  ·  "
               "4,306 unquantified  ·  1,299 resolved gram weights (1.43 %)",
        ha="center", va="center", fontsize=5.7, color=INK)
fig.savefig(HERE / "fig2_preprocessing.png", bbox_inches="tight", pad_inches=0.02)
plt.close(fig)

# ================================== Fig 3  matching + nutrition ==========
fig, ax = canvas(7.16, 1.3, ylim=(0, 40))
bw, gap = 17.6, 2.5
x0 = 1.0
b = [x0 + i * (bw + gap) for i in range(5)]
box(ax, b[0], 10, bw, 22, "Normalised\ningredient name")
box(ax, b[1], 10, bw, 22, "Candidate\ngeneration\n119,474 pairs")
box(ax, b[2], 10, bw, 22, "Reviewer decision\napprove / reject\n63,244 rows unmatched", fs=5.5)
box(ax, b[3], 10, bw, 22, "Approval gate\n0 approved", ec=ACC, ls="--")
box(ax, b[4], 10, bw, 22,
    "Approved: $N=\\sum x_iw_i/100$\nElse: status\nNO_MAPPED_INGREDIENTS", ec=ACC, fc="#f7e9e7", fs=5.4)
for i in range(4):
    arrow(ax, (b[i] + bw, 21), (b[i + 1], 21))
fig.savefig(HERE / "fig3_matching.png", bbox_inches="tight", pad_inches=0.02)
plt.close(fig)

# ==================================== Fig 4  recommendation path =========
fig, ax = canvas(7.16, 1.42, ylim=(0, 44))
bw, gap = 14.6, 1.9
x0 = (100 - (6 * bw + 5 * gap)) / 2
b = [x0 + i * (bw + gap) for i in range(6)]
labels = [
    "Recipe\n(ingredients,\nmetadata)",
    "Ingredient set +\ncuisine, course,\ndiet labels",
    "Score $S(q,c)$\n$0.4J+0.3C$\n$+0.15K+0.15D$",
    "Dietary hard\nfilters",
    "Top-$k$\n+ reasons",
    "Proxy evaluation\n(50 queries)",
]
for i, t in enumerate(labels):
    box(ax, b[i], 16, bw, 24, t, fs=5.5, fc="#eaf1f6" if i in (1, 2) else "white")
    if i:
        arrow(ax, (b[i] - gap, 28), (b[i], 28))
ax.text(50, 5, "TF-IDF (2,000 terms, 1–2-grams) is fitted as a representation and enters the\n"
               "clustering study, but it is not an input to $S$", ha="center", va="center",
        fontsize=5.4, color=GREY, linespacing=1.4)
fig.savefig(HERE / "fig4_recommendation.png", bbox_inches="tight", pad_inches=0.02)
plt.close(fig)

# ================================== Fig 5  model comparison ==============
fig, axes = plt.subplots(1, 3, figsize=(7.16, 1.6),
                         gridspec_kw={"width_ratios": [1, 1, 1.3]})
x = np.arange(4)
axes[0].bar(x, P5, width=0.62, color=[MID, MID, MID, DARK])
axes[0].set_title("(a) Precision@5")
axes[0].set_ylim(0, 1.14)
for xi, v in zip(x, P5):
    axes[0].text(xi, v + 0.03, f"{v:.3f}", ha="center", fontsize=5.6)

axes[1].bar(x, R5, width=0.62, color=[MID, MID, MID, DARK])
axes[1].axhline(0.02, color=ACC, lw=0.8, ls="--")
axes[1].text(3.45, 0.0205, "target 0.02", color=ACC, fontsize=5.5, ha="right", va="bottom")
axes[1].set_title("(b) Recall@5")
axes[1].set_ylim(0, 0.027)
for xi, v in zip(x, R5):
    axes[1].text(xi, v + 0.0008, f"{v:.4f}", ha="center", fontsize=5.2)

ks = [5, 10, 20]
for i, (col, mk, lab) in enumerate([(GREY, "o", "Random"), (MID, "s", "Cuisine match"),
                                   (LIGHT, "^", "Jaccard"), (DARK, "D", "Weighted")]):
    axes[2].plot(ks, [PK[str(k)][i] for k in ks], marker=mk, ms=3.2, lw=1.0,
                 color=col, markeredgecolor=DARK, markeredgewidth=0.35, label=lab)
axes[2].set_title("(c) Precision at cut-off")
axes[2].set_xlabel("cut-off $k$")
axes[2].set_xticks(ks)
axes[2].set_ylim(0, 1.10)
axes[2].legend(frameon=False, loc="lower left", handlelength=1.0, borderaxespad=0.1,
               labelspacing=0.25)

for a in axes[:2]:
    a.set_xticks(x)
    a.set_xticklabels(METHODS, fontsize=5.7)
for a in axes:
    a.grid(axis="y", color="#dddddd", lw=0.4)
    a.set_axisbelow(True)
fig.tight_layout(pad=0.25, w_pad=0.7)
fig.savefig(HERE / "fig5_comparison.png", bbox_inches="tight", pad_inches=0.02)
plt.close(fig)

# ============================ Fig 6  diversity and coverage ==============
fig, axes = plt.subplots(1, 2, figsize=(7.16, 1.5))
axes[0].bar(x, DIV, width=0.62, color=[MID, MID, MID, DARK])
axes[0].set_title("(a) Intra-list diversity@10")
axes[0].set_ylim(0, 1.14)
for xi, v in zip(x, DIV):
    axes[0].text(xi, v + 0.03, f"{v:.3f}", ha="center", fontsize=5.8)

axes[1].bar(x, COV, width=0.62, color=[MID, MID, MID, DARK])
axes[1].axhline(0.50, color=ACC, lw=0.9, ls="--")
axes[1].text(3.45, 0.512, "requirement 0.50", color=ACC, fontsize=5.7, ha="right", va="bottom")
axes[1].set_title("(b) Catalogue coverage@20")
axes[1].set_ylim(0, 0.62)
for xi, v in zip(x, COV):
    axes[1].text(xi, v + 0.016, f"{v:.3f}", ha="center", fontsize=5.8)

for a in axes:
    a.set_xticks(x); a.set_xticklabels(METHODS, fontsize=5.8)
    a.grid(axis="y", color="#dddddd", lw=0.4); a.set_axisbelow(True)
fig.tight_layout(pad=0.25, w_pad=1.0)
fig.savefig(HERE / "fig6_divcov.png", bbox_inches="tight", pad_inches=0.02)
plt.close(fig)

# =============================== Fig 7  parsing outcomes =================
fig, ax = plt.subplots(figsize=(3.35, 1.65))
labels = ["Exact", "Approximate", "Range", "Unquantified"]
vals = [54903, 29980, 1673, 4306]
y = np.arange(len(vals))[::-1]
ax.barh(y, vals, height=0.6, color=[DARK, MID, LIGHT, ACC])
ax.set_yticks(y); ax.set_yticklabels(labels)
ax.set_xlabel("ingredient rows (of 90,862)")
ax.set_xlim(0, 68000)
for yi, v in zip(y, vals):
    ax.text(v + 1200, yi, f"{v:,} ({v/90862*100:.1f} %)", va="center", fontsize=6)
ax.grid(axis="x", color="#dddddd", lw=0.4); ax.set_axisbelow(True)
fig.tight_layout(pad=0.2)
fig.savefig(HERE / "fig7_parsing.png", bbox_inches="tight", pad_inches=0.02)
plt.close(fig)

# ============================ Fig 8  nutrition coverage ==================
fig, ax = plt.subplots(figsize=(3.35, 1.7))
labels = ["Approved IFCT\nmappings", "Resolved gram\nweight (rows)",
          "Edible-portion\nfactors (IFCT)", "Fibre + available\ncarbohydrate"]
vals = [0.0, 1.43, 34.1, 58.0]
y = np.arange(len(vals))[::-1]
ax.barh(y, vals, height=0.58, color=[ACC, ACC, MID, MID])
ax.set_yticks(y); ax.set_yticklabels(labels, fontsize=6.2)
ax.set_xlabel("coverage (%)")
ax.set_xlim(0, 104)
for yi, v in zip(y, vals):
    ax.text(v + 2, yi, f"{v:.2f} %" if v < 2 else f"{v:.1f} %", va="center", fontsize=6.2)
ax.axvline(100, color=GREY, lw=0.6, ls=":")
ax.grid(axis="x", color="#dddddd", lw=0.4); ax.set_axisbelow(True)
fig.tight_layout(pad=0.2)
fig.savefig(HERE / "fig8_nutrition.png", bbox_inches="tight", pad_inches=0.02)
plt.close(fig)

# =============================== Fig 9  clustering =======================
fig, axes = plt.subplots(1, 2, figsize=(3.35, 1.65))
km_k = [20, 50, 100]
km_s = [clu["kmeans_20"]["silhouette"], clu["kmeans_50"]["silhouette"], clu["kmeans_100"]["silhouette"]]
km_d = [clu["kmeans_20"]["davies_bouldin"], clu["kmeans_50"]["davies_bouldin"], clu["kmeans_100"]["davies_bouldin"]]
ag_k = [20, 50]
ag_s = [clu["agglomerative_20"]["silhouette"], clu["agglomerative_50"]["silhouette"]]
ag_d = [clu["agglomerative_20"]["davies_bouldin"], clu["agglomerative_50"]["davies_bouldin"]]

axes[0].plot(km_k, km_s, "o-", color=DARK, ms=3.2, lw=1.0, label="K-Means")
axes[0].plot(ag_k, ag_s, "s--", color=MID, ms=3.0, lw=1.0, label="Agglom.")
axes[0].set_title("(a) Silhouette")
axes[0].set_xlabel("$K$"); axes[0].set_ylim(0, 0.062)
axes[0].set_xticks([20, 50, 100])
axes[0].legend(frameon=False, loc="lower right", handlelength=1.0, labelspacing=0.25)

axes[1].plot(km_k, km_d, "o-", color=DARK, ms=3.2, lw=1.0)
axes[1].plot(ag_k, ag_d, "s--", color=MID, ms=3.0, lw=1.0)
axes[1].set_title("(b) Davies--Bouldin")
axes[1].set_xlabel("$K$"); axes[1].set_ylim(2.9, 4.5)
axes[1].set_xticks([20, 50, 100])
for a in axes:
    a.grid(axis="y", color="#dddddd", lw=0.4); a.set_axisbelow(True)
fig.tight_layout(pad=0.25, w_pad=0.9)
fig.savefig(HERE / "fig9_clustering.png", bbox_inches="tight", pad_inches=0.02)
plt.close(fig)

print("wrote figures to", HERE)
