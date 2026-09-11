# -*- coding: utf-8 -*-
"""
Rev 7 predmjer changes: new LOT split, 13,5 kVA reference set, DN 50 exhaust,
drip tray instead of a 110 % bund, 250 l first fill.

The LOT boundary moved (TD `_K`, 2026-08-11):
  LOT 1 = PV support structure only - supports, anchors, static calculation,
          bonding, LOT-1 documentation, and all of the civil works.
  LOT 2 = genset, tank, GRO, PV panel mounting, DC connections, commissioning.

So LOT 1 item 1.5 (DC cable) moves to LOT 2, and 1.6 (PVDB) is deleted outright -
`PVDB500-15-2B (01075918)` is in the Huawei quotation on file. Item 1.6a (DC SPD)
also moves rather than being deleted: whether type-2 DC protection is integrated in
the PVDB is not established by any document in the pack, and a missing SPD is the
worse error.

Row mechanics, per the traps recorded in review/:
  - `insert_rows` does NOT translate formulas, so every SUM range that spans an
    insertion point is rewritten explicitly here;
  - it also blanks the row immediately below the insertion point, so an integrity
    pass compares against an untouched copy and restores anything lost;
  - merge anchors do not move, and writing to a MergedCell is silently discarded.
"""
import os
import re
import shutil
import sys

import openpyxl
from openpyxl.styles import Alignment

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XLSX = os.path.join(BASE, "TD-OUTPUT",
                    "3.1 PRILOG II TD - predmjer Sjednica Bileca.xlsx")
NL = "\n"


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def rc(ws, col, needle):
    """Row whose cell in `col` contains `needle`."""
    for r in range(1, ws.max_row + 1):
        if needle in str(ws.cell(r, col).value or ""):
            return r
    raise SystemExit(f"{ws.title}: not found in column {col}: {needle!r}")


def wrap(ws, r):
    c = ws.cell(r, 2)
    c.alignment = Alignment(wrap_text=True, vertical="top")


def free_cell(ws, r, col=6):
    """Drop any merged range covering (r, col) - see module docstring."""
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


def sub(ws, r, old, new, log, why):
    """Substring replacement inside a description cell.

    Never a whole-cell write: item 5.6 once lost its entire GRO specification
    that way, replaced by a single bullet.
    """
    cur = str(ws.cell(r, 2).value or "")
    if old not in cur:
        if new in cur:
            return False
        raise SystemExit(f"{ws.title}!B{r}: anchor missing: {old[:70]!r}")
    ws.cell(r, 2).value = cur.replace(old, new)
    wrap(ws, r)
    log.append((f"{ws.title}!B{r}", new.strip().split(NL)[0][:60], why))
    return True


def set_sum(ws, r, rng, log, why):
    free_cell(ws, r)
    ws.cell(r, 6).value = rng
    log.append((f"{ws.title}!F{r}", rng, why))


REF = re.compile(r"(?<![A-Za-z0-9_!])([A-F])(\d+)\b")


def remap_formulas(ws, src_ws, rowmap):
    """Do what `insert_rows`/`delete_rows` should have done: move row references.

    `rowmap` maps every ORIGINAL row number to the row it now occupies, or to
    None if it was removed. Each formula is re-derived from the untouched copy,
    every reference inside it remapped, and the result written at the row the
    cell has moved to.

    Why this exists: openpyxl rewrites no formula at all when rows shift, and it
    does not complain. The first run of this script left section 6's items still
    multiplying D128..D131, `UKUPNO 6` summing a blank band, and the
    recapitulation pointing at the wrong pair of cells - the totals were simply
    wrong, which is the worst way for a priced document to fail.

    Ranges are preserved rather than re-inferred: the sheet's own numbering is
    irregular, so inferring a section's extent from item numbers collapses
    `UKUPNO 3`, which spans items numbered 1.1 and 3.2, down to a single cell.
    """
    def new(r):
        return rowmap.get(r, r)

    for row in src_ws.iter_rows(min_col=6, max_col=6):
        for c in row:
            f = c.value
            if not (isinstance(f, str) and f.startswith("=")):
                continue
            dst = new(c.row)
            if dst is None:                    # the row itself is gone
                continue
            if ws.cell(dst, 6).value == f and c.row == dst:
                continue                       # untouched row, nothing to do

            def move(m):
                tgt = new(int(m.group(2)))
                # A reference into a deleted row cannot be silently kept - it
                # would point at whatever slid into its place.
                if tgt is None:
                    raise SystemExit(
                        f"{ws.title}!F{c.row}: {f} references row "
                        f"{m.group(2)}, which was deleted")
                return f"{m.group(1)}{tgt}"

            free_cell(ws, dst)
            ws.cell(dst, 6).value = REF.sub(move, f)


