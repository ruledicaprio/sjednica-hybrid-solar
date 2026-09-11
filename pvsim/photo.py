"""Photo survey helper: where the sun was in each site photo, and what the
obstacles seen in the photos do to the array.

The Hamzići photos carry the time and UTC offset but no GPS and no compass
heading (EXIF GPS is NaN on every file), so orientation cannot be read from
them. What the files do give is the exact sun position for each photo; shadow
directions in the pictures are then checked against it by eye, and the
annotated copies carry it in a caption.

Obstacles (the lone tree SSE-SE of the tower) are described in the site JSON
by bearing and distance from the tower, height and crown width - as ranges,
because they are estimates from photos. Each case is projected onto the
horizon seen from the array centre. The beam that falls inside the silhouette
is removed hour by hour from PVGIS's in-plane beam, scaled by a monthly
opacity (a leafless crown passes about half the light), and the sky diffuse is
reduced by the sky the crown hides. PVGIS's own user horizon would treat the
tree as solid rock all year, which overstates a deciduous tree in winter.
"""
from __future__ import annotations

import glob
import json
import math
import os

import numpy as np
import pandas as pd
import pvlib

from pvsim import config, figures, model, pv, pvgis

FIELD_SLOPE_M = 4.576          # 2 x 2278 + 20 mm, both stand layouts


def _exif(path):
    from PIL import Image

    im = Image.open(path)
    ex = im.getexif()
    ifd = ex.get_ifd(0x8769)
    stamp = ifd.get(36867) or ex.get(306)
    off = ifd.get(36881) or "+00:00"
    t = pd.Timestamp(stamp.replace(":", "-", 2) + off)
    return t, im.size, ifd.get(41989)


def sun(site, times):
    sp = pvlib.solarposition.get_solarposition(pd.DatetimeIndex(times), site["lat"],
                                               site["lon"], altitude=site["altitude_m"])
    return sp["azimuth"].to_numpy(), sp["apparent_elevation"].to_numpy()


def photo_table(site):
    folder = os.path.join(config.ROOT, site["photos"]["folder"])
    rows, empty = [], []
    for f in sorted(glob.glob(os.path.join(folder, "*.jpg"))):
        name = os.path.basename(f)
        if os.path.getsize(f) == 0:
            empty.append(name)
            continue
        t, size, f35 = _exif(f)
        az, el = sun(site, [t])
        rows.append({"file": name, "local": t.isoformat(), "sun_az": float(az[0]),
                     "sun_el": float(el[0]), "shadow_az": float((az[0] + 180) % 360),
                     "shadow_per_m": 1 / math.tan(math.radians(el[0])),
                     "focal_35mm": f35, "px": list(size)})
    valid = {r["file"].replace("(1)", "") for r in rows}
    lost = sorted({e.replace("(1)", "") for e in empty} - valid)
    return rows, lost


# --------------------------------------------------------------------------
def cases(obstacle):
    """Unfavourable / middle / favourable reading of an obstacle's ranges.
    Unfavourable = nearest, tallest, and furthest round towards south."""
    b, d, h = obstacle["bearing_deg"], obstacle["dist_m"], obstacle["height_m"]
    return {
        "nepovoljno": {"bearing": max(b), "dist": min(d), "height": max(h)},
        "srednje": {"bearing": sum(b) / 2, "dist": sum(d) / 2, "height": sum(h) / 2},
        "povoljno": {"bearing": min(b), "dist": max(d), "height": min(h)},
    }


def silhouette(site, obstacle, case, tilt):
    """The obstacle as seen from the array centre: azimuth, half-width and top
    elevation (degrees), distance (m)."""
    pos = site["array_position"]
    bottom = site["stands"]["bottom_edge_m"]
    mid = bottom + FIELD_SLOPE_M / 2 * math.sin(math.radians(tilt))
    b = math.radians(case["bearing"])
    de = case["dist"] * math.sin(b) - pos["east_m"]
    dn = case["dist"] * math.cos(b) - pos["north_m"]
    r = math.hypot(de, dn)
    return {"az": math.degrees(math.atan2(de, dn)) % 360,
            "hw": math.degrees(math.atan2(obstacle["crown_w_m"] / 2, r)),
            "el": math.degrees(math.atan2(case["height"] - mid, r)), "r": r}


def shade(df, site, tilt, sil, opacity_monthly):
    """PVGIS in-plane components with the obstacle applied."""
    az, el = sun(site, df.index)
    d = (az - sil["az"] + 180) % 360 - 180
    blocked = (np.abs(d) <= sil["hw"]) & (el > 0) & (el < sil["el"])
    op = np.asarray(opacity_monthly, dtype=float)[df.index.month.to_numpy() - 1]
    out = df.copy()
    out["poa_direct"] = df["poa_direct"] * np.where(blocked, 1 - op, 1.0)
    # isotropic sky hidden by the crown, weighted towards the low southern sky a
    # tilted south plane sees (factor 2) - about a per cent, kept for honesty
    sky_lost = 2 * (2 * sil["hw"] / 360) * math.sin(math.radians(max(sil["el"], 0))) ** 2
    out["poa_sky_diffuse"] = df["poa_sky_diffuse"] * (1 - op * sky_lost)
    return out, float(blocked.mean())


