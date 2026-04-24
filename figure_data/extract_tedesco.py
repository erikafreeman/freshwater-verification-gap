"""Extract and summarise Tedesco et al. 2017 freshwater fish occurrences.

Source: Figshare DOI 10.6084/m9.figshare.c.3739145_D5.v1, CC0.
Input : tedesco_2017.zip (31 MB)
Output: tedesco_basin_richness.csv — per HydroBASIN richness counts for
        join to Figure 2A underlay.

Tedesco's deposit ships species × basin occurrences keyed to HydroBASINS
level 8 IDs. We aggregate to unique-species-per-basin.
"""
from pathlib import Path
import zipfile
import csv
import io
from collections import defaultdict

HERE = Path(__file__).parent
zip_path = HERE / "tedesco_2017.zip"
out_dir = HERE / "tedesco_2017"
out_dir.mkdir(exist_ok=True)

with zipfile.ZipFile(zip_path) as z:
    names = z.namelist()
    print(f"Tedesco zip contains {len(names)} entries. Sample:")
    for n in names[:15]:
        info = z.getinfo(n)
        print(f"  {n}  ({info.file_size:,} bytes)")
    # Extract everything to a subfolder for inspection
    z.extractall(out_dir)

# Look for the occurrence table — file names vary across Figshare deposits.
candidate = None
for n in names:
    low = n.lower()
    if low.endswith((".csv", ".tsv", ".txt")) and ("occ" in low or "species" in low or "database" in low):
        candidate = out_dir / n
        break
if not candidate:
    for n in names:
        if n.lower().endswith((".csv", ".tsv", ".txt")):
            candidate = out_dir / n
            break

print(f"\nFirst likely data file: {candidate}")
if candidate and candidate.exists():
    with open(candidate, encoding="utf-8", errors="replace") as f:
        head = [next(f) for _ in range(5)]
    print("Header rows:")
    for h in head:
        print("  ", h.rstrip()[:150])

# The actual aggregation will run only once we know the column names — leave
# as a manual step after inspection.
print("\nNext step: inspect column names above, then add the aggregate block:")
print("  species_col = ...; basin_col = ...; etc.")
