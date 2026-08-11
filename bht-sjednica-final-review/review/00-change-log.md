# Change log — BS Sjednica (Bileća) tender package

Revision 1 · 2026-08-07 · Rusmir Skopljak, dipl. ing. el.
Revision 2 · 2026-08-11 · airflow relayout and closure of the open items in
`07-calculations.md` §G — see the Revision 2 section at the end of this file.

Baseline of the pre-change state: `bht-sjednica-final-review/TD-OUTPUT-BASELINE-20260807/`
(byte-for-byte copy of TD-OUTPUT as of 2026-08-07, before any edit).
**Note:** since Rev 2 this folder is kept in sync with TD-OUTPUT as the delivery
copy; the pre-change state is the git history of Rev 1, not this folder.

Format: **file** · location · before → after · reason · source.

---

## 1. `4. Izjava o stanju zaliha BS Sjednica.docx` — package repair

### 1.1 Missing `[Content_Types].xml` — RED, fixed

| | |
|---|---|
| **Location** | OPC package root |
| **Before** | Part absent. The archive held 26 entries and no `[Content_Types].xml`. |
| **After** | Rebuilt with 4 `Default` entries (`rels`, `xml`, `jpeg`, `png`) and 18 `Override` entries, enumerated from the parts that actually exist in the package. |
| **Reason** | ECMA-376 Part 2 §10.1.2 makes the Content Types stream mandatory. Without it Word reports "unreadable content" and offers recovery; LibreOffice refuses outright (`Error: source file could not be loaded`). The document was undeliverable. |
| **Source** | `zipfile.ZipFile(...).namelist()`; `soffice --headless --convert-to txt` failing only on this one of the four docx files. |

### 1.2 Three dangling `customXml` relationships — RED, fixed

| | |
|---|---|
| **Location** | `word/_rels/document.xml.rels` (rId1, rId2, rId3) and `customXml/_rels/item{1,2,3}.xml.rels` |
| **Before** | `document.xml.rels` pointed at `../customXml/item1.xml`, `item2.xml`, `item3.xml`; all three targets were absent, as were `itemProps{1,2,3}.xml`. The three `customXml/_rels/*.rels` orphans pointed at the equally absent itemProps. |
| **After** | The three relationships and the three orphan `.rels` parts removed. Package is now internally consistent: every relationship resolves to a part that exists. |
| **Reason** | An OPC relationship whose target does not exist invalidates the package. Two repairs were possible — import the missing parts from a sibling document, or drop the references. Dropping was chosen because the `customXml` items are a Boldon James Classifier datastore plus an empty Word bibliography; importing `item2`/`item3` from another document would have stamped **that** document's classification label and label history onto this one. Verified first that `word/document.xml` references none of rId1–rId3 (it uses only rId10–rId16), so nothing in the body is orphaned by the removal. |
| **Note** | The document's own classification is untouched — it lives in `docProps/custom.xml` (`bjDocumentLabelXML`, `bjSaver`, `docIndexRef`), which is the store the Classifier add-in reads. Opening and re-saving in Word with the add-in installed will regenerate the `customXml` datastore automatically. |
| **Source** | `word/_rels/document.xml.rels` vs `namelist()`; `docProps/custom.xml`. |

All 23 remaining parts were copied byte-for-byte, so template formatting, styles, numbering, headers, footers and both images are unchanged.

**Verification** — all four checks pass on the repaired file:

| Check | Result |
|---|---|
| `soffice --headless --convert-to txt` on all four docx | 4/4 OK (was 3/4) |
| `zipfile.testzip()` | `None` (no CRC errors) |
| `docx.Document()` opens | OK — 14 paragraphs, 1 section |
| LibreOffice PDF render | 1 page, 2 images, 2288 chars of text |

### 1.3 Content corrections

The plan reference still cited *"18.4 — Agregatska postrojenja za RR čvorišta — nove
lokacije"*, inherited from the 46-generator template. **Left as is deliberately**: it
names a real line in the Investor's approved three-year investment plan, and changing
which budget line a procurement is booked against is a finance decision, not a document
correction. Flagged for the Investor to confirm the correct plan item for a hybrid
power-supply investment.

---

## 2. `3. TD JN Hibridni sistem napajanja BS Sjednica.docx`

Nine targeted OOXML run edits (`tools/fix_td.py` + `tools/ooxml_edit.py`). The document
is never regenerated, so template styles, numbering, headers, footers and layout are
byte-identical; only the affected runs change. Every edit must match its expected
occurrence count or the whole run is refused, so template drift fails loudly.

