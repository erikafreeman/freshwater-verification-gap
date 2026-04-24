"""Aggregate Aqueduct 4.0 baseline annual BWS to two tidy CSVs.

Output:
  aqueduct_basins.csv    — slim basin-level (pfaf_id, country, area_km2, BWS)
  aqueduct_by_country.csv — area-weighted mean BWS score per country + dominant category

The per-basin CSV drives the final Fig 2A underlay (once geopandas is available
and pfaf_id can be joined to HydroBASINS polygons). The per-country CSV lets us
cross-tabulate water stress against GBIF observer effort without geopandas.
"""
from pathlib import Path
import csv
from collections import defaultdict

HERE = Path(__file__).parent
src = HERE / "aqueduct40" / "Aqueduct40_waterrisk_download_Y2023M07D05" / "CVS" / "Aqueduct40_baseline_annual_y2023m07d05.csv"

basin_rows = []
by_country = defaultdict(lambda: {"n_basins": 0, "area_km2": 0.0, "weighted_bws": 0.0, "cat_counts": defaultdict(int)})

with open(src, encoding="utf-8", errors="replace", newline="") as f:
    reader = csv.DictReader(f)
    for r in reader:
        pfaf = r.get("pfaf_id") or ""
        country = r.get("name_0") or ""
        try:
            area = float(r.get("area_km2") or 0)
        except ValueError:
            area = 0
        try:
            bws = float(r.get("bws_score") or "nan")
        except ValueError:
            bws = float("nan")
        try:
            cat = int(float(r.get("bws_cat") or "-1"))
        except ValueError:
            cat = -1
        label = r.get("bws_label") or ""
        # bws_raw = 9999 means data missing; skip from country aggregate
        is_valid = bws == bws and bws >= 0 and bws <= 5
        basin_rows.append({
            "pfaf_id": pfaf, "country": country, "area_km2": round(area, 4),
            "bws_score": bws if is_valid else "", "bws_cat": cat if is_valid else "",
            "bws_label": label if is_valid else "",
        })
        if is_valid and country and area > 0:
            c = by_country[country]
            c["n_basins"] += 1
            c["area_km2"] += area
            c["weighted_bws"] += area * bws
            c["cat_counts"][cat] += 1

out1 = HERE / "aqueduct_basins.csv"
with open(out1, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(basin_rows[0].keys()))
    w.writeheader()
    w.writerows(basin_rows)
print(f"Wrote {len(basin_rows):,} basin rows -> {out1.name}")

country_rows = []
for country, c in by_country.items():
    if c["area_km2"] == 0:
        continue
    mean_bws = c["weighted_bws"] / c["area_km2"]
    dominant = max(c["cat_counts"].items(), key=lambda x: x[1])[0]
    country_rows.append({
        "country": country,
        "n_basins": c["n_basins"],
        "total_area_km2": round(c["area_km2"], 1),
        "area_weighted_bws_score": round(mean_bws, 3),
        "dominant_bws_cat": dominant,
    })
country_rows.sort(key=lambda r: r["area_weighted_bws_score"], reverse=True)

out2 = HERE / "aqueduct_by_country.csv"
with open(out2, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(country_rows[0].keys()))
    w.writeheader()
    w.writerows(country_rows)

print(f"Wrote {len(country_rows):,} country aggregates -> {out2.name}")
print("\nTop 15 most water-stressed countries (area-weighted BWS):")
for r in country_rows[:15]:
    print(f"  {r['area_weighted_bws_score']:>5.2f}  {r['country']:<35} {r['n_basins']:>5} basins")
print("\nLeast-stressed:")
for r in country_rows[-5:]:
    print(f"  {r['area_weighted_bws_score']:>5.2f}  {r['country']:<35} {r['n_basins']:>5} basins")
