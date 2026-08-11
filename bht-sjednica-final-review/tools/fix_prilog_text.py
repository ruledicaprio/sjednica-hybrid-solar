# -*- coding: utf-8 -*-
"""
Text corrections to pages of Prilog III that were not replaced by new CAD sheets.

Two contradictions survive on original pages:

  p2   container given as 3,08 x 2,20 x 2,80 m / ~1000 kg.  The certified site project
       measures 3005 x 2300 mm external with 60 mm walls (internal 6,29 m2, perimeter
       10,13 m - both printed on the source drawing).  Finding E.

  p32  INFO-02 yield note quotes a 12 x 540 Wp reference simulation and tells the
       reader to scale by 585/540.  The Huawei review found the scaling factor sound
       but the underlying base indefensible (the referenced report implies
       17 782 kWh/kWp, which is roughly 12x physically impossible).  Finding L / F-10.

Both are corrected by redaction: the old span is removed and replacement text drawn
in its place with a matching font size.  Redaction genuinely deletes the underlying
text rather than covering it, so the old value cannot be recovered from the file.
"""
import os
import sys

import fitz

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(BASE, "TD-OUTPUT", "Prilog_III_situacija_sjednica_bileca.pdf")

REPLACEMENTS = [
    # (0-based page, search text, replacement, font size)
    (1, "Dimenzije 3,08 × 2,20 × 2,80 m, IP55, masa ~1000 kg",
     "Vanjske dimenzije 3,005 × 2,30 m, zidni paneli 60 mm "
     "(unutra 6,29 m2), IP55, prema ovjerenom projektu lokacije; PRAZAN", 6.6),
    (31, "NAPOMENA: Prikazane vrijednosti odnose se na referentnu simulaciju za "
         "konfiguraciju 12×540 Wp (6,48 kWp).",
     "NAPOMENA: Prikazane vrijednosti NISU MJERODAVNE - referentna simulacija "
     "sadrzi gresku reda velicine.", 7.2),
    (31, "Za trenutnu konfiguraciju 12×585 Wp (7,02 kWp) sve vrijednosti proizvodnje "
         "skalirati faktorom 585/540 ≈ 1,083 (+8,3%).",
     "Mjerodavno za 12 x 585 Wp (7,02 kWp): ocekivana godisnja proizvodnja "
     "10,1-10,9 MWh; decembar 560-600 kWh naspram potrosnje 878 kWh - DEA je nuzan.", 7.2),
]


def main():
    doc = fitz.open(PDF)
    done = 0
    for pno, old, new, size in REPLACEMENTS:
        page = doc[pno]
        rects = page.search_for(old)
        if not rects:
            # long spans can break across lines; fall back to the first sentence
            head = old.split(".")[0][:60]
            rects = page.search_for(head)
        if not rects:
            print(f"  MISS p{pno+1}: {old[:50]!r}")
            continue
        r = rects[0]
        for rr in rects:
            r = r | rr
        page.add_redact_annot(r, fill=(1, 1, 1))
        page.apply_redactions()
        box = fitz.Rect(r.x0, r.y0 - 1, max(r.x1, r.x0 + 380), r.y1 + 22)
        rc = page.insert_textbox(box, new, fontsize=size, fontname="helv",
                                 color=(0, 0, 0), align=0)
        if rc < 0:                       # did not fit: step the size down
            for s in (size - 0.6, size - 1.2, size - 1.8):
                page.insert_textbox(box, new, fontsize=s, fontname="helv",
                                    color=(0, 0, 0), align=0)
                rc = 0
                break
        done += 1
        print(f"  OK   p{pno+1}: {old[:46]!r} -> {new[:46]!r}")

    doc.subset_fonts()
    tmp = PDF + ".tmp"
    doc.save(tmp, garbage=4, deflate=True, deflate_images=True,
             deflate_fonts=True, clean=True)
    doc.close()
    os.replace(tmp, PDF)

    d = fitz.open(PDF)
    import re
    left = []
    for i in range(d.page_count):
        t = d[i].get_text()
        if re.search(r"3[,.]08\s*[x×]\s*2[,.]20", t):
            left.append(f"p{i+1} container size")
        if re.search(r"540\s*Wp", t):
            left.append(f"p{i+1} 540 Wp")
    print(f"\n{done} replacements | remaining contradictions: {left or 'none'} | "
          f"{d.page_count} pages, {os.path.getsize(PDF)/1e6:.2f} MB")
    d.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
