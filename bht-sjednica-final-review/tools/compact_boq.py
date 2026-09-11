# -*- coding: utf-8 -*-
"""
Sažimanje Priloga II i ispravke grešaka (Rev 8, 2026-08-12).

Predmjer je kroz šest revizija narastao na 157 redova u LOT-u 2, od kojih je ~40
„siročad" - nastavci opisa tačke 3.1 razliveni po redovima bez broja stavke.
Pojedini opisi nose obrazloženja koja već stoje u Prilogu I i u
`review/07-proracuni.md`.

PRAVILO SAŽIMANJA: **brisati objašnjenje, zadržati obavezu.** Nijedan tehnički
zahtjev ne smije nestati; briše se samo tekst koji obrazlaže *zašto* je zahtjev
postavljen. Zaštita je `COVERAGE` niže - lista obaveznih tokena koja mora preživjeti,
inače skript pada.

Ispravljene greške:
  E1  prva stavka sekcije 3 numerisana `1.1` umjesto `3.1` - i stavka 4.1 i
      Prilog I referenciraju „Tačku 3.1", pa su obje reference visile
  E2  stavka 6.4 ostala bez opisa (regresija iz `fix_boq_lots.py`)
  E3  stavka 4.19 ima broj i nema opis (naslijeđeno)
  E4  dvostruko obračunavanje: 3.1 i 4.1 obje cjenovne, pa `UKUPNO LOT 2`
      namjerno izostavlja `UKUPNO 3` - i time gubi 3.2 (rezervni dijelovi)
  E5  5.13 referencira obrisanu „Tačku 1.6"; „Tačka 1.1" nejednoznačna
  E6  jedinica `pšl` umjesto `paušal`
  E7  tri prazna reda u LOT 1 (ostatak Rev 7 repacka)
  E8  4.4 nosi 3,93 kN/m² (vrijednost za P22-6) i riječ „tankvane"
  E9  5.6 / 5.16 referenciraju obrisanu „Tačku 1.6 LOT-a 1"
  E10 5.6 napomena tvrdi „agregat je SHUNT pobude", a tender PMG/AREP zahtijeva
  E11 LOT 1 1.1 nosi moment 62,8 kNm i 1.2 nosi 39,3 kN/traci - vrijednosti za
      donju ivicu +1,50 m, koja je spuštena na +0,50 m
  E12 LOT 1 1.1 referencira obrisanu „Tačku 1.6a" i odmak 400 mm izveden na
      staroj visini
"""
import os
import shutil
import sys

import openpyxl

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fix_boq_lots import (assert_no_loss, extend_section_sums,  # noqa: E402
                          free_cell, priced_items, remap_formulas, wrap)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XLSX = os.path.join(BASE, "TD-OUTPUT",
                    "3.1 PRILOG II TD - predmjer Sjednica Bileca.xlsx")
NL = "\n"

# Tokeni koji MORAJU preživjeti sažimanje. Svaki je tehnički zahtjev, ne opis.
COVERAGE = [
    "PMG", "AREP", "IP23", "klasa izolacije H", "THDv", "3 × In", "10 s",
    "BAS EN 590", "−20 °C", "ISO 3046", "ISO 8528-3", "SoC", "GIM01C1", "AIU03",
    "DSE 7420", "12 VDC", "70 Ah", "IP41", "9,5 kW", "404D-22G1", "dvoplašn",
    "međuplašt", "HVATAČ ISKRI", "NO 50", "EN 61643-11", "EN 61643-21",
    "TIP 1 + 2", "RCD", "300 mA", "roštilj", "C30/37", "XF3", "B500B",
    "paušal", "250 h", "ICC360-HA1-C1", "MTS9302A", "EMERGENCY STOP",
    "S275JR", "EN ISO 1461", "EXC2", "M16", "8.8", "pull-out", "ETA",
    "Stamford", "VDE 0530", "IEC 60034-1", "Modbus", "SNMP", "Ignition",
    "DIN 2448", "NO 8 mm", "S-6", "ROS", "OZR-1", "600 °C", "H1Z2Z2-K",
    "MC4", "iSSU", "PVDB", "Fe/Zn 25×4", "50 mm²", "10 Ω", "1,20 kN/m²",
    "45°", "18,1 kN", "13,4 kN", "42,6 kNm", "26,6 kN", "10,00 kN/m²",
    "3,80 kN/m²", "9,2 kN/m²", "1150 × 640", "K7", "72-satni",
]


