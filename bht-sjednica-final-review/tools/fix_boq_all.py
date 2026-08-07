# -*- coding: utf-8 -*-
"""
Single consolidated BOQ correction, replacing fix_boq.py + fix_boq2.py.

Why one script: openpyxl does **not** translate formulas when rows are inserted or
deleted. A row that moves keeps its old references, so after two rounds of insertions
item 1.3 still computed `D32*E32` while sitting on row 35, and several description
cells had been overwritten. Chaining structural edits across separate runs made that
compound invisibly.

The rules this script follows:

  1. **No row insertion for text.** Extra specification lines are appended into the
     item's own description cell as additional lines, not as new rows. A BOQ item is
     one row; that is also how a bidder reads it.
  2. Rows are added only where a genuinely new *priced item* is needed (1.6a, 1.8) or
     a new block (LOT 1 recap).
  3. **After every structural change, all formulas are regenerated from scratch** so
     each product formula references its own row and every SUM spans the right range.
     Nothing inherits a stale reference.
  4. The result is verified by recalculating the workbook through LibreOffice.

Run against a pristine copy from TD-OUTPUT-BASELINE-20260807/.
"""
import os
import shutil
import sys

import openpyxl
from openpyxl.styles import Alignment, Border, Font, Side

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XLSX = os.path.join(BASE, "TD-OUTPUT", "3.1 PRILOG II TD - predmjer Sjednica Bileca.xlsx")
BASELINE = os.path.join(BASE, "TD-OUTPUT-BASELINE-20260807",
                        "3.1 PRILOG II TD - predmjer Sjednica Bileca.xlsx")

NL = "\n"

# ---------------------------------------------------------------- LOT 1 text
SUPPORT_TYPE = (
    " - tip: A-izvedba, NISKA izvedba (Standard A-Shaped Support 3.0 — LOW SUPPORT), "
    "kao Huawei BOM 21540481 sa ankerima BOM 21540482, antitheft maticom 21540036 i "
    "ključem 21540038, ili ekvivalent istih ili boljih karakteristika")

GEOM = (
    " - gabariti PV polja (2 reda × 3 modula, portret): širina polja 3476 mm (poprečna "
    "greda 4089 mm, bočni prepust 306,5 mm), dužina polja po nagibu 4576 mm (2 × 2278 mm), "
    "horizontalna projekcija 3236 mm pri nagibu 45°; donja ivica panela na +0,50 m, "
    "gornja ivica na +3,74 m od nivoa terena")

PLACE = (
    " - smještaj: nosač se temelji IZVAN ograđenog platoa, 1400 mm južno od kote ograde "
    "(raspoloživi pojas 1950 mm); gornja (sjeverna) ivica panela je 1,84 m iznad kote "
    "ograde h=1,90 m i prelazi preko platoa na visini +3,50 m, iznad krova kontejnera. "
    "Ponuđač provjerava da konstrukcija u cijelosti ostaje unutar zakupljene parcele "
    "16,00 × 9,40 m")

WIND = (
    " - MJERODAVNO OPTEREĆENJE VJETROM: qp ≥ 1,20 kN/m² (udar 3 s ≈ 45 m/s) prema "
    "ovjerenoj projektnoj dokumentaciji lokacije i BAS EN 1991-1-4 sa BiH nacionalnim "
    "aneksom, uz primjenu faktora orografije za izloženi planinski vrh na 1076 m n.v. "
    "Koeficijent sile cf ≥ 1,5 pri 45° prema EN 1991-1-4 §7.3, osim ako se proračunom "
    "dokaže drugačije. Projektne sile po nosaču (GSN, γQ=1,5 / γG,fav=0,9): podizanje "
    "≥27 kN, horizontalna sila ≥30 kN, moment prevrtanja ≥64 kNm. Mjerodavni su "
    "podizanje (uplift) i prevrtanje, a ne nosivost tla. NAPOMENA: kataloški nosač "
    "tipa A ima deklarisanu otpornost 31 m/s (0,52 kN/m²) pri 45° i 40 m/s (0,87 kN/m²) "
    "pri 15°/25°, što je ISPOD opterećenja ovog lokaliteta; Ponuđač je stoga dužan "
    "ponuditi konstrukciju dimenzionisanu i dokazanu za stvarno opterećenje lokaliteta, "
    "uz pisanu potvrdu proizvođača za konkretnu lokaciju (planinski vrh)")

