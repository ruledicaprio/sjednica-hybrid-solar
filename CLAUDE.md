# sjednica-hybrid-solar

Solar/hybrid energy infrastructure project ("Solarna ograda"). Uses the
Radiance lighting-simulation suite (LBNL) vendored under `bin/` and
`lib/` for irradiance/bifacial-panel simulations, plus two subprojects:
`rural-star-sjednica/` (structured Python simulation pipeline) and
`moja_solar_ograda/` (working scripts, CAD/DXF data, weather files).

## Repo rename history

- Renamed on GitHub from `ruledicaprio/radiance_build` to
  `ruledicaprio/sjednica-hybrid-solar`. Local git remote updated to match.
- Hardcoded absolute paths (`E:\Radiance_build\...`) in
  `moja_solar_ograda/*.py` scripts were made portable — computed from
  `__file__` instead of tied to the old folder name.
- Do NOT rename references to the actual third-party **Radiance**
  rendering engine (`bin/`, `lib/`, `radiance_engine.py`, its docs) —
  that's vendored software, not this project's branding.

## Active initiative: RFP / proposal documents

Goal: produce Request for Proposal documents for infrastructure
installation across 46 locations (grounding, ground support panels,
and Genset installation at indoor-skid units placed inside existing
containers under antennas/towers).

Workflow:

1. User provides a sample RFP / scope-of-work `.docx` from a similar
   past project — used as the structural template for new RFP docs.
2. User provides a PDF describing the chosen technical solution
   (grounding, ground support panels, Genset installation) — used as
   the technical content source.
3. `.docx` edits are made by editing the underlying OOXML directly (a
   `.docx` is a zip of XML), not by regenerating the file from
   scratch — this preserves the template's formatting, styles, and
   layout; only the requested text/sections change.
4. Deliverables land under `proposals/` (create this folder when the
   first file arrives — it doesn't exist yet).

Also planned, later: a Rust-based ("anydoc") PDF-parsing pipeline to
extract text/context from provided PDFs and other docs to feed into
the RFP content.

## Status as of this writing

Waiting on the user to provide:
- The sample RFP/scope-of-work `.docx` template
- The PDF describing the chosen technical solution (grounding/ground
  support panels/gensets)

Once received: create `proposals/`, build the RFP template from the
sample doc, and pull technical details from the PDF into the content.