def translate_formulas(ws, src_ws, inserted_at, count):
    """`count` rows inserted immediately before original row `inserted_at`."""
    remap_formulas(ws, src_ws, {r: (r + count if r >= inserted_at else r)
                                for r in range(1, src_ws.max_row + 1)})


def assert_no_loss(wb, src, deliberate=(), floor=0.5, priced_only=True):
    """Fail loudly if any priced item lost its text, its formula, or its row.

    The earlier version of this check only restored descriptions that came out
    *empty*, and it silently missed item 6.4 losing all 167 characters of its
    text on the very run it was written to police - the loss was found days
    later by diffing against git. So it now checks three things and raises
    instead of repairing:

      - every item present before is still present;
      - no description shrank below `floor` of its original length, unless the
        item number is listed in `deliberate` (compaction is intentional there);
      - every priced row's formula addresses ITS OWN row.

    Repairing quietly was the mistake: a description that vanished is a tender
    requirement that vanished, and it should stop the run, not be patched over.
    """
    bad = []
    for name in ("LOT 1", "LOT 2"):
        old, new = priced_items(src[name]), priced_items(wb[name])
        ws = wb[name]
        for key, orow in old.items():
            if key in deliberate:
                continue
            nrow = new.get(key)
            if nrow is None:
                bad.append(f"{name} {key}: item disappeared")
                continue
            o = str(src[name].cell(orow, 2).value or "").strip()
            n = str(ws.cell(nrow, 2).value or "").strip()
            if o and not n:
                bad.append(f"{name} {key} (row {nrow}): description emptied")
            elif o and len(n) < floor * len(o):
                bad.append(f"{name} {key} (row {nrow}): description shrank "
                           f"{len(o)} -> {len(n)} chars")
        if priced_only:
            for key, r in new.items():
                f = str(ws.cell(r, 6).value or "")
                if f and f"D{r}<>" not in f:
                    bad.append(f"{name} {key} (row {r}): formula {f[:40]!r} "
                               f"does not address its own row")
    if bad:
        raise SystemExit("integrity check failed:\n  " + "\n  ".join(bad))


def extend_section_sums(ws):
    """Grow each `UKUPNO n` range to cover items appended at its end.

    Rows inserted immediately above the total row fall *outside* the existing
    SUM - Excel only auto-extends a range when the insertion is inside it - so
    5.12/5.13/5.14 would be priced and then not counted. The end of the range is
    pushed down to the last priced item above the total; it is never pulled up,
    so ranges that already run over blank rows keep doing so.
    """
    items = priced_items(ws)
    for r in range(1, ws.max_row + 1):
        a = str(ws.cell(r, 1).value or "").strip()
        f = str(ws.cell(r, 6).value or "")
        m = re.fullmatch(r"=SUM\(F(\d+):F(\d+)\)", f)
        if not (a.startswith("UKUPNO ") and m):
            continue
        last = max((x for x in items.values() if int(m.group(1)) <= x < r),
                   default=int(m.group(2)))
        end = max(int(m.group(2)), last)
        if end != int(m.group(2)):
            free_cell(ws, r)
            ws.cell(r, 6).value = f"=SUM(F{m.group(1)}:F{end})"


