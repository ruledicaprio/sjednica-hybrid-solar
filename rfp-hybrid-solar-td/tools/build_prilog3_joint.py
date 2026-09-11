# -*- coding: utf-8 -*-
"""
Prilog III of the joint tender: one annex, two site blocks.

    cover (joint)
    A. BS Sjednica  - pages 2-16 of the Sjednica Rev 9 annex, unchanged
                      (photo, site data, S-01..E-01, the seven K2 sheets, INFO-02)
    B. BS Hamzići   - photos, site data, H-01..H-05, sheets of the certified
                      2017 project (as reference), INFO-02 from the pvsim run

The Sjednica block is taken as built (tools/build_prilog3.py in its folder),
so the two annexes cannot drift apart. The Hamzići pages are built here from
hamzici-hybrid-solar/cad/design.json, its review/pvsim/ and its drawings.
"""
import hashlib
import json
import os
import sys

import fitz

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import paths                                                        # noqa: E402

SJ = paths.SITES["sjednica"]["folder"]
HZ = paths.SITES["hamzici"]["folder"]
sys.path.insert(0, os.path.join(SJ, "tools"))
import build_prilog3 as bp3                                         # noqa: E402

SJ_ANNEX = bp3.OUT            # Sjednica Rev 9 Prilog III (16 pages)
HZ_PROJECT = os.path.join(HZ, "GP BS HAMZIĆI_Čitluk K2 i AS 36 m")
_AG = os.path.join(HZ_PROJECT, "4 - ARHITEKTONSKO GRADJEVINSKI DIO", "6 Graficki dio")
CERTIFIED = [
    (os.path.join(_AG, "461 Graficki dio TEMELJ i OGRADA", "01_Situacija 1_200.dwg"),
     "Situacija 1:200"),
    (os.path.join(_AG, "461 Graficki dio TEMELJ i OGRADA", "04_Ograda.dwg"), "Ograda"),
    (os.path.join(_AG, "462 Graficki dio ANTENSKI STUB 32 m", "01_Dispozicija S32 m.dwg"),
     "Dispozicija antenskog stuba S32"),
    (os.path.join(_AG, "463 Graficki dio OBJEKAT", "01 Osnova.dwg"), "Kontejner K2 — osnova"),
    (os.path.join(_AG, "463 Graficki dio OBJEKAT", "04 Fasade.dwg"), "Kontejner K2 — fasade"),
    (os.path.join(HZ_PROJECT, "5_ELEKTRO INSTALACIJE", "Graficki dio",
                  "3.6.9  Plan uzemljivača objekta.dwg"), "Plan uzemljivača objekta"),
]
PHOTOS = [("20260908_121209_sunce.jpg", "Antenski stub i kontejner; pogled prema jugu-jugoistoku"),
          ("20260908_121141_sunce.jpg", "Kontejner sa klima-uređajem Stulz WDE80 (demontira se)")]
H_SHEETS = ["H-01", "H-02", "H-03", "H-04", "H-05"]
ORANGE, GREY, INK = (0.96, 0.51, 0.12), (0.35, 0.35, 0.35), (0.04, 0.04, 0.04)


def r10(v):
    return int(v / 10 + 0.5) * 10


def num(v, nd=0):
    return f"{v:,.{nd}f}".replace(",", " ").replace(".", ",")


def fonts(page):
    have = {}
    for tag, fname in (("bht", "arial.ttf"), ("bhtb", "arialbd.ttf")):
        p = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", fname)
        if os.path.exists(p):
            page.insert_font(fontname=tag, fontfile=p)
            have[tag] = True
    return ("bht" if "bht" in have else "helv"), ("bhtb" if "bhtb" in have else "hebo")


def line(page, font, txt, y, size, colour=INK, x0=50, x1=545, align=1):
    if page.insert_textbox(fitz.Rect(x0, y, x1, y + size * 3.4), txt, fontname=font,
                           fontsize=size, color=colour, align=align) < 0:
        raise SystemExit(f"Prilog III: {txt[:50]!r} nije stalo")


