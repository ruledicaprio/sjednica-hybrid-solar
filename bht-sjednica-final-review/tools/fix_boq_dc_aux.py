# -*- coding: utf-8 -*-
"""2026-09-11 — trajni potrošači na −48 V DC (odluka Naručioca, obje lokacije).

Lokacije nemaju priključak na mrežu: novi GRO ima napon samo dok agregat radi. Trajni
potrošači — svjetiljka za obilježavanje stuba, vatrodojavna centrala, punjač akumulatora
za start agregata, ventilator prostora i jedna svjetiljka kontejnera — zato se napajaju
iz Huawei sistema −48 V DC, a ne iz GRO. Zajednički predmjer (rfp-hybrid-solar-td,
joint_boq.py) kopira ovaj list, pa izmjene važe i za Hamziće.

  D1  LOT 2 · 5.16 / 5.17 / 5.18  nove stavke iza posljednje stavke sekcije 5: DC razvod
      −48 V, svjetiljka stuba 48 V DC, DC/DC pretvarači. Broj 5.15 je namjerno slobodan:
      u zajedničkom predmjeru to je demontaža klima-uređaja Stulz na Hamzićima, pa ove tri
      stavke nose isti broj na obje lokacije. UKUPNO 5 i UKUPNO LOT 2 ih obuhvataju, a
      REKAPITULACIJA ispod prati pomjerene redove.
  D2  LOT 2 · 4.8   ventilator prostora postaje EC 48 V DC iz DC razvoda; radi po
      termostatu dok agregat miruje, a kontroler agregata ga gasi dok agregat radi.
  D3  LOT 2 · 5.10  signalna rasvjeta stuba (K7) ne prevezuje se na novi GRO nego na DC
      razvod (5.16), svjetiljka prema 5.17.
  D4  LOT 2 · 3.1   punjač start baterije napaja se iz DC razvoda preko DC/DC pretvarača
      (5.18), ne sa 230 V — AC napon postoji samo dok agregat radi.
  D5  LOT 2 · 5.6   položaji sklopke izvora 1-0-2 prema Prilogu I, Tačka 4.5 (koji je po
      redoslijedu mjerodavnosti iznad predmjera): 1-„agregat", 0-„isključeno", 2-„rezerva".
  D6  LOT 2 · 3.1   grijač rashladne tečnosti 230 V -> DC predgrijač iz DC razvoda (5.16),
      samo kratko predgrijavanje prije pokretanja, nikad trajno (Prilog I, Tačka 4.1).
  D7  LOT 2 · 4.13  bez grijača prostora (odluka Naručioca); stavka ostaje za termoizolaciju
      cjevovoda goriva i zaštitu spremnika, samo tekst grijača se briše.
  D8  LOT 2 · 5.16  predgrijač rashladne tečnosti agregata je izvod DC razvoda.
  D9  LOT 2 · 3.1   KOA: umjesto kruga grijača motora, izlaz kontrolera (relej) za DC
      predgrijač; komutacija između agregata (1) i rezervnog izvora (2).
  D10 LOT 2 · 4.13  bez grijanja spremnika (van mreže radi samo dok agregat radi); ostaje
      termoizolacija cjevovoda goriva, dodato zimsko gorivo za prvo punjenje (4.15).
  D11 LOT 2 · 4.14  termojavljač snižene temperature: podesivi prag, zadano −10 °C.
  T1  LOT 2 · 4.5   „izlazne žaluzine iz Tačke 4.7" -> 4.6 (4.7 je usisna žaluzina).
  T2  LOT 2 · 4.2 i OPŠTE NAPOMENE UZ TAČKU 4   roštilj „iz Tačke 4.4" -> 4.3 (4.4 je
      fleksibilni spoj hladnjaka, roštilj je 4.3).
  T1/T2 su iste zamjene kao BOTH_SITES_EDITS u joint_boq.py (preuzete odande), pa
  zajednički predmjer ostaje ispravan i sa i bez njih u izvorniku.

Idempotentno: drugi prolaz ništa ne mijenja i ne snima fajl. Obrazac kao
fix_boq_quantities.py (assert_no_loss, COVERAGE); umetanje redova i pomjeranje formula su
iz rfp-hybrid-solar-td/tools/joint_boq.py. Zaglavlje stranice, svojstva dokumenta i
postavke štampe provjeravaju se poslije snimanja; redovi koji su u izvorniku imali
automatsku visinu ostaju automatski (openpyxl bi ih inače zamrznuo na staroj visini i
odsjekao tekst). Rezervna kopija ide u privremeni folder, ne u TD-OUTPUT —
check_consistency.py čita svaki .xlsx iz TD-OUTPUT.

    python fix_boq_dc_aux.py
"""
import copy
import html
import os
import re
import shutil
import sys
import tempfile
import zipfile

