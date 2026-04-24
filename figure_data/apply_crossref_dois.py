"""Apply Crossref DOIs to references in the v39 manuscript.

Only adds DOIs to refs that currently lack them. Does not overwrite existing
vol/pages even if Crossref disagrees (those discrepancies are flagged separately
in the proposals report). Ref 21 (OSF preprint DOI only) is skipped by policy
to avoid citing a preprint when a journal version likely exists.

Also applies two flagged vol/page corrections (refs 53, 79) where the user
review confirmed Crossref is correct.
"""
from pathlib import Path
import re

HERE = Path(__file__).parent
MS = HERE.parent / "freshwater_prediction_v39_naturewater.md"

# Crossref-confirmed DOIs for refs that currently lack one.
# Keyed by reference number. Values are the DOIs (without "doi:" prefix).
ADD_DOI = {
    1:  "10.1126/science.293.5530.657",
    3:  "10.1111/oik.03726",
    4:  "10.1111/gcb.16590",
    5:  "10.1038/s41558-024-02182-0",
    6:  "10.1002/eap.70004",
    7:  "10.1002/ecs2.70335",
    8:  "10.1017/s1464793105006950",
    9:  "10.1111/brv.12480",
    10: "10.1093/biosci/biaa002",
    11: "10.5268/iw-5.1.566",
    12: "10.1002/fee.2616",
    13: "10.1016/j.scitotenv.2017.12.001",
    15: "10.1111/j.1442-9993.2011.02351.x",
    16: "10.1890/120103",
    18: "10.1073/pnas.1710231115",
    19: "10.1111/ele.13994",
    20: "10.1098/rstb.2004.1595",
    # 21 skipped — Crossref returned OSF preprint; published Ecol Lett version preferred
    23: "10.1002/ecs2.70205",
    25: "10.1016/j.patter.2023.100804",
    26: "10.1111/2041-210x.13955",
    # 29 no_match (Vollenweider 1975, pre-digital)
    30: "10.1038/nature14956",
    31: "10.1002/eap.2642",
    32: "10.1002/ecy.70292",
    35: "10.1111/brv.13137",
    36: "10.1002/2014gl060641",
    37: "10.1111/fwb.12646",
    39: "10.1016/j.ecolind.2025.113207",
    41: "10.3389/frwa.2025.1699240",
    43: "10.1038/nature20584",
    44: "10.1017/eds.2024.14",
    45: "10.1016/j.ecolind.2025.113646",
    46: "10.1098/rspb.2024.0980",
    47: "10.1080/20442041.2023.2239110",
    48: "10.1016/j.ecolind.2012.12.010",
    49: "10.1021/acs.est.6b01604",
    50: "10.1038/s41467-018-02922-9",
    51: "10.4319/lo.2014.59.4.1388",
    52: "10.1016/b978-0-08-095975-7.01010-x",
    53: "10.1002/lno.10721",
    54: "10.1038/s41467-023-44431-4",
    56: "10.1016/j.tree.2024.12.006",
    57: "10.1029/2025jg009064",
    58: "10.1111/mec.14350",
    59: "10.1002/2688-8319.12361",
    60: "10.1002/ece3.72891",
    61: "10.2307/1467397",
    62: "10.1890/1051-0761(2001)011[0981:hcatmo]2.0.co;2",
    63: "10.1111/j.1600-0706.2010.18553.x",
    64: "10.1007/s10651-006-0022-8",
    65: "10.1111/ele.12084",
    66: "10.5194/essd-14-4525-2022",
    67: "10.1080/17538947.2024.2391033",
    68: "10.1038/s41586-023-06221-2",
    71: "10.1038/s41586-024-07146-0",
    72: "10.1002/ecs2.4752",
    73: "10.1038/sdata.2016.18",
    78: "10.1002/aqc.2958",
    79: "10.1080/iw-6.4.904",
}

# Volume / page corrections Crossref identified (apply + log)
VOL_PAGE_FIX = {
    53: {"old": "**66**, S13–S30", "new": "**62**, S3–S18"},  # Xenopoulos 2017 L&O 62(S1)
    79: {"old": "**6**, 468–482",  "new": "**6**(4), 543–554"},  # Hanson 2016 Inland Waters 6(4)
}

def main():
    text = MS.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    out_lines = []
    applied_doi = []
    applied_fix = []
    for line in lines:
        m = re.match(r"^(\d+)\.\s", line)
        if not m:
            out_lines.append(line)
            continue
        num = int(m.group(1))
        new_line = line
        # Apply vol/page fix first (pre-DOI append)
        if num in VOL_PAGE_FIX:
            v = VOL_PAGE_FIX[num]
            if v["old"] in new_line:
                new_line = new_line.replace(v["old"], v["new"])
                applied_fix.append(num)
        # Append DOI if missing
        if num in ADD_DOI and "doi:" not in new_line.lower():
            doi = ADD_DOI[num]
            # Strip trailing newline, add DOI, restore newline
            rstripped = new_line.rstrip("\r\n ")
            # Ensure line ends in a period before doi
            if not rstripped.endswith("."):
                rstripped += "."
            rstripped += f" doi:{doi}."
            # preserve original line ending
            ending = new_line[len(new_line.rstrip("\r\n ")):]
            new_line = rstripped + ending
            applied_doi.append(num)
        out_lines.append(new_line)

    MS.write_text("".join(out_lines), encoding="utf-8")
    print(f"Applied DOI additions: {len(applied_doi)} refs")
    print(f"  refs: {applied_doi}")
    print(f"Applied vol/page fixes: {len(applied_fix)} refs")
    print(f"  refs: {applied_fix}")

if __name__ == "__main__":
    main()