# --------------------------------------------------------------------------
def cover(doc):
    page = doc.new_page(width=595, height=842)
    svg = fitz.open(bp3.LOGO_SVG)
    logo = fitz.open("pdf", svg.convert_to_pdf())
    w = 52 * logo[0].rect.width / logo[0].rect.height
    page.show_pdf_page(fitz.Rect(60, 50, 60 + w, 50 + 52), logo, 0)
    reg, bold = fonts(page)
    line(page, bold, "BH TELECOM d.d. SARAJEVO", 120, 13)
    line(page, reg, "Izvršna direkcija za tehnologiju i razvoj servisa", 140, 10, GREY)
    page.draw_line(fitz.Point(50, 168), fitz.Point(545, 168), color=ORANGE, width=1.6)
    line(page, bold, "TENDERSKA DOKUMENTACIJA ZA NABAVKU", 210, 14)
    line(page, bold, "INFRASTRUKTURA I INSTALACIJA OPREME ZA AUTONOMNI HIBRIDNI SISTEM "
                     "NAPAJANJA SJEDNICA, BILEĆA I HAMZIĆI, ČITLUK (LOT 1 i 2)", 250, 13)
    line(page, reg, "PROVOĐENJEM NABAVKE PUTEM PREGOVARAČKOG POSTUPKA NABAVKE SA OBJAVOM "
                    "OBAVJEŠTENJA", 330, 10, GREY)
    page.draw_rect(fitz.Rect(90, 400, 505, 500), color=ORANGE, width=1.2)
    line(page, bold, "PRILOG III", 418, 20)
    line(page, reg, "SITUACIJE, DISPOZICIJA OPREME I GRAFIČKI PRILOZI (NACRTI)", 452, 11)
    line(page, bold, "Lokacije", 545, 10)
    line(page, reg, "A.  BS Sjednica, Bileća — 42,9448° N · 18,3236° E · 1076 m n.v.", 563, 10)
    line(page, reg, "B.  BS Hamzići, Čitluk — 43,2880° N · 17,6248° E · 493 m n.v.", 581, 10)
    line(page, bold, "Sarajevo, septembar 2026. godine", 700, 11)


def separator(doc, letter, site, place, contents):
    page = doc.new_page(width=595, height=842)
    reg, bold = fonts(page)
    page.draw_line(fitz.Point(50, 300), fitz.Point(545, 300), color=ORANGE, width=1.6)
    line(page, bold, f"{letter}.  BS {site.upper()} ({place.upper()})", 320, 20)
    y = 380
    for row in contents:
        line(page, reg, row, y, 10, GREY)
        y += 18


def photo_page(doc):
    page = doc.new_page(width=595, height=842)
    reg, bold = fonts(page)
    page.insert_textbox(fitz.Rect(40, 36, 555, 56), "BH TELECOM d.d. SARAJEVO   |   BS HAMZIĆI "
                        "(ČITLUK)   |   PRILOG III", fontname=reg, fontsize=8, color=GREY)
    page.insert_textbox(fitz.Rect(40, 58, 555, 80), "Fotografije postojećeg stanja lokacije, "
                        "08.09.2026.", fontname=bold, fontsize=12)
    y = 90
    for name, caption in PHOTOS:
        path = os.path.join(HZ, "review", "pvsim", "photo", name)
        pix = fitz.Pixmap(path)
        w = 515
        h = w * pix.height / pix.width
        if h > 330:
            h = 330
            w = h * pix.width / pix.height
        x0 = (595 - w) / 2
        page.insert_image(fitz.Rect(x0, y, x0 + w, y + h), filename=path)
        page.insert_textbox(fitz.Rect(40, y + h + 4, 555, y + h + 30), caption,
                            fontname=reg, fontsize=8.5, color=GREY, align=1)
        y += h + 40


def table_page(doc, title, rows, note):
    """A titled two-column data page, rows sized to their text (the same layout
    as the Sjednica site-data page)."""
    page = doc.new_page(width=595, height=842)
    reg, bold = fonts(page)
    page.insert_textbox(fitz.Rect(50, 60, 545, 90), title, fontname=bold, fontsize=14)
    page.draw_line(fitz.Point(50, 92), fitz.Point(545, 92), color=ORANGE, width=1.6)
    x0, x1, x2, size = 50, 195, 545, 8.5
    scratch = fitz.open()
    probe = scratch.new_page(width=595, height=842)
    preg, _ = fonts(probe)

    def height_for(txt):
        for h in range(24, 108, 11):
            if probe.insert_textbox(fitz.Rect(x1 + 7, 6, x2 - 4, h), txt, fontname=preg,
                                    fontsize=size) >= 0:
                return h
        raise SystemExit(f"{title}: red ne stane — {txt[:60]!r}")

    y = 115
    for label, value in rows:
        h = height_for(value)
        page.draw_rect(fitz.Rect(x0, y, x2, y + h), color=(0.75, 0.75, 0.75), width=0.6)
        page.draw_line(fitz.Point(x1, y), fitz.Point(x1, y + h), color=(0.75, 0.75, 0.75),
                       width=0.6)
        for rect, txt, font in ((fitz.Rect(x0 + 7, y + 6, x1 - 4, y + h), label, bold),
                                (fitz.Rect(x1 + 7, y + 6, x2 - 4, y + h), value, reg)):
            if page.insert_textbox(rect, txt, fontname=font, fontsize=size) < 0:
                raise SystemExit(f"{title}: {txt[:50]!r} nije stalo")
        y += h
    scratch.close()
    page.insert_textbox(fitz.Rect(x0, y + 14, x2, y + 100), note, fontname=reg,
                        fontsize=7.6, color=(0.25, 0.25, 0.25))


