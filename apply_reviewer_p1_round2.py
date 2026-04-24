"""Apply Round-2 reviewer revisions.

Round-2 reviewer = the 'Manuscript Referee Report' + 'Figure Referee Report'
requesting minor revisions. Three minor wording edits, two main-text additions
(FAIR/open-data tension for blind validation; Global South endowment mechanism),
and Figure 2 caption tweaks for Panel A inset clarity + Panel C log-scale.
"""
from pathlib import Path
HERE = Path(__file__).parent

MAIN_EDITS = [
    # 1. Line 27 GBIF — add caveat about improving structured survey ingestion
    (
        "Repositories such as the Global Biodiversity Information Facility (GBIF) hold mostly opportunistic occurrence records; five countries alone account for 61% of all human-observation records in GBIF while the least-monitored half of countries together hold 0.4% (Figure 2A).",
        "Repositories such as the Global Biodiversity Information Facility (GBIF) hold mostly opportunistic occurrence records — although GBIF is actively expanding its ingestion of structured survey events — and five countries alone account for 61% of all human-observation records in GBIF, while the least-monitored half of countries together hold 0.4% (Figure 2A).",
    ),
    # 2. Line 49 SWOT — note elevation and slope, not just extent
    (
        "That combination is available only through satellite remote sensing (Sentinel-2, Landsat, SWOT, JRC Global Surface Water), which captures surface-water extent, temperature, chlorophyll-a, and turbidity on 1–21 day revisits but not the sub-surface, biogeochemical, or biological variables most forecasts require.",
        "That combination is available only through satellite remote sensing (Sentinel-2, Landsat, SWOT, JRC Global Surface Water), which captures surface-water extent, elevation and slope (from SWOT), temperature, chlorophyll-a, and turbidity on 1–21 day revisits, but not the sub-surface, biogeochemical, or biological variables most forecasts require.",
    ),
    # 3. Line 63 eDNA — soften 'unresolved abundance quantification' to reflect progress
    (
        "Environmental DNA is transforming biodiversity monitoring [58-59] but its integration into forecasting workflows remains limited by reference-database gaps, quality-control inconsistencies, and unresolved abundance quantification [60].",
        "Environmental DNA is transforming biodiversity monitoring [58-59] but its integration into forecasting workflows remains limited by reference-database gaps, quality-control inconsistencies, and abundance quantification that — while advancing rapidly through qPCR calibration, read-count normalisation, and joint occupancy–detection modelling — is not yet consistent enough to underpin routine forecast verification [60].",
    ),
    # 4. Figure 2 caption — strengthen GBIF inset label (reviewer asked for
    #    explicit 'General biological observer effort (proxy)' framing)
    (
        "GBIF country-level observer effort (inset colour ramp): five countries account for 61% of all human-observation records globally, while the least-monitored 125 countries hold 0.4%.",
        "GBIF country-level **general biological observer effort (proxy)** (inset colour ramp): five countries account for 61% of all human-observation records globally, while the least-monitored 125 countries hold 0.4%.",
    ),
    # 5. Figure 2 caption — make Panel C log-scale explicit a second time
    #    (in addition to 'on a logarithmic y-axis' already in the caption)
    (
        "**(C)** Freshwater modelling publications are diverging from monitoring publications. Cumulative OpenAlex works per year on a logarithmic y-axis, 2000–2025, for four keyword queries",
        "**(C)** Freshwater modelling publications are diverging from monitoring publications. Cumulative OpenAlex works per year (y-axis: log-scale cumulative publications), 2000–2025, for four keyword queries",
    ),
    # 6. MAJOR concern 1 — FAIR/open-data tension for blind validation.
    # Expand the blind-validation-watersheds paragraph to explicitly name the
    # tension and the two reconciliation mechanisms (cryptographic pre-commit
    # / trusted third-party custodian) currently only in Supp Text S3.
    (
        "Making site-level independence a network-level rule turns the reproducibility diagnosis into operational infrastructure.",
        "Making site-level independence a network-level rule turns the reproducibility diagnosis into operational infrastructure. Selective embargo sits in evident tension with the FAIR and open-data mandates that now govern most freshwater data flows, and that tension must be resolved in the open. Two mechanisms already used in other fields reconcile the two: cryptographic pre-commitment, in which hashed observations are published immediately while the plaintext is time-locked (used for blinded analyses in high-energy physics and clinical trials); and trusted third-party custodians, in which an independent consortium holds embargoed streams on behalf of the community and certifies access (the model used for controlled-access genomic data and for blinded cosmology datasets). Either route keeps data ultimately open while preserving the one property forecast verification requires, that the model has not seen the test set. We see these as minimum-viable governance patterns rather than departures from open science.",
    ),
]

# DBPR version: blind-validation paragraph text is identical in v44 except the
# self-reference suppression — the major-concern-1 edit applies cleanly to both.

# MAJOR concern 2 — Global South endowment mechanism. Instead of a brand-new
# paragraph, extend the existing five-near-term-actions list item about
# witness sites in the concluding section. Locate the section first.

def apply_edits(path: Path, edits):
    text = path.read_text(encoding="utf-8")
    applied = []
    for old, new in edits:
        if old in text:
            text = text.replace(old, new)
            applied.append(old[:80])
        else:
            print(f"  SKIP (not found in {path.name}): {old[:80]}...")
    path.write_text(text, encoding="utf-8")
    return applied

for p in [HERE / "freshwater_prediction_v43_naturewater.md",
          HERE / "freshwater_prediction_v44_naturewater_DBPR.md"]:
    applied = apply_edits(p, MAIN_EDITS)
    print(f"{p.name}: {len(applied)}/{len(MAIN_EDITS)} edits applied")

print("done")
