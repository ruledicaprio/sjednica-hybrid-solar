# -*- coding: utf-8 -*-
"""Render a DXF sheet to PNG (visual check) and to A3 PDF (deliverable)."""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import ezdxf
from ezdxf.addons.drawing import Frontend, RenderContext
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf.addons.drawing.config import Configuration, BackgroundPolicy, ColorPolicy

HERE = os.path.dirname(os.path.abspath(__file__))
DWG = os.path.join(os.path.dirname(HERE), "TD-OUTPUT", "DWG")


def render(dxf_path, out_path, dpi=150, dark_on_white=True):
    doc = ezdxf.readfile(dxf_path)
    msp = doc.modelspace()
    ctx = RenderContext(doc)
    ctx.set_current_layout(msp)

    # A3 landscape, exact aspect
    fig = plt.figure(figsize=(420 / 25.4, 297 / 25.4))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_axis_off()
    cfg = Configuration(
        background_policy=BackgroundPolicy.WHITE,
        color_policy=ColorPolicy.COLOR if not dark_on_white else ColorPolicy.BLACK,
        lineweight_scaling=0.7,
    )
    Frontend(ctx, MatplotlibBackend(ax), config=cfg).draw_layout(msp, finalize=True)
    fig.savefig(out_path, dpi=dpi, facecolor="white")
    plt.close(fig)
    return out_path


def render_window(dxf_path, out_path, window, dpi=200, pad=400,
                  skip_layers=("Okvir",), drop_leaders=False, text_scale=1.0,
                  in_colour=False):
    """Render only the model-space rectangle `window` = (x0, y0, x1, y1).

    Used to lift the container layout out of M-01 as a figure for Prilog I, so
    the drawing and the specification cannot drift apart.  The sheet frame and
    title block ("Okvir") are dropped - inside a document they would frame the
    page a second time.

    A sheet is drawn for A3 at 1:25; inside an A4 document the same content is
    roughly half the size, so `drop_leaders` removes the leader callouts (whose
    text lands outside a tight window anyway) and `text_scale` enlarges the
    labels that remain.  The callout wording lives in the Prilog I table
    instead, so nothing is lost.
    """
    doc = ezdxf.readfile(dxf_path)
    msp = doc.modelspace()
    ctx = RenderContext(doc)
    ctx.set_current_layout(msp)
    x0, y0, x1, y1 = window

    keep = []
    for e in msp:
        if e.dxf.get("layer") in skip_layers:
            continue
        if drop_leaders and e.dxf.get("layer") == "Izvod":
            continue
        if e.dxftype() == "TEXT":
            ins = e.dxf.insert
            if not (x0 <= ins.x <= x1 and y0 <= ins.y <= y1):
                continue
            if text_scale != 1.0:
                e.dxf.height *= text_scale
        keep.append(e)

    fig = plt.figure(figsize=((x1 - x0) / 1000.0, (y1 - y0) / 1000.0))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_axis_off()
    cfg = Configuration(
        background_policy=BackgroundPolicy.WHITE,
        # openings and the exhaust are only distinguishable by colour: against
        # the solid black wall hatch a monochrome louvre disappears.  SWAP_BW
        # keeps the palette but turns ACI 7 (white on a CAD screen) into black
        # so the labels survive on a white page.
        color_policy=ColorPolicy.COLOR_SWAP_BW if in_colour else ColorPolicy.BLACK,
        lineweight_scaling=0.7)
    Frontend(ctx, MatplotlibBackend(ax), config=cfg).draw_entities(keep)
    ax.set_xlim(x0 - pad, x1 + pad)
    ax.set_ylim(y0 - pad, y1 + pad)
    fig.savefig(out_path, dpi=dpi, facecolor="white")
    plt.close(fig)
    return out_path


if __name__ == "__main__":
    names = sys.argv[1:] or [f[:-4] for f in os.listdir(DWG) if f.endswith(".dxf")]
    for n in names:
        src = os.path.join(DWG, n + ".dxf")
        png = os.path.join(HERE, f"_{n}.png")
        render(src, png, dpi=130, dark_on_white=False)
        print("rendered", png)
