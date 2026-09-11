# Objedinjeni proračuni — BS Hamzići (Čitluk)

**Verzija:** Rev 1, 11.09.2026.
**Status:** radni proračun Naručioca uz zajedničku tendersku dokumentaciju za lokacije
Sjednica i Hamzići. **Nije zamjena za ovjereni statički i mašinski proračun** koji
dostavlja ponuđač — ovdje su izvedene vrijednosti koje tenderska dokumentacija propisuje
kao ulazne i granične.

**Lokacija:** φ = 43,2880° N, λ = 17,6248° E, **493 m n.v.** (PVGIS DEM; projekat 500 m),
k.č. 109/1 K.O. Hamzići, zakup 12,00 × 12,50 m = 150 m². Postojeći kontejner K2
3005 × 2300 mm na AB ploči 5,40 × 5,40 m, u sredini između nogu rešetkastog stuba
h = 32 m (platforma na +3,0 m iznad krova kontejnera). Ovjereni projekat:
GP-BS-10472-291 (2017), verzija A; geometrija u `cad/site_geometry.json`.

**Sistem je isti kao na Sjednici** (odluka Naručioca 11.09.2026.): 12 × iPV585-M2A,
3 nosača × 4 modula pri 45°, FG Wilson P18-6 u kontejneru, baterije 6 × 150 Ah (48,6 kWh),
ICC360-HA1-C1, ograničenje ispravljača 9,5 kW. Ovdje su proračunate samo vrijednosti koje zavise od
lokacije; ostale su u proračunu za Sjednicu i vrijede i ovdje.

**Orijentacija.** Vrata kontejnera i kapija ograde su na **SJEVERU, malo prema
sjeverozapadu** (fotografije 08.09.2026. i Naručilac). Ovjereni crtež iz 2017. ih
prikazuje na suprotnoj strani uz strelicu sjevera okrenutu naviše — zakrenut je ≈180°.
Klima-uređaj Stulz je na **južnom zidu, u sredini** (fotografije; Naručilac
11.09.2026).

---

## A. Ambijentalni uslovi

### A.1 Gustoća zraka

`p = 101325·(1 − 2,25577·10⁻⁵·h)^5,25588`, `ρ = p / (287,05·T)`:

| Stanje | p | ρ |
|---|---|---|
| 0 m, +25 °C (referenca tehničkog lista) | 101,3 kPa | **1,184 kg/m³** |
| 493 m, +25 °C | 95,5 kPa | **1,116 kg/m³** |
| 493 m, −5 °C | 95,5 kPa | 1,241 kg/m³ |
| 493 m, +40 °C | 95,5 kPa | 1,063 kg/m³ |

### A.2 Derating agregata na 493 m

ISO 3046-1 / ISO 8528-1: −1 % na svakih 100 m iznad 100 m (−3,9 %) i ≈−3 % za ambijent
+40 °C. Ukupni faktor **0,931**:

| | tehnički list (25 °C, 100 m) | **na lokaciji (493 m, 40 °C)** |
|---|---|---|
| Standby | 18 kVA / 14,4 kW | **16,8 kVA / 13,4 kW** |
| Prime | 16,5 kVA / 13,2 kW | **15,4 kVA / 12,3 kW** |

Protok zraka hladnjaka: `1980 × 1,184/1,063 ≈ 2206 m³/h` (C.1). Ljetni prosjek jula i
avgusta je 24,7 °C, pa je +40 °C mjerodavan projektni ambijent.

### A.3 Snijeg i led

Ovjereni projekat kontejnera računa sa **S = 2,10 kN/m²** na tlu. Pri nagibu 45° je
μ₁ = 0,4 (EN 1991-1-3 §5.3.2), pa na ravni panela:

```
s = μ₁ · Ce · Ct · sk = 0,4 · 1,0 · 1,0 · 2,10  ≈  0,84 kN/m²
```

**Mjerodavan je vjetar** (1,20 kN/m², B.1). Snijeg djeluje naniže i umanjuje
mjerodavni uzgon. Na 493 m u hercegovačkom pojasu snijeg je rijedak i kratkotrajan.

