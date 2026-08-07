# 02 — CONSTRUCTION / STRUCTURAL REVIEW
## BS Sjednica, Bileća (RS, BiH) — Autonomous hybrid power supply, LOT 1 + LOT 2

| | |
|---|---|
| **Discipline** | Structural / Civil (Arhitektonsko-građevinski dio) |
| **Documents under review** | `TD-OUTPUT\3.1 PRILOG II TD - predmjer Sjednica Bileca.xlsx` (LOT 1, LOT 2); `TD-OUTPUT\3. TD JN Hibridni sistem napajanja BS Sjednica.docx`; `TD-OUTPUT\Prilog_III_situacija_sjednica_bileca.pdf` (S-01, S-02, S-03) |
| **Reviewer** | Chartered structural/civil engineer (independent review) |
| **Revision** | Rev. 0 |
| **Date** | 2026-08-07 |
| **Review basis** | `prompt.md` (Engineering Document Review – Rules & Philosophy), BAS EN 1990/1991-1-3/1991-1-4/1992-1-1/1993-1-1/1997-1, manufacturer documentation, the Investor's own certified site project |

---

## 0. Source register and abbreviations

| Tag | Document | Path |
|---|---|---|
| **[BOQ]** | Prilog II — Obrazac za cijenu ponude (predmjer), sheets *LOT 1* / *LOT 2* | `bht-sjednica-final-review\TD-OUTPUT\3.1 PRILOG II TD - predmjer Sjednica Bileca.xlsx` |
| **[TD]** | Tenderska dokumentacija (main text) | `bht-sjednica-final-review\TD-OUTPUT\3. TD JN Hibridni sistem napajanja BS Sjednica.docx` |
| **[S-01] [S-02] [S-03]** | PRILOG III — Situacija i dispozicija, pp. 3, 4, 5 | `bht-sjednica-final-review\TD-OUTPUT\Prilog_III_situacija_sjednica_bileca.pdf` |
| **[HW-GD]** | Huawei *Sharp A Bracket 3.0 Foundation* — General Description (p. 3), Foundation Plan (p. 4), Sections + Steel/Concrete tables (p. 5), Anchor Bolt Dimensions (p. 2) | `bht-sjednica-final-review\EQUIPEMENT\PV\GroundSupport_drawing.pdf` |
| **[HW-QG]** | Huawei *PV Module Support (Standard A-Shaped Support 3.0) Quick Guide*, pp. 6–42 of the same PDF | as above |
| **[AG]** | Certified site project, AG part — technical description + JUS static calculation for BS Sjednica | `SITE-PROJECT-SJEDNICA-Bileca-K2-S38-m\2 - ARHITEKTONSKO GRADJEVINSKI DIO\04 AG dio.docx` |
| **[WIND-XLS]** | Certified site wind calculation | `…\2 - ARHITEKTONSKO GRADJEVINSKI DIO\proračun vjetra JUS EXCEL.xlsx` |
| **[LU]** | Lokacijski uslovi br. 11.06/364-11/18, Opština Bileća, 24.07.2018, p. 1 | `SITE-PROJECT-SJEDNICA-Bileca-K2-S38-m\ULAZNI\Lokacijski uslovi Sjednica novi.pdf` |
| **[PZ]** | BH Telecom — Projektni zadatak, tipska prenosiva kućica (kontejner) | `docs\site_container\CONTAINER_PZ_3_Kontejner.md` |
| **[MATISA]** | Reference design: container for 2 × 13.3 kVA gensets, MATISA d.o.o. 2008 | `docs\genset_inside_container\2_DIS_AG_DIO_MATISA Kontejner 2x13kVA 2008.md` |
| **[P22]** | FG Wilson P22-6 Product Specification (3 pp., no dimensions/masses) | `bht-sjednica-final-review\EQUIPEMENT\GENSET\P22-6.pdf` / `P22-6.md` |

---

## 1. EXECUTIVE SUMMARY

### Risk level: **HIGH**

**Key conclusion.** The LOT 1 PV support solution is **structurally non-compliant and must be redesigned before the tender is issued**. The Investor's own certified documents for this exact location give a design wind pressure of **1.10–1.20 kN/m²** on low-level exposed structures — equivalent to a **42–44 m/s three-second gust**. The Huawei Standard A-Shaped Support is rated for a **31 m/s** gust at the 45° tilt fixed by [BOQ] LOT 1 item 1.1 [HW-GD p. 3], i.e. **0.60 kN/m²**. The tendered structure is therefore loaded to **1.8–2.0 × its rated wind capacity**. Reducing the tilt does not rescue it: even the best-rated tilts (15°/25°, 40 m/s = 1.00 kN/m²) remain **10–20 % short**. **No standard tilt of this product is compliant at BS Sjednica.**

Compounding this, the tender's stated panel geometry is wrong (horizontal projection 2 590 mm instead of ≈ 3 240 mm), the foundation figures are copied from the **HIGH**-support drawing while the parts list specifies the **LOW** support, the bottom module edge at +0,50 m will be buried by drifted snow at 1 076 m, item 2.7 prices a 5,40 × 5,40 m slab that **already exists as the 1,80 m deep tower foundation block**, and the container floor capacity of "10,00 kN/m²" asserted throughout LOT 2 **appears in no source document** — the governing design brief states **2,00 kN/m²**.

There are **11 RED findings**. Items 1.1, 1.3, 2.3, 2.4 and 2.7 of LOT 1 and items 4.1, 4.2 and 4.4 of LOT 2 cannot be priced or built as written.

---

## 2. INFORMATION EXTRACTION TABLE (ground truth)

### 2.1 Site and environment

| Parameter | Value | Source |
|---|---|---|
| Location | BS Sjednica, Bileća, Republika Srpska | [TD] Tabela 1 |
| Coordinates | 42,944810 N / 18,323640 E | [TD] Tabela 1 |
| Altitude | **1 076 m** (tender) / **1 077 m** (certified project, tower base) | [TD] §3.1.3; [AG] "NADMORSKA VISINA PODNOŽJA TORNJA: 1077 m.n.m." |
| Cadastre | k.č. 1/1 (stari premjer), KO Granica 2 | [LU] p. 1 |
| Character of works permitted | *"Карактер објекта: **привремени**"* — base station only (GSM housing + antenna tower) | [LU] p. 1 |
| Basic wind velocity (certified) | **v<sub>m,50,10</sub> = 35,0 m/s**, k<sub>t</sub> = 1,00, k<sub>T</sub> = 0,92 → v<sub>m,T,10</sub> = 32,2 m/s | [AG] §L9; [WIND-XLS] sheet *AS 38 m 30m-s* C4, C19 |
| Wind code used in certified project | **JUS U.C7.110 – 113** (not EN 1991-1-4) | [AG] §L9 |
| Basic wind pressure at 10 m | q<sub>m,T,10</sub> = 0,565 kN/m² (ρ = 1,0904 kg/m³ at 1 077 m) | [WIND-XLS] F4, E4 |
| **Design wind pressure on panel elements at this site** | **W = 1,20 kN/m²** ("Maksimalno dopušteno opterećenje panela odgovara opterećenju vjetrom brzine v = 185 km/h") | [AG] §4.4.2.4 |
| **BH Telecom standard wind pressure, exposed structures ≤ 10 m, all BiH ≤ 1 500 m** | **1,10 kN/m²** | [PZ] §2.12 |
| Design ice (rime) | **s = 0,02 m radial**, ρ<sub>e</sub> = 300 kg/m³ ([AG]) / 500 kg/m³ ([WIND-XLS]) | [AG] §L10; [WIND-XLS] sheet *snijeg* F7:H7 |
| **BH Telecom standard snow load, all BiH ≤ 1 500 m** | **3,00 kN/m²** (roof) | [PZ] §2.12 |
| Snow used for panel elements at this site | S = 2,10 kN/m² | [AG] §4.4.2.4 |
| **Geotechnical investigation** | **"GEOMEHANIČKI ELABORAT: nema"** — none exists; tower designed for assumed σ<sub>doz</sub> = 150 kPa, to be verified by a geotechnician on opening the excavation | [AG] "GEOMEHANIČKI ELABORAT"; [AG] §PRORAČUN TEMELJA |
| Excavation class (certified project, tower) | IV–V kategorija | [AG] §4.5.1 |

### 2.2 Existing structures

| Item | Value | Source |
|---|---|---|
| Antenna tower | Lattice, h = 38,00 m, base 4,20 × 4,20 m | [AG]; [LU]; [S-01] |
| **Tower foundation** | **Massive RC block 5,40 × 5,40 × 1,80 m**, MB 25 frost grade M-100; **0,30 m above ground, 1,50 m below** | [AG] §2.1.2 / §"Temeljenje antenskog stuba" |
| Container | Type **"K2"**, anchored **directly onto the tower foundation block** by drilled anchors | [AG] §NAMJENA, §TEMELJENJE |
| Container external dims — **four conflicting values** | 3,00 × 2,10 × 2,40 m [TD §3.1.3] · 3,08 × 2,20 m [S-01] · 3,08 × 2,80 m [S-03] · 3,00 × 2,44 × 2,89 m [LU] | as noted |
| Container mass | ~850 kg [TD §3.1.3] | [TD] |
| Container floor build-up | 0,8 mm galv. sheet + 100 mm mineral wool (50 kg/m³) + 20 mm WBP plywood + antistatic PVC | [AG] §POD |
| **Container floor design load** | **2,00 kN/m² UDL + concentrated loads of the specified equipment schedule (2 × RBS 250 kg + 2 × rectifier 900 kg), with local strengthening where required** | [PZ] §2.12; [AG] §POD |
| Container door | **1 000 × 2 020 mm** (certified project) vs **900 × 2 000 mm** (tender) | [AG] §ULAZNA VRATA; [TD] §3.1.7, [BOQ] LOT 2 4.1 |
| Fence | Posts 50/50/3, total 2 000 mm of which 200 mm cast in → **1 800 mm above ground** (tender states 1 900 mm) | [AG] §4.6 predmjer; [TD] §3.1.3 |
| Gate | **1 000 × 1 800 mm** single leaf, east side | [AG] §4.6 predmjer; [S-01] |
| Leased plot | ≈ 150 m² (drawn 16,00 × 9,40 m = 150,4 m²) | [S-01]; [TD] §3.1.3 |
| Outdoor cabinets | **Huawei ICC330-H1 (outdoor) + MTS9302 — on the NORTH side of the container** | [S-01], [S-02] legend note |

### 2.3 LOT 1 — PV support as tendered

