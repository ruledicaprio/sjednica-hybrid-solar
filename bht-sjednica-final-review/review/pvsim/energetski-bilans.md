# Energetski bilans — BS Sjednica (Bileća)

*Simulacija pvlib + PVGIS-SARAH3, satno 2005–2023. Generisano 2026-09-11, pvsim 0.1.0, commit f06377c. Ulazi i pretpostavke: `pvsim/sites/sjednica.json`; brojevi: `kpis.json` u ovom folderu. Ne uređivati ručno — `python -m pvsim report --site sjednica`.*

## Metoda

- **Ozračenje:** PVGIS v5.3 `seriescalc`, SARAH3 + ERA5 (temperatura, vjetar), satno za 19 godina; horizont iz PVGIS DEM-a; polje jug, nagib 45° i 60°.
- **FN lanac:** refleksija Martin-Ruiz (a_r 0,16), temperatura modula Faiman (26,9 / 6,2), model modula Huld c-Si (PVGIS), mjesečno zaprljanje i snijeg, neusklađenost i LID, DC kablovi 0,78 % pri Imp, optimizatori 99,0 %, iSSU S4875G2 po krivulji proizvođača (Vin 330 V), ograničenje 4 kW po modulu.
- **Bilans na −48 V DC sabirnici:** satno, sve godine neprekidno. Baterija 6 × 150 Ah LFP = 48,6 kWh, η punjenja/pražnjenja 97,5 %, punjenje do 0,50 C. DEA preko ispravljača ograničenih na 9,5 kW AC (η 96 %): start pri DOD 85 %, stop pri SoC 60 %, najkraći rad 1,0 h. Gorivo po tehničkom listu P18-6 (prime).
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
| jan | 591 | 893 | 360 | 39,5 | 130 |
| feb | 632 | 812 | 289 | 31,7 | 105 |
| mar | 853 | 892 | 218 | 23,9 | 79 |
| apr | 892 | 864 | 136 | 14,9 | 49 |
| maj | 949 | 895 | 91 | 10,0 | 33 |
| jun | 999 | 874 | 54 | 5,9 | 20 |
| jul | 1 108 | 913 | 14 | 1,6 | 5 |
| aug | 1 092 | 912 | 23 | 2,5 | 8 |
| sep | 957 | 869 | 78 | 8,6 | 28 |
| okt | 890 | 894 | 167 | 18,3 | 60 |
| nov | 613 | 864 | 319 | 35,0 | 116 |
| dec | 560 | 893 | 386 | 42,3 | 140 |

## Mjesečni bilans, nagib 60° (prosjek godina)

| Mjesec | FN na sabirnici, kWh | Potrošnja, kWh | DEA (DC), kWh | DEA, h | Gorivo, l |
|---|---|---|---|---|---|
| jan | 652 | 893 | 342 | 37,5 | 124 |
| feb | 663 | 812 | 288 | 31,5 | 104 |
| mar | 839 | 892 | 231 | 25,3 | 84 |
| apr | 821 | 864 | 164 | 18,0 | 59 |
| maj | 828 | 895 | 137 | 15,0 | 50 |
| jun | 848 | 874 | 84 | 9,2 | 30 |
| jul | 948 | 913 | 36 | 3,9 | 13 |
| aug | 981 | 912 | 43 | 4,7 | 16 |
| sep | 911 | 869 | 94 | 10,3 | 34 |
| okt | 896 | 894 | 171 | 18,8 | 62 |
| nov | 647 | 864 | 306 | 33,5 | 111 |
| dec | 617 | 893 | 366 | 40,2 | 133 |

## Ključni pokazatelji

| Pokazatelj | 45° | 60° | RFI / Odluka do Rev 9 |
|---|---|---|---|
| FN na DC sabirnici, kWh/god | 10 137 | 9 651 |  |
| Specifični prinos na sabirnici, kWh/kWp | 1 444 | 1 375 |  |
| FN iskorišteno / odbačeno (baterija puna), kWh/god | 8 783 / 1 354 | 8 659 / 992 |  |
| Potrošnja, kWh/god | 10 575 | 10 575 |  |
| Solarni udio u potrošnji | 79,8 % | 78,6 % |  |
| Decembar: FN / potrošnja, kWh | 560 / 893 | 617 / 893 |  |
| DEA rad, h/god — prosjek / P90 / najgora god. | 234 / 293 / 313 | 248 / 309 / 336 | ≤250 h/god |
| DEA startova, /god — prosjek / najviše | 83 / 112 | 88 / 120 |  |
| Gorivo, l/god — prosjek / P90 / najgora god. | 773 / 969 / 1 032 | 819 / 1 022 / 1 109 |  |
| Spremnik 500 l traje, god — prosjek / najgora | 0,65 / 0,48 | 0,61 / 0,45 | ≥1 god |
| Dopuna goriva, /god — prosjek / najviše | 1,9 / 3 | 2,1 / 3 |  |
| Najduže razdoblje bez rada DEA, dana | 111 | 110 |  |
| Ekvivalentnih ciklusa baterije, /god | 136 | 138 |  |
| Rad DEA ispod 30 % opterećenja, h/god | 0,0 | 0,0 |  |
| Nepokrivena potrošnja, kWh | 0,0 | 0,0 | 0 |
| ≤250 h/god (P90 / najgora god.) | **NIJE ispunjeno** / **NIJE ispunjeno** | **NIJE ispunjeno** / **NIJE ispunjeno** | |
| ≥1 god na spremnik (prosjek / najgora god.) | **NIJE ispunjeno** / **NIJE ispunjeno** | **NIJE ispunjeno** / **NIJE ispunjeno** | |

