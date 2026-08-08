# -*- coding: utf-8 -*-
"""
Full-year (8760h) POA irradiance and DC energy estimate using PVLib only - no
Radiance raytracing, so no per-hour self-shading detail, but physically sound and
fast (seconds, not days). Cross-check against the earlier PVGIS-based December
figures already cited in review/01-huawei-solar.md (560-600 kWh production,
878 kWh consumption -> 280-320 kWh December deficit at 45 deg tilt).

The existing output/report_results/RuralStar_Sjednica_FINAL_REPORT.pdf is NOT used
as a reference here - it reports 115,582 kWh/yr from a 6.5 kWp system, i.e.
17,782 kWh/kWp/yr, the exact physically-impossible figure already flagged in
review/01-huawei-solar.md Lessons Learned #6 (ceiling is ~1800 kWh/kWp/yr for any
European site). That report is a known-bad artifact, not a valid baseline.
"""
import json
import os
import sys

import numpy as np
import pandas as pd
import pvlib
from pvlib.iotools import read_epw

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from logger import log_header, log_info, log_success

EPW_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "bileca_cemerno.epw")
SITE_CFG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "site_config.json")

KWP = 7.02          # actual design capacity (cad/design.json), not the report's 6.5 kWp
PERFORMANCE_RATIO = 0.80  # flat system derate: temp, wiring, soiling, inverter - not
                           # a detailed cell-temp model; documented assumption, not a
                           # precise result


def main():
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    log_header("PVLIB-ONLY FULL-YEAR ESTIMATE (no Radiance, no self-shading)")

    site_cfg = json.load(open(SITE_CFG_PATH, encoding="utf-8"))["site_config"]
    full_cfg = json.load(open(SITE_CFG_PATH, encoding="utf-8"))
    tilt = full_cfg.get("tilt_angle", 45.0)
    azimuth = full_cfg.get("azimuth_angle", 180.0)
    albedo = full_cfg.get("albedo", 0.40)
    lat = full_cfg.get("latitude", 42.9448)
    lon = full_cfg.get("longitude", 18.3236)

    source = os.environ.get("WEATHER_SOURCE", "epw").lower()
    if source == "pvgis":
        log_info(f"Izvor: PVGIS TMY API direktno za {lat}, {lon} (izbjegava "
                 f"neusklađenost nadmorske visine sa Cemerno EPW stanicom)")
        data, meta = pvlib.iotools.get_pvgis_tmy(lat, lon, map_variables=True)
        weather_alt_note = "n/a (PVGIS upit je na tačnim koordinatama, ne posebnoj stanici)"
    else:
        data, metadata = read_epw(EPW_PATH)
        weather_alt_note = metadata.get("altitude")
    log_info(f"{source.upper()} učitan: {len(data)} zapisa, "
             f"nadmorska visina izvora: {weather_alt_note}")

    # Nadmorska visina lokacije (site_config.json) za solarnu poziciju - NE visina
    # meteorološkog izvora, koja se moze razlikovati (Cemerno EPW: 1309 m vs stvarnih
    # 1076 m lokacije).
    site_alt = full_cfg.get("altitude", 1076.0)
    solpos = pvlib.solarposition.get_solarposition(data.index, lat, lon, site_alt)
    dni_extra = pvlib.irradiance.get_extra_radiation(data.index)
    airmass = pvlib.atmosphere.get_relative_airmass(solpos["apparent_zenith"])
    poa = pvlib.irradiance.get_total_irradiance(
        surface_tilt=tilt, surface_azimuth=azimuth,
        dni=data["dni"], ghi=data["ghi"], dhi=data["dhi"],
        solar_zenith=solpos["apparent_zenith"], solar_azimuth=solpos["azimuth"],
        dni_extra=dni_extra, airmass=airmass,
        albedo=albedo, model="perez",
    )
    poa_global = poa["poa_global"].clip(lower=0)

    # DC energy per hour (kWh): kWp is rated at 1000 W/m2 STC, so a hazard-free
    # DC yield estimate is kWp * (POA/1000) per hour, times a flat performance ratio.
    e_dc_kwh = KWP * (poa_global / 1000.0) * PERFORMANCE_RATIO

    annual_kwh = e_dc_kwh.sum()
    annual_poa_kwh_m2 = poa_global.sum() / 1000.0
    specific_yield = annual_kwh / KWP

    log_success(f"Godišnja POA ozračenost: {annual_poa_kwh_m2:,.0f} kWh/m2/god")
    log_success(f"Godišnja DC proizvodnja ({KWP} kWp, PR={PERFORMANCE_RATIO}): "
                f"{annual_kwh:,.0f} kWh/god")
    log_success(f"Specifični prinos: {specific_yield:,.0f} kWh/kWp/god "
                f"(fizička granica ~1800 - ovo MORA biti ispod te vrijednosti)")

    monthly = e_dc_kwh.groupby(e_dc_kwh.index.month).sum()
    month_names = ["Jan", "Feb", "Mar", "Apr", "Maj", "Jun", "Jul", "Aug",
                    "Sep", "Okt", "Nov", "Dec"]
    print("\nMjesečna DC proizvodnja (kWh):")
    for m, name in enumerate(month_names, start=1):
        val = monthly.get(m, 0.0)
        print(f"  {name}: {val:,.0f} kWh")

    dec_kwh = monthly.get(12, 0.0)
    print(f"\nDecembar: {dec_kwh:,.0f} kWh "
          f"(review/01-huawei-solar.md navodi 560-600 kWh iz PVGIS-a, za usporedbu)")

    out_dir = os.path.join(os.path.dirname(__file__), "..", "results")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "pvlib_annual_estimate.csv")
    df_out = pd.DataFrame({"poa_global_w_m2": poa_global, "e_dc_kwh": e_dc_kwh})
    df_out.to_csv(out_path)
    log_success(f"Sačuvano: {out_path}")


if __name__ == "__main__":
    main()