# --------------------------------------------------------------------------
def lot1(ws, log):
    """Repack section 1: 1.5/1.6/1.6a leave, the documentation item becomes 1.5.

    Done by rewriting rows rather than deleting them - `delete_rows` has the same
    formula and merge hazards as `insert_rows`, and the section total
    SUM(F12:F37) stays valid over the blanked tail.
    """
    r15 = rc(ws, 1, "1.5")
    r16 = rc(ws, 1, "1.6")
    r16a = rc(ws, 1, "1.6a")
    r17 = rc(ws, 1, "1.7")
    if not (r15 < r16 < r16a < r17):
        raise SystemExit("LOT 1: unexpected item order")

    moved = {c: ws.cell(r17, c).value for c in range(1, 7)}
    dc_cable = str(ws.cell(r15, 2).value or "")
    spd_dc = str(ws.cell(r16a, 2).value or "")
    spd_qty = ws.cell(r16a, 4).value

    # documentation item slides up into the first vacated row and is renumbered
    for c in range(1, 7):
        free_cell(ws, r15, c)
        ws.cell(r15, c).value = moved[c]
    ws.cell(r15, 1).value = "1.5"
    ws.cell(r15, 6).value = f'=IF(AND(D{r15}<>"",E{r15}<>""),D{r15}*E{r15},"")'
    wrap(ws, r15)

    for r in (r16, r16a, r17):
        for c in range(1, 7):
            free_cell(ws, r, c)
            ws.cell(r, c).value = None

    log.append(("LOT 1", "1.7 -> 1.5 (documentation), rows 1.5/1.6/1.6a cleared",
                "DC cable and DC SPD move to LOT 2; PVDB is in the Huawei package"))
    return dc_cable, spd_dc, spd_qty


def add_item(ws, before_label, number, desc, unit, qty, log, why):
    """Insert a priced row immediately above the row carrying `before_label`."""
    r = rc(ws, 1, before_label)
    ws.insert_rows(r)
    for c in range(1, 7):
        ws.cell(r, c)._style = ws.cell(r - 1, c)._style
        free_cell(ws, r, c)
    ws.cell(r, 1).value = number
    ws.cell(r, 2).value = desc
    ws.cell(r, 3).value = unit
    ws.cell(r, 4).value = qty
    ws.cell(r, 6).value = f'=IF(AND(D{r}<>"",E{r}<>""),D{r}*E{r},"")'
    wrap(ws, r)
    log.append((f"{ws.title} new {number}", desc.split(NL)[0][:60], why))
    return r


PV_MOUNT = (
    "Montaža fotonaponskih panela na nosive konstrukcije iz LOT 1 i njihovo DC "
    "povezivanje u stringove, sa svim pripadajućim priborom za pričvršćenje, "
    "vođenjem i označavanjem kablova." + NL +
    " - 12 modula 585 Wp na 3 nosača (po 4 modula), spoj u 2 stringa × 6 modula" + NL +
    " - DC veze: string 1 → PVDB → iSSU 1;  string 2 → PVDB → iSSU 2" + NL +
    " - GRO, sekcija SOLAR → Huawei iSSU" + NL +
    "NAPOMENA: fotonaponske panele, PVDB i ostalu opremu hibridnog sistema "
    "obezbjeđuje Kupac (posebna nabavka). Ponuđač izvodi montažu, povezivanje, "
    "označavanje i ispitivanje.")


