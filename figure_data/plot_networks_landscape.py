"""Supplementary Figure S1 — freshwater monitoring networks landscape.

Redesigned for publication-quality presentation:
  - simplified color palette (5 super-categories, not 13 sub-types)
  - subtle coverage-tier background bands for depth without clutter
  - labels placed with collision-aware offsets + thin leader lines
  - cleaner typography and a narrower title
  - single-colour marker edges for a uniform, less patchwork look
"""
from pathlib import Path
import math
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

HERE = Path(__file__).parent
df = pd.read_csv(HERE / "networks_landscape.csv")

# ---------------------------------------------------------------------------
# Data preparation
# ---------------------------------------------------------------------------
# Collapse the 13 sample_type values into 5 super-categories for visual clarity
SUPERCAT = {
    "multi-variable":       ("In-situ (multi-variable)", "#1F6FB2"),
    "physical+chemistry":   ("In-situ (hydrology / WQ)",  "#2A6EBB"),
    "hydrology":            ("In-situ (hydrology / WQ)",  "#2A6EBB"),
    "hydrology+chemistry":  ("In-situ (hydrology / WQ)",  "#2A6EBB"),
    "chemistry":            ("In-situ (hydrology / WQ)",  "#2A6EBB"),
    "chemistry+biology":    ("In-situ (biology)",          "#16A34A"),
    "biology":              ("In-situ (biology)",          "#16A34A"),
    "biodiversity":         ("Biodiversity (aggregators)", "#84CC16"),
    "citizen-chemistry":    ("Citizen science",            "#F59E0B"),
    "citizen-biology":      ("Citizen science",            "#F59E0B"),
    "citizen-hydrology":    ("Citizen science",            "#F59E0B"),
    "remote-sensing":       ("Remote sensing",             "#A855F7"),
    "water-stress":         ("Pressure / stress",          "#6B7280"),
}
df["supercat"] = df["sample_type"].map(lambda s: SUPERCAT.get(s, ("Other", "#9CA3AF"))[0])
df["colour"]   = df["sample_type"].map(lambda s: SUPERCAT.get(s, ("Other", "#9CA3AF"))[1])

COVERAGE_ORDER = ["sub-national", "national", "continental", "global"]
COV_Y = {c: i + 1 for i, c in enumerate(COVERAGE_ORDER)}
df["y"] = df["coverage_level"].map(COV_Y)

df["x"] = df["frequency_days"].replace(0, 365 * 12)  # static → right edge

# Uniform marker size — the previous size-by-log-count legend mixed "sites"
# (physical stations) with "records" (observations), which was not a
# coherent scale. Keep the visualisation focused on the two dimensions that
# matter most: sampling frequency (x) and geographic coverage (y).
df["marker_size"] = 150  # uniform ~8 pt diameter

# ---------------------------------------------------------------------------
# Figure
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(13, 7.2))

# Coverage-tier background bands (alternating very-light fills)
for i, y in enumerate([1, 2, 3, 4]):
    if i % 2 == 0:
        ax.axhspan(y - 0.5, y + 0.5, color="#F9FAFB", zorder=0)

# Forecast-relevant window shaded band
ax.axvspan(1 / 24, 30, color="#FEF3C7", alpha=0.35, zorder=1)
ax.text(
    math.sqrt(1 / 24 * 30),
    4.45,
    "F O R E C A S T - R E L E V A N T   W I N D O W",
    color="#92400E",
    fontsize=8,
    fontweight="bold",
    ha="center",
    va="center",
)

# Thin grid lines at each coverage tier
for y in [1, 2, 3, 4]:
    ax.axhline(y, color="#E5E7EB", linewidth=0.8, linestyle="-", zorder=0.5)

# Deterministic jitter: tie-break y positions within a coverage tier
# by spreading across a small vertical offset relative to rank within tier.
def assign_jitter(group):
    n = len(group)
    # Distribute points over ±0.32 within the tier based on x rank
    order = group["x"].rank(method="first").astype(int).values - 1
    if n == 1:
        return pd.Series([0.0], index=group.index)
    offsets = ((order / max(n - 1, 1)) - 0.5) * 0.64
    return pd.Series(offsets, index=group.index)

df["jitter"] = df.groupby("y", group_keys=False).apply(assign_jitter)
df["y_plot"] = df["y"] + df["jitter"]

# Scatter
for supercat, sub in df.groupby("supercat"):
    ax.scatter(
        sub["x"], sub["y_plot"],
        s=sub["marker_size"],
        c=sub["colour"],
        alpha=0.88,
        edgecolors="white",
        linewidth=1.0,
        zorder=4,
        label=supercat,
    )

