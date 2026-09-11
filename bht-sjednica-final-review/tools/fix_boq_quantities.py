"""Rev 8 (2026-08-12) — količine u Prilogu II.

Pokreće se JEDNOM. Naručilac je osporio 6 m² limenog kanala; provjera je pokazala
da su tri grupe količina pogrešne, a jedna stavka sama sebi protivrječi.

  Q1  LOT 1 · 2.1/2.2/2.2a/2.3  temeljne trake nose 0,41 m³ po traci (450 × 275),
      a S-02 crta i njegova napomena 2 propisuje traku PUNE dubine 900 mm =
      1,485 m³. Iskop je već bio dimenzionisan za rov 900 mm, pa su se iskop i
      beton razilazili. Mjerodavan je crtež: spreg od 26,6 kN po traci traži
      32,1 kN stabilizujuće težine, koju puna traka daje sama (0,41 m³ daje 8,9 kN
      i fali joj 17,7 kN, koje bi mogla posuditi samo od trenja o zasip — na kršu
      to nije dokaz).
  Q2  LOT 2 · 4.5   limeni kanal 6 m² → ≈1,0 m². Hladnjak je 60 mm od ZAPADNOG
      zida, kanal je prelazni komad ≈0,2 m. Naslijeđeno iz specifikacije za salu
      „POTOCI" Mostar, gdje je stavka glasila 10 m² jer je agregat stajao daleko
      od zida.
  Q3  LOT 2 · 4.12  izolacija izduva 6 m² → ≈3,0 m². 6 m² traži 12 m cijevi;
      stvarna trasa je 1 m + do 4 m. Trasa se sada iskazuje u metrima, kako je i
      mostarski predložak radio, pa se površina više ne može otkinuti od dužine.
  Q4  LOT 2 · 4.10  isti opis traži izduv „oboreno prema zemlji u obliku lule" I
      „završetak IZNAD KROVA usmjeren naviše". Prilog I §4.4 i design.json traže
      iznad krova — prva varijanta se briše.
  Q5  LOT 2 · 4.1   antivibracioni oslonci su bili pola rečenice, bez tipa, broja
      i progiba; Prilog I §4.1 traži vlastitu frekvenciju ≤8 Hz.
  Q6  LOT 2 · 4.2   gorivo ide do motora KRUTOM Cu cijevi NO 8. Motor stoji na
      antivibracionim osloncima i pomiče se — kruta cijev na priključku puca.
      Izduv već ima elastični umetak, hladnjak ceradni spoj; vod goriva je jedini
      koji je ostao krut.
  Q7  LOT 1 · 1.4   tekst kaže „obje konstrukcije", a količina je 3.
  Q8  LOT 2 · 5.1   rov 30 m1 uz kablove „do 15 m" — dopisano iz čega se sastoji.
"""
import os
import shutil
import sys

import openpyxl

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from compact_boq import item_row, set_text, sub_in  # noqa: E402
from fix_boq_lots import assert_no_loss, free_cell, priced_items  # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XLSX = os.path.join(BASE, "TD-OUTPUT",
                    "3.1 PRILOG II TD - predmjer Sjednica Bileca.xlsx")
NL = "\n"


def set_qty(ws, num, qty):
    r = item_row(ws, num)
    free_cell(ws, r, 4)
    ws.cell(r, 4).value = qty
    return r


# --------------------------------------------------------------------------
def lot1(ws):
    # Q7 --------------------------------------------------------------------
    sub_in(ws, "1.4", [("povezivanje obje konstrukcije",
                        "povezivanje sva tri nosača")])

    # Q1 — trake pune dubine ------------------------------------------------
    set_text(ws, item_row(ws, "2.1"),
             "Iskop zemlje/stijene IV-V kategorije za temeljne trake nosača, do "
             "donje ivice podložnog betona. Rov širine 550 mm, dubine 950 mm, "
             "dužine 3300 mm. 3 nosača × 2 trake × 1,725 m3")
    set_qty(ws, "2.1", 10.35)

    set_text(ws, item_row(ws, "2.2"),
             "Zatrpavanje preostalog dijela rova zemljom od iskopa uz nabijanje u "
             "slojevima. Traka je pune dubine, pa se zatrpava samo klin uz "
             "kosinu rova. 3 nosača × 2 trake × 0,149 m3")
    set_qty(ws, "2.2", 0.89)

    set_qty(ws, "2.2a", 9.45)

    sub_in(ws, "2.2b", [("3 nosača × 2 trake × 0,094 m3",
                         "3 nosača × 2 trake × 0,091 m3")])
    set_qty(ws, "2.2b", 0.54)

    sub_in(ws, "2.3", [
        ("3 nosača × 2 trake × 0,41 m³",
         "Traka 450 mm (gore) / 550 mm (dolje) × 3300 mm, PUNE dubine 900 mm = "
         "1,485 m³ po traci. 3 nosača × 2 trake × 1,485 m³"),
        ("Dubina trake prema ovjerenom statičkom proračunu iz Tačke 1.3.",
         "Dubina 900 mm je tenderska osnova i mjerodavna je za ponudu; konačnu "
         "dubinu i armaturu potvrđuje ovjereni statički proračun iz Tačke 1.3. "
         "Traka se betonira punom dubinom rova — vlastita težina trake je dio "
         "dokaza sigurnosti na podizanje i prevrtanje."),
    ])
    set_qty(ws, "2.3", 8.91)