def horizon_for_figure(site, tilt, which="srednje"):
    """(user horizon at 1° steps from north, markers) for figures.f2_horizon."""
    dem = pvgis.horizon(site, offline=True)
    az = np.arange(360.0)
    uh = np.interp(az, dem["azimuth"], dem["elevation"], period=360)
    markers = []
    for ob in site.get("obstacles", []):
        sil = silhouette(site, ob, cases(ob)[which], tilt)
        d = (az - sil["az"] + 180) % 360 - 180
        uh = np.where(np.abs(d) <= sil["hw"], np.maximum(uh, sil["el"]), uh)
        markers.append({"az": sil["az"], "el": sil["el"],
                        "label": f"{ob['name']} (procjena, {which})"})
    return uh.tolist(), markers


# --------------------------------------------------------------------------
def _annotate(src, dst, row):
    from PIL import Image, ImageDraw, ImageFont

    im = Image.open(src)
    im = im.convert("RGB")
    im.thumbnail((1400, 1400))
    bar = 46
    canvas = Image.new("RGB", (im.width, im.height + bar), "white")
    canvas.paste(im, (0, 0))
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype(os.path.join(os.environ.get("WINDIR", r"C:\Windows"),
                                               "Fonts", "arial.ttf"), 20)
    except OSError:
        font = ImageFont.load_default()
    t = pd.Timestamp(row["local"])
    txt = (f"{row['file']} · {t:%d.%m.%Y %H:%M:%S} (UTC{t:%z}) · Sunce: azimut "
           f"{figures.num(row['sun_az'], 1)}°, visina {figures.num(row['sun_el'], 1)}° · "
           f"sjena prema {figures.num(row['shadow_az'], 1)}°, "
           f"{figures.num(row['shadow_per_m'], 2)} m po m visine")
    draw.text((12, im.height + 12), txt, fill=(11, 11, 11), font=font)
    canvas.save(dst, quality=82, optimize=True)


def run(site, offline=False):
    if not site.get("photos"):
        print(f"{site['id']}: no photos configured")
        return 0
    out = os.path.join(config.ROOT, site["review_dir"], "photo")
    os.makedirs(out, exist_ok=True)

    rows, lost = photo_table(site)
    print(f"{site['id']}: {len(rows)} photos with data, lost (0 bytes, both copies): "
          f"{lost or 'none'}")
    for r in rows:
        print(f"  {r['file']:26s} {r['local'][11:19]}  sun az {r['sun_az']:6.1f}°  "
              f"el {r['sun_el']:5.1f}°  shadow -> {r['shadow_az']:6.1f}°  "
              f"{r['shadow_per_m']:.2f} m/m")
    folder = os.path.join(config.ROOT, site["photos"]["folder"])
    by_name = {r["file"]: r for r in rows}
    for name in site["photos"].get("key", []):
        if name in by_name:
            _annotate(os.path.join(folder, name),
                      os.path.join(out, name.replace("(1)", "").replace(".jpg", "_sunce.jpg")),
                      by_name[name])

    results = {}
    for tilt in site["array"]["tilts"]:
        s = config.with_tilt(site, tilt)
        df, _ = pvgis.hourly(s, tilt, s["array"]["azimuth_deg"], offline=offline)
        base_kw, temp, *_ = model.pv_series(site, tilt, offline)
        k0, *_ = model.dispatch(s, base_kw, temp)
        res = {"bez prepreke (DEM)": _brief(k0, None, None)}
        for ob in site.get("obstacles", []):
            for label, case in cases(ob).items():
                sil = silhouette(site, ob, case, tilt)
                shaded, frac = shade(df, s, tilt, sil, ob["opacity_monthly"])
                chain, _ = pv.dc_chain(shaded, s, tilt, s["array"]["azimuth_deg"])
                k, *_ = model.dispatch(s, chain["p_bus"] / 1000.0, temp)
                res[f"{ob['name']}: {label}"] = _brief(k, sil, case)
        results[f"{tilt:g}"] = res

    print()
    for t, res in results.items():
        print(f"== {site['id']} {t}°")
        base = res["bez prepreke (DEM)"]
        for label, r in res.items():
            sil = r.get("silhouette")
            geo = (f"  [az {sil['az']:.0f}° ±{sil['hw']:.0f}°, do {sil['el']:.0f}°, "
                   f"{sil['r']:.1f} m]" if sil else "")
            print(f"  {label:32s} FN {r['pv_bus_kwh']:7.0f} kWh  dec {r['dec_pv_kwh']:4.0f} "
                  f"({100 * (r['dec_pv_kwh'] / base['dec_pv_kwh'] - 1):+5.1f} %)  DEA "
                  f"{r['genset_h_mean']:4.0f} h / P90 {r['genset_h_p90']:4.0f}  gorivo "
                  f"{r['fuel_l_mean']:5.0f} l{geo}")
    doc = {"photos": rows, "lost": lost, "obstacles": site.get("obstacles", []),
           "array_position": site["array_position"], "results": results}
    with open(os.path.join(out, "zasjenjenje.json"), "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=1, ensure_ascii=False)
    return 0


def _brief(k, sil, case):
    r = {key: k[key] for key in ("pv_bus_kwh", "dec_pv_kwh", "genset_h_mean",
                                 "genset_h_p90", "fuel_l_mean", "tank_years_mean")}
    if sil:
        r["silhouette"], r["case"] = sil, case
    return r