| Parameter | Tendered value | Verified value / comment |
|---|---|---|
| Product | Huawei Standard A-Shaped Support, **LOW** variant, 2 no. | Parts list in [BOQ] 1.1 matches [HW-QG] p. 9 **exactly** (4089×4, 3656×2, 2986×1, 2165×2, 1862×4, 1321×2, 4 column brackets, 8 anchor brackets, M12×100/M12×140) ✔ |
| Modules | 6 × Huawei **iPV585-M2A** per support (12 total, 7,02 kWp) | Support is qualified for **540 W / iPV540-M1A only**, 2 256–2 285 × 1 133–1 134 × **35 mm** [HW-QG] pp. 19, 32 — 585 W not covered |
| Tilt | **fixed 45°** ("prema projektnoj tabeli proizvođača za 31–45° → 45°") | Latitude table [HW-QG] p. 14 is an **energy** rule, not a structural one |
| Azimuth | 180° (south) | ✔ correct for 42,94 N |
| **Array envelope stated** | **4 089 mm × 2 590 mm** (horizontal projection at 45°) | **WRONG** — see §5, Finding R-02. Array is ≈ **3 442 mm wide × 3 236 mm projection**; 4 089 is the *beam* length and 2 590 = 3 656 · cos 45° is derived from the *longitudinal beam*, not the module field |
| Module edge heights stated | bottom +0,50 m, top **+3,09 m** | Correct top edge = 0,50 + 4 576·sin 45° = **+3,74 m** |
| Foundations | 2 strips/support, 450 (550 at base) × 3 300 × 900 deep, C25 on C10, Ø10 @ 335 MPa (19,53 kg/strip), 2 600 mm centres N–S, U-anchors M16/320, 180 mm legs, 2 groups @ 1 800 mm | Numerically identical to [HW-GD] p. 4/p. 5, **but that drawing is titled "Sharp A Bracket 3.0 Foundation (HIGH solar bracket) / 高支架"** — see Finding R-03 |
| Manufacturer per-strip quantities | concrete 0,407 m³ · cushion 0,094 m³ · excavation 1,59 m³ · backfill 1,10 m³ · rebar 19,53 kg | [HW-GD] p. 5, tables "Steel Bar List of Each Foundation" and "Concrete and Excavation List of Each Foundation" |
| **Actual foundation geometry** | *not a 900 mm deep strip* | Footing slab 3 300 × 450/550 × **200 mm** + **two 280 × 280 × 700 pedestals** @ 1 800. Check: 3,30·0,45·0,20 + 2·0,28·0,28·0,70 = 0,297 + 0,110 = **0,407 m³** ✔ exact |
| Manufacturer rated wind (3 s gust) | 15° → 40 m/s · 25° → 40 m/s · 35° → 35 m/s · **45° → 31 m/s** | [HW-GD] p. 3 "GENERAL DESCRIPTION / SCENE" |
| Manufacturer soil requirement | f<sub>ak</sub> ≥ 100 kPa | [HW-GD] p. 3 and p. 5 note 2 |
| Manufacturer terrain validity | *"flat terrain where the ground surface roughness category is **C in ASCE 7-05** (B in GB50009-2001)"* | [HW-GD] p. 3 |
| **Manufacturer caveat** | *"In some particular scene, such as island and **mountain peak**, site designer should **recheck the foundation design and modify the drawing**"* | [HW-GD] p. 3 "NOTICE" |

### 2.4 LOT 2 — genset installation

| Parameter | Tendered value | Source / comment |
|---|---|---|
| Genset | FG Wilson **P22-6**, 22 kVA / 17,6 kW standby, skid ("inside skid"), on AVMs | [BOQ] LOT 2 1.1, 4.1 |
| **Genset mass & dimensions** | **NOT STATED ANYWHERE** | [P22] contains no mass and no dimensions (pp. 1–3 are image-only; the extracted text lists ratings and equipment only) |
| Fuel tank | 500 l double-wall steel, inside the container, + 110 % bund (tankvana) | [BOQ] LOT 2 4.2, 4.3 |
| **Claimed floor capacity** | **10,00 kN/m²**, "prema statičkom proračunu tipskog kontejnera **K3**" | [BOQ] LOT 2 §4 note, 4.4; [S-03] note 6 — **no such document is in the pack, and this site has a K2 container** |
| Claimed usable budget | "cca 5,0 kN/m² na zoni od cca 5,8 m²"; skid + full tank "cca 1 150–1 350 kg na 2–3 m²"; *"ojačanje se NE očekuje kao neophodno"* | [BOQ] LOT 2 4.4 |
| Access route stated | gate clear width ~1,00 m; container door 900 × 2 000 mm; *"Ponuđač … dužan je u ponudi potvrditi izvodljivost"* | [TD] §3.1.7; [BOQ] LOT 2 4.1 |
| Reference precedent | MATISA 2008: purpose-built genset container, **floor 8,00 kN/m²**, 6 mm chequer deck, joists @ 650 mm, **400 mm RC raft** under the whole container | [MATISA] §POD, §ANALIZA OPTEREĆENJA, §TEMELJNA KONSTRUKCIJA |

---

## 3. FINDINGS — RED (Critical)

> **RED = direct non-compliance, safety hazard, or impossible spatial conflict. Must be resolved before any further design or construction.**

---

### R-01 — **THE DECISIVE FINDING: 45° tilt is not compliant; no standard tilt of this product is compliant at this site**

**Source:** [BOQ] LOT 1 item 1.1 ("inklinacija: fiksno 45°") and item 2.3 ("osnovna brzina vjetra za nagib 45° iznosi 31 m/s (3 s udar)"); [HW-GD] p. 3; [AG] §L9 and §4.4.2.4; [PZ] §2.12; [WIND-XLS] sheet *AS 38 m 30m-s*.

#### R-01.1 The manufacturer's rating

> *"The basic wind speed of the solar bracket is related to the elevation angle of the photovoltaic panel. The basic wind speed for the elevation angle of 15, 25, 35, and 45 degrees is 40, 40, 35, and 31 m/s (3 s time interval)."* — [HW-GD] p. 3

Converted to velocity pressure at ρ = 1,25 kg/m³ (q = ½ρv²):

| Tilt | Rated 3 s gust | Rated velocity pressure |
|---|---|---|
| 15° | 40 m/s | 1,000 kN/m² |
| 25° | 40 m/s | 1,000 kN/m² |
| 35° | 35 m/s | 0,766 kN/m² |
| **45° (tendered)** | **31 m/s** | **0,601 kN/m²** |

The rating is explicitly valid only for *"flat terrain … roughness category C in ASCE 7-05"* and explicitly **excludes** mountain peaks without re-design [HW-GD] p. 3.

#### R-01.2 The site design wind — five independent derivations

**(A) BH Telecom's own type-container design brief.**
> *"Zidove kontejnera proračunati na opterećenje vjetrom od **1,10 kN/m²**, što odgovara **izloženim objektima visine do 10 m nad terenom**"* — [PZ] §2.12, valid *"na bilo kojoj lokaciji sa nadmorskom visinom do 1 500 m.n.m."* ([PZ] §2.1).

The PV supports are precisely such a structure (h = 3,74 m, fully exposed, 1 076 m).
q = 1,10 kN/m² → v = √(2 × 1 100 / 1,25) = **41,9 m/s**.

**(B) The certified site project for BS Sjednica.**
> *"opterećenje vjetrom W = **1,20 kN/m²**"*; *"Maksimalno dopušteno opterećenje panela odgovara opterećenju vjetrom brzine **v = 185 km/h**"* — [AG] §4.4.2.4.

