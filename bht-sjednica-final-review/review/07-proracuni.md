# Objedinjeni proračuni — BS Sjednica (Bileća)

**Verzija:** Rev 8, 12.08.2026.
**Status:** radni proračun Naručioca uz tendersku dokumentaciju. **Nije zamjena za
ovjereni statički i mašinski proračun** koji dostavlja ponuđač — ovdje su izvedene
vrijednosti koje tenderska dokumentacija propisuje kao ulazne i granične.

**Lokacija:** φ = 42,9448° N, λ = 18,3236° E, **1076 m n.v.**, zakupljena parcela
≈150 m², postojeći kontejner K2 3005 × 2300 mm, antenski stub h = 38 m.

---

## A. Ambijentalni uslovi

### A.1 Gustoća zraka u funkciji visine i temperature

Barometarski: `p = 101325·(1 − 2,25577·10⁻⁵·h)^5,25588`, zatim `ρ = p / (287,05·T)`.

| Stanje | p | ρ |
|---|---|---|
| 0 m, +25 °C (referenca tehničkog lista) | 101,3 kPa | **1,184 kg/m³** |
| 1076 m, +25 °C | 89,0 kPa | **1,040 kg/m³** |
| 1076 m, −10 °C | 89,0 kPa | 1,179 kg/m³ |
| 1076 m, +40 °C | 89,0 kPa | 0,991 kg/m³ |
| 1076 m, za proračun vjetra (ovjereni projekat) | — | 1,0904 kg/m³ |

**Mjerodavno za:** derating hlađenja agregata (A.2), pritisak vjetra (B.1), gustoću
izduvnih gasova (C.4).

### A.2 Derating agregata na 1076 m

Prema ISO 3046-1 / ISO 8528-1, orijentaciono −1 % snage na svakih 100 m iznad 100 m,
uz dodatnih ≈−3 % za ambijent +40 °C u odnosu na referentnih +25 °C. Ukupni faktor
**0,875**:

| | tehnički list (25 °C, 100 m) | **na lokaciji (1076 m, 40 °C)** |
|---|---|---|
| Standby | 18 kVA / 14,4 kW | **15,8 kVA / 12,6 kW** |
| Prime | 16,5 kVA / 13,2 kW | **14,4 kVA / 11,6 kW** |

Protok zraka hladnjaka raste obrnuto sa gustoćom: `1980 × 1,184/1,090 ≈ 2151 m³/h`.
Ta vrijednost se koristi kao mjerodavni protok u C.1.

**Ponuđač je dužan dostaviti derating proizvođača za tačne uslove lokacije** — ovo je
tenderski zahtjev, ne pretpostavka.

### A.3 Snijeg i led

Koeficijent oblika pri nagibu 45°: **μ₁ = 0,4** prema EN 1991-1-3 §5.3.6 (linearno od
0,8 pri 30° do 0 pri 60°).

Najveća visina snijega opažena na lokaciji je **≈0,5 m**. Pri gustoći slegnutog
snijega 300 kg/m³ to je ≈1,5 kN/m² na tlu, odnosno na ravan panela:

```
s = μ₁ · Ce · Ct · sk = 0,4 · 1,0 · 1,0 · 1,5  ≈  0,6 kN/m²
```

**Mjerodavan je vjetar** — 1,20 kN/m² je dvostruko više. Pri 45° i donjoj ivici na
+0,50 m snijeg se na ravni panela ne zadržava, a izložen vrh u pojasu bure sa udarima
45 m/s ga raznosi. Snijeg pritom djeluje naniže i **umanjuje** mjerodavni uzgon iz
B.5, pa nije ni u jednoj kombinaciji nepovoljan.

**Led je druga stvar.** Naledica se na ovoj koti stvara i zadržava tamo gdje se snijeg
ne zadržava. Zahtjev ostaje **radijalni led 20 mm gustine 300 kg/m³** (Prilog I §1.1,
predmjer 1.3) — mjerodavan je kao akrecija na profile, spojeve i kablove, a ne kao
opterećenje ravni panela.

Provjera snijega prema **BAS EN 1991-1-3 sa BiH nacionalnim aneksom** svejedno mora
postojati u ovjerenom proračunu ponuđača.

### A.4 Ciklusi smrzavanja