import openpyxl
from openpyxl.xml.functions import tostring

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
ROOT = os.path.dirname(BASE)
XLSX = os.path.join(BASE, "TD-OUTPUT", "3.1 PRILOG II TD - predmjer Sjednica Bileca.xlsx")

# joint_boq.py imports its own `paths`, and this folder has a `paths` too: import it,
# then free the module name so nothing here picks up the joint one.
JOINT_TOOLS = os.path.join(ROOT, "rfp-hybrid-solar-td", "tools")
sys.path.insert(0, JOINT_TOOLS)
import joint_boq as jb  # noqa: E402
sys.path[:] = [p for p in sys.path
               if os.path.normcase(os.path.abspath(p)) != os.path.normcase(JOINT_TOOLS)]
sys.modules.pop("paths", None)
sys.path.insert(0, HERE)
from compact_boq import COVERAGE  # noqa: E402
from fix_boq_lots import assert_no_loss  # noqa: E402

SHEET = "LOT 2"

# D1 — (stavka, jedinica, količina, opis), iza posljednje stavke sekcije 5
NEW_DC_ITEMS = [
    ("5.16", "kpl", 1,
     "DC razvod −48 V za trajne potrošače: isporuka, montaža i povezivanje ormarića u "
     "kontejneru, napojenog sa slobodnog DC izvoda ormara Huawei ICC360-HA1-C1 (vlastiti "
     "zaštitni prekidač), kablom 2 × 6 mm² kroz zid kontejnera. DC prekidači za izvode: "
     "svjetiljka za obilježavanje stuba (Tačka 5.17), vatrodojavna centrala i punjač "
     "akumulatora za start agregata (preko DC/DC pretvarača iz Tačke 5.18), ventilator "
     "prostora (Tačka 4.8) i rasvjeta kontejnera. Uključena jedna LED svjetiljka 48 V DC, "
     "IP65, sa prekidačem uz ulazna vrata — svjetlo i kad agregat ne radi. Signalizacija "
     "ispada prema SMU. Dozvoljena potrošnja trajnih potrošača: Prilog I, Tačka 4.5."),
    ("5.17", "kpl", 1,
     "Svjetiljka za obilježavanje antenskog stuba 48 V DC: zamjena postojeće svjetiljke LED "
     "svjetiljkom za 48 V DC niskog intenziteta, sa foto-senzorom i nadzorom ispada; kabl od "
     "DC razvoda iz Tačke 5.16 do svjetiljke po postojećoj trasi uz stub; uključen rad na "
     "visini. Alternativa: postojeća svjetiljka ostaje i napaja se preko DC/AC pretvarača "
     "≤100 W; Ponuđač bira rješenje. Dozvoljena potrošnja: Prilog I, Tačka 4.5."),
    ("5.18", "kpl", 1,
     "DC/DC pretvarači za trajne potrošače, napojeni iz DC razvoda iz Tačke 5.16: 48 V → "
     "nazivni napon vatrodojavne centrale (centrala zadržava vlastite akumulatore prema "
     "EN 54-4) i punjač akumulatora za start agregata (48 V → 12/24 V prema agregatu), sa "
     "strujnim ograničenjem, zaštitom i signalizacijom."),
]

