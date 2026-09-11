# -*- coding: utf-8 -*-
"""Copy the energy figures from review/pvsim/kpis.json into cad/design.json.

design.json is the file the drawings and Prilog III read their numbers from;
the energy figures in it must be the ones pvsim produced, with a hash that
ties them to the exact run - never numbers typed in by hand. Rerun after
`python -m pvsim report --site <id>`:

    python tools/sync_energy.py              # this site folder
    TD_SITE=<folder> python tools/sync_energy.py
"""
import hashlib
import json
import os
import sys

BASE = os.environ.get("TD_SITE") or os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))
DESIGN = os.path.join(BASE, "cad", "design.json")
KPIS = os.path.join(BASE, "review", "pvsim", "kpis.json")


def main():
    raw = open(KPIS, "rb").read()
    doc = json.loads(raw.decode("utf-8"))
    design = json.load(open(DESIGN, encoding="utf-8"))
    tilt = f"{design['array']['tilt_deg']:g}"
    if tilt not in doc["tilts"]:
        raise SystemExit(f"kpis.json has no run for the design tilt {tilt}°")
    k, v = doc["tilts"][tilt]["kpis"], doc["validation"][tilt]
    keep = ("pv_bus_kwh", "specific_yield_bus", "pv_used_kwh", "curtailed_kwh",
            "load_kwh", "solar_fraction", "dec_pv_kwh", "dec_load_kwh",
            "genset_h_mean", "genset_h_p90", "genset_h_max", "starts_mean",
            "fuel_l_mean", "fuel_l_p90", "fuel_l_max", "refills_mean",
            "tank_years_mean", "longest_genset_free_days", "cycles_mean",
            "unmet_kwh_total")
    design["energy"] = {
        "_source": "review/pvsim/kpis.json, written by `python -m pvsim report "
                   f"--site {doc['site']}`; copied here by tools/sync_energy.py. "
                   "Do not edit by hand.",
        "kpis_sha256": hashlib.sha256(raw).hexdigest(),
        "pvsim_commit": doc["git_commit"], "generated_utc": doc["generated_utc"],
        "tilt_deg": design["array"]["tilt_deg"],
        "years": k["years"],
        **{key: round(k[key], 3) for key in keep},
        "validation": {"pvcalc_E_y": round(v["pvcalc_E_y"], 1),
                       "pvsim_E_y": round(v["pvsim_E_y"], 1),
                       "worst_month_dev": round(v["worst_month_dev"], 4),
                       "hourly_r": round(v["hourly_r"], 5)},
        "limits_odluka": {"genset_h_max": 250, "tank_years_min": 1.0,
                          "_status": "superseded in Rev 9 by the simulated values "
                                     "(review/09-odluka-nosaci-nagib.md)"},
    }
    c, b, g = doc["inputs"]["control"], doc["inputs"]["battery"], doc["inputs"]["genset"]
    design["control"] = {
        "_source": "Prilog I §4.6 (Rev 9): SMU settings the bidder sets and proves "
                   "with evidence item 12; the same values are the pvsim base case.",
        "dod_start": c["dod_start"], "soc_stop": c["soc_stop"],
        "min_run_h": c["min_run_h"], "charge_c_rate": b["charge_c_rate"],
        "rect_cap_ac_kw": g["rect_cap_ac_kw"],
    }
    with open(DESIGN, "w", encoding="utf-8") as fh:
        json.dump(design, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    e = design["energy"]
    print(f"design.json energy <- kpis.json {e['kpis_sha256'][:12]} ({tilt}°): "
          f"DEA {e['genset_h_mean']:.0f} h/god, gorivo {e['fuel_l_mean']:.0f} l/god")
    return 0


if __name__ == "__main__":
    sys.exit(main())
