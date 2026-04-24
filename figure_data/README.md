# Figure reproducibility — Nature Water Perspective

All data and code behind **Figure 2** of the manuscript
(`freshwater_prediction_v40_naturewater.md`). The pipeline is fully
reproducible from public sources: each raw dataset is downloaded from its
authoritative host, processed to a tidy CSV, and composed into the final
three-panel figure.

Figures 1 and 3 are conceptual schematics and are not built by this
pipeline; they are generated from the prompts in
`../figure_prompts_gemini.md`.

## Quick start

```bash
# From the figure_data/ directory:
pip install -r requirements.txt
make all       # fetch + process + plot in one go
```

This produces `fig2_v40.png` (300 dpi) and `fig2_v40.svg`, plus tidy
intermediate CSVs that can be inspected or re-used.

Re-running `make all` is a no-op if inputs haven't changed. Use `make clean`
to wipe all generated files (keeps raw zips for offline work) or
`make distclean` to remove the raw archives too.

## Data sources and licences

| Dataset | Used in | Source | Licence |
|---|---|---|---|
| NEON aquatic site registry | Panel A | `data.neonscience.org/api/v0/sites` | CC0 (US federal) |
| ILTER global site registry via DEIMS-SDR | Panel A | `deims.org/api/sites` | CC BY (per DEIMS TOS) |
| Tedesco *et al.* 2017 freshwater fish × drainage basin | Panel A | Figshare 5245072 | CC0 |
| GBIF country-level observer effort | Panel A legend | `api.gbif.org/v1/occurrence/search` | CC BY per dataset |
| WRI Aqueduct 4.0 baseline water stress | Panel A overlay (optional) | `files.wri.org/aqueduct` | CC BY 4.0 |
| Variable-dynamics × sampling-frequency table (14 rows) | Panel B | Literature synthesis (28 primary refs; see `panel_b_timescales.csv`) | CC-BY (compiled here, cite underlying refs) |
| OpenAlex works counts by year × four queries | Panel C | `api.openalex.org/works` | CC0 |

## Pipeline steps

### 1. Fetch raw data (`make fetch`)

Downloads the following to `figure_data/`:

- `neon_sites_raw.json` (~25 MB) — NEON site registry including aquatic + terrestrial
- `deims_all_sites.json` (~1 MB) — ILTER site records with WKT POINT coordinates
- `gbif_country_effort_raw.json` (~20 KB) — GBIF country facets for all human observations
- `openalex_freshwater_{models,ml,prediction,monitoring}_by_year.json` (~6 KB each) — yearly publication counts for four queries
- `tedesco_2017.zip` (31 MB) — species × basin occurrence matrix + basin polygon shapefile
- `aqueduct40.zip` (262 MB) — WRI Aqueduct 4.0 basin-level water-risk indicators

All network calls use standard `curl`; no credentials required.

### 2. Process to tidy CSVs (`make process`)

| Script | Input | Output |
|---|---|---|
| `extract_neon_aquatic.py` | `neon_sites_raw.json` | `neon_aquatic_sites.csv` (34 sites) |
| `process_deims.py` | `deims_all_sites.json` | `ilter_sites.csv` (1,379 sites; 205 aquatic) |
| `process_gbif_country_effort.py` | `gbif_country_effort_raw.json` | `gbif_country_effort.csv` (250 countries) |
| `build_scissors_csv.py` | 4× OpenAlex JSON | `scissors_publications_by_year.csv` (108 rows) |
| `extract_tedesco.py` + `aggregate_tedesco.py` | `tedesco_2017.zip` | `tedesco_basin_richness.csv` (3,119 basins) |
| `extract_aqueduct.py` + `aggregate_aqueduct.py` | `aqueduct40.zip` | `aqueduct_basins.csv` (68,510 basins), `aqueduct_by_country.csv` (212 countries) |
| `cross_tab_effort_stress_richness.py` | three country-level CSVs | `country_effort_stress_richness.csv` (81 countries with all three metrics) |

