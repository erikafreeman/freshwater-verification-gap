"""Convert GBIF country-level human-observation counts into a CSV for Figure 2A."""
import json
import csv
from pathlib import Path

HERE = Path(__file__).parent
d = json.loads((HERE / "gbif_country_effort_raw.json").read_text(encoding="utf-8"))
total = d.get("count", 0)
facets = d.get("facets", [])
counts = facets[0]["counts"] if facets else []

rows = []
for c in counts:
    rows.append({
        "iso2": c["name"],
        "occurrence_records": c["count"],
        "share_pct": round(100 * c["count"] / total, 4),
    })

out = HERE / "gbif_country_effort.csv"
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

print(f"Wrote {len(rows)} countries -> {out.name}")
print(f"Total occurrence records: {total:,}")
print(f"Top 5 countries hold {sum(r['share_pct'] for r in rows[:5]):.1f}% of all records")
print(f"Bottom 50% of countries (by record count) hold {sum(r['share_pct'] for r in rows[len(rows)//2:]):.2f}%")