# D2-D4 i T1/T2 — tačne zamjene; svaka stara mora biti tačno jednom (ili već zamijenjena)
EDITS = {
    "4.8": [  # D2
        ("aksijalnog ventilatora za prinudnu ventilaciju prostora agregata, kapaciteta "
         "1200 m³/h, Ø315 mm, sa termostatskim upravljanjem. Ventilator spojiti sa komandnim "
         "ormarom agregata tako da se prilikom uključenja agregata vrši i direktno uključenje "
         "ventilatora.",
         "aksijalnog EC ventilatora 48 V DC za prinudnu ventilaciju prostora agregata, "
         "kapaciteta 1200 m³/h, Ø315 mm, napajanog iz DC razvoda −48 V (Tačka 5.16), sa "
         "termostatskim upravljanjem. Ventilator radi prema termostatu dok agregat miruje; za "
         "vrijeme rada agregata kontroler agregata ga isključuje."),
    ],
    "5.10": [  # D3
        ("SIGNALNA RASVJETA antenskog stuba h=38 m (krug K7) izvodi se kao ZASEBAN NADZIRANI "
         "strujni krug, sa nadzorom prisustva napona i strujnim nadzorom ispravnosti "
         "svjetiljke, i dojavom ispada u sistem daljinskog nadzora",
         "SIGNALNA RASVJETA antenskog stuba h=38 m (krug K7) NE prevezuje se na novi GRO: "
         "priključuje se na DC razvod −48 V iz Tačke 5.16, svjetiljka prema Tački 5.17, sa "
         "nadzorom ispada i dojavom u sistem daljinskog nadzora"),
    ],
    "3.1": [
        ("punjač start baterije 12 V / 5 A / 230 V, programabilni",                  # D4
         "punjač start baterije 12 V / 5 A, napajan iz DC razvoda −48 V preko DC/DC pretvarača "
         "iz Tačke 5.18 (ne sa 230 V — AC napon postoji samo dok agregat radi), programabilni"),
        ("GRIJAČ RASHLADNE TEČNOSTI 230 V sa podesivim termostatom (obavezno — zimski rad)",  # D6
         "PREDGRIJAČ RASHLADNE TEČNOSTI na DC napajanje — direktno 48 V ili preko DC/DC "
         "pretvarača odgovarajuće snage, iz DC razvoda −48 V (Tačka 5.16); uključuje ga "
         "kontroler agregata samo za kratko predgrijavanje prije pokretanja, pri niskoj "
         "temperaturi, i nikada ne radi trajno (obavezno — zimski rad; Prilog I, Tačka 4.1)"),
        ("neovisan strujni krug za grijač motora",                                    # D9
         "izlaz kontrolera (relej) za uključivanje DC predgrijača rashladne tečnosti "
         "(napajanje iz DC razvoda, Tačka 5.16) prije svakog pokretanja"),
        ("komutacija se izvodi između hibridnog sistema napajanja i agregata.",       # D9
         "komutacija se izvodi između agregata (položaj 1) i rezervnog izvora (položaj 2, npr. "
         "mobilni agregat)."),
    ],
    "5.6": [  # D5 — Prilog I §4.5 je mjerodavan
        ('položaje obilježiti: 1-„hibridni sistem", 0-„isključeno", 2-„agregat"',
         'položaje obilježiti: 1-„agregat", 0-„isključeno", 2-„rezerva"'),
    ],
    "4.13": [  # D7 — samo grijač prostora; ostatak stavke ostaje
        ("opreme za zimski rad: grijač prostora agregata sa termostatom, termoizolacija",
         "opreme za zimski rad: termoizolacija"),
        ("termoizolacija cjevovoda goriva i grijanje/zaštita spremnika od hladnog starta, "  # D10
         "komplet sa napajanjem i upravljanjem iz KOA.",
         "termoizolacija cjevovoda goriva; prvo punjenje (Tačka 4.15) zimskim dizel gorivom prema "
         "EN 590, klase prema najnižoj temperaturi lokacije."),
    ],
    "4.14": [  # D11
        ("i snižene temperature (t<10 °C)",
         "i snižene temperature (podesivi prag, zadano −10 °C — upozorenje na rizik hladnog "
         "starta i goriva)"),
    ],
    "5.16": [  # D8 — stavka iz D1; zamjena važi i za prvi i za ponovljeni prolaz
        ("ventilator prostora (Tačka 4.8) i rasvjeta kontejnera.",
         "ventilator prostora (Tačka 4.8), predgrijač rashladne tečnosti agregata (Tačka 3.1) i "
         "rasvjeta kontejnera."),
    ],
    **jb.BOTH_SITES_EDITS[SHEET],       # T1 (4.5) i T2 (4.2)
}
NOTE_EDITS = jb.BOTH_SITES_NOTE_EDITS[SHEET]        # T2 (OPŠTE NAPOMENE UZ TAČKU 4)

