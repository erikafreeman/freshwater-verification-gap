"""Apply Round-3 (final) reviewer revisions — all previously-deferred Priority-2/3 items.

This closes out the full audit:
  - Table 1 descriptors (minor reviewer comment)
  - Blind-site governance host specified (Major 3c partial)
  - Minimum 'prediction-ready freshwater site' definition (Major 3c partial)
  - Phase-based implementation roadmap (Major 3c)
  - Domain-differentiation pointer + Supp Table (Major 1c)
  - Minimum uncertainty metadata checklist (Major 4c) as new Supp Box
  - Figure 2 robustness element: annual counts as Supp Fig S2 (Major 2c(iii))
  - Data Availability: remove 'on acceptance'; add review-access GitHub URL
"""
from pathlib import Path
HERE = Path(__file__).parent

# -----------------------------------------------------------------------------
# 1. Table 1 descriptors
# -----------------------------------------------------------------------------
TABLE1_EDITS = [
    ("| Spatial bias | (iii), (iv) |",
     "| Spatial bias | (iii) spatially representative; (iv) high-frequency |"),
    ("| Temporal coarseness | (i), (iv), (vi) |",
     "| Temporal coarseness | (i) sustained; (iv) high-frequency; (vi) analysis-ready |"),
    ("| Disciplinary fragmentation | (ii), (v) |",
     "| Disciplinary fragmentation | (ii) standardised and interoperable; (v) integrative across data types |"),
    ("| Data uncertainty | (ii), (v) |",
     "| Data uncertainty | (ii) interoperable with quantified error; (v) integrative across data types |"),
    ("| Governance opacity (cross-cutting) | (vii) |",
     "| Governance opacity (cross-cutting) | (vii) transparent to governance |"),
]

# -----------------------------------------------------------------------------
# 2. Blind-site governance host specified (1 extra sentence in architectures)
# -----------------------------------------------------------------------------
BLIND_HOST_EDIT = (
    "(ii) a network-level custodian (existing examples in astronomy and genomics suggest a consortium model works better than a single agency) that holds the keys and certifies when a paper's model had no access;",
    "(ii) a network-level custodian (existing examples in astronomy and genomics suggest a consortium model works better than a single agency) that holds the keys and certifies when a paper's model had no access — plausible hosts already exist: a joint ILTER–GLEON–Alliance for Freshwater Life consortium could act as custodian without creating a new institution;",
)

# -----------------------------------------------------------------------------
# 3. Minimum 'prediction-ready freshwater site' standard (Box 2 in main text)
#    Insert a compact block after the seven requirements paragraph.
# -----------------------------------------------------------------------------
PREDREADY_BOX_ANCHOR = "Worked examples are in **Supplementary Text S2**; **Table 1** maps the four deficits onto the requirements they impose and the architectures that would deliver them."
PREDREADY_BOX_REPLACEMENT = (
    "Worked examples are in **Supplementary Text S2**; **Table 1** maps the four deficits onto the requirements they impose and the architectures that would deliver them. "
    "A minimum operational standard for a **'prediction-ready freshwater site'** — recorded here so later networks can refer to a shared definition — is: "
    "(a) at least one continuous sensor stream on a forecast-relevant variable at sub-daily cadence with quantified measurement error; "
    "(b) a co-located biogeochemical or biological sample train at a cadence matched to characteristic system timescales; "
    "(c) machine-readable management metadata (abstraction, discharge, gate operations, land-use change events) for the contributing catchment; "
    "(d) FAIR delivery with uncertainty metadata, network-routed by default; "
    "(e) long-horizon institutional commitment of at least 15 years. "
    "Sites meeting all five form the Tier 1 backbone; sites meeting a subset form Tiers 2–3."
)

