# Energetski bilans — BS Sjednica (Bileća)

*Simulacija pvlib + PVGIS-SARAH3, satno 2005–2023. Generisano 2026-09-11, pvsim 0.1.0, commit 4d4cbcb. Ulazi i pretpostavke: `pvsim/sites/sjednica.json`; brojevi: `kpis.json` u ovom folderu. Ne uređivati ručno — `python -m pvsim report --site sjednica`.*

## Metoda

- **Ozračenje:** PVGIS v5.3 `seriescalc`, SARAH3 + ERA5 (temperatura, vjetar), satno za 19 godina; horizont iz PVGIS DEM-a; polje jug, nagib 45° i 60°.
- **FN lanac:** refleksija Martin-Ruiz (a_r 0,16), temperatura modula Faiman (26,9 / 6,2), model modula Huld c-Si (PVGIS), mjesečno zaprljanje i snijeg, neusklađenost i LID, DC kablovi 0,78 % pri Imp, optimizatori 99,0 %, iSSU S4875G2 po krivulji proizvođača (Vin 330 V), ograničenje 4 kW po modulu.
- **Bilans na −48 V DC sabirnici:** satno, sve godine neprekidno. Baterija 6 × ESM-48100A6 = 28,8 kWh, η punjenja/pražnjenja 97,5 %, punjenje do 0,25 C. DEA preko ispravljača ograničenih na 9,5 kW AC (η 96 %): start pri DOD 85 %, stop pri SoC 90 %, najkraći rad 1,0 h. Gorivo po tehničkom listu P18-6 (prime).
- **Potrošnja:** 1180 W TK + 20 W pomoćna (SMU, BMS, ventilatori) + hlađenje ormara do 150 W (linearno 20→35 °C).
- Parametri bez podatka proizvođača (efikasnost i punjenje baterije, stop SoC, zaprljanje, snijeg, hlađenje) su pretpostavke, označene u ulaznom fajlu; njihov uticaj je u tabeli osjetljivosti.

## Validacija prema PVGIS-u

| Nagib | PVcalc, kWh/god | pvsim s PVGIS gubicima 14 %, kWh/god | najveće mjesečno odstupanje | satna korelacija s PVGIS P |
|---|---|---|---|---|
| 45° | 9 692 | 9 621 | 2,0 % | 1,0000 |
| 60° | 9 173 | 9 096 | 2,0 % | 1,0000 |

## Gubici FN lanca (prosjek godine)

| Stavka | 45°, kWh | 60°, kWh | 45°, gubitak | 60°, gubitak |
|---|---|---|---|---|
| Ozračenje u ravni × kWp (STC) | 12 280 | 11 595 |  |  |
| Refleksija (IAM) | 11 920 | 11 235 | −2,94 % | −3,10 % |
| Temperatura i slabo svjetlo (Huld) | 11 187 | 10 576 | −6,15 % | −5,86 % |
| Zaprljanje | 10 993 | 10 397 | −1,73 % | −1,70 % |
| Snijeg | 10 806 | 10 301 | −1,70 % | −0,93 % |
| Neusklađenost + LID | 10 720 | 10 218 | −0,80 % | −0,80 % |
| DC kablovi | 10 669 | 10 171 | −0,47 % | −0,46 % |
| Optimizatori | 10 562 | 10 069 | −1,00 % | −1,00 % |
| iSSU S4875G2 (krivulja) | 10 137 | 9 651 | −4,02 % | −4,16 % |
| iSSU ograničenje 4 kW | 10 137 | 9 651 | −0,00 % | −0,00 % |

## Mjesečni bilans, nagib 45° (prosjek godina)

