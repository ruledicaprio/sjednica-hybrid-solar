# Change log — BS Sjednica (Bileća) tender package

Revision 1 · 2026-08-07 · Rusmir Skopljak, dipl. ing. el.

Baseline of the pre-change state: `bht-sjednica-final-review/TD-OUTPUT-BASELINE-20260807/`
(byte-for-byte copy of TD-OUTPUT as of 2026-08-07, before any edit).

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