DC_COVERAGE = ["−48 V", "ICC360-HA1-C1", "2 × 6 mm²", "48 V DC", "EC ventilator", "EN 54-4",
               "DC/DC", "foto-senzor", "Prilog I, Tačka 4.5", "prekidačem uz ulazna vrata",
               "K7", "rasvjeta prepreke", "PREDGRIJAČ RASHLADNE TEČNOSTI",
               "predgrijač rashladne tečnosti agregata", "Prilog I, Tačka 4.1",
               '1-„agregat", 0-„isključeno", 2-„rezerva"', "izlaz kontrolera (relej)",
               "položaj 2, npr. mobilni agregat", "zimskim dizel gorivom prema EN 590",
               "zadano −10 °C"]


# --------------------------------------------------------------------------
def xml_rows(path):
    """{list: {red: (ht, customHeight)}} direktno iz XML-a paketa."""
    out = {}
    with zipfile.ZipFile(path) as z:
        wbx = z.read("xl/workbook.xml").decode("utf-8")
        rels = z.read("xl/_rels/workbook.xml.rels").decode("utf-8")
        target = {}
        for m in re.finditer(r"<Relationship\b([^>]*)>", rels):
            a = dict(re.findall(r'(\w+)="([^"]*)"', m.group(1)))
            target[a.get("Id")] = a.get("Target", "")
        for m in re.finditer(r"<sheet\b([^>]*)>", wbx):
            a = dict(re.findall(r'([\w:]+)="([^"]*)"', m.group(1)))
            t = target[a["r:id"]]
            part = t.lstrip("/") if t.startswith("/") else "xl/" + t
            rows = {}
            for rm in re.finditer(r"<row\b([^>]*)>", z.read(part).decode("utf-8")):
                ra = dict(re.findall(r'(\w+)="([^"]*)"', rm.group(1)))
                rows[int(ra["r"])] = (ra.get("ht"), ra.get("customHeight") in ("1", "true"))
            out[html.unescape(a["name"])] = rows
    return out


def props(wb):
    """Ono što snimanje mora sačuvati: zaglavlje, postavke štampe, svojstva dokumenta."""
    snap = {}
    for ws in wb.worksheets:
        pr = ws.sheet_properties.pageSetUpPr
        snap[ws.title] = (tostring(ws.HeaderFooter.to_tree()), tostring(ws.page_setup.to_tree()),
                          tostring(ws.print_options.to_tree()), tostring(ws.page_margins.to_tree()),
                          pr.fitToPage if pr is not None else None, ws.print_area,
                          ws.print_title_rows, ws.print_title_cols,
                          {k: v.width for k, v in ws.column_dimensions.items()})
    snap["custom properties"] = [(p.name, str(p.value)) for p in wb.custom_doc_props.props]
    c = wb.properties
    snap["core properties"] = (c.creator, c.title, c.subject, c.description, c.keywords,
                               c.category)
    return snap


def shifted(r, inserted):
    return r + inserted[1] if inserted and r >= inserted[0] else r


