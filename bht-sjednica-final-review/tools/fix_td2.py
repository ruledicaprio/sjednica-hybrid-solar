# -*- coding: utf-8 -*-
"""
Rev-2 text corrections to `3. TD JN Hibridni sistem napajanja BS Sjednica.docx`.

Closes, in the TD body:
  - Y-16   the garbled LOT-2 sentence in the scope list (a LOT-1 fragment was
           merged into it) and the blanket "sve na SJEVERNOJ strani kontejnera"
           placement, replaced by the per-wall cross-flow layout of drawing M-01
           (closes EL RED-03 at the document level);
  - Y-14   first fuel fill 200 l vs the 500 l priced in BOQ 4.16 — unified at 500 l;
  - sec-G #7  power-system naming — unified on ICC330-H1 + MTS9302 (Investor's
           choice, 2026-08-11);
  - sec-G #9  existing GRO circuits incl. the K7 tower obstruction light get a
           survey-and-transfer obligation tied to the new BOQ item.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ooxml_edit import edit_docx  # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TD = os.path.join(BASE, "TD-OUTPUT",
                  "3. TD JN Hibridni sistem napajanja BS Sjednica.docx")
ODLUKA = os.path.join(BASE, "TD-OUTPUT",
                      "2. Prijedlog Odluke Hibridni sistem napajanja BS Sjednica.docx")
NZ = os.path.join(BASE, "TD-OUTPUT",
                  "1. NZ hibridni sistem napajanja BS Sjednica.docx")

EDITS = [
    # Y-16 + placement: de-garble and replace the blanket north-wall statement
    ("transport, montažu, povezivanje i pričvršćenje DEA — SMJEŠTANJE U "
     "POSTOJEĆI KONTEJNER transport montažu nosača fotonaponskih panela za "
     "podlogu, uključujući ugradnju sistema za odvod dimnih gasova, žaluzina i "
     "ventilacije prostora agregata, sve na SJEVERNOJ strani kontejnera.",
     "transport, montažu, povezivanje i pričvršćenje DEA — SMJEŠTANJE U "
     "POSTOJEĆI KONTEJNER — uključujući ugradnju sistema za odvod dimnih "
     "gasova, žaluzina i ventilacije prostora agregata, u rasporedu prema "
     "crtežu M-01 (Prilog III): usisna žaluzina na SJEVERNOM zidu kontejnera "
     "(donja ivica cca 0,30 m od poda), kanal hladnjaka sa izlaznom žaluzinom "
     "i izduvni sistem na ZAPADNOM zidu (završetak izduva iznad krova, sa "
     "hvatačem iskri), odušna cijev spremnika na JUŽNOM zidu — međusobna "
     "prostorna udaljenost usisa, izduva i odušne cijevi ≥3 m.",
     1),
    # Y-14: first fill aligned with BOQ 4.16 (500 l priced)
    ("tankanje najmanje 200 l dizel goriva EURO 5 EN 590",
     "tankanje 500 l (pun spremnik) dizel goriva EURO 5 EN 590",
     1),
    # sec-G #7: name the actual outdoor units
    ("planirani sistem napajanja: Huawei MTS9302 sa ispravljačima, LFP "
     "baterijama i kontrolerom, ili drugi kompatibilan sistem",
     "postojeći/planirani sistem napajanja: Huawei ICC330-H1 + MTS9302 "
     "(vanjski ormari) sa ispravljačima, LFP baterijama i kontrolerom, ili "
     "drugi kompatibilan sistem",
     1),
    # sec-G #9: circuit survey + transfer, obstruction light on its own circuit
    ("prema zahtjevima iz Priloga II i Priloga III ove tenderske "
     "dokumentacije. Lokacija nije priključena",
     "prema zahtjevima iz Priloga II i Priloga III ove tenderske "
     "dokumentacije. U novi GRO se, uz prethodno snimanje stanja, prevezuje "
     "svih 7 postojećih strujnih krugova postojećeg razvoda, uključujući "
     "signalnu rasvjetu prepreke antenskog stuba (krug K7) koja se izvodi kao "
     "zaseban nadzirani strujni krug (v. Predmjer, LOT 2). Lokacija nije "
     "priključena",
     1),
    # stale since the 3x4 redesign
    ("Nosači za fotonaponske panele (ground support), 2 kom",
     "Nosači za fotonaponske panele (ground support), 3 kom",
     1),
]


ODLUKA_EDITS = [
    # sec-G #7 again: the decision paper named a third power system
    ("ispravljačima Huawei PowerCube 1000, tip ICC360-HA1-C1",
     "ispravljačima Huawei ICC330-H1 + MTS9302 ili kompatibilnim sistemom",
     1),
    # stale since the 3x4 redesign - the BOQ, Prilog I and the drawings all say 3
    ("nosača za fotonaponske panele (gound mount support) - 2 kpl",
     "nosača za fotonaponske panele (ground mount support) - 3 kpl",
     2),
]

NZ_EDITS = [
    ("nosača za fotonaponske panele (gound mount support) - 2 kpl",
     "nosača za fotonaponske panele (ground mount support) - 3 kpl",
     1),
]


def pending(path, edits):
    """Drop edits already applied, so a rerun is a no-op instead of an error."""
    import re
    import zipfile
    z = zipfile.ZipFile(path)
    text = "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>",
                              z.read("word/document.xml").decode("utf-8")))
    z.close()
    out = []
    for e in edits:
        if e[0] in text:
            out.append(e)
        elif e[1] not in text:
            raise SystemExit(f"EDIT LOST: neither the original nor the replacement "
                             f"is present in {os.path.basename(path)}: {e[0][:60]}...")
    return out


def main():
    for path, edits in ((TD, EDITS), (ODLUKA, ODLUKA_EDITS), (NZ, NZ_EDITS)):
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
