# -*- coding: utf-8 -*-
"""
Corrections to `3.1 PRILOG II TD - predmjer Sjednica Bileca.xlsx`.

openpyxl edits in place, preserving cell styles, merges and formulas.  Row deletions
are followed by an explicit rebuild of the total formulas, located by their label
text rather than by a hard-coded address, so the file cannot silently end up summing
the wrong range.

Findings closed: B (geometry), I (item 2.7), J (no recap on LOT 1, phantom rows),
HW F-01 (support BOM), HW F-06 (cable), CON R-01 (wind), EL RED-13 (earth conductor).
"""
import os
import re
import sys

import openpyxl
from openpyxl.styles import Alignment, Border, Font, Side
from openpyxl.utils import get_column_letter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XLSX = os.path.join(BASE, "TD-OUTPUT", "3.1 PRILOG II TD - predmjer Sjednica Bileca.xlsx")

# ---------------------------------------------------------------- corrected text
GEOM = (" - gabariti PV stringa (2 reda × 3 modula, portret): 3476 mm (širina polja, "
        "poprečna greda 4089 mm) × 3236 mm (horizontalna projekcija pri 45°); "
        "dužina polja po nagibu 4576 mm (2 × 2278 mm); donja ivica PV panela na "
        "+0,50 m, gornja ivica na +3,74 m od nivoa terena")

PLACE = (" - smještaj: nosač se temelji IZVAN ograđenog platoa; gornja (sjeverna) "
         "ivica panela je 1,84 m iznad kote ograde h=1,90 m. Ponuđač je dužan "
         "provjeriti da konstrukcija u cijelosti ostaje unutar zakupljene parcele "
         "16,00 × 9,40 m i da ne zadire u pristupni koridor oko kontejnera")

WIND = (" - uticaji: konstrukcija se dimenzioniše na stvarne klimatske uticaje "
        "lokaliteta (1076 m n.v., Istočna Hercegovina, područje bure). MJERODAVNO "
        "OPTEREĆENJE: pritisak vjetra qp ≥ 1,20 kN/m² (udar 3 s ≈ 45 m/s), prema "
        "ovjerenoj projektnoj dokumentaciji lokacije i BAS EN 1991-1-4 sa BiH "
        "nacionalnim aneksom; snijeg prema BAS EN 1991-1-3. NAPOMENA: katalog "
        "proizvođača nosača tipa A daje otpornost 31 m/s (0,52 kN/m²) pri nagibu 45° "
        "i 40 m/s (0,87 kN/m²) pri 15°/25°, što je ISPOD navedenog opterećenja "
        "lokaliteta — Ponuđač je stoga dužan ponuditi konstrukciju dimenzionisanu i "
        "dokazanu za stvarno opterećenje lokaliteta, uz pisanu potvrdu proizvođača "
        "za konkretnu lokaciju (planinski vrh). Mjerodavni su podizanje (uplift) i "
        "prevrtanje konstrukcije")

TILT = (" - inklinacija: fiksno 45°, uz obavezu dokazivanja otpornosti na vjetar "
        "prema Tački 1.3. Ukoliko statički proračun pokaže da nagib 45° nije "
        "ostvariv sa ponuđenom konstrukcijom, Ponuđač može ponuditi manji nagib "
        "(25°–35°), uz dokaz da je godišnji prinos umanjen za najviše 2 %")

STATIC = ("Statički proračun nosive konstrukcije i temelja, ovjeren i potpisan od "
          "strane ovlaštenog inženjera, sa dokazom otpornosti na pritisak vjetra "
          "qp ≥ 1,20 kN/m² i opterećenje snijegom za lokaciju, uključujući dokaz "
          "sigurnosti na podizanje (uplift) i prevrtanje, te dimenzionisanje temelja "
          "prema stvarnim geotehničkim uslovima (kamenito tlo). NAPOMENA: proračun "
          "se dostavlja UZ PONUDU, kao uslov kvalifikacije, a ne nakon dodjele ugovora.")

SUPPORT = ("Isporuka i montaža nosive metalne konstrukcije (ground mount support) za "
           "prihvat fotonaponskih panela, karakteristika:")