# --------------------------------------------------------------------------
def insert_dc_items(ws, log):
    """D1. Vraća (red umetanja, broj redova), ili None ako stavke već postoje."""
    items = jb.structure(ws)["items"]
    have = [n for n, *_ in NEW_DC_ITEMS if n in items]
    if have:
        if len(have) != len(NEW_DC_ITEMS):
            raise SystemExit(f"{SHEET}: postoji samo dio novih stavki ({have}) — provjeriti ručno")
        for n, unit, qty, text in NEW_DC_ITEMS:
            r = items[n]
            final = jb.fix_text(text, EDITS.get(n, []), n, idempotent=True)[0]   # poslije D8
            if ((ws.cell(r, 3).value, ws.cell(r, 4).value) != (unit, qty)
                    or ws.cell(r, 2).value not in (text, final)):
                raise SystemExit(f"{SHEET} {n}: postoji, ali se razlikuje od ove skripte")
        return None
    sec = NEW_DC_ITEMS[0][0].split(".")[0]
    anchor = [n for n in items if n.split(".")[0] == sec][-1]
    prev = anchor
    for n, *_ in NEW_DC_ITEMS:                 # brojevi kao cijeli brojevi: 5.1 nije 5.16
        if n.split(".")[0] != sec or jb.minor(n) <= jb.minor(prev):
            raise SystemExit(f"{SHEET}: {n} ne može iza {prev}")
        prev = n
    at, srow = items[anchor] + 1, items[anchor]
    for k, (n, unit, qty, text) in enumerate(NEW_DC_ITEMS):
        r = at + k
        jb.insert_row(ws, r, cross_sheet=True)          # 'LOT 1'!F29 u rekapitulaciji ostaje
        for col in range(1, 7):
            ws.cell(r, col)._style = copy.copy(ws.cell(srow, col)._style)
        ws.cell(r, 1).value, ws.cell(r, 2).value = n, text
        ws.cell(r, 3).value, ws.cell(r, 4).value = unit, qty
        ws.cell(r, 6).value = jb.line_formula(r)
        log.append(f"D1  {n}: novi red {r} ({unit} × {qty})")
    s = jb.structure(ws)
    r0, _, rsub = s["sections"][sec]
    old = ws.cell(rsub, 6).value
    ws.cell(rsub, 6).value = f"=SUM(F{r0}:F{rsub - 1})"
    lot = "=" + "+".join(f"F{v[2]}" for v in sorted(s["sections"].values(), key=lambda v: v[2]))
    old_lot = ws.cell(s["lot_row"], 6).value
    ws.cell(s["lot_row"], 6).value = lot
    log.append(f"D1  UKUPNO {sec}: F{rsub} {old} -> {ws.cell(rsub, 6).value}; "
               f"UKUPNO LOT 2: F{s['lot_row']} {old_lot} -> {lot}")
    return at, len(NEW_DC_ITEMS)


def edit_texts(ws, log):
    """D2-D4, T1, T2 — idempotentno."""
    items = jb.structure(ws)["items"]
    for n, pairs in EDITS.items():
        c = ws.cell(items[n], 2)
        c.value, done = jb.fix_text(c.value, pairs, f"{SHEET} {n}", idempotent=True)
        if done:
            log.append(f"    {n}: {done} zamjena")
    for start, pairs in NOTE_EDITS.items():
        r = jb.note_row(ws, start)
        c = ws.cell(r, 2)
        c.value, done = jb.fix_text(c.value, pairs, f"{SHEET} B{r}", idempotent=True)
        if done:
            log.append(f"    B{r} ({start[:26]}…): {done} zamjena")


def restore_auto_heights(wb, rows_before, inserted):
    """Redovi sa automatskom visinom u izvorniku (i novi redovi) ostaju bez zapisane visine."""
    for ws in wb.worksheets:
        auto = {r for r, (_, custom) in rows_before.get(ws.title, {}).items() if not custom}
        if ws.title == SHEET and inserted:
            auto = {shifted(r, inserted) for r in auto} | set(range(inserted[0],
                                                                  inserted[0] + inserted[1]))
        for r in auto:
            if r in ws.row_dimensions:
                ws.row_dimensions[r].height = None


def check_structure(ws):
    s = jb.structure(ws)
    items, lot_row = s["items"], s["lot_row"]
    r0, r1, rsub = s["sections"]["5"]
    bad = []
    if ws.cell(rsub, 6).value != f"=SUM(F{r0}:F{rsub - 1})":
        bad.append(f"UKUPNO 5 F{rsub} = {ws.cell(rsub, 6).value}")
    for n, *_ in NEW_DC_ITEMS:
        r = items.get(n)
        if r is None or not r0 <= r <= r1 or ws.cell(r, 6).value != jb.line_formula(r):
            bad.append(f"{n} nije cjenovna stavka unutar UKUPNO 5")
    want = "=" + "+".join(f"F{v[2]}" for v in sorted(s["sections"].values(), key=lambda v: v[2]))
    if ws.cell(lot_row, 6).value != want:
        bad.append(f"UKUPNO LOT 2 F{lot_row} = {ws.cell(lot_row, 6).value} != {want}")
    recap = [c.coordinate for row in ws.iter_rows(min_row=lot_row + 1) for c in row
             if c.value == f"=F{lot_row}"]
    if len(recap) != 1:
        bad.append(f"REKAPITULACIJA ne upućuje na UKUPNO LOT 2 (F{lot_row}): {recap}")
    if bad:
        raise SystemExit("struktura:\n  " + "\n  ".join(bad))
    return rsub, lot_row, recap[0]