| # | Location | Before → After | Finding |
|---|---|---|---|
| 2.1 | Tabela 1, Izvedba_snaga | `kontejner_skid_13,5kVA` → `kontejner_skid_22kVA` | **F** |
| 2.2 | §3.1.3 | `kontejner dimenzija 3,00 x 2,10 x 2,40 m … ~850 kg` → `vanjskih dimenzija 3,005 × 2,30 m (zidni paneli 60 mm, unutrašnja površina 6,29 m², obim 10,13 m) … kontejner je trenutno PRAZAN` | **E** + Investor's site correction |
| 2.3 | §3.1.3 | `…150 m², zbog čega je predviđeno proširenje postojeće ograde` → `…150 m² (16,00 × 9,40 m)` | **H** — no BOQ item existed for a fence extension |
| 2.4 | §4.5.8 | `dokumentaciju za vučnu prikolicu,` deleted | **H** — skid inside a container, no trailer |
| 2.5 | §5.2.1 | `isporučene agregate, vučnu prikolicu i prateću opremu` → `isporučeni agregat, nosače fotonaponskih panela i prateću opremu` | **H** |
| 2.6 | §5.2.2 | same, postguarantee | **H** |
| 2.7 | §8.1.2 | `Izuzetno, plaćanje … nakon uspješne implementacije FN sistema na najmanje dvije lokacije.` deleted | **H** — single-location contract |
| 2.8 | §3.1.4 | `prema rješenju primijenjenom na lokaciji Brloški Potok iz referentne tenderske dokumentacije` → `prema zahtjevima iz Priloga II i Priloga III ove tenderske dokumentacije` | EL RED-11 — the referenced document is not in the package |
| 2.9 | §1.6 | `kao FG Wilson P22-6 (Skid),` → `… (Skid) ili ekvivalent,` | ZJN art. 54 — a brand was named without "or equivalent"; §2.1 had it, §1.6 did not |

## 3. `3.1 PRILOG II TD - predmjer Sjednica Bileca.xlsx`

openpyxl edits preserving styles, merges and formulas (`tools/fix_boq.py`).

| # | Location | Change | Finding |
|---|---|---|---|
| 3.1 | LOT 1 B13 | names the actual product: **Standard A-shaped Support 3.0 — LOW, Huawei BOM 21540481**, anchors **21540482** | HW F-01 — no part number was given, and the 21540421 family does not accept 585 W |
| 3.2 | LOT 1 B23 | geometry rebuilt from the **module field**, not the beam: field 3476 × 4576 mm, **projection 3236 mm** (was 2590), **top edge +3,74 m** (was +3,09) | **B** |
| 3.3 | LOT 1 B24 | overshoot restated: top edge **1,84 m above the fence** (was "cca 0,20 m" / "0,17 m") | **B** |
| 3.4 | LOT 1 B25 | states the real site load **qp ≥ 1,20 kN/m² (≈45 m/s)** and that the catalogue support rates only 0,52 kN/m² at 45° | CON R-01 |
| 3.5 | LOT 1 B20 | tilt tied to the wind proof; 25°–35° admissible if the calculation requires it | CON R-01 + Investor's snow correction |
| 3.6 | LOT 1 B32 (1.3) | static calculation becomes a **pre-award** submission, not a post-award deliverable | CON A-03 |
| 3.7 | LOT 1 B33 (1.4) | earthing conductor `H07V-K 25 mm²` → **Cu 50 mm² UV/burial-rated with bimetallic Cu/Fe-Zn joints**, R ≤ 10 Ω | EL RED-13 — H07V-K is indoor conduit wire and below EN 62305-3 Table 7 |
| 3.8 | LOT 1 B34 (1.5) | notes the iSSU input terminal requires **exactly 4 mm²** | HW F-06 |
| 3.9 | LOT 1 B35 (1.6) | PVDB corrected to **IP55** (Huawei PVDB500-15-2B is IP55, not IP65) and the SPD split out, because that box contains none | HW F-05 |
| 3.10 | LOT 1 new 1.6a | **new item**: DC type 2 SPD per string, 2 kpl | HW F-05 / EL RED-12 |
| 3.11 | LOT 1 items 2.6 / 2.7 / 2.8 | **deleted** — 2.7 priced a new 5,40 × 5,40 m slab that already exists; 2.6 and 2.8 were empty rows carrying formulas | **I** / CON R-07 (removes ~1 500–2 500 KM of phantom cost from a 15 000 KM LOT) |
| 3.12 | LOT 1 totals | `SUM` ranges rebuilt after the deletions | **J** |
| 3.13 | LOT 1 rows 52–57 | **new recap**: subtotal → popust → PDV 17 % → total | **J** — a LOT-1-only bidder previously never reached a total |
| 3.14 | LOT 1 rows 58+ | ~138 phantom rows trimmed | **J** |
| 3.15 | **LOT 2 F132** | `='LOT 1'!F52` → `='LOT 1'!F50` | **self-inflicted regression, caught by the recalculation test** |