def hamzici_data(doc):
    d = json.load(open(os.path.join(HZ, "cad", "design.json"), encoding="utf-8"))
    e, g = d["energy"], d["genset"]
    rows = [
        ("Investitor", "BH Telecom d.d. Sarajevo, Franca Lehara 7, 71000 Sarajevo"),
        ("Objekat", "Bazna stanica HAMZIĆI"),
        ("Općina", "Čitluk"),
        ("Koordinate", "43,2880° N,  17,6248° E"),
        ("Nadmorska visina", "493 m (projekat lokacije: 500 m)"),
        ("Zakupljena površina", "150 m² (12,00 × 12,50 m), k.č. 109/1 K.O. Hamzići (novi premjer)"),
        ("Betonski temelj", "5,40 × 5,40 m, sa metalnom ogradom visine 1,80 m; kapija 1,30 m na "
                            "sjeveru"),
        ("Antenski stub", "Rešetkasta izvedba, visina 32 m; baza 3,70 × 3,70 m; platforma na "
                          "+3,0 m iznad krova kontejnera"),
        ("Kontejner", "K2, vanjske dimenzije 3,005 × 2,30 m, zidni paneli 60 mm; vrata na "
                      "sjeveru; PRAZAN (bez GRO i instalacija)"),
        ("Klima-uređaj", "Stulz WDE80 (8 kW) na istočnom zidu — demontira se i odvozi u "
                         "skladište BH Telecom, Alipašino Polje"),
        ("Priključak na EES", "NE — priključak projektovan 2017. godine nije izveden"),
        ("Snaga potrošača", "1.180 W nazivno / 1.330 W maksimalno — privremeno, do izmjerene "
                            "potrošnje"),
        ("Sistem napajanja", "Hibridni: FN moduli (primarni) + LFP baterije + DEA (rezervni), "
                             "isti kao na lokaciji Sjednica"),
        ("FN konfiguracija", "12 × iPV585-M2A (7,02 kWp), fiksni nagib 45°, azimut 180° (jug); "
                             "monofacijalni iPV moduli sa optimizatorima"),
        ("DEA", f"{g['kVA']:g} kVA / {num(g['kW'], 1)} kW stand-by (ISO 8528-3), rad u prime "
                f"režimu, ulaz ispravljača ograničen na 9,5 kW; skid izvedba u kontejneru"),
        ("Spremnik goriva", "Dvoplašni, 500 l, sa nivo sondom i detekcijom curenja"),
        ("Očekivani rad DEA", f"≈{r10(e['genset_h_mean'])} h/god (9 od 10 godina "
                              f"≤{r10(e['genset_h_p90'])} h), gorivo ≈{r10(e['fuel_l_mean'])} "
                              f"l/god — simulacija pvsim, uz parametriranje SMU iz Priloga I, "
                              f"Tačka 4.6"),
        ("Orijentacija", "vrata i kapija na sjeveru, malo prema sjeverozapadu (fotografije "
                         "08.09.2026.); ovjereni crtež iz 2017. je zakrenut ≈180°"),
    ]
    note = ("Napomena: podaci preuzeti iz ovjerenog projekta lokacije GP-BS-10472-291 (2017), "
            "fotografija lokacije od 08.09.2026. i odluka Naručioca od 11.09.2026. "
            "Konstruktivni podaci kontejnera: opterećenje poda 10,00 kN/m² (AG dio, tačka "
            "4.4.2). DEA kao FG Wilson P18-6 (Skid) (motor Perkins 404D-22G1) ili ekvivalent.")
    table_page(doc, "1.  OPŠTI PODACI O LOKACIJI — BS HAMZIĆI", rows, note)


