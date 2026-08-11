# -*- coding: utf-8 -*-
"""
Builds `3. Prilog I TD - Specifikacija zahtjeva.docx`.

A new document, so there is no template to preserve - it is generated with
python-docx in BH Telecom's house style (Arial, orange headings, the corporate
mark in the header).

Content follows the structure the Investor supplied, corrected against the
verified data in review/07-calculations.md. Where the supplied draft conflicted
with measured values it is corrected here and the correction is listed in
section 0 so the change is visible rather than silent.
"""
import os
import sys
import zipfile

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "TD-OUTPUT", "3. Prilog I TD - Specifikacija zahtjeva.docx")
LOGO_SRC = os.path.join(BASE, "TD-OUTPUT", "3. TD JN Hibridni sistem napajanja BS Sjednica.docx")
FIG = os.path.join(BASE, "EQUIPEMENT", "GENSET", "render")  # tools/render_equipment.py

ORANGE = RGBColor(0xF5, 0x82, 0x1F)
GREY = RGBColor(0x59, 0x59, 0x59)


def extract_logo():
    """Pull the BH Telecom header image out of an existing tender document."""
    z = zipfile.ZipFile(LOGO_SRC)
    for n in z.namelist():
        if n.startswith("word/media/") and z.getinfo(n).file_size > 50000:
            p = os.path.join(os.environ.get("TEMP", "."), "bht_header.png")
            open(p, "wb").write(z.read(n))
            return p
    return None


def style(doc):
    n = doc.styles["Normal"]
    n.font.name = "Arial"
    n.font.size = Pt(9.5)
    n._element.rPr.rFonts.set(qn("w:eastAsia"), "Arial")
    n.paragraph_format.space_after = Pt(4)
    for i, sz in ((1, 14), (2, 11.5), (3, 10)):
        h = doc.styles[f"Heading {i}"]
        h.font.name = "Arial"
        h.font.size = Pt(sz)
        h.font.bold = True
        h.font.color.rgb = ORANGE if i == 1 else GREY
        h.paragraph_format.space_before = Pt(10 if i == 1 else 7)
        h.paragraph_format.space_after = Pt(3)
    ti = doc.styles["Title"]
    ti.font.name = "Arial"
    ti.font.size = Pt(15)
    ti.font.bold = True
    ti.font.color.rgb = ORANGE
    ti.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    ti.paragraph_format.space_after = Pt(2)
    su = doc.styles["Subtitle"]
    su.font.name = "Arial"
    su.font.size = Pt(13)
    su.font.bold = True
    su.font.color.rgb = RGBColor(0, 0, 0)
    su.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    su.paragraph_format.space_after = Pt(4)


def shade(cell, hexcolor):
    el = OxmlElement("w:shd")
    el.set(qn("w:fill"), hexcolor)
    cell._tc.get_or_add_tcPr().append(el)


def table(doc, headers, rows, widths=None):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    trPr = t.rows[0]._tr.get_or_add_trPr()
    hdr = OxmlElement("w:tblHeader")
    hdr.set(qn("w:val"), "true")
    trPr.append(hdr)
    for i, h in enumerate(headers):
        c = t.rows[0].cells[i]
        c.text = ""
        r = c.paragraphs[0].add_run(h)
        r.bold = True
        r.font.size = Pt(8.5)
        shade(c, "F2F2F2")
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""
            run = cells[i].paragraphs[0].add_run(str(v))
            run.font.size = Pt(8.5)
    if widths:
        for r in t.rows:
            for i, w in enumerate(widths):
                r.cells[i].width = Cm(w)
    doc.add_paragraph()
    return t


def para(doc, text, bold=False, size=9.5, italic=False, space=4):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space)
    r = p.add_run(text)
    r.bold = bold
    r.italic = italic
    r.font.size = Pt(size)
    return p


