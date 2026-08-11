# -*- coding: utf-8 -*-
"""
Sheets S-02, S-03, M-01 and E-01.

Geometry comes from `design.json`, which carries the numbers settled by the three
expert reviews and by the Investor's site corrections (`review/05-site-corrections.md`).
S-01 lives in build_drawings.py; this module is imported by it.
"""
from __future__ import annotations

import math

from ezdxf.enums import TextEntityAlignment as TA

from bht_frame import draw_frame, new_doc, north_arrow, scale_bar, _txt


def register(B):
    """B is the build_drawings module - reuse its helpers so style stays identical."""
    rect, solid_rect, hatch_rect = B.rect, B.solid_rect, B.hatch_rect
    dim_h, dim_v, leader = B.dim_h, B.dim_v, B.leader
    legend, note_block, site_plan = B.legend, B.note_block, B.site_plan
    _design, GEO = B._design, B.GEO

    # ------------------------------------------------------------------ S-02
    def sheet_s02():
        SC = 50
        D = _design()
        doc = new_doc()
        msp = doc.modelspace()
        draw_frame(msp, SC, naziv="Situacija — BUDUĆE STANJE (LOT 1 + LOT 2)",
                   broj="S-02", razmjera="1:50")

        # PY set so the 9,40 m parcel boundary stays inside the 14850-unit sheet
        # height at 1:50 (it used to overrun the top edge by 150)
        PX, PY = 2600, 5350
        ox, oy = PX + 8000 - 2750, PY + 4700 - 2750
        k = site_plan(msp, ox, oy, SC)
        cx, cy, CW, CH = k["cont"]
        F = k["fence"][2]
        px, py, pw, ph = k["parcel"]

        sup = D["support"]
        fw, proj = sup["field_w"], sup["proj"]
        # The array is set as far SOUTH as the leased parcel allows: its lower edge
        # sits just inside the southern boundary, so both foundation strips fall in
        # the 1950 mm band outside the fence and the panels clear the container
        # instead of oversailing it. See review/07-calculations.md F.6.
        ay = py + 100
        mid = ox + F / 2
        gap = 500
        total_w = 3 * fw + 2 * gap
        axs = [mid - total_w / 2 + i * (fw + gap) for i in range(3)]

        for i, ax in enumerate(axs, 1):
            rect(msp, ax, ay, fw, proj, "Panel", color=110, lw=70)
            # cross-hatch reads as a module field at 1:50. ANSI37 (the ANSI31
            # family already used on this package) renders reliably; NET came out
            # as a solid fill through the plot backend.
            hatch_rect(msp, ax, ay, fw, proj, "Panel", "ANSI37", SC * 1.2, 110)
            msp.add_line((ax, ay + proj / 2), (ax + fw, ay + proj / 2),
                         dxfattribs={"layer": "Panel", "color": 8})
            msp.add_line((ax + fw / 2, ay), (ax + fw / 2, ay + proj),
                         dxfattribs={"layer": "Panel", "color": 8})
            # strips run north from the panel's lower edge, staying inside the
            # 1950 mm band between the parcel boundary and the fence
            for so in (fw / 2 - sup["strip_spacing"] / 2,
                       fw / 2 + sup["strip_spacing"] / 2):
                rect(msp, ax + so - 225, ay, 450, 1500,
                     "Temelj", color=32, lw=35)
            _txt(msp, f"PV-{i}  ·  4 × 585 Wp  ·  45°  JUG", ax + fw / 2,
                 ay - 800, 2.2 * SC, layer="Tekst", color=7, align=TA.CENTER)

        msp.add_lwpolyline([(mid, ay + proj), (mid, cy + 150)],
                           dxfattribs={"layer": "Kabal", "color": 2, "lineweight": 35})
        for ax in (axs[0], axs[2]):
            msp.add_lwpolyline([(ax + fw / 2, ay + proj), (ax + fw / 2, oy - 380),
                                (mid, oy - 380), (mid, cy + 150)],
                               dxfattribs={"layer": "Kabal", "color": 2,
                                           "lineweight": 35})

        v = D["ventilation"]
        # cross-flow layout (see M-01 / design.json ventilation.layout):
        # intake SOUTH wall east end, discharge WEST wall on the radiator axis
        solid_rect(msp, cx + 2150, cy, v["intake_mm"][0], 60, "Ventilacija", 4)
        solid_rect(msp, cx, cy + 430, 60, v["discharge_mm"][0], "Ventilacija", 4)

        g, tk = D["genset"], D["tank"]
        gx, gy = cx + 450, cy + 420
        rect(msp, gx, gy, g["skid_L"], g["skid_W"], "Agregat", color=30, lw=50)
        _txt(msp, "DEA 22 kVA", gx + g["skid_L"] / 2, gy + g["skid_W"] / 2,
             1.7 * SC, layer="Tekst", color=7, align=TA.MIDDLE_CENTER)
        bnd = tk["bund"]
        rect(msp, cx + 350, cy + CH - 60 - bnd["W"], bnd["L"], bnd["W"],
             "Agregat", color=1)
        rect(msp, cx + 550, cy + CH - 60 - bnd["W"] + 180, tk["L"], tk["W"],
             "Agregat", color=30)
        _txt(msp, "500 l", cx + 550 + tk["L"] / 2,
             cy + CH - 60 - bnd["W"] + 180 + tk["W"] / 2,
             1.7 * SC, layer="Tekst", color=7, align=TA.MIDDLE_CENTER)

        dim_h(msp, axs[0], axs[0] + fw, ay, SC, off=-1000)
        dim_v(msp, ay, ay + proj, axs[0], SC, off=-1000)
        dim_h(msp, px, px + pw, py, SC, off=-1400)
        dim_v(msp, py, py + ph, px + pw, SC, off=1400)

        leader(msp, (cx + 2400, cy + 30),
               "usisna žaluzina 500 × 700 mm — JUŽNI zid", 2600, -1500, SC)
        leader(msp, (cx + 30, cy + 730),
               "kanal + žaluzina 600 × 600, izduv DN 65 iznad krova — ZAPADNI zid; "
               "ventilator 1200 m³/h — ISTOČNI zid",
               -1900, 2500, SC)
        leader(msp, (mid, oy - 380), "DC trasa u PEHD Ø50 → PVDB (2 stringa, v. E-01)",
               2900, -1250, SC)
        leader(msp, (axs[0] + 400, ay - 100),
               "2 temeljne trake po nosaču (×3), 450 × 3300, razmak 1600 — IZVAN ograde",
               -2200, -900, SC)

        north_arrow(msp, 19500, 11700, 1700)
        scale_bar(msp, 1200, 4500, SC, total_m=5, step_m=1)
        # below the parcel dimension line (py - 1400 = 4000), which used to run
        # straight through the second line of the notes
        legend(msp, 1200, 3400, SC, [
            (110, "LOT 1 — nosači FN panela PV-1..PV-3 (po 4 × 585 Wp, 45°, JUG) — 2 stringa × 6"),
            (32,  "LOT 1 — AB temeljne trake 450 × 3300 mm, razmak 1600 mm"),
            (2,   "LOT 1 — DC trasa u PEHD Ø50 do PVDB"),
            (30,  "LOT 2 — DEA 22 kVA u skid izvedbi i spremnik 500 l"),
            (4,   "LOT 2 — usisna žaluzina (JUG); kanal, žaluzina i izduv (ZAPAD); ventilator (ISTOK)"),
        ])
        note_block(msp, 7900, 3400, SC, "NAPOMENA — PRORAČUNSKO OPTEREĆENJE:", [
            "Vjetar qp ≥ 1,20 kN/m² (udar 3 s ≈ 45 m/s) — iznad kapaciteta kataloškog",
            "nosača tipa A, stoga CUSTOM IZRADA: sail 10,55 m²/nosaču, ULS uzgon 18,1 kN,",
            "moment prevrtanja 62,8 kNm; ovjerava ponuđač (Prilog II, 1.3).",
            "Temelji IZVAN ograde (400 mm od kote ograde); gornja ivica panela +4,74 m,",
            "2836 mm iznad ograde. Kontejner je PRAZAN.",
        ])
        return doc

    # ------------------------------------------------------------------ S-03
    def sheet_s03():
        SC = 30
        D = _design()
        doc = new_doc()
        msp = doc.modelspace()
        draw_frame(msp, SC, naziv="Presjek A–A kroz nosač FN panela", broj="S-03",
                   razmjera="1:30")

        sup, arr = D["support"], D["array"]
        C_H = D["container"]["height"]
        proj = sup["proj"]
        b, top = arr["bottom_edge"], arr["top_edge"]
        # A3 window at 1:30 is 600..12300 x 300..8610, title block x>6900 below
        # y=1740. The panel reaches +4736 above the ground line, so the ground line
        # sits at 2600 and the notes go bottom-left, clear of the title block.
        GX, GY = 2200, 2600
        msp.add_line((GX - 1400, GY), (GX + 10200, GY),
                     dxfattribs={"layer": "Objekat", "color": 8, "lineweight": 50})
        for i in range(26):
            x = GX - 1200 + i * 450
            msp.add_line((x, GY), (x - 150, GY - 150),
                         dxfattribs={"layer": "Objekat", "color": 8})

        x0, y0 = GX + 500, GY + b
        x1, y1 = x0 + proj, GY + top
        msp.add_lwpolyline([(x0, y0), (x1, y1)],
                           dxfattribs={"layer": "Panel", "color": 5, "lineweight": 70})
        msp.add_lwpolyline([(x0, y0 - 80), (x1, y1 - 80)],
                           dxfattribs={"layer": "Panel", "color": 8})
        msp.add_line((x0, y0), (x0, GY), dxfattribs={"layer": "Konstrukcija", "color": 5})
        msp.add_line((x1, y1), (x1, GY), dxfattribs={"layer": "Konstrukcija", "color": 5})
        msp.add_line((x0, y0), (x1, GY), dxfattribs={"layer": "Konstrukcija", "color": 8})
        for fx in (x0, x1):
            rect(msp, fx - 225, GY - 900, 450, 900, "Temelj", color=32, lw=50)
            hatch_rect(msp, fx - 225, GY - 900, 450, 900, "Temelj", "ANSI31",
                       SC * 0.35, 32)

        fx = x1 + 800
        msp.add_line((fx, GY), (fx, GY + 1900),
                     dxfattribs={"layer": "Ograda", "color": 8, "lineweight": 50})

        # existing slab and container north of the fence, so the section shows what
        # the panel actually oversails
        S_, CW_, CH_ = 5400, 3005, 2300
        sx_ = fx + 50
        rect(msp, sx_, GY - 300, S_, 300, "Objekat", color=254, lw=35)
        hatch_rect(msp, sx_, GY - 300, S_, 300, "Objekat", "ANSI31", SC * 0.5, 8)
        cx_ = sx_ + (S_ - CH_) / 2
        rect(msp, cx_, GY, CH_, C_H, "Objekat", color=6, lw=50)
        _txt(msp, "postojeći kontejner", cx_ + CH_ / 2, GY + C_H / 2, 2.0 * SC,
             layer="Tekst", color=7, align=TA.MIDDLE_CENTER)
        _txt(msp, f"{CH_} × {C_H} mm", cx_ + CH_ / 2, GY + C_H / 2 - 350,
             1.7 * SC, layer="Tekst", color=8, align=TA.CENTER)
        _txt(msp, "postojeća AB ploča 5,40 × 5,40 m", sx_ + S_ / 2, GY - 620,
             1.7 * SC, layer="Tekst", color=8, align=TA.CENTER)

        for lvl, lab in ((b, f"donja ivica panela  +{b / 1000:.2f}".replace(".", ",")),
                         (1900, "kota ograde  +1,90"),
                         (top, f"gornja ivica panela  +{top / 1000:.2f}".replace(".", ","))):
            msp.add_line((GX - 1100, GY + lvl), (fx + 1900, GY + lvl),
                         dxfattribs={"layer": "Sakriveno", "color": 8})
            _txt(msp, lab, fx + 2000, GY + lvl - 50, 2.0 * SC,
                 layer="Kota_tekst", color=7)

        dim_h(msp, x0, x1, GY - 900, SC, off=-1300)
        dim_v(msp, GY, GY + top, GX - 1100, SC, off=-800)
        _txt(msp, "45°", x0 + 700, GY + b + 500, 2.6 * SC, layer="Kote", color=7)
        # kept above y=1740 so they clear the title block, which starts at x=6900
        _txt(msp, "S J E V E R  →", fx + 500, GY - 480, 2.4 * SC,
             layer="Orijentacija", color=1)
        _txt(msp, "←  J U G", GX - 1100, GY - 480, 2.4 * SC,
             layer="Orijentacija", color=1)
        _txt(msp, "ograda h=1,90 m", fx + 150, GY + 900, 2.0 * SC,
             layer="Tekst", color=8)

        note_block(msp, 700, 1500, SC, "OBJAŠNJENJA:", [
            "1  Polje: 2 reda × 2 modula 585 Wp, portret — 2305 × 4576 mm po nagibu,",
            "    horizontalna projekcija 3236 mm pri 45°.",
            "2  Dvije temeljne trake po nosaču 450 × 3300 mm, dubina 900 mm, razmak 1600 mm;",
            "    beton C30/37 (XC4+XF3) na podlozi C12/15, armatura B500B.",
            "3  Donja ivica +1,50 m, gornja +4,74 m — 2,84 m iznad kote ograde h=1,90 m.",
            "4  CUSTOM IZRADA prema qp ≥ 1,20 kN/m²: sail 10,55 m²/nosaču, ULS uzgon 18,1 kN,",
            "    moment prevrtanja 62,8 kNm (v. S-02).",
        ])
        return doc

    # ------------------------------------------------------------------ M-01
    def sheet_m01():
        SC = 25
        D = _design()
        doc = new_doc()
        msp = doc.modelspace()
        draw_frame(msp, SC, naziv="DEA u postojećem kontejneru — osnova i presjek",
                   broj="M-01", razmjera="1:25")
        C, g, tk, v = D["container"], D["genset"], D["tank"], D["ventilation"]
        CW, CH = C["ext"]
        t = C["wall"]

        # Plan and section both sit inside the A3 window (500..10250 x 250..7175 at
        # 1:25); the title block occupies x>5750 below y=1450. Keeping to it is what
        # makes the sheet plot at a true 1:25 instead of being shrunk to fit.
        ox, oy = 1900, 4300
        rect(msp, ox, oy, CW, CH, "Objekat", color=6, lw=50)
        rect(msp, ox + t, oy + t, CW - 2 * t, CH - 2 * t, "Objekat", color=6)
        for hx, hy, hw, hh in ((ox, oy, CW, t), (ox, oy + CH - t, CW, t),
                               (ox, oy + t, t, CH - 2 * t),
                               (ox + CW - t, oy + t, t, CH - 2 * t)):
            solid_rect(msp, hx, hy, hw, hh, "Objekat", 8)
        _txt(msp, "OSNOVA  —  kontejner je PRAZAN", ox, oy + CH + 520, 2.6 * SC,
             layer="Tekst", color=7)

        lay = tk["bund"]

        def arrow(pts, color=4):
            msp.add_lwpolyline(pts, dxfattribs={"layer": "Ventilacija",
                                                "color": color, "lineweight": 35})
            (x1, y1), (x0, y0) = pts[-1], pts[-2]
            ang = math.atan2(y1 - y0, x1 - x0)
            a1 = (x1 - 160 * math.cos(ang - 0.42), y1 - 160 * math.sin(ang - 0.42))
            a2 = (x1 - 160 * math.cos(ang + 0.42), y1 - 160 * math.sin(ang + 0.42))
            msp.add_solid([a1, (x1, y1), a2],
                          dxfattribs={"layer": "Ventilacija", "color": color})

        # genset along the SOUTH side, radiator end WEST; skid entry through the
        # east door, then shifted south.  Cross-flow SE -> W (see design.json
        # ventilation.layout - closes EL RED-03).
        gx, gy = ox + 450, oy + 420
        rect(msp, gx - 120, gy - 120, g["skid_L"] + 240, g["skid_W"] + 240,
             "Konstrukcija", color=5, lw=35)
        rect(msp, gx, gy, g["skid_L"], g["skid_W"], "Agregat", color=30, lw=50)
        _txt(msp, "DEA 22 kVA / 17,6 kW, skid", gx + g["skid_L"] / 2,
             gy + g["skid_W"] / 2, 1.9 * SC, layer="Tekst", color=7,
             align=TA.MIDDLE_CENTER)
        # radiator end (WEST) marked as a band across the skid
        rect(msp, gx, gy, 180, g["skid_W"], "Agregat", color=4, lw=35)
        _txt(msp, "RADIJATOR", gx + 90, gy - 230, 1.4 * SC,
             layer="Tekst", color=8, align=TA.CENTER)

        # radiator duct straight out the WEST wall + discharge louvre 600x600
        dy_c = gy + g["skid_W"] / 2                       # radiator axis
        rect(msp, ox + t, dy_c - 300, gx - ox - t, 600, "Ventilacija", color=4,
             lw=35)
        solid_rect(msp, ox, dy_c - 300, t, 600, "Ventilacija", 4)

        # intake louvre 500 wide in the SOUTH wall, east end
        solid_rect(msp, ox + 2150, oy, v["intake_mm"][0], t, "Ventilacija", 4)

        # exhaust DN65 riser at the WEST wall, north of the duct
        msp.add_circle((ox + t + 90, oy + 1350), 60,
                       dxfattribs={"layer": "Ventilacija", "color": 1})

        # Tank in its 110 % bund against the NORTH wall, set east of the west end so
        # its mass lands over more secondary floor beams and clear of the radiator
        # duct penetration. Its own spreading frame is drawn under the bund.
        bx, by = ox + 1150, oy + CH - t - lay["W"]
        rect(msp, bx - 120, by - 120, lay["L"] + 240, lay["W"] + 240,
             "Konstrukcija", color=5, lw=35)
        rect(msp, bx, by, lay["L"], lay["W"], "Agregat", color=1, lw=35)
        tx, ty = bx + (lay["L"] - tk["L"]) / 2, by + (lay["W"] - tk["W"]) / 2
        rect(msp, tx, ty, tk["L"], tk["W"], "Agregat", color=30, lw=35)
        _txt(msp, "spremnik 500 l", tx + tk["L"] / 2, ty + tk["W"] / 2,
             1.7 * SC, layer="Tekst", color=7, align=TA.MIDDLE_CENTER)

        # tank vent penetration, NORTH wall east end
        msp.add_circle((ox + 2800, oy + CH - t / 2), 40,
                       dxfattribs={"layer": "Ventilacija", "color": 1})

        # door in the EAST wall with outward swing; room fan above it to the north
        dy0 = oy + CH / 2 - 450
        solid_rect(msp, ox + CW - t, dy0, t, 900, "Objekat", 0)
        msp.add_line((ox + CW, dy0), (ox + CW + 900, dy0),
                     dxfattribs={"layer": "Objekat", "color": 8})
        msp.add_arc(center=(ox + CW, dy0), radius=900, start_angle=0,
                    end_angle=90, dxfattribs={"layer": "Objekat", "color": 8})
        solid_rect(msp, ox + CW - t, oy + 1750, t, 315, "Ventilacija", 4)

        # airflow arrows: in at SE low, across the room, out west through the duct
        arrow([(ox + 2400, oy - 350), (ox + 2400, oy + 550)])
        arrow([(ox + 2300, oy + 730), (gx + g["skid_L"] + 150, dy_c)])
        arrow([(ox + t + 150, dy_c), (ox - 500, dy_c)])

        dim_h(msp, ox, ox + CW, oy, SC, off=-800)
        dim_v(msp, oy, oy + CH, ox, SC, off=-800)
        dim_h(msp, ox + 2150, ox + 2650, oy, SC, off=-350)

        # Callouts stay short and stay on the sheet; the normative wording lives in
        # the notes below and in Prilog I 4.3.
        leader(msp, (ox + 2400, oy + t / 2), "usis 500 × 700 (JUG, +0,30)",
               900, -700, SC)
        leader(msp, (ox + t / 2, dy_c), "kanal + žaluzina 600 × 600 (ZAPAD)",
               -500, 1500, SC)
        leader(msp, (ox + t + 90, oy + 1350), "izduv DN 65 (ZAPAD)", -500, -750, SC)
        leader(msp, (bx + lay["L"], by + lay["W"] / 2), "tankvana ≥110 %",
               700, -350, SC)
        leader(msp, (ox + 2800, oy + CH), "oduška (SJEVER)", 500, 400, SC)
        leader(msp, (ox + CW - t / 2, oy + 1900), "ventilator Ø315 (ISTOK)",
               600, 350, SC)
        leader(msp, (gx - 120, gy - 120), "roštilj za raznošenje opterećenja",
               -500, -400, SC)
        # walls are referenced by cardinal name throughout the TD and Prilog I,
        # so name them on the plan itself
        # note: not tx/ty - those hold the tank origin, which the section reuses
        for label, lx, ly, al in (
                ("S J E V E R", ox + CW / 2, oy + CH + 130, TA.CENTER),
                ("J U G", ox + CW / 2, oy - 300, TA.CENTER),
                ("Z A P A D", ox - 130, oy + CH / 2, TA.RIGHT),
                ("I S T O K", ox + CW + 130, oy + CH - 400, TA.LEFT)):
            _txt(msp, label, lx, ly, 2.0 * SC, layer="Orijentacija", color=1,
                 align=al)

        sxo, syo = 6600, 4000
        H = C["height"]
        rect(msp, sxo, syo, CW, H, "Objekat", color=6, lw=50)
        _txt(msp, "PRESJEK 1–1  (pogled prema SJEVERU — ZAPAD lijevo)", sxo,
             syo + H + 520, 2.6 * SC, layer="Tekst", color=7)
        msp.add_line((sxo - 500, syo), (sxo + CW + 500, syo),
                     dxfattribs={"layer": "Objekat", "color": 8, "lineweight": 50})

        # genset elevation, radiator end at the WEST (left) wall
        rect(msp, sxo + 450, syo, g["skid_L"], g["skid_H"], "Agregat", color=30, lw=50)
        hatch_rect(msp, sxo + 450, syo, g["skid_L"], g["skid_H"], "Agregat",
                   "ANSI31", SC * 0.3, 30)

        # radiator duct + discharge louvre through the WEST wall
        rect(msp, sxo + t, syo + 380, 450 - t, 640, "Ventilacija", color=4, lw=35)
        solid_rect(msp, sxo, syo + 400, t, 600, "Ventilacija", 4)
        arrow([(sxo + 350, syo + 700), (sxo - 500, syo + 700)])

        # exhaust: flex -> silencer -> riser along the WEST wall, above the roof
        msp.add_lwpolyline([(sxo + 900, syo + g["skid_H"]),
                            (sxo + 900, syo + 1600), (sxo + 260, syo + 1600),
                            (sxo + 260, syo + H + 380)],
                           dxfattribs={"layer": "Ventilacija", "color": 1,
                                       "lineweight": 70})
        rect(msp, sxo + 700, syo + 1650, 400, 260, "Ventilacija", color=1, lw=35)
        _txt(msp, "prigušivač", sxo + 1180, syo + 1730, 1.5 * SC,
             layer="Tekst", color=8)
        _txt(msp, "izduv iznad krova", sxo + 400, syo + H + 200, 1.5 * SC,
             layer="Tekst", color=8)

        # intake louvre on the SOUTH wall (in front of the section plane) - shown
        # dashed at its true x-position and height
        rect(msp, sxo + 2150, syo + 300, 500, 700, "Sakriveno", color=8)
        _txt(msp, "usis (JUŽNI zid)", sxo + 2000, syo + 1120, 1.5 * SC,
             layer="Tekst", color=8)
        arrow([(sxo + 2400, syo + 650), (sxo + 2000, syo + 650)])

        # tank behind the section plane (NORTH wall), dashed at its plan position -
        # at 1310 mm it stands above the 1020 mm genset silhouette
        rect(msp, sxo + (tx - ox), syo, tk["L"], tk["H"], "Sakriveno", color=8)
        _txt(msp, "spremnik iza presjeka", sxo + (tx - ox), syo + tk["H"] + 110,
             1.5 * SC, layer="Tekst", color=8)

        # room fan high on the EAST (right) wall
        solid_rect(msp, sxo + CW - t, syo + 1750, t, 315, "Ventilacija", 4)
        _txt(msp, "ventilator", sxo + CW - 700, syo + 2130, 1.5 * SC,
             layer="Tekst", color=8)

        dim_v(msp, syo, syo + H, sxo, SC, off=-700)

        # below the container dimension line at oy-800 = 3500
        note_block(msp, 700, 3150, SC, "NAPOMENE:", [
            "1  FG Wilson P22-6 (Skid), TL 2019-08-14: hladnjak 1980 m³/h, sagorijevanje 90 m³/h,",
            "    toplota u prostor 7,1 kW, maks. vanjski otpor 125 Pa.",
            "2  Žaluzine zadovoljavaju: usis 500 × 700 (Δp≈16 Pa) + izlaz 600 × 600 (≈15 Pa) + kanal < 125 Pa.",
            "3  Ventilator 1200 m³/h je DOPUNSKA ventilacija (min. 120 m³/h); protok hlađenja daje ventilator hladnjaka.",
            "4  Izduv DN 65 usvojen (NO 50 zadovoljava protutlak, ali radi pri 33 m/s).",
            "5  Pod je dimenzionisan na 10,00 kN/m² ravnomjerno raspodijeljeno (projekat lokacije, 4.4.2.3).",
            "    Agregat 3,93 i pun spremnik 9,2 kN/m² su KONCENTRISANI — roštilj za raznošenje je OBAVEZAN.",
            "6  RASPORED: usis JUG (+0,30), kanal/izlaz i izduv ZAPAD, oduška SJEVER, ventilator ISTOK;",
            "    ≥3 m između usisa, izduva i oduške. Ništa ne izbacuje prema ormarima na SJEVERU.",
            "7  UNOS: skid 620 mm kroz vrata 900 mm. Kontejner je PRAZAN.",
        ])
        return doc

    # ------------------------------------------------------------------ E-01
    def sheet_e01():
        SC = 50
        doc = new_doc()
        msp = doc.modelspace()
        draw_frame(msp, SC, naziv="Jednopolna shema — hibridni sistem napajanja",
                   broj="E-01", razmjera="—")
        L = "Sema"

        def box(x, y, w, h, label, sub="", color=7):
            rect(msp, x, y, w, h, L, color=color, lw=50)
            _txt(msp, label, x + w / 2, y + h / 2 + (150 if sub else -80),
                 2.2 * SC, layer="Tekst", color=7, align=TA.MIDDLE_CENTER)
            if sub:
                _txt(msp, sub, x + w / 2, y + h / 2 - 330, 1.8 * SC,
                     layer="Tekst", color=8, align=TA.MIDDLE_CENTER)
            return (x + w, y + h / 2), (x, y + h / 2)

        def wire(a, b, color=7):
            pts = [a, b] if abs(a[1] - b[1]) < 1 else [a, (b[0], a[1]), b]
            msp.add_lwpolyline(pts, dxfattribs={"layer": L, "color": color,
                                                "lineweight": 35})

        Y = 10200
        # 12 modules wired as 2 strings of 6, not 3 of 4: the priced PVDB500-15-2B
        # has two outputs, and 6 x 51,55 V = 309 V Voc sits inside the iSSU's
        # 85-435 V window. A string therefore spans two supports.
        s1r, _ = box(1600, Y - 700, 2900, 1300, "STRING 1", "6 × 585 Wp = 3,51 kWp", 5)
        s2r, _ = box(1600, Y - 3500, 2900, 1300, "STRING 2", "6 × 585 Wp = 3,51 kWp", 5)
        _txt(msp, "nosači PV-1 + PV-2", 1600, Y - 900, 1.8 * SC,
             layer="Tekst", color=8)
        _txt(msp, "nosači PV-2 + PV-3", 1600, Y - 3700, 1.8 * SC,
             layer="Tekst", color=8)
        spd1r, spd1l = box(5500, Y - 700, 1900, 1300, "SPD DC", "tip 2 · string 1", 1)
        spd2r, spd2l = box(5500, Y - 3500, 1900, 1300, "SPD DC", "tip 2 · string 2", 1)
        pvdbr, pvdbl = box(8400, Y - 2100, 2500, 1300, "PVDB",
                           "500-15-2B · IP55 · 2 rute", 5)
        issur, issul = box(11900, Y - 2100, 2600, 1300, "iSSU", "S4875G2 · MPPT", 30)
        wire(s1r, spd1l, 5)
        wire(s2r, spd2l, 5)
        wire(spd1r, (pvdbl[0], pvdbl[1] + 300), 5)
        wire(spd2r, (pvdbl[0], pvdbl[1] - 300), 5)
        wire(pvdbr, issul, 5)

        gr, _ = box(1600, Y - 6200, 2900, 1300, "DEA 22 kVA", "17,6 kW · skid", 30)
        atsr, atsl = box(5500, Y - 6200, 1900, 1300, "KOA / ATS", "sklopka izvora", 30)
        grol, gror = box(8400, Y - 6200, 2500, 1300, "GRO",
                         "sekcije AGREGAT / SOLAR", 30)
        wire(gr, atsl, 30)
        wire(atsr, gror if False else (8400, Y - 5550), 30)
        box(8400, Y - 4300, 2500, 800, "SPD AC  tip 1+2", "", 1)
        msp.add_lwpolyline([(9650, Y - 4900), (9650, Y - 4300)],
                           dxfattribs={"layer": L, "color": 1, "lineweight": 35})

        rectr, rectl = box(11900, Y - 6200, 2600, 1300, "ISPRAVLJAČI",
                           "R4875 · −48 V DC", 30)
        wire((10900, Y - 5550), rectl, 30)
        battr, battl = box(15900, Y - 6200, 2500, 1300, "BATERIJA", "LFP  −48 V", 5)
        dcr, dcl = box(15900, Y - 1100, 2500, 1300, "DC RAZVOD",
                       "potrošači 1,18 kW", 7)
        wire(issur, dcl, 30)
        wire(rectr, battl, 30)
        msp.add_lwpolyline([(17150, Y - 4900), (17150, Y - 1100)],
                           dxfattribs={"layer": L, "color": 7, "lineweight": 50})

        msp.add_lwpolyline([(1600, Y - 7600), (18400, Y - 7600)],
                           dxfattribs={"layer": "Uzemljenje", "color": 2,
                                       "lineweight": 70})
        for x in (3050, 9650, 13200, 17150):
            msp.add_lwpolyline([(x, Y - 7600), (x, Y - 7100)],
                               dxfattribs={"layer": "Uzemljenje", "color": 2})
        _txt(msp, "postojeći prstenasti uzemljivač Fe/Zn 25×4 · R ≤ 10 Ω · nosači FN "
                  "vezani bakrenim užetom 50 mm² preko bimetalnih spojeva",
             1600, Y - 8100, 2.0 * SC, layer="Tekst", color=8)

        note_block(msp, 1600, Y - 8900, SC, "NAPOMENE:", [
            "1  Lokacija NIJE na mreži — DEA je jedini AC izvor; KOA/ATS je sklopka izvora, ne prebacivanje sa mreže.",
            "2  Uzemljenje otočnog izvora TN-S: tačka spajanja N-PE u novom GRO, ne u postojećem PMO.",
            "3  Prenaponska zaštita: AC tip 1+2 (objekat ima LPS), DC tip 2 po stringu, signalni vodovi EN 61643-21.",
            "4  Zaštita u GRO mora isključiti prema IEC 60364-4-41 pri struji kvara ograničenoj pobudom generatora.",
            "5  FN polja su unutar zone zaštite antenskog stuba h=38 m (EN 62305).",
            "6  12 modula = 2 stringa × 6 (na 3 nosača × 4); PVDB ima 2 rute, po jedan DC odvodnik po stringu.",
        ])
        return doc

    return {"S-02": sheet_s02, "S-03": sheet_s03, "M-01": sheet_m01,
            "E-01": sheet_e01}
