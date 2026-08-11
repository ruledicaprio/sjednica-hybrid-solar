# -*- coding: utf-8 -*-
"""
Rev-2 BOQ corrections: closes the open items of review/07-calculations.md section G
that were specified in Prilog I but never priced, and aligns the priced document
with the new container layout (drawing M-01).

Runs ON TOP of fix_boq_all.py's output in TD-OUTPUT, not from the baseline.

Same rules as fix_boq_all.py, and for the same reason - openpyxl does not
translate formulas when rows move:

  1. Wording changes are appended into the item's own description cell.
  2. Rows are inserted only for genuinely new PRICED items, always immediately
     before the section's UKUPNO row.
  3. Every product formula and every SUM range is regenerated afterwards.
  4. The result is verified by recalculating through LibreOffice
     (tools/check_boq_recalc.py).

Closes: G-2 (concrete class stated twice, inconsistently), G-3 (floor capacity
claimed from a K3 container), G-5 (fire elaborate / fuel shut-off / ventilation
interlock unpriced), G-6 (AC SPD only type 2, no data-line SPD), G-7 (three
different power systems named), G-9 (obstruction lighting absent).
"""
import os
import sys

import openpyxl
from openpyxl.styles import Alignment

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fix_boq_all import normalise_products, rc, rs, rx, wrap  # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XLSX = os.path.join(BASE, "TD-OUTPUT",
                    "3.1 PRILOG II TD - predmjer Sjednica Bileca.xlsx")
NL = "\n"

# --------------------------------------------------------------- new items
FIRE_ELABORAT = (
    "Izrada elaborata zaštite od požara za prostor agregata sa 500 l dizel goriva, "
    "od strane ovlaštene kuće, sa mjerama koje se ugrađuju u izvedbu (klasifikacija "
    "prostora, potrebna vatrootpornost pregrada, izbor i raspored detekcije i "
    "gašenja). Elaborat se izrađuje i dostavlja Kupcu PRIJE početka izvođenja "
    "radova, a izvedeno stanje mora biti u skladu sa njim.")

FIRE_VALVE = (
    "Isporuka i ugradnja protupožarnog (sigurnosnog) ventila na izlaznom vodu "
    "goriva iz spremnika, sa termičkim okidanjem (topljivi osigurač) ili "
    "solenoidnom izvedbom, koji zatvara dovod goriva pri požaru i pri aktiviranju "
    "tastera EMERGENCY STOP. Komplet sa nosačem, spojnim materijalom, uvezivanjem "
    "u sistem detekcije požara i funkcionalnim ispitivanjem.")

FIRE_INTERLOCK = (
    "Isporuka, ugradnja i parametriranje blokade ventilacije pri aktiviranju "
    "automatskog gašenja: pri detekciji požara i aktivaciji uređaja za gašenje "
    "automatski se zaustavlja agregat, isključuje aksijalni ventilator prostora i "
    "zatvaraju se motorne žaluzine dovoda i odvoda zraka, kako sredstvo za gašenje "
    "ne bi bilo odneseno strujom zraka. Uključene motorne klapne na usisnoj i "
    "izlaznoj žaluzini, upravljački modul, kablovanje i funkcionalno ispitivanje.")

CIRCUIT_TRANSFER = (
    "Snimanje postojećeg stanja i prevezivanje postojećih strujnih krugova na novi "
    "GRO iz Tačke 5.6. Obuhvata:" + NL +
    " - snimanje i evidentiranje svih 7 postojećih strujnih krugova postojećeg "
    "razvoda, sa mjerenjem opterećenja i izradom jednopolne sheme zatečenog stanja" + NL +
    " - prevezivanje krugova na odgovarajuće izvode novog GRO, sa označavanjem" + NL +
    " - SIGNALNA RASVJETA PREPREKE antenskog stuba h=38 m (krug K7) izvodi se kao "
    "ZASEBAN NADZIRANI strujni krug, sa nadzorom prisustva napona i strujnim "
    "nadzorom ispravnosti svjetiljke, i dojavom ispada u sistem daljinskog nadzora "
    "— rasvjeta prepreke je trajno noćno opterećenje i ne smije biti isključena "
    "prilikom rekonfiguracije napajanja" + NL +
    " - Ponuđač mjeri stvarnu snagu rasvjete prepreke i dostavlja je Kupcu radi "
    "provjere energetskog bilansa (Prilog I, Tačka 1)" + NL +
    "Komplet sa spojnim materijalom, oznakama, ispitivanjem i ažuriranom "
    "jednopolnom shemom izvedenog stanja.")