The Panel B timescale table (`panel_b_timescales.csv`) is literature-compiled
(not derived from an external dataset); it lives in the repo alongside the
generated CSVs.

### 3. Plot Figure 2 (`make plot`)

`plot_fig2_combined.py` reads the five CSVs needed for the final figure
(NEON, ILTER, Tedesco, Panel B timescales, scissors) and renders:

- **Panel A** — global map of monitoring sites over Tedesco fish-richness
  centroids; legend shows NEON/ILTER site counts by subtype.
- **Panel B** — bar chart of variable dynamic timescales vs sampling
  frequencies on a log-time axis.
- **Panel C** — cumulative OpenAlex works per year 2000–2025 for four
  freshwater queries, with the AI inflection annotated.

Output files:

- `fig2_v40.png` at 300 dpi
- `fig2_v40.svg` for vector re-editing

Headline statistics are logged to stdout and feed directly into the caption
and cover letter:

```
Tedesco basins plotted:                 2,898
High-richness basins (>=200 native):    41
  Of which tropical (lat ±23.5°):       80%
NEON aquatic sites plotted:             34
  Of which tropical:                    2  (both in Puerto Rico: CUPE, GUIL)
ILTER aquatic sites plotted:            205
ML growth 2000 -> 2025:                 ~204×
Monitoring growth 2000 -> 2025:         ~14×
```

## File-level inventory

Code:

- `extract_neon_aquatic.py` — NEON JSON → CSV
- `process_deims.py` — DEIMS JSON → CSV (aquatic flag by name keyword)
- `process_gbif_country_effort.py` — GBIF facets JSON → CSV
- `build_scissors_csv.py` — merge four OpenAlex JSON into tidy long CSV
- `extract_tedesco.py` — unzip Tedesco archive
- `aggregate_tedesco.py` — aggregate species occurrences to per-basin richness
- `extract_aqueduct.py` — unzip Aqueduct archive
- `aggregate_aqueduct.py` — area-weighted BWS per country
- `cross_tab_effort_stress_richness.py` — join GBIF × Aqueduct × Tedesco
- `plot_fig2_combined.py` — the final 3-panel render
- `crossref_doi_lookup.py` — reference-metadata verification (not part of the figure pipeline; kept for provenance)
- `apply_crossref_dois.py` — apply verified DOIs to the manuscript (one-shot; already run)

Derived data:

- `neon_aquatic_sites.csv`, `ilter_sites.csv`, `gbif_country_effort.csv`
- `scissors_publications_by_year.csv`
- `tedesco_basin_richness.csv`, `aqueduct_basins.csv`, `aqueduct_by_country.csv`
- `country_effort_stress_richness.csv`
- `panel_b_timescales.csv` (literature-compiled)
- `panel_fig3_architectures.csv` (literature-compiled, feeds Figure 3 schematic captions)

Final figures:

- `fig2_v40.png`, `fig2_v40.svg` — the composite Figure 2

## Known limitations

- **GBIF backbone re-keying (2024):** `taxonKey=204` (Actinopterygii) no
  longer returns occurrences. Panel A currently uses the country-level
  all-taxa observer-effort facet as a proxy; a freshwater-only facet can be
  added once GBIF's new backbone keys stabilise.
- **GLEON registry:** no canonical public coordinate list as of 2026-04
  (site-membership programme discontinued 2024). Sharma *et al.* 2015 Sci
  Data (NSIDC DOI) is the practical proxy but is not yet integrated into
  this pipeline.
- **Choropleth rendering:** `geopandas` and `cartopy` are intentionally not
  dependencies (no stable ARM64 wheels). The final submission-quality
  rendering of Panel A is best produced in R (`sf` + `ggplot2`) or on an
  x64 host with conda-forge geopandas; tidy CSVs here are the join-ready
  inputs.

## Versioning

Each script uses only standard-library modules plus `pandas` and
`matplotlib`. The Makefile targets are idempotent; re-running with
unchanged inputs produces byte-identical outputs.
