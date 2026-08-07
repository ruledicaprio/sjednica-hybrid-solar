# Engineering Document Review – Rules & Philosophy

## 1. Review Philosophy
- **Purpose**: Identify risks, inconsistencies, and missing information before construction.
- **Approach**: Treat every drawing and specification as a potential source of error. Assume nothing; verify everything against:
  - Manufacturer datasheets
  - Applicable standards (Eurocode, local codes)
  - Company internal standards
  - Past project lessons learned
- **Output**: Actionable, prioritized findings. Not a subjective opinion, but a checklist of verifiable issues.

## 2. Review Structure
Every review must produce a report with the following sections:

### 2.1. Executive Summary
- **Risk Level**: HIGH / MEDIUM / LOW
- **Key Conclusion**: 1‑2 sentences summarising the overall state of the design.

### 2.2. Information Extraction Table
- A structured table that captures all critical dimensions, equipment, orientations, and annotations from the document.
- This serves as a ground truth for the review.

### 2.3. Findings Categorised by Severity
| Severity | Definition | Action Required |
|----------|------------|------------------|
| **RED (Critical)** | Direct non‑compliance, safety hazard, or impossible spatial conflict. | Must be resolved before any further design or construction. |
| **YELLOW (Minor)** | Missing data, ambiguity, or potential issue that may become critical. | Requires clarification or additional calculation. |
| **GREEN (Positive)** | Correctly implemented – note for reference. | No action, but useful for future projects. |

### 2.4. Detailed Checklist (applied per document)
The review must systematically check the following categories (tick all that apply):

| Category | Checks |
|----------|--------|
| **Geometry & Layout** | – Are all critical dimensions present? <br> – Is the equipment layout feasible on the given plot? <br> – Are clearances for installation/maintenance respected? <br> – Is the orientation consistent with sun path/wind? |
| **Structural** | – Are foundation dimensions specified? <br> – Is a static calculation referenced or provided? <br> – Are uplift and overturning considered? <br> – Is soil bearing capacity data available? <br> – Are safety factors in line with Eurocode? |
| **Manufacturing / Fabrication** | – Are all steel profiles and thicknesses specified? <br> – Are weld symbols and accessibility indicated? <br> – Are standard stock sizes used? <br> – Is galvanisation or corrosion protection defined? |
| **Installation** | – Is the assembly sequence plausible? <br> – Are lifting points and access for heavy equipment considered? <br> – Are temporary works (scaffolding, propping) required? |
| **Maintenance** | – Is there safe access for cleaning, inspection, and repair? <br> – Are drainage and snow clearance provided? <br> – Are fasteners accessible with standard tools? |
| **Documentation & BOM** | – Is a Bill of Materials provided? <br> – Are quantities, lengths, and part numbers consistent with drawings? <br> – Is the drawing revision and date clearly marked? <br> – Are references to standards and datasheets correct? |
| **Safety** | – Are sharp edges, pinch points, or fall hazards identified? <br> – Is earthing and bonding clearly shown? <br> – Are fire safety distances (generator, fuel) respected? |

### 2.5. Action Items
- A numbered list of concrete tasks that must be completed to resolve RED and YELLOW findings.
- Each action should be specific and assignable (e.g., *“Provide soil bearing capacity report”* rather than *“Check foundation”*).

### 2.6. Lessons Learned (Optional)
- Note any good practices observed in this design that could be applied to future projects.

## 3. Inputs Required for a Complete Review
The review assumes that the following knowledge is available in the Claude Project:
- **Manufacturer Datasheets** – for all major equipment (PV panels, inverters, generators, steel profiles).
- **Company Standards** – internal guidelines on clearance, spacing, safety, and preferred solutions.
- **Past Projects** – similar designs for comparison.
- **Applicable Codes** – Eurocode sections (EN 1990, EN 1991, EN 1993, EN 1997) or local equivalents.

If any of these are missing, the reviewer (AI) must flag it as a YELLOW finding.

## 4. Output Format
- **Preferred format**: Markdown with tables, bold headings, and clear severity tags.
- **Length**: Concise but comprehensive. Aim for 2‑4 pages for a typical telecom site layout.
- **Attachments**: The review may reference specific pages or drawing numbers for clarity.

## 5. Review Style
- Use objective, neutral language.
- When citing a rule, quote the source (e.g., *“Eurocode 3, §6.3.2 requires…”*).
- Avoid speculation; clearly distinguish between *“is missing”* and *“may be missing”*.
- Offer constructive solutions, not just criticism.

## 6. Revision History
- The review itself should note its own revision and date.
- When a second review is run on an updated document, produce a *delta review* that highlights only changes since last time.

---
*End of Review Rules*