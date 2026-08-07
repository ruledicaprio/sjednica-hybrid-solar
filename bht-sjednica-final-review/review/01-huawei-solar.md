# Review 01 — Huawei PV / Solar Scope
## Tender: "Infrastruktura i instalacija opreme za autonomni hibridni sistem napajanja Sjednica, Bileća (LOT 1 i 2)"

| | |
|---|---|
| **Reviewer discipline** | Huawei telecom-site solar power (PV modules, supports, SJB/PVDB, solar supply modules, DC architecture, yield) |
| **Review revision / date** | Rev 01 — 2026-08-07 |
| **Documents under review** | `TD-OUTPUT/3.1 PRILOG II TD - predmjer Sjednica Bileca.xlsx` (sheets LOT 1 / LOT 2); `TD-OUTPUT/3. TD JN Hibridni sistem napajanja BS Sjednica.docx` (11 pp. as converted); `TD-OUTPUT/Prilog_III_situacija_sjednica_bileca.pdf` (34 pp.) |
| **Reference documents used** | Huawei *PV Module Solution User Manual*, Issue 07 (2026-07-20), 340 pp. [cited as **PVM**, PDF page / printed page]; *GroundSupport_drawing.pdf* (44 pp., contains Huawei *PV Module Support (Standard A-Shaped Support 3.0) Quick Guide*, Issue 01, 2022-04-30, part numbers 21540480/21540481) [**GSD**]; *iSitePower-A V100R023C10 User Manual (ICC330-H1-C6/-C8, ESC330-D9)*, Issue 09 (2026-04-20) [**ISP**]; *【GA】Outdoor Equipment Cabinet ICC330-H1* datasheet (2020-10-21) [**GA-ICC330**]; *【GA】iSSU S4875G2 Datasheet* (2026-01-15) [**GA-iSSU**]; *PowerCube 1000 Installation Guide (Orange, Egypt, ICC360-HA1-C1)*, Issue 01 (2021-02-25) [**PC1000**]; `iSitePower for Sjednica_…_BOQ.xlsx` and `…_BOQ_v2.xlsx` [**HW-BOQ**]; `rural-star-sjednica/output/report_results/RuralStar_Sjednica_FINAL_REPORT.pdf` [**RS-REP**] |
| **Scope limitation** | This review covers the PV scope only. Site wind speed, snow load, Eurocode verification of the support and its foundations, and the genset/mechanical scope are covered by separate reviews. Where a finding depends on the site wind speed, this review supplies the **yield side** of the trade-off only. |

---

## 1. Executive Summary

**Risk Level: HIGH**

**Key conclusion:** The PV scope is built on a correct product family (Huawei Standard A-shaped Support 3.0 + iPV585-M2A + PVDB500-15-2B + iSSU S4875G2) but is specified without a single Huawei BOM number, its panel-field geometry is arithmetically wrong by **+650 mm of horizontal projection and +0.65 m of top-edge height (+21 %)** because the 3656 mm longitudinal beam was mistaken for the module field length, and the power system named on the drawings (ICC330-H1 + MTS9302) contradicts the Huawei quotation actually on file (**ICC360-HA1-C1 with 12 × iPV540-M1A, not 585 Wp**). The yield statement is not defensible: the *scaling factor* 585/540 is sound, but the base simulation it scales (**RS-REP: 115,582 kWh/yr from 6.5 kWp = 17,782 kWh/kWp**) is physically impossible.

---

## 2. Information Extraction Table (ground truth)

### 2.1 Site and load

| Item | Value | Source |
|---|---|---|
| Location | BS Sjednica, Bileća, RS, BiH | Prilog III p.1–2 |
| Coordinates | 42.9448° N, 18.3236° E | Prilog III p.2 |
| Altitude | 1076 m a.s.l. | Prilog III p.2; TD p.3 |
| Leased plot | ≈150 m² (16.00 × 9.40 m) | Prilog III p.2, p.4 (S-02) |
| Existing RC slab | 5.40 × 5.40 m, fence h = 1.90 m | Prilog III p.2, p.3 (S-01) |
| Tower | Lattice, h = 38 m, base 4.20 × 4.20 m | Prilog III p.2 |
| Grid connection | **None** | Prilog III p.2; TD p.3 |
| Load | **1180 W nominal / 1330 W max, −48 VDC** (= 24.6 A / 27.7 A) | Prilog III p.2 |
| Annual load energy | 1.180 kW × 8760 h = **10,337 kWh/yr**; December = **878 kWh** | derived |

### 2.2 PV configuration as tendered

| Item | Tender value | Source |
|---|---|---|
| Supports | 2 × "A-izvedba, NISKA (Standard A-Shaped Support — LOW SUPPORT)", **no BOM number** | BOQ LOT 1 item 1.1 (cells B12–B13) |
| Modules | 12 × 585 Wp = **7.02 kWp**, "Huawei iPV585-M2A ili ekvivalent", 6 per support | BOQ LOT 1 B18–B19; Prilog III p.2, p.4 |
| Module technology claim | "**bifacijalni**" | Prilog III p.2 |
| Tilt / azimuth | Fixed 45°, azimuth 180° (South) | BOQ LOT 1 B20–B21; Prilog III p.4, p.5 |
| Claimed array envelope | 4089 mm (width) × **2590 mm** (horizontal projection at 45°) | BOQ LOT 1 B23 |
| Claimed edge levels | bottom **+0.50 m**, top **+3.09 m** | BOQ LOT 1 B23; Prilog III p.5 (S-03) |
| Claimed fence overshoot | "cca 0.20 m" (BOQ, S-02) / "**0.17 m**" (S-03 dimension) | BOQ LOT 1 B24; Prilog III p.4, p.5 |
| N–S extent on plan | **3.22 m** (dimension on S-02, PV-2) | Prilog III p.4 |
| Component list | horizontal beam 4089×4, longitudinal beam 3656×2, reinforced beam 2986×1, long raking strut 2165×2, column 1862×4, short raking strut 1321×2, column brackets ×4, anchor brackets ×8, 9+9 clamps (incl. 1 spare each), M12×100 ×15, M12×140 ×19 | BOQ LOT 1 B15–B18; Prilog III p.27 (FN-05) |
| Anchors | U-bolt M16, L = 320 mm, legs @ 180 mm, plates 50×50 mm, double nuts, 2 groups per strip @ 1800 mm | BOQ LOT 1 items 1.2 (B30–B31) |
| Foundations | 2 strips/support: 450 mm wide (550 at base) × 3300 long × 900 deep, C25 on C10 cushion, Ø10 / 335 MPa, 19.53 kg/strip, cover 50 mm, spacing 2600 mm | BOQ LOT 1 item 2.3 (B44) |
| Support earthing | H07V-K 25 mm² Y/G to existing ring earth, 2 kpl | BOQ LOT 1 item 1.4 |
| DC string cable | 1×6 mm² H1Z2Z2-K, MC4, **100 m** (2 supports × 2 × 25.00 m) | BOQ LOT 1 item 1.5 |
| PV combiner | generic "PVDB ormar sa DC rastavljačem, osiguračima i odvodnikom prenapona DC (tip 2), **IP65**", 1 kpl | BOQ LOT 1 item 1.6 |
| Power system named | "Huawei MTS9302 … ili drugi kompatibilan sistem" | TD p.4 |
| Power system on drawings | "postojeći vanjski ormari … **Huawei ICC330-H1 (outdoor) + MTS9302**" | Prilog III p.3 (S-01), p.4 (S-02) |
| Power system in BOQ LOT 2 | "ispravljački sistem (**Huawei PowerCube 1000**)", "3 × R4875G5 = 12 kW", "modul GIM01C1", "AC ulazni modul AIU03" | BOQ LOT 2 items 5.6 (B103, B110), 5.7 (B116), 1.1 (B41–B43) |

### 2.3 Huawei manufacturer ground truth