# --------------------------------------------------------------------------
def item_row(ws, num):
    for r in range(1, ws.max_row + 1):
        if str(ws.cell(r, 1).value or "").strip() == num:
            return r
    raise SystemExit(f"{ws.title}: nema stavke {num!r}")


def set_text(ws, r, text):
    free_cell(ws, r, 2)
    ws.cell(r, 2).value = text
    wrap(ws, r)


def blank(ws, r):
    for c in range(1, 7):
        free_cell(ws, r, c)
        ws.cell(r, c).value = None


def absorb(ws, num, text, n_follow, dead):
    """Upisati sažeti tekst u red stavke i isprazniti n narednih „siročad" redova."""
    r = item_row(ws, num)
    set_text(ws, r, text)
    for k in range(1, n_follow + 1):
        if str(ws.cell(r + k, 1).value or "").strip():
            raise SystemExit(f"{ws.title}: red {r + k} nosi broj stavke "
                             f"{ws.cell(r + k, 1).value!r} - ne briše se")
        blank(ws, r + k)
        dead.add(r + k)
    return r


def sub_in(ws, num, pairs):
    """Ciljane zamjene unutar opisa stavke; svaka mora pogoditi."""
    r = item_row(ws, num)
    cur = str(ws.cell(r, 2).value or "")
    for old, new in pairs:
        if old not in cur:
            if new in cur:
                continue
            raise SystemExit(f"{ws.title} {num}: nema sidra {old[:60]!r}")
        cur = cur.replace(old, new)
    set_text(ws, r, cur)
    return r


