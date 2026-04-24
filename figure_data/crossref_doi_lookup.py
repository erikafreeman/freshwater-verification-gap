"""Query Crossref for every reference in the v39 manuscript to propose missing
DOIs, volumes, issues, and pages. Writes a report the user can verify before
any edit is applied to the manuscript itself. No automatic writes to the .md.
"""
from pathlib import Path
import re
import json
import urllib.request
import urllib.parse
import time

HERE = Path(__file__).parent
MS = HERE.parent / "freshwater_prediction_v39_naturewater.md"
REPORT = HERE / "crossref_proposals.md"

UA = "FreshwaterVerificationGap/1.0 (mailto:erika.freeman@igb-berlin.de)"

# Parse a reference line: number, first-author surname, year, title, journal
REF_RE = re.compile(
    r"^(\d+)\.\s+([A-Z][A-Za-zÀ-ÖØ-öø-ÿ'\- ]+?),.*?\((\d{4}[a-z]?)\)\.\s+(.+?)\.\s+\*?([^*]+?)\*?,",
    re.M,
)

def parse_refs(text: str):
    refs = []
    for line in text.splitlines():
        if not re.match(r"^\d+\.\s", line):
            continue
        m = re.match(r"^(\d+)\.\s+([^,]+),.*?\((\d{4}[a-z]?)\)\.\s+(.+)$", line)
        if not m:
            continue
        num, first_author, year, rest = m.groups()
        # Title ends at the first period that precedes italic journal
        # Try: first "*"-delimited chunk after title is the journal
        journal_match = re.search(r"\*([^*]+)\*", rest)
        journal = journal_match.group(1).strip() if journal_match else ""
        # Title is everything before ". *Journal*"
        if journal_match:
            title = rest[: journal_match.start()].rstrip(". ").rstrip()
        else:
            title = rest.rstrip(".")
        # Strip trailing period from title
        title = title.rstrip(".")
        has_doi = "doi:" in rest.lower()
        refs.append({
            "num": int(num),
            "first_author": first_author.strip(),
            "year": year,
            "title": title,
            "journal": journal,
            "has_doi": has_doi,
            "raw": line.strip(),
        })
    return refs

def crossref_search(title, first_author, year):
    q = f"query.title={urllib.parse.quote(title)}&query.author={urllib.parse.quote(first_author)}&rows=3"
    url = f"https://api.crossref.org/works?{q}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read().decode("utf-8"))
    except Exception as e:
        return None, f"HTTP error: {e}"
    items = data.get("message", {}).get("items", [])
    if not items:
        return None, "no match"
    # Pick the best item: year match + title similarity
    def score(it):
        t = (it.get("title") or [""])[0].lower()
        tl = title.lower()
        # crude jaccard
        ws_a = set(re.findall(r"\w+", t))
        ws_b = set(re.findall(r"\w+", tl))
        if not ws_a or not ws_b:
            return 0
        jac = len(ws_a & ws_b) / len(ws_a | ws_b)
        y = it.get("issued", {}).get("date-parts", [[None]])[0][0]
        year_bonus = 0.2 if y and str(y) == year[:4] else 0
        return jac + year_bonus
    items.sort(key=score, reverse=True)
    best = items[0]
    best_title = (best.get("title") or [""])[0]
    ws_a = set(re.findall(r"\w+", best_title.lower()))
    ws_b = set(re.findall(r"\w+", title.lower()))
    jac = len(ws_a & ws_b) / max(len(ws_a | ws_b), 1)
    if jac < 0.5:
        return None, f"low similarity ({jac:.2f}); closest={best_title[:90]!r}"
    return best, f"match (jac={jac:.2f})"

def extract_metadata(item):
    return {
        "doi": item.get("DOI"),
        "volume": item.get("volume"),
        "issue": item.get("issue"),
        "pages": item.get("page"),
        "journal": (item.get("container-title") or [""])[0],
        "title": (item.get("title") or [""])[0],
    }

def main():
    text = MS.read_text(encoding="utf-8")
    # Only parse the references block
    ref_block_match = re.search(r"# \*\*References\*\*\s*\n(.*?)(?=\n# |\Z)", text, re.S)
    ref_block = ref_block_match.group(1) if ref_block_match else ""
    refs = parse_refs(ref_block)
    print(f"Parsed {len(refs)} references")

    rows = []
    for r in refs:
        if r["has_doi"]:
            rows.append({"num": r["num"], "status": "has_doi", "note": "skipped (already has DOI)", "raw": r["raw"]})
            continue
        best, status = crossref_search(r["title"], r["first_author"], r["year"])
        if best is None:
            rows.append({"num": r["num"], "status": "no_match", "note": status, "raw": r["raw"]})
        else:
            md = extract_metadata(best)
            rows.append({"num": r["num"], "status": "found", "note": status, "raw": r["raw"], "proposed": md})
        time.sleep(0.3)  # be polite to Crossref

    # Write report
    with open(REPORT, "w", encoding="utf-8") as f:
        f.write("# Crossref DOI lookup proposals\n\n")
        f.write("Proposals for references that currently lack DOIs. Review each row before applying.\n\n")
        f.write("| Ref # | Status | Proposed DOI | Vol / Issue / Pages | Note |\n")
        f.write("|---|---|---|---|---|\n")
        for r in rows:
            if r["status"] == "has_doi":
                continue
            if r["status"] == "no_match":
                f.write(f"| {r['num']} | no_match | — | — | {r['note']} |\n")
            else:
                p = r["proposed"]
                vip = f"{p.get('volume','')}/{p.get('issue','')}/{p.get('pages','')}"
                f.write(f"| {r['num']} | found | `{p.get('doi','')}` | {vip} | {r['note']} |\n")
        f.write("\n## Raw entries for context\n\n")
        for r in rows:
            if r["status"] == "has_doi":
                continue
            f.write(f"- **#{r['num']}** — {r['raw']}\n")
            if r["status"] == "found":
                p = r["proposed"]
                f.write(f"  - Crossref title: *{p.get('title','')}*\n")
                f.write(f"  - Crossref journal: *{p.get('journal','')}*\n")
                f.write(f"  - Proposed addition: `vol {p.get('volume','?')}`, `issue {p.get('issue','?')}`, `pages {p.get('pages','?')}`, DOI `{p.get('doi','')}`\n")
            f.write("\n")

    # Quick summary
    found = sum(1 for r in rows if r["status"] == "found")
    nomatch = sum(1 for r in rows if r["status"] == "no_match")
    skipped = sum(1 for r in rows if r["status"] == "has_doi")
    print(f"Report written -> {REPORT.name}")
    print(f"  has_doi (skipped): {skipped}")
    print(f"  Crossref match:    {found}")
    print(f"  no_match:          {nomatch}")

if __name__ == "__main__":
    main()
