# -*- coding: utf-8 -*-
"""
Assemble Prilog III from parts, instead of splicing into an inherited PDF.

Rev 3 restructure (Investor, 2026-08-11):

  - the eight K3 container drawings (G-01..G-08) are replaced by the K2 set from
    the certified project of THIS object - the site is a K2, so the K3 sheets
    described a different container;
  - the nine K3 electrical drawings (E-01..E-09) all go, replaced by the single
    K2 single-line diagram of the GRO. The PMO drawings go with them: the PMO no
    longer has a supply, and our own E-01 sheet shows the new GRO;
  - INFO-03 (RFI block diagram), INFO-04 (names PowerCube, which the package no
    longer specifies) and the closing REFERENTNA DOKUMENTACIJA page are dropped;
  - INFO-01 (site photo) moves directly behind the cover;
  - the cover is rebuilt in the style of the TD cover page.

The K2 drawings are vendor DWGs: they are converted to DXF with the ODA File
Converter, cropped to their own sheet frame (several carry stray content beside
the frame) and plotted to A3.
"""

from __future__ import annotations

import glob
import os
import shutil
import subprocess
import sys
import tempfile

import ezdxf
import fitz

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from paths import GRAFIKA as DWG, LOGO_SVG, PRILOG3 as OUT          # noqa: E402

SITE = os.path.join(BASE, "SITE-PROJECT-SJEDNICA-Bileca-K2-S38-m")
ODA = os.environ.get(
    "ODA_CONVERTER_PATH", r"C:\Program Files\ODA\ODAFileConverter\ODAFileConverter.exe"
)

ARCH = os.path.join(SITE, "2 - ARHITEKTONSKO GRADJEVINSKI DIO", "6 Graficki dio")
ELEC = os.path.join(SITE, "3_ELEKTRO INSTALACIJE", "Graficki dio")

# K2 source drawing -> (caption, crop). Cropping is opt-in per sheet, not
# guessed: only the GRO single-line parks content away from its frame, and a
# heuristic applied to all of them threw away real content on the plans.
K2_SHEETS = [
    (
        os.path.join(ARCH, "463 Graficki dio OBJEKAT", "01 Osnova.dwg"),
        "Kontejner K2 — osnova",
        False,
    ),
    (
        os.path.join(ARCH, "463 Graficki dio OBJEKAT", "02 Presjek 1_1.dwg"),
        "Kontejner K2 — presjek 1-1",
        False,
    ),
    (
        os.path.join(ARCH, "463 Graficki dio OBJEKAT", "03 Presjek 2_2.dwg"),
        "Kontejner K2 — presjek 2-2",
        False,
    ),
    (
        os.path.join(ARCH, "463 Graficki dio OBJEKAT", "04 Fasade.dwg"),
        "Kontejner K2 — fasade",
        False,
    ),
    (
        os.path.join(ARCH, "463 Graficki dio OBJEKAT", "05 Detalji.dwg"),
        "Kontejner K2 — detalji",
        False,
    ),
    (
        os.path.join(ARCH, "461 Graficki dio TEMELJ i OGRADA", "03 Osnova temelja.dwg"),
        "Osnova temelja",
        False,
    ),
    (os.path.join(ELEC, "3.5.2 Jednopolna sema GRO.dwg"), "Jednopolna šema GRO", True),
]

# Pages lifted unchanged out of the previous annex, matched by drawing number.
# The separator in those codes is a soft hyphen in the source PDF, so match on
# any single non-alphanumeric character rather than a literal dash.
KEEP_FROM_OLD = {"INFO-01": "site photo", "INFO-02": "solar irradiation"}


# --------------------------------------------------------------------------
def to_dxf(dwg_paths):
    """Convert the vendor DWGs in one ODA batch; returns {source: dxf path}."""
    tmp = tempfile.mkdtemp(prefix="prilog3_")
    src, dst = os.path.join(tmp, "in"), os.path.join(tmp, "out")
    os.makedirs(src)
    names = {}
    for i, p in enumerate(dwg_paths):
        # flat, ASCII names: the converter is unhappy with some source names
        stem = f"k2_{i:02d}"
        shutil.copy(p, os.path.join(src, stem + ".dwg"))
        names[p] = os.path.join(dst, stem + ".dxf")
    r = subprocess.run(
        [ODA, src, dst, "ACAD2018", "DXF", "0", "1"],
        capture_output=True,
        text=True,
        timeout=1800,
    )
    made = glob.glob(os.path.join(dst, "*.dxf"))
    if not made:
        raise SystemExit(f"ODA produced nothing.\n{r.stdout}\n{r.stderr}")
    return names, tmp