def main():
    if not os.path.exists(XLSX):
        raise SystemExit(f"nema fajla: {XLSX}")
    rows_before = xml_rows(XLSX)
    src = openpyxl.load_workbook(XLSX)
    wb = openpyxl.load_workbook(XLSX)
    before = props(wb)
    ws = wb[SHEET]
    for other in wb.worksheets:                 # niko spolja ne smije pokazivati u LOT 2
        refs = [c.coordinate for row in other.iter_rows() for c in row if other is not ws
                and isinstance(c.value, str) and c.value.startswith("=") and SHEET in c.value]
        if refs:
            raise SystemExit(f"{other.title} upućuje na {SHEET} ({refs}) — umetanje bi ga slomilo")

    log = []
    inserted = insert_dc_items(ws, log)
    edit_texts(ws, log)
    if not log:
        print(f"ništa za uraditi — sve izmjene su već u fajlu:\n  {XLSX}")
        return

    restore_auto_heights(wb, rows_before, inserted)
    assert_no_loss(wb, src)                     # stavke, opisi, formule na svom redu
    rsub, lot_row, recap = check_structure(ws)
    def blob(book):
        return "\n".join(str(w.cell(r, c).value) for w in book.worksheets
                         for r in range(1, w.max_row + 1) for c in (1, 2, 3) if w.cell(r, c).value)
    had, has = blob(src), blob(wb)
    # COVERAGE iz compact_boq je stariji od Rev 9 („250 h" je namjerno uklonjen): ovdje se
    # traži da se ništa što je bilo prisutno ne izgubi, i da su novi DC zahtjevi tu.
    stale = [t for t in COVERAGE if t not in had]
    lost = [t for t in COVERAGE if t in had and t not in has]
    missing = [t for t in DC_COVERAGE if t not in has]
    if lost or missing:
        raise SystemExit(f"COVERAGE — izgubljeno: {lost}; nedostaje (DC): {missing}")

    bak = os.path.join(tempfile.gettempdir(), "PRILOG II Sjednica - prije fix_boq_dc_aux.xlsx")
    shutil.copy2(XLSX, bak)
    wb.save(XLSX)

    # poslije snimanja: zaglavlje, štampa i svojstva isti; visine redova po izvorniku
    after = props(openpyxl.load_workbook(XLSX))
    changed = [k for k in before if before[k] != after.get(k)]
    if changed:
        shutil.copy2(bak, XLSX)
        raise SystemExit(f"snimanje je promijenilo {changed} — izvornik vraćen iz {bak}")
    rows_after, bad = xml_rows(XLSX), []
    for name, flags in rows_before.items():
        for r, (ht, custom) in flags.items():
            rr = shifted(r, inserted) if name == SHEET else r
            got = rows_after.get(name, {}).get(rr, (None, False))
            if custom and (not got[1] or float(got[0]) != float(ht)):
                bad.append(f"{name} red {rr}: fiksna visina {ht} -> {got}")
            if not custom and got[1]:
                bad.append(f"{name} red {rr}: automatska visina postala fiksna {got}")
    if bad:
        shutil.copy2(bak, XLSX)
        raise SystemExit("visine redova:\n  " + "\n  ".join(bad[:10]))

    print(f"snimljeno: {XLSX}\nbackup:    {bak}")
    for line in log:
        print("  " + line)
    print(f"UKUPNO 5 F{rsub}, UKUPNO LOT 2 F{lot_row}, REKAPITULACIJA {recap} = F{lot_row}")
    print(f"COVERAGE: {len(COVERAGE) - len(stale)} postojećih + {len(DC_COVERAGE)} DC zahtjeva "
          f"prisutno, ništa izgubljeno (već ranije nedostaje: {stale}); zaglavlje, postavke "
          f"štampe i svojstva dokumenta nepromijenjeni; visine redova po izvorniku")


if __name__ == "__main__":
    main()
