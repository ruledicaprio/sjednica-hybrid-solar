# 03 — ELECTRICAL & MECHANICAL SERVICES REVIEW
## Autonomni hibridni sistem napajanja — BS SJEDNICA (Bileća)
### LOT 2 (DEA in existing container) + electrical scope of LOT 1

| | |
|---|---|
| **Review ref.** | 03-electrical |
| **Revision / date** | Rev. 0 — 2026-08-07 |
| **Reviewer discipline** | Chartered electrical engineer (electrical + mechanical services) |
| **Documents under review** | `TD-OUTPUT\3. TD JN Hibridni sistem napajanja BS Sjednica.docx`; `TD-OUTPUT\3.1 PRILOG II TD - predmjer Sjednica Bileca.xlsx` (LOT 1 & LOT 2); `TD-OUTPUT\Prilog_III_situacija_sjednica_bileca.pdf` (34 pp.) |
| **Reference documents used** | `EQUIPEMENT\GENSET\P22-6.pdf` (3 pp.); `docs\genset_inside_container\*` (MATISA 2×13 kVA, BH Telecom 2008/017BH); certified site project `SITE-PROJECT-SJEDNICA…\3_ELEKTRO INSTALACIJE\03 ELEKTRO dio.doc` + DXF 3.5.1 / 3.5.3 / 3.5.8 / 3.5.9; `docs\site_container\CONTAINER_Tablica_ozicenja_AC/DC_instalacija.xlsx`; Huawei `PV Module Solution User Manual` Iss. 07; `iSSU S4875G2 Datasheet` 2026-01-15 |
| **Review basis** | prompt.md §2 (structure), §5 (style) |

---

## 1. EXECUTIVE SUMMARY

**RISK LEVEL: HIGH — do not issue to tender.**

**Key conclusion.** The ventilation, exhaust and fire-safety concept for the 22 kVA genset has been copied verbatim from the 2008 MATISA reference (a **dedicated, TK-free** genset container housing 2 × 13.3 kVA sets) into a **live, 6.29 m² telecom container** without a single recalculation. The extract fan (1 200 m³/h), the intake louvre (500 × 700 mm) and the exhaust (DN 50) are all undersized by factors of **3.5×, 2.7× and 1.5–2×** respectively against the Perkins 404D-22G's actual radiator, intake and exhaust duty. As specified the set will not hold coolant temperature and will trip on its own **High Coolant Temperature Shutdown** (P22-6.pdf p.2, *Standard Equipment / Engine*), and the container interior will reach **≈ 55 °C** while it runs. Independently of ventilation, the package contains a **safety-critical protection failure** (a 22 kVA alternator cannot trip the specified C32 MCBs on an earth fault; the certified design's 40 A/30 mA RCD has been deleted), an **unassessed Class B fire risk** (500 l of diesel added to a container whose approved fire elaborate covers Class E only), and a **spatial impossibility** (the future-state drawing S-02 shows the container empty; in reality both walls are fully occupied by GRO, UPS, UPS-R, RBS_1, RBS_2, PRENOS, ROS, TZ, MPU and the A/C).

**14 RED findings, 21 YELLOW, 9 GREEN.** RED-01 through RED-05 are individually sufficient to prevent construction.

---

## 2. INFORMATION EXTRACTION TABLE (ground truth)

### 2.1 Site & load

| Parameter | Value | Source |
|---|---|---|
| Location / altitude | Sjednica, Bileća, RS; 42.9448° N 18.3236° E; **1 076 m a.s.l.** | Prilog III p.2 |
| Site air pressure / density (calc.) | 89 049 Pa; ρ = 1.041 kg/m³ @ 25 °C, 1.007 @ 35 °C | ISA, calculated |
| Utility connection | **NONE** — "Objekat nema priključak na elektroenergetsku mrežu" | TD p.1; Prilog III p.2 |
| …but certified project states | "Priključenje… planira se sa NN mreže podzemnim kablom… elektroenergetska saglasnost br. 02.03.0222-09-04/18"; PMO with 3-ph two-tariff meter 5–40 A + limiter, 35 A fuses | `03 ELEKTRO dio.doc` §3.2.1 |
| TK load | **1 180 W nominal / 1 330 W max**, −48 VDC; 3 × Huawei RRU + BBU/MPLS | Prilog III p.2 |
| Tower | Lattice, **h = 38 m**, base 4.20 × 4.20 m, air termination (*gromobranska hvataljka*) at top | Prilog III p.2; DXF 3.5.9 |
| Fenced pad | 5.40 × 5.40 m RC slab; fence h = 1.90 m; plot ≈ 150 m² (16.00 × 9.40 m) | Prilog III p.3 |
| Existing earth electrode | Ring Fe/Zn 25×4 mm @ 0.80 m depth + ring in slab foundation + tape in feeder duct @ 0.60 m; R calculated **5.91 Ω** (ρ = 250 Ωm, l = 95 m) | DXF 3.5.9; `03 ELEKTRO dio.doc` §3.3.8 |
| Huawei power plant | **Outdoor cabinets ICC330-H1 + MTS9302, on the NORTH wall** | Prilog III p.3, p.4 |

### 2.2 Container — three conflicting descriptions in one package

| Source | Dimensions | Mass |
|---|---|---|
| TD prose, "Postojeće stanje" | 3.00 × 2.10 × 2.40 m, IP55 | ~850 kg |
| Prilog III p.2 | 3.08 × 2.20 × 2.80 m, IP55 | ~1 000 kg |
| Prilog III p.5 (Presjek A–A) | "KONTEJNER 3,08 × 2,80 m" | — |
| **Certified drawing (as-built)** | **internal P = 6.29 m², O = 10.13 m → 2.88 × 2.18 m clear**; floor antistatic | — |
| Envelope | Roof thermo-panel d = 80 mm, façade thermo-panel d = 60 mm, galvanised sheet 0.8 mm, 20 mm plywood, Tervol 100 mm | DXF `02 Presjek 1_1` |
| Fire rating | "vatrootpornost 2 sata" | `03 ELEKTRO dio.doc` §3.7.2 |
| Internal volume (2.88 × 2.18 × 2.40) | **≈ 15.1 m³** | calculated |

### 2.3 Existing equipment inside the container (all of it omitted from drawing S-02)

GRO · UPS · UPS-R · U1 · PE1 — west/north wall  ‖  ROS · TZ · PRENOS · RBS_2 · RBS_1 · MPU · PE2 · ROXTEK · U2 · U3 — east/north wall  ‖  ceiling: S1, S2 (AJP fire detector), S3.
Also: **air-conditioning unit** (AC klime + DC control), anti-panic lighting, motion sensor, door contact, card reader, 2 internal cameras, security rack.
*Sources: Prilog III p.21 (E-08, dwg 5.5.8, GP-TO-13617); DXF 3.5.3; `CONTAINER_Tablica_ozicenja_AC/DC_instalacija.csv`.*

### 2.4 Existing electrical installation

| Item | Value | Source |
|---|---|---|
| PMO | 3×35 A/400 V, TN-C/S, meter 10–40 A, **Type 2 SPD 3P+N, 275 V, 8/20 µs, Ipn = 20 kA, Un < 1.3 kV**; note: *"Spoj nultog i zaštitnog provodnika (N i PE) izvršiti samo u ovom ormaru"* | DXF 3.5.1 |
| Existing GRO incomer | **3-pole FID SKLOPKA 40 / 0,03 A** (RCD) | Prilog III p.16 (E-03, dwg 5.5.3) |
| Existing GRO ways | UPS, UPS-R (spare), AC klima, 2× utičnice, tehnička zaštita, rasvjeta+vanjska+antipanik, DC to klima, photorelay probe, tower-light fault, 4× reserve | Prilog III p.16; AC wiring schedule |
| Equipotential bonding | K1 GRO 1×16, K2 antistatic floor 1×16, K3 klima 1×16, K4 prenos 1×16, K5 TZ 1×16, K6/K7 RBS 1×35, K8 UPS +pole 1×50, **K9/K12 earthing PE1/PE2 to Fe/Zn tape 1×50 mm²**, K10 feeder down-lead 1×35, K11 feeder braid 1×16 (all P/F) | Prilog III p.20 (E-07); DXF 3.5.8 |
| ROS alarms | KVAR S.L., **NEST.1.F (mains phase loss)**, klima t> / t< / kvar, UPS 24 V, ISP AC, ISP DC, AJP, OT.V., DF, SP, RU, UK1, VK1, VK2 | DC wiring schedule |
| Fire protection (approved) | Fire class assessed = **E only** (electrical). Automatic suppression = **BONPET ampoules**. | `03 ELEKTRO dio.doc` §3.7.2/3.7.3 |

### 2.5 Genset — P22-6 datasheet content vs. what is needed

| Data required for this design | In the supplied datasheet? |
|---|---|
| Cooling (radiator) air flow | **ABSENT** |
| Combustion air flow | **ABSENT** |
| Radiator heat rejection | **ABSENT** |
| Max. allowable **external static restriction** on cooling air | **ABSENT** |
| Exhaust gas flow / temperature | **ABSENT** |
| **Max. allowable exhaust back pressure** | **ABSENT** |
| Exhaust connection size | **ABSENT** (only "Exhaust flange outlet", "Exhaust stub pipe and gasket") |
| Dry / wet weight | **ABSENT** |
| Fuel consumption | **ABSENT** |
| Noise data (Lp / LWA) | **ABSENT** |

**What the 3-page datasheet does give:** 50 Hz Prime 20 kVA/16 kW, 50 Hz Standby **22 kVA/17.6 kW**; Perkins 404D-22G; bore 84 mm, stroke 100 mm, **displacement 2.2 l**, CR 13.3:1, mechanical governor; package-mounted radiator + cooling fan; **High Coolant Temperature Shutdown**; **SHUNT excitation**, IP23; FG100 control panel; skid base or single-wall tank; ratings at **25 °C, 100 m a.s.l., 30 % RH** (P22-6.pdf pp.1–3).

### 2.6 Derived engine duty (calculated — must be confirmed against the manufacturer's Technical Data Sheet)

| Quantity | Value | Basis |
|---|---|---|
| Shaft power at standby rating | 20.0 kW | 17.6 kW ÷ η_alt 0.88 |
| Fuel rate at full load | 5.0 kg/h = **5.95 l/h** | BSFC 250 g/kWh |
| Fuel energy input | **59.3 kW** (η_el 29.7 %) | LHV 42.7 MJ/kg |
| **Heat to radiator** | **≈ 15 kW** | 25 % of fuel input |
| Heat to exhaust | ≈ 17.8 kW | 30 % |
| **Heat radiated into the room** (engine surfaces + alternator losses) | **≈ 7 kW** (range 6–9) | balance |
| **Combustion air** | **85 m³/h** (0.024 m³/s), AFR ≈ 17.6 | 2.216 l × 750 min⁻¹ × ηv 0.85 |
| **Exhaust mass / volume flow** | 93 kg/h; **238 m³/h (0.066 m³/s) at 520 °C** | ρ_exh = 0.391 kg/m³ at site pressure |