## Osjetljivost, nagib 45°

| Slučaj | DEA h/god prosjek | P90 | najgora | Gorivo l/god prosjek | najgora | Spremnik traje, god | Startova/god |
|---|---|---|---|---|---|---|---|
| Osnovni slučaj (TD Rev 9): start DOD 85 %, stop SoC 60 %, punjenje 0,5 C | 234 | 293 | 313 | 773 | 1 032 | 0,65 | 83 |
| SMU bez parametriranja: stop SoC 90 %, punjenje 0,25 C | 263 | 312 | 349 | 867 | 1 153 | 0,58 | 57 |
| Stop SoC 90 % | 263 | 312 | 349 | 867 | 1 153 | 0,58 | 57 |
| Stop SoC 100 % (punjenje do vrha) | 274 | 322 | 357 | 902 | 1 176 | 0,55 | 53 |
| Stop SoC 40 % | 221 | 281 | 303 | 730 | 999 | 0,68 | 137 |
| Punjenje 0,25 C | 234 | 293 | 313 | 773 | 1 032 | 0,65 | 83 |
| Punjenje 0,15 C | 262 | 326 | 349 | 797 | 1 069 | 0,63 | 83 |
| Start pri DOD 70 % | 243 | 302 | 326 | 804 | 1 078 | 0,62 | 127 |
| Baterija 28,8 kWh (6 × 100 Ah, stara ponuda Huawei) | 284 | 345 | 359 | 938 | 1 187 | 0,53 | 165 |
| Potrošnja 1180 W stalno (bez hlađenja i pomoćne) | 223 | 275 | 307 | 738 | 1 015 | 0,68 | 79 |
| Potrošnja 1330 W stalno | 307 | 378 | 396 | 1 014 | 1 307 | 0,49 | 107 |

## Osjetljivost, nagib 60°

| Slučaj | DEA h/god prosjek | P90 | najgora | Gorivo l/god prosjek | najgora | Spremnik traje, god | Startova/god |
|---|---|---|---|---|---|---|---|
| Osnovni slučaj (TD Rev 9): start DOD 85 %, stop SoC 60 %, punjenje 0,5 C | 248 | 309 | 336 | 819 | 1 109 | 0,61 | 88 |
| SMU bez parametriranja: stop SoC 90 %, punjenje 0,25 C | 278 | 342 | 368 | 918 | 1 216 | 0,54 | 61 |
| Stop SoC 90 % | 278 | 342 | 368 | 918 | 1 216 | 0,54 | 61 |
| Stop SoC 100 % (punjenje do vrha) | 292 | 355 | 381 | 961 | 1 254 | 0,52 | 57 |
| Stop SoC 40 % | 232 | 296 | 320 | 768 | 1 058 | 0,65 | 144 |
| Punjenje 0,25 C | 248 | 309 | 336 | 819 | 1 109 | 0,61 | 88 |
| Punjenje 0,15 C | 277 | 347 | 380 | 845 | 1 147 | 0,59 | 88 |
| Start pri DOD 70 % | 258 | 321 | 345 | 853 | 1 139 | 0,59 | 135 |
| Baterija 28,8 kWh (6 × 100 Ah, stara ponuda Huawei) | 300 | 366 | 387 | 991 | 1 278 | 0,50 | 175 |
| Potrošnja 1180 W stalno (bez hlađenja i pomoćne) | 235 | 295 | 319 | 775 | 1 054 | 0,65 | 84 |
| Potrošnja 1330 W stalno | 329 | 405 | 424 | 1 086 | 1 400 | 0,46 | 115 |

## Zaključak (izveden iz brojeva iznad)

- **45°:** DEA 234 h/god u prosjeku (P90 293), gorivo 773 l/god. Najpovoljniji slučaj osjetljivosti za sate (Potrošnja 1180 W stalno (bez hlađenja i pomoćne)) daje P90 275 h/god; za gorivo (Stop SoC 40 %) 730 l/god, tj. spremnik 500 l traje 0,68 god.
- **60°:** DEA 248 h/god u prosjeku (P90 309), gorivo 819 l/god. Najpovoljniji slučaj osjetljivosti za sate (Potrošnja 1180 W stalno (bez hlađenja i pomoćne)) daje P90 295 h/god; za gorivo (Stop SoC 40 %) 768 l/god, tj. spremnik 500 l traje 0,65 god.