Led: ovjereni projekat stuba računa sa naslagom **20 mm, gustine 500 kg/m³** — zahtjev
za akreciju na profile i spojeve nosača. Provjera prema BAS EN 1991-1-3 sa NA ostaje
obavezna u ovjerenom proračunu ponuđača.

### A.4 Beton i smrzavanje

Zadržano je **C30/37, XC4 + XF3, aerant 4–6 %**, na podlozi C12/15, armatura B500B,
zaštitni sloj 50 mm, dubina 900 mm — ista specifikacija kao na Sjednici, radi jednog
opisa za obje lokacije u LOT-u 1. Na 493 m bi XF1 bio dovoljan.

Tlo: prema ovjerenom projektu σdop = **150 kN/m²**, bez podzemne vode; krš, stijena blizu
površine (fotografije).

### A.5 Geometrija Sunca

Visina Sunca u podne `= 90 − φ + δ`, φ = 43,288°:

| Datum | δ | Visina u podne | Nagib za normalnu upadnost |
|---|---|---|---|
| 21.12. | −23,44° | **23,3°** | 66,7° |
| 21.03. / 21.09. | 0° | 46,7° | 43,3° |
| 21.06. | +23,44° | 70,2° | 19,8° |

Pri 45° upadni ugao direktnog zračenja u podne 21. decembra je 21,7° (cos 0,929, 93 %).
Kao i na Sjednici, strmiji nagib pomaže decembru, ali agregat godišnje radi više: pri
60° 644 kWh u decembru prema 601 kWh pri 45°, ali **241 h/god rada agregata prema
226 h** (A.6). **Usvojeni nagib: 45°** (odluka 11.09.2026.).

**Horizont:** PVGIS DEM ≤2,7°, samo na sjeveru. **Stablo** JJI–JI od stuba (≈7–9 m,
15–20 m, procjena iz fotografija, izvan zakupa) zaklanja zimsko jutarnje Sunce: sa sredine
polja vidi se na azimutu ≈124–149°, do 16–32° visine. Stablo ostaje (odluka
11.09.2026.); uticaj je u A.6.

### A.6 Energetski bilans — simulacija (pvlib + PVGIS-SARAH3, 2005–2023)

Isti alat i ista metoda kao na Sjednici (tamo A.6): satni bilans na −48 V DC sabirnici za
19 godina bez prekida. Ulazi i pretpostavke: `pvsim/sites/hamzici.json`; rezultati:
`review/pvsim/` (`kpis.json`, `energetski-bilans.md`, slike). Razlike u ulazima prema
Sjednici: zaprljanje 1–3 % mjesečno (suši i prašnjaviji ljetni period), snijeg zanemariv
(≤1 % u januaru i februaru), više hlađenja ormara ljeti. Potrošnja **1180 W / 1330 W je
privremena**, preuzeta sa Sjednice do dostavljanja izmjerene potrošnje ove bazne stanice.
Baterija je ista kao na Sjednici: **6 × 150 Ah = 48,6 kWh** (Odluka, Aneks 2). Pomoćna
potrošnja je 45 W, sa trajnim potrošačima na −48 V (D.9).

**Provjera prema PVGIS-u.** Isti model modula sa PVGIS-ovim gubitkom 14 % daje
9 780 kWh/god prema 9 840 kWh/god iz PVGIS PVcalc (−0,6 %); nijedan mjesec ne odstupa
više od 2,2 %; satna korelacija sa PVGIS-ovom proizvodnjom r = 1,0000.

**Gubici FN lanca (prosjek godine).**

| Stavka | kWh/god | Gubitak |
|---|---|---|
| Ozračenje u ravni × kWp (STC) | 12 727 | |
| Refleksija (IAM) | 12 368 | −2,82 % |
| Temperatura i slabo svjetlo | 11 372 | −8,05 % |
| Zaprljanje | 11 146 | −1,99 % |
| Snijeg | 11 129 | −0,15 % |
| Neusklađenost + LID | 11 040 | −0,80 % |
| DC kablovi | 10 987 | −0,48 % |
| Optimizatori | 10 878 | −1,00 % |
| **iSSU S4875G2 → DC sabirnica** | **10 448** | −3,95 % |

