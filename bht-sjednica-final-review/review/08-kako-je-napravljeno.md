# Kako je napravljena tenderska dokumentacija za BS Sjednica

*Bilješka za Aidu i Naidu — šta je ovaj projekat, čime je rađen, i koliko bi trebalo
napraviti isto za drugu lokaciju.*

Rusmir Skopljak · 12.08.2026.

---

## 1. Šta je ovo

Tenderska dokumentacija za **autonomni hibridni sistem napajanja bazne stanice
Sjednica (Bileća)** — fotonaponsko polje sa nosačima i dizel agregat u postojećem
kontejneru, na planinskom vrhu na **1076 m n.v.** koji **nije priključen na
elektroenergetsku mrežu**.

Cijeli paket — tekst, predmjer, proračuni i crteži — **generiše se iz koda i podataka**,
a ne kuca ručno u Wordu i ne crta ručno u AutoCAD-u. To je jedina stvarno bitna
osobina ovog projekta i sve ostalo iz nje slijedi.

Isporuka je 9 fajlova u `TD-OUTPUT/`:

| Fajl | Šta je | Kako nastaje |
|---|---|---|
| `1. NZ …docx` | nacrt zahtjeva | ručno, sitne ispravke skriptom |
| `2. TD JN …docx` | tenderska dokumentacija | ručno + hirurške izmjene u OOXML-u |
| `2.1 Prijedlog Odluke …docx` | prijedlog odluke | ručno + skripta |
| `3. Prilog I …docx` | **specifikacija zahtjeva** | **generisan** iz `review/prilog1.md` |
| `3.1 PRILOG II …xlsx` | **predmjer i predračun** | **generisan/održavan** skriptama |
| `3.2 Prilog III …pdf` | grafički prilozi | **generisan** iz crteža |
| `4. Izjava …docx` | izjava o zalihama | ručno |
| `grafika/` | **S-01, S-02, S-03, M-01, E-01** | **generisani** DXF → DWG → PDF |
| `proracuni_sjednica.pdf` | proračuni | render `review/07-proracuni.md` |

---

## 2. Struktura repozitorija

```
bht-sjednica-final-review/
│
├── SITE-PROJECT-SJEDNICA-Bileca-K2-S38-m/   ULAZ: ovjereni projekat lokacije
│   ├── 2 - ARHITEKTONSKO GRADJEVINSKI DIO/  (DWG: temelji, ograda, fasade)
│   ├── 3_ELEKTRO INSTALACIJE/
│   └── 4_MASINSKE INSTALACIJE/
│
├── EQUIPEMENT/                              ULAZ: dokumentacija opreme
│   ├── GENSET/    FG Wilson tehnički listovi, DWG-ovi agregata i spremnika
│   ├── CABINETS/  Huawei ICC360-HA1-C1, MTS9302A, iSSU, ponuda dobavljača
│   └── PV/        Huawei moduli i optimizatori
│
├── TD-EXAMPLES-TEMPLATES/                   ULAZ: raniji tenderi kao predložak
│
├── cad/                    ★ IZVOR CRTEŽA
│   ├── design.json           sve izvedene vrijednosti projekta (JEDAN izvor istine)
│   ├── site_geometry.json    geometrija izmjerena iz ovjerenog DWG-a lokacije
│   ├── bht_frame.py          A3 okvir, sastavnica, slojevi, stilovi kota
│   ├── build_drawings.py     list S-01 + zajedničke funkcije crtanja
│   ├── sheets_new.py         listovi S-02, S-03, M-01, E-01
│   ├── export.py             DXF → DWG (AC1024) → PDF, sa verifikacijom
│   └── render.py             brzi PNG pregled lista
│
├── tools/                  ★ IZVOR DOKUMENATA
│   ├── ooxml_edit.py         hirurška izmjena teksta unutar .docx
│   ├── build_prilog1.py      prilog1.md → Pandoc → Prilog I .docx
│   ├── build_prilog3.py      sastavlja Prilog III iz dijelova
│   ├── compact_boq.py        sažimanje predmjera + COVERAGE zaštita
│   ├── fix_boq_quantities.py ispravke količina (Rev 8)
│   ├── check_consistency.py  ★ PROVJERA CIJELOG PAKETA
│   └── (fix_boq*.py, fix_td*.py — jednokratne skripte po revizijama)
│
├── review/                 ★ ZAPIS I IZVORNI TEKSTOVI
│   ├── 00-change-log.md      historija svake izmjene i ZAŠTO (26 sekcija)
│   ├── 01…06-*.md            pregledi po disciplinama
│   ├── 07-proracuni.md       objedinjeni proračuni (bosanski, aktuelno stanje)
│   ├── prilog1.md            IZVOR Priloga I
│   └── backup-rev7/          sigurnosne kopije prije zadnje revizije
│
└── TD-OUTPUT/              ★ ISPORUKA
```

