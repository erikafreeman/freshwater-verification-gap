# Closing the freshwater verification gap — code and data

This repository contains the reproducible scripts and extracted data tables
underlying the Perspective *"Closing the freshwater verification gap"*
(submitted to *Nature Water*).

**Purpose:** reviewer and public access to the analysis pipeline before the
paper is accepted. After acceptance, a versioned snapshot will be archived
with a Zenodo DOI; the GitHub repository will remain as the working copy.

## What you can reproduce

- **Figure 2 (main text) Panel B + C:** timescale bars (B); scissors plot of
  freshwater ML vs monitoring publications (C). Panel A (map) is prepared
  separately; the Tedesco + NEON + ILTER CSVs that feed it are included here.
- **Supplementary Figure S1:** 32 freshwater monitoring networks plotted in
  frequency × coverage space.
- **Supplementary Figure S2:** annual (non-cumulative) version of Panel C,
  as a robustness check for the cumulative-on-log-axis presentation.
- **Headline statistics** used in the abstract, main text, and figure
  captions (reproducible from the same CSVs).

## Data provenance

All datasets are public and fully cited in the paper's Data Availability
Statement. In summary:

| Source | Access | Licence |
|---|---|---|
| NEON aquatic site registry | `data.neonscience.org` | CC0 |
| ILTER via DEIMS-SDR | `deims.org` | CC BY |
| GBIF country aggregates | `gbif.org` | CC BY |
| Tedesco *et al.* 2017 fish basins | Figshare `5245072` | CC0 |
| WRI Aqueduct 4.0 | `wri.org/aqueduct` | CC BY 4.0 |
| OpenAlex works counts | `api.openalex.org` | CC0 |

## How to reproduce

```bash
# install the minimal Python environment
pip install -r requirements.txt

# fetch the raw inputs (respects APIs' rate limits)
cd figure_data
python extract_neon_aquatic.py
python process_deims.py
python extract_tedesco.py
python build_scissors_csv.py

# build the figures
python plot_fig2_combined.py
python plot_networks_landscape.py
python plot_supp_fig_s2_annual.py
```

A `Makefile` orchestrates the above.

## Reviewer notes

- The bibliometric panel (Fig 2C) is built from four OpenAlex keyword queries.
  Query strings are in `figure_data/build_scissors_csv.py`. Precise
  fold-changes are sensitive to query choice; the robust signal is the
  widening divergence, as shown in Supp Fig S2.
- Figure 2A uses GBIF country-level observer effort as a *proxy* for freshwater
  monitoring capacity. After the 2024 GBIF backbone re-keying, the 
  Actinopterygii-only taxon key no longer resolves; we use the all-taxa facet
  and flag the proxy nature throughout.
- Figure 2A plots 2,898 basins after filtering Tedesco *et al.*'s 3,119-basin
  archive to those with outlet coordinates available.

## Scope

This repository is limited to the figure reproduction pipeline. Submission-side
tooling (markdown → DOCX conversion, reviewer-response helpers) lives elsewhere
and is not part of the reproducible science.

## Contact

Erika C. Freeman — erika.freeman@igb-berlin.de
