"""Prilog I: review/prilog1.md  --pandoc-->  TD-OUTPUT/3. Prilog I TD ... .docx

Rev 8 (2026-08-12). Naručilac je odlučio da Prilog I dobije izgled md dokumenata
(kao render `proracuni_sjednica.pdf`), a da ostane .docx — dakle editabilan.

Dva koraka:
  1. `ref_docx()` gradi tools/ref-prilog1.docx iz pandoc-ovog podrazumijevanog
     reference dokumenta i podešava A4, margine i font. Radi se jednom i rezultat
     se commituje; ovdje stoji da se zna kako je nastao i da se može ponoviti.
  2. `build()` pokreće pandoc i onda PROVJERAVA rezultat.

Provjera je razlog zašto ovo nije jednolinijski shell poziv. Prilog I je do Rev 8
nosio 13 zastarjelih vrijednosti koje su preživjele šest revizija upravo zato što
ih niko nije provjeravao programski — među njima i pogrešan zid za usisnu žaluzinu,
što ponuđača šalje da probije pogrešnu stranu kontejnera. FORBIDDEN/REQUIRED liste
niže su te vrijednosti; ako se ijedna vrati, build pada.
"""
import os
import re
import shutil
import subprocess
import sys
import zipfile

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "tools"))
from paths import PRILOG1 as OUT                                    # noqa: E402

MD = os.path.join(BASE, "review", "prilog1.md")
REF = os.path.join(BASE, "tools", "ref-prilog1.docx")

# Vrijednosti koje su bile pogrešne i ne smiju se vratiti (Rev 8, P1-P13).
FORBIDDEN = [
    ("62,8 kNm", "moment prevrtanja pri donjoj ivici +1,50 m"),
    ("39,3 kN", "spreg po traci pri donjoj ivici +1,50 m"),
    ("7,1 kW", "toplota u prostor za P22-6"),
    ("95 A", "3 × In za 22 kVA"),
    ("407 A", "prva poluperioda za 22 kVA"),
    ("31,75 A", "In za 22 kVA"),
    ("P22-6", "povučeni agregat"),
    ("ICC330-H1", "povučeni ormar"),
    ("stavka 4.11", "izduv je u predmjeru 4.10"),
    ("Tačku 4.8", "Prilog I nema tačku 4.8"),
    ("Tečnički", "tipfeler"),
    ("usis JUG", "usis je na SJEVERNOM zidu"),
    ("400 mm južno od kote ograde", "odmak vrijedio pri +1,50 m"),
    ("≈6 m²", "kanal i izolacija izduva"),
    ("h = 1,90 m", "ograda je 2,10 m"),
    # Rev 9: energetske vrijednosti dolaze samo iz pvsim simulacije
    ("bifacijal", "moduli su monofacijalni iPV sa optimizatorima"),
    ("≤250 h", "granica iz RFI; simulacija daje više — zamijenjena u Rev 9"),
    ("do 250 h", "granica iz RFI; simulacija daje više — zamijenjena u Rev 9"),
    ("najmanje godinu", "500 l nije godišnja zaliha goriva (Rev 9)"),
    ("10,1–10,9 MWh", "stara procjena prinosa sa PR 0,80"),
    ("560–600 kWh", "stara procjena decembra"),
]

# Vrijednosti koje MORAJU biti u izlazu.
REQUIRED = [
    "42,6 kNm", "26,6 kN", "5,8 kW", "78 A", "26,0 A", "P18-6",
    "ICC360-HA1-C1", "MTS9302A", "9,5 kW", "1,0 m²", "3,0 m²",
    "SJEVERNI zid, istočni kraj", "JUŽNI zid", "1,485 m³", "8,91 m³",
    "1150 × 640", "2,10 m", "+0,50 m / +3,74 m", "1,64 m", "NO 50",
    "PMG", "AREP", "1,20 kN/m²", "18,1 kN", "13,4 kN", "0,6 kN/m²",
    # Rev 9
    "DOD 85 %", "SoC 60 %", "PVGIS-SARAH3", "Očekivani energetski bilans",
    "≈250 h/god", "≈820 l/god", "DC razvod −48 V", "≤25 W prosječno",
]

SECT = re.compile(rb"<w:sectPr\b.*?</w:sectPr>", re.S)
A4 = (b'<w:pgSz w:w="11906" w:h="16838"/>'
      b'<w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134" '
      b'w:header="709" w:footer="709" w:gutter="0"/>')


def pandoc():
    """pandoc.exe: $PANDOC, pa PATH, pa winget instalacija po korisniku — ona
    ne stigne na PATH dok se ne otvori nova ljuska."""
    for exe in (os.environ.get("PANDOC"), shutil.which("pandoc"),
                os.path.join(os.environ.get("LOCALAPPDATA", ""), "Pandoc",
                             "pandoc.exe")):
        if exe and os.path.exists(exe):
            return exe
    raise SystemExit("pandoc nije pronađen — winget install --id "
                     "JohnMacFarlane.Pandoc -e --scope user")


