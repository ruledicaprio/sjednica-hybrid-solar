# Energetski bilans — BS Hamzići (Čitluk)

*Simulacija pvlib + PVGIS-SARAH3, satno 2005–2023. Generisano 2026-09-11, pvsim 0.1.0, commit 4d4cbcb. Ulazi i pretpostavke: `pvsim/sites/hamzici.json`; brojevi: `kpis.json` u ovom folderu. Ne uređivati ručno — `python -m pvsim report --site hamzici`.*

## Metoda

- **Ozračenje:** PVGIS v5.3 `seriescalc`, SARAH3 + ERA5 (temperatura, vjetar), satno za 19 godina; horizont iz PVGIS DEM-a; polje jug, nagib 45° i 60°.
- **FN lanac:** refleksija Martin-Ruiz (a_r 0,16), temperatura modula Faiman (26,9 / 6,2), model modula Huld c-Si (PVGIS), mjesečno zaprljanje i snijeg, neusklađenost i LID, DC kablovi 0,78 % pri Imp, optimizatori 99,0 %, iSSU S4875G2 po krivulji proizvođača (Vin 330 V), ograničenje 4 kW po modulu.
- **Bilans na −48 V DC sabirnici:** satno, sve godine neprekidno. Baterija 6 × ESM-48100A6 = 28,8 kWh, η punjenja/pražnjenja 97,5 %, punjenje do 0,25 C. DEA preko ispravljača ograničenih na 9,5 kW AC (η 96 %): start pri DOD 85 %, stop pri SoC 90 %, najkraći rad 1,0 h. Gorivo po tehničkom listu P18-6 (prime).
- **Potrošnja:** 1180 W TK + 20 W pomoćna (SMU, BMS, ventilatori) + hlađenje ormara do 150 W (linearno 20→35 °C).
- Parametri bez podatka proizvođača (efikasnost i punjenje baterije, stop SoC, zaprljanje, snijeg, hlađenje) su pretpostavke, označene u ulaznom fajlu; njihov uticaj je u tabeli osjetljivosti.

## Validacija prema PVGIS-u

| Nagib | PVcalc, kWh/god | pvsim s PVGIS gubicima 14 %, kWh/god | najveće mjesečno odstupanje | satna korelacija s PVGIS P |
|---|---|---|---|---|
| 45° | 9 840 | 9 780 | 2,2 % | 1,0000 |
| 60° | 9 322 | 9 256 | 2,1 % | 1,0000 |

## Gubici FN lanca (prosjek godine)

| Stavka | 45°, kWh | 60°, kWh | 45°, gubitak | 60°, gubitak |
|---|---|---|---|---|
| Ozračenje u ravni × kWp (STC) | 12 727 | 12 024 |  |  |
| Refleksija (IAM) | 12 368 | 11 661 | −2,82 % | −3,01 % |
| Temperatura i slabo svjetlo (Huld) | 11 372 | 10 762 | −8,05 % | −7,71 % |
| Zaprljanje | 11 146 | 10 553 | −1,99 % | −1,94 % |
| Snijeg | 11 129 | 10 544 | −0,15 % | −0,09 % |
| Neusklađenost + LID | 11 040 | 10 460 | −0,80 % | −0,80 % |
| DC kablovi | 10 987 | 10 412 | −0,48 % | −0,47 % |
| Optimizatori | 10 878 | 10 307 | −1,00 % | −1,00 % |
| iSSU S4875G2 (krivulja) | 10 448 | 9 887 | −3,95 % | −4,08 % |
| iSSU ograničenje 4 kW | 10 448 | 9 887 | −0,00 % | −0,00 % |

## Mjesečni bilans, nagib 45° (prosjek godina)