SUPPORT_TYPE = (" - tip: A-izvedba, NISKA izvedba (Standard A-Shaped Support 3.0 — LOW "
                "SUPPORT), kao Huawei BOM 21540481 sa ankerima BOM 21540482 ili "
                "ekvivalent istih ili boljih karakteristika")

CABLE = ("Isporuka i polaganje DC solarnog kabla 1×6 mm² (H1Z2Z2-K) od fotonaponskih "
         "panela do PVDB distribucije, uključujući MC4 konektore, obujmice i "
         "UV-otporne kanalice. NAPOMENA: završni priključak na ulaznu stezaljku "
         "iSSU modula izvesti presjekom 4 mm² prema zahtjevu proizvođača. "
         "2 nosača × 2 × 25,00 m")

EARTH = ("Uzemljenje nosivih konstrukcija: povezivanje obje konstrukcije na postojeći "
         "prstenasti uzemljivač lokacije bakarnim užetom 50 mm² sa PVC izolacijom, "
         "otpornim na UV i ukopavanje (npr. H07RN-F ili istovjetno), preko priključnih "
         "stezaljki na konstrukciji i bimetalnih (Cu/Fe-Zn) ukrsnih komada radi "
         "sprječavanja galvanske korozije. Presjek prema EN 62305-3 za odvođenje "
         "atmosferskog pražnjenja. Otpor uzemljenja ≤ 10 Ω.")

PVDB = ("Isporuka i montaža PVDB ormara za PV panele sa DC rastavljačem i osiguračima "
        "za svaki string, min. IP55, kao Huawei PVDB500-15-2B (01075918) ili "
        "ekvivalent. Odvodnik prenapona DC (tip 2) isporučuje se kao zasebna stavka "
        "1.6a jer nije sadržan u navedenom ormaru.")

SPD = ("Isporuka i ugradnja odvodnika prenapona DC, tip 2, za svaki string (2 kom), "
       "sa pripadajućim rastavnim osiguračima, u PVDB ormaru iz Tačke 1.6 ili u "
       "zasebnom kućištu min. IP55.")


def find_row(ws, col, needle):
    for r in range(1, ws.max_row + 1):
        v = ws.cell(r, col).value
        if isinstance(v, str) and needle.lower() in v.lower():
            return r
    raise SystemExit(f"row not found: {needle!r}")