# --------------------------------------------------------------------------
# Sažeti tekstovi
# --------------------------------------------------------------------------
DEA = (
    "Isporuka automatskog DEA sljedećih karakteristika. TEHNIČKA SPECIFIKACIJA — "
    "bez cijene; nabavna vrijednost agregata iskazuje se u Tački 4.1." + NL +
    "AGREGAT: 18 kVA / 14,4 kW (±5 %) pri cosφ 0,8, Stand-by prema ISO 8528-3; "
    "kao FG Wilson P18-6 (Skid) ili ekvivalent. Pouzdan start i rad do −20 °C. "
    "Snaga prema ISO 3046 za nadmorsku visinu preko 1000 m (lokacija 1076 m n.v.); "
    "ponuđač dostavlja derating snage za nadmorsku visinu i temperaturu." + NL +
    "DIZEL MOTOR: Perkins, Cummins, Cat®, Deutz ili John Deere; četverotaktni "
    "linijski, direktno ubrizgavanje, vodeno hlađen; radna zapremina cca 2,2 l, "
    "mehanički regulator broja obrtaja; gorivo BAS EN 590; elektropokretač 12 VDC, "
    "1500 o/min; senzor temperature rashladne tečnosti, senzor pritiska ulja, "
    "start/stop relej; filter ulja, zraka i goriva; samousisna dobavna pumpa "
    "goriva 12 VDC; GRIJAČ RASHLADNE TEČNOSTI 230 V sa podesivim termostatom "
    "(obavezno — zimski rad). Kao Perkins 404D-22G1 ili ekvivalent." + NL +
    "GENERATOR: Stamford, Leroy-Somer, Mecc Alte ili Marelli; VDE 0530, "
    "IEC 60034-1; trofazni, sinhroni, samouzbudni, bezčetkični; 18 kVA pri "
    "cosφ 0,8, 1500 o/min, 3×400/230 V, 50 Hz; IP23, klasa izolacije H, "
    "AVR ±1 %, THDv 5 %." + NL +
    " - POBUDA (OBAVEZNO): nezavisni sistem pobude — PMG ili AREP/AUX namotaj. "
    "Trajna struja kratkog spoja najmanje 3 × In (≈78 A pri 18 kVA / 400 V) u "
    "trajanju od najmanje 10 s, prema ISO 8528-3. Standardna SHUNT pobuda NIJE "
    "prihvatljiva — kod nje trajna struja kvara pada na ≈0,5 × In (13 A), ispod "
    "nazivne struje, i ne aktivira prekostrujnu zaštitu; tehnički list "
    "referentnog P18-6 navodi Short Circuit Capacity 0 % u SHUNT izvedbi. "
    "Ponuđač dostavlja podatak o trajnoj struji kratkog spoja iz tehničkog lista "
    "proizvođača." + NL +
    " - kao Stamford BCI164C u izvedbi sa PMG ili AREP/AUX pobudom, ili "
    "ekvivalent." + NL +
    "KOMANDNI ORMAR (KOA): limeni, zabravljen, mehaničke zaštite min. IP41, svi "
    "priključci odozdo; sabirnice L1, L2, L3, N i PE (N i PE spojene samo na "
    "jednom mjestu); neovisan strujni krug za grijač motora, servisna utičnica "
    "230 V AC, rasvjeta KOA." + NL +
    "KOMUTACIJA — LOKACIJA NIJE PRIKLJUČENA NA ELEKTROENERGETSKU MREŽU: ne "
    "predviđa se mrežni sklopnik niti izbor izvora „mreža\"; komutacija se izvodi "
    "između hibridnog sistema napajanja i agregata. Start/stop DEA komanduje se "
    "iz Huawei kontrolno-upravljačkog sistema preko modula GIM01C1, po kriteriju "
    "stanja napunjenosti baterija (SoC), a NE po ispadu mrežnog napona. Izlaz "
    "agregata vodi se na AC ulazni modul AIU03 hibridnog sistema." + NL +
    " - OGRANIČENJE ULAZNE SNAGE ISPRAVLJAČA (OBAVEZNO): ograničava se u "
    "kontroleru na maks. 9,5 kW dok radi DEA. Ispravljači 3 × R4875G5 = 12 kW "
    "(cca 12,5 kW na AC strani) premašuju derativanu prime snagu agregata na "
    "lokaciji (11,6 kW pri 1076 m n.v. i 40 °C prema ISO 3046 / ISO 8528-1). "
    "Ponuđač dokazuje usklađenost proračunom deratinga za lokaciju." + NL +
    "KONTROLER I NADZOR: RS232, RS485, Ethernet (RJ45), USB; Modbus RTU, "
    "Modbus TCP, SNMP, SMS; integracija u krovni sistem nadzora BH Telecom-a "
    "(SCADA — Ignition) putem SNMP / Modbus TCP / Web REST API. Mjerenja: "
    "pritisak ulja, temperatura rashladnog sredstva, nivo goriva, napon i struja "
    "generatora po fazama, snaga, frekvencija, napon akumulatora, vrijeme rada "
    "motora. Alarmi: hitno zaustavljanje, nizak pritisak ulja, visoka/niska "
    "temperatura, pod/prekomjerna brzina, nizak/visok napon generatora i "
    "baterije, kvar alternatora, neuspješno pokretanje i zaustavljanje, NIZAK "
    "NIVO GORIVA, DETEKCIJA CURENJA GORIVA, POŽAR. Režimi rada: automatski, "
    "ručni, testni. Kao Deep Sea Electronics DSE 7420 MKII ili ekvivalent." + NL +
    "OSTALA OPREMA: start baterija 12 V / 70 Ah; punjač start baterije "
    "12 V / 5 A / 230 V, programabilni, sa dojavom kvara, uvezan sa kontrolerom."
)