Zlatno pravilo: **`TD-OUTPUT/` se ne uređuje ručno.** Sve što je tamo ili je
generisano iz `cad/` i `review/`, ili je mijenjano skriptom iz `tools/`. Ako neko
otvori Prilog I u Wordu i sačuva, sljedeći build to pregazi.

---

## 3. Lanac — kako od podatka nastaje isporuka

```
             ovjereni projekat lokacije (DWG)
                          │
                  ručno očitavanje kota
                          ▼
              cad/site_geometry.json  ──┐
                                        ├──►  cad/design.json  ◄── tehnički listovi
              proračuni (07-proracuni)──┘        (jedan izvor istine)      opreme
                                                       │
        ┌──────────────────────────────────────────────┼───────────────────┐
        ▼                                              ▼                   ▼
   crteži (ezdxf)                          Prilog I (Pandoc)        predmjer (openpyxl)
   S-01 S-02 S-03 M-01 E-01                prilog1.md → .docx       Prilog II .xlsx
        │                                              │                   │
   DWG + A3 PDF (ODA)                                  │                   │
        │                                              │                   │
        └──────────────► Prilog III (PyMuPDF) ◄────────┘                   │
                                    │                                      │
                                    └──────────►  check_consistency.py  ◄──┘
                                                  (čita SVE i traži svađe)
```

**Ključna ideja:** ako se jedna vrijednost promijeni — recimo agregat sa 22 kVA na
18 kVA — ona se mijenja **na jednom mjestu** (`design.json`), a onda se crteži
regenerišu, tekstovi isprave skriptom, i `check_consistency.py` kaže da li je iko
ostao sa starom brojkom. Bez toga je nemoguće držati 9 dokumenata usklađenim kroz
osam revizija.

---

## 4. Čime je rađeno

### Python biblioteke

| Biblioteka | Za šta |
|---|---|
| **ezdxf** | crtanje DXF-a iz koda — svih 5 listova, okvir, kote, šrafure, sastavnica |
| **openpyxl** | čitanje i pisanje predmjera `.xlsx`, uz formule |
| **PyMuPDF (fitz)** | sastavljanje i mjerenje PDF-ova (Prilog III), render stranica |
| **zipfile + re** | `.docx` je zip sa XML-om — tekst se mijenja hirurški, bez regenerisanja |
| **matplotlib** | ezdxf backend za A3 PDF izlaz crteža |
| **Pillow** | obrada slika opreme |

### Vanjski alati

| Alat | Za šta |
|---|---|
| **ODA File Converter** | DXF → **DWG AC1024** (format koji traži projektant) i nazad radi provjere |
| **Pandoc 3.10** | `prilog1.md` → `.docx` sa referentnim stilom |
| **LibreOffice (headless)** | prerachun predmjera i render `.docx` → PDF radi vizuelne kontrole |

### Claude Code

Radio sam sa **Claude Code (Opus 5)** u terminalu. Konkretno je koristio:

- **čitanje/pisanje/izmjena fajlova** i **Bash/PowerShell** za pokretanje skripti
- **plan mode** — prije većih zahvata Claude napiše plan, ja ga odobrim ili
  izmijenim prije nego išta dirne