def main():
    if not os.path.exists(XLSX):
        raise SystemExit(f"missing: {XLSX}")
    bak = XLSX + ".bak"
    shutil.copy2(XLSX, bak)
    wb = openpyxl.load_workbook(XLSX)
    src = openpyxl.load_workbook(XLSX)            # untouched reference
    l1, l2 = wb["LOT 1"], wb["LOT 2"]
    log = []

    # ---- LOT 1: repack ---------------------------------------------------
    dc_cable, spd_dc, spd_qty = lot1(l1, log)

    # ---- LOT 2: the moved electrical, then the new PV mounting item ------
    u5 = "UKUPNO 5 —"
    anchor = rc(l2, 1, u5)          # original row of the insertion point
    add_item(l2, u5, "5.12", dc_cable, "m", 100, log,
             "moved from LOT 1 1.5 - Huawei supplies only 2 x 7 m of module extension")
    add_item(l2, u5, "5.13", spd_dc, "kpl", spd_qty, log,
             "moved from LOT 1 1.6a - kept priced until PVDB integration is proven")
    add_item(l2, u5, "5.14", PV_MOUNT, "kpl", 1, log,
             "new LOT 2 scope per TD _K: PV mounting, DC connections, GRO-SOLAR -> iSSU")

    # ---- LOT 2: 18 kVA reference set -------------------------------------
    # The P18-6 keeps the P22-6's Perkins 404D-22G1 (2,2 l, 4-cyl) and its
    # 1980 m3/h cooling pack, so the engine bullets B20/B27 need no change at all
    # apart from a gender slip; only the ratings, the current and the mass move.
    sub(l2, rc(l2, 2, "snaga 22 kVA"),
        "snaga 22 kVA / 17,6 kW (±5%)", "snaga 18 kVA / 14,4 kW (±5%)",
        log, "Investor's reference rating, 2026-08-12")
    sub(l2, rc(l2, 2, "kao FG Wilson P22-6"),
        "kao FG Wilson P22-6 ili ekvivalent",
        "kao FG Wilson P18-6 (Skid) ili ekvivalent", log, "reference set")
    sub(l2, rc(l2, 2, "radni zapremina cca 2,2 l"),
        "radni zapremina cca 2,2 l", "radna zapremina cca 2,2 l", log,
        "gender agreement; the displacement is unchanged on the P18-6")
    sub(l2, rc(l2, 2, "nazivna snaga 22 kVA uz cos"),
        "nazivna snaga 22 kVA", "nazivna snaga 18 kVA", log, "alternator rating")

    # In = 18000 / (sqrt(3) x 400) = 26,0 A, so 3 x In = 78 A and 0,5 x In = 13 A
    r32 = rc(l2, 2, "POBUDA (OBAVEZNO)")
    sub(l2, r32, "(≈95 A pri 22 kVA / 400 V)", "(≈78 A pri 18 kVA / 400 V)", log,
        "In falls from 31,75 A to 26,0 A at 18 kVA")
    sub(l2, r32, "≈0,5 × In (16 A)", "≈0,5 × In (13 A)", log, "same")
    sub(l2, r32,
        "Ponuđač dostavlja podatak o trajnoj struji kratkog spoja iz tehničkog "
        "lista proizvođača.",
        "Ponuđač dostavlja podatak o trajnoj struji kratkog spoja iz tehničkog "
        "lista proizvođača. NAPOMENA: tehnički list referentnog agregata "
        "FG Wilson P18-6 navodi Short Circuit Capacity 0 % u standardnoj SHUNT "
        "izvedbi, a traženu trajnu struju kvara daje tek opciona PMG/AUX pobuda "
        "— zahtjev za nezavisnom pobudom je time potvrđen tehničkim listom.",
        log, "P18-6 TDS p.4 states 0 % short-circuit capacity without PMG/AUX")

    # The set is derated by 12,5 % at 1076 m / 40 C, which takes the PRIME rating
    # to 11,6 kW - below the 12,5 kW the rectifiers can draw. The input limit was
    # already required here, but only qualitatively; it now carries a number.
    sub(l2, rc(l2, 2, "ulazna snaga ispravljača mora biti ograničena"),
        "(3 × R4875G5 = 12 kW); ponuđač dokazuje usklađenost proračunom",
        "(3 × R4875G5 = 12 kW, tj. cca 12,5 kW na AC strani). OGRANIČENJE SE "
        "ZADAJE BROJČANO: ulazna snaga ispravljačkog sistema ograničava se na "
        "maks. 9,5 kW dok radi DEA. OBRAZLOŽENJE: agregat 18 kVA / 14,4 kW "
        "(standby) odnosno 16,5 kVA / 13,2 kW (prime) derativa se na lokaciji "
        "1076 m n.v. i 40 °C prema ISO 3046 / ISO 8528-1 za cca 12,5 % — na "
        "12,6 kW standby i 11,6 kW prime. Kako lokacija NIJE na mreži i agregat "
        "radi ciklično po SoC baterija, mjerodavan je PRIME režim, pa "
        "neograničeno opterećenje od 12,5 kW premašuje raspoloživu snagu. "
        "Zadana granica od 9,5 kW iznosi cca 82 % derativane prime snage, "
        "ostavlja cca 8,2 kW za punjenje baterija iznad TK potrošnje od 1,33 kW "
        "i istovremeno drži agregat iznad minimalnog opterećenja od 30 % "
        "(sprječavanje mokrog rada motora). Ponuđač dokazuje usklađenost "
        "proračunom deratinga za lokaciju",
        log, "derated prime 11,6 kW < 12,5 kW draw - the cap must be numeric")

    # ---- LOT 2: floor loading at the new wet mass -------------------------
    sub(l2, rc(l2, 2, "NOSIVOST PODA KONTEJNERA"),
        "Agregat (385 kg mokro na 0,96 m² = 3,93 kN/m²)",
        "Agregat (372 kg mokro na 0,96 m² = 3,80 kN/m²)", log,
        "P18-6 wet mass 372 kg")

    # ---- LOT 2: exhaust stays NO 50 --------------------------------------
    r411 = rc(l2, 2, "IZMJENA — PREČNIK I TRASA")
    cur = str(l2.cell(r411, 2).value)
    head, _, tail = cur.partition("IZMJENA — PREČNIK I TRASA:")
    keep = tail.split(".", 1)[1] if "." in tail else ""
    l2.cell(r411, 2).value = head + (
        "TRASA: fleksibilni spoj i prigušivač neposredno iza motora, uspon uz "
        "ZAPADNI zid kontejnera, završetak IZNAD KROVA usmjeren naviše, sa "
        "hvatačem iskri." + NL +
        "NO 50 je ZADRŽAN: sa agregatom 18 kVA protok izduvnih gasova je "
        "192 m³/h pri 413 °C, brzina 27,2 m/s (ispod uobičajenih 30 m/s), "
        "protutlak ≈1,9 kPa uz dozvoljenih 10,2 kPa. Raniji zahtjev za DN 65 "
        "vrijedio je za agregat 22 kVA (234 m³/h pri 505 °C = 33 m/s) i "
        "POVLAČI SE.")
    wrap(l2, r411)
    log.append((f"LOT 2!B{r411}", "DN 65 withdrawn, NO 50 retained",
                "P18-6 exhaust flow 192 m3/h at 413 C -> 27,2 m/s"))

    # ---- LOT 2: drip tray, not a 110 % bund ------------------------------
    r43 = rc(l2, 2, "prihvatnog korita (tankvane)")
    l2.cell(r43, 2).value = (
        "Izrada i montaža prihvatnog KORITA (kade) ispod spremnika goriva, "
        "referentnih dimenzija 1150 × 640 mm sa visinom ruba 200 mm, od čeličnog "
        "lima sa zaštitom otpornom na dizel gorivo, sa vidljivim najnižim mjestom "
        "za kontrolu i pražnjenje." + NL +
        "NAPOMENA — SEKUNDARNA ZAŠTITA: spremnik je DVOPLAŠNI sa sondom za "
        "detekciju curenja u međuplaštu (Tačka 4.2), pa međuplašt predstavlja "
        "sekundarnu zaštitu i tankvana zapremine 110 % NIJE zahtijevana. Korito "
        "služi za prihvat kapanja i prosipanja pri punjenju i pretakanju." + NL +
        "Korito se postavlja uz JUŽNI zid, JUŽNO od ulaznih vrata, prema crtežu "
        "M-01, tako da ostanu slobodni ulaz i put unosa agregata.")
    wrap(l2, r43)
    log.append((f"LOT 2!B{r43}", "110 % bund -> drip tray under a double-skinned tank",
                "Investor 2026-08-11; a bund gains no capacity from height"))

    sub(l2, rc(l2, 2, "u tankvani iz Tačke 4.3"),
        "smještaj uz JUŽNI zid kontejnera u tankvani iz Tačke 4.3",
        "smještaj u JUGOISTOČNI ugao kontejnera, u koritu iz Tačke 4.3", log,
        "tank moved out of the way of the genset")

    # ---- LOT 2: first fill 250 l ----------------------------------------
    r416 = rc(l2, 2, "Prvo punjenje spremnika")
    l2.cell(r416, 4).value = 250
    sub(l2, r416, "Obračun po stvarno isporučenoj količini.",
        "Obračun po stvarno isporučenoj količini. Prvo punjenje je 250 l "
        "(spremnik 500 l se ne puni do vrha pri primopredaji).", log,
        "TD _K: tankanje 250 l")
    log.append((f"LOT 2!D{r416}", "500 -> 250 l", "TD _K"))

    # ---- LOT 2: the closing notes ---------------------------------------
    r147 = rc(l2, 1, "Procijenjena vrijednost nabavke")
    cur = str(l2.cell(r147, 1).value)
    l2.cell(r147, 1).value = cur.replace(
        "LOT 2 = 35.000,00 KM, UKUPNO 50.000,00 KM",
        "LOT 2 = 34.000,00 KM, UKUPNO 49.000,00 KM")
    log.append((f"LOT 2!A{r147}", "LOT 2 35.000 -> 34.000, total 49.000 KM",
                "LOT 2 loses the PVDB, gains the PV mounting and DC work"))

    # Fuel: read off the P18-6 TDS instead of scaled from the 22 kVA set.
    # 3,7 l/h at 75 % standby x 250 h = 925 l/yr; 500 l = 135 h at 75 % load.
    r151 = rc(l2, 1, "Orijentaciona potrošnja goriva")
    l2.cell(r151, 1).value = (
        "- Orijentaciona potrošnja goriva agregata 18 kVA pri opterećenju od "
        "75 % iznosi 3,7 l/h prema tehničkom listu referentnog agregata "
        "FG Wilson P18-6 (50 Hz standby). Pri projektovanom godišnjem radu do "
        "250 h (standby režim prema ISO 8528) to iznosi cca 925 l godišnje, "
        "odnosno spremnik od 500 l obezbjeđuje cca 135 h rada, tj. autonomiju "
        "od cca 6–7 mjeseci između dopunjavanja. Ponuđač je dužan dostaviti "
        "stvarne podatke o potrošnji za ponuđeni tip DEA.")
    log.append((f"LOT 2!A{r151}", "fuel note recomputed from the P18-6 TDS",
                "3,2 l/h was scaled from the 22 kVA set, not measured"))

    # ---- repair what insert_rows did not translate ------------------------
    translate_formulas(l2, src["LOT 2"], anchor, 3)
    extend_section_sums(l2)
    log.append(("formulas", f"rows >= {anchor} shifted by 3; UKUPNO 5 extended",
                "insert_rows translates nothing below the insertion point"))

    # ---- integrity pass --------------------------------------------------
    lost = []
    for name in ("LOT 1", "LOT 2"):
        old_i, new_i = priced_items(src[name]), priced_items(wb[name])
        for key, orow in old_i.items():
            if key in ("1.5", "1.6", "1.6a", "1.7") and name == "LOT 1":
                continue
            nrow = new_i.get(key)
            if nrow is None:
                lost.append(f"{name} {key} vanished")
                continue
            o = str(src[name].cell(orow, 2).value or "")
            n = str(wb[name].cell(nrow, 2).value or "")
            if not n:
                wb[name].cell(nrow, 2).value = o
                wrap(wb[name], nrow)
                lost.append(f"{name} {key} description restored")
            elif len(n) < 0.5 * len(o):
                raise SystemExit(
                    f"{name} {key}: description shrank {len(o)} -> {len(n)} chars")
    if lost:
        log.append(("integrity pass", "; ".join(lost),
                    "insert_rows blanks the row below the insertion point"))

    # Nothing above may pass silently: assert that every priced item still has a
    # description and a formula addressing its own row.
    # LOT 2 item 4.19 carries a number and no text in the inherited file; that is
    # a defect in the source, not a regression, so the check is comparative.
    bad = []
    for name in ("LOT 1", "LOT 2"):
        ws, was = wb[name], priced_items(src[name])
        for key, r in priced_items(ws).items():
            had = str(src[name].cell(was[key], 2).value or "").strip() if key in was else ""
            if had and not str(ws.cell(r, 2).value or "").strip():
                bad.append(f"{name} {key} (row {r}) lost its description")
            f = str(ws.cell(r, 6).value or "")
            if f"D{r}<>" not in f:
                bad.append(f"{name} {key} (row {r}) formula addresses {f[:40]!r}")
    if bad:
        raise SystemExit("integrity check failed:\n  " + "\n  ".join(bad))

    wb.save(XLSX)
    os.remove(bak)
    for where, what, why in log:
        print(f"  {where:<24} {what}")
        print(f"  {'':<24}   -> {why}")
    print(f"\n{len(log)} change(s) written to {os.path.basename(XLSX)}")


if __name__ == "__main__":
    main()