### 3.15 in detail — a bug this process introduced and caught

Deleting rows 2.6–2.8 moved LOT 1's subtotal from row 52 to row 50. openpyxl does not
update **cross-sheet** references, so LOT 2's grand total silently kept pointing at the
old address and reported `SVE UKUPNO = 65.100` when LOT 1 + LOT 2 was `78.973` — LOT 1
was being dropped from the tender total entirely.

The first repair was also wrong: matching on `"UKUPNO LOT 1"` caught the **with-VAT**
line, which would have made the grand total charge VAT twice on LOT 1. The reference
must be the **ex-VAT** subtotal because LOT 2's recap applies VAT itself.

Verified by recalculating the workbook through LibreOffice with 100,00 KM injected into
every unit-price cell:

| | |
|---|---|
| LOT 1 ex-VAT | 13.873,00 |
| LOT 2 ex-VAT | 65.100,00 |
| SVE UKUPNO ex-VAT | **78.973,00** ✓ |
| PDV 17 % | **13.425,41** ✓ |
| SVE UKUPNO with VAT | **92.398,41** ✓ |
| LOT 1 standalone, 0 % discount | 13.873,00 → PDV 2.358,41 → **16.231,41** ✓ |

Both bidder paths — LOT 1 only, and LOT 1 + LOT 2 — now resolve correctly.

## 4. `1. NZ …docx` and `2. Prijedlog Odluke …docx`

Checked against the corrected TD and **left unchanged**. The LOT values (15.000 /
35.000 / 50.000 KM), the procedure type, the commission members and the contact block
are already consistent across both documents and the TD; the consistency checker
confirms a single value for each across the package. No template leftovers were found
in either file.

## 5. Drawings and PDFs

### 5.1 `Prilog_III_situacija_sjednica_bileca.pdf` — 79.6 MB → 8.5 MB, losslessly

The plan assumed the bulk was the CAD-derived vector pages and that they would have
to be rasterised. Measurement showed otherwise, so no rasterisation was needed:

| Cause | Detail |
|---|---|
| Un-subsetted duplicate fonts | Full **Arial Regular (1.05 MB) and Arial Bold (0.99 MB) embedded 17 times** between them — **16.64 MB** of the file. |
| Never compressed | The content streams were stored without deflate. |

Fix: `subset_fonts()` + `save(garbage=4, deflate=True, deflate_images=True, deflate_fonts=True, clean=True)`.
Embedded font bytes fall from 16.64 MB to 0.40 MB.

Proof it is lossless, across all 34 pages: extracted text identical, drawing-object
count identical, image count identical, page geometry identical, and pages 6, 12, 17,
29 and 31 render **pixel-for-pixel identical** at 100 dpi. All pages stay vector and
searchable. Applied after the corrected sheets are spliced in (§5.3).

### 5.2 CAD infrastructure

- `cad/style_profile.json` — layers, text styles, dimension styles, blocks and text
  heights harvested from the certified site project's own DWGs, so the new sheets match
  it: layers `Okvir`, `Tekst`, `Kote`, `Objekat`, `Konstrukcija`, `Panel`, `Kabal`,
  `Osovina`, `Orijentacija`; dimension styles `M 20 / M 50 / M 100 / M 200`
  (`dimscale` = plot denominator, `dimtxt` 2.5, `dimasz` 1.0); title block `Sastavnica`.
- `cad/site_geometry.json` — **existing-state ground truth measured from the certified
  project**, resolving finding **E**. Container is **3005 × 2300 mm external** with
  60 mm sandwich walls, centred on the 5400 × 5400 slab (offsets 1197 / 1550).
  Self-consistent: internal 2180 × 2885 = 6.29 m² and perimeter 10.13 m, both of which
  the source drawing states in its own annotations. Neither the TD's 3,00 × 2,10 nor
  Prilog III's 3,08 × 2,20 matches.
- `cad/bht_frame.py` — A3 frame and BH Telecom title block. The logo is traced from
  `bht-logo.svg` by parsing the path data and flattening the Béziers (cairosvg is
  unusable on this machine — its cairo DLL is absent). Designer field:
  **Rusmir Skopljak, dipl. ing. el.**
- `cad/build_drawings.py`, `cad/export.py`, `cad/render.py` — sheet construction and the
  DXF → DWG → verify → PDF pipeline.

