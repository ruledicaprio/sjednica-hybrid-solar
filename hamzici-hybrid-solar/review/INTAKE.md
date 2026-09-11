# Hamzići — intake of the site inputs

11.09.2026 · what was received, what is used from it, and what is still missing.
The inputs themselves are held locally and are not committed (~850 MB; see the repo
`.gitignore`): `GP BS*/`, `EQUIPEMENT/`, `hamzici-photos/`.

## Certified site project (two copies)

| | Folder | Used for |
|---|---|---|
| **A — authoritative** | `GP BS HAMZIĆI_Čitluk K2 i AS 36 m/` | everything: CD PDFs dated 25.09.2017, Hamzići-specific PPZ 137/17 and ZNR 144/17 certificates, project code GP-BS-10472-291 (July 2017), all DWGs |
| B | `GP BS HAMZIĆI_Čitluk_K2 i AS 36 m/` | only the 06.07.2017 ELEKTRO revision (Hamzići-specific: EES 10 kW, meter 10–40 A, 5×6 mm²) and the 2019 photos. Its OVJERA folder belongs to other sites. |

Both ELEKTRO parts carry project code -287 instead of -291 (template leftover).

### Facts taken from A (and where)

| Fact | Value | Source |
|---|---|---|
| Lease | 12,00 × 12,50 m = 150 m², k.č. 109/1 K.O. Hamzići (novi premjer) | `461 …/01_Situacija 1_200.dwg` (dimensions 12000, 12500; text) |
| Slab | 5,40 × 5,40 m, centred in the lease | same drawing |
| Fence | around the slab, h = 1,80 m; gate 1,30 m | `04_Ograda.dwg` ("+ 1.80"), situation drawing (arc r = 1300) |
| Container | K2 3005 × 2300, 60 mm panels, 6,29 m², +2,63 / +2,89 m, 10 % roof; door 1,00 × 2,15 m | `463 …/01 Osnova.dwg`, `04 Fasade.dwg`; AG dio; 6_MASINSKE heat-gain table |
| Floor | 10,00 kN/m² (g+p): secondary HOP U 100×50×3 at 0,51 m, primary 15,00 kN/m′ | AG dio p70 |
| Tower | lattice, **32 m** (the title's "AS 36 m" is a template leftover), legs 3,70 m apart, footings 1,70 × 1,70 × 2,00 m, platforms at +3 / +12 / +30 m; P I at +3 m is also the ice shield | `462 …/01_Dispozicija S32 m.dwg`, AG dio |
| Wind | JUS U.C7.110–113, vm,50,10 = 25 m/s, qm,T,10 = 0,29 kN/m², qg 0,41–0,56 kN/m² at 1,5–4,5 m | AG dio p24–p30 |
| Snow / ice | S = 2,10 kN/m² (container); ice 20 mm, 500 kg/m³ (tower) | AG dio p71, p24 |
| Soil | σdop = 150 kN/m², no groundwater | AG dio p65 |
| Earthing | FeZn 25×4 ring in the tower footings + ring at 0,8 m | `5_ELEKTRO/3.6.9 Plan uzemljivača objekta.dwg` |
| Grid | a 10 kW connection was designed (TP Čalići, PMO) but never built | ELEKTRO; site photos (no poles) |
| AC design 2017 | one compact wall unit 5,4 kW sensible, free cooling, heater 800 W, 230 V AC + 48 V DC; openings 2 × 30/70 cm + 10/10 cable hole; GRO feeds 3×2,5 mm² AC and 2×6 mm² DC | 6_MASINSKE (tehnički opis, dispozicija), ELEKTRO p11 |

### Orientation — resolved against the drawing

The certified situation drawing has its north arrow pointing up and shows the container
door and the fence gate on the south. The photos of 08.09.2026 and the Investor
(11.09.2026) put them on the **north, a little north-west**. The photos govern: the
drawing is rotated ≈180° to the site. `cad/site_geometry.json` is written in the true
orientation. The Stulz unit is on the east wall at its south end (photos).

## Site photos (08.09.2026, 12:11–12:17 CEST, Samsung Galaxy A55)

12 usable images (each exists twice; one copy of every pair is 0 bytes). Lost in both
copies: `20260908_121619`, `_121701`, `_123320` — re-export requested. EXIF has the time
and UTC offset but no GPS and no compass heading. Sun positions per photo and annotated
copies of the key images: `review/pvsim/photo/`. Found: the lone deciduous tree 7–9 m,
15–20 m SSE–SE of the tower; black pines ENE; the Stulz wall unit; dry grass on karst.

## Equipment documents (`EQUIPEMENT/`)

iSSU S4875G2 datasheet (efficiency curve digitised into `pvsim/sites/*.json`), ICC360-HA1-C1
installation guide (SMU defaults: DOD to Start 85 %, Refuel THR 20 %; ESM-48100A6 48 V /
100 Ah; PC1500D-1 ≤500 W), MTS9300A manuals, PV Module Solution User Manual, Huawei BOQ for
Sjednica (quotes 12 × iPV540-M1A — to be aligned to iPV585-M2A), GroundSupport drawing.

## Still missing

Measured DC load of the base station · Stulz nameplate and cut-out sizes · photos of the
container interior · re-export of the three lost photos · maximum charge current of the
6 × 150 Ah battery (48,6 kWh, per the Odluka; Investor 11.09.2026) · estimates per site
and LOT.
