# solar-rfp-engine

Solar/hybrid-power engineering toolkit used to produce RFP and technical
proposal documents for infrastructure rollouts. The Sjednica-Bileca 46-site
rollout (see "Active initiative" below) is the first project run through it,
not the whole of its scope.

One subproject remains: `rural-star-sjednica/` (structured Python simulation
pipeline). For the solar portion of the RFPs we now just use the existing
solar irradiation figures under `rural-star-sjednica/output/report_results/`
— the simulation pipeline is kept for reference but is not being re-run.

## Data & tool sources

Radiance is one input tool among several this toolkit is meant to lean on.
Not implemented yet — noted here as the intended source list for future
work:

- **Radiance** — daylighting/irradiance simulation (`rural-star-sjednica/`,
  `src/radiance_engine.py`). Binaries live in the gitignored `bin/`/`lib/`
  (see repo history below) — install from radiance-online.org if missing.
- **pvlib** — PV yield modeling.
- **PVGIS** — solar irradiation data source.
- Wind load data sources — for structural/mounting calculations.
- Snow load data sources — for structural/mounting calculations.
- Floor/equipment weight capacity calculations — for construction-phase
  equipment siting (e.g. indoor-skid Genset units inside existing
  containers).

## Repo history

- Renamed on GitHub from `ruledicaprio/radiance_build` to
  `ruledicaprio/sjednica-hybrid-solar`, then to
  `ruledicaprio/solar-rfp-engine` (2026-08-13), reflecting the broader
  toolkit scope above.
- **2026-08-06 cleanup (history rewritten, force-pushed).** The repo was
  ~100 MB because it vendored a full Radiance Windows distribution. These
  were purged from all history:
  - `bin/`, `lib/` and `Radiance_*_Windows.zip` — the Radiance suite.
    It is third-party redistributable software; download it from
    radiance-online.org rather than committing it here.
  - `moja_solar_ograda/` — superseded by `rural-star-sjednica/`.
  - `rural-star-sjednica/output/radiance_{results,scene}/`,
    `__pycache__/`, `weather_cache.csv` — regenerable artifacts.

  Result: ~100 MB -> ~3.6 MB tracked, `.git` 66 MB -> ~1.9 MB. A full
  pre-cleanup backup bundle is at
  `D:\sjednica-hybrid-solar-BACKUP-20260806.bundle` (local only).
- **2026-08-13**: `bin/`/`lib/` restored locally (still gitignored, not
  re-vendored into git) from a stale pre-rename clone that was otherwise
  retired — `src/radiance_engine.py`, `src/skies_engine.py` and
  `src/generate_false_color.py` are runnable again.

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
