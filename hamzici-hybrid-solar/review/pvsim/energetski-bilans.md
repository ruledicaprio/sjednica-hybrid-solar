# Energetski bilans — BS Hamzići (Čitluk)

*Simulacija pvlib + PVGIS-SARAH3, satno 2005–2023. Generisano 2026-09-11, pvsim 0.1.0, commit f06377c. Ulazi i pretpostavke: `pvsim/sites/hamzici.json`; brojevi: `kpis.json` u ovom folderu. Ne uređivati ručno — `python -m pvsim report --site hamzici`.*

## Metoda

- **Ozračenje:** PVGIS v5.3 `seriescalc`, SARAH3 + ERA5 (temperatura, vjetar), satno za 19 godina; horizont iz PVGIS DEM-a; polje jug, nagib 45° i 60°.
- **FN lanac:** refleksija Martin-Ruiz (a_r 0,16), temperatura modula Faiman (26,9 / 6,2), model modula Huld c-Si (PVGIS), mjesečno zaprljanje i snijeg, neusklađenost i LID, DC kablovi 0,78 % pri Imp, optimizatori 99,0 %, iSSU S4875G2 po krivulji proizvođača (Vin 330 V), ograničenje 4 kW po modulu.
- **Bilans na −48 V DC sabirnici:** satno, sve godine neprekidno. Baterija 6 × 150 Ah LFP = 48,6 kWh, η punjenja/pražnjenja 97,5 %, punjenje do 0,50 C. DEA preko ispravljača ograničenih na 9,5 kW AC (η 96 %): start pri DOD 85 %, stop pri SoC 60 %, najkraći rad 1,0 h. Gorivo po tehničkom listu P18-6 (prime).
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
| jan | 646 | 893 | 327 | 35,8 | 118 |
| feb | 655 | 812 | 274 | 30,1 | 99 |
| mar | 885 | 892 | 192 | 21,0 | 69 |
| apr | 938 | 865 | 116 | 12,7 | 42 |
| maj | 987 | 899 | 85 | 9,3 | 31 |
| jun | 1 022 | 887 | 36 | 4,0 | 13 |
| jul | 1 122 | 933 | 12 | 1,3 | 4 |
| aug | 1 116 | 932 | 17 | 1,9 | 6 |
| sep | 986 | 878 | 56 | 6,2 | 20 |
| okt | 884 | 896 | 157 | 17,3 | 57 |
| nov | 606 | 864 | 317 | 34,7 | 115 |
| dec | 601 | 893 | 358 | 39,3 | 130 |

## Mjesečni bilans, nagib 60° (prosjek godina)

| Mjesec | FN na sabirnici, kWh | Potrošnja, kWh | DEA (DC), kWh | DEA, h | Gorivo, l |
|---|---|---|---|---|---|
| jan | 687 | 893 | 313 | 34,3 | 113 |
| feb | 671 | 812 | 274 | 30,0 | 99 |
| mar | 860 | 892 | 209 | 22,9 | 76 |
| apr | 863 | 865 | 142 | 15,5 | 51 |
| maj | 863 | 899 | 115 | 12,6 | 42 |
| jun | 868 | 887 | 69 | 7,6 | 25 |
| jul | 961 | 933 | 30 | 3,3 | 11 |
| aug | 1 005 | 932 | 33 | 3,7 | 12 |
| sep | 942 | 878 | 70 | 7,7 | 25 |
| okt | 891 | 896 | 161 | 17,7 | 58 |
| nov | 633 | 864 | 313 | 34,3 | 113 |
| dec | 644 | 893 | 340 | 37,3 | 123 |

## Ključni pokazatelji

| Pokazatelj | 45° | 60° | RFI / Odluka do Rev 9 |
|---|---|---|---|
| FN na DC sabirnici, kWh/god | 10 448 | 9 887 |  |
| Specifični prinos na sabirnici, kWh/kWp | 1 488 | 1 408 |  |
| FN iskorišteno / odbačeno (baterija puna), kWh/god | 9 040 / 1 408 | 8 924 / 963 |  |
| Potrošnja, kWh/god | 10 644 | 10 644 |  |
| Solarni udio u potrošnji | 81,7 % | 80,6 % |  |
| Decembar: FN / potrošnja, kWh | 601 / 893 | 644 / 893 |  |
| DEA rad, h/god — prosjek / P90 / najgora god. | 214 / 256 / 300 | 227 / 274 / 310 | ≤250 h/god |
| DEA startova, /god — prosjek / najviše | 76 / 106 | 81 / 110 |  |
| Gorivo, l/god — prosjek / P90 / najgora god. | 706 / 847 / 992 | 749 / 905 / 1 026 |  |
| Spremnik 500 l traje, god — prosjek / najgora | 0,71 / 0,50 | 0,67 / 0,49 | ≥1 god |
| Dopuna goriva, /god — prosjek / najviše | 1,8 / 3 | 1,9 / 2 |  |
| Najduže razdoblje bez rada DEA, dana | 134 | 84 |  |
| Ekvivalentnih ciklusa baterije, /god | 136 | 138 |  |
| Rad DEA ispod 30 % opterećenja, h/god | 0,0 | 0,0 |  |
| Nepokrivena potrošnja, kWh | 0,0 | 0,0 | 0 |
| ≤250 h/god (P90 / najgora god.) | **NIJE ispunjeno** / **NIJE ispunjeno** | **NIJE ispunjeno** / **NIJE ispunjeno** | |
| ≥1 god na spremnik (prosjek / najgora god.) | **NIJE ispunjeno** / **NIJE ispunjeno** | **NIJE ispunjeno** / **NIJE ispunjeno** | |

