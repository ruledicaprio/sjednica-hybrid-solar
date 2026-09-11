# -*- coding: utf-8 -*-
"""
Tender drawings for BS Hamzići (Čitluk), in the style of the BS Sjednica package.

    H-01  Situacija — postojeće stanje              1:100
    H-02  Situacija — buduće stanje                 1:100
    H-03  Presjek A–A kroz FN polje                 1:30
    H-04  Agregat u kontejneru — osnova i presjek   1:25
    H-05  Jednopolna šema novog GRO                 —

Frame, title block, layers, text and dimension styles are the Sjednica ones
(bht-sjednica-final-review/cad/bht_frame.py) and so are the drawing helpers
(build_drawings.py: rect, hatch_rect, solid_rect, dim_h, dim_v, leader, legend,
note_block).  Both modules are imported, never copied.  build_drawings loads the
Sjednica site_geometry.json when it is imported; that GEO is never used here.

S-03, M-01 and E-01 in sheets_new.py are closures with the Sjednica values
written into them - fence 2100 mm, the Sjednica 38 m tower taper, a container
lying E-W with its door on the east wall, the Sjednica title block - so none of
them can be called with a patched design dict.  H-03, H-04 and H-05 are
equivalents of them, with every Hamzići coordinate derived from this folder's
design.json and site_geometry.json.

Frame convention: slab-local millimetres, origin = SW corner of the existing
5400 x 5400 slab, +X = EAST, +Y = NORTH - the TRUE orientation.  The certified
2017 drawing is rotated about 180 deg against the site (site_geometry.json,
"orientation"); the small residual rotation is not measured.
"""
from __future__ import annotations

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SJ_CAD = os.path.join(os.path.dirname(os.path.dirname(HERE)),
                      "bht-sjednica-final-review", "cad")
if SJ_CAD not in sys.path:
    sys.path.insert(0, SJ_CAD)

from ezdxf.enums import TextEntityAlignment as TA                  # noqa: E402

from bht_frame import (A3_H, A3_W, MARGIN, MARGIN_L, TB_H, TB_W,   # noqa: E402
                       draw_frame, new_doc, north_arrow, scale_bar, _txt)
import build_drawings as B                                          # noqa: E402

rect, solid_rect, hatch_rect = B.rect, B.solid_rect, B.hatch_rect
dim_h, dim_v, leader = B.dim_h, B.dim_v, B.leader
legend, note_block = B.legend, B.note_block


