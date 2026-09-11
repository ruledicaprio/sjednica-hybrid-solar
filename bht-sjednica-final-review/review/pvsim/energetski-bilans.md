# Energetski bilans — BS Sjednica (Bileća)

*Simulacija pvlib + PVGIS-SARAH3, satno 2005–2023. Generisano 2026-09-11, pvsim 0.1.0, commit 4ae2366. Ulazi i pretpostavke: `pvsim/sites/sjednica.json`; brojevi: `kpis.json` u ovom folderu. Ne uređivati ručno — `python -m pvsim report --site sjednica`.*

## Metoda

- **Ozračenje:** PVGIS v5.3 `seriescalc`, SARAH3 + ERA5 (temperatura, vjetar), satno za 19 godina; horizont iz PVGIS DEM-a; polje jug, nagib 45° i 60°.
- **FN lanac:** refleksija Martin-Ruiz (a_r 0,16), temperatura modula Faiman (26,9 / 6,2), model modula Huld c-Si (PVGIS), mjesečno zaprljanje i snijeg, neusklađenost i LID, DC kablovi 0,78 % pri Imp, optimizatori 99,0 %, iSSU S4875G2 po krivulji proizvođača (Vin 330 V), ograničenje 4 kW po modulu.
- **Bilans na −48 V DC sabirnici:** satno, sve godine neprekidno. Baterija 6 × ESM-48100A6 = 28,8 kWh, η punjenja/pražnjenja 97,5 %, punjenje do 0,50 C. DEA preko ispravljača ograničenih na 9,5 kW AC (η 96 %): start pri DOD 85 %, stop pri SoC 60 %, najkraći rad 1,0 h. Gorivo po tehničkom listu P18-6 (prime).
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
| jan | 591 | 893 | 403 | 44,2 | 146 |
| feb | 632 | 812 | 325 | 35,6 | 118 |
| mar | 853 | 892 | 261 | 28,6 | 94 |
| apr | 892 | 864 | 184 | 20,2 | 67 |
| maj | 949 | 895 | 140 | 15,3 | 51 |
| jun | 999 | 874 | 82 | 9,0 | 30 |
| jul | 1 108 | 913 | 40 | 4,4 | 15 |
| aug | 1 092 | 912 | 51 | 5,6 | 19 |
| sep | 957 | 869 | 126 | 13,8 | 45 |
| okt | 890 | 894 | 208 | 22,8 | 75 |
| nov | 613 | 864 | 356 | 39,0 | 129 |
| dec | 560 | 893 | 416 | 45,6 | 151 |

## Mjesečni bilans, nagib 60° (prosjek godina)

| Mjesec | FN na sabirnici, kWh | Potrošnja, kWh | DEA (DC), kWh | DEA, h | Gorivo, l |
|---|---|---|---|---|---|
| jan | 652 | 893 | 388 | 42,5 | 140 |
| feb | 663 | 812 | 328 | 35,9 | 119 |
| mar | 839 | 892 | 268 | 29,4 | 97 |
| apr | 821 | 864 | 206 | 22,5 | 74 |
| maj | 828 | 895 | 180 | 19,8 | 65 |
| jun | 848 | 874 | 114 | 12,5 | 41 |
| jul | 948 | 913 | 70 | 7,7 | 26 |
| aug | 981 | 912 | 76 | 8,3 | 27 |
| sep | 911 | 869 | 141 | 15,4 | 51 |
| okt | 896 | 894 | 215 | 23,6 | 78 |
| nov | 647 | 864 | 352 | 38,5 | 127 |
| dec | 617 | 893 | 400 | 43,9 | 145 |

## Ključni pokazatelji

| Pokazatelj | 45° | 60° | RFI / Odluka do Rev 9 |
|---|---|---|---|
| FN na DC sabirnici, kWh/god | 10 137 | 9 651 |  |
| Specifični prinos na sabirnici, kWh/kWp | 1 444 | 1 375 |  |
| FN iskorišteno / odbačeno (baterija puna), kWh/god | 8 323 / 1 815 | 8 180 / 1 471 |  |
| Potrošnja, kWh/god | 10 575 | 10 575 |  |
| Solarni udio u potrošnji | 75,5 % | 74,1 % |  |
| Decembar: FN / potrošnja, kWh | 560 / 893 | 617 / 893 |  |
| DEA rad, h/god — prosjek / P90 / najgora god. | 284 / 345 / 359 | 300 / 366 / 387 | ≤250 h/god |
| DEA startova, /god — prosjek / najviše | 165 / 208 | 175 / 225 |  |
| Gorivo, l/god — prosjek / P90 / najgora god. | 938 / 1 140 / 1 187 | 991 / 1 208 / 1 278 |  |
| Spremnik 500 l traje, god — prosjek / najgora | 0,53 / 0,42 | 0,50 / 0,39 | ≥1 god |
| Dopuna goriva, /god — prosjek / najviše | 2,4 / 3 | 2,5 / 3 |  |
| Najduže razdoblje bez rada DEA, dana | 67 | 32 |  |
| Ekvivalentnih ciklusa baterije, /god | 227 | 229 |  |
| Rad DEA ispod 30 % opterećenja, h/god | 0,0 | 0,0 |  |
| Nepokrivena potrošnja, kWh | 0,0 | 0,0 | 0 |
| ≤250 h/god (P90 / najgora god.) | **NIJE ispunjeno** / **NIJE ispunjeno** | **NIJE ispunjeno** / **NIJE ispunjeno** | |
| ≥1 god na spremnik (prosjek / najgora god.) | **NIJE ispunjeno** / **NIJE ispunjeno** | **NIJE ispunjeno** / **NIJE ispunjeno** | |