DATA_SPD = (
    "Isporuka i ugradnja odvodnika prenapona za SIGNALNE i KOMUNIKACIONE VODOVE "
    "prema EN 61643-21: na signalnom kablu J-Y(ST)Y i na Ethernet vodu prema "
    "kontroleru agregata i sistemu daljinskog nadzora, na oba kraja dionice. "
    "Objekat ima vanjski sistem zaštite od munje i antenski stub h=38 m, pa je "
    "zaštita signalnih vodova obavezna prema EN 62305-4. Komplet sa nosačima, "
    "uzemljenjem odvodnika i ispitivanjem.")

# --------------------------------------------------------------- text edits
FLOOR_NOTE = (
    "Opšte napomene  NOSIVOST PODA KONTEJNERA: mjerodavna projektna vrijednost je "
    "2,00 kN/m² prema Projektnom zadatku. Ranije navedenih 10,00 kN/m² preuzeto je "
    "iz statičkog proračuna tipskog kontejnera K3, a na ovoj lokaciji ugrađen je "
    "kontejner tipa K2, pa ta vrijednost NIJE mjerodavna. Agregat (385 kg mokro na "
    "0,96 m² = 3,93 kN/m²) i pun spremnik (≈590 kg na 0,63 m² = 9,2 kN/m²) oba "
    "prekoračuju projektnu nosivost, zbog čega je OBAVEZAN čelični ram/roštilj za "
    "raznošenje opterećenja ispod skida I ispod tankvane, sa prenosom opterećenja "
    "na temeljnu konstrukciju, dokazan statičkim proračunom iz Tačke 4.4."
    "Napomena uz Tačku 4: DEA se ugrađuje u postojeći kontejner na lokaciji, u "
    "\"inside skid\" izvedbi (agregat na zajedničkom nosivom skid-okviru, bez "
    "vlastitog vanjskog kućišta, jer funkciju kućišta preuzima kontejner). "
    "Referentna izvedba data je u Prilogu III")

LAYOUT_INTAKE = (
    NL + "RASPORED (OBAVEZNO, prema crtežu M-01): žaluzina se ugrađuje u JUŽNI zid "
    "kontejnera, na istočnom kraju, sa donjom ivicom na cca 0,30 m od poda. "
    "Prostorna udaljenost od izduva i od odušne cijevi spremnika ≥3 m. Nije "
    "dozvoljeno izvesti dovod zraka kroz ulazna vrata.")

LAYOUT_DISCHARGE = (
    NL + "RASPORED (OBAVEZNO, prema crtežu M-01): žaluzina se ugrađuje u ZAPADNI "
    "zid kontejnera, na osi radijatora agregata. Topli zrak se NE smije izbacivati "
    "prema SJEVERNOJ strani, gdje se nalaze postojeći vanjski ormari ICC330-H1 i "
    "MTS9302.")

LAYOUT_DUCT = (
    NL + "RASPORED (OBAVEZNO, prema crtežu M-01): kanal se vodi najkraćim putem od "
    "radijatora kroz ZAPADNI zid kontejnera do izlazne žaluzine iz Tačke 4.7.")

LAYOUT_FAN = (
    NL + "RASPORED (OBAVEZNO, prema crtežu M-01): ventilator se ugrađuje u ISTOČNI "
    "zid kontejnera, u gornjoj zoni (donja ivica cca 1,75 m), sjeverno od ulaznih "
    "vrata.")

LAYOUT_EXHAUST = (
    NL + "IZMJENA — PREČNIK I TRASA: usvaja se DN 65 umjesto NO 50 (pri NO 50 brzina "
    "izduvnih gasova je 33 m/s, iznad uobičajenih 30 m/s; protutlak je zadovoljen u "
    "oba slučaja). Trasa: fleksibilni spoj i prigušivač neposredno iza motora, "
    "uspon uz ZAPADNI zid kontejnera, završetak IZNAD KROVA usmjeren naviše, sa "
    "hvatačem iskri, na prostornoj udaljenosti ≥3 m od usisne žaluzine i od odušne "
    "cijevi spremnika (prema crtežu M-01).")

