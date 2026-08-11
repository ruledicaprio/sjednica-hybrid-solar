# -*- coding: utf-8 -*-
"""
Surgical text editing inside a .docx, at the OOXML level.

Per CLAUDE.md the .docx must never be regenerated - only the affected runs are
touched, so the template's styles, numbering, headers, footers and layout survive
byte-for-byte.

Word routinely splits a single visible sentence across many <w:t> runs (spell-check
state, rsid tracking, formatting islands), so a naive string replace on document.xml
misses most real edits. This module concatenates the runs, does the replacement on
that flat text, then writes the result back into the first affected run and blanks
the remainder of the span - which preserves the first run's formatting for the whole
replacement.

Every replacement must match exactly the expected number of times or the edit is
refused, so a template that has drifted fails loudly instead of silently half-editing.
"""
from __future__ import annotations

import re
import shutil
import zipfile

WT = re.compile(r"(<w:t(?:\s[^>]*)?>)(.*?)(</w:t>)", re.S)
XML_ESC = {"&": "&amp;", "<": "&lt;", ">": "&gt;"}


def _esc(s):
    return "".join(XML_ESC.get(c, c) for c in s)


def _unesc(s):
    return (s.replace("&lt;", "<").replace("&gt;", ">")
             .replace("&quot;", '"').replace("&apos;", "'")
             .replace("&amp;", "&"))


class Part:
    """One XML part, indexed so edits can be expressed against its visible text."""

    def __init__(self, xml):
        self.xml = xml
        self._index()

    def _index(self):
        self.runs = []          # (start, end, prefix, text, suffix)
        self.text = ""
        self.map = []           # text position -> run number
        for m in WT.finditer(self.xml):
            t = _unesc(m.group(2))
            self.runs.append([m.start(), m.end(), m.group(1), t, m.group(3)])
            self.map.extend([len(self.runs) - 1] * len(t))
            self.text += t

    def replace(self, find, repl, expect=1, regex=False):
        pat = find if regex else re.escape(find)
        hits = list(re.finditer(pat, self.text))
        if len(hits) != expect:
            raise ValueError(
                f"expected {expect} match(es) for {find!r}, found {len(hits)}")
        for h in reversed(hits):                    # right to left keeps offsets valid
            a, b = h.start(), h.end()
            new = h.expand(repl) if regex else repl
            first, last = self.map[a], self.map[b - 1]
            off_a = a - self.map.index(first)
            head = self.runs[first][3][:off_a]
            tail_run = self.runs[last]
            off_b = b - 1 - self.map.index(last)
            tail = tail_run[3][off_b + 1:]
            self.runs[first][3] = head + new + (tail if first == last else "")
            for i in range(first + 1, last + 1):
                self.runs[i][3] = tail if i == last else ""
            self._rebuild()
        return len(hits)

    def _rebuild(self):
        out, prev = [], 0
        for s, e, pre, txt, suf in self.runs:
            out.append(self.xml[prev:s])
            keep = ' xml:space="preserve"'
            p = pre if "xml:space" in pre else pre[:-1] + keep + ">"
            out.append(p + _esc(txt) + suf)
            prev = e
        out.append(self.xml[prev:])
        self.xml = "".join(out)
        self._index()


def edit_docx(path, edits, parts=("word/document.xml",), backup=None):
    """
    edits: list of (find, replace, expect) or (find, replace, expect, regex_bool),
    applied in order against the first part that contains the target.
    Returns a list of (find, part, count).
    """
    if backup:
        shutil.copy(path, backup)
    z = zipfile.ZipFile(path)
    names = z.namelist()
    loaded = {n: Part(z.read(n).decode("utf-8")) for n in parts if n in names}
    raw = {n: z.read(n) for n in names}
    z.close()

    applied = []
    for e in edits:
        find, repl, expect = e[0], e[1], e[2]
        rx = e[3] if len(e) > 3 else False
        done = False
        errs = []
        for n, part in loaded.items():
            probe = re.escape(find) if not rx else find
            if not re.search(probe, part.text):
                continue
            try:
                c = part.replace(find, repl, expect, rx)
                applied.append((find, n, c))
                done = True
                break
            except ValueError as exc:               # noqa: PERF203
                errs.append(f"{n}: {exc}")
        if not done:
            raise SystemExit(f"EDIT FAILED: {find!r}\n  " + "\n  ".join(errs or
                             ["target text not present in any part"]))

    tmp = path + ".tmp"
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as out:
        for n in names:
            info = zipfile.ZipInfo(n)
            info.compress_type = zipfile.ZIP_DEFLATED
            data = (loaded[n].xml.encode("utf-8") if n in loaded else raw[n])
            out.writestr(info, data)
    shutil.move(tmp, path)
    return applied
