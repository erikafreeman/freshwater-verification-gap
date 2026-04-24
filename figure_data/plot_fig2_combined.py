"""Figure 2 — Empirical evidence of the freshwater verification gap.

Produces a single 3-panel composite figure matching v40 Figure 2:
  Panel A: Global monitoring sites (NEON + ILTER aquatic) over Tedesco
           freshwater fish richness basin centroids. Inset legend notes
           GBIF country-effort skew (61% in top 5).
  Panel B: Variable dynamics vs sampling-frequency bars on log-time axis.
  Panel C: Scissors plot — freshwater ML vs monitoring publications, 2000-2025.

All inputs are produced by upstream scripts (see Makefile); this script is
deterministic given those CSVs and makes no network calls.

Inputs (from figure_data/):
  neon_aquatic_sites.csv
  ilter_sites.csv
  tedesco_basin_richness.csv
  panel_b_timescales.csv
  scissors_publications_by_year.csv

Output: fig2_v40.png (300 dpi) and fig2_v40.svg
"""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

HERE = Path(__file__).parent

# ---------------------------------------------------------------------------
# Load inputs
# ---------------------------------------------------------------------------
neon = pd.read_csv(HERE / "neon_aquatic_sites.csv")
ilter = pd.read_csv(HERE / "ilter_sites.csv")
ilter_aq = ilter[ilter["is_aquatic_by_name"] == True].copy()

tedesco = pd.read_csv(HERE / "tedesco_basin_richness.csv")
for c in ("latitude", "longitude"):
    tedesco[c] = pd.to_numeric(tedesco[c], errors="coerce")
tedesco = tedesco.dropna(subset=["latitude", "longitude"])
tedesco = tedesco[tedesco["native_richness"] > 0]

panel_b = pd.read_csv(HERE / "panel_b_timescales.csv")
var_df = panel_b[panel_b["group"] == "variable_dynamics"].sort_values("anchor_days")
freq_df = panel_b[panel_b["group"] == "sampling_frequency"].sort_values("anchor_days")

scissors = pd.read_csv(HERE / "scissors_publications_by_year.csv")
scissors = scissors[(scissors["year"] >= 2000) & (scissors["year"] <= 2025)]

# ---------------------------------------------------------------------------
# Figure layout: 2 rows, 2 cols (Panel A spans full top row)
# ---------------------------------------------------------------------------
fig = plt.figure(figsize=(14, 10))
gs = gridspec.GridSpec(2, 2, height_ratios=[1.1, 1.0], hspace=0.32, wspace=0.22)

# --- Panel A: map ----------------------------------------------------------
axA = fig.add_subplot(gs[0, :])
tmax = tedesco["native_richness"].max()
axA.scatter(
    tedesco["longitude"], tedesco["latitude"],
    s=tedesco["native_richness"] / tmax * 300 + 3,
    c=tedesco["native_richness"], cmap="YlOrRd",
    alpha=0.55, edgecolors="none", zorder=2,
    label=f"Tedesco 2017 basins (n={len(tedesco):,})",
)
neon_colors = {"LAKE": "#1F6FB2", "RIVER": "#0D9488", "STREAM": "#60A5FA"}
for subtype, colour in neon_colors.items():
    sub = neon[neon["subtype"] == subtype]
    axA.scatter(
        sub["longitude"], sub["latitude"],
        s=30, c=colour, edgecolors="white", linewidth=0.6,
        label=f"NEON {subtype.lower()} (n={len(sub)})", zorder=5,
    )
axA.scatter(
    ilter_aq["longitude"], ilter_aq["latitude"],
    s=16, c="#0D9488", edgecolors="white", linewidth=0.3, alpha=0.8,
    label=f"ILTER aquatic (n={len(ilter_aq)})", zorder=4,
)
axA.set_xlim(-180, 180)
axA.set_ylim(-60, 85)
axA.set_xlabel("Longitude", fontsize=9)
axA.set_ylabel("Latitude", fontsize=9)
axA.set_title(
    "A  |  Freshwater monitoring is concentrated where fish biodiversity is lowest",
    loc="left", fontsize=11,
)
axA.legend(loc="lower left", fontsize=8, framealpha=0.9)
axA.grid(True, linestyle=":", linewidth=0.4, alpha=0.5)
axA.set_aspect("equal")

# --- Panel B: timescale bars ----------------------------------------------
axB = fig.add_subplot(gs[1, 0])

def draw_group(ax, sub, y_offset, colour):
    for i, (_, r) in enumerate(sub.iterrows()):
        y = y_offset + i
        ax.barh(y, r["high_days"] - r["low_days"], left=r["low_days"],
                height=0.62, color=colour, edgecolor="white", linewidth=0.8, alpha=0.85)
        ax.plot([r["anchor_days"]], [y], marker="|", color="black",
                markersize=8, markeredgewidth=1.1)
        ax.text(r["high_days"] * 1.1, y, r["label"], va="center", fontsize=7.5)

