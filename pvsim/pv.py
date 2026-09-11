"""PV chain: PVGIS plane-of-array irradiance -> DC power on the -48 V bus.

The irradiance is PVGIS's own plane-of-array beam / sky / ground split, which
already carries the transposition and the horizon (DEM, or a user horizon from
the photo survey). PVGIS folds everything after that into one flat "system
loss" of 14 %. This module replaces that figure with the individual losses:
reflection (IAM), module temperature and low light (Huld c-Si model), soiling,
snow, mismatch, LID, DC wiring, the per-module optimizers and the measured
efficiency curve of the iSSU S4875G2 DC/DC converters feeding the bus.

`pvgis_equivalent()` runs the same module model with PVGIS's flat loss instead,
so the chain can be checked hour by hour against the P that PVGIS reports.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pvlib


def tilt_table(table, tilt):
    """Monthly factors given per tilt ({"45": [...12], "60": [...12]}),
    interpolated linearly between the listed tilts and held flat outside."""
    keys = sorted(table, key=float)
    xs = np.array([float(k) for k in keys])
    arr = np.array([table[k] for k in keys], dtype=float)
    return np.array([np.interp(tilt, xs, arr[:, m]) for m in range(12)])


def solar_position(index, site):
    return pvlib.solarposition.get_solarposition(index, site["lat"], site["lon"],
                                                 altitude=site["altitude_m"])


def effective_irradiance(df, site, tilt, azimuth):
    """(irradiance reaching the cells after reflection, total plane-of-array
    irradiance), both W/m²."""
    sp = solar_position(df.index, site)
    aoi = pvlib.irradiance.aoi(tilt, azimuth, sp["apparent_zenith"], sp["azimuth"])
    a_r = site["pv"]["iam_a_r"]
    iam_b = np.asarray(pvlib.iam.martin_ruiz(aoi, a_r=a_r), dtype=float)
    iam_sky, iam_gnd = pvlib.iam.martin_ruiz_diffuse(tilt, a_r=a_r)
    b = df["poa_direct"].to_numpy(float)
    d = df["poa_sky_diffuse"].to_numpy(float)
    g = df["poa_ground_diffuse"].to_numpy(float)
    return b * iam_b + d * float(iam_sky) + g * float(iam_gnd), b + d + g


def module_temperature(poa, df, site):
    pv = site["pv"]
    return np.asarray(pvlib.temperature.faiman(
        poa, df["temp_air"].to_numpy(float), df["wind_speed"].to_numpy(float),
        u0=pv["faiman_u0"], u1=pv["faiman_u1"]), dtype=float)


def huld_dc(geff, tmod, pdc0, k_version):
    """Huld c-Si DC power (W). The model takes log(G), so G = 0 is masked
    rather than passed through as -inf."""
    out = np.zeros_like(geff, dtype=float)
    ok = geff > 0.5
    out[ok] = pvlib.pvarray.huld(geff[ok], tmod[ok], pdc0, cell_type="csi",
                                 k_version=k_version)
    return np.clip(out, 0.0, None)


def pvgis_equivalent(df, site, tilt, azimuth=180, loss_pct=14.0):
    """The PVGIS model with its flat loss: comparable hour by hour with the
    P column PVGIS returns for the same plane and loss."""
    geff, poa = effective_irradiance(df, site, tilt, azimuth)
    tmod = module_temperature(poa, df, site)
    p = huld_dc(geff, tmod, site["array"]["kWp"] * 1000.0,
                site["pv"]["huld_k_version"])
    return pd.Series(p * (1 - loss_pct / 100.0), index=df.index, name="P_model")


# --------------------------------------------------------------------------
class ISSU:
    """iSSU S4875G2 efficiency from the datasheet curve.

    The digitised curve (output current -> efficiency) is converted to losses
    in watts and interpolated linearly between the points, so the model IS the
    datasheet at every point. (A quadratic loss fit was tried first; it missed
    the steep light-load end by 0,6 %.) Below the first point (10,5 A) the
    loss is held at that point's value, ~44 W: at light load the fixed losses -
    control, gate drive, fans - dominate, and holding them is the conservative
    reading of a curve that stops at 10 A. Above the last point the final
    segment is extended; the 4 kW output limit sits just below it anyway.
    """

    def __init__(self, cfg):
        a = np.array(cfg["curve_a_pct"], dtype=float)
        self.pout_pts = a[:, 0] * cfg["v_out"]
        self.eta_pts = a[:, 1] / 100.0
        self.loss_pts = self.pout_pts / self.eta_pts - self.pout_pts
        self.cfg = cfg
        # input as a function of output is monotonic, so it is inverted on a
        # fine grid rather than solved piecewise
        self._pout_grid = np.linspace(0.0, 1.25 * cfg["p_out_max_w"], 20001)
        self._pin_grid = self._pout_grid + self.loss(self._pout_grid)
        if not np.all(np.diff(self._pin_grid) > 0):
            raise ValueError("iSSU curve gives a non-monotonic input power")

    @property
    def fixed_loss_w(self):
        return float(self.loss_pts[0])

    def loss(self, pout):
        pout = np.asarray(pout, dtype=float)
        x, y = self.pout_pts, self.loss_pts
        slope = (y[-1] - y[-2]) / (x[-1] - x[-2])
        return np.where(pout > x[-1], y[-1] + slope * (pout - x[-1]),
                        np.interp(pout, x, y))

    def efficiency(self, pout):
        pout = np.asarray(pout, dtype=float)
        return pout / (pout + self.loss(pout))

    def p_max(self, t_cabinet):
        d = np.array(self.cfg["derate_c_w"], dtype=float)
        return np.interp(t_cabinet, d[:, 0], d[:, 1],
                         left=self.cfg["p_out_max_w"], right=0.0)

    def output(self, p_in, t_cabinet):
        """(output W, clipped input W) for input power p_in per unit."""
        p_in = np.asarray(p_in, dtype=float)
        pout = np.where(p_in > self._pin_grid[0],
                        np.interp(p_in, self._pin_grid, self._pout_grid), 0.0)
        cap = self.p_max(t_cabinet)
        over = pout > cap
        clipped = np.where(over, p_in - (cap + self.loss(cap)), 0.0)
        return np.where(over, cap, pout), np.maximum(clipped, 0.0)


STAGES = [
    ("stc", "Ozračenje u ravni × kWp (STC)"),
    ("iam", "Refleksija (IAM)"),
    ("temp", "Temperatura i slabo svjetlo (Huld)"),
    ("soiling", "Zaprljanje"),
    ("snow", "Snijeg"),
    ("mm_lid", "Neusklađenost + LID"),
    ("wiring", "DC kablovi"),
    ("optimizer", "Optimizatori"),
    ("issu", "iSSU S4875G2 (krivulja)"),
    ("clip", "iSSU ograničenje 4 kW"),
]


def dc_chain(df, site, tilt, azimuth=180):
    """Hourly DC power delivered to the -48 V bus (W) and the loss stages.

    Returns (DataFrame with 'p_bus' and the stage powers, dict of the ISSU fit).
    """
    pv = site["pv"]
    pdc0 = site["array"]["kWp"] * 1000.0
    geff, poa = effective_irradiance(df, site, tilt, azimuth)
    tmod = module_temperature(poa, df, site)
    p_huld = huld_dc(geff, tmod, pdc0, pv["huld_k_version"])

    month = df.index.month.to_numpy() - 1
    soil = np.asarray(pv["soiling_monthly"], dtype=float)[month]
    snow = tilt_table(pv["snow_monthly"], tilt)[month]

    p_soil = p_huld * (1 - soil)
    p_snow = p_soil * (1 - snow)
    p_mm = p_snow * (1 - pv["mismatch"]) * (1 - pv["lid"])
    p_wire = p_mm * (1 - pv["dc_wiring_stc"] * (p_mm / pdc0))
    p_opt = p_wire * pv["optimizer_eff"]

    issu = ISSU(pv["issu"])
    units = pv["issu"]["units"]
    t_cab = df["temp_air"].to_numpy(float) + pv["issu"]["cabinet_rise_c"]
    per_unit, clipped = issu.output(p_opt / units, t_cab)
    p_bus = per_unit * units
    p_clip = clipped * units

    out = pd.DataFrame({
        "poa": poa, "geff": geff, "tmod": tmod,
        "stc": poa / 1000.0 * pdc0, "iam": geff / 1000.0 * pdc0,
        "temp": p_huld, "soiling": p_soil, "snow": p_snow, "mm_lid": p_mm,
        "wiring": p_wire, "optimizer": p_opt, "issu": p_bus + p_clip,
        "clip": p_bus, "p_bus": p_bus,
    }, index=df.index)
    fit = {"curve_vin_v": pv["issu"]["curve_vin_v"],
           "curve_points": int(len(issu.pout_pts)),
           "fixed_loss_w": issu.fixed_loss_w}
    return out, fit


def loss_waterfall(chain, years):
    """Mean annual energy (kWh) after each stage, and the loss of each stage."""
    rows, prev = [], None
    for key, label in STAGES:
        e = float(chain[key].sum()) / 1000.0 / years
        rows.append({"stage": key, "label": label, "kwh": e,
                     "loss_kwh": None if prev is None else prev - e,
                     "loss_pct": None if prev is None else 100 * (prev - e) / prev})
        prev = e
    return rows
