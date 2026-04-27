"""Figure 2 - Triangulating evidence of the freshwater verification gap.

Produces a 3-panel composite matching the aesthetic of the published PDF:

  Panel A: World scatter of NEON + ILTER aquatic sites over Tedesco 2017
           freshwater fish richness (green-sequential binning on basin
           centroids). Two insets on the right stack a GBIF observer-effort
           bar chart on top of a tropical-biodiversity callout.

  Panel B: Dumbbell plot comparing characteristic timescales of variable
           dynamics (green) against routine sampling programmes (orange)
           and high-frequency observatories (hollow blue, NEON + GLEON).

  Panel C: Cumulative OpenAlex publications, 2000-2025, log-y axis, with
           hedged growth labels matching the paper's "two orders of
           magnitude" / "one order of magnitude" language.

All inputs are produced by upstream scripts (see Makefile); this script is
deterministic given those CSVs and makes no network calls.
"""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.lines import Line2D

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

scissors = pd.read_csv(HERE / "scissors_publications_by_year.csv")
scissors = scissors[(scissors["year"] >= 2000) & (scissors["year"] <= 2025)]

# ---------------------------------------------------------------------------
# Style: ggplot-inspired theme with white background and light grid
# ---------------------------------------------------------------------------
plt.style.use("ggplot")
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 9,
    "axes.titleweight": "bold",
    "axes.titlelocation": "left",
    "axes.facecolor": "white",
    "figure.facecolor": "white",
    "axes.edgecolor": "#dcdcdc",
    "axes.labelcolor": "#333333",
    "axes.grid": False,
    "xtick.color": "#555555",
    "ytick.color": "#555555",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "legend.frameon": False,
})

GREEN = "#2d6a4f"
ORANGE = "#e76f51"
BLUE = "#1d4e89"
RED_DIAMOND = "#c1272d"
NEON_ORANGE = "#f4a261"

RICHNESS_BINS = [0, 10, 50, 200, 500, 1000, 10000]
RICHNESS_LABELS = ["1-10", "11-50", "51-200", "201-500", "501-1,000", ">1,000"]
RICHNESS_COLOURS = ["#e5f5e0", "#c7e9c0", "#a1d99b", "#74c476", "#31a354", "#006d2c"]

# ---------------------------------------------------------------------------
# Outer figure and nested layout
#
#   [      Panel A title spans full width (row 0 of outer)              ]
#   [  map (left 70%)  |  insets column (30%)                            ]
#   [                  |   - GBIF bar chart                              ]
#   [                  |   - tropics callout                             ]
#   [ Panel B | Panel C ]                                                 (row 1)
# ---------------------------------------------------------------------------
fig = plt.figure(figsize=(16, 10.5))
outer = gridspec.GridSpec(
    2, 1, height_ratios=[1.25, 1.0], hspace=0.22, figure=fig,
)

# Top row: map + insets
top = gridspec.GridSpecFromSubplotSpec(
    1, 2, width_ratios=[3.2, 1.0], wspace=0.08, subplot_spec=outer[0],
)
insets = gridspec.GridSpecFromSubplotSpec(
    2, 1, height_ratios=[1.2, 1.0], hspace=0.55, subplot_spec=top[1],
)

# Bottom row: Panels B and C
bot = gridspec.GridSpecFromSubplotSpec(
    1, 2, width_ratios=[1.0, 1.0], wspace=0.25, subplot_spec=outer[1],
)

# ---------------------------------------------------------------------------
# Panel A: map
# ---------------------------------------------------------------------------
axA = fig.add_subplot(top[0])

tedesco["bin"] = pd.cut(
    tedesco["native_richness"], bins=RICHNESS_BINS, labels=RICHNESS_LABELS,
    right=True, include_lowest=True,
)
for label, colour in zip(RICHNESS_LABELS, RICHNESS_COLOURS):
    sub = tedesco[tedesco["bin"] == label]
    axA.scatter(sub["longitude"], sub["latitude"], s=20, c=colour,
                alpha=0.9, edgecolors="none", zorder=2)

axA.scatter(neon["longitude"], neon["latitude"], s=45,
            facecolor=NEON_ORANGE, edgecolors="white", linewidth=0.8,
            marker="o", zorder=5)
axA.scatter(ilter_aq["longitude"], ilter_aq["latitude"], s=26,
            facecolor=RED_DIAMOND, edgecolors="white", linewidth=0.5,
            marker="D", zorder=4)

axA.set_xlim(-180, 180)
axA.set_ylim(-60, 85)
axA.set_xticks([])
axA.set_yticks([])
axA.set_title(
    "A   Spatial mismatch: biodiversity hotspots are in the tropics, "
    "monitoring sites are in temperate regions",
    fontsize=11.5, pad=10,
)
for spine in axA.spines.values():
    spine.set_visible(False)

