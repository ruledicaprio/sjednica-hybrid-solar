"""Figures for the tender annexes - Bosnian labels, decimal comma.

Print figures (PNG for the .docx / A3 PDF), so no hover layer; every value a
figure shows is also in a table of 07-proracuni, which is the table view.

Colour follows the entity across every figure, from the reference palette of
the dataviz method, validated with its script (light surface):
  PV = slot 1 blue, genset = slot 2 orange, 60° variant = slot 3 aqua
  (blue/orange/aqua: worst adjacent CVD dE 9,2, normal-vision 27,6; aqua sits
  below 3:1 on the surface, so it is always direct-labelled).
Limits and the load are reference lines in ink, labelled in place.
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt                                     # noqa: E402
import numpy as np                                                  # noqa: E402
import pandas as pd                                                 # noqa: E402
from matplotlib.colors import LinearSegmentedColormap              # noqa: E402
from matplotlib.ticker import FuncFormatter                         # noqa: E402

BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#898781"
GRID, BASE, SURFACE = "#e1e0d9", "#c3c2b7", "#ffffff"
MONTHS = ["jan", "feb", "mar", "apr", "maj", "jun", "jul", "aug", "sep", "okt",
          "nov", "dec"]
DPI = 220
# one-hue orange ramp for genset magnitude (sequential: light -> dark)
GEN_RAMP = LinearSegmentedColormap.from_list(
    "dea", ["#ffffff", "#fbd9cb", "#f2a07d", ORANGE, "#b8461a", "#7a2a0c"])


def num(v, nd=0):
    """1234.5 -> '1 234,5' (thin space, decimal comma)."""
    s = f"{v:,.{nd}f}"
    return s.replace(",", " ").replace(".", ",")


def _style():
    plt.rcParams.update({
        "font.family": ["Segoe UI", "Arial", "DejaVu Sans"], "font.size": 8.5,
        "axes.edgecolor": BASE, "axes.linewidth": 0.8, "axes.labelcolor": INK2,
        "axes.titlesize": 9.5, "axes.titleweight": "semibold", "axes.titlecolor": INK,
        "axes.titlelocation": "left", "axes.spines.top": False,
        "axes.spines.right": False, "axes.grid": True, "axes.grid.axis": "y",
        "grid.color": GRID, "grid.linewidth": 0.7, "axes.axisbelow": True,
        "xtick.color": MUTED, "ytick.color": MUTED, "xtick.labelcolor": INK2,
        "ytick.labelcolor": INK2, "legend.frameon": False,
        "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
        "savefig.facecolor": SURFACE,
    })


def _yfmt(ax, nd=0):
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: num(v, nd)))


def _save(fig, path):
    fig.savefig(path, dpi=DPI, bbox_inches="tight", pad_inches=0.06)
    plt.close(fig)
    return path


def _span(monthly):
    ys = monthly.index.get_level_values("year")
    return f"{ys.min()}–{ys.max()}"


# --------------------------------------------------------------------------
def f1_monthly(monthly, title, path):
    """Monthly mean PV on the bus and genset energy against the load, with the
    range over all simulated years as a whisker."""
    _style()
    g = monthly.groupby(level="month")
    pv_m, pv_lo, pv_hi = g["pv_kwh"].mean(), g["pv_kwh"].min(), g["pv_kwh"].max()
    ge_m, ge_lo, ge_hi = (g["gen_dc_kwh"].mean(), g["gen_dc_kwh"].min(),
                          g["gen_dc_kwh"].max())
    ld = g["load_kwh"].mean()
    x = np.arange(12)
    fig, ax = plt.subplots(figsize=(6.9, 3.3))
    ax.bar(x - 0.2, pv_m, 0.37, color=BLUE, label="FN na DC sabirnici")
    ax.bar(x + 0.2, ge_m, 0.37, color=ORANGE, label="DEA preko ispravljača")
    ax.vlines(x - 0.2, pv_lo, pv_hi, color=INK, lw=0.8)
    ax.vlines(x + 0.2, ge_lo, ge_hi, color=INK, lw=0.8)
    ax.plot(x, ld, color=INK, lw=1.5, marker="o", ms=3.2, label="Potrošnja")
    ax.set_xticks(x, MONTHS)
    ax.set_ylabel("kWh / mjesec")
    _yfmt(ax)
    ax.set_title(title)
    ax.text(0.0, -0.16, f"decembar: FN {num(pv_m[12])} kWh · potrošnja {num(ld[12])} kWh"
            f" · DEA {num(ge_m[12])} kWh", transform=ax.transAxes, ha="left",
            fontsize=7.4, color=INK2)
    ax.legend(loc="upper left", ncol=3, fontsize=7.8, handlelength=1.4)
    ax.text(1.0, -0.16, f"stubić = raspon {_span(monthly)}; stupac = prosjek",
            transform=ax.transAxes, ha="right", fontsize=7, color=MUTED)
    ax.set_ylim(0, max(pv_hi.max(), ld.max()) * 1.18)
    return _save(fig, path)


def f2_horizon(site, horizon, path, user_horizon=None, markers=()):
    """Horizon (DEM, optionally a photo-derived obstacle) with the sun paths
    of the solstices and equinox, local solar time ticks on 21 December."""
    import pvlib

    _style()
    fig, ax = plt.subplots(figsize=(6.9, 2.9))
    az = np.asarray(horizon["azimuth"], float)
    el = np.asarray(horizon["elevation"], float)
    order = np.argsort(az)
    az, el = np.r_[az[order], 360.0], np.r_[el[order], el[order][0]]
    ax.fill_between(az, 0, el, color=GRID, lw=0)
    ax.plot(az, el, color=INK2, lw=1.0)
    ax.text(62, max(el[(az > 55) & (az < 90)].max(), 0.5) + 1.2, "horizont (PVGIS DEM)",
            fontsize=7.5, color=INK2)
    if user_horizon is not None:
        uaz = np.linspace(0, 360, len(user_horizon), endpoint=False)
        uel = np.maximum(np.asarray(user_horizon, float), np.interp(uaz, az, el))
        ax.fill_between(np.r_[uaz, 360], 0, np.r_[uel, uel[0]], color=MUTED,
                        alpha=0.45, lw=0)
    for m in markers:
        ax.plot(m["az"], m["el"], "o", ms=5, color=INK, mec=SURFACE, mew=1.5)
        ax.annotate(m["label"], (m["az"], m["el"]), xytext=(-8, 6), ha="right",
                    textcoords="offset points", fontsize=7.5, color=INK)

    year = 2023
    for date, label in ((f"{year}-12-21", "21. dec"), (f"{year}-03-20", "20. mar / 22. sep"),
                        (f"{year}-06-21", "21. jun")):
        t = pd.date_range(date, periods=24 * 12, freq="5min", tz="UTC")
        sp = pvlib.solarposition.get_solarposition(t, site["lat"], site["lon"],
                                                   altitude=site["altitude_m"])
        up = sp["apparent_elevation"] > 0
        ax.plot(sp["azimuth"][up], sp["apparent_elevation"][up], color=INK, lw=1.5)
        top = sp["apparent_elevation"].idxmax()
        ax.annotate(label, (sp.loc[top, "azimuth"], sp.loc[top, "apparent_elevation"]),
                    xytext=(0, 4), textcoords="offset points", ha="center",
                    fontsize=7.5, color=INK2)
        if label.startswith("21. dec"):
            hrs = sp[up & (t.minute == 0)]
            local = hrs.index.tz_convert("Europe/Sarajevo")
            ax.plot(hrs["azimuth"], hrs["apparent_elevation"], "o", ms=3.5, color=INK,
                    mec=SURFACE, mew=1.2)
            for (i, r), lt in zip(hrs.iterrows(), local):
                if lt.hour % 2 == 0:
                    ax.annotate(f"{lt.hour}h", (r["azimuth"], r["apparent_elevation"]),
                                xytext=(0, -10), textcoords="offset points",
                                ha="center", fontsize=6.8, color=MUTED)
    ax.axvline(180, color=BASE, lw=0.8)
    ax.set_xlim(45, 315)
    ax.set_ylim(0, 75)
    ax.set_xticks([60, 90, 120, 150, 180, 210, 240, 270, 300],
                  ["60", "I 90", "120", "150", "J 180", "210", "240", "Z 270", "300"])
    ax.set_xlabel("azimut (°)")
    ax.set_ylabel("visina (°)")
    ax.grid(axis="x", color=GRID, lw=0.7)
    ax.set_title(f"{site['name']} — horizont i putanje Sunca")
    return _save(fig, path)


def f3_heatmap(hourly, title, path):
    """Genset hours per day, one row per year - where in the year the set runs
    and how that moves from year to year."""
    _style()
    local = hourly.index.tz_convert("Europe/Sarajevo")
    daily = hourly["gen_frac"].groupby([local.year, local.dayofyear]).sum()
    grid = daily.unstack(level=1).reindex(columns=range(1, 367)).fillna(0.0)
    hours = hourly["gen_frac"].groupby(local.year).size()
    grid = grid.loc[hours[hours >= 8700].index]      # drop the UTC-shift stubs
    fig, ax = plt.subplots(figsize=(6.9, 3.0))
    im = ax.imshow(grid.to_numpy(), aspect="auto", cmap=GEN_RAMP, vmin=0,
                   vmax=max(4.0, float(grid.to_numpy().max())), interpolation="nearest")
    ax.set_yticks(range(len(grid.index)), [str(y) for y in grid.index], fontsize=6.5)
    starts = pd.date_range("2023-01-01", periods=12, freq="MS").dayofyear - 1
    ax.set_xticks(starts, MONTHS)
    ax.grid(False)
    cb = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.01)
    cb.set_label("DEA h / dan", color=INK2)
    cb.outline.set_visible(False)
    cb.ax.tick_params(colors=MUTED, labelsize=7)
    ax.set_title(title)
    return _save(fig, path)


def f4_years(years, limits, tank_l, title, path):
    """Genset hours and fuel per year against the tender limits - two panels,
    never one plot with two y-scales."""
    _style()
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.9, 4.2), sharex=True)
    x = years.index.to_numpy()
    # The 250 h line is the RFI figure the design was first judged against; since
    # Rev 9 the TD no longer states it as a limit, so it is labelled as what it is.
    for ax, col, lim, lim_label, unit in (
            (a1, "genset_h", limits["genset_h_max"], f"RFI: {limits['genset_h_max']} h",
             "rad DEA, h / god"),
            (a2, "fuel_l", tank_l, f"spremnik {tank_l} l", "gorivo, l / god")):
        v = years[col].to_numpy()
        mean, top = v.mean(), max(v.max(), lim) * 1.16
        ax.bar(x, v, 0.62, color=ORANGE)
        ax.axhline(lim, color=INK, lw=1.2)
        ax.axhline(mean, color=MUTED, lw=0.8)
        # two reference lines close together: the upper label sits above its
        # line and the lower one below, instead of printing over each other
        close = abs(mean - lim) < 0.08 * top
        va_lim = ("bottom" if lim > mean else "top") if close else "center"
        va_mean = ("bottom" if mean >= lim else "top") if close else "center"
        ax.text(x[-1] + 0.45, lim, lim_label, va=va_lim, fontsize=7, color=INK)
        ax.text(x[-1] + 0.45, mean, f"prosjek {num(mean)}", va=va_mean, fontsize=7,
                color=MUTED)
        i = int(np.argmax(v))
        ax.annotate(num(v[i]), (x[i], v[i]), xytext=(0, 2), textcoords="offset points",
                    ha="center", fontsize=7.5, color=INK2)
        ax.set_ylabel(unit)
        _yfmt(ax)
        ax.set_ylim(0, top)
    a1.set_title(title)
    a2.set_xticks(x, [str(y) for y in x], rotation=90, fontsize=7)
    return _save(fig, path)


def f5_waterfall(waterfall, title, path):
    """From 'irradiance x kWp' to the energy delivered to the -48 V bus."""
    _style()
    rows = list(waterfall)
    fig, ax = plt.subplots(figsize=(6.9, 3.2))
    y = np.arange(len(rows))[::-1]
    first, last = rows[0]["kwh"], rows[-1]["kwh"]
    for yy, r in zip(y, rows):
        if r["loss_kwh"] is None:
            ax.barh(yy, r["kwh"], 0.56, color=BLUE)
            ax.text(r["kwh"], yy, f"  {num(r['kwh'])} kWh", va="center", fontsize=7.5,
                    color=INK2)
        else:
            ax.barh(yy, r["loss_kwh"], 0.56, left=r["kwh"], color=MUTED)
            pct = "0,0 %" if r["loss_pct"] < 0.05 else f"−{num(r['loss_pct'], 1)} %"
            ax.text(r["kwh"] + r["loss_kwh"], yy, f"  {pct}", va="center", fontsize=7.5,
                    color=INK2)
    ax.barh(y[-1] - 1.1, last, 0.56, color=BLUE)
    ax.text(last, y[-1] - 1.1, f"  {num(last)} kWh = {num(100 * last / first, 1)} %",
            va="center", fontsize=7.5, color=INK2)
    labels = [r["label"] for r in rows] + ["Na DC sabirnici (−48 V)"]
    ax.set_yticks(list(y) + [y[-1] - 1.1], labels)
    ax.grid(axis="x", color=GRID, lw=0.7)
    ax.grid(axis="y", visible=False)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: num(v)))
    ax.set_xlim(0, first * 1.2)
    ax.set_xlabel("kWh / god (prosjek)")
    ax.set_title(title)
    return _save(fig, path)


def f6_tilts(results, site_name, limits, path):
    """45° against 60°: annual PV, December PV and genset hours (mean with the
    P90-max range)."""
    _style()
    tilts = sorted(results)
    colors = {tilts[0]: BLUE, tilts[-1]: AQUA}
    fig, axes = plt.subplots(1, 3, figsize=(6.9, 2.6))
    panels = (("pv_bus_kwh", "FN na sabirnici, kWh/god", None),
              ("dec_pv_kwh", "FN u decembru, kWh\nlinija = potrošnja", "dec_load_kwh"),
              ("genset_h_mean", f"DEA, h/god\nlinija = RFI {limits['genset_h_max']} h",
               "genset"))
    for ax, (key, label, ref) in zip(axes, panels):
        for i, t in enumerate(tilts):
            k = results[t]
            v = k[key]
            ax.bar(i, v, 0.56, color=colors[t])
            if ref == "genset":
                ax.vlines(i, k["genset_h_p90"], k["genset_h_max"], color=INK, lw=1.6)
                ax.text(i + 0.06, k["genset_h_max"], f"P90–max\n{num(k['genset_h_p90'])}–"
                        f"{num(k['genset_h_max'])}", fontsize=6.5, color=MUTED,
                        va="bottom")
            ax.text(i, v, num(v), ha="center", va="bottom", fontsize=7.5, color=INK2)
        if ref == "dec_load_kwh":
            ax.axhline(results[tilts[0]]["dec_load_kwh"], color=INK, lw=1.2)
        if ref == "genset":
            ax.axhline(limits["genset_h_max"], color=INK, lw=1.2)
        ax.set_xticks(range(len(tilts)), [f"{t:g}°" for t in tilts])
        ax.set_title(label, fontsize=8, fontweight="normal", color=INK2)
        _yfmt(ax)
        top = max(results[t][key] for t in tilts)
        if ref == "genset":
            top = max(top, limits["genset_h_max"], *(results[t]["genset_h_max"]
                                                     for t in tilts)) * 1.12
        if ref == "dec_load_kwh":
            top = max(top, results[tilts[0]]["dec_load_kwh"])
        ax.set_ylim(0, top * 1.2)
        ax.set_xlim(-0.6, len(tilts) - 0.4)
    fig.suptitle(f"{site_name} — nagib {tilts[0]:g}° i {tilts[-1]:g}°", x=0.01, ha="left",
                 fontsize=9.5, fontweight="semibold", color=INK)
    fig.tight_layout()
    return _save(fig, path)
