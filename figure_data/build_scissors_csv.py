"""Merge OpenAlex yearly publication counts into a single tidy CSV for Figure 4.

Produces:
  scissors_publications_by_year.csv with columns:
    year, query, n_works, cumulative

Scope: 2000–2026. OpenAlex coverage before ~1990 is patchy; cap at 2000 for the
figure. 2026 and 2027 are partial and should be excluded from the plot but are
kept in the CSV for transparency.
"""
import json
import csv
from pathlib import Path

HERE = Path(__file__).parent

queries = {
    "freshwater_model":      "openalex_freshwater_models_by_year.json",
    "freshwater_prediction": "openalex_freshwater_prediction_by_year.json",
    "freshwater_ml":         "openalex_freshwater_ml_by_year.json",
    "freshwater_monitoring": "openalex_freshwater_monitoring_by_year.json",
}

rows = []
for q, fname in queries.items():
    d = json.loads((HERE / fname).read_text(encoding="utf-8"))
    buckets = d.get("group_by", [])
    per_year = {}
    for b in buckets:
        y = b.get("key")
        if not y:
            continue
        try:
            yi = int(y)
        except ValueError:
            continue
        if 2000 <= yi <= 2026:
            per_year[yi] = b.get("count", 0)

    cum = 0
    for y in sorted(per_year):
        cum += per_year[y]
        rows.append({"year": y, "query": q, "n_works": per_year[y], "cumulative": cum})

rows.sort(key=lambda r: (r["query"], r["year"]))
out = HERE / "scissors_publications_by_year.csv"
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["year", "query", "n_works", "cumulative"])
    w.writeheader()
    w.writerows(rows)

print(f"Wrote {len(rows)} rows -> {out.name}")
for q in queries:
    sub = [r for r in rows if r["query"] == q]
    if not sub:
        continue
    first, last = sub[0], sub[-1]
    growth = (last["n_works"] / first["n_works"]) if first["n_works"] else float("nan")
    print(f"  {q}: {first['year']} {first['n_works']:,}/yr -> {last['year']} {last['n_works']:,}/yr  "
          f"({growth:.1f}x); cumulative total {last['cumulative']:,}")
