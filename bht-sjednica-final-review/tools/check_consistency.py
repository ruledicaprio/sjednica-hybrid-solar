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
        # Paragraph breaks have to survive as text: the run collector below keeps
        # only <w:t> contents, so a bare "\n" substitution here was discarded and
        # adjacent table cells came out glued together ("gorivomranije:"), which
        # silently defeated every \b-anchored pattern.
        xml = re.sub(r"</w:p>", "<w:t>\n</w:t>", xml)
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
    # Rev 2 (2026-08-11): the airflow relayout and the section-G closures below.
    # Each corrected value is quoted once more in Prilog I's "Ranije navedeno"
    # column, so the superseded variants carry the same lookahead as above.
    # The certified project of this K2 object ("04 AG dio.docx" 4.4.2.3) dimensions
    # the floor for a total (g+p) UDL of 10,00 kN/m². The 2,00 kN/m² in the same
    # project is the pedestrian live load on the walkable strip, so it may only
    # appear where it is named as such - hence the lookahead rather than a ban.
    "container floor capacity": {
        "10,00 kN/m² (correct - K2 project 4.4.2.3)": r"10[,.]00\s*kN/m²",
        "2,00 kN/m² (WRONG - that is the walkable-strip live load)":
            r"2[,.]00\s*kN/m²(?![^§]{0,160}(pokretn|prohodn|walkable))",
    },
    "foundation concrete class": {
        "C25 (WRONG - no exposure class)": r"\bC25\b(?![^§]{0,90}C30/37)",
        "C30/37 XF3 (correct)": r"C30/37",
    },
    "fuel tank footprint": {
        "1200 x 700 (WRONG - estimate)":
            r"1200\s*[x×]\s*700(?![^§]{0,90}1050\s*[x×]\s*600)",
        "1050 x 600 x 1310 (correct - vendor data)":
            r"1050\s*[x×]\s*600",
    },
    "first fuel fill": {
        "200 l (WRONG - contradicts the priced 500 l)":
            r"najmanje\s*200\s*l|≥\s*200\s*l",
        "500 l (correct - matches BOQ 4.16)": r"500\s*l\s*\(pun spremnik\)|500\s*l\b",
    },
    "power system named": {
        "PowerCube 1000 (WRONG - not installed here)": r"PowerCube\s*1000",
        "ICC330-H1 + MTS9302 (correct)": r"ICC330-H1",
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
    # closed in Rev 2 - each was specified nowhere or in only one document
    "tower obstruction lighting (G-9)": r"rasvjet[ae]\s+prepreke",
    "type 1+2 AC SPD (G-6)": r"[Tt]ip\s*1\s*\+\s*2|TIP\s*1\s*\+\s*2",
    "signal-line SPD (G-6)": r"61643-21",
    "fire elaborate priced (G-5)": r"elaborat[a]?\s+za[šs]tite\s+od\s+po[žz]ara",
    "intake on the south wall": r"JU[ŽZ]NI\s*zid|JU[ŽZ]NOM\s*zidu",
    "discharge on the west wall": r"ZAPADNI\s*zid|ZAPADNOM\s*zidu",
}

# text that must not survive from the 46-generator template
BANNED = {
    "towing trailer (this job is skid-mounted)": r"vu[čc]n[uae]?\s+prikolic",
    "multi-location rollout clause": r"najmanje\s+dvije\s+lokacije",
    "fence extension with no BOQ item": r"pro[šs]irenje\s+postoje[ćc]e\s+ograde",
    "unresolved reference site": r"Brlo[šsž]ki\s+Potok",
    "empty numbered clause": r"\n\s*1\.5\s*\n\s*1\.6",
    "placeholder": r"\bTBD\b|\bXXX\b|<<[^>]+>>",
    # Rev 2: the blanket placement that put intake, discharge and the 505 °C
    # exhaust on the same wall, next to the outdoor power cabinets (EL RED-03)
    "all openings on the north wall": r"sve\s+na\s+SJEVERNOJ\s+strani",
}


# A superseded value quoted inside a documented correction is a record, not a live
# specification. Prilog I's corrigendum table and the drawings' design-history notes
# both do this deliberately, so a hit whose neighbourhood carries one of these
# markers does not count. Keep the list short - it is an exemption, not a loophole.
# Stems, not whole words: Bosnian inflects these ("mjerodavan / mjerodavna /
# mjerodavni", "ranije / ranija / raniji"), and an over-specific ending silently
# turns the exemption off - which is exactly how the first version of this list
# let a documented correction be reported as a live conflict.
CORRECTION_MARKERS = re.compile(
    r"\branij[aeiou]\w*|ISPRAVLJENO|IZMJENA|NIJE\s+mjerodav|nisu\s+mjerodav|"
    r"umjesto|razli[čc]ito\s+u\s+dokumentima|REDOSLIJED\s+MJERODAVNOSTI", re.I)
CONTEXT = 240


def scan(docs, pattern, live_only=False, skip=()):
    """Count matches per document. With live_only, ignore matches that sit inside
    a documented correction."""
    hits = {}
    for name, text in docs.items():
        if name in skip:
            continue
        n = 0
        for m in re.finditer(pattern, text, re.I):
            if live_only:
                near = text[max(0, m.start() - CONTEXT):m.end() + CONTEXT]
                if CORRECTION_MARKERS.search(near):
                    continue
            n += 1
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
        found = {label: scan(docs, pat, live_only="WRONG" in label or
                             "superseded" in label)
                 for label, pat in variants.items()}
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
        hits = scan(docs, pat, live_only=True)
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
