# -*- coding: utf-8 -*-
"""
Rev 7 corrections to the `_K` master TD and Prilog I: FG Wilson P18-6.

Both `_K` files are hand-maintained by the Investor and must NEVER be
regenerated - `make_prilog1.py` is updated in step so the generator does not
drift, but it is not run. Every change here is a surgical OOXML substring
replacement through `ooxml_edit`, with the same `pending()` guard as
`tools/fix_td2.py` so a rerun is a no-op.

What moves, and what deliberately does not:

  - The reference set becomes **P18-6, 18 kVA / 14,4 kW** standby. The Investor
    chose 13,5 kVA on 2026-08-11 and reversed it on 2026-08-12: at 1076 m and
    40 C the P13.5-6's prime rating derates to 9,7 kW, below the 12,5 kW the
    rectifiers can draw.
  - The **engine does not change**. The P18-6 carries the same Perkins 404D-22G1
    (2,2 l, 4-cyl) as the P22-6, so only the cylinder/displacement wording is
    tightened.
  - The **ventilation figures do not change either**: radiator 1980 m3/h,
    combustion air 90 m3/h and the 3 kPa intake restriction are identical on the
    two sets, because they share the cooling pack. Only the exhaust is specific.
  - Exhaust returns to **NO 50**: 192 m3/h at 413 C is 27,2 m/s, under the
    customary 30 m/s, where the P22-6's 234 m3/h at 505 C gave 33 m/s. This
    restores agreement with BOQ 4.11, whose text always said NO 50 mm.
  - Masses 378/385 -> **365/372 kg**; In 31,75 -> **26,0 A**, so 3 x In is 78 A.

Carried in the same pass, since both files are open anyway: the Rev 6 fence
correction (1,90 -> 2,10 m, overhang 2,84 -> 2,64 m) and the bund -> korito
change that followed the double-skinned tank decision.

NOT touched here, and reported instead: Prilog I 4.3 still carries the pre-Rev-4
airflow layout (intake SOUTH, tank vent NORTH), which contradicts BOQ 4.8, M-01
and design.json - all three say intake NORTH, vent SOUTH. That is a genuine
tender conflict but it is not part of the genset swap.
"""
import os
import re
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ooxml_edit import edit_docx  # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TD = os.path.join(BASE, "TD-OUTPUT",
                  "3. TD JN Hibridni sistem napajanja BS Sjednica_K.docx")
PRILOG1 = os.path.join(BASE, "TD-OUTPUT",
                       "3. Prilog I TD - Specifikacija zahtjeva_K.docx")

ICC = "Huawei ICC360-HA1-C1 (PowerCube 1000)"

TD_EDITS = [
    ("agregatskog postrojenja snage cca 13.5 kVA",
     "agregatskog postrojenja snage cca 18 kVA", 1),
    # Table 1, Izvedba_snaga
    ("Kontejner_13.5 kVA", "Kontejner_18 kVA", 1),
    # the vendor quotation and review/01-huawei-solar.md §185/§190 both name the
    # actively cooled ICC360; Rev 2 had unified on ICC330-H1 + MTS9302 by count
    ("Huawei ICC330-H1 i MTS9302 (vanjski ormari)",
     f"{ICC} (vanjski ormar sa aktivnim hlađenjem)", 1),
    # LOT 2 qualification threshold follows the revised estimate
    ("za LOT 2 zbirne vrijednosti od minimalno 35.000,00 KM",
     "za LOT 2 zbirne vrijednosti od minimalno 34.000,00 KM", 1),
]

