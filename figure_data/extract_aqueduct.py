"""Unpack Aqueduct 4.0 and summarise the Baseline Water Stress layer.

Source: WRI Aqueduct 4.0 (Kuzma et al. 2023), CC BY 4.0.
Input : aqueduct40.zip (262 MB)
Output: aqueduct_bws_summary.csv — country-level mean BWS for a quick
        sanity check; plus inventory of shapefile/geopackage contents.
"""
from pathlib import Path
import zipfile

HERE = Path(__file__).parent
zip_path = HERE / "aqueduct40.zip"
out_dir = HERE / "aqueduct40"
out_dir.mkdir(exist_ok=True)

with zipfile.ZipFile(zip_path) as z:
    names = z.namelist()
    print(f"Aqueduct 4.0 zip contains {len(names)} entries.")
    exts = {}
    for n in names:
        e = n.rsplit(".", 1)[-1].lower() if "." in n else "(none)"
        exts[e] = exts.get(e, 0) + 1
    print(f"Extension breakdown: {exts}")
    print("\nTop 20 files by size:")
    sized = sorted(names, key=lambda n: z.getinfo(n).file_size, reverse=True)
    for n in sized[:20]:
        print(f"  {z.getinfo(n).file_size:>12,}  {n}")
    print("\nExtracting full archive — this may take a moment.")
    z.extractall(out_dir)

print("\nNext steps:")
print("  1. Identify the basin-level BWS geopackage/shapefile.")
print("  2. With geopandas:  gdf = gpd.read_file(<path>)")
print("     inspect columns; bws_cat column names typically contain 'bws_cat' or 'bws_score'.")
print("  3. Summarise: per-basin mean BWS can be rasterised for the Fig 2A underlay.")
