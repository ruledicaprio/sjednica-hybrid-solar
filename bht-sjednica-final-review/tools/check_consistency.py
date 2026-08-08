# -*- coding: utf-8 -*-
"""
Cross-document consistency check for the BS Sjednica tender package.

Reads every deliverable in its native form - OOXML straight out of the .docx zip,
openpyxl for the .xlsx, PyMuPDF for the .pdf, ezdxf for the .dxf - so nothing is
lost to a text-export round trip (LibreOffice's txt export mangles Bosnian
diacritics on a cp1252 console, which silently breaks naive greps).

Two kinds of check:

  CONFLICT  a fact that must have exactly one value across the package
            (generator rating, container size, panel geometry, LOT values)
  BANNED    text that must not appear at all - leftovers from the 46-generator
            template that this single-location job inherited

Exit code is the number of failures, so it can gate a release.
"""
from __future__ import annotations

import glob
import os
import re
import sys
import zipfile

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TD = os.path.join(BASE, "TD-OUTPUT")


# --------------------------------------------------------------------------
# readers
# --------------------------------------------------------------------------
def read_docx(path):
    """Concatenate the visible text of every w:t run, in document order."""
    z = zipfile.ZipFile(path)
    out = []
    for part in ("word/document.xml", "word/header1.xml", "word/header2.xml",
                 "word/header3.xml", "word/footer1.xml", "word/footer2.xml",
                 "word/footer3.xml", "word/footnotes.xml", "word/endnotes.xml"):
        if part not in z.namelist():
            continue
        xml = z.read(part).decode("utf-8", "replace")
        xml = re.sub(r"</w:p>", "\n", xml)
        out.append("".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", xml)))
        out.append("\n")
    return "".join(out)


def read_xlsx(path):
    import openpyxl
    wb = openpyxl.load_workbook(path, data_only=False)
    out = []
    for ws in wb:
        for row in ws.iter_rows():
            for c in row:
                if isinstance(c.value, str):
                    out.append(c.value)
                elif c.value is not None:
                    out.append(str(c.value))
    return "\n".join(out)


def read_pdf(path):
    import fitz
    d = fitz.open(path)
    return "\n".join(d[i].get_text() for i in range(d.page_count))


def read_dxf(path):
    import ezdxf
    d = ezdxf.readfile(path)
    out = []
    for e in d.modelspace():
        if e.dxftype() == "TEXT":
            out.append(e.dxf.text)
        elif e.dxftype() == "MTEXT":
            out.append(e.text)
    return "\n".join(out)


READERS = {".docx": read_docx, ".xlsx": read_xlsx, ".pdf": read_pdf, ".dxf": read_dxf}


def load():
    docs = {}
    for p in sorted(glob.glob(os.path.join(TD, "*")) +
                    glob.glob(os.path.join(TD, "DWG", "*.dxf"))):
        ext = os.path.splitext(p)[1].lower()
        if ext not in READERS or os.path.basename(p).startswith("~"):
            continue
        try:
            docs[os.path.relpath(p, TD)] = READERS[ext](p)
        except Exception as exc:                       # noqa: BLE001
            print(f"  ! could not read {os.path.basename(p)}: "
                  f"{type(exc).__name__}: {exc}")
    return docs


# --------------------------------------------------------------------------
# rules
# --------------------------------------------------------------------------
# name -> {variant label: regex}.  Exactly ONE variant may appear package-wide.
CONFLICTS = {
    "generator rating": {
        "22 kVA": r"22\s*kVA",
        "13,5 kVA": r"13[,.]5\s*kVA",
        # excluded: bibliographic/explanatory mentions of the MATISA 2x13 kVA
        # reference installation, which are correct usages rather than conflicts
        "2x13 kVA as a spec": r"(?<!MATISA )(?<!agregata \()2\s*[x×]\s*13\s*kVA(?![^.]{0,40}referent)",
    },
    # A superseded value quoted in Prilog I's "Ranije navedeno" column is a
    # documented correction, not a live specification: it is always followed within
    # the same table row by the corrected value, so a lookahead excludes it.
    "container external size": {
        "3005 x 2300 (certified project)":
            r"3005\s*[x×]\s*2300|3[,.]00\s*[x×]\s*2[,.]30|3[,.]005\s*[x×]\s*2[,.]30",
        "3,08 x 2,20 (WRONG)": r"3[,.]08\s*[x×]\s*2[,.]20(?![^§]{0,90}3[,.]005)",
        "3,00 x 2,10 (WRONG)": r"3[,.]00\s*[x×]\s*2[,.]10(?![^§]{0,90}3[,.]005)",
    },
    "PV module power": {
        "585 Wp": r"585\s*Wp",
        "540 Wp": r"540\s*Wp",
    },
    "panel horizontal projection": {
        # 2590 mm survives only inside S-03's note explaining the correction, so a
        # following "nije"/"ISPRAVLJENO" marks a legitimate historical mention
        # also excluded when followed by the corrected 3236 (Prilog I corrections table)
        "2590 (WRONG - beam length)":
            r"2590\s*mm(?![^.]{0,80}(nije|ISPRAVLJENO|raniji))(?![^§]{0,90}3236)"
            r"|2[,.]59\s*m\b",
        "3236 (correct - module field)": r"3236\s*mm|3[,.]24\s*m\b",
    },
    # +3,74 was correct for the 2x6 design; the 2026-08-08 3x4 redesign raised the
    # bottom edge to spend the freed-up wind budget on height (review/07-calculations.md
    # F.6), so +3,74 is now only a legitimate historical/superseded mention (Prilog I
    # §0's corrigendum table, or S-03's design-history note) when the corrected +4,74
    # appears nearby, same lookahead pattern as the 2590/3236 correction above.
    "top panel edge level": {
        "+3,09 (WRONG - superseded twice)": r"\+?3[,.]09(?![^§]{0,90}3[,.]74)",
        "+3,74 (superseded - was correct for 2x6)": r"\+?3[,.]74(?![^§]{0,90}4[,.]74)",
        "+4,74 (correct - 3x4 raised)": r"\+?4[,.]74",
    },
    "fence overhang": {
        "0,17 m (WRONG)": r"0[,.]17\s*m",
        "0,20 m (WRONG)": r"nadvi[šs]uje ogradu[^.]{0,20}0[,.]20\s*m",
        "1,84 m / 1836 mm (superseded - was correct for 2x6)":
            r"(1[,.]84\s*m|1836\s*mm)(?![^§]{0,90}(2[,.]84|2836))",
        "2,84 m / 2836 mm (correct - 3x4 raised)": r"2[,.]84\s*m|2836\s*mm",
    },
}

# these must appear with a single consistent value; reported if they disagree
SINGLE_VALUE = {
    "LOT 1 estimate": r"15\.000,00",
    "LOT 2 estimate": r"35\.000,00",
    "total estimate": r"50\.000,00",
    "fuel tank": r"500\s*l\b",
    "site altitude": r"1076\s*m",
}

# text that must not survive from the 46-generator template
BANNED = {
    "towing trailer (this job is skid-mounted)": r"vu[čc]n[uae]?\s+prikolic",
    "multi-location rollout clause": r"najmanje\s+dvije\s+lokacije",
    "fence extension with no BOQ item": r"pro[šs]irenje\s+postoje[ćc]e\s+ograde",
    "unresolved reference site": r"Brlo[šsž]ki\s+Potok",
    "empty numbered clause": r"\n\s*1\.5\s*\n\s*1\.6",
    "placeholder": r"\bTBD\b|\bXXX\b|<<[^>]+>>",
}


def scan(docs, pattern):
    hits = {}
    for name, text in docs.items():
        n = len(re.findall(pattern, text, re.I))
        if n:
            hits[name] = n
    return hits


def main():
    docs = load()
    print(f"documents read: {len(docs)}")
    for n in docs:
        print(f"   {n}  ({len(docs[n]):,} chars)")
    fails = 0

    print("\n=== CONFLICTS (exactly one variant allowed) ===")
    for topic, variants in CONFLICTS.items():
        found = {label: scan(docs, pat) for label, pat in variants.items()}
        found = {k: v for k, v in found.items() if v}
        if len(found) > 1:
            fails += 1
            print(f"  FAIL  {topic}: {len(found)} variants coexist")
            for label, hits in found.items():
                print(f"          '{label}' in " +
                      ", ".join(f"{k} x{v}" for k, v in hits.items()))
        elif len(found) == 1:
            label = next(iter(found))
            print(f"  OK    {topic}: '{label}' "
                  f"({sum(found[label].values())} mentions)")
        else:
            print(f"  --    {topic}: not mentioned anywhere")

    print("\n=== REQUIRED VALUES ===")
    for topic, pat in SINGLE_VALUE.items():
        hits = scan(docs, pat)
        if not hits:
            fails += 1
            print(f"  FAIL  {topic}: absent from the whole package")
        else:
            print(f"  OK    {topic}: {sum(hits.values())} mentions "
                  f"in {len(hits)} document(s)")

    print("\n=== BANNED TEXT (template leftovers) ===")
    for topic, pat in BANNED.items():
        hits = scan(docs, pat)
        if hits:
            fails += 1
            print(f"  FAIL  {topic}: " +
                  ", ".join(f"{k} x{v}" for k, v in hits.items()))
        else:
            print(f"  OK    {topic}: gone")

    print(f"\nRESULT: {fails} failure(s)")
    return fails


if __name__ == "__main__":
    sys.exit(main())