NAP4 = (
    "OPŠTE NAPOMENE UZ TAČKU 4: DEA se ugrađuje u postojeći kontejner u „inside "
    "skid\" izvedbi (agregat na zajedničkom nosivom skid-okviru, bez vlastitog "
    "vanjskog kućišta — funkciju kućišta preuzima kontejner). Referentna izvedba "
    "data je u Prilogu III." + NL +
    "NOSIVOST PODA: podna konstrukcija je dimenzionisana na 10,00 kN/m² ukupnog "
    "(g+p) RAVNOMJERNO RASPODIJELJENOG opterećenja prema ovjerenom projektu "
    "lokacije („04 AG dio\", tačka 4.4.2.3). Agregat (372 kg mokro na 0,96 m² = "
    "3,80 kN/m²) i pun spremnik (≈590 kg na 0,63 m² = 9,2 kN/m²) ostaju unutar te "
    "vrijednosti, ali djeluju KONCENTRISANO na malom broju sekundarnih nosača, "
    "zbog čega je roštilj za raznošenje opterećenja iz Tačke 4.4 OBAVEZAN. "
    "Vrijednost 2,00 kN/m² iz istog projekta odnosi se samo na pokretno "
    "opterećenje prohodnog dijela poda i nije mjerodavna za oslanjanje opreme."
)

I41 = (
    "Isporuka i montaža automatskog DEA opisanog pod Tačkom 3.1 u postojeći "
    "kontejner, u skid izvedbi, na antivibracionim osloncima sa pripremom za "
    "pričvršćenje za podlogu. Stavka obuhvata i nabavnu vrijednost agregata iz "
    "Tačke 3.1." + NL +
    " - PRISTUP: unos kroz kapiju na sredini istočne strane ograde (svijetla "
    "širina cca 1,00 m) i ulazna vrata kontejnera 900 × 2000 mm; ponuđač bira "
    "način unosa i dužan je u ponudi potvrditi izvodljivost" + NL +
    " - SERVISNI PROSTOR (OBAVEZNO, prema crtežu M-01): agregat se postavlja "
    "CENTRIRANO u slobodnom prostoru kontejnera, sa najmanje 720 mm sa JUŽNE i "
    "720 mm sa SJEVERNE strane (520 mm na dijelu gdje je GRO) te 1155 mm sa "
    "ISTOČNE strane. Sa ZAPADNE strane je hladnjak, koji izduvava u kanal kroz "
    "zid i ne servisira se s te strane. Prolazi se ne smiju zauzimati opremom "
    "niti skladištenjem" + NL +
    " - dimenzije skida prilagoditi raspoloživom prostoru" + NL +
    " - dozvoljeni nivo buke izvan kontejnera <68 dBA pri opterećenju 75 % na "
    "7 m, režim Standby" + NL +
    " - taster EMERGENCY STOP uz ulazna vrata kontejnera"
)

I42 = (
    "Isporuka, montaža i povezivanje dvoplašnog spremnika dizel goriva zapremine "
    "500 l (0,5 m³), od čeličnog lima, sa svim spojnim priborom, cjevovodima i "
    "armaturama. Zapremina spremnika nije predmet varijantnih rješenja i ne "
    "umanjuje se ni u slučaju ojačanja poda iz Tačke 4.4." + NL +
    " - referentne dimenzije 1050 × 600 × 1310 mm, masa prazan 170 kg (pun "
    "≈590 kg); smještaj u JUGOISTOČNI ugao kontejnera, u koritu iz Tačke 4.3, "
    "prema crtežu M-01" + NL +
    " - odušna cijev izvedena IZVAN kontejnera, otvor zaštićen metalnom "
    "mrežicom; odzračni cjevovod od čeličnih bešavnih cijevi prema DIN 2448 sa "
    "odzračnim ventilom tip AT" + NL +
    " - priključak za punjenje sa zatvaračem, izveden na vanjskoj strani "
    "kontejnera; obezbijediti prilaz autocisterne, a na pretakalištu ugraditi "
    "uređaj za odvođenje statičkog elektriciteta" + NL +
    " - priključak za pražnjenje sa zatvaračem i priključkom za crijevo" + NL +
    " - DVA uređaja za mjerenje nivoa goriva koji rade nezavisno, sa različitim "
    "principom prikazivanja; nivo se prosljeđuje u nadzorni centar" + NL +
    " - sonda za detekciju curenja goriva u međuplaštu" + NL +
    " - pločica sa tehničkim podacima (proizvođač, tvornički broj, tip, godina, "
    "materijal, ispitni pritisak, zapremina)" + NL +
    " - napajanje motora gorivom kroz Cu cijevi NO 8 mm (polazni i povratni vod)" + NL +
    " - spremnik strukturno ojačan i zaštićen od krađe goriva"
)

