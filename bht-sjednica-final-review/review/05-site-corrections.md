# Site corrections from the Investor — and what they change in the reviews

Rev 1 · 2026-08-07 · recorded by Rusmir Skopljak, dipl. ing. el.

The three expert reviews were produced from the documents alone. The Investor, who
knows the site, supplied two corrections of fact. Documented facts beat inference,
so the affected findings are amended here. **This file overrides the three reviews
where they conflict.**

---

## C-1 — The container is EMPTY

**Investor's statement:** there is no equipment inside the container.

The electrical review inferred a fully occupied container from the *type* container's
as-built drawings (Prilog III p.21, drawing 3.5.3 "raspored opreme", showing GRO, UPS,
UPS-R, RBS_1, RBS_2, PRENOS, ROS, TZ, MPU, klima). Those are the **generic BH Telecom
K3 type drawings**, not a survey of this site — which is exactly the caveat printed on
the last page of Prilog III itself ("Nacrti kontejnera K3 dati u ovom Prilogu
predstavljaju TIPSKU izvedbu"). The reviewer treated a type drawing as an as-built.

| Finding | Status | Effect |
|---|---|---|
| **EL RED-06** "It does not fit — 6.29 m² fully occupied, bund alone needs 2.65 m²" | **WITHDRAWN** | With an empty 6.29 m² floor, the genset skid and the 500 l tank fit. Spatial feasibility must still be proved by the bidder's installation elaborate against the **real** measured plan, but it is no longer a blocker. |
| **EL RED-02** "container reaches 55 °C, outside ETSI class 3.1/3.2 for the RBS/PRENOS/ROS" | **DOWNGRADED to YELLOW** | No TK equipment is present to overheat. The temperature rise still matters for the genset's own air intake and for anything installed later, but it is no longer a safety-of-service issue. |
| **EL RED-03** "openings on the north wall blow hot air at the ICC330-H1 + MTS9302" | **STANDS** | Those cabinets are **outdoor**, on the north wall — unaffected by the container being empty. Exhaust re-ingestion and hot-air impingement on the rectifiers and LFP batteries remain real. |
| **EL RED-05** fire — diesel sharing a space with live TK equipment | **AMENDED, still RED** | The Class-E/BONPET premise falls away with no TK equipment. But 500 l of diesel in an enclosed space still requires a fire elaborate, detection, a fire-safe shut-off valve and bunding under BiH fire regulations. The *reason* changes; the requirement does not. |
| **EL finding 15** "put the genset in its own enclosure outside" | **NOT ADOPTED** | Its main justifications were spatial conflict and TK equipment. Both are void. Installing in the existing empty container — the tender's original intent — is retained. |

**Still outstanding regardless:** the ventilation sizing (EL RED-01) and the exhaust
diameter (EL RED-04) are properties of the **engine**, not of what else is in the room.
A 15 kW radiator still needs ~4 250 m³/h and DN 65–80. Those stand unchanged.

---

## C-2 — Snow does not govern

**Investor's statement:** snow is not a problem at this location.

Physically consistent, and the reason is the same phenomenon that makes the wind
severe: an exposed Herzegovinian peak ~30 km from the Adriatic, in the bura belt, is
**wind-scoured** — snow does not accumulate where gusts reach 45 m/s. A ground snow
load derived from a regional map does not describe a site that the wind sweeps clean.

| Finding | Status | Effect |
|---|---|---|
| **CON R-05** "the LOW support with a +0,50 m bottom edge will be buried; wind and snow requirements conflict" | **WITHDRAWN as governing** | The conflict dissolves. Snow no longer argues for a steep tilt. |
| **CON A-02** "the correct combination is a steep tilt (40–45°) — best for snow shedding" | **SUPERSEDED** | With snow not governing, the steep tilt loses its main justification, and tilt becomes a pure **wind-vs-yield** decision. See below. |

This is the important consequence: **the option of lowering the tilt is now open.** It
was previously argued down on snow grounds. Per the Huawei review's own trade study,
25° costs only ≈1.9 % of annual yield, and 35° costs ≈0.2 %.

---

## C-3 — Wind: what the options actually are

Certified site design pressure, from BH Telecom's own archive for this location:
**q = 1.10–1.20 kN/m²**, i.e. a **45–47 m/s** three-second gust at ρ = 1.0904 kg/m³
(1076 m). Manufacturer's rated capacity for the Standard A-shaped support 3.0:

| Tilt | Rated gust | Capacity | % of site 1.20 kN/m² | Shortfall |
|---|---|---|---|---|
| 15° / 25° | 40 m/s | 0.87 kN/m² | 73 % | **+38 % needed** |
| 35° | 35 m/s | 0.67 kN/m² | 56 % | +80 % needed |
| **45° (tendered)** | **31 m/s** | **0.52 kN/m²** | **44 %** | **+129 % needed** |

**Conclusion: the frame is the binding constraint, not the foundation.** Lowering the
tilt from 45° to 25° buys a genuine **+66 %** in rated capacity — the single largest
improvement available — but still leaves 38 % missing. No catalogue tilt is compliant,
which is what CON R-01 concluded, and lowering the tilt does not by itself rescue it.

Foundation, for context — 6-module support at 1.20 kN/m² on 15.91 m² of sail:

- uplift ≈ **19.1 kN**; dead weight of frame + modules only **3.4 kN**
- the foundation must therefore supply ≈ **15.7 kN**
- by gravity alone that is ≈0.65 m³ of concrete against the tendered 0.81 m³ — which
  looks adequate until partial factors are applied (γ_Q = 1.5 on wind, γ_G,fav = 0.9
  on the resisting dead load), at which point it is not. This is the factor-of-≈2
  deficit CON R-04 reports.

### The four levers, ranked by effect

1. **Specify the load, not the product** *(recommended — no redesign needed by the Investor)*
   The tender must state **q_p ≥ 1.20 kN/m²** and require a static calculation signed
   by a licensed engineer **with the offer**, not after award. Bidders then supply a
   structure that actually meets it — "Huawei ground support **ili ekvivalent**" stays,
   but the equivalence is measured against the real site load instead of a catalogue
   latitude table. This converts an unbuildable specification into a buildable one
   without the Investor designing anything.

2. **Halve the sail per structure — 3 supports × 4 modules instead of 2 × 6**
   Sail per structure drops from 15.91 m² to 7.95 m² (**−50 %**), and with it the
   uplift and the overturning moment. 12 modules and 7.02 kWp are unchanged. Three
   smaller, lower structures are far easier to make compliant than two large ones, and
   the plot has room. Cost rises modestly (one more foundation pair and anchor set).

3. **Drop the tilt to 25°** — now that snow does not object
   **+66 %** rated capacity for **−1.9 %** annual yield. It does not achieve compliance
   alone, but it removes more than half the deficit and makes levers 1 and 2 far
   cheaper to satisfy.

4. **Rock anchors instead of gravity foundations**
   The site is karst limestone. Anchors bonded into rock resist uplift — the actual
   failure mode — far more efficiently than concrete mass, and are typically cheaper
   than the enlarged gravity blocks they replace. This addresses the foundation half of
   the problem and suits the ground conditions the BOQ already describes as "kamenito tlo".

**Also required regardless:** Huawei's own installation drawing states that *"in some
particular scene, such as island and mountain peak, site designer should recheck the
foundation design and modify the drawing"* (GroundSupport_drawing p.3). BS Sjednica is
literally a mountain peak. **Written site-specific confirmation from the manufacturer
should be a condition of award.**

### What is being done in this revision

Per the Investor's instruction (option 1): every objective error is corrected and the
full document set re-issued, and **no redesign is invented**. The tender is amended to
state the real site wind load and to require a certified static calculation pre-award,
so that the structural decision is placed where it belongs — with a licensed structural
engineer working to the actual site data — rather than being silently frozen at a
non-compliant catalogue value.