q = 1,20 kN/m² → v = √(2 × 1 200 / 1,25) = **43,8 m/s**. (185 km/h = 51,4 m/s is quoted as the panel's *capability*, above the required value.)

**(C) BAS EN 1991-1-4, terrain category II, no orography.**
Basic velocity back-derived from the certified basic pressure q<sub>b,10</sub> = 0,5653 kN/m² [WIND-XLS] F4 at ρ = 1,25:
v<sub>b</sub> = √(2 × 565,3 / 1,25) = 30,1 m/s → take **v<sub>b</sub> = 30 m/s** (consistent with [AG] v<sub>m,50,10</sub> = 35 m/s × k<sub>T</sub> = 0,92 = 32,2 m/s mean).

Reference height z<sub>e</sub> = top of array = 3,74 m; TC II → z₀ = 0,05 m, k<sub>r</sub> = 0,19:

```
c_r(3,74)  = 0,19 · ln(3,74/0,05) = 0,19 × 4,3149  = 0,8198
v_m        = 0,8198 × 1,00 × 30                    = 24,59 m/s
I_v        = 1 / (1,00 × 4,3149)                   = 0,2318
q_p        = (1 + 7·0,2318) × ½ × 1,25 × 24,59²
           = 2,6224 × 0,625 × 604,7                = 991 N/m²  = 0,991 kN/m²
v_p        = √(2 × 991 / 1,25)                     = 39,8 m/s
```

**(D) BAS EN 1991-1-4 with orography (isolated hilltop, EN 1991-1-4 Annex A.3, c₀ = 1,15).**
```
v_m        = 0,8198 × 1,15 × 30                    = 28,28 m/s
I_v        = 1 / (1,15 × 4,3149)                   = 0,2015
q_p        = (1 + 7·0,2015) × 0,625 × 28,28²
           = 2,4105 × 0,625 × 799,8                = 1 205 N/m² = 1,205 kN/m²
v_p        = √(2 × 1 205 / 1,25)                   = 43,9 m/s
```
**Derivation (D) reproduces the certified project's 1,20 kN/m² [AG] to within 0,5 %** — the chain is validated.

**(E) The site's own JUS calculation (lower bound).** [WIND-XLS] rows 86–91 tabulate *"brzina vjetra po visini objekta"*: at z = 3,5 m, **v = 32,50 m/s (117 km/h)**, q<sub>g,T,z</sub> = 0,660 kN/m². The JUS profile is markedly less onerous than EN near the ground (it applies one uniform gust factor G<sub>z</sub> = 1,807 referenced to z = h/2 = 19 m); it is quoted here only as an absolute floor.

#### R-01.3 Verdict table

| Tilt | Rated q | (A) 1,10 | (B) 1,20 | (C) 0,991 | (D) 1,205 | (E) 0,660 |
|---|---|---|---|---|---|---|
| **45°** — 0,601 kN/m² | | **+83 %** ✗ | **+100 %** ✗ | **+65 %** ✗ | **+100 %** ✗ | **+10 %** ✗ |
| 35° — 0,766 kN/m² | | +44 % ✗ | +57 % ✗ | +29 % ✗ | +57 % ✗ | −14 % ✔ |
| 25° / 15° — 1,000 kN/m² | | +10 % ✗ | +20 % ✗ | −1 % (≈) | +20 % ✗ | −34 % ✔ |

**PLAIN STATEMENT: 45° is NOT compliant.** It is exceeded under **every one of the five derivations**, including the most favourable. In velocity terms the site gust of 39,8–43,9 m/s exceeds the 31 m/s rating by **28–42 %**; in pressure terms — which is what the structure actually resists — by **65–100 %**.

**Which tilt is compliant?** **None of the standard tilts.** 35° fails by 29–57 %. The best-rated tilts (15° and 25°, both 40 m/s) still fall **10–20 % short** of the Investor's own site values (A) and (B), and are at best exactly marginal under a plain EN check without orography (C). Selecting 25° would therefore substitute a *proven* non-compliance with a *marginal* one — and would simultaneously **triple the snow load** (Finding R-05).

**Consequence.** LOT 1 cannot be procured as a catalogue item. It requires either (i) a manufacturer-certified reinforced/special variant demonstrably rated for q<sub>p</sub> ≥ 1,20 kN/m² and s<sub>k</sub> = 3,00 kN/m², or (ii) a bespoke support designed to BAS EN 1993-1-1 for the site actions. **This single answer drives the whole LOT 1 redesign.**

**Aggravating factor.** [BOQ] LOT 1 item 1.3 prices the certified static calculation as a **post-award deliverable**. Because the standard product provably cannot satisfy the site actions, the tender as written *guarantees* a post-award variation. The proof of wind and snow resistance must be a **pre-award qualification requirement** (see A-03).

---

### R-02 — Panel-field geometry is wrong by 650 mm; every derived dimension in the tender is affected

**Source:** [BOQ] LOT 1 item 1.1; [S-02]; [S-03] notes 1 and 3; [HW-QG] pp. 9, 19; [HW-GD] p. 4.

The tender states the horizontal projection at 45° as **2 590 mm** and the top module edge as **+3,09 m**. 2 590 = 3 656 · cos 45° — i.e. it was derived from the **longitudinal beam (rafter)**, not from the module field.

**Correct derivation.** From [HW-QG] p. 9 the LOW support has **4 horizontal beams** and **8 edge + 8 middle clamps** (9 of each including one spare). That clamp/beam count is satisfied by exactly one layout: **2 rows up-slope × 3 portrait modules across**, each row carried on 2 horizontal beams, giving 2 edge + 2 middle clamps per beam. Therefore:

```
module field slope length = 2 × 2 278 + 20 (gap)  = 4 576 mm
horizontal projection at 45° = 4 576 × cos 45°    = 3 236 mm   (tender: 2 590 mm)
vertical rise at 45°         = 4 576 × sin 45°    = 3 236 mm
top module edge              = 0,50 + 3,236       = +3,74 m    (tender: +3,09 m)
array width                  = 3 × 1 134 + 40     = 3 442 mm   (tender: 4 089 mm = beam length)
array area                   = 6 × 2,278 × 1,134  = 15,50 m²
```

**Independent corroboration from the manufacturer's own drawing.** The dashed *"Solar panel Contour (6×540W)"* on [HW-GD] p. 4 was measured from the PDF vector geometry. Scaling on the hard 2 600 mm strip-centre dimension (strip width scales to 449 mm against the drawn 450 mm — 0,2 % error), the contour measures **≈ 4,16 m in the N–S direction**. The Quick Guide states the HIGH-support illustration is drawn at 25° [HW-QG] p. 13; 4 576 × cos 25° = **4 147 mm**. The agreement (0,3 %) confirms a module field of ≈ 4 576 mm slope length. *Caveat: the plan on [HW-GD] p. 4 is internally inconsistent by ~5 % between its two axes and must not be scaled for construction.*

**Effects — answering each part of the question:**

| Affected item | Effect |
|---|---|
| **2 600 mm strip spacing** | **UNAFFECTED.** 2 600 mm is the fixed column-base spacing of the support frame [HW-GD] p. 4, not a function of the panel projection. However [BOQ] 2.3 implies the two are linked ("u pravcu nagiba panela … na osovinskom razmaku 2600 mm"); the wording must be corrected so no bidder "adjusts" it. |
| **Footprint vs the 150 m² plot** | Per support: 4,089 × 3,30 = 13,5 m² (foundation) → 2 supports = 27,0 m². Plus the existing 5,40 × 5,40 = 29,2 m² compound = 56 m² of 150 m². **Area is not the constraint.** The constraint is depth: [S-02] leaves only 4,00 m between the compound's south fence and the plot's south boundary; a 3,30 m foundation plus a 3,24 m array leaves **≈ 0,7 m to the boundary and ZERO clearance behind (north of) the arrays**. |
| **Setback from the 1,90 m fence** | [S-03] note 3 and [S-02] annotate the array's plan overhang past the fence line as **0,17 m** in one place and **0,20 m** in another (two different values on the same drawing set). With the correct projection, the overhang becomes **0,17 + 0,65 = ≈ 0,82 m**, at a height of 3,74 m, over the fence and over the tower foundation block. Alternatively the supports must move **0,65 m south**, reducing the boundary setback to ≈ 0,05 m. Either way the layout must be re-drawn. |
| **Overturning lever arm** | Array centroid height rises from 0,50 + ½·3 663·sin45° = **1,79 m** to 0,50 + ½·4 576·sin45° = **2,12 m**, i.e. **+18 %**, and the wind area rises from the implied 12,6–15,0 m² to the true **15,50 m²**. Combined effect on the overturning moment: **+22 % to +45 %** relative to the tender's implicit basis. See R-04. |

**Additional internal contradiction.** [BOQ] 1.1 states the support *"naliježe nad plato AB ploče 5,40 × 5,40 m"* (overlies the slab). [S-02] shows both supports **entirely south of and clear of** the compound. The BOQ text and the drawing disagree.

**Dependency.** The exact iPV585-M2A module dimensions are not in this pack. The parallel Huawei/PV review must confirm 2 278 × 1 134 mm; if the module differs, the projection changes proportionally. The **conclusion does not change** — the tender's 2 590 mm cannot be correct under any plausible module size.

---

### R-03 — Foundation details are taken from the **HIGH**-support drawing while the parts list specifies the **LOW** support

**Source:** [HW-GD] pp. 3, 4, 5 title block: *"Sharp A Bracket 3.0 Foundation **(High solar bracket)**" / "A型支架3.0基础基础（高支架）"*; [BOQ] LOT 1 items 1.1 and 2.3.

All three foundation sheets supplied are for the **HIGH** bracket. [BOQ] 1.1 specifies *"NISKA izvedba (Standard A-Shaped Support — LOW SUPPORT)"* and lists the LOW parts (columns 1 862 mm × 4, no 3 391 mm high columns) — correctly. But **all** foundation data in [BOQ] 2.3 (3 300 / 450 / 550 / 900 / 2 600 / 1 800 / 0,407 / 0,094 / 1,59 / 1,10 / 19,53 kg) come from the HIGH-support drawing.

**Why this matters concretely:** the **1 800 mm anchor-group spacing** is the column-base spacing of the frame. If the LOW support at 45° has a different base spacing, the M16 U-anchors will be cast into the concrete in the wrong position — an **irreversible** construction error discovered only at steel erection. The LOW-support foundation drawing is not in the pack.

**Action:** obtain and issue the LOW-support foundation drawing, or delete all foundation dimensions from [BOQ] 2.3 and make them an output of the item 1.3 static calculation.

---

### R-04 — Uplift and overturning: the standard foundation is inadequate at this site by a factor of ≈ 2

**Source:** [BOQ] LOT 1 item 2.3 (*"MJERODAVNO je podizanje (uplift) i prevrtanje konstrukcije, a ne nosivost tla (kamenito tlo)"* — also [BOQ] 1.1 and [S-03] note); [HW-GD] p. 5; [AG] §4.4.2.4; [AG] §KONTROLA TEMELJA NA PREVRTANJE.

The BOQ's premise — that uplift and overturning govern, not bearing — is **correct**. The arithmetic, however, has not been done.

**Actions per support** (characteristic, using the Investor's own site pressure q = 1,20 kN/m² [AG] §4.4.2.4, net force coefficient c<sub>f,net</sub> = 1,3 normal to the array, array area 15,50 m², tilt 45°):

```
F_w,normal   = 1,3 × 1,20 × 15,50                        = 24,18 kN
F_uplift (V) = 24,18 × cos 45°                           = 17,10 kN
F_horiz  (H) = 24,18 × sin 45°                           = 17,10 kN
lever arm to foundation base h = 2,118 (centroid) + 0,90 = 3,018 m
```

**Resistances per support:**
```
2 strips × 0,407 m³ × 25 kN/m³                           = 20,35 kN
steel frame (~140 kg) + 6 modules (~190 kg)              =  3,20 kN
                                                    W_tot= 23,55 kN
```

**(a) Global uplift (EN 1990 Table A1.2(A) / EN 1997 UPL: γ_Q,dst = 1,5; γ_G,stb = 0,9):**
```
E_d,dst = 1,5 × 17,10 = 25,65 kN
R_d,stb = 0,9 × 23,55 = 21,20 kN      →  utilisation 1,21   ✗ FAILS
```
Even with the most generous coefficient c<sub>f,net</sub> = 1,0: E<sub>d,dst</sub> = 19,73 kN vs 21,20 kN — a residual margin of 7 %, i.e. **no margin at all**, and that ignores the local edge/corner pressure zones which for free-standing PV arrays reach 2–3 × the mean.

**(b) Overturning about the leeward strip axis (taken at foundation base level):**
```
M_dst = 17,10 × 1,30 + 17,10 × 3,018 = 22,23 + 51,61      = 73,84 kNm
M_stb = 10,18 × 2,60 + 3,20 × 1,30   = 26,47 +  4,16      = 30,63 kNm
γ = M_stb / M_dst = 0,41                                    ✗ FAILS grossly
```
Net design uplift on the **windward strip**: (1,5 × 73,84 − 0,9 × 30,63) / 2,60 = **32,0 kN**, against a strip self-weight of 10,18 kN and essentially **zero overburden** (the pedestals project above ground; no soil sits on the footing).

**Benchmark.** The certified project checked the 38 m tower foundation to γ = M<sub>s</sub>/M<sub>p</sub> = 3 618 / 1 693 = **2,14** against overturning ([WIND-XLS] sheet *temeljni blok* C27, C28, C30). The tendered PV foundation achieves **0,41** at the same site. The disparity is not a matter of judgement.

**Reconciling the BOQ's three contradictory statements about the ground:**

| Statement | Assessment |
|---|---|
| *"MJERODAVNO je podizanje (uplift) i prevrtanje … a ne nosivost tla (kamenito tlo)"* | **Correct in principle.** Downward check: (W + V) / A = (23,55 + 17,10) / (2 × 3,30 × 0,55) = 40,65 / 3,63 = **11,2 kPa** — trivially satisfied by any ground. Bearing is genuinely not the governing action. |
| *"nosivost tla ispod temelja (f_ak) mora iznositi najmanje 100 kPa"* | Not contradictory — it is the **manufacturer's minimum** [HW-GD] p. 3, quoted correctly. But **no evidence is required from the bidder and none exists**: [AG] states plainly **"GEOMEHANIČKI ELABORAT: nema"**, and the tower foundation was designed on an *assumed* σ<sub>doz</sub> = 150 kPa with a mandatory geotechnician's inspection of the open excavation. That mandatory inspection has **not** been carried into this tender. |
| Excavation priced as *"zemlja IV-V kategorije"* | **Contradicts** the "kamenito tlo" assertion in method terms, not in substance. Category IV–V is rock requiring hydraulic breaking or blasting; [BOQ] 2.1 prices plain excavation with no rock-breaking, and [BOQ] 2.2 then requires the same material to be placed back as compacted layered fill — broken rock cannot be compacted as ordinary trench backfill. See R-07. |

**Does the dead weight resist the uplift at the governing tilt?** **No.** At 45° it is short by ~21 % on global uplift and by ~59 % on overturning. The correct and cheap remedy on rock is **not** a heavier footing but **hold-down**: 2 no. Ø25 resin-anchored rock dowels per strip, ≥ 1,0 m embedment into sound rock (typical bond capacity 150–250 kN/m ⇒ > 150 kN per dowel, against 32 kN demand). This is **not in the tender**.

---

### R-05 — Snow: the LOW support with a +0,50 m bottom edge will be buried; the wind justification and the snow requirement are in direct conflict

**Source:** [BOQ] LOT 1 item 1.1 (*"opterećenje snijegom prema EN 1991-1-3"*, *"donja zona PV panela na +0,50 m"*); [S-03] note 4 (*"Donja ivica panela na +0,50 m — niska ugradbena visina uz propuštanje snijega"*) and note 1 (*"Niski nosač zbog VJETRA"*); [PZ] §2.12; [AG] §4.4.2.4, §L10.

**Characteristic ground snow load.** The BiH National Annex map value is not reproduced in the tender pack (**YELLOW Y-01**). The Investor's own governing figure is unambiguous:
> *"Krovnu konstrukciju proračunati na opterećenje snijegom od **3,00 kN/m²**, što odgovara svim lokacijama do 1 500 m.n.m."* — [PZ] §2.12

and the certified site project uses **S = 2,10 kN/m²** for panel elements [AG] §4.4.2.4. Adopt **s<sub>k</sub> = 3,00 kN/m²** at 1 076 m pending NA confirmation.

**Snow on the array (EN 1991-1-3 §5.3.2, Table 5.2, μ₁ = 0,8·(60−α)/30 for 30° ≤ α ≤ 60°; C<sub>e</sub> = C<sub>t</sub> = 1,0):**

| Tilt | μ₁ | s on horiz. projection | Projected area | Load per support |
|---|---|---|---|---|
| **45° (tendered)** | 0,40 | 1,20 kN/m² | 15,50·cos45° = 10,96 m² | **13,2 kN** |
| 35° | 0,67 | 2,00 kN/m² | 12,70 m² | 25,4 kN |
| 25° | 0,80 | 2,40 kN/m² | 14,05 m² | **33,7 kN** |
| 15° | 0,80 | 2,40 kN/m² | 14,97 m² | 35,9 kN |

**This is the conflict, quantified.** [S-03] note 1 states the LOW support and the 45° tilt were chosen **"zbog VJETRA"**. But:
- 45° is the **worst** tilt for wind (31 m/s rating) and the **best** for snow (μ₁ = 0,40, and snow slides off a 45° glass surface);
- 25° is the **best** available for wind (40 m/s) and the **worst** for snow (**2,6 × the load**, and snow does **not** reliably shed below ~30°).

The two decisions were therefore made independently and in opposite directions. Neither the tilt nor the support height was chosen on a load basis.

**Burial of the bottom edge — the harder problem.** At s<sub>k</sub> = 3,00 kN/m², the equivalent settled snow depth (γ ≈ 2,0–3,0 kN/m³) is **1,0 – 1,5 m** of undrifted snow. On a bura-swept summit at 1 076 m, drift accumulation against an obstruction (EN 1991-1-3 §6.2) routinely reaches **1,5 – 2,5 m**. A bottom module edge at **+0,50 m** will therefore be **buried in a normal winter**, with the following consequences:

1. Complete loss of the lower module row for weeks at a time — precisely in the season when a *standby-only* hybrid site depends on PV output.
2. Drift and ice loading on the module face and lower frame far in excess of the design snow load, applied as an out-of-plane pressure the clamps are not designed for.
3. Snow-creep and ice-lens forces on the lower frame, clamps and the anchor brackets — a common failure mode for low-mounted arrays.
4. The bottom edge is 0,50 m above the **natural ground outside the compound**, while [BOQ] 1.1 quotes the datum as *"+0,50 m od nivoa AB ploče objekta"*. The tower foundation block stands **0,30 m above ground** [AG] §2.1.2 — so the two datums differ by 300 mm and the drawing [S-03] shows a single ground line. **Datum error.**

**Requirement.** For s<sub>k</sub> = 3,00 kN/m², the bottom module edge must be at **≥ 1,20 m** above finished ground, preferably **1,50 m**. That is exactly what the Huawei **HIGH** support (3 391 mm columns) exists for [HW-QG] p. 11 — but the HIGH support has a *worse* wind problem. The site needs a purpose-designed structure: **steep tilt (40–45°) for snow shedding and winter yield, raised bottom edge ≥ 1,20 m, and a frame designed for q<sub>p</sub> = 1,20 kN/m²**.

**Rime ice, unaddressed anywhere.** The certified project designs the tower for **20 mm radial rime at 300 kg/m³** [AG] §L10 (500 kg/m³ in [WIND-XLS] — an inconsistency within the certified project itself). The site is in a severe icing zone. Neither the tender nor the manufacturer documentation addresses ice on the array, ice-shedding from a 3,7 m high inclined glass surface onto the walkway below, or the increase in frame wind area under glaze. Not a single item in [BOQ] LOT 1 covers it.

---

### R-06 — [BOQ] LOT 1 item 2.3 misdescribes the foundation; description and quantity differ by a factor of 3,3

**Source:** [BOQ] LOT 1 item 2.3; [HW-GD] p. 5 (section B–B, section A–A, and the "Concrete and Excavation List of Each Foundation" table).

The item reads: *"Traka je širine 450 mm (550 mm u dnu), dužine 3300 mm i **dubine 900 mm** … 2 nosača × 2 trake × **0,407 m³**."*

A prismatic element 3 300 × 450/550 × 900 has a volume of **1,37 m³**, not 0,407 m³. A bidder pricing from the written description would compute **5,48 m³** against a priced quantity of **1,63 m³**.

The manufacturer's actual element ([HW-GD] p. 5 sections) is a **footing slab 3 300 × 450 (550 at base) × 200 mm thick with two 280 × 280 × 700 mm pedestals at 1 800 mm centres**; the "900 mm" is the overall depth from pedestal top to underside of slab:

```
3,300 × 0,450 × 0,200            = 0,297 m³
2 × 0,280 × 0,280 × 0,700        = 0,110 m³
                            total = 0,407 m³   ✔ exactly the manufacturer's figure
```

**The priced quantity is right; the description is wrong.** As written the item is a guaranteed claim under [TD] §8.2 (viškovi radova). It must be rewritten to describe the slab-plus-pedestal geometry explicitly, with the pedestal formwork (8 boxes 280 × 280 × ~800 mm) stated.

The same error has propagated into **item 2.4** — see R-07 and §5.

---

### R-07 — [BOQ] LOT 1 item 2.7 prices a 5,40 × 5,40 m slab that already exists as the 1,80 m deep tower foundation block: **DELETE**

**Source:** [BOQ] LOT 1 item 2.7; [AG] §2.1.2 and §"Temeljenje antenskog stuba"; [S-01].

Item 2.7 prices *"betoniranje AB platforme (nivelacijska/temeljna ploča) betonom C20/25, debljine 10 cm, armirane mrežom Q188 … sa oplatom po obodu (perimetar 21,60 m) … dimenzija **5,40 × 5,40 m** … 2,92 m³"*.

The certified project states:
> *"Temeljenje antenskog stuba je ostvareno preko temeljnog bloka dimenzija **5.40 × 5.40 × 1.80 m** od betona MB 25 marke na mraz M-100. Temelj je nad zemljom 30 cm, a ispod 1.50 m."* — [AG]

and

> *"Temeljenje objekta [kontejnera] se vrši na AB temeljnoj konstrukciji — **temeljnom bloku antenskog stuba** ankerisanjem pomoću čeličnih anker sidara."* — [AG] §TEMELJENJE

[S-01] confirms it on the drawing. The 5,40 × 5,40 m element is not a levelling slab — it is a **52,5 m³ massive RC foundation block carrying the 38 m tower and the container**, standing 300 mm proud of the ground.

**Verdict: DELETE item 2.7.** It is a template artefact — its own note (*"konačna debljina, klasa betona i armatura utvrđuju se glavnim projektom … količina je data orijentaciono"*) confirms it was copied from another site and never checked. It cannot be "rewritten as a local slab under the new supports" because the PV supports have their own strip footings under items 2.1–2.3 and require no slab; a 100 mm Q188 slab would in any case be structurally useless as a support foundation. Its removal takes an estimated **1 500 – 2 500 KM (10–17 %)** out of a LOT 1 valued at 15 000 KM.

**Replace with the two items that are genuinely missing:**
- **Fence extension**, which [TD] §3.1.3 explicitly promises (*"ukupno zakupljena površina parcele 150 m², zbog čega je predviđeno **proširenje postojeće ograde**"*) but which appears in **no BOQ item and on no drawing**. As tendered, ~15,5 m² of PV modules and 12 no. 585 W panels sit **outside any fence** on an unmanned mountain site — with no security, no protection from livestock, and the manufacturer's anti-theft nuts as the only mitigation.
- **Site reinstatement / regrading** around the new foundations (the certified project has an equivalent item; [AG] §4.5.1).

---

### R-08 — Container floor: the "10,00 kN/m²" capacity is unsubstantiated; the correct design value is 2,00 kN/m², and the check **FAILS**. The steel grillage is REQUIRED, not optional

**Source:** [BOQ] LOT 2 §4 general note, item 4.4; [S-03] note 6; [TD] §1.7; [PZ] §2.12; [AG] §POD, §NAMJENA; [MATISA]; [P22].

**(a) The figure has no source.** The tender asserts *"Nosivost poda kontejnera je 10,00 kN/m² … prema statičkom proračunu **tipskog kontejnera K3**"* three times ([BOQ] §4 note, [BOQ] 4.4, [S-03] note 6). Two problems:
1. **No such calculation is in the pack.** A full-text search of the project documentation returns no 10 kN/m² floor value anywhere.
2. **This site does not have a K3 container.** The certified project is explicit: *"isprojektovan je tipski montažni objekat **"K2"**"* [AG] §NAMJENA, and the folder itself is named *SITE-PROJECT-SJEDNICA-Bileca-**K2**-S38-m*. The K3 drawings in the certified project are filed under *"kontejner K3 **ne printati**"*.

**(b) The governing design value is 2,00 kN/m².**
> *"Podnu konstrukciju proračunati na ravnomjerno podijeljeno opterećenje u iznosu **2,00 kN/m²** i na koncentrisana opterećenja od težine ugrađene opreme. Na mjestima montaže opreme po potrebi predvidjeti dodatna [ojačanja]."* — [PZ] §2.12

(The 3,00 kN/m² in the same clause is **roof snow**; the 1,10 kN/m² is **wall wind**.) The certified project confirms the capacity is layout-specific: *"Nosivost podne konstrukcije je određena prema rasporedu GSM opreme"* [AG] §POD, for a schedule of **2 RBS cabinets + 2 rectifier systems + AC unit + distribution board** [AG] §NAMJENA, [LU] p. 1. Neither a genset skid nor a fuel tank is in that schedule.

**(c) The floor build-up cannot take point loads.** 0,8 mm galvanised sheet + 100 mm mineral wool + 20 mm WBP plywood + antistatic PVC [AG] §POD. By contrast the purpose-built genset container [MATISA] uses a **6 mm chequer plate deck on joists at 650 mm**, designed for **8,00 kN/m²**, on a **400 mm RC raft**.

**(d) The check.** The P22-6 datasheet supplied contains **no mass and no dimensions** [P22] — the tender's own load basis is undocumented. Using typical manufacturer figures for the P22-6 open skid set (**≈ 1 730 × 750 × 1 220 mm, ≈ 610 kg dry / ≈ 650 kg operating**), which must be confirmed:

```
Genset, operating (oil, coolant, battery)           6,4 kN over 1,73 × 0,75 = 1,30 m²  → 4,9 kN/m² mean
  per anti-vibration mount (4 no.)                  1,6 kN on ≈120 × 120 mm            → 111 kN/m² LOCAL
  per skid rail (2 lines, 1,73 m long)              3,2 kN/line                        → 1,85 kN/m LINE LOAD
500 l double-wall tank + bund:
  diesel 500 l × 0,832 kg/l                         4,16 kN
  tank shell (double wall, steel)                   1,80 kN
  bund / tankvana 110 % = 550 l                     0,60 kN
                                             total  6,56 kN over ≈1,30 × 0,85 = 1,11 m² → 5,9 kN/m²
NEW LOAD TOTAL                                     12,96 kN  (≈ 1 320 kg)
```

Container net internal floor (3,08 × 2,20 external [S-01], 60 mm walls [LU]): **2,96 × 2,08 = 6,16 m²**.

```
New equipment alone            12,96 / 6,16 = 2,10 kN/m²   >  2,00 kN/m² design UDL
+ existing TK equipment (~600 kg)              0,96 kN/m²
+ maintenance imposed load (EN 1991-1-1)       2,00 kN/m²
                                    TOTAL   ≈  5,06 kN/m²
```

**Utilisation against the design basis of 2,00 kN/m²: ≈ 2,5. The check FAILS.** It also fails against [MATISA]'s purpose-built 8,00 kN/m² on **local** grounds: 111 kN/m² under each AVM will punch a 0,8 mm sheet + 20 mm plywood deck.

**Load spreading alone is impossible.** To bring 12,96 kN down to 2,00 kN/m² requires 6,5 m² — larger than the entire floor. **The load must therefore be taken out of the container floor altogether.**

**(e) Required specification for the "roštilj" (grillage) — to replace [BOQ] LOT 2 item 4.4:**

> **Preferred (base case).** An independent hot-dip galvanised steel frame (EN ISO 1461) carrying the genset skid and the tank/bund, taking its load **through the container floor** onto **new concrete pads bearing directly on the existing 5,40 × 5,40 × 1,80 m tower foundation block** (which has abundant reserve capacity), structurally independent of the container floor. Local penetrations through the floor to be sealed, insulated and made watertight.
>
> **Alternative (only if a certified calculation demonstrates the container's perimeter floor frame is adequate).** Two longitudinal main beams (e.g. UNP 120 / HEA 100, S235) under the skid rails, spanning the container's short direction onto the perimeter floor beams; cross members at ≤ 650 mm centres under the tank/bund zone; **6 mm chequer plate deck** over the whole genset + tank zone (matching the [MATISA] precedent); all connections bolted/welded and hot-dip galvanised.
>
> **Measurement:** the grillage must be a **measured item in kg (estimate 180–250 kg)**, not a "kpl" lump combined with the calculation. As currently written, item 4.4 bundles an engineering study *and* an unquantified strengthening works into one lump sum with the instruction *"ojačanje se NE očekuje kao neophodno"* — it is **unpriceable**, and every bidder will price it at zero.

**(f) The container's own anchorage and foundation.** The new load increases the container's total mass from ~850 kg to ~2 200 kg (**+155 %**). The container is anchored to the tower foundation block by drilled anchors [AG] §TEMELJENJE, so the *foundation* is adequate — but the anchor group and the container's own steel floor frame have never been checked for this load, nor for the additional overturning from the new north-wall penetrations. **Not required anywhere in the tender.**

---

### R-09 — Genset handling and internal spatial feasibility: the tender delegates an unresolved conflict to the bidder

**Source:** [TD] §3.1.7; [BOQ] LOT 2 items 4.1, 4.2; [S-01], [S-02], [S-03]; [AG] §ULAZNA VRATA, §4.6 predmjer; [LU] p. 1.

**(a) Does it physically fit?** On typical P22-6 open-skid dimensions (1 730 × 750 × 1 220 mm) and the **certified** door of **1 000 × 2 020 mm** [AG] §ULAZNA VRATA:

| Constraint | Aperture | Skid | Clearance |
|---|---|---|---|
| Gate (single leaf) | **1 000 × 1 800 mm** [AG] §4.6 | 750 W × 1 220 H | 250 mm / 580 mm ✔ |
| Container door (certified) | 1 000 × 2 020 mm | 750 × 1 220 | 250 mm / 800 mm ✔ |
| Container door (**as stated in the tender**) | 900 × 2 000 mm | 750 × 1 220 | **150 mm total, 75 mm per side** — marginal |

The gate and the container door are both on the **east** side and are roughly aligned on [S-01], so the set can be pushed straight in without a 90° turn. **Dimensionally it fits** — but on a clearance of 75 mm per side if the tender's own (incorrect) 900 mm figure is the true one, and only for the bare open skid without the control panel, radiator guard or exhaust stub projecting. **This has never been dimensionally verified against a real P22-6 drawing, because no such drawing exists in the pack.**

**(b) The real conflict is inside, and it is not resolvable by the bidder.** Net internal floor **2,96 × 2,08 m = 6,16 m²**, already occupied by existing TK equipment which [TD] §3.1.4 forbids removing (*"bez demontaže postojeće opreme"*). Adding:

```
genset skid           1,73 × 0,75  = 1,30 m²
tank + bund          ≈1,30 × 0,85  = 1,11 m²
new GRO cabinet       0,60 × 0,25  = 0,15 m²   [BOQ] LOT 2 5.6
existing TK racks    ≈             = 0,40 m²
                              total = 2,96 m²  (48 % of the floor)
```
Genset (0,75 m) + tank (0,85 m) side by side = **1,60 m of the 2,08 m depth**, leaving a clear walkway of **≈ 0,48 m**. That is below any reasonable maintenance access and below the minimum escape-route width — in a room containing a **running diesel engine**, **500 l of diesel fuel**, and an **EMERGENCY STOP button required at the door** ([BOQ] LOT 2 4.1). [S-02] and [S-03] show exactly this arrangement, and show no existing equipment at all.

**(c) The tender does not require what it needs.** [TD] §3.1.7 and [BOQ] 4.1 simply state *"Ponuđač bira način unosa i montaže i dužan je u ponudi potvrditi izvodljivost."* The BOQ contains **no** item for: lifting/crane or HIAB, skates/rollers/skid pans, a temporary ramp or platform onto the raised container floor, temporary works, or removal and refitting of a roof or wall panel. There is no internal layout drawing of the existing equipment and no free-space survey.

**What the tender must require instead:**
1. A **dimensioned internal survey drawing** of the container as-built, showing all existing equipment, issued as a tender annex.
2. A **certified skid general-arrangement drawing** with mass and dimensions, as a mandatory pre-award submission (item 6.1.4 asks for catalogue data but does not require dimensions and masses).
3. A stated method: **removal and refitting of one roof panel** is the realistic route for a 650 kg unit onto a raised floor in a 2,08 m deep room; a wall-panel opening is the alternative. Both must be **priced items**, including reinstatement of the thermal envelope and vapour barrier.
4. **Split delivery** (engine/alternator delivered separately from the skid and assembled in situ) is the only route if the 900 mm door figure turns out to be correct — and it invalidates the *"testiran, fabrički testiran i isporučuje se kao jedan proizvod"* requirement of [TD] §6.1.2.
5. A **temporary access platform / ramp** to the container floor level, and confirmation of vehicle access to the gate.

---

### R-10 — Fire and spatial safety: 500 l of diesel and a running engine in an unseparated 6 m² room with live telecom equipment

**Source:** [BOQ] LOT 2 items 4.2, 4.3, 4.11, 4.15; [TD] §1.6; [PZ] §2.4, §2.6 (panel fire class **B1** — combustible PU core).

- The container is a **B1** (combustible) PU sandwich-panel structure [PZ] §2.4/§2.6. A 500 l diesel store plus an operating diesel engine are placed inside it with **no fire compartmentation** of any kind. In BiH practice, storing > 250 l of a flammable liquid indoors alongside an ignition source requires a dedicated fire compartment (EI 60/90 separation) and an approved fire-protection design.
- The [MATISA] precedent placed the gensets in a **container dedicated to gensets**, physically separate from the TK container.
- The exhaust (NO 50, [BOQ] 4.11) penetrates a **PU-cored panel**. Item 4.13 provides 50 mm rockwool lagging and Al cladding ✔ and item 4.11 requires a spark arrester ✔ — both good — but the **wall penetration collar** through the combustible core is not specified.
- No spill containment, no impermeable hardstanding and no spill kit are provided at the tanker fill point, although [BOQ] 4.2 requires an external fill connection and a tanker earthing device.
- **No permit route.** The Lokacijski uslovi [LU] authorise only a base station (GSM housing + antenna tower), *"karakter objekta: privremeni"*. They do **not** cover two PV arrays on permanent concrete foundations, a diesel generator, or a fuel installation. Under Zakon o uređenju prostora i građenju RS (Sl. gl. RS 40/13) these require **amended location conditions and a building permit**, plus fire-protection and environmental consents for the fuel store. [BOQ] contains **no permitting item and no allowance**; [TD] §3.3.1 merely reserves the Investor's right to swap the site if consent is refused.

---

### R-11 — Hot-air discharge, exhaust and combustion-air intake are placed on the same wall as the outdoor power cabinets

**Source:** [S-01] and [S-02] annotation *"postojeći vanjski ormari na **SJEVERNOJ** strani: Huawei ICC330-H1 (outdoor) + MTS9302"*; [S-02] annotation *"LOT 2 — radovi na kontejneru (sve na **SJEVERNOJ** strani)"*; [S-03] note 5; [BOQ] LOT 2 items 4.6–4.9, 4.11.

Every LOT 2 penetration — the 500 × 700 mm fresh-air intake, the 600 × 600 mm hot-air discharge louvre with a 1 200 m³/h fan, and the NO 50 exhaust — is placed on the **north** wall. The Huawei ICC330-H1 outdoor rectifier/battery cabinet and the MTS9302 stand on that same north face, drawn on both [S-01] and [S-02].

Consequences:
- Radiator discharge air from a 22 kVA set is typically 25–40 °C above ambient at 3 000–4 000 m³/h. Directing it at the intake of an outdoor rectifier and LFP battery cabinet will drive nuisance high-temperature alarms, derate the rectifiers, and shorten battery life — the batteries are the core asset of an off-grid hybrid site.
- Diesel exhaust discharged beside the cabinets will foul the heat exchangers and filters.
- Combustion-air intake located next to the exhaust outlet risks recirculation.

The layout is a straightforward conflict visible on the tender's own drawings and has not been recognised.

*Related consistency check:* [BOQ] 4.9 states *"Minimalna potrebna ventilacija prostora iznosi 120 m³/h (6 izmjena zraka na sat)"* — which implies a room volume of 20 m³. The container is **3,08 × 2,20 × 2,40 = 16,3 m³ gross, ≈ 13 m³ net**. The ventilation basis was not checked against the actual container.

---

## 4. FINDINGS — YELLOW (Minor / requires clarification)

| # | Finding | Source | Action |
|---|---|---|---|
| **Y-01** | The BAS EN 1991-1-4 and EN 1991-1-3 **BiH National Annex map values** (v<sub>b,0</sub>, s<sub>k</sub>, zone) for the Bileća region are **not reproduced anywhere** in the tender. All wind and snow values in this review are derived from the Investor's own certified documents, which is defensible but not a substitute for the NA. *Per `prompt.md` §3, a missing applicable code must be flagged.* | — | Obtain and state v<sub>b,0</sub>, terrain category, c₀ and s<sub>k</sub> in the tender |
| **Y-02** | **Module compatibility.** The support is qualified for **540 W / iPV540-M1A** modules, 2 256–2 285 × 1 133–1 134 × **35 mm** [HW-QG] pp. 19, 32. The tender specifies **iPV585-M2A**. If the module thickness is not 35 mm the clamps will not grip; if the dimensions differ, the 31/35/40 m/s ratings do not apply. | [HW-QG] pp. 19, 32 vs [BOQ] 1.1 | Obtain Huawei written confirmation, or change the module |
| **Y-03** | **Rebar grade 335 MPa is not a European grade.** Ø10 at f<sub>yk</sub> = 335 MPa is HRB335 (GB 1499.2); it is not procurable in BiH. BAS EN 1992-1-1 practice is **B500B**. | [HW-GD] p. 5 note 4; [BOQ] 2.3 | Restate as B500B, area ≥ that of the manufacturer's schedule |
| **Y-04** | **Concrete grades and exposure class.** "C25" and "C10" are GB designations. Under BAS EN 206 these should be **C25/30** and **C12/15**. More importantly, at 1 076 m with severe freeze-thaw the exposed foundation requires exposure class **XF3 (+ XC4)**, which demands **≥ C30/37 with air entrainment**. Plain C25/30 is inadequate. The certified project used MB 25 **"marke na mraz M-100"** [AG] §2.1.2 — a frost grade the tender omits entirely. Cover 50 mm ✔ appropriate. | [BOQ] 2.2b, 2.3; [AG] §2.1.2 | Specify C30/37, XC4/XF3, air-entrained, D<sub>max</sub> 16, and a frost-resistance test |
| **Y-05** | **Container dimensions: four conflicting values** — 3,00 × 2,10 × 2,40 [TD §3.1.3]; 3,08 × 2,20 [S-01]; **3,08 × 2,80** [S-03]; 3,00 × 2,44 × 2,89 [LU]. Every spatial and floor-loading conclusion depends on which is right. | as noted | Measure on site; issue one figure |
| **Y-06** | **Container door: 900 × 2 000 mm** (tender) vs **1 000 × 2 020 mm** (certified project [AG] §ULAZNA VRATA). The discrepancy works in the contractor's favour but must be settled before the access method is fixed. | [AG]; [TD] §3.1.7 | Verify on site |
| **Y-07** | **Fence height: 1,90 m** (tender) vs **1,80 m above ground** (certified: 2 000 mm total, 200 mm cast in) [AG] §4.6. | [AG]; [TD] §3.1.3 | Verify; affects the "nadvišenje" note on [S-03] |
| **Y-08** | **Panel overhang annotated twice with different values** — "0,20 m" on [S-02] and "0,17 m" on [S-03], on the same drawing set. | [S-02], [S-03] | Single value after the R-02 geometry correction |
| **Y-09** | **[S-03] contradicts [BOQ] 2.3 on foundation depth** — the section note reads *"Dubina prema statičkom proračunu"* while [BOQ] 2.3 fixes 900 mm and prices 1,63 m³. | [S-03]; [BOQ] 2.3 | Align |
| **Y-10** | **DEA / tank positions differ between plan and section** — [S-02] shows DEA west / tank east; [S-03] shows DEA north / tank south. | [S-02], [S-03] | Align |
| **Y-11** | **BOQ numbering is broken in LOT 2.** The section is headed "1 — AUTOMATSKI DIZEL ELEKTRIČNI AGREGAT" with sub-item 1.1, then jumps to "3.2" and "UKUPNO 3". Item **4.1 cross-refers to "Tačkom 3.1", which does not exist**. Bidders cannot map the references. | [BOQ] LOT 2 rows 11, 12, 54, 55, 59 | Renumber |
| **Y-12** | **Empty priced items.** [BOQ] LOT 1 rows 47 ("2.6") and 49 ("2.8") carry an item number, a unit column and a price column but **no description**. A bidder may insert arbitrary text and price. | [BOQ] LOT 1 rows 47, 49 | Delete or populate |
| **Y-13** | **Item 2.5 "Ostali sitni građevinski i potrošni materijal — paušal 1"** is undefined. Combined with [TD] §8.2, an undefined lump sum on a remeasured contract invites dispute. | [BOQ] 2.5 | Define a scope and a cap, or delete |
| **Y-14** | **First fuel fill contradiction:** [TD] §1.7 requires *"tankanje najmanje **200 l**"*; [BOQ] LOT 2 4.16 prices **500 l**. | [TD] §1.7; [BOQ] 4.16 | Align on 500 l |
| **Y-15** | **[TD] §1.7 is headed "LOT 1" but its entire content is LOT 2** (genset, container floor, exhaust). §1.4 and §1.7 carry the same heading. Editorial, but it is the clause that defines the works. | [TD] §1.4, §1.7 | Correct headings |
| **Y-16** | **Garbled scope sentence** in [TD] §1.7: *"transport montažu nosača fotonaponskih panela za podlogu, uključujući ugradnju sistema za odvod dimnih gasova, žaluzina i ventilacije prostora agregata"* — merges PV supports with flue-gas works. | [TD] §1.7 | Rewrite |
| **Y-17** | **Rime-ice inconsistency inside the certified project itself:** ρ<sub>e</sub> = 300 kg/m³ [AG] §L10 vs 500 kg/m³ [WIND-XLS] sheet *snijeg*. | [AG]; [WIND-XLS] | Resolve before any icing check |
| **Y-18** | **Earthing conductor type.** [BOQ] 1.4 specifies **H07V-K 25 mm²** — a PVC-insulated **indoor** cable, not rated for buried or UV-exposed use. | [BOQ] 1.4 | Use bare Cu 25 mm² or Fe/Zn 25×4 for buried runs |
| **Y-19** | **Lightning protection separation not addressed.** A 3,74 m array with DC cabling sits within metres of a 38 m tower with a bonded LPS. EN 62305-3 separation distance and the need for a **Type 1** DC surge arrester (only Type 2 is specified in [BOQ] 1.6) are not stated. | [BOQ] 1.6, 1.4 | Require an EN 62305 verification |
| **Y-20** | **Acoustic requirement not achievable as specified.** [BOQ] 4.1 requires **< 68 dBA at 7 m at 75 % load**, from an **open** skid set inside a 70 mm PU sandwich enclosure with a 600 × 600 discharge louvre and a 500 × 700 intake louvre. An open 22 kVA set is ~95–100 dBA at 1 m; the two unattenuated louvres bypass the panel insulation entirely. **No attenuators are in the BOQ.** | [BOQ] 4.1, 4.7, 4.8 | Add intake and discharge attenuators as measured items, or delete the requirement |
| **Y-21** | **Forming the wall openings is not priced.** Items 4.7/4.8 price the louvres only; cutting, trimming and reinstating the thermal/vapour envelope of a structural sandwich panel for a 600 × 600 and a 500 × 700 opening plus the NO 50 exhaust is not covered. [BOQ] 5.5 covers cable penetrations only. | [BOQ] 4.7, 4.8, 4.11, 5.5 | Add measured items |
| **Y-22** | **Tanker access is asserted, not verified.** [BOQ] 4.2 requires *"na lokaciji obezbijediti mogućnost prilaza autocisterne"*, while [TD] §3.1.2 describes the access as *"ravni ili strmi makadam, nekategorizirani šumski put ili livada"* requiring off-road vehicles. Refuelling frequency ≈ 1,6 visits/year. No road works, no turning head, no hardstanding priced. | [TD] §3.1.2; [BOQ] 4.2, 4.16 | Survey the route; price access works or change the refuelling method |

---

## 5. BOQ QUANTITY AUDIT — LOT 1, SECTION 2 (recomputed from first principles)

**Basis:** manufacturer per-strip figures [HW-GD] p. 5; 2 supports × 2 strips = **4 strips**; verified element geometry per R-06 (slab 3 300 × 450/550 × 200 + 2 pedestals 280 × 280 × 700; overall depth 900 mm, top of pedestal ≈ 100 mm above finished ground).

| Item | Description | Priced | Recomputed | Verdict |
|---|---|---|---|---|
| **2.1** | Excavation, cat. IV–V | **6,36 m³** | 4 × 1,59 = 6,36 m³ ✔ *arithmetically consistent with the manufacturer.* But 1,59 m³/strip corresponds to a trench of 3,30 × 0,57 × 0,95 with **vertical faces and zero working space**. With a realistic 100 mm working space: 3,50 × 0,75 × 0,85 = 2,23 m³/strip → **8,93 m³**. | **Consistent with the manufacturer; understated by ~40 % against buildable practice.** Also the wording *"iskop **zemlje** IV-V kategorije"* is wrong: category IV–V is **rock** and requires hydraulic breaking or blasting, which is **not priced**. |
| **2.2** | Backfill with excavated material, compacted in layers | **4,40 m³** | 4 × 1,10 = 4,40 m³ ✔ (manufacturer: 1,59 − 0,407 − 0,094 = 1,089). With realistic excavation: 4 × 1,73 = **6,92 m³**. | **Arithmetically correct, but methodologically void.** Broken cat. IV–V rock **cannot** be placed as compacted layered backfill against a foundation. Either import ~4,4–6,9 m³ of granular backfill (**new item**) or delete the compaction requirement. |
| **2.2a** | Spoil disposal to ≤ 20 km | **1,96 m³** | 6,36 − 4,40 = 1,96 m³ in situ ✔. **But spoil is transported LOOSE.** Rock bulks 40–60 %: 1,96 × 1,5 = **2,94 m³ loose**. If the spoil is not reusable (see 2.2), the whole excavation is disposed of: 6,36 in situ = **≈ 9,5 m³ loose**, and with realistic excavation **≈ 13,4 m³ loose**. | **Understated by 50 % at best, by 580 % if the spoil is not reusable.** State the bulking factor and the measurement basis (in situ or loose). |
| **2.2b** | C10 blinding | **0,38 m³** | 4 × 0,094 = 0,376 → 0,38 ✔ (= 3,30 × 0,57 × 0,05) | ✔ **CORRECT** |
| **2.3** | C25 foundation concrete | **1,63 m³** | 4 × 0,407 = 1,628 → 1,63 ✔ (verified: 0,297 slab + 0,110 pedestals = 0,407) | **Quantity CORRECT; DESCRIPTION WRONG** — see R-06. The written geometry (3 300 × 450 × 900) yields 5,48 m³, a **3,3 ×** discrepancy. Rewrite. |
| **2.4** | Cement-mortar finish to visible faces and top surface, 1 % fall | **12 m²** | Exposed concrete = 2 pedestals/strip projecting ≈ 100 mm: top 2 × 0,28² = 0,157 m² + sides 2 × 4 × 0,28 × 0,10 = 0,224 m² = **0,381 m²/strip** → 4 strips = **1,52 m²**; say **2,0 m²** with the anchor-plate grouting. If instead the whole 3,30 m strip top is to be finished and left proud: 4 × (3,30 × 0,45) + exposed sides ≈ **8,9 m²**. | ✗ **OVERSTATED by ≈ 6 ×.** The origin is traceable: 4 × 3,30 × 0,90 = **11,88 ≈ 12 m²** — i.e. the *side elevation* of a strip taken as 3 300 × 900. The R-06 misdescription has propagated into this item. **Correct to 2,0 m²** and rewrite the description. |
| **2.5** | Sundries, lump sum | 1 paušal | — | See Y-13 |
| **2.6** | *(blank)* | — | — | See Y-12 |
| **2.7** | New AB slab 5,40 × 5,40 × 0,10, C20/25, Q188 | **2,92 m³** | 29,16 × 0,10 = 2,916 ✔ arithmetically | ✗ **DELETE — the slab already exists as the 1,80 m deep tower foundation block.** See R-07. |
| **2.8** | *(blank)* | — | — | See Y-12 |
| — | **Reinforcement** | not itemised (inside 2.3) | 4 × 19,53 = 78,1 kg ✔ (R01 3 × 3 300; R02 17 × 450; R03 8 × 900; R04 12 × 560 @ 0,62 kg/m) | ✔ Quantity correct, matches [HW-GD] p. 5 exactly. Make it a measured item (kg) and change 335 MPa → B500B (Y-03). |

### Summary of quantity corrections

| Item | Priced | Corrected | Δ |
|---|---|---|---|
| 2.1 Excavation | 6,36 m³ | **8,93 m³** | +40 % |
| 2.2 Backfill | 4,40 m³ | **6,92 m³** (and change to imported granular) | +57 % |
| 2.2a Spoil disposal | 1,96 m³ | **2,94 m³** loose (reusable) / **13,4 m³** loose (not reusable) | +50 % … +580 % |
| 2.2b Blinding | 0,38 m³ | 0,38 m³ | 0 |
| 2.3 Concrete | 1,63 m³ | 1,63 m³ *(description rewritten)* | 0 |
| 2.4 Mortar finish | 12 m² | **2,0 m²** | **−83 %** |
| 2.7 Slab | 2,92 m³ | **0 — delete** | **−100 %** |
| Rebar (new item) | — | **78,1 kg B500B** | new |
| Rock breaking (new item) | — | measured, cat. IV–V | new |
| Rock dowels (new item) | — | 8 no. Ø25 resin-anchored, ≥ 1,0 m into sound rock | new |
| Fence extension (new item) | — | per revised layout | new |

---

## 6. FINDINGS — GREEN (correctly implemented, note for reference)

| # | Finding | Source |
|---|---|---|
| **G-01** | **The support parts list is exactly correct.** [BOQ] 1.1 reproduces the Huawei LOW-support bill of materials without error: horizontal beam 4 089 × 4, longitudinal beam 3 656 × 2, reinforced beam 2 986 × 1, long raking strut 2 165 × 2, column 1 862 × 4, short raking strut 1 321 × 2, column bracket × 4, anchor bracket × 8, M12×100 and M12×140. Whoever wrote it read the source document properly. | [BOQ] 1.1 vs [HW-QG] p. 9 |
| **G-02** | **The anchor bolt specification is exactly correct.** M16, total length 320 mm, leg spacing 180 mm, anchor plates 50 × 50 mm, double nuts, 2 groups per strip at 1 800 mm centres — all match the manufacturer's anchor-bolt drawing. Requiring double nuts is good practice and matches [HW-QG] p. 16. | [BOQ] 1.2 vs [HW-GD] p. 2, p. 4 |
| **G-03** | **The rebar schedule is exactly correct** — 19,53 kg/strip, 78 kg total, matching R01–R04 in the manufacturer's steel bar list. Cover 50 mm and the ±3 mm setting-out tolerance are both taken correctly from [HW-GD] p. 5 notes 1 and 7. | [BOQ] 2.3 |
| **G-04** | **Orientation and array layout are correct.** Azimuth 180° south for 42,94° N; two supports side by side east–west with no inter-row shading; both arrays **south** of the compound so that neither the 38 m tower nor the container casts a midday shadow on them. This is the right arrangement and the reasoning is sound. | [BOQ] 1.1; [S-02] |
| **G-05** | **Corrosion protection is correctly specified** — hot-dip galvanising to EN ISO 1461 for the structure, A2/A4 stainless fixings. Appropriate for a 1 076 m exposed site. | [BOQ] 1.1 |
| **G-06** | **The manufacturer's mountain-peak caveat was found and quoted** in [BOQ] 2.3: *"Proizvođač izričito zahtijeva da se za lokacije na planinskim vrhovima projekat temelja ponovo provjeri i prilagodi."* The warning was correctly identified — it was simply not acted upon. | [BOQ] 2.3 |
| **G-07** | **Item 1.3 requires a certified static calculation** for site snow and wind, signed by a licensed engineer. The right requirement, in the wrong place in the process (see R-01, A-03). | [BOQ] 1.3 |
| **G-08** | **The exhaust system is well specified** — spark arrester, downturned outlet, elastic connector, 600 °C paint, 50 mm rockwool lagging with Al cladding. This is a correct and complete specification for a mountain site in a fire-risk landscape. | [BOQ] 4.11–4.13 |
| **G-09** | **Winter operation is properly addressed** on the mechanical side — mandatory coolant heater with adjustable thermostat, room heater, fuel-line insulation, tank cold-start protection, −20 °C start requirement, ISO 3046 derating for > 1 000 m. Rare to see this done properly. | [BOQ] LOT 2 1.1, 4.14 |
| **G-10** | **Earthing depth is correctly reasoned** — [BOQ] 5.3 requires the earthing tape at 1,00 m depth *"obzirom da se radi o planinskoj lokaciji (izbjegavanje efekta zaleđivanja tla)"*. Correct, and consistent with the certified project's frost-depth logic (tower foundation 1,50 m below ground, *"izvan zone zamrzavanja tla"* [AG] §2.1.2). | [BOQ] 5.3 |
| **G-11** | **Item 2.4's wording is inherited verbatim from the certified site project** (*"u nagibu 1,0 %, zaglađeno do crnog sjaja"*, [AG] §4.5.1) — good provenance and consistent with the existing works. Only the quantity is wrong. | [BOQ] 2.4; [AG] |
| **G-12** | **Double-wall tank with interstitial leak probe, two independent level gauges of different principle, and remote alarm reporting** is a genuinely good specification for an unmanned site and exceeds common practice. | [BOQ] 4.2 |

---

## 7. DETAILED CHECKLIST (per `prompt.md` §2.4)

### Geometry & Layout
| Check | Result |
|---|---|
| Are all critical dimensions present? | ✗ **No.** Genset mass and dimensions absent [P22]; container internal layout absent; four conflicting container sizes (Y-05); door 900 vs 1 000 (Y-06). |
| Is the equipment layout feasible on the given plot? | ✗ **Partly.** LOT 1 fits the 150 m² plot by area but leaves ≈ 0,7 m to the south boundary and **zero access behind the arrays** (R-02). LOT 2 is **not** feasible inside a 6,16 m² container with existing equipment retained (R-09). |
| Are clearances for installation/maintenance respected? | ✗ **No.** ≈ 0,48 m walkway in the container (R-09); no rear access to the PV arrays; no maintenance zone shown. |
| Is the orientation consistent with sun path / wind? | ✔ **Sun path yes** (G-04). ✗ **Wind no** — the arrays are the most exposed elements on the plot, unshielded, with the 38 m tower immediately upwind of the array **backs** for the prevailing NE bura, i.e. the worst uplift case, and wake/interference effects are not considered (Y-19 adjacent). |

### Structural
| Check | Result |
|---|---|
| Are foundation dimensions specified? | ✔ Dimensions given — ✗ but **misdescribed** (R-06) and taken from the **wrong bracket variant** (R-03). |
| Is a static calculation referenced or provided? | ✗ Required only as a **post-award deliverable** [BOQ] 1.3; none provided (R-01, A-03). |
| Are uplift and overturning considered? | ✗ **Asserted but never calculated.** Recomputation shows uplift utilisation 1,21 and overturning γ = 0,41 (R-04). |
| Is soil bearing capacity data available? | ✗ **No. "GEOMEHANIČKI ELABORAT: nema"** [AG]. f<sub>ak</sub> ≥ 100 kPa is demanded with no means of verification and no site-inspection obligation (R-04). |
| Are safety factors in line with Eurocode? | ✗ **No.** The tendered PV foundation achieves γ = 0,41 against overturning where the certified tower foundation on the same plot achieves 2,14. |

### Manufacturing / Fabrication
| Check | Result |
|---|---|
| Are all steel profiles and thicknesses specified? | ✔ For the proprietary support (G-01). ✗ **Not at all** for the container floor grillage ([BOQ] 4.4 is a "kpl" lump with no section, no grade and no weight — R-08). |
| Are weld symbols and accessibility indicated? | ✗ N/A for the bolted support; ✗ absent for the grillage. |
| Are standard stock sizes used? | ✔ Support is a catalogue kit. ✗ Rebar at 335 MPa is not a European stock grade (Y-03). |
| Is galvanisation / corrosion protection defined? | ✔ EN ISO 1461 for the support (G-05). ✗ Stated generically for the grillage, with no standard. |

### Installation
| Check | Result |
|---|---|
| Is the assembly sequence plausible? | ✔ For the support ([HW-QG] pp. 14–20 is a complete sequence). ✗ For the genset — no method, no drawing, no verified opening (R-09). |
| Are lifting points and access for heavy equipment considered? | ✗ **No.** No crane/HIAB, no skates, no ramp, no roof-panel removal item. The set has certified base-mounted lifting eyes [P22] but nothing in the BOQ uses them. |
| Are temporary works required / priced? | ✗ **Required and not priced** — access platform to the raised container floor, propping during panel removal, trench support (or a rock-face stability statement), site establishment. |

### Maintenance
| Check | Result |
|---|---|
| Safe access for cleaning, inspection, repair? | ✗ PV: no rear access; the array's top edge is at **3,74 m**, requiring a ladder or MEWP for cleaning — no provision. Container: ≈ 0,48 m walkway. |
| Drainage and snow clearance provided? | ✗ **No.** The bottom edge at +0,50 m will be buried (R-05); no snow-clearance zone, no drainage of meltwater away from the foundations, no ice-shedding exclusion zone below a 3,7 m inclined glass surface. |
| Are fasteners accessible with standard tools? | ✔ M12/M16 with a stated 45 N·m torque [HW-QG] p. 17. ✗ Anti-theft nuts require a proprietary wrench, which is not listed as a deliverable. |

### Documentation & BOM
| Check | Result |
|---|---|
| Is a Bill of Materials provided? | ✔ For the support (G-01). ✗ For the grillage, the fence extension, rock dowels and permits — items that do not exist. |
| Are quantities, lengths and part numbers consistent with the drawings? | ✗ **No** — see §5: 2.4 overstated 6 ×, 2.7 wholly spurious, 2.1/2.2a understated, 2.3 description at odds with its own quantity. |
| Is the drawing revision and date clearly marked? | ✗ **No revision number or date on S-01, S-02 or S-03.** The Huawei foundation sheets carry no part number, version, scale or approval signature — every title-block field is blank [HW-GD] pp. 3–5. |
| Are references to standards and datasheets correct? | ✗ EN 1991-1-3/-4 are invoked [BOQ] 1.1 but never applied; the "K3 static calculation" cited three times does not exist and the site has a K2 container; the P22-6 datasheet supplied contains no load data. |

### Safety
| Check | Result |
|---|---|
| Sharp edges, pinch points, fall hazards identified? | ✗ Not addressed. Ice-shedding and snow-slide from a 3,7 m high 45° glass surface onto the adjacent walking area is an unassessed hazard. |
| Is earthing and bonding clearly shown? | ✔ Scope is present ([BOQ] 1.4, 5.3, 5.4) — ✗ wrong conductor type for buried use (Y-18); EN 62305 separation not verified (Y-19). |
| Are fire safety distances (generator, fuel) respected? | ✗ **No.** 500 l of diesel and an operating engine in an unseparated 6 m² B1-rated compartment with live telecom equipment; no fire compartmentation; no permit route for a fuel installation (R-10). |

---

## 8. ACTION ITEMS

> Numbered, specific and assignable. **A-01 to A-11 must be closed before the tender is issued.**

### Critical — block tender issue

1. **A-01 — Establish and publish the site design wind action.** *[Investor / structural designer]* Issue in the tender: v<sub>b,0</sub> and terrain category per the BAS EN 1991-1-4 BiH National Annex for the Bileća region; the orography factor c₀ for a 1 076 m summit per Annex A.3; and the resulting peak velocity pressure q<sub>p</sub>(z) at z = 3,74 m. Reconcile against the Investor's own values of **1,10 kN/m²** [PZ §2.12] and **1,20 kN/m²** [AG §4.4.2.4]. **Expected result: q<sub>p</sub> ≈ 1,20 kN/m², v<sub>p</sub> ≈ 43 m/s.**

2. **A-02 — Delete "inklinacija: fiksno 45°" from [BOQ] LOT 1 item 1.1, and do not replace it with 25°.** *[Investor]* Neither tilt is compliant (R-01). Fix the *structure* first; choose the tilt afterwards. For this site the correct combination is a **steep tilt (40–45°)** — best for snow shedding and for winter yield at 42,94° N — on a **structure designed for the real wind**, not a catalogue kit selected by a latitude table.

3. **A-03 — Make the certified static calculation a PRE-AWARD qualification requirement, not a post-award deliverable.** *[Investor / procurement]* Move [BOQ] 1.3 into [TD] §6.1 (Dokumentacija vezana za predmet nabavke). The bidder must submit, with the offer, a calculation signed by a licensed engineer demonstrating resistance to **q<sub>p</sub> ≥ 1,20 kN/m² wind**, **s<sub>k</sub> = 3,00 kN/m² ground snow at the offered tilt**, and **20 mm radial rime ice at 300 kg/m³**, to BAS EN 1991-1-3/-4 and EN 1993-1-1. Without this, the lowest-price criterion ([TD] §9.1) will award a provably non-compliant product.

4. **A-04 — Specify a minimum bottom-module-edge height of 1,20 m (preferably 1,50 m) above finished ground.** *[Investor / structural designer]* Justify against drifted snow at s<sub>k</sub> = 3,00 kN/m² per EN 1991-1-3 §6.2. Delete the "+0,50 m" and the "niska ugradbena visina uz propuštanje snijega" note on [S-03]. State the datum unambiguously as **finished ground level at the support**, not the top of the tower foundation block (which stands 0,30 m proud).

5. **A-05 — Correct the panel-field geometry throughout the tender.** *[Designer]* Replace 2 590 mm with the true horizontal projection at the adopted tilt (≈ **3 236 mm at 45°**), replace "+3,09 m" with the true top-edge height (**+3,74 m at 45°**), and distinguish the **array width (≈ 3 442 mm)** from the **horizontal beam length (4 089 mm)**. Re-draw [S-02] and [S-03] accordingly, re-check the fence overhang and the boundary setback, and confirm the module dimensions of the iPV585-M2A with Huawei. **Coordinate with the parallel Huawei/PV review.**

6. **A-06 — Obtain the Huawei foundation drawing for the LOW support, or delete all foundation dimensions from [BOQ] 2.3.** *[Investor / supplier]* The drawing supplied is titled *"Sharp A Bracket 3.0 Foundation (**High** solar bracket)"*. Confirm in particular the **1 800 mm anchor-group spacing** for the LOW variant — a wrong cast-in anchor position is unrecoverable.

7. **A-07 — Calculate uplift and overturning, and add hold-down.** *[Structural designer]* At the adopted tilt and q<sub>p</sub> from A-01, verify to EN 1990 Table A1.2(A) (γ<sub>Q,dst</sub> = 1,5 / γ<sub>G,stb</sub> = 0,9) and EN 1997-1 (UPL). Current values at 45°: uplift utilisation **1,21**, overturning γ = **0,41**, windward-strip design uplift **32,0 kN**. Add a new BOQ item: **8 no. Ø25 resin-anchored rock dowels, ≥ 1,0 m embedment into sound rock, one pair per strip, with pull-out testing of 10 % to 1,5 × design load.**

8. **A-08 — Provide a geotechnical statement for the PV foundation zone.** *[Investor]* The certified project records **"GEOMEHANIČKI ELABORAT: nema"** and designed the tower on an assumed σ<sub>doz</sub> = 150 kPa **subject to inspection of the open excavation by a geotechnician** [AG]. Carry that obligation into this tender as a hold point, and either commission trial pits / a geotechnical report, or add a provisional item for foundation adaptation on the geotechnician's instruction. Confirm f<sub>ak</sub> ≥ 100 kPa [HW-GD p. 3] and the rock quality required for the A-07 dowels.

9. **A-09 — Delete [BOQ] LOT 1 item 2.7 (5,40 × 5,40 m slab).** *[Investor]* The element already exists as the tower's 5,40 × 5,40 × **1,80 m** RC foundation block [AG]. Replace with (a) a **fence extension** item to enclose the new PV area — promised by [TD] §3.1.3 and absent from the BOQ — and (b) a **reinstatement/regrading** item.

10. **A-10 — Withdraw the "10,00 kN/m²" container floor capacity and rewrite [BOQ] LOT 2 item 4.4.** *[Investor / structural designer]* The figure is unsourced and cites a **K3** calculation for a **K2** container. The governing value is **2,00 kN/m² UDL + the specific equipment schedule** [PZ §2.12, AG §POD]. Reverse the statement *"ojačanje se NE očekuje kao neophodno"* — the recomputed utilisation is **≈ 2,5** and local AVM pressures reach **111 kN/m²**. Make the strengthening the **base case**, specified as: an independent galvanised steel frame carrying the skid and tank **through** the container floor onto new pads bearing on the existing tower foundation block; measured in **kg** (estimate 180–250 kg) as a separate item from the calculation. Also require a check of the container's own floor frame and anchorage for the +155 % mass increase.

11. **A-11 — Resolve the genset access and internal layout before tender, and relocate the LOT 2 penetrations.** *[Investor / designer]*
 - Issue a **dimensioned as-built internal survey** of the container showing all existing equipment.
 - Require a **certified P22-6 skid GA drawing with mass and dimensions** as a pre-award submission (the supplied [P22] has neither).
 - Verify the container door on site (900 × 2 000 vs the certified 1 000 × 2 020).
 - Price the realistic access method — **roof-panel removal and reinstatement** — as a measured item, with wall opening and split delivery as priced alternatives.
 - Demonstrate a maintenance walkway of **≥ 0,80 m** with the genset, tank, bund and existing equipment all in place, or relocate the genset outside the container.
 - **Move the fresh-air intake, hot-air discharge and exhaust off the north wall**, which carries the existing ICC330-H1 and MTS9302 outdoor cabinets ([S-01], [S-02]), or demonstrate by calculation that the discharge does not raise the cabinet intake temperature.

### High priority — before contract award

12. **A-12 — Rewrite [BOQ] LOT 1 item 2.3** to describe the real element: *strip footing 3 300 × 450 (550 mm at base) × 200 mm thick with two 280 × 280 × 700 mm pedestals at 1 800 mm centres, overall depth 900 mm*, and state the pedestal formwork (8 boxes). The quantity 1,63 m³ is correct; the description generates a claim of the order of 3,8 m³.

13. **A-13 — Correct [BOQ] LOT 1 item 2.4 from 12 m² to 2,0 m²** and rewrite it to cover the pedestal tops and exposed faces only. The 12 m² derives from 4 × 3,30 × 0,90 — the side elevation of a strip wrongly taken as 900 mm deep.

14. **A-14 — Correct the earthworks items:** 2.1 to ≈ 8,93 m³ with a separate measured item for **rock breaking (hydraulic hammer / blasting) in category IV–V**; 2.2 changed to **imported granular backfill** (broken rock cannot be placed as compacted layered fill); 2.2a restated on a **loose** measurement basis with the bulking factor declared (2,94 m³ if the spoil is reusable, up to 13,4 m³ if not).

15. **A-15 — Upgrade the concrete specification** to BAS EN 206: **C30/37, exposure XC4 + XF3, air-entrained**, cover 50 mm, with a frost-resistance test — consistent with the certified project's *"marka na mraz M-100"* [AG §2.1.2]. Change blinding to C12/15. Change reinforcement from *335 MPa* to **B500B** with an area not less than the manufacturer's schedule; make it a measured item at 78,1 kg.

16. **A-16 — Obtain Huawei's written confirmation** that the **iPV585-M2A** module is mechanically compatible with the Standard A-Shaped Support 3.0 (the Quick Guide qualifies **540 W / iPV540-M1A** at 2 256–2 285 × 1 133–1 134 × **35 mm** only) **and** that the 31/35/40 m/s ratings apply to the 585 W configuration. If not, change the module or the support.

17. **A-17 — Amend the Lokacijski uslovi and obtain the required consents.** *[Investor]* The existing conditions [LU] authorise a base station only, of *"privremeni"* character. Two PV arrays on permanent concrete foundations, a diesel generator and a 500 l fuel installation require amended location conditions, a building permit, and fire-protection and environmental approvals. Add a permitting item and allowance to the BOQ, or state explicitly that the Investor carries this risk and programme.

18. **A-18 — Add a fire strategy for the fuel store.** Provide an EI 60 (minimum) separation between the genset/fuel zone and the telecom equipment, or relocate the genset and tank into a separate enclosure — as the [MATISA] precedent did. Specify a certified non-combustible collar for the exhaust penetration through the B1 PU sandwich panel. Add impermeable hardstanding and a spill kit at the tanker fill point.

### Medium priority — tender housekeeping

19. **A-19 — Fix the BOQ integrity defects:** renumber LOT 2 (the section is numbered both "1" and "3"; item 4.1 cross-refers to a non-existent "Tačka 3.1"); delete or populate the blank items 2.6 and 2.8; define or delete the undefined lump sum 2.5; reconcile the 200 l vs 500 l first fill; correct the "LOT 1" headings on [TD] §1.4/§1.7 and the garbled sentence in §1.7.

20. **A-20 — Reconcile the container dimensions to one value** measured on site (four different values are currently in circulation: 3,00 × 2,10 × 2,40 / 3,08 × 2,20 / 3,08 × 2,80 / 3,00 × 2,44 × 2,89) and correct [S-03]. Reconcile the fence height (1,80 vs 1,90 m) and the two "nadvišenje" values (0,17 vs 0,20 m).

21. **A-21 — Add revision numbers, dates and a signature block to S-01, S-02 and S-03**, and record the source and issue date of the Huawei foundation sheets (every title-block field is blank).

22. **A-22 — Add the missing enabling and closing items:** site establishment; setting-out and geodetic survey (referenced by the [BOQ] note but not priced); access-track condition survey and any improvement needed for a road tanker; temporary works; concrete cube testing; HSE including RF-exposure control while working at the base of a live 38 m base station; and site reinstatement.

23. **A-23 — Add intake and discharge acoustic attenuators** as measured items, or delete the *"< 68 dBA at 7 m"* requirement — it is unachievable with an open skid set behind two unattenuated louvres in a 70 mm sandwich-panel enclosure.

24. **A-24 — Correct the earthing and lightning-protection details:** change H07V-K to bare Cu 25 mm² or Fe/Zn 25 × 4 for buried runs; require an EN 62305-3 separation-distance verification between the tower LPS and the PV DC installation; add a **Type 1** DC surge arrester where required.

---

## 9. LESSONS LEARNED

1. **The Investor's own archive answered the decisive question.** The wind verdict did not need a new study: BH Telecom's type-container brief (**1,10 kN/m² on exposed structures ≤ 10 m, all BiH ≤ 1 500 m**) and the certified BS Sjednica project (**1,20 kN/m²; 185 km/h**) both sit in the project folder, and a first-principles EN 1991-1-4 check with orography reproduces the second to within 0,5 %. **Always mine the certified site project before commissioning new analysis.**

2. **A manufacturer's tilt table is an energy rule, not a structural rule.** The Huawei latitude table (31–45° → 45°) optimises yield. The *same document*, two pages earlier, states that 45° halves the wind rating. Reading the two together is the whole of this review's headline finding.

3. **Never derive an array footprint from a frame member.** The 2 590 mm error came from taking the 3 656 mm longitudinal beam as the module field length. Derive the field from the modules — and cross-check against the clamp and beam counts in the installation guide, which uniquely determine the layout.

4. **Check the title block, not just the dimensions.** The foundation figures were transcribed perfectly from a drawing titled *"(High solar bracket)"* into a specification for the **LOW** support.

5. **A quantity that agrees with a source is not a quantity that agrees with its own description.** Item 2.3's 1,63 m³ is exactly right and its written geometry is 3,3 × wrong — because the manufacturer's element is a slab with pedestals, not a deep strip. Reconstruct the volume before accepting the description.

6. **Trace every asserted capacity to a document.** "10,00 kN/m²" was repeated three times across the BOQ and the drawings and appears in **no** source; the governing brief says 2,00 kN/m², and the nearest genuine precedent — a container **purpose-built** for gensets — was designed for 8,00 kN/m² with a 6 mm chequer deck on a 400 mm raft.

7. **"The contractor shall confirm feasibility" is not a specification.** Where the tender could not resolve access, spatial fit or floor capacity, it transferred the unknown to the bidder. Under a lowest-price award this reliably produces either a non-compliant offer or a post-award claim.

8. **Wind and snow must be optimised together.** Here the tilt was chosen for energy, the support height for wind, and the snow load was never checked — producing the one combination that is wrong for both: the worst tilt for wind and the worst mounting height for snow.

---

*End of review — 02-construction.md, Rev. 0, 2026-08-07.*
*Delta review to be produced on re-issue of the tender documents (per `prompt.md` §6).*
