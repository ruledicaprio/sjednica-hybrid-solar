# -*- coding: utf-8 -*-
"""
Rebuild the two PDF deliverables.

`Situacija_BS_Sjednica.pdf`  - replaced outright by the corrected S-01/S-02/S-03 plots.

`Prilog_III_situacija_sjednica_bileca.pdf` - the corrected sheets are spliced in over
the superseded pages 3-5, then the whole file is optimised.  The optimisation is
lossless: it subsets fonts (the original embedded full Arial Regular + Arial Bold
seventeen times, 16.6 MB) and deflates streams that were stored uncompressed.  No
page is rasterised, so every page stays vector and searchable.
"""
import os
import sys

import fitz

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TD = os.path.join(BASE, "TD-OUTPUT")
DWG = os.path.join(TD, "DWG")

PRILOG = os.path.join(TD, "Prilog_III_situacija_sjednica_bileca.pdf")
SITUACIJA = os.path.join(TD, "Situacija_BS_Sjednica.pdf")

# 1-based pages in Prilog III that the corrected sheets supersede
REPLACE = {3: "S-01", 4: "S-02", 5: "S-03"}
APPEND = ["M-01", "E-01"]


def sheet(name):
    p = os.path.join(DWG, name + ".pdf")
    if not os.path.exists(p):
        raise SystemExit(f"missing plot {p} - run cad/export.py first")
    return fitz.open(p)


def build_situacija():
    out = fitz.open()
    for n in ("S-01", "S-02", "S-03", "M-01", "E-01"):
        out.insert_pdf(sheet(n))
    out.set_metadata({
        "title": "Situacija i dispozicija — BS Sjednica (Bileća)",
        "author": "BH Telecom d.d. Sarajevo",
        "subject": "Autonomni hibridni sistem napajanja — nacrti S-01, S-02, S-03, M-01, E-01",
        "creator": "Rusmir Skopljak, dipl. ing. el.",
    })
    out.subset_fonts()
    out.save(SITUACIJA, garbage=4, deflate=True, deflate_images=True,
             deflate_fonts=True, clean=True)
    out.close()
    return SITUACIJA


def build_prilog():
    before = os.path.getsize(PRILOG)
    src = fitz.open(PRILOG)
    out = fitz.open()
    for i in range(src.page_count):
        pno = i + 1
        if pno in REPLACE:
            out.insert_pdf(sheet(REPLACE[pno]))
        else:
            out.insert_pdf(src, from_page=i, to_page=i)
        if pno == 5:                       # keep the new sheets with the situation set
            for n in APPEND:
                out.insert_pdf(sheet(n))
    meta = src.metadata or {}
    meta.update({"creator": "Rusmir Skopljak, dipl. ing. el."})
    out.set_metadata(meta)
    src.close()
    out.subset_fonts()
    out.save(PRILOG, garbage=4, deflate=True, deflate_images=True,
             deflate_fonts=True, clean=True)
    n = out.page_count
    out.close()
    return before, os.path.getsize(PRILOG), n


def main():
    s = build_situacija()
    d = fitz.open(s)
    print(f"Situacija_BS_Sjednica.pdf   {d.page_count} pages, "
          f"{os.path.getsize(s)/1e6:.2f} MB")
    d.close()

    before, after, pages = build_prilog()
    print(f"Prilog_III...pdf            {pages} pages, "
          f"{before/1e6:.1f} MB -> {after/1e6:.2f} MB "
          f"({100*(1-after/before):.0f}% smaller)")

    d = fitz.open(PRILOG)
    fonts = set()
    for i in range(d.page_count):
        for f in d[i].get_fonts(full=True):
            fonts.add(f[0])
    tot = 0
    for x in fonts:
        try:
            tot += len(d.extract_font(x)[3])
        except Exception:                                   # noqa: BLE001
            pass
    txt = sum(1 for i in range(d.page_count) if d[i].get_text().strip())
    a3 = sum(1 for i in range(d.page_count)
             if abs(d[i].rect.width * 25.4 / 72 - 420) < 2)
    print(f"  embedded font bytes {tot/1e6:.2f} MB | pages with text {txt}/{d.page_count} "
          f"| A3 pages {a3}")
    d.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
