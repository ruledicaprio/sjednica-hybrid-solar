"""python -m pvsim <command> --site <id> [--set key=value ...] [--offline]

  fetch     download and cache the PVGIS responses a site needs; copy the
            small ones into sites/<id>/pvgis_ref/ with a sha256 manifest
  validate  check the PV model against PVGIS hour by hour and against PVcalc
  run       PV chain + dispatch over all years for one tilt; print the KPIs
  stands    wind actions and foundations for 3x4 / 2x6 at each tilt
  report    run every tilt, write kpis.json and figures into the site's
            review/pvsim/
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys

from pvsim import config, pvgis

HERE = os.path.dirname(os.path.abspath(__file__))


def _parser():
    ap = argparse.ArgumentParser(prog="python -m pvsim", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("fetch", "validate", "run", "stands", "photo", "report"):
        p = sub.add_parser(name)
        p.add_argument("--site", required=True, choices=config.site_ids())
        p.add_argument("--set", action="append", default=[], metavar="KEY=VALUE",
                       help="override a site parameter, e.g. --set battery.charge_c_rate=0.15")
        p.add_argument("--offline", action="store_true",
                       help="use only cached PVGIS responses")
        if name == "run":
            p.add_argument("--tilt", type=float, help="default: design.json tilt")
    return ap


def _ref_dir(site):
    return os.path.join(HERE, "sites", site["id"], "pvgis_ref")


def cmd_fetch(site, args):
    ref = _ref_dir(site)
    os.makedirs(ref, exist_ok=True)
    manifest = {}

    def keep(name, endpoint, params, text):
        path = os.path.join(ref, name)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
        manifest[name] = {"endpoint": endpoint, "params": params,
                          "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()}

    p = pvgis.horizon_params(site)
    keep("horizon.json", "printhorizon", p,
         pvgis.fetch("printhorizon", p, args.offline))
    cap_wh = site["battery"]["modules"] * site["battery"]["kwh_per_module"] * 1000
    load_wh = (site["load"]["base_w"] + site["load"].get("aux_w", 0)) * 24
    for tilt in site["array"]["tilts"]:
        t = int(tilt)
        p = pvgis.pvcalc_params(site, tilt)
        keep(f"pvcalc_t{t}.json", "PVcalc", p, pvgis.fetch("PVcalc", p, args.offline))
        cutoff = round(100 * (1 - site["control"]["dod_start"]))
        p = pvgis.shscalc_params(site, tilt, cap_wh, cutoff, load_wh)
        keep(f"shscalc_t{t}.json", "SHScalc", p, pvgis.fetch("SHScalc", p, args.offline))
        p = pvgis.hourly_params(site, tilt)
        print(f"  seriescalc {site['id']} {t}° ... ", end="", flush=True)
        text = pvgis.fetch("seriescalc", p, args.offline)
        side = pvgis.cache_manifest("seriescalc", p)
        manifest[f"seriescalc_t{t} (cache only)"] = {
            "endpoint": "seriescalc", "params": p,
            "sha256": side["sha256"] if side else None,
            "fetched_utc": side["fetched_utc"] if side else None}
        print(f"{len(text) / 1e6:.1f} MB")
    with open(os.path.join(ref, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=1, ensure_ascii=False)
    print(f"{site['id']}: {len(manifest)} responses, references in {ref}")
    return 0


def _fmt(v, nd=1):
    if isinstance(v, float):
        return f"{v:,.{nd}f}".replace(",", " ").replace(".", ",")
    return str(v)


def print_kpis(k, wf=None):
    print(f"\n== {k['site']} {k['tilt']:g}°  ({k['years'][0]}-{k['years'][1]}, "
          f"{k['n_years']} god.)")
    rows = [
        ("FN na DC sabirnici", k["pv_bus_kwh"], "kWh/god"),
        ("  specifični prinos", k["specific_yield_bus"], "kWh/kWp"),
        ("  iskorišteno / odbačeno", f"{_fmt(k['pv_used_kwh'], 0)} / "
         f"{_fmt(k['curtailed_kwh'], 0)}", "kWh/god"),
        ("Potrošnja", k["load_kwh"], "kWh/god"),
        ("Solarni udio", 100 * k["solar_fraction"], "%"),
        ("Decembar FN / potrošnja", f"{_fmt(k['dec_pv_kwh'], 0)} / "
         f"{_fmt(k['dec_load_kwh'], 0)}", "kWh"),
        ("DEA sati prosjek / P90 / max", f"{_fmt(k['genset_h_mean'])} / "
         f"{_fmt(k['genset_h_p90'])} / {_fmt(k['genset_h_max'])} "
         f"({k['genset_h_max_year']})", "h/god"),
        ("DEA startova prosjek / max", f"{_fmt(k['starts_mean'])} / {k['starts_max']}",
         "/god"),
        ("Gorivo prosjek / P90 / max", f"{_fmt(k['fuel_l_mean'], 0)} / "
         f"{_fmt(k['fuel_l_p90'], 0)} / {_fmt(k['fuel_l_max'], 0)}", "l/god"),
        ("500 l traje (prosjek / najgora god.)", f"{_fmt(k['tank_years_mean'], 2)} / "
         f"{_fmt(k['tank_years_worst'], 2)}", "god"),
        ("Dopuna prosjek / max, najkraći razmak", f"{_fmt(k['refills_mean'], 2)} / "
         f"{k['refills_max']}, {_fmt(k['refill_interval_min_days'], 0)}", "dana"),
        ("Najduže bez DEA", k["longest_genset_free_days"], "dana"),
        ("Ciklusa baterije", k["cycles_mean"], "/god"),
        ("Mokri rad (<30 %)", k["wet_stack_h_mean"], "h/god"),
        ("Nepokrivena potrošnja", k["unmet_kwh_total"], "kWh ukupno"),
    ]
    for label, v, unit in rows:
        print(f"  {label:40s} {_fmt(v) if not isinstance(v, str) else v:>28s} {unit}")
    flag = lambda ok: "PROLAZI" if ok else "NE PROLAZI"   # noqa: E731
    print(f"  ≤250 h/god (P90 / najgora):      {flag(k['pass_genset_h'])} / "
          f"{flag(k['pass_genset_h_worst'])}")
    print(f"  ≥1 god. na 500 l (prosj./najg.): {flag(k['pass_tank_year'])} / "
          f"{flag(k['pass_tank_year_worst'])}")
    if wf:
        print("  gubici FN lanca (kWh/god):")
        for r in wf:
            loss = "" if r["loss_pct"] is None else f"  −{r['loss_pct']:.2f} %"
            print(f"    {r['label']:36s} {_fmt(r['kwh'], 0):>8s}{loss}")


def cmd_run(site, args):
    from pvsim.model import run_tilt

    tilt = args.tilt if args.tilt is not None else site["array"]["tilt_deg"]
    k, years, monthly, chain, h, wf = run_tilt(site, tilt, args.offline)
    print_kpis(k, wf)
    out = os.path.join(HERE, "out", site["id"], f"t{tilt:g}")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "kpis.json"), "w", encoding="utf-8") as fh:
        json.dump(k, fh, indent=1, ensure_ascii=False)
    years.to_csv(os.path.join(out, "years.csv"))
    monthly.to_csv(os.path.join(out, "monthly.csv"))
    return 0


def cmd_validate(site, args):
    from pvsim import validate
    return validate.run(site, args.offline)


def cmd_stands(site, args):
    from pvsim import stands
    rows = stands.compare(site)
    print(f"\n== {site['id']}: nosači, qp = {_fmt(site['stands']['qp_kNm2'], 2)} kN/m² "
          f"(donja ivica +{_fmt(site['stands']['bottom_edge_m'], 2)} m)")
    hdr = ("raspored", "nagib", "c_f", "A m²", "Fh kN", "uzgon kN", "M kNm",
           "spreg kN", "traka m³", "beton m³", "gornja ivica", "dubina", "širina", "stane")
    print("  " + " | ".join(hdr))
    for r in rows:
        fits = "da" if r["fits_width"] and r["fits_depth"] else (
            "NE (dubina)" if not r["fits_depth"] else "NE (širina)")
        vals = (r["layout"], f"{r['tilt']:g}°", _fmt(r["c_f"]), _fmt(r["area_m2"], 2),
                _fmt(r["Fh_kN"]), _fmt(r["uplift_uls_kN"]), _fmt(r["M_kNm"]),
                _fmt(r["couple_kN"]), _fmt(r["strip_m3_required"], 2),
                _fmt(r["concrete_m3_total"], 2), f"+{_fmt(r['top_edge_m'], 2)} m",
                f"{_fmt(r['depth_m'], 2)} m", f"{_fmt(r['array_w_m'], 1)} m", fits)
        print("  " + " | ".join(vals))
    return 0


def cmd_report(site, args):
    from pvsim import report
    return report.run(site, args.offline)


def cmd_photo(site, args):
    from pvsim import photo
    return photo.run(site, args.offline)


def main(argv=None):
    args = _parser().parse_args(argv)
    site = config.load(args.site, args.set)
    return {"fetch": cmd_fetch, "validate": cmd_validate, "run": cmd_run,
            "stands": cmd_stands, "report": cmd_report,
            "photo": cmd_photo}[args.cmd](site, args)
