"""Compute per-basin native fish species richness from Tedesco 2017.

Joins occurrence table to basin table. Output columns:
  basin_code, basin_name, native_richness, exotic_richness, total_richness,
  latitude, longitude (basin centroid), area_km2 (if present).
"""
from pathlib import Path
import csv
from collections import defaultdict

HERE = Path(__file__).parent
TDIR = HERE / "tedesco_2017"

occ = TDIR / "Occurrence_Table.csv"
basins = TDIR / "Drainage_Basins_Table.csv"

with open(basins, encoding="utf-8", errors="replace") as f:
    first = f.readline().rstrip()
print("Basin table header:", first[:200])

with open(occ, encoding="utf-8", errors="replace") as f:
    first = f.readline().rstrip()
print("Occurrence table header:", first[:200])

def read_sep_csv(path):
    with open(path, encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        return reader.fieldnames, list(reader)

basin_cols, basin_rows = read_sep_csv(basins)
occ_cols,   occ_rows   = read_sep_csv(occ)
print(f"\nBasin table cols: {basin_cols}")
print(f"Occurrence rows: {len(occ_rows):,}")
print(f"Basin rows: {len(basin_rows):,}")

basin_key_occ = "1.Basin.Name"
species_key = "6.Fishbase.Valid.Species.Name"
status_key = "3.Native.Exotic.Status"

native_counts = defaultdict(set)
exotic_counts = defaultdict(set)
for r in occ_rows:
    b = r[basin_key_occ]
    sp = r[species_key]
    if not sp:
        continue
    if r[status_key] == "native":
        native_counts[b].add(sp)
    elif r[status_key] == "exotic":
        exotic_counts[b].add(sp)

# Find coordinate columns in basin table
lat_col = next((c for c in basin_cols if "lat" in c.lower()), None)
lon_col = next((c for c in basin_cols if "lon" in c.lower() or "long" in c.lower()), None)
name_col = next((c for c in basin_cols if "basin" in c.lower() and "name" in c.lower()), basin_cols[0])
id_col = next((c for c in basin_cols if "id" in c.lower() or "code" in c.lower()), basin_cols[0])
print(f"\nUsing id_col={id_col!r}, name_col={name_col!r}, lat_col={lat_col!r}, lon_col={lon_col!r}")

rows = []
for b in basin_rows:
    key = b[basin_cols[0]]  # basin code, first column
    nat = len(native_counts.get(key, set()))
    exo = len(exotic_counts.get(key, set()))
    rows.append({
        "basin_code": key,
        "basin_name": b.get(name_col, ""),
        "native_richness": nat,
        "exotic_richness": exo,
        "total_richness": nat + exo,
        "latitude": b.get(lat_col, "") if lat_col else "",
        "longitude": b.get(lon_col, "") if lon_col else "",
    })

rows.sort(key=lambda r: r["native_richness"], reverse=True)
out = HERE / "tedesco_basin_richness.csv"
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

print(f"\nWrote {len(rows):,} basins -> {out.name}")
total_basins = len(rows)
nonzero = sum(1 for r in rows if r["native_richness"] > 0)
print(f"  Basins with >=1 native species: {nonzero:,} ({100*nonzero/total_basins:.1f}%)")
print("  Top 10 basins by native fish richness:")
for r in rows[:10]:
    print(f"    {r['native_richness']:>5}  {r['basin_name'][:50]:<50}  {r['latitude']},{r['longitude']}")