Na sabirnicu stiže **10 448 kWh/god** (1 488 kWh/kWp, 82,1 % od STC). Temperaturni
gubitak je veći nego na Sjednici (8,1 % prema 6,2 %) — lokacija je niža i toplija.

**Mjesečni bilans (prosjek 2005–2023).**

| Mjesec | FN na sabirnici, kWh | Potrošnja, kWh | Agregat (DC), kWh | Agregat, h | Gorivo, l |
|---|---|---|---|---|---|
| jan | 646 | 911 | 335 | 36,8 | 122 |
| feb | 655 | 829 | 287 | 31,4 | 104 |
| mar | 885 | 910 | 210 | 23,0 | 76 |
| apr | 938 | 883 | 127 | 14,0 | 46 |
| maj | 987 | 918 | 89 | 9,8 | 32 |
| jun | 1 022 | 905 | 40 | 4,4 | 15 |
| jul | 1 122 | 952 | 13 | 1,5 | 5 |
| aug | 1 116 | 951 | 21 | 2,3 | 8 |
| sep | 986 | 896 | 65 | 7,1 | 23 |
| okt | 884 | 915 | 165 | 18,1 | 60 |
| nov | 606 | 882 | 335 | 36,7 | 121 |
| dec | 601 | 911 | 372 | 40,8 | 135 |
| **godina** | **10 448** | **10 864** | **2 061** | **226** | **746** |

**Ključni pokazatelji (nagib 45°, bez stabla).**

| Pokazatelj | Vrijednost |
|---|---|
| Solarni udio u potrošnji | 81,0 % |
| **Rad agregata** | **226 h/god** prosjek · P90 271 h · najgora godina 307 h (2010) |
| Startova agregata | 80/god prosjek, najviše 108 |
| **Gorivo** | **746 l/god** prosjek · P90 895 l · najviše 1 013 l |
| Dopuna spremnika 500 l (pri 20 %) | 1,8 puta godišnje, najkraći razmak 71 dan |
| Najduže razdoblje bez rada agregata | 134 dana |
| Ekvivalentnih ciklusa baterije | 139/god |
| Rad ispod 30 % opterećenja | 0 h |
| Nepokrivena potrošnja | 0 kWh u 19 godina |

**Stablo.** Zasjenjenje prema tri procjene položaja i visine (povoljna / srednja /
nepovoljna), uz propuštanje pola direktnog zračenja kroz golu krošnju zimi:
decembar −2,7 / −7,2 / −10,4 %, rad agregata 231 / 239 / 249 h/god, gorivo 764 / 788 /
822 l/god (`review/pvsim/photo/zasjenjenje.json`).

**Osjetljivost na postavke SMU i pretpostavke.**

| Slučaj | DEA h/god prosjek | P90 | Najgora | Gorivo l/god | Startova/god |
|---|---|---|---|---|---|
| **Osnovni (Prilog I §4.6): stop SoC 60 %, punjenje 0,5 C** | **226** | **271** | **307** | **746** | **80** |
| SMU bez parametriranja: stop SoC 90 %, 0,25 C | 253 | 298 | 330 | 834 | 55 |
| Stop SoC 100 % | 267 | 316 | 346 | 879 | 52 |
| Stop SoC 40 % | 212 | 258 | 295 | 700 | 131 |
| Punjenje 0,15 C | 252 | 299 | 344 | 769 | 80 |
| Start pri DOD 70 % | 237 | 281 | 320 | 781 | 123 |
| Baterija 28,8 kWh (6 × 100 Ah, stara ponuda Huawei) | 277 | 323 | 354 | 915 | 160 |
| Potrošnja 1180 W stalno | 203 | 246 | 290 | 670 | 72 |
| Potrošnja 1330 W stalno | 280 | 330 | 368 | 924 | 98 |

Trajni potrošači na −48 V (D.9, 25 W) dodaju ≈12 h rada agregata godišnje.

