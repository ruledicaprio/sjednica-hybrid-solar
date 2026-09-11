# Energetski bilans — BS Hamzići (Čitluk)

*Simulacija pvlib + PVGIS-SARAH3, satno 2005–2023. Generisano 2026-09-11, pvsim 0.1.0, commit 4ae2366. Ulazi i pretpostavke: `pvsim/sites/hamzici.json`; brojevi: `kpis.json` u ovom folderu. Ne uređivati ručno — `python -m pvsim report --site hamzici`.*

## Metoda

- **Ozračenje:** PVGIS v5.3 `seriescalc`, SARAH3 + ERA5 (temperatura, vjetar), satno za 19 godina; horizont iz PVGIS DEM-a; polje jug, nagib 45° i 60°.
- **FN lanac:** refleksija Martin-Ruiz (a_r 0,16), temperatura modula Faiman (26,9 / 6,2), model modula Huld c-Si (PVGIS), mjesečno zaprljanje i snijeg, neusklađenost i LID, DC kablovi 0,78 % pri Imp, optimizatori 99,0 %, iSSU S4875G2 po krivulji proizvođača (Vin 330 V), ograničenje 4 kW po modulu.
- **Bilans na −48 V DC sabirnici:** satno, sve godine neprekidno. Baterija 6 × ESM-48100A6 = 28,8 kWh, η punjenja/pražnjenja 97,5 %, punjenje do 0,50 C. DEA preko ispravljača ograničenih na 9,5 kW AC (η 96 %): start pri DOD 85 %, stop pri SoC 60 %, najkraći rad 1,0 h. Gorivo po tehničkom listu P18-6 (prime).
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
| jan | 646 | 893 | 368 | 40,3 | 133 |
| feb | 655 | 812 | 316 | 34,6 | 114 |
| mar | 885 | 892 | 242 | 26,5 | 88 |
| apr | 938 | 865 | 163 | 17,9 | 59 |
| maj | 987 | 899 | 123 | 13,5 | 44 |
| jun | 1 022 | 887 | 63 | 7,0 | 23 |
| jul | 1 122 | 933 | 35 | 3,8 | 13 |
| aug | 1 116 | 932 | 45 | 5,0 | 16 |
| sep | 986 | 878 | 102 | 11,2 | 37 |
| okt | 884 | 896 | 202 | 22,1 | 73 |
| nov | 606 | 864 | 360 | 39,4 | 130 |
| dec | 601 | 893 | 385 | 42,2 | 139 |

## Mjesečni bilans, nagib 60° (prosjek godina)

| Mjesec | FN na sabirnici, kWh | Potrošnja, kWh | DEA (DC), kWh | DEA, h | Gorivo, l |
|---|---|---|---|---|---|
| jan | 687 | 893 | 363 | 39,8 | 131 |
| feb | 671 | 812 | 319 | 35,0 | 116 |
| mar | 860 | 892 | 253 | 27,7 | 91 |
| apr | 863 | 865 | 187 | 20,5 | 68 |
| maj | 863 | 899 | 158 | 17,3 | 57 |
| jun | 868 | 887 | 100 | 11,0 | 36 |
| jul | 961 | 933 | 58 | 6,3 | 21 |
| aug | 1 005 | 932 | 62 | 6,8 | 22 |
| sep | 942 | 878 | 114 | 12,5 | 41 |
| okt | 891 | 896 | 207 | 22,7 | 75 |
| nov | 633 | 864 | 354 | 38,8 | 128 |
| dec | 644 | 893 | 380 | 41,6 | 138 |

## Ključni pokazatelji

| Pokazatelj | 45° | 60° | RFI / Odluka do Rev 9 |
|---|---|---|---|
| FN na DC sabirnici, kWh/god | 10 448 | 9 887 |  |
| Specifični prinos na sabirnici, kWh/kWp | 1 488 | 1 408 |  |
| FN iskorišteno / odbačeno (baterija puna), kWh/god | 8 579 / 1 869 | 8 434 / 1 453 |  |
| Potrošnja, kWh/god | 10 644 | 10 644 |  |
| Solarni udio u potrošnji | 77,4 % | 76,0 % |  |
| Decembar: FN / potrošnja, kWh | 601 / 893 | 644 / 893 |  |
| DEA rad, h/god — prosjek / P90 / najgora god. | 264 / 307 / 347 | 280 / 331 / 357 | ≤250 h/god |
| DEA startova, /god — prosjek / najviše | 153 / 200 | 163 / 206 |  |
| Gorivo, l/god — prosjek / P90 / najgora god. | 871 / 1 015 / 1 145 | 925 / 1 095 / 1 178 |  |
| Spremnik 500 l traje, god — prosjek / najgora | 0,57 / 0,44 | 0,54 / 0,42 | ≥1 god |
| Dopuna goriva, /god — prosjek / najviše | 2,2 / 3 | 2,3 / 3 |  |
| Najduže razdoblje bez rada DEA, dana | 52 | 48 |  |
| Ekvivalentnih ciklusa baterije, /god | 227 | 230 |  |
| Rad DEA ispod 30 % opterećenja, h/god | 0,0 | 0,0 |  |
| Nepokrivena potrošnja, kWh | 0,0 | 0,0 | 0 |
| ≤250 h/god (P90 / najgora god.) | **NIJE ispunjeno** / **NIJE ispunjeno** | **NIJE ispunjeno** / **NIJE ispunjeno** | |
| ≥1 god na spremnik (prosjek / najgora god.) | **NIJE ispunjeno** / **NIJE ispunjeno** | **NIJE ispunjeno** / **NIJE ispunjeno** | |