Pipeline proven end to end on S-01: ezdxf → DXF → ODA → **DWG header AC1024** →
ODA → DXF → ezdxf, with 25 layers, all five `M *` dimension styles, hatches and 23
diacritic-bearing text strings surviving intact.

### 5.3 Sheets

| Sheet | State |
|---|---|
| S-01 Postojeće stanje 1:50 | built, converted to DWG and verified, A3 PDF plotted |
| S-02 / S-03 / M-01 / E-01 | blocked on the expert numbers |

---

## 6. Verification tooling

`tools/check_consistency.py` reads every deliverable in its native form — OOXML from
the docx zip, openpyxl, PyMuPDF, ezdxf — rather than via a text export, because
LibreOffice's txt export mangles Bosnian diacritics on a cp1252 console and silently
defeats naive greps. It asserts that facts which must have one value have exactly one,
and that template leftovers are gone. Exit code = failure count, so it can gate release.

**Baseline before correction: 7 failures.**

| | Check | Baseline |
|---|---|---|
| CONFLICT | generator rating | FAIL — `22 kVA`, `13,5 kVA` and `2×13 kVA` coexist (finding **F**) |
| CONFLICT | container external size | FAIL — three different sizes (finding **E**) |
| CONFLICT | PV module power | FAIL — 585 Wp and 540 Wp coexist (finding **L**) |
| CONFLICT | panel horizontal projection | one value (2,59 m) — but it is the **wrong** one (finding **B**) |
| CONFLICT | top panel edge level | one value (+3,09) — likewise wrong (finding **B**) |
| CONFLICT | fence overhang | FAIL — 0,17 m and 0,20 m coexist |
| BANNED | "vučna prikolica" | FAIL — 3 occurrences in the TD (finding **H**) |
| BANNED | "najmanje dvije lokacije" | FAIL — 1 occurrence in the TD (finding **H**) |
| BANNED | "proširenje postojeće ograde" | FAIL — 1 occurrence in the TD (finding **H**) |

LOT values are already consistent (15.000 / 35.000 / 50.000 KM across six documents),
as are the 500 l tank and the 1076 m altitude.

---

## 7. New finding — genset technical data is missing from the package

`EQUIPEMENT/GENSET/P22-6.pdf` is a **three-page web-page printout with no text layer**;
`P22-6.md` is its OCR. Between them they give ratings, engine model and the
standard/optional equipment lists, but **no physical dimensions, no dry or wet weight,
no cooling-air or combustion-air flow, no exhaust connection size and no back-pressure
limit**.

Those are precisely the figures needed to size the container ventilation and exhaust
(finding **D**), to check the container floor against the skid plus a full 500 l tank,
and to prove the set fits through a 1,00 m gate and a 900 × 2000 mm door. Per
`prompt.md` §3 this is a **YELLOW**: the tender names a generator model whose
installation cannot be verified from the documents supplied with it. The full FG Wilson
technical data sheet must be obtained, or the tender must place the sizing obligation
explicitly on the bidder with stated minimum performance requirements.


---

## 8. Revision 2 — 2026-08-07, Investor's decisions

### 8.1 New deliverable: `3. Prilog I TD - Specifikacija zahtjeva.docx`

A new tender annex (7 pages, A4, BH Telecom house style), generated by
`tools/make_prilog1.py`. It carries the requirements and the **proofs the bidder must
submit with the offer**, which is the change that matters most: under a lowest-price
award, anything verified after award is verified too late.

Structure follows the draft the Investor supplied. Section 0 of the document is a
**corrections table** listing every value that differs from that draft, with its source,
so the changes are visible rather than silent. The nine corrections are:

| Item | Draft said | Correct | Source |
|---|---|---|---|
| PV geometry | projection 2590 mm, top +3,09 m | **3236 mm, +3,74 m** | derived from the module field, not the beam |
| Fence height | 1,80 m | **1,90 m** | certified site project |
| Container | 3,08 × 2,20 × 2,80 / 3,00 × 2,10 | **3,005 × 2,30, empty** | certified project (6,29 m², 10,13 m) |
| Radiator air | ≈4250 m³/h | **1980 m³/h** | FG Wilson TDS |
| Intake louvre | ≥0,43 m² (1200 × 800) | **500 × 700 adequate** | 125 Pa restriction budget |
| Room fan | ≥2400 m³/h | **1200 m³/h supplementary** | radiator has its own fan |
| Exhaust | DN 65 minimum | **DN 50 passes; DN 65 recommended** | 2,6 kPa vs 10,2 kPa limit |
| Panel bottom edge | ≥1,20 m for snow | **+0,50 m** | snow not governing (wind-scoured site) |
| Snow | s_k = 3,00 kN/m² governing | **check required, not governing** | Investor's site knowledge |