| Mjesec | FN na sabirnici, kWh | Potrošnja, kWh | DEA (DC), kWh | DEA, h | Gorivo, l |
|---|---|---|---|---|---|
| jan | 646 | 893 | 402 | 50,1 | 152 |
| feb | 655 | 812 | 332 | 41,7 | 126 |
| mar | 885 | 892 | 263 | 32,6 | 99 |
| apr | 938 | 865 | 192 | 23,5 | 72 |
| maj | 987 | 899 | 147 | 18,2 | 55 |
| jun | 1 022 | 887 | 79 | 10,1 | 30 |
| jul | 1 122 | 933 | 49 | 6,5 | 19 |
| aug | 1 116 | 932 | 57 | 7,5 | 22 |
| sep | 986 | 878 | 127 | 16,1 | 48 |
| okt | 884 | 896 | 227 | 27,9 | 85 |
| nov | 606 | 864 | 385 | 47,7 | 145 |
| dec | 601 | 893 | 413 | 51,1 | 155 |

## Mjesečni bilans, nagib 60° (prosjek godina)

| Mjesec | FN na sabirnici, kWh | Potrošnja, kWh | DEA (DC), kWh | DEA, h | Gorivo, l |
|---|---|---|---|---|---|
| jan | 687 | 893 | 395 | 49,0 | 149 |
| feb | 671 | 812 | 334 | 42,2 | 127 |
| mar | 860 | 892 | 274 | 34,0 | 103 |
| apr | 863 | 865 | 208 | 25,9 | 78 |
| maj | 863 | 899 | 188 | 23,6 | 71 |
| jun | 868 | 887 | 127 | 16,3 | 48 |
| jul | 961 | 933 | 77 | 10,1 | 30 |
| aug | 1 005 | 932 | 77 | 9,8 | 29 |
| sep | 942 | 878 | 141 | 17,6 | 53 |
| okt | 891 | 896 | 232 | 28,5 | 87 |
| nov | 633 | 864 | 382 | 46,9 | 143 |
| dec | 644 | 893 | 404 | 49,7 | 152 |

## Ključni pokazatelji

| Pokazatelj | 45° | 60° | Granica (Odluka) |
|---|---|---|---|
| FN na DC sabirnici, kWh/god | 10 448 | 9 887 |  |
| Specifični prinos na sabirnici, kWh/kWp | 1 488 | 1 408 |  |
| FN iskorišteno / odbačeno (baterija puna), kWh/god | 8 306 / 2 142 | 8 144 / 1 743 |  |
| Potrošnja, kWh/god | 10 644 | 10 644 |  |
| Solarni udio u potrošnji | 74,9 % | 73,3 % |  |
| Decembar: FN / potrošnja, kWh | 601 / 893 | 644 / 893 |  |
| DEA rad, h/god — prosjek / P90 / najgora god. | 333 / 382 / 421 | 353 / 421 / 430 | ≤250 h/god |
| DEA startova, /god — prosjek / najviše | 105 / 133 | 112 / 136 |  |
| Gorivo, l/god — prosjek / P90 / najgora god. | 1 008 / 1 158 / 1 274 | 1 071 / 1 276 / 1 309 |  |
| Spremnik 500 l traje, god — prosjek / najgora | 0,50 / 0,39 | 0,47 / 0,38 | ≥1 god |
| Dopuna goriva, /god — prosjek / najviše | 2,5 / 3 | 2,7 / 3 |  |
| Najduže razdoblje bez rada DEA, dana | 52 | 48 |  |
| Ekvivalentnih ciklusa baterije, /god | 224 | 227 |  |
| Rad DEA ispod 30 % opterećenja, h/god | 3,6 | 3,3 |  |
| Nepokrivena potrošnja, kWh | 0,0 | 0,0 | 0 |
| ≤250 h/god (P90 / najgora god.) | **NIJE ispunjeno** / **NIJE ispunjeno** | **NIJE ispunjeno** / **NIJE ispunjeno** | |
| ≥1 god na spremnik (prosjek / najgora god.) | **NIJE ispunjeno** / **NIJE ispunjeno** | **NIJE ispunjeno** / **NIJE ispunjeno** | |

## Osjetljivost, nagib 45°

