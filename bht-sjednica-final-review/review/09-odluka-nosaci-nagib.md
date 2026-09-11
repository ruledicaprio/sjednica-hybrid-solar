# Odluka — nosači, nagib i granice rada agregata (obje lokacije)

Rev 9 · 11.09.2026. · zapisnik odluke Naručioca, na osnovu simulacije `pvsim`
(pvlib + PVGIS-SARAH3, satno 2005–2023). Brojevi su iz `review/pvsim/kpis.json`
ove lokacije i `hamzici-hybrid-solar/review/pvsim/kpis.json`; tabele osjetljivosti u
`energetski-bilans.md` istih foldera.

Sistem je nepromijenjen (odluka Naručioca): 12 × iPV585-M2A = 7,02 kWp, 2 stringa × 6,
PVDB500-15-2B, 2 × iSSU S4875G2, ICC360-HA1-C1 + 6 × ESM-48100A6 (28,8 kWh), FG Wilson
P18-6 u kontejneru, start po SoC preko GIM01C1, ograničenje ispravljača 9,5 kW.
Otvoreno je bilo samo: raspored nosača (3×4 ili 2×6) i nagib (45° ili 60°, „60° ako je
primjenjivo") po lokaciji.

---

## 1. Odluke

| Tema | Odluka |
|---|---|
| Sjednica — nosači i nagib | **3 nosača × 4 modula, 45°** — Rev 8 ostaje; crteži, količine i Prilog I §3 se ne mijenjaju |
| Hamzići — nosači i nagib | **3 nosača × 4 modula, 45°**, kao Sjednica. Uklapanje potvrđeno iz ovjerenog `01_Situacija 1_200.dwg`: zakup 12 000 (I–Z) × 12 500 mm (S–J), ploča 5 400 mm u sredini, strelica sjevera na 0°, pa je južno od ploče **3 525 mm** — polje pri 45° (projekcija 3,24 m, trake 3,30 m) staje uz ≈0,22 m rezerve. 60° (dubina 2,29 m) nije potreban |
| Granice rada agregata (Odluka, Aneks 2) | tvrdnje „≤250 h/god" i „500 l najmanje godinu dana" **zamjenjuju se simuliranim vrijednostima**, uz zahtjev za parametriranje SMU za minimalan rad DEA; tačan tekst Naručilac odobrava prije izmjene |
| Stablo JJI–JI kod Hamzića | **ostaje**; TD bilježi zasjenjenje i traži od Ponuđača da polje pozicionira tako da ga umanji |

## 2. Zašto 45°, a ne 60°

60° daje više u decembru, ali manje u ostatku godine, pa agregat radi **više**:

| | Sjednica 45° | Sjednica 60° | Hamzići 45° | Hamzići 60° |
|---|---|---|---|---|
| FN na DC sabirnici, kWh/god | 10 137 | 9 651 | 10 448 | 9 887 |
| Decembar FN / potrošnja, kWh | 560 / 893 | 617 / 893 | 601 / 893 | 644 / 893 |
| DEA h/god prosjek / P90 (postavke SMU po defaultu) | 356 / 429 | 378 / 459 | 333 / 382 | 353 / 421 |
| Gorivo, l/god | 1 079 | 1 142 | 1 008 | 1 071 |

Baterija od 28,8 kWh je ≈1 dan autonomije: agregat pokriva nizove oblačnih dana u
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
najmanje godinu između dopuna goriva". **Nijedno se ne ostvaruje** ni na jednoj
lokaciji, ni uz jednu ispitanu postavku SMU:

| 45° | DEA h/god prosjek / P90 / najgora | Gorivo l/god | 500 l traje | Startova/god |
|---|---|---|---|---|
| Sjednica, SMU po defaultu (stop SoC 90 %, 0,25 C) | 356 / 429 / 445 | 1 079 | 0,46 god | 113 |
| Sjednica, **preporuka: stop SoC 60 %, punjenje 0,5 C** | 284 / 345 / 359 | 938 | 0,53 god | 165 |
| Sjednica, najmanje sati (stop SoC 40 %, 0,5 C) | 268 / 327 / 349 | 884 | 0,57 god | 262 |
| Hamzići, SMU po defaultu | 333 / 382 / 421 | 1 008 | 0,50 god | 105 |
| Hamzići, **preporuka** | 264 / 307 / 347 | 871 | 0,57 god | 153 |
| Hamzići, najmanje sati | 249 / 294 / 327 | 823 | 0,61 god | 244 |

Već je i sam dosadašnji 07-proračuni C.5 davao ≈925 l/god pri 250 h — dakle 500 l nikad
nije bilo godišnja zaliha. Preporuka (60 % / 0,5 C) je kompromis: ≈20 % manje sati i
≈13 % manje goriva od postavki po defaultu, uz ≈0,45 starta dnevno; 40 % daje još
≈5 % manje, ali udvostručuje broj startova. Punjenje 0,5 C je dozvoljeno samo ako ga
BMS modula ESM-48100A6 prihvata — Ponuđač to potvrđuje.

## 4. Stablo kod Hamzića

Procjena iz fotografija 08.09.2026 (bez geodetskog snimka): listopadno stablo 7–9 m,
15–20 m JJI–JI od stuba. Sa sredine polja južno od ploče vidi se na azimutu
≈124–149°, do 16–32° visine. Zimi bez lišća propušta ≈pola direktnog zračenja
(pretpostavka). Uz postavke SMU iz Priloga I §4.6:

| 45° | Decembar FN | DEA h/god | Gorivo l/god |
|---|---|---|---|
| bez stabla | 601 kWh | 264 | 871 |
| stablo, povoljna / srednja / nepovoljna procjena | −2,7 / −7,2 / −10,4 % | 268 / 273 / 280 | 885 / 902 / 924 |

Uticaj je mali prema nalazu iz tačke 3, pa stablo ostaje. Detalji:
`hamzici-hybrid-solar/review/pvsim/photo/zasjenjenje.json`.