P1_EDITS = [
    # --- reference documents -------------------------------------------
    ("FG Wilson P22-6 (Skid) TDS 2019-08-14",
     "FG Wilson P18-6 (Skid) TDS 2019-08-14", 1),
    ("Huawei ICC330-H1 PowerCube Installation Guide",
     "Huawei ICC360-HA1-C1 (PowerCube 1000) Installation Guide", 1),

    # --- 4.1 the set ----------------------------------------------------
    ("22 kVA / 17,6 kW standby, 400/230 V, 50 Hz",
     "18 kVA / 14,4 kW standby, 400/230 V, 50 Hz", 1),
    ("FG Wilson P22-6 ili ekvivalent", "FG Wilson P18-6 ili ekvivalent", 1),
    ("Perkins 404D-22G ili ekvivalent, 4-cilindarski, 1500 o/min",
     "Perkins 404D-22G1 ili ekvivalent, 4-cilindarski, 2,2 l, 1500 o/min", 1),
    ("378 kg suho / 385 kg mokro (referentno)",
     "365 kg suho / 372 kg mokro (referentno)", 1),
    ("trajna struja kratkog spoja ≥3 × In (≈95 A)",
     "trajna struja kratkog spoja ≥3 × In (≈78 A)", 1),
    # the figures are P22-6 general-arrangement renders; the skid envelope is
    # identical on the P18-6, so they stay - but they are marked as illustrative,
    # the way the tank figures already are
    ("FG Wilson P22-6, bočni pogled",
     "FG Wilson P18-6 (Skid), bočni pogled (ilustrativno)", 1),
    ("Slika 2 — FG Wilson P22-6, čeoni pogled (generator)",
     "Slika 2 — FG Wilson P18-6 (Skid), čeoni pogled (generator) (ilustrativno)", 1),

    # --- 4.2 tank: drip tray, not a 110 % bund --------------------------
    ("Sekundarna zaštita zapremine ≥110 % (550 l), referentno 1600 × 1060 mm, "
     "visina ruba 330 mm",
     "Sekundarnu zaštitu čini međuplašt dvoplašnog spremnika sa sondom za "
     "detekciju curenja, pa tankvana zapremine ≥110 % NIJE zahtijevana. Ispod "
     "spremnika se izvodi prihvatno KORITO (kada) za prihvat kapanja i "
     "prosipanja, referentno 1150 × 640 mm, visina ruba 200 mm, sa vidljivim "
     "najnižim mjestom za kontrolu i pražnjenje", 1),

    # --- 4.4 exhaust ----------------------------------------------------
    ("234 m³/h (3,9 m³/min) pri 505 °C", "192 m³/h (3,2 m³/min) pri 413 °C", 1),
    ("DN 65 (stavka 4.11)",
     "NO 50 (stavka 4.11) — pri 192 m³/h i 413 °C brzina je 27,2 m/s "
     "(< 30 m/s), protutlak ≈1,9 kPa uz dozvoljenih 10,2 kPa", 1),

    # --- electrical -----------------------------------------------------
    ("In = 31,75 A pri 22 kVA / 400 V", "In = 26,0 A pri 18 kVA / 400 V", 1),

    # --- Rev 6 fence correction, carried at the same time ----------------
    ("ograda h = 1,90 m, kapija 1,00 m", "ograda h = 2,10 m, kapija 1,00 m", 1),
    ("2,84 m iznad kote ograde h = 1,90 m",
     "2,64 m iznad kote ograde h = 2,10 m", 1),
]


def pending(path, edits):
    """Drop edits already applied, so a rerun is a no-op instead of an error."""
    z = zipfile.ZipFile(path)
    text = "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>",
                              z.read("word/document.xml").decode("utf-8")))
    z.close()
    out = []
    for e in edits:
        if e[0] in text:
            out.append(e)
        elif e[1] not in text:
            raise SystemExit(
                f"EDIT LOST: neither the original nor the replacement is present "
                f"in {os.path.basename(path)}: {e[0][:60]}...")
    return out


def main():
    for path, edits in ((TD, TD_EDITS), (PRILOG1, P1_EDITS)):
        todo = pending(path, edits)
        print(os.path.basename(path))
        if not todo:
            print("  already applied")
            continue
        applied = edit_docx(path, todo, backup=path + ".bak")
        for find, part, count in applied:
            print(f"  ok ({count}x): {find[:66]}...")
        os.remove(path + ".bak")


if __name__ == "__main__":
    main()
