# -*- coding: utf-8 -*-
"""Where the Sjednica TD package lives, in one place.

Rev 8 renamed two things the scripts had hard-coded: the drawings moved from
TD-OUTPUT/DWG to TD-OUTPUT/grafika (the folder name the client uses) and
Prilog III became "3.2 Prilog III TD - Situacije.pdf". The drawing, export and
annex scripts still wrote to the old names, so a rebuild produced files nobody
reads while the deliverables went stale.

TD_OUT redirects every OUTPUT to another folder: the reproduction gate builds
into scratch and compares against the committed package without touching it.
Inputs (review/, cad/, reference/) always come from this site folder.
"""
import os

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TD = os.environ.get("TD_OUT") or os.path.join(SITE, "TD-OUTPUT")
GRAFIKA = os.path.join(TD, "grafika")

PRILOG1 = os.path.join(TD, "3. Prilog I TD - Specifikacija zahtjeva.docx")
PRILOG2 = os.path.join(TD, "3.1 PRILOG II TD - predmjer Sjednica Bileca.xlsx")
PRILOG3 = os.path.join(TD, "3.2 Prilog III TD - Situacije.pdf")
SITUACIJA = os.path.join(TD, "Situacija_BS_Sjednica.pdf")

LOGO_SVG = os.path.join(SITE, "cad", "bht-logo.svg")