- **pitanja sa ponuđenim opcijama** kad je odluka moja, a ne njegova (npr. „Prilog I
  kao DOCX preko Pandoc-a ili kao PDF?")
- **memoriju projekta** — bilješke koje preživljavaju između sesija

Ono što **nije** korišteno, da ne bude zabune: nisu korišteni MCP serveri (postoji
`dwg-tools` MCP, ali konverziju radi ODA direktno iz `export.py`), niti browser
automatizacija, niti podagenti. Sve je obični Python + pozivi vanjskih alata.

### Zašto toliko provjera

`check_consistency.py` čita **svaki dokument u njegovom izvornom formatu** — OOXML iz
`.docx` zipa, `openpyxl` za `.xlsx`, PyMuPDF za PDF, ezdxf za DXF — i onda pita:

- **KONFLIKTI:** smije postojati samo jedna varijanta vrijednosti u cijelom paketu.
  Ako se negdje pojavi „22 kVA" a negdje „18 kVA", to je greška. Trenutno 18 pravila.
- **OBAVEZNE VRIJEDNOSTI:** stvari koje MORAJU postojati (procijenjena vrijednost,
  ograničenje ispravljača 9,5 kW, tip SPD-a…). Trenutno 14.
- **ZABRANJENI TEKST:** ostaci iz predloška ranijeg tendera („vučna prikolica",
  „najmanje dvije lokacije") koji nemaju veze sa ovim poslom.

Uz to, predmjer ima **`COVERAGE` listu od 76 tehničkih zahtjeva** koji ne smiju
nestati pri sažimanju teksta, i **prerachun kroz LibreOffice** sa 100 KM po stavci —
tako se provjerava da se svi zbirovi slažu.

> **Zašto je to bilo neophodno.** U zadnjoj reviziji te provjere su otkrile tri
> stvari koje su tiho stajale u paketu: ograničenje snage ispravljača od 9,5 kW nije
> postojalo nigdje u predmjeru; prihvatno korito ispod spremnika dvije stavke
> spominju a nijedna ne isporučuje; a stavka 6.4 imala je formulu bez jedinice i
> količine, pa je dokumentacija izvedenog stanja za cijeli LOT 2 ispadala iz zbira.
> Nijednu od te tri nije moguće uočiti čitanjem.

---

## 5. Šta sam ja radio, a šta Claude

Ovo nije bilo „napiši mi tender". Podjela je bila prilično jasna:

**Ja (Investitor / projektant):**

- **Ulazni podaci i njihova vjerodostojnost** — ovjereni projekat lokacije, tehnički
  listovi FG Wilson agregata i spremnika, Huawei ponuda i priručnici. Visina ograde
  2,10 m i visine kontejnera 2,63/2,89 m su očitane sa **ovjerenih** crteža, a ne
  pretpostavljene.
- **Sve inženjerske odluke:** 18 kVA umjesto 22 ili 13,5; donja ivica panela na
  +0,50 m; dvoplašni spremnik umjesto tankvane od 110 %; podjela na dva LOT-a;
  servisni prostor oko agregata umjesto zida.
- **Znanje o lokaciji koje nije ni u jednom dokumentu** — da se snijeg na tom vrhu ne
  zadržava jer ga bura raznosi, ali da je **led** stvarni problem. To je promijenilo
  cijeli konstruktivni zaključak.
- **Kontrola renderā.** Svaki list sam pregledao i vraćao: agregat nije centriran,
  MTS9302 je nestao sa tlocrta, izlazna žaluzina nije na osi hladnjaka.
- **Osporavanje brojki.** Zadnja revizija je krenula od moje sumnje da je 6 m²
  limenog kanala previše — i bila je. Ja sam dao i **specifikaciju za salu „POTOCI"
  Mostar**, iz koje je ta brojka naslijeđena, što je i omogućilo da se pokaže odakle
  greška potiče.

**Claude:**

- napisao i održavao sav kod — crteži, generatori dokumenata, provjere
- izvodio proračune (derating, ventilacija, izduv, vjetar, temelji, struje kvara)
- uočio i ispravio greške u naslijeđenom predmjeru i Prilogu I
- vodio `00-change-log.md` — zapis **zašto** je nešto promijenjeno, ne samo šta

Najkorisnije je bilo tamo gdje se dvije stvari ukrštaju: ja kažem „6 m² mi djeluje
puno", Claude izračuna da je hladnjak 60 mm od zida pa kanal ne može biti veći od
1 m², i onda još nađe da ista brojka stoji i kod izolacije izduva gdje bi tražila
12 m cijevi.

---

## 6. HAMZIĆI (Čapljina) — koliko bi trebalo

Kratak odgovor: **infrastruktura se prenosi gotovo besplatno, ali ulazni podaci i
zaključci se moraju izvesti iznova.** Nije „isto sa malim izmjenama" — i to je dobra
vijest, jer je nekoliko stvari na Hamzićima vjerovatno **jednostavnije**.

### Šta se prenosi bez posla

Sav alat: `bht_frame.py`, funkcije crtanja, `export.py`, `ooxml_edit.py`,
`build_prilog1.py`, `check_consistency.py`, struktura predmjera, struktura Priloga I,
struktura proračuna. To je najveći dio uloženog rada i on je **već plaćen**.

Praktično: `design.json` i `site_geometry.json` se popune novim vrijednostima,
`prilog1.md` se uredi kao tekst, i dokumenti izađu.

### Šta se mora izvesti iznova

| Ulaz | Zašto |
|---|---|
| **Ovjereni projekat lokacije Hamzići** (DWG) | bez njega nema S-01 — parcela, ograda, ploča, baza stuba, postojeći uzemljivač |
| **Nadmorska visina i temperature** | Čapljina je nizinska i vrlo topla; **visinski derating praktično nestaje, a temperaturni raste** |
| **Zona vjetra i snijega** | Sjednica je izložen vrh sa qp ≥ 1,20 kN/m²; Hamzići gotovo sigurno nisu |
| **Bilans potrošnje bazne stanice** | određuje sve ostalo |

Tri zaključka sa Sjednice vjerovatno **padaju** na Hamzićima, i to u našu korist:

1. **Nosač možda više ne mora biti custom izrada.** Cijeli argument na Sjednici je
   bio da nijedan kataloški nagib ne podnosi 1,20 kN/m². Pri nižem pritisku vjetra
   kataloški nosač prolazi → **LOT 1 postaje kupovina, ne projektovanje.** To je
   najveća ušteda.
2. **Klasa izloženosti betona XF3** je tražena zbog ciklusa smrzavanja na 1076 m.
   U Čapljini vjerovatno nije mjerodavna.
3. **Ograničenje ispravljača na 9,5 kW** postoji jer derating na 1076 m obara prime
   snagu na 11,6 kW. Bez visinskog deratinga granica se pomjera — ali **pažljivo**,
   jer temperaturni derating u Čapljini radi u suprotnom smjeru i mora se preračunati,
   ne pretpostaviti.

### Agregat VANI — to nije mala izmjena

Ovo je zapravo najveća stavka i vrijedi je iskreno prikazati, jer mijenja **skoro
cijelu sekciju 4 predmjera**:

**Ispada:** ventilacione žaluzine, limeni kanal, ventilator prostora, fleksibilni
spoj hladnjaka, statički proračun poda kontejnera i čelični roštilj za raznošenje
opterećenja, prihvatno korito, protupožarni elaborat za prostoriju sa 500 l goriva.
To je oko osam stavki.

**Ulazi:** vremenski otporno i **zvučno izolovano kućište** (agregat vani, pa buka na
granici parcele postaje mjerodavan zahtjev, a ne usputna napomena), **betonski temelj
/ postolje** sa svojim iskopom i armaturom, **spremnik goriva u nosivom ramu** sa
integrisanom tankvanom umjesto zasebnog spremnika u kontejneru, kablovska trasa od
kućišta do kontejnera, i **zaštita od krađe i vandalizma**.

**Crteži:** S-01 (situacija) se radi iznova iz novog projekta lokacije. **M-01 i S-02
se ne uređuju — oni se zamjenjuju**, jer prikazuju unutrašnjost kontejnera koje više
nema. Umjesto njih ide dispozicija kućišta sa temeljom i presjek.

> Ovdje treba biti realan: `sheets_new.py` ima oko 430 tvrdo upisanih koordinata
> prema 57 čitanja iz `design.json`. Crteži **nisu** parametrizovan šablon — oni su
> kod pisan za ovu lokaciju. Tekstualni dio jeste blizu šablona, crteži nisu.

### Procjena

| Faza | Procjena |
|---|---|
| `design.json` + `site_geometry.json` za Hamziće | 2–3 h, uz dostupan projekat lokacije |
| Proračuni (derating, vjetar, ventilacija kućišta, izduv) | 3–4 h |
| Prilog I, TD, Odluka, NZ | 2–3 h (tekst, struktura ostaje) |
| Predmjer — prekrajanje sekcije 4 na vanjsku izvedbu | 4–5 h |
| Crteži: S-01 nova situacija, nova dispozicija kućišta | 6–8 h |
| Provjere, revizija, ispravke | 3–4 h |
| **Ukupno** | **≈3 radna dana**, uz spremne ulazne podatke |

Za poređenje, Sjednica je trajala **osam revizija** i znatno duže — jer se tada
gradio i sav alat.

**Šta blokira početak:** ovjereni projekat lokacije Hamzići u DWG-u, bilans potrošnje
bazne stanice, i potvrda zone vjetra/snijega. Bez prvog se ne može nacrtati situacija;
bez druga dva se ne može dimenzionisati ništa.

**Prijedlog:** krenuti od `design.json` za Hamziće i pustiti `check_consistency.py`
odmah — on će sam prijaviti svaku vrijednost sa Sjednice koja je ostala u tekstu.

---

*Sve tehničke vrijednosti u ovom dokumentu izvedene su iz `cad/design.json` i
`review/07-proracuni.md`. Historija svake izmjene je u `review/00-change-log.md`.*