The draft's ventilation figures were the electrical review's superseded estimates; the
bottom-edge change would also have pushed the top edge to +4,44 m, increased the wind
lever arm and broken the fit in the 1950 mm south strip.

### 8.2 BOQ round 2 — consolidated into `tools/fix_boq_all.py`

| Change | Reason |
|---|---|
| Item 1.1 rewritten: BOM 21540481, corrected geometry, **real site wind load with design actions** (≥27 kN uplift, ≥30 kN horizontal, ≥64 kNm overturning), full material/section/galvanising/EXC2 spec | calc F.1, F.2 — makes the item BOQ-quantifiable instead of naming an unbuildable catalogue kit |
| Item 1.2 → **chemical (epoxy) anchors**, M16/M20 with ETA, ≥30 kN each, 4 per support, pull-out test on ≥10 % | calc B.6 — gravity foundation was 40 % short; rock anchors address the actual failure mode |
| Item 2.3 → **C30/37, XC4 + XF3**, air-entrained 4–6 %, B500B, cover ≥50 mm, frost depth stated by bidder | calc A.4 — freeze-thaw at 1076 m; the BOQ had no exposure class at all |
| **New item 1.8** — optional 3 supports × 4 modules, priced separately, excluded from all sums | calc F.6 — halves sail per structure (15,91 → 7,95 m²) at the same 7,02 kWp |
| LOT 2 GRO → **RCD 4p 63 A/300 mA S-type + 2 × RCBO 16 A/30 mA type A** | calc D.4 — SHUNT excitation with 0 % short-circuit capacity means overcurrent can never meet IEC 60364-4-41 |

### 8.3 Three bugs found and fixed in the BOQ tooling

Documented because they are all silent-corruption modes in openpyxl, and any future
edit will meet them again:

1. **Formulas are not translated on row insert.** After two rounds of insertions, item
   1.3 sat on row 35 while still computing `D32*E32`. Fix: regenerate every product
   formula from scratch after all structural edits, so each references its own row.
2. **Substring matching on item numbers.** `"4.1"` matched `"4.10"`, producing SUM
   ranges over the wrong rows and a `#VALUE!` grand total. Fix: exact match only.
3. **Stale merge ranges migrate onto other rows.** Deleting a total row left its
   `A:E` merge behind; openpyxl does not move merge anchors, so `A37:E37` settled over
   item 1.7 and `A47:E47` over item 2.4 — hiding their unit, quantity and price columns
   and making the description read as `None`. This is why those two items appeared
   blank. Fix: a final pass that strips any merge covering a priced item row and
   restores content from the baseline by item number.

The first attempt at round 2 also destroyed items 1.3–1.7 by inserting 3 rows and then
writing 5 lines into them. It was caught by the recalculation test, the file was
restored from the baseline, and the two scripts were consolidated into one that runs
from a pristine copy every time.

**Verification after all of it** — LOT 1 13.873,00 + LOT 2 64.900,00 = 78.773,00;
PDV 13.391,41; total 92.164,41; LOT-1-only 16.231,41. Item 1.8 correctly outside the
totals. Diff against baseline: **0 unintended content losses**.

### 8.4 Consistency checker

Taught to recognise a **documented correction**: a superseded value quoted in Prilog I's
"Ranije navedeno" column is always followed within the same table row by the corrected
value, so a lookahead distinguishes it from a live specification. Without this the
corrections table would have failed the very check it exists to satisfy.

**Final gate: 0 failures across 10 documents.**

---

# Revision 2 · 2026-08-11

Two things drove this revision: the Investor asked for the genset air intake to be
taken through the **container walls** with the equipment positioned properly, and the
items left open in `07-calculations.md` §G had to be closed in the documents that are
actually issued.

## 9. Airflow relayout — closes EL RED-03

### 9.1 What was wrong

Rev 1 put the intake louvre (500 × 700), the radiator discharge louvre (600 × 600) **and**
the 505 °C exhaust on the **north** wall, 1,4 m apart, on the same face as the existing
outdoor cabinets ICC330-H1 and MTS9302. On drawing M-01 the fuel tank stood directly in
front of the intake (tank x 450–1650 against an intake at x 250–750), and the plan and the
section disagreed about which wall the openings were on. The room fan and the 110 % bund
were not drawn at all.

### 9.2 What it is now

Cross-flow, south-east in → west out (`cad/design.json` → `ventilation.layout`, drawing M-01):

