#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import pandas as pd
from typing import Dict, Any, Optional

from logger import log_info, log_success, log_error, log_warning

# Konfiguracija
try:
    from config_loader import load_equipment_data, load_scenarios
except ImportError:
    log_error("config_loader nije pronađen.")
    sys.exit(1)

# Geometrija (Opciono)
try:
    from geometry_engine import generate_geometry_files
except ImportError:
    log_warning("geometry_engine nije pronađen.")
    def generate_geometry_files(*args, **kwargs): 
        return None

# Energija
try:
    from energy_simulator import simulate_energy_balance
except ImportError:
    log_error("energy_simulator nije pronađen.")
    sys.exit(1)

# Radiance
try:
    from radiance_engine import RadianceEngine
    RADIANCE_AVAILABLE = True
except ImportError:
    log_warning("radiance_engine nije dostupan.")
    RADIANCE_AVAILABLE = False

def load_weather_data(config):
    log_info("Učitavam vremenske podatke...")
    try:
        import pvlib
        lat = config.get('latitude', 42.94483338639821)
        lon = config.get('longitude', 18.323625614573174)
        
        log_info(f"PVGIS TMY za {lat:.4f}, {lon:.4f} (1076m)...")
        result = pvlib.iotools.get_pvgis_tmy(lat, lon, map_variables=True)
        
        # Sigurna ekstrakcija DataFrame-a
        if isinstance(result, tuple):
            df, meta = result
        else:
            df = result
            
        log_success(f"Podaci preuzeti: {len(df)} sati.")
        return df
    except Exception as e:
        log_error(f"Greška: {e}")
        # Dummy podaci
        dates = pd.date_range(start="2023-01-01", periods=8760, freq="h")
        df = pd.DataFrame(index=dates)
        df['ghi'] = 0.0; df['dni'] = 0.0; df['dhi'] = 0.0
        df['temp_air'] = 20.0; df['wind_speed'] = 1.0
        return df

def main():
    log_info("="*60)
    log_info("🚀 RURALSTAR SJEDNICA - FINALNA SIMULACIJA")
    log_info("="*60)
    
    # Konfiguracija sajta
    config = {
        'latitude': 42.94483338639821,
        'longitude': 18.323625614573174,
        'altitude': 1076,
        'n_panels': 12,
        'tilt_angle': 45.0,
        'azimuth_angle': 180.0, # Jug
        'battery_capacity_kwh': 46.08, # 6x150Ah
        'load_base_w': 820.0,
        'gen_power_kw': 13.5,
        'gen_fuel_eff_l_kwh': 0.35
    }
    
    try:
        equipment = load_equipment_data()
        # Spoji hardkodirani config sa onim iz fajla ako postoji
        scenarios = load_scenarios()
        file_config = scenarios.get('site_config', {})
        config.update(file_config)
    except Exception as e:
        log_error(f"Greška konfiguracije: {e}")
        return

    log_info("Generišem geometriju...")
    try:
        generate_geometry_files(config, equipment)
        log_success("Geometrija generisana.")
    except Exception as e:
        log_warning(f"Geometrija preskočena: {e}")

    weather_df = load_weather_data(config)
    
    radiance_results = None
    if RADIANCE_AVAILABLE:
        log_info("Pokrećem Radiance...")
        try:
            rad_engine = RadianceEngine(config, equipment)
            radiance_results = rad_engine.run_simulation(weather_df)
        except Exception as e:
            log_error(f"Radiance greška: {e}")
    else:
        log_info("Koristim PVLib (Radiance nedostupan).")

    log_info("Energetski bilans...")
    try:
        results = simulate_energy_balance(config, equipment, weather_df, radiance_results=radiance_results)
    except Exception as e:
        log_error(f"Simulacija neuspjela: {e}")
        return

    if results:
        log_success("SIMULACIJA ZAVRŠENA!")
        log_info(f"PV: {results.get('pv_generation_wh', 0)/1000:.1f} kWh")
        log_info(f"Potrošnja: {results.get('load_consumption_wh', 0)/1000:.1f} kWh")
        log_info(f"Generator: {results.get('generator_runtime_minutes', 0)/60:.1f} h")
        log_info(f"Gorivo: {results.get('fuel_consumption_liters', 0):.1f} L")
        log_info(f"Min SoC: {results.get('min_soc_percent', 0):.1f}%")

if __name__ == "__main__":
    if sys.platform == "win32":
        import io, locale
        try: locale.setlocale(locale.LC_ALL, '')
        except: pass
        for s in (sys.stdin, sys.stdout, sys.stderr):
            if isinstance(s, io.TextIOWrapper): s.reconfigure(encoding='utf-8')
    main()