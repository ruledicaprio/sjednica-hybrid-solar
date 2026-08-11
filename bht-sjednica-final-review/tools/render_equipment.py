"""Render clean, print-ready equipment figures for Prilog I.

Sources (vendor filenames are unreliable — mapping below reflects actual content):
  - reference/P_22-6_*.png        : dark-background wireframe renders of the P22-6
                                    genset -> inverted to black-on-white.
  - EQUIPEMENT/GENSET/*.pdf       : tessellated-mesh vector plots of the 500 l tank
                                    -> rasterised at 300 DPI so mesh edges become
                                    hairlines; silhouette dominates in print.

Output: EQUIPEMENT/GENSET/render/*.png (white background, cropped to content).
"""
from pathlib import Path

import fitz
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "reference"
GEN = ROOT / "EQUIPEMENT" / "GENSET"
OUT = GEN / "render"

# actual content -> (source, kind)
SOURCES = {
    # genset: dark wireframe renders, invert to print form
    "genset_side": (REF / "P_22-6_FG_Wilson_LONG_SIDE_VIEW_compressed.png", "invert"),
    "genset_front": (REF / "P_22-6_FG_Wilson_SHORT_SIDE_VIEW_GEN_compressed.png", "invert"),
    # tank: vendor PDFs (mislabelled as P22-6 views — they show the 500 l tank)
    "tank_side": (GEN / "FG_Wilson_P_22-6_LONG_SIDE_VIEW.pdf", "pdf"),
    "tank_top": (GEN / "FG_Wilson_P_22-6_TOP_VIEW.pdf", "pdf"),
}

MARGIN = 24  # px kept around the content bbox


def _autocrop(img: Image.Image, threshold: int = 245) -> Image.Image:
    """Crop white margins, keep a small border. Also drops tiny stray view
    labels ('TOP', 'FRONT') hugging the sheet edge by cropping to the main
    content cluster."""
    gray = img.convert("L")
    mask = gray.point(lambda v: 255 if v < threshold else 0)
    bbox = mask.getbbox()
    if bbox:
        l, t, r, b = bbox
        l = max(0, l - MARGIN)
        t = max(0, t - MARGIN)
        r = min(img.width, r + MARGIN)
        b = min(img.height, b + MARGIN)
        img = img.crop((l, t, r, b))
    return img


def render_pdf(path: Path, dpi: int = 300) -> Image.Image:
    doc = fitz.open(path)
    pix = doc[0].get_pixmap(dpi=dpi)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    doc.close()
    return img


def invert_reference(path: Path) -> Image.Image:
    img = Image.open(path).convert("L")
    # vendor renders carry a tiny "TOP"/"RIGHT" label in the outer margin;
    # the machine is centred, so trim 5 % per side before autocrop
    dx, dy = int(img.width * 0.05), int(img.height * 0.05)
    img = img.crop((dx, dy, img.width - dx, img.height - dy))
    img = ImageOps.invert(img)          # white-on-dark -> dark-on-white
    img = ImageOps.autocontrast(img, cutoff=1)
    # lift the near-white haze left by the dark background
    img = img.point(lambda v: 255 if v > 230 else v)
    return img.convert("RGB")


def render_layout() -> None:
    """Lift the container layout out of drawing M-01 so Prilog I 4.3 shows the
    same arrangement the tender drawing does."""
    import sys
    sys.path.insert(0, str(ROOT / "cad"))
    import render as cad_render

    dxf = ROOT / "TD-OUTPUT" / "DWG" / "M-01.dxf"
    if not dxf.exists():
        print("skip layout figure: build the drawings first (cad/build_drawings.py)")
        return
    dst = OUT / "layout_m01.png"
    cad_render.render_window(str(dxf), str(dst), (1750, 5550, 8350, 9120),
                             dpi=200, pad=0, skip_layers=("Okvir", "Kote"),
                             drop_leaders=True, text_scale=1.7, in_colour=True)
    print(f"{dst.name} <- M-01.dxf")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    for name, (src, kind) in SOURCES.items():
        img = render_pdf(src) if kind == "pdf" else invert_reference(src)
        img = _autocrop(img)
        dst = OUT / f"{name}.png"
        img.save(dst, optimize=True)
        print(f"{dst.name}: {img.width}x{img.height} <- {src.name}")
    render_layout()


if __name__ == "__main__":
    main()
