"""The model in two steps, so a sensitivity run can reuse the PV half.

  pv_series()  PVGIS hourly -> PV chain -> DC power on the bus (per tilt)
  dispatch()   bus power + temperature -> 19-year dispatch -> KPIs
"""
from __future__ import annotations

import copy

from pvsim import config, dispatch as _dispatch, pv, pvgis


def pv_series(site, tilt, offline=False):
    """(bus power kW, air temperature, chain DataFrame, iSSU fit, years)."""
    s = config.with_tilt(site, tilt)
    az = s["array"]["azimuth_deg"]
    df, _ = pvgis.hourly(s, tilt, az, offline=offline)
    chain, fit = pv.dc_chain(df, s, tilt, az)
    return chain["p_bus"] / 1000.0, df["temp_air"], chain, fit, len(set(df.index.year))


def dispatch(site, pv_kw, temp_air, overrides=None):
    """(kpis, years, monthly, hourly) for one set of control/battery/load
    parameters; `overrides` is {dotted.key: value}."""
    s = copy.deepcopy(site)
    for key, val in (overrides or {}).items():
        config.set_path(s, key, val)
    h = _dispatch.simulate(pv_kw, temp_air, s)
    k, years, monthly = _dispatch.summarise(h, s, s["design"]["tank"]["litres"])
    return k, years, monthly, h


def run_tilt(site, tilt, offline=False):
    """PV chain + dispatch for one tilt; returns (kpis, years, monthly, chain,
    hourly, waterfall)."""
    pv_kw, temp, chain, fit, n_years = pv_series(site, tilt, offline)
    s = config.with_tilt(site, tilt)
    k, years, monthly, h = dispatch(s, pv_kw, temp)
    k.update({"site": site["id"], "tilt": tilt,
              "specific_yield_bus": k["pv_bus_kwh"] / site["array"]["kWp"],
              "issu_fit": fit})
    return k, years, monthly, chain, h, pv.loss_waterfall(chain, n_years)
