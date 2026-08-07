# Delta review — BS Sjednica (Bileća) tender package, Rev. 1

Per `prompt.md` §6. Compares the re-issued package against the state recorded in
`TD-OUTPUT-BASELINE-20260807/`. Only changes since the last review are listed.

**Date:** 2026-08-07 · **Reviewer:** Rusmir Skopljak, dipl. ing. el.
**Inputs:** `01-huawei-solar.md`, `02-construction.md`, `03-electrical.md`,
`05-site-corrections.md` (Investor's corrections of fact), `00-change-log.md`.

---

## 1. Executive summary

**Risk level: MEDIUM** (was HIGH in all three Rev. 0 reviews).

> **Rev. 1a, same day.** The Investor supplied the full FG Wilson data sheet after this
> review was drafted. It closes **O-4**, withdraws **O-2** and resolves the access
> question — the electrical review's ventilation and exhaust findings were derived from
> estimates that the measured data shows were 2,1× conservative, and the tendered design
> is adequate. See `06-genset-datasheet.md`; M-01 and S-02 were reverted accordingly.

Every defect that could be closed by correcting a document has been closed, and the
package is now internally consistent: the automated cross-document check reports
**0 failures against 7 at baseline**. The residual risk is no longer documentary — it
is a **single unresolved engineering question**, the wind capacity of the PV support,
which the tender now states openly and places on the bidder's certified structural
engineer instead of silently freezing at a non-compliant catalogue value.

Two Rev. 0 RED findings were **withdrawn** on the Investor's evidence: the container is
empty, so the "does not fit" and "TK equipment overheats" findings do not apply. They
were inferred from the generic K3 **type** drawings, which Prilog III itself labels as
typical rather than as-built.

---

## 2. What changed, by severity

### 2.1 RED findings closed

| Finding | Was | Now |
|---|---|---|
| **A** Izjava docx corrupt | Undeliverable — no `[Content_Types].xml`, 3 dangling relationships. Word offered recovery; LibreOffice refused. | Repaired. All 4 docx load, 0 uncovered parts, 0 dangling relationships. |
| **B** Panel geometry wrong by 650 mm | Projection derived from the 3656 mm beam → 2590 mm, top edge +3,09 m | Derived from the module field → **3236 mm**, top edge **+3,74 m**, overshoot **1,84 m**. Corrected in the BOQ, S-02, S-03 and Prilog III. |
| **F** 13,5 kVA in Table 1 | Contradicted 22 kVA everywhere else | Single value package-wide: **22 kVA** (20 mentions, 0 conflicts). |
| **E** Container size | Three different sizes across the package | Single value: **3005 × 2300 mm** external, from the certified project and self-proving via its own 6,29 m² / 10,13 m annotations. |
| **I** BOQ item 2.7 | Priced a 5,40 × 5,40 m slab that already exists | Deleted. Removes ≈1 500–2 500 KM of phantom cost from a 15 000 KM LOT. |
| **J** No total for a LOT-1-only bid | Recap, discount and VAT existed only on LOT 2 | LOT 1 recap added; both bidder paths verified arithmetically by recalculation. |
| **H** Template leftovers | Towing trailer ×3, multi-location clause, fence extension, unresolved reference site | All gone, verified by automated check. |
| HW **F-01** Support unidentified | No BOM number; the named family does not accept 585 W | **21540481** + anchors **21540482** specified. |
| HW **F-05** PVDB wrong | Demanded IP65 with an integral type 2 SPD; the Huawei unit is IP55 with none | Corrected to IP55; SPD split into new item 1.6a. |
| HW **F-06** Cable/terminal | 6 mm² everywhere; iSSU terminal requires 4 mm² | Noted in item 1.5. |
| EL **RED-13** Earth conductor | H07V-K 25 mm² — indoor conduit wire, below EN 62305-3 | Cu 50 mm², UV/burial rated, bimetallic joints, R ≤ 10 Ω. |
| **L** Yield statement | Quoted a 12 × 540 Wp base that implies ~12× impossible specific yield | Replaced: 10,1–10,9 MWh/yr, December 560–600 kWh vs 878 kWh load. |

### 2.2 RED findings withdrawn on the Investor's evidence

| Finding | Why withdrawn |
|---|---|
| EL **RED-06** "the genset does not fit" | Container is **empty**. The 6,29 m² floor is free; the finding assumed the K3 type drawing's equipment layout was as-built. |
| EL **RED-02** "container reaches 55 °C, outside ETSI class for the RBS/PRENOS/ROS" | No TK equipment present. Downgraded to YELLOW — the temperature rise still matters for the genset's own intake air. |
| CON **R-05** "snow buries the low support; wind and snow conflict" | Investor's site knowledge: snow does not accumulate on this wind-scoured Adriatic-facing peak. Physically consistent with a 45 m/s bura site. The conflict dissolves and **tilt reduction becomes available**, which Rev. 0 had ruled out on snow grounds. |

### 2.3 RED findings that remain OPEN — the Investor must decide

| # | Finding | Status |
|---|---|---|
| **O-1** | **CON R-01 — no catalogue tilt is wind-compliant.** Site qp = 1,10–1,20 kN/m² (≈45 m/s); the support rates 0,52 kN/m² at 45° and 0,87 kN/m² at 15°/25°. Even the best tilt is **38 % short**. | **Stated openly** in BOQ 1.1/1.3, on S-02 and on S-03. The tender now requires a certified static calculation for qp ≥ 1,20 kN/m² **with the offer**. Not silently designed around. |
| **O-2** | ~~EL RED-01/RED-04 ventilation and exhaust undersized~~ | **WITHDRAWN — see `06-genset-datasheet.md`.** The manufacturer data sheet arrived after Rev. 1 was drafted. Radiator demand is **1980 m³/h**, not the 4250 the review estimated (2,1× over), and the tendered louvres pass comfortably inside the 125 Pa budget. DN 50 meets the 10,2 kPa back-pressure limit with ~4× margin. M-01 and S-02 have been **reverted to the tendered sizes**. |
| **O-3** | **CON R-08 — container floor.** The 10,00 kN/m² design figure is disputed by the construction review, which derives 2,00 kN/m². | Loads now known: genset **3,93 kN/m²**, full tank **5,84 kN/m²**, combined mass **885 kg** (the review assumed 1350 kg). Grillage retained as a recommendation. **The static check against the real floor capacity is still open.** |
| **O-4** | ~~Genset technical data absent~~ | **CLOSED.** The Investor supplied the full FG Wilson data sheet (2019-08-14), now filed at `EQUIPEMENT/GENSET/P22-6_FG_Wilson_full_datasheet_2019-08-14.pdf` and analysed in `06-genset-datasheet.md`. It should be issued to bidders as a reference document. Closing it also resolved **O-2** and CON R-09 (access). |
| **O-5** | **EL RED-09/RED-10 — protection and earthing of an island supply.** Automatic disconnection cannot be demonstrated with a SHUNT-excited generator and C32 breakers; the certified project's N–PE bond sits in a PMO whose source no longer exists. | Principles stated on E-01 notes 2 and 4. **A revision of the certified electrical project is not procured by this tender** and should be. |
| **O-6** | **EL RED-05 — fire.** 500 l of diesel in an enclosed space still requires a fire elaborate, detection, a fire-safe shut-off valve and bunding, even with no TK equipment present. | Open. Not yet a BOQ item. |

---

## 3. Verification results

All seven checks from the plan, re-run on the re-issued package.

| # | Check | Result |
|---|---|---|
| 1 | `soffice --headless --convert-to txt` on all four docx | **4/4 OK** (baseline 3/4) |
| 2 | OPC integrity — `[Content_Types].xml` present, every part covered, no dangling relationships | **4/4 OK**, 0 uncovered, 0 dangling |
| 3 | BOQ recalculated through LibreOffice with injected unit prices | LOT 1 13.873,00 + LOT 2 65.100,00 = **78.973,00**; PDV **13.425,41**; total **92.398,41**; LOT-1-only path **16.231,41** — all correct |
| 4 | DWG readable by a real DWG engine (ODA round-trip + ezdxf) | **5/5 OK**, all header **AC1024**, 25 layers each, diacritics intact |
| 5 | PDF page geometry and size | Prilog III **36 p, 10,94 MB** (was 79,6 MB), 33 A3 pages; Situacija **5 p, 2,45 MB**; all sheet plots **420 × 297 mm** |
| 6 | Cross-document consistency | **0 failures** (baseline 7) |
| 7 | This delta review | complete |

### 3.1 Prilog III optimisation — lossless, verified

79,6 MB → 10,94 MB (**86 % smaller**) with **no rasterisation**. The bulk was not the
CAD geometry as assumed but **full un-subsetted Arial Regular and Arial Bold embedded
17 times (16,64 MB)** in a file whose streams were never deflated. Font bytes now
0,39 MB. Verified across all 34 original pages: identical extracted text, identical
drawing-object counts, identical image counts, identical page geometry, and pages 6,
12, 17, 29 and 31 **pixel-identical at 100 dpi**. Every page remains vector and
searchable.

---

## 4. Known limitations of this revision

Stated plainly rather than left to be discovered:

1. **The sheet PDF plots carry no selectable text.** ezdxf's PDF backend converts
   glyphs to filled paths to guarantee the plot matches the CAD exactly; it offers no
   native-text option. The **DWG and DXF carry real `TEXT` entities** (S-01 alone has
   50, of which 23 contain diacritics), so nothing is lost for CAD use — only PDF text
   search on those five sheets.
2. ~~The P22-6 skid dimensions on M-01 are indicative~~ — **superseded**: the real
   data sheet gives **1550 × 620 × 1020 mm, 385 kg wet**, now carried on M-01 and in
   `design.json`.
3. **Cardinal orientation** rests on Prilog III: the certified site drawing carries no
   north arrow. It corroborates that the container door and the compound gate share a
   face, which is consistent, but the site visit required by TD §3.2 should confirm it.
4. **The investment-plan reference in the Izjava** still cites the generator programme
   line (§1.3 of the change log). Deliberately left for the Investor — which budget line
   a procurement is booked against is a finance decision.
5. **Two of the three Rev. 0 reviews were written before the Investor's corrections.**
   `05-site-corrections.md` overrides them where they conflict; the original text is
   retained unedited so the reasoning chain stays auditable.

---

## 5. Lessons learned

0. **An estimate does not announce itself as one.** The review that reached the most
   alarming conclusion was the one working from the least data, and it erred
   consistently conservative — 2,1× on cooling air, 1,5× on mass, an exhaust limit
   assumed rather than read. What saved it was that the missing data sheet was itself
   recorded as an open finding rather than quietly worked around; requesting it
   collapsed four findings at once. Where a document specifies equipment, the
   manufacturer's data sheet belongs in the tender pack.
1. **The Investor's own archive answered the decisive question.** The site wind
   pressure did not need a new study — the certified BS Sjednica project and the
   type-container brief both carry it, and a first-principles EN 1991-1-4 check
   reproduces it to within 0,5 %. Mine the certified project before commissioning
   analysis.
2. **A type drawing is not an as-built.** Two RED findings rested on reading the generic
   K3 layout as this site's reality, against Prilog III's own printed warning. Where a
   review depends on site state, confirm the state.
3. **Automated consistency checking earns its cost immediately.** It caught the 13,5 kVA
   Table 1 entry, three container sizes and the surviving template leftovers on the
   first run, and it is what makes "0 failures" a fact rather than a claim.
4. **Verify by recalculating, not by reading.** Deleting three BOQ rows silently broke a
   cross-sheet reference and dropped LOT 1 out of the tender total; the first repair
   then introduced double VAT. Neither was visible by inspecting the file — only by
   computing it.
5. **Measure the file before optimising it.** The plan budgeted for rasterising heavy
   CAD pages; measurement showed duplicated fonts instead, and the correct fix was
   lossless and took seconds.
6. **"The contractor shall confirm feasibility" is not a specification.** Where the
   baseline could not resolve wind, access, floor capacity or spatial fit, it transferred
   the unknown to the bidder. Under a lowest-price award that reliably produces either a
   non-compliant offer or a post-award claim.

---

*End of delta review — Rev. 1, 2026-08-07.*
