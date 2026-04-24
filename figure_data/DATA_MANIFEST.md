# Figure data manifest — Nature Water Perspective

Generated 2026-04-21 during the v39 → submission preparation cycle.
Every dataset used or planned for Figures 1–4 is listed below, with access method, license, current status, and which figure panel consumes it. "Status" means how the file in `figure_data/` was produced, **not** whether the figure is finished.

Legend for **Status**:
- `fetched` = downloaded programmatically in this pass, file sits in `figure_data/`
- `manual` = requires human click-through (EULA, registration, shopping cart) — a one-line instruction is given
- `blocked` = data exists but is not redistributable from Nature Water figure; must cite an aggregate

---

## FIGURE 1 — Forecast cycle + verification gap (conceptual)

No data required. Schematic only. Gemini prompt in `figure_prompts_gemini.md`.

---

## FIGURE 2A — Global evidence map

### In-situ monitoring stations (coloured dots)

| Dataset | URL / API | License | Status | File |
|---|---|---|---|---|
| **NEON aquatic sites** | `https://data.neonscience.org/api/v0/sites` | CC0 (US federal) | **fetched** | `neon_aquatic_sites.csv` (34 sites: 7 lakes, 3 rivers, 24 streams, per NEON canonical classification) |
| **ILTER via DEIMS-SDR** | `https://deims.org/api/sites` | CC BY (per DEIMS terms of use) | **fetched** | `ilter_sites.csv` (1,379 sites globally, 205 aquatic by name) |
| **GLEON lake observatories** | No public registry as of 2026-04 — **site-membership programme discontinued 2024** | — | **blocked** | Cite Sharma et al. 2015 (Sci. Data, doi:10.1038/sdata.2015.8) or Jane et al. 2021 (Nature) compilations as practical proxies; or email `gleonoffice@gleon.org` |
| **EU WFD / WISE-SoE stations** | `https://water.discomap.eea.europa.eu/` (WFS) + EEA datahub | EEA re-use (attribution) | **manual** | Download the "WISE SoE spatial dataset" from EEA datahub; UK coverage stops at 2020 |
| **US EPA NARS (NLA, NRSA, NWCA, NCCA)** | `https://www.epa.gov/national-aquatic-resource-surveys/data-national-aquatic-resource-surveys` | Public domain | **manual** | Per-cycle CSV; most recent cycle is 2023-24 NRSA |
| **GRDC streamflow gauges** | `https://grdc.bafg.de/` (registration required) | Free for research with attribution | **manual** | Download "GRDC Station Catalogue" Excel after free registration |
| **GEMS/Water (GEMStat)** | `https://gemstat.org/` (registration) | Open with attribution | **manual** | CSV of station catalogue; patchy outside OECD |
| **GRQA (global river quality archive)** | Virta et al. 2023 ESSD doi:10.5194/essd-15-5551-2023 — PANGAEA DOI | CC BY 4.0 | **manual** | Single geopackage; merges GEMStat + Waterbase + WQP — the practical spine |
| **HydroLAKES / HydroRIVERS basemap** | `https://www.hydrosheds.org/` | Free non-commercial + peer-reviewed research; attribute Lehner & Grill 2013 | **manual** | ~180 MB zipped shapefile — avoid downloading via the assistant, click through manually |

### Biodiversity + water-stress underlay (warm-shaded polygons)