## Osjetljivost, nagib 45°

| Slučaj | DEA h/god prosjek | P90 | najgora | Gorivo l/god prosjek | najgora | Spremnik traje, god | Startova/god |
|---|---|---|---|---|---|---|---|
| Osnovni slučaj (TD Rev 9): start DOD 85 %, stop SoC 60 %, punjenje 0,5 C | 284 | 345 | 359 | 938 | 1 187 | 0,53 | 165 |
| SMU bez parametriranja: stop SoC 90 %, punjenje 0,25 C | 356 | 429 | 445 | 1 079 | 1 341 | 0,46 | 113 |
| Stop SoC 90 % | 317 | 380 | 392 | 1 046 | 1 294 | 0,48 | 114 |
| Stop SoC 100 % (punjenje do vrha) | 328 | 397 | 405 | 1 079 | 1 332 | 0,46 | 104 |
| Stop SoC 40 % | 268 | 327 | 349 | 884 | 1 152 | 0,57 | 262 |
| Punjenje 0,25 C | 317 | 386 | 403 | 972 | 1 239 | 0,51 | 165 |
| Punjenje 0,15 C | 497 | 604 | 623 | 1 149 | 1 457 | 0,44 | 155 |
| Start pri DOD 70 % | 298 | 358 | 380 | 984 | 1 256 | 0,51 | 252 |
| Potrošnja 1180 W stalno (bez hlađenja i pomoćne) | 273 | 333 | 353 | 901 | 1 167 | 0,55 | 160 |
| Potrošnja 1330 W stalno | 358 | 426 | 448 | 1 182 | 1 480 | 0,42 | 205 |

## Osjetljivost, nagib 60°

| Slučaj | DEA h/god prosjek | P90 | najgora | Gorivo l/god prosjek | najgora | Spremnik traje, god | Startova/god |
|---|---|---|---|---|---|---|---|
| Osnovni slučaj (TD Rev 9): start DOD 85 %, stop SoC 60 %, punjenje 0,5 C | 300 | 366 | 387 | 991 | 1 278 | 0,50 | 175 |
| SMU bez parametriranja: stop SoC 90 %, punjenje 0,25 C | 378 | 459 | 462 | 1 142 | 1 408 | 0,44 | 120 |
| Stop SoC 90 % | 335 | 404 | 416 | 1 108 | 1 372 | 0,45 | 121 |
| Stop SoC 100 % (punjenje do vrha) | 348 | 418 | 433 | 1 145 | 1 424 | 0,44 | 111 |
| Stop SoC 40 % | 282 | 346 | 369 | 933 | 1 219 | 0,54 | 277 |
| Punjenje 0,25 C | 335 | 406 | 431 | 1 026 | 1 323 | 0,49 | 174 |
| Punjenje 0,15 C | 525 | 639 | 676 | 1 212 | 1 564 | 0,41 | 164 |
| Start pri DOD 70 % | 314 | 379 | 403 | 1 039 | 1 331 | 0,48 | 266 |
| Potrošnja 1180 W stalno (bez hlađenja i pomoćne) | 285 | 348 | 364 | 943 | 1 204 | 0,53 | 167 |
| Potrošnja 1330 W stalno | 380 | 454 | 481 | 1 254 | 1 590 | 0,40 | 218 |

## Zaključak (izveden iz brojeva iznad)

- **45°:** DEA 284 h/god u prosjeku (P90 345), gorivo 938 l/god. Najpovoljniji slučaj osjetljivosti za sate (Stop SoC 40 %) daje P90 327 h/god; za gorivo (Stop SoC 40 %) 884 l/god, tj. spremnik 500 l traje 0,57 god.
- **60°:** DEA 300 h/god u prosjeku (P90 366), gorivo 991 l/god. Najpovoljniji slučaj osjetljivosti za sate (Stop SoC 40 %) daje P90 346 h/god; za gorivo (Stop SoC 40 %) 933 l/god, tj. spremnik 500 l traje 0,54 god.