def info_pv(doc, base, header, t):
    """INFO-02 for one site, from its review/pvsim (the Sjednica block carries its own)."""
    kp = os.path.join(base, "review", "pvsim", "kpis.json")
    raw = open(kp, "rb").read()
    d = json.loads(raw.decode("utf-8"))
    k, v, c = d["tilts"][t]["kpis"], d["validation"][t], d["inputs"]["control"]
    fig = os.path.join(base, "review", "pvsim", "fig")
    page = doc.new_page(width=1190.55, height=841.89)
    reg, bold = fonts(page)
    page.insert_text(fitz.Point(40, 40), f"BH TELECOM d.d. SARAJEVO   |   {header}   |   "
                     "PRILOG III", fontname=reg, fontsize=9, color=GREY)
    page.insert_text(fitz.Point(40, 68), "FN simulacija — proizvodnja i energetski bilans "
                     "(informativno)", fontname=bold, fontsize=17, color=INK)
    page.draw_line(fitz.Point(40, 78), fitz.Point(1150, 78), color=ORANGE, width=1.6)
    page.insert_image(fitz.Rect(40, 92, 585, 392), filename=os.path.join(fig, f"f1_bilans_t{t}.png"))
    page.insert_image(fitz.Rect(605, 92, 1150, 432),
                      filename=os.path.join(fig, f"f4_dea_godine_t{t}.png"))
    rows = [
        ("Polje", f"12 × iPV585-M2A = 7,02 kWp, nagib {t}°, azimut 180° (jug)"),
        ("FN na DC sabirnici (−48 V)", f"{num(k['pv_bus_kwh'])} kWh/god · "
                                       f"{num(k['specific_yield_bus'])} kWh/kWp"),
        ("Potrošnja", f"{num(k['load_kwh'])} kWh/god (1180 W + hlađenje ormara i pomoćna "
                      f"potrošnja)"),
        ("Decembar", f"FN {num(k['dec_pv_kwh'])} kWh prema potrošnji {num(k['dec_load_kwh'])} kWh"),
        ("Solarni udio u potrošnji", f"{num(100 * k['solar_fraction'], 1)} %"),
        ("Rad DEA", f"prosjek {num(k['genset_h_mean'])} h/god · 9 od 10 godina "
                    f"≤{num(k['genset_h_p90'])} h · najviše {num(k['genset_h_max'])} h"),
        ("Gorivo", f"prosjek {num(k['fuel_l_mean'])} l/god · dopuna spremnika 500 l "
                   f"{num(k['refills_mean'], 1)} puta godišnje"),
        ("Nepokrivena potrošnja", f"{num(k['unmet_kwh_total'])} kWh u {k['n_years']} godina"),
        ("Provjera prema PVGIS-u", f"PVcalc {num(v['pvcalc_E_y'])} kWh/god, pvsim sa istim "
                                   f"gubicima {num(v['pvsim_E_y'])} kWh/god; najveće mjesečno "
                                   f"odstupanje {num(100 * v['worst_month_dev'], 1)} %"),
    ]
    x0, x1, x2, y = 40, 250, 800, 452
    for label, value in rows:
        page.draw_rect(fitz.Rect(x0, y, x2, y + 24), color=(0.75, 0.75, 0.75), width=0.6)
        page.draw_line(fitz.Point(x1, y), fitz.Point(x1, y + 24), color=(0.75, 0.75, 0.75),
                       width=0.6)
        for rect, txt, font in ((fitz.Rect(x0 + 6, y + 6, x1 - 4, y + 24), label, bold),
                                (fitz.Rect(x1 + 6, y + 6, x2 - 4, y + 24), value, reg)):
            if page.insert_textbox(rect, txt, fontname=font, fontsize=9) < 0:
                raise SystemExit(f"INFO-02: {txt[:50]!r} nije stalo")
        y += 24
    note = (f"Satna simulacija energetskog bilansa na −48 V DC sabirnici za "
            f"{k['years'][0]}–{k['years'][1]} (pvlib + PVGIS-SARAH3), uz parametriranje SMU iz "
            f"Priloga I, Tačka 4.6: start pri DOD {num(100 * c['dod_start'])} %, zaustavljanje "
            f"pri SoC {num(100 * c['soc_stop'])} %, ograničenje ispravljača 9,5 kW. Bez "
            f"zasjenjenja stablom JJI–JI; sa stablom rad DEA raste za 5–23 h/god. Metoda, "
            f"gubici, osjetljivost i pretpostavke: proračuni lokacije, dio A.6. Vrijednosti su "
            f"informativne. Izvor: review/pvsim/kpis.json (sha256 "
            f"{hashlib.sha256(raw).hexdigest()[:12]}, pvsim commit {d['git_commit']}).")
    page.insert_textbox(fitz.Rect(820, 452, 1150, 700), note, fontname=reg, fontsize=8.5,
                        color=GREY)
    page.draw_rect(fitz.Rect(1030, 760, 1150, 800), color=INK, width=0.8)
    page.insert_textbox(fitz.Rect(1030, 770, 1150, 800), "INFO-02", fontname=bold,
                        fontsize=14, align=1)