TANK_DIMS = (
    NL + " - referentne dimenzije spremnika 1050 × 600 × 1310 mm, masa prazan 170 kg "
    "(pun ≈590 kg); smještaj uz SJEVERNI zid kontejnera u tankvani iz Tačke 4.3, "
    "prema crtežu M-01")

EXCITATION_REF = (
    "    kao Stamford BCI164C U IZVEDBI SA PMG ILI AREP/AUX POBUDOM, ili "
    "ekvivalent — standardna SHUNT izvedba NIJE prihvatljiva (v. zahtjev za "
    "pobudu iznad)")

SPD_AC = (
    " - 1 kom odvodnik prenapona AC, KOMBINOVANI TIP 1 + 2 prema EN 61643-11, "
    "Iimp ≥12,5 kA (10/350 µs) po polu, Up ≤1,5 kV, 4p, sa signalizacijom za "
    "daljinsko očitanje stanja i uvezanim statusom sa kontrolerom agregata. "
    "Objekat ima vanjski sistem zaštite od munje (antenski stub h=38 m), pa "
    "odvodnik tipa 2 sam po sebi NIJE dovoljan prema EN 62305-4.")

POWER_SYSTEM_OLD = "Huawei PowerCube 1000"
POWER_SYSTEM_NEW = "Huawei ICC330-H1 + MTS9302 ili kompatibilan"

FLOOR_ITEM = (
    "OBAVEZAN statički proračun nosivosti podne konstrukcije postojećeg "
    "kontejnera, ovjeren od strane ovlaštenog inženjera, te izvođenje OJAČANJA "
    "poda. Ojačanje obuhvata izradu i ugradnju čeličnog roštilja/rama za "
    "raznošenje opterećenja ISPOD SKIDA AGREGATA I ISPOD TANKVANE SA SPREMNIKOM, "
    "sa prenosom opterećenja na temeljnu konstrukciju kontejnera, uključujući "
    "antikorozivnu zaštitu i sav spojni materijal." + NL +
    "OBRAZLOŽENJE: mjerodavna projektna nosivost poda je 2,00 kN/m² prema "
    "Projektnom zadatku. Agregat daje 3,93 kN/m² (385 kg mokro na 0,96 m²), a pun "
    "spremnik 9,2 kN/m² (≈590 kg na 0,63 m²) — oba prekoračuju projektnu "
    "vrijednost, pa je ojačanje NEOPHODNO, a ne uslovno. Ranija formulacija se "
    "pozivala na proračun tipskog kontejnera K3 (10,00 kN/m²), koji NIJE "
    "mjerodavan jer je na ovoj lokaciji ugrađen kontejner tipa K2." + NL +
    "Zapremina spremnika se ne umanjuje.")

CONCRETE_FIX = (
    "Nabavka materijala, transport i betoniranje DVIJE temeljne trake po nosaču, "
    "betonom C30/37 klase izloženosti XC4 + XF3 prema BAS EN 206 (aerant 4–6 %, "
    "Dmax 16, konzistencija S3), uz upotrebu oplate i njegovanje betona. Armatura "
    "B500B, zaštitni sloj ≥50 mm, prema ovjerenom statičkom proračunu iz Tačke 1.3. "
    "Obračun po m³ ugrađenog betona. 3 nosača × 2 trake × 0,41 m³")


def append(ws, r, text, log, why):
    ws.cell(r, 2).value = str(ws.cell(r, 2).value or "") + text
    wrap(ws, r)
    log.append((f"{ws.title}!B{r}", text.strip().split(NL)[0][:48], why))


def add_item(ws, before_label, number, desc, unit, qty, log, why):
    """Insert a priced row immediately above the section's UKUPNO row."""
    r = rs(ws, 1, before_label)
    ws.insert_rows(r)
    for c in range(1, 7):
        ws.cell(r, c)._style = ws.cell(r - 1, c)._style
    ws.cell(r, 1).value = number
    ws.cell(r, 2).value = desc
    ws.cell(r, 3).value = unit
    ws.cell(r, 4).value = qty
    ws.cell(r, 6).value = f'=IF(AND(D{r}<>"",E{r}<>""),D{r}*E{r},"")'
    wrap(ws, r)
    log.append((f"{ws.title} new item {number}", desc.split(NL)[0][:48], why))
    return r