def _bbox(e):
    """Bounding box via ezdxf's own extents, so block INSERTs and hatches are
    measured too - a hand-rolled version skipped them, and the stray table on
    the GRO sheet is a block, so it survived every crop."""
    from ezdxf import bbox

    try:
        b = bbox.extents([e], fast=True)
    except Exception:  # noqa: BLE001
        return None
    if not b.has_data:
        return None
    return b.extmin.x, b.extmin.y, b.extmax.x, b.extmax.y


def find_frame(msp, extents=None):
    """Largest axis-aligned closed rectangle - the sheet frame on these drawings.

    A candidate that spans essentially the whole file is skipped: some of these
    drawings carry an outer border around the sheet *and* whatever is parked
    beside it, so cropping to that would crop nothing. The sheet frame is then
    the next-largest rectangle.
    """
    cands = []
    for e in msp.query("LWPOLYLINE"):
        pts = [(p[0], p[1]) for p in e.get_points()]
        if len(pts) not in (4, 5):
            continue
        xs = sorted({round(p[0], 1) for p in pts})
        ys = sorted({round(p[1], 1) for p in pts})
        if len(xs) != 2 or len(ys) != 2:
            continue  # not axis-aligned
        cands.append(((xs[1] - xs[0]) * (ys[1] - ys[0]), (xs[0], ys[0], xs[1], ys[1])))
    if not cands:
        return None
    cands.sort(key=lambda c: -c[0])
    if extents:
        ex0, ey0, ex1, ey1 = extents
        whole = (ex1 - ex0) * (ey1 - ey0)
        for area, box in cands:
            if area < 0.9 * whole:
                return box
    return cands[0][1]


def main_cluster(centres, span):
    """Keep the densest run of coordinates, split at the largest wide gap.

    Not every drawing draws its frame as a polyline, so frame detection alone is
    not enough. What these sheets do have in common is that the stray content
    sits well away from the drawing, leaving a gap far wider than anything
    inside it - so split on the widest gap and keep the busier side.
    """
    if len(centres) < 8:
        return None
    xs = sorted(centres)
    gaps = [(xs[i + 1] - xs[i], i) for i in range(len(xs) - 1)]
    width, i = max(gaps)
    if width < 0.18 * span:
        return None
    left, right = xs[: i + 1], xs[i + 1 :]
    keep = left if len(left) >= len(right) else right
    return min(keep), max(keep)


def crop_to_frame(doc):
    """Delete anything wholly outside the sheet frame.

    Several of these drawings park a stray table or an old revision beside the
    frame; plotted with fit-to-page that padding would shrink the drawing into a
    corner of the sheet.
    """
    msp = doc.modelspace()
    boxes = [(e, _bbox(e)) for e in msp]
    boxes = [(e, b) for e, b in boxes if b is not None]
    if not boxes:
        return 0

    allx = [b[0] for _, b in boxes] + [b[2] for _, b in boxes]
    ally = [b[1] for _, b in boxes] + [b[3] for _, b in boxes]
    extents = (min(allx), min(ally), max(allx), max(ally))
    fr = find_frame(msp, extents)
    if fr is None:
        span_x, span_y = max(allx) - min(allx), max(ally) - min(ally)
        cx = main_cluster([(b[0] + b[2]) / 2 for _, b in boxes], span_x)
        cy = main_cluster([(b[1] + b[3]) / 2 for _, b in boxes], span_y)
        if cx is None and cy is None:
            return 0
        x0, x1 = cx if cx else (min(allx), max(allx))
        y0, y1 = cy if cy else (min(ally), max(ally))
        fr = (x0, y0, x1, y1)

    x0, y0, x1, y1 = fr
    pad = 0.03 * max(x1 - x0, y1 - y0)
    dropped = 0
    for e, b in boxes:
        if b[2] < x0 - pad or b[0] > x1 + pad or b[3] < y0 - pad or b[1] > y1 + pad:
            msp.delete_entity(e)
            dropped += 1
    return dropped