def certified_sheets(doc):
    names, tmp = bp3.to_dxf([p for p, _ in CERTIFIED])
    for src, caption in CERTIFIED:
        pdf = os.path.join(tmp, os.path.basename(names[src])[:-4] + ".pdf")
        bp3.plot_a3(names[src], pdf, crop=False)
        sheet = fitz.open(pdf)
        page = sheet[0]
        reg, bold = fonts(page)
        box = fitz.Rect(page.rect.width - 470, 12, page.rect.width - 14, 52)
        page.draw_rect(box, color=ORANGE, fill=(1, 1, 1), width=1.0)
        page.insert_textbox(fitz.Rect(box.x0 + 6, box.y0 + 4, box.x1 - 6, box.y1),
                            f"{caption} — preuzeto iz ovjerenog projekta GP-BS-10472-291 (2017), "
                            f"samo kao podloga. Strelica sjevera na crtežima iz 2017. zakrenuta "
                            f"je ≈180° prema stanju na terenu (vidi H-01).",
                            fontname=reg, fontsize=7.5, color=INK)
        doc.insert_pdf(sheet)
        print(f"  certified: {caption}")
    return tmp


def main():
    if not os.path.exists(SJ_ANNEX):
        raise SystemExit(f"Sjednica annex missing: {SJ_ANNEX}")
    missing = [s for s in H_SHEETS
               if not os.path.exists(os.path.join(HZ, "TD-OUTPUT", "grafika", s + ".pdf"))]
    if missing:
        raise SystemExit(f"Hamzići drawings missing: {missing} - run cad/build_hamzici.py")
    sj = fitz.open(SJ_ANNEX)
    out = fitz.open()
    cover(out)
    separator(out, "A", "Sjednica", "Bileća",
              ["fotografija lokacije · opšti podaci", "S-01 postojeće stanje · S-02 buduće stanje",
               "S-03 presjek · M-01 agregat u kontejneru · E-01 jednopolna šema",
               "listovi ovjerenog projekta kontejnera K2 · INFO-02 energetski bilans"])
    out.insert_pdf(sj, from_page=1, to_page=sj.page_count - 1)
    separator(out, "B", "Hamzići", "Čitluk",
              ["fotografije lokacije · opšti podaci",
               "H-01 postojeće stanje · H-02 buduće stanje · H-03 presjek",
               "H-04 agregat u kontejneru · H-05 jednopolna šema novog GRO",
               "listovi ovjerenog projekta lokacije (2017) · INFO-02 energetski bilans"])
    photo_page(out)
    hamzici_data(out)
    for s in H_SHEETS:
        out.insert_pdf(fitz.open(os.path.join(HZ, "TD-OUTPUT", "grafika", s + ".pdf")))
    tmp = certified_sheets(out)
    info_pv(out, HZ, "BS HAMZIĆI (ČITLUK)", "45")
    out.set_metadata({"title": "Prilog III — Situacije, dispozicija opreme i grafički prilozi",
                      "author": "BH Telecom d.d. Sarajevo",
                      "subject": "BS Sjednica (Bileća) i BS Hamzići (Čitluk) — autonomni "
                                 "hibridni sistemi napajanja"})
    out.subset_fonts()
    out.save(paths.PRILOG3, garbage=4, deflate=True, deflate_images=True, deflate_fonts=True,
             clean=True)
    n = out.page_count
    out.close()
    import shutil
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"Prilog III (joint): {n} pages, {os.path.getsize(paths.PRILOG3) / 1e6:.1f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