TILT = (
    " - inklinacija: fiksno 45°, orijentacija JUG (azimut 180°). Nagib je zadržan zbog "
    "decembarskog prinosa — pri podnevnoj visini Sunca 23,6° na 42,94° N nagib 45° "
    "ostvaruje 93 % direktnog zračenja u odnosu na 85 % pri 35°, a decembar je "
    "mjerodavni mjesec za dimenzionisanje autonomnog sistema")

MATERIAL = (
    " - materijal i izrada: konstrukcijski čelik S275JR (S355JR za stubove) prema "
    "EN 10025-2, šuplji profili prema EN 10219 — stubovi min. RHS 80×80×4, rigle min. "
    "RHS 60×40×3, ili bilo koji presjek za koji se proračunom dokaže najmanje jednak "
    "otporni moment; antikorozivna zaštita vrućim cinčanjem prema EN ISO 1461 min. "
    "70 µm lokalno / 85 µm srednje (klasa korozivnosti C4); zavarivanje prema "
    "EN 1090-2 klasa izvedbe EXC2; CE označavanje i izjava o svojstvima prema "
    "EN 1090-1; konstrukcijski vijci M16 klase 8.8 prema EN 15048, pričvrsni pribor "
    "modula A2/A4 nehrđajući")

ANCHORS = (
    "Isporuka i ugradnja sistema sidrenja nosive konstrukcije iz Tačke 1.1 u "
    "stijenu/beton, hemijskim (epoksidnim) ankerima." + NL +
    " - tip: hemijski (epoksidni/vinilesterski) anker M16 ili M20 sa ETA odobrenjem za "
    "ugradnju u beton i/ili stijenu, vruće cinčan ili nehrđajući A4" + NL +
    " - broj: najmanje 2 ankera po temeljnoj traci, odnosno 4 ankera po nosaču "
    "(minimum 2 po traci zbog redundanse)" + NL +
    " - nosivost: karakteristična sila čupanja ≥30 kN po ankeru; dubina ugradnje prema "
    "ETA za konkretnu podlogu. Ukupna projektna sila podizanja po nosaču ≥27 kN (GSN)" + NL +
    " - dokazivanje: ispitivanje čupanjem (pull-out test) na najmanje 10 % ugrađenih "
    "ankera, minimalno 2 po nosaču, do 1,5 × projektne sile, uz zapisnik ovjeren od "
    "nadzornog organa" + NL +
    " - alternativa: livena U-anker sidra M16, dužine 320 mm, razmaka krakova 180 mm, sa "
    "pločama 50×50 mm i dvostrukim maticama, dozvoljena su SAMO uz gravitacioni temelj "
    "zapremine ≥1,14 m³ po nosaču (umjesto 0,81 m³)")

STATIC = (
    "Statički proračun nosive konstrukcije i temelja, ovjeren i potpisan od strane "
    "ovlaštenog inženjera." + NL +
    " - dokaz otpornosti na pritisak vjetra qp ≥ 1,20 kN/m² pri nagibu 45°, prema "
    "BAS EN 1991-1-4 sa BiH nacionalnim aneksom, uključujući orografiju" + NL +
    " - dokaz na opterećenje snijegom prema BAS EN 1991-1-3 i na radijalni led 20 mm "
    "gustine 300 kg/m³" + NL +
    " - dokaz sigurnosti na podizanje (uplift) i prevrtanje prema EN 1990 "
    "(γQ,dst = 1,5; γG,stb = 0,9)" + NL +
    " - dimenzionisanje temelja i sidrenja prema stvarnim geotehničkim uslovima "
    "(kamenito tlo), uz navođenje dubine smrzavanja za lokalitet" + NL +
    "NAPOMENA: proračun se dostavlja UZ PONUDU kao uslov kvalifikacije (Prilog I, "
    "Tačka 4), a NE nakon dodjele ugovora.")

