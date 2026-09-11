# Energetski bilans — BS Hamzići (Čitluk)

*Simulacija pvlib + PVGIS-SARAH3, satno 2005–2023. Generisano 2026-09-11, pvsim 0.1.0, commit b6d6f60. Ulazi i pretpostavke: `pvsim/sites/hamzici.json`; brojevi: `kpis.json` u ovom folderu. Ne uređivati ručno — `python -m pvsim report --site hamzici`.*

## Metoda

- **Ozračenje:** PVGIS v5.3 `seriescalc`, SARAH3 + ERA5 (temperatura, vjetar), satno za 19 godina; horizont iz PVGIS DEM-a; polje jug, nagib 45° i 60°.
- **FN lanac:** refleksija Martin-Ruiz (a_r 0,16), temperatura modula Faiman (26,9 / 6,2), model modula Huld c-Si (PVGIS), mjesečno zaprljanje i snijeg, neusklađenost i LID, DC kablovi 0,78 % pri Imp, optimizatori 99,0 %, iSSU S4875G2 po krivulji proizvođača (Vin 330 V), ograničenje 4 kW po modulu.
- **Bilans na −48 V DC sabirnici:** satno, sve godine neprekidno. Baterija 6 × 150 Ah LFP = 48,6 kWh, η punjenja/pražnjenja 97,5 %, punjenje do 0,50 C. DEA preko ispravljača ograničenih na 9,5 kW AC (η 96 %): start pri DOD 85 %, stop pri SoC 60 %, najkraći rad 1,0 h. Gorivo po tehničkom listu P18-6 (prime).
- **Potrošnja:** 1180 W TK + 45 W pomoćna (SMU, BMS, ventilatori) + hlađenje ormara do 150 W (linearno 20→35 °C).
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
| jan | 646 | 911 | 335 | 36,8 | 122 |
| feb | 655 | 829 | 287 | 31,4 | 104 |
| mar | 885 | 910 | 210 | 23,0 | 76 |
| apr | 938 | 883 | 127 | 14,0 | 46 |
| maj | 987 | 918 | 89 | 9,8 | 32 |
| jun | 1 022 | 905 | 40 | 4,4 | 15 |
| jul | 1 122 | 952 | 13 | 1,5 | 5 |
| aug | 1 116 | 951 | 21 | 2,3 | 8 |
| sep | 986 | 896 | 65 | 7,1 | 23 |
| okt | 884 | 915 | 165 | 18,1 | 60 |
| nov | 606 | 882 | 335 | 36,7 | 121 |
| dec | 601 | 911 | 372 | 40,8 | 135 |

## Mjesečni bilans, nagib 60° (prosjek godina)

| Mjesec | FN na sabirnici, kWh | Potrošnja, kWh | DEA (DC), kWh | DEA, h | Gorivo, l |
|---|---|---|---|---|---|
| jan | 687 | 911 | 329 | 36,1 | 119 |
| feb | 671 | 829 | 289 | 31,7 | 105 |
| mar | 860 | 910 | 218 | 23,9 | 79 |
| apr | 863 | 883 | 154 | 16,9 | 56 |
| maj | 863 | 918 | 121 | 13,3 | 44 |
| jun | 868 | 905 | 75 | 8,2 | 27 |
| jul | 961 | 952 | 43 | 4,7 | 16 |
| aug | 1 005 | 951 | 35 | 3,9 | 13 |
| sep | 942 | 896 | 83 | 9,1 | 30 |
| okt | 891 | 915 | 169 | 18,5 | 61 |
| nov | 633 | 882 | 326 | 35,8 | 118 |
| dec | 644 | 911 | 359 | 39,4 | 130 |

## Ključni pokazatelji

| Pokazatelj | 45° | 60° | RFI / Odluka do Rev 9 |
|---|---|---|---|
| FN na DC sabirnici, kWh/god | 10 448 | 9 887 |  |
| Specifični prinos na sabirnici, kWh/kWp | 1 488 | 1 408 |  |
| FN iskorišteno / odbačeno (baterija puna), kWh/god | 9 154 / 1 294 | 9 018 / 869 |  |
| Potrošnja, kWh/god | 10 864 | 10 864 |  |
| Solarni udio u potrošnji | 81,0 % | 79,7 % |  |
| Decembar: FN / potrošnja, kWh | 601 / 911 | 644 / 911 |  |
| DEA rad, h/god — prosjek / P90 / najgora god. | 226 / 271 / 307 | 241 / 291 / 327 | ≤250 h/god |
| DEA startova, /god — prosjek / najviše | 80 / 108 | 86 / 114 |  |
| Gorivo, l/god — prosjek / P90 / najgora god. | 746 / 895 / 1 013 | 797 / 960 / 1 078 |  |
| Spremnik 500 l traje, god — prosjek / najgora | 0,67 / 0,49 | 0,63 / 0,46 | ≥1 god |
| Dopuna goriva, /god — prosjek / najviše | 1,8 / 3 | 2,0 / 3 |  |
| Najduže razdoblje bez rada DEA, dana | 134 | 84 |  |
| Ekvivalentnih ciklusa baterije, /god | 139 | 141 |  |
| Rad DEA ispod 30 % opterećenja, h/god | 0,0 | 0,0 |  |
| Nepokrivena potrošnja, kWh | 0,0 | 0,0 | 0 |
| ≤250 h/god (P90 / najgora god.) | **NIJE ispunjeno** / **NIJE ispunjeno** | **NIJE ispunjeno** / **NIJE ispunjeno** | |
| ≥1 god na spremnik (prosjek / najgora god.) | **NIJE ispunjeno** / **NIJE ispunjeno** | **NIJE ispunjeno** / **NIJE ispunjeno** | |