def _load(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as fh:
        return json.load(fh)


GEO = _load("site_geometry.json")
D = _load("design.json")

# --------------------------------------------------------------------------
# Values the two JSON files do not carry.  Each one is stated on the sheet that
# depends on it and listed in the build report.
# --------------------------------------------------------------------------
ARRAY_GAP = 400          # clear gap between stands (brief: 3 x 2305 + 2 x 400 = 7715)
MIN_CLEAR = 100          # strips must stay >= ~0,1 m off the slab and inside the lease
FRAME_W = 740            # load-spreading frame under the 620 mm skid (as Sjednica M-01)
FRAME_H = 60             # its height, drawn schematically in section 1-1
PLENUM = 120             # radiator face -> inner face of the south wall (Sjednica M-01 gap)
DIS_Z0 = 300             # bottom of the combined Stulz discharge opening (to be measured)
HOOD_W, HOOD_D = 700, 600   # deflector hood over the discharge, outside the south wall
HOOD_Z = 1300            # its top louvre: the warm air leaves UPWARDS, not onto the PV array
LEG_CLEAR = 1000         # hood -> south tower legs, minimum
INTAKE_Y = 1550          # intake centre on the WEST wall: alternator end, north of the tank
EXH_Y = 1000             # exhaust run, container-relative Y (engine outlet, schematic)
EXH_Z = 2300             # exhaust through the east wall "≈+2,30 m" (design.json layout)
EXH_OUT = 400            # exhaust pipe projects beyond the east wall
GRO_W, GRO_D, GRO_H = 500, 250, 800   # the north wall west of the door is only 595 mm
GRO_Z = 1000             # underside of the GRO (section 1-1)
FAN_D = 315              # room fan Ø315
FAN_Y = 2400             # room fan centre on the WEST wall, north of the intake
FAN_Z = 1950             # underside of the fan ("gore")
DCB_W, DCB_H, DCB_D = 300, 200, 150   # DC razvod -48 V box (coordinator: ≈300 × 200 × 150)
DCB_GAP = 120            # door's east jamb -> DC razvod box
DCB_Z = 1600             # underside of the DC razvod box
SLAB_T = 300             # slab thickness drawn in section A-A (not in the inputs)
EARTH_RINGS = tuple(GEO["earth_rings"]["offset_from_slab_mm"])    # 3.6.9, at 0,8 m
TERRAIN = GEO["terrain"]["level_mm"]                               # -200 vs slab top
FENCE_ABOVE_GROUND = GEO["fence"]["height"] - TERRAIN              # 1800 + 200
# design.json array.above_fence (1936) predates the -0,20 terrain; this supersedes it
PV_OVER_FENCE = D["array"]["top_edge"] - FENCE_ABOVE_GROUND        # 1736

OBJEKAT = "BS HAMZIĆI (ČITLUK) — autonomni hibridni sistem napajanja"
SIFRA = "BHT-HAMZICI-2026"


def minus(v, nd=2):
    """-200 -> '−0,20' with a true minus sign."""
    return ("−" if v < 0 else "+") + dec(abs(v), nd)


def site_checks():
    """Tank vent and ICC360 rules set by the coordinator (11.09.2026).

    Vent >= 3 m straight line from the exhaust termination and from the intake
    louvre centre, >= 1 m horizontally from the ICC360, below the +3,0 platform;
    ICC360 clear of the NW leg, the door swing, the container and the fence.
    Returns the distances; raises SystemExit if a rule is broken.
    """
    L = interior()
    cx0, cy0 = GEO["container"]["origin"]
    E = (cx0 + L["cw"] + EXH_OUT, cy0 + L["exh_y"], EXH_Z)
    I = (cx0, cy0 + sum(L["intake"]) / 2, sum(L["intake_z"]) / 2)
    tv = GEO["tank_vent"]
    V = (*tv["termination"], tv["termination_z_mm"])
    ic = GEO["icc360"]
    (ix, iy), (iw, ih) = ic["footprint"]["origin"], ic["footprint"]["size"]
    dx = max(ix - V[0], 0, V[0] - (ix + iw))
    dy = max(iy - V[1], 0, V[1] - (iy + ih))
    r = {"vent_exhaust": math.dist(V, E), "vent_intake": math.dist(V, I),
         "vent_icc360": math.hypot(dx, dy), "exhaust_intake": math.dist(E, I)}
    hx, hy, hw, hd = L["hood"]
    lf = GEO["tower"]["leg_footprint"][0]
    r["hood_leg"] = min(
        math.hypot(max(lx_ - lf / 2 - (cx0 + hx + hw), 0, cx0 + hx - (lx_ + lf / 2)),
                   max(ly_ - lf / 2 - (cy0 + hy + hd), 0, cy0 + hy - (ly_ + lf / 2)))
        for lx_, ly_ in GEO["tower"]["legs_centres"])
    A = array_layout()
    edge = A["fy0"] + A["proj"]                   # the PV field's high (north) edge
    r["wall_array"] = cy0 - edge
    r["hood_array"] = cy0 + hy - edge
    bad = []
    if r["hood_leg"] < LEG_CLEAR:
        bad.append("deflector hood closer than 1 m to a tower leg")
    if r["vent_exhaust"] < 3000 or r["vent_intake"] < 3000:
        bad.append("tank vent closer than 3 m to the exhaust or the intake")
    if r["vent_icc360"] < 1000:
        bad.append("tank vent closer than 1 m to the ICC360")
    if V[2] >= GEO["tower"]["platforms_m"][0] * 1000:
        bad.append("tank vent reaches the +3,0 m platform")
    if r["exhaust_intake"] < 3000:
        bad.append("exhaust termination closer than 3 m to the intake")
    lf = GEO["tower"]["leg_footprint"][0]
    for lx_, ly_ in GEO["tower"]["legs_centres"]:
        if ix < lx_ + lf / 2 and lx_ - lf / 2 < ix + iw and iy < ly_ + lf / 2 and ly_ - lf / 2 < iy + ih:
            bad.append("ICC360 overlaps a tower leg")
    (hx, hy), op = GEO["container"]["door"]["hinge"], GEO["container"]["door"]["opening"]
    for px_, py_ in ((ix + iw, iy), (ix + iw, iy + ih)):
        if math.hypot(px_ - hx, py_ - hy) < op:
            bad.append("ICC360 inside the door swing")
    if iy < cy0 + GEO["container"]["external"][1] or \
            iy + ih > GEO["fence"]["origin"][1] + GEO["fence"]["size"][1]:
        bad.append("ICC360 not between the container and the north fence")
    if bad:
        raise SystemExit("site checks: " + "; ".join(bad))
    return r


# --------------------------------------------------------------------------
# small helpers
# --------------------------------------------------------------------------
def dec(v, nd=2):
    """millimetres -> metres with a decimal comma: 1800 -> '1,80'."""
    return f"{v / 1000:.{nd}f}".replace(".", ",")


def mmc(v):
    """millimetres, with a decimal comma only when needed: 137.5 -> '137,5'."""
    return f"{v:.0f}" if abs(v - round(v)) < 1e-6 else f"{v:.1f}".replace(".", ",")


def _sheet(sc, naziv, broj, razmjera):
    doc = new_doc()
    msp = doc.modelspace()
    draw_frame(msp, sc, naziv=naziv, broj=broj, razmjera=razmjera,
               objekat=OBJEKAT, sifra=SIFRA)
    name = f"M {int(sc)}"
    if name not in doc.dimstyles:
        # bht_frame defines M 20/30/50/100/200 only; without this a 1:25 sheet's
        # dimensions fall back to 'Standard' and print 0,1 mm high (Sjednica M-01
        # carries exactly that defect)
        ds = doc.dimstyles.duplicate_entry("M 20", name)
        ds.dxf.dimscale = float(sc)
    # everything drawn so far is frame + title block; the build's layout check
    # skips these entities
    doc.hz_frame_handles = {e.dxf.handle for e in msp}
    return doc, msp


def ltype(e, name, sc, k=3.0):
    """Give an entity a linetype that actually shows on the plot.

    The ezdxf patterns are a few model units long, so at 1:100 they plot as a
    solid line unless scaled - the Sjednica ring earth printed solid for exactly
    that reason.  (ACAD_ISO03W100, the 'Sakriveno' layer's type, is not loaded by
    new_doc, so that layer falls back to Continuous and needs this as well.)
    """
    e.dxf.linetype = name
    e.dxf.ltscale = k * sc
    return e


def lead(msp, tip, text, elbow, sc, h=2.2):
    """leader() with an absolute elbow point instead of an offset."""
    leader(msp, tip, text, elbow[0] - tip[0], elbow[1] - tip[1], sc, h=h)


def arrow(msp, pts, color=4, size=160, layer="Ventilacija", lw=35):
    """Polyline with a filled arrow head at its last point (as Sjednica M-01)."""
    msp.add_lwpolyline(pts, dxfattribs={"layer": layer, "color": color,
                                        "lineweight": lw})
    (x1, y1), (x0, y0) = pts[-1], pts[-2]
    ang = math.atan2(y1 - y0, x1 - x0)
    a1 = (x1 - size * math.cos(ang - 0.42), y1 - size * math.sin(ang - 0.42))
    a2 = (x1 - size * math.cos(ang + 0.42), y1 - size * math.sin(ang + 0.42))
    msp.add_solid([a1, (x1, y1), a2], dxfattribs={"layer": layer, "color": color})


def dim_free(msp, p1, p2, base, sc, angle=0, text="<>", loc=None):
    """Linear dimension between two arbitrary points (optional text location)."""
    kw = {"location": loc} if loc is not None else {}
    d = msp.add_linear_dim(base=base, p1=p1, p2=p2, angle=angle,
                           dimstyle=f"M {int(sc)}", text=text,
                           dxfattribs={"layer": "Kote"}, **kw)
    d.render()
    return d


# --------------------------------------------------------------------------
# layouts shared between sheets, so the plan, the section and the detail can
# never drift apart (the Sjednica S-02 / M-01 pair did, twice)
# --------------------------------------------------------------------------
def array_layout():
    """PV stands and their strips in the south strip, slab-local mm."""
    sup, arr, fnd = D["support"], D["array"], D["foundation"]
    (lx, ly), (lw, lh) = GEO["parcel"]["lease"]["origin"], GEO["parcel"]["lease"]["size"]
    S = GEO["slab"]["size"][0]
    fw, proj, n = sup["field_w"], sup["proj"], arr["count"]
    sl, sp = fnd["strip_l"], sup["strip_spacing"]
    south = GEO["parcel"]["strips_outside_slab_mm"]["south"]

    if abs(lx + lw / 2 - S / 2) > 1:
        raise SystemExit("lease and slab are no longer concentric E-W - re-centre the array")
    if abs(south + ly) > 1:
        raise SystemExit("strips_outside_slab_mm.south disagrees with the lease origin")

    total = n * fw + (n - 1) * ARRAY_GAP
    xmid = S / 2
    x0 = xmid - total / 2
    margin = (south - sl) / 2            # strip end to lease edge = strip end to slab
    sy0 = -south + margin                # south ends of all strips
    fy0 = sy0 + (sl - proj) / 2          # low (south) edge of the field
    stands = [x0 + i * (fw + ARRAY_GAP) for i in range(n)]
    strips = [ax + fw / 2 + s * sp / 2 for ax in stands for s in (-1, 1)]

    bad = []
    if margin < MIN_CLEAR:
        bad.append(f"strips only {margin:.0f} mm from the slab / lease edge")
    if x0 < lx or x0 + total > lx + lw:
        bad.append("array wider than the lease")
    if fy0 + proj > GEO["fence"]["origin"][1]:
        bad.append("field oversails the south fence")
    if sp / 2 + fnd["strip_w_base"] / 2 > fw / 2:
        bad.append("strip base wider than the stand")
    if bad:
        raise SystemExit("PV layout: " + "; ".join(bad))

    return {"fw": fw, "proj": proj, "sl": sl, "sp": sp, "total": total,
            "xmid": xmid, "x0": x0, "margin": margin, "sy0": sy0, "fy0": fy0,
            "stands": stands, "strips": strips,
            "section_x": xmid - sp / 2}   # A-A runs along PV-2's west strip


def interior():
    """Container layout, container-relative: external SW corner = (0, 0),
    +X east, +Y north.  Used by H-02 (at 1:100) and H-04 (at 1:25).

    The Stulz is centred on the SOUTH wall (Investor, 11.09.2026), so the genset
    stands on the container's centre line, long axis N-S, radiator SOUTH at the
    Stulz cut-outs; a hood outside turns the warm air upwards, off the PV array.
    Rectangles are (x, y, width E-W, height N-S)."""
    c = GEO["container"]
    (cx0, cy0), (cw, ch) = c["origin"], c["external"]
    t = c["wall_panel_thickness"]
    g, tk, v = D["genset"], D["tank"], D["ventilation"]
    kada = tk["kada"]
    st_w, st_d, st_h = GEO["stulz"]["size_mm_estimated"]

    L = {"cw": cw, "ch": ch, "t": t}
    L["door"] = (c["door"]["span_x"][0] - cx0, c["door"]["span_x"][1] - cx0)
    L["hinge"] = (c["door"]["hinge"][0] - cx0, c["door"]["hinge"][1] - cy0)
    L["door_op"] = c["door"]["opening"]

    # the radiator axis is the axis of the Stulz cut-outs, centred on the south wall
    axis = cw / 2
    L["axis"] = axis                                         # an X value
    L["stulz"] = (axis - st_w / 2, -st_d, st_w, st_d)        # outside the south wall
    dis = v["discharge_mm"]
    L["discharge"] = (axis - dis[1] / 2, axis + dis[1] / 2)  # X range in the south wall
    L["dis_z"] = (DIS_Z0, DIS_Z0 + dis[0])
    L["hood"] = (axis - HOOD_W / 2, -HOOD_D, HOOD_W, HOOD_D)

    sx0 = axis - g["skid_W"] / 2
    sy0 = t + PLENUM
    L["skid"] = (sx0, sy0, g["skid_W"], g["skid_L"])
    fm = (FRAME_W - g["skid_W"]) / 2
    L["frame"] = (sx0 - fm, sy0 - fm, FRAME_W, g["skid_L"] + 2 * fm)
    sx1, sy1 = sx0 + g["skid_W"], sy0 + g["skid_L"]

    # tank in the SW corner: no spot keeps both 780 mm sides clear, so the east
    # side is the service side; the intake sits north of the tank, at the
    # alternator end
    L["kada"] = (t, t, kada["W"], kada["L"])
    L["tank"] = (t + (kada["W"] - tk["W"]) / 2, t + (kada["L"] - tk["L"]) / 2,
                 tk["W"], tk["L"])
    iw, ih = v["intake_mm"]
    L["intake"] = (INTAKE_Y - iw / 2, INTAKE_Y + iw / 2)     # Y range in the west wall
    L["intake_z"] = (300, 300 + ih)          # "donja ivica +0,30 m od poda"
    L["fan"] = (FAN_Y - FAN_D / 2, FAN_Y + FAN_D / 2)

    # exhaust: engine outlet on the east side of the skid, up to +2,30, then east
    # through the east wall with the silencer in the east service passage
    L["exh_y"] = EXH_Y
    L["exh_x0"] = sx1 - 120
    L["silencer"] = (sx1 + 100, sx1 + 600)

    wall_w = L["door"][0] - t                               # wall west of the door
    L["gro"] = (t + (wall_w - GRO_W) / 2, ch - t - GRO_D, GRO_W, GRO_D)
    L["gro_wall"] = wall_w
    # DC razvod -48 V east of the door; ceiling LED luminaires (one AC from GRO F2,
    # one 48 V DC from D5); light switch by the door; F1 + DC cable entry above the GRO
    L["dcbox"] = (L["door"][1] + DCB_GAP, ch - t - DCB_D, DCB_W, DCB_D)
    L["lights"] = {"AC": (sx1 + 390, 2250), "DC": (700, 2250)}
    L["switch"] = (L["door"][1] + 60, ch - t)
    L["cable_x"] = L["gro"][0] + GRO_W / 2

    # clearances, measured to the skid (the frame is flat and walkable)
    L["clr"] = {"west": sx0 - t, "west_tank": sx0 - (t + kada["W"]), "east": cw - t - sx1,
                "south": PLENUM, "north_gro": L["gro"][1] - sy1,
                "north_wall": ch - t - sy1}

    bad = []
    fx, fy, fwid, fdep = L["frame"]
    if fx < t or fy < t or fx + fwid > cw - t or fy + fdep > ch - t:
        bad.append("genset frame outside the room")
    if t + kada["W"] > fx:
        bad.append("drip tray overlaps the genset frame")
    if L["intake"][0] < t + kada["L"]:
        bad.append("intake is not north of the drip tray")
    if wall_w < GRO_W:
        bad.append(f"GRO {GRO_W} mm does not fit the {wall_w:.0f} mm of wall")
    if L["fan"][0] <= L["intake"][1]:
        bad.append("room fan is not north of the intake")
    if L["discharge"][0] < t or L["discharge"][1] > cw - t:
        bad.append("discharge opening runs into a corner")
    if L["silencer"][1] > cw - t:
        bad.append("silencer does not fit the east passage")
    if L["dcbox"][0] + DCB_W > cw - t:
        bad.append("DC razvod does not fit on the wall east of the door")
    if L["dcbox"][0] - (L["gro"][0] + GRO_W) < 300:
        bad.append("DC razvod closer than 0,3 m to the GRO")
    if L["clr"]["north_gro"] < 800:
        bad.append("less than 0,8 m in front of the GRO")
    if bad:
        raise SystemExit("container layout: " + "; ".join(bad))
    return L


def plan_equipment(msp, X0, Y0, L, sc, detail):
    """Genset, tank, GRO, openings and exhaust in plan; (X0, Y0) = container SW."""
    t, cw = L["t"], L["cw"]
    sx, sy, sl, sw = L["skid"]
    if detail:
        fx, fy, fw, fd = L["frame"]
        rect(msp, X0 + fx, Y0 + fy, fw, fd, "Konstrukcija", color=5, lw=35)
    rect(msp, X0 + sx, Y0 + sy, sl, sw, "Agregat", color=30, lw=50)
    if detail:
        # radiator band at the SOUTH end, sheet-metal plenum from it to the wall
        rect(msp, X0 + sx, Y0 + sy, sl, 180, "Agregat", color=4, lw=35)
        rect(msp, X0 + sx, Y0 + t, sl, sy - t, "Ventilacija", color=4, lw=35)
    d0, d1 = L["discharge"]
    solid_rect(msp, X0 + d0, Y0, d1 - d0, t, "Ventilacija", 4)
    # deflector hood outside the south wall; the warm air leaves upwards
    hx, hy, hw, hd = L["hood"]
    rect(msp, X0 + hx, Y0 + hy, hw, hd, "Ventilacija", color=4, lw=50 if detail else 35)
    if detail:
        for r_ in (90, 18):                                  # "up" symbol
            msp.add_circle((X0 + hx + hw / 2, Y0 + hy + hd / 2), r_,
                           dxfattribs={"layer": "Ventilacija", "color": 4})
    i0, i1 = L["intake"]
    solid_rect(msp, X0, Y0 + i0, t, i1 - i0, "Ventilacija", 4)
    f0, f1 = L["fan"]
    solid_rect(msp, X0, Y0 + f0, t, f1 - f0, "Ventilacija", 4)

    kx, ky, kw, kh = L["kada"]
    rect(msp, X0 + kx, Y0 + ky, kw, kh, "Agregat", color=1 if detail else 30, lw=35)
    if detail:
        tx, ty, tw, th = L["tank"]
        rect(msp, X0 + tx, Y0 + ty, tw, th, "Agregat", color=30, lw=35)
    gx, gy, gw, gd = L["gro"]
    if not detail:
        solid_rect(msp, X0 + gx, Y0 + gy, gw, gd, "Novi1", 30)
    rect(msp, X0 + gx, Y0 + gy, gw, gd, "Novi1", color=30, lw=50)

    # exhaust: engine outlet on the east side of the skid, up to +2,30 (section),
    # then east out through the wall; silencer in line in the east passage
    ey, ex0 = L["exh_y"], L["exh_x0"]
    msp.add_lwpolyline([(X0 + ex0, Y0 + ey), (X0 + cw + EXH_OUT, Y0 + ey)],
                       dxfattribs={"layer": "Ventilacija", "color": 1,
                                   "lineweight": 50 if detail else 35})
    if detail:
        s0, s1 = L["silencer"]
        rect(msp, X0 + s0, Y0 + ey - 130, s1 - s0, 260, "Ventilacija", color=1, lw=35)


# --------------------------------------------------------------------------
# site plan, shared by H-01 and H-02 (1:100)
# --------------------------------------------------------------------------
PLAN_O = (12300, 13500)          # sheet position of the slab's SW corner


def P(x, y):
    """slab-local -> sheet coordinates on the 1:100 plans."""
    return (PLAN_O[0] + x, PLAN_O[1] + y)


def site_plan(msp, sc, future):
    """Lease, earthing, slab, fence, tower and container.  +X east, +Y north."""
    par = GEO["parcel"]
    (lx, ly), (lw, lh) = par["lease"]["origin"], par["lease"]["size"]
    S = GEO["slab"]["size"][0]
    fe, c, tw = GEO["fence"], GEO["container"], GEO["tower"]
    (fx, fy), (fw, fh) = fe["origin"], fe["size"]
    (cx, cy), (cw, ch) = c["origin"], c["external"]
    t = c["wall_panel_thickness"]
    L = interior()

    # lease (k.č. 109/1)
    e = msp.add_lwpolyline([P(lx, ly), P(lx + lw, ly), P(lx + lw, ly + lh),
                            P(lx, ly + lh)], close=True,
                           dxfattribs={"layer": "Sakriveno", "color": 8,
                                       "lineweight": 35})
    ltype(e, "PHANTOM", sc, 1.5)
    _txt(msp, f"GRANICA ZAKUPA  {dec(lw)} × {dec(lh)} m = {par['leased_area_m2']} m²",
         *P(lx + 1500, ly + lh - 500), 2.0 * sc, color=8)
    _txt(msp, par["cadastral"], *P(lx + 1500, ly + lh - 850), 2.0 * sc, color=8)

    # existing earth rings at 0,8 m (3.6.9), dashed so they read as buried
    for off in EARTH_RINGS:
        e = rect(msp, *P(-off, -off), S + 2 * off, S + 2 * off, "Uzemljenje")
        ltype(e, "DASHED", sc)

    solid_rect(msp, *P(0, 0), S, S, "Objekat", 254)
    rect(msp, *P(0, 0), S, S, "Objekat", color=8)
    fs = tw["footings"]["size"][0]
    for lcx, lcy in tw["legs_centres"]:
        e = rect(msp, *P(lcx - fs / 2, lcy - fs / 2), fs, fs, "Sakriveno", color=8)
        ltype(e, "DASHED", sc, 1.5)

    # fence with the gate gap on the NORTH line
    gx0, gx1 = fe["gate"]["span_x"]
    top = fy + fh
    msp.add_lwpolyline([P(gx0, top), P(fx, top), P(fx, fy), P(fx + fw, fy),
                        P(fx + fw, top), P(gx1, top)],
                       dxfattribs={"layer": "Ograda", "color": 8, "lineweight": 50})
    for gx in (gx0, gx1):
        solid_rect(msp, *P(gx - 35, top - 35), 70, 70, "Ograda", 8)
    # Drawn opening OUTWARD: swung in, the 1300 mm leaf would strike the
    # container's north wall, which stands only 1247,5 mm inside the fence.
    (hx, hy), leaf = fe["gate"]["hinge"], fe["gate"]["leaf"]
    msp.add_line(P(hx, hy), P(hx, hy + leaf), dxfattribs={"layer": "Ograda", "color": 8})
    msp.add_arc(center=P(hx, hy), radius=leaf, start_angle=0, end_angle=90,
                dxfattribs={"layer": "Ograda", "color": 8})

    # tower legs and outline (the platform P I at +3,0 m spans it)
    lf = tw["leg_footprint"][0]
    legs = tw["legs_centres"]
    for lcx, lcy in legs:
        solid_rect(msp, *P(lcx - lf / 2, lcy - lf / 2), lf, lf, "Konstrukcija", 5)
    ring = sorted(legs, key=lambda p: math.atan2(p[1] - S / 2, p[0] - S / 2))
    e = msp.add_lwpolyline([P(*p) for p in ring], close=True,
                           dxfattribs={"layer": "Osovina", "color": 8})
    ltype(e, "CENTER", sc, 2)

    # container, 60 mm walls, north wall split at the door
    X0, Y0 = P(cx, cy)
    rect(msp, X0, Y0, cw, ch, "Objekat", color=6, lw=50)
    rect(msp, X0 + t, Y0 + t, cw - 2 * t, ch - 2 * t, "Objekat", color=6)
    d0, d1 = L["door"]
    for x, y, w, h in ((0, 0, cw, t), (0, t, t, ch - 2 * t),
                       (cw - t, t, t, ch - 2 * t),
                       (0, ch - t, d0, t), (d1, ch - t, cw - d1, t)):
        solid_rect(msp, X0 + x, Y0 + y, w, h, "Objekat", 8)
    (hxr, hyr), op = L["hinge"], L["door_op"]
    msp.add_line((X0 + hxr, Y0 + hyr), (X0 + hxr, Y0 + hyr + op),
                 dxfattribs={"layer": "Objekat", "color": 8})
    msp.add_arc(center=(X0 + hxr, Y0 + hyr), radius=op, start_angle=90,
                end_angle=180, dxfattribs={"layer": "Objekat", "color": 8})

    if not future:
        # existing Stulz wall unit, crossed out: it is removed
        sx_, sy_, sw_, sh_ = L["stulz"]
        a, b = X0 + sx_, Y0 + sy_
        rect(msp, a, b, sw_, sh_, "Objekat", color=1, lw=35)
        msp.add_line((a, b), (a + sw_, b + sh_), dxfattribs={"layer": "Objekat", "color": 1})
        msp.add_line((a, b + sh_), (a + sw_, b), dxfattribs={"layer": "Objekat", "color": 1})
    else:
        plan_equipment(msp, X0, Y0, L, sc, detail=False)
        sx, sy, sl, sw = L["skid"]
        _txt(msp, "DEA", X0 + sx + sl / 2 - 150, Y0 + sy + sw / 2, 1.6 * sc, color=7,
             align=TA.MIDDLE_CENTER)
        tx, ty, tw_, th = L["tank"]
        _txt(msp, "500 l", X0 + tx + tw_ / 2, Y0 + ty + th / 2, 1.4 * sc, color=7,
             align=TA.MIDDLE_CENTER, rotation=90)
    return {"L": L, "X0": X0, "Y0": Y0}


def plan_dims(msp, sc, container_dims=True):
    """Lease, the four strips outside the slab, and (H-01) the container."""
    par = GEO["parcel"]
    (lx, ly), (lw, lh) = par["lease"]["origin"], par["lease"]["size"]
    S = GEO["slab"]["size"][0]
    st = par["strips_outside_slab_mm"]
    for k, v in (("north", ly + lh - S), ("south", -ly), ("east", lx + lw - S),
                 ("west", -lx)):
        if abs(st[k] - v) > 1:
            raise SystemExit(f"strip {k}: json says {st[k]}, lease gives {v}")
    dim_h(msp, *(P(lx, 0)[0], P(lx + lw, 0)[0]), P(0, ly + lh)[1], sc, off=1000)
    dim_v(msp, P(0, ly)[1], P(0, ly + lh)[1], P(lx, 0)[0], sc, off=-700)
    xs = P(lx + 1100, 0)[0]                  # N and S strips, west part
    dim_v(msp, P(0, S)[1], P(0, ly + lh)[1], xs, sc, off=0)
    dim_v(msp, P(0, ly)[1], P(0, 0)[1], xs, sc, off=0)
    ye = P(0, S - 1300)[1]                   # E and W strips
    dim_h(msp, P(lx, 0)[0], P(0, 0)[0], ye, sc, off=0)
    dim_h(msp, P(S, 0)[0], P(lx + lw, 0)[0], ye, sc, off=0)
    if container_dims:
        c = GEO["container"]
        (cx, cy), (cw, ch) = c["origin"], c["external"]
        dim_h(msp, P(cx, 0)[0], P(cx + cw, 0)[0], P(0, cy)[1], sc, off=-600)
        dim_v(msp, P(0, cy)[1], P(0, cy + ch)[1], P(cx, 0)[0], sc, off=-500)


WX, EX = 7600, 21800             # elbow x of west / east callouts on the plans
NOTES_X = 28000                  # right-hand note column on the plans


def _orientation_note(msp, sc, y):
    return note_block(msp, NOTES_X, y, sc, "NAPOMENA — ORIJENTACIJA:", [
        "Vrata kontejnera i kapija ograde su na SJEVERU, malo prema sjeverozapadu",
        "(fotografije 08.09.2026, Naručilac 11.09.2026). Ovjereni crtež lokacije iz 2017",
        "(GP-BS-10472-291, 01_Situacija 1_200) zakrenut je ≈180° u odnosu na teren;",
        "ovdje je okrenut prema terenu i nacrtan pravougaono na sjever.",
        "Mali preostali zakret NIJE izmjeren — potvrđuje se obilaskom lokacije.",
    ])


# --------------------------------------------------------------------------
# H-01  Postojeće stanje                                               1:100
# --------------------------------------------------------------------------
def sheet_h01():
    SC = 100
    doc, msp = _sheet(SC, "Situacija — POSTOJEĆE STANJE", "H-01", "1:100")
    k = site_plan(msp, SC, future=False)
    plan_dims(msp, SC)
    L = k["L"]
    tw, fe = GEO["tower"], GEO["fence"]
    (cx, cy), (cw, ch) = GEO["container"]["origin"], GEO["container"]["external"]
    ly = GEO["parcel"]["lease"]["origin"][1]
    S = GEO["slab"]["size"][0]
    fs = tw["footings"]["size"][0]
    lf = tw["leg_footprint"][0]
    (lcx, lcy) = tw["legs_centres"][0]

    # west
    lead(msp, P(400, S - fs), f"temelji stuba {dec(fs)} × {dec(fs)} m",
         (WX, P(0, 6300)[1]), SC)
    lead(msp, P(cx + 350, cy + 2300), "kontejner K2 — PRAZAN",
         (WX, P(0, 4300)[1]), SC)
    lead(msp, P(fe["origin"][0], 2600),
         f"ograda h = {dec(fe['height'])} m od ploče",
         (WX, P(0, 2900)[1]), SC)
    lead(msp, P(-EARTH_RINGS[1], 1500), "uzemljivač — 2 prstena na 0,8 m",
         (WX, P(0, 1400)[1]), SC)
    lead(msp, P(lcx - lf / 2, lcy), f"noge stuba h = {tw['height'] // 1000} m, {lf} × {lf} mm",
         (WX, P(0, -300)[1]), SC)
    # east
    gx0 = fe["gate"]["hinge"][0]
    gr = fe["gate"]["leaf"]
    lead(msp, P(gx0 + gr * 0.707, fe["gate"]["hinge"][1] + gr * 0.707),
         f"kapija {dec(gr)} m (otvara se van)", (EX, P(0, 7900)[1]), SC)
    (hxr, hyr), op = L["hinge"], L["door_op"]
    dw, dh = GEO["container"]["door"]["size_mm"]
    lead(msp, P(cx + hxr - op * 0.707, cy + hyr + op * 0.707),
         f"vrata {dw} × {dh} mm (SJEVER)", (EX, P(0, 6800)[1]), SC)
    lead(msp, P(tw["legs_centres"][1][0], 3200),
         f"platforma P I +{dec(tw['platforms_m'][0] * 1000, 1)} m iznad krova",
         (EX, P(0, 5700)[1]), SC)
    sx_, sy_, sw_, sh_ = L["stulz"]
    lead(msp, P(cx + sx_ + sw_, cy + sy_ + sh_ / 2), "klima-uređaj Stulz WDE80 — DEMONTIRA SE",
         (EX, P(0, 2400)[1]), SC)
    lead(msp, P(S - 300, 300), f"AB ploča {dec(S)} × {dec(S)} m", (EX, P(0, 400)[1]), SC)

    _txt(msp, "J U G", *P(S / 2, ly - 1000), 3.2 * SC, layer="Orijentacija", color=1,
         align=TA.CENTER)
    north_arrow(msp, 39000, 25200, 2000)
    scale_bar(msp, 2600, 3000, SC, total_m=10, step_m=1)
    legend(msp, 2600, 7800, SC, [
        (8,   f"postojeća ograda {dec(fe['size'][0])} × {dec(fe['size'][1])} m, "
              f"h = {dec(fe['height'])} m od ploče ({dec(FENCE_ABOVE_GROUND)} m od terena)"
              f" — kapija {dec(gr)} m na SJEVERU"),
        (254, f"postojeća AB ploča {dec(S)} × {dec(S)} m"),
        (6,   f"postojeći kontejner K2 {cw} × {ch} mm — vrata na SJEVERU"),
        (5,   f"noge rešetkastog stuba h = {tw['height'] // 1000} m, "
              f"baza {dec(tw['base'][0])} × {dec(tw['base'][1])} m"),
        (1,   "klima-uređaj Stulz WDE80 (JUŽNI zid, u sredini) — demontira se"),
        (2,   "postojeći uzemljivač FeZn 25×4 mm (isprekidano — u tlu)"),
    ])

    y = _orientation_note(msp, SC, 23000)
    note_block(msp, NOTES_X, y - 700, SC, "NAPOMENE:", [
        "1  Geometrija iz ovjerenog projekta lokacije GP-BS-10472-291 (2017): 01_Situacija 1_200,",
        "    04_Ograda, 01 Osnova, 04 Fasade, 01_Dispozicija S32 m, 3.6.9 Plan uzemljivača objekta.",
        f"2  Zakup {dec(12000)} × {dec(12500)} m = 150 m²: {GEO['parcel']['cadastral']}.",
        "3  Kontejner je PRAZAN; na južnom zidu, u sredini, je samo klima-uređaj Stulz WDE80",
        "    (≈700 × 500 × 2200 mm, procjena s fotografija; Naručilac 11.09.2026).",
        "    Mjere uređaja i otvora u zidu uzimaju se na obilasku lokacije.",
        f"4  Rešetkasti stub h = {tw['height'] // 1000} m; platforma P I na +3,0 m je iznad krova",
        "    kontejnera (+2,63 / +2,89 m) — izduv agregata ne može završiti iznad krova.",
        "5  Uzemljivač FeZn 25×4 mm: prsten u temeljima stopa stuba i dva prstena na dubini",
        "    0,8 m oko ploče (kvadrati 7,50 i 10,00 m prema 3.6.9).",
        "6  Kapija se otvara prema van: krilo 1,30 m udarilo bi u kontejner (1,25 m od ograde).",
        f"7  Teren uz ploču je na {minus(TERRAIN)} m (04_Ograda): ograda je {dec(fe['height'])} m "
        f"iznad ploče, {dec(FENCE_ABOVE_GROUND)} m iznad terena.",
    ])
    return doc


# --------------------------------------------------------------------------
# H-02  Buduće stanje                                                  1:100
# --------------------------------------------------------------------------
def sheet_h02():
    SC = 100
    doc, msp = _sheet(SC, "Situacija — BUDUĆE STANJE", "H-02", "1:100")
    k = site_plan(msp, SC, future=True)
    plan_dims(msp, SC, container_dims=False)
    L, X0, Y0 = k["L"], k["X0"], k["Y0"]
    A = array_layout()
    fw, proj, sl = A["fw"], A["proj"], A["sl"]
    fnd = D["foundation"]
    swt = fnd["strip_w_top"]
    (lx, ly), (lw, lh) = GEO["parcel"]["lease"]["origin"], GEO["parcel"]["lease"]["size"]
    ftop = GEO["fence"]["origin"][1] + GEO["fence"]["size"][1]
    cy = GEO["container"]["origin"][1]

    for i, ax in enumerate(A["stands"], 1):
        x, y = P(ax, A["fy0"])
        rect(msp, x, y, fw, proj, "Panel", color=110, lw=70)
        hatch_rect(msp, x, y, fw, proj, "Panel", "ANSI37", SC * 1.2, 110)
        msp.add_line((x, y + proj / 2), (x + fw, y + proj / 2),
                     dxfattribs={"layer": "Panel", "color": 8})
        msp.add_line((x + fw / 2, y), (x + fw / 2, y + proj),
                     dxfattribs={"layer": "Panel", "color": 8})
        _txt(msp, f"PV-{i}", x + fw / 2, P(0, ly)[1] - 450, 2.5 * SC, color=7,
             align=TA.CENTER)
    for sxa in A["strips"]:
        rect(msp, *P(sxa - swt / 2, A["sy0"]), swt, sl, "Temelj", color=32, lw=35)

    # string cables along the stands, then ONE trench from PV-2 to the container
    xm, yb = A["xmid"], A["fy0"] + proj / 2
    msp.add_lwpolyline([P(A["stands"][0] + fw / 2, yb), P(A["stands"][-1] + fw / 2, yb)],
                       dxfattribs={"layer": "Kabal", "color": 2, "lineweight": 35})
    # a straight run north would pass under the deflector hood: north to the slab,
    # east along it south of the hood, then into the container's east passage
    xin = GEO["container"]["origin"][0] + L["silencer"][0] + 150
    e = msp.add_lwpolyline([P(xm, yb), P(xm, 300), P(xin, 300), P(xin, cy)],
                           dxfattribs={"layer": "Kabal", "color": 2, "lineweight": 50})
    ltype(e, "DASHED", SC)

    # section A-A along PV-2's west strip, looking WEST
    xs = A["section_x"]
    for y_from, y_to in ((ly - 150, ly - 750), (ftop + 1400, ftop + 2150)):
        e = msp.add_lwpolyline([P(xs, y_from), P(xs, y_to)],
                               dxfattribs={"layer": "Osovina", "color": 1, "lineweight": 70})
        ltype(e, "CENTER", SC, 1.5)
        arrow(msp, [P(xs, y_to), P(xs - 700, y_to)], color=1, size=220,
              layer="Osovina", lw=50)
        _txt(msp, "A", *P(xs - 400, y_to + 150), 3.0 * SC, layer="Orijentacija",
             color=1, align=TA.CENTER)

    # Huawei ICC360-HA1-C1 outdoors on the slab (NW), front EAST, fed from GRO F1
    # through the north wall; its door protrudes 330 mm on the east face
    ic = GEO["icc360"]
    (ix, iy), (iw, ih) = ic["footprint"]["origin"], ic["footprint"]["size"]
    body = ic["size_mm"]["D"]
    solid_rect(msp, *P(ix, iy), body, ih, "Novi1", 30)
    rect(msp, *P(ix, iy), body, ih, "Novi1", color=30, lw=50)
    rect(msp, *P(ix + body, iy), iw - body, ih, "Novi1", color=30, lw=35)
    # tank vent: out through the north wall east of the door, stand-pipe by the fence
    tv = GEO["tank_vent"]
    e = msp.add_lwpolyline([P(*tv["wall_exit"]), P(*tv["termination"])],
                           dxfattribs={"layer": "Ventilacija", "color": 1, "lineweight": 35})
    ltype(e, "DASHED", SC, 1.5)
    msp.add_circle(P(*tv["termination"]), 90, dxfattribs={"layer": "Ventilacija", "color": 1})

    # array dimensions: chain lease edge | stands | gaps | lease edge, then total
    yd = P(0, ly)[1] - 1300
    pts = [(lx, ly)] + [(v, A["fy0"]) for ax in A["stands"] for v in (ax, ax + fw)] \
        + [(lx + lw, ly)]
    for a, b in zip(pts, pts[1:]):
        dim_free(msp, P(*a), P(*b), (0, yd), SC, text=mmc(b[0] - a[0]))
    dim_free(msp, P(A["x0"], A["fy0"]), P(A["x0"] + A["total"], A["fy0"]),
             (0, yd - 800), SC)
    xe = A["stands"][-1] + fw
    dim_free(msp, P(xe, A["fy0"]), P(xe, A["fy0"] + proj), (P(xe + 700, 0)[0], 0),
             SC, angle=90)
    xw = A["strips"][0] - swt / 2
    dim_free(msp, P(xw, A["sy0"]), P(xw, A["sy0"] + sl), (P(A["x0"] - 450, 0)[0], 0),
             SC, angle=90)

    # west callouts
    lead(msp, P(A["strips"][0], A["sy0"] + 500),
         "temeljne trake (6 kom)",
         (WX, P(0, -2600)[1]), SC)
    lead(msp, P(xm, 150), "DC trasa PEHD Ø50 (2 stringa)",
         (WX, P(0, -900)[1]), SC)
    lead(msp, (X0 + L["t"] / 2, Y0 + sum(L["intake"]) / 2), "usis 500 × 700 (novo)",
         (WX, P(0, 1700)[1]), SC)
    lead(msp, (X0 + L["t"] / 2, Y0 + FAN_Y), "ventilator Ø315 — izvlačni",
         (WX, P(0, 3000)[1]), SC)
    gx, gy, gw, gd = L["gro"]
    lead(msp, (X0 + gx + gw / 2, Y0 + gy + gd / 2), f"GRO ≤{GRO_W} × {GRO_D} × {GRO_H}",
         (WX, P(0, 4600)[1]), SC)
    # east callouts
    cw = L["cw"]
    hx, hy, hw, hd = L["hood"]
    lead(msp, (X0 + hx + hw, Y0 + hy + hd / 2),
         "izlaz zraka — otvori Stulz, hauba naviše", (EX, P(0, 1300)[1]), SC)
    lead(msp, (X0 + cw + EXH_OUT, Y0 + L["exh_y"]),
         f"izduv NO 50, ≈+{dec(EXH_Z)}, ≥{dec(EXH_OUT)} m od zida", (EX, P(0, 2600)[1]), SC)
    sx, sy, sl_, sw_ = L["skid"]
    lead(msp, (X0 + sx + sl_, Y0 + sy + sw_ - 200),
         "DEA, spremnik, GRO — v. H-04", (EX, P(0, 3900)[1]), SC)
    lead(msp, P(A["strips"][-1], A["sy0"] + sl),
         f"trake {mmc(A['margin'])} mm od ploče / zakupa",
         (EX, P(0, -1100)[1]), SC)
    lead(msp, P(A["strips"][-1] + swt / 2, -EARTH_RINGS[1]),
         "prsteni uzemljivača × trake (LOT 1)", (EX, P(0, -2500)[1]), SC)

    lead(msp, P(ix + 150, iy + ih - 80), "ICC360-HA1-C1 — principijelno",
         (WX, P(0, 5900)[1]), SC)
    lead(msp, P(*tv["termination"]), "odušak spremnika — principijelno",
         (WX, P(0, 400)[1]), SC)

    north_arrow(msp, 39000, 25200, 2000)
    scale_bar(msp, 2600, 3000, SC, total_m=10, step_m=1)
    legend(msp, 2600, 7800, SC, [
        (110, f"FN nosači PV-1..PV-3 — po 4 × 585 Wp (2 × 2 portret), "
              f"{D['array']['tilt_deg']}°, JUG — 2 stringa × 6"),
        (32,  f"AB temeljne trake {swt}/{fnd['strip_w_base']} × {sl} mm, "
              f"d = {fnd['strip_d']} mm, razmak {A['sp']} mm"),
        (2,   "DC trasa u PEHD Ø50 (isprekidano) — od polja do kontejnera"),
        (30,  "DEA 18 kVA (skid), spremnik 500 l u koritu, novi GRO"),
        (4,   "usis 500 × 700 (ZAPAD), izlaz zraka kroz otvore Stulz (JUG) i haubu naviše, ventilator Ø315"),
        (1,   "izduv NO 50 (ISTOK, ≈+2,30 m); odušak spremnika (isprekidano); presjek A–A"),
        (30,  "Huawei ICC360-HA1-C1 vani na ploči (SJEVER), vrata na ISTOK — principijelno"),
    ])

    y = _orientation_note(msp, SC, 23000)
    note_block(msp, NOTES_X, y - 700, SC, "NAPOMENE:", [
        "1  Nosači su okrenuti prema JUGU (azimut 180°), nagib 45°; donja ivica panela +0,50 m,",
        f"    gornja +3,74 m — {dec(PV_OVER_FENCE)} m iznad vrha ograde (ograda "
        f"{dec(GEO['fence']['height'])} m iznad ploče = {dec(FENCE_ABOVE_GROUND)} m iznad terena).",
        f"2  Polje 3 × {mmc(fw)} + 2 × {ARRAY_GAP} = {mmc(A['total'])} mm, centrirano "
        "istok–zapad; sve je unutar granice zakupa.",
        "3  Ako granica zakupa odstupa od pravca istok–zapad, nosači se postavljaju kaskadno",
        "    unutar južnog pojasa ili upravno na granicu zakupa, uz odstupanje azimuta ≤15°.",
        f"4  Temeljne trake {swt}/{fnd['strip_w_base']} × {sl} mm, d = {fnd['strip_d']} mm, "
        f"na podložnom betonu {fnd['blinding_thk']} mm,",
        f"    pravac SJEVER–JUG; {mmc(A['margin'])} mm od ploče i od granice zakupa.",
        f"5  Postojeći prsteni uzemljivača (0,8 m; {dec(EARTH_RINGS[0])} i {dec(EARTH_RINGS[1])} m "
        "od ploče): ukrštanja sa temeljnim trakama —",
        "    lociranje, otkopavanje i premještanje ili premoštavanje prstena (LOT 1).",
        "6  Vjetar qp ≥ 1,20 kN/m² — nosač CUSTOM izrade; ovjereni statički proračun",
        "    dostavlja Ponuđač.",
        "7  Raspored u kontejneru prema H-04; izlaz zraka kroz otvore Stulz (JUG) i haubu naviše.",
        "8  Ormar ICC360-HA1-C1 — principijelno, potvrđuje se na licu mjesta; napaja se iz GRO",
        "    (izvod F1) kroz sjeverni zid. Odušak spremnika — principijelno, konačno prema",
        "    elaboratu zaštite od požara (≥3 m od izduva i usisa, ≥1 m od ormara).",
    ])
    return doc


# --------------------------------------------------------------------------
# H-03  Presjek A–A kroz FN polje                                       1:30
# --------------------------------------------------------------------------
def sheet_h03():
    """Equivalent of Sjednica S-03.  Section along PV-2's west strip (plane
    x = A['section_x']), looking WEST: south on the left, north on the right.
    Levels are from the terrain beside the array; the slab top is +0,20
    (terrain -0,20 against the slab, 04_Ograda)."""
    SC = 30
    doc, msp = _sheet(SC, "Presjek A–A kroz FN polje", "H-03", "1:30")
    A = array_layout()
    sup, arr, fnd, mod = D["support"], D["array"], D["foundation"], D["module"]
    proj, b, top = A["proj"], arr["bottom_edge"], arr["top_edge"]
    FH = GEO["fence"]["height"]                     # above the slab
    if FH != arr["fence_height"]:
        raise SystemExit("fence height: design.json and site_geometry.json disagree")
    ZS = -TERRAIN                                   # slab top above the terrain
    ly = GEO["parcel"]["lease"]["origin"][1]
    S = GEO["slab"]["size"][0]
    fe_s = GEO["fence"]["origin"][1]
    fe_n = fe_s + GEO["fence"]["size"][1]
    c = GEO["container"]
    cy, ch = c["origin"][1], c["external"][1]
    t = c["wall_panel_thickness"]
    H_LO, H_HI = c["heights"]["eave_low"], c["heights"]["eave_high"]
    tw = GEO["tower"]
    L = interior()
    sy0, sl = A["sy0"], A["sl"]
    fd, bl = fnd["strip_d"], fnd["blinding_thk"]

    # A3 window at 1:30 is 600..12300 x 300..8610; title block x > 6900 below 1740
    GX, GY = 5775, 3300                             # GY = terrain beside the array

    def X(s):                                       # s = slab-local Y, north to the right
        return GX + s

    # terrain at -0,20 against the slab, both sides; hatch ticks clear of strip/slab
    x_l, x_r = X(ly) - 1500, X(fe_n) + 700
    for xa_, xb_ in ((x_l, X(0)), (X(S), x_r)):
        msp.add_line((xa_, GY), (xb_, GY),
                     dxfattribs={"layer": "Objekat", "color": 8, "lineweight": 50})
    x = x_l + 150
    while x < x_r - 100:
        if not (X(sy0) - 100 <= x <= X(sy0 + sl) + 250 or X(0) - 100 <= x <= X(S) + 250):
            msp.add_line((x, GY), (x - 150, GY - 150),
                         dxfattribs={"layer": "Objekat", "color": 8})
        x += 450
    e = msp.add_line((X(ly), GY - 1300), (X(ly), GY + 4300),
                     dxfattribs={"layer": "Sakriveno", "color": 8})
    ltype(e, "PHANTOM", SC, 1.5)
    _txt(msp, "granica zakupa", X(ly) - 80, GY + 4150, 1.7 * SC, color=8, align=TA.RIGHT)

    # foundation strip, full depth, on blinding (seen along its length)
    rect(msp, X(sy0), GY - fd, sl, fd, "Temelj", color=32, lw=50)
    hatch_rect(msp, X(sy0), GY - fd, sl, fd, "Temelj", "ANSI31", SC * 0.35, 32)
    solid_rect(msp, X(sy0) - 50, GY - fd - bl, sl + 100, bl, "Temelj", 254)
    rect(msp, X(sy0) - 50, GY - fd - bl, sl + 100, bl, "Temelj", color=8, lw=35)

    # the two existing earth rings (E-W tapes) cross the strip at 0,8 m
    dr = GEO["earth_rings"]["depth_mm"]
    for off in EARTH_RINGS:
        solid_rect(msp, X(-off) - 40, GY - dr - 40, 80, 80, "Uzemljenje", 2)

    # stand: two modules along the 45 deg slope, rail, posts and brace
    fy0 = A["fy0"]
    x0, y0 = X(fy0), GY + b
    x1, y1 = X(fy0 + proj), GY + top
    ang = math.atan2(y1 - y0, x1 - x0)
    ux, uy, nx, ny = math.cos(ang), math.sin(ang), -math.sin(ang), math.cos(ang)
    ML, MT = mod["L"], mod["T"]
    gap_m = sup["field_slope"] - 2 * ML
    for k0 in (0.0, ML + gap_m):
        p0 = (x0 + ux * k0, y0 + uy * k0)
        p1 = (x0 + ux * (k0 + ML), y0 + uy * (k0 + ML))
        pts = [p0, p1, (p1[0] + nx * MT, p1[1] + ny * MT), (p0[0] + nx * MT, p0[1] + ny * MT)]
        h_ = msp.add_hatch(color=5, dxfattribs={"layer": "Panel"})
        h_.paths.add_polyline_path(pts, is_closed=True)
        msp.add_lwpolyline(pts, close=True,
                           dxfattribs={"layer": "Panel", "color": 5, "lineweight": 50})
    msp.add_line((x0 - nx * 80, y0 - ny * 80), (x1 - nx * 80, y1 - ny * 80),
                 dxfattribs={"layer": "Panel", "color": 8})
    for a_, b_ in (((x0, y0), (x0, GY)), ((x1, y1), (x1, GY)), ((x0, y0), (x1, GY))):
        msp.add_line(a_, b_, dxfattribs={"layer": "Konstrukcija", "color": 5,
                                         "lineweight": 50})
    for xp in (x0, x1):                             # base plates on the strip
        solid_rect(msp, xp - 110, GY, 220, 20, "Konstrukcija", 5)
    msp.add_line((x0, y0), (x0 + 1000, y0), dxfattribs={"layer": "Kote", "color": 8})
    msp.add_arc((x0, y0), 750, 0, math.degrees(ang), dxfattribs={"layer": "Kote", "color": 8})
    _txt(msp, f"{arr['tilt_deg']}°", x0 + 820, y0 + 160, 2.4 * SC, layer="Kote", color=7)

    # fences, cut by the plane: posts 50 outside the slab, on the terrain,
    # 1,80 m above the slab = 2,00 m above the ground
    FT = ZS + FH                                    # fence top above the terrain
    for s in (fe_s, fe_n):
        fx = X(s)
        solid_rect(msp, fx - 25, GY, 50, FT, "Ograda", 8)
        rect(msp, fx - 25, GY, 50, FT, "Ograda", color=8, lw=70)
        for ry in (GY + ZS + 100, GY + FT - 30):
            rect(msp, fx - 15, ry, 30, 30, "Ograda", color=8, lw=50)
    _txt(msp, f"ograda {dec(FH)} m od ploče", X(fe_s) + 110, GY + 150, 1.6 * SC,
         color=7, rotation=90)

    # slab, top at +0,20
    rect(msp, X(0), GY + ZS - SLAB_T, S, SLAB_T, "Objekat", color=254, lw=35)
    hatch_rect(msp, X(0), GY + ZS - SLAB_T, S, SLAB_T, "Objekat", "ANSI31", SC * 0.5, 8)
    _txt(msp, f"postojeća AB ploča {dec(S)} × {dec(S)} m, gornja površina +{dec(ZS)}",
         X(S / 2), GY + ZS - SLAB_T - 300, 1.7 * SC, color=8, align=TA.CENTER)

    # tower in the background (west legs), schematic; platform P I over the roof
    lf = tw["leg_footprint"][0]
    TOP = 4400
    zp = tw["platforms_m"][0] * 1000
    G0 = GY + ZS                                    # slab top
    legs_s = sorted({p[1] for p in tw["legs_centres"]})
    for s in legs_s:
        rect(msp, X(s) - lf / 2, G0, lf, TOP, "Konstrukcija", color=5, lw=35)
        msp.add_lwpolyline([(X(s) - lf / 2 - 80, G0 + TOP), (X(s) - 60, G0 + TOP + 90),
                            (X(s) + 60, G0 + TOP - 90), (X(s) + lf / 2 + 80, G0 + TOP)],
                           dxfattribs={"layer": "Konstrukcija", "color": 5})
    xa, xb = X(legs_s[0]) + lf / 2, X(legs_s[1]) - lf / 2
    solid_rect(msp, X(legs_s[0]) - lf / 2, G0 + zp, xb - xa + 2 * lf, 80, "Konstrukcija", 5)
    msp.add_line((xa, G0 + zp + 80), (xb, G0 + TOP), dxfattribs={"layer": "Konstrukcija", "color": 5})
    msp.add_line((xb, G0 + zp + 80), (xa, G0 + TOP), dxfattribs={"layer": "Konstrukcija", "color": 5})
    _txt(msp, f"rešetkasti stub h = {tw['height'] // 1000} m — pozadina, šematski",
         (xa + xb) / 2, G0 + TOP + 200, 1.8 * SC, color=8, align=TA.CENTER)
    lead(msp, (X(legs_s[1]) + lf / 2, G0 + zp + 40),
         f"platforma +{dec(zp, 1)}", (X(legs_s[1]) + 450, G0 + zp + 500), SC)

    # container, cut 350 mm inside its west wall: S and N walls cut, the west
    # wall seen beyond with the new intake and room fan; the GRO is cut
    xc0, xc1 = X(cy), X(cy + ch)
    msp.add_lwpolyline([(xc0, G0), (xc1, G0), (xc1, G0 + H_LO), (xc0, G0 + H_LO)],
                       close=True, dxfattribs={"layer": "Objekat", "color": 6, "lineweight": 50})
    for xw in (xc0, xc1 - t):
        solid_rect(msp, xw, G0, t, H_LO, "Objekat", 8)
    msp.add_lwpolyline([(xc0 - 120, G0 + H_LO), (xc1 + 120, G0 + H_LO),
                        (xc1 + 120, G0 + H_LO + 100), (xc0 - 120, G0 + H_LO + 100)],
                       close=True, dxfattribs={"layer": "Objekat", "color": 6, "lineweight": 35})
    e = msp.add_line((xc0 - 120, G0 + H_HI), (xc1 + 120, G0 + H_HI),
                     dxfattribs={"layer": "Objekat", "color": 6})
    ltype(e, "DASHED", SC, 1.5)
    _txt(msp, f"+{dec(H_LO)} / +{dec(H_HI)} od ploče (krov 10 %)", xc0 + 150,
         G0 + H_HI + 60, 1.5 * SC, layer="Kota_tekst", color=8)
    i0, i1 = L["intake"]
    iz0, iz1 = L["intake_z"]
    rect(msp, xc0 + i0, G0 + iz0, i1 - i0, iz1 - iz0, "Ventilacija", color=4, lw=35)
    f0, f1 = L["fan"]
    rect(msp, xc0 + f0, G0 + FAN_Z, f1 - f0, FAN_D, "Ventilacija", color=4, lw=35)
    gx, gy, gw, gd = L["gro"]
    solid_rect(msp, xc0 + gy, G0 + GRO_Z, gd, GRO_H, "Novi1", 30)
    _txt(msp, "usis", xc0 + (i0 + i1) / 2, G0 + iz1 + 60, 1.4 * SC, color=8, align=TA.CENTER)
    _txt(msp, "ventilator (izvlačni)", xc0 + (f0 + f1) / 2, G0 + FAN_Z + FAN_D + 60,
         1.4 * SC, color=8, align=TA.CENTER)
    _txt(msp, "GRO", xc0 + gy - 60, G0 + GRO_Z + GRO_H / 2, 1.4 * SC, color=8, align=TA.RIGHT)
    # the tank in the SW corner is cut by the plane as well (tray and tank)
    kx, ky, kw, kh = L["kada"]
    tx, ty, tw_, th = L["tank"]
    tk = D["tank"]
    rect(msp, xc0 + ky, G0, kh, tk["kada"]["rim_mm"], "Agregat", color=1, lw=35)
    rect(msp, xc0 + ty, G0 + 40, th, tk["H"], "Agregat", color=30, lw=50)
    _txt(msp, "spremnik 500 l", xc0 + ty + th / 2, G0 + tk["H"] + 110, 1.4 * SC, color=8,
         align=TA.CENTER)
    # tank vent: out through the south wall to a stand-pipe between container and fence
    tv = GEO["tank_vent"]
    vz, vy_t = tv["termination_z_mm"], tv["termination"][1]
    msp.add_lwpolyline([(xc0 + ty + 150, G0 + tk["H"] + 40), (xc0 + ty + 150, G0 + tk["H"] + 250),
                        (X(vy_t), G0 + tk["H"] + 250), (X(vy_t), G0 + vz)],
                       dxfattribs={"layer": "Ventilacija", "color": 1, "lineweight": 35})
    _txt(msp, "odušak", X(vy_t) + 70, G0 + vz - 450, 1.4 * SC, color=8, rotation=90)
    # the ICC360 north of the container is cut by the plane as well
    ic = GEO["icc360"]
    (ix, iy), (iw, ih) = ic["footprint"]["origin"], ic["footprint"]["size"]
    solid_rect(msp, X(iy), G0, ih, ic["size_mm"]["H"], "Novi1", 30)
    rect(msp, X(iy), G0, ih, ic["size_mm"]["H"], "Novi1", color=30, lw=50)
    _txt(msp, "ICC360-HA1-C1 (principijelno)", X(iy) + ih / 2 + 25, G0 + 150, 1.5 * SC,
         color=7, rotation=90)
    _txt(msp, "postojeći kontejner K2", (xc0 + xc1) / 2, G0 + 1350, 2.0 * SC,
         color=7, align=TA.CENTER)
    _txt(msp, f"presjek po dužini {ch} mm", (xc0 + xc1) / 2, G0 + 1150, 1.6 * SC,
         color=8, align=TA.CENTER)

    # levels from the terrain, labelled at the left end
    for lvl, lab in ((b, f"donja ivica panela  +{dec(b)}"),
                     (FT, f"vrh ograde  +{dec(FT)}  ({dec(FH)} iznad ploče)"),
                     (top, f"gornja ivica panela  +{dec(top)}")):
        msp.add_line((650, GY + lvl), (X(fe_s) + 150, GY + lvl),
                     dxfattribs={"layer": "Sakriveno", "color": 8})
        _txt(msp, lab, 700, GY + lvl + 40, 1.9 * SC, layer="Kota_tekst", color=7)
    _txt(msp, "teren  ±0,00", 700, GY + 40, 1.9 * SC, layer="Kota_tekst", color=7)

    # dimensions
    dim_free(msp, (1750, GY), (1750, GY + top), (1750, 0), SC, angle=90)
    dim_free(msp, (X(fe_s), GY + FT), (x1, GY + top), (X(fe_s) + 350, 0), SC, angle=90)
    yb = GY - fd - bl
    dim_free(msp, (x0, yb), (x1, yb), (0, yb - 450), SC)
    yc = yb - 900
    dim_free(msp, (X(ly), yb), (X(sy0), yb), (0, yc), SC, text=mmc(A["margin"]),
             loc=(X(ly) - 320, yc + 60))
    dim_free(msp, (X(sy0), yb), (X(sy0 + sl), yb), (0, yc), SC)
    dim_free(msp, (X(sy0 + sl), yb), (X(0), yb), (0, yc), SC, text=mmc(A["margin"]),
             loc=(X(0) + 330, yc + 60))

    # callouts
    km = ML + gap_m + ML / 2
    lead(msp, (x0 + ux * km + nx * MT, y0 + uy * km + ny * MT),
         f"FN moduli {mod['model'].split(' /')[0]} {ML} × {mod['W']}, portret, 2 reda × 2",
         (X(fy0) + 1500, GY + top + 700), SC)
    lead(msp, (x1, GY + 1400), "nosač — CUSTOM izrada", (x1 - 500, GY + 1900), SC)
    lead(msp, (X(sy0 + sl) - 400, GY - 600),
         f"temeljna traka {fnd['strip_w_top']}/{fnd['strip_w_base']} × {sl}, "
         f"d = {fd} — C30/37", (X(sy0 + sl) + 650, GY - 1100), SC)
    lead(msp, (X(-EARTH_RINGS[0]), GY - dr), "2 postojeća prstena FeZn 25×4 na −0,80 — ukrštanje",
         (X(sy0 + sl) + 650, GY - 1450), SC)
    lead(msp, (X(sy0) + 300, GY - fd - bl / 2), f"podložni beton C12/15, d = {bl}",
         (X(sy0) - 350, GY - 1250), SC)

    _txt(msp, "PRESJEK A–A  (osa zapadne trake nosača PV-2 — pogled prema ZAPADU)",
         700, 8300, 2.6 * SC, color=7)
    _txt(msp, "←  J U G", 700, GY - 350, 2.4 * SC, layer="Orijentacija", color=1)
    _txt(msp, "S J E V E R  →", X(fe_n) - 700, GY - 650, 2.4 * SC,
         layer="Orijentacija", color=1)

    note_block(msp, 700, 1250, SC, "OBJAŠNJENJA:", [
        f"1  Polje: 2 reda × 2 modula 585 Wp ({ML} × {mod['W']} mm), portret; nagib "
        f"{arr['tilt_deg']}°, horizontalna projekcija {proj} mm.",
        f"2  Dvije temeljne trake po nosaču {fnd['strip_w_top']}/{fnd['strip_w_base']} × {sl} mm, "
        f"dubina {fd} mm, razmak {A['sp']} mm (druga iza ravni presjeka);",
        f"    beton C30/37 (XC4+XF3), armatura B500B, na podložnom betonu C12/15 d = {bl} mm.",
        f"3  Kote od terena uz FN polje; teren je {minus(TERRAIN)} m ispod ploče (04_Ograda). "
        f"Donja ivica panela +{dec(b)}, gornja +{dec(top)};",
        f"    vrh ograde +{dec(FT)} ({dec(FH)} m iznad ploče) — gornja ivica je "
        f"{dec(PV_OVER_FENCE)} m iznad ograde.",
        "4  Postojeći prsteni uzemljivača na 0,8 m presijecaju traku: lociranje, otkopavanje i",
        "    premještanje ili premoštavanje prstena (LOT 1).",
        f"5  Trake su {mmc(A['margin'])} mm od granice zakupa (JUG) i od ploče (SJEVER); "
        "položaj presjeka na H-02.",
        "6  Stub, platforma P I (+3,0 m od ploče), kontejner i ormar ICC360 prikazani su šematski.",
    ])
    return doc


# --------------------------------------------------------------------------
# H-04  Agregat u kontejneru — osnova i presjek 1–1                     1:25
# --------------------------------------------------------------------------
def sheet_h04():
    """Equivalent of Sjednica M-01 for the Hamzići container: 2300 E-W x 3005
    N-S, door NORTH.  The Stulz is centred on the SOUTH wall (Investor,
    11.09.2026): the genset stands on the centre line, long axis N-S, radiator
    SOUTH, discharging through the Stulz cut-outs into a hood that turns the warm
    air upwards; intake WEST at the alternator end, exhaust EAST under the +3,0 m
    platform, tank in the SW corner."""
    SC = 25
    doc, msp = _sheet(SC, "Agregat u kontejneru — osnova i presjek 1–1", "H-04", "1:25")
    L = interior()
    chk = site_checks()
    g, tk = D["genset"], D["tank"]
    kada = tk["kada"]
    cw, ch, t = L["cw"], L["ch"], L["t"]
    c = GEO["container"]
    cx0, cy0 = c["origin"]
    H_LO, H_HI = c["heights"]["eave_low"], c["heights"]["eave_high"]
    sx0, sy0, sw, sl = L["skid"]                    # width E-W, length N-S
    sx1, sy1 = sx0 + sw, sy0 + sl
    fx, fy, fwid, fdep = L["frame"]
    kx, ky, kw, kh = L["kada"]
    tx, ty, tw_, th = L["tank"]
    gx, gy, gw, gd = L["gro"]
    bx, by, bw, bd = L["dcbox"]
    hx, hy, hw, hd = L["hood"]
    d0, d1 = L["door"]
    (hgx, hgy), op = L["hinge"], L["door_op"]
    ax = L["axis"]
    i0, i1 = L["intake"]
    iyc = (i0 + i1) / 2
    iz0, iz1 = L["intake_z"]
    f0, f1 = L["fan"]
    dz0, dz1 = L["dis_z"]
    s0, s1 = L["silencer"]
    ey = L["exh_y"]
    dh_ = c["door"]["size_mm"][1]
    tv = GEO["tank_vent"]
    vx = tv["wall_exit"][0] - cx0
    vyt = tv["termination"][1] - cy0

    # A3 window at 1:25 is 500..10250 x 250..7175; title block x > 5750 below 1450
    ox, oy = 2100, 2450
    rect(msp, ox, oy, cw, ch, "Objekat", color=6, lw=50)
    rect(msp, ox + t, oy + t, cw - 2 * t, ch - 2 * t, "Objekat", color=6)
    for x, y, w, h in ((0, 0, cw, t), (0, t, t, ch - 2 * t), (cw - t, t, t, ch - 2 * t),
                       (0, ch - t, d0, t), (d1, ch - t, cw - d1, t)):
        solid_rect(msp, ox + x, oy + y, w, h, "Objekat", 8)
    msp.add_line((ox + hgx, oy + hgy), (ox + hgx, oy + hgy + op),
                 dxfattribs={"layer": "Objekat", "color": 8})
    msp.add_arc(center=(ox + hgx, oy + hgy), radius=op, start_angle=90, end_angle=180,
                dxfattribs={"layer": "Objekat", "color": 8})
    _txt(msp, "vrata", ox + d0 + 380, oy + ch + 330, 1.6 * SC, color=7)
    _txt(msp, f"{c['door']['size_mm'][0]} × {dh_}", ox + d0 + 380, oy + ch + 170,
         1.4 * SC, color=8)

    plan_equipment(msp, ox, oy, L, SC, detail=True)

    # DC razvod -48 V, the two luminaires, the door switch, and the cable entry
    # from the ICC360 (F1 AC and DC -48 V) through the north wall above the GRO
    solid_rect(msp, ox + bx, oy + by, bw, bd, "Novi1", 30)
    rect(msp, ox + bx, oy + by, bw, bd, "Novi1", color=30, lw=50)
    for (lx_, ly_), lab in ((L["lights"]["AC"], "LED 230 V AC (F2)"),
                            (L["lights"]["DC"], "LED 48 V DC (D5)")):
        X_, Y_ = ox + lx_, oy + ly_
        msp.add_circle((X_, Y_), 110, dxfattribs={"layer": "Sema", "color": 2})
        for s in (-1, 1):
            msp.add_line((X_ - 78, Y_ - 78 * s), (X_ + 78, Y_ + 78 * s),
                         dxfattribs={"layer": "Sema", "color": 2})
        _txt(msp, lab, X_ - 160, Y_ - 20, 1.3 * SC, color=8, align=TA.RIGHT)
    swx, swy = L["switch"]
    msp.add_circle((ox + swx, oy + swy - 50), 35, dxfattribs={"layer": "Sema", "color": 2})
    msp.add_line((ox + swx + 25, oy + swy - 75), (ox + swx + 90, oy + swy - 160),
                 dxfattribs={"layer": "Sema", "color": 2})
    _txt(msp, "prekidač (D5)", ox + swx - 20, oy + swy - 300, 1.2 * SC, color=8)
    xe_ = L["cable_x"]
    iy_ = GEO["icc360"]["footprint"]["origin"][1] - cy0
    e = msp.add_lwpolyline([(ox + xe_, oy + iy_), (ox + xe_, oy + ch - t - 40),
                            (ox + bx, oy + ch - t - 40)],
                           dxfattribs={"layer": "Kabal", "color": 2, "lineweight": 35})
    ltype(e, "DASHED", SC, 1)
    _txt(msp, "F1 (AC) + DC −48 V kroz zid", ox + xe_ - 60, oy + ch + 50, 1.2 * SC,
         color=8, align=TA.RIGHT)

    # labels in the plan
    _txt(msp, "DEA 18 kVA / 14,4 kW", ox + ax - 60, oy + sy0 + sl * 0.55, 1.8 * SC,
         color=7, align=TA.MIDDLE_CENTER, rotation=90)
    _txt(msp, f"skid {sl} × {sw}", ox + ax + 150, oy + sy0 + sl * 0.55, 1.4 * SC,
         color=8, align=TA.MIDDLE_CENTER, rotation=90)
    _txt(msp, "HLADNJAK", ox + ax, oy + sy0 + 90, 1.3 * SC, color=8,
         align=TA.MIDDLE_CENTER)
    _txt(msp, "spremnik 500 l", ox + tx + tw_ / 2 - 40, oy + ty + 120, 1.6 * SC,
         color=7, rotation=90)
    _txt(msp, "dvoplašni", ox + tx + tw_ / 2 + 160, oy + ty + 120, 1.3 * SC,
         color=8, rotation=90)
    _txt(msp, "GRO", ox + gx + gw / 2, oy + gy + gd / 2, 1.6 * SC, color=7,
         align=TA.MIDDLE_CENTER)
    _txt(msp, "prigušivač", (2 * ox + s0 + s1) / 2, oy + ey + 170, 1.3 * SC, color=8,
         align=TA.CENTER)
    _txt(msp, "servisna strana agregata — ISTOK", ox + sx1 + 390, oy + sy0 + 60,
         1.4 * SC, color=8, rotation=90)

    # outside the north wall: ICC360 (outdoors, principle)
    ic = GEO["icc360"]
    (ix, iy), (iw, ih) = ic["footprint"]["origin"], ic["footprint"]["size"]
    e = rect(msp, ox + ix - cx0, oy + iy - cy0, iw, ih, "Novi1", color=30, lw=35)
    ltype(e, "DASHED", SC, 1.5)
    msp.add_line((ox + ix - cx0 + ic["size_mm"]["D"], oy + iy - cy0),
                 (ox + ix - cx0 + ic["size_mm"]["D"], oy + iy - cy0 + ih),
                 dxfattribs={"layer": "Novi1", "color": 30})
    _txt(msp, "ICC360-HA1-C1 (vani)", ox + ix - cx0 + 60, oy + iy - cy0 + ih - 140,
         1.4 * SC, color=7)
    _txt(msp, "principijelno", ox + ix - cx0 + 60, oy + iy - cy0 + ih - 290, 1.3 * SC,
         color=8)
    _txt(msp, "vrata →", ox + ix - cx0 + ic["size_mm"]["D"] + 20, oy + iy - cy0 + 60,
         1.2 * SC, color=8)
    # tank vent: from the tank out through the south wall to a stand-pipe
    e = msp.add_lwpolyline([(ox + vx, oy + ty + th - 200), (ox + vx, oy + vyt)],
                           dxfattribs={"layer": "Ventilacija", "color": 1, "lineweight": 35})
    ltype(e, "DASHED", SC, 1.5)
    msp.add_circle((ox + vx, oy + vyt), 60, dxfattribs={"layer": "Ventilacija", "color": 1})

    # airflow: in through the WEST wall at the alternator end, along the genset to
    # the radiator, out through the Stulz cut-outs into the hood and UP; the room
    # fan is an EXTRACT fan (arrow out)
    arrow(msp, [(ox - 700, oy + iyc), (ox + 400, oy + iyc)], size=130)
    arrow(msp, [(ox + ax + 200, oy + sy0 - 10), (ox + ax + 200, oy - 180)], size=110)
    arrow(msp, [(ox + 250, oy + FAN_Y), (ox - 550, oy + FAN_Y)], size=110)

    # dimensions: container, door, passages to the skid, plenum, GRO working space
    dim_h(msp, ox, ox + cw, oy, SC, off=-850)
    dim_v(msp, oy, oy + ch, ox, SC, off=-300)
    dim_h(msp, ox + d0, ox + d1, oy + ch - t - 320, SC, off=0)
    dim_h(msp, ox + t, ox + sx0, oy + 1950, SC, off=0)
    dim_h(msp, ox + kx + kw, ox + sx0, oy + ky + 350, SC, off=0)
    dim_h(msp, ox + sx1, ox + cw - t, oy + 1950, SC, off=0)
    dim_v(msp, oy + t, oy + sy0, ox + sx1 + 180, SC, off=0)
    dim_free(msp, (ox + sx0, oy + sy1), (ox + 400, oy + gy), (ox + 1000, 0), SC, angle=90)

    # callouts, west
    WXp = ox - 450
    lead(msp, (ox + kx + 150, oy + ky + kh - 150),
         f"korito {kada['L']} × {kada['W']}, rub {kada['rim_mm']} (JZ ugao)",
         (WXp, oy + 1000), SC, h=1.8)
    lead(msp, (ox + t / 2, oy + iyc), "usis 500 × 700, +0,30 (novo)", (WXp, oy + 1650),
         SC, h=1.8)
    lead(msp, (ox + t / 2, oy + FAN_Y), "ventilator Ø315 — izvlačni", (WXp, oy + 2200),
         SC, h=1.8)
    lead(msp, (ox + gx + 80, oy + gy + gd / 2), f"GRO ≤{GRO_W} × {GRO_D} × {GRO_H}",
         (WXp, oy + 2850), SC, h=1.8)
    lead(msp, (ox + vx, oy + vyt), "odušak spremnika — principijelno", (WXp, oy - 450),
         SC, h=1.8)
    # callouts, east
    EXp = ox + cw + 450
    lead(msp, (ox + bx + bw / 2, oy + by), "DC razvod −48 V (≤25 W)", (EXp, oy + 2750),
         SC, h=1.8)
    lead(msp, (ox + cw + EXH_OUT, oy + ey), f"izduv NO 50 — ≥{dec(EXH_OUT)} m od zida",
         (EXp + 150, oy + 1450), SC, h=1.8)
    lead(msp, (ox + hx + hw, oy + hy + hd / 2), "izlaz: otvori Stulz → hauba naviše",
         (EXp, oy - 350), SC, h=1.8)

    north_arrow(msp, 1000, 5800, 550)
    _txt(msp, "OSNOVA  —  kontejner je PRAZAN; klima-uređaj Stulz se demontira", 600, 6900,
         2.4 * SC, color=7)

    # ---------------------------------------------------------------- section 1-1
    # along the genset axis, looking WEST: south on the left, north on the right;
    # the west wall with the intake, fan, tank and GRO is seen beyond the cut
    sxo, syo = 6650, 2650
    msp.add_line((sxo - hd - 350, syo), (sxo + ch + 450, syo),
                 dxfattribs={"layer": "Objekat", "color": 8, "lineweight": 50})
    msp.add_lwpolyline([(sxo, syo), (sxo + ch, syo), (sxo + ch, syo + H_LO), (sxo, syo + H_LO)],
                       close=True, dxfattribs={"layer": "Objekat", "color": 6, "lineweight": 50})
    e = msp.add_line((sxo - 100, syo + H_HI), (sxo + ch + 100, syo + H_HI),
                     dxfattribs={"layer": "Objekat", "color": 6})
    ltype(e, "DASHED", SC, 1.5)
    # cut walls: SOUTH with the discharge opening; NORTH open below the door head
    # (the plane runs through the door opening)
    for y, z0, z1 in ((0, 0, dz0), (0, dz1, H_LO), (ch - t, dh_, H_LO)):
        solid_rect(msp, sxo + y, syo + z0, t, z1 - z0, "Objekat", 8)
    solid_rect(msp, sxo, syo + dz0, t, dz1 - dz0, "Ventilacija", 4)
    # deflector hood outside the south wall: closed bottom and sides, louvre on top
    msp.add_lwpolyline([(sxo, syo + dz0 - 50), (sxo - hd, syo + dz0 - 50),
                        (sxo - hd, syo + HOOD_Z)],
                       dxfattribs={"layer": "Ventilacija", "color": 4, "lineweight": 50})
    e = msp.add_line((sxo - hd, syo + HOOD_Z), (sxo, syo + HOOD_Z),
                     dxfattribs={"layer": "Ventilacija", "color": 4})
    ltype(e, "DASHED", SC, 1)
    for k in range(1, 5):                                   # louvre blades
        xk = sxo - hd + k * hd / 5
        msp.add_line((xk - 50, syo + HOOD_Z - 40), (xk + 50, syo + HOOD_Z + 40),
                     dxfattribs={"layer": "Ventilacija", "color": 4})
    # beyond the cut, on the west wall and in the SW corner (hidden parts dashed)
    e = rect(msp, sxo + i0, syo + iz0, i1 - i0, iz1 - iz0, "Ventilacija", color=4, lw=35)
    ltype(e, "DASHED", SC, 1)
    rect(msp, sxo + f0, syo + FAN_Z, f1 - f0, FAN_D, "Ventilacija", color=4, lw=35)
    e = rect(msp, sxo + ky, syo, kh, kada["rim_mm"], "Agregat", color=1)
    ltype(e, "DASHED", SC, 1)
    e = rect(msp, sxo + ty, syo + 40, th, tk["H"], "Agregat", color=30)
    ltype(e, "DASHED", SC, 1)
    rect(msp, sxo + gy, syo + GRO_Z, gd, GRO_H, "Novi1", color=30)
    rect(msp, sxo + L["lights"]["DC"][1] - 200, syo + H_LO - 90, 400, 60, "Sema", color=2)
    # frame, skid (cut along its length), radiator band, plenum to the opening
    rect(msp, sxo + fy, syo, fdep, FRAME_H, "Konstrukcija", color=5, lw=35)
    rect(msp, sxo + sy0, syo + FRAME_H, sl, g["skid_H"], "Agregat", color=30, lw=50)
    hatch_rect(msp, sxo + sy0, syo + FRAME_H, sl, g["skid_H"], "Agregat", "ANSI31",
               SC * 0.3, 30)
    rect(msp, sxo + sy0, syo + FRAME_H + 100, 180, g["skid_H"] - 150, "Agregat",
         color=4, lw=35)
    msp.add_lwpolyline([(sxo + sy0, syo + FRAME_H + 150), (sxo + t, syo + dz0),
                        (sxo + t, syo + dz1), (sxo + sy0, syo + FRAME_H + g["skid_H"] - 50)],
                       close=True, dxfattribs={"layer": "Ventilacija", "color": 4,
                                               "lineweight": 35})
    zm = (dz0 + dz1) / 2
    arrow(msp, [(sxo + sy0 + 40, syo + zm), (sxo - hd / 2, syo + zm)], size=110)
    arrow(msp, [(sxo - hd / 2, syo + zm), (sxo - hd / 2, syo + HOOD_Z + 650)], size=130)
    # exhaust: off the engine up to +2,30, then EAST (towards the viewer, in front of
    # the cut) through the east wall; the silencer sits in the east passage
    msp.add_line((sxo + ey, syo + FRAME_H + g["skid_H"]), (sxo + ey, syo + EXH_Z),
                 dxfattribs={"layer": "Ventilacija", "color": 1, "lineweight": 70})
    msp.add_circle((sxo + ey, syo + EXH_Z), 70, dxfattribs={"layer": "Ventilacija", "color": 1})
    for s in (-1, 1):
        msp.add_line((sxo + ey - 50, syo + EXH_Z - 50 * s), (sxo + ey + 50, syo + EXH_Z + 50 * s),
                     dxfattribs={"layer": "Ventilacija", "color": 1})
    # tower platform P I over the roof, broken at both ends
    zp = GEO["tower"]["platforms_m"][0] * 1000
    xa, xb = sxo - hd - 250, sxo + ch + 350
    solid_rect(msp, xa, syo + zp, xb - xa, 80, "Konstrukcija", 5)
    for xz in (xa, xb):
        msp.add_lwpolyline([(xz, syo + zp - 120), (xz - 50, syo + zp + 40), (xz + 50, syo + zp + 40),
                            (xz, syo + zp + 200)], dxfattribs={"layer": "Konstrukcija", "color": 5})

    # section labels
    _txt(msp, "DEA 18 kVA", sxo + sy0 + sl / 2, syo + FRAME_H + g["skid_H"] + 90, 1.6 * SC,
         color=7, align=TA.CENTER)
    _txt(msp, f"+{dec(EXH_Z)}", sxo + ey - 110, syo + EXH_Z - 25, 1.4 * SC,
         layer="Kota_tekst", color=7, align=TA.RIGHT)
    _txt(msp, "izduv → ISTOK (ispred presjeka)", sxo + ey - 110, syo + EXH_Z + 130,
         1.3 * SC, color=8, align=TA.RIGHT)
    _txt(msp, f"platforma stuba P I +{dec(zp, 1)} m — izduv ne ide iznad krova", xa + 50,
         syo + zp + 180, 1.5 * SC, color=7)
    _txt(msp, f"krov +{dec(H_LO)} / +{dec(H_HI)}", sxo + ch - 100, syo + H_HI + 50, 1.3 * SC,
         layer="Kota_tekst", color=8, align=TA.RIGHT)
    _txt(msp, "GRO (iza)", sxo + gy + gd / 2, syo + GRO_Z + GRO_H + 60, 1.3 * SC, color=8,
         align=TA.CENTER)
    _txt(msp, "spremnik (iza)", sxo + ty + th / 2, syo + tk["H"] + 110, 1.3 * SC, color=8,
         align=TA.CENTER)
    _txt(msp, "ventilator — izvlačni (iza)", sxo + (f0 + f1) / 2, syo + FAN_Z + FAN_D + 60,
         1.3 * SC, color=8, align=TA.CENTER)
    _txt(msp, "vrata (u presjeku)", sxo + ch - t - 60, syo + dh_ - 150, 1.3 * SC, color=8,
         align=TA.RIGHT)
    lead(msp, (sxo + iyc, syo + iz0 + 100),
         f"usis {i1 - i0:.0f} × {iz1 - iz0}, +{dec(iz0)} (zapadni zid, iza)",
         (sxo + iyc + 300, syo - 350), SC, h=1.8)
    lead(msp, (sxo + t / 2, syo + dz0 + 100),
         f"izlaz {dz1 - dz0} × {L['discharge'][1] - L['discharge'][0]:.0f} "
         f"(otvori Stulz), +{dec(dz0)}", (sxo + 350, syo - 700), SC, h=1.8)
    lead(msp, (sxo - hd, syo + HOOD_Z - 250),
         f"hauba {HOOD_W} × {HOOD_D} — izlaz NAVIŠE, rešetka +{dec(HOOD_Z)}",
         (sxo - hd - 150, syo + 2250), SC, h=1.8)
    lead(msp, (sxo + (sy0 + t) / 2, syo + zm + 200), "limeni plenum",
         (sxo + 700, syo + 1650), SC, h=1.8)
    dim_v(msp, syo, syo + H_LO, sxo + ch, SC, off=450)
    _txt(msp, "PRESJEK 1–1  (os agregata — pogled prema ZAPADU, JUG lijevo)", 6000, 6900,
         2.4 * SC, color=7)

    note_block(msp, 600, 1450, SC, "NAPOMENE:", [
        "1  DEA FG Wilson P18-6 (Skid) ili ekv., 18 kVA / 14,4 kW, pobuda PMG ili AREP/AUX; "
        "os SJEVER–JUG u sredini, hladnjak JUG.",
        "2  RASPORED (obavezujući): Stulz je u sredini JUŽNOG zida — izlaz zraka hladnjaka "
        "kroz njegove otvore, spojene/proširene",
        "    na ≥0,36 m² bruto (npr. 600 × 600), limeni plenum; višak otvora zatvoriti "
        "panelom 60 mm.",
        f"3  Vani hauba {HOOD_W} × {HOOD_D}, zatvorenih bočnih strana, rešetka na vrhu "
        f"(+{dec(HOOD_Z)}): topli zrak ide NAVIŠE, ne na FN polje.",
        f"4  Usis 500 × 700 ZAPAD (+0,30, novo, uz alternator). Izduv NO 50 kroz ISTOČNI "
        f"zid na ≈+{dec(EXH_Z)} m, ispod platforme stuba;",
        f"    prigušivač u istočnom prolazu, hvatač iskri, kapa; završetak ≥{dec(EXH_OUT)} m "
        f"od zida ({dec(chk['exhaust_intake'])} m od usisa).",
        f"5  GRO ≤{GRO_W} × {GRO_D} × {GRO_H} mm na SJEVERNOM zidu zapadno od vrata "
        f"(zid {L['gro_wall']:.0f} mm); roštilj OBAVEZAN pod skidom i koritom.",
        f"6  Spremnik 500 l DVOPLAŠNI u koritu {kada['L']} × {kada['W']}, rub "
        f"{kada['rim_mm']} mm, u JUGOZAPADNOM uglu.",
        f"7  SERVIS: istočna strana {L['clr']['east']:.0f} mm (servisna), sjeverni kraj "
        f"{L['clr']['north_gro']:.0f} mm do GRO, zapadna {L['clr']['west']:.0f} mm "
        f"(uz korito {L['clr']['west_tank']:.0f} mm).",
        "8  Unos: skid 620 mm kroz vrata svijetle širine 990 mm, pravo po osi; najprije "
        "spremnik, zatim agregat.",
        "9  Ventilator Ø315 ZAPAD gore je IZVLAČNI (EC 48 V DC, D4). ICC360-HA1-C1 vani "
        "(SJEVER) — principijelno.",
        f"10 Odušak spremnika kroz JUŽNI zid — principijelno: {dec(chk['vent_exhaust'])} m "
        f"od izduva, {dec(chk['vent_intake'])} m od usisa; konačno prema elaboratu ZOP.",
        f"11 DC razvod −48 V ≈{DCB_W} × {DCB_H} × {DCB_D} istočno od vrata: rasvjeta "
        "prepreke, vatrodojava, punjač aku., ventilator, predgrijač, D5.",
        "12 Rasvjeta: LED 230 V AC iz GRO (F2, radi dok DEA radi) i LED 48 V DC (D5) sa "
        "prekidačem uz vrata.",
        "13 Raspored je principijelan — Ponuđač ga potvrđuje na licu mjesta (mjere otvora "
        "Stulz, servisne tačke agregata).",
    ])
    return doc


# --------------------------------------------------------------------------
# H-05  Jednopolna šema — novi GRO i DC razvod −48 V                       —
# --------------------------------------------------------------------------
def sheet_h05():
    """Equivalent of Sjednica E-01: the PV DC chain as E-01 draws it, the
    Huawei ICC360, the new GRO (AC, live only while the DEA runs) and the new
    DC razvod -48 V for the always-on loads (user decision 11.09.2026)."""
    SC = 50
    doc, msp = _sheet(SC, "Jednopolna šema — novi GRO i DC razvod −48 V", "H-05", "—")
    LY = "Sema"
    arr, ctl = D["array"], D["control"]
    per_string = arr["modules_total"] // 2
    wp = int(round(arr["kWp"] * 1000 / arr["modules_total"]))

    def box(x, y, w, h, label, sub="", sub2="", color=7, new=False):
        if new:
            hatch_rect(msp, x, y, w, h, LY, "ANSI31", SC * 4, 8)
        rect(msp, x, y, w, h, LY, color=color, lw=50)
        n = 1 + bool(sub) + bool(sub2)
        yy = y + h / 2 + (n - 1) * 95
        _txt(msp, label, x + w / 2, yy, 1.9 * SC, color=7, align=TA.MIDDLE_CENTER)
        for s in (sub, sub2):
            if s:
                yy -= 190
                _txt(msp, s, x + w / 2, yy, 1.5 * SC, color=8, align=TA.MIDDLE_CENTER)

    def wire(*pts, color=7, lw=35):
        msp.add_lwpolyline(pts, dxfattribs={"layer": LY, "color": color, "lineweight": lw})

    def enclosure(x, y, w, h, color, title, sub=""):
        e = rect(msp, x, y, w, h, LY, color=color, lw=35)
        ltype(e, "DASHED", SC, 2)
        _txt(msp, title, x + 150, y + h - 250, 1.8 * SC, color=7)
        if sub:
            _txt(msp, sub, x + 150, y + h - 420, 1.4 * SC, color=8)

    # ---- PV DC chain (as E-01): 2 strings x 6, DC SPD at the array, PVDB, 2 x iSSU
    kwp_s = dec(arr["kWp"] * 1000 / 2)
    box(1300, 12800, 2600, 1000, "STRING 1", f"{per_string} × {wp} Wp = {kwp_s} kWp", color=5)
    box(1300, 11350, 2600, 1000, "STRING 2", f"{per_string} × {wp} Wp = {kwp_s} kWp", color=5)
    _txt(msp, "nosači PV-1 + PV-2", 1300, 12600, 1.6 * SC, color=8)
    _txt(msp, "nosači PV-2 + PV-3", 1300, 11150, 1.6 * SC, color=8)
    box(4500, 12800, 1900, 1000, "SPD DC tip 2", "na polju · string 1", color=1)
    box(4500, 11350, 1900, 1000, "SPD DC tip 2", "na polju · string 2", color=1)
    box(7100, 11900, 2600, 1300, "PVDB 500-15-2B", "IP55 · 2 rute", "DC SPD tip 2", color=5)
    wire((3900, 13300), (4500, 13300), color=5)
    wire((3900, 11850), (4500, 11850), color=5)
    wire((6400, 13300), (6750, 13300), (6750, 12850), (7100, 12850), color=5)
    wire((6400, 11850), (6750, 11850), (6750, 12250), (7100, 12250), color=5)
    wire((9700, 12850), (11200, 12850), (11200, 13300), (12000, 13300), color=5)
    wire((9700, 12250), (11400, 12250), (11400, 11900), (12000, 11900), color=5)

    # ---- Huawei ICC360-HA1-C1 (Buyer's equipment)
    enclosure(11600, 6700, 4800, 7500, 30, "Huawei ICC360-HA1-C1 (oprema Kupca)",
              "vani na ploči, SJEVER — principijelno")
    box(12000, 12900, 2000, 800, "iSSU S4875G2", "MPPT · ruta 1", color=30)
    box(12000, 11500, 2000, 800, "iSSU S4875G2", "MPPT · ruta 2", color=30)
    box(12000, 9300, 2000, 1100, "ISPRAVLJAČI", "R4875 · AC → −48 V",
        f"ulaz ≤{dec(ctl['rect_cap_ac_kw'] * 1000, 1)} kW (SMU)", color=30)
    wire((14700, 7400), (14700, 13400), lw=70)
    _txt(msp, "−48 V DC", 14780, 13450, 1.6 * SC, color=7)
    for y in (13300, 11900, 9850):
        wire((14000, y), (14700, y), color=30)
    box(15000, 12700, 1250, 900, "BATERIJA", "LFP −48 V", color=5)
    box(15000, 10900, 1250, 900, "DC TK", "oprema TK", color=7)
    box(15000, 7700, 1250, 1000, "DC IZLAZ", "rezerva, prekidač", color=7)
    for y in (13150, 11350, 8200):
        wire((14700, y), (15000, y))

    # ---- new GRO (AC) - the DEA is the only AC source
    box(1300, 9300, 2600, 1300, "DEA 18 kVA", "400/230 V · 14,4 kW", "PMG ili AREP/AUX",
        color=30, new=True)
    msp.add_circle((4200, 8900), 60, dxfattribs={"layer": LY, "color": 7})
    _txt(msp, "poz. 2 — rezerva", 4050, 8860, 1.5 * SC, color=8, align=TA.RIGHT)
    enclosure(4400, 5000, 6700, 5900, 30, f"GRO (AC) — NOVO, ≤{GRO_W} × {GRO_D} × {GRO_H} mm",
              "SJEVERNI zid kontejnera, zapadno od vrata")
    box(4700, 9300, 2200, 1100, "Q0 SKLOPKA IZVORA", "4p · 1-0-2 · 63 A",
        "1 DEA · 0 · 2 rezerva", color=30, new=True)
    wire((3900, 10100), (4700, 10100), color=30)
    wire((4260, 8900), (4500, 8900), (4500, 9550), (4700, 9550), color=30)
    _txt(msp, "1", 4580, 10150, 1.4 * SC, color=8)
    _txt(msp, "2", 4580, 9600, 1.4 * SC, color=8)
    box(4700, 7500, 2200, 1000, "FI0 · RCD 4p", "63 A / 300 mA · S-tip", color=30, new=True)
    wire((5800, 9300), (5800, 8500), color=30)
    wire((5800, 8900), (7500, 8900), color=1)
    box(7500, 8450, 2300, 900, "SPD AC tip 1+2", "Iimp ≥12,5 kA/pol · Up ≤1,5 kV", color=1, new=True)
    wire((5800, 7500), (5800, 7000), color=30)
    wire((4600, 7000), (10900, 7000), color=7, lw=100)
    _txt(msp, "L1 L2 L3 N · 400/230 V", 9100, 7090, 1.4 * SC, color=8)
    # GSI with the one N-PE link and the SPD earth
    for c_, dy in ((2, 0), (3, -60)):
        wire((4600, 5300 + dy), (10900, 5300 + dy), color=c_, lw=50)
    _txt(msp, "PE / GSI", 4650, 5380, 1.4 * SC, color=7)
    wire((4800, 7000), (4800, 5300), color=3, lw=50)
    rect(msp, 4650, 6000, 300, 300, LY, color=3, lw=35)
    _txt(msp, "jedini spoj N–PE (TN-S)", 5000, 5600, 1.4 * SC, color=7)
    wire((8650, 8450), (8650, 5300), color=1)
    feeders = [(6350, "F2 · RCBO", "16 A / 30 mA, A", "RASVJETA AC", "1 svjetiljka", "NOVO"),
               (7400, "F3 · RCBO", "16 A / 30 mA, A", "UTIČNICE", "kontejnera", "NOVO"),
               (8450, "F4", "1p C 16 A", "POMOĆNI", "potrošači DEA", "AC"),
               (9500, "F5", "1p C 16 A", "REZERVA", "", "")]
    for x, b1, b2, l1, l2, l3 in feeders:
        wire((x, 7000), (x, 6600), color=30)
        box(x - 450, 5700, 900, 900, b1, b2, color=30, new=True)
        wire((x, 5700), (x, 4700), color=30)
        box(x - 500, 3300, 1000, 1400, l1, l2, l3, color=7)
    wire((10550, 7000), (10550, 6600), color=30)
    box(10100, 5700, 900, 900, "F1", "3p C 32 A", color=30, new=True)
    wire((11000, 6150), (11350, 6150), (11350, 9850), (12000, 9850), color=30)
    _txt(msp, "F1 kroz sjeverni zid", 11300, 6500, 1.3 * SC, color=8, rotation=90)

    # ---- new DC razvod -48 V (always-on loads)
    enclosure(16900, 3300, 3450, 7300, 30, "DC RAZVOD −48 V — NOVO",
              "trajni potrošači (≤25 W prosječno)")
    _txt(msp, "SJEVERNI zid, istočno od vrata", 17050, 9880, 1.3 * SC, color=8)
    wire((16250, 8200), (16650, 8200), (16650, 9600), (17300, 9600), color=5)
    _txt(msp, "−48 V iz ICC360, kroz sjeverni zid", 16600, 7200, 1.3 * SC, color=8,
         rotation=90)
    wire((17300, 9600), (17300, 3950), lw=70)
    rows = [(8750, "D1", "2p 6 A DC", "RASVJETA PREPREKE", "LED 48 V DC, fotoćelija",
             "nadzor ispada → SMU"),
            (7700, "D2", "2p 6 A DC", "VATRODOJAVA", "DC/DC → centrala",
             "baterije EN 54-4"),
            (6650, "D3", "2p 10 A DC", "PUNJAČ AKU. DEA", "DC/DC, strujni limit",
             "alarm → SMU"),
            (5600, "D4", "2p 10 A DC", "VENTILATOR Ø315", "EC 48 V DC, izvlačni",
             "termostat; stop dok DEA radi"),
            (4550, "D5", "2p 6 A DC", "RASVJETA DC", "LED 48 V DC",
             "prekidač uz vrata"),
            (3500, "D6", "2p 10 A DC", "PREDGRIJAČ DEA", "rashladna tečnost, DC",
             "uključuje ga KOA prije starta")]
    for y, b1, b2, l1, l2, l3 in rows:
        yc = y + 450
        wire((17300, yc), (17550, yc))
        box(17550, y, 900, 900, b1, b2, color=30, new=True)
        wire((18450, yc), (18600, yc))
        box(18600, y - 50, 1650, 1000, l1, l2, l3, color=7)
    e = msp.add_lwpolyline([(20300, 8150), (20300, 6050)],
                           dxfattribs={"layer": LY, "color": 1, "lineweight": 35})
    ltype(e, "DASHED", SC, 1)
    _txt(msp, "blokada pri požaru", 20290, 6400, 1.2 * SC, color=1, rotation=90)

    # ---- earth
    for c_, dy in ((2, 0), (3, -70)):
        wire((1300, 3050 + dy), (20350, 3050 + dy), color=c_, lw=70)
    for x, ytop in ((2600, 9300), (10900, 5300), (13500, 6700), (18600, 3300)):
        wire((x, 3050), (x, ytop), color=2, lw=50)
    _txt(msp, "postojeći uzemljivač FeZn 25×4 (2 prstena na 0,8 m + temelji stuba) · R ≤ 10 Ω "
              "· nosači FN vezani Cu užetom 50 mm² preko bimetalnih spojeva",
         1300, 2760, 1.6 * SC, color=7)

    note_block(msp, 1300, 2450, SC, "NAPOMENE:", h=1.8, lines=[
        "1  Lokacija NIJE na mreži — DEA je jedini AC izvor; izvodi GRO su pod naponom samo dok "
        "DEA radi. Trajni potrošači su na DC razvodu −48 V.",
        "2  TN-S: jedini spoj N–PE je u novom GRO; R ≤ 10 Ω. Odvodnici: AC tip 1+2, DC tip 2 po "
        "stringu, signalni vodovi EN 61643-21.",
        "3  DEA sa nezavisnom pobudom PMG ili AREP/AUX (≥3 × In ≈ 78 A, ≥10 s); RCD 63 A / 300 mA "
        "S-tip je obavezan.",
        f"4  Ulaz ispravljača ograničen na {dec(ctl['rect_cap_ac_kw'] * 1000, 1)} kW dok radi DEA "
        "(SMU). Klima-uređaj Stulz se demontira — nema izvoda za klimatizaciju.",
        f"5  FN: {arr['modules_total']} modula = 2 stringa × {per_string}; PVDB ima 2 rute → "
        "2 × iSSU S4875G2. Požar: STOP DEA i isključenje ventilatora.",
        "6  Nazivne struje F4–F5 i D1–D6 su orijentacione; presjeke i selektivnost potvrđuje "
        "Izvođač. ICC360 — principijelno.",
    ])
    hatch_rect(msp, 1300, 700, 700, 300, LY, "ANSI31", SC * 4, 8)
    rect(msp, 1300, 700, 700, 300, LY, color=8)
    _txt(msp, "isporuka i montaža Izvođača (DEA, GRO, DC razvod −48 V)", 2150, 790,
         1.6 * SC, color=7)
    rect(msp, 7300, 700, 700, 300, LY, color=8)
    _txt(msp, "oprema Kupca (FN, ICC360) i potrošači", 8150, 790, 1.6 * SC, color=7)
    return doc


SHEETS = {"H-01": (sheet_h01, 100), "H-02": (sheet_h02, 100), "H-03": (sheet_h03, 30),
          "H-04": (sheet_h04, 25), "H-05": (sheet_h05, 50)}
