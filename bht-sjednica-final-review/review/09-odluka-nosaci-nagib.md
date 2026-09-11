# Odluka — nosači, nagib i granice rada agregata (obje lokacije)

Rev 9 · 11.09.2026. · zapisnik odluke Naručioca, na osnovu simulacije `pvsim`
(pvlib + PVGIS-SARAH3, satno 2005–2023). Brojevi su iz `review/pvsim/kpis.json`
ove lokacije i `hamzici-hybrid-solar/review/pvsim/kpis.json`; tabele osjetljivosti u
`energetski-bilans.md` istih foldera.

Sistem je nepromijenjen (odluka Naručioca): 12 × iPV585-M2A = 7,02 kWp, 2 stringa × 6,
PVDB500-15-2B, 2 × iSSU S4875G2, ICC360-HA1-C1 + LFP baterije 6 × 150 Ah (48,6 kWh), FG Wilson
P18-6 u kontejneru, start po SoC preko GIM01C1, ograničenje ispravljača 9,5 kW.
Otvoreno je bilo samo: raspored nosača (3×4 ili 2×6) i nagib (45° ili 60°, „60° ako je
primjenjivo") po lokaciji.

---

## 1. Odluke

| Tema | Odluka |
|---|---|
| Sjednica — nosači i nagib | **3 nosača × 4 modula, 45°** — Rev 8 ostaje; crteži, količine i Prilog I §3 se ne mijenjaju |
| Hamzići — nosači i nagib | **3 nosača × 4 modula, 45°**, kao Sjednica. Uklapanje potvrđeno iz ovjerenog `01_Situacija 1_200.dwg`: zakup 12 000 × 12 500 mm, ploča 5 400 mm u sredini. Vrata i kapija su prema fotografijama i Naručiocu na **SJEVERU, malo prema sjeverozapadu** (crtež ih prikazuje suprotno, dakle zakrenut je ≈180°), pa je južno od ploče **3 575 mm** — polje pri 45° (projekcija 3,24 m, trake 3,30 m) staje uz ≈0,27 m rezerve, bez prolaza kroz polje. Nosači gledaju na jug: stepenasto unutar pojasa ili paralelno sa ivicom zakupa uz odstupanje azimuta ≤15° (≈−1 % prinosa); potvrđuje se obilaskom. 60° (dubina 2,29 m) nije potreban |
| Granice rada agregata (Odluka, Aneks 2) | tvrdnje „≤250 h/god" i „500 l najmanje godinu dana" **zamjenjuju se simuliranim vrijednostima**, uz zahtjev za parametriranje SMU za minimalan rad DEA; tačan tekst Naručilac odobrava prije izmjene |
| Stablo JJI–JI kod Hamzića | **ostaje**; TD bilježi zasjenjenje i traži od Ponuđača da polje pozicionira tako da ga umanji |
| Baterije | **6 × 150 Ah = 48,6 kWh** na obje lokacije, kako navodi Odluka (Aneks 2); Huawei ponuda na dosjeu (6 × ESM-48100A6, 28,8 kWh, uz module od 540 W) je zastarjela i ostaje samo kao slučaj osjetljivosti |
| Trajni potrošači (obje lokacije) | na **−48 V DC** iz ormara ICC360, preko novog DC razvoda: svjetiljka za obilježavanje stuba, vatrodojava, punjač akumulatora za start agregata, ventilator prostora, jedna svjetiljka u kontejneru i predgrijač rashladne tečnosti agregata, koji kontroler agregata uključuje samo prije starta (grijač prostora se ne predviđa) — agregat je jedini izvor izmjeničnog napona i ≈97 % godine ne radi. Prilog I ih ograničava na 25 W prosječno; simulacija računa sa 45 W pomoćne potrošnje umjesto 20 W (≈+13 h/god rada DEA na Sjednici, ≈+12 h na Hamzićima) |

## 2. Zašto 45°, a ne 60°

60° daje više u decembru, ali manje u ostatku godine, pa agregat radi **više**:

| | Sjednica 45° | Sjednica 60° | Hamzići 45° | Hamzići 60° |
|---|---|---|---|---|
| FN na DC sabirnici, kWh/god | 10 137 | 9 651 | 10 448 | 9 887 |
| Decembar FN / potrošnja, kWh | 560 / 893 | 617 / 893 | 601 / 893 | 644 / 893 |
| DEA h/god prosjek / P90 (48,6 kWh, trajni potrošači na −48 V, postavke SMU iz Priloga I) | 247 / 307 | 263 / 325 | 226 / 271 | 241 / 291 |
| Gorivo, l/god | 815 | 868 | 746 | 797 |

Baterija od 48,6 kWh pokriva ≈1,5 dan potrošnje: agregat pokriva nizove oblačnih dana u
proljeće i jesen, ne samo decembar. Tu 60° gubi više nego što dobije u decembru.
„60° ako je primjenjivo" dakle **nije primjenjivo** ni na jednoj lokaciji.

Konstrukcija ide istim smjerom (qp 1,20 kN/m², `python -m pvsim stands`):

| Po nosaču | 3×4 @ 45° | 3×4 @ 60° (c_f 1,5–1,8) | 2×6 @ 45° | 2×6 @ 60° |
|---|---|---|---|---|
| Moment prevrtanja, kNm | 42,6 | 61,2–73,4 | 64,3 | 92,3–110,8 |
| Spreg po traci, kN | 26,6 | 38,3–45,9 | 40,2 | 57,7–69,2 |
| Beton ukupno, m³ | 8,91 | 10,6–12,8 | 7,4 | 10,7–12,8 |
| Gornja ivica / dubina polja | +3,74 m / 3,24 m | +4,46 m / 2,29 m | +3,74 m / 3,24 m | +4,46 m / 2,29 m |

## 3. Granice rada agregata — nalaz

Odluka, Aneks 2 (Obrazloženje) navodi: maksimalno dozvoljeno godišnje vrijeme rada DEA
250 h (standby prema ISO 8528-3) i da spremnik od 500 l „treba obezbjediti autonomiju od
najmanje godinu između dopuna goriva". Uz baterije od 48,6 kWh i trajne potrošače na
−48 V (odluke 11.09.2026.) **prosjek** rada agregata je na Sjednici tik ispod 250 h, a na
Hamzićima ispod, ali **lošije godine nisu**, a spremnik od 500 l **ne traje godinu dana**
ni na jednoj lokaciji:

| 45° | DEA h/god prosjek / P90 / najgora | Gorivo l/god | 500 l traje | Startova/god |
|---|---|---|---|---|
| Sjednica, 48,6 kWh, **SMU iz Priloga I (stop SoC 60 %)** | 247 / 307 / 327 | 815 | 0,61 god | 88 |
| Sjednica, 48,6 kWh, SMU bez parametriranja (stop SoC 90 %) | 275 / 332 / 360 | 909 | 0,55 god | 60 |
| Sjednica, 28,8 kWh (stara ponuda), SMU iz Priloga I | 297 / 361 / 376 | 981 | 0,51 god | 172 |
| Hamzići, 48,6 kWh, **SMU iz Priloga I** | 226 / 271 / 307 | 746 | 0,67 god | 80 |
| Hamzići, 48,6 kWh, SMU bez parametriranja | 253 / 298 / 330 | 834 | 0,60 god | 55 |
| Hamzići, 28,8 kWh (stara ponuda), SMU iz Priloga I | 277 / 323 / 354 | 915 | 0,55 god | 160 |

Već je i sam dosadašnji 07-proračuni C.5 davao ≈925 l/god pri 250 h — dakle 500 l nikad
nije bilo godišnja zaliha. Zaustavljanje pri SoC 60 % daje ≈10 % manje sati i goriva od
zaustavljanja pri 90 %, uz ≈0,25 starta dnevno; 40 % daje još ≈5 % manje, ali povećava
broj startova za ≈60 %. Pri 48,6 kWh struja punjenja od 0,25 C više ne ograničava agregat;
najveću struju punjenja potvrđuje Ponuđač uz potvrdu proizvođača baterija.

## 4. Stablo kod Hamzića

Procjena iz fotografija 08.09.2026 (bez geodetskog snimka): listopadno stablo 7–9 m,
15–20 m JJI–JI od stuba. Sa sredine polja južno od ploče vidi se na azimutu
≈124–149°, do 16–32° visine. Zimi bez lišća propušta ≈pola direktnog zračenja
(pretpostavka). Uz postavke SMU iz Priloga I §4.6:

| 45° | Decembar FN | DEA h/god | Gorivo l/god |
|---|---|---|---|
| bez stabla | 601 kWh | 226 | 746 |
| stablo, povoljna / srednja / nepovoljna procjena | −2,7 / −7,2 / −10,4 % | 231 / 239 / 249 | 764 / 788 / 822 |

Uticaj je mali prema nalazu iz tačke 3, pa stablo ostaje. Detalji:
`hamzici-hybrid-solar/review/pvsim/photo/zasjenjenje.json`.
