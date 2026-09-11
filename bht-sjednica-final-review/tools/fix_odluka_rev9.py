# -*- coding: utf-8 -*-
"""
Rev 9 (2026-09-11): Prijedlog Odluke — genset operation, genset type, stand count.

Three statements in the Odluka no longer held:

  Aneks 2   "maksimalno dozvoljeno godišnje vrijeme rada ... 250 h (standby ...)" and
            "spremnik goriva zapremine 500 l treba obezbjediti autonomiju od najmanje
            godinu između dopuna goriva". The pvsim simulation (review/pvsim/,
            decision in review/09-odluka-nosaci-nagib.md) gives ≈280 h and ≈940 l a
            year even with the SMU set for minimum genset running - no setting
            reaches either figure. Replaced with the simulated expectation, in the
            wording the Investor approved on 2026-09-11.
  LOT 2     "za režim rada u pričuvi (stand-by) prema ISO 8528-3, kao FG Wilson P22-6"
            - the P22-6 was withdrawn in Rev 7, and a set that cycles on battery SoC
            at an off-grid site runs in prime duty, capped at 9,5 kW (07-proracuni D.5).
  LOT 1     "sa 2 (dva) nosača" - the design has had three stands since 2026-08-08;
            the same document says "3 kpl" in two other places.

OOXML edit through ooxml_edit.edit_docx - the document is not regenerated.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ooxml_edit import edit_docx                                    # noqa: E402
from paths import TD                                                # noqa: E402

DOC = os.path.join(TD, "2.1 Prijedlog Odluke Hibridni sistem napajanja BS Sjednica.docx")

OLD_LIMITS = (
    "Projektnim zadatkom i RFI dokumentom, maksimalno dozvoljeno godišnje vrijeme rada "
    "dizel električnog agregata iznosi 250 h (standby režim prema ISO 8528-3), zbog "
    "čega je sistem dimenzionisan da se rad agregata svede na minimum u vrijeme "
    "uzastopnih dana bez osunčanosti ili kvara na opremi, dok sam spremnik goriva "
    "zapremine 500 l treba obezbjediti autonomiju od najmanje godinu između dopuna "
    "goriva, a teoretski i više.")
NEW_LIMITS = (
    "Sistem je dimenzionisan tako da fotonaponsko polje pokriva najveći dio "
    "potrošnje, a dizel električni agregat radi samo kada baterije dostignu zadanu "
    "dubinu pražnjenja, tj. u nizovima dana slabe osunčanosti i pri kvaru opreme. "
    "Satna simulacija energetskog bilansa za 19 godina (pvlib, PVGIS-SARAH3, "
    "2005–2023) daje očekivani rad agregata od ≈280 h godišnje (u najlošijoj godini "
    "do ≈360 h), uz potrošnju goriva od ≈940 l godišnje; spremnik od 500 l "
    "dopunjava se u prosjeku dva do tri puta godišnje. Vrijednosti važe uz "
    "parametriranje upravljačke jedinice za minimalan rad agregata, propisano "
    "Prilogom I TD. Agregat radi u režimu trajne (prime) snage prema ISO 8528-1, sa "
    "ulaznom snagom ispravljača ograničenom na 9,5 kW.")

EDITS = [
    (OLD_LIMITS, NEW_LIMITS, 1),
    ("za režim rada u pričuvi (stand-by) prema ISO 8528-3, kao FG Wilson P22-6 ili "
     "ekvivalent",
     "za rad u režimu trajne (prime) snage prema ISO 8528-1, sa ulaznom snagom "
     "ispravljača ograničenom na 9,5 kW, kao FG Wilson P18-6 ili ekvivalent", 1),
    ("sa ožičenjem sistema do potpune funcionalnosti i puštanjem u rad..",
     "sa ožičenjem sistema do potpune funcionalnosti i puštanjem u rad.", 1),
    ("metalne konstrukcija sa 2 (dva) nosača za fotonaponske panele",
     "metalna konstrukcija sa 3 (tri) nosača za fotonaponske panele", 1),
]


def main():
    for find, part, n in edit_docx(DOC, EDITS):
        print(f"  {n}× {part}: {find[:70]}…")
    print(f"snimljeno: {DOC}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
