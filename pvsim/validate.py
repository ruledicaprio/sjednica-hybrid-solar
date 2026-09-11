"""Checks the PV model against PVGIS before any KPI is trusted.

1. Hour by hour: pvsim's module model with PVGIS's flat 14 % loss against the
   P column PVGIS returns for the same hours - same irradiance, so this tests
   the IAM / temperature / Huld implementation directly.
2. Long-term means: the same model against PVcalc's monthly and yearly
   energy (month within 3 %, year within 2 %).
3. Ceilings: nothing may exceed 1800 kWh/kWp·yr - the check that the old
   report_results figure (17 782 kWh/kWp) would have failed at once.

Exit code = number of failed checks.
"""
from __future__ import annotations

import numpy as np

from pvsim import config, pv, pvgis

MONTH_TOL, YEAR_TOL, CEILING = 0.03, 0.02, 1800.0


def metrics(site, tilt, offline=False):
    """The comparison numbers for one tilt (also written into kpis.json)."""
    s = config.with_tilt(site, tilt)
    az = s["array"]["azimuth_deg"]
    df, _ = pvgis.hourly(s, tilt, az, offline=offline)
    n_years = len(set(df.index.year))
    ours = pv.pvgis_equivalent(df, s, tilt, az, 14.0)
    theirs = df["P"]
    ref = pvgis.pvcalc(s, tilt, az, offline=offline)
    e_m = {m["month"]: m["E_m"] for m in ref["outputs"]["monthly"]["fixed"]}
    mo = ours.groupby(ours.index.month).sum() / 1000 / n_years
    mt = theirs.groupby(theirs.index.month).sum() / 1000 / n_years
    return {
        "n_years": n_years,
        "pvcalc_E_y": ref["outputs"]["totals"]["fixed"]["E_y"],
        "pvcalc_E_m": [e_m[m] for m in range(1, 13)],
        "seriescalc_E_y": float(theirs.sum() / 1000 / n_years),
        "seriescalc_E_m": [float(mt[m]) for m in range(1, 13)],
        "pvsim_E_y": float(ours.sum() / 1000 / n_years),
        "pvsim_E_m": [float(mo[m]) for m in range(1, 13)],
        "hourly_r": float(np.corrcoef(ours, theirs)[0, 1]),
        "worst_month_dev": float(max(abs(mo[m] / e_m[m] - 1) for m in range(1, 13))),
    }


def run(site, offline=False):
    fails = 0
    kwp = site["array"]["kWp"]
    for tilt in site["array"]["tilts"]:
        v = metrics(site, tilt, offline)
        n_years, e_y, r = v["n_years"], v["pvcalc_E_y"], v["hourly_r"]
        yr_o, yr_t = v["pvsim_E_y"], v["seriescalc_E_y"]
        e_m = dict(zip(range(1, 13), v["pvcalc_E_m"]))
        mo = dict(zip(range(1, 13), v["pvsim_E_m"]))
        mt = dict(zip(range(1, 13), v["seriescalc_E_m"]))

        print(f"\n== {site['id']} {tilt:g}°  ({n_years} god.)")
        print(f"  PVcalc godišnje            {e_y:8.1f} kWh  ({e_y / kwp:.1f} kWh/kWp)")
        print(f"  PVGIS seriescalc P         {yr_t:8.1f} kWh")
        print(f"  pvsim (PVGIS model, 14 %)  {yr_o:8.1f} kWh   satna korelacija r = {r:.4f}")
        print("  mjesec   PVcalc  seriescalc   pvsim   pvsim/PVcalc")
        worst = 0.0
        for m in range(1, 13):
            ratio = mo[m] / e_m[m]
            worst = max(worst, abs(ratio - 1))
            print(f"    {m:2d}   {e_m[m]:7.1f}   {mt[m]:7.1f}   {mo[m]:7.1f}   {ratio:7.3f}")

        checks = [
            (f"godišnje unutar {YEAR_TOL:.0%} od PVcalc", abs(yr_o / e_y - 1) <= YEAR_TOL),
            (f"svaki mjesec unutar {MONTH_TOL:.0%} od PVcalc (najgori "
             f"{worst:.1%})", worst <= MONTH_TOL),
            ("satna korelacija sa PVGIS P ≥ 0,99", r >= 0.99),
            (f"specifični prinos < {CEILING:.0f} kWh/kWp", yr_o / kwp < CEILING),
        ]
        for label, ok in checks:
            print(f"  {'OK  ' if ok else 'FAIL'} {label}")
            fails += not ok
    print(f"\nRESULT: {fails} failure(s)")
    return fails
