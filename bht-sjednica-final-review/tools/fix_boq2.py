# -*- coding: utf-8 -*-
"""
Second round of BOQ corrections, from the Investor's decisions of 2026-08-07.

  1. LOT 1 item 1.2  -> resin (epoxy) rock anchors replace cast-in U-bolts
  2. LOT 1 item 2.3  -> concrete C30/37, exposure XC4 + XF3 (freeze-thaw at 1076 m)
  3. LOT 1 item 1.8  -> NEW optional alternative: 3 supports x 4 modules
  4. LOT 2 GRO       -> RCD reinstated (4p 300 mA S-type + 2 x RCBO 30 mA)

Two traps this script exists to avoid, both hit on the first attempt:

  * inserting N rows and then writing M > N lines silently overwrites the items
    below.  `replace_block` inserts exactly the shortfall and never writes past
    the block it owns.
  * item numbers must match EXACTLY: a substring test makes "4.1" match "4.10",
    which produced SUM ranges over the wrong rows and a #VALUE! grand total.

Every total is rebuilt afterwards by label, and the result must be verified by
recalculating the workbook - see review/00-change-log.md section 3.15.
"""
import os
import sys

import openpyxl

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XLSX = os.path.join(BASE, "TD-OUTPUT", "3.1 PRILOG II TD - predmjer Sjednica Bileca.xlsx")

ANCHORS = ("Isporuka i ugradnja sistema sidrenja nosive konstrukcije iz Tačke 1.1 u "
           "stijenu/beton, hemijskim (epoksidnim) ankerima, karakteristika:")
ANCHORS_B = [
    " - tip: hemijski (epoksidni/vinilesterski) anker M16 ili M20 sa ETA odobrenjem za "
    "ugradnju u beton i/ili stijenu, vruće cinčan ili nehrđajući A4",
    " - broj: najmanje 2 ankera po temeljnoj traci, odnosno 4 ankera po nosaču "
    "(minimum 2 po traci zbog redundanse)",
    " - nosivost: karakteristična sila čupanja ≥30 kN po ankeru; ukupna projektna sila "
    "podizanja po nosaču iznosi ≥27 kN (GSN), moment prevrtanja ≥64 kNm",
    " - dokazivanje: ispitivanje čupanjem (pull-out test) na najmanje 10 % ugrađenih "
    "ankera, minimalno 2 po nosaču, do 1,5 × projektne sile, uz zapisnik ovjeren od "
    "nadzornog organa",
    " - alternativa: livena U-anker sidra M16/320 prema nacrtu proizvođača dozvoljena su "
    "SAMO uz gravitacioni temelj zapremine ≥1,14 m³ po nosaču (umjesto 0,81 m³)",
]

CONCRETE_NOTE = (
    " IZMJENA — BETON I ARMATURA: beton klase C30/37, klase izloženosti XC4 + XF3 prema "
    "BAS EN 206, sa aerantom 4–6 %, Dmax 16, konzistencija S3; podložni beton C12/15 "
    "d=50 mm; armatura B500B, zaštitni sloj ≥50 mm. Klasa XF3 je mjerodavna zbog "
    "cikličnog smrzavanja i odmrzavanja u vlažnom stanju na 1076 m n.v. Temeljna "
    "spojnica mora biti ispod dubine smrzavanja za lokalitet, koju Ponuđač navodi u ponudi.")

ALT = ("OPCIJA (alternativna ponuda — cijena se iskazuje posebno i NE ulazi u zbir): "
       "Isporuka i montaža TRI nosača sa po 4 fotonaponska modula (3 × 4 = 12 modula, "
       "ista ukupna snaga 7,02 kWp) umjesto dva nosača sa po 6 modula. Površina "
       "izloženosti vjetru po nosaču smanjuje se sa 15,91 m² na 7,95 m² (−50 %), čime se "
       "približno prepolovljuju sila podizanja i moment prevrtanja po temelju, uz "
       "zadržavanje nagiba 45°. Uključuje treći komplet temelja, sidrenja i uzemljenja. "
       "Kupac zadržava pravo izbora između osnovne i alternativne izvedbe.")