I44 = (
    "OBAVEZAN statički proračun nosivosti podne konstrukcije postojećeg "
    "kontejnera, ovjeren od strane ovlaštenog inženjera, te izrada i ugradnja "
    "čeličnog roštilja/rama za RAZNOŠENJE OPTEREĆENJA ispod skida agregata I "
    "ispod korita sa spremnikom, sa prenosom opterećenja na primarne nosače "
    "podne konstrukcije, uključujući antikorozivnu zaštitu i sav spojni "
    "materijal. Sekundarni nosači su HOP 100×50×3 na razmaku 0,51 m. Ponuđač "
    "proračunom dokazuje raspodjelu i dimenzije rama. Zapremina spremnika se ne "
    "umanjuje."
)

I55 = (
    "Isporuka i polaganje veza na dionici hibridni sistem — DEA:" + NL +
    " - energetski kabl dužine do 15 m, tip NYY-J 5×6 mm²" + NL +
    " - signalni kabl dužine do 15 m, tip J-Y(ST)Y 4×2×0,6 mm²" + NL +
    " - komunikacioni Ethernet kabl dužine do 15 m, tip STP Cat5" + NL +
    "Kablovi se polažu uvlačenjem u PEHD cijevi/bužire i u metalne kanale, "
    "komplet sa montažnim materijalom, spajanjem na obje strane, bušenjem "
    "prodora na kontejneru, ugradnjom uvodnica i zaštitnog lima. Obavezna obrada "
    "svih prodora sa aspekta sigurnosti, toplinske izolacije (pur pjena, "
    "armaflex) i estetike."
)

I56 = (
    "Isporuka i montaža NOVOG GLAVNOG RAZVODNOG ORMARA (GRO) — AC RAZVODNA "
    "SEKCIJA, za ugradnju u postojeći kontejner. Ormar je zajednička AC razvodna "
    "kutija za agregat (DEA), ispravljački sistem (Huawei ICC360-HA1-C1 ili "
    "kompatibilan) i ostalu AC opremu kontejnera. DC/solarni razvod NIJE dio "
    "ovog ormara — DC rastavljač, osigurači nizova i DC odvodnik prenapona "
    "smješteni su u zasebnom PVDB ormaru koji obezbjeđuje Kupac, fizički "
    "odvojenom od GRO-a. Ormar zidni sa nosačima, orijentacionih dimenzija "
    "0,60 × 0,25 × 0,80 m (Š×D×V), mehaničke zaštite min. IP66, zabravljen "
    "bravom sa višestrukim zaključavanjem, kao Schrack ili ekvivalent. Sa donje "
    "strane obezbijediti prostor za uvod kablova sa PG uvodnicama, stezaljkama, "
    "elementima za uzemljenje i sabirnicama, komplet ožičeno, sa min. 30 % "
    "rezerve za naknadna proširenja." + NL +
    "AC RAZVOD — AGREGAT I ISPRAVLJAČI:" + NL +
    " - 1 kom 4p tropoložajna sklopka za odabir izvora, 1-0-2, 63 A, sa uvezanim "
    "statusom slobodnog kontakta sa kontrolerom agregata (DIG IN); položaje "
    "obilježiti: 1-„hibridni sistem\", 0-„isključeno\", 2-„agregat\"" + NL +
    " - 1 kom 3p dvopoložajna sklopka 0-1, 63 A, sa pomoćnim kontaktom za "
    "uvezivanje statusa sa kontrolerom agregata (DIG IN)" + NL +
    " - 3 kom 1p automatski prekidač, C, 32 A, 10 kA, za zaštitu napajanja preko "
    "DEA" + NL +
    " - 1 kom odvodnik prenapona AC, KOMBINOVANI TIP 1 + 2 prema EN 61643-11, "
    "Iimp ≥12,5 kA (10/350 µs) po polu, Up ≤1,5 kV, 4p, sa signalizacijom za "
    "daljinsko očitanje i uvezanim statusom sa kontrolerom agregata. Objekat ima "
    "vanjski sistem zaštite od munje (antenski stub h=38 m), pa odvodnik tipa 2 "
    "sam po sebi NIJE dovoljan prema EN 62305-4" + NL +
    " - 1 kom 4p zaštitna strujna sklopka (RCD) 63 A / 300 mA, S-tip "
    "(selektivna), za cjelokupni napojni krug iza sklopke izvora" + NL +
    " - 2 kom 1p+N RCBO 16 A / 30 mA, tip A, za utičnice i rasvjetu kontejnera" + NL +
    " - 1 kom 3p automatski prekidač, C, 32 A, 10 kA, za AC napajanje "
    "ispravljačkog sistema" + NL +
    " - 2 kom 1p automatski prekidač, C, 16 A, sa rezervom za ostalu AC opremu "
    "kontejnera i buduća proširenja" + NL +
    "NAPOMENA (OBAVEZNO) — ZAŠTITA OD INDIREKTNOG DODIRA: agregat je otočni izvor "
    "ograničene struje kvara. I sa traženom PMG/AREP pobudom trajna struja kvara "
    "je 3 × In ≈ 78 A, što ne obezbjeđuje trenutno isključenje prekidača "
    "karakteristike C 32 A, pa SAMO prekostrujna zaštita NE MOŽE ostvariti "
    "isključenje u vremenu prema IEC 60364-4-41 (0,4 s za 230 V). Zaštita "
    "zaštitnom strujnom sklopkom je stoga OBAVEZNA. Sistem uzemljenja je TN-S sa "
    "jedinstvenom tačkom spajanja N i PE u ovom ormaru; otpor uzemljenja ≤10 Ω." + NL +
    "Sve metalne mase ormara koje u normalnom radu nisu pod naponom povezati na "
    "sabirnice za izjednačenje potencijala. Uvodi kablova brtvljeni uvodnicama. "
    "Izraditi i pričvrstiti gravirane natpisne pločice: „GRO AC — "
    "AGREGAT/ISPRAVLJAČI — BS SJEDNICA\" i oznaku W012 „OPASAN NAPON\" prema "
    "EN ISO 7010."
)

