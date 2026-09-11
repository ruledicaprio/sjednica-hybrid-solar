# -*- coding: utf-8 -*-
"""Proračuni: review/07-proracuni.md -> PDF with a text layer.

Until Rev 8 this PDF was rendered outside the repo (jsPDF) as page images:
nothing in it was searchable and check_consistency could not read one figure
of it. It is now built like Prilog I - pandoc with the same reference style -
and printed to PDF by LibreOffice, so the text survives. The copy in TD-OUTPUT
had also drifted: its .md was the Prilog I source under the proračuni name.

    python tools/build_proracuni.py
"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from build_prilog1 import REF, pandoc, widen_tables                  # noqa: E402
from paths import TD                                                # noqa: E402

MD = os.path.join(BASE, "review", "07-proracuni.md")
OUTS = [os.path.join(BASE, "review", "07-proracuni_sjednica.pdf"),
        os.path.join(TD, "proracuni_BS_Sjednica_Bileca.pdf")]
MD_COPY = os.path.join(TD, "proracuni_BS_Sjednica_Bileca.md")
SOFFICE = os.environ.get("SOFFICE",
                         r"C:\Program Files\LibreOffice\program\soffice.exe")
REQUIRED = ["A.6 Energetski bilans", "PVGIS-SARAH3", "≈250 h/god", "≈820 l/god",
            "42,6 kNm", "9,5 kW", "SoC 60 %"]


def main():
    import fitz

    tmp = tempfile.mkdtemp(prefix="proracuni_")
    docx = os.path.join(tmp, "07-proracuni.docx")
    subprocess.run([pandoc(), MD, "-o", docx, "--reference-doc", REF,
                    "--resource-path", os.path.dirname(MD),
                    "--from", "markdown+pipe_tables+raw_attribute",
                    "--columns", "999"], check=True)
    widen_tables(docx)
    # a private profile, so a LibreOffice window the user has open does not
    # swallow the headless conversion
    profile = "file:///" + os.path.join(tmp, "lo").replace("\\", "/")
    subprocess.run([SOFFICE, f"-env:UserInstallation={profile}", "--headless",
                    "--convert-to", "pdf", "--outdir", tmp, docx],
                   check=True, capture_output=True, timeout=600)
    pdf = os.path.join(tmp, "07-proracuni.pdf")
    d = fitz.open(pdf)
    text = "".join(p.get_text() for p in d).replace("\xa0", " ")
    pages = d.page_count
    d.close()
    missing = [r for r in REQUIRED if r not in text]
    if missing:
        raise SystemExit(f"PRORAČUNI — nedostaje u PDF-u: {missing}")
    for out in OUTS:
        os.makedirs(os.path.dirname(out), exist_ok=True)
        shutil.copy(pdf, out)
    shutil.copy(MD, MD_COPY)
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"proračuni: {pages} str., {len(text)} znakova teksta -> " +
          ", ".join(os.path.relpath(o, BASE) for o in OUTS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
