"""PVGIS API v5.3 client with an on-disk cache.

Every response is stored gzip-compressed under pvsim/cache/, keyed by a hash of
the endpoint and its parameters, with a sidecar that records the URL, the
fetch time and the sha256 of the raw body. A run can therefore be repeated
offline and gives identical numbers: PVGIS revises its databases (the move
from SARAH2 to SARAH3 shifted yields by several per cent), so a figure that
went into the tender without a cached source could not be reproduced later.

Only the small responses (PVcalc, printhorizon, SHScalc) are also copied into
pvsim/sites/<id>/pvgis_ref/ and committed; the hourly series (~1 MB per year
of JSON) stay in the gitignored cache and are refetched on demand.
"""
from __future__ import annotations

import datetime as dt
import gzip
import hashlib
import io
import json
import os
import time

import pandas as pd
import requests

API = "https://re.jrc.ec.europa.eu/api/v5_3/"
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache")

_MIN_INTERVAL = 0.1          # PVGIS allows 30 requests/s; stay well under it
_last_call = [0.0]


class OfflineMiss(RuntimeError):
    """--offline was given and the response is not in the cache."""


def _norm(params):
    """45.0 and 45 are the same request, so they must be the same cache entry."""
    return {k: (int(v) if isinstance(v, float) and v.is_integer() else v)
            for k, v in params.items()}


def _canonical(endpoint, params):
    return endpoint + "?" + "&".join(f"{k}={params[k]}" for k in sorted(params))


def cache_path(endpoint, params):
    canon = _canonical(endpoint, params)
    key = hashlib.sha1(canon.encode("utf-8")).hexdigest()[:16]
    return os.path.join(CACHE, f"{endpoint}-{key}.json.gz")


def fetch(endpoint, params, offline=False, timeout=300):
    """Raw JSON text of one PVGIS call, from the cache when present."""
    params = _norm(dict(params, outputformat="json"))
    path = cache_path(endpoint, params)
    if os.path.exists(path):
        with gzip.open(path, "rt", encoding="utf-8") as fh:
            return fh.read()
    if offline:
        raise OfflineMiss(_canonical(endpoint, params))

    wait = _MIN_INTERVAL - (time.monotonic() - _last_call[0])
    if wait > 0:
        time.sleep(wait)
    r = requests.get(API + endpoint, params=params, timeout=timeout)
    _last_call[0] = time.monotonic()
    if not r.ok:
        try:
            msg = r.json().get("message", r.text[:300])
        except ValueError:
            msg = r.text[:300]
        raise RuntimeError(f"PVGIS {endpoint}: HTTP {r.status_code}: {msg}")

    raw = r.content
    os.makedirs(CACHE, exist_ok=True)
    with gzip.open(path + ".tmp", "wb") as fh:
        fh.write(raw)
    os.replace(path + ".tmp", path)
    meta = {"url": API + endpoint, "params": params,
            "fetched_utc": dt.datetime.now(dt.timezone.utc).isoformat(
                timespec="seconds"),
            "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
    with open(path[:-len(".json.gz")] + ".meta.json", "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=1)
    return raw.decode("utf-8")


def cache_manifest(endpoint, params):
    """Sidecar of a cached response (URL, fetch time, sha256), or None."""
    p = cache_path(endpoint, _norm(dict(params, outputformat="json")))
    side = p[:-len(".json.gz")] + ".meta.json"
    return json.load(open(side, encoding="utf-8")) if os.path.exists(side) else None


# --------------------------------------------------------------------------
def _site_params(site, userhorizon=None):
    p = {"lat": site["lat"], "lon": site["lon"],
         "raddatabase": site["pvgis"]["db"], "usehorizon": 1}
    uh = userhorizon if userhorizon is not None else site["pvgis"].get("userhorizon")
    if uh:
        p["userhorizon"] = ",".join(f"{h:g}" for h in uh)
    return p


def _plane(site, tilt, azimuth):
    # PVGIS aspect: 0 = south, -90 = east (pvlib azimuth 180 = south)
    return {"angle": tilt, "aspect": azimuth - 180}


def hourly_params(site, tilt, azimuth=180, loss=14.0, userhorizon=None):
    return (_site_params(site, userhorizon)
            | _plane(site, tilt, azimuth)
            | {"startyear": site["pvgis"]["start"], "endyear": site["pvgis"]["end"],
               "pvcalculation": 1, "peakpower": site["array"]["kWp"], "loss": loss,
               "components": 1, "pvtechchoice": "crystSi", "mountingplace": "free"})


def hourly(site, tilt, azimuth=180, loss=14.0, userhorizon=None, offline=False):
    """Hourly in-plane beam/sky/ground irradiance, sun height, T2m, WS10m and
    PVGIS's own P (W, with `loss` %) for the site's years. Index is UTC."""
    import pvlib

    params = hourly_params(site, tilt, azimuth, loss, userhorizon)
    text = fetch("seriescalc", params, offline)
    data, meta = pvlib.iotools.read_pvgis_hourly(io.StringIO(text),
                                                 pvgis_format="json",
                                                 map_variables=True)
    return data, meta


def pvcalc_params(site, tilt, azimuth=180, loss=14.0, userhorizon=None):
    return (_site_params(site, userhorizon) | _plane(site, tilt, azimuth)
            | {"peakpower": site["array"]["kWp"], "loss": loss,
               "pvtechchoice": "crystSi", "mountingplace": "free"})


def pvcalc(site, tilt, azimuth=180, loss=14.0, userhorizon=None, offline=False):
    """PVGIS's grid-connected calculator: monthly and yearly long-term means."""
    return json.loads(fetch("PVcalc",
                            pvcalc_params(site, tilt, azimuth, loss, userhorizon),
                            offline))


def horizon_params(site):
    return {"lat": site["lat"], "lon": site["lon"]}


def horizon(site, offline=False):
    """DEM horizon: azimuth (pvlib convention, north = 0, clockwise) and
    elevation in degrees."""
    d = json.loads(fetch("printhorizon", horizon_params(site), offline))
    h = pd.DataFrame(d["outputs"]["horizon_profile"])
    h["azimuth"] = (h["A"] + 180) % 360
    return h.rename(columns={"H_hor": "elevation"})[["azimuth", "elevation"]] \
        .sort_values("azimuth").drop_duplicates("azimuth").reset_index(drop=True)


def shscalc_params(site, tilt, battery_wh, cutoff_pct, load_wh_day, azimuth=180):
    return (_site_params(site) | _plane(site, tilt, azimuth)
            | {"peakpower": site["array"]["kWp"] * 1000, "batterysize": battery_wh,
               "cutoff": cutoff_pct, "consumptionday": load_wh_day})


def shscalc(site, tilt, battery_wh, cutoff_pct, load_wh_day, azimuth=180,
            offline=False):
    """PVGIS's off-grid calculator (PV + battery, no genset) - a cross-check of
    the dispatch model's PV-only behaviour, not an input to it."""
    return json.loads(fetch("SHScalc",
                            shscalc_params(site, tilt, battery_wh, cutoff_pct,
                                           load_wh_day, azimuth), offline))
