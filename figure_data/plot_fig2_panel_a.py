"""Plotting scaffold for Figure 2 Panel A — global monitoring sites over a
freshwater biodiversity underlay (Tedesco 2017 native fish richness).

Draft uses basin-centroid bubbles (no geopandas dependency). The final
submission figure should rasterise the Tedesco basin shapefile and render
a true choropleth. WFD/NARS/GRDC overlays and Aqueduct BWS layer are marked
with TODO placeholders.
"""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

HERE = Path(__file__).parent

# --- Underlay: Tedesco 2017 native fish richness (basin centroids) ---------
tedesco = pd.read_csv(HERE / "tedesco_basin_richness.csv")
tedesco = tedesco.dropna(subset=["latitude", "longitude"])
tedesco["latitude"] = pd.to_numeric(tedesco["latitude"], errors="coerce")
tedesco["longitude"] = pd.to_numeric(tedesco["longitude"], errors="coerce")
tedesco = tedesco.dropna(subset=["latitude", "longitude"])
tedesco = tedesco[tedesco["native_richness"] > 0]

# --- Layer 1: NEON aquatic (6+5+19) ----------------------------------------
neon = pd.read_csv(HERE / "neon_aquatic_sites.csv")
neon_colors = {"LAKE": "#1F6FB2", "RIVER": "#0D9488", "STREAM": "#60A5FA"}

# --- Layer 2: ILTER aquatic via DEIMS (205 of 1,379) -----------------------
ilter = pd.read_csv(HERE / "ilter_sites.csv")
ilter_aquatic = ilter[ilter["is_aquatic_by_name"] == True]

# --- Assembly --------------------------------------------------------------
fig, ax = plt.subplots(figsize=(14, 7))

# Basin biodiversity bubbles — size ~ native richness, warm palette
tmax = tedesco["native_richness"].max()
ax.scatter(tedesco["longitude"], tedesco["latitude"],
           s=tedesco["native_richness"] / tmax * 350 + 4,
           c=tedesco["native_richness"], cmap="YlOrRd",
           alpha=0.55, edgecolors="none", zorder=2,
           label=f"Tedesco 2017 basins (n={len(tedesco):,})")

# NEON with per-subtype colour
for subtype, colour in neon_colors.items():
    sub = neon[neon["subtype"] == subtype]
    ax.scatter(sub["longitude"], sub["latitude"],
               s=28, c=colour, edgecolors="white", linewidth=0.6,
               label=f"NEON {subtype.lower()} (n={len(sub)})", zorder=5)

# ILTER aquatic
ax.scatter(ilter_aquatic["longitude"], ilter_aquatic["latitude"],
           s=18, c="#0D9488", edgecolors="white", linewidth=0.4, alpha=0.85,
           label=f"ILTER aquatic (n={len(ilter_aquatic)})", zorder=4)

# TODO: add WFD/WISE, NARS, GRDC, GEMS/Water, GLEON (Sharma 2015) layers;
#       and Aqueduct 4.0 BWS as a semi-transparent overlay once unpacked.

ax.set_xlim(-180, 180)
ax.set_ylim(-60, 85)
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
ax.set_title("Figure 2A — Global freshwater monitoring is concentrated where fish biodiversity is lowest\n"
             "(Tedesco 2017 basin richness underlay; NEON + ILTER sites overlaid; WFD/NARS/GRDC pending)")
ax.legend(loc="lower left", fontsize=8, framealpha=0.9)
ax.grid(True, linestyle=":", linewidth=0.4, alpha=0.5)
ax.set_aspect("equal")

out = HERE / "fig2a_draft.png"
fig.savefig(out, dpi=200, bbox_inches="tight")
print(f"Saved draft -> {out.name}")
print(f"  Tedesco basins plotted: {len(tedesco):,}")
print(f"  NEON sites plotted: {len(neon)}")
print(f"  ILTER aquatic plotted: {len(ilter_aquatic)}")
# Headline comparison for the caption
high_rich = tedesco[tedesco["native_richness"] >= 200]
tropical = high_rich[(high_rich["latitude"].between(-23.5, 23.5))]
print(f"  High-richness basins (>=200 native fish): {len(high_rich):,}; of those in tropics: {len(tropical):,} ({100*len(tropical)/len(high_rich):.0f}%)")
print(f"  NEON sites in tropics: {((neon['latitude'].between(-23.5,23.5)).sum())}")