def plot_a3(dxf_path, out_pdf, crop=False):
    from ezdxf.addons.drawing import Frontend, RenderContext, layout, pymupdf
    from ezdxf.addons.drawing.config import BackgroundPolicy, Configuration

    doc = ezdxf.readfile(dxf_path)
    dropped = crop_to_frame(doc) if crop else 0
    msp = doc.modelspace()
    backend = pymupdf.PyMuPdfBackend()
    cfg = Configuration(
        background_policy=BackgroundPolicy.WHITE, lineweight_scaling=0.7
    )
    Frontend(RenderContext(doc), backend, config=cfg).draw_layout(msp)
    page = layout.Page(420, 297, layout.Units.mm, margins=layout.Margins.all(0))
    data = backend.get_pdf_bytes(page, settings=layout.Settings(fit_page=True, scale=1))
    with open(out_pdf, "wb") as fh:
        fh.write(data)
    return dropped


# --------------------------------------------------------------------------
def cover_page(doc):
    """Cover in the style of the TD title page, adapted for Prilog III."""
    page = doc.new_page(width=595, height=842)  # A4 portrait
    # The mark comes from cad/bht-logo.svg, the file the drawing title blocks
    # trace, and is placed as vector. It used to be lifted out of the TD .docx by
    # make_prilog1, which Rev 8 deleted: the import failed inside a bare except
    # and the Rev 8 cover shipped without a logo.
    svg = fitz.open(LOGO_SVG)
    logo = fitz.open("pdf", svg.convert_to_pdf())
    w = 52 * logo[0].rect.width / logo[0].rect.height
    page.show_pdf_page(fitz.Rect(60, 50, 60 + w, 50 + 52), logo, 0)

    # The base-14 PDF fonts have no š/ć/č/ž/đ, so Bosnian text comes out with
    # question marks. Embed the system Arial instead.
    fonts = {}
    for tag, fname in (("bht", "arial.ttf"), ("bhtb", "arialbd.ttf")):
        p = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", fname)
        if os.path.exists(p):
            page.insert_font(fontname=tag, fontfile=p)
            fonts[tag] = True

    def line(txt, y, size, bold=False, colour=(0, 0, 0), align=1):
        if bold:
            font = "bhtb" if "bhtb" in fonts else "hebo"
        else:
            font = "bht" if "bht" in fonts else "helv"
        page.insert_textbox(
            fitz.Rect(50, y, 545, y + size * 3.4),
            txt,
            fontname=font,
            fontsize=size,
            color=colour,
            align=align,
        )

    line("BH TELECOM d.d. SARAJEVO", 120, 13, bold=True)
    line(
        "Izvršna direkcija za tehnologiju i razvoj servisa",
        140,
        10,
        colour=(0.35, 0.35, 0.35),
    )
    page.draw_line(
        fitz.Point(50, 168), fitz.Point(545, 168), color=(0.96, 0.51, 0.12), width=1.6
    )

    line("TENDERSKA DOKUMENTACIJA ZA NABAVKU", 210, 14, bold=True)
    line(
        "INFRASTRUKTURA I INSTALACIJA OPREME ZA AUTONOMNI HIBRIDNI "
        "SISTEM NAPAJANJA SJEDNICA, BILEĆA (LOT 1 i 2)",
        250,
        13,
        bold=True,
    )
    line(
        "PROVOĐENJEM NABAVKE PUTEM PREGOVARAČKOG POSTUPKA NABAVKE "
        "SA OBJAVOM OBAVJEŠTENJA",
        330,
        10,
        colour=(0.35, 0.35, 0.35),
    )

    page.draw_rect(fitz.Rect(90, 400, 505, 500), color=(0.96, 0.51, 0.12), width=1.2)
    line("PRILOG III", 418, 20, bold=True)
    line("SITUACIJA, DISPOZICIJA OPREME I GRAFIČKI PRILOZI (NACRTI)", 452, 11)

    line("Lokacija:  BS Sjednica, Bileća, BiH", 560, 10)
    line("Koordinate:  42,9448° N · 18,3236° E · 1076 m n.v.", 578, 10)
    line("Sarajevo, august 2026. godine", 700, 11, bold=True)
    return page