| Slučaj | DEA h/god prosjek | P90 | najgora | Gorivo l/god prosjek | najgora | Spremnik traje, god | Startova/god |
|---|---|---|---|---|---|---|---|
| Osnovni slučaj: start DOD 85 %, stop SoC 90 %, punjenje 0,25 C | 333 | 382 | 421 | 1 008 | 1 274 | 0,50 | 105 |
| Stop SoC 100 % (punjenje do vrha) | 346 | 392 | 440 | 1 046 | 1 331 | 0,48 | 97 |
| Stop SoC 60 % | 295 | 345 | 386 | 904 | 1 185 | 0,55 | 153 |
| Stop SoC 40 % | 274 | 324 | 362 | 843 | 1 117 | 0,59 | 247 |
| Punjenje 0,15 C | 524 | 594 | 659 | 1 187 | 1 502 | 0,42 | 100 |
| Punjenje 0,5 C | 295 | 339 | 376 | 975 | 1 241 | 0,51 | 106 |
| Stop SoC 40 % + punjenje 0,5 C | 249 | 294 | 327 | 823 | 1 081 | 0,61 | 244 |
| PREPORUKA TD: stop SoC 60 % + punjenje 0,5 C | 264 | 307 | 347 | 871 | 1 145 | 0,57 | 153 |
| Start pri DOD 70 % | 368 | 427 | 434 | 1 105 | 1 318 | 0,45 | 145 |
| Potrošnja 1180 W stalno (bez hlađenja i pomoćne) | 317 | 367 | 399 | 960 | 1 208 | 0,52 | 100 |
| Potrošnja 1330 W stalno | 420 | 491 | 499 | 1 271 | 1 521 | 0,39 | 132 |

## Osjetljivost, nagib 60°

| Slučaj | DEA h/god prosjek | P90 | najgora | Gorivo l/god prosjek | najgora | Spremnik traje, god | Startova/god |
|---|---|---|---|---|---|---|---|
| Osnovni slučaj: start DOD 85 %, stop SoC 90 %, punjenje 0,25 C | 353 | 421 | 430 | 1 071 | 1 309 | 0,47 | 112 |
| Stop SoC 100 % (punjenje do vrha) | 368 | 435 | 453 | 1 111 | 1 376 | 0,45 | 103 |
| Stop SoC 60 % | 313 | 369 | 394 | 958 | 1 213 | 0,52 | 162 |
| Stop SoC 40 % | 290 | 344 | 376 | 892 | 1 158 | 0,56 | 261 |
| Punjenje 0,15 C | 557 | 651 | 680 | 1 259 | 1 555 | 0,40 | 106 |
| Punjenje 0,5 C | 313 | 373 | 384 | 1 035 | 1 269 | 0,48 | 113 |
| Stop SoC 40 % + punjenje 0,5 C | 263 | 312 | 342 | 870 | 1 128 | 0,57 | 258 |
| PREPORUKA TD: stop SoC 60 % + punjenje 0,5 C | 280 | 331 | 357 | 925 | 1 178 | 0,54 | 163 |
| Start pri DOD 70 % | 393 | 446 | 477 | 1 180 | 1 444 | 0,42 | 155 |
| Potrošnja 1180 W stalno (bez hlađenja i pomoćne) | 333 | 383 | 411 | 1 006 | 1 254 | 0,50 | 105 |
| Potrošnja 1330 W stalno | 448 | 519 | 542 | 1 355 | 1 645 | 0,37 | 141 |

## Zaključak (izveden iz brojeva iznad)

- **45°:** DEA 333 h/god u prosjeku (P90 382), gorivo 1 008 l/god. Najpovoljniji slučaj osjetljivosti za sate (Stop SoC 40 % + punjenje 0,5 C) daje P90 294 h/god; za gorivo (Stop SoC 40 % + punjenje 0,5 C) 823 l/god, tj. spremnik 500 l traje 0,61 god.
- **60°:** DEA 353 h/god u prosjeku (P90 421), gorivo 1 071 l/god. Najpovoljniji slučaj osjetljivosti za sate (Stop SoC 40 % + punjenje 0,5 C) daje P90 312 h/god; za gorivo (Stop SoC 40 % + punjenje 0,5 C) 870 l/god, tj. spremnik 500 l traje 0,57 god.