def ref_docx():
    """Napraviti reference dokument: A4, margine 20 mm, Calibri."""
    default = subprocess.run(
        [pandoc(), "--print-default-data-file", "reference.docx"],
        capture_output=True, check=True).stdout
    tmp = REF + ".tmp"
    with open(tmp, "wb") as fh:
        fh.write(default)

    src = zipfile.ZipFile(tmp)
    with zipfile.ZipFile(REF, "w", zipfile.ZIP_DEFLATED) as dst:
        for item in src.namelist():
            data = src.read(item)
            if item == "word/document.xml":
                new, n = SECT.subn(b"<w:sectPr>" + A4 + b"</w:sectPr>", data)
                if not n:
                    raise SystemExit("reference.docx: nema <w:sectPr>")
                data = new
            elif item == "word/theme/theme1.xml":
                # Font NE dolazi iz styles.xml nego iz teme: stilovi upućuju na
                # minorHAnsi/majorHAnsi, a tema kaže koji je to font. Mijenjanje
                # styles.xml ovdje ne radi ništa.
                data = re.sub(rb'(<a:(?:major|minor)Font>\s*<a:latin '
                              rb'typeface=")[^"]*(")',
                              rb'\1Calibri\2', data)
            elif item == "word/styles.xml":
                # 12 pt -> 10,5 pt; tenderski prilog sa 18 tabela
                data = data.replace(b'<w:sz w:val="24" />',
                                    b'<w:sz w:val="21" />')
                data = data.replace(b'<w:szCs w:val="24" />',
                                    b'<w:szCs w:val="21" />')
            dst.writestr(item, data)
    src.close()
    os.remove(tmp)
    print(f"reference stil: {REF}")


TEXT_W = 11906 - 2 * 1134          # A4 manje margine, u twips


def widen_tables(path):
    """Razvući tabele na punu širinu teksta.

    Pandoc emituje `tblW type="auto" w="0"` i jednake gridCol širine, pa tabele
    zauzmu ~80 % sloga i drugi stupac se nepotrebno prelama dok desno stoji
    prazan pojas. Kolone se skaliraju proporcionalno, ne izjednačavaju — prvi
    stupac je oznaka parametra i treba da ostane uži.
    """
    z = zipfile.ZipFile(path)
    items = {n: z.read(n) for n in z.namelist()}
    z.close()
    xml = items["word/document.xml"].decode("utf-8")

    def grid(m):
        cols = [int(w) for w in re.findall(r'<w:gridCol w:w="(\d+)"\s*/>',
                                           m.group(0))]
        if not cols:
            return m.group(0)
        # prvi stupac 34 %, ostatak ravnomjerno — čitljiv raspored za 2 i 4 kol.
        if len(cols) == 2:
            share = [0.34, 0.66]
        elif len(cols) == 3:
            share = [0.26, 0.30, 0.44]
        else:
            share = [1.0 / len(cols)] * len(cols)
        new = [int(TEXT_W * s) for s in share]
        new[-1] += TEXT_W - sum(new)
        return ("<w:tblGrid>"
                + "".join(f'<w:gridCol w:w="{w}"/>' for w in new)
                + "</w:tblGrid>")

    xml = re.sub(r"<w:tblGrid>.*?</w:tblGrid>", grid, xml, flags=re.S)
    xml = xml.replace('<w:tblW w:type="auto" w:w="0" />',
                      f'<w:tblW w:type="dxa" w:w="{TEXT_W}"/>')
    items["word/document.xml"] = xml.encode("utf-8")

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as out:
        for name, data in items.items():
            out.writestr(name, data)


def build(md=MD, out=OUT, forbidden=FORBIDDEN, required=REQUIRED, n_media=7,
          ref=REF):
    """Pandoc + provjera. Parametri su tu da isti build i iste provjere posluže
    i zajedničkom paketu dvije lokacije, koji ima svoj md, izlaz i liste."""
    if not os.path.exists(ref):
        ref_docx()
    os.makedirs(os.path.dirname(out), exist_ok=True)
    cmd = [pandoc(), md, "-o", out,
           "--reference-doc", ref,
           "--resource-path", os.path.dirname(os.path.abspath(md)),
           "--from", "markdown+pipe_tables+raw_attribute",
           "--columns", "999"]
    subprocess.run(cmd, check=True)
    widen_tables(out)

    z = zipfile.ZipFile(out)
    xml = z.read("word/document.xml").decode("utf-8")
    text = "".join(re.findall(r"<w:t[^>]*>(.*?)</w:t>", xml, re.S))
    text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    media = [n for n in z.namelist() if n.startswith("word/media/")]

    fail = []
    for needle, why in forbidden:
        if needle in text:
            fail.append(f"vratila se zastarjela vrijednost {needle!r} ({why})")
    for needle in required:
        if needle not in text:
            fail.append(f"nedostaje obavezna vrijednost {needle!r}")
    if len(media) != n_media:
        fail.append(f"očekivano {n_media} slika, ugrađeno {len(media)}")
    if fail:
        raise SystemExit("PRILOG I — provjera pala:\n  " + "\n  ".join(fail))

    print(f"snimljeno: {out}")
    print(f"  slika: {len(media)} · znakova teksta: {len(text)}")
    print(f"  {len(forbidden)} zabranjenih vrijednosti odsutno, "
          f"{len(required)} obaveznih prisutno")


if __name__ == "__main__":
    if "--ref" in sys.argv:
        ref_docx()
    build()