Na 1076 m temeljne trake su izložene ciklusima smrzavanja i odmrzavanja uz prisustvo
vode, pa uz klasu čvrstoće mora biti propisana i klasa izloženosti. Usvojeno:
**C30/37, XC4 + XF3, aerant 4–6 %**, na podlozi C12/15, armatura **B500B**, zaštitni
sloj **50 mm**, dubina temeljenja **900 mm**.

### A.5 Geometrija Sunca i decembarski prihvat

Visina Sunca u podne `= 90 − φ + δ`, φ = 42,9448°.

| Datum | δ | Visina u podne | Nagib za normalnu upadnost |
|---|---|---|---|
| 21.12. | −23,44° | **23,6°** | 66,4° |
| 21.03. / 21.09. | 0° | 47,1° | 42,9° |
| 21.06. | +23,44° | 70,5° | 19,5° |

Udio direktnog zračenja prihvaćen u podne 21. decembra, `cos(|h − (90 − nagib)|)`:

| Nagib | Upadni ugao | cos | Prihvat u decembru |
|---|---|---|---|
| 15° | 51,4° | 0,624 | 62 % |
| 25° | 41,4° | 0,750 | 75 % |
| 35° | 31,4° | 0,854 | 85 % |
| **45° (usvojeno)** | **21,4°** | **0,931** | **93 %** |
| 55° | 11,4° | 0,980 | 98 % |

**Zaključak.** Zimski optimum ovdje je ≈ φ + 10…15 = **53–58°**, dakle 45° je već
*ispod* decembarskog optimuma. Spuštanje na 35° košta oko 8 % decembarskog prinosa na
lokaciji kojoj je **decembar deficitarni mjesec**. Godišnja brojka nije mjerodavna za
dimenzionisanje otočnog sistema — najgori mjesec jeste. **Usvojeni nagib: 45°.**

### A.6 Prinos i decembarski deficit

| | |
|---|---|
| Ozračenje u ravni panela, 45° jug | 1800–1930 kWh/m²·god |
| Polje | 12 × 585 Wp = **7,02 kWp** |
| Usvojeni performance ratio | 0,80 |
| **Godišnji prinos** | **10,1–10,9 MWh** |
| **Decembarski prinos** | **560–600 kWh** |
| **Decembarska potrošnja** | 1,180 kW × 24 × 31 = **878 kWh** |
| **Decembarski deficit** | **280–320 kWh (32–36 %)** |
| Rad agregata | ≈1,2–2,1 MWh/god → **110–190 h/god**, unutar predviđenih 250 h/god |

**Agregat je konstrukcijski neophodan, a ne formalnost**, i decembar je ono što
određuje njegov režim rada.

---

## B. Konstrukcija — nosači FN panela

### B.1 Proračunski pritisak vjetra

Osnovni udar 3 s ≈ **45 m/s**, ρ = 1,0904 kg/m³:

```
qp = 0,5 · 1,0904 · 45²  ≈  1,10 kN/m²   →  usvojeno qp ≥ 1,20 kN/m²
```

### B.2 Kataloški nosači i opterećenje lokacije

Kataloški nosači tipa A deklarisani su na sljedeće udare, odnosno pritiske:

| Nagib | Deklarisani udar | Deklarisani qp | vs. lokacija 1,20 kN/m² |
|---|---|---|---|
| 15° | 40 m/s | 0,87 kN/m² | **ne zadovoljava** |
| 25° | 40 m/s | 0,87 kN/m² | **ne zadovoljava** |
| 35° | 35 m/s | 0,67 kN/m² | **ne zadovoljava** |
| 45° | 31 m/s | 0,52 kN/m² | **ne zadovoljava** |

**Zaključak:** nijedan kataloški nagib nije usklađen sa lokacijom. Nosač je zato
**CUSTOM IZRADA**, a tender traži **ovjereni statički proračun za lokaciju prije
dodjele ugovora**. Kataloške konvencije (marže, prepusti) zadržane su samo kao
geometrijska referenca.

### B.3 Geometrija polja

| | |
|---|---|
| Modul | Huawei iPV585-M2A, **2278 × 1134 × 30 mm, 32,0 kg** |
| Raspored | **2 reda × 2 kolone, portret** — 4 modula po nosaču |
| Širina polja | **2305 mm** |
| Dužina polja po nagibu | **4576 mm** (2 × 2278) |
| Horizontalna projekcija pri 45° | **3236 mm** |
| Broj nosača | **3** (PV-1, PV-2, PV-3) → ukupno **12 modula = 7,02 kWp** |
| Masa nosača (procjena) | ≈110 kg — potvrđuje izrađivač proračunom |

