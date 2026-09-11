"""Site configuration: pvsim/sites/<id>.json merged with the site's design.json.

design.json is the tender's single record of the system (module, array,
genset, tank); the site JSON adds only what the simulation needs. Every
parameter that is an assumption rather than a vendor or project figure carries
a "_src" note, so no number in a KPI table is untraceable.
"""
from __future__ import annotations

import copy
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SITES = os.path.join(HERE, "sites")


def site_ids():
    return sorted(f[:-5] for f in os.listdir(SITES) if f.endswith(".json"))


def _parse(val):
    try:
        return json.loads(val)
    except json.JSONDecodeError:
        return val


def set_path(cfg, dotted, value):
    """`array.tilt_deg=60` -> cfg["array"]["tilt_deg"] = 60."""
    node = cfg
    keys = dotted.split(".")
    for k in keys[:-1]:
        node = node.setdefault(k, {})
    node[keys[-1]] = value


def load(site_id, overrides=()):
    path = os.path.join(SITES, f"{site_id}.json")
    if not os.path.exists(path):
        raise SystemExit(f"unknown site {site_id!r}; known: {site_ids()}")
    cfg = json.load(open(path, encoding="utf-8"))

    design = {}
    if cfg.get("design_json"):
        design = json.load(open(os.path.join(ROOT, cfg["design_json"]),
                                encoding="utf-8"))
    cfg["design"] = {k: design.get(k, {}) for k in ("module", "array", "genset",
                                                    "tank")}

    # array: the TD's design.json first, the site file on top of it
    da = cfg["design"]["array"]
    array = {"kWp": da.get("kWp"), "modules": da.get("modules_total"),
             "tilt_deg": da.get("tilt_deg"), "azimuth_deg": da.get("azimuth_deg")}
    array.update({k: v for k, v in cfg.get("array", {}).items() if v is not None})
    cfg["array"] = array

    for item in overrides:
        key, sep, val = item.partition("=")
        if not sep:
            raise SystemExit(f"--set expects key=value, got {item!r}")
        set_path(cfg, key.strip(), _parse(val.strip()))

    missing = [k for k in ("kWp", "tilt_deg", "azimuth_deg") if cfg["array"].get(k)
               is None]
    if missing:
        raise SystemExit(f"{site_id}: array.{missing} not set in design.json or "
                         f"sites/{site_id}.json")
    return cfg


def with_tilt(cfg, tilt):
    c = copy.deepcopy(cfg)
    c["array"]["tilt_deg"] = tilt
    return c