def free_cell(ws, r, col=6):
    """Drop any merged range covering (r, col).

    Inserting rows shifts cell contents but leaves merge anchors where they were,
    so a range that used to sit over a note block can end up covering a recap
    cell. Writing to a MergedCell is silently discarded, so the formula would
    vanish without any error - unmerge first.
    """
    for rng in list(ws.merged_cells.ranges):
        if rng.min_row <= r <= rng.max_row and rng.min_col <= col <= rng.max_col:
            ws.unmerge_cells(str(rng))


def priced_items(ws):
    out = {}
    for r in range(1, ws.max_row + 1):
        a = str(ws.cell(r, 1).value or "").strip()
        if a and a[0].isdigit() and "." in a:
            out[a] = r
    return out


def main():
    wb = openpyxl.load_workbook(XLSX)
    src = openpyxl.load_workbook(XLSX)          # untouched reference copy
    l1, l2 = wb["LOT 1"], wb["LOT 2"]
    log = []

    # ---------------- G-2: one concrete class per item ----------------------
    r23 = rc(l1, 2, "betonom C25")
    tail = str(l1.cell(r23, 2).value)
    keep = tail[tail.index("IZMJENA — BETON"):] if "IZMJENA — BETON" in tail else ""
    l1.cell(r23, 2).value = CONCRETE_FIX + (NL + keep if keep else "")
    wrap(l1, r23)
    log.append(("LOT 1 item 2.3", "C25 / Ø10 335 MPa removed from the lead text",
                "G-2 — the item stated two different concrete classes"))

    r22b = rc(l1, 2, "betona C10")
    l1.cell(r22b, 2).value = str(l1.cell(r22b, 2).value).replace(
        "betona C10", "podložnog betona C12/15")
    wrap(l1, r22b)
    log.append(("LOT 1 item 2.2b", "C10 -> C12/15 blinding",
                "G-2 — C10 is not a BAS EN 206 class for this exposure"))

    # ---------------- G-3: floor capacity ----------------------------------
    r58 = rc(l2, 2, "Nosivost poda kontejnera je 10,00")
    l2.cell(r58, 2).value = FLOOR_NOTE
    wrap(l2, r58)
    log.append(("LOT 2 section 4 note", "10,00 kN/m² (K3) -> 2,00 kN/m² (K2)",
                "G-3 / CON R-08 — the quoted figure came from another container type"))

    # ---------------- layout per drawing M-01 -------------------------------
    append(l2, rc(l2, 2, "dvoplašnog spremnika dizel goriva"), TANK_DIMS, log,
           "real tank data supplied 2026-08-11")
    append(l2, rx(l2, 1, "4.6"), LAYOUT_DUCT, log, "EL RED-03 — cross-flow layout")
    append(l2, rx(l2, 1, "4.7"), LAYOUT_DISCHARGE, log, "EL RED-03 — off the cabinet wall")
    append(l2, rx(l2, 1, "4.8"), LAYOUT_INTAKE, log, "EL RED-03 — intake through the south wall")
    append(l2, rx(l2, 1, "4.9"), LAYOUT_FAN, log, "EL RED-03 — cross-flow layout")
    append(l2, rx(l2, 1, "4.11"), LAYOUT_EXHAUST, log,
           "calc C.4 — 33 m/s at NO 50; west-wall route")

    # ---------------- G-4 residual: excitation reference --------------------
    r34 = rc(l2, 2, "kao Stamford BCI164C")
    l2.cell(r34, 2).value = EXCITATION_REF
    wrap(l2, r34)
    log.append(("LOT 2 generator reference", "BCI164C -> PMG/AREP variant required",
                "G-4 residual — the named reference is shunt-excited by default"))

    # ---------------- G-6 / G-7: GRO contents -------------------------------
    rspd = rc(l2, 2, "odvodnik prenapona AC")
    old = str(l2.cell(rspd, 2).value)
    l2.cell(rspd, 2).value = SPD_AC + old[old.index(NL):] if NL in old else SPD_AC
    wrap(l2, rspd)
    log.append(("LOT 2 GRO AC SPD", "40 kA type 2 -> type 1+2, Iimp ≥12,5 kA",
                "G-6 — Prilog I required type 1+2, the BOQ priced type 2"))

    # substring replacement, not whole-cell: item 5.6 names the rectifier both in
    # its own long description and in a bullet, and overwriting the cell would
    # throw away the rest of the GRO specification
    hits = 0
    for r in range(1, l2.max_row + 1):
        v = l2.cell(r, 2).value
        if isinstance(v, str) and POWER_SYSTEM_OLD in v:
            l2.cell(r, 2).value = v.replace(POWER_SYSTEM_OLD, POWER_SYSTEM_NEW)
            wrap(l2, r)
            hits += 1
    log.append(("LOT 2 rectifier naming", f"PowerCube 1000 -> ICC330-H1 + MTS9302 ({hits}x)",
                "G-7 — Investor's decision, matches drawings S-01/S-02"))

    # G-3 continued: item 4.4 still argued from the K3 sheet that no strengthening
    # was expected, which contradicts the section note and Prilog I 4.2
    r44 = rx(l2, 1, "4.4")
    l2.cell(r44, 2).value = FLOOR_ITEM
    wrap(l2, r44)
    log.append(("LOT 2 item 4.4", "'ojačanje se NE očekuje' -> strengthening required",
                "G-3 — both loads exceed the 2,00 kN/m² brief value"))

    # ---------------- G-5 / G-6 / G-9: new priced items ---------------------
    add_item(l2, "UKUPNO 4 —", "4.19", FIRE_ELABORAT, "kpl", 1, log,
             "G-5 — required by Prilog I 4.7, never priced")
    add_item(l2, "UKUPNO 4 —", "4.20", FIRE_VALVE, "kpl", 1, log,
             "G-5 — required by Prilog I 4.2, never priced")
    add_item(l2, "UKUPNO 4 —", "4.21", FIRE_INTERLOCK, "kpl", 1, log,
             "G-5 — required by Prilog I 4.7, never priced")
    add_item(l2, "UKUPNO 5 —", "5.10", CIRCUIT_TRANSFER, "kpl", 1, log,
             "G-9 — obstruction light K7 appears nowhere in the package")
    add_item(l2, "UKUPNO 5 —", "5.11", DATA_SPD, "kpl", 1, log,
             "G-6 — no signal-line SPD anywhere in the BOQ")

    # ---------------- regenerate every formula ------------------------------
    fixed = normalise_products(l1) + normalise_products(l2)
    log.append(("all product formulas", f"{fixed} stale reference(s) rewritten",
                "openpyxl does not translate formulas when rows move"))

    r1 = rs(l1, 1, "UKUPNO 1 —")
    r2 = rs(l1, 1, "UKUPNO 2 —")
    rl = rs(l1, 1, "UKUPNO LOT 1 —")
    s2 = rx(l1, 1, "2.1")
    l1.cell(r1, 6).value = f"=SUM(F12:F{r1-1})"
    l1.cell(r2, 6).value = f"=SUM(F{s2}:F{r2-1})"
    l1.cell(rl, 6).value = f"=F{r1}+F{r2}"

    ends = []
    for st, lab in (("1.1", "UKUPNO 3 —"), ("4.1", "UKUPNO 4 —"),
                    ("5.1", "UKUPNO 5 —"), ("6.1", "UKUPNO 6 —")):
        a, b = rx(l2, 1, st), rs(l2, 1, lab)
        if a and b:
            l2.cell(b, 6).value = f"=SUM(F{a}:F{b-1})"
            ends.append(b)
    r2t = rs(l2, 1, "UKUPNO LOT 2 —")
    a = rs(l2, 2, "LOT 1 — NOSAČI")
    b = rs(l2, 2, "LOT 2 — DIZEL")
    rsum = rs(l2, 1, "SVE UKUPNO (LOT 1 + LOT 2) bez PDV")
    rp = rs(l2, 1, "Popust")
    for r in (r2t, a, b, rsum, rp, rp + 1, rp + 2, rp + 3):
        free_cell(l2, r)
    l2.cell(r2t, 6).value = "=" + "+".join(f"F{e}" for e in ends)
    l2.cell(a, 6).value = f"='LOT 1'!F{rl}"
    l2.cell(b, 6).value = f"=F{r2t}"
    l2.cell(rsum, 6).value = f"=SUM(F{a}:F{b})"
    l2.cell(rp + 1, 6).value = f'=F{rsum}*(1-IF(F{rp}="",0,F{rp}/100))'
    l2.cell(rp + 2, 6).value = f"=F{rp+1}*0.17"
    l2.cell(rp + 3, 6).value = f"=F{rp+1}+F{rp+2}"

    # a priced row must never sit inside a merged range - it would hide its
    # unit, quantity and price columns (see fix_boq_all.py)
    for ws in (l1, l2):
        for r in range(1, ws.max_row + 1):
            aa = str(ws.cell(r, 1).value or "").strip()
            if not (aa and aa[0].isdigit() and "." in aa):
                continue
            for rng in list(ws.merged_cells.ranges):
                if rng.min_row <= r <= rng.max_row and rng.min_col <= 2:
                    ws.unmerge_cells(str(rng))
                    log.append((f"{ws.title} item {aa}", f"stale merge {rng} removed",
                                "insert_rows does not move merge anchors"))

    # ---------------- final integrity pass ----------------------------------
    # openpyxl's insert_rows drops the contents of the row immediately below the
    # insertion point, and does not move merge anchors - so a priced item can end
    # up blank or hidden under a total row's stale merge. Restore by item number
    # from the untouched copy, last, so nothing downstream can undo it.
    restored = []
    for sheet in ("LOT 1", "LOT 2"):
        old_ws, new_ws = src[sheet], wb[sheet]
        old_i, new_i = priced_items(old_ws), priced_items(new_ws)
        for key, nr in new_i.items():
            if key not in old_i:
                continue                        # new item, no twin to restore
            orr = old_i[key]
            for col in (2, 3, 4):
                cur = new_ws.cell(nr, col).value
                ref = old_ws.cell(orr, col).value
                if (cur is None or str(cur).strip() == "") and \
                        ref is not None and str(ref).strip() != "":
                    for rng in list(new_ws.merged_cells.ranges):
                        if (rng.min_row <= nr <= rng.max_row
                                and rng.min_col <= col <= rng.max_col):
                            new_ws.unmerge_cells(str(rng))
                    new_ws.cell(nr, col).value = ref
                    if col == 2:
                        new_ws.cell(nr, 2).alignment = Alignment(wrap_text=True,
                                                                 vertical="top")
                        restored.append(f"{sheet} {key}")
    if restored:
        log.append(("final integrity pass", ", ".join(restored) + " restored",
                    "insert_rows blanks the row below the insertion point"))

    # Shrink guard. A whole-cell write aimed at one bullet can silently swallow a
    # long specification (it happened to item 5.6, whose GRO description was
    # replaced by a single line). Anything that lost more than half its text and
    # was not deliberately rewritten is reported rather than saved quietly.
    rewritten = {"4.4"}
    for sheet in ("LOT 1", "LOT 2"):
        old_ws, new_ws = src[sheet], wb[sheet]
        old_i, new_i = priced_items(old_ws), priced_items(new_ws)
        for key, nr in new_i.items():
            if key not in old_i or key in rewritten:
                continue
            a = len(str(old_ws.cell(old_i[key], 2).value or ""))
            b = len(str(new_ws.cell(nr, 2).value or ""))
            if a > 200 and b < a * 0.5:
                raise SystemExit(
                    f"REFUSED: {sheet} item {key} description shrank {a} -> {b} "
                    f"chars. A targeted replace was probably written as a "
                    f"whole-cell assignment; nothing has been saved.")

    # the same blanking takes out the product formula, which normalise_products
    # cannot repair because it only rewrites rows that still have one
    for ws in (l1, l2):
        for key, r in priced_items(ws).items():
            if key == "1.8":                    # priced option, outside the sum
                continue
            if isinstance(ws.cell(r, 4).value, (int, float)) and \
                    ws.cell(r, 6).value in (None, ""):
                ws.cell(r, 6).value = f'=IF(AND(D{r}<>"",E{r}<>""),D{r}*E{r},"")'
                log.append((f"{ws.title} item {key}", "product formula restored",
                            "blanked together with the row's contents"))

    wb.save(XLSX)
    for what, change, why in log:
        print(f"  {what:28s} {change:52.52s} | {why}")
    print(f"\n{len(log)} changes · LOT 1 total row {rl} · LOT 2 total row {r2t}")


if __name__ == "__main__":
    sys.exit(main())
