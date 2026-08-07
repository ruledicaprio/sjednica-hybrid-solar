# -*- coding: utf-8 -*-
"""
Corrections to `3. TD JN Hibridni sistem napajanja BS Sjednica.docx`.

Applied as targeted OOXML run edits (see ooxml_edit.py) so the template's styles,
numbering, headers and layout are untouched.  Each edit carries the finding it
closes; the full rationale is in review/00-change-log.md.

Sources:
  [CON]  review/02-construction.md      [EL]  review/03-electrical.md
  [HW]   review/01-huawei-solar.md      [SC]  review/05-site-corrections.md
  [GEO]  cad/site_geometry.json  (measured from the certified site project)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ooxml_edit import edit_docx                                    # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOC = os.path.join(BASE, "TD-OUTPUT",
                   "3. TD JN Hibridni sistem napajanja BS Sjednica.docx")

EDITS = [
    # ---- F: Table 1 still carries the template's 13,5 kVA -------------------
    ("kontejner_skid_13,5kVA", "kontejner_skid_22kVA", 1),

    # ---- E: container size contradicted the certified project [GEO] ---------
    ("tipski objekat: kontejner dimenzija 3,00 x 2,10 x 2,40 m, IP55, mase ~850 kg, "
     "za smještaj TK opreme",
     "tipski objekat: kontejner vanjskih dimenzija 3,005 x 2,30 m (zidni paneli 60 mm, "
     "unutrašnja površina 6,29 m², obim 10,13 m), IP55, prema ovjerenom projektu "
     "lokacije; kontejner je trenutno PRAZAN", 1),

    # ---- H: fence extension with no BOQ item, and no longer intended --------
    ("; ukupno zakupljena površina parcele 150 m², zbog čega je predviđeno "
     "proširenje postojeće ograde",
     "; ukupno zakupljena površina parcele 150 m² (16,00 x 9,40 m)", 1),

    # ---- H: towing trailer - this job is a skid inside a container ----------
    ("dokumentaciju za vučnu prikolicu, ", "", 1),
    ("o garantnom periodu za isporučene agregate, vučnu prikolicu i prateću opremu",
     "o garantnom periodu za isporučeni agregat, nosače fotonaponskih panela i "
     "prateću opremu", 1),
    ("o postgarantnom periodu za isporučene agregate, vučnu prikolicu i prateću opremu",
     "o postgarantnom periodu za isporučeni agregat, nosače fotonaponskih panela i "
     "prateću opremu", 1),

    # ---- H: multi-location clause on a single-location contract ------------
    ("Izuzetno, plaćanje usluga na izradi tipskog tehničkog rješenja (nakon usvajanja "
     "istog) se treba realizovati posebnom fakturom i to nakon uspješne implementacije "
     "FN sistema na najmanje dvije lokacije. ", "", 1),

    # ---- EL RED-11: the Brložki Potok reference is not in the package -------
    ("prema rješenju primijenjenom na lokaciji Brloški Potok iz referentne tenderske "
     "dokumentacije",
     "prema zahtjevima iz Priloga II i Priloga III ove tenderske dokumentacije", 1),

    # ---- ZJN art. 54: brand named without "or equivalent" ------------------
    ("za smještaj u postojeći kontejner, kao FG Wilson P22-6 (Skid),",
     "za smještaj u postojeći kontejner, kao FG Wilson P22-6 (Skid) ili ekvivalent,", 1),
]


def main():
    applied = edit_docx(DOC, EDITS, backup=None)
    for find, part, n in applied:
        print(f"  OK  x{n}  {part}  {find[:64]!r}")
    print(f"\n{len(applied)} edits applied to {os.path.basename(DOC)}")


if __name__ == "__main__":
    main()
