# -*- coding: utf-8 -*-
"""
Rebuild `Situacija_BS_Sjednica.pdf` from the S-01/S-02/S-03/M-01/E-01 plots.

The optimisation is lossless: it subsets fonts and deflates streams that were
stored uncompressed. No page is rasterised, so every page stays vector and
searchable.

This script used to splice the same sheets into Prilog III by page number too.
Since Rev 3 Prilog III is assembled from parts by build_prilog3.py, and in the
Rev 8 layout page 3 is the site-data page - the splice would overwrite it with
S-01. That half is removed rather than left to be run by mistake.
"""

import os
import sys

import fitz

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import GRAFIKA as DWG, SITUACIJA                         # noqa: E402


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


def main():
    s = build_situacija()
    d = fitz.open(s)
    print(
        f"Situacija_BS_Sjednica.pdf   {d.page_count} pages, "
        f"{os.path.getsize(s) / 1e6:.2f} MB"
    )
    d.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