def page_text(page):
    """Text with the PDF's non-breaking spaces and soft hyphens normalised.

    This annex sets words with NBSP between them, so a plain substring search
    for "OPŠTI PODACI O LOKACIJI" finds nothing.
    """
    return page.get_text().replace("\xa0", " ").replace("­", "-").replace("‑", "-")


def portrait_page(out, src, pno, margin=40):
    """Put the site photo on an A4 portrait sheet, so the front matter (cover,
    photo, site data) reads as one portrait set before the A3 drawings.

    The source is A3 landscape with a portrait photograph in the middle and the
    title block bottom right. Fitting the whole sheet would leave the photo tiny,
    so the photo and the title block are placed separately.
    """
    sp = src[pno]
    page = out.new_page(width=595, height=842)
    photo = None
    for im in sp.get_images(full=True):
        for r in sp.get_image_rects(im[0]):
            if photo is None or r.get_area() > photo.get_area():
                photo = r
    if photo is None:                                   # no image - fit the sheet
        w = 595 - 2 * margin
        h = w * sp.rect.height / sp.rect.width
        page.show_pdf_page(fitz.Rect(margin, (842 - h) / 2, margin + w,
                                     (842 - h) / 2 + h), src, pno)
        return page

    w = 595 - 2 * margin
    h = w * photo.height / photo.width
    if h > 660:                                         # keep room for the strip
        h = 660
        w = h * photo.width / photo.height
    x0 = (595 - w) / 2
    page.show_pdf_page(fitz.Rect(x0, margin + 22, x0 + w, margin + 22 + h),
                       src, pno, clip=photo)
    # title-block strip from the bottom right of the source sheet
    strip = fitz.Rect(sp.rect.width * 0.58, sp.rect.height * 0.90,
                      sp.rect.width - 18, sp.rect.height - 8)
    sh = w * strip.height / strip.width
    top = margin + 22 + h + 16
    page.show_pdf_page(fitz.Rect(x0, top, x0 + w, top + sh), src, pno, clip=strip)
    return page


