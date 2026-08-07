# Genset data sheet received — corrections to the electrical review

Rev 1 · 2026-08-07 · Rusmir Skopljak, dipl. ing. el.

The Investor supplied the full FG Wilson technical data sheet
(`EQUIPEMENT/GENSET/P22-6_FG_Wilson_full_datasheet_2019-08-14.pdf`, 6 pages,
Caterpillar (NI) Ltd, issue 2019-08-14). It closes finding **O-4** of the delta review.

It also **overturns the electrical review's headline finding.** `03-electrical.md` was
written without this document — the package contained only a three-page web printout
with no text layer — so its ventilation and exhaust findings were derived from
first-principles estimates. The measured data shows those estimates were substantially
wrong, and in the conservative direction: the tendered design is adequate.

**This file overrides `03-electrical.md` wherever they conflict.**

---

## 1. Manufacturer data (50 Hz standby, the governing rating)

| Item | Value |
|---|---|
| Rating | 22 kVA / 17,6 kW standby · 20 kVA / 16 kW prime, 400/230 V |
| Engine | Perkins 404D-22G, 4-cyl in-line, **naturally aspirated**, 1500 rpm, 2,2 l |
| Alternator | FG Wilson FGL10060, **SHUNT** excitation, IP23, insulation class H |
| **Skid dimensions** | **1550 × 620 × 1020 mm** |
| **Mass** | **378 kg dry · 385 kg wet** |
| **Radiator cooling airflow** | **1980 m³/h** (33 m³/min) |
| **Max external restriction to cooling airflow** | **125 Pa** |
| Combustion air flow | 90 m³/h (1,5 m³/min); max intake restriction 3 kPa |
| Heat rejected to water + lube oil | 19,6 kW |
| Heat radiated to room | 7,1 kW |
| **Exhaust gas flow** | **234 m³/h** (3,9 m³/min) at **505 °C** |
| **Max allowable back pressure** | **10,2 kPa** |
| Fuel consumption, 100 % standby | 5,9 l/h → **500 l gives ≈85 h** |
| Ambient capability | up to 50 °C |

---

## 2. What this changes

### 2.1 EL RED-01 "ventilation grossly undersized" — **WITHDRAWN**

The review computed a radiator demand of **4250 m³/h** from an assumed 15 kW at a 12 K
rise. The manufacturer figure is **1980 m³/h** — the review **overestimated by 2,1×**.

It also misread the arrangement. BOQ LOT 2 items 4.6–4.9 specify a conventional ducted
layout, not a fan-cooled room:

| BOQ item | What it is |
|---|---|
| 4.6 | sheet-metal duct ≈6 m² carrying radiator discharge out of the container |
| 4.7 | fixed louvre **600 × 600 mm** at the end of that duct |
| 4.8 | fresh-air intake louvre **500 × 700 mm** |
| 4.9 | axial fan **1200 m³/h**, thermostat, interlocked to genset start — explicitly *"minimalna potrebna ventilacija prostora iznosi 120 m³/h (6 izmjena zraka na sat)"* |

The radiator's **own** fan moves the 1980 m³/h through duct 4.6 to louvre 4.7. Item 4.9
is a **supplementary room-ventilation** fan, and the 120 m³/h it cites is a room
air-change minimum. The review treated 1200 m³/h as the cooling path ("3,5× short") and
120 m³/h as a cooling figure ("35× short"). Both readings were mistaken.

Checked against the manufacturer's own 125 Pa budget, with air density 1,09 kg/m³ at
1076 m (an 8 % mass-flow derate, so 2151 m³/h volumetric):

| Path | Free area | Velocity | Δp |
|---|---|---|---|
| Intake 500 × 700 (≈50 % free) | 0,175 m² | 3,4 m/s | ≈16 Pa |
| Discharge 600 × 600 (≈50 % free) | 0,180 m² | 3,3 m/s | ≈15 Pa |
| Duct ≈6 m² | — | — | ≈20–40 Pa |
| **Total** | | | **≈50–70 Pa against a 125 Pa limit — PASSES** |