## Osjetljivost, nagib 45°

| Slučaj | DEA h/god prosjek | P90 | najgora | Gorivo l/god prosjek | najgora | Spremnik traje, god | Startova/god |
|---|---|---|---|---|---|---|---|
| Osnovni slučaj (TD Rev 9): start DOD 85 %, stop SoC 60 %, punjenje 0,5 C | 264 | 307 | 347 | 871 | 1 145 | 0,57 | 153 |
| SMU bez parametriranja: stop SoC 90 %, punjenje 0,25 C | 333 | 382 | 421 | 1 008 | 1 274 | 0,50 | 105 |
| Stop SoC 90 % | 295 | 339 | 376 | 975 | 1 241 | 0,51 | 106 |
| Stop SoC 100 % (punjenje do vrha) | 307 | 350 | 387 | 1 013 | 1 277 | 0,49 | 98 |
| Stop SoC 40 % | 249 | 294 | 327 | 823 | 1 081 | 0,61 | 244 |
| Punjenje 0,25 C | 295 | 345 | 386 | 904 | 1 185 | 0,55 | 153 |
| Punjenje 0,15 C | 465 | 537 | 592 | 1 071 | 1 373 | 0,47 | 145 |
| Start pri DOD 70 % | 279 | 330 | 348 | 922 | 1 149 | 0,54 | 237 |
| Potrošnja 1180 W stalno (bez hlađenja i pomoćne) | 254 | 295 | 335 | 838 | 1 107 | 0,60 | 148 |
| Potrošnja 1330 W stalno | 332 | 389 | 416 | 1 097 | 1 373 | 0,46 | 190 |

## Osjetljivost, nagib 60°

| Slučaj | DEA h/god prosjek | P90 | najgora | Gorivo l/god prosjek | najgora | Spremnik traje, god | Startova/god |
|---|---|---|---|---|---|---|---|
| Osnovni slučaj (TD Rev 9): start DOD 85 %, stop SoC 60 %, punjenje 0,5 C | 280 | 331 | 357 | 925 | 1 178 | 0,54 | 163 |
| SMU bez parametriranja: stop SoC 90 %, punjenje 0,25 C | 353 | 421 | 430 | 1 071 | 1 309 | 0,47 | 112 |
| Stop SoC 90 % | 313 | 373 | 384 | 1 035 | 1 269 | 0,48 | 113 |
| Stop SoC 100 % (punjenje do vrha) | 327 | 386 | 400 | 1 076 | 1 317 | 0,46 | 104 |
| Stop SoC 40 % | 263 | 312 | 342 | 870 | 1 128 | 0,57 | 258 |
| Punjenje 0,25 C | 313 | 369 | 394 | 958 | 1 213 | 0,52 | 162 |
| Punjenje 0,15 C | 491 | 581 | 621 | 1 133 | 1 445 | 0,44 | 153 |
| Start pri DOD 70 % | 296 | 342 | 372 | 978 | 1 229 | 0,51 | 251 |
| Potrošnja 1180 W stalno (bez hlađenja i pomoćne) | 267 | 313 | 347 | 881 | 1 147 | 0,57 | 156 |
| Potrošnja 1330 W stalno | 352 | 409 | 431 | 1 163 | 1 423 | 0,43 | 202 |

## Zaključak (izveden iz brojeva iznad)

- **45°:** DEA 264 h/god u prosjeku (P90 307), gorivo 871 l/god. Najpovoljniji slučaj osjetljivosti za sate (Stop SoC 40 %) daje P90 294 h/god; za gorivo (Stop SoC 40 %) 823 l/god, tj. spremnik 500 l traje 0,61 god.
- **60°:** DEA 280 h/god u prosjeku (P90 331), gorivo 925 l/god. Najpovoljniji slučaj osjetljivosti za sate (Stop SoC 40 %) daje P90 312 h/god; za gorivo (Stop SoC 40 %) 870 l/god, tj. spremnik 500 l traje 0,57 god.

