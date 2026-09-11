# -*- coding: utf-8 -*-
"""
Consistency check for the joint two-site package (rfp-hybrid-solar-td/TD-OUTPUT).

Reuses the Sjednica checker's readers and rules: both sites carry the same
system, so every "exactly one value" rule (generator rating, container size,
module power, stand forces, foundation volume, ...) still has one correct value
across the joint package. Site-specific values that differ (fence 2,10 / 1,80 m,
overhang 1,64 / 1,94 m, altitude 1076 / 493 m) are not variants of those rules,
so they do not collide; they are added below as values that must be present.

Three additions for the joint package:
  COVERAGE   every deliverable names both sites
  BANNED+    single-site leftovers and wrong facts about Hamzići
  PENDING    estimate placeholders - reported, and counted, until the Investor
             supplies the estimates

Exit code = failures + pending, so the package cannot be released by accident.
"""
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import paths                                                        # noqa: E402

sys.path.insert(0, os.path.join(paths.SITES["sjednica"]["folder"], "tools"))
import check_consistency as cc                                      # noqa: E402

SINGLE_VALUE = {k: v for k, v in cc.SINGLE_VALUE.items() if "estimate" not in k}
SINGLE_VALUE.update({
    "Hamzići altitude 493 m": r"493\s*m",
    "Hamzići parcel k.č. 109/1": r"109/1",
    "Hamzići fence 1,80 m": r"1[,.]80\s*m",
    "Stulz WDE80 removal": r"Stulz\s*WDE80",
    "Stulz delivered to Alipašino Polje": r"Alipašino\s*Polje",
    "Hamzići expected genset ≈210 h/god": r"≈\s*210\s*h",
    "Hamzići expected fuel ≈710 l/god": r"≈\s*710\s*l",
})

BANNED = dict(cc.BANNED)
BANNED.update({
    "Hamzići placed in Čapljina (it is Čitluk)": r"Čapljin",
    "Hamzići tower as 36 m (it is 32 m)": r"AS\s*36\s*m|visine\s+(h\s*=\s*)?36\s*m",
    "question-mark placeholder": r"Hamzi[ćc]i\?",
    "single-site title": r"NAPAJANJA\s+SJEDNICA,\s+BILEĆA\s+\(LOT",
    "single-site phrase in the Odluka": r"na\s+baznoj\s+stanici\s+Sjednica",
    "withdrawn 2017 grid connection presented as existing": r"priključen\w*\s+na\s+EES\s+preko",
})

PENDING = {"estimate placeholder": r"___\.___"}


def load():
    cc.TD = paths.TD
    docs = cc.load()
    for p in sorted(glob.glob(os.path.join(paths.GRAFIKA, "*", "*.dxf"))):
        try:
            docs[os.path.relpath(p, paths.TD)] = cc.read_dxf(p)
        except Exception as exc:                                    # noqa: BLE001
            print(f"  ! could not read {p}: {exc}")
    return docs


def main():
    docs = load()
    print(f"documents read: {len(docs)}")
    for n in docs:
        print(f"   {n}  ({len(docs[n]):,} chars)")
    fails = 0

    print("\n=== COVERAGE (every deliverable names both sites) ===")
    for name, text in docs.items():
        # drawings and the per-site calculations belong to one site by design
        if name.startswith("grafika") or name.startswith("proracuni_BS_"):
            continue
        has = {s: bool(re.search(p, text, re.I)) for s, p in
               (("Sjednica", r"Sjednic"), ("Hamzići", r"Hamzi[ćc]"))}
        ok = all(has.values())
        fails += not ok
        print(f"  {'OK  ' if ok else 'FAIL'} {name}: " +
              ", ".join(f"{s} {'da' if v else 'NE'}" for s, v in has.items()))

    print("\n=== CONFLICTS (exactly one variant allowed) ===")
    for topic, variants in cc.CONFLICTS.items():
        found = {label: cc.scan(docs, pat, live_only="WRONG" in label or "superseded" in label)
                 for label, pat in variants.items()}
        found = {k: v for k, v in found.items() if v}
        if len(found) > 1:
            fails += 1
            print(f"  FAIL  {topic}: {len(found)} variants coexist")
            for label, hits in found.items():
                print(f"          '{label}' in " + ", ".join(f"{k} x{v}" for k, v in hits.items()))
        elif found:
            label = next(iter(found))
            print(f"  OK    {topic}: '{label}' ({sum(found[label].values())} mentions)")
        else:
            print(f"  --    {topic}: not mentioned anywhere")

    print("\n=== REQUIRED VALUES ===")
    for topic, pat in SINGLE_VALUE.items():
        hits = cc.scan(docs, pat)
        if not hits:
            fails += 1
            print(f"  FAIL  {topic}: absent from the whole package")
        else:
            print(f"  OK    {topic}: {sum(hits.values())} mentions in {len(hits)} document(s)")

    print("\n=== BANNED TEXT ===")
    for topic, pat in BANNED.items():
        hits = cc.scan(docs, pat, live_only=True)
        if hits:
            fails += 1
            print(f"  FAIL  {topic}: " + ", ".join(f"{k} x{v}" for k, v in hits.items()))
        else:
            print(f"  OK    {topic}: gone")

    print("\n=== PENDING (Naručilac) ===")
    pending = 0
    for topic, pat in PENDING.items():
        hits = cc.scan(docs, pat)
        if hits:
            pending += 1
            print(f"  PENDING  {topic}: " + ", ".join(f"{k} x{v}" for k, v in hits.items()))
        else:
            print(f"  OK       {topic}: none left")

    print(f"\nRESULT: {fails} failure(s), {pending} pending")
    return fails + pending


if __name__ == "__main__":
    sys.exit(main())
