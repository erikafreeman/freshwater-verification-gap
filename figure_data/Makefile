# Reproducible build of Figure 2 (empirical evidence) for the Nature Water Perspective.
#
# Usage:
#   make all        # run the full pipeline end to end
#   make fetch      # fetch raw data from public APIs + archives
#   make process    # derive tidy CSVs from the raw data
#   make plot       # render Figure 2 from the tidy CSVs
#   make clean      # remove all generated files (keeps raw zips)
#   make distclean  # also remove raw zips
#
# Figures 1 and 3 are conceptual schematics; they are generated from the
# prompts in ../figure_prompts_gemini.md and not produced by this Makefile.

PY := python

# ---- Targets --------------------------------------------------------------

all: plot

fetch: neon_sites_raw.json deims_all_sites.json gbif_country_effort_raw.json \
       openalex_freshwater_models_by_year.json openalex_freshwater_ml_by_year.json \
       openalex_freshwater_monitoring_by_year.json openalex_freshwater_prediction_by_year.json \
       tedesco_2017.zip aqueduct40.zip

process: neon_aquatic_sites.csv ilter_sites.csv gbif_country_effort.csv \
         scissors_publications_by_year.csv tedesco_basin_richness.csv \
         aqueduct_by_country.csv country_effort_stress_richness.csv

plot: fig2_v40.png

# ---- Raw downloads --------------------------------------------------------

neon_sites_raw.json:
	curl -sL "https://data.neonscience.org/api/v0/sites" -o $@

deims_all_sites.json:
	curl -sL "https://deims.org/api/sites" -H "Accept: application/json" -o $@

gbif_country_effort_raw.json:
	curl -sL "https://api.gbif.org/v1/occurrence/search?limit=0&basisOfRecord=HUMAN_OBSERVATION&facet=country&facetLimit=250" -o $@

openalex_freshwater_models_by_year.json:
	curl -sL "https://api.openalex.org/works?search=freshwater+ecological+model&group_by=publication_year&per_page=200" -o $@

openalex_freshwater_ml_by_year.json:
	curl -sL "https://api.openalex.org/works?search=freshwater+machine+learning&group_by=publication_year&per_page=200" -o $@

openalex_freshwater_monitoring_by_year.json:
	curl -sL "https://api.openalex.org/works?search=freshwater+monitoring+station&group_by=publication_year&per_page=200" -o $@

openalex_freshwater_prediction_by_year.json:
	curl -sL "https://api.openalex.org/works?search=freshwater+prediction+model&group_by=publication_year&per_page=200" -o $@

tedesco_2017.zip:
	curl -sL "https://ndownloader.figshare.com/files/8964583" -o $@

aqueduct40.zip:
	curl -sL "https://files.wri.org/aqueduct/aqueduct-4-0-water-risk-data.zip" -o $@

# ---- Processing -----------------------------------------------------------

neon_aquatic_sites.csv: neon_sites_raw.json extract_neon_aquatic.py
	$(PY) extract_neon_aquatic.py

ilter_sites.csv: deims_all_sites.json process_deims.py
	$(PY) process_deims.py

gbif_country_effort.csv: gbif_country_effort_raw.json process_gbif_country_effort.py
	$(PY) process_gbif_country_effort.py

scissors_publications_by_year.csv: openalex_freshwater_models_by_year.json \
                                   openalex_freshwater_ml_by_year.json \
                                   openalex_freshwater_monitoring_by_year.json \
                                   openalex_freshwater_prediction_by_year.json \
                                   build_scissors_csv.py
	$(PY) build_scissors_csv.py

tedesco_basin_richness.csv: tedesco_2017.zip aggregate_tedesco.py extract_tedesco.py
	$(PY) extract_tedesco.py
	$(PY) aggregate_tedesco.py

aqueduct_by_country.csv: aqueduct40.zip aggregate_aqueduct.py extract_aqueduct.py
	$(PY) extract_aqueduct.py
	$(PY) aggregate_aqueduct.py

country_effort_stress_richness.csv: gbif_country_effort.csv aqueduct_by_country.csv \
                                    tedesco_basin_richness.csv \
                                    cross_tab_effort_stress_richness.py
	$(PY) cross_tab_effort_stress_richness.py

# ---- Plot -----------------------------------------------------------------

fig2_v40.png: neon_aquatic_sites.csv ilter_sites.csv tedesco_basin_richness.csv \
              panel_b_timescales.csv scissors_publications_by_year.csv \
              plot_fig2_combined.py
	$(PY) plot_fig2_combined.py

# ---- Housekeeping ---------------------------------------------------------

clean:
	rm -f neon_aquatic_sites.csv ilter_sites.csv gbif_country_effort.csv
	rm -f scissors_publications_by_year.csv tedesco_basin_richness.csv
	rm -f aqueduct_basins.csv aqueduct_by_country.csv country_effort_stress_richness.csv
	rm -f fig2_v40.png fig2_v40.svg fig2a_draft.png fig2b_draft.png fig4_draft.png
	rm -rf tedesco_2017 aqueduct40

distclean: clean
	rm -f neon_sites_raw.json deims_all_sites.json gbif_country_effort_raw.json
	rm -f openalex_*.json
	rm -f tedesco_2017.zip aqueduct40.zip

.PHONY: all fetch process plot clean distclean