def site_data_page(doc):
    """Set the site-data page from data instead of inheriting it.

    It used to be lifted verbatim out of the previous annex, which meant it went
    on saying 22 kVA / 17,6 kW, "FG Wilson P22-6" and "ograda visine 1,90 m" long
    after all three were superseded - and `check_consistency` cannot see it,
    because Prilog III carries no text layer once assembled, so a stale figure
    here shipped unnoticed.

    Spot-redacting the inherited page was tried and reverted: its values share
    text objects with the labels beside them, so a redaction rect takes the
    neighbour with it and the reprint collides with the next column. The same
    flaw truncated "Bileća" to "Bile" when the entity was stripped. Rebuilding
    the page is both simpler and self-maintaining - every figure below comes
    from cad/design.json.
    """
    import json

    d = json.load(open(os.path.join(BASE, "cad", "design.json"), encoding="utf-8"))
    g, a, m, tk, c = d["genset"], d["array"], d["module"], d["tank"], d["container"]
    fence = 2.10                       # certified 04 Ograda.dwg (Rev 6)

    page = doc.new_page(width=595, height=842)
    fonts = {}
    for tag, fname in (("bht", "arial.ttf"), ("bhtb", "arialbd.ttf")):
        p = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", fname)
        if os.path.exists(p):
            page.insert_font(fontname=tag, fontfile=p)
            fonts[tag] = True
    reg = "bht" if "bht" in fonts else "helv"
    bold = "bhtb" if "bhtb" in fonts else "hebo"

    page.insert_textbox(fitz.Rect(50, 60, 545, 90), "1.  OPŠTI PODACI O LOKACIJI",
                        fontname=bold, fontsize=14)
    page.draw_line(fitz.Point(50, 92), fitz.Point(545, 92),
                   color=(0.96, 0.51, 0.12), width=1.6)

    rows = [
        ("Investitor", "BH Telecom d.d. Sarajevo, Franca Lehara 7, 71000 Sarajevo"),
        ("Objekat", "Bazna stanica SJEDNICA"),
        ("Općina", "Bileća"),
        ("Koordinate", "42,9448° N,  18,3236° E"),
        ("Nadmorska visina", "1076 m"),
        ("Zakupljena površina", "≈150 m² (dio k.č. 1/1, k.o. Granica 2)"),
        ("Betonski temelj", f"5,40 × 5,40 m, sa metalnom ogradom visine "
                            f"{fence:.2f} m".replace(".", ",")),
        ("Antenski stub", "Rešetkasta izvedba, visina 38 m; baza 4,20 m (dno) / "
                          "1,20 m (vrh)"),
        ("Kontejner", f"Vanjske dimenzije {c['ext'][0] / 1000:.3f} × "
                      f"{c['ext'][1] / 1000:.2f} m, zidni paneli {c['wall']} mm; "
                      f"IP55, prema ovjerenom projektu lokacije; PRAZAN"
                      .replace(".", ",")),
        ("Priključak na EES", "NE — lokacija nije priključena na "
                              "elektroenergetsku mrežu"),
        ("TK oprema", "Huawei RRU (3 kom) + BBU/MPLS, −48 VDC"),
        ("Snaga potrošača", "1.180 W nazivno / 1.330 W maksimalno (sa hlađenjem)"),
        ("Sistem napajanja", "Hibridni: FN moduli (primarni) + LFP baterije + "
                             "DEA (rezervni)"),
        ("FN konfiguracija", f"{a['modules_total']} × {m['model'].split('/')[-1].strip()} "
                             f"({a['kWp']:.2f} kWp), fiksni nagib {a['tilt_deg']}°, "
                             f"bifacijalni".replace(".", ",")),
        ("DEA", f"{g['kVA']:g} kVA / {g['kW']} kW stand-by (ISO 8528-3), skid "
                f"izvedba u kontejneru".replace(".", ",")),
        ("Spremnik goriva", f"Dvoplašni, {tk['litres']} l, sa nivo sondom i "
                            f"detekcijom curenja"),
        ("Maks. rad DEA", "250 h/god (standby režim prema ISO 8528)"),
    ]

    x0, x1, x2 = 50, 195, 545
    SIZE = 8.5

    # `insert_textbox` draws NOTHING when the text does not fit and merely
    # returns a negative number - that is how the "Kontejner" row came out blank
    # on the first build of this page. So the row height is measured before the
    # frame is drawn, on a scratch page carrying the same font, and a row that
    # still will not fit stops the build instead of shipping empty.
    scratch = fitz.open()
    probe = scratch.new_page(width=595, height=842)
    arial = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts",
                         "arial.ttf")
    pfont = "p" if os.path.exists(arial) else "helv"
    if pfont == "p":
        probe.insert_font(fontname="p", fontfile=arial)

    def height_for(txt):
        for h in range(24, 108, 11):
            if probe.insert_textbox(fitz.Rect(x1 + 7, 6, x2 - 4, h),
                                    txt, fontname=pfont, fontsize=SIZE) >= 0:
                return h
        raise SystemExit(f"stranica opštih podataka: red ne stane — {txt[:60]!r}")

    y = 115
    for label, value in rows:
        h = height_for(value)
        page.draw_rect(fitz.Rect(x0, y, x2, y + h), color=(0.75, 0.75, 0.75),
                       width=0.6)
        page.draw_line(fitz.Point(x1, y), fitz.Point(x1, y + h),
                       color=(0.75, 0.75, 0.75), width=0.6)
        for rect, txt, font in (
                (fitz.Rect(x0 + 7, y + 6, x1 - 4, y + h), label, bold),
                (fitz.Rect(x1 + 7, y + 6, x2 - 4, y + h), value, reg)):
            if page.insert_textbox(rect, txt, fontname=font,
                                   fontsize=SIZE) < 0:
                raise SystemExit(
                    f"stranica opštih podataka: {txt[:50]!r} nije stalo")
        y += h
    scratch.close()

    page.insert_textbox(
        fitz.Rect(x0, y + 14, x2, y + 90),
        "Napomena: podaci preuzeti iz RFI dokumenta „Autonomno napajanje za BS\" "
        "od 27.04.2026. godine i Projektnog zadatka za hibridno napajanje BS "
        "Sjednica. Konstruktivni podaci kontejnera preuzeti iz Projektnog zadatka "
        "za tipsku prenosivu kućicu — kontejner (opterećenje poda 10,00 kN/m², "
        f"snijeg 3,00 kN/m², vjetar 1,10 kN/m²). DEA kao "
        f"{g['model'].split(' ili ')[0]} (motor "
        f"{g['engine'].split(',')[0]}) ili ekvivalent.",
        fontname=reg, fontsize=7.6, color=(0.25, 0.25, 0.25))
    return page