**Zaključak.** Uz baterije od 48,6 kWh i trajne potrošače na −48 V prosječan rad agregata
(≈230 h/god) je ispod 250 h/god iz RFI, ali ne i u lošijim godinama (u 9 od 10 godina
do ≈270 h, najviše ≈310 h); spremnik od 500 l ne traje godinu dana (≈750 l/god). TD
navodi simulirane vrijednosti — **≈230 h/god i ≈750 l/god**, dopuna dva puta godišnje —
uz obavezno parametriranje SMU iz Priloga I §4.6.

---

## B. Konstrukcija — nosači FN panela

### B.1 Proračunski pritisak vjetra

Ovjereni projekat (2017) računa prema JUS U.C7.110–113 sa osnovnom brzinom vjetra
**vm,50,10 = 25 m/s**: srednji pritisak qm,T,10 = 0,29 kN/m², a pritisak na udar
qg,T,z = 0,41 kN/m² na 1,5 m i 0,56 kN/m² na 4,5 m (Gz = 1,86).

Uz vb,0 = 25 m/s, BAS EN 1991-1-4 na visini gornje ivice polja (z = 3,74 m):

| Kategorija terena | ce(z) | qp |
|---|---|---|
| II (nisko rastinje) | 1,76 | 0,69 kN/m² |
| I (otvoren teren) | 2,21 | 0,86 kN/m² |
| 0 (izložen vrh) | 2,45 | 0,96 kN/m² |

(qb = ½ · 1,25 · 25² = 0,39 kN/m²)

**Usvojeno: qp ≥ 1,20 kN/m²**, isto kao na Sjednici. Izvedena vrijednost je niža, ali
jedna konstrukcija nosača i jedan temelj za obje lokacije pojednostavljuju LOT 1, a
rezerva pokriva nepoznatu orografiju i buru u širem području Mostara. **Ponuđač
dokazuje nosivost ovjerenim proračunom za lokaciju.**

### B.2 Kataloški nosači

Kataloški nosač tipa A je pri 45° deklarisan na 0,52 kN/m² — ispod i najniže izvedene
vrijednosti (0,69 kN/m²). Nosač je i ovdje **CUSTOM IZRADA**.

### B.3 Geometrija polja

Kao Sjednica: 3 nosača × 4 modula (2 reda × 2 kolone, portret), polje 2305 × 4576 mm,
horizontalna projekcija pri 45° **3236 mm**, ukupno 12 modula = 7,02 kWp.

### B.4 Položaj polja

| | |
|---|---|
| Donja / gornja ivica | **+0,50 m / +3,74 m** od terena |
| Kota ograde | **+1,80 m** od ploče (ovjereni `04_Ograda.dwg`); teren oko ploče je na **−0,20 m**, pa je ograda 2,00 m iznad terena |
| **Nadvišenje ograde** | **1,74 m** (3,74 − 2,00) |
| Raspoloživi pojas južno od ploče | **3575 mm** (zakup 12,00 × 12,50 m, ploča 5,40 m u sredini) |
| Dubina polja / dužina trake | 3236 / 3300 mm → **rezerva ≈0,27 m** |
| Širina polja (3 nosača, razmak 0,40 m) | 7,7 m od raspoloživih 12,0 m |

Polje je južno od ograde, izvan platoa; kapija i vrata su na sjeveru, pa prolaz kroz
polje nije potreban. Ako ivica zakupa odstupa od pravca istok–zapad (vrata gledaju malo
prema sjeverozapadu), nosači se postavljaju **stepenasto, svaki okrenut na jug**, ili
paralelno sa ivicom zakupa uz odstupanje azimuta **≤15°** (≈−1 % godišnjeg prinosa).
Tačan položaj utvrđuje Ponuđač geodetskim snimanjem.

### B.5 Dejstva vjetra po nosaču

Ista geometrija i isti usvojeni qp kao na Sjednici, pa i ista dejstva: površina
**10,55 m²**, ULS uzgon **18,1 kN**, horizontalna sila **13,4 kN**, moment prevrtanja
**42,6 kNm**, spreg po traci **26,6 kN** pri razmaku 1600 mm.

### B.6 Temelji