---

## 3. FINDINGS BY SEVERITY

### 3.1 RED — CRITICAL

---

#### RED-01 — Cooling-air ventilation is undersized by a factor of ≈ 3.5. The set will overheat and shut down.

**What the tender requires.** BOQ LOT 2 item 4.9: axial fan **1 200 m³/h, Ø315 mm**, thermostat-controlled, interlocked with the genset; explicit statement *"Minimalna potrebna ventilacija prostora iznosi 120 m³/h (6 izmjena zraka na sat)"*. Item 4.8: fresh-air louvre **500 × 700 mm**. Items 4.5/4.6/4.7: flexible connection to the radiator, sheet-metal duct "P ≈ 6 m²", fixed discharge louvre **600 × 600 mm**. Prilog III p.4 places all of this on the **north wall**.

**Where the "120 m³/h / 6 ACH" figure comes from.** It is copied verbatim from the MATISA report: *"minimalna potreba za ventilacijom iznosi 120 m³/h, odnosno 6 izmjena po satu. Broj izmjena je dobijen tabelarno iz knjige Ventilacija i klimatizacija (A. Fetisov i V. Karas)"* (`3_DIS_MAS_EL_DIO…`, Stranica 9, list 80). **This is a general room-occupancy air-change figure. It has no relationship whatsoever to the cooling duty of a radiator-cooled diesel engine.** Applying it here is a category error, and the tender repeats it as a design requirement.

**Required cooling air (calculated).**

V̇ = Q_rad / (ρ · c_p · ΔT), with Q_rad = 15 kW, ρ = 1.041 kg/m³ (1 076 m, 25 °C), c_p = 1.005 kJ/kg·K:

| ΔT across radiator | Required air flow |
|---|---|
| 10 K | 1.42 m³/s = **5 100 m³/h** |
| **12 K (design)** | 1.18 m³/s = **4 250 m³/h** |
| 15 K | 0.95 m³/s = **3 400 m³/h** |

**Verdict on the numbers:**
- vs. the 1 200 m³/h fan → **3.5× short**
- vs. the tender's stated "minimum 120 m³/h" → **35× short**
- Combustion air (85 m³/h) is a further, separate demand — and is itself ~70 % of the tender's stated "minimum ventilation".

**Required free intake area.** Genset installation practice (FG Wilson / Perkins / Cummins Application & Installation Guides) requires **free** inlet area ≥ 1.5 × radiator core face area, with free-area velocity ≤ 5 m/s and preferably ≤ 3 m/s.

| | Value |
|---|---|
| Total intake demand (radiator + combustion) | **1.205 m³/s** |
| Provided: 500 × 700 gross | 0.350 m²; **free area ≈ 0.158 m²** (45 % for weather blades + mesh) |
| Resulting free-area velocity | **7.7 m/s** — exceeds the 5 m/s absolute limit |
| Resulting louvre pressure drop (ζ ≈ 3) | **≈ 91 Pa** |
| Required free area @ 3 m/s | **0.402 m²** → gross ≈ **0.89 m²** |
| Required free area @ 5 m/s (absolute max) | 0.241 m² → gross ≈ 0.54 m² |
| **Deficit** | **2.7× on the recommended criterion** |

**With the 1 200 m³/h extract fan also drawing through the same opening** (which is what the tender specifies — there is only one intake): total 1.538 m³/s → **9.8 m/s free-area velocity, ≈ 149 Pa** on the intake alone.

**Required discharge area.** Radiator core face area for a set of this class ≈ 0.25 m²; discharge free area must be ≥ core area, preferably 1.25×.

| | Value |
|---|---|
| Provided: 600 × 600 gross | 0.36 m²; free ≈ **0.162 m²** |
| Free-area velocity at 1.18 m³/s | **7.3 m/s**, Δp ≈ **83 Pa** |
| Required free area | ≥ 0.31 m² → gross ≈ **0.72 m²** |
| **Deficit** | **≈ 2×** |

**The fatal item: external static pressure.** A standard genset radiator uses an engine-driven pusher fan with a very small external static allowance — typically of the order of **12.5 mm H₂O ≈ 123 Pa** for a set of this size, and **zero** on some open-set-only configurations. **This figure is absent from the supplied datasheet and must be obtained from FG Wilson.** The as-designed path is:

> intake louvre 91 Pa + duct & bends (cross-section undefined — see RED-02) ≥ 50 Pa + discharge louvre 83 Pa + flexible + mesh ≈ **230–300 Pa**

i.e. roughly **2–2.5× a typical fan allowance**, before any acoustic attenuator is added. The fan operating point collapses, radiator air flow falls, coolant top-tank temperature rises, and the engine trips on its own **High Coolant Temperature Shutdown** (P22-6.pdf p.2). On an off-grid site where the genset is the *only* AC source, that is a total-site-outage failure mode.

**Correct sizing (to be adopted):**

| Element | Specify |
|---|---|
| Fresh-air intake louvre | **≥ 1 200 × 800 mm** gross (0.96 m² → 0.43 m² free), weather blades + bird mesh, **motorised damper** |
| Radiator discharge louvre | **≥ 900 × 800 mm** gross (0.72 m² → 0.32 m² free), **motorised/gravity damper** |
| Radiator discharge duct | Free cross-section **≥ 0.25 m²** (e.g. 500 × 500 mm), velocity ≤ 5 m/s; *state the cross-section, not the sheet area* |
| Room extract fan (radiated heat only) | **≥ 2 400 m³/h** to hold ΔT = 10 K; **≥ 4 800 m³/h** to hold ΔT = 5 K |
| Verification | Bidder to submit the genset maker's Technical Data Sheet (cooling air flow, radiator heat rejection, **max. external static restriction**) and a system pressure-drop calculation demonstrating total resistance ≤ the stated allowance |

*Refs: BOQ LOT 2 items 4.5–4.9; Prilog III p.4; P22-6.pdf p.2; MATISA `3_DIS_MAS_EL_DIO…` p.80.*

---

#### RED-02 — Container interior reaches ≈ 55 °C, over the limits of the TK equipment sharing the space.

Because the radiator is ducted out (BOQ 4.5/4.6/4.7 — correct in principle), the extract fan's only remaining job is to remove the **≈ 7 kW radiated** from the engine block, manifold, alternator and control panel.

ΔT = Q / (ρ · c_p · V̇):

| Extract flow | ΔT above outside air | Interior at 35 °C ambient |
|---|---|---|
| **1 200 m³/h (as specified)** | **20.1 K** | **55.1 °C** |
| 2 400 m³/h | 10.0 K | 45.0 °C |
| 4 800 m³/h | 5.0 K | 40.0 °C |

Against this:
- **TK equipment** (RBS_1, RBS_2, PRENOS, ROS, TZ, MPU) is specified to **ETSI EN 300 019-1-3 class 3.1/3.2, i.e. +40 °C / +45 °C**. 55 °C is outside class.
- **Huawei PVDU / PV distribution equipment**: "–20 °C to +65 °C (**starts to derate at 55 °C**, derated to 80 % at 65 °C)" (*PV Module Solution User Manual* Iss. 07, p.89).
- **iSSU S4875G2**: –25 °C to +75 °C (iSSU datasheet p.2) — but see RED-03, it is outdoors in the discharge plume.
- **The existing air-conditioner** (AC klime — AC wiring schedule; klima on E-08) has a capacity of the order of 2–3.5 kW. It cannot offset a 7 kW internal gain, and it is defeated anyway by **0.79 m² of permanently open aperture** cut into the envelope (0.35 + 0.36 + Ø315). **No motorised or gravity dampers are specified anywhere in the BOQ**, so the container loses its IP55 rating, its thermal envelope and its EMC shield permanently, not just while the genset runs.

**LFP batteries.** Per Prilog III p.3/p.4 the batteries are in the outdoor ICC330-H1 / MTS9302 cabinets — see RED-03. Wherever they sit, Li-ion cycle life follows Arrhenius: **service life approximately halves for each +10 K above 25 °C**, and BMS charge current is limited above ~45–50 °C. Exposing them to a genset heat plume every charge cycle directly undermines the economics of the hybrid system.

*Refs: BOQ LOT 2 items 4.8, 4.9; Prilog III p.21 (E-08); `CONTAINER_Tablica_ozicenja_AC_instalacija`; Huawei PV manual p.89.*

---

#### RED-03 — All genset openings are placed on the north wall, which is already occupied by the Huawei outdoor power cabinets.

Prilog III p.3 and p.4 both state: *"postojeći vanjski ormari na SJEVERNOJ strani: Huawei ICC330-H1 (outdoor) + MTS9302"*. Prilog III p.4 then places, in red, on that same north wall: *"žaluzina ulaza zraka 500×700 mm · izlaz zraka + ventilator 1200 m³/h · izduv NO 50 sa hvatačem iskri"*. Prilog III p.5 confirms the set is *"ORIJENTISAN PREMA SJEVERU (hladnjak i izduv prema sjevernoj strani kontejnera)"*.

Consequences, all on one wall:

1. **≈ 4 250 m³/h of radiator air at ambient + 12 K is discharged directly at the cabinets containing the rectifiers, the iSSU solar modules and the LFP batteries.** Those cabinets are naturally/fan cooled and draw their own intake air from exactly that zone.
2. **A 520 °C exhaust plume** terminating *"oboreno prema zemlji u obliku lule"* (BOQ 4.11) discharges at ground level on the same wall.
3. **Exhaust re-ingestion**: the combustion/cooling air intake and the exhaust outlet are on the same face. Good practice requires the exhaust terminal to be **≥ 3 m from any air intake and downwind**. Neither is achievable on a 3.08 m wall that also carries a 1 200 × 800 intake, a 900 × 800 discharge and two equipment cabinets.
4. **The fuel tank breather** (BOQ 4.2, *"odušna cijev izvedena IZVAN kontejnera"*) has no specified location and, on this layout, will end up beside a 520 °C exhaust terminal. See RED-08.
5. **Physical clash**: the cabinets stand against the wall. There is no dimension on any drawing establishing that a 0.96 m² louvre, a 0.72 m² discharge and an exhaust riser can be accommodated at all.

The exhaust and hot-air discharge must be moved to the **west or south** face, or ducted up above roof level, and the layout must be dimensioned.

*Refs: Prilog III p.3, p.4, p.5; BOQ LOT 2 items 4.8, 4.9, 4.11.*

---

#### RED-04 — Exhaust DN 50 is a scaling error copied from a 13.3 kVA set. Back pressure cannot be verified.

BOQ LOT 2 item 4.11 specifies *"čelična cijev NO 50 mm sa ispušnim loncem… završena oboreno prema zemlji u obliku lule… HVATAČ ISKRI"*. This is word-for-word the MATISA specification: *"Izduvni gasovi se odvode vani kroz čeličnu cijev NO 50 mm, koja se završava oboreno prema zemlji u obliku lule. Na kraju izduvnih cijevi postaviti hvatače iskri"* (`3_DIS_MAS_EL_DIO…`, Stranica 9, list 80).