RCD = [
    " - 1 kom 4p zaštitna strujna sklopka (RCD) 63 A / 300 mA, S-tip (selektivna), za "
    "zaštitu cjelokupnog napojnog kruga iza sklopke izvora",
    " - 2 kom 1p+N zaštitna strujna sklopka sa prekostrujnom zaštitom (RCBO) 16 A / "
    "30 mA, tip A, za utičnice i rasvjetu kontejnera",
    " NAPOMENA (obavezno): agregat je SHUNT pobude i prema tehničkom listu proizvođača "
    "ima sposobnost trajne struje kratkog spoja 0 %, zbog čega SAMO prekostrujna zaštita "
    "NE MOŽE ostvariti automatsko isključenje u vremenu zahtijevanom prema "
    "IEC 60364-4-41 (0,4 s za 230 V). Zaštita zaštitnom strujnom sklopkom je stoga "
    "OBAVEZNA. Sistem uzemljenja je TN-S sa jedinstvenom tačkom spajanja N i PE u ovom "
    "ormaru; otpor uzemljenja ≤10 Ω.",
]


def row_exact(ws, col, value):
    """Row whose cell equals `value` exactly - never a substring."""
    for r in range(1, ws.max_row + 1):
        v = ws.cell(r, col).value
        if isinstance(v, str) and v.strip() == value:
            return r
    return None


def row_startswith(ws, col, prefix):
    for r in range(1, ws.max_row + 1):
        v = ws.cell(r, col).value
        if isinstance(v, str) and v.strip().startswith(prefix):
            return r
    return None


def row_contains(ws, col, needle):
    for r in range(1, ws.max_row + 1):
        v = ws.cell(r, col).value
        if isinstance(v, str) and needle.lower() in v.lower():
            return r
    return None


def copy_style(ws, src, dst):
    for c in range(1, 7):
        ws.cell(dst, c)._style = ws.cell(src, c)._style


def replace_block(ws, first, last_exclusive, lines):
    """
    Replace the description rows [first, last_exclusive) with `lines`,
    inserting only the shortfall so nothing below is ever overwritten.
    """
    have = last_exclusive - first
    if len(lines) > have:
        ws.insert_rows(first, len(lines) - have)
        for i in range(len(lines) - have):
            copy_style(ws, first + (len(lines) - have), first + i)
    elif len(lines) < have:
        ws.delete_rows(first, have - len(lines))
    for i, txt in enumerate(lines):
        ws.cell(first + i, 2).value = txt
        for c in (1, 3, 4, 5, 6):
            ws.cell(first + i, c).value = None
    return len(lines) - have