| Dataset | URL | License | Status | Use |
|---|---|---|---|---|
| **WRI Aqueduct 4.0** | `https://www.wri.org/aqueduct/data` / `github.com/wri/aqueduct40` | CC BY 4.0 | **manual** | Basin shapefile with Baseline Water Stress — the dominant pressure layer |
| **FEOW (Freshwater Ecoregions)** | `https://www.feow.org/` | CC BY 4.0 (TNC/WWF) | **manual** | 426 ecoregion polygons; good for masking to freshwater |
| **Tedesco et al. 2017 fish richness** | Figshare, doi:10.1038/sdata.2017.141 | CC0 | **manual** | CSV × HydroBASINS L08 — gives a per-basin richness raster |
| **IUCN Red List freshwater species** | `https://www.iucnredlist.org/resources/spatial-data-download` | Free research use, account required | **manual** | Compute 10 km Behrmann richness raster; 2024-2 is current |
| **Grill et al. 2019 free-flowing rivers** | Figshare, doi:10.6084/m9.figshare.7688801 | CC BY 4.0 | **manual** | River Connectivity Status Index — single-layer stress alternative |
| **Global Dam Watch 1.0 (2025)** | `https://www.globaldamwatch.org/` | CC BY 4.0 | **manual** | Unified dam layer (supersedes GRanD/GOODD/GeoDAR) |

### Observer-effort sanity check (all-taxa country totals)

| Dataset | API | License | Status | File |
|---|---|---|---|---|
| **GBIF country-level record counts** | `https://api.gbif.org/v1/occurrence/search?facet=country&basisOfRecord=HUMAN_OBSERVATION` | CC BY (per dataset) | **fetched** | `gbif_country_effort.csv` — 250 countries, 3.19B records, top-5 countries hold 61%, bottom 50% hold 0.4% |

Note: the GBIF 2024 backbone re-keying broke `taxonKey=204` (Actinopterygii) — occurrence-by-taxon queries need the new keys once the backbone settles; effort-by-country works today and is the stronger argument for the figure anyway.

---

## FIGURE 2B — Timescales vs sampling frequencies

| Dataset | Source | Status | File |
|---|---|---|---|
| **Compiled timescale table** | Literature synthesis across 28 primary refs (Staehr 2010; Kirchner 2006; Huisman 2018; Carey 2022; Bieroza 2018; etc.) | **fetched/compiled** | `panel_b_timescales.csv` — 14 rows (7 variable dynamics, 7 sampling programmes) with `low_days`, `high_days`, `anchor_days`, DOIs |

---

## FIGURE 3 — Verification architecture / GFVN

| Dataset | Source | Status | File |
|---|---|---|---|
| **Architecture table** | v39 manuscript §"New architectures for verification" + §"What prediction-ready infrastructure requires" | **fetched/compiled** | `panel_fig3_architectures.csv` — 9 architectures × 3 tiers + governance layer |

---

## FIGURE 4 — Scissors (models vs monitoring)

| Dataset | URL / API | License | Status | File |
|---|---|---|---|---|
| **OpenAlex yearly counts** — four queries (model, prediction, ML, monitoring) | `https://api.openalex.org/works?search={q}&group_by=publication_year` | CC0 (OpenAlex) | **fetched** | `scissors_publications_by_year.csv` — 2000–2026, four series; freshwater_ml grew 62.8× vs freshwater_monitoring 3.9× |
| **Active GRDC stations reporting real-time 2000–2024** | WMO 2008/2014 Hydrometric Status Reports; GRDC annual reports | — | **manual** | Quote the known drop (≈6,000 → <2,000 near-real-time stations 1980s→2020s) as a second line if editorial policy allows mixed sources |

---

## Summary — what's in place now

Programmatically fetched (this session): NEON aquatic (30), ILTER via DEIMS (1,379 with 205 aquatic), GBIF country effort (250), OpenAlex publication counts (four series × 27 years). These alone give a defensible first draft of Figures 2A and 4.

Requires a human click-through before the final figure: WFD/WISE, NARS, GRDC, GEMS, GRQA, HydroLAKES, Aqueduct, IUCN, FEOW, Tedesco, Grill. None of these block a draft — each slots into an existing column in the plotting scaffold.

Blocked / non-canonical: GLEON (membership programme discontinued 2024; use Sharma 2015 GLTC as proxy).

Panel B and Figure 3 are fully compiled from literature and manuscript text — no further fetching needed.