### B.4 Visinski položaj polja

| | |
|---|---|
| **Donja ivica** | **+0,50 m** od nivoa terena |
| **Gornja ivica** | **+3,74 m** (0,50 + 3,236) |
| Kota ograde | +2,10 m (ovjereni projekat, `04 Ograda`) |
| **Nadvišenje ograde** | **1,64 m** |

> **Otvoreno pitanje.** Pri 45° ravan panela presijeca kotu ograde na **1600 mm** od
> donje ivice. **Odmak polja od ograde mora se utvrditi pri poziciranju nosača**, tako
> da ravan panela nigdje ne dodiruje ogradu, a konstrukcija u cijelosti ostane unutar
> zakupljene parcele 16,00 × 9,40 m.

### B.5 Dejstva vjetra po nosaču pri 45°

| | |
|---|---|
| Površina izložena vjetru | **10,55 m²** (2305 × 4576 mm) |
| Krak težišta iznad terena | **2,118 m** |
| **ULS uzgon** | **18,1 kN** — ne zavisi od visine |
| **Horizontalna sila** | **13,4 kN** |
| **Moment prevrtanja** | **42,6 kNm** |
| **Spreg po traci**, razmak 1600 mm | **26,6 kN** |

Krak težišta: `c = b + (4,576/2)·sin45° = b + 1,618 m`.
Moment: `M = 1,5 · F_h · c`, uz `F_h = 13,4 kN`.

**Mjerodavni su uzgon i prevrtanje, a ne nosivost tla.**

### B.6 Temelji

| | |
|---|---|
| Broj nosača | 3 |
| Traka po nosaču | 2 → **ukupno 6 traka** |
| Dimenzija trake | **450 (gore) / 550 (dolje) × 3300 mm**, **puna dubina 900 mm** |
| **Zapremina trake** | **1,485 m³** → ukupno **8,91 m³** C30/37 |
| Razmak traka (poprečno) | **1600 mm** |
| Razmak grupa ankera | 1200 mm |
| Beton | **C30/37 (XC4 + XF3, aerant 4–6 %)** na podlozi C12/15 |
| Armatura | **B500B**, zaštitni sloj 50 mm |
| Ankeri | **M16–M20 hemijski (rezinski)**, za kraški vapnenac — nije kataloški dio |

**Zašto traka ide punom dubinom.** Spreg iz B.5 daje **26,6 kN** uzgona na navjetrenu
traku. Uz `γG,stb = 0,9` stabilizujuća težina mora biti ≥29,6 kN:

```
puna traka   1,485 m³ × 24 kN/m³ × 0,9  =  32,1 kN     ZADOVOLJAVA
```

Traka manje zapremine ne zatvara ovu provjeru vlastitom težinom i morala bi je
posuditi od trenja o zasip, što na kršu nije dokaz. Ankeri prenose uzgon u traku, ne
u tlo, pa tu razliku ne pokrivaju.

Izvedene količine (predmjer LOT 1, sekcija 2), po traci i ukupno za 6 traka:

| | po traci | ukupno |
|---|---|---|
| Iskop (širina 550, dubina 950 mm) | 1,725 m³ | **10,35 m³** |
| Podložni beton C12/15, d = 50 mm | 0,091 m³ | **0,54 m³** |
| Beton C30/37 | 1,485 m³ | **8,91 m³** |
| Zatrpavanje (klin uz kosinu) | 0,149 m³ | **0,89 m³** |
| Odvoz viška | — | **9,45 m³** |

Dubina i armatura se **potvrđuju ovjerenim proračunom ponuđača** za qp ≥ 1,20 kN/m².
Temelji se izvode **IZVAN ograđenog platoa**.

### B.7 Pod kontejnera i unos opreme

| | |
|---|---|
| Nosivost poda (g+p, ravnomjerno) | **10,00 kN/m²** — ovjereni projekat, „04 AG dio" 4.4.2.3 |
| Agregat mokro | 372 kg / 0,96 m² = **3,80 kN/m²** |
| Pun spremnik 500 l | 590 kg / 0,63 m² = **9,2 kN/m²** |
| Ukupna masa u kontejneru | **962 kg** |