Kao Sjednica: **6 traka** 450/550 × 3300 mm, **puna dubina 900 mm**, **1,485 m³ po traci →
8,91 m³** C30/37. Vlastita težina trake 32,1 kN > potrebnih 29,6 kN. Iste količine
iskopa, podložnog betona i odvoza (LOT 1, sekcija 2).

### B.7 Pod kontejnera i unos opreme

| | |
|---|---|
| Nosivost poda (g+p) | **10,00 kN/m²** — ovjereni projekat, AG dio §4.4.2 (sekundarni HOP U 100 × 50 × 3 na 0,51 m, primarni nosači 15,00 kN/m′) |
| Agregat mokro | 372 kg / 0,96 m² = **3,80 kN/m²** |
| Pun spremnik 500 l | 590 kg / 0,63 m² = **9,2 kN/m²** |

Koncentrisana opterećenja na malom broju sekundarnih nosača: **čelični roštilj za
raznošenje opterećenja je OBAVEZAN**, kao na Sjednici.

**Unos:** skid širine 620 mm kroz vrata **1,00 × 2,15 m** (kapija ograde 1,30 m) — nije
potrebno skidati krovni panel ni otvarati zid.

---

## C. Mašinski dio — agregat

Referentni agregat, spremnik i sekundarna zaštita su isti kao na Sjednici (tamo C.2,
C.6). Razlike su u rasporedu otvora i izduvu.

### C.1 Zrak za hlađenje

| | |
|---|---|
| Protok hladnjaka (tehnički list) | 1980 m³/h |
| Korigovano na gustoću lokacije (493 m, 40 °C) | **2206 m³/h** |
| Zrak za sagorijevanje | 90 m³/h |
| **Ukupno kroz usis** | **2296 m³/h** |
| Maks. vanjski otpor | **125 Pa** |

Izlaz toplog zraka ide kroz **postojeće otvore klima-uređaja Stulz** na istočnom zidu
(odluka Naručioca 11.09.2026.). Projekat klimatizacije iz 2017. predviđa dva otvora
30/70 cm; ugrađeni WDE80 je veći uređaj, pa se stvarni otvori mjere pri obilasku.
Uz 50 % slobodne površine žaluzina:

| | Bruto | Slobodno | Brzina | Δp |
|---|---|---|---|---|
| Oba otvora Stulz 300 × 700 zajedno | 0,42 m² | 0,210 m² | **3,0 m/s** | ≈12 Pa |
| Izlaz 600 × 600 (spojeni/prošireni otvori) | 0,36 m² | 0,180 m² | 3,5 m/s | ≈17 Pa |
| Usisna žaluzina 500 × 700, ZAPADNI zid | 0,35 m² | 0,175 m² | **3,6 m/s** | ≈18 Pa |

Izlazna površina mora biti **≥0,36 m² bruto**: jedan otvor 300 × 700 sam (0,21 m²) dao
bi ≈6 m/s kroz žaluzinu. Plenum od hladnjaka do otvora ≈1,5 m² razvijene površine.
Ukupni otpor ≲50 Pa — **unutar budžeta od 125 Pa**.

### C.2 Toplota u prostoriju

Kao Sjednica: **5,8 kW** zračene toplote, odnosi je struja zraka hladnjaka.

### C.3 Dopunska ventilacija

Aksijalni **izvlačni** ventilator **1200 m³/h, Ø315 mm, 48 V DC (EC)**, napajan sa DC
razvoda (D.9), na **ZAPADNOM** zidu gore,
sjeverno od usisa. Radi po termostatu dok agregat ne radi (i za hlađenje nakon
zaustavljanja); kontroler DEA ga isključuje dok agregat radi, jer tada prostor ventilira
struja zraka hladnjaka. Kao izlazni otvor ne ulazi u uslov razmaka ≥3 m od izduva (C.4).

### C.4 Izduvni sistem

| | |
|---|---|
| Protok / temperatura | 192 m³/h pri 413 °C |
| Prečnik | **NO 50**, brzina 27,2 m/s (< 30 m/s) |
| Trasa | elastični umetak → prigušivač ≈1 m, zatim ≈3 m **horizontalno kroz ISTOČNI zid** na ≈+2,30 m; završetak ≥0,40 m od zida (H-04: 3,2 m do sredine usisne žaluzine) |
| Protutlak | ≈1,6 kPa uz dozvoljenih 10,2 kPa |
| Izolacija i opšav | 4 m × 0,52 m²/m + prigušivač ≈ **2,5 m²** |