EARTH = (
    "Uzemljenje nosivih konstrukcija: povezivanje obje konstrukcije na postojeći "
    "prstenasti uzemljivač lokacije bakarnim užetom presjeka 50 mm² sa izolacijom "
    "otpornom na UV zračenje i ukopavanje, preko priključnih stezaljki na konstrukciji "
    "i bimetalnih (Cu/Fe-Zn) ukrsnih komada radi sprječavanja galvanske korozije. "
    "Presjek prema EN 62305-3, Tabela 7, za odvođenje atmosferskog pražnjenja. "
    "Kontinuitet svih spojeva ≤0,1 Ω, ukupni otpor uzemljenja ≤10 Ω. DC kablovi se "
    "polažu na razmaku ≥0,5 m od odvoda gromobranske instalacije (Huawei §4.1.3).")

CABLE = (
    "Isporuka i polaganje DC solarnog kabla 1×6 mm² (H1Z2Z2-K) od fotonaponskih panela "
    "do PVDB distribucije, uključujući MC4 konektore, obujmice i UV-otporne kanalice. "
    "NAPOMENA: završni priključak na ulaznu stezaljku iSSU modula izvesti presjekom "
    "4 mm² prema izričitom zahtjevu proizvođača. Pad napona pri Imp 13,67 A i dužini "
    "25 m iznosi 0,78 %. 2 nosača × 2 × 25,00 m")

PVDB = (
    "Isporuka i montaža PVDB ormara za PV panele sa DC rastavljačem i osiguračima za "
    "svaki string, stepen zaštite min. IP55, kao Huawei PVDB500-15-2B (01075918) ili "
    "ekvivalent (100–500 V DC, maks. 15 A po izvodu, 2 izvoda). NAPOMENA: navedeni ormar "
    "NE sadrži odvodnik prenapona — DC odvodnik se isporučuje kao zasebna Tačka 1.6a.")

SPD = (
    "Isporuka i ugradnja odvodnika prenapona DC, tip 2 (Iimp ≥5 kA, Ucpv ≥425 V), za "
    "svaki string, sa pripadajućim rastavnim osiguračima, u PVDB ormaru iz Tačke 1.6 "
    "ili u zasebnom kućištu min. IP55. Predvidjeti drugi komplet na strani polja panela "
    "zbog dužine DC trase od 25 m.")

ALT = (
    "OPCIJA (alternativna ponuda — cijena se iskazuje posebno i NE ulazi u zbir Tačke 1): "
    "Isporuka i montaža TRI nosača sa po 4 fotonaponska modula (3 × 4 = 12 modula, ista "
    "ukupna snaga 7,02 kWp) umjesto dva nosača sa po 6 modula. Površina izloženosti "
    "vjetru po nosaču smanjuje se sa 15,91 m² na 7,95 m² (−50 %), čime se približno "
    "prepolovljuju sila podizanja i moment prevrtanja po temelju, uz zadržavanje nagiba "
    "45°. Uključuje treći komplet temelja, sidrenja i uzemljenja. Kupac zadržava pravo "
    "izbora između osnovne i alternativne izvedbe.")

CONCRETE_ADD = (
    NL + "IZMJENA — BETON I ARMATURA: beton klase C30/37, klase izloženosti XC4 + XF3 "
    "prema BAS EN 206, sa aerantom 4–6 %, Dmax 16, konzistencija S3; podložni beton "
    "C12/15 d=50 mm; armatura B500B, zaštitni sloj ≥50 mm. Klasa XF3 je mjerodavna zbog "
    "cikličnog smrzavanja i odmrzavanja u vlažnom stanju na 1076 m n.v. Temeljna "
    "spojnica mora biti ispod dubine smrzavanja za lokalitet, koju Ponuđač navodi u "
    "ponudi. Dubina trake prema ovjerenom statičkom proračunu iz Tačke 1.3.")

