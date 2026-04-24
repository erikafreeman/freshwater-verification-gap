"""Plotting scaffold for Figure 4 — the scissors.

Two panels side-by-side:
  (a) Annual rate on log-y — the scissors shape is clearest here.
  (b) Ratio of model publications to monitoring publications, by year.

Cumulative plotting mutes the effect because monitoring has a 50-year legacy
while ML is a decade old; annual rates show the post-2018 divergence.
"""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

HERE = Path(__file__).parent
df = pd.read_csv(HERE / "scissors_publications_by_year.csv")
df = df[(df["year"] >= 2000) & (df["year"] <= 2025)]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))

# --- Panel (a): annual rate, log y ---------------------------------------
series_style = {
    "freshwater_ml":         dict(colour="#1F6FB2", label="ML / AI freshwater", lw=2.6),
    "freshwater_prediction": dict(colour="#60A5FA", label="Freshwater prediction", lw=2.0),
    "freshwater_model":      dict(colour="#93C5FD", label="Freshwater models (broad)", lw=1.6),
    "freshwater_monitoring": dict(colour="#D97706", label="Freshwater monitoring", lw=2.6),
}
for q, s in series_style.items():
    sub = df[df["query"] == q].sort_values("year")
    ax1.plot(sub["year"], sub["n_works"], color=s["colour"], linewidth=s["lw"], label=s["label"])

ax1.set_yscale("log")
ax1.set_xlabel("Year")
ax1.set_ylabel("Publications per year (log)")
ax1.set_title("(a) Model-adjacent publications outpace monitoring", loc="left", fontsize=11)
ax1.axvline(2018, color="grey", linestyle="--", linewidth=1, alpha=0.6)
ax1.text(2018.3, ax1.get_ylim()[1] * 0.5,
         "AI inflection\n(model generation:\nyears → weeks)",
         fontsize=8, va="top", color="#374151")
ax1.legend(loc="upper left", fontsize=8, framealpha=0.9)
ax1.grid(True, which="both", linestyle=":", linewidth=0.4, alpha=0.4)

# --- Panel (b): ratio, model-adjacent / monitoring -----------------------
pivot = df.pivot_table(index="year", columns="query", values="n_works").fillna(0)
pivot["ml_over_mon"]    = pivot["freshwater_ml"]         / pivot["freshwater_monitoring"]
pivot["pred_over_mon"]  = pivot["freshwater_prediction"] / pivot["freshwater_monitoring"]
pivot["model_over_mon"] = pivot["freshwater_model"]      / pivot["freshwater_monitoring"]

ax2.plot(pivot.index, pivot["ml_over_mon"],    color="#1F6FB2", linewidth=2.6, label="ML / monitoring")
ax2.plot(pivot.index, pivot["pred_over_mon"],  color="#60A5FA", linewidth=2.0, label="Prediction / monitoring")
ax2.plot(pivot.index, pivot["model_over_mon"], color="#93C5FD", linewidth=1.6, label="Models (broad) / monitoring")
ax2.axhline(1, color="grey", linestyle="-", linewidth=0.8, alpha=0.5)
ax2.axvline(2018, color="grey", linestyle="--", linewidth=1, alpha=0.6)

ax2.set_xlabel("Year")
ax2.set_ylabel("Publications per year (ratio to monitoring)")
ax2.set_title("(b) The gap is widening: model growth per monitoring paper", loc="left", fontsize=11)
ax2.legend(loc="upper left", fontsize=8, framealpha=0.9)
ax2.grid(True, linestyle=":", linewidth=0.4, alpha=0.4)

fig.suptitle("Figure 4 — Model generation has accelerated; observational capacity has not.",
             fontsize=12, y=1.02, x=0.02, ha="left")
fig.text(0.01, -0.04,
         "Source: OpenAlex (api.openalex.org) keyword search across 2000–2025 — raw matches, not curated corpus.",
         fontsize=8, style="italic", color="#6B7280")

out = HERE / "fig4_draft.png"
fig.savefig(out, dpi=200, bbox_inches="tight")
print(f"Saved draft -> {out.name}")

# Report headline numbers
def at(q, y):
    m = df[(df["query"] == q) & (df["year"] == y)]
    return int(m["n_works"].iloc[0]) if len(m) else 0

for q in series_style:
    a, b = at(q, 2000), at(q, 2025)
    print(f"  {q:<22} {a:>6,}/yr (2000) -> {b:>6,}/yr (2025)   growth {b/max(a,1):.1f}x")
print(f"\n  ML / monitoring ratio: 2000 = {pivot['ml_over_mon'].iloc[0]:.2f};  2025 = {pivot['ml_over_mon'].iloc[-1]:.2f}")