def strip_entity(page):
    """Drop the entity from the municipality row - the Investor wants the
    opština named on its own."""
    hits = []
    for word in ("Republika", "Srpska"):
        hits += page.search_for(word)
    if not hits:
        return 0
    r = hits[0]
    for h in hits[1:]:
        r |= h
    # reach left far enough to take the separator in "Bileća / Republika Srpska"
    page.add_redact_annot(fitz.Rect(r.x0 - 14, r.y0 - 2, r.x1 + 3, r.y1 + 2),
                          fill=(1, 1, 1))
    page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
    return len(hits)


def old_pages_by_code(src):
    """Map drawing number (INFO-01 ...) to page index in the previous annex."""
    found = {}
    for i in range(src.page_count):
        t = page_text(src[i])
        for code in KEEP_FROM_OLD:
            if code in t:
                found.setdefault(code, i)
    return found


def main():
    if not os.path.exists(OUT):
        raise SystemExit(f"previous annex missing: {OUT}")
    src = fitz.open(OUT)
    codes = old_pages_by_code(src)
    missing = [c for c in KEEP_FROM_OLD if c not in codes]
    if missing:
        raise SystemExit(f"cannot find {missing} in the previous annex")
    # "1. OPŠTI PODACI O LOKACIJI" is the only other inherited page kept
    opsti = next(
        i
        for i in range(src.page_count)
        if "OPŠTI PODACI O LOKACIJI" in page_text(src[i])
    )

    names, tmp = to_dxf([p for p, _, _ in K2_SHEETS])
    plots = []
    for source, caption, crop in K2_SHEETS:
        pdf = os.path.join(tmp, os.path.basename(names[source])[:-4] + ".pdf")
        dropped = plot_a3(names[source], pdf, crop=crop)
        plots.append((pdf, caption))
        note = f"cropped {dropped} stray entities" if crop else "full sheet"
        print(f"  plotted {caption:34s} ({note})")

    out = fitz.open()
    cover_page(out)
    portrait_page(out, src, codes["INFO-01"])
    site_data_page(out)
    print("  site-data page: set from cad/design.json (no longer inherited)")
    for n in ("S-01", "S-02", "S-03", "M-01", "E-01"):
        p = os.path.join(DWG, n + ".pdf")
        if not os.path.exists(p):
            raise SystemExit(f"missing plot {p} - run cad/export.py first")
        out.insert_pdf(fitz.open(p))
    for pdf, _ in plots:
        out.insert_pdf(fitz.open(pdf))
    out.insert_pdf(src, from_page=codes["INFO-02"], to_page=codes["INFO-02"])

    out.set_metadata(
        {
            "title": "Prilog III — Situacija, dispozicija opreme i grafički prilozi",
            "author": "BH Telecom d.d. Sarajevo",
            "subject": "BS Sjednica (Bileća) — autonomni hibridni sistem napajanja",
            "creator": "______________, dipl. ing. ___",
        }
    )
    out.subset_fonts()
    before = os.path.getsize(OUT)
    src.close()
    out.save(
        OUT,
        garbage=4,
        deflate=True,
        deflate_images=True,
        deflate_fonts=True,
        clean=True,
    )
    n = out.page_count
    out.close()
    shutil.rmtree(tmp, ignore_errors=True)
    print(
        f"\nPrilog III: {n} pages, {before / 1e6:.1f} MB -> "
        f"{os.path.getsize(OUT) / 1e6:.2f} MB"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
