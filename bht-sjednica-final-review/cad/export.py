# -*- coding: utf-8 -*-
"""
Export pipeline for the tender drawings.

    DXF (ezdxf)  ->  DWG AC1024 (ODA File Converter)  ->  DXF  ->  verify
                 ->  A3 PDF (ezdxf matplotlib backend)

ODA File Converter works on whole directories, so the DXFs are staged into a
scratch folder and the products copied back next to the sources.
"""
from __future__ import annotations

import collections
import glob
import os
import shutil
import subprocess
import sys
import tempfile

import ezdxf

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "tools"))
from paths import GRAFIKA as DWGDIR                                 # noqa: E402
ODA = os.environ.get(
    "ODA_CONVERTER_PATH",
    r"C:\Program Files\ODA\ODAFileConverter\ODAFileConverter.exe")

# AC1024 = AutoCAD 2010, matching the site project's architectural drawings
DWG_VERSION = "ACAD2010"


def _oda(indir, outdir, out_ext, version):
    os.makedirs(outdir, exist_ok=True)
    cmd = [ODA, indir, outdir, version, out_ext, "0", "1"]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    produced = glob.glob(os.path.join(outdir, "*." + out_ext.lower()))
    if not produced:
        raise RuntimeError(
            f"ODA produced nothing.\ncmd={cmd}\nstdout={p.stdout}\nstderr={p.stderr}")
    return produced


def to_dwg(dxf_paths):
    """Convert DXFs to DWG and drop the .dwg next to each source."""
    made = []
    with tempfile.TemporaryDirectory() as tmp:
        src, dst = os.path.join(tmp, "in"), os.path.join(tmp, "out")
        os.makedirs(src)
        for p in dxf_paths:
            shutil.copy(p, src)
        for produced in _oda(src, dst, "DWG", DWG_VERSION):
            target = os.path.join(DWGDIR, os.path.basename(produced))
            shutil.copy(produced, target)
            made.append(target)
    return made


def verify_dwg(dwg_paths):
    """Round-trip each DWG back to DXF and report what a real DWG engine sees."""
    ok = True
    with tempfile.TemporaryDirectory() as tmp:
        src, dst = os.path.join(tmp, "in"), os.path.join(tmp, "out")
        os.makedirs(src)
        for p in dwg_paths:
            shutil.copy(p, src)
        backs = _oda(src, dst, "DXF", "ACAD2018")
        for b in sorted(backs):
            name = os.path.basename(b)[:-4]
            hdr = open(os.path.join(DWGDIR, name + ".dwg"), "rb").read(6).decode()
            d = ezdxf.readfile(b)
            msp = d.modelspace()
            ents = collections.Counter(e.dxftype() for e in msp)
            layers = [l.dxf.name for l in d.layers]
            texts = [e.dxf.text for e in msp.query("TEXT")]
            dia = sum(1 for t in texts if any(c in t for c in "čćžšđČĆŽŠĐ"))
            status = "OK " if hdr == "AC1024" and len(msp) > 20 else "FAIL"
            ok &= status == "OK "
            print(f"  {status} {name}.dwg  hdr={hdr}  entities={sum(ents.values()):4d} "
                  f"layers={len(layers):2d}  diacritic-texts={dia}")
            print(f"        {dict(ents.most_common(6))}")
    return ok


def to_pdf(dxf_paths):
    """
    Plot each sheet to a true A3 landscape PDF.

    Uses ezdxf's PyMuPDF backend rather than the matplotlib one: matplotlib sizes the
    page from the drawing extents (which produced 172 x 122 mm sheets, not A3) and
    converts every glyph to a filled path, so the plots carried no selectable text.
    """
    from ezdxf.addons.drawing import Frontend, RenderContext, layout, pymupdf
    from ezdxf.addons.drawing.config import BackgroundPolicy, Configuration

    made = []
    for p in dxf_paths:
        doc = ezdxf.readfile(p)
        msp = doc.modelspace()
        ctx = RenderContext(doc)
        backend = pymupdf.PyMuPdfBackend()
        cfg = Configuration(background_policy=BackgroundPolicy.WHITE,
                            lineweight_scaling=0.7)
        Frontend(ctx, backend, config=cfg).draw_layout(msp)
        page = layout.Page(420, 297, layout.Units.mm,
                           margins=layout.Margins.all(0))
        data = backend.get_pdf_bytes(page, settings=layout.Settings(
            fit_page=True, scale=1))
        out = p[:-4] + ".pdf"
        with open(out, "wb") as fh:
            fh.write(data)
        made.append(out)
        import fitz
        d = fitz.open(out)
        w, h = d[0].rect.width * 25.4 / 72, d[0].rect.height * 25.4 / 72
        ntxt = len(d[0].get_text().strip())
        d.close()
        flag = "OK " if abs(w - 420) < 2 and abs(h - 297) < 2 else "SIZE?"
        print(f"  {flag} {os.path.basename(out):10s} {w:.0f} x {h:.0f} mm  "
              f"{os.path.getsize(out)/1024:5.0f} KB  text={ntxt}")
    return made


def main(names=None):
    dxfs = sorted(glob.glob(os.path.join(DWGDIR, "*.dxf")))
    if names:
        dxfs = [p for p in dxfs if os.path.basename(p)[:-4] in names]
    if not dxfs:
        raise SystemExit("no DXF sheets found - run build_drawings.py first")
    print(f"sheets: {[os.path.basename(p) for p in dxfs]}\n")
    print("DXF -> DWG:")
    dwgs = to_dwg(dxfs)
    print("\nverify DWG (round-trip through ODA, read with ezdxf):")
    ok = verify_dwg(dwgs)
    print("\nDXF -> A3 PDF:")
    to_pdf(dxfs)
    print("\nRESULT:", "all sheets verified" if ok else "SOME SHEETS FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:] or None))