| Mjesec | FN na sabirnici, kWh | Potrošnja, kWh | DEA (DC), kWh | DEA, h | Gorivo, l |
|---|---|---|---|---|---|
| jan | 591 | 893 | 429 | 52,7 | 161 |
| feb | 632 | 812 | 343 | 42,2 | 129 |
| mar | 853 | 892 | 288 | 35,5 | 108 |
| apr | 892 | 864 | 209 | 25,8 | 78 |
| maj | 949 | 895 | 176 | 21,9 | 66 |
| jun | 999 | 874 | 98 | 12,7 | 37 |
| jul | 1 108 | 913 | 53 | 7,0 | 20 |
| aug | 1 092 | 912 | 65 | 8,5 | 25 |
| sep | 957 | 869 | 154 | 19,1 | 58 |
| okt | 890 | 894 | 228 | 28,1 | 86 |
| nov | 613 | 864 | 380 | 47,5 | 143 |
| dec | 560 | 893 | 440 | 54,7 | 166 |

## Mjesečni bilans, nagib 60° (prosjek godina)

| Mjesec | FN na sabirnici, kWh | Potrošnja, kWh | DEA (DC), kWh | DEA, h | Gorivo, l |
|---|---|---|---|---|---|
| jan | 652 | 893 | 414 | 51,1 | 156 |
| feb | 663 | 812 | 341 | 42,4 | 128 |
| mar | 839 | 892 | 296 | 36,2 | 111 |
| apr | 821 | 864 | 232 | 28,8 | 87 |
| maj | 828 | 895 | 215 | 26,9 | 81 |
| jun | 848 | 874 | 139 | 17,7 | 53 |
| jul | 948 | 913 | 93 | 12,0 | 36 |
| aug | 981 | 912 | 99 | 13,0 | 38 |
| sep | 911 | 869 | 171 | 21,6 | 65 |
| okt | 896 | 894 | 233 | 28,9 | 88 |
| nov | 647 | 864 | 375 | 46,5 | 141 |
| dec | 617 | 893 | 420 | 52,5 | 159 |

## Ključni pokazatelji

| Pokazatelj | 45° | 60° | Granica (Odluka) |
|---|---|---|---|
| FN na DC sabirnici, kWh/god | 10 137 | 9 651 |  |
| Specifični prinos na sabirnici, kWh/kWp | 1 444 | 1 375 |  |
| FN iskorišteno / odbačeno (baterija puna), kWh/god | 8 046 / 2 092 | 7 885 / 1 766 |  |
| Potrošnja, kWh/god | 10 575 | 10 575 |  |
| Solarni udio u potrošnji | 72,9 % | 71,4 % |  |
| Decembar: FN / potrošnja, kWh | 560 / 893 | 617 / 893 |  |
| DEA rad, h/god — prosjek / P90 / najgora god. | 356 / 429 / 445 | 378 / 459 / 462 | ≤250 h/god |
| DEA startova, /god — prosjek / najviše | 113 / 141 | 120 / 146 |  |
| Gorivo, l/god — prosjek / P90 / najgora god. | 1 079 / 1 300 / 1 341 | 1 142 / 1 389 / 1 408 |  |
| Spremnik 500 l traje, god — prosjek / najgora | 0,46 / 0,37 | 0,44 / 0,36 | ≥1 god |
| Dopuna goriva, /god — prosjek / najviše | 2,7 / 3 | 2,8 / 4 |  |
| Najduže razdoblje bez rada DEA, dana | 67 | 33 |  |
| Ekvivalentnih ciklusa baterije, /god | 224 | 226 |  |
| Rad DEA ispod 30 % opterećenja, h/god | 2,6 | 4,3 |  |
| Nepokrivena potrošnja, kWh | 0,0 | 0,0 | 0 |
| ≤250 h/god (P90 / najgora god.) | **NIJE ispunjeno** / **NIJE ispunjeno** | **NIJE ispunjeno** / **NIJE ispunjeno** | |
| ≥1 god na spremnik (prosjek / najgora god.) | **NIJE ispunjeno** / **NIJE ispunjeno** | **NIJE ispunjeno** / **NIJE ispunjeno** | |

## Osjetljivost, nagib 45°