**But MATISA's DN 50 served a Perkins 403C-15G — 1.5 l, 13.3 kVA — one pipe per set.** Sjednica has a 2.216 l, 22 kVA engine:

- Volume flow ratio = 2.216 / 1.496 = **1.48×**
- Pressure drop at constant diameter scales with v² = **2.19×**

**Calculated exhaust duty:** 93 kg/h, **238 m³/h (0.066 m³/s) at 520 °C**, ρ = 0.391 kg/m³.

| Pipe | Velocity | Δp, pipe + 3 bends + gooseneck + flex + exit | + industrial silencer + arrestor | + residential silencer + arrestor |
|---|---|---|---|---|
| **DN 50 (ID 52.5)** | **30.5 m/s** | 1 422 Pa | **3.12 kPa** | **4.72 kPa** |
| DN 65 (ID 68.8) | 17.8 m/s | 440 Pa | 2.14 kPa | 3.74 kPa |
| **DN 80 (ID 80.9)** | 12.9 m/s | 220 Pa | **1.92 kPa** | 3.52 kPa |

30.5 m/s is at the top of the accepted 25–35 m/s band before back pressure and regenerated noise become dominant, and the calculation above assumes only a 5 m run with three bends — the real run must clear the container, the outdoor cabinets and reach a safe terminal (RED-03), i.e. 8–10 m.

**The decisive point: the maximum allowable exhaust back pressure is not in the supplied datasheet** (P22-6.pdf carries no technical data at all — see §2.5). Excess back pressure on a naturally aspirated diesel causes power loss, high exhaust temperature, smoke, valve and turbo-free-end damage, and voids the engine warranty. **The design cannot be verified as submitted.**

**Specify:** **DN 65 minimum, DN 80 preferred** for the run (the engine flange may remain DN 50 with an expansion immediately after the flexible bellows — this is standard practice). Require the bidder to submit the engine maker's back-pressure limit and a calculation of the complete installed system including the silencer and spark arrestor.

**Retained and correct:** flexible bellows (item 4.11), 600 °C paint (4.12), 50 mm rockwool + Al cladding (4.13). Add: independent support of the exhaust off the engine, a certified fire-rated/thermally isolated wall penetration, and ≥ 225 mm clearance (or an insulated sleeve) to any combustible or cable.

*Refs: BOQ LOT 2 items 4.11–4.13; MATISA `3_DIS_MAS_EL_DIO…` list 80; P22-6.pdf pp.1–3.*

---

#### RED-05 — 500 l of diesel added to a container whose approved fire assessment covers electrical fire only.

The certified fire annex for this container states the assessed fire class explicitly:

> *"Prema standardu JUS Z.CO.003 klasa požara koji se može pojaviti unutar posmatranog objekta je: **E** (požari na uređajima i instalacijama pod električnim naponom)."* — `03 ELEKTRO dio.doc` §3.7.2

and the installed automatic suppression is:

> *"opremljen je **bonpet ampulama** za automatsko gašenje požara"* — `03 ELEKTRO dio.doc` §3.7.2

Adding a 500 l diesel inventory plus a running diesel engine introduces a **Class B (flammable liquid) pool-fire risk** and an ignition source, in a room with live TK equipment. BONPET self-activating ampoules are not a Class B pool-fire suppression solution and are certainly not designed against a 550 l spill. **The approved fire elaborate no longer covers the installation and must be re-done.**

**Regulatory position.** Diesel to BAS EN 590 has a flash point ≥ 55 °C → **III. klasa zapaljivih tečnosti**. Storage and handling inside a building falls under the *Pravilnik o izgradnji postrojenja za zapaljive tečnosti i o uskladištavanju i pretakanju zapaljivih tečnosti* (Sl. list SFRJ 20/71, 23/71 — still applied in BiH) and, for the site's entity, the *Zakon o zaštiti od požara Republike Srpske*, which requires an **Elaborat zaštite od požara** and a competent-authority approval as part of the technical documentation. **Nothing in the TD or the BOQ procures a fire elaborate, a fire-safety design, or any approval.**

**BH Telecom's own precedent contradicts this design.** The MATISA reference — the executed, approved BH Telecom solution — placed the gensets and the 3 000 l tank in a **dedicated container containing no TK equipment**:

> *"Prostor u kojem se projektuje električna instalacija je namjenjen za smještaj agregata 2x13,3 kVA."* … *"Posjednutost ljudima je povremena i to samo u periodima kada se vrše kontrole i opravke uređaja."* — `3_DIS_MAS_EL_DIO…`, list 90

The Sjednica design abandons that separation without justification and without any fire compartmentation. **If the genset and tank must share the container, an EI 60/EI 90 fire-rated separation between the genset/fuel zone and the TK zone is required — which is spatially impossible in 6.29 m² (see RED-06). The correct answer is a separate genset enclosure/kiosk outside the container.**

*Refs: `03 ELEKTRO dio.doc` §3.7.2, §3.7.3; MATISA `3_DIS_MAS_EL_DIO…` lists 79, 90; BOQ LOT 2 items 4.2, 4.3, 4.15.*

---

#### RED-06 — The installation does not fit. The tender's own future-state drawing shows the container empty.

**Available floor.** Certified as-built: **P = 6.29 m², perimeter 10.13 m → 2.88 × 2.18 m clear** (DXF `01 Osnova`).

**Already occupied** (Prilog III p.21 / E-08 and DXF 3.5.3): GRO, UPS, UPS-R, U1, PE1 on one wall; ROS, TZ, PRENOS, RBS_2, RBS_1, MPU, PE2, U2, U3 on the other; A/C indoor unit; cable trays; ceiling luminaires + AJP.

**Required to be added:**

| Item | Footprint |
|---|---|
| P22-6 open skid (≈ 1 900 × 750 mm) | 1.43 m² |
| 500 l double-wall tank (≈ 1 200 × 800 mm) | 0.96 m² |
| 110 % bund beneath both (BOQ 4.3) | **≥ 2.65 m²** (see RED-07) |
| Service access (radiator, alternator, control panel, oil/filter access) | on all sides |
| Aisle to the existing TK racks | ≥ 0.80 m |

A realistic K3 container leaves a central aisle of **≈ 2.4 m²**. The requirement is at least **2.65 m² for the bund alone**. **The scope is not physically constructible in this container.**

**Compounding drawing defect.** Prilog III drawing **S-02 "BUDUĆE STANJE"** draws the container as an **empty rectangle** with the DEA and the fuel tank filling it. Not one existing item — GRO, UPS, UPS-R, RBS_1/2, PRENOS, ROS, TZ, MPU, klima — is shown. **Bidders are being asked to price from a drawing that misrepresents the site.** Under prompt.md §2.4 (*Geometry & Layout — is the equipment layout feasible on the given plot; are clearances for installation/maintenance respected*) this fails outright.

**Access.** BOQ 4.1: *"unos agregata vrši se kroz kapiju na sredini istočne strane ograde i kroz ulazna vrata kontejnera (svijetla širina cca 1,00 m; vrata 900 × 2000 mm)"*. A ~700–800 kg skid will pass the door dimensionally but there is no crane access and no manoeuvring space inside a 2.18 m wide room. Placing the responsibility on the bidder (*"Ponuđač bira način unosa i montaže i dužan je u ponudi potvrditi izvodljivost"*) does not make an infeasible layout feasible.

*Refs: DXF `01 Osnova`; Prilog III p.4 (S-02), p.21 (E-08); BOQ LOT 2 items 4.1, 4.3.*

---

#### RED-07 — The tender's own floor-loading arithmetic is wrong, and the weight data needed to check it is absent.

BOQ LOT 2 item 4.4 asserts:

