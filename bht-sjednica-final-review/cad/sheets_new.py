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

        PX, PY = 2600, 5600
        ox, oy = PX + 8000 - 2750, PY + 4700 - 2750
        k = site_plan(msp, ox, oy, SC)
        cx, cy, CW, CH = k["cont"]
        F = k["fence"][2]
        px, py, pw, ph = k["parcel"]

        sup = D["support"]
        fw, proj = sup["field_w"], sup["proj"]
        # The foundations sit OUTSIDE the fence, south of it; the upper (north) part
        # of the panel oversails the fence.  At 45 deg the panel plane reaches the
        # 1.90 m fence height north of its lower edge, so that run lies south of the
        # fence (south strip is 1950 mm) and the rest oversails.  See
        # review/07-calculations.md F.6 and review/05-site-corrections.md.
        run_to_fence = (1900.0 - D["array"]["bottom_edge"]) / math.tan(
            math.radians(D["array"]["tilt_deg"]))
        ay = oy - run_to_fence
        mid = ox + F / 2
        gap = 500
        total_w = 3 * fw + 2 * gap
        axs = [mid - total_w / 2 + i * (fw + gap) for i in range(3)]

        for i, ax in enumerate(axs, 1):
            rect(msp, ax, ay, fw, proj, "Panel", color=110, lw=70)
            msp.add_line((ax, ay + proj / 2), (ax + fw, ay + proj / 2),
                         dxfattribs={"layer": "Panel", "color": 8})
            msp.add_line((ax + fw / 2, ay), (ax + fw / 2, ay + proj),
                         dxfattribs={"layer": "Panel", "color": 8})
            for so in (fw / 2 - sup["strip_spacing"] / 2,
                       fw / 2 + sup["strip_spacing"] / 2):
                rect(msp, ax + so - 225, ay - 250, 450, 1500,
                     "Temelj", color=32, lw=35)
            _txt(msp, f"PV-{i}  ·  4 × 585 Wp  ·  45°  JUG", ax + fw / 2,
                 ay - 900, 2.2 * SC, layer="Tekst", color=7, align=TA.CENTER)

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
        leader(msp, (mid, oy - 380), "DC trasa u PEHD Ø50 → PVDB (3 stringa, v. E-01)",
               2900, -1250, SC)
        leader(msp, (axs[0] + 400, ay - 100),
               "2 temeljne trake po nosaču (×3), 450 × 3300, razmak 1600 — IZVAN ograde",
               -2200, -900, SC)

        north_arrow(msp, 19500, 11700, 1700)
        scale_bar(msp, 1200, 4500, SC, total_m=5, step_m=1)
        legend(msp, 1200, 4150, SC, [
            (110, "LOT 1 — nosači FN panela PV-1, PV-2, PV-3 (4 × 585 Wp, 45°, JUG)"),
            (32,  "LOT 1 — AB temeljne trake 450 × 3300 mm, razmak 1600 mm"),
            (2,   "LOT 1 — DC trasa u PEHD Ø50 do PVDB"),
            (30,  "LOT 2 — DEA 22 kVA u skid izvedbi i spremnik 500 l"),
            (4,   "LOT 2 — usisna žaluzina (JUG); kanal, žaluzina i izduv (ZAPAD); ventilator (ISTOK)"),
        ])
        note_block(msp, 7900, 4150, SC, "NAPOMENA — PRORAČUNSKO OPTEREĆENJE:", [
            "Vjetar na lokaciji qp ≥ 1,20 kN/m² (udar 3 s ≈ 45 m/s), prema ovjerenoj",
            "dokumentaciji lokacije — iznad kataloškog kapaciteta standardnog nosača",
            "tipa A, stoga nosač CUSTOM IZRADA prema opterećenju iz proračuna",
            "(review/07-calculations.md F.6): sail 10,55 m²/nosaču, ULS uzgon 18,1 kN,",
            "moment 62,8 kNm — ovjerava ponuđač statičkim proračunom (Prilog II, 1.3).",
            "GEOMETRIJA: temelji IZVAN ograde (400 mm od ograde, pojas 1950 mm);",
            "gornji dio panela nadvišuje ogradu 2836 mm, na visini +4,74 m — iznad",
            "krova kontejnera. Kontejner je PRAZAN.",
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
        proj = sup["proj"]
        b, top = arr["bottom_edge"], arr["top_edge"]
        GX, GY = 3200, 5200
        msp.add_line((GX - 1400, GY), (GX + 10500, GY),
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
        _txt(msp, "S J E V E R  →", fx + 300, GY - 2000, 2.4 * SC,
             layer="Orijentacija", color=1)
        _txt(msp, "←  J U G", GX - 1100, GY - 2000, 2.4 * SC,
             layer="Orijentacija", color=1)
        _txt(msp, "ograda h=1,90 m", fx + 150, GY + 900, 2.0 * SC,
             layer="Tekst", color=8)

        note_block(msp, GX - 1300, GY + top + 2900, SC, "OBJAŠNJENJA:", [
            "1  Polje FN panela: 2 reda × 2 modula 585 Wp u portretu — širina polja 2305 mm,",
            "    dužina po nagibu 4576 mm (2 × 2278 mm), horizontalna projekcija 3236 mm pri 45°",
            "    (nepromijenjeno — isti broj redova po nagibu kao ranija izvedba 2×3).",
            "    ISPRAVLJENO (istorija): raniji nacrt je projekciju izvodio iz uzdužne grede",
            "    3656 mm (2590 mm), što nije dužina polja modula — vidjeti F.2 u proračunu.",
            "2  Dvije temeljne trake po nosaču, 450 × 3300 mm, dubina 900 mm, razmak 1600 mm,",
            "    beton C30/37 (XC4+XF3, aerant) na podlozi C12/15, armatura B500B;",
            "    dubina i armatura prema ovjerenom proračunu.",
            "3  Donja ivica podignuta na +1,50 m (bilo +0,50 m uz 2×6 izvedbu) — iskorišten",
            "    prostor dobijen manjim opterećenjem vjetra po nosaču (3×4 umjesto 2×6,",
            "    v. F.6). Gornja ivica +4,74 m, 2,84 m iznad kote ograde h=1,90 m.",
            "4  CUSTOM IZRADA prema qp ≥ 1,20 kN/m² (sail 10,55 m²/nosaču, ULS uzgon",
            "    18,1 kN, moment 62,8 kNm) — vidjeti napomenu na listu S-02 i proračun F.6.",
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

        ox, oy = 2900, 6100
        rect(msp, ox, oy, CW, CH, "Objekat", color=6, lw=50)
        rect(msp, ox + t, oy + t, CW - 2 * t, CH - 2 * t, "Objekat", color=6)
        for hx, hy, hw, hh in ((ox, oy, CW, t), (ox, oy + CH - t, CW, t),
                               (ox, oy + t, t, CH - 2 * t),
                               (ox + CW - t, oy + t, t, CH - 2 * t)):
            solid_rect(msp, hx, hy, hw, hh, "Objekat", 8)
        _txt(msp, "OSNOVA  —  kontejner je PRAZAN", ox, oy + CH + 600, 2.9 * SC,
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

        # tank in its 110 % bund against the NORTH wall
        bx, by = ox + 350, oy + CH - t - lay["W"]
        rect(msp, bx, by, lay["L"], lay["W"], "Agregat", color=1, lw=35)
        tx, ty = bx + (lay["L"] - tk["L"]) / 2, by + (lay["W"] - tk["W"]) / 2
        rect(msp, tx, ty, tk["L"], tk["W"], "Agregat", color=30, lw=35)
        _txt(msp, "spremnik 500 l, dvoplašni", tx + tk["L"] / 2, ty + tk["W"] / 2,
             1.9 * SC, layer="Tekst", color=7, align=TA.MIDDLE_CENTER)

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

        leader(msp, (ox + 2400, oy + t / 2),
               "usisna žaluzina 500 × 700 mm, JUŽNI zid, donja ivica +0,30 m "
               "(v≈3,4 m/s, Δp≈16 Pa)", 1900, -1500, SC)
        leader(msp, (ox + t / 2, dy_c),
               "kanal hladnjaka + žaluzina 600 × 600 — ZAPADNI zid",
               -600, 2600, SC)
        leader(msp, (ox + t + 90, oy + 1350),
               "izduv DN 65 uz ZAPADNI zid, iznad krova", -800, 1500, SC)
        leader(msp, (bx + lay["L"], by + lay["W"] / 2),
               f"tankvana ≥110 % (1600 × 1060, h=330 mm)", 1500, 900, SC)
        leader(msp, (ox + 2800, oy + CH),
               "odušna cijev spremnika sa plamenobranom — SJEVERNI zid, ≥3 m od izduva",
               600, 1300, SC)
        leader(msp, (ox + CW - t / 2, oy + 1900),
               "aksijalni ventilator Ø315, 1200 m³/h — ISTOČNI zid, gore",
               1400, 900, SC)
        leader(msp, (gx - 120, gy - 120),
               "čelični roštilj za raznošenje opterećenja pod skid ramom",
               -1200, -1300, SC)
        north_arrow(msp, ox + CW + 1900, oy + CH + 900, 900)
        # walls are referenced by cardinal name throughout the TD and Prilog I,
        # so name them on the plan itself
        for label, tx, ty, al in (
                ("S J E V E R", ox + CW / 2, oy + CH + 130, TA.CENTER),
                ("J U G", ox + CW / 2, oy - 300, TA.CENTER),
                ("Z A P A D", ox - 130, oy + CH / 2, TA.RIGHT),
                ("I S T O K", ox + CW + 130, oy + CH - 400, TA.LEFT)):
            _txt(msp, label, tx, ty, 2.0 * SC, layer="Orijentacija", color=1,
                 align=al)

        sxo, syo = 11200, 6100
        H = C["height"]
        rect(msp, sxo, syo, CW, H, "Objekat", color=6, lw=50)
        _txt(msp, "PRESJEK 1–1  (pogled prema SJEVERU — ZAPAD lijevo)", sxo,
             syo + H + 600, 2.9 * SC, layer="Tekst", color=7)
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
                            (sxo + 260, syo + H + 600)],
                           dxfattribs={"layer": "Ventilacija", "color": 1,
                                       "lineweight": 70})
        rect(msp, sxo + 700, syo + 1650, 400, 260, "Ventilacija", color=1, lw=35)
        _txt(msp, "prigušivač", sxo + 1180, syo + 1730, 1.6 * SC,
             layer="Tekst", color=8)
        _txt(msp, "izduv DN 65 uz ZAPADNI zid, iznad krova,", sxo - 500,
             syo + H + 1150, 1.9 * SC, layer="Tekst", color=7)
        _txt(msp, "sa hvatačem iskri — ≥3 m od usisa i odušne cijevi", sxo - 500,
             syo + H + 700, 1.9 * SC, layer="Tekst", color=8)

        # intake louvre on the SOUTH wall (in front of the section plane) - shown
        # dashed at its true x-position and height
        rect(msp, sxo + 2150, syo + 300, 500, 700, "Sakriveno", color=8)
        _txt(msp, "usisna žaluzina 500 × 700, JUŽNI zid (+0,30)", sxo + 1750,
             syo + 1250, 1.6 * SC, layer="Tekst", color=8)
        arrow([(sxo + 2400, syo + 650), (sxo + 2000, syo + 650)])

        # tank behind the section plane (NORTH wall), dashed - at 1310 mm it
        # stands above the 1020 mm genset silhouette
        rect(msp, sxo + 625, syo, tk["L"], tk["H"], "Sakriveno", color=8)
        _txt(msp, "spremnik 500 l (1050 × 600 × 1310), u tankvani uz SJEVERNI zid",
             sxo + 350, syo + tk["H"] + 130, 1.6 * SC, layer="Tekst", color=8)

        # room fan high on the EAST (right) wall
        solid_rect(msp, sxo + CW - t, syo + 1750, t, 315, "Ventilacija", 4)
        _txt(msp, "ventilator Ø315", sxo + CW - 900, syo + 1950, 1.6 * SC,
             layer="Tekst", color=8)

        dim_v(msp, syo, syo + H, sxo, SC, off=-800)

        note_block(msp, 2900, 4300, SC, "NAPOMENE — VENTILACIJA I IZDUV:", [
            "1  Podaci prema tehničkom listu proizvođača FG Wilson P22-6 (Skid), 2019-08-14:",
            "    zrak hladnjaka 1980 m³/h (33 m³/min), zrak za sagorijevanje 90 m³/h, toplota",
            "    zračena u prostor 7,1 kW, maks. vanjski otpor strujanju zraka 125 Pa.",
            "2  Tenderom zadate žaluzine ZADOVOLJAVAJU: ulaz 500 × 700 mm daje v≈3,4 m/s i",
            "    Δp≈16 Pa, izlaz 600 × 600 mm ≈15 Pa; sa kanalom ukupno ostaje unutar 125 Pa.",
            "3  Aksijalni ventilator 1200 m³/h je DOPUNSKA ventilacija prostora (min. 120 m³/h",
            "    = 6 izmjena/h) — glavni protok ostvaruje vlastiti ventilator hladnjaka kroz",
            "    limeni kanal do izlazne žaluzine.",
            "4  Izduv: USVOJEN DN 65. NO 50 zadovoljava granicu protivpritiska (≈2,6 kPa",
            "    prema 10,2 kPa), ali radi pri 33 m/s — iznad uobičajenih 30 m/s.",
            "5  Masa agregata 385 kg (mokro) na 0,96 m² = 3,93 kN/m²; pun spremnik 500 l",
            "    (1050 × 600 × 1310 mm, 170 kg prazan) ≈590 kg na 0,63 m² = 9,2 kN/m². Oba",
            "    prekoračuju projektnu nosivost poda 2,00 kN/m² — čelični roštilj/ram za",
            "    raznošenje opterećenja pod skidom I pod tankvanom je OBAVEZAN, dokazati",
            "    statičkim proračunom.",
            "6  UNOS: skid širine 620 mm prolazi kroz vrata 900 mm (zazor 280 mm) — nije",
            "    potrebno skidanje krovnog panela ni otvaranje zida. Kontejner je PRAZAN.",
            "7  RASPORED (ukrsni tok zraka JI→Z): usisna žaluzina na JUŽNOM zidu (donja ivica",
            "    +0,30 m), kanal hladnjaka i izlazna žaluzina na ZAPADNOM zidu, izduv uz",
            "    zapadni zid iznad krova; spremnik sa tankvanom ≥110 % uz SJEVERNI zid;",
            "    ventilator Ø315 na ISTOČNOM zidu gore. Ništa ne izbacuje prema vanjskim",
            "    ormarima na SJEVERU niti recirkuliše u usis (zatvara nalaz EL RED-03).",
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
        pv1r, _ = box(1600, Y, 2900, 1300, "FN POLJE PV-1", "4 × 585 Wp = 2,34 kWp", 5)
        pv2r, _ = box(1600, Y - 2200, 2900, 1300, "FN POLJE PV-2",
                      "4 × 585 Wp = 2,34 kWp", 5)
        pv3r, _ = box(1600, Y - 4400, 2900, 1300, "FN POLJE PV-3",
                      "4 × 585 Wp = 2,34 kWp", 5)
        spd1r, spd1l = box(5500, Y - 1100, 1900, 1300, "SPD DC",
                           "tip 2/string · PV1+PV2", 1)
        spd2r, spd2l = box(5500, Y - 4400, 1900, 1300, "SPD DC",
                           "tip 2/string · PV3", 1)
        pvdbr, pvdbl = box(8400, Y - 2750, 2500, 1300, "PVDB",
                           "500-15-2B · IP55 · 2 rute", 5)
        issur, issul = box(11900, Y - 2750, 2600, 1300, "iSSU", "S4875G2 · MPPT", 30)
        wire(pv1r, (spd1l[0], spd1l[1] + 200), 5)
        wire(pv2r, (spd1l[0], spd1l[1] - 200), 5)
        wire(pv3r, spd2l, 5)
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
            "1  Lokacija NIJE priključena na elektroenergetsku mrežu — DEA je jedini AC izvor,",
            "    te KOA/ATS radi kao sklopka izvora, a ne kao prebacivanje sa mreže.",
            "2  Sistem uzemljenja otočnog izvora (TN-S) definisati projektom: tačka spajanja",
            "    N-PE je u novom GRO, a ne u postojećem PMO koji više nema izvor napajanja.",
            "3  Prenaponska zaštita: tip 1+2 na AC strani (objekat ima vanjski LPS), tip 2",
            "    po stringu na DC strani, te zaštita signalnih vodova prema EN 62305-4.",
            "4  Zaštitni uređaj u GRO mora obezbijediti automatsko isključenje prema",
            "    IEC 60364-4-41 pri struji kvara ograničenoj SHUNT pobudom generatora.",
            "5  FN polja su unutar zone zaštite antenskog stuba h=38 m prema EN 62305.",
            "6  3 nosača × 4 modula (v. S-02/S-03, F.6): svaki string kompletan po nosaču",
            "    (bez dijeljenja stringa preko dva nosača). PVDB ima 2 rute — PV-1+PV-2",
            "    paralelno na rutu 1, PV-3 samostalno na rutu 2.",
        ])
        return doc

    return {"S-02": sheet_s02, "S-03": sheet_s03, "M-01": sheet_m01,
            "E-01": sheet_e01}