**Završetak ne može biti iznad krova**: platforma stuba na +3,0 m je iznad krova
kontejnera (+2,89 m). Izduv izlazi horizontalno kroz istočni zid, usmjeren na istok —
dalje od FN polja (jug) i ulaznih vrata (sjever) — sa hvatačem iskri i kapom protiv
padavina, ≥3 m od usisa zraka i odušne cijevi spremnika, i ne smije se usmjeriti na noge
stuba ni na kablove.

### C.5 Gorivo

Prime potrošnja P18-6 (2,6 / 3,4 / 4,4 l/h pri 50 / 75 / 100 %); pri ograničenju 9,5 kW
≈3,3 l/h.

| | |
|---|---|
| Očekivani godišnji rad (A.6) | **≈230 h/god**; u 9 od 10 godina do ≈270 h, najviše ≈310 h |
| Očekivana godišnja potrošnja (A.6) | **≈750 l/god**; najviše ≈1 010 l |
| Spremnik 500 l, dopuna pri 20 % | ≈400 l, ≈120 h rada — **dva puta godišnje** |
| **Prvo punjenje** | **250 l** |

### C.6 Raspored otvora

Ukrsno strujanje **ZAPAD → ISTOK**:

| Element | Zid | Napomena |
|---|---|---|
| Usis 500 × 700 | **ZAPAD** | donja ivica +0,30 m, na osi agregata |
| Plenum + izlaz ≥0,36 m² | **ISTOK**, južni kraj | kroz postojeće otvore Stulz; višak otvora zatvoriti panelom 60 mm |
| Izduv NO 50 | **ISTOK** | horizontalno na ≈+2,30 m, ispod platforme stuba; završetak ≥0,40 m od zida |
| Ventilator Ø315, izvlačni | **ZAPAD**, gore | sjeverno od usisa; izlazni otvor (C.3) |
| Agregat | uz **JUG** | duža osa istok–zapad, hladnjak na istoku; servis sa sjeverne strane (do ≈2,0 m), južna strana ≈0,23 m od zida |
| Spremnik 500 l | **ISTOK**, sjeverno od agregata | ne u jugoistočnom uglu (plenum); izolovani izduv prolazi između spremnika i agregata, ≥0,30 m od spremnika |
| Oduška spremnika | kroz **SJEVER** istočno od vrata, stojeća cijev uz sjevernu ogradu, završetak +2,80 m | H-04: 3,0 m od završetka izduva, 4,6 m od usisa, 1,5 m od ormara Huawei; principijelno — konačno prema elaboratu zaštite od požara |
| GRO | **SJEVER**, zapadno od vrata | raspoloživi zid 0,595 m → širina GRO ≤0,50 m |
| Ulazna vrata | **SJEVER** | 1,00 × 2,15 m |
| Huawei ICC360-HA1-C1 | vani, **SJEVER** | vanjski ormar na ploči između sjeverozapadne noge stuba i krila vrata, kao na Sjednici; napaja se iz GRO kroz sjeverni zid |

Na crtežu H-04 razmak od završetka izduva do sredine usisne žaluzine je **3,2 m** (≥3 m);
izvlačni ventilator je izlazni otvor i ne ulazi u taj uslov. Hladnjak agregata je uz
istočni zid, na mjestu otvora Stulz. Položaj otvora Stulz je procjena sa fotografije, pa
je raspored u kontejneru na crtežu H-04 principijelan — Ponuđač ga potvrđuje na licu
mjesta.

### C.7 Demontaža klima-uređaja Stulz

Postojeći kompaktni zidni klima-uređaj **Stulz WDE80** (8 kW, rashladni medij R407C,
radni opseg −20 do +50 °C; natpisna pločica nije čitljiva na fotografijama) se odspaja
(230 V AC, 48 V DC, signalizacija) i demontira **bez otvaranja rashladnog kruga**, pakuje
i prevozi u skladište **BH Telecom d.d., Alipašino Polje, Sarajevo**, uz zapisnik o
primopredaji (tip, serijski broj, stanje). Otvori ostaju za izlaz zraka agregata.