**The tendered louvres are adequate.** The 1200 × 800 intake and 900 × 800 discharge
that this revision briefly specified were derived from the review's inflated figure and
have been **reverted to the tendered sizes** on M-01 and S-02. Retaining them would have
inflated the tender for no engineering reason.

### 2.2 EL RED-04 "exhaust DN 50 is a scaling error" — **DOWNGRADED to YELLOW**

The review assumed the back-pressure limit; the data sheet states **10,2 kPa**.

| | Velocity | Pipe Δp (6 m) | With industrial silencer | vs 10,2 kPa |
|---|---|---|---|---|
| **DN 50 (tendered)** | 33,1 m/s | ≈600 Pa | ≈2,6 kPa | **PASSES** |
| DN 65 | 19,6 m/s | ≈160 Pa | ≈2,2 kPa | passes |
| DN 80 | 12,9 m/s | ≈60 Pa | ≈2,1 kPa | passes |

DN 50 is **compliant on back pressure with a ~4× margin**. The one valid reservation is
velocity: 33 m/s exceeds the customary ≤30 m/s guide for noise and erosion. **DN 65 is
therefore a recommendation, not a correction** — stated that way on M-01.

### 2.3 EL RED-07 / CON R-08 floor loading — **numbers corrected**

The review assumed 1350 kg over 2,0 m². Actual:

| | Mass | Footprint | Pressure |
|---|---|---|---|
| Genset, wet | 385 kg | 1,550 × 0,620 = 0,96 m² | **3,93 kN/m²** |
| Tank, 500 l full | ≈500 kg | 1,20 × 0,70 = 0,84 m² | **5,84 kN/m²** |
| **Combined** | **885 kg** | | (review assumed 1350 kg) |

Both are below the 10,00 kN/m² design value in the container brief, though the
construction review disputes that value and derives 2,00 kN/m². The spreader grillage
is retained as a **recommendation** to distribute point loads under the skid rails —
its wording on M-01 was softened from "OBAVEZAN" accordingly. **The static check still
has to be done against the real floor capacity**; what has changed is that the load is
now known and is modest.

### 2.4 CON R-09 access — **RESOLVED**

The skid is **620 mm wide** against a **900 mm** container door: **280 mm clearance**,
and 1020 mm high against a 2000 mm door. It goes through the existing opening
lengthwise. **No roof-panel removal, wall opening or split delivery is required**, and
the tender need not provide for any. Noted on M-01.

### 2.5 Findings that STAND

| Finding | Why it survives |
|---|---|
| EL **RED-03** exhaust/hot-air discharge aimed at the outdoor cabinets | Unaffected by flow rate. A 505 °C plume and 1980 m³/h of warm air still discharge on the north wall, where the ICC330-H1 and MTS9302 stand. Route the exhaust above roof level and away from them. |
| EL **RED-05** fire | 500 l of diesel in an enclosed space still needs a fire elaborate, detection, a fire-safe shut-off valve and bunding. |
| EL **RED-09/RED-10** protection and earthing of the island supply | Confirmed and reinforced: the data sheet states **SHUNT** excitation, so sustained short-circuit current really is limited and "Short Circuit Capacity 0 %" is printed on page 4. Automatic disconnection to IEC 60364-4-41 cannot be achieved by overcurrent alone — **RCD protection is mandatory**, and deleting the certified GRO's 40 A/30 mA RCD was a genuine regression. |
| EL **RED-12** surge protection | Unaffected. |
| CON **R-01** wind | Unaffected — a different scope. |

---

## 3. Lesson

The review that reached the most alarming conclusion was the one working from the least
data, and it erred consistently on the conservative side — 2,1× on cooling air, 1,5× on
mass, and an exhaust limit assumed rather than read. Estimates degrade quietly: nothing
in the review's own output signalled that its inputs were guesses.

Two safeguards worked. The review flagged the missing data sheet itself, which is why it
was requested; and the delta review carried it as open finding **O-4** rather than
letting a specification stand on estimated numbers. **Where a document specifies
equipment, the manufacturer's data sheet belongs in the tender pack** — it is now filed
at `EQUIPEMENT/GENSET/P22-6_FG_Wilson_full_datasheet_2019-08-14.pdf` and should be
issued to bidders as a reference document.