| Element | Wall | Position |
|---|---|---|
| Intake louvre 500 × 700 | **JUG** | east end, bottom edge +0,30 m |
| Radiator duct + discharge louvre 600 × 600 | **ZAPAD** | on the radiator axis, shortest route |
| Exhaust DN 65 | **ZAPAD** | riser, terminating above the roof, spark arrestor |
| Tank vent | **SJEVER** | east end, ≥3 m from exhaust and intake |
| Room fan Ø315 | **ISTOK** | high, north of the entrance door |

Nothing discharges toward the cabinet wall, and intake and exhaust are on opposite ends
of the airflow path. M-01 gained cardinal wall labels, the door leaf and swing, airflow
arrows, the 110 % bund and the room fan; its plan and section now agree. The louvre and
duct sizes themselves are **unchanged** — the 125 Pa budget was already satisfied and is
not affected by moving the openings.

### 9.3 Fuel tank — real data

The Investor supplied the tank data on 2026-08-11: **1050 × 600 × 1310 mm, 170 kg empty**.
This supersedes the unverified 1200 × 700 × 800 estimate that Rev 1 carried. Full mass is
now ≈590 kg on 0,63 m² = **9,2 kN/m²**, which changes the floor conclusion below.

## 10. Section G items — closed

| § G | Item | Closure |
|---|---|---|
| 2 | Concrete class stated twice, inconsistently | BOQ 2.3 lead text rewritten to C30/37 XC4+XF3 on C12/15, B500B; 2.2b C10 → C12/15; `design.json` and S-03 note synced |
| 3 | Floor capacity claimed from a K3 type sheet | Governing value is **2,00 kN/m²** (project brief); K2 is what is installed. Both the genset (3,93 kN/m²) and the full tank (9,2 kN/m²) exceed it, so the load-spreading frame under **both** the skid and the bund is now **required**, not conditional (BOQ 4.4 rewritten — it previously argued that strengthening was "not expected") |
| 4 residual | Reference alternator is shunt-excited by default | BOQ now reads "kao Stamford BCI164C **u izvedbi sa PMG ili AREP/AUX pobudom**" |
| 5 | Fire elaborate, fuel shut-off valve, ventilation interlock specified but unpriced | New priced items **4.19, 4.20, 4.21** |
| 6 | AC SPD priced as type 2; no signal-line SPD anywhere | BOQ AC SPD → **type 1+2, Iimp ≥12,5 kA (10/350)**; new priced item **5.11** for EN 61643-21 signal-line protection |
| 7 | Three different power systems named | Unified on **ICC330-H1 + MTS9302** (Investor's decision) across the TD, the Odluka, the BOQ and Prilog I |
| 9 | Tower obstruction lighting absent from the whole package | New priced item **5.10**: survey and transfer of all 7 existing circuits, with **K7 obstruction lighting on its own monitored circuit** and the bidder measuring its real load for the energy balance |

Also aligned while in there: first fuel fill 200 l → **500 l** (the BOQ priced 500 l all
along), exhaust **DN 65 adopted** rather than "recommended", and the garbled LOT-2 scope
sentence (Y-16, a LOT-1 fragment merged into it) rewritten.

## 11. Prilog I — figures and precedence

Prilog I now carries the equipment figures (Slika 1–4) and a **Slika 5 lifted directly out
of drawing M-01**, so the specification and the drawing cannot drift apart — the figure is
rendered from the DXF by `tools/render_equipment.py`, not drawn separately. §4.3 gained a
binding "Raspored otvora" table and a callout forbidding any arrangement that puts intake,
discharge and exhaust on one wall or vents toward the cabinets.

A **REDOSLIJED MJERODAVNOSTI** clause was added to §0: TD → Prilog I → Prilog II →
Prilog III, and it states explicitly that the inherited K3 pages in Prilog III (including
their 10,00 kN/m² floor figure) do not govern.

## 12. Tooling

- `tools/render_equipment.py` (new) — vendor figures and the M-01 layout extract.
- `tools/fix_td2.py`, `tools/fix_boq_gaps.py` (new) — the text and BOQ edits above.
  `fix_td2.py` is idempotent; `fix_boq_gaps.py` carries the same integrity pass as
  `fix_boq_all.py` plus a **shrink guard** that refuses to save if a priced item's
  description loses more than half its text (it caught a whole-cell write that had
  replaced item 5.6's entire GRO specification with a single bullet).
- `cad/render.py` — `render_window()` for document figures; `cad/bht_frame.py` gained an
  `Izvod` layer so leader callouts can be separated from labels.
- `tools/check_consistency.py` — six new conflict rules and six new required values.
  Two bugs of its own were fixed: the docx reader discarded paragraph breaks, gluing
  adjacent table cells into fake words ("gorivomranije:") and silently defeating every
  `\b`-anchored pattern; and the correction-marker list used the ending `mjerodavn`,
  which does not match the masculine `mjerodavan`.

**Final gate: 0 failures across 13 documents.** BOQ recalculated through LibreOffice with
100 KM on every item: LOT 1 20.008 + LOT 2 65.300 = 85.308, with VAT 99.810,36.

## 13. Still open

- §G 1 — certified static calculation for 45° at qp ≥ 1,20 kN/m² (bidder, pre-award).
- §G 8 — revision of the certified electrical project (its PMO source no longer exists).
- The real power of the obstruction light is measured by the bidder under item 5.10;
  until then the December energy balance carries an allowance, not a measured figure.
- Prilog III still contains the **K3** container drawings (pages 8–15) although the site
  folder identifies the container as **K2**. They are inherited pages and are now
  explicitly non-governing, but replacing them with K2 drawings would be the cleaner fix.
- Container height 2400 mm is taken from the type sheet; `02-construction.md` Y-05 lists
  four conflicting heights. To be confirmed on the mandatory site visit.

---

# Revision 3 · 2026-08-11

Investor review of Rev 2. One item reverses a Rev-2 change, and the Investor is
right on the evidence.

## 14. Floor capacity is 10,00 kN/m² — Rev-2 change RETRACTED

`SITE-PROJECT-SJEDNICA-Bileca-K2-S38-m\2 - ARHITEKTONSKO GRADJEVINSKI DIO\04 AG dio.docx`
is the certified project of **this K2 object**, and its §4.4.2.3 PODNA KONSTRUKCIJA
dimensions the floor for *"ukupno opterećenje (g+p) **10.00 kN/m2**"* — secondary beams
HOP 100×50×3 at 0,51 m carrying 5,10 kN/m′, primary beams 15,00 kN/m′. The 2,00 kN/m²
that appears in §POD of the same document is the **pedestrian live load on the walkable
strip**, not the structural capacity.

So Rev 2 §G-3 was wrong twice over: it took the walkable-strip figure for the design
load, and it argued the 10,00 kN/m² came from a K3 type sheet. It did not — it is in the
K2 project. **`02-construction.md` R-08's claim that no such document is in the pack is
hereby retracted**; the document was in the site project folder all along.

The load-spreading frame **stays required**, but for the correct reason: 10,00 kN/m² is a
uniformly distributed load, while the genset (3,93 kN/m²) and the full tank (9,2 kN/m²)
bear concentrated on a few secondary beams. The frame distributes onto the primary beams.
Item 4.4 and the section-4 note now say that; neither claims capacity is exceeded.

## 15. Sheets S-03 and M-01 were not true A3

Measured content extents against the frame: **M-01** ran to x=14705 against a 10500-unit
frame (the section 1–1 sat beside the sheet), **S-03** to y=12836 against 8910 (the note
block sat above it). `export.py` plots with `fit_page=True`, so the overflow was absorbed
by shrinking the whole sheet — it printed smaller than A3 and the scales in the title
blocks (1:25, 1:30) were false. These are Situacija pages 3–4 = Prilog III pages 5–6.

Fixed by moving the section and the note blocks inside the frame and compacting every
note block (M-01 22 lines → 10, S-03 13 → 7, E-01 12 → 6, S-02 8 → 5, S-01 5 → 3). All
five sheets now plot with the frame **at the page edge**.

`build_drawings.py` gained `check_extents()`, which refuses to write a sheet whose content
leaves the A3 area. It immediately caught two more: S-02's parcel boundary overran the
top edge by 150 units, and E-01's notes ran 495 units off the bottom. It also caught a
loop variable in `sheet_m01` (`for label, tx, ty ...`) that was shadowing the tank origin
`tx`, which put the section's dashed tank 3 m off its true position.

## 16. Two strings of six

12 modules on 3 supports are wired as **2 strings × 6**, not 3 × 4. The binding constraint
is the priced **PVDB500-15-2B, which has two outputs**; 6 × 51,55 V = 309 V Voc sits inside
the iSSU's 85–435 V window and Imp 13,67 A is under the 15 A per output. A string therefore
spans two supports, so E-01's "svaki string kompletan po nosaču" rule is gone.

BOQ: item 1.1 routing text rewritten, **1.5 DC cable 150 → 100 m**, **1.6a DC SPD 3 → 2 kpl**.
The last also settles a Rev-2 inconsistency — 3 SPD sets were priced against 2 drawn on
E-01. LOT 1 falls by 5.100 KM at the 100 KM/unit test rate.

## 17. Other Investor corrections

- **Fuel tank moved east** along the north wall, onto more secondary beams and clear of
  the radiator duct penetration; its own spreading frame is now drawn under the bund.
- **PV panels hatched** on S-02 with a cross-hatch mesh (ANSI37). `NET` was tried first
  and came out as a solid fill through the plot backend.
- **Prilog I section 0 deleted** — a 17-row corrigendum against internal working versions
  that no bidder ever saw. The REDOSLIJED MJERODAVNOSTI precedence clause is kept, moved
  to the top and stripped of its now-wrong floor-load sentence.
- **PV foundation unchanged** — confirmed by the Investor, together with the earthworks
  and strip-footing items in BOQ section 2.
- TD, NZ and Odluka still said **LOT 1 = 2 kom/kpl** supports, stale since the 3×4
  redesign; corrected to 3 in all three.

## 18. Checker

`check_consistency.py`: the floor-capacity rule flipped polarity — 10,00 kN/m² is now the
correct variant, and 2,00 kN/m² is only tolerated where it is named as the walkable-strip
load. The `INHERITED_ANNEX` / `ANNEX_EXEMPT` machinery is deleted: with 10,00 kN/m²
correct, the inherited Prilog III pages agree with the package instead of contradicting it.

**Gate: 0 failures across 13 documents.** BOQ recalculated through LibreOffice:
LOT 1 14.908 + LOT 2 65.300 = 80.208, with VAT 93.843,36.

## 19. Still open

Unchanged from Rev 2 (§G 1 static calculation, §G 8 certified electrical project revision,
measured obstruction-light load), plus:

- Prilog III pages 8–15 are still the **K3** container drawings while the site is K2. They
  are now explicitly non-governing under the precedence clause, but replacing them with the
  K2 set — which exists, in `2 - ARHITEKTONSKO GRADJEVINSKI DIO` — would be the clean fix.
- Container height 2400 mm is from the type sheet; `02-construction.md` Y-05 lists four
  conflicting heights. To be confirmed on the site visit.

## 20. Prilog III rebuilt from parts (Rev 3, second pass)

The annex was previously maintained by splicing corrected sheets into an inherited
30-page PDF. It is now **assembled from sources** by `tools/build_prilog3.py`, which
made the Investor's restructure possible:

| Was | Now |
|---|---|
| 8 K3 container drawings (G-01..G-08) | **6 K2 drawings** from the certified project of this object: osnova, presjek 1-1, presjek 2-2, fasade, detalji, osnova temelja |
| 9 K3 electrical drawings (E-01..E-09) | **1 K2 drawing**: 3.5.2 Jednopolna šema GRO. The PMO sheets go with the rest — the PMO no longer has a supply, and sheet E-01 of this package shows the new GRO |
| INFO-03 (RFI block diagram), INFO-04 (named PowerCube), closing REFERENTNA DOKUMENTACIJA page | removed |
| INFO-01 at page 25 | moved directly behind the cover |
| inherited cover | rebuilt in the style of the TD title page |

**30 pages → 16**, 10,0 MB → 7,3 MB, and the K3 container — which was never the
container on this site — no longer appears anywhere in the package.

Three things the vendor DWGs needed:

- **Fonts.** The cover is generated with PyMuPDF, whose base-14 fonts have no
  š/ć/č/ž/đ; Bosnian text came out as question marks. The system Arial is embedded.
- **Text normalisation.** The inherited pages set words with non-breaking spaces and
  soft hyphens, so `"OPŠTI PODACI O LOKACIJI"` and `"INFO-01"` could not be found by
  substring search — the same class of bug as the docx reader in §12.
- **Cropping.** The GRO single-line parks a duplicate load table outside its sheet
  frame; plotted fit-to-page that padding shrank the drawing into a corner. Cropping
  is **opt-in per sheet**, after a heuristic applied to all of them threw away real
  content on the plans. The bounding boxes come from `ezdxf.bbox` — a hand-rolled
  version ignored block INSERTs, and the stray table is a block, so it survived
  every crop until that was fixed.

Also in this pass: **the container is drawn on S-03**, on the existing slab north of
the fence, so the section shows what the panel actually oversails.

## 21. Note on the K2 architectural drawings

They are the 2018 as-built set and show the container with RBS cabinets and
"UREĐAJI ZA NAPAJANJE" in place. The package states the container is now **PRAZAN**
(Investor's site visit, `05-site-corrections.md` C-1). That is not a contradiction to
fix in the drawings — they are a historical annex — and the precedence clause in
Prilog I §0 settles which document governs.