---

## D. Elektro dio

### D.1 String FN panela

Isto kao Sjednica: 2 stringa × 6 × iPV585-M2A, Voc 309,3 V, Imp 13,67 A, PVDB500-15-2B,
2 × iSSU S4875G2.

### D.2 DC kabl

Polje je neposredno južno od ploče; trasa do ormara ≈20 m u jednom smjeru:

```
ΔU = 2 · 20 · 13,67 · 0,0175 / 6 = 1,59 V = 0,62 % od 257 V     ZADOVOLJAVA (<1 %)
```

### D.3 Potrošnja

1180 W nazivno / 1330 W maksimalno — **privremeno**, do izmjerene potrošnje; uz to 45 W
pomoćne potrošnje na −48 V, sa trajnim potrošačima (D.9).

### D.4 Struja kvara agregata

Isto kao Sjednica: In = 26,0 A, traženo 3 × In ≈ 78 A trajno ≥10 s — **PMG ili AREP/AUX
pobuda obavezna**; zaštita od indirektnog dodira preko RCD.

### D.5 Ograničenje ulazne snage ispravljača

Derativana prime snaga je 12,3 kW, neograničeni ispravljački sistem vuče ≈12,5 kW.
**Ograničenje 9,5 kW** ostaje; ovdje je to 77 % derativane prime snage (na Sjednici
82 %), dakle sa većom rezervom, a agregat ostaje iznad 30 % opterećenja.

### D.6 Uzemljenje i zaštita od munje

| | |
|---|---|
| Postojeći uzemljivač | Fe/Zn 25 × 4 mm: prsten u temeljima stopa stuba i prsten na dubini 0,8 m (ovjereni `3.6.9 Plan uzemljivača`) |
| Vodič do nosača | Cu 50 mm², bimetalni spojevi Cu/Fe-Zn |
| Ciljani otpor | ≤10 Ω |
| Ukrštanja sa temeljnim trakama | oba postojeća prstena (kvadrati 7,50 m i 10,00 m oko ploče, 1,05 m i 2,30 m od ivice ploče, dubina 0,8 m) presijecaju temeljne trake (dubina 0,9 m): lociranje, otkopavanje i premještanje ispod ili oko trake ili premoštavanje, bez trajnog prekida prstena; otpor se mjeri prije i poslije radova — posebna stavka LOT 1 |
| FN polje i stub | rešetkasti stub h = 32 m; metoda kotrljajuće sfere, LPL I (r = 20 m): na visini gornje ivice (3,74 m) zaštićeni radijus je ≈8,4 m, a polje je ≈2–5 m od najbliže noge stuba → **unutar zone zaštite, dodatne hvataljke nisu potrebne** |

### D.7 Prenaponska zaštita

Kao Sjednica: AC porijeklo **TIP 1 + 2** (Iimp ≥12,5 kA), DC tip 2 po stringu, signalni
vodovi prema **EN 61643-21** (stub sa LPS).

### D.8 Novi GRO

Kontejner je prazan — nema GRO ni postojećih krugova. Novi GRO (TN-S, jedini spoj N i PE
u GRO): dovod agregata 18 kVA preko sklopke 1-0-2, glavni RCD 63 A/300 mA tip S, SPD
tip 1 + 2, odvodi — pod naponom samo dok agregat radi: AC ulaz Huawei ICC360-HA1-C1
(ispravljači, ograničenje 9,5 kW), rasvjeta i utičnice u kontejneru (RCBO 16 A/30 mA),
pomoćni potrošači agregata, blokada ventilacije pri gašenju.
**Nema kruga za klima-uređaj** (demontira se). GRO je na sjevernom zidu, zapadno od
vrata; raspoloživi zid je 0,595 m, pa je **širina GRO ≤0,50 m** (npr. 500 × 250 × 800 mm).

### D.9 Trajni potrošači na −48 V DC

