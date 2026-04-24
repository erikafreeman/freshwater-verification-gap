"""Supplementary Figure S2 — robustness check for Figure 2C.

Figure 2C in the main text plots cumulative publication counts on a log y-axis.
A reviewer flagged that cumulative + log could visually amplify divergence.
This Supp Fig re-plots the same data as annual counts, showing that the
divergence is not a cumulation artefact: the widening gap is present in the
year-by-year series as well.

Inputs: scissors_publications_by_year.csv (with 'n_works' = annual count).
Outputs: supplementary_figure_s2.png (300 dpi) and .svg.
"""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

HERE = Path(__file__).parent
sciss = pd.read_csv(HERE / "scissors_publications_by_year.csv")
sciss = sciss[(sciss["year"] >= 2000) & (sciss["year"] <= 2025)].copy()

series = {
    "freshwater_ml":         {"colour": "#1F6FB2", "label": "Freshwater machine learning",  "lw": 2.4, "ls": "-"},
    "freshwater_prediction": {"colour": "#60A5FA", "label": "Freshwater prediction model",  "lw": 1.8, "ls": "-"},
    "freshwater_monitoring": {"colour": "#D97706", "label": "Freshwater monitoring",        "lw": 2.4, "ls": "-"},
}
# If an ecological_model query exists, include it
if "freshwater_ecological_model" in sciss["query"].unique():
    series["freshwater_ecological_model"] = {
        "colour": "#64748B", "label": "Freshwater ecological model", "lw": 1.8, "ls": "--",
    }

fig, (axA, axB) = plt.subplots(1, 2, figsize=(11, 4.2))

# Panel A: linear-y annual counts — shows the divergence without log compression
for q, s in series.items():
    sub = sciss[sciss["query"] == q].sort_values("year")
    if len(sub) == 0:
        continue
    axA.plot(sub["year"], sub["n_works"], color=s["colour"],
             linewidth=s["lw"], linestyle=s["ls"], label=s["label"])
axA.set_xlabel("Year", fontsize=9)
axA.set_ylabel("Publications per year (linear scale)", fontsize=9)
axA.set_title("A  |  Annual counts, linear y-axis", loc="left", fontsize=11)
axA.axvline(2018, color="grey", linestyle=":", linewidth=0.8, alpha=0.7)
axA.legend(loc="upper left", fontsize=8, framealpha=0.9)
axA.grid(True, linestyle=":", linewidth=0.4, alpha=0.5)
for spine in ("top", "right"):
    axA.spines[spine].set_visible(False)

# Panel B: log-y annual counts — same data, log axis shows relative rates
for q, s in series.items():
    sub = sciss[sciss["query"] == q].sort_values("year")
    if len(sub) == 0:
        continue
    axB.plot(sub["year"], sub["n_works"], color=s["colour"],
             linewidth=s["lw"], linestyle=s["ls"], label=s["label"])
axB.set_yscale("log")
axB.set_xlabel("Year", fontsize=9)
axB.set_ylabel("Publications per year (log scale)", fontsize=9)
axB.set_title("B  |  Annual counts, log y-axis", loc="left", fontsize=11)
axB.axvline(2018, color="grey", linestyle=":", linewidth=0.8, alpha=0.7)
axB.legend(loc="lower right", fontsize=8, framealpha=0.9)
axB.grid(True, which="both", linestyle=":", linewidth=0.4, alpha=0.4)
for spine in ("top", "right"):
    axB.spines[spine].set_visible(False)

fig.suptitle(
    "Supplementary Figure S2 — robustness check for Figure 2C: annual (non-cumulative) counts "
    "show the same widening divergence",
    fontsize=10, y=1.02, x=0.02, ha="left",
)

for ext in ("png", "svg"):
    out = HERE / f"supplementary_figure_s2.{ext}"
    fig.savefig(out, dpi=300, bbox_inches="tight")
    print(f"wrote {out.name}")
