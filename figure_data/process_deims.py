"""Process DEIMS-SDR ILTER site registry into CSV.

DEIMS returns site records with WKT POINT coordinates. We parse those into
lat/lon and classify by name keywords into aquatic vs terrestrial so the
aquatic subset can be plotted on Figure 2 Panel A.
"""
import json
import csv
import re
from pathlib import Path

HERE = Path(__file__).parent
raw = json.loads((HERE / "deims_all_sites.json").read_text(encoding="utf-8"))

POINT_RE = re.compile(r"POINT\s*\(\s*(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)\s*\)")
AQUATIC_KWS = ["lake", "river", "stream", "creek", "estuary", "lagoon",
               "pond", "reservoir", "wetland", "marsh", "bog", "mire",
               "catchment", "watershed", "basin", "floodplain", "coastal",
               "fjord", "delta"]

rows = []
for site in raw:
    title = site.get("title") or ""
    sid = site.get("id", {}).get("suffix") or ""
    coord = site.get("coordinates") or ""
    m = POINT_RE.search(coord)
    if not m:
        continue
    lon, lat = float(m.group(1)), float(m.group(2))
    name_lower = title.lower()
    is_aquatic = any(kw in name_lower for kw in AQUATIC_KWS)
    country = title.split(" - ")[-1].strip() if " - " in title else ""
    rows.append({
        "site_id": sid,
        "site_name": title,
        "country_guess": country,
        "latitude": lat,
        "longitude": lon,
        "is_aquatic_by_name": is_aquatic,
        "network": "ILTER/DEIMS-SDR",
    })

rows.sort(key=lambda r: (not r["is_aquatic_by_name"], r["site_name"]))

out = HERE / "ilter_sites.csv"
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

aquatic = [r for r in rows if r["is_aquatic_by_name"]]
print(f"Parsed {len(rows)} ILTER sites with coordinates -> {out.name}")
print(f"  Aquatic-by-name: {len(aquatic)} ({100*len(aquatic)/len(rows):.0f}%)")
print("  Sample aquatic sites:")
for r in aquatic[:5]:
    print(f"    {r['latitude']:>8.3f},{r['longitude']:>9.3f}  {r['site_name']}")
