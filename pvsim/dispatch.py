"""Hourly off-grid energy balance on the -48 V DC bus.

PV (through the iSSU converters), the LFP battery, the genset through the
rectifiers, and the TK load. All years run as one continuous series, so the
state of charge and the fuel level carry across year boundaries - a December
deficit that ends in January is one deficit, not two half-deficits.

Genset control follows the Huawei SMU: the set starts when the battery depth
of discharge reaches "DOD to Start" (default 85 %), runs with the rectifier
input capped (9,5 kW AC in this tender) and stops at the stop SoC once its
minimum run time is served. While it runs, PV keeps priority; the rectifiers
make up the rest of the load plus the battery's charge acceptance.

Energy is conserved and checked every hour: PV used + genset + battery
discharge + unmet = load + battery charge. Unmet load must be zero for a
compliant design - the genset is sized to always cover it.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def load_kw(temp_air, site):
    L = site["load"]
    ramp = np.clip((np.asarray(temp_air, dtype=float) - L["cooling_t0_c"])
                   / (L["cooling_t1_c"] - L["cooling_t0_c"]), 0.0, 1.0)
    return (L["base_w"] + L.get("aux_w", 0.0) + L["cooling_w_max"] * ramp) / 1000.0


def fuel_l_h(p_ac_kw, genset):
    """Fuel rate from the data-sheet points, linear in output power; below the
    lowest point (50 % prime) the first segment is extrapolated towards idle."""
    pts = np.array(genset["fuel_l_h"], dtype=float)
    x, y = pts[:, 0], pts[:, 1]
    p = np.asarray(p_ac_kw, dtype=float)
    slope = (y[1] - y[0]) / (x[1] - x[0])
    low = y[0] + slope * (p - x[0])
    return np.where(p < x[0], np.maximum(low, 0.0), np.interp(p, x, y))


def simulate(pv_kw, temp_air, site, tol=1e-9):
    """Run the dispatch. pv_kw: DC power on the bus per hour (kW = kWh/h).

    Returns a DataFrame indexed like pv_kw with the hourly flows (kWh), the
    state of charge at the end of each hour and the genset run fraction.
    """
    b, c, g = site["battery"], site["control"], site["genset"]
    cap = b["modules"] * b["kwh_per_module"]
    eta_c, eta_d = b["eta_charge"], b["eta_discharge"]
    ch_lim = b["charge_c_rate"] * cap
    soc_start = (1.0 - c["dod_start"]) * cap
    soc_stop = c["soc_stop"] * cap
    floor = b["soc_floor"] * cap
    gen_cap = g["rect_cap_ac_kw"] * g["eta_rect"]
    min_run = c["min_run_h"]

    index = pv_kw.index
    pv = np.asarray(pv_kw, dtype=float).tolist()
    ld = load_kw(temp_air, site).tolist()
    n = len(pv)

    soc_end = [0.0] * n
    frac = [0.0] * n
    egen = [0.0] * n
    chg = [0.0] * n
    dis = [0.0] * n
    curt = [0.0] * n
    unmet = [0.0] * n
    start = [0] * n

    soc = b["soc_initial"] * cap
    on = False
    run = 0.0
    for i in range(n):
        p, l = pv[i], ld[i]
        if not on and soc <= soc_start + tol:
            on, run, start[i] = True, 0.0, 1
        f = eg = 0.0
        reached = False
        if on:
            gpow = min(gen_cap, max(0.0, l + ch_lim - p))
            r_on = min(p + gpow - l, ch_lim) * eta_c
            f = 1.0
            if r_on > 0 and soc + r_on >= soc_stop - tol:
                # The stop SoC is reached part-way through the hour. The stop
                # decision is taken there, not on the end-of-hour SoC: for the
                # rest of the hour the battery carries the load again, so the
                # end-of-hour SoC sits just below the stop value and a check on
                # it would keep the set running at a sliver of every hour.
                reached = True
                f = min(1.0, max((soc_stop - soc) / r_on, min_run - run, 0.0))
            eg = gpow * f

        e_bal = p + eg - l
        ch = ds = cu = um = 0.0
        if e_bal >= 0:
            ch = min(e_bal, ch_lim, (cap - soc) / eta_c)
            cu = e_bal - ch
            if cu > 0 and eg > 0:        # the set throttles back before PV is shed
                r = min(cu, eg)
                eg -= r
                cu -= r
            soc += ch * eta_c
        else:
            need = -e_bal
            ds = min(need, max(soc - floor, 0.0) * eta_d)
            um = need - ds
            soc -= ds / eta_d

        # every hour: PV used + genset + discharge + unmet = load + charge
        err = (p - cu) + eg + ds + um - (l + ch)
        if abs(err) > 1e-6:
            raise AssertionError(f"energy balance off by {err:.3g} kWh at {index[i]}")

        if on:
            run += f
            if reached and run >= min_run - tol:
                on = False
        soc_end[i], frac[i], egen[i] = soc, f, eg
        chg[i], dis[i], curt[i], unmet[i] = ch, ds, cu, um

    h = pd.DataFrame({"pv": pv, "load": ld, "pv_used": np.array(pv) - np.array(curt),
                      "curtailed": curt, "gen_dc": egen, "gen_frac": frac,
                      "charge": chg, "discharge": dis, "unmet": unmet,
                      "soc": np.array(soc_end) / cap, "start": start}, index=index)
    frac_a = h["gen_frac"].to_numpy()
    p_ac = np.where(frac_a > 0, h["gen_dc"].to_numpy() / np.maximum(frac_a, 1e-12)
                    / g["eta_rect"], 0.0)
    h["gen_ac_kw"] = p_ac
    h["fuel_l"] = frac_a * fuel_l_h(p_ac, g)
    h["wet_stack_h"] = np.where((frac_a > 0) & (p_ac < g["wet_stack_frac"]
                                                * g["prime_kw"]), frac_a, 0.0)
    return h


def tank(fuel_l, site, tank_l):
    """Fuel level bookkeeping: first fill, refill to full at the SMU refuel
    threshold. Returns the refill timestamps."""
    t = site["tank"]
    level = float(t["first_fill_l"])
    at = t["refill_at_frac"] * tank_l
    refills = []
    f = fuel_l.to_numpy()
    for i in np.flatnonzero(f > 0):
        level -= f[i]
        if level <= at:
            refills.append(fuel_l.index[i])
            level = tank_l
    return refills


def longest_gap_days(h):
    """Longest stretch without the genset running, in days."""
    run = h["gen_frac"].to_numpy() > 0
    idx = np.flatnonzero(run)
    if len(idx) < 2:
        return len(run) / 24.0
    edges = np.concatenate([[idx[0]], np.diff(idx), [len(run) - idx[-1]]])
    return float(edges.max()) / 24.0


def summarise(h, site, tank_l):
    """Per-year table and the KPIs the tender quotes."""
    local = h.index.tz_convert("Europe/Sarajevo")
    y = h.groupby(local.year)
    years = pd.DataFrame({
        "pv_kwh": y["pv"].sum(), "pv_used_kwh": y["pv_used"].sum(),
        "curtailed_kwh": y["curtailed"].sum(), "load_kwh": y["load"].sum(),
        "gen_dc_kwh": y["gen_dc"].sum(), "genset_h": y["gen_frac"].sum(),
        "starts": y["start"].sum(), "fuel_l": y["fuel_l"].sum(),
        "wet_stack_h": y["wet_stack_h"].sum(), "unmet_kwh": y["unmet"].sum(),
        "discharge_kwh": y["discharge"].sum(), "soc_min": y["soc"].min(),
    })
    cap = site["battery"]["modules"] * site["battery"]["kwh_per_module"]
    years["cycles"] = years["discharge_kwh"] / cap
    # years only partly covered (the UTC -> local shift at the ends) are dropped
    counts = y.size()
    years = years[counts >= 8700]

    refills = tank(h["fuel_l"], site, tank_l)
    rf = pd.Series(1, index=pd.DatetimeIndex(refills)).tz_convert(
        "Europe/Sarajevo") if refills else pd.Series(dtype=float)
    years["refills"] = [int((rf.index.year == yr).sum()) if len(rf) else 0
                        for yr in years.index]
    gaps = np.diff(pd.DatetimeIndex(refills).asi8) / 86400e9 if len(refills) > 1 \
        else np.array([])

    m = h.groupby([local.year, local.month])
    monthly = pd.DataFrame({"pv_kwh": m["pv"].sum(), "pv_used_kwh": m["pv_used"].sum(),
                            "load_kwh": m["load"].sum(), "gen_dc_kwh": m["gen_dc"].sum(),
                            "genset_h": m["gen_frac"].sum(), "fuel_l": m["fuel_l"].sum()})
    monthly.index.names = ["year", "month"]
    monthly = monthly[monthly.index.get_level_values("year").isin(years.index)]
    mm = monthly.groupby(level="month").mean()

    lim = site["limits"]
    gh, fl = years["genset_h"], years["fuel_l"]
    k = {
        "years": [int(years.index.min()), int(years.index.max())],
        "n_years": int(len(years)),
        "pv_bus_kwh": float(years["pv_kwh"].mean()),
        "pv_used_kwh": float(years["pv_used_kwh"].mean()),
        "curtailed_kwh": float(years["curtailed_kwh"].mean()),
        "load_kwh": float(years["load_kwh"].mean()),
        "solar_fraction": float((years["load_kwh"] - years["gen_dc_kwh"]).sum()
                                / years["load_kwh"].sum()),
        "gen_dc_kwh": float(years["gen_dc_kwh"].mean()),
        "genset_h_mean": float(gh.mean()), "genset_h_p90": float(gh.quantile(0.9)),
        "genset_h_max": float(gh.max()), "genset_h_max_year": int(gh.idxmax()),
        "starts_mean": float(years["starts"].mean()),
        "starts_max": int(years["starts"].max()),
        "fuel_l_mean": float(fl.mean()), "fuel_l_p90": float(fl.quantile(0.9)),
        "fuel_l_max": float(fl.max()),
        "tank_years_mean": float(tank_l / fl.mean()) if fl.mean() > 0 else None,
        "tank_years_worst": float(tank_l / fl.max()) if fl.max() > 0 else None,
        "refills_mean": float(years["refills"].mean()),
        "refills_max": int(years["refills"].max()),
        "refill_interval_min_days": float(gaps.min()) if len(gaps) else None,
        "wet_stack_h_mean": float(years["wet_stack_h"].mean()),
        "cycles_mean": float(years["cycles"].mean()),
        "unmet_kwh_total": float(years["unmet_kwh"].sum()),
        "soc_min": float(years["soc_min"].min()),
        "longest_genset_free_days": longest_gap_days(h),
        "dec_pv_kwh": float(mm.loc[12, "pv_kwh"]),
        "dec_load_kwh": float(mm.loc[12, "load_kwh"]),
        "dec_gen_dc_kwh": float(mm.loc[12, "gen_dc_kwh"]),
        "worst_month_genset_h": float(monthly["genset_h"].max()),
        "worst_month": [int(v) for v in monthly["genset_h"].idxmax()],
    }
    k["pass_genset_h"] = bool(k["genset_h_p90"] <= lim["genset_h_max"])
    k["pass_genset_h_worst"] = bool(k["genset_h_max"] <= lim["genset_h_max"])
    k["pass_tank_year"] = bool(k["tank_years_mean"] is None
                               or k["tank_years_mean"] >= lim["tank_years_min"])
    k["pass_tank_year_worst"] = bool(k["tank_years_worst"] is None
                                     or k["tank_years_worst"] >= lim["tank_years_min"])
    return k, years, monthly