| Item | Value | Source |
|---|---|---|
| **585 W PV module (52240406/52240407)** | 585 W; **2278 × 1134 × 30 mm**; 32.0 / 32.1 kg; η 22.6 %; Vmp 42.79 / 43.88 V; Imp 13.67 / 13.33 A; **Voc 51.55 / 52.42 V**; Isc 14.40 / 14.07 A; Vsys 1500 V; −40…+85 °C; IP68; monocrystalline (**no bifacial statement**) | PVM p.43 (printed 32), Table 3-5 |
| **iPV585-M2A (52240385/52240386)** | Same 585 W module + PV optimizer **SUN2000-600W-P (02314PAJ)**; identical electrical/mechanical data | PVM p.60–61 (49–50), Table 3-17 |
| SUN2000-600W-P optimizer | Rated PV 600 W, max PV 630 W, Vin max 80 V, MPPT 10–80 V, Isc max 14.5 A, **Iout max 15 A**, Vout 0–80 V, MC4, IP68 | PVM p.62–63 (51–52), Table 3-18 |
| iPV540-M1A (52240289) | 540 W, **2279 × 1134 × 35 mm** | HW-BOQ sheet `L3-iSitePower-A` |
| **A-shaped support 21540421 / 21540424** | Applicable modules **280 W / 300 W / 335 W / 445 W; iPV375-M1A / iPV400-M1A only** | PVM p.70–71 (59–60), Table 3-23 |
| **Standard A-shaped support 2.0, 21540460 / 21540461** | Table 3-24 states **280 / 300 / 335 / 445 W; iPV375-M1A / iPV400-M1A** — i.e. **not 585 W** (contradicts Table 2-1, see F-13) | PVM p.72–73 (61–62), Table 3-24 |
| **Standard A-shaped support 3.0, 21540481 (low) / 21540480 (high)** | Weight 154 kg (low) / 227 kg (high); **280/300/335/445/535/540/585 W; iPV375/iPV400/iPV540-M1A/iPV585-M2A**; tilts 15/25/35/45°; Class C; **1–6 modules per support**; anchor bolt **21540482**, antitheft nut **21540036**, antitheft nut wrench **21540038** | PVM p.80–81 (69–70), Table 3-29 |
| Wind resistance (all A-shaped families, 3-second gust) | **15° / 25° → 40 m/s; 35° → 35 m/s; 45° → 31 m/s** | PVM p.80 (69), Table 3-29; GSD p.3 |
| Foundation design basis | Soil bearing at base **≥ 100 kPa**; ASCE 7-05 exposure C (GB50009 B); *"In some particular scene, such as island and **mountain peak**, site designer should recheck the foundation design and modify the drawing"* | GSD p.3 (General Description) |
| Component list, Std. A-shaped 3.0 **LOW** | Horizontal beam 4089 ×4; **Vertical (longitudinal) beam 3656 ×2**; Reinforced beam 2986 ×1; Long raking strut 2165 ×2; Column 1862 ×4; Short raking strut 1321 ×2; connecting bracket ×4; anchor bracket ×8; middle clamp 9 (1 spare); edge clamp 9 (1 spare); M12×100 ×15; M12×140 ×19; M8×35 ground bolt ×2; M16 anchor pairs (21540482) ×2 | **PVM p.171 (160), Table 4-18** — identical to GSD p.9 |
| Component list, Std. A-shaped 3.0 **HIGH** | as above **plus** high column 3391 ×4, reinforced beam ×2, short raking strut ×4, M12×150 ×3 | PVM p.185 (174), Table 4-21 |
| Support dimensions (figure at 15°) | Foundation strip spacing **2600 mm**, anchor group spacing **1800 mm**, heights 1203 / 1727 / 2430 mm | PVM p.170 (159), Fig. 4-71 |
| Tilt vs latitude table | 0–15° → 15°; 16–25° → 25°; 26–30° → 35°; **31–45° → 45°** | PVM p.171 (160), Table 4-19; GSD p.14 |
| **Module-to-crossbeam clearance, 585 W / iPV585-M2A** | **Overhang length 558.5 mm; long-side margin 306.5 mm (crossbeam length 4089 mm)** | **PVM p.180–181 (169), Table 4-20** (identical Table 4-23, p.195) |
| Max modules per support | **"A maximum of six PV modules can be installed on each support"** | PVM p.182 (170); Table 3-29 |
| Clamp compatibility warning | *"If old PV modules are used together with 585 W/630 W … modules, the middle clamps in the spare part package of the old support are not applicable. Replace the middle clamps with new ones, which can be obtained from the fitting bag of the new PV modules."* | PVM p.180 (169) |
| **iSitePower-A V100R023C10 PV configuration (Config 7 / 8)** | PV module support: **standard A-shaped support 3.0 only**; SJB: **PVDB500-15-2B only**; PVDU: PVDU-150A4; solar supply module: **S4875G2 / S4875G3** | **PVM p.34–35 (23–24), Table 2-3** |
| iSitePower-A cross-reference | *"For details about the PV solution configuration, see … **Configuration 7**"* | ISP p.33 (25), p.34, p.41 |
| **iSSU / module pairing** | *"The **iSSU can be connected only to iPV modules**"*; iPV540/iPV585/iPV630 → **3 to 12 per string**; PVDB max 2 inputs | **PVM p.230 (219), Table 5-5** |
| SSU S4875G6 pairing | *"The S4875G6 can be connected only to **PV modules**"*; 585 W plain: **3–7 modules/string if lowest ambient < −10 °C**, 3–8 if ≥ −10 °C | PVM p.236 (225), Table 5-6 |
| iSSU input terminal cable | *"The cable cross-sectional area **must be 4 mm²**"* (terminal 14192168, strip 17 mm) | **PVM p.229 (218)** |
| Cable table | Support ground cable **16–35 mm²**; PV connector cable max 25 A, **2.5–6 mm²**; PVDB500-15-2B in/out 15 A, 2.5–6 mm² | PVM p.117–118 (106), Table 4-6 |
| **Surge protection requirement** | Site **shall** have a surge protection system; **all PV modules, PV devices and the highest point of the support shall be inside the 45° protective cone of the lightning rod**; PV cable ≥ **0.5 m** from the lightning-rod down-conductor | **PVM p.118 (107), §4.1.3** |
| Earthing requirement | **Ground resistance ≤ 10 Ω**; all supports to the same site ground bar; ground screw at the bottom of the column | PVM p.120 (109) §4.1.5; p.182 (170) |
| **PVDB500-15-2B (01075918)** | 260 × 115.6 × 260 mm; ≤5 kg; **input/output 100–500 V DC**; **max 15 A per route**; 2 routes with circuit breakers; **IP55**; −35…+55 °C; pole/wall mount; **no SPD listed** | **PVM p.84 (73), Table 3-30**; p.82 (71) |
| **iSSU S4875G2 (02314JWW)** | Input **85–435 V DC**, max input current **1 × 25 A**, max input power **4000 W**, **iPV modules 3–12 in series per string**, output −43.2…−58 V DC (default −53.5 V), η ≥97.5 %, −25…+75 °C, IP20 | **GA-iSSU p.2** |
| ICC330-H1-C6 (01075071) | 650 × 650 × 1600 mm, 21 U, IP55, heat exchanger, DCDU-400AN5, max 400 A / 24 kW; **operating temperature −20 … +45 °C**; batteries **ESM-48100B1 / 48150B1 / 48100A7 / 48150A3 / 48200A1** | GA-ICC330 p.2; ISP p.90–91 (82–83) |
| **Huawei quotation actually on file** | Product **iSitePower-A (01520078)**, model *"iSitepower-S2 Outdoor, site load 1180 W; **PV 12 × 540 Wp**; ESM, 15.9 h backup, 600 Ah"*; **12 × iPV540-M1A (52240289)**; **1 × ICC360-HA1-C1 (01075399)**; 2 × S4875G2; 3 × R4875G5; 1 × AIU03-100C; **1 × PVDB500-15-2B (01075918)**; 1 × GIM01C1; 6 × **ESM-48100A6**; 2 × PV extension cable 7 m 4 mm² | **HW-BOQ (both v1 and v2), sheet `L3-iSitePower-A`** |
| ICC360-HA1-C1 identity | Belongs to the **PowerCube 1000** family; guide is an **Orange Egypt customer-specific** issue (2021-02-25); uses ESM-48100A6 | PC1000 p.1, p.5–6 |

---

## 3. Findings

### 3.1 RED — Critical

---

**F-01 (RED) — The Huawei BOM number of the support is missing from the BOQ; the product name used is ambiguous across three incompatible generations.**

BOQ LOT 1 item 1.1 (cell B13) specifies only *"tip: A-izvedba, NISKA izvedba (Standard A-Shaped Support — LOW SUPPORT)"* and *"kao Huawei Ground Support ili ekvivalent"* (B28). No BOM number is given anywhere in the BOQ, the TD or Prilog III. Huawei markets three different A-shaped low-support families with the same commercial name:

| BOM | Product | Modules accepted | Source |
|---|---|---|---|
| 21540421 (low) / 21540424 (high) | A-shaped Support | 280/300/335/**445** W; iPV375/iPV400 only | PVM p.70–71, Table 3-23 |
| 21540460 (low) / 21540461 (high) | Standard A-shaped Support **2.0** | Table 3-24: 280/300/335/445 W only (Table 2-1 lists ≤585 W — internal conflict, see F-13) | PVM p.72–73 |
| **21540481 (low)** / 21540480 (high) | Standard A-shaped Support **3.0** | 280/300/335/445/535/540/**585 W**; iPV375/iPV400/**iPV540-M1A/iPV585-M2A** | PVM p.80–81, Table 3-29 |

**Determination — the BOQ must name `21540481` (Standard A-shaped low support 3.0).** Two independent proofs:

1. PVM p.34 (printed 23), Table 2-3, Configuration 7 — *iSitePower-A V100R023C10 New Site* — permits exactly one support: *"PV module support: **standard A-shaped support 3.0**"*, and exactly one SJB (PVDB500-15-2B) and one solar supply module family (S4875G2/S4875G3). Configuration 8 (Rural PV Power Supply) is identical. ISP p.33 (25) confirms that the ICC330-H1 cabinet family is governed by Configuration 7. There is **no** iSitePower-A configuration that permits 21540421 or 21540460/61.
2. PVM p.80–81 (69–70), Table 3-29 is the only A-shaped table that lists 585 W and iPV585-M2A as applicable modules.

**The component list currently in the tender belongs to 21540481, not to a different generation.** BOQ B15–B18 (horizontal beam 4089 ×4, longitudinal 3656 ×2, reinforced 2986 ×1, long raking strut 2165 ×2, column 1862 ×4, short raking strut 1321 ×2, 4 column brackets, 8 anchor brackets, 9 middle + 9 edge clamps, M12×100 ×15, M12×140 ×19) is a **character-for-character copy of PVM Table 4-18, p.171 (printed 160)** and of GSD p.9, both of which are headed *"Standard A-shaped support 3.0 (Low Support)"* / part numbers 21540480, 21540481 (GSD p.6). It is therefore internally consistent — but a bidder reading only *"A-shaped low support"* may legitimately offer 21540421, which is rated for 335 W modules and would be a direct non-compliance.

**Also missing from the BOQ** (all part of the 21540481 BOM per PVM Table 3-29, p.80): anchor bolt for the concrete foundation **21540482**, antitheft nut **21540036**, antitheft nut wrench **21540038**, and the M8×35 ground-cable bolt (Table 4-18 item 13). BOQ item 1.2 describes the anchor geometrically but never cites 21540482.

**Required text for BOQ item 1.1:** *"Huawei Standard A-shaped Support 3.0 — LOW support, BOM 21540481, komplet sa ankerima 21540482, protuprovalnim maticama 21540036 i ključem 21540038 — ili ekvivalent dokazano certificiran za module 2278 × 1134 mm / 585 W pri nagibu 45° i za klimatske uticaje lokaliteta."*

---

**F-02 (RED) — Panel-field geometry is wrong. Horizontal projection is 3.24 m, not 2.59 m; top edge is +3.74 m, not +3.09 m.**

The tender derived the array projection from the **3656 mm longitudinal beam**: Prilog III p.5 (S-03), explanation ①, states *"uzdužna greda 3656 mm (**projekcija 2,59 m**)"*, and 3656 × cos 45° = 2585 mm ≈ 2590 mm, which is exactly the value in BOQ B23 and the S-03 dimension chain +0.50 → +3.09 m (3.09 − 0.50 = 2.59). **The longitudinal beam is a structural member that sits under the modules; it is not the module field.**

The correct geometry, derived entirely from the manual:

| Quantity | Value | Derivation / source |
|---|---|---|
| 585 W module | 2278 × 1134 × 30 mm | PVM p.43 (32), Table 3-5 |
| Arrangement | **2 rows × 3 columns, modules PORTRAIT** (1134 mm across the slope width, 2278 mm up the slope) | PVM p.170 Fig. 4-71; p.181 Fig. 4-87; forced by the crossbeam length (3 × 2278 = 6834 mm ≫ 4089 mm) |
| Module block width | 4089 − 2 × 306.5 = **3476 mm** | Table 4-20 long-side margin 306.5 mm, crossbeam 4089 mm |
| — check | 3 × 1134 = 3402 mm + 2 inter-module gaps of 37 mm = 3476 mm ✔ | |
| Overall structure width | **4089 mm** (crossbeam ends project 306.5 mm each side beyond the glass) | Table 4-20 |
| **Module field slope length** | 2 × 2278 + gap (≈20–40 mm) = **4576–4596 mm; use 4.58 m** | |
| — check against beam | crossbeam 1 → crossbeam 4 = 4576 − 2 × 558.5 = **3459 mm ≤ 3656 mm** longitudinal beam ✔ (≈98 mm spare at each end) | Table 4-20 overhang 558.5 mm |
| — check against Fig. 4-71 | Figure drawn at 15°: 2430 − 1203 = 1227 mm rise ⇒ slope length 1227/sin 15° = 4741 mm to structure faces ✔ consistent with 4576 mm of glass + beams | PVM p.170 |
| **Horizontal projection at 45°** | 4576 × cos 45° = **3236 mm ≈ 3.24 m** | |
| **Vertical rise at 45°** | 4576 × sin 45° = **3236 mm ≈ 3.24 m** | |
| **Top edge with bottom edge at +0.50 m** | **+3.74 m** | |
| Glass area | 6 × 2.278 × 1.134 = **15.50 m² per support; 31.00 m² total** | |
| Mass | 6 × 32.0 kg modules + 154 kg support = **≈346 kg per support** | Table 3-5; Table 3-29 |

**Errors in the tender:**

| Parameter | Tender | Correct | Error |
|---|---|---|---|
| Horizontal projection @45° | 2590 mm (BOQ B23; Prilog III p.5) | **3236 mm** | **−646 mm (−20 %)** |
| Top edge level | +3.09 m (BOQ B23; Prilog III p.5) | **+3.74 m** | **−0.65 m (−17 %)** |
| Overshoot above 1.90 m fence | "0.20 m" / "0.17 m" | see F-03 | inconsistent |

**The tender contradicts itself:** Prilog III p.4 (drawing S-02) carries the dimension **3,22** on the north–south extent of support PV-2, which is within 20 mm of the correct 3.24 m, while p.5 (S-03) and BOQ B23 state 2.59 m. One of the two drawings in the same annex is wrong.

**Consequences that must be re-checked once the geometry is corrected:** (a) wind uplift lever arm and overturning moment increase — the top edge rises 0.65 m and the projected sail area seen in plan grows from 4.089 × 2.59 = 10.6 m² to 4.089 × 3.24 = **13.2 m² per support (+25 %)**; (b) the north edge of the array now oversails the RC slab by ≈0.85 m instead of 0.17 m; (c) the setback between the two supports and the fence, and the maintenance clearance behind the array, change.

**The 6-modules-per-support / 2 × 3 arrangement in the tender is CONFIRMED, not refuted.** Three independent proofs: (i) PVM p.81 (70), Table 3-29 and p.182 (170): *"One support for one to six PV modules" / "A maximum of six PV modules can be installed on each support"*; (ii) PVM p.170 Fig. 4-71 and p.181 Fig. 4-87 both depict 2 rows × 3 columns on 4 crossbeams; (iii) **clamp arithmetic**: 9 middle + 9 edge clamps including 1 spare each = **8 + 8 usable**. A 2 × 3 portrait field on 4 crossbeams needs, per crossbeam, 2 edge clamps (outer glass edges) + 2 middle clamps (between modules 1–2 and 2–3) = 4 × 2 = **8 edge and 8 middle** — an exact match. Any other arrangement fails: 3 rows × 2 columns would need 6 crossbeams and a field width of 2 × 2278 = 4556 mm > 4089 mm crossbeam (physically impossible), and landscape modules would need 3 × 2278 = 6834 mm of crossbeam.

---

**F-03 (RED) — The stated fence overshoot is internally inconsistent and both values are invalidated by F-02.**

BOQ LOT 1 B24 states *"gornja (sjeverna) ivica panela nadvišuje ogradu h=1,90 m za cca 0,20 m"*; Prilog III p.4 (S-02) legend repeats "0,20"; Prilog III p.5 (S-03) dimensions it as **"nadvišenje panela nad ogradom 0,17 m"**. Two different values for the same dimension in the same annex. Moreover, the sentence is ambiguous — it can be read as a vertical overshoot (top edge above the fence top) or as a horizontal oversail of the array over the fenced slab. On S-03 the dimension line is horizontal, so it is an oversail; but the wording *"nadvišuje ogradu h=1,90 m za 0,20 m"* reads as vertical. With the corrected geometry (F-02) the top edge is at +3.74 m, i.e. **1.84 m above the fence top**, and the horizontal oversail becomes ≈**0.85 m**. Neither 0.17 m nor 0.20 m is correct under either reading.

---

**F-04 (RED) — The power system identified in the tender does not exist in any single consistent form, and none of the four names matches the Huawei quotation actually on file.**

| Document | Page / cell | System named | Status claimed |
|---|---|---|---|
| TD .docx | p.4, §3 *Postojeće stanje* | *"planirani sistem napajanja: **Huawei MTS9302** sa ispravljačima, LFP baterijama i kontrolerom, ili drugi kompatibilan sistem"* | **planned** |
| Prilog III | p.3 (S-01) and p.4 (S-02) | *"**postojeći** vanjski ormari na SJEVERNOJ strani: Huawei **ICC330-H1** (outdoor) + **MTS9302**"* | **existing** |
| Prilog III | p.32 (INFO-04) | *"FN moduli — **PowerCube** — baterija — agregat"* | — |
| Prilog III | p.34, ref. item 8 | *"Huawei **iSitePower-A / ICC330-H1** — korisnička dokumentacija"* | — |
| BOQ LOT 2 | items 5.6 (B103, B110) | *"ispravljački sistem (Huawei **PowerCube 1000**)"* | — |
| **HW-BOQ** (both versions) | sheet `L3-iSitePower-A` | **ICC360-HA1-C1 (01075399)**, 12 × **iPV540-M1A**, 2 × S4875G2, 3 × R4875G5, AIU03-100C, PVDB500-15-2B, GIM01C1, 6 × **ESM-48100A6** | **quoted** |

What is consistent:
- The **module-level** architecture is consistent across all documents: 2 × S4875G2 iSSU, 1 × PVDB500-15-2B, 3 × R4875G5 (12 kW — correctly quoted in BOQ LOT 2 B43), AIU03 AC input, GIM01C1 genset interface (BOQ LOT 2 B41, B116), SoC-based genset start (BOQ LOT 2 B41; ISP p.41–42, §3.5 *Solar-Diesel Hybrid Scenario*). All of this belongs to the **PowerCube 1000 / iSitePower** platform.
- The load figure 1180 W is identical in Prilog III p.2 and in the HW-BOQ model string.

What is contradictory:
1. **ICC330-H1 vs ICC360-HA1-C1.** These are different products with different battery part numbers. ICC330-H1-C6/-C8 accepts ESM-48100B1 / 48150B1 / 48100A7 / 48150A3 / 48200A1 (ISP p.90, §4.3.27) — **ESM-48100A6 is not on that list**. The quoted 6 × ESM-48100A6 belongs to ICC360-HA1-C1 (PC1000 p.5–6, §2.13). The two cabinets also differ in size: 650 × 650 × 1600 mm (ISP p.91, Table 4-44) vs 650 × 650 × 2000 mm (HW-BOQ description).
2. **MTS9302 is a different product line entirely.** The MTS9300A family (MTS9302A-HD16A1 etc.) is a 19-inch telecom power subrack (*MTS9300A V100R001C00 Telecom Power User Manual*, p.5), whose solar option is the older **S4850G1 + PVDU** (p.60), not the S4875G2 + PVDB500-15-2B specified everywhere else. An ICC330-H1 and an MTS9302 cannot both be "the" hybrid power system.
3. **"Existing" vs "planned."** S-01/S-02 draw the cabinets as *postojeći* (existing); TD p.4 calls the system *planirani* (planned). A bidder cannot know whether the cabinet is on site or is to be delivered under the separate procurement.
4. **12 × 540 Wp vs 12 × 585 Wp** (see F-09).

**What the tender must state:** a single sentence naming the actual power system, its status, and its PV configuration reference, e.g. *"Hibridni sistem napajanja je Huawei PowerCube 1000 / iSitePower, kabinet ICC360-HA1-C1 (BOM 01075399), sa 2 × iSSU S4875G2 (02314JWW), 3 × R4875G5, AIU03-100C, GIM01C1, PVDB500-15-2B (01075918) i 6 × ESM-48100A6 (600 Ah / 28,8 kWh), predmet posebne nabavke, isporuka [postojeća / planirana za datum]. PV konfiguracija prema PV Module Solution User Manual, Configuration 7."* Every occurrence of "ICC330-H1", "MTS9302" and the bare word "PowerCube" must then be aligned to it.

---

**F-05 (RED) — BOQ item 1.6 (generic PVDB) conflicts with the mandated Huawei PVDB500-15-2B in three verifiable respects.**

PVM p.34–35 (23–24), Table 2-3, Configurations 7 and 8 admit exactly one SJB for iSitePower-A: **PVDB500-15-2B**. It is already in the Huawei quotation (HW-BOQ, part 01075918, qty 1). PVM p.30 (19) allows an alternative only in narrow terms: *"…it is recommended that the iSSU (S4875G2 or S4875G3) … be connected to PV modules through the PVDB500-15-2B **or a high-voltage maintenance box purchased by the customer**"*, and PVM p.232 (221) qualifies that box as *"input voltage ranging from 100 V DC to 500 V DC"*.

BOQ item 1.6 as written is **not** an acceptable substitute and **is inconsistent with the Huawei product it is supposed to replace or duplicate**:

| Requirement in BOQ 1.6 | Huawei PVDB500-15-2B | Verdict |
|---|---|---|
| "IP65" | **IP55** (PVM p.84 (73), Table 3-30) | The tender's own IP class **excludes** the mandated Huawei product |
| "odvodnik prenapona DC (tip 2) **za svaki string**" | **No SPD** is listed in Table 3-30 or in the interior figure (PVM p.83 (72), items 1–9 are input/output terminals and a ground block only) | The mandated product **cannot** meet the tender's own requirement |
| "DC rastavljač, osigurači" | 2 branches, **each controlled by a circuit breaker** (PVM p.82 (71)); no separate fuses | Partially met |
| Voltage rating | not stated in BOQ | 100–500 V DC | **is missing** |
| Current rating | not stated in BOQ | **15 A max per route** | **is missing** |
| Quantity 1 kpl | max 2 inputs = 2 strings ✔ | correct |

Additionally, item 1.6 duplicates an item already in the Huawei quotation (HW-BOQ: PVDB500-15-2B × 1) while TD p.3 states *"Predmet nabavke ne obuhvata isporuku fotonaponskih panela, baterijskog sistema niti kontrolno-upravljačkog sistema hibridnog napajanja, koji su predmet posebne nabavke."* Whether the PVDB belongs to LOT 1 or to the separate Huawei order **is not resolved anywhere in the package** — a double-procurement / gap risk.

**Resolution:** either (a) delete item 1.6 and state that the PVDB500-15-2B (01075918) is supplied under the separate Huawei order, LOT 1 supplying only its mounting, cabling and earthing; or (b) keep item 1.6 but re-specify it as *"Huawei PVDB500-15-2B (01075918) ili ekvivalent: 100–500 V DC, 2 nezavisna stringa sa DC prekidačem po stringu, ≥15 A po stringu, min. IP55, −35…+55 °C"*, and — because neither the PVDB500-15-2B nor the tender's generic box carries one — **add a separate Type 2 DC SPD enclosure as its own BOQ line** with a stated Ucpv ≥ 600 V DC, In ≥ 5 kA (8/20 µs), and remote status contact.

---

**F-06 (RED) — DC cable size 6 mm² is incompatible with the iSSU input terminal, which requires exactly 4 mm².**

BOQ LOT 1 item 1.5 specifies 100 m of **1 × 6 mm² H1Z2Z2-K** with MC4 connectors *"od fotonaponskih panela do PVDB distribucije"*. PVM p.229 (printed 218), §5.5.1 states for the iSSU input terminal (14192168): ***"The cable cross-sectional area must be 4 mm². When preparing the terminal, strip the cables for 17 mm."*** (The identical requirement applies to the S4875G6, PVM p.235 (224).) PVM Table 4-6, p.117 (106) allows 2.5–6 mm² for the PV connector cable and for the PVDB in/out, so 6 mm² is acceptable **up to** the PVDB, but the final PVDB → iSSU tails **must be 4 mm²**. The Huawei quotation includes only 2 × *"PV Module Extension Cable, 7 m, 4 mm²"* (HW-BOQ 04153586) and 12 m each of black/white H07Z-K 4 mm² (25030700, 25030730-001).

**Consequence:** the PVDB → iSSU jumpers **are missing** from the tender scope as a distinct item, and item 1.5 as written would lead a bidder to terminate 6 mm² into a spring terminal specified for 4 mm².

**Voltage-drop check of item 1.5 (result: sizing is generous, the problem is the terminal, not the losses).** Per string: 25 m per pole, loop 50 m, Cu 6 mm², ρ = 0.0175 Ω·mm²/m ⇒ R = 0.146 Ω.
- Non-optimised 585 W string: Imp = 13.67 A ⇒ ΔU = 2.00 V on Vmp = 6 × 42.79 = 256.7 V ⇒ **0.78 %**.
- iPV585-M2A string at the optimizer current ceiling of 15 A (PVM Table 3-18, p.62): ΔU = 2.19 V on a minimum string voltage of 3510 W / 15 A = 234 V ⇒ **0.94 %**.
Both well inside the customary 1 % DC-side limit; 4 mm² would give 1.2–1.4 %, also acceptable. So 4 mm² throughout is the simplest compliant solution.

---

**F-07 (RED) — The tender's own reference drawings (Prilog III FN-01…FN-06) exclude the 585 W module and have had their Huawei provenance stripped.**

Prilog III pp. 23–28 reproduce the Huawei *Standard A-Shaped Support 3.0 Quick Guide* and the Huawei foundation drawings under the BH Telecom title block *"Nosač fotonaponskih panela (ground support) — LOW Support"*. Three defects:

1. **Wrong module class.** GSD p.14 (Quick Guide §1.2) states: *"The PV module support can be mounted with **540 W PV modules or iPV540-M1A**."* GSD p.19 gives the only permitted module dimensions: *"540 W/iPV540-M1A — Length 2256–2285, Width 1133–1134, **Thickness 35**"*. The 585 W module is **30 mm thick** (PVM Table 3-5, p.43) and is therefore outside the envelope of the document the tender hands to bidders. The Quick Guide is Issue 01, 2022-04-30 — it predates the 585 W module. Only PVM Issue 07 Table 3-29 (p.80) authorises 585 W on 21540481.
2. **Wrong support variant on the foundation sheets.** The Huawei source sheets (GSD pp. 3–5) are titled ***"Sharp A Bracket 3.0 Foundation (High solar bracket)"***. In Prilog III (FN-02/FN-03/FN-04, pp. 24–26) the Huawei title block containing that designation **has been cropped off** and the sheets re-labelled "LOW Support". GSD p.3 explicitly warns *"Selection of foundation grade shall be decided by bracket height, angle"* — i.e. the low and high brackets do not necessarily share a foundation. The tender's entire civil quantity set for item 2.3 (0.407 m³ C25 + 0.094 m³ C10 + 1.59 m³ excavation + 1.1 m³ backfill + 19.53 kg rebar per strip) is taken from the **high-bracket** sheet.
3. **Residual 540 W annotation.** The foundation plan reproduced as FN-03 (Prilog III p.25) still carries the Huawei annotation *"Solar panel Contour (**6X540W**)"*, contradicting BOQ B19 (585 Wp).

---

**F-08 (RED) — The clamp/module thickness interface is unassigned between LOT 1 and the separate panel procurement.**

PVM p.180 (printed 169) warns: *"If old PV modules are used together with 585 W/630 W PV modules or iPV585-M2A/iPV630-M2A modules, the middle clamps in the spare part package of the old support are **not applicable**. Replace the middle clamps with new ones, which can be obtained from the **fitting bag of the new PV modules**."* The 540 W module is 35 mm thick, the 585 W module 30 mm (PVM Tables 3-5 and HW-BOQ). LOT 1 supplies the support (with 9 + 9 clamps per BOQ B18); the panels come from a separate procurement (TD p.3). If the delivered support carries 35 mm clamps and the delivered modules are 30 mm, the array cannot be clamped to torque. **The tender does not assign responsibility for supplying the correct clamp set.** This must be stated explicitly in BOQ item 1.1.

---

**F-09 (RED) — The PV nameplate in the tender (12 × 585 Wp = 7.02 kWp) does not match the Huawei configuration on file (12 × iPV540-M1A = 6.48 kWp).**

Both versions of the Huawei quotation (`…_BOQ.xlsx` and `…_BOQ_v2.xlsx`, sheet `L3-iSitePower-A`) list **12 × iPV540-M1A (52240289)** and the model string *"…site load 1180W; **PV 12x540Wp**; ESM, 15.9h backup, 600Ah"*. The tender states 12 × 585 Wp throughout (BOQ B19, Prilog III pp. 2, 4, 5). Mechanically this is harmless — both modules are 1134 mm wide and 2278/2279 mm long, so the support, clamp positions, foundation and array envelope are identical — but:
- the **yield statement is 8.3 % optimistic** relative to the equipment actually on order (see F-10);
- the **clamp thickness differs** (35 mm vs 30 mm — see F-08);
- BOQ item 1.1 asks bidders to dimension a structure for a module the buyer has not ordered.

Either the Huawei order must be amended to iPV585-M2A (52240385/52240386), or the tender must be corrected to 12 × iPV540-M1A = 6.48 kWp.

---

**F-10 (RED) — The yield statement is not defensible. The scaling factor is sound; the simulation it scales is physically impossible.**

Prilog III p.30 (INFO-02) presents a single heat-map of *"PV Proizvodnja — Heatmap (W, prosjek po satu)"* for 12 × 540 Wp with the note *"Za trenutnu konfiguraciju 12×585 Wp (7,02 kWp) sve vrijednosti proizvodnje skalirati faktorom 585/540 ≈ 1,083 (+8,3 %)."*

**(a) The linear factor 1.083 IS defensible.** The 585 W and 540 W modules occupy the same area (2278 × 1134 = 2.583 m² vs 2279 × 1134 = 2.584 m²); the difference is purely cell efficiency (22.6 % vs ≈20.9 %). Same area, same tilt, same azimuth, same shading, same string count ⇒ energy scales with nameplate to within <1 %. Two second-order caveats: the temperature and low-irradiance coefficients of the two module types are not published side by side in the manual, and — see F-11 — if the modules really were bifacial the scaling would not be linear. Recommend stating the factor as **1.083 ± 1 %**.

**(b) The base being scaled is not usable.**
- **RS-REP p.1** states *"Instalirana snaga: 6.5 kWp — Godišnja proizvodnja: **115,582.0 kWh**"*. That is **17,782 kWh/kWp/yr**, roughly **12 × the physical maximum** at this latitude (the annual plane-of-array irradiation itself is only ≈1,900 kWh/m²). The same report gives *"Godišnja potrošnja: 7,183.2 kWh"*, whereas 1180 W continuous is 10,337 kWh/yr. **The reference simulation is unusable and must not be cited.**
- The INFO-02 heat map itself, summed hour-by-hour over the twelve monthly columns, yields **≈11,220 kWh/yr for 6.48 kWp = 1,731 kWh/kWp**, and shows monthly-mean hourly powers up to **5,835 W from a 6,480 W array (90 % of nameplate)**. A monthly *average* at 90 % of nameplate is only reachable under clear-sky, loss-free assumptions; it is ≈15–20 % above any weather-corrected value. The heat map appears to be a clear-sky / low-loss result, not a TMY-based one.
- INFO-02 contains **no annual energy figure, no performance ratio, no PV/genset energy split, and no December energy balance** — the three numbers a bidder and a reviewer actually need. These **are missing**.

**(c) Corrected figures (independent calculation, HDKR transposition, ρ = 0.20, south-facing, 42.9448° N, 1076 m):**

| | 7.02 kWp @ 45° | 6.48 kWp @ 45° |
|---|---|---|
| Plane-of-array irradiation, annual | **1,800 – 1,930 kWh/m²** | same |
| Plane-of-array irradiation, December | **100 – 107 kWh/m²** | same |
| Generable energy, annual (PR = 0.80) | **10,100 – 10,850 kWh/yr** (1,440–1,545 kWh/kWp) | **9,320 – 10,010 kWh/yr** |
| Generable energy, December | **560 – 600 kWh** | **520 – 555 kWh** |
| Load, annual / December | 10,337 kWh / **878 kWh** | same |
| **December balance** | **deficit 280 – 320 kWh = 32–36 % of December load** | **deficit 325 – 360 kWh = 37–41 %** |
| PV share of annual load, ideal monthly balancing | 88 – 94 % | 84 – 91 % |
| PV share of annual load, realistic (daily resolution, cloudy runs, 28.8 kWh battery ⇒ ≈22 h autonomy) | **80 – 88 %** | **76 – 85 %** |
| **Genset energy, annual (DC bus)** | **1.2 – 2.1 MWh/yr** | **1.5 – 2.5 MWh/yr** |
| **Genset run hours** (at the 12 kW rectifier ceiling, η ≈ 0.94) | **≈110 – 190 h/yr** | **≈140 – 230 h/yr** |

**Answer to the adequacy question: 7.02 kWp is NOT adequate for a 1180 W continuous load in December at this location.** Even in an average December the array delivers roughly two-thirds of the December load; in a cloudy December week it delivers a small fraction of it. December self-sufficiency at 45° would require 878 / (0.1073 × 0.80) ≈ **10.2 kWp in an average December**, and ≈14 kWp with any reserve for consecutive overcast days — i.e. 18–24 modules and 3–4 supports, which neither the 150 m² parcel nor the 2-support scope allows. The genset is therefore **structurally necessary**, not merely a back-up, and the tender should say so. The good news is that the resulting **110–190 genset hours/yr sits comfortably inside the 250 h/yr assumed in the BOQ note** (BOQ LOT 2 note A146) — that assumption is sound.

---

### 3.2 YELLOW — Requires clarification or additional calculation

---

**F-11 (YELLOW) — The "bifacijalni" claim is unsupported by any Huawei document in the package.**

Prilog III p.2 states *"FN konfiguracija: 12 × 585 Wp (7,02 kWp), fiksni nagib 45°, **bifacijalni**"*. Neither PVM Table 3-5 (585 W, p.43) nor Table 3-17 (iPV585-M2A, p.61) nor Table 3-4 (540 W) describes any of these modules as bifacial; all are given only as *"Monocrystalline silicon"* with a single power rating and no bifaciality factor or rear-side irradiance rating. Even if the module were bifacial, with the lower edge at +0.50 m over natural ground the rear-side gain would be small (typically 3–5 %) and would not survive the snow condition of F-12. **Either delete the word "bifacijalni" or substantiate it with a datasheet stating the bifaciality factor** — as written, a bidder could price a genuinely bifacial third-party module and change the whole mechanical interface.

---

**F-12 (YELLOW) — Snow accumulation at the lower module edge is not addressed, and the 0.50 m mounting height is questionable at 1076 m.**

BOQ B22–B25 and Prilog III p.5, note ④, justify the low support as *"niska ugradbena visina uz **propuštanje snijega**"* (low mounting height allowing snow to pass). At 45° the EN 1991-1-3 roof shape coefficient is favourable (µ₁ = 0.4 at 45°, interpolated from 0.8 at 30° to 0 at 60°), so **snow load on the panels is not the issue — snow burial of the lower row is**. Snow shed from a 4.58 m long 45° surface piles at the foot of the array; with the lower glass edge at only +0.50 m the entire lower module row (2.278 m of slope length, i.e. **half the array, 3.51 kWp**) can be buried by a 0.6–1.0 m drift, which at 1076 m in East Herzegovina is an ordinary winter event, and exactly in the months when the energy is needed (F-10). Huawei markets a dedicated **Snowy Ground Support 21540475** (90° installation, 40 m/s, 585 W capable, PVM p.74 (63), Table 3-25) and a **High Support 21540480**, either of which raises or steepens the array. **Action:** provide the site snow depth statistics; if the 50-year ground snow depth exceeds ≈0.5 m, re-evaluate the low support against the high support 21540480 or a raised plinth, and state the required winter clearing regime in the O&M scope.

---

**F-13 (YELLOW) — The Huawei manual itself contradicts its own module/support compatibility for the 2.0 family; the tender must not rely on Table 2-1 alone.**

PVM p.30 (printed 19), Table 2-1 groups *"Standard A-shaped low/high support 2.0 (21540460/21540461)"* together with the Snowy Ground Support and the 6 m pole support in a row whose applicable modules read *"280 W/300 W/335 W/445 W/535 W/540 W/**585 W**"*. But PVM p.72–73 (61–62), Table 3-24 — the dedicated specification table for 21540460/21540461 — states *"PV series: 280 W/300 W/335 W/445 W; iPV series: iPV375-M1A/iPV400-M1A"*, i.e. **no 585 W**. The same editorial confusion appears at PVM p.70 where §3.4.3 (*A-shaped Support 21540421/21540424*) is captioned "Table 3-23 Specifications of the standard A-shaped support **2.0**". This is a documentation defect in Issue 07. It does not affect the outcome here — Configuration 7/8 (PVM p.34–35) permits only support 3.0 — but it is a live trap for anyone specifying a Huawei support from Table 2-1 and a reason to always name the BOM number (F-01). **Recommend requesting written confirmation from Huawei on the 21540460/21540461 module range before any future site reuses that product.**

---

**F-14 (YELLOW) — Lightning protection: the manual's mandatory 45° cone requirement is not addressed anywhere in the tender.**

PVM p.118 (printed 107), §4.1.3 *Surge Protection* is a CAUTION, i.e. mandatory: *"The site shall be equipped with a surge protection system… **All PV modules, PV devices, and the highest position of the PV module support shall be within the conical protection range of the lightning rod**… The PV module cable shall be at least **0.5 m** away from the ground cable of the lightning rod."* The site has a 38 m lattice tower; the protective cone at the corrected panel top height of +3.74 m has a radius of 38 − 3.74 ≈ 34 m, so geometric compliance is very likely — **but the tender never states it, never dimensions the distance from the tower to the array, and never states the 0.5 m separation between the DC route and the tower down-conductor.** BOQ LOT 2 item 5.2 routes three PEHD Ø50 conduits past the tower base with no separation requirement. **Action:** add a compliance statement and a dimension on S-02, and add the 0.5 m separation clause to BOQ item 1.5 / 5.2.

---

**F-15 (YELLOW) — The 10 Ω earthing limit from the manual is not quoted; the earthing conductor type is questionable for the exposure.**

PVM p.120 (printed 109), §4.1.5 is a CAUTION: ***"Ground resistance: ≤ 10 Ω"***, and *"If multiple supports are installed onsite, the ground cables of all supports must be connected to the same site ground bar."* BOQ LOT 2 item 5.8 only says *"Otpor uzemljenja mora zadovoljiti zahtjeve Projektnog zadatka"* — the numeric limit **is missing** from the tender. Add "≤ 10 Ω" explicitly.

Conductor sizing is compliant: BOQ item 1.4 specifies 25 mm², within the manual's 16–35 mm² range (PVM Table 4-6, p.117). However **H07V-K is a single-core PVC building wire (H07V-K = 450/750 V, PVC, indoor/conduit)**; for an exposed outdoor run from a galvanised support to a buried ring earth at 1076 m, a UV/ozone-resistant type (e.g. H07Z-K or a PVC-sheathed earthing conductor in conduit) is the correct choice — Huawei itself supplies **H07Z-K 16 mm² Y/G** for this duty (HW-BOQ part 25030429). Also, the Huawei kit contains a dedicated **M8×35 ground-cable bolt** at the bottom of the column (PVM Table 4-18 item 13; Fig. 4-88, p.182); BOQ item 1.4 instead calls for *"priključne stezaljke na konstrukciji"*, which may lead a bidder to drill the galvanised structure. Specify the M8×35 bolt.

---

**F-16 (YELLOW) — Item 2.7 (5.40 × 5.40 m RC platform, 2.92 m³) duplicates and contradicts the strip-footing design of item 2.3.**

BOQ LOT 1 item 2.3 procures four 450 × 3300 × 900 mm C25 strip footings — the complete Huawei foundation (GSD pp. 4–5). Item 2.7 then procures, additionally, *"AB platforma (nivelacijska/temeljna ploča) betonom C20/25, debljine 10 cm, armirana Q188 … dimenzija 5,40 × 5,40 m … 29,16 m² × 0,10 m"* = 2.92 m³, with the disclaimer *"količina je data orijentaciono"*. Three problems: (a) a 100 mm slab and 900 mm deep strip footings are two different foundation systems for the same structure; (b) 5.40 × 5.40 m does not cover the two supports, which together span **2 × 4.089 m ≈ 8.2 m** in the E–W direction (Prilog III p.4, S-02) and 3.24 m N–S (F-02); (c) 5.40 × 5.40 m is the dimension of the **existing** container slab (TD p.3; Prilog III p.2), suggesting the line was copied. **Action:** state explicitly whether a levelling slab is required in addition to the strip footings, and if so re-dimension it to the actual array footprint; otherwise delete item 2.7 from LOT 1.

---

**F-17 (YELLOW) — The stated wind speed is the product's capacity, presented as if it were a site datum.**

BOQ LOT 1 item 2.3 (cell B44) states: *"NAPOMENA: nosivost tla ispod temelja (fak) mora iznositi najmanje 100 kPa, a **osnovna brzina vjetra za nagib 45° iznosi 31 m/s (3 s udar)**."* 31 m/s is the **wind resistance of the Huawei support at 45°** (PVM Table 3-29, p.80; GSD p.3), not the basic wind velocity at Sjednica. The site basic wind velocity **is missing from the entire package** (TD, BOQ and Prilog III). This is a material omission for bidders who must produce the static calculation demanded by BOQ item 1.3.

For the structural reviewer's benefit, the unit conversion is decisive and should be stated in the tender: Huawei's figures are **3-second gusts to ASCE 7-05 exposure C** (GSD p.3), whereas EN 1991-1-4 / BAS uses the **10-minute mean at 10 m**, v<sub>b,0</sub>. With the customary gust factor of ≈1.40–1.50 for open terrain:

| Huawei rating (3-s gust) | Equivalent v<sub>b,0</sub> (10-min mean) | Applies to tilt |
|---|---|---|
| 31 m/s | **≈21 – 22 m/s** | 45° |
| 35 m/s | **≈23 – 25 m/s** | 35° |
| 40 m/s | **≈27 – 28.5 m/s** | 15° and 25° |

BiH national-annex values for the East Herzegovina mountains are typically v<sub>b,0</sub> = 25–30 m/s before the altitude factor, so **the standard Huawei support and foundation at 45° are likely to be non-compliant at 1076 m**, and even 25° may be marginal. GSD p.3 anticipates this: *"In some particular scene, such as island and mountain peak, site designer should recheck the foundation design and modify the drawing."* BOQ item 2.3 correctly repeats that sentence — see F-22.

---

**F-18 (YELLOW) — String and DC architecture: the design is valid only because the module is an iPV type; the tender never says the module MUST be an iPV type.**

BOQ B19 specifies *"Huawei iPV585-M2A **ili ekvivalent**"* — but "equivalent" is undefined and a bidder or the separate panel procurement could deliver the **plain** 585 W PV module (52240406/52240407). The manual makes this a hard incompatibility:

- PVM p.230 (printed 219), Table 5-5, NOTICE: ***"The iSSU can be connected only to iPV modules."*** Strings of iPV540/iPV585/iPV630: **3 to 12 per route**; PVDB max 2 inputs.
- PVM p.236 (printed 225), Table 5-6, NOTICE: ***"The S4875G6 can be connected only to PV modules."*** For a plain 585 W module: **3–7 modules per route where the lowest ambient temperature is < −10 °C** (which is the case at Sjednica), 3–8 otherwise.

Verification of the tendered 2 × 6 architecture **with iPV585-M2A + 2 × iSSU S4875G2** (the quoted hardware):

| Check | Requirement | Design | Verdict |
|---|---|---|---|
| Modules per string | 3–12 (iPV) — PVM Table 5-5 | 6 | ✔ |
| Strings per iSSU | 1 input per module | 2 strings on 2 × S4875G2 | ✔ |
| Input power per iSSU | ≤ 4000 W — GA-iSSU p.2 | 6 × 585 = **3510 W** | ✔ (88 %) |
| Input current per iSSU | ≤ 25 A — GA-iSSU p.2 | ≤15 A (optimizer ceiling, PVM Table 3-18) | ✔ |
| Input voltage window | 85–435 V DC — GA-iSSU p.2 | ≈258 V nominal (6 × 43 V); ≥234 V at the 15 A ceiling | ✔ |
| PVDB branches | 2 max — PVM p.82, Table 3-30 | 2 strings, 1 PVDB | ✔ |
| PVDB current per route | ≤ 15 A — Table 3-30 | 15 A optimizer ceiling | ✔ **but at 100 % of rating** |
| PVDB voltage | 100–500 V DC — Table 3-30 | ≈258 V operating | ✔ |
| Conversion capacity | 2 × 4000 W = 8000 W | 7020 Wp | ✔ |

**If a plain 585 W module were substituted, three things break at once:** (i) the iSSU S4875G2 cannot be used at all (Table 5-5 NOTICE) and would have to be swapped for an S4875G6, which is not part of Configuration 7 for iSitePower-A (PVM Table 2-3, p.34); (ii) the string limit drops to 7 modules for lowest ambient < −10 °C, so 6 still works but with no headroom; (iii) the module Isc of **14.40 A** (Table 3-5) would be passed straight through to the PVDB's **15 A** branch rating and would exceed it at irradiance above ≈1040 W/m², whereas with the optimizer the string output is hard-limited to 15 A.

**Action:** replace *"iPV585-M2A ili ekvivalent"* with a bounded equivalence clause: *"Huawei iPV585-M2A (52240385/52240386) — modul sa integrisanim optimizatorom SUN2000-600W-P; ekvivalent mora imati integrisani optimizator sa izlaznom strujom ≤15 A, gabarite 2278 × 1134 × 30 mm (±10 mm) i Voc stringa ≤500 V DC pri −25 °C."*

Also note that the tender never states the maximum permissible string open-circuit voltage. For the record: 6 × Voc 52.42 V × (1 + 0.0025 × 50 K) ≈ **353 V at −25 °C**, safely inside both the PVDB (500 V) and the iSSU (435 V) limits — but only for a 6-module string of this specific module. **This limit is missing from the tender.**

---

**F-19 (YELLOW) — The Huawei cabinet's operating temperature envelope is not checked against the site.**

ICC330-H1-C6 is specified at **−20 °C to +45 °C** (ISP p.90 (82), Table 4-43; the GA sheet, GA-ICC330 p.2, gives *0…+45 °C with solar radiation, −20…+45 °C with a heater*). At 1076 m in East Herzegovina the design minimum air temperature can reach −20 to −25 °C. The alternative on file, ICC360-HA1-C1, comes from an **Orange Egypt** customer-specific guide (PC1000 p.1) and is fitted with a DC air conditioner — a warm-climate configuration. Neither cabinet's low-temperature option (heater) is called for anywhere in the tender. The PVDB500-15-2B is rated −35…+55 °C (PVM Table 3-30) and the iSSU −25…+75 °C with −40 °C start-up (GA-iSSU p.2), so those are fine. **Action:** confirm the cabinet variant and its heater option against the site design minimum temperature with the separate Huawei order.

---

**F-20 (YELLOW) — Corrosion-protection and fastener clauses conflict with the proprietary Huawei kit.**

BOQ B22 requires *"čelični profili, antikorozivno zaštićeni vrućim cinčanjem prema **EN ISO 1461**"* and B26 requires *"spojni i montažni materijal od nehrđajućeg čelika (**A2/A4**)"*. The Huawei 21540481 kit is a closed factory product supplied with its own coating (rated for Class C environment, PVM Table 3-29, p.81) and its own carbon-steel bolts M12×100 / M12×140 / M8×35 (Table 4-18, p.171). A bidder offering the genuine Huawei support **cannot** comply with the A2/A4 clause without replacing Huawei's own fasteners — which would void the manufacturer's structural rating and its 45 N·m torque specification (PVM p.177). **Action:** re-word as *"Za nuđeni tipski proizvod proizvođača, antikorozivna zaštita i spojni pribor prema specifikaciji proizvođača (Class C, min. ekvivalent EN ISO 1461 / EN ISO 12944 C4); za ekvivalentne konstrukcije nespecificiranih proizvođača primjenjuje se EN ISO 1461 i pribor A2/A4."*

---

**F-21 (YELLOW) — PV module theft protection is offered by Huawei and omitted from the tender.**

PVM §3.3, p.68 (57) describes the **PV Antitheft Kit** (antitheft bolts + disassembly tool) and the **PV antitheft alarm kit** (signal cable routed through all module cable holes to a DIN port on the solar controller; wiring procedure at GSD p.42). The antitheft nut **21540036** and its wrench **21540038** are part of the 21540481 BOM (PVM Table 3-29, p.80) and the installation procedure explicitly branches on their use (PVM p.177, step 9). At an unmanned mountain site with a 1.90 m fence, 12 modules worth several thousand KM are an obvious target. **The antitheft nuts, the wrench, and the antitheft alarm cable are missing from BOQ item 1.1.** Also missing: any requirement for a PV-array theft alarm to be forwarded to the SCADA, even though BOQ LOT 2 item 6.2 procures the SCADA integration.

---

**F-22 (YELLOW) — Where the PVDB is mounted, and who mounts it, is not stated.**

BOQ item 1.6 is in LOT 1; the DC route (item 1.5) ends *"do PVDB distribucije"*; BOQ LOT 2 item 5.6 note B112–B113 says the DC/solar distribution sits *"u zasebnom PVDB ormaru prema Tački 1.6 (LOT 1), fizički odvojenom od ovog GRO-a"*. But no drawing shows the PVDB. Prilog III p.4 (S-02) shows only *"DC trasa u PEHD Ø50 → PVDB"* with no PVDB symbol. The PVDB500-15-2B is IP55, pole- or wall-mounted, bottom cabling, 260 × 115.6 × 260 mm (PVM Table 3-30) — it can go outdoors on the cabinet or on the support column, but the choice determines the 100 m cable quantity in item 1.5 and the conduit count in LOT 2 item 5.2. **Action:** dimension the PVDB position on S-02 and confirm the 100 m DC quantity against it.

---

**F-23 (YELLOW) — Two orphan line items in the price form.**

BOQ LOT 1 contains cell A46 = "2.6" and A49 = "2.8" with no description, no unit and no quantity. A bidder filling in the form will not know whether to price them. **Action:** delete or complete.

---

**F-24 (YELLOW) — Inputs required by the review rules that are not in the package.**

Per §3 of the review rules, the following are **missing** and must be flagged: (a) site basic wind velocity v<sub>b,0</sub> and terrain category (F-17); (b) site ground snow load s<sub>k</sub> and snow depth statistics (F-12); (c) a geotechnical statement of the actual bearing capacity — BOQ item 2.3 asserts ≥100 kPa and "kamenito tlo" without a report; (d) the design minimum and maximum ambient temperatures (F-19); (e) a TMY or PVGIS irradiation dataset for the site (F-10); (f) the Huawei datasheet for the module actually to be delivered (F-09, F-11).

---

### 3.3 GREEN — Correctly implemented

- **G-01** The support component list in BOQ B15–B18 and Prilog III p.27 (FN-05) is an exact, error-free transcription of the Huawei Standard A-shaped Support 3.0 (low) BOM — PVM Table 4-18, p.171 (160). All six lengths, all quantities, and both "including one spare part" notes match.
- **G-02** Tilt selection follows the manufacturer's own table. BOQ B20 cites *"za geografske širine 31–45° → nagib 45°"*, which is exactly PVM Table 4-19, p.171 (160) and GSD p.14. Azimuth 180° / South (BOQ B21) matches PVM p.171: *"In the northern hemisphere, PV modules face true south."*
- **G-03** The anchor specification in BOQ item 1.2 (U-bolt M16, total length 320 mm, leg spacing 180 mm, 50 × 50 mm plates, double nuts, two groups per strip at 1800 mm centres) is a faithful reproduction of GSD p.2 (*Anchor Bolt Dimensions*, 2023-05-03) and GSD p.4 (Foundation Plan). Double-nutting matches PVM p.176 (165): *"When installing anchor bolts, secure each bolt using two nuts."*
- **G-04** All civil quantities in BOQ item 2.3 and items 2.1/2.2/2.2a/2.2b match the Huawei foundation sheet GSD p.5 exactly: concrete 0.407 m³/strip (×4 = 1.63 m³ ✔), cushion 0.094 m³ (×4 = 0.376 ≈ 0.38 m³ ✔), excavation 1.59 m³ (×4 = 6.36 m³ ✔), backfill 1.1 m³ (×4 = 4.4 m³ ✔), rebar Ø10 at f<sub>y</sub> = 335 MPa, 19.53 kg/strip, cover 50 mm, C25 on C10, tolerance ±3 mm, poker-vibrated, cured wet ≥3 days, strip 450 mm (550 at base) × 3300 × 900, spacing 2600 mm. This is unusually well done.
- **G-05** BOQ item 2.3 correctly transcribes Huawei's mountain-site caveat: *"Proizvođač izričito zahtijeva da se za lokacije na planinskim vrhovima projekat temelja ponovo provjeri i prilagodi"* — GSD p.3: *"In some particular scene, such as island and mountain peak, site designer should recheck the foundation design and modify the drawing."*
- **G-06** The support earthing conductor size (25 mm², BOQ item 1.4) is inside the manual's 16–35 mm² window (PVM Table 4-6, p.117), and the requirement to connect **both** supports to the existing ring earth matches PVM p.182 (170): *"the ground cables of all supports must be connected to the same site ground bar."*
- **G-07** The DC cable type H1Z2Z2-K (EN 50618, 1.5 kV DC, UV/ozone resistant, −40…+90 °C) is the correct product class for an exposed mountain PV array, and 6 mm² sits at the top of Huawei's permitted 2.5–6 mm² range for the PV connector cable (PVM Table 4-6). Voltage drop is 0.78–0.94 % (F-06) — comfortably compliant.
- **G-08** The AC/DC segregation rule in BOQ LOT 2 item 5.6 (notes B112–B113: DC isolator, string fuses and DC SPD in a **separate** PVDB enclosure, physically apart from the AC GRO) is good practice and correctly stated.
- **G-09** The genset control philosophy in BOQ LOT 2 B41 (*"start/stop DEA komanduje se iz Huawei kontrolno-upravljačkog sistema preko modula GIM01C1, po kriteriju stanja napunjenosti baterija (SoC), a NE po ispadu mrežnog napona"*) exactly matches ISP p.41 §3.5: *"the power source preference sequence is solar power > battery > genset. The genset is started to supply power to loads and batteries only when there is no sunlight and the battery DOD reaches the preset value."*
- **G-10** The rectifier power ceiling in BOQ LOT 2 B43 (*"3 × R4875G5 = 12 kW"*) matches the Huawei quotation (HW-BOQ: 3 × 02312NFE-002, 4000 W each) and is correctly imposed as a genset-protection constraint.
- **G-11** The genset run-hour assumption in BOQ note A146 (250 h/yr) is conservative and consistent with this review's independent estimate of 110–190 h/yr (F-10).
- **G-12** Foundation strip spacing (2600 mm) and anchor group spacing (1800 mm) in BOQ item 2.3 / 1.2 match PVM Fig. 4-71, p.170 (159) and GSD p.4.
- **G-13** The N–S dimension **3,22 m** on Prilog III p.4 (S-02) is, alone among the tender's geometry figures, correct (within 20 mm of the computed 3.24 m — F-02).

---

## 4. Detailed Checklist

| Category | Check | Result | Ref. |
|---|---|---|---|
| **Geometry & Layout** | All critical dimensions present? | **NO** — module dimensions, module arrangement, array field width (3476 mm), overhang 558.5 mm and long-side margin 306.5 mm are absent from BOQ and Prilog III | F-02 |
| | Dimensions correct? | **NO** — horizontal projection understated by 646 mm; top edge by 0.65 m; S-02 (3.22 m) contradicts S-03 (2.59 m) | F-02, F-03 |
| | Layout feasible on plot? | **PARTIAL** — 2 × 4.089 m plus gap fits in the 16.00 m plot width; the 3.24 m N–S projection fits the 9.40 m depth, but the array now oversails the RC slab by ≈0.85 m and this is not shown | F-02 |
| | Installation/maintenance clearances respected? | **NOT DEMONSTRATED** — no clearance dimension between the two supports, between the array and the fence, or behind the array for module cleaning/replacement | F-02 |
| | Orientation consistent with sun path? | **YES** — 180° / true south, per PVM p.171 | G-02 |
| | Orientation consistent with wind? | **NOT DEMONSTRATED** — site wind data absent; the array faces south while the prevailing bura at this location is typically NE | F-17 |
| **Structural** | Foundation dimensions specified? | **YES** and correct — but taken from the **high-bracket** Huawei sheet and re-labelled "LOW" | G-04, F-07 |
| | Static calculation referenced/provided? | **REFERENCED, NOT PROVIDED** — BOQ item 1.3 demands a certified calculation from the bidder; no input data supplied | F-17, F-24 |
| | Uplift and overturning considered? | **STATED, NOT QUANTIFIED** — BOQ B25: *"MJERODAVNO je podizanje (uplift) i prevrtanje"*; no wind pressure, no anchor tension check. Sail area understated by 25 % (F-02) | F-02, F-17 |
| | Soil bearing capacity data available? | **NO** — 100 kPa asserted without a geotechnical report | F-24 |
| | Safety factors per Eurocode? | **NOT DEMONSTRATED** — Huawei design basis is ASCE 7-05 / GB50009, not EN 1991-1-4; no conversion given | F-17 |
| **Manufacturing / Fabrication** | Steel profiles and thicknesses specified? | **PARTIAL** — lengths and quantities given (G-01); section sizes and wall thicknesses are proprietary to Huawei and not stated, which blocks a genuine "equivalent" offer | F-01 |
| | Weld symbols / accessibility? | **N/A** — fully bolted kit; torque 45 N·m specified by manufacturer (PVM p.177) but **not** quoted in the tender | — |
| | Standard stock sizes used? | **N/A** — proprietary kit | — |
| | Galvanisation / corrosion protection defined? | **CONFLICTING** — EN ISO 1461 + A2/A4 fasteners demanded of a closed factory kit | F-20 |
| **Installation** | Assembly sequence plausible? | **YES** — 11-step sequence at PVM pp. 172–180 and GSD pp. 14–20; not referenced in the tender, but Prilog III pp. 27–28 reproduce it | G-01 |
| | Lifting points / heavy-equipment access? | **PARTIAL** — support 154 kg + 6 × 32 kg modules = 346 kg per support, all manageable by hand; access road condition is flagged in TD p.3 but no crane/vehicle requirement is stated for the PV scope | — |
| | Temporary works? | **NOT REQUIRED** for the low support (max working height 3.74 m) — but working at height >2 m applies to the upper module row, and no fall-protection requirement is stated | F-02 |
| **Maintenance** | Safe access for cleaning/inspection/repair? | **NO** — no access dimension behind or between the arrays; upper module row is at 2.4–3.7 m | F-02 |
| | Drainage and snow clearance provided? | **NO** — lower edge at +0.50 m with a 4.58 m 45° shed surface above it; no clearance regime specified | F-12 |
| | Fasteners accessible with standard tools? | **YES** — M12/M16/M8, insulated torque sockets listed at PVM p.114 (103); antitheft nut wrench 21540038 not procured | F-21 |
| **Documentation & BOM** | BOM provided? | **YES**, and correct in content — **but with no Huawei part numbers at all** | G-01, F-01 |
| | Quantities/lengths/part numbers consistent with drawings? | **PARTIAL** — lengths/quantities consistent; part numbers absent; array geometry inconsistent between S-02 and S-03 | F-01, F-02 |
| | Drawing revision and date clearly marked? | **NO** — Prilog III sheets S-01…S-03, FN-01…FN-06, INFO-01…INFO-05 carry no revision number and no date; the Huawei title blocks on FN-02…FN-04 were cropped, destroying the provenance | F-07 |
| | References to standards and datasheets correct? | **PARTIAL** — EN 1991-1-3/-1-4 and EN ISO 1461 correctly cited; the Huawei reference document handed to bidders (GSD Quick Guide, Issue 01/2022) explicitly excludes the 585 W module | F-07 |
| **Safety** | Sharp edges / pinch / fall hazards identified? | **NO** — none identified in the PV scope | — |
| | Earthing and bonding clearly shown? | **PARTIAL** — BOQ items 1.4, 5.3, 5.4 cover it; the manufacturer's 10 Ω limit and the M8×35 ground bolt are not quoted | F-15 |
| | Lightning protection (45° cone) demonstrated? | **NO** — mandatory CAUTION in PVM §4.1.3 not addressed | F-14 |
| | DC arc / rapid-shutdown provisions? | **NOT CONSIDERED** — the AFCI-capable iSSU **S4875G3** (02314JWW-003, PVM p.102 (91)) is an available alternative to the quoted S4875G2 and is permitted by Configuration 7; not evaluated anywhere | — |
| | Fire safety distances (generator, fuel) vs PV array? | **NOT IN PV SCOPE** — but note the DEA and 500 l tank are inside the container ≈4 m north of the array; separate review | — |

---

## 5. Action Items

**Must be resolved before the tender is issued (RED):**

1. **Insert the Huawei BOM number into BOQ LOT 1 item 1.1:** `21540481` — *Standard A-shaped Support 3.0, LOW support* — together with anchor bolt `21540482`, antitheft nut `21540036` and antitheft nut wrench `21540038`. Add the bounded equivalence clause given in F-01. *(Owner: tender author / PV engineer)*
2. **Re-issue drawing S-03 and BOQ cell B23 with the corrected panel-field geometry:** module 2278 × 1134 × 30 mm, 2 rows × 3 columns portrait, field 3476 mm wide × 4576 mm along the slope; at 45° horizontal projection **3.24 m**, rise **3.24 m**, top edge **+3.74 m** with the bottom edge at +0.50 m. Reconcile with the 3.22 m already dimensioned on S-02. *(Owner: PV engineer)*
3. **Re-issue the fence-overshoot dimension** consistently on S-02, S-03 and BOQ B24, stating explicitly whether it is a vertical or a horizontal dimension. With the corrected geometry: horizontal oversail ≈0.85 m, top edge 1.84 m above the fence top. *(Owner: PV engineer)*
4. **Re-run the wind uplift/overturning input to the structural review with the corrected sail area:** 4.089 × 3.24 = **13.2 m² per support in plan (+25 % over the tendered 10.6 m²)**, lever arm to +3.74 m. *(Owner: structural engineer; input supplied by PV engineer)*
5. **Decide and state the actual power system.** Confirm with the Huawei account team whether the site receives **ICC360-HA1-C1 (01075399)** as quoted, or **ICC330-H1-C6/-C8**, and whether it is existing or to be delivered. Then delete every reference to "MTS9302" and align "ICC330-H1", "PowerCube 1000" and "iSitePower-A" to the single confirmed name in TD p.4, Prilog III pp. 3, 4, 32, 34 and BOQ LOT 2 items 5.6/5.7. *(Owner: tender author + Huawei account team)*
6. **Resolve the PV nameplate.** Either amend the Huawei order from 12 × iPV540-M1A (52240289) to 12 × iPV585-M2A (52240385/52240386), or correct the tender everywhere from 7.02 kWp to 6.48 kWp. *(Owner: procurement + PV engineer)*
7. **Re-specify BOQ item 1.6** as either (a) deleted, with a note that the PVDB500-15-2B (01075918) comes with the Huawei order, or (b) *"Huawei PVDB500-15-2B (01075918) ili ekvivalent: 100–500 V DC, 2 stringa, DC prekidač po stringu, ≥15 A/string, min. IP55, −35…+55 °C"*. In **either** case add a **separate BOQ line for a Type 2 DC SPD enclosure** (U<sub>cpv</sub> ≥ 600 V DC, I<sub>n</sub> ≥ 5 kA 8/20 µs, remote status contact), because the PVDB500-15-2B contains no SPD. Remove the "IP65" requirement, which excludes the mandated IP55 product. *(Owner: electrical engineer)*
8. **Correct BOQ item 1.5:** keep 1 × 6 mm² H1Z2Z2-K for the array-to-PVDB run (100 m), and **add a separate item for the PVDB → iSSU tails in 4 mm²** as required by PVM p.229. Add the 0.5 m separation requirement from the tower down-conductor. *(Owner: electrical engineer)*
9. **Replace Prilog III sheets FN-01…FN-06.** Restore the Huawei title blocks (or add a provenance note), correct the "LOW Support" label on the sheets that are the **high-bracket** foundation, and either obtain the low-bracket foundation drawing from Huawei or state explicitly that the high-bracket foundation is being used conservatively for the low bracket, with the structural engineer's sign-off. Replace the 2022 Quick Guide extract (which permits only 540 W / 35 mm modules) with the corresponding pages of *PV Module Solution User Manual* Issue 07 (pp. 169–182). *(Owner: tender author)*
10. **Assign clamp responsibility in BOQ item 1.1:** state that the middle and edge clamps must match the delivered module thickness (30 mm for 585 W, 35 mm for 540 W) and name which party supplies them, quoting PVM p.180. *(Owner: tender author)*
11. **Replace the yield statement (Prilog III INFO-02).** Withdraw the citation of `RuralStar_Sjednica_FINAL_REPORT.pdf` (115,582 kWh/yr from 6.5 kWp is physically impossible). Publish instead a PVGIS- or TMY-based table containing: annual POA irradiation, annual generable energy, performance ratio, monthly PV/genset energy split, and the December balance. Keep the 585/540 = 1.083 scaling factor — it is defensible for an area-identical, efficiency-only module change — but state it as ±1 %. *(Owner: PV engineer)*
12. **State the December energy balance explicitly in the TD**, so bidders and the genset supplier size to it: 7.02 kWp yields **560–600 kWh** against an **878 kWh** December load, a **280–320 kWh deficit (32–36 %)**; the genset is a structural part of the December supply, not a stand-by. *(Owner: PV engineer)*

**Requires clarification or additional data before contract award (YELLOW):**

13. Delete or substantiate the word *"bifacijalni"* on Prilog III p.2. *(F-11)*
14. Obtain site snow-depth statistics and re-evaluate the low support (bottom edge +0.50 m) against burial of the lower module row; consider high support 21540480 or the Snowy Ground Support 21540475; specify a winter clearing regime in the O&M scope. *(F-12)*
15. Obtain written Huawei confirmation of the module range for supports 21540460/21540461, given the Table 2-1 vs Table 3-24 conflict in Issue 07. *(F-13)*
16. Add a lightning-protection compliance statement: dimension the array on S-02 relative to the 38 m tower, confirm it lies inside the 45° protective cone at the corrected +3.74 m top height, and add the 0.5 m PV-cable-to-down-conductor separation. *(F-14)*
17. Insert the numeric earthing limit **≤ 10 Ω** into BOQ LOT 2 item 5.8; change the support earthing conductor from H07V-K to a UV-resistant type (H07Z-K 25 mm² Y/G) and specify the Huawei M8×35 ground bolt as the connection point. *(F-15)*
18. Decide whether the 5.40 × 5.40 m RC platform (BOQ item 2.7) is required in addition to the four strip footings; if yes, re-dimension it to the real 8.2 × 3.3 m array footprint; if no, delete it. *(F-16)*
19. Publish the site basic wind velocity v<sub>b,0</sub> and terrain category in the TD, and re-word BOQ item 2.3 so that 31 m/s is identified as the **support's capacity**, not the site's wind. Include the 3-s-gust ⇄ 10-min-mean conversion table from F-17. *(F-17)*
20. Bound the "equivalent module" clause in BOQ B19 (integrated optimizer, I<sub>out</sub> ≤ 15 A, 2278 × 1134 × 30 mm ±10 mm) and add the maximum string open-circuit voltage (≤ 435 V DC at the iSSU, ≤ 500 V DC at the PVDB, at −25 °C). *(F-18)*
21. Confirm the cabinet variant and its low-temperature (heater) option against the site design minimum temperature; ICC330-H1 is rated only to −20 °C. *(F-19)*
22. Re-word the corrosion-protection and fastener clauses (BOQ B22, B26) so that a genuine Huawei kit can comply. *(F-20)*
23. Add the PV antitheft kit (nuts 21540036, wrench 21540038) and the antitheft alarm cable to BOQ item 1.1, and add PV-theft alarm forwarding to the SCADA scope in LOT 2 item 6.2. *(F-21)*
24. Show the PVDB position on drawing S-02 and verify the 100 m DC cable quantity against it. *(F-22)*
25. Delete or complete the empty BOQ LOT 1 rows 2.6 and 2.8. *(F-23)*
26. Supply the missing design inputs listed in F-24 (wind, snow, geotechnics, temperature extremes, irradiation dataset, module datasheet) as an annex to the TD. *(F-24)*

---

## 6. Tilt Trade-Off Study (answer to the tilt question)

**Method:** HDKR anisotropic-sky transposition, monthly-mean-day integration, ground albedo ρ = 0.20, south-facing, latitude 42.9448° N, calculated for this site. Ratios are insensitive to the absolute irradiation level assumed; the absolute figures assume an annual GHI of 1,500–1,606 kWh/m².

| Tilt | Annual POA vs 45° | **December POA vs 45°** | Nov–Feb POA vs 45° | Huawei wind rating (3-s gust) | Equivalent v<sub>b,0</sub> (10-min) |
|---:|---:|---:|---:|:--:|:--:|
| 15° | −6.3 % | **−32.7 %** | −29.1 % | 40 m/s | ≈27–28.5 m/s |
| 25° | −1.9 % | **−19.7 %** | −17.2 % | 40 m/s | ≈27–28.5 m/s |
| 35° | **+0.2 %** | **−8.7 %** | −7.4 % | 35 m/s | ≈23–25 m/s |
| 40° | +0.4 % | −4.0 % | −3.4 % | *not offered* | — |
| **45° (tendered)** | **0 (ref)** | **0 (ref)** | **0 (ref)** | **31 m/s** | **≈21–22 m/s** |
| 50° | −0.9 % | +3.4 % | +2.8 % | *not offered* | — |

**Reading of the result.** At 42.94° N the annual optimum is ≈38–40° and the annual curve is essentially flat between 34° and 45°. **There is therefore no meaningful annual-yield penalty for reducing the tilt from 45° to 35° — the annual yield actually rises by 0.2 %, and 25° costs only 1.9 % annually.** Anyone trading tilt against wind on *annual* grounds is trading nothing.

The real cost is seasonal and it falls exactly where this off-grid site is weakest. December solar noon elevation at Sjednica is 90 − 42.94 − 23.44 = **23.6°**, so the December-optimal tilt is ≈66°; 45° is already 21° short of it, and every degree removed makes the December deficit of F-10 worse.

**Recommendation if 45° proves non-compliant on wind:**

- **Go to 35°.** Wind capacity rises from 31 to 35 m/s 3-s gust (+13 % in velocity, **+27 % in pressure**), at zero annual yield cost and **−8.7 % December energy** (≈50 kWh in December, ≈65 kWh over Nov–Feb). The December deficit widens from ≈300 kWh to ≈350 kWh, i.e. roughly **+10–15 genset hours per year** — a cheap and entirely acceptable price for structural compliance. This is the recommended fallback.
- **Go to 25° only if the structural check demands the full 40 m/s rating.** The cost is **−19.7 % December** (≈115 kWh) and **−17.2 % Nov–Feb**, i.e. roughly **+35–50 genset hours per year**. Acceptable, but it should be a deliberate decision recorded in the design.
- **Do not go to 15°.** It buys nothing over 25° structurally (both are rated 40 m/s, PVM Table 3-29 p.80) and costs a further 13 percentage points of December energy.
- **Do not exceed 45°** — the Huawei support offers no tilt above 45° (PVM p.174, raking-strut hole positions 15L/25L/35L/45L) and, at 50°, gains only 3.4 % in December while losing 0.9 % annually.

**Caveat for the structural reviewer:** if the site v<sub>b,0</sub> turns out to be in the 25–30 m/s range typical of the East Herzegovina mountains, then **even 15°/25° (40 m/s ≈ 27–28.5 m/s v<sub>b,0</sub>) is marginal at 1076 m once the altitude factor c<sub>alt</sub> is applied**, and no standard Huawei A-shaped tilt will pass. In that case the answer is not a shallower tilt but a **site-specific reinforced support and foundation**, which GSD p.3 explicitly anticipates for mountain-peak sites, and the tilt should then stay at **45°** to preserve the winter yield.

---

## 7. Lessons Learned

1. **The civil quantity take-off (BOQ items 2.1–2.3) is exemplary.** Every figure traces to the manufacturer's foundation sheet, down to the 0.094 m³ blinding layer and the 19.53 kg of rebar per strip. This should be the template for future Huawei ground-support tenders — *provided* the correct low/high sheet is used.
2. **Never derive an array footprint from a structural member.** The 2590 mm error in this tender comes entirely from treating the 3656 mm longitudinal beam as the module field. The module field is always *n* × module length + gaps, and it deliberately overhangs the beam (here by 450 mm at each end). Always cross-check with the clamp count: it is a closed arithmetic identity (2 clamps of each type per crossbeam per module column boundary) and it caught the correct 2 × 3 arrangement here in one line.
3. **Always cite the Huawei BOM number, never the marketing name.** Huawei has shipped three "A-shaped low support" generations under near-identical names with a 335 W → 585 W capability spread, and Issue 07 of the manual contradicts itself on the middle one (F-13).
4. **Check the manufacturer's own configuration matrix first.** PVM Table 2-3 Configuration 7 answers, in five lines, which support, which SJB, which SSU and which modules are permitted for iSitePower-A. Reading it first would have prevented findings F-01, F-05 and F-18.
5. **A quoted BOQ from the vendor is the highest-quality evidence in a package like this** — it settled the ICC360 vs ICC330 vs MTS9302 question (F-04) and the 540 vs 585 Wp question (F-09) in minutes, and it should be circulated to every reviewer at the start.
6. **Sanity-check every simulation output against the irradiation ceiling.** 17,782 kWh/kWp/yr should have been caught by inspection: the plane-of-array irradiation at any European site is ≈1,000–2,000 kWh/m²/yr, so specific yield can never plausibly exceed ≈1,800 kWh/kWp.

---

*End of Review 01 — Huawei PV / Solar Scope, Rev 01, 2026-08-07.*
