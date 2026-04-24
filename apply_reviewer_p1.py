"""Apply Priority-1 reviewer revisions to v43 manuscript, v44 DBPR, and
supplement v10/v11. All changes are small wording adjustments responding to
reviewer comments without adding new content blocks.

Priority-2/3 items (phased roadmap table, uncertainty checklist, Fig 2
robustness panel) require new content and are left for user decision.
"""
from pathlib import Path
HERE = Path(__file__).parent

# (old, new) pairs. Each should appear once in each file it targets.
# Two-file sets: main text (v43) + DBPR (v44)
MAIN_EDITS = [
    # 1. Soften abstract closing
    (
        "The path to better freshwater prediction runs through better observation.",
        "Across many classes of near-term freshwater forecast, the path to better prediction increasingly runs through better observation.",
    ),
    # 2. Soften Conclusion
    (
        "For the near-term forecasts freshwater science can now run, the binding problem is verification, not modelling.",
        "For many classes of near-term freshwater forecast, the binding problem has shifted towards verification-ready observation rather than modelling; the balance differs by subfield, and we do not claim this reweighting holds equally everywhere.",
    ),
    # 3. Clarify 'verification' near first appearance
    (
        "We call this mismatch the freshwater verification gap.",
        "We call this mismatch the freshwater verification gap, using 'verification' in the hydrology-aligned sense developed in Box 1 (independent testing of forecasts against unseen observations).",
    ),
    # 4. Align 'machine-learning publications' label with full query set
    (
        "In our OpenAlex-based bibliometric analysis, freshwater machine-learning publications grew roughly 200-fold between 2000 and 2025, while freshwater monitoring publications grew about 14-fold (Figure 2C; analysis described in Supplementary Methods).",
        "In an OpenAlex-based bibliometric analysis combining four model-adjacent keyword queries (Supplementary Methods), freshwater machine-learning and modelling publications grew by roughly two orders of magnitude between 2000 and 2025, while a comparable query for freshwater monitoring grew by about an order of magnitude (Figure 2C). The precise fold-change is sensitive to query choice; the robust signal is the widening divergence between the two literatures.",
    ),
    # 5. Harmonize blind-validation terminology (main text uses 'watersheds',
    #    Figure 3 caption uses 'basins'). Harmonise to 'watersheds' throughout.
    (
        "carrying the flagship architectures (blind-validation basins, forecast-triggered sampling, moving observatories, and management-event co-logging)",
        "carrying the flagship architectures (blind-validation watersheds, forecast-triggered sampling, moving observatories, and management-event co-logging)",
    ),
    # 6. Figure 2 caption — recast from "Empirical evidence" to triangulation,
    #    add caveats for Panel A (mixed proxy) and Panel C (bibliometric).
    (
        "**Figure 2.** Empirical evidence of the freshwater verification gap. **(A)** Global map of in-situ freshwater monitoring sites (NEON aquatic, n = 34; ILTER aquatic, n = 205) overlaid on native freshwater fish richness per basin (Tedesco *et al.* 2017; n = 2,898 basins with ≥1 native species).",
        "**Figure 2.** Triangulating evidence of the freshwater verification gap across spatial, temporal, and bibliometric dimensions. Panels A and C rest on proxy measurements — a mixed spatial proxy and a keyword-sensitive bibliometric time series — and should be read as triangulation rather than decisive measurement (see caveats in each panel description). **(A)** Global map of in-situ freshwater monitoring sites (NEON aquatic, n = 34; ILTER aquatic, n = 205) overlaid on native freshwater fish richness per basin (Tedesco *et al.* 2017; n = 2,898 basins plotted after filtering the 3,119-basin archive to those with outlet coordinates available; see Supplementary Methods).",
    ),
    # 7. Fig 2 caption — add log-y-axis + cumulative note for Panel C
    (
        "**(C)** Freshwater modelling publications are diverging from monitoring publications. Cumulative OpenAlex works per year, 2000–2025: freshwater machine-learning papers (blue) grew ~200-fold; freshwater monitoring papers (orange) grew ~14-fold. The inflection after 2018 tracks the AI acceleration discussed in the text.",
        "**(C)** Freshwater modelling publications are diverging from monitoring publications. Cumulative OpenAlex works per year on a logarithmic y-axis, 2000–2025, for four keyword queries (freshwater machine learning, prediction model, ecological model, and monitoring station; see Supplementary Methods). Precise fold-changes are sensitive to query choice; the robust signal is the widening divergence between model-adjacent and monitoring literatures, with an inflection after 2018 that tracks the AI acceleration discussed in the text.",
    ),
    # 8. Supp Fig S1 citation in main text — add 'curated cross-section, not exhaustive'
    (
        "Mapping active freshwater monitoring networks in frequency × coverage space (**Supplementary Figure S1**) sharpens this diagnosis: no in-situ network currently achieves both sub-weekly observation and global coverage.",
        "Mapping 32 active freshwater monitoring networks in frequency × coverage space (**Supplementary Figure S1**; a curated cross-section, not exhaustive) sharpens this diagnosis: no in-situ network in this sample currently achieves both sub-weekly observation and global coverage.",
    ),
]

# Table 1 descriptors — rewrite the requirement-id cells to include short descriptors
TABLE1_EDITS = [
    ("| Spatial bias | (iii) spatially representative; (iv) high-frequency where dynamics demand it |",
     "| Spatial bias | (iii) spatially representative; (iv) high-frequency |"),
    ("| Temporal coarseness | (i) sustained; (iv) high-frequency; (vi) easy to use |",
     "| Temporal coarseness | (i) sustained; (iv) high-frequency; (vi) analysis-ready |"),
    ("| Disciplinary fragmentation | (ii) standardised and interoperable; (v) integrative across data types |",
     "| Disciplinary fragmentation | (ii) standardised and interoperable; (v) integrative across data types |"),
    ("| Data uncertainty (equifinality, unquantified error) | (ii) standardised and interoperable; (v) integrative across data types |",
     "| Data uncertainty (equifinality, unquantified error) | (ii) interoperable; (v) integrative across data types |"),
    ("| Governance opacity (cross-cutting) | (vii) transparent to governance |",
     "| Governance opacity (cross-cutting) | (vii) transparent to governance |"),
]
# (Several cells already contained descriptors; the main benefit is the small rewrites above.)

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
    applied = apply_edits(p, MAIN_EDITS + TABLE1_EDITS)
    print(f"{p.name}: {len(applied)} edits applied")

# Supplement: ensure "blind-validation basins" → "blind-validation watersheds" too
for p in [HERE / "freshwater_prediction_supp_v10.md",
          HERE / "freshwater_prediction_supp_v11_DBPR.md"]:
    text = p.read_text(encoding="utf-8")
    # Blind-validation terminology harmonisation in supp
    text = text.replace("blind-validation basins", "blind-validation watersheds")
    p.write_text(text, encoding="utf-8")
    print(f"{p.name}: harmonised")

print("done")