## Osjetljivost, nagib 45°

| Slučaj | DEA h/god prosjek | P90 | najgora | Gorivo l/god prosjek | najgora | Spremnik traje, god | Startova/god |
|---|---|---|---|---|---|---|---|
| Osnovni slučaj (TD Rev 9): start DOD 85 %, stop SoC 60 %, punjenje 0,5 C | 226 | 271 | 307 | 746 | 1 013 | 0,67 | 80 |
| SMU bez parametriranja: stop SoC 90 %, punjenje 0,25 C | 253 | 298 | 330 | 834 | 1 091 | 0,60 | 55 |
| Stop SoC 90 % | 253 | 298 | 330 | 834 | 1 091 | 0,60 | 55 |
| Stop SoC 100 % (punjenje do vrha) | 267 | 316 | 346 | 879 | 1 140 | 0,57 | 52 |
| Stop SoC 40 % | 212 | 258 | 295 | 700 | 976 | 0,71 | 131 |
| Punjenje 0,25 C | 226 | 271 | 307 | 746 | 1 013 | 0,67 | 80 |
| Punjenje 0,15 C | 252 | 299 | 344 | 769 | 1 060 | 0,65 | 80 |
| Start pri DOD 70 % | 237 | 281 | 320 | 781 | 1 057 | 0,64 | 123 |
| Baterija 28,8 kWh (6 × 100 Ah, stara ponuda Huawei) | 277 | 323 | 354 | 915 | 1 168 | 0,55 | 160 |
| Potrošnja 1180 W stalno (bez hlađenja i pomoćne) | 203 | 246 | 290 | 670 | 959 | 0,75 | 72 |
| Potrošnja 1330 W stalno | 280 | 330 | 368 | 924 | 1 214 | 0,54 | 98 |

## Osjetljivost, nagib 60°

| Slučaj | DEA h/god prosjek | P90 | najgora | Gorivo l/god prosjek | najgora | Spremnik traje, god | Startova/god |
|---|---|---|---|---|---|---|---|
| Osnovni slučaj (TD Rev 9): start DOD 85 %, stop SoC 60 %, punjenje 0,5 C | 241 | 291 | 327 | 797 | 1 078 | 0,63 | 86 |
| SMU bez parametriranja: stop SoC 90 %, punjenje 0,25 C | 272 | 326 | 349 | 899 | 1 150 | 0,56 | 59 |
| Stop SoC 90 % | 272 | 326 | 348 | 899 | 1 150 | 0,56 | 59 |
| Stop SoC 100 % (punjenje do vrha) | 287 | 334 | 364 | 944 | 1 198 | 0,53 | 56 |
| Stop SoC 40 % | 225 | 277 | 308 | 743 | 1 017 | 0,67 | 139 |
| Punjenje 0,25 C | 242 | 291 | 327 | 798 | 1 078 | 0,63 | 86 |
| Punjenje 0,15 C | 270 | 322 | 363 | 821 | 1 107 | 0,61 | 85 |
| Start pri DOD 70 % | 250 | 299 | 329 | 824 | 1 087 | 0,61 | 130 |
| Baterija 28,8 kWh (6 × 100 Ah, stara ponuda Huawei) | 295 | 349 | 371 | 974 | 1 225 | 0,51 | 171 |
| Potrošnja 1180 W stalno (bez hlađenja i pomoćne) | 214 | 260 | 297 | 708 | 981 | 0,71 | 76 |
| Potrošnja 1330 W stalno | 300 | 358 | 391 | 990 | 1 291 | 0,51 | 104 |

## Zaključak (izveden iz brojeva iznad)

- **45°:** DEA 226 h/god u prosjeku (P90 271), gorivo 746 l/god. Najpovoljniji slučaj osjetljivosti za sate (Potrošnja 1180 W stalno (bez hlađenja i pomoćne)) daje P90 246 h/god; za gorivo (Potrošnja 1180 W stalno (bez hlađenja i pomoćne)) 670 l/god, tj. spremnik 500 l traje 0,75 god.
- **60°:** DEA 241 h/god u prosjeku (P90 291), gorivo 797 l/god. Najpovoljniji slučaj osjetljivosti za sate (Potrošnja 1180 W stalno (bez hlađenja i pomoćne)) daje P90 260 h/god; za gorivo (Potrošnja 1180 W stalno (bez hlađenja i pomoćne)) 708 l/god, tj. spremnik 500 l traje 0,71 god.

