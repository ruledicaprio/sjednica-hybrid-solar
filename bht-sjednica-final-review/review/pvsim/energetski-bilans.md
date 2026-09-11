# Energetski bilans — BS Sjednica (Bileća)

*Simulacija pvlib + PVGIS-SARAH3, satno 2005–2023. Generisano 2026-09-11, pvsim 0.1.0, commit cd567a2. Ulazi i pretpostavke: `pvsim/sites/sjednica.json`; brojevi: `kpis.json` u ovom folderu. Ne uređivati ručno — `python -m pvsim report --site sjednica`.*

## Metoda

- **Ozračenje:** PVGIS v5.3 `seriescalc`, SARAH3 + ERA5 (temperatura, vjetar), satno za 19 godina; horizont iz PVGIS DEM-a; polje jug, nagib 45° i 60°.
- **FN lanac:** refleksija Martin-Ruiz (a_r 0,16), temperatura modula Faiman (26,9 / 6,2), model modula Huld c-Si (PVGIS), mjesečno zaprljanje i snijeg, neusklađenost i LID, DC kablovi 0,78 % pri Imp, optimizatori 99,0 %, iSSU S4875G2 po krivulji proizvođača (Vin 330 V), ograničenje 4 kW po modulu.
- **Bilans na −48 V DC sabirnici:** satno, sve godine neprekidno. Baterija 6 × 150 Ah LFP = 48,6 kWh, η punjenja/pražnjenja 97,5 %, punjenje do 0,50 C. DEA preko ispravljača ograničenih na 9,5 kW AC (η 96 %): start pri DOD 85 %, stop pri SoC 60 %, najkraći rad 1,0 h. Gorivo po tehničkom listu P18-6 (prime).
- **Potrošnja:** 1180 W TK + 45 W pomoćna (SMU, BMS, ventilatori) + hlađenje ormara do 150 W (linearno 20→35 °C).
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
| jan | 591 | 911 | 371 | 40,7 | 134 |
| feb | 632 | 829 | 305 | 33,4 | 110 |
| mar | 853 | 910 | 233 | 25,6 | 84 |
| apr | 892 | 882 | 144 | 15,8 | 52 |
| maj | 949 | 913 | 105 | 11,5 | 38 |
| jun | 999 | 892 | 56 | 6,1 | 20 |
| jul | 1 108 | 932 | 17 | 1,8 | 6 |
| aug | 1 092 | 931 | 26 | 2,9 | 10 |
| sep | 957 | 887 | 86 | 9,4 | 31 |
| okt | 890 | 913 | 173 | 19,0 | 63 |
| nov | 613 | 882 | 332 | 36,4 | 120 |
| dec | 560 | 911 | 402 | 44,1 | 146 |

## Mjesečni bilans, nagib 60° (prosjek godina)

| Mjesec | FN na sabirnici, kWh | Potrošnja, kWh | DEA (DC), kWh | DEA, h | Gorivo, l |
|---|---|---|---|---|---|
| jan | 652 | 911 | 355 | 38,9 | 128 |
| feb | 663 | 829 | 298 | 32,7 | 108 |
| mar | 839 | 910 | 241 | 26,4 | 87 |
| apr | 821 | 882 | 178 | 19,5 | 64 |
| maj | 828 | 913 | 152 | 16,6 | 55 |
| jun | 848 | 892 | 96 | 10,5 | 35 |
| jul | 948 | 932 | 44 | 4,9 | 16 |
| aug | 981 | 931 | 47 | 5,1 | 17 |
| sep | 911 | 887 | 102 | 11,2 | 37 |
| okt | 896 | 913 | 180 | 19,7 | 65 |
| nov | 647 | 882 | 323 | 35,4 | 117 |
| dec | 617 | 911 | 381 | 41,7 | 138 |

## Ključni pokazatelji

| Pokazatelj | 45° | 60° | RFI / Odluka do Rev 9 |
|---|---|---|---|
| FN na DC sabirnici, kWh/god | 10 137 | 9 651 |  |
| Specifični prinos na sabirnici, kWh/kWp | 1 444 | 1 375 |  |
| FN iskorišteno / odbačeno (baterija puna), kWh/god | 8 894 / 1 244 | 8 753 / 898 |  |
| Potrošnja, kWh/god | 10 794 | 10 794 |  |
| Solarni udio u potrošnji | 79,2 % | 77,8 % |  |
| Decembar: FN / potrošnja, kWh | 560 / 911 | 617 / 911 |  |
| DEA rad, h/god — prosjek / P90 / najgora god. | 247 / 307 / 327 | 263 / 325 / 349 | ≤250 h/god |
| DEA startova, /god — prosjek / najviše | 88 / 117 | 93 / 123 |  |
| Gorivo, l/god — prosjek / P90 / najgora god. | 815 / 1 015 / 1 081 | 868 / 1 075 / 1 152 |  |
| Spremnik 500 l traje, god — prosjek / najgora | 0,61 / 0,46 | 0,58 / 0,43 | ≥1 god |
| Dopuna goriva, /god — prosjek / najviše | 2,1 / 3 | 2,2 / 3 |  |
| Najduže razdoblje bez rada DEA, dana | 109 | 109 |  |
| Ekvivalentnih ciklusa baterije, /god | 139 | 141 |  |
| Rad DEA ispod 30 % opterećenja, h/god | 0,0 | 0,0 |  |
| Nepokrivena potrošnja, kWh | 0,0 | 0,0 | 0 |
| ≤250 h/god (P90 / najgora god.) | **NIJE ispunjeno** / **NIJE ispunjeno** | **NIJE ispunjeno** / **NIJE ispunjeno** | |
| ≥1 god na spremnik (prosjek / najgora god.) | **NIJE ispunjeno** / **NIJE ispunjeno** | **NIJE ispunjeno** / **NIJE ispunjeno** | |

## Osjetljivost, nagib 45°

| Slučaj | DEA h/god prosjek | P90 | najgora | Gorivo l/god prosjek | najgora | Spremnik traje, god | Startova/god |
|---|---|---|---|---|---|---|---|
| Osnovni slučaj (TD Rev 9): start DOD 85 %, stop SoC 60 %, punjenje 0,5 C | 247 | 307 | 327 | 815 | 1 081 | 0,61 | 88 |
| SMU bez parametriranja: stop SoC 90 %, punjenje 0,25 C | 275 | 332 | 360 | 909 | 1 188 | 0,55 | 60 |
| Stop SoC 90 % | 275 | 332 | 360 | 909 | 1 188 | 0,55 | 60 |
| Stop SoC 100 % (punjenje do vrha) | 288 | 337 | 371 | 949 | 1 220 | 0,53 | 56 |
| Stop SoC 40 % | 234 | 292 | 318 | 772 | 1 052 | 0,65 | 144 |
| Punjenje 0,25 C | 247 | 307 | 327 | 815 | 1 081 | 0,61 | 88 |
| Punjenje 0,15 C | 275 | 340 | 369 | 840 | 1 127 | 0,60 | 87 |
| Start pri DOD 70 % | 256 | 318 | 342 | 846 | 1 129 | 0,59 | 133 |
| Baterija 28,8 kWh (6 × 100 Ah, stara ponuda Huawei) | 297 | 361 | 376 | 981 | 1 241 | 0,51 | 172 |
| Potrošnja 1180 W stalno (bez hlađenja i pomoćne) | 223 | 275 | 307 | 738 | 1 015 | 0,68 | 79 |
| Potrošnja 1330 W stalno | 307 | 378 | 396 | 1 014 | 1 307 | 0,49 | 107 |

## Osjetljivost, nagib 60°

| Slučaj | DEA h/god prosjek | P90 | najgora | Gorivo l/god prosjek | najgora | Spremnik traje, god | Startova/god |
|---|---|---|---|---|---|---|---|
| Osnovni slučaj (TD Rev 9): start DOD 85 %, stop SoC 60 %, punjenje 0,5 C | 263 | 325 | 349 | 868 | 1 152 | 0,58 | 93 |
| SMU bez parametriranja: stop SoC 90 %, punjenje 0,25 C | 293 | 355 | 374 | 968 | 1 233 | 0,52 | 64 |
| Stop SoC 90 % | 293 | 354 | 373 | 968 | 1 233 | 0,52 | 64 |
| Stop SoC 100 % (punjenje do vrha) | 309 | 364 | 390 | 1 017 | 1 285 | 0,49 | 60 |
| Stop SoC 40 % | 247 | 314 | 332 | 816 | 1 098 | 0,61 | 152 |
| Punjenje 0,25 C | 263 | 325 | 349 | 868 | 1 152 | 0,58 | 93 |
| Punjenje 0,15 C | 293 | 359 | 386 | 896 | 1 188 | 0,56 | 93 |
| Start pri DOD 70 % | 272 | 337 | 361 | 897 | 1 192 | 0,56 | 141 |
| Baterija 28,8 kWh (6 × 100 Ah, stara ponuda Huawei) | 314 | 379 | 398 | 1 037 | 1 316 | 0,48 | 181 |
| Potrošnja 1180 W stalno (bez hlađenja i pomoćne) | 235 | 295 | 319 | 775 | 1 054 | 0,65 | 84 |
| Potrošnja 1330 W stalno | 329 | 405 | 424 | 1 086 | 1 400 | 0,46 | 115 |

## Zaključak (izveden iz brojeva iznad)

- **45°:** DEA 247 h/god u prosjeku (P90 307), gorivo 815 l/god. Najpovoljniji slučaj osjetljivosti za sate (Potrošnja 1180 W stalno (bez hlađenja i pomoćne)) daje P90 275 h/god; za gorivo (Potrošnja 1180 W stalno (bez hlađenja i pomoćne)) 738 l/god, tj. spremnik 500 l traje 0,68 god.
- **60°:** DEA 263 h/god u prosjeku (P90 325), gorivo 868 l/god. Najpovoljniji slučaj osjetljivosti za sate (Potrošnja 1180 W stalno (bez hlađenja i pomoćne)) daje P90 295 h/god; za gorivo (Potrošnja 1180 W stalno (bez hlađenja i pomoćne)) 775 l/god, tj. spremnik 500 l traje 0,65 god.