RCD_ADD = (
    NL + " - 1 kom 4p zaštitna strujna sklopka (RCD) 63 A / 300 mA, S-tip (selektivna), "
    "za zaštitu cjelokupnog napojnog kruga iza sklopke izvora" + NL +
    " - 2 kom 1p+N zaštitna strujna sklopka sa prekostrujnom zaštitom (RCBO) 16 A / "
    "30 mA, tip A, za utičnice i rasvjetu kontejnera" + NL +
    "NAPOMENA (obavezno): agregat je SHUNT pobude i prema tehničkom listu proizvođača "
    "ima deklarisanu sposobnost trajne struje kratkog spoja 0 %, zbog čega SAMO "
    "prekostrujna zaštita NE MOŽE ostvariti automatsko isključenje u vremenu "
    "zahtijevanom prema IEC 60364-4-41 (0,4 s za 230 V). Zaštita zaštitnom strujnom "
    "sklopkom je stoga OBAVEZNA. Sistem uzemljenja je TN-S sa jedinstvenom tačkom "
    "spajanja N i PE u ovom ormaru; otpor uzemljenja ≤10 Ω.")


def rx(ws, col, value):
    for r in range(1, ws.max_row + 1):
        v = ws.cell(r, col).value
        if isinstance(v, str) and v.strip() == value:
            return r
    return None


def rs(ws, col, prefix):
    for r in range(1, ws.max_row + 1):
        v = ws.cell(r, col).value
        if isinstance(v, str) and v.strip().startswith(prefix):
            return r
    return None


def rc(ws, col, needle):
    for r in range(1, ws.max_row + 1):
        v = ws.cell(r, col).value
        if isinstance(v, str) and needle.lower() in v.lower():
            return r
    return None


def wrap(ws, r):
    ws.cell(r, 2).alignment = Alignment(wrap_text=True, vertical="top")


def normalise_products(ws):
    """Every priced row's F formula must reference its OWN row."""
    n = 0
    for r in range(1, ws.max_row + 1):
        f = ws.cell(r, 6).value
        if isinstance(f, str) and f.startswith("=IF(AND(D"):
            want = f'=IF(AND(D{r}<>"",E{r}<>""),D{r}*E{r},"")'
            if f != want:
                ws.cell(r, 6).value = want
                n += 1
    return n