Agregat je jedini izvor izmjeničnog napona i ≈97 % godine ne radi. Potrošači koji moraju
raditi stalno napajaju se zato sa −48 V DC iz ormara ICC360, preko novog DC razvoda
(odluka Naručioca 11.09.2026, obje lokacije):

| Potrošač | Napajanje | Prosječno |
|---|---|---|
| Svjetiljka za obilježavanje stuba, LED | 48 V DC, foto-senzor (≈12 h noću) | ≈8 W |
| Vatrodojavna centrala | DC/DC | ≈4 W |
| Punjač akumulatora za start agregata | DC/DC | ≈3 W |
| Ventilator prostora 48 V DC (EC) | termostat, ljeti | ≈2 W |
| Predgrijač rashladne tečnosti DEA | DC, samo prije starta pri niskoj temperaturi (≈0,1 kWh po startu) | ≈1 W |
| Gubici DC/DC | | ≈3 W |
| **Ukupno** | | **≈21 W → usvojeno ≤25 W** |

Jedna svjetiljka u kontejneru je za 48 V DC, pa je svjetlo dostupno i kad agregat ne
radi; radi samo pri obilasku i ne ulazi u trajnu potrošnju. Energetski bilans (A.6)
računa sa 45 W pomoćne potrošnje na −48 V: 20 W za SMU, BMS i ispravljače u mirovanju i
25 W za trajne potrošače.

---

## E. Šta šta određuje — sažetak

| Veličina | Određuje je | Vrijednost |
|---|---|---|
| Nagib 45° | godišnji rad agregata (A.5, A.6) | 226 h pri 45° prema 241 h pri 60° |
| Custom nosač | qp lokacije vs. kataloške deklaracije (B.1, B.2) | 0,69–0,96 > 0,52 kN/m² |
| Usvojeni qp 1,20 kN/m² | jedna konstrukcija za obje lokacije (B.1) | moment 42,6 kNm |
| Polje u južnom pojasu | zakup 12,00 × 12,50 m (B.4) | 3236 mm od raspoloživih 3575 |
| Izlaz zraka kroz otvore Stulz | odluka Naručioca, protok 2206 m³/h (C.1) | ≥0,36 m² bruto, ≲50 Pa |
| Horizontalni izduv | platforma stuba +3,0 m iznad krova (C.4) | NO 50, istočni zid |
| Ograničenje ispravljača 9,5 kW | derating u prime režimu (D.5) | 77 % od 12,3 kW |
| Baterije 6 × 150 Ah (48,6 kWh) | Odluka, Aneks 2 (A.6) | ≈230 h/god prema ≈280 h sa 28,8 kWh |
| Parametriranje SMU | osjetljivost simulacije (A.6) | ≈230 h i ≈750 l/god |
| Trajni potrošači na −48 V DC | agregat je jedini AC izvor; odluka Naručioca (D.9) | ≤25 W, ≈+12 h/god rada DEA |

---

## F. Otvorene stavke

1. **Izmjerena DC potrošnja** bazne stanice — do tada vrijedi 1180 W / 1330 W sa Sjednice.
2. **Natpisna pločica i otvori klima-uređaja Stulz** — mjere otvora određuju plenum i
   izlaznu žaluzinu (C.1).
3. **Fotografije unutrašnjosti kontejnera** i potvrda orijentacije pri obilasku.
4. **Ovjereni statički proračun nosača i temelja** za qp ≥ 1,20 kN/m² — uslov prije
   dodjele ugovora.
5. **Derating proizvođača** za 493 m i +40 °C (A.2, D.5).
6. **Baterije i struja punjenja** — 6 × 150 Ah (48,6 kWh) prema Odluci; najveću struju
   punjenja potvrđuje proizvođač baterija (A.6).
7. **Tri izgubljene fotografije** (20260908_121619, _121701, _123320) — ponovni izvoz.
8. **Procijenjene vrijednosti** po lokaciji i LOT-u dostavlja Naručilac.

---

*Geometrija lokacije: `cad/site_geometry.json`; vrijednosti sistema: `cad/design.json`;
energetski bilans: `review/pvsim/`. Crteži H-01 … H-05 formatiraju kote iz tih fajlova.*
