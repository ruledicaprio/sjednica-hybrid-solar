"""The PV model against PVGIS, per site and tilt.

Runs from the cache (python -m pvsim fetch --site <id>); a site whose series is
not cached is skipped here and covered by `pytest -m network`, which fetches.
"""
import numpy as np
import pytest

from pvsim import config, pv, pvgis

CASES = [(s, t) for s in ("sjednica", "hamzici") for t in (45, 60)]


def _load(site_id, tilt, offline):
    s = config.with_tilt(config.load(site_id), tilt)
    try:
        df, _ = pvgis.hourly(s, tilt, 180, offline=offline)
        ref = pvgis.pvcalc(s, tilt, 180, offline=offline)
    except pvgis.OfflineMiss:
        pytest.skip(f"{site_id} {tilt}° not cached - run python -m pvsim fetch")
    return s, df, ref


def _check(s, df, ref, tilt):
    n = len(set(df.index.year))
    ours = pv.pvgis_equivalent(df, s, tilt, 180, 14.0)
    e_m = {m["month"]: m["E_m"] for m in ref["outputs"]["monthly"]["fixed"]}
    mo = ours.groupby(ours.index.month).sum() / 1000 / n
    for m in range(1, 13):
        assert mo[m] == pytest.approx(e_m[m], rel=0.03), f"month {m}"
    e_y = ref["outputs"]["totals"]["fixed"]["E_y"]
    assert ours.sum() / 1000 / n == pytest.approx(e_y, rel=0.02)
    assert np.corrcoef(ours, df["P"])[0, 1] > 0.99
    assert e_y / s["array"]["kWp"] < 1800


@pytest.mark.parametrize("site_id,tilt", CASES)
def test_parity_cached(site_id, tilt):
    s, df, ref = _load(site_id, tilt, offline=True)
    _check(s, df, ref, tilt)


@pytest.mark.network
@pytest.mark.parametrize("site_id,tilt", CASES)
def test_parity_network(site_id, tilt):
    s, df, ref = _load(site_id, tilt, offline=False)
    _check(s, df, ref, tilt)


def test_sjednica_december_matches_the_plan_figure():
    s, df, ref = _load("sjednica", 45, offline=True)
    dec = {m["month"]: m["E_m"] for m in ref["outputs"]["monthly"]["fixed"]}[12]
    assert dec == pytest.approx(562, abs=5)