| Slučaj | DEA h/god prosjek | P90 | najgora | Gorivo l/god prosjek | najgora | Spremnik traje, god | Startova/god |
|---|---|---|---|---|---|---|---|
| Osnovni slučaj: start DOD 85 %, stop SoC 90 %, punjenje 0,25 C | 356 | 429 | 445 | 1 079 | 1 341 | 0,46 | 113 |
| Stop SoC 100 % (punjenje do vrha) | 369 | 449 | 453 | 1 116 | 1 377 | 0,45 | 104 |
| Stop SoC 60 % | 317 | 386 | 403 | 972 | 1 239 | 0,51 | 165 |
| Stop SoC 40 % | 294 | 359 | 388 | 905 | 1 195 | 0,55 | 265 |
| Punjenje 0,15 C | 563 | 678 | 696 | 1 269 | 1 578 | 0,39 | 107 |
| Punjenje 0,5 C | 317 | 380 | 392 | 1 046 | 1 294 | 0,48 | 114 |
| Stop SoC 40 % + punjenje 0,5 C | 268 | 327 | 349 | 884 | 1 152 | 0,57 | 262 |
| PREPORUKA TD: stop SoC 60 % + punjenje 0,5 C | 284 | 345 | 359 | 938 | 1 187 | 0,53 | 165 |
| Start pri DOD 70 % | 388 | 458 | 469 | 1 168 | 1 418 | 0,43 | 153 |
| Potrošnja 1180 W stalno (bez hlađenja i pomoćne) | 343 | 416 | 427 | 1 037 | 1 311 | 0,48 | 109 |
| Potrošnja 1330 W stalno | 449 | 523 | 540 | 1 364 | 1 647 | 0,37 | 142 |

## Osjetljivost, nagib 60°

| Slučaj | DEA h/god prosjek | P90 | najgora | Gorivo l/god prosjek | najgora | Spremnik traje, god | Startova/god |
|---|---|---|---|---|---|---|---|
| Osnovni slučaj: start DOD 85 %, stop SoC 90 %, punjenje 0,25 C | 378 | 459 | 462 | 1 142 | 1 408 | 0,44 | 120 |
| Stop SoC 100 % (punjenje do vrha) | 393 | 472 | 486 | 1 185 | 1 467 | 0,42 | 110 |
| Stop SoC 60 % | 335 | 406 | 431 | 1 026 | 1 323 | 0,49 | 174 |
| Stop SoC 40 % | 310 | 381 | 404 | 956 | 1 246 | 0,52 | 280 |
| Punjenje 0,15 C | 599 | 717 | 760 | 1 348 | 1 709 | 0,37 | 114 |
| Punjenje 0,5 C | 335 | 404 | 416 | 1 108 | 1 372 | 0,45 | 121 |
| Stop SoC 40 % + punjenje 0,5 C | 282 | 346 | 369 | 933 | 1 219 | 0,54 | 277 |
| PREPORUKA TD: stop SoC 60 % + punjenje 0,5 C | 300 | 366 | 387 | 991 | 1 278 | 0,50 | 175 |
| Start pri DOD 70 % | 412 | 476 | 504 | 1 238 | 1 521 | 0,40 | 162 |
| Potrošnja 1180 W stalno (bez hlađenja i pomoćne) | 359 | 440 | 443 | 1 088 | 1 349 | 0,46 | 114 |
| Potrošnja 1330 W stalno | 479 | 553 | 586 | 1 451 | 1 789 | 0,34 | 151 |

## Zaključak (izveden iz brojeva iznad)

- **45°:** DEA 356 h/god u prosjeku (P90 429), gorivo 1 079 l/god. Najpovoljniji slučaj osjetljivosti za sate (Stop SoC 40 % + punjenje 0,5 C) daje P90 327 h/god; za gorivo (Stop SoC 40 % + punjenje 0,5 C) 884 l/god, tj. spremnik 500 l traje 0,57 god.
- **60°:** DEA 378 h/god u prosjeku (P90 459), gorivo 1 142 l/god. Najpovoljniji slučaj osjetljivosti za sate (Stop SoC 40 % + punjenje 0,5 C) daje P90 346 h/god; za gorivo (Stop SoC 40 % + punjenje 0,5 C) 933 l/god, tj. spremnik 500 l traje 0,54 god.