def main():
    wb = openpyxl.load_workbook(XLSX)
    ws = wb["LOT 1"]
    log = []

    def setb(row, text, why):
        old = ws.cell(row, 2).value
        ws.cell(row, 2).value = text
        log.append((f"LOT 1!B{row}", str(old)[:60], text[:60], why))

    setb(12, SUPPORT, "unchanged wording, anchor for 1.1")
    setb(13, SUPPORT_TYPE, "HW F-01: name the actual Huawei BOM number")
    setb(20, TILT, "CON R-01: tilt tied to the wind proof")
    setb(23, GEOM, "B: geometry derived from the module field, not the beam")
    setb(24, PLACE, "B: fence overshoot restated correctly (1,84 m above fence)")
    setb(25, WIND, "CON R-01: state the real site wind load")
    setb(32, STATIC, "CON A-03: static calculation becomes a pre-award condition")
    setb(33, EARTH, "EL RED-13: H07V-K 25 mm² is indoor wire and undersized")
    setb(34, CABLE, "HW F-06: iSSU terminal requires 4 mm²")
    setb(35, PVDB, "HW F-05: Huawei PVDB is IP55 and carries no SPD")

    # ---- new item 1.6a: the DC SPD the PVDB does not contain -----------------
    ws.insert_rows(36)
    src = 35
    for c in range(1, 7):
        ws.cell(36, c)._style = ws.cell(src, c)._style
    ws.cell(36, 1).value = "1.6a"
    ws.cell(36, 2).value = SPD
    ws.cell(36, 3).value = "kpl"
    ws.cell(36, 4).value = 2
    ws.cell(36, 6).value = '=IF(AND(D36<>"",E36<>""),D36*E36,"")'
    log.append(("LOT 1!A36", "-", "1.6a DC SPD", "HW F-05 / EL RED-12: SPD not in the PVDB"))

    # ---- delete the empty 2.6 / 2.8 rows and the spurious 2.7 slab ----------
    r27 = find_row(ws, 1, "2.7")
    r26, r28 = find_row(ws, 1, "2.6"), find_row(ws, 1, "2.8")
    desc = str(ws.cell(r27, 2).value)[:70]
    for r in sorted({r26, r27, r28}, reverse=True):
        ws.delete_rows(r)
    log.append(("LOT 1 rows 2.6/2.7/2.8", desc, "DELETED",
                "I / CON R-07: the 5,40×5,40 slab already exists; 2.6 and 2.8 were empty"))

    # ---- rebuild the totals, located by label ------------------------------
    r1 = find_row(ws, 1, "UKUPNO 1 —")
    r2 = find_row(ws, 1, "UKUPNO 2 —")
    rl = find_row(ws, 1, "UKUPNO LOT 1")
    first2 = find_row(ws, 1, "2.1")
    ws.cell(r1, 6).value = f"=SUM(F12:F{r1-1})"
    ws.cell(r2, 6).value = f"=SUM(F{first2}:F{r2-1})"
    ws.cell(rl, 6).value = f"=F{r1}+F{r2}"
    log.append(("LOT 1 totals", "SUM(F12:F36)/SUM(F40:F49)",
                f"SUM(F12:F{r1-1})/SUM(F{first2}:F{r2-1})",
                "J: ranges rebuilt after row deletion"))

    # ---- recap + discount + PDV on LOT 1, mirroring LOT 2 ------------------
    thin = Side(style="thin")
    box = Border(left=thin, right=thin, top=thin, bottom=thin)
    r = rl + 2
    rows = [("REKAPITULACIJA — LOT 1", None, True),
            ("UKUPNO LOT 1 (bez PDV-a):", f"=F{rl}", False),
            ("Popust (%):", None, False),
            ("UKUPNO LOT 1 sa popustom (bez PDV-a):", None, False),
            ("PDV 17%:", None, False),
            ("UKUPNO LOT 1 sa PDV-om:", None, True)]
    for i, (label, formula, bold) in enumerate(rows):
        rr = r + i
        ws.cell(rr, 1).value = label
        ws.cell(rr, 1).font = Font(bold=bold, size=10)
        ws.cell(rr, 1).alignment = Alignment(horizontal="left", vertical="center")
        ws.merge_cells(start_row=rr, start_column=1, end_row=rr, end_column=5)
        if formula:
            ws.cell(rr, 6).value = formula
        ws.cell(rr, 6).font = Font(bold=bold, size=10)
        ws.cell(rr, 6).number_format = "#,##0.00"
        for c in range(1, 7):
            ws.cell(rr, c).border = box
    disc = r + 2
    ws.cell(disc, 6).value = None
    ws.cell(r + 3, 6).value = f'=F{r+1}*(1-IF(F{disc}="",0,F{disc}/100))'
    ws.cell(r + 4, 6).value = f"=F{r+3}*0.17"
    ws.cell(r + 5, 6).value = f"=F{r+3}+F{r+4}"
    log.append((f"LOT 1!A{r}:F{r+5}", "-", "recap + popust + PDV 17%",
                "J: a LOT-1-only bidder previously never reached a total"))

    # ---- trim the phantom rows past the content ----------------------------
    last = r + 5
    if ws.max_row > last:
        ws.delete_rows(last + 1, ws.max_row - last)
        log.append((f"LOT 1 rows {last+1}+", f"{ws.max_row} rows", f"trimmed to {last}",
                    "J: ~138 empty rows carried formatting past the content"))

    wb.save(XLSX)

    print(f"{'cell':22s} {'before':32s} {'after':34s} reason")
    for c, a, b, why in log:
        print(f"{c:22s} {a:32.32s} {b:34.34s} {why}")
    print(f"\n{len(log)} changes written to {os.path.basename(XLSX)}")


if __name__ == "__main__":
    main()
