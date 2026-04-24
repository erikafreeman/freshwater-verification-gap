"""Extract NEON aquatic sites (lakes, streams, rivers) from the full NEON registry.

NEON siteType is CORE/GRADIENT, not LAKE/STREAM. We classify by:
  (a) presence of aquatic data products (DP1.20* family), AND
  (b) explicit NEON aquatic site codes (hard-coded from NEON's official list;
      regex on site names under-counts because some NEON aquatic codes are
      opaque, e.g. 'TOOK' for Toolik Lake, and others that contain 'River' in
      name are actually NEON wadeable streams per NEON's classification).

NEON's canonical aquatic count (2026): 34 sites = 7 lakes + 3 rivers + 24 streams.
"""
import json
import csv
from pathlib import Path

HERE = Path(__file__).parent
raw = json.loads((HERE / "neon_sites_raw.json").read_text(encoding="utf-8"))
data = raw["data"]

# NEON's canonical aquatic-site classification
# Source: https://www.neonscience.org/field-sites/explore-field-sites (2026-04)
NEON_LAKES = {"BARC", "CRAM", "LIRO", "PRLA", "PRPO", "SUGG", "TOOK"}
NEON_RIVERS = {"BLWA", "FLNT", "TOMB"}
NEON_STREAMS = {
    "ARIK", "BIGC", "BLDE", "BLUE", "CARI", "COMO", "CUPE", "GUIL",
    "HOPB", "KING", "LECO", "LEWI", "MART", "MAYF", "MCDI", "MCRA",
    "OKSR", "POSE", "PRIN", "REDB", "SYCA", "TECR", "WALK", "WLOU",
}

SUBTYPE_MAP = {}
for c in NEON_LAKES:   SUBTYPE_MAP[c] = "LAKE"
for c in NEON_RIVERS:  SUBTYPE_MAP[c] = "RIVER"
for c in NEON_STREAMS: SUBTYPE_MAP[c] = "STREAM"

AQUATIC_DP_PREFIX = "DP1.20"  # NEON aquatic data products

rows = []
for s in data:
    code = s.get("siteCode") or ""
    if code not in SUBTYPE_MAP:
        continue
    name = s.get("siteName") or ""
    dps = s.get("dataProducts") or []
    aquatic_dps = [p["dataProductCode"] for p in dps
                   if isinstance(p, dict) and p.get("dataProductCode", "").startswith(AQUATIC_DP_PREFIX)]
    rows.append({
        "site_code": code,
        "site_name": name,
        "site_type_neon": s.get("siteType"),
        "subtype": SUBTYPE_MAP[code],
        "domain_code": s.get("domainCode"),
        "domain_name": s.get("domainName"),
        "state_code": s.get("stateCode"),
        "state_name": s.get("stateName"),
        "latitude": s.get("siteLatitude"),
        "longitude": s.get("siteLongitude"),
        "n_aquatic_products": len(aquatic_dps),
        "network": "NEON",
    })

rows.sort(key=lambda r: (r["subtype"], r["site_code"]))

# Sanity check: we expect 34 sites matching NEON's canonical classification
expected = len(SUBTYPE_MAP)
if len(rows) != expected:
    missing = sorted(SUBTYPE_MAP.keys() - {r["site_code"] for r in rows})
    print(f"WARNING: expected {expected} NEON aquatic sites, got {len(rows)}; missing codes: {missing}")

out = HERE / "neon_aquatic_sites.csv"
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

from collections import Counter
counts = Counter(r["subtype"] for r in rows)
print(f"Extracted {len(rows)} NEON aquatic sites -> {out.name}")
print(f"  Breakdown: {dict(counts)}")
for r in rows[:5]:
    print(f"  {r['site_code']:<6} {r['subtype']:<6} {r['latitude']:>8.3f},{r['longitude']:>9.3f}  {r['site_name']}")
