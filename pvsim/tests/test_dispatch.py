"""Synthetic cases where the right answer is known without running PVGIS."""
import numpy as np
import pandas as pd
import pytest

from pvsim import config, dispatch

HOURS = 24 * 60


def _site(**over):
    s = config.load("sjednica")
    for k, v in over.items():
        config.set_path(s, k, v)
    return s


def _index(n=HOURS):
    return pd.date_range("2021-01-01", periods=n, freq="h", tz="UTC")


def test_surplus_pv_never_starts_the_genset():
    s = _site(**{"battery.soc_initial": 1.0})
    idx = _index()
    h = dispatch.simulate(pd.Series(5.0, index=idx), pd.Series(10.0, index=idx), s)
    assert h["gen_frac"].sum() == 0
    assert h["unmet"].sum() == 0
    # full battery: everything above the load is curtailed
    assert h["curtailed"].sum() == pytest.approx((5.0 - h["load"]).sum(), rel=1e-9)


def test_no_pv_cycles_genset_between_start_and_stop():
    s = _site()
    idx = _index()
    h = dispatch.simulate(pd.Series(0.0, index=idx), pd.Series(10.0, index=idx), s)
    assert h["unmet"].sum() == 0
    cap = s["battery"]["modules"] * s["battery"]["kwh_per_module"]
    assert h["soc"].min() >= (1 - s["control"]["dod_start"]) - h["load"].max() / cap - 1e-9
    assert h["start"].sum() >= 3
    # with no PV every kWh of load comes from the genset, less what the
    # battery held at the start, plus storage losses
    b = s["battery"]
    delivered = h["gen_dc"].sum()
    assert delivered > h["load"].sum() - b["soc_initial"] * cap
    # the set runs at the rectifier cap or the charge limit, never above
    cap_dc = s["genset"]["rect_cap_ac_kw"] * s["genset"]["eta_rect"]
    run = h["gen_frac"] > 0
    assert (h.loc[run, "gen_dc"] / h.loc[run, "gen_frac"] <= cap_dc + 1e-9).all()


def test_energy_balance_on_random_series():
    s = _site()
    idx = _index(24 * 365)
    rng = np.random.default_rng(7)
    day = np.clip(np.sin((idx.hour - 6) / 12 * np.pi), 0, None)
    pv = pd.Series(day * rng.uniform(0, 6, len(idx)), index=idx)
    t = pd.Series(rng.uniform(-10, 38, len(idx)), index=idx)
    h = dispatch.simulate(pv, t, s)
    b = s["battery"]
    cap = b["modules"] * b["kwh_per_module"]
    stored = (h["charge"] * b["eta_charge"] - h["discharge"] / b["eta_discharge"]).sum()
    assert stored == pytest.approx((h["soc"].iloc[-1] - b["soc_initial"]) * cap, abs=1e-6)
    lhs = h["pv_used"] + h["gen_dc"] + h["discharge"] + h["unmet"]
    rhs = h["load"] + h["charge"]
    assert np.max(np.abs(lhs - rhs)) < 1e-6
    assert h["unmet"].sum() == 0


def test_fuel_curve_matches_datasheet_points():
    g = config.load("sjednica")["genset"]
    assert dispatch.fuel_l_h(np.array([6.6, 9.9, 13.2]), g) == pytest.approx([2.6, 3.4, 4.4])
    assert 0.8 < float(dispatch.fuel_l_h(0.0, g)) < 1.2      # idle, extrapolated


def test_cooling_ramp():
    s = config.load("sjednica")
    kw = dispatch.load_kw(np.array([0.0, 27.5, 40.0]), s)
    assert kw == pytest.approx([1.200, 1.275, 1.350])
