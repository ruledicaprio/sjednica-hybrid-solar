# Consolidated calculations — BS Sjednica (Bileća)

Rev 1 · 2026-08-07 · Rusmir Skopljak, dipl. ing. el.

Every calculation performed during the review, in one place, **including those that did
not end up driving the issued documents**. Each carries its inputs, its source, and a
note on whether it governs. Intended as the permanent working reference for this site.

**Site constants used throughout**

| | |
|---|---|
| Location | BS Sjednica, Bileća, Republika Srpska · 42,9448° N, 18,3236° E |
| Altitude | 1076 m a.s.l. |
| Grid | **none** — off-grid, genset is the only AC source |
| Load | 1180 W nominal / 1330 W max at −48 V DC |
| Leased plot | ≈150 m² (16,00 × 9,40 m); fenced compound 5,50 × 5,50 m; slab 5,40 × 5,40 m |
| Fence height | 1,90 m |
| Tower | lattice, h = 38 m, base 4,20 × 4,20 m |
| Container | 3005 × 2300 mm external, 60 mm walls, **empty** |

---

## A. Environmental / ambient

### A.1 Air density vs altitude and temperature

Barometric: `p = 101325·(1 − 2,25577·10⁻⁵·h)^5,25588`, then `ρ = p / (287,05·T)`.

| Condition | p | ρ |
|---|---|---|
| 0 m, +25 °C (datasheet reference) | 101,3 kPa | **1,184 kg/m³** |
| 1076 m, +25 °C | 89,0 kPa | **1,040 kg/m³** |
| 1076 m, −10 °C | 89,0 kPa | 1,179 kg/m³ |
| 1076 m, +40 °C | 89,0 kPa | 0,991 kg/m³ |
| 1076 m, wind calc (per certified sheet) | — | 1,0904 kg/m³ |

**Governs:** genset cooling derate (A.2), wind pressure (B.1), exhaust density (C.6).

### A.2 Altitude derate on genset cooling

A radiator fan is a constant-**volume** device, so at altitude it moves the same m³/h
but less mass. Mass-flow deficit at 1076 m vs the datasheet's 100 m reference:

`1 − 1,040/1,184 = 12 %` (8 % if referenced to the wind sheet's 1,0904 kg/m³)

To restore the reference mass flow, volumetric demand rises to
`1980 × 1,184/1,090 ≈ 2151 m³/h`. Used as the sizing flow in C.1.

**Note:** FG Wilson rate the set for ambients to 50 °C and offer site-specific ratings;
at 1076 m and 22 kVA standby the derate is small but the **contractor must confirm the
rating at site conditions** — this is a tender requirement, not an assumption.

### A.3 Snow — computed, then set aside

BAS EN 1991-1-3 with the BiH National Annex would give a substantial ground snow load at
1076 m, and the construction review used it to argue against a low support with a
+0,50 m bottom edge.

**Does not govern.** The Investor's site knowledge is that snow does not accumulate here,
which is physically consistent: an exposed Adriatic-facing Herzegovinian peak in the bura
belt, with gusts to 45 m/s, is wind-scoured. A regional map value does not describe a
site the wind sweeps clean. Retained here for completeness and because a *code* check
still has to appear in the bidder's certified calculation even where site experience says
it is not the governing case. See `05-site-corrections.md` §C-2.

### A.4 Freeze–thaw exposure — **a gap in the tendered BOQ**

At 1076 m the foundations undergo repeated freeze–thaw while wet. BOQ item 2.3 specifies
concrete class **C25** but **no exposure class**. Per EN 206 / BAS EN 206 this site is
**XF3** (high water saturation, no de-icing agent), which requires air-entrained concrete
and a minimum strength class typically **C30/37**, not C25.

**Recommendation:** specify `C30/37, XC4 + XF3, Dmax 16, S3, air-entrained 4–6 %` and
cover ≥50 mm. Not yet incorporated — see §F.

### A.5 Solar geometry and December capture

Solar noon altitude `= 90 − φ + δ`, φ = 42,9448°.

| Date | δ | Noon altitude | Tilt for normal incidence |
|---|---|---|---|
| 21 Dec | −23,44° | **23,6°** | 66,4° |
| 21 Mar / Sep | 0° | 47,1° | 42,9° |
| 21 Jun | +23,44° | 70,5° | 19,5° |

Fraction of normal-incidence beam captured at solar noon on 21 December,
`cos(|alt − (90 − tilt)|)`:

| Tilt | Incidence | cos | December beam captured |
|---|---|---|---|
| 15° | 51,4° | 0,624 | 62 % |
| 25° | 41,4° | 0,750 | 75 % |
| 35° | 31,4° | 0,854 | 85 % |
| **45° (chosen)** | **21,4°** | **0,931** | **93 %** |
| 55° | 11,4° | 0,980 | 98 % |

**Conclusion — this is why 45° stays.** The winter optimum here is ≈ φ + 10…15 = **53–58°**,
so 45° is already *below* the December optimum, not above it. Dropping to 35° would cost
about 8 % of December yield on a site whose **December is the deficit month**. The annual
figure is irrelevant to sizing an off-grid store; the worst month is. Retained tilt: **45°**.

### A.6 Yield and the December deficit

From `01-huawei-solar.md`, corrected (the referenced simulation implied ~17 782 kWh/kWp,
about 12× physically impossible, and was discarded):

| | |
|---|---|
| POA irradiation at 45°, south | 1800–1930 kWh/m²·yr |
| Array | 12 × 585 Wp = **7,02 kWp** |
| Performance ratio assumed | 0,80 |
| **Annual yield** | **10,1–10,9 MWh** |
| **December yield** | **560–600 kWh** |
| **December load** | 1,180 kW × 24 × 31 = **878 kWh** |
| **December deficit** | **280–320 kWh (32–36 %)** |
| Genset duty | ≈1,2–2,1 MWh/yr → **110–190 h/yr**, inside the 250 h/yr allowance |

**The genset is structurally necessary, not a formality**, and December is what sets its
duty. This is the quantitative backing for A.5.

---

## B. Structural / mechanical — PV support

### B.1 Design wind pressure

Two independent routes from the Investor's own archive, plus a code check:

| Source | Value |
|---|---|
| Certified BS Sjednica project (`proračun vjetra JUS EXCEL.xlsx`, `04 AG dio.docx`) | v_m,50,10 = 35,0 m/s; k_T = 0,92 → 32,2 m/s mean; **q ≈ 1,20 kN/m²** |
| BH Telecom type-container brief | **1,10 kN/m²** on exposed structures ≤10 m, all BiH ≤1500 m |
| EN 1991-1-4 first principles with orography | reproduces the certified value to within 0,5 % |

**Adopted: q_p = 1,20 kN/m², equivalent to a ≈45 m/s 3-second gust** at ρ = 1,0904 kg/m³.

### B.2 Catalogue support capacity — why no standard tilt works

Manufacturer rating (PV Module Solution User Manual Table 3-29; GroundSupport_drawing p.3),
converted with `q = ½ρv²` at ρ = 1,0904:

| Tilt | Rated 3 s gust | Capacity | % of 1,20 kN/m² | Shortfall |
|---|---|---|---|---|
| 15° / 25° | 40 m/s | 0,87 kN/m² | 73 % | **+38 % needed** |
| 35° | 35 m/s | 0,67 kN/m² | 56 % | +80 % needed |
| **45°** | **31 m/s** | **0,52 kN/m²** | **44 %** | **+129 % needed** |

**No catalogue tilt is compliant.** Tilt selection cannot solve this — only a
site-specific structure can. See §F for the recommended tender treatment.

### B.3 Panel field geometry (corrected)

585 W module 2278 × 1134 × 30 mm; crossbeam 4089 mm; long-side margin 306,5 mm;
6 modules as 2 rows × 3 columns, portrait.

| | |
|---|---|
| Field width | 4089 − 2 × 306,5 = **3476 mm** |
| Field slope length | 2 × 2278 + 20 = **4576 mm** |
| Horizontal projection at 45° | 4576 · cos45 = **3236 mm** |
| Rise | 4576 · sin45 = **3236 mm** |
| Bottom edge | +0,50 m |
| **Top edge** | **+3,74 m** |
| **Above fence (1,90 m)** | **1,84 m** |
| Sail area per support | 3,476 × 4,576 = **15,91 m²** |

The tender previously derived the projection from the 3656 mm *longitudinal beam*
(→ 2590 mm, top edge +3,09 m). That is the beam, not the module field. Error 650 mm.

### B.4 Site fit at 45°

| | |
|---|---|
| Run from bottom edge to fence height | (1900 − 500)/tan45 = **1400 mm** |
| South strip available | (9400 − 5500)/2 = **1950 mm** |
| **Verdict** | **fits, 550 mm spare** — foundations stay outside the fence |
| Oversail above the fence | 3236 − 1400 = **1836 mm** |
| Panel underside at the container face | **+3,50 m** vs container height 2,40–2,80 m → **clears** |
| East/west strips (alternative) | 5250 mm each — 2014 mm spare if relocation is ever wanted |

### B.5 Wind actions per support at 45°

Net force coefficient for a free-standing inclined panel, EN 1991-1-4 §7.3 (canopy
roofs), taken as **c_f = 1,5** — to be confirmed by the bidder's engineer.

```
F  = c_f · q_p · A = 1,5 × 1,20 × 15,91         = 28,6 kN normal to the panel
Fv = F · cos45                                   = 20,2 kN  (uplift)
Fh = F · sin45                                   = 20,2 kN  (horizontal)
G  = (154 kg frame + 6 × 32 kg modules) · 9,81   =  3,4 kN  (favourable)

ULS uplift  = 1,5 · Fv − 0,9 · G = 30,3 − 3,1    = 27,3 kN per support
centroid    = 0,50 + (4,576/2)·sin45             =  2,12 m
overturning = 1,5 · Fh · 2,12                     = 64,3 kNm
couple over 2,60 m strip spacing                  = 24,7 kN per strip
```

### B.6 Foundation adequacy — the tendered design fails

| Option | Requirement | Tendered | Verdict |
|---|---|---|---|
| Gravity only | 27,3/24 = **1,14 m³** concrete per support | 2 × 0,407 = **0,81 m³** | **40 % short** |
| Rock anchors | 27,3 kN over 2 strips = 13,7 kN/strip | none specified | see below |

**Rock anchors are the better answer here.** The ground is karst limestone; the BOQ
itself calls it *kamenito tlo*. A resin-bonded M16–M20 anchor into sound limestone
develops 30–60 kN characteristic pull-out — so **2 anchors per strip, 4 per support**
(minimum 2 per strip for redundancy, not 1 as the arithmetic alone would allow) covers
27,3 kN with large margin, at a fraction of the cost of 0,33 m³ of extra concrete per
support. **Anchor capacity must be proven by site pull-out test.**

### B.7 Container floor and access (from the FG Wilson data sheet)

| | Mass | Footprint | Pressure |
|---|---|---|---|
| Genset, wet | 385 kg | 1,550 × 0,620 = 0,96 m² | **3,93 kN/m²** |
| Tank, 500 l full | ≈500 kg | 1,20 × 0,70 = 0,84 m² | **5,84 kN/m²** |
| Combined | **885 kg** | | |

Container brief states 10,00 kN/m²; the construction review disputes it and derives
2,00 kN/m². **Both point loads must be checked against the real capacity** — but the
loads are modest and far below the 1350 kg the electrical review had assumed. A spreader
grillage under the skid rails remains a sensible recommendation.

**Access:** skid **620 mm** wide through a **900 mm** door = 280 mm clearance; 1020 mm
high against a 2000 mm door. **It goes in through the existing opening.** No roof-panel
removal, wall opening or split delivery.

---

## C. Mechanical — genset installation

All from the FG Wilson P22-6 (Skid) data sheet, 2019-08-14, **50 Hz standby**.

### C.1 Cooling air

| | |
|---|---|
| Radiator airflow (manufacturer) | **1980 m³/h** (33 m³/min) |
| Site-derated sizing flow (A.2) | **2151 m³/h** |
| Max external restriction | **125 Pa** ← the real design constraint |
| Combustion air | 90 m³/h (1,5 m³/min), max intake restriction 3 kPa |

Louvre pressure drop, `Δp = ½ρv²·K` with K ≈ 2,5 and ρ = 1,09, 50 % free area:

| Element | Gross | Free | v | Δp |
|---|---|---|---|---|
| Intake 500 × 700 (tendered) | 0,35 m² | 0,175 m² | 3,4 m/s | **≈16 Pa** |
| Discharge 600 × 600 (tendered) | 0,36 m² | 0,180 m² | 3,3 m/s | **≈15 Pa** |
| Duct ≈6 m² sheet metal | — | — | — | ≈20–40 Pa |
| **Total** | | | | **≈50–70 Pa vs 125 Pa — PASSES** |

**The tendered arrangement is adequate.** The electrical review's demand for
1200 × 800 / 900 × 800 rested on an estimated 4250 m³/h — 2,1× the manufacturer figure.

### C.2 Heat balance in the container

```
heat to water + lube oil      19,6 kW  -> removed by the radiator, ducted out
heat radiated to room          7,1 kW  -> removed by the same swept air
ΔT across radiator = 19600/(0,550 · 1,09 · 1005)      = 32,5 K   (normal)
room ΔT if swept   =  7100/(0,550 · 1,09 · 1005)      = 11,8 K
```

Room reaches ≈37 °C at 25 °C ambient — inside the engine's 50 °C rating, and with the
container **empty** there is no telecom equipment to derate.

### C.3 Supplementary room fan

BOQ item 4.9: axial fan **1200 m³/h**, Ø315, thermostat, interlocked to genset start;
stated room minimum **120 m³/h = 6 air changes/h**. This is **room ventilation, not the
cooling path** — the radiator's own fan drives the 1980 m³/h through the duct. Correct
as specified; the review's "3,5× short" and "35× short" both misread the roles.

### C.4 Exhaust

| | |
|---|---|
| Gas flow, standby | 234 m³/h (3,9 m³/min) |
| Gas temperature | **505 °C** |
| Gas density at 505 °C | 353/(505+273) = **0,454 kg/m³** |
| **Max allowable back pressure** | **10,2 kPa** |

| DN | Area | Velocity | Pipe Δp (6 m) | + industrial silencer | vs 10,2 kPa |
|---|---|---|---|---|---|
| **50 (tendered)** | 19,6 cm² | **33,1 m/s** | ≈600 Pa | ≈2,6 kPa | **passes, ~4× margin** |
| **65 (recommended)** | 33,2 cm² | 19,6 m/s | ≈160 Pa | ≈2,2 kPa | passes |
| 80 | 50,3 cm² | 12,9 m/s | ≈60 Pa | ≈2,1 kPa | passes |

DN 50 is **compliant on back pressure**; the only reservation is velocity above the
customary ≤30 m/s for noise and erosion. **DN 65 is a recommendation, not a correction.**

### C.5 Fuel

| | |
|---|---|
| Consumption, 100 % standby | 5,9 l/h |
| **Autonomy on 500 l** | **≈85 h** |
| At the 250 h/yr allowance | ≈1475 l/yr → ~3 fills |

Cross-check against A.6: 110–190 h/yr expected duty → 650–1120 l/yr. **Consistent**, and
500 l gives a comfortable margin between visits.

---

## D. Electrical

### D.1 PV string

| | |
|---|---|
| 6 × iPV585-M2A | Voc **309,3 V**, Vmp **256,7 V**, Imp 13,67 A, Isc 14,40 A |
| iSSU S4875G2 window | 85–435 V DC, max 25 A, max 4000 W |
| Check | 257 V ✓ · 13,67 A ✓ · 3510 W ✓ |
| Optimizer SUN2000-600W-P | Vout 0–80 V, **Iout max 15 A** → 13,67 A ✓ |
| PVDB500-15-2B | 100–500 V, **max 15 A per route**, 2 routes → 1 string per route ✓ |
| Huawei string rule | iPV540/585/630: **3–12 modules per string** → 6 ✓ |

**Note:** the iSSU connects **only** to iPV (optimizer-equipped) modules. Plain 585 W
modules would require an SSU S4875G6 and a different string rule (3–7 per string below
−10 °C ambient). The tender must not leave this open.

### D.2 DC cabling

```
6 mm² Cu, 25 m one way, Imp 13,67 A
ΔV = 2 · 25 · 13,67 · 0,0175 / 6 = 1,99 V = 0,78 % of 257 V     OK (<1 %)
```

Cross-section is generous; **the constraint is the terminal, not the cable** — the iSSU
input terminal requires **exactly 4 mm²**, so a transition is needed at the cabinet.
BOQ item 1.5 now says so.

### D.3 DC load

| | at 53,5 V float | at 48,0 V |
|---|---|---|
| 1180 W nominal | 22,1 A | 24,6 A |
| 1330 W maximum | 24,9 A | 27,7 A |

Annual 10 337 kWh; December 878 kWh (feeds A.6).

### D.4 Genset AC and protection — excitation is the root cause

```
In = 22000 / (√3 · 400) = 31,75 A
```

The data sheet prints **Short Circuit Capacity 0 %** with the footnote
*"** With optional independant excitation system (PMG / AUX winding)"* — i.e. the
sustained short-circuit capability requires the **optional** independent excitation,
which this set does not have as standard. Its excitation is **SHUNT** (p.4).

**Why shunt gives nothing to trip on.** Shunt excitation draws field power from the
machine's own terminals through the AVR. On a fault the terminal voltage collapses, so
the field loses its power source and decays. The current profile follows the reactances
printed on the same page:

| Stage | Reactance | Current | × In | Duration |
|---|---|---|---|---|
| Subtransient | X″d = 0,078 | **407 A** | 12,8 | ~10–20 ms |
| Transient | X′d = 0,155 | **205 A** | 6,5 | ~100 ms, decaying |
| **Sustained** | Xd = 1,938 | **16,4 A** | **0,5** | indefinite |

The sustained value is **below rated current**. That is the physical meaning of "0 %":
not zero current at the instant of fault, but **no sustained overcurrent** — nothing an
overcurrent device can grade against. A C32 MCB (magnetic band 160–320 A) may or may not
catch the first cycle depending on fault impedance and point-on-wave; nothing holds it
in for the 0,4 s that IEC 60364-4-41 Table 41.1 requires, and remote or impedant faults
never reach the band at all.

**With PMG or AREP/AUX excitation**, the field is fed independently of terminal voltage,
so the machine sustains **3 × In ≈ 95 A for 10 s** per ISO 8528-3 — above the magnetic
band and long enough for both tripping and discrimination. This is the customary
specification and the correct fix at source.

**Adopted requirement (both, not either):**

1. **Independent excitation — PMG or AREP/AUX — with ≥3 × In sustained for ≥10 s.**
   Written into BOQ LOT 2 (alternator specification) and Prilog I §4.1. On this model it
   is a listed option; the Leroy Somer alternator option provides it.
2. **RCD retained** — 4p 63 A/300 mA S-type plus 2 × RCBO 30 mA type A. Earth faults on
   an island TN-S supply are not reliably cleared by overcurrent even with PMG, and the
   certified project already had a 40 A/30 mA RCD that had been deleted.

Earthing system for the island supply (TN-S) must be defined: the N–PE bond belongs in
the **new GRO**, not the existing PMO whose utility source no longer exists.

### D.5 Earthing and lightning

| | |
|---|---|
| Required conductor | **Cu 50 mm²** per EN 62305-3 Table 7 for lightning-current duty |
| Tendered originally | H07V-K 25 mm² — indoor conduit wire, non-UV, non-burial, undersized |
| Ring earth | existing Fe/Zn 25 × 4 mm — **bimetallic Cu/Fe-Zn joints required** against galvanic corrosion |
| Target resistance | **≤10 Ω** (Huawei §4.1.5) |
| Cable-to-down-conductor separation | **≥0,5 m** (Huawei §4.1.3); BOQ's single 0,40 m trench breaches it |
| PV arrays vs tower protection zone | **inside** the rolling-sphere zone at every LPL (7,5 m actual vs 10,68 m protected radius at LPL I) → **no extra air terminations needed** |

### D.6 Surge protection

The site has an external LPS with separation deliberately not maintained, so
**Type 1 (10/350) is required** at the AC origin, not Type 2 alone. Required set:

- AC origin: **Type 1 + 2**
- DC, per string: Type 2 — at the PVDB **and** a second set at the array (25 m run)
- **Data lines: currently missing entirely** on a 38 m-tower site

---

## E. Summary — what governs what

| Decision | Governed by | Value |
|---|---|---|
| Tilt = **45°** | December capture (A.5, A.6) | 93 % of noon beam vs 85 % at 35° |
| Structure must be site-specific | Wind (B.1, B.2) | 1,20 kN/m² vs 0,52 kN/m² catalogue |
| Foundation type | Uplift (B.5, B.6) | 27,3 kN → rock anchors, not gravity |
| Concrete class | Freeze–thaw (A.4) | C30/37 XF3, **not** the tendered C25 |
| Louvre sizes | Manufacturer restriction (C.1) | tendered sizes adequate, 125 Pa budget |
| Exhaust DN | Velocity, not back pressure (C.4) | DN 50 passes; DN 65 recommended |
| Genset presence | December deficit (A.6) | 280–320 kWh short — genset necessary |
| Generator excitation | Fault clearing (D.4) | PMG/AREP, 3 × In for 10 s — shunt gives 0,5 × In sustained |
| RCD in GRO | Island TN-S earth faults (D.4) | mandatory as second level |
| Earth conductor | EN 62305-3 (D.5) | Cu 50 mm², bimetallic joints |

---

## F. Recommended tender treatment of the PV structure

Answering the Investor's proposal directly: **yes — specify foundation, anchoring,
profiles and material quality so the item is BOQ-quantifiable, and keep 45°.**

The reason this works is that the failure is *not* in the concept but in the product
selection. A 45° array at this site is a perfectly ordinary steel structure; it is simply
not the catalogue kit, which is rated for 0,52 kN/m². Specifying performance **and** the
material/section framework lets a local fabricator price and build it, keeps the bid
comparable line by line, and keeps the December yield.

### F.1 State the design actions, not just the pressure

Put these in the BOQ so no bidder can quietly design to a softer load:

| Parameter | Value |
|---|---|
| Peak velocity pressure | **q_p ≥ 1,20 kN/m²** (3 s gust ≈45 m/s), BAS EN 1991-1-4 + BiH NA |
| Terrain / orography | exposed hilltop, ≥1076 m — orography factor to be applied |
| Net force coefficient | per EN 1991-1-4 §7.3, **c_f ≥ 1,5** at 45° unless justified |
| **Design uplift per support** | **≥27 kN** (ULS, γ_Q = 1,5, γ_G,fav = 0,9) |
| **Design horizontal per support** | **≥30 kN** (ULS) |
| **Design overturning per support** | **≥64 kNm** (ULS) |
| Snow | BAS EN 1991-1-3 + BiH NA at 1076 m (check required even if not governing) |
| Ice | radial rime 20 mm at 300 kg/m³ (exposed peak) |
| Seismic | BAS EN 1998-1, to be confirmed for the zone |

### F.2 Material and fabrication — quantifiable

| Item | Specification |
|---|---|
| Structural steel | **S275JR** minimum to EN 10025-2 (S355JR preferred for the posts) |
| Sections | hollow sections to EN 10219; posts **min. RHS 80 × 80 × 4**, rails **min. RHS 60 × 40 × 3** — *or* any section proven by calculation to give ≥ the same section modulus |
| Corrosion protection | **hot-dip galvanised to EN ISO 1461, min. 70 µm** local / 85 µm mean (C4 environment) |
| Welding | EN 1090-2, **EXC2**; welders qualified to EN ISO 9606-1; WPS to EN ISO 15614 |
| CE marking | EN 1090-1 declaration of performance |
| Structural bolts | **M16 class 8.8**, galvanised, to EN 15048 (SB) |
| Module fixings | **A2/A4 stainless** |
| Anti-theft | anti-theft nuts on module clamps |

### F.3 Anchoring — the item that actually carries the load

| Item | Specification |
|---|---|
| Type | **resin-bonded (chemical) anchors into rock**, M16 or M20, galvanised or A4 |
| Quantity | **min. 2 per foundation strip, 4 per support** (redundancy — not the 1 the arithmetic alone allows) |
| Capacity | **≥30 kN characteristic pull-out each**, embedment per ETA in C20/25 or sound limestone |
| Proof | **site pull-out test on ≥10 % of anchors**, minimum 2 per support, to 1,5 × design load, witnessed by the supervising engineer |
| Alternative | cast-in U-bolts M16/320 as per the manufacturer drawing **only if** the gravity foundation is enlarged to ≥1,14 m³/support |

### F.4 Foundations

| Item | Specification |
|---|---|
| Concrete | **C30/37, exposure XC4 + XF3**, air-entrained 4–6 %, Dmax 16, S3 |
| Blinding | C12/15, 50 mm |
| Reinforcement | **B500B**, cover **≥50 mm** |
| Geometry | 2 strips per support, min. 450 mm wide × 3300 long, **depth per calculation** (≥900 mm), spacing 2600 mm, N–S |
| Bearing | f_ak ≥ 100 kPa to be confirmed on site; rock excavation cat. IV–V |
| Frost depth | founding level below local frost line — **to be stated by the bidder for 1076 m** |

### F.5 Make it a qualification requirement, not a deliverable

The single most valuable change: move the static calculation from BOQ item 1.3
(post-award deliverable) into TD §6.1 (documents that must accompany the **offer**).
Under a lowest-price award, anything checked after award is checked too late.

Require **with the offer**: calculation signed by a licensed engineer to the actions in
F.1; fabrication drawings; EN 1090-1 DoP; galvanising and material certificates; and —
because Huawei's own drawing says *"in some particular scene, such as island and mountain
peak, site designer should recheck the foundation design"* — **written manufacturer
confirmation for this specific site** if a catalogue product is offered.

### F.6 Optional: reduce the sail per structure

Not required, but worth pricing as an alternative: **3 supports × 4 modules** instead of
2 × 6 halves the sail per structure (15,91 → 7,95 m²) and roughly halves the uplift and
overturning per foundation, for the same 12 modules and 7,02 kWp. Three smaller
structures are markedly easier and cheaper to make compliant at 45°, and the plot has
room. Cost: one extra foundation pair and anchor set.

---

## G. Items still open

| # | Item | Owner |
|---|---|---|
| 1 | Certified static calculation for 45° at q_p ≥ 1,20 kN/m² | bidder, pre-award |
| 2 | Concrete exposure class XF3 / C30/37 not yet in the BOQ (A.4) | Investor |
| 3 | Container floor capacity — real value, 10,00 vs 2,00 kN/m² (B.7) | Investor / structural |
| 4 | RCD reinstated and PMG/AREP excitation specified; island-supply earthing defined (D.4) | Investor / electrical |
| 5 | Fire elaborate, detection, fire-safe fuel shut-off, bunding for 500 l | Investor |
| 6 | Type 1 AC SPD and data-line SPDs not in the BOQ (D.6) | Investor |
| 7 | Which power system is actually installed — MTS9302 / ICC330-H1 / PowerCube 1000 / ICC360-HA1-C1 all appear | Investor |
| 8 | Revision of the certified electrical project (its PMO source no longer exists) | Investor |
| 9 | **Tower obstruction lighting (signalna rasvjeta prepreke) is not specified anywhere in this package** — 0 mentions in the TD and the BOQ. On a 38 m tower it is likely present and is a *continuous night load*. If it is not inside the 1180 W figure, the December deficit in A.6 is understated: 4 h/night average over December at even 30 W adds ≈4 kWh/month, at 100 W ≈12 kWh/month, and the aviation supply may also require its own monitored circuit. Verify the actual load and its supply arrangement from the certified electrical project before the tender is issued. | Investor / electrical |

---

*End of consolidated calculations — Rev 1, 2026-08-07.*