I64 = (
    "Izrada dokumentacije izvedenog stanja za kompletan LOT 2 (elektro, mašinski "
    "i građevinski dio), u 3 štampana primjerka i u elektronskoj formi "
    "(PDF + izvorni DWG/DOCX)."
)



# --------------------------------------------------------------------------
def main():
    if not os.path.exists(XLSX):
        raise SystemExit(f"nema fajla: {XLSX}")
    bak = XLSX + ".bak"
    shutil.copy2(XLSX, bak)
    wb = openpyxl.load_workbook(XLSX)
    src = openpyxl.load_workbook(XLSX)          # netaknuta kopija
    l1, l2 = wb["LOT 1"], wb["LOT 2"]
    dead = {"LOT 1": set(), "LOT 2": set()}
    log = []

    # ---- LOT 2, sekcija 3: E1 + sažimanje -------------------------------
    r31 = absorb(l2, "1.1", DEA, 41, dead["LOT 2"])
    l2.cell(r31, 1).value = "3.1"                                    # E1
    for col in (3, 4, 5, 6):                                         # E4
        free_cell(l2, r31, col)
        l2.cell(r31, col).value = None
    hdr = item_row(l2, "3.1") - 1
    while not str(l2.cell(hdr, 2).value or "").startswith("AUTOMATSKI"):
        hdr -= 1
    l2.cell(hdr, 2).value = ("AUTOMATSKI DIZEL ELEKTRIČNI AGREGAT (DEA) — "
                             "TEHNIČKA SPECIFIKACIJA (bez cijene)")
    log.append(("LOT 2 3.1", "1.1 -> 3.1, 41 redova sažeto u jednu ćeliju",
                "Tačka 4.1 i Prilog I referenciraju „Tačku 3.1\""))

    # ---- E4: 3.2 seli u sekciju 4 kao 4.22 ------------------------------
    r32 = item_row(l2, "3.2")
    spare = str(l2.cell(r32, 2).value or "")
    spare_qty, spare_unit = l2.cell(r32, 4).value, l2.cell(r32, 3).value
    blank(l2, r32)
    dead["LOT 2"].add(r32)
    r_u3 = None
    for r in range(1, l2.max_row + 1):
        if str(l2.cell(r, 1).value or "").startswith("UKUPNO 3"):
            r_u3 = r
            break
    blank(l2, r_u3)
    dead["LOT 2"].add(r_u3)
    log.append(("LOT 2", "3.2 -> 4.22, UKUPNO 3 uklonjen",
                "3.1 i 4.1 su obje bile cjenovne; UKUPNO 3 je bio izvan zbira"))

    # ---- LOT 2, sekcija 4 -----------------------------------------------
    rn = item_row(l2, "4.1") - 1
    set_text(l2, rn, NAP4)                                           # E8
    absorb(l2, "4.1", I41, 4, dead["LOT 2"])
    absorb(l2, "4.2", I42, 10, dead["LOT 2"])
    sub_in(l2, "4.4", [(str(l2.cell(item_row(l2, "4.4"), 2).value), I44)])
    sub_in(l2, "4.17", [])
    l2.cell(item_row(l2, "4.17"), 3).value = "paušal"                # E6
    # E3 + E4 zajedno: prazna stavka 4.19 dobija sadržaj rezervnih dijelova iz
    # 3.2. Time se rješavaju obje greške bez ijednog umetanja reda - `insert_rows`
    # bi tražio još jedan remap formula, a upravo je to mjesto na kojem je Rev 7
    # tiho pokvario zbirove.
    r419 = item_row(l2, "4.19")
    set_text(l2, r419, spare)
    free_cell(l2, r419, 3)
    free_cell(l2, r419, 4)
    l2.cell(r419, 3).value = spare_unit
    l2.cell(r419, 4).value = spare_qty
    log.append(("LOT 2 4.19", "prazna stavka postaje set rezervnih dijelova (iz 3.2)",
                "prazan numerisani red poziva na pitanje na tenderu"))
    log.append(("LOT 2 4.4", "OBRAZLOŽENJE obrisano, 3,93 -> 3,80 kN/m², "
                "„tankvane\" -> „korita\"", "vrijednost je bila za P22-6"))

    # ---- LOT 2, sekcija 5 -----------------------------------------------
    absorb(l2, "5.5", I55, 4, dead["LOT 2"])
    absorb(l2, "5.6", I56, 12, dead["LOT 2"])                        # E9, E10
    sub_in(l2, "5.13", [
        ("u PVDB ormaru iz Tačke 1.6 ili u zasebnom kućištu",
         "u PVDB ormaru koji obezbjeđuje Kupac ili u zasebnom kućištu"),
        ("v. Tačku 1.1 i crtež E-01", "v. LOT 1, Tačka 1.1 i crtež E-01"),
    ])                                                               # E5
    log.append(("LOT 2 5.6", "12 redova sažeto; „Tačka 1.6 LOT-a 1\" uklonjena; "
                "napomena o zaštiti prepisana", "PVDB je u Huawei paketu; "
                "tender traži PMG/AREP, pa tvrdnja „agregat je SHUNT\" nije tačna"))

    # ---- E2: vratiti opis 6.4 -------------------------------------------
    set_text(l2, item_row(l2, "6.4"), I64)
    log.append(("LOT 2 6.4", "opis vraćen (167 znakova)",
                "izgubljen pri pokretanju fix_boq_lots.py"))

    # ---- LOT 1: E11, E12, E7 --------------------------------------------
    sub_in(l1, "1.1", [
        ("moment prevrtanja ≥62,8 kNm", "moment prevrtanja ≥42,6 kNm"),
        (" (v. Tačku 1.6a i crtež E-01)", " (v. crtež E-01)"),
        ("nosači se temelje IZVAN ograđenog platoa, 400 mm južno od kote ograde "
         "(raspoloživi pojas 1950 mm); gornja",
         "nosači se temelje IZVAN ograđenog platoa, južno od ograde, u pojasu "
         "širine cca 1950 mm; odmak od ograde ponuđač utvrđuje pri poziciranju "
         "nosača tako da ravan panela nigdje ne dodiruje ogradu; gornja"),
    ])
    sub_in(l1, "1.2", [
        ("sila po traci od momenta prevrtanja ≥39,3 kN pri razmaku traka "
         "1600 mm (v. proračun F.6)",
         "sila po traci od momenta prevrtanja ≥26,6 kN pri razmaku traka 1600 mm"),
    ])
    log.append(("LOT 1", "62,8 -> 42,6 kNm, 39,3 -> 26,6 kN/traci, "
                "Tačka 1.6a i odmak 400 mm uklonjeni",
                "donja ivica panela spuštena na +0,50 m (Rev 7c)"))
    for r in range(1, l1.max_row + 1):                               # E7
        if r > 11 and not any(str(l1.cell(r, c).value or "").strip()
                              for c in range(1, 7)):
            if any(str(l1.cell(x, 1).value or "").strip().startswith("UKUPNO")
                   for x in range(r + 1, min(r + 4, l1.max_row + 1))):
                continue                       # prazan red ispred zbira ostaje
            dead["LOT 1"].add(r)

    # ---- brisanje praznih redova + remap formula ------------------------
    maps = {}
    for name in ("LOT 1", "LOT 2"):
        ws, rows = wb[name], sorted(dead[name])
        rowmap = {}
        for r in range(1, src[name].max_row + 1):
            rowmap[r] = None if r in dead[name] else r - sum(1 for d in rows if d < r)
        maps[name] = rowmap
        for r in reversed(rows):
            for rng in list(ws.merged_cells.ranges):
                if rng.min_row <= r <= rng.max_row:
                    ws.unmerge_cells(str(rng))
            ws.delete_rows(r)
        remap_formulas(ws, src[name], rowmap)
        extend_section_sums(ws)
        log.append((name, f"{len(rows)} praznih redova obrisano",
                    "formule remapirane iz netaknute kopije"))

    # `remap_formulas` namjerno ne dira reference sa imenom lista - REF ima
    # lookbehind na „!" - pa se ='LOT 1'!F50 mora prevesti RUČNO, kroz rowmap
    # DRUGOG lista. Bez ovoga rekapitulacija pokazuje na prazan red i ukupna
    # cijena ponude tiho pada na vrijednost samo LOT-a 2.
    for r in range(1, wb["LOT 2"].max_row + 1):
        f = wb["LOT 2"].cell(r, 6).value
        if isinstance(f, str) and "'LOT 1'!F" in f:
            old = int(f.split("'LOT 1'!F")[1].split()[0].strip("+-*/() "))
            new = maps["LOT 1"].get(old)
            if new is None:
                raise SystemExit(f"rekapitulacija pokazuje na obrisani red {old}")
            wb["LOT 2"].cell(r, 6).value = f.replace(f"'LOT 1'!F{old}",
                                                     f"'LOT 1'!F{new}")
            log.append(("LOT 2 rekapitulacija", f"'LOT 1'!F{old} -> F{new}",
                        "referenca na drugi list se ne remapira automatski"))

    # 3.1 je specifikacija bez cijene; remap joj je vratio formulu iz kopije
    r31 = item_row(l2, "3.1")
    for col in (3, 4, 5, 6):
        free_cell(l2, r31, col)
        l2.cell(r31, col).value = None

    # ---- provjere --------------------------------------------------------
    text = ""
    for name in ("LOT 1", "LOT 2"):
        # kolona 3 je u opsegu jer je „paušal" jedinica, ne dio opisa
        for row in wb[name].iter_rows(min_col=1, max_col=3):
            for c in row:
                if isinstance(c.value, str):
                    text += c.value + "\n"
    missing = [t for t in COVERAGE if t not in text]
    if missing:
        raise SystemExit("COVERAGE: nedostaju obavezni tokeni:\n  " +
                         "\n  ".join(missing))

    assert_no_loss(wb, src, deliberate={
        "1.1", "1.2", "3.2", "4.1", "4.2", "4.4", "4.19", "5.5", "5.6", "6.4"})

    wb.save(XLSX)
    os.remove(bak)
    for where, what, why in log:
        print(f"  {where:<12} {what}")
        print(f"  {'':<12}   -> {why}")
    for name in ("LOT 1", "LOT 2"):
        print(f"\n{name}: {src[name].max_row} -> {wb[name].max_row} redova")


if __name__ == "__main__":
    main()