GAP = 1.3
var_y0 = len(freq_df) + GAP
draw_group(axB, freq_df, 0, "#D97706")
draw_group(axB, var_df, var_y0, "#1F6FB2")

axB.axvspan(1, 30, color="#FEF3C7", alpha=0.35, zorder=-1)
axB.set_xscale("log")
axB.set_xticks([1/24, 1, 7, 30, 365, 365*5])
axB.set_xticklabels(["1 h", "1 d", "1 wk", "1 mo", "1 yr", "5 yr"])
axB.set_xlim(1/48, 365*6)
axB.set_yticks([])
axB.set_xlabel("Characteristic timescale (log)", fontsize=9)
axB.set_title("B  |  Sampling cadence lags variable dynamics", loc="left", fontsize=11)
axB.text(0.01, var_y0 + len(var_df) - 0.5,
         "Variable dynamics", transform=axB.get_yaxis_transform(),
         fontsize=9, fontweight="bold", color="#1F6FB2")
axB.text(0.01, len(freq_df) - 0.5,
         "Sampling frequency", transform=axB.get_yaxis_transform(),
         fontsize=9, fontweight="bold", color="#D97706")
for spine in ("top", "right"):
    axB.spines[spine].set_visible(False)

# --- Panel C: scissors -----------------------------------------------------
axC = fig.add_subplot(gs[1, 1])
series = {
    "freshwater_ml":         {"colour": "#1F6FB2", "label": "ML / AI freshwater",        "lw": 2.4},
    "freshwater_prediction": {"colour": "#60A5FA", "label": "Freshwater prediction",     "lw": 1.8},
    "freshwater_monitoring": {"colour": "#D97706", "label": "Freshwater monitoring",     "lw": 2.4},
}
for q, s in series.items():
    sub = scissors[scissors["query"] == q].sort_values("year")
    axC.plot(sub["year"], sub["n_works"], color=s["colour"],
             linewidth=s["lw"], label=s["label"])

axC.set_yscale("log")
axC.set_xlabel("Year", fontsize=9)
axC.set_ylabel("Publications per year (log)", fontsize=9)
axC.set_title("C  |  Models outpace monitoring; AI accelerates the divergence",
              loc="left", fontsize=11)
axC.axvline(2018, color="grey", linestyle="--", linewidth=0.8, alpha=0.7)
axC.text(2018.3, axC.get_ylim()[1] * 0.4,
         "AI inflection\n(model generation:\nyears → weeks)",
         fontsize=8, va="top", color="#374151")
axC.legend(loc="upper left", fontsize=8, framealpha=0.9)
axC.grid(True, which="both", linestyle=":", linewidth=0.4, alpha=0.4)
for spine in ("top",):
    axC.spines[spine].set_visible(False)

# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------
fig.suptitle(
    "Figure 2 — Empirical evidence of the freshwater verification gap",
    fontsize=13, y=0.995, x=0.02, ha="left",
)

for ext in ("png", "svg"):
    out = HERE / f"fig2_v40.{ext}"
    fig.savefig(out, dpi=300, bbox_inches="tight")
    print(f"wrote {out.name}")

# Headline stats (logged to stdout; referenced in captions and cover letter)
high_rich = tedesco[tedesco["native_richness"] >= 200]
tropical = high_rich[high_rich["latitude"].between(-23.5, 23.5)]
print("\nHeadline statistics used in the caption:")
print(f"  Tedesco basins plotted: {len(tedesco):,}")
print(f"  High-richness basins (>=200 native): {len(high_rich)}; tropical share: {100*len(tropical)/len(high_rich):.0f}%")
print(f"  NEON sites plotted: {len(neon)}; in tropics: {(neon['latitude'].between(-23.5,23.5)).sum()}")
print(f"  ILTER aquatic sites: {len(ilter_aq)}")

ml_2025 = scissors[(scissors['query']=='freshwater_ml') & (scissors['year']==2025)]['n_works'].iloc[0]
ml_2000 = scissors[(scissors['query']=='freshwater_ml') & (scissors['year']==2000)]['n_works'].iloc[0]
mon_2025 = scissors[(scissors['query']=='freshwater_monitoring') & (scissors['year']==2025)]['n_works'].iloc[0]
mon_2000 = scissors[(scissors['query']=='freshwater_monitoring') & (scissors['year']==2000)]['n_works'].iloc[0]
print(f"  ML growth 2000->2025: {ml_2000}->{ml_2025}/yr ({ml_2025/ml_2000:.0f}x)")
print(f"  Monitoring growth:    {mon_2000}->{mon_2025}/yr ({mon_2025/mon_2000:.0f}x)")