# --------------------------------------------------------------------------
def lot2(ws):
    # Q5 --------------------------------------------------------------------
    sub_in(ws, "4.1", [
        ("na antivibracionim osloncima sa pripremom za pričvršćenje za podlogu",
         "na antivibracionim gumeno-metalnim osloncima (min. 4 kom, vlastita "
         "frekvencija ≤8 Hz, statički progib ≥5 mm), postavljenim između skida i "
         "roštilja iz Tačke 4.3, sa pripremom za pričvršćenje za podlogu"),
    ])

    # Q6 --------------------------------------------------------------------
    sub_in(ws, "4.2", [
        (" - napajanje motora gorivom kroz Cu cijevi NO 8 mm (polazni i povratni "
         "vod)",
         " - napajanje motora gorivom kroz Cu cijevi NO 8 mm (polazni i povratni "
         "vod); na oba voda, neposredno uz motor, ugraditi FLEKSIBILNI UMETAK "
         "(armirano crijevo za dizel gorivo) — motor stoji na antivibracionim "
         "osloncima i kruta cijev na priključku zamara i puca"),
    ])

    # Q2 --------------------------------------------------------------------
    sub_in(ws, "4.5", [
        ("Izrada i montaža limenog kanala P ≈ 6 m² za odvod toplog zraka sa "
         "agregata, od pocinčanog lima d=1 mm, sa prirubnicama 30 × 1,5 mm, "
         "komplet sa fazonskim komadima i ovjesnim priborom.",
         "Izrada i montaža limenog kanala za odvod toplog zraka sa agregata, od "
         "pocinčanog lima d=1 mm, sa prirubnicama 30 × 1,5 mm, komplet sa "
         "fazonskim komadima i ovjesnim priborom. Kanal je PRELAZNI KOMAD od "
         "prirubnice hladnjaka do žaluzine 600 × 600 mm kroz ZAPADNI zid; "
         "hladnjak je 60 mm od zida, pa je razvijena površina ≈1,0 m². Stvarnu "
         "mjeru uzeti na licu mjesta prema ponuđenom agregatu."),
    ])

    # Q4 + trasa u metrima --------------------------------------------------
    sub_in(ws, "4.10", [
        ("čelična cijev NO 50 mm sa ispušnim loncem, izvedena izvan kontejnera i "
         "završena oboreno prema zemlji u obliku lule. Na kraju izduvne cijevi "
         "postaviti HVATAČ ISKRI.",
         "čelična cijev NO 50 mm sa ispušnim loncem (prigušivačem), izvedena "
         "izvan kontejnera i završena IZNAD KROVA, usmjereno naviše, sa kapom "
         "protiv upada padavina. Na kraju izduvne cijevi postaviti HVATAČ ISKRI. "
         "Dužine: od elastičnog umetka do prigušivača, sa jednim lukom 90°, "
         "1 m; od prigušivača do izlaza iznad krova, do 4 m."),
    ])

    # Q3 --------------------------------------------------------------------
    sub_in(ws, "4.12", [
        ("Termička izolacija izduvnog sistema kamenom vunom d=50 mm i opšivanje "
         "izduvnog cjevovoda i lonca Al limom d=1 mm, do P ≈ 6 m².",
         "Termička izolacija izduvnog sistema kamenom vunom d=50 mm i opšivanje "
         "izduvnog cjevovoda i lonca Al limom d=1 mm. Za trasu do 5 m iz Tačke "
         "4.10 i vanjski prečnik izolacije ≈165 mm razvijena površina je "
         "≈3,0 m²."),
    ])

    # G1 — ograničenje ulazne snage ispravljača ------------------------------
    # Zatečeno stanje: broj 9,5 kW ne postoji nigdje u predmjeru, iako je to
    # mjerodavno elektro ograničenje (07-proracuni D.5). Derativana prime snaga
    # agregata je 11,6 kW, a neograničen ispravljački sistem vuče 12,5 kW — bez
    # ovog broja ponuđač isporučuje postavku koja preopterećuje agregat.
    # Prilog I §4.6 traži „ograničenje ulazne snage" ali BEZ brojke.
    sub_in(ws, "3.1", [
        ("OSTALA OPREMA: start baterija 12 V / 70 Ah;",
         "OGRANIČENJE OPTEREĆENJA (OBAVEZNO): dok agregat radi, ulazna snaga "
         "ispravljačkog sistema ograničava se u kontroleru na maks. 9,5 kW "
         "(≈82 % derativane prime snage na 1076 m n.v. i +40 °C, koja iznosi "
         "11,6 kW). Neograničen ispravljački sistem vuče ≈12,5 kW i premašuje "
         "raspoloživu snagu. Granica ujedno drži agregat iznad 30 % opterećenja "
         "i sprječava mokri rad motora.\n"
         "OSTALA OPREMA: start baterija 12 V / 70 Ah;"),
    ])
    sub_in(ws, "5.7", [
        ("parametriranje kriterija automatskog starta po stanju napunjenosti "
         "baterija (SoC).",
         "parametriranje kriterija automatskog starta po stanju napunjenosti "
         "baterija (SoC) te postavljanje ograničenja ulazne snage ispravljačkog "
         "sistema na maks. 9,5 kW za vrijeme rada agregata, prema Tački 3.1."),
    ])

    # G2 — korito ispod spremnika niko ne isporučuje --------------------------
    # Zatečeno stanje: 4.2 i 4.3 oba upućuju na „korito iz Tačke 4.3", ali 4.3
    # isporučuje samo roštilj. Nijedna stavka ne nabavlja samo korito, a njegove
    # mjere (1150 × 640, rub 200) ne postoje nigdje u predmjeru.
    sub_in(ws, "4.2", [
        ("smještaj u JUGOISTOČNI ugao kontejnera, u koritu iz Tačke 4.3, prema "
         "crtežu M-01",
         "smještaj u JUGOISTOČNI ugao kontejnera, prema crtežu M-01"),
        (" - spremnik strukturno ojačan i zaštićen od krađe goriva",
         " - PRIHVATNO KORITO (kada) ispod spremnika, 1150 × 640 mm, visina ruba "
         "200 mm, od čeličnog lima sa antikorozivnom zaštitom, sa vidljivim "
         "najnižim mjestom za kontrolu i pražnjenje. Korito NIJE tankvana od "
         "110 % — sekundarnu zaštitu čini međuplašt dvoplašnog spremnika — nego "
         "prihvata kapanje i prosipanje pri punjenju i pretakanju\n"
         " - spremnik strukturno ojačan i zaštićen od krađe goriva"),
    ])

    # G3 — 6.4 ima formulu, ali nema ni jedinicu ni količinu -----------------
    # Posljedica: ćelija cijene ostaje prazna, stavka tiho ispada iz UKUPNO 6 i
    # dokumentacija izvedenog stanja za cijeli LOT 2 se ne plaća. Otkriveno
    # prerachunom sa 100 KM po stavci.
    r = item_row(ws, "6.4")
    if ws.cell(r, 3).value or ws.cell(r, 4).value:
        raise SystemExit("6.4 već ima jedinicu/količinu — provjeriti ručno")
    free_cell(ws, r, 3)
    ws.cell(r, 3).value = "kpl"
    free_cell(ws, r, 4)
    ws.cell(r, 4).value = 1

    # Q8 --------------------------------------------------------------------
    sub_in(ws, "5.1", [
        ("Obračun po ostvarenom m1.",
         "Količina obuhvata trasu hibridni sistem — DEA i nosači FN panela do "
         "15 m1 i krak uzemljivačke trake do nosača, ukupno do 30 m1. Obračun po "
         "ostvarenom m1."),
    ])