legend_elems = [
    Line2D([0], [0], marker="o", color="w", markerfacecolor=c, markersize=8, label=lab)
    for lab, c in zip(RICHNESS_LABELS, RICHNESS_COLOURS)
]
legend_elems += [
    Line2D([0], [0], marker="o", color="w", markerfacecolor=NEON_ORANGE,
           markeredgecolor="white", markersize=9,
           label=f"NEON aquatic (n = {len(neon)})"),
    Line2D([0], [0], marker="D", color="w", markerfacecolor=RED_DIAMOND,
           markeredgecolor="white", markersize=7,
           label=f"ILTER aquatic (n = {len(ilter_aq)})"),
]
leg = axA.legend(handles=legend_elems, loc="lower left", fontsize=7.5,
                 framealpha=0.9, title="Native freshwater fish richness\n(species per basin)",
                 title_fontsize=7.5, handletextpad=0.4, labelspacing=0.35,
                 borderpad=0.7, edgecolor="#dcdcdc")
leg.get_title().set_fontweight("bold")
leg.get_frame().set_linewidth(0.6)

# ---------------------------------------------------------------------------
# Panel A inset 1 (top): GBIF observer-effort bars
# ---------------------------------------------------------------------------
ax_gbif = fig.add_subplot(insets[0])
gbif_countries = ["United States", "United Kingdom", "Germany", "France", "Australia"]
gbif_shares = [21, 13, 10, 9, 8]
y_pos = list(range(len(gbif_countries)))
ax_gbif.barh(y_pos, gbif_shares, color=ORANGE, height=0.65)
for y, pct in zip(y_pos, gbif_shares):
    ax_gbif.text(pct + 0.6, y, f"{pct}%", va="center", fontsize=8.5, color="#333333")
ax_gbif.set_yticks(y_pos)
ax_gbif.set_yticklabels(gbif_countries, fontsize=8.5)
ax_gbif.invert_yaxis()
ax_gbif.set_xlim(0, 30)
ax_gbif.set_xlabel("Share of global human-observation records (%)", fontsize=8)
ax_gbif.set_title("GBIF observer effort concentration by country",
                  fontsize=9.5, pad=6)
ax_gbif.tick_params(axis="x", labelsize=8)
ax_gbif.grid(False)
for spine in ("top", "right"):
    ax_gbif.spines[spine].set_visible(False)

# ---------------------------------------------------------------------------
# Panel A inset 2 (below): tropical-biodiversity callout
# ---------------------------------------------------------------------------
ax_note = fig.add_subplot(insets[1])
ax_note.axis("off")
ax_note.text(
    0.0, 0.95,
    "Top five countries account for 61% of\n"
    "global human-observation records; the\n"
    "least-monitored half of countries together\n"
    "hold 0.4%.",
    transform=ax_note.transAxes, fontsize=8.5, color="#333333",
    verticalalignment="top",
)
ax_note.text(
    0.0, 0.45,
    "~80% of river basins with >200 native\n"
    "freshwater fish species lie in the tropics.\n"
    "Only about 5% of the 205 ILTER aquatic\n"
    "sites are tropical, and only 2 of the 34\n"
    "NEON aquatic sites do (both in Puerto Rico).",
    transform=ax_note.transAxes, fontsize=8.5, color="#333333",
    verticalalignment="top", fontweight="normal",
)

# ---------------------------------------------------------------------------
# Panel B: timescale dumbbell plot
# ---------------------------------------------------------------------------
axB = fig.add_subplot(bot[0])

pairings = [
    ("Dissolved oxygen overnight swings", 0.5, 30, 0.02),
    ("Storm nutrient fluxes",             1,   60, 0.02),
    ("Wetland redox dynamics",            10,  60, None),
    ("Phytoplankton blooms",              10,  30, None),
    ("Zooplankton turnover",              30,  90, None),
    ("Seasonal fish / habitat shifts",    180, 365, None),
    ("Long-lived community trends",       365, 1825, None),
]
y_positions = list(range(len(pairings), 0, -1))
for y, (label, nat_d, routine_d, highfreq_d) in zip(y_positions, pairings):
    axB.plot([nat_d, routine_d], [y, y], color="#555555", linewidth=1.2,
             zorder=1, alpha=0.6)
    axB.scatter([nat_d], [y], s=85, c=GREEN, edgecolors="white",
                linewidth=0.8, zorder=3)
    axB.scatter([routine_d], [y], s=85, c=ORANGE, edgecolors="white",
                linewidth=0.8, zorder=3)
    if highfreq_d is not None:
        axB.scatter([highfreq_d], [y], s=95, facecolor="white",
                    edgecolors=BLUE, linewidth=1.6, zorder=3)

axB.set_yticks(y_positions)
axB.set_yticklabels([lab for lab, *_ in pairings], fontsize=8.5)
axB.set_xscale("log")
axB.set_xticks([1/24/60, 1/24, 1, 7, 30, 365, 365*10])
axB.set_xticklabels(["Minutes", "Hours", "Days", "Weeks", "Months", "Years", "Decades"])
axB.set_xlim(0.0005, 365*15)
axB.set_xlabel("Characteristic timescale", fontsize=9, labelpad=6)
axB.set_title("B   Temporal mismatch: freshwater dynamics are sampled too infrequently",
              fontsize=10.5, pad=10)