# ---------------------------------------------------------------------------
# Label placement with leader lines
# ---------------------------------------------------------------------------
# For each point, choose a label position: alternate above / below the point
# based on whether its neighbours cluster nearby.
import numpy as np
points = list(zip(df["x"].values, df["y_plot"].values, df["network"].values))

placements = []  # list of (x, y, text, anchor_x, anchor_y)
used_positions = []  # [(x, y)] already placed labels, to avoid crashes

def find_position(cx, cy, label_w_est):
    """Find a non-overlapping label position near (cx, cy)."""
    # Try a series of radial offsets
    candidates = [
        (cx * 1.20, cy + 0.22),  # up-right
        (cx * 0.83, cy + 0.22),  # up-left
        (cx * 1.20, cy - 0.22),  # down-right
        (cx * 0.83, cy - 0.22),  # down-left
        (cx * 1.45, cy),          # far right
        (cx * 0.70, cy),          # far left
        (cx * 1.20, cy + 0.40),   # up-right far
        (cx * 0.83, cy - 0.40),   # down-left far
    ]
    for lx, ly in candidates:
        # Check distance to already-placed labels
        conflict = False
        for ux, uy in used_positions:
            dx = math.log10(max(lx, 0.01) / max(ux, 0.01))
            dy = ly - uy
            if abs(dx) < 0.20 and abs(dy) < 0.22:
                conflict = True
                break
        if not conflict:
            used_positions.append((lx, ly))
            return lx, ly
    # Fallback: near the point with small offset
    return cx * 1.1, cy + 0.15

for (cx, cy, name) in points:
    lx, ly = find_position(cx, cy, len(name) * 0.04)
    placements.append((lx, ly, name, cx, cy))

# Draw leader lines first (so markers are on top)
for (lx, ly, name, cx, cy) in placements:
    ax.plot([cx, lx], [cy, ly], color="#9CA3AF", linewidth=0.5, alpha=0.55, zorder=2)

# Then draw labels
for (lx, ly, name, cx, cy) in placements:
    ax.text(
        lx, ly, name,
        fontsize=7.5, color="#111827",
        ha="left" if lx > cx else "right",
        va="center",
        zorder=5,
        bbox=dict(facecolor="white", edgecolor="none", alpha=0.75, pad=1.0),
    )

# ---------------------------------------------------------------------------
# Axes + labels
# ---------------------------------------------------------------------------
ax.set_xscale("log")
ax.set_xlim(1 / 48, 365 * 40)
ax.set_xticks([1 / 24, 1, 7, 30, 365, 365 * 5, 365 * 12])
ax.set_xticklabels(["1 hour", "1 day", "1 week", "1 month", "1 year", "5 years", "static"],
                   fontsize=9)
ax.set_xlabel("Typical sampling frequency (log scale)", fontsize=10, color="#374151")

ax.set_yticks([1, 2, 3, 4])
ax.set_yticklabels(["Sub-national", "National", "Continental", "Global"],
                   fontsize=9)
ax.set_ylim(0.5, 4.6)
ax.set_ylabel("Geographic coverage", fontsize=10, color="#374151")

# Title
fig.suptitle(
    "Freshwater monitoring networks: frequency and coverage",
    fontsize=13, fontweight="bold", color="#111827",
    x=0.02, ha="left", y=0.97,
)
fig.text(
    0.02, 0.932,
    "No in-situ network occupies the high-frequency × global corner; only satellite remote sensing delivers that combination.",
    fontsize=9, color="#6B7280", ha="left",
)

# Remove spines
for spine in ("top", "right"):
    ax.spines[spine].set_visible(False)
ax.spines["left"].set_color("#D1D5DB")
ax.spines["bottom"].set_color("#D1D5DB")
ax.tick_params(colors="#6B7280")

# Legend — super-categories only, positioned outside
legend_categories = [
    "In-situ (multi-variable)",
    "In-situ (hydrology / WQ)",
    "In-situ (biology)",
    "Biodiversity (aggregators)",
    "Citizen science",
    "Remote sensing",
    "Pressure / stress",
]
legend_elements = [
    Line2D([0], [0], marker="o", color="w",
           markerfacecolor=next(c for s, (cat, c) in SUPERCAT.items() if cat == label),
           markersize=9, label=label)
    for label in legend_categories
]
ax.legend(
    handles=legend_elements,
    title="Category",
    loc="lower left",
    bbox_to_anchor=(1.01, 0.35),
    fontsize=8, title_fontsize=9,
    frameon=False,
)

fig.subplots_adjust(left=0.06, right=0.82, top=0.88, bottom=0.08)

for ext in ("png", "svg"):
    out = HERE / f"networks_landscape.{ext}"
    fig.savefig(out, dpi=300, bbox_inches="tight")
    print(f"wrote {out.name}")