# --------------------------------------------------------------------------
def main():
    if not os.path.exists(XLSX):
        raise SystemExit(f"nema fajla: {XLSX}")
    bak = XLSX.replace(".xlsx", ".rev8-bak.xlsx")
    shutil.copy2(XLSX, bak)

    wb = openpyxl.load_workbook(XLSX)
    src = openpyxl.load_workbook(bak)

    lot1(wb["LOT 1"])
    lot2(wb["LOT 2"])

    # Nijedan opis ne smije nestati niti se prepoloviti. 4.12 se namjerno skraćuje
    # jer gubi brojku 6 m2, ali ostaje daleko iznad polovine.
    assert_no_loss(wb, src)

    # Svaka cjenovna stavka mora zadržati formulu koja adresira SVOJ red.
    for ws in wb.worksheets:
        for num, r in priced_items(ws).items():
            f = str(ws.cell(r, 6).value or "")
            if not f:
                continue          # 3.1 je tehnička specifikacija, bez cijene
            if f"D{r}<>" not in f:
                raise SystemExit(f"{ws.title} {num} (red {r}): formula ne "
                                 f"adresira svoj red — {f!r}")

    # COVERAGE iz compact_boq: nijedan tehnički zahtjev ne smije nedostajati.
    # „9,5 kW" i „1150 × 640" su ovdje i nedostajali prije ovog skripta — ovaj
    # prolaz je jedini razlog što se to uopšte vidjelo.
    from compact_boq import COVERAGE
    blob = "\n".join(str(ws.cell(r, c).value)
                     for ws in wb.worksheets
                     for r in range(1, ws.max_row + 1)
                     for c in (1, 2, 3)
                     if ws.cell(r, c).value)
    missing = [t for t in COVERAGE if t not in blob]
    if missing:
        raise SystemExit(f"COVERAGE — nedostaju zahtjevi: {missing}")

    wb.save(XLSX)
    print(f"snimljeno: {XLSX}\nbackup:    {bak}\nCOVERAGE: svih "
          f"{len(COVERAGE)} zahtjeva prisutno")


if __name__ == "__main__":
    main()