Obje vrijednosti su ispod 10,00 kN/m², ali su **koncentrisana opterećenja na malom
broju sekundarnih nosača**, dok se 10,00 kN/m² odnosi na ravnomjerno raspodijeljeno
opterećenje. Zbog toga je **čelični roštilj za raznošenje opterećenja OBAVEZAN** —
ispod skida **i** ispod korita — sa prenosom na primarne nosače.

Vrijednost **2,00 kN/m²** iz istog projekta je pokretno opterećenje prohodnog dijela
poda i **nije mjerodavna** za oslanjanje opreme.

**Unos:** skid širine **620 mm** kroz vrata **900 × 2000 mm** — ostaje 280 mm zazora;
visina skida 1020 mm. **Nije potrebno skidati krovni panel ni otvarati zid.**

---

## C. Mašinski dio — agregat

Referentni agregat: **FG Wilson P18-6 (Skid) ili ekvivalent**, tehnički list
2019-08-14. Motor **Perkins 404D-22G1**, 4-cilindarski, linijski, atmosferski, 2,2 l,
1500 o/min. Generator **FG Wilson FGL10040**, IP23, klasa izolacije H, AVR R120.
Skid **1550 × 620 × 1020 mm**, 365 kg suho / **372 kg mokro**.

### C.1 Zrak za hlađenje

| | |
|---|---|
| Protok hladnjaka (tehnički list) | **1980 m³/h** (33 m³/min) |
| Korigovano na gustoću lokacije | **2151 m³/h** |
| Zrak za sagorijevanje | **90 m³/h** (1,5 m³/min) |
| **Ukupno kroz usis** | **2241 m³/h** |
| Maks. vanjski otpor (tehnički list) | **125 Pa** |
| Maks. otpor usisa za sagorijevanje | 3 kPa |

Žaluzine, uz uobičajenih 50 % slobodne površine:

| | Bruto | Slobodno | Brzina | Δp |
|---|---|---|---|---|
| Usisna žaluzina | 500 × 700 = 0,35 m² | 0,175 m² | **3,56 m/s** | ≈17 Pa |
| Izlazna žaluzina | 600 × 600 = 0,36 m² | 0,180 m² | **3,46 m/s** | ≈16 Pa |

Ukupno ≈33 Pa — **duboko unutar budžeta od 125 Pa**, pa se žaluzine ne smanjuju.

**Limeni kanal.** Hladnjak stoji **60 mm** od zapadnog zida (zid 60 mm), pa kanal nije
razvod nego **prelazni komad** od prirubnice hladnjaka do žaluzine 600 × 600 mm:
razvijena dužina ≈0,2 m × 2,4 m opsega ≈ 0,5 m², sa prirubnicama i fazonskim komadima
**≈1,0 m²**. Doprinos padu pritiska je zanemariv.

### C.2 Toplotni bilans u prostoriji

| | |
|---|---|
| Toplota odvedena rashladnom tečnošću i uljem | 15,2 kW |
| **Toplota zračena u prostoriju** | **5,8 kW** |

Toplotu iz prostorije odnosi struja zraka hladnjaka; **ventilator hladnjaka je
rashladni put**, ne prostorni ventilator.

### C.3 Dopunska ventilacija prostorije

Aksijalni ventilator **1200 m³/h, Ø315 mm**, termostatski upravljan, u ISTOČNOM zidu.
Minimalna propisana prostorna ventilacija **120 m³/h** (6 izmjena zraka na sat).
**Ovaj ventilator nije dio rashladnog puta** — on je dopuna.

### C.4 Izduvni sistem

| | |
|---|---|
| Protok izduvnih gasova (standby, 50 Hz) | **192 m³/h** (3,2 m³/min) |
| Temperatura izduva | **413 °C** |
| Usvojeni prečnik | **NO 50** |
| **Brzina** | **27,2 m/s** — ispod uobičajenih 30 m/s ✔ |
| **Protutlak** | **≈1,9 kPa** uz dozvoljenih **10,2 kPa** ✔ |

**Prečnik određuje brzina, ne protutlak** — protutlak ima petostruku rezervu, a brzina
je ta koja se približava granici.

Trasa i količine:

| | |
|---|---|
| Elastični umetak → prigušivač, sa jednim lukom 90° | **1 m** |
| Prigušivač → izlaz iznad krova | **do 4 m** |
| Vanjski prečnik izolacije (NO 50 + 2 × 50 mm vune + Al lim) | ≈165 mm |
| **Površina izolacije i opšava** | 5,0 m × 0,52 m + prigušivač ≈ **3,0 m²** |

Završetak je **iznad krova, usmjeren naviše**, sa hvatačem iskri i kapom protiv upada
padavina.

### C.5 Gorivo

| Opterećenje | Potrošnja (standby, 50 Hz) |
|---|---|
| 100 % | 4,8 l/h |
| **75 %** | **3,7 l/h** |
| 50 % | 2,7 l/h |

| | |
|---|---|
| Projektovani godišnji rad | do **250 h/god** |
| Godišnja potrošnja pri 75 % | **≈925 l/god** |
| Spremnik **500 l** → autonomija pri 75 % | **≈135 h** rada |
| **Prvo punjenje** | **250 l** (spremnik se pri primopredaji ne puni do vrha) |

### C.6 Spremnik i sekundarna zaštita

Spremnik **dvoplašni, 500 l**, 1050 × 600 × 1310 mm, 170 kg prazan / ≈590 kg pun, sa
nivo sondom i **sondom za detekciju curenja u međuplaštu**.

**Tankvana zapremine 110 % NIJE zahtijevana**, jer međuplašt dvoplašnog spremnika
jeste sekundarna zaštita. Ispod spremnika se izvodi samo **prihvatno korito (kada)
1150 × 640 mm, visina ruba 200 mm**, za prihvat kapanja i prosipanja pri punjenju i
pretakanju, sa vidljivim najnižim mjestom za kontrolu i pražnjenje.

> Tankvana ne dobija zapreminu visinom, jer spremnik koji u njoj stoji istiskuje
> zapreminu zadržavanja — računa se samo **slobodna površina × visina ruba**. Uz
> slobodnu površinu od 0,33 m², koliko je ostaje u raspoloživom pojasu, rub bi morao
> biti visok **1,67 m** da se dosegne 110 %. Zato dvoplašni spremnik, a ne tankvana.

### C.7 Raspored otvora i servisni prostor

Ukrsno strujanje **SJEVER → ZAPAD**:

| Element | Zid | Napomena |
|---|---|---|
| Usis 500 × 700 | **SJEVER**, istočni kraj | donja ivica +0,30 m; zasjenjena strana, najhladniji zrak |
| Kanal + izlazna žaluzina 600 × 600 | **ZAPAD** | na osi hladnjaka, prelazni komad |
| Izduv NO 50 | **ZAPAD** | uspon uz zid, iznad krova |
| Oduška spremnika | **JUG**, istočni kraj | ≥3 m od izduva i usisa |
| Ventilator Ø315 | **ISTOK**, gore | donja ivica ≈+1,75 m |
| GRO | **SJEVER** | uz vanjski ormar koji napaja |

Izlaz toplog zraka i izduv **nisu** na sjevernoj strani, pa se vanjski ormari
**ICC360-HA1-C1** (sa aktivnim hlađenjem) i **MTS9302A** ne izlažu toplom zraku.

**Servisni prostor oko agregata** — agregat je centriran u slobodnom prostoru:

| Strana | Slobodno |
|---|---|
| JUG | **720 mm** |
| SJEVER | **720 mm** (520 mm na dijelu gdje je GRO) |
| ISTOK | **1155 mm** |
| ZAPAD | 60 mm — hladnjak, izduvava u kanal, ne servisira se s te strane |

Unutrašnja dubina 2180 mm umanjena za 740 mm (roštilj) ostavlja 1440 mm, podijeljeno
na pola. **Ovi prolazi se ne smiju zauzimati opremom niti skladištenjem.**

Skid stoji na **antivibracionim gumeno-metalnim osloncima** (vlastita frekvencija
≤8 Hz, statički progib ≥5 mm) između skida i roštilja. Zbog toga svi priključci na
motor moraju biti elastični: izduv preko elastičnog umetka, hladnjak preko ceradnog
spoja, a **vod goriva preko fleksibilnog umetka na polaznom i povratnom vodu** — kruta
Cu cijev NO 8 na priključku motora koji se pomiče zamara se i puca.

---

## D. Elektro dio

### D.1 String FN panela