axB.grid(axis="x", linestyle=":", linewidth=0.4, color="#dcdcdc", alpha=0.7)
axB.set_facecolor("white")

legend_b = [
    Line2D([0], [0], marker="o", color="w", markerfacecolor=GREEN, markersize=9,
           markeredgecolor="white", label="Natural dynamics"),
    Line2D([0], [0], marker="o", color="w", markerfacecolor=ORANGE, markersize=9,
           markeredgecolor="white",
           label="Routine programmes (representative cadence)"),
    Line2D([0], [0], marker="o", color="w", markerfacecolor="white", markersize=9,
           markeredgecolor=BLUE, markeredgewidth=1.5,
           label="High-frequency observatories (NEON / GLEON)"),
]
axB.legend(handles=legend_b, loc="upper left", bbox_to_anchor=(-0.02, -0.12),
           ncol=1, fontsize=7.8, frameon=False, handletextpad=0.4)

# ---------------------------------------------------------------------------
# Panel C: bibliometric scissors
# ---------------------------------------------------------------------------
axC = fig.add_subplot(bot[1])

ml_series = scissors[scissors["query"] == "freshwater_ml"].sort_values("year")
mon_series = scissors[scissors["query"] == "freshwater_monitoring"].sort_values("year")

# Normalise both series to their 2000 baseline so the comparison is about
# growth rate, not absolute counts. This is what the paper's 200-fold vs
# 14-fold claim refers to, and it gives clean visual separation even though
# monitoring starts at a much higher absolute baseline in OpenAlex.
ml_base = ml_series[ml_series["year"] == 2000]["n_works"].iloc[0]
mon_base = mon_series[mon_series["year"] == 2000]["n_works"].iloc[0]
ml_norm = ml_series["n_works"] / ml_base
mon_norm = mon_series["n_works"] / mon_base

axC.plot(ml_series["year"], ml_norm,
         color=BLUE, linewidth=2.2, marker="o", markersize=3.5,
         label="Freshwater machine-learning papers")
axC.plot(mon_series["year"], mon_norm,
         color=ORANGE, linewidth=2.2, marker="o", markersize=3.5,
         label="Freshwater monitoring papers")

axC.set_yscale("log")
axC.set_ylim(0.7, 500)
axC.set_xlim(2000, 2025)
axC.set_ylabel("Publication rate (relative to 2000, log scale)", fontsize=9)
axC.set_xlabel("Year", fontsize=9)
axC.set_title("C   Bibliometric mismatch: models outpace monitoring",
              fontsize=10.5, pad=10)
axC.grid(which="both", axis="y", linestyle=":", linewidth=0.4,
         color="#dcdcdc", alpha=0.7)
axC.set_facecolor("white")

ml_2025 = ml_norm.iloc[-1]
mon_2025 = mon_norm.iloc[-1]
axC.text(2024.5, ml_2025 * 1.3, f"~{ml_2025:.0f}-fold growth",
         color=BLUE, fontsize=9.5, fontweight="bold", ha="right", va="bottom")
axC.text(2024.5, mon_2025 * 0.7, f"~{mon_2025:.0f}-fold growth",
         color=ORANGE, fontsize=9.5, fontweight="bold", ha="right", va="top")
axC.text(0.98, 0.03, "OpenAlex-based analysis",
         transform=axC.transAxes, fontsize=8, ha="right",
         style="italic", color="#555555")

axC.legend(loc="upper left", fontsize=8, framealpha=0.9,
           edgecolor="#dcdcdc")

# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------
for ext in ("png", "svg"):
    out = HERE / f"fig2_v40.{ext}"
    fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    print(f"wrote {out.name}")

high_rich = tedesco[tedesco["native_richness"] >= 200]
tropical = high_rich[high_rich["latitude"].between(-23.5, 23.5)]
print("\nHeadline statistics used in the caption:")
print(f"  Tedesco basins plotted: {len(tedesco):,}")
print(f"  High-richness basins (>=200): {len(high_rich)}; tropical: {100*len(tropical)/len(high_rich):.0f}%")
print(f"  NEON sites plotted: {len(neon)}")
print(f"  ILTER aquatic sites: {len(ilter_aq)}")
ml_2000_n = ml_series[ml_series["year"] == 2000]["n_works"].iloc[0]
mon_2000_n = mon_series[mon_series["year"] == 2000]["n_works"].iloc[0]
ml_2025_n = ml_series[ml_series["year"] == 2025]["n_works"].iloc[0]
mon_2025_n = mon_series[mon_series["year"] == 2025]["n_works"].iloc[0]
print(f"  ML annual rate: {ml_2000_n}/yr (2000) -> {ml_2025_n:,.0f}/yr (2025); fold change {ml_2025_n/ml_2000_n:.0f}x")
print(f"  Monitoring annual rate: {mon_2000_n}/yr (2000) -> {mon_2025_n:,.0f}/yr (2025); fold change {mon_2025_n/mon_2000_n:.0f}x")
