"""Plotting scaffold for Figure 2 Panel B — variable dynamics vs sampling frequency.

Consumes panel_b_timescales.csv. Produces horizontal log-scale bar groups:
  Top group  : characteristic timescales of freshwater variables (blue)
  Bottom     : typical cadence of monitoring programmes (warm)
The mismatch — programme bars sitting to the right of the matched variable bars
for most pairs — is the figure's point.
"""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

HERE = Path(__file__).parent
df = pd.read_csv(HERE / "panel_b_timescales.csv")

var_df = df[df["group"] == "variable_dynamics"].sort_values("anchor_days")
freq_df = df[df["group"] == "sampling_frequency"].sort_values("anchor_days")

fig, ax = plt.subplots(figsize=(11, 6.5))

def draw_group(sub, y_offset, colour, label_suffix):
    for i, (_, r) in enumerate(sub.iterrows()):
        y = y_offset + i
        ax.barh(y, r["high_days"] - r["low_days"], left=r["low_days"],
                height=0.65, color=colour, edgecolor="white", linewidth=1, alpha=0.85)
        ax.plot([r["anchor_days"]], [y], marker="|", color="black", markersize=10, markeredgewidth=1.2)
        ax.text(r["high_days"] * 1.15, y, r["label"], va="center", fontsize=9)

BAND_GAP = 1.5
var_y0 = len(freq_df) + BAND_GAP
draw_group(freq_df, 0, "#D97706", "sampling")
draw_group(var_df, var_y0, "#1F6FB2", "variable")

# Forecast-relevant window (days-to-weeks) shaded
ax.axvspan(1, 30, color="#FEF3C7", alpha=0.4, zorder=-1)
ax.text(5, var_y0 + len(var_df) - 0.3, "Forecast-relevant window (1–30 d)",
        fontsize=9, style="italic", ha="center", color="#92400E")

ax.set_xscale("log")
ax.set_xticks([1/24, 1, 7, 30, 365, 365*5])
ax.set_xticklabels(["1 h", "1 d", "1 wk", "1 mo", "1 yr", "5 yr"])
ax.set_xlim(1/48, 365*6)
ax.set_yticks([])
ax.set_ylabel("")
ax.set_xlabel("Characteristic timescale (log)")
ax.set_title("Figure 2B — Sampling cadence lags variable dynamics across freshwater programmes",
             loc="left", fontsize=11)

# Group labels
ax.text(0.01, var_y0 + len(var_df) - 0.5, "Variable dynamics",
        transform=ax.get_yaxis_transform(), fontsize=10, fontweight="bold", color="#1F6FB2")
ax.text(0.01, len(freq_df) - 0.5, "Sampling frequency",
        transform=ax.get_yaxis_transform(), fontsize=10, fontweight="bold", color="#D97706")

for spine in ("top", "right"):
    ax.spines[spine].set_visible(False)

out = HERE / "fig2b_draft.png"
fig.savefig(out, dpi=200, bbox_inches="tight")
print(f"Saved draft -> {out.name}")
print(f"  Variable bars: {len(var_df)}; Programme bars: {len(freq_df)}")