| | |
|---|---|
| 6 × iPV585-M2A | Voc **309,3 V**, Vmp **256,7 V**, Imp 13,67 A, Isc 14,40 A |
| Prozor iSSU S4875G2 | 85–435 V DC, maks. 25 A, maks. 4000 W |
| Provjera | 257 V ✔ · 13,67 A ✔ · 3510 W ✔ |
| Optimizator SUN2000-600W-P | Vout 0–80 V, **Iout maks. 15 A** → 13,67 A ✔ |
| PVDB500-15-2B | 100–500 V, **maks. 15 A po ruti**, 2 rute → 1 string po ruti ✔ |
| Huawei pravilo za string | iPV540/585/630: **3–12 modula po stringu** → 6 ✔ |

**12 modula = 2 stringa × 6**, a ne 3 × 4: PVDB ima dva izlaza, a 6 × 51,55 V = 309 V
Voc je unutar prozora iSSU. String time obuhvata dva nosača.

> **Napomena koju tender ne smije ostaviti otvorenom:** iSSU se povezuje **isključivo**
> na iPV module sa optimizatorima. Obični 585 W moduli tražili bi SSU S4875G6 i drugo
> pravilo za string (3–7 modula ispod −10 °C).

### D.2 DC kabl

```
6 mm² Cu, 25 m u jednom smjeru, Imp 13,67 A
ΔU = 2 · 25 · 13,67 · 0,0175 / 6 = 1,99 V = 0,78 % od 257 V     ZADOVOLJAVA (<1 %)
```

Presjek je predimenzionisan; **ograničenje je stezaljka, a ne kabl** — ulazna
stezaljka iSSU traži **tačno 4 mm²**, pa je na ormaru potreban prelaz.

### D.3 DC potrošnja

| | pri 53,5 V | pri 48,0 V |
|---|---|---|
| 1180 W nazivno | 22,1 A | 24,6 A |
| 1330 W maksimalno | 24,9 A | 27,7 A |

Godišnje 10 337 kWh; decembar 878 kWh (ulaz za A.6).

### D.4 AC strana agregata — pobuda i struja kvara

| | |
|---|---|
| Nazivna struja pri 18 kVA / 400 V | **In = 26,0 A** |
| Traženo 3 × In, 10 s (ISO 8528-3) | **≈78 A** |
| Trajna struja kvara sa SHUNT pobudom | **≈13 A (0,5 × In)** — **ISPOD** nazivne struje |

**Standardna SHUNT pobuda nije prihvatljiva.** Kod nje se pri kvaru napon na
stezaljkama uruši, pobuda nestaje, i trajna struja kvara padne ispod nazivne — ne može
aktivirati nijednu prekostrujnu zaštitu. Tehnički list referentnog P18-6 na strani 4
navodi **Short Circuit Capacity 0 %** u standardnoj izvedbi, a traženu trajnu struju
kvara daje tek opciona **PMG / AUX** pobuda. **Zahtjev za nezavisnom pobudom (PMG ili
AREP/AUX) time je potvrđen samim tehničkim listom.**

Posljedica za zaštitu: na otočnom izvoru struja kvara ne može pouzdano isključiti
MCB, pa se zaštita od indirektnog dodira oslanja na **RCD** prema IEC 60364-4-41.

### D.5 Ograničenje ulazne snage ispravljača — **mjerodavno**

| | |
|---|---|
| Ispravljački sistem 3 × R4875G5 | 12 kW DC → **≈12,5 kW na AC strani** |
| Derativana snaga agregata, standby | **12,6 kW** — bez ikakve rezerve |
| Derativana snaga agregata, **prime** | **11,6 kW** — **premašeno** |

Lokacija **nije na mreži** i agregat radi ciklično po stanju napunjenosti baterija
(SoC), pa je mjerodavan **PRIME režim**, a ne standby. Neograničeno opterećenje od
12,5 kW premašuje raspoloživu snagu.

**Usvojeno: ulazna snaga ispravljačkog sistema ograničava se u kontroleru na
maks. 9,5 kW dok radi agregat** (≈82 % derativane prime snage). To ostavlja ≈8,2 kW
za punjenje baterija iznad TK potrošnje od 1,33 kW i istovremeno drži agregat iznad
minimalnog opterećenja od 30 %, čime se sprječava mokri rad motora (cilindarsko
glaziranje). **Ponuđač dokazuje usklađenost proračunom deratinga za lokaciju.**