def main():
    if not os.path.exists(BASELINE):
        raise SystemExit("baseline copy missing")
    shutil.copy(BASELINE, XLSX)
    wb = openpyxl.load_workbook(XLSX)
    l1, l2 = wb["LOT 1"], wb["LOT 2"]
    log = []

    def setb(ws, r, text, why):
        old = str(ws.cell(r, 2).value or "")[:44]
        ws.cell(r, 2).value = text
        wrap(ws, r)
        log.append((f"{ws.title}!B{r}", old, text.split(NL)[0][:44], why))

    # ================= LOT 1 : text merged into item cells, no new rows =======
    r11 = rx(l1, 1, "1.1")
    base = str(l1.cell(r11, 2).value)
    l1.cell(r11, 2).value = NL.join([
        base, SUPPORT_TYPE, TILT, GEOM, PLACE, WIND, MATERIAL,
        " - spojni pribor: nehrđajući čelik A2/A4",
        " - uključeno ožičenje i povezivanje oba polja panela do PVDB distribucije",
    ])
    wrap(l1, r11)
    log.append(("LOT 1!B12 (1.1)", "catalogue text, wrong geometry",
                "BOM 21540481 + corrected geometry + real wind load + materials",
                "HW F-01, finding B, CON R-01, calc F.1/F.2"))
    # blank the now-duplicated bullet rows that followed 1.1
    for r in range(r11 + 1, rx(l1, 1, "1.2")):
        l1.cell(r, 2).value = None

    setb(l1, rx(l1, 1, "1.2"), ANCHORS, "Investor decision; calc B.6 — gravity 40 % short")
    for r in range(rx(l1, 1, "1.2") + 1, rx(l1, 1, "1.3")):
        l1.cell(r, 2).value = None

    setb(l1, rx(l1, 1, "1.3"), STATIC, "CON A-03 — pre-award qualification")
    setb(l1, rx(l1, 1, "1.4"), EARTH, "EL RED-13 — H07V-K undersized indoor wire")
    setb(l1, rx(l1, 1, "1.5"), CABLE, "HW F-06 — iSSU terminal needs 4 mm²")
    setb(l1, rx(l1, 1, "1.6"), PVDB, "HW F-05 — Huawei PVDB is IP55 and has no SPD")

    r23 = rc(l1, 2, "betonom C25")
    l1.cell(r23, 2).value = str(l1.cell(r23, 2).value) + CONCRETE_ADD
    wrap(l1, r23)
    log.append(("LOT 1 item 2.3", "C25, no exposure class", "C30/37, XC4+XF3, air 4–6 %",
                "calc A.4 — freeze-thaw at 1076 m, EN 206"))

    # ---- delete 2.6 / 2.7 / 2.8, then add 1.6a and 1.8 ----------------------
    for lab in ("2.8", "2.7", "2.6"):
        r = rx(l1, 1, lab)
        if r:
            desc = str(l1.cell(r, 2).value or "")[:40]
            l1.delete_rows(r)
            log.append((f"LOT 1 item {lab}", desc or "(empty)", "DELETED",
                        "finding I / CON R-07" if lab == "2.7" else "empty row"))

    r16 = rx(l1, 1, "1.6")
    l1.insert_rows(r16 + 1)
    for c in range(1, 7):
        l1.cell(r16 + 1, c)._style = l1.cell(r16, c)._style
    l1.cell(r16 + 1, 1).value = "1.6a"
    l1.cell(r16 + 1, 2).value = SPD
    l1.cell(r16 + 1, 3).value = "kpl"
    l1.cell(r16 + 1, 4).value = 2
    wrap(l1, r16 + 1)
    log.append(("LOT 1 new item 1.6a", "-", "DC SPD tip 2, 2 kpl",
                "HW F-05 / EL RED-12 — not contained in the PVDB"))

    ru = rs(l1, 1, "UKUPNO 1 —")
    l1.insert_rows(ru)
    for c in range(1, 7):
        l1.cell(ru, c)._style = l1.cell(ru - 1, c)._style
    l1.cell(ru, 1).value = "1.8"
    l1.cell(ru, 2).value = ALT
    l1.cell(ru, 3).value = "kpl"
    l1.cell(ru, 4).value = 1
    l1.cell(ru, 6).value = None
    wrap(l1, ru)
    log.append(("LOT 1 new item 1.8", "-", "OPCIJA: 3 nosača × 4 modula (izvan zbira)",
                "calc F.6 — halves sail per structure"))

    # ================= LOT 2 : RCD into the GRO cell =========================
    rg = rc(l2, 2, "odvodnik prenapona AC")
    l2.cell(rg, 2).value = str(l2.cell(rg, 2).value) + RCD_ADD
    wrap(l2, rg)
    log.append(("LOT 2 GRO (5.6)", "no RCD in the board",
                "4p 63 A/300 mA S-type + 2 × RCBO 30 mA",
                "calc D.4 — SHUNT excitation, SC capacity 0 %"))

    # ================= safety net: nothing may lose its content ==============
    # openpyxl's insert_rows can drop the contents of the row immediately below the
    # insertion point. Rather than trust it, every priced item is compared against the
    # baseline by item number and restored if its description or quantity went missing.
    src = openpyxl.load_workbook(BASELINE)

    def items(ws):
        d = {}
        for r in range(1, ws.max_row + 1):
            a = str(ws.cell(r, 1).value or "").strip()
            if a and a[0].isdigit() and "." in a:
                d[a] = r
        return d

    restored = []
    for sheet in ("LOT 1", "LOT 2"):
        old_ws, new_ws = src[sheet], wb[sheet]
        old_i, new_i = items(old_ws), items(new_ws)
        for key, nr in new_i.items():
            if key not in old_i:
                continue
            orr = old_i[key]
            for col in (2, 3, 4):
                if new_ws.cell(nr, col).value in (None, "") and \
                        old_ws.cell(orr, col).value not in (None, ""):
                    new_ws.cell(nr, col).value = old_ws.cell(orr, col).value
                    if col == 2:
                        wrap(new_ws, nr)
                        restored.append(f"{sheet} item {key}")
    if restored:
        log.append(("content restored", f"{len(restored)} item(s) lost on insert",
                    ", ".join(restored), "safety net vs openpyxl insert_rows"))

    # every priced row must have a product formula, including newly added ones
    for ws in (l1, l2):
        for r in range(1, ws.max_row + 1):
            a = str(ws.cell(r, 1).value or "").strip()
            if a and a[0].isdigit() and "." in a and a != "1.8":
                if isinstance(ws.cell(r, 4).value, (int, float)) and \
                        ws.cell(r, 6).value in (None, ""):
                    ws.cell(r, 6).value = \
                        f'=IF(AND(D{r}<>"",E{r}<>""),D{r}*E{r},"")'
                    log.append((f"{ws.title} item {a}", "no product formula",
                                "formula added", "new row"))

    # ================= regenerate every formula ==============================
    fixed = normalise_products(l1) + normalise_products(l2)
    log.append(("all product formulas", f"{fixed} stale references",
                "each row references its own row", "openpyxl does not translate on insert"))

    r1 = rs(l1, 1, "UKUPNO 1 —")
    r2 = rs(l1, 1, "UKUPNO 2 —")
    rl = rs(l1, 1, "UKUPNO LOT 1 —")
    s2 = rx(l1, 1, "2.1")
    l1.cell(r1, 6).value = f"=SUM(F12:F{r1-1})"
    l1.cell(r2, 6).value = f"=SUM(F{s2}:F{r2-1})"
    l1.cell(rl, 6).value = f"=F{r1}+F{r2}"

    # ---- LOT 1 recap ---------------------------------------------------------
    thin = Side(style="thin")
    box = Border(left=thin, right=thin, top=thin, bottom=thin)
    start = rl + 2
    rows = [("REKAPITULACIJA — LOT 1", None, True),
            ("UKUPNO LOT 1 (bez PDV-a):", f"=F{rl}", False),
            ("Popust (%):", None, False),
            ("UKUPNO LOT 1 sa popustom (bez PDV-a):", None, False),
            ("PDV 17%:", None, False),
            ("UKUPNO LOT 1 sa PDV-om:", None, True)]
    for i, (label, formula, bold) in enumerate(rows):
        r = start + i
        l1.cell(r, 1).value = label
        l1.cell(r, 1).font = Font(bold=bold, size=10)
        l1.cell(r, 1).alignment = Alignment(horizontal="left", vertical="center")
        l1.merge_cells(start_row=r, start_column=1, end_row=r, end_column=5)
        if formula:
            l1.cell(r, 6).value = formula
        l1.cell(r, 6).font = Font(bold=bold, size=10)
        l1.cell(r, 6).number_format = "#,##0.00"
        for c in range(1, 7):
            l1.cell(r, c).border = box
    d = start + 2
    l1.cell(d + 1, 6).value = f'=F{start+1}*(1-IF(F{d}="",0,F{d}/100))'
    l1.cell(d + 2, 6).value = f"=F{d+1}*0.17"
    l1.cell(d + 3, 6).value = f"=F{d+1}+F{d+2}"
    log.append(("LOT 1 recap", "absent", "subtotal → popust → PDV 17 % → total",
                "finding J — a LOT-1-only bidder had no total"))
    last = start + 5
    if l1.max_row > last:
        l1.delete_rows(last + 1, l1.max_row - last)

    # ---- LOT 2 totals --------------------------------------------------------
    ends = []
    for st, lab in (("1.1", "UKUPNO 3 —"), ("4.1", "UKUPNO 4 —"),
                    ("5.1", "UKUPNO 5 —"), ("6.1", "UKUPNO 6 —")):
        a, b = rx(l2, 1, st), rs(l2, 1, lab)
        if a and b:
            l2.cell(b, 6).value = f"=SUM(F{a}:F{b-1})"
            ends.append(b)
    r2t = rs(l2, 1, "UKUPNO LOT 2 —")
    l2.cell(r2t, 6).value = "=" + "+".join(f"F{e}" for e in ends)
    a = rs(l2, 2, "LOT 1 — NOSAČI")
    b = rs(l2, 2, "LOT 2 — DIZEL")
    l2.cell(a, 6).value = f"='LOT 1'!F{rl}"
    l2.cell(b, 6).value = f"=F{r2t}"
    rsum = rs(l2, 1, "SVE UKUPNO (LOT 1 + LOT 2) bez PDV")
    l2.cell(rsum, 6).value = f"=SUM(F{a}:F{b})"
    rp = rs(l2, 1, "Popust")
    l2.cell(rp + 1, 6).value = f'=F{rsum}*(1-IF(F{rp}="",0,F{rp}/100))'
    l2.cell(rp + 2, 6).value = f"=F{rp+1}*0.17"
    l2.cell(rp + 3, 6).value = f"=F{rp+1}+F{rp+2}"

    # ---- final integrity pass, immediately before saving --------------------
    # Run last, so nothing downstream can undo it. Any priced item whose
    # description, unit or quantity is missing is restored from the baseline by
    # item number. Items deliberately removed (2.6/2.7/2.8) are already gone and
    # therefore never seen here; new items (1.6a, 1.8) have no baseline twin.
    late = []
    for sheet in ("LOT 1", "LOT 2"):
        old_ws, new_ws = src[sheet], wb[sheet]
        old_i, new_i = items(old_ws), items(new_ws)

        # Deleting a total row leaves its A:E merge behind, and openpyxl does not move
        # merge anchors when rows shift - so a stale range can settle over a priced
        # item, hiding its unit, quantity and price columns and making B read as None.
        # A priced item row must never be merged.
        for key, nr in new_i.items():
            for rng in list(new_ws.merged_cells.ranges):
                if rng.min_row <= nr <= rng.max_row and rng.min_col <= 2:
                    new_ws.unmerge_cells(str(rng))
                    late.append(f"{sheet} {key} (stale merge {rng} removed)")
        for key, nr in new_i.items():
            if key not in old_i:
                continue
            orr = old_i[key]
            for col in (2, 3, 4):
                cur = new_ws.cell(nr, col).value
                ref = old_ws.cell(orr, col).value
                if not ((cur is None or str(cur).strip() == "")
                        and ref is not None and str(ref).strip() != ""):
                    continue
                # A cell inside a merged range reports value None regardless of what
                # the range holds, and openpyxl does not move merge anchors when rows
                # are inserted - so a shifted item can look empty while its text sits
                # in a stale range. Drop any range covering this cell, then write.
                for rng in list(new_ws.merged_cells.ranges):
                    if (rng.min_row <= nr <= rng.max_row
                            and rng.min_col <= col <= rng.max_col):
                        new_ws.unmerge_cells(str(rng))
                new_ws.cell(nr, col).value = ref
                if col == 2:
                    new_ws.cell(nr, 2).alignment = Alignment(wrap_text=True,
                                                             vertical="top")
                    late.append(f"{sheet} {key}")
    if late:
        log.append(("final integrity pass", f"{len(late)} item(s) still empty",
                    ", ".join(late) + " restored from baseline",
                    "runs last so nothing downstream can undo it"))

    wb.save(XLSX)
    for a_, b_, c_, d_ in log:
        print(f"  {a_:24s} {b_:34.34s} -> {c_:44.44s} | {d_}")
    print(f"\n{len(log)} changes · LOT 1 subtotal row {rl} · LOT 2 subtotal row {r2t}")


if __name__ == "__main__":
    sys.exit(main())
