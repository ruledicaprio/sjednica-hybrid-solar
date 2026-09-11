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

# 1-based pages in Prilog III that the corrected sheets supersede. Covers all 5 sheet
# slots (3-7) as a single replace-in-place set so reruns are idempotent -- a prior
# version only replaced 3-5 and unconditionally re-inserted M-01/E-01 after page 5,
# which duplicated stale copies of them on every second run (found 2026-08-08: pages
# 8-9 were a leftover pre-redesign M-01/E-01 pair from before the 3x4 support change).
REPLACE = {3: "S-01", 4: "S-02", 5: "S-03", 6: "M-01", 7: "E-01"}

# Pages identified by content, not position, so detection survives page-count drift.
# The Huawei "Standard A-Shaped Support 3.0" catalogue quick-guide (FN-01..FN-06,
# originally pp.27-32) describes the 6-module/4089mm product the design moved away
# from (site wind load exceeds its rating; see review/07-calculations.md F.6) --
# keeping it in the annex now misrepresents what is actually being tendered.
DROP_IF_CONTAINS = ["Nosač fotonaponskih panela (ground support) — LOW Support"]


def _should_drop(page):
    t = page.get_text().replace("\xa0", " ")  # PDF text uses NBSP between words
    return any(marker in t for marker in DROP_IF_CONTAINS)


def sheet(name):
    p = os.path.join(DWG, name + ".pdf")
    if not os.path.exists(p):
        raise SystemExit(f"missing plot {p} - run cad/export.py first")
    return fitz.open(p)


def build_situacija():
    out = fitz.open()
    for n in ("S-01", "S-02", "S-03", "M-01", "E-01"):
        out.insert_pdf(sheet(n))
    out.set_metadata(
        {
            "title": "Situacija i dispozicija — BS Sjednica (Bileća)",
            "author": "BH Telecom d.d. Sarajevo",
            "subject": "Autonomni hibridni sistem napajanja — nacrti S-01, S-02, S-03, M-01, E-01",
            "creator": "Rusmir Skopljak, dipl. ing. el.",
        }
    )
    out.subset_fonts()
    out.save(
        SITUACIJA,
        garbage=4,
        deflate=True,
        deflate_images=True,
        deflate_fonts=True,
        clean=True,
    )
    out.close()
    return SITUACIJA


def build_prilog():
    before = os.path.getsize(PRILOG)
    src = fitz.open(PRILOG)
    out = fitz.open()
    dropped = 0
    for i in range(src.page_count):
        pno = i + 1
        if pno in REPLACE:
            out.insert_pdf(sheet(REPLACE[pno]))
        elif _should_drop(src[i]):
            dropped += 1
        else:
            out.insert_pdf(src, from_page=i, to_page=i)
    if dropped:
        print(f"  dropped {dropped} superseded reference page(s)")
    meta = src.metadata or {}
    meta.update({"creator": "_______________, dipl. ing. __."})
    out.set_metadata(meta)
    src.close()
    out.subset_fonts()
    out.save(
        PRILOG,
        garbage=4,
        deflate=True,
        deflate_images=True,
        deflate_fonts=True,
        clean=True,
    )
    n = out.page_count
    out.close()
    return before, os.path.getsize(PRILOG), n


def main():
    s = build_situacija()
    d = fitz.open(s)
    print(
        f"Situacija_BS_Sjednica.pdf   {d.page_count} pages, "
        f"{os.path.getsize(s) / 1e6:.2f} MB"
    )
    d.close()

    before, after, pages = build_prilog()
    print(
        f"Prilog_III...pdf            {pages} pages, "
        f"{before / 1e6:.1f} MB -> {after / 1e6:.2f} MB "
        f"({100 * (1 - after / before):.0f}% smaller)"
    )

    d = fitz.open(PRILOG)
    fonts = set()
    for i in range(d.page_count):
        for f in d[i].get_fonts(full=True):
            fonts.add(f[0])
    tot = 0
    for x in fonts:
        try:
            tot += len(d.extract_font(x)[3])
        except Exception:  # noqa: BLE001
            pass
    txt = sum(1 for i in range(d.page_count) if d[i].get_text().strip())
    a3 = sum(
        1 for i in range(d.page_count) if abs(d[i].rect.width * 25.4 / 72 - 420) < 2
    )
    print(
        f"  embedded font bytes {tot / 1e6:.2f} MB | pages with text {txt}/{d.page_count} "
        f"| A3 pages {a3}"
    )
    d.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