Brojka **9,5 kW** mora stajati u predmjeru (Tačke 3.1 i 5.7) — opisni zahtjev
„ograničiti ulaznu snagu" bez broja ne obavezuje nikoga.

### D.6 Uzemljenje i zaštita od munje

| | |
|---|---|
| Traženi presjek vodiča | **Cu 50 mm²** prema EN 62305-3, tabela 7 |
| Postojeći prstenasti uzemljivač | Fe/Zn 25 × 4 mm — **obavezni bimetalni spojevi** Cu/Fe-Zn |
| Ciljani otpor rasprostiranja | **≤10 Ω** |
| Razmak kabla od odvoda munje | **≥0,5 m** |
| FN polja vs. zona zaštite stuba | **unutar** zone kotrljajuće sfere (7,5 m stvarno prema 10,68 m zaštićenog poluprečnika pri LPL I) → **nisu potrebne dodatne hvataljke** |

Sistem uzemljenja **TN-S**; tačka spajanja **N i PE samo u novom GRO**.

### D.7 Prenaponska zaštita

Objekat ima vanjski sistem zaštite od munje (antenski stub h = 38 m) i separacija nije
održana, pa **tip 2 sam po sebi nije dovoljan**:

- **AC porijeklo: kombinovani TIP 1 + 2** prema EN 61643-11, Iimp ≥12,5 kA (10/350 µs)
  po polu, Up ≤1,5 kV, 4p, sa daljinskom signalizacijom
- **DC, po stringu: tip 2** — u PVDB ormaru
- **Signalni i komunikacioni vodovi: EN 61643-21**, na oba kraja dionice

---

## E. Šta šta određuje — sažetak

| Veličina | Određuje je | Vrijednost |
|---|---|---|
| Nagib 45° | decembarski prihvat (A.5), ne godišnji prinos | 93 % decembarskog snopa |
| Custom nosač | qp lokacije vs. kataloške deklaracije (B.2) | nijedan nagib ne prolazi |
| Donja ivica +0,50 m | vjetar je mjerodavan, snijeg nije (A.3) | moment 42,6 kNm |
| Puna dubina temeljne trake | spreg od uzgona po traci (B.6) | 32,1 > 29,6 kN |
| Prečnik izduva NO 50 | brzina, ne protutlak (C.4) | 27,2 m/s < 30 |
| Roštilj za raznošenje | koncentrisano vs. ravnomjerno opterećenje (B.7) | OBAVEZAN |
| Ograničenje ispravljača 9,5 kW | derating u prime režimu (D.5) | 11,6 kW raspoloživo |
| PMG/AREP pobuda | struja kvara ispod In kod SHUNT (D.4) | 0 % po tehničkom listu |
| Zapremina spremnika 500 l | decembarski deficit i 250 h/god (A.6, C.5) | ≈135 h autonomije |

---

## F. Otvorene stavke

1. **Odmak polja od ograde** utvrđuje se pri poziciranju nosača (B.4) — ravan panela
   siječe kotu ograde na 1600 mm od donje ivice.
2. **Ovjereni statički proračun nosača i temelja** za qp ≥ 1,20 kN/m² — uslov prije
   dodjele ugovora, ne isporuka nakon nje.
3. **Derating agregata za tačne uslove lokacije** iz podataka proizvođača (A.2, D.5).
4. **Integracija DC odvodnika tipa 2 u PVDB500-15-2B** nije dokazana nijednim
   dokumentom u paketu — stavka ostaje zasebno iskazana dok se ne potvrdi.
5. **Kapacitet baterija**: Naručilac navodi 150 Ah, a ponuda na dosjeu 6 × ESM-48100A6.
   Nijedan generisani dokument ne navodi kapacitet i baterije su zasebna nabavka, pa
   se ništa ne mijenja do dostavljanja revidirane ponude.
6. **Masa nosača (≈110 kg)** je procjena — potvrđuje je proračun izrađivača.
7. **Procijenjena vrijednost LOT 1** (15.000 KM) računata je na raniju zapreminu
   temeljnih traka; puna dubina iz B.6 nosi 8,91 m³ betona umjesto 2,44 m³.

---

*Izvedene vrijednosti se održavaju u `cad/design.json`; crteži S-01…S-03, M-01 i E-01
formatiraju kote direktno iz tog fajla. Historija izmjena je u `00-change-log.md`.*