def main():
    wb = openpyxl.load_workbook(XLSX)
    l1, l2 = wb["LOT 1"], wb["LOT 2"]
    log = []

    # ---- 1. anchors ---------------------------------------------------------
    r12, r13 = row_exact(l1, 1, "1.2"), row_exact(l1, 1, "1.3")
    old = str(l1.cell(r12, 2).value)[:46]
    l1.cell(r12, 2).value = ANCHORS
    replace_block(l1, r12 + 1, r13, ANCHORS_B)
    log.append(("LOT 1 item 1.2", old, "hemijski (epoksidni) ankeri ≥30 kN + pull-out test",
                "Investor decision; calc B.6 — gravity foundation was 40 % short"))

    # ---- 2. concrete --------------------------------------------------------
    r = row_contains(l1, 2, "betonom C25")
    l1.cell(r, 2).value = str(l1.cell(r, 2).value) + CONCRETE_NOTE
    log.append(("LOT 1 item 2.3", "C25, no exposure class", "C30/37, XC4+XF3, air 4–6 %",
                "calc A.4 — freeze-thaw at 1076 m, EN 206"))

    # ---- 3. optional 3 x 4 --------------------------------------------------
    ru = row_startswith(l1, 1, "UKUPNO 1 —")
    l1.insert_rows(ru)
    copy_style(l1, ru - 1, ru)
    l1.cell(ru, 1).value = "1.8"
    l1.cell(ru, 2).value = ALT
    l1.cell(ru, 3).value = "kpl"
    l1.cell(ru, 4).value = 1
    l1.cell(ru, 6).value = None                      # deliberately outside every SUM
    log.append(("LOT 1 new item 1.8", "-", "OPCIJA: 3 nosača × 4 modula",
                "calc F.6 — halves sail per structure at the same 7,02 kWp"))

    # ---- rebuild LOT 1 totals ----------------------------------------------
    r1 = row_startswith(l1, 1, "UKUPNO 1 —")
    r2 = row_startswith(l1, 1, "UKUPNO 2 —")
    rl = row_startswith(l1, 1, "UKUPNO LOT 1 —")
    s2 = row_exact(l1, 1, "2.1")
    l1.cell(r1, 6).value = f"=SUM(F12:F{r1-1})"
    l1.cell(r2, 6).value = f"=SUM(F{s2}:F{r2-1})"
    l1.cell(rl, 6).value = f"=F{r1}+F{r2}"
    rr = row_startswith(l1, 1, "UKUPNO LOT 1 (bez PDV")
    l1.cell(rr, 6).value = f"=F{rl}"
    rp = row_startswith(l1, 1, "Popust")
    l1.cell(rp + 1, 6).value = f'=F{rr}*(1-IF(F{rp}="",0,F{rp}/100))'
    l1.cell(rp + 2, 6).value = f"=F{rp+1}*0.17"
    l1.cell(rp + 3, 6).value = f"=F{rp+1}+F{rp+2}"

    # ---- 4. RCD into the GRO ------------------------------------------------
    r = row_contains(l2, 2, "odvodnik prenapona AC")
    l2.insert_rows(r, len(RCD))
    for i, txt in enumerate(RCD):
        copy_style(l2, r + len(RCD), r + i)
        l2.cell(r + i, 2).value = txt
        for c in (1, 3, 4, 5, 6):
            l2.cell(r + i, c).value = None
    log.append(("LOT 2 GRO item 5.6", "no RCD in the board",
                "4p 63 A/300 mA S-type + 2 × RCBO 16 A/30 mA",
                "calc D.4 — SHUNT excitation, SC capacity 0 %"))

    # ---- rebuild LOT 2 totals, exact matches only --------------------------
    secs = [("1.1", "UKUPNO 3 —"), ("4.1", "UKUPNO 4 —"),
            ("5.1", "UKUPNO 5 —"), ("6.1", "UKUPNO 6 —")]
    ends = []
    for start, endlab in secs:
        st, en = row_exact(l2, 1, start), row_startswith(l2, 1, endlab)
        if st and en:
            l2.cell(en, 6).value = f"=SUM(F{st}:F{en-1})"
            ends.append(en)
    rlot2 = row_startswith(l2, 1, "UKUPNO LOT 2 —")
    l2.cell(rlot2, 6).value = "=" + "+".join(f"F{e}" for e in ends)

    # the two recap lines carry their labels in column B, not A
    a = row_startswith(l2, 2, "LOT 1 — NOSAČI")
    b = row_startswith(l2, 2, "LOT 2 — DIZEL")
    l2.cell(a, 6).value = f"='LOT 1'!F{rl}"
    l2.cell(b, 6).value = f"=F{rlot2}"
    rs = row_startswith(l2, 1, "SVE UKUPNO (LOT 1 + LOT 2) bez PDV")
    l2.cell(rs, 6).value = f"=SUM(F{a}:F{b})"
    rp2 = row_startswith(l2, 1, "Popust")
    l2.cell(rp2 + 1, 6).value = f'=F{rs}*(1-IF(F{rp2}="",0,F{rp2}/100))'
    l2.cell(rp2 + 2, 6).value = f"=F{rp2+1}*0.17"
    l2.cell(rp2 + 3, 6).value = f"=F{rp2+1}+F{rp2+2}"
    log.append(("LOT 2 totals", "shifted by the RCD rows",
                f"rebuilt; grand total ='LOT 1'!F{rl}", "re-pointed after row shifts"))

    wb.save(XLSX)
    for a_, b_, c_, d_ in log:
        print(f"  {a_:22s} {b_:34.34s} -> {c_:46.46s} | {d_}")
    print(f"\n{len(log)} changes | LOT 1 subtotal row {rl} | LOT 2 subtotal row {rlot2}")


if __name__ == "__main__":
    sys.exit(main())
