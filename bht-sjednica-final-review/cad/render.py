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


if __name__ == "__main__":
    names = sys.argv[1:] or [f[:-4] for f in os.listdir(DWG) if f.endswith(".dxf")]
    for n in names:
        src = os.path.join(DWG, n + ".dxf")
        png = os.path.join(HERE, f"_{n}.png")
        render(src, png, dpi=130, dark_on_white=False)
        print("rendered", png)