> *"…masa skida i punog spremnika od 500 l (cca 1.150–1.350 kg na 2–3 m²) **NE prelazi ove vrijednosti**, zbog čega se ojačanje **NE očekuje** kao neophodno…"*
> (against a stated available live-load budget of ≈ 5.0 kN/m² over ≈ 5.8 m², from the K3 container's 10.00 kN/m² total)

**Check:**

| Mass | Over 2.0 m² | Over 2.5 m² | Over 3.0 m² |
|---|---|---|---|
| 1 150 kg | **5.64 kN/m² ✗** | 4.51 kN/m² ✓ | 3.76 kN/m² ✓ |
| 1 350 kg | **6.62 kN/m² ✗** | **5.30 kN/m² ✗** | 4.41 kN/m² ✓ |

**Minimum spread area for 1 350 kg at 5.0 kN/m² = 2.65 m².** The tender's statement is **false across most of its own stated range**. Consequently the steel spreader grillage (*čelični roštilj*) is **not conditional — it is required**, and must be designed to distribute over ≥ 2.65 m² onto the container's main floor beams. The tender's conclusion that strengthening "is not expected to be necessary" must be deleted; it will bias bidders into omitting it from their price.

Additionally, **the P22-6 datasheet contains no dry or wet weight** (§2.5). Neither a bidder nor a checking engineer can perform item 4.4's mandatory static calculation from the tender pack.

Also missing: a **dynamic amplification factor** for a reciprocating machine on anti-vibration mounts (EN 1991-1-1 / ISO 8528-9; typically 1.2–1.5), and any requirement on the AV mounts' natural frequency (must be ≤ 8 Hz against the 25 Hz firing frequency at 1 500 rpm) to protect the TK racks from structure-borne vibration.

*Refs: BOQ LOT 2 item 4.4; TD "Postojeće stanje"; Prilog III p.34; P22-6.pdf.*

---

#### RED-08 — Fire and fuel safety measures that are simply not in the scope.

BOQ item 4.15 procures: ceiling smoke detector, thermal detectors t > 30 °C and t < 10 °C, one S-6 extinguisher, and *"automatski uređaj za gašenje požara"*. That is the whole of the fire scope. Missing, all mandatory for this installation:

| Missing item | Why it is required |
|---|---|
| **Fire-safe fuel shut-off valve at the tank outlet** (fusible link or fail-closed solenoid), closing on fire alarm and on E-STOP | Without it a ruptured fuel line feeds the fire from a 500 l reservoir. This is the single most important omission after ventilation. |
| **CO and NO₂ detection** with alarm to ROS and forced ventilation | A diesel engine in a 6.29 m² room entered by staff. No gas detection of any kind is specified. |
| **Ventilation / damper interlock with the suppression system** | An automatic extinguishing discharge into a room with a running 1 200 m³/h fan and 0.79 m² of open louvre is expelled within seconds. The suppression must shut down the engine, stop the fan and close the dampers. |
| **Motorised or gravity dampers** on both louvres | Fire containment, weather-tightness, IP55, EMC shield, and A/C effectiveness (RED-02). |
| **Type, agent, design concentration and certification** of the "automatski uređaj za gašenje požara" | Undefined — it cannot be priced, verified or approved. |
| **Anti-siphon / non-return valve** on the fuel feed | The BOQ specifies a self-priming pump (item 3.1) but no siphon break. |
| **Breather terminal detail**: height ≥ 2 m, ≥ 3 m from the exhaust terminal and any air intake, **flame arrestor** | Currently only *"otvor zaštićen metalnom mrežicom"*. On the north wall it will sit beside a 520 °C exhaust (RED-03). |
| **Overfill prevention device** and drip tray at the fill point | Filling by road tanker on a mountain track. |
| **Class B / flammable-liquid signage** — P003 no smoking/naked flame, W021 flammable, product and capacity marking, exhaust-gas warning | Only W012 "OPASAN NAPON" on the GRO is specified (BOQ 5.6). |
| **Second extinguisher** | One 6 kg dry powder (S-6) beside live TK electronics; add a 5 kg CO₂ and locate both **outside** the door. |

**E-STOP.** BOQ 4.1 specifies *"taster EMERGENCY STOP uz ulazna vrata kontejnera"* but does not say **which side of the door**. It must be **outside**, plus one at the KOA, hard-wired as an ISO 13850 category-0 stop that kills the engine, the fan and the fuel valve.

**Correctly specified — retain (GREEN, see §3.3):** double-wall tank *and* 110 % bund under both tank and set (4.2/4.3); interstitial leak probe; two independent level gauges; external fill point with tanker static-discharge earthing; external breather.

*Refs: BOQ LOT 2 items 4.1, 4.2, 4.3, 4.15; MATISA `3_DIS_MAS_EL_DIO…` list 80.*

---

#### RED-09 — Automatic disconnection of supply cannot be achieved. The certified design's RCD has been deleted.

**The generator's fault current.** BOQ item 3.1 (Generator) itself specifies *"dozvoljena struja kratkog spoja 3×In u trajanju 10 s"*.

- I_n = 22 000 / (√3 × 400) = **31.75 A**
- Sustained short-circuit current = 3 × I_n = **95.3 A**

**The specified protection.** BOQ 5.6 fits *"3 kom 1p automatski prekidač, C, 32 A, 10 kA za zaštitu napajanja preko DEA"* and *"1 kom 3p automatski prekidač, C, 32 A, 10 kA"* for the rectifier.

- C-curve 32 A magnetic band = 5–10 × I_n = **160–320 A**. At 95 A **there is no magnetic trip.**
- Thermal trip at 95 A (≈ 3 × I_n) takes of the order of **4–15 s**.
- **IEC 60364-4-41 Table 41.1** requires **0.4 s** for 230 V a.c. TN final circuits ≤ 32 A, and §411.3.2.3 allows 5 s for distribution circuits.
- Even a **B-curve 32 A** (3–5 × I_n = 96–160 A) sits at the very bottom of its magnetic band at 95.3 A — no guaranteed instantaneous operation.

**→ An earth fault on this island supply will not be cleared within the required disconnection time.**

**It gets worse: the reference set has a SHUNT-excited alternator.** P22-6.pdf p.2 lists, under Standard Equipment / Alternator: *"FG Wilson Alternator — **SHUNT Excitation** — IP23 Protection"*. A shunt-excited alternator loses its excitation on a close-up short circuit; sustained fault current can fall to **1–1.5 × I_n**, not 3 ×. **The BOQ's requirement of 3 × I_n for 10 s is therefore incompatible with the named reference product** — it requires PMG or AREP/auxiliary-winding excitation, which is a cost item the tender does not identify.

**And the certified design already solved this — the tender removed the solution.** Prilog III p.16 (drawing 5.5.3 *tropolna šema GRO*, GP-TO-13617, 2018) shows the existing GRO incomer as a **"3 polna FID SKLOPKA 40/0,03A"**. The new GRO in BOQ 5.6 contains **no RCD at all**, while still feeding *"2 kom 1p automatski prekidač, C, 16 A… za ostalu AC opremu kontejnera (rasvjeta, utičnice…)"* — socket-outlets for which **IEC 60364-4-41 §411.3.3 mandates 30 mA RCD protection**. This is a direct regression from an approved design.

**Required corrections to BOQ 5.6:**

| Replace | With |
|---|---|
| 3 × 1P C32 for the genset feed | **1 × 4P (3P+N) MCCB 40 A** with adjustable magnetic setting — never three independent single-pole devices on a three-phase supply (a single-pole trip single-phases the load and leaves two phases live) |
| — | **4P RCD 300 mA, S-type (selective, time-delayed)** as the incomer, for fault protection per IEC 60364-4-41 §411.4.4 |
| — | **30 mA type A RCBOs** on the socket and lighting circuits, discriminating under the S-type incomer |
| 3P C32 for the rectifier | **3P C25** (rectifier design current 18.4 A — see RED-11), giving 40/25 = 1.6 grading; verify let-through energy against the manufacturer's discrimination tables |

*Refs: BOQ LOT 2 items 3.1, 5.6; P22-6.pdf p.2; Prilog III p.16; IEC/BAS EN 60364-4-41 §411.3.3, §411.4.4, Table 41.1.*

---

#### RED-10 — Earthing system type is undefined for an island supply; the only N–PE bond is in a cabinet that no longer has a source.

The certified project builds the earthing system around a **utility** connection:

> *"PEN vodič napojnog kabla u PMO vezati na uzemljivačku šinu…"* — `03 ELEKTRO dio.doc` §3.2.1
> *"Napomena: 1) Spoj nultog i zaštitnog provodnika (N i PE) izvršiti **samo u ovom ormaru** [PMO]. U usponskoj instalaciji ovi se vodiči nigdje više ne spajaju."* — DXF 3.5.1
> *"…na ulaznoj strani napajanja u PMO izveden prelaz TN/C na TN/S…"* — `03 ELEKTRO dio.doc` §3.3.6

**There is no utility supply.** The PEN that established the system earth does not exist. Yet:

- The TD does not state the earthing system type for the new island supply.
- BOQ 5.6 (GRO) says nothing about N–PE.
- The only statement is buried in the **KOA** specification (BOQ 3.1): *"sabirnice L1, L2, L3, N i PE (N i PE spojene samo na jednom mjestu)"* — which does not say **where**.

**This must be resolved explicitly, because two failure modes follow from getting it wrong:**
1. If **no** N–PE bond is made, the installation is an unearthed IT system by accident, with no insulation monitoring and no fault protection.
2. If a **new** bond is made at the GRO or KOA **and** the old PMO bond remains connected to the earth bar, a parallel N–PE path is created, circulating load current in the protective conductors and defeating the RCDs required by RED-09.

**Specify:** **TN-S island system**, with the **alternator star point earthed at exactly one point** — at the KOA / first distribution point — via an earthing conductor of ≥ 16 mm² Cu, connected to the site MET (PE1/PE2) and thence to the ring electrode. Require the contractor to **verify and record the removal/isolation of the PMO PEN bond**, or the formal decommissioning of the PMO. State that no further N–PE connection may exist anywhere downstream. (An IT system with insulation monitoring is a defensible alternative for continuity of service and should be priced as an option, but must not be arrived at by accident.)

**Also affected:** the whole of the certified project's §3.3.4 (touch voltage), §3.3.5 (short circuit) and §3.3.6 (earth-fault current) is computed for a low-impedance utility source with 35 A fuses and is **void** for a 95 A island supply. **No revision of the certified electrical project (izmjena glavnog projekta) is procured anywhere in the tender.**

*Refs: `03 ELEKTRO dio.doc` §3.2.1, §3.3.4–3.3.6; DXF 3.5.1; BOQ LOT 2 items 3.1, 5.6.*

---

#### RED-11 — The GRO's source selector is conceptually wrong; the referenced design ("Brložki Potok") is not in the package.

**The missing reference.** TD, "Postojeće stanje": *"Predviđena je i ugradnja NOVOG GLAVNOG RAZVODNOG ORMARA (GRO) sa sekcijama AGREGAT i SOLAR u kontejner, **prema rješenju primijenjenom na lokaciji Brloški Potok iz referentne tenderske dokumentacije**."* That document is **not in the package** and is **not listed** among the nine reference documents in Prilog III p.34. A tender cannot incorporate by reference a document bidders do not have.

**However — BOQ 5.6 already defines the board in full.** The correct fix is therefore to **delete the Brložki Potok reference from the TD** and rely on a corrected item 5.6, so the tender stands alone. The corrections needed are:

**(a) The three-position selector is wrong.** BOQ 5.6: *"1 kom 4p tropoložajna sklopka za odabir izvora napajanja, izvedbe 1-0-2, 63 A… Položaje obilježiti: 1-'hibridni sistem', 0-'isključeno', 2-'agregat'."*

The hybrid system is an **AC load** (the rectifiers consume AC), **not an AC source**. On an off-grid site the genset is the only AC source. Position "1 — hibridni sistem" would connect the AC busbar to nothing. This is a mains/genset changeover with the label "mreža" simply overwritten — a copy-paste from a grid-connected site, and precisely the error the TD elsewhere warns against (*"LOKACIJA NIJE PRIKLJUČENA NA ELEKTROENERGETSKU MREŽU — NE predviđa se mrežni sklopnik"*, BOQ item 3.1).

**No ATS/changeover contactor is appropriate here.** There is nothing to transfer *from*. What *is* genuinely useful at an off-grid site is a **standby-source inlet**:

> Replace with a **4-pole 63 A three-position changeover 1-0-2** labelled **1 – "FIKSNI DEA"**, **0 – "ISKLJUČENO"**, **2 – "VANJSKI/MOBILNI AGREGAT"**, with a **63 A 5-pin CEE 400 V inlet socket** on the container wall, mechanically interlocked so the two sources can never be paralleled, plus a status contact to the DSE controller. This lets a mobile set restore the site when the fixed genset fails — a real operational requirement on a 1 076 m mountain top.

**(b) Missing from the board specification.** Beyond RED-09's RCD and 4-pole breaker corrections:

| Missing | Requirement |
|---|---|
| Prospective fault current / Icu rating basis | 10 kA is specified but the actual PSCC of a 22 kVA alternator is ~0.1 kA; state the basis. |
| Discrimination study | Required between the 40 A incomer, the 25 A rectifier feed and the 16 A auxiliary ways. |
| SPD backup fuse and lead-length rule | IEC 60364-5-534 §534.4.9: total SPD connecting-lead length a + b **≤ 0.5 m**, preferably ≤ 0.25 m. Not stated. |
| SPD Type | See RED-12. |
| Metering | No kWh meter for genset output / rectifier consumption. Only controller telemetry. |
| Neutral disconnection | The isolator must switch N (4-pole) — a 3-pole *"dvopoložajna sklopka… 0-1, 63 A"* is specified. |
| Circuit schedule / labelling | Only two nameplate texts are specified; a full circuit chart is needed. |

**(c) Scope contradiction between the TD and the BOQ.** The TD requires *"GRO sa sekcijama AGREGAT i SOLAR"*. BOQ 5.6 is titled *"GRO — AC RAZVODNA SEKCIJA"* and states explicitly that the DC/solar distribution is **not** in this board but in the PVDB under **LOT 1** item 1.6. Since the two LOTs may be awarded to **different contractors**, the "SOLAR" section the TD requires may be supplied by neither. Resolve the LOT interface explicitly.

**(d) The existing GRO is orphaned.** The AC wiring schedule shows the existing GRO feeding seven circuits (K1 UPS, K2 UPS-R, K3 AC klima, K4 U1+U2, K5 tehnička zaštita, K6 rasvjeta+vanjska+antipanik, K7 tower obstruction light). **No BOQ item covers disconnecting, re-terminating and re-testing those circuits onto the new GRO**, nor decommissioning the old board, nor reworking the ROS alarm scheme — which still expects a mains-failure signal (**"NEST.1.F"** in the DC wiring schedule) that will never occur on an off-grid site. The new GRO's *"2 kom 1p… C, 16 A, sa rezervom"* is nowhere near enough for seven existing circuits.

*Refs: TD "Postojeće stanje"; BOQ LOT 2 items 3.1, 5.6; BOQ LOT 1 item 1.6; Prilog III p.16, p.34; `CONTAINER_Tablica_ozicenja_AC/DC_instalacija`.*

---

#### RED-12 — Surge protection: Type 1 SPDs and all data-line SPDs are missing.

**The site has an external LPS.** Air termination on the 38 m tower, Fe/Zn 25×4 down-conductor down the tower to the first leg flange, ring electrode at 0.80 m, fence bonded at ≥ 4 points (DXF 3.5.9; `03 ELEKTRO dio.doc` BOQ items 1–2). The container, the fence and the new PV supports are **all bonded to that same electrode** (BOQ LOT 1 item 1.4). **Separation distance per EN 62305-3 §6.3 is therefore not maintained anywhere on this site — by design, and correctly so.**

**Consequence (EN 62305-4 §7.3.1 / IEC 61643-12):** where an external LPS exists and separation is not maintained, **Type 1 SPDs tested with I_imp (10/350 µs)** are required at every LPZ 0_A / LPZ 1 boundary. The tender specifies only Type 2 (8/20 µs) devices:

| Location | Tender specifies | Required |
|---|---|---|
| PV strings, PVDB (LOT 1 item 1.6) | *"odvodnik prenapona DC (tip 2) za svaki string"* | **Type 1+2 combined**, I_imp ≥ 5 kA (10/350) per mode, **U_cpv ≥ 425 V** (= 1.2 × Voc at −25 °C, see §4.7), U_p ≤ 80 % of the equipment withstand |
| **Array end of the DC run** | *nothing* | **A second SPD set at the array junction box** — the run is 25 m, and EN 61643-32 / IEC 62548 require SPDs at both ends when the array-to-SPD distance exceeds ~10 m |
| AC origin (GRO, item 5.6) | *"odvodnik prenapona AC, 4p, katodni, min. 40 kA / 275 V"* — a Type 2 | **Type 1+2**, I_imp ≥ 12.5 kA (10/350) per mode, U_c 275 V, with backup fuse |
| **Data / signal lines** | *nothing* | **SPDs on the STP Cat5 to the site switch, on the J-Y(ST)Y alarm multicore to the ROS, and on the genset controller's RS485/Ethernet** — EN 61643-21. On a 38 m-tower site these are the highest-risk entry paths. |
| −48 V DC side | *nothing* | SPD at the new PV feed into the ICC330 / MTS9302 |

**Note:** the iSSU S4875G2 has *"Input port dual-wire-to-ground common mode ± 10 kA 8/20 µs"* built in (iSSU datasheet p.2). That is a Type 2-class internal device in **common mode only**; it does **not** substitute for a Type 1 at the LPZ boundary and does not protect differential mode.

**Huawei's own mandatory requirement is breached by BOQ 5.1.** *PV Module Solution User Manual* Iss. 07, **§4.1.3 Surge Protection**, p.107:

> *"The site shall be equipped with a surge protection system and site devices shall be properly grounded."*
> *"**The PV module cable shall be at least 0.5 m away from the ground cable of the lightning rod.**"*

BOQ LOT 2 item **5.1** excavates *"rov dimenzija **0,40 × 0,80 m** … za polaganje elektroenergetskih kablova **i uzemljivačke trake**"* — i.e. the DC/power cables and the earth tape share **one 0.40 m wide trench**. **0.40 m < 0.50 m: non-compliant by construction.** The certified project got this right, using **two separate trenches** (70 m for the earth tape, 25 m for the supply cable — `03 ELEKTRO dio.doc` §3.4.1 items 3 and 4). Restore the separation.

*Refs: BOQ LOT 1 item 1.6; BOQ LOT 2 items 5.1, 5.6; Huawei PV manual §4.1.3 p.107; iSSU datasheet p.2; DXF 3.5.9; EN 62305-3 §6.3, EN 62305-4 §7.3.1, EN 61643-21/-32, IEC 60364-5-534.*

---

#### RED-13 — H07V-K 25 mm² is the wrong cable and the wrong size for bonding outdoor structures.

BOQ LOT 1 item 1.4: *"Uzemljenje nosivih konstrukcija: povezivanje obje konstrukcije na postojeći prstenasti uzemljivač lokacije vodičem **H07V-K 25 mm²** (žuto-zeleni), preko priključnih stezaljki na konstrukciji, komplet sa ukrsnim komadima."*

**Three separate defects:**

1. **Wrong cable type.** H07V-K (HD 21.3 S3 / IEC 60227-3) is a 450/750 V PVC single-core **building wire for fixed installation inside conduits and enclosures, in dry indoor locations**. It is **not UV-resistant, not suitable for outdoor exposure, and not suitable for direct burial**. Using it to bond outdoor galvanised structures at 1 076 m in East Herzegovina is a direct misapplication that will fail within a few winters.

2. **Undersized for lightning-current duty.** The PV supports are exposed outdoor metal structures bonded to an earth-termination system on a site with an external LPS. **EN 62305-3 Table 7** requires earthing conductors and down-conductors capable of carrying lightning current to be **≥ 50 mm² Cu** (or 50 mm² steel). 25 mm² Cu is not listed for this duty. (EN 62305-3 **Table 6** permits 16 mm² Cu for a pure equipotential bonding conductor, but that classification is not defensible here.)

3. **Below the site's own established practice.** The certified project earths PE1 and PE2 to the Fe/Zn tape with **P/F 1×50 mm²** (K9, K12) and uses **1×35 mm²** for the down-conductor bond (K10) — Prilog III p.20 (E-07); DXF 3.5.8. Bonding a *new outdoor* structure with 25 mm² is half the size used for existing *indoor* main bonds.

4. **Galvanic incompatibility, unaddressed.** A copper conductor bolted to hot-dip galvanised steel and buried in soil will strip the zinc (EN 50522 §5.4; EN 62305-3 Annex E). BOQ 5.4 procures *"FeZn 60×60 mm ukrsnih komada"* — galvanised **tape-to-tape** cross clamps, which are not the right fitting for a Cu conductor at all. Items 1.4 and 5.4 do not match, and no corrosion protection of the buried joint is specified.

**Preferred solution (cheapest and correct):** continue the **Fe/Zn 25×4 mm tape** already procured under BOQ 5.3 (40 m) all the way to each support and terminate on a **stainless-steel bolted lug** on the galvanised column, with an **accessible bolted inspection joint above grade**, all buried joints encapsulated (bitumen tape / anticorrosive compound). No copper in the soil. If a cable must be used, specify **bare Cu 50 mm²** or a **UV-resistant, burial-rated earthing cable of 50 mm² Cu**, with bimetallic connectors.

**Also add:** the ground-support frames are **bolted, hot-dip galvanised** assemblies. Bolted galvanised joints are not a reliable lightning-current path. Specify bonding jumpers across the bolted joints, or a continuity test (< 0.1 Ω across each joint) as a hold point, and bond **each support at two points** (currently 2 kpl total for two supports = one each).

*Refs: BOQ LOT 1 item 1.4; BOQ LOT 2 items 5.3, 5.4; Prilog III p.20; DXF 3.5.8, 3.5.9; EN 62305-3 Tables 6 & 7, Annex E; EN 50522 §5.4.*

---

#### RED-14 — The <68 dBA at 7 m requirement is unachievable with what is in the BOQ.

BOQ item 4.1: *"dozvoljeni nivo buke izvan kontejnera: **< 68 dBA pri opterećenju 75 % na 7 m**, režim Standby"* — for a set explicitly supplied **without its own enclosure** (item 4, *"bez vlastitog vanjskog kućišta, jer funkciju kućišta preuzima kontejner"*).

**Calculation:**

- Required sound power: L_W = 68 + 10·log₁₀(2π × 7²) = **92.9 dB(A)**
- An open-frame 22 kVA set: L_p ≈ 96 dB(A) at 1 m → L_W ≈ **104 dB(A)**
- **Required insertion loss ≈ 11.1 dB(A)**

**But the container, once perforated, cannot deliver it.** Composite transmission loss is dominated by the openings:

- North wall area ≈ 3.08 × 2.80 = **8.62 m²**
- Open area = 0.35 (intake) + 0.36 (discharge) + Ø315 fan (0.078) = **0.788 m²**
- Composite TL ≤ 10·log₁₀(8.62 / 0.788) = **10.4 dB(A)**

**10.4 dB available vs. 11.1 dB required — and that is before the openings are enlarged to the correct sizes in RED-01, which will make it worse (larger apertures → lower composite TL).** With the corrected 0.96 m² + 0.72 m² louvres the composite TL falls to ≈ 7 dB.

**What is actually needed, and is entirely absent from the BOQ:**
- **Absorptive splitter attenuators** on both the intake and the radiator discharge (typically 0.9–1.5 m long)
- A **residential-grade exhaust silencer** (P22-6.pdf p.3 lists *"Industrial, Residential, Critical Silencers"* as **optional** equipment — the BOQ says only *"ispušni lonac"*, unspecified)
- Attenuation of the extract fan discharge

**And this closes a vicious circle with RED-01:** attenuators add **100–250 Pa each** to the airflow path, against a radiator fan whose total external static allowance is of the order of 123 Pa. **A standard open skid set + a standard radiator fan + < 68 dBA at 7 m is not a buildable combination.** Either the noise limit is relaxed with a justification, or the set is supplied in a proper acoustic canopy — which returns to the conclusion of RED-05 and RED-06: **put the genset in its own enclosure outside the TK container.**

*Refs: BOQ LOT 2 items 4.1, 4.6–4.11; P22-6.pdf p.3 (Optional Equipment / Exhaust, Enclosure).*

---

### 3.2 YELLOW — requires clarification or additional calculation

| # | Finding | Source / basis |
|---|---|---|
| **Y-01** | **The genset datasheet supplied contains no technical data.** P22-6.pdf is a 3-page product-specification sheet. Cooling air flow, combustion air, radiator heat rejection, max. external static restriction, exhaust flow/temperature, max. back pressure, exhaust connection size, weights, fuel consumption and noise data are **all absent**. The entire mechanical design was produced without them. Require the manufacturer's **Technical Data Sheet** as a mandatory tender deliverable. | P22-6.pdf pp.1–3; prompt.md §3 (missing manufacturer datasheet ⇒ flag) |
| **Y-02** | **Duty class is wrong.** The set is specified as **Standby (ESP), ISO 8528-3**. ESP is defined for *"supplying continuous electrical power… in the event of a utility power failure"* (P22-6.pdf p.1) — there is no utility. A set cycling daily on battery SoC for 250 h/yr is a **Prime (PRP)** duty. Derated at site the PRP rating (20 kVA/16 kW) still covers the 12.8 kVA rectifier load. | P22-6.pdf p.1; BOQ item 3.1; ISO 8528-1 |
| **Y-03** | **No minimum-load requirement — wet stacking.** The TK load alone is 1.33 kW = **7.6 %** of 17.6 kW. Running a diesel below ~30 % load causes cylinder glazing and wet stacking. The BOQ mandates SoC-based start (correct) but sets no minimum load, no minimum run time, and no periodic exercise regime. Specify: start only with the rectifiers at their full programmed current limit (≥ 30 % = 5.3 kW), minimum run 30 min, and a quarterly ≥ 50 % load exercise. | BOQ items 3.1, 6.1 |
| **Y-04** | **Site derating not quantified in the BOQ.** ISO 3046-1 / ISO 8528-1: ~−1 %/100 m above 100 m → **≈ −10 %** at 1 076 m, plus ~−2–4 % for 40 °C ambient. 22 kVA ESP → ≈ **18.7–19.4 kVA at site**; 20 kVA PRP → ≈ **17.0–17.6 kVA**. Both still exceed the 12.8 kVA duty. The BOQ correctly requires the bidder to prove it — but the reference conditions (25 °C, 100 m) should be quoted from the datasheet in the item. | P22-6.pdf p.1; BOQ item 3.1 |
| **Y-05** | **Signal cable core count is insufficient.** BOQ 5.5: **J-Y(ST)Y 4×2×0.6 = 8 cores**. Item 4.15 alone needs 4 signals (smoke, high temp, low temp, fire), plus tank leak, low fuel, run status, common fault = **8**, with the E-STOP loop needing its own dedicated pair. Zero spare. Specify **10×2×0.6 minimum**, or carry the non-safety signals over the Modbus RTU link already provided by the STP Cat5. | BOQ items 4.15, 5.5 |
| **Y-06** | **PVDB is under-specified.** BOQ 1.6 gives no DC isolator rating, no fuse type, no SPD parameters. Specify: isolator U_e ≥ 1.15 × Voc(−25 °C) = **≥ 410 V DC**, utilisation category **DC-PV2 / DC-21B** per IEC 60947-3 Annex D; if fuses are fitted they must be **gPV** to IEC 60269-6; SPD per RED-12. Note that Huawei's own **PVDB500-15-2B is rated 15 A per route** (PV manual p.72) — **below the 18.0 A design current** — so that specific product must not be used. | BOQ item 1.6; Huawei PV manual p.72 |
| **Y-07** | **MC4 connectors are not quantified and inter-brand mating is not prohibited.** BOQ 1.5 says *"uključujući MC4 konektore"* with no count. Minimum **8 field-terminated connectors** (2 strings × 2 poles × 2 ends), plus spares. **IEC 62852** requires connectors to be of the same type/manufacturer as those they mate with unless the combination is type-tested — mating different brands is one of the most common causes of PV DC arc fires. State it explicitly. | BOQ item 1.5; IEC 62852 |
| **Y-08** | **Bifacial gain may exceed the iSSU input power limit.** 6 × 585 = 3 510 Wp per string; the iSSU S4875G2 maximum input power is **4 000 W**. A bifacial gain of 15 % gives 4 037 W. Confirm the bifacial gain assumption and the iSSU's clipping behaviour. | BOQ item 1.1; iSSU datasheet p.2 |
| **Y-09** | **Quantity inconsistencies in the cable/trench items.** BOQ 1.5 needs **2 × 25 m of DC route**; BOQ 5.2 provides only **3 × 15 m = 45 m** of PEHD Ø50; BOQ 5.1 provides only **30 m** of trench. These cannot all be true. Drawing S-02 suggests a route of ~6–9 m per support. Reconcile against a dimensioned route drawing. | BOQ items 1.5, 5.1, 5.2; Prilog III p.4 |
| **Y-10** | **Earth resistance target is undefined.** BOQ 5.8: *"Otpor uzemljenja mora zadovoljiti zahtjeve Projektnog zadatka"* — a document bidders do not have. State a number. The certified project computes **R = 5.91 Ω** (ρ = 250 Ωm, 95 m tape, 0.80 m). EN 62305-3 §5.4.1 recommends a single earth resistance **< 10 Ω**. | BOQ item 5.8; `03 ELEKTRO dio.doc` §3.3.8 |
| **Y-11** | **New earth tape depth (1.00 m) does not match the existing ring (0.80 m).** BOQ 5.3 specifies 1.00 m *"obzirom da se radi o planinskoj lokaciji"*; the certified ring is at 0.80 m (DXF 3.5.9; §3.3.8). Not wrong, but the transition detail between the two depths must be drawn. | BOQ 5.3; DXF 3.5.9 |
| **Y-12** | **Cable fire performance not specified.** NYY-J is PVC (class Eca under EN 50575/CPR). In a room containing 500 l of diesel and live TK equipment, specify **halogen-free** (EN 60754-1/-2, EN 61034 smoke) and at least **Cca-s1b,d1,a1**. Consider circuit integrity (FE180/E30) for the E-STOP and fire-alarm wiring. | BOQ item 5.5 |
| **Y-13** | **No ventilation start-permissive.** Item 4.9 correctly interlocks the fan with genset start (copied from MATISA). But nothing proves the discharge path is **open** before the engine cranks. Add damper end-switches / a differential-pressure switch as a start permissive to the DSE controller. | BOQ item 4.9; MATISA `3_DIS_MAS_EL_DIO…` list 81 |
| **Y-14** | **110 % bund creates a 220 mm upstand.** 550 l over the ≈ 2.65 m² required footprint = **0.22 m** of wall height inside a 2.18 m wide room. Trip hazard, headroom loss and an obstruction to maintenance. Detail it, with a low-point sampling/drain point fitted with a **locked, normally closed** valve, and no floor penetrations inside the bund. | BOQ items 4.3, 4.4 |
| **Y-15** | **Anti-vibration performance unspecified.** Specify mounts with a natural frequency ≤ 8 Hz (vs. 25 Hz at 1 500 rpm) and ≥ 90 % isolation efficiency, plus flexible connections on **all** services crossing the skid boundary (fuel, exhaust, electrical, coolant). | BOQ items 4.1, 4.5, 4.11 |
| **Y-16** | **TD requires a factory-assembled set including an enclosure and transfer panel, contradicting the skid scope.** TD §6: *"…isporučuje se kao jedan proizvod (sastavljen od dijelova: dizel motora, generatora, kontrolera, **izolovanog kućišta**, **transfer panela** i spremnika)"* vs. BOQ item 4: *"bez vlastitog vanjskog kućišta"*. Also the guarantee clauses repeatedly reference a **"vučna prikolica"** (tow trailer) that is not in this scope — residue from a mobile-genset tender. | TD §5.2, §6 |
| **Y-17** | **BOQ LOT 2 numbering is broken.** The sheet has section header "**1** AUTOMATSKI DIZEL ELEKTRIČNI AGREGAT" with item **1.1**, then item **3.2** and total "UKUPNO **3**", then sections 4, 5, 6. Item **4.1** references *"DEA opisanog pod **Tačkom 3.1**"* — which does not exist. Bidders cannot cross-reference or price reliably. | BOQ LOT 2 rows 11–59 |
| **Y-18** | **TD lists LOT 2 works under the LOT 1 heading.** The phrase *"Radovi i usluge za puštanje u rad hibridnog sistema (LOT 1) obuhvataju:"* appears **twice**; the second list contains genset transport, installation, floor strengthening and remote-monitoring connection — all LOT 2. A LOT 1 bidder could be held to genset works. | TD "Predmet nabavke" |
| **Y-19** | **First fuel fill contradicts itself.** TD: *"tankanje **najmanje 200 l**"*; BOQ 4.16: *"Prvo punjenje… **500 l**"*. | TD; BOQ item 4.16 |
| **Y-20** | **The power system is named three different ways.** TD: *"Huawei **MTS9302**"*; Prilog III p.3/p.4: *"**ICC330-H1** (outdoor) + MTS9302"*; BOQ: *"**PowerCube 1000**"*, *"**AIU03**"*, *"**GIM01C1**"*, *"3 × **R4875G5**"*. There is no single, consistent definition of the system the genset must interface with — yet TD makes the bidder responsible for *"mehaničku i električnu kompatibilnost"*. | TD; Prilog III pp.2–4; BOQ items 3.1, 5.6, 5.7 |
| **Y-21** | **Lightning protection level is nowhere stated.** The result of §4.5 changes with LPL. Declare the LPS class for the site (BH Telecom standard is typically LPS Class III for BS sites) and record it in the tender. | EN 62305-3 §5.2 |

---

### 3.3 GREEN — correctly implemented, note for reference

| # | Finding |
|---|---|
| **G-01** | **The radiator is ducted out.** BOQ 4.5 (flexible plenum connection to the radiator core), 4.6 (sheet-metal discharge duct) and 4.7 (discharge louvre) establish the right *architecture* — a sealed radiator discharge, not an open room. This is a genuine improvement on the MATISA reference and it is what makes the installation correctable rather than fundamentally wrong. Only the *sizes* are wrong (RED-01). |
| **G-02** | **Belt-and-braces fuel containment.** Double-wall tank (4.2) **and** a 110 % catch tray under both tank and set (4.3) **and** an interstitial leak probe. This exceeds the minimum and is the right call for a mountain site with no attendance. |
| **G-03** | **Two independent, dissimilar level gauges** with level reported to the monitoring centre (4.2) — directly and correctly carried over from the MATISA reference (list 80, item 4). |
| **G-04** | **External fill point with a tanker static-discharge earthing device at the transfer point** (4.2) — again correctly carried over from MATISA. |
| **G-05** | **Correct off-grid control philosophy.** BOQ 3.1: *"start/stop DEA komanduje se iz Huawei kontrolno-upravljačkog sistema preko modula GIM01C1, po kriteriju stanja napunjenosti baterija (SoC), a NE po ispadu mrežnog napona"*, and *"ulazna snaga ispravljača mora biti ograničena u kontroleru… (3 × R4875G5 = 12 kW)"*. Capping the rectifier input so it cannot overload the set is exactly right and is often omitted. |
| **G-06** | **Single N–PE bond principle is stated** (BOQ 3.1, KOA: *"N i PE spojene samo na jednom mjestu"*) — the principle is correct; only its location is missing (RED-10). |
| **G-07** | **The PV strings are electrically compatible with the iSSU S4875G2.** Voc at −25 °C = **353.8 V** vs. the 435 V maximum (19 % margin); Vmp at 70 °C cell = **227.7 V** vs. the 85 V minimum; Isc 14.40 A vs. the 25 A input limit; 6 modules in series is inside the permitted 3–12. *(iSSU datasheet p.2; PV manual p.32.)* |
| **G-08** | **DC cable sizing, voltage drop and duct fill are all comfortably compliant.** 6 mm² H1Z2Z2-K: design current 1.25 × Isc = 18.0 A against ≥ 37.6 A in the worst installed condition (buried in duct, 2 circuits grouped); voltage drop **2.50 V = 0.95 %** of Vmp over the 25 m route (33 W/string loss); PEHD Ø50 duct fill with 4 cores = **9.4 %** against a 40 % limit. No change needed. |
| **G-09** | **The PV arrays are inside the tower's lightning protection zone.** Rolling-sphere method, EN 62305-3 §5.2.3, 38 m tower with an air termination, PV top at +3.09 m: protected horizontal radius = **10.68 m (LPL I)**, 13.26 m (LPL II), 28.06 m (LPL III), 36.81 m (LPL IV). Maximum distance from the tower axis to the farthest PV corner, scaled from drawing S-02, is **≈ 7.5 m**. **Protected at every LPL, including Class I.** Huawei's own 45° cone criterion (§4.1.3) gives a 34.9 m radius at that height and is also satisfied — though note that **EN 62305-3 Table 2 does not permit the protective-angle method above h = 20 m**, so the rolling sphere is the governing check and Huawei's 45° cone must not be relied on for a 38 m mast. **No additional air terminations are required.** Bonding *is* required, and separation distance is deliberately not maintained — see RED-12 and RED-13. |

---

## 4. DETAILED CHECKLIST (per prompt.md §2.4)

### 4.1 Geometry & Layout
| Check | Result |
|---|---|
| All critical dimensions present | **✗** Container quoted four different ways (§2.2). Duct cross-section given as sheet area "P ≈ 6 m²" instead of a free area. No dimension from the tower to the PV supports. No dimension on the north wall for the louvres vs. the existing cabinets. |
| Equipment layout feasible | **✗ RED-06.** 6.29 m² already fully occupied; ≥ 2.65 m² of bund alone required. |
| Clearances for installation/maintenance | **✗** No service clearance shown around the skid; drawing S-02 omits all existing equipment. |
| Orientation consistent with sun path / wind | **✓** PV azimuth 180°, tilt 45° per the manufacturer's table for 31–45° latitude (site 42.94° N); low support selected for wind. **✗** for the genset: all openings on the north wall, clashing with the Huawei cabinets (RED-03). |

### 4.2 Structural
| Check | Result |
|---|---|
| Foundation dimensions specified | **✓** LOT 1 items 2.3, 2.7 fully dimensioned. |
| Static calculation referenced/provided | **✓ required** (LOT 1 item 1.3; LOT 2 item 4.4) — **✗ cannot be performed**: no genset weight in the datasheet (RED-07, Y-01). |
| Uplift and overturning considered | **✓** explicitly declared governing (LOT 1 items 1.1, 2.3). |
| Soil bearing data | **✓** ≥ 100 kPa stated; noted as not governing. |
| Safety factors per Eurocode | **✓** EN 1991-1-3 (snow), EN 1991-1-4 (wind) with BAS NAs cited. **✗** No dynamic factor for the reciprocating machine (RED-07). |
| Container floor loading | **✗ RED-07** — the tender's own arithmetic is wrong. |

### 4.3 Manufacturing / Fabrication
| Check | Result |
|---|---|
| Steel profiles and thicknesses specified | **✓** LOT 1 item 1.1 (per Huawei BOM, Prilog III p.27); LOT 2 items 4.5–4.7, 4.13 (sheet 1 mm, flange 30×1.5, rockwool 50 mm, Al 1 mm). |
| Weld symbols / accessibility | **✗** Not applicable to LOT 1 (bolted); not addressed for the bund and grillage fabrication. |
| Standard stock sizes | **✓** |
| Corrosion protection defined | **✓** Hot-dip galvanising to **EN ISO 1461** (LOT 1 item 1.1); A2/A4 stainless fixings; 600 °C exhaust paint (4.12). **✗** No corrosion protection specified for the buried Cu-to-Fe/Zn joints (RED-13). |

### 4.4 Installation
| Check | Result |
|---|---|
| Assembly sequence plausible | **✗ RED-06** — no crane access, no set-down space, no sequence given. |
| Lifting points / heavy-equipment access | **Partly** — P22-6 has *"Certified Base Mounted Lifting Eyes, and Rear Drag Eyelets"* (P22-6.pdf p.3), but nothing inside the container can lift 800 kg. |
| Temporary works | **✗** Not addressed. |
| Re-termination of existing circuits | **✗ RED-11(d)** — seven existing GRO circuits orphaned, no BOQ item. |

### 4.5 Maintenance
| Check | Result |
|---|---|
| Safe access for cleaning/inspection/repair | **✗** No service clearance; a 220 mm bund upstand across the aisle (Y-14). |
| Drainage and snow clearance | **✓** LOT 1: panel lower edge at +0.50 m for snow shedding; 1 % fall on foundation tops (item 2.4). **✗** Louvres: *"Žaluzine postaviti tako da se spriječi ulaz vode"* stated, but no snow/drifting provision at 1 076 m and no drain from the discharge duct. |
| Fasteners accessible with standard tools | **✓** |
| Spares | **✓** 500-hour spares set (item 3.2). |

### 4.6 Documentation & BOM
| Check | Result |
|---|---|
| Bill of materials provided | **✓** Prilog II, both LOTs. |
| Quantities/lengths/part numbers consistent with drawings | **✗** Y-09 (cable/duct/trench), Y-17 (broken item numbering), Y-18/Y-19/Y-20 (TD vs. BOQ contradictions). |
| Drawing revision and date clearly marked | **Partly** — Prilog III sheets are numbered (S-01…INFO-05) but carry no revision or date; the embedded K3 drawings do (GP-TO-13617, 2018). |
| References to standards and datasheets correct | **✗** The **Brložki Potok** reference document is cited but absent (RED-11); the P22-6 datasheet contains none of the data the design depends on (Y-01); Huawei's §4.1.3 requirement is breached (RED-12). |
| **Missing deliverables** | Fire elaborate (RED-05); revision of the certified electrical project (RED-10); ventilation & back-pressure calculations (RED-01, RED-04); discrimination study (RED-11); acoustic calculation (RED-14). |

### 4.7 Safety
| Check | Result |
|---|---|
| Sharp edges / pinch points / fall hazards | **Partly** — fan guard (4.10) and *"Fan, Fan drive and battery charging Alternator drive fully guarded to meet EC Machinery Directive"* (P22-6.pdf p.2) ✓; bund upstand trip hazard ✗. |
| Earthing and bonding clearly shown | **✗ RED-10, RED-13** — no earthing-system type for the island supply; wrong bonding conductor. |
| **Fire safety distances (generator, fuel) respected** | **✗ RED-05, RED-08, RED-03** — no fire compartmentation, no fire elaborate, no fuel fire-valve, exhaust terminal beside the fuel breather and the air intake. |
| Automatic disconnection of supply | **✗ RED-09** — cannot be achieved; the certified 30 mA RCD deleted. |
| Toxic atmosphere | **✗ RED-08** — no CO/NO₂ detection. |
| Emergency stop | **Partly** — specified but its location (inside/outside the door) is undefined (RED-08). |
| Noise exposure | **✗ RED-14** — the stated limit is unachievable with the specified scope. |

---

## 5. ACTION ITEMS

### Priority 1 — must be closed before the tender is issued

1. **Obtain the FG Wilson P22-6 Technical Data Sheet** and insert into the tender pack: cooling air flow, combustion air flow, radiator heat rejection, **maximum allowable external static restriction on the cooling air path**, exhaust gas flow and temperature, **maximum allowable exhaust back pressure**, exhaust connection size, dry and wet weight, fuel consumption at 50/75/100 % load, and L_p/L_WA noise data. *(Owner: Procurement / genset supplier. Closes Y-01; prerequisite for actions 2, 3, 5, 6.)*

2. **Re-size the cooling ventilation.** Amend BOQ items 4.6–4.9 to: intake louvre ≥ 1 200 × 800 mm gross with motorised damper; radiator discharge louvre ≥ 900 × 800 mm gross with motorised/gravity damper; discharge duct **free cross-section ≥ 0.25 m²** (state the cross-section, delete "P ≈ 6 m²" as a specification); room extract fan **≥ 2 400 m³/h** (≥ 4 800 m³/h to hold 5 K). **Delete the statement "Minimalna potrebna ventilacija prostora iznosi 120 m³/h (6 izmjena zraka na sat)"** — it is a room-occupancy figure with no engineering relevance to a radiator-cooled engine. *(Owner: Mechanical designer. Closes RED-01.)*

3. **Require a ventilation system pressure-drop calculation** as a mandatory bid deliverable, demonstrating that the total resistance of the intake louvre + damper + attenuator + duct + bends + flexible + discharge louvre + damper + attenuator is **below the manufacturer's stated maximum external static restriction**, at site air density (ρ = 1.007 kg/m³ at 35 °C, 1 076 m). *(Owner: Bidder; verified by mechanical supervision. Closes RED-01.)*

4. **Re-site the exhaust terminal, the radiator discharge and the air intake off the north wall**, or provide a dimensioned layout proving they can coexist with the Huawei ICC330-H1 and MTS9302 outdoor cabinets. Mandate: exhaust terminal **≥ 3 m from any air intake and from the fuel breather**, discharged **upward above roof level**, downwind, and not directed at the Huawei cabinets or the PV array. Delete the *"oboreno prema zemlji u obliku lule"* detail. *(Owner: Designer. Closes RED-03.)*

5. **Change the exhaust pipe to DN 65 minimum, DN 80 preferred**, with expansion immediately downstream of the flexible bellows (the engine flange may remain DN 50). Specify the silencer grade explicitly, and require a **back-pressure calculation of the complete installed system** against the engine maker's limit as a bid deliverable. Add: independent exhaust support off the engine; certified fire-rated, thermally isolated wall penetration; ≥ 225 mm clearance (or insulated sleeve) to any combustible or cable. *(Owner: Mechanical designer. Closes RED-04.)*

6. **Commission an Elaborat zaštite od požara** by a licensed fire-safety engineer for the container with a 500 l diesel inventory and a running engine, addressing Class B risk, compartmentation, suppression agent and design concentration, and obtain the competent-authority approval required under the *Zakon o zaštiti od požara RS*. **The existing approved assessment covers Class E only, with BONPET ampoules** (`03 ELEKTRO dio.doc` §3.7.2). Add the elaborate as a priced BOQ item. *(Owner: Investor + fire engineer. Closes RED-05.)*

7. **Decide the fundamental question the fire elaborate will force: separate enclosure vs. shared container.** BH Telecom's own approved precedent (MATISA 2008/017BH) used a **dedicated genset container containing no TK equipment**. Given RED-05 (Class B fire), RED-06 (no space), RED-02 (55 °C), RED-14 (noise unachievable) and RED-08 (no compartmentation possible in 6.29 m²), the recommended solution is a **separate acoustic genset enclosure / kiosk sited outside the container**, with the fuel tank in a bunded external position. Re-scope LOT 2 accordingly. *(Owner: Investor. Closes RED-02, RED-05, RED-06, RED-14 simultaneously.)*

8. **Correct BOQ 5.6 (new GRO).** Replace the 3 × 1P C32 with **one 4-pole 40 A MCCB**; add a **4-pole 300 mA S-type RCD** incomer and **30 mA type A RCBOs** on socket and lighting circuits (restoring the protection the certified design already had — Prilog III p.16, "3 polna FID SKLOPKA 40/0,03A"); change the rectifier feed to **3P C25**; relabel selector position 1 from *"hibridni sistem"* to **"VANJSKI/MOBILNI AGREGAT"** and add a mechanically interlocked **63 A 5-pin CEE inlet**; make the isolator 4-pole; add a full circuit schedule; add SPD backup fuses and the ≤ 0.5 m lead-length requirement. Require a **discrimination study** as a bid deliverable. *(Owner: Electrical designer. Closes RED-09, RED-11(a)(b).)*

9. **Specify the earthing system for the island supply.** State **TN-S**, with the alternator star point earthed at **exactly one point** (at the KOA / first distribution point) via ≥ 16 mm² Cu to the site MET. Add a BOQ item and a hold point for **verifying and recording the isolation of the existing PMO PEN bond**, and confirm no second N–PE connection exists downstream. *(Owner: Electrical designer. Closes RED-10.)*

10. **Procure a revision of the certified electrical project (izmjena glavnog projekta)** covering the change from a utility-fed TN-C/S installation with 35 A fuses to a 22 kVA island supply. Sections §3.3.2 (conductor sizing), §3.3.4 (touch voltage), §3.3.5 (short circuit) and §3.3.6 (earth-fault current) of `03 ELEKTRO dio.doc` are all void as written. Add as a priced BOQ item. *(Owner: Investor + original designer. Closes RED-10.)*

11. **Add the missing fire and fuel safety items to BOQ 4.15/4.2**: fire-safe fuel shut-off valve at the tank outlet (fusible link or fail-closed solenoid, tripped by fire alarm and E-STOP); **CO and NO₂ detection**; interlock shutting down the engine, stopping the fan and closing the dampers on suppression discharge; motorised/gravity dampers on both louvres; the type, agent, design concentration and certification of the automatic suppression system; anti-siphon/non-return valve; breather terminal detail (≥ 2 m high, ≥ 3 m from exhaust and intakes, **flame arrestor**); overfill prevention device and drip tray at the fill point; a second extinguisher (5 kg CO₂) with both located outside the door; Class B signage (P003, W021, product and capacity marking). Specify the **E-STOP outside the door** plus one at the KOA, as an ISO 13850 category-0 stop. *(Owner: Electrical + fire designer. Closes RED-08.)*

12. **Correct the surge protection scope.** Upgrade the AC origin SPD to **Type 1+2, I_imp ≥ 12.5 kA (10/350)**; upgrade the PV SPD to **Type 1+2, I_imp ≥ 5 kA (10/350), U_cpv ≥ 425 V**; add a **second DC SPD set at the array junction box**; add **data-line SPDs (EN 61643-21)** on the STP Cat5, the J-Y(ST)Y alarm multicore and the controller RS485/Ethernet; add an SPD on the −48 V feed into the ICC330/MTS9302. **Separate BOQ 5.1 into two trenches** so the DC/power cables are ≥ 0.5 m from the earth tape, as Huawei §4.1.3 requires and as the certified project already did. *(Owner: Electrical designer. Closes RED-12.)*

13. **Replace the H07V-K 25 mm² bonding conductor.** Preferred: continue the **Fe/Zn 25×4 tape** (BOQ 5.3) to each support and terminate on a stainless-steel bolted lug with an above-grade inspection joint, all buried joints encapsulated. Alternative: **bare or burial-rated Cu ≥ 50 mm²** per EN 62305-3 Table 7, with bimetallic connectors. Bond **each support at two points**. Add a continuity hold point (< 0.1 Ω) across the bolted galvanised frame joints, or bonding jumpers. Reconcile item 1.4 with item 5.4. *(Owner: Electrical designer. Closes RED-13.)*

14. **Correct the container floor loading item 4.4.** Delete the assertion that the load *"NE prelazi"* the budget and that strengthening *"se NE očekuje"* — at 1 350 kg the load exceeds 5.0 kN/m² over any area below **2.65 m²**. Make the steel spreader grillage a **mandatory, priced item** designed to distribute over ≥ 2.65 m² onto the container's main floor beams, and apply a dynamic amplification factor (1.2–1.5) per EN 1991-1-1 / ISO 8528-9. *(Owner: Structural engineer. Closes RED-07.)*

15. **Re-draw Prilog III S-02 and add a container general arrangement** showing **all** existing equipment (GRO, UPS, UPS-R, RBS_1, RBS_2, PRENOS, ROS, TZ, MPU, klima, PE1, PE2, trays) to the certified internal dimensions (2.88 × 2.18 m, 6.29 m²), with the proposed skid, tank, bund and service clearances dimensioned, and the north-wall elevation showing the louvres against the Huawei cabinets. *(Owner: Designer. Closes RED-06.)*

16. **Resolve the noise requirement.** Either relax the < 68 dBA at 7 m limit with a documented justification, or add **intake and discharge splitter attenuators** and a **residential-grade exhaust silencer** to the BOQ — and then re-run action 3, because the attenuators consume 100–250 Pa each. Require an **acoustic calculation** as a bid deliverable. *(Owner: Designer. Closes RED-14; strongly favours action 7.)*

### Priority 2 — close before contract award

17. Re-size the AC cable, BOQ 5.5: **NYY-J 5×16 mm²** (5×6 mm² fails at 40 °C and 50 °C ambient — see §4.6 of the calculations), halogen-free, CPR ≥ Cca-s1b,d1,a1, and coordinated with the corrected 40 A outgoing device. *(Y-12 + RED-09.)*
18. Increase the signal cable to **J-Y(ST)Y 10×2×0.6** or migrate non-safety signals to Modbus RTU. *(Y-05.)*
19. Change the duty class to **Prime (PRP) per ISO 8528-1**; quote the datasheet reference conditions (25 °C, 100 m) in item 3.1; require the derating calculation for 1 076 m and 40 °C. *(Y-02, Y-04.)*
20. Add a **minimum-load and anti-wet-stacking regime**: start only with the rectifiers at full programmed current limit (≥ 5.3 kW), minimum run 30 min, quarterly ≥ 50 % load exercise. *(Y-03.)*
21. Resolve the **shunt-excitation conflict**: either delete the "3 × I_n for 10 s" requirement, or require PMG/AREP excitation as a priced item — the named reference set P22-6 is SHUNT-excited (P22-6.pdf p.2). *(RED-09.)*
22. Complete the PVDB specification: DC isolator ≥ 410 V DC, DC-PV2/DC-21B; gPV fuses if fitted; SPD parameters per action 12; **exclude the Huawei PVDB500-15-2B** (15 A/route < 18.0 A design current). *(Y-06.)*
23. Quantify **MC4 connectors (≥ 8 + spares)** and prohibit inter-brand mating per IEC 62852. *(Y-07.)*
24. Reconcile the cable/duct/trench quantities (BOQ 1.5 vs. 5.1 vs. 5.2) against a dimensioned route drawing. *(Y-09.)*
25. State the **earth resistance target numerically** (recommend ≤ 10 Ω per EN 62305-3 §5.4.1; the certified calculation gives 5.91 Ω) and draw the 1.00 m / 0.80 m transition detail. *(Y-10, Y-11.)*
26. Add a BOQ item for **re-terminating the seven existing GRO circuits** onto the new GRO, decommissioning the old board, and reworking the ROS alarm scheme (the "NEST.1.F" mains-failure signal is meaningless off-grid; replace with genset run/fail, low fuel, fuel leak, fire, high room temperature). *(RED-11(d).)*
27. **Declare the LPS class** for the site and record the rolling-sphere verification of G-09 in the tender, noting that EN 62305-3 Table 2 forbids the protective-angle method above h = 20 m and that Huawei's 45° cone (§4.1.3) must not be relied on for a 38 m mast. *(Y-21, G-09.)*
28. Fix the documentation defects: BOQ LOT 2 item numbering and the broken "Tačka 3.1" cross-reference (Y-17); the duplicated "LOT 1" work list in the TD (Y-18); the 200 l / 500 l first-fill contradiction (Y-19); the MTS9302 / ICC330-H1 / PowerCube 1000 naming (Y-20); the enclosure/transfer-panel/"vučna prikolica" residue (Y-16); **delete the Brložki Potok reference** and rely on the corrected item 5.6 (RED-11). Add revision numbers and dates to all Prilog III sheets.
29. Confirm the **bifacial gain** assumption against the iSSU's 4 000 W input limit. *(Y-08.)*
30. Add the ventilation **start-permissive** (damper end-switches / differential-pressure switch to the DSE controller) and AV mount performance requirements. *(Y-13, Y-15.)*
31. Detail the **bund upstand** (220 mm), its low-point locked drain, and confirm no floor penetrations inside it. *(Y-14.)*

---

## 6. LESSONS LEARNED

1. **A reference design is only transferable together with its boundary conditions.** The MATISA 2008 package is a good document and was correctly identified as the precedent — but its ventilation figures were derived for a *dedicated, unoccupied* genset container, and its DN 50 exhaust for a *1.5 l, 13.3 kVA* engine. Copying the numbers into a 2.2 l, 22 kVA set inside a *live TK container* inverted every assumption. Future re-use of reference designs should carry a mandatory "what changed" table: engine displacement, rating, room occupancy, adjacent equipment, and ambient.

2. **"6 air changes per hour" must never appear in a genset specification.** Radiator cooling air is set by the heat balance, not by room volume. For this set the two figures differ by a factor of 35.

3. **The certified as-built project is the authoritative source for what is already in the container** — not the type drawings. The DXF gave the true internal area (6.29 m², 2.88 × 2.18 m) and the existing GRO's 40 A/30 mA RCD, both of which the new tender contradicts. Always read the site-specific set, not just the K3 type set.

4. **Island supplies break MCB-based fault protection.** A 22 kVA alternator delivering 3 × I_n = 95 A cannot trip a C32 MCB. Every off-grid genset installation in this programme should default to an RCD-based fault-protection strategy, and the standard GRO design should be revised accordingly before the next site.

5. **What was done well and should be repeated:** ducting the radiator discharge rather than dumping it into the room; capping the rectifier input power in the controller so it cannot overload the set; starting on battery SoC rather than a phantom mains-failure signal; and specifying both a double-wall tank *and* a 110 % bund. These are the marks of someone who has thought about the problem — the failures are all failures of *quantification*, not of intent.

---

*End of review 03-electrical, Rev. 0, 2026-08-07.*
*Next revision to be issued as a delta review against the corrected tender documents, per prompt.md §6.*