## Osjetljivost, nagib 45°

| Slučaj | DEA h/god prosjek | P90 | najgora | Gorivo l/god prosjek | najgora | Spremnik traje, god | Startova/god |
|---|---|---|---|---|---|---|---|
| Osnovni slučaj (TD Rev 9): start DOD 85 %, stop SoC 60 %, punjenje 0,5 C | 214 | 256 | 300 | 706 | 992 | 0,71 | 76 |
| SMU bez parametriranja: stop SoC 90 %, punjenje 0,25 C | 242 | 290 | 319 | 798 | 1 053 | 0,63 | 53 |
| Stop SoC 90 % | 242 | 290 | 319 | 798 | 1 053 | 0,63 | 53 |
| Stop SoC 100 % (punjenje do vrha) | 254 | 301 | 330 | 836 | 1 090 | 0,60 | 50 |
| Stop SoC 40 % | 201 | 248 | 282 | 664 | 930 | 0,75 | 125 |
| Punjenje 0,25 C | 214 | 256 | 300 | 706 | 992 | 0,71 | 76 |
| Punjenje 0,15 C | 240 | 285 | 329 | 729 | 1 011 | 0,69 | 76 |
| Start pri DOD 70 % | 225 | 268 | 303 | 743 | 1 001 | 0,67 | 117 |
| Baterija 28,8 kWh (6 × 100 Ah, stara ponuda Huawei) | 264 | 307 | 347 | 871 | 1 145 | 0,57 | 153 |
| Potrošnja 1180 W stalno (bez hlađenja i pomoćne) | 203 | 246 | 290 | 670 | 959 | 0,75 | 72 |
| Potrošnja 1330 W stalno | 280 | 330 | 368 | 924 | 1 214 | 0,54 | 98 |

## Osjetljivost, nagib 60°

| Slučaj | DEA h/god prosjek | P90 | najgora | Gorivo l/god prosjek | najgora | Spremnik traje, god | Startova/god |
|---|---|---|---|---|---|---|---|
| Osnovni slučaj (TD Rev 9): start DOD 85 %, stop SoC 60 %, punjenje 0,5 C | 227 | 274 | 310 | 749 | 1 026 | 0,67 | 81 |
| SMU bez parametriranja: stop SoC 90 %, punjenje 0,25 C | 257 | 309 | 334 | 849 | 1 102 | 0,59 | 56 |
| Stop SoC 90 % | 257 | 308 | 334 | 849 | 1 102 | 0,59 | 56 |
| Stop SoC 100 % (punjenje do vrha) | 271 | 318 | 348 | 891 | 1 147 | 0,56 | 53 |
| Stop SoC 40 % | 212 | 262 | 292 | 699 | 964 | 0,72 | 131 |
| Punjenje 0,25 C | 227 | 274 | 311 | 749 | 1 026 | 0,67 | 81 |
| Punjenje 0,15 C | 254 | 307 | 344 | 774 | 1 053 | 0,65 | 80 |
| Start pri DOD 70 % | 237 | 286 | 317 | 784 | 1 047 | 0,64 | 124 |
| Baterija 28,8 kWh (6 × 100 Ah, stara ponuda Huawei) | 280 | 331 | 357 | 925 | 1 178 | 0,54 | 163 |
| Potrošnja 1180 W stalno (bez hlađenja i pomoćne) | 214 | 260 | 297 | 708 | 981 | 0,71 | 76 |
| Potrošnja 1330 W stalno | 300 | 358 | 391 | 990 | 1 291 | 0,51 | 104 |

## Zaključak (izveden iz brojeva iznad)

- **45°:** DEA 214 h/god u prosjeku (P90 256), gorivo 706 l/god. Najpovoljniji slučaj osjetljivosti za sate (Potrošnja 1180 W stalno (bez hlađenja i pomoćne)) daje P90 246 h/god; za gorivo (Stop SoC 40 %) 664 l/god, tj. spremnik 500 l traje 0,75 god.
- **60°:** DEA 227 h/god u prosjeku (P90 274), gorivo 749 l/god. Najpovoljniji slučaj osjetljivosti za sate (Potrošnja 1180 W stalno (bez hlađenja i pomoćne)) daje P90 260 h/god; za gorivo (Stop SoC 40 %) 699 l/god, tj. spremnik 500 l traje 0,72 god.