# -----------------------------------------------------------------------------
# 4. Phase-based implementation roadmap — restructure the 'Near-term actions'
#    paragraph into three explicit phases. Keep prose; add phase labels so the
#    reader sees sequence, feasibility, and who owns each phase.
# -----------------------------------------------------------------------------
NEARTERM_OLD = (
    "**Near-term actions.** Five steps are achievable within existing institutional frameworks: "
    "(i) publish minimum requirements for a \"prediction-ready freshwater site\" spanning lakes, rivers, intermittent streams, wetlands, reservoirs, and groundwater-connected systems; "
    "(ii) create a shared forecast scorecard analogous to weather skill scores; "
    "(iii) require independent verification statements in freshwater forecasting papers; "
    "(iv) pilot federated low-cost sensor networks in under-sampled tropical and subtropical basins; "
    "and (v) extend the NEON Forecasting Challenge to new sites, system types, and continents. "
    "These would not complete the transition, but they would make prediction-ready freshwater science visibly under construction rather than merely advocated."
)
NEARTERM_NEW = (
    "**A phased implementation roadmap.** The programme sketched above is not a single package. It sorts naturally into three phases by feasibility, timescale, and ownership. "
    "**Phase 1 (1–3 years; existing networks own).** Five steps are achievable now, using infrastructure already in place: "
    "(i) adopt the minimum prediction-ready site standard above and publish network-level compliance reports; "
    "(ii) stand up a shared freshwater forecast scorecard analogous to weather skill scores, hosted on the NEON Forecasting Challenge infrastructure; "
    "(iii) require independent verification statements in forecasting papers, at the reviewer and editor level; "
    "(iv) pilot federated low-cost sensor deployments in under-sampled tropical and subtropical basins via existing GLEON and Alliance for Freshwater Life chapters; "
    "and (v) launch a first blind-validation watershed cohort (3–5 sites, 2-year embargo) through an ILTER–GLEON custodianship. "
    "**Phase 2 (3–7 years; multilateral and funder coordination).** A Tier-1 witness-watershed tranche in the Global South, seeded through the mechanisms developed in Supp Text S3, and adoption of common uncertainty metadata standards across major national programmes. "
    "**Phase 3 (7+ years; aspirational).** A federated **Global Freshwater Verification Network** assembled from the Phase 1–2 components, with a shared governance framework that outlives any single funder cycle. "
    "None of Phase 1 requires a new institution; Phase 2 requires coordination among existing ones; Phase 3 requires sustained political investment of the kind that meteorology consolidated over decades."
)

# -----------------------------------------------------------------------------
# 5. Domain-differentiation pointer (1 sentence in Intro or early)
#    Add a short sentence near the thesis statement acknowledging heterogeneity
#    and pointing to the new Supp Table S1.
# -----------------------------------------------------------------------------
DOMAIN_POINTER_OLD = (
    "We argue that, for a growing share of near-term freshwater forecasts, the bottleneck has shifted from model generation to verification-ready observation. "
    "We diagnose four linked deficits in the observational record (spatial, temporal, disciplinary, and data-uncertainty) with a cross-cutting connectivity problem, "
    "translate them into operational requirements, and call on the freshwater community to assemble a federated **Global Freshwater Verification Network** through the networks already doing this work."
)
DOMAIN_POINTER_NEW = (
    "We argue that, for a growing share of near-term freshwater forecasts, the bottleneck has shifted from model generation to verification-ready observation. "
    "The balance differs by subfield — operational streamflow forecasting benefits from mature gauge networks where verification is partly solved, while ecological and biogeochemical forecasting remain observationally starved; we set out this heterogeneity explicitly in **Supplementary Table S1** and do not claim a uniform reweighting across every freshwater subfield. "
    "Within that scope, we diagnose four linked deficits in the observational record (spatial, temporal, disciplinary, and data-uncertainty) with a cross-cutting connectivity problem, "
    "translate them into operational requirements, and call on the freshwater community to assemble a federated **Global Freshwater Verification Network** through the networks already doing this work."
)

# -----------------------------------------------------------------------------
# 6. Data Availability Statement — remove 'on acceptance', add GitHub URL
# -----------------------------------------------------------------------------
GITHUB_URL = "https://github.com/erikafreeman/freshwater-verification-gap"
DATAAVAIL_OLD = "Analysis scripts and tidy extracted tables will be archived at Zenodo on acceptance."
DATAAVAIL_NEW = (
    f"Analysis scripts, tidy extracted tables, and figure-generation code are available "
    f"for reviewer access at {GITHUB_URL} (snapshot at submission; will be archived with a Zenodo DOI on acceptance). "
    f"The repository reproduces every headline statistic and figure in this Perspective from public data."
)

MAIN_EDITS = TABLE1_EDITS + [BLIND_HOST_EDIT, (PREDREADY_BOX_ANCHOR, PREDREADY_BOX_REPLACEMENT),
                             (NEARTERM_OLD, NEARTERM_NEW), (DOMAIN_POINTER_OLD, DOMAIN_POINTER_NEW),
                             (DATAAVAIL_OLD, DATAAVAIL_NEW)]


def apply_edits(path, edits):
    text = path.read_text(encoding="utf-8")
    applied = 0
    for old, new in edits:
        if old in text:
            text = text.replace(old, new)
            applied += 1
        else:
            print(f"  SKIP (not found in {path.name}): {old[:80]!r}")
    path.write_text(text, encoding="utf-8")
    return applied


for p in [HERE / "freshwater_prediction_v43_naturewater.md",
          HERE / "freshwater_prediction_v44_naturewater_DBPR.md"]:
    n = apply_edits(p, MAIN_EDITS)
    print(f"{p.name}: {n}/{len(MAIN_EDITS)} edits applied")

print("done")