def warning(doc, text, size=9.5):
    """Shaded, left-bordered callout paragraph for normative warnings -- replaces
    ad hoc bold=True paragraphs so callouts are visually distinct from headings
    and emphasized body text, not just bold."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(6)
    pPr = p._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), "FCEEDD")
    pPr.append(shd)
    pBdr = OxmlElement("w:pBdr")
    left = OxmlElement("w:left")
    left.set(qn("w:val"), "single")
    left.set(qn("w:sz"), "18")
    left.set(qn("w:space"), "4")
    left.set(qn("w:color"), "F5821F")
    pBdr.append(left)
    pPr.append(pBdr)
    p.paragraph_format.left_indent = Pt(8)
    r = p.add_run(text)
    r.bold = True
    r.font.size = Pt(size)
    return p


def add_field(paragraph, instr, font_size=None, color=None):
    """Insert a Word field (e.g. PAGE, NUMPAGES) as a run sequence."""
    def _run():
        r = paragraph.add_run()
        if font_size:
            r.font.size = font_size
        if color:
            r.font.color.rgb = color
        return r

    r1 = _run()
    fb = OxmlElement("w:fldChar")
    fb.set(qn("w:fldCharType"), "begin")
    r1._r.append(fb)
    r2 = _run()
    it = OxmlElement("w:instrText")
    it.set(qn("xml:space"), "preserve")
    it.text = instr
    r2._r.append(it)
    r3 = _run()
    fe = OxmlElement("w:fldChar")
    fe.set(qn("w:fldCharType"), "end")
    r3._r.append(fe)


def figures(doc, items):
    """Side-by-side figures in a borderless table row: items is a list of
    (png_path, width_cm, caption). Captions are centred italic 8.5 pt."""
    t = doc.add_table(rows=1, cols=len(items))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for cell, (path, width_cm, caption) in zip(t.rows[0].cells, items):
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(path, width=Cm(width_cm))
        cp = cell.add_paragraph()
        cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cp.paragraph_format.space_before = Pt(2)
        r = cp.add_run(caption)
        r.italic = True
        r.font.size = Pt(8.5)
    doc.add_paragraph()
    return t


def bullet(doc, text, size=9.5):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(text)
    r.font.size = Pt(size)
    return p


def build():
    doc = Document()
    style(doc)
    for s in doc.sections:
        s.page_width = Cm(21.0)          # A4 - python-docx defaults to US Letter
        s.page_height = Cm(29.7)
        s.top_margin = Cm(2.0)
        s.bottom_margin = Cm(1.8)
        s.left_margin = Cm(2.2)
        s.right_margin = Cm(1.8)

    logo = extract_logo()
    if logo:
        hp = doc.sections[0].header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.LEFT
        hp.add_run().add_picture(logo, width=Cm(7.2))

    fp = doc.sections[0].footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fr = fp.add_run("PRILOG I — Specifikacija zahtjeva · BS Sjednica (Bileća) · "
                    "Rev. 1, 2026 · stranica ")
    fr.font.size = Pt(7.5)
    fr.font.color.rgb = GREY
    add_field(fp, "PAGE", font_size=Pt(7.5), color=GREY)
    fr2 = fp.add_run(" od ")
    fr2.font.size = Pt(7.5)
    fr2.font.color.rgb = GREY
    add_field(fp, "NUMPAGES", font_size=Pt(7.5), color=GREY)

    # ---------------- title ------------------------------------------------
    t = doc.add_paragraph("PRILOG I TENDERSKOJ DOKUMENTACIJI", style="Title")
    t2 = doc.add_paragraph("SPECIFIKACIJA ZAHTJEVA", style="Subtitle")
    t3 = doc.add_paragraph()
    t3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r3 = t3.add_run("Autonomni hibridni sistem napajanja — bazna stanica SJEDNICA "
                    "(Bileća)\nLOT 1: nosači fotonaponskih panela · LOT 2: dizel "
                    "električni agregat u kontejneru")
    r3.font.size = Pt(10)
    r3.font.color.rgb = GREY
    doc.add_paragraph()

    para(doc, "Ovaj Prilog utvrđuje tehničke zahtjeve i dokaze koje Ponuđač dostavlja "
              "UZ PONUDU. Zahtjevi označeni kao OBAVEZNI predstavljaju uslov "
              "kvalifikacije — ponuda koja ih ne sadrži smatra se neprihvatljivom. "
              "Prilog se čita zajedno sa Prilogom II (Obrazac za cijenu ponude) i "
              "Prilogom III (Situacija, dispozicija i grafički prilozi).", size=9.5)

    # ---------------- 0. corrections ---------------------------------------
    doc.add_heading("0. Napomena o ispravkama u odnosu na raniju verziju", 1)
    para(doc, "Sljedeće vrijednosti su ispravljene u odnosu na ranije radne verzije "
              "tehničkog opisa. Ispravke su zasnovane na ovjerenom projektu lokacije, "
              "tehničkim listovima proizvođača i mjerenjima na licu mjesta.")
    warning(doc, "REDOSLIJED MJERODAVNOSTI. U slučaju neslaganja između dokumenata "
              "tenderske dokumentacije mjerodavni su, tim redom: (1) Tenderska "
              "dokumentacija (TD), (2) ovaj Prilog I, (3) Prilog II (Predmjer), "
              "(4) Prilog III (grafički prilozi i referentna dokumentacija). "
              "Prilog III sadrži i preuzete stranice ranije dokumentacije (npr. "
              "nacrte i podatke tipskog kontejnera K3, sa nosivošću poda 10,00 "
              "kN/m²) koje NISU mjerodavne za ovu nabavku — mjerodavna nosivost "
              "poda je 2,00 kN/m² prema Projektnom zadatku, a mjerodavni raspored "
              "opreme i otvora je onaj sa crteža M-01.")
    # every superseded value is prefixed "ranije:" so it is legible as a record
    # rather than a specification - both to a reader skimming one row out of
    # context and to tools/check_consistency.py, which exempts documented
    # corrections from its conflict rules
    corrections = [["Geometrija PV polja",
            "projekcija 2590 mm, gornja ivica +3,09 m",
            "projekcija 3236 mm, gornja ivica +3,74 m (v. red niže — sada +4,74 m "
            "uz 3×4 konfiguraciju)",
            "Huawei PVM Tab. 4-20; izvedeno iz polja modula, a ne iz uzdužne grede"],
           ["Visina ograde", "1,80 m", "1,90 m", "ovjereni projekat lokacije"],
           ["Kontejner",
            "3,08 × 2,20 × 2,80 m / 3,00 × 2,10 m",
            "3,005 × 2,30 m vanjski, zid 60 mm, PRAZAN",
            "ovjereni projekat (unutra 6,29 m², obim 10,13 m)"],
           ["Zrak hladnjaka DEA", "≈4250 m³/h (procjena)", "1980 m³/h",
            "FG Wilson P22-6 TDS, 2019-08-14"],
           ["Usisna žaluzina", "≥0,43 m² (1200 × 800 mm)",
            "500 × 700 mm zadovoljava (Δp≈16 Pa)",
            "proračun prema max. vanjskom otporu 125 Pa"],
           ["Ventilator prostora", "≥2400 m³/h", "1200 m³/h (dopunska ventilacija)",
            "hlađenje ostvaruje vlastiti ventilator hladnjaka"],
           ["Izduv", "DN 65 minimum", "DN 50 zadovoljava; DN 65 preporučeno",
            "protutlak ≈2,6 kPa pri granici 10,2 kPa"],
           ["Donja ivica panela", "≥1,20 m zbog snijega", "+0,50 m",
            "snijeg nije mjerodavan — vjetrom raznošena lokacija (bura)"],
           ["Snijeg", "s_k = 3,00 kN/m² mjerodavno",
            "provjera obavezna, ali nije mjerodavna",
            "iskustvo Investitora na lokaciji"],
           ["Konfiguracija nosača",
            "2 nosača, 6 modula (2×3), +0,50/+3,74 m, 15,91 m² izloženosti/nosaču",
            "3 nosača, 4 modula (2×2), +1,50/+4,74 m, 10,55 m² izloženosti/nosaču — "
            "manji presjek dozvoljava veću visinu bez povećanja opterećenja",
            "review/07-calculations.md F.6 — custom izrada, kataloški nosač ne "
            "zadovoljava ni pri ranijoj ni pri ovoj konfiguraciji"],
           ["Raspored otvora ventilacije",
            "sve na SJEVERNOJ strani kontejnera",
            "ukrsni tok: usis JUG, kanal i izduv ZAPAD, oduška SJEVER, "
            "ventilator ISTOK (Tačka 4.3)",
            "usis, izlaz i izduv na istom zidu na 1,4 m recirkulišu i griju "
            "postojeće vanjske ormare (nalaz EL RED-03)"],
           ["Spremnik goriva",
            "1200 × 700 × 800 mm (procjena)",
            "1050 × 600 × 1310 mm, 170 kg prazan / ≈590 kg pun",
            "podaci Investitora, 2026-08-11"],
           ["Nosivost poda kontejnera",
            "10,00 kN/m² prema tipskom proračunu kontejnera K3",
            "2,00 kN/m² prema Projektnom zadatku — ram za raznošenje "
            "opterećenja OBAVEZAN",
            "lokacija je kontejner tipa K2; K3 proračun nije mjerodavan"],
           ["Sistem napajanja",
            "MTS9302 / PowerCube 1000 (različito u dokumentima)",
            "Huawei ICC330-H1 + MTS9302 (postojeći vanjski ormari)",
            "ovjereni projekat lokacije i crteži S-01/S-02"],
           ["Beton temelja", "C25 na podlozi C10",
            "C30/37, XC4 + XF3, aerant 4–6 % na podlozi C12/15; armatura B500B",
            "izloženost mrazu i solima na 1076 m n.v., BAS EN 206"],
           ["Prvo punjenje gorivom", "najmanje 200 l",
            "500 l (pun spremnik)", "usklađeno sa Predmjerom, stavka 4.16"]]
    for row in corrections:
        row[1] = "ranije: " + row[1]
    table(doc, ["Stavka", "Ranije navedeno", "Ispravno (mjerodavno)", "Izvor"],
          corrections, widths=[3.2, 4.0, 4.4, 5.0])

    # ---------------- 1. site ----------------------------------------------
    doc.add_heading("1. Osnovni podaci o lokaciji", 1)
    table(doc, ["Parametar", "Vrijednost"],
          [["Lokacija", "BS Sjednica, Bileća, Republika Srpska, BiH"],
           ["Koordinate", "42,9448° N · 18,3236° E"],
           ["Nadmorska visina", "1076 m n.v."],
           ["Priključak na EES", "NE — lokacija nije priključena na elektroenergetsku mrežu"],
           ["Potrošnja", "1180 W nazivno / 1330 W maksimalno, −48 V DC"],
           ["Zakupljena parcela", "≈150 m² (16,00 × 9,40 m)"],
           ["Postojeći plato", "AB ploča 5,40 × 5,40 m, ograda h = 1,90 m, kapija 1,00 m"],
           ["Antenski stub", "rešetkasti, h = 38 m, baza 4,20 × 4,20 m"],
           ["Kontejner", "3,005 × 2,30 m vanjski, zidni paneli 60 mm, PRAZAN; "
                         "ulazna vrata 900 × 2000 mm na ISTOČNOM zidu"],
           ["Nosivost poda kontejnera", "2,00 kN/m² prema Projektnom zadatku — "
                                        "mjerodavno za dimenzionisanje rama"],
           ["Postojeći sistem napajanja",
            "Huawei ICC330-H1 + MTS9302, vanjski ormari uz SJEVERNI zid kontejnera"],
           ["Uzemljenje", "postojeći prstenasti uzemljivač Fe/Zn 25 × 4 mm"]],
          widths=[5.0, 11.6])

    doc.add_heading("1.1 Klimatski i geotehnički uslovi (MJERODAVNO)", 2)
    table(doc, ["Uticaj", "Projektna vrijednost", "Napomena"],
          [["Vjetar", "qp ≥ 1,20 kN/m² (udar 3 s ≈ 45 m/s)",
            "ovjereni projekat lokacije i BAS EN 1991-1-4 + BiH NA, sa orografijom"],
           ["Snijeg", "prema BAS EN 1991-1-3 + BiH NA",
            "provjera obavezna; nije mjerodavan zbog raznošenja vjetrom"],
           ["Led", "radijalni 20 mm, gustina 300 kg/m³", "izloženi planinski vrh"],
           ["Temperatura", "−25 °C do +50 °C", "radni opseg opreme"],
           ["Gustina zraka", "1,04–1,09 kg/m³ na 1076 m",
            "derating agregata i dimenzionisanje ventilacije"],
           ["Tlo", "kamenito (krš); nosivost ≥100 kPa",
            "Ponuđač potvrđuje geomehaničkim uvidom"],
           ["Smrzavanje", "temeljna spojnica ispod dubine smrzavanja",
            "Ponuđač navodi usvojenu dubinu"]],
          widths=[3.0, 5.4, 8.2])

    # ---------------- 2. standards -----------------------------------------
    doc.add_heading("2. Referentni standardi", 1)
    table(doc, ["Oblast", "Standardi"],
          [["Osnove proračuna", "BAS EN 1990"],
           ["Dejstva", "BAS EN 1991-1-3 (snijeg), BAS EN 1991-1-4 (vjetar), sa BiH NA"],
           ["Beton i čelik", "BAS EN 1992-1-1, BAS EN 1993-1-1, BAS EN 206, EN 10025-2, EN 10219"],
           ["Geotehnika", "BAS EN 1997-1"],
           ["Izrada čeličnih konstrukcija", "EN 1090-1, EN 1090-2 (EXC2)"],
           ["Antikorozivna zaštita", "EN ISO 1461"],
           ["Elektroinstalacije", "IEC 60364 (posebno 60364-4-41), BAS EN 60529"],
           ["Gromobranska zaštita", "EN 62305-1 do -4"],
           ["Prenaponska zaštita", "EN 61643-11, EN 61643-21"],
           ["Fotonaponski sistemi", "IEC 62548, IEC 62852"],
           ["Agregati", "ISO 8528-1, ISO 8528-3, ISO 3046-1"],
           ["Zaštita od požara", "važeći propisi RS/BiH; elaborat zaštite od požara"],
           ["Dokumentacija proizvođača",
            "Huawei PV Module Solution User Manual; Huawei GroundSupport; "
            "FG Wilson P22-6 (Skid) TDS 2019-08-14"]],
          widths=[4.4, 12.2])

    # ---------------- 3. LOT 1 ---------------------------------------------
    doc.add_heading("3. LOT 1 — Nosači fotonaponskih panela", 1)
    doc.add_heading("3.1 Konfiguracija", 2)
    table(doc, ["Parametar", "Zahtjev"],
          [["Broj nosača", "3 kom"],
           ["Moduli", "12 × 585 Wp = 7,02 kWp; 4 modula po nosaču, 2 reda × 2 stupca, portret"],
           ["Tip modula", "Huawei iPV585-M2A (2278 × 1134 × 30 mm) ili ekvivalent"],
           ["Nagib", "fiksno 45° — ZADRŽAN zbog decembarskog prinosa"],
           ["Azimut", "180° (JUG)"],
           ["Širina polja", "2305 mm (poprečna greda 2918 mm, bočni prepust 306,5 mm)"],
           ["Dužina polja po nagibu", "4576 mm (2 × 2278 mm)"],
           ["Horizontalna projekcija", "3236 mm pri 45°"],
           ["Donja / gornja ivica", "+1,50 m / +4,74 m"],
           ["Nadvišenje ograde", "2,84 m iznad kote ograde h = 1,90 m"],
           ["Površina izloženosti vjetru", "10,55 m² po nosaču"],
           ["Referentna izvedba",
            "CUSTOM IZRADA čeličnog nosača po opterećenju iz Tačke 3.2 — nijedan "
            "kataloški proizvod (npr. Huawei Standard A-shaped Support 3.0) ne "
            "zadovoljava opterećenje vjetrom na ovoj lokaciji ni pri ovoj, manjoj "
            "površini nosača"]],
          widths=[5.0, 11.6])

    para(doc, "Obrazloženje nagiba 45°: pri podnevnoj visini Sunca 23,6° na dan 21.12. "
              "i geografskoj širini 42,94°, nagib 45° ostvaruje 93 % direktnog zračenja, "
              "naspram 85 % pri 35° i 75 % pri 25°. Decembar je mjerodavni mjesec za "
              "dimenzionisanje autonomnog sistema (proizvodnja 560–600 kWh naspram "
              "potrošnje 878 kWh), zbog čega se godišnji prinos ne uzima kao kriterij.",
         italic=True, size=9)

    doc.add_heading("3.2 Projektna opterećenja konstrukcije (OBAVEZNO)", 2)
    warning(doc, "OSNOVA PRORAČUNA: kataloški nosač tipa A ima deklarisanu otpornost "
              "31 m/s (0,52 kN/m²) pri nagibu 45° i 40 m/s (0,87 kN/m²) pri 15°/25°, "
              "što je ISPOD opterećenja ovog lokaliteta — i pri punoj (2×6) i pri ovoj, "
              "manjoj (3×4) površini nosača. Zahtijeva se CUSTOM IZRADA konstrukcije "
              "dimenzionisane i dokazane za stvarno opterećenje lokaliteta (Tačka 3.1); "
              "kataloški proizvod se ne prihvata kao osnovna ponuda.")
    table(doc, ["Parametar", "Zahtjev"],
          [["Pritisak vjetra", "qp ≥ 1,20 kN/m² (udar 3 s ≈ 45 m/s)"],
           ["Koeficijent sile", "cf ≥ 1,5 pri 45° prema EN 1991-1-4 §7.3, osim uz dokaz"],
           ["Površina izloženosti vjetru", "10,55 m² po nosaču"],
           ["Sila podizanja po nosaču", "≥18,1 kN (GSN, γQ = 1,5 / γG,fav = 0,9)"],
           ["Horizontalna sila po nosaču", "≥13,4 kN (GSN)"],
           ["Moment prevrtanja po nosaču", "≥62,8 kNm (GSN)"],
           ["Mjerodavno", "podizanje (uplift) i prevrtanje, a NE nosivost tla"]],
          widths=[5.4, 11.2])

    doc.add_heading("3.3 Materijal i izrada (OBAVEZNO)", 2)
    table(doc, ["Element", "Zahtjev"],
          [["Konstrukcijski čelik", "S275JR (S355JR za stubove) prema EN 10025-2"],
           ["Profili",
            "šuplji profili prema EN 10219; stubovi min. RHS 80 × 80 × 4, rigle min. "
            "RHS 60 × 40 × 3, ili presjek sa dokazano najmanje jednakim otpornim momentom"],
           ["Antikorozivna zaštita",
            "vruće cinčanje prema EN ISO 1461, min. 70 µm lokalno / 85 µm srednje (C4)"],
           ["Zavarivanje", "EN 1090-2, klasa izvedbe EXC2; zavarivači prema EN ISO 9606-1"],
           ["Označavanje", "CE i izjava o svojstvima prema EN 1090-1"],
           ["Konstrukcijski vijci", "M16 klase 8.8, cinčani, prema EN 15048"],
           ["Pričvršćenje modula", "nehrđajući A2/A4; stezaljke za debljinu modula 30 mm"],
           ["Zaštita od krađe", "antitheft matice na stezaljkama modula"],
           ["Moment pritezanja", "prema uputstvu proizvođača (45 N·m za Huawei)"]],
          widths=[4.4, 12.2])

    doc.add_heading("3.4 Sidrenje (OBAVEZNO)", 2)
    table(doc, ["Element", "Zahtjev"],
          [["Tip", "hemijski (epoksidni/vinilesterski) anker M16 ili M20, sa ETA odobrenjem"],
           ["Materijal", "vruće cinčan ili nehrđajući A4"],
           ["Broj", "min. 2 ankera po temeljnoj traci, odnosno 4 po nosaču"],
           ["Nosivost", "karakteristična sila čupanja ≥30 kN po ankeru"],
           ["Dubina ugradnje", "prema ETA za konkretnu podlogu (beton / stijena)"],
           ["Projektna sila",
            "ukupno podizanje po nosaču ≥18,1 kN; sila po traci od momenta prevrtanja "
            "≥39,3 kN pri razmaku traka 1600 mm — ovo je mjerodavno opterećenje za "
            "sidrenje, ne ukupno podizanje"],
           ["Dokazivanje",
            "ispitivanje čupanjem na ≥10 % ugrađenih ankera, min. 2 po nosaču, do "
            "1,5 × projektne sile, uz zapisnik ovjeren od nadzornog organa"],
           ["Alternativa",
            "livena U-sidra M16/320 dozvoljena SAMO uz gravitacioni temelj ≥0,75 m³ po "
            "nosaču — momenat prevrtanja i dalje zahtijeva provjeru lokalnog istezanja "
            "trake, ne samo ukupne mase"]],
          widths=[4.0, 12.6])

    doc.add_heading("3.5 Temelji (OBAVEZNO)", 2)
    table(doc, ["Element", "Zahtjev"],
          [["Beton", "C30/37, klasa izloženosti XC4 + XF3, aerant 4–6 %, Dmax 16, S3"],
           ["Podložni beton", "C12/15, d = 50 mm"],
           ["Armatura", "B500B, zaštitni sloj ≥50 mm"],
           ["Geometrija",
            "2 trake po nosaču (×3 nosača = 6 traka ukupno), min. 450 mm široke × "
            "3300 mm duge, razmak 1600 mm, pravac SJEVER–JUG; dubina prema statičkom "
            "proračunu (≥900 mm)"],
           ["Smještaj", "IZVAN ograđenog platoa, 400 mm južno od kote ograde"],
           ["Dubina smrzavanja", "temeljna spojnica ispod dubine smrzavanja; Ponuđač navodi vrijednost"]],
          widths=[4.0, 12.6])
    para(doc, "NAPOMENA: postojeća AB ploča 5,40 × 5,40 m već postoji i NIJE predmet "
              "ovog LOT-a.", italic=True, size=9)

    doc.add_heading("3.6 Uzemljenje (LOT 1)", 2)
    for b in ["povezivanje sva tri nosača na postojeći prstenasti uzemljivač Fe/Zn 25 × 4 mm",
              "vodič: bakarno uže ≥50 mm² prema EN 62305-3, Tabela 7, otporno na UV i "
              "ukopavanje — NIJE dozvoljen H07V-K 25 mm² (unutrašnji instalacioni vodič)",
              "bimetalni (Cu/Fe-Zn) ukrsni komadi radi sprječavanja galvanske korozije",
              "kontinuitet spojeva ≤0,1 Ω; ukupni otpor uzemljenja ≤10 Ω",
              "DC kablovi na razmaku ≥0,5 m od odvoda gromobranske instalacije"]:
        bullet(doc, b)

    # ---------------- 4. LOT 2 ---------------------------------------------
    doc.add_heading("4. LOT 2 — Dizel električni agregat i instalacije", 1)
    doc.add_heading("4.1 Agregat", 2)
    table(doc, ["Parametar", "Zahtjev / referentna vrijednost"],
          [["Snaga", "22 kVA / 17,6 kW standby (20 kVA / 16 kW prime), 400/230 V, 50 Hz"],
           ["Referentni tip", "FG Wilson P22-6 (Skid) ili ekvivalent"],
           ["Motor", "Perkins 404D-22G ili ekvivalent, 4-cilindarski, 1500 o/min"],
           ["Izvedba", "skid, za ugradnju u postojeći kontejner"],
           ["Dimenzije skida", "1550 × 620 × 1020 mm (referentno)"],
           ["Masa", "378 kg suho / 385 kg mokro (referentno)"],
           ["Derating", "dokazati za 1076 m n.v. i temperaturu do +40 °C prema ISO 3046-1"],
           ["Pobuda (OBAVEZNO)",
            "nezavisna pobuda — PMG ili AREP/AUX namotaj; trajna struja kratkog spoja "
            "≥3 × In (≈95 A) u trajanju ≥10 s prema ISO 8528-3. Standardna SHUNT pobuda "
            "NIJE prihvatljiva"],
           ["Antivibracioni elementi", "sopstvena frekvencija ≤8 Hz; fleksibilni priključci"],
           ["Potrošnja goriva", "5,9 l/h pri 100 % standby → autonomija ≈85 h na 500 l"]],
          widths=[4.6, 12.0])
    figures(doc, [
        (os.path.join(FIG, "genset_side.png"), 9.2,
         "Slika 1 — Dizel električni agregat 22 kVA u skid izvedbi, "
         "bočni izgled (ilustrativno)"),
        (os.path.join(FIG, "genset_front.png"), 4.8,
         "Slika 2 — Agregat, čeoni izgled sa strane "
         "hladnjaka (ilustrativno)")])

    doc.add_heading("4.2 Spremnik goriva", 2)
    for b in ["dvoplašni, zapremine 500 l, sa sondom za detekciju curenja",
              "referentne dimenzije 1050 × 600 × 1310 mm, masa prazan 170 kg — "
              "pun ≈590 kg na 0,63 m² = 9,2 kN/m², što prekoračuje projektnu "
              "nosivost poda 2,00 kN/m²: OBAVEZAN je čelični ram/roštilj za "
              "raznošenje opterećenja i pod tankvanom, dokazan statičkim proračunom",
              "tankvana / sekundarna zaštita zapremine ≥110 % (550 l), "
              "referentno 1600 × 1060 mm, visina ruba 330 mm",
              "vanjski priključak za punjenje sa zaštitom od statičkog elektriciteta i "
              "sprječavanjem prelijevanja",
              "odušna cijev izvan kontejnera, sa plamenobranom, udaljena ≥3 m od izduva "
              "i usisa zraka",
              "protupožarni ventil na izlazu iz spremnika (topljivi osigurač ili "
              "solenoid), aktiviran požarom i E-STOP-om",
              "sifon protiv povratnog toka"]:
        bullet(doc, b)
    figures(doc, [
        (os.path.join(FIG, "tank_side.png"), 7.4,
         "Slika 3 — Spremnik goriva 500 l, bočni izgled sa pretakačkom "
         "opremom (ilustrativno)"),
        (os.path.join(FIG, "tank_top.png"), 8.6,
         "Slika 4 — Spremnik goriva 500 l, izgled odozgo sa priključcima "
         "(ilustrativno)")])

    doc.add_heading("4.3 Ventilacija i hlađenje", 2)
    para(doc, "Dimenzionisano prema tehničkom listu proizvođača. Mjerodavno ograničenje "
              "je maksimalni vanjski otpor strujanju zraka od 125 Pa, a NE brzina izmjene "
              "zraka u prostoriji.", italic=True, size=9)
    table(doc, ["Parametar", "Vrijednost"],
          [["Zrak hladnjaka", "1980 m³/h (33 m³/min) — ostvaruje vlastiti ventilator hladnjaka"],
           ["Zrak za sagorijevanje", "90 m³/h; max. otpor usisa 3 kPa"],
           ["Maks. vanjski otpor", "125 Pa (ukupno: usis + kanal + izlaz)"],
           ["Toplota u prostor", "7,1 kW"],
           ["Usisna žaluzina", "500 × 700 mm (v ≈ 3,4 m/s, Δp ≈ 16 Pa) — zadovoljava"],
           ["Kanal hladnjaka", "limeni kanal ≈6 m², od pocinčanog lima d = 1 mm"],
           ["Izlazna žaluzina", "600 × 600 mm (Δp ≈ 15 Pa) — zadovoljava"],
           ["Ventilator prostora", "1200 m³/h, Ø315, termostat, blokiran sa radom agregata"],
           ["Provjera", "Ponuđač dostavlja proračun pada pritiska ukupne putanje"]],
          widths=[4.6, 12.0])
    para(doc, "Raspored otvora (OBAVEZNO — prema crtežu M-01, Prilog III)", bold=True,
         size=9.5)
    table(doc, ["Element", "Zid i položaj"],
          [["Usisna žaluzina 500 × 700", "JUŽNI zid, istočni kraj; donja ivica "
                                         "+0,30 m od poda"],
           ["Kanal hladnjaka + izlazna žaluzina 600 × 600",
            "ZAPADNI zid, na osi radijatora agregata; kanal najkraćim putem od "
            "radijatora kroz zid"],
           ["Izduvni sistem", "uz ZAPADNI zid, završetak iznad krova (Tačka 4.4)"],
           ["Odušna cijev spremnika", "SJEVERNI zid, istočni kraj"],
           ["Ventilator prostora Ø315", "ISTOČNI zid, gore (donja ivica ≈+1,75 m), "
                                        "sjeverno od ulaznih vrata"],
           ["Minimalna razdaljina", "≥3 m prostorno između usisa zraka, izduva i "
                                    "odušne cijevi"]],
          widths=[5.6, 11.0])
    figures(doc, [
        (os.path.join(FIG, "layout_m01.png"), 16.0,
         "Slika 5 — Raspored opreme i otvora u kontejneru: ukrsni tok zraka "
         "(usis JUG → agregat → izlaz ZAPAD). Izvod iz crteža M-01, Prilog III")])
    warning(doc, "Otvori se izvode kroz ZIDNE PANELE kontejnera, a NE kroz ulazna "
              "vrata. Raspored je ukrsni (usis JUG → agregat → izlaz ZAPAD) i "
              "obavezujući: nije dozvoljeno izvesti usis, izlaz i izduv na istom "
              "zidu, niti usmjeriti izlaz toplog zraka ili izduv prema SJEVERNOJ "
              "strani, gdje se nalaze postojeći vanjski ormari ICC330-H1 i "
              "MTS9302. Svaki drugačiji raspored Ponuđač mora dokazati proračunom "
              "recirkulacije i temperaturnog uticaja i dobiti pisanu saglasnost "
              "Kupca.")

    doc.add_heading("4.4 Izduvni sistem", 2)
    table(doc, ["Parametar", "Vrijednost"],
          [["Protok izduvnih gasova", "234 m³/h (3,9 m³/min) pri 505 °C"],
           ["Maks. dozvoljeni protutlak", "10,2 kPa"],
           ["Prečnik", "DN 65 — USVOJENO (Predmjer, stavka 4.11). DN 50 zadovoljava "
                       "protutlak (≈2,6 kPa prema granici 10,2 kPa), ali radi pri "
                       "33 m/s, iznad uobičajenih 30 m/s"],
           ["Prigušivač", "industrijski; hvatač iskri obavezan"],
           ["Fleksibilni priključak", "neposredno iza motora"],
           ["Izolacija", "kamena vuna d = 50 mm + Al lim; boja otporna na 600 °C"],
           ["Trasa", "uspon uz ZAPADNI zid kontejnera (v. Tačku 4.3 i crtež M-01)"],
           ["Završetak", "iznad krova, usmjeren naviše, ≥3 m od usisa zraka i odušne cijevi"],
           ["Provjera", "Ponuđač dostavlja proračun protutlaka"]],
          widths=[4.6, 12.0])

    doc.add_heading("4.5 Elektroinstalacije i zaštita (OBAVEZNO)", 2)
    warning(doc, "KRITIČNO — POBUDA GENERATORA. Referentni agregat je u standardnoj izvedbi "
              "SHUNT pobude, za koju tehnički list proizvođača deklariše trajnu struju "
              "kratkog spoja 0 % (nezavisna pobuda PMG / AUX je opcija). Kod SHUNT pobude "
              "napon na stezaljkama se pri kvaru uruši, pobuda nestaje, a trajna struja "
              "kvara padne na ≈0,5 × In — ISPOD nazivne struje, pa ne može aktivirati "
              "nijednu prekostrujnu zaštitu. Zbog toga se zahtijeva NEZAVISNA POBUDA "
              "(PMG ili AREP/AUX) sa 3 × In u trajanju ≥10 s (Tačka 4.1), a zaštita "
              "zaštitnom strujnom sklopkom ostaje OBAVEZNA kao drugi nivo zaštite.")
    table(doc, ["Element", "Zahtjev"],
          [["Struja kvara (SHUNT)",
            "prvi poluperiod 407 A (12,8 × In, X\"d = 0,078) → prelazna 205 A "
            "(6,5 × In) → TRAJNA 16 A (0,5 × In, Xd = 1,938) — ne aktivira zaštitu"],
           ["Struja kvara (PMG/AREP)", "≥95 A (3 × In) trajno ≥10 s — ZAHTIJEVANO"],
           ["Sistem uzemljenja", "TN-S, jedinstvena tačka spajanja N i PE u novom GRO"],
           ["Glavna zaštita", "4p RCD 63 A / 300 mA, S-tip (selektivna)"],
           ["Krajnji strujni krugovi", "2 × RCBO 16 A / 30 mA, tip A (utičnice, rasvjeta)"],
           ["Nazivna struja", "In = 31,75 A pri 22 kVA / 400 V"],
           ["Sklopka izvora", "4p 63 A, položaji 1 – agregat / 0 – isključeno / 2 – rezerva"],
           ["SPD, AC strana", "tip 1 + 2 (Iimp ≥12,5 kA) — objekat ima vanjski LPS"],
           ["SPD, DC strana", "tip 2 po stringu (Iimp ≥5 kA, Ucpv ≥425 V), na PVDB i na polju"],
           ["SPD, signalni vodovi", "prema EN 61643-21 — OBAVEZNO (stub h = 38 m)"],
           ["Postojeći strujni krugovi",
            "snimiti stanje i prevezati svih 7 postojećih krugova u novi GRO; "
            "signalna rasvjeta prepreke antenskog stuba (K7) na zasebnom "
            "nadziranom krugu, sa signalizacijom ispada u sistem daljinskog "
            "nadzora"],
           ["AC kablovi", "bezhalogeni, CPR ≥ Cca-s1b,d1,a1"],
           ["DC kablovi", "H1Z2Z2-K 6 mm²; priključak na iSSU presjekom 4 mm²"],
           ["Otpor uzemljenja", "≤10 Ω"]],
          widths=[4.6, 12.0])

    doc.add_heading("4.6 Upravljanje i nadzor", 2)
    for b in ["start agregata prema stanju napunjenosti baterija (SoC), a ne prema "
              "ispadu mreže — lokacija nije priključena na EES",
              "ograničenje ulazne snage ispravljača radi sprječavanja preopterećenja agregata",
              "prijenos alarma u sistem daljinskog nadzora: rad agregata, kvar, nivo "
              "goriva, curenje goriva, požar, temperatura prostora",
              "komunikacioni modul kompatibilan sa postojećim sistemom napajanja"]:
        bullet(doc, b)

    doc.add_heading("4.7 Zaštita od požara (OBAVEZNO)", 2)
    for b in ["elaborat zaštite od požara za prostor sa 500 l dizel goriva — prije izvođenja",
              "detekcija: dimni i termički detektori; detekcija CO i NO₂",
              "automatsko gašenje sredstvom za klasu B, sa blokadom ventilacije pri aktivaciji",
              "protupožarni ventil na izlazu iz spremnika",
              "E-STOP izvan kontejnera pored ulaznih vrata, prema ISO 13850 kategorija 0",
              "oznake opasnosti, zabrana pušenja, oznaka kapaciteta goriva",
              "najmanje dva aparata za gašenje odgovarajuće klase"]:
        bullet(doc, b)
    para(doc, "Elaborat zaštite od požara, protupožarni ventil na spremniku i "
              "blokada ventilacije pri aktivaciji gašenja zasebno su iskazani u "
              "Predmjeru (Prilog II, LOT 2) i ulaze u cijenu ponude.",
         italic=True, size=9)

    # ---------------- 5. proofs --------------------------------------------
    doc.add_heading("5. Dokazi koji se dostavljaju UZ PONUDU (uslov kvalifikacije)", 1)
    warning(doc, "Ponuda koja ne sadrži dokaze označene kao OBAVEZNI smatra se "
              "neprihvatljivom. Dokazi se NE dostavljaju naknadno, nakon dodjele ugovora.")
    table(doc, ["Br.", "Dokaz", "LOT", "Status"],
          [["1", "Statički proračun nosive konstrukcije i temelja za qp ≥ 1,20 kN/m² pri "
                 "45°, ovjeren i potpisan od ovlaštenog inženjera, sa dokazom na "
                 "podizanje i prevrtanje", "1", "OBAVEZNO"],
           ["2", "Radionički crteži konstrukcije i temelja", "1", "OBAVEZNO"],
           ["3", "Izjava o svojstvima prema EN 1090-1 i klasa izvedbe EXC2", "1", "OBAVEZNO"],
           ["4", "Atesti materijala (čelik) i potvrda o vrućem cinčanju (debljina sloja)",
            "1", "OBAVEZNO"],
           ["5", "ETA odobrenje ponuđenih hemijskih ankera sa proračunom nosivosti",
            "1", "OBAVEZNO"],
           ["6", "Tehnički list (TDS) ponuđenog agregata sa podacima o hlađenju, "
                 "izduvu i masama", "2", "OBAVEZNO"],
           ["7", "Proračun ventilacije sa padom pritiska ukupne putanje (≤125 Pa)",
            "2", "OBAVEZNO"],
           ["8", "Proračun protutlaka izduvnog sistema", "2", "OBAVEZNO"],
           ["9", "Proračun nosivosti poda kontejnera za skid i pun spremnik",
            "2", "OBAVEZNO"],
           ["10", "Jednopolna shema novog GRO sa zaštitnim uređajima", "2", "OBAVEZNO"],
           ["11", "Ovlaštenje proizvođača ili ovlaštenog distributera za ponuđeni agregat",
            "2", "OBAVEZNO"],
           ["12", "ISO 9001 i ISO 14001 proizvođača agregata", "2", "OBAVEZNO"],
           ["13", "Kataloška dokumentacija sa označenim ponuđenim tipovima", "1, 2", "OBAVEZNO"],
           ["14", "Akustički proračun, ako se zahtijeva nivo buke", "2", "po potrebi"]],
          widths=[1.2, 9.6, 1.6, 4.2])

    # ---------------- 6. tests ---------------------------------------------
    doc.add_heading("6. Ispitivanja i puštanje u rad", 1)
    table(doc, ["Ispitivanje", "Kriterij"],
          [["Otpor uzemljenja", "≤10 Ω"],
           ["Kontinuitet zaštitnih vodiča", "≤0,1 Ω po spoju"],
           ["Ispitivanje čupanja ankera", "≥10 % ankera, do 1,5 × projektne sile"],
           ["Funkcionalno ispitivanje RCD", "vrijeme i struja isključenja prema IEC 61008/61009"],
           ["Ispitivanje ventilacije", "izmjereni pad pritiska ≤125 Pa"],
           ["Funkcionalno ispitivanje agregata", "automatski start/stop, zaštite, alarmi"],
           ["Probni rad", "72 h neprekidnog rada sa simulacijom opterećenja"],
           ["Mjerenje temperature prostora", "pri radu agregata na nazivnom opterećenju"]],
          widths=[6.0, 10.6])

    doc.add_heading("7. Garancija", 1)
    for b in ["garantni period minimalno 24 mjeseca od zapisnika o primopredaji bez primjedbi",
              "postgarantni period minimalno 5 godina",
              "spisak preporučenih rezervnih dijelova za 500 h rada agregata",
              "dokumentacija izvedenog stanja i uputstva za pogon i održavanje"]:
        bullet(doc, b)

    doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r = p.add_run("Sačinio: Rusmir Skopljak, dipl. ing. el.\n"
                  "Izvršna direkcija za tehnologiju i razvoj servisa\n"
                  "BH Telecom d.d. Sarajevo")
    r.font.size = Pt(9)

    doc.save(OUT)
    return OUT


if __name__ == "__main__":
    p = build()
    print("wrote", p, f"({os.path.getsize(p)/1024:.0f} KB)")
    sys.exit(0)
