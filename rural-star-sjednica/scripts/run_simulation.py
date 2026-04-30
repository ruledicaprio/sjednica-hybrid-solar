import os
import sys
import pandas as pd
import pvlib
from typing import Dict, Any

# Importi tvojih modula
from logger import log_info, log_success, log_error, log_warning, log_header
from geometry_engine import generate_geometry_files
from skies_engine import prepare_sky_simulation, generate_sky, read_epw_data
from simulation_engine import build_octree, run_sensor_simulation
from config_loader import load_equipment_data, load_scenarios, load_full_config
from energy_simulator import simulate_energy_balance
from generate_advanced_report import generate_pro_report


def run_dual_simulation(
    epw_path: str,
    scenarios: Dict[str, Any],
    equip_db: Dict[str, Any],
    site_cfg: Dict[str, Any],
) -> pd.DataFrame:
    log_header("POKRETANJE DUALNE SIMULACIJE (PVGIS EPW FIX)")

    # 1. DIREKTNO UČITAVANJE EPW PREKO PVLIB-A
    try:
        from pvlib.iotools import read_epw
        data, metadata = read_epw(epw_path)
        weather_df = data
        current_altitude = metadata.get('altitude')
        log_info(f"Izvor: {epw_path} | Visina: {current_altitude}m")
        log_success(f"✅ EPW učitan. Pronađeno {len(weather_df)} zapisa.")
    except Exception as e:
        log_error(f"Neuspjelo čitanje EPW preko pvlib: {e}")
        return pd.DataFrame()

    # 2. Mapiranje kolona
    if 'temp' not in weather_df.columns and 'temp_air' in weather_df.columns:
        weather_df['temp'] = weather_df['temp_air']

    # 3. PVLib Model — koristi site_cfg direktno
    lat = site_cfg.get('latitude', 42.9448)
    lon = site_cfg.get('longitude', 18.3236)

    log_info(f"🤖 Računam PVLib za lokaciju: {lat}, {lon} (Alt: {current_altitude}m)")

    try:
        solpos = pvlib.solarposition.get_solarposition(
            weather_df.index, lat, lon, current_altitude
        )
        poa_output = pvlib.irradiance.get_total_irradiance(
            surface_tilt=site_cfg.get('tilt_angle', 45.0),
            surface_azimuth=site_cfg.get('azimuth_angle', 180.0),
            dni=weather_df['dni'],
            ghi=weather_df['ghi'],
            dhi=weather_df['dhi'],
            solar_zenith=solpos['zenith'],
            solar_azimuth=solpos['azimuth'],
            albedo=site_cfg.get('albedo', 0.40),
        )
        poa_pvlib = pd.DataFrame(poa_output)
        log_success("✅ PVLib proračun završen.")
    except Exception as e:
        log_error(f"PVLib Crash: {e}")
        log_info(f"Dostupne kolone: {list(weather_df.columns)}")
        return pd.DataFrame()

    # 4. Radiance Priprema
    log_info("🔦 Pripremam Radiance scenu i geometriju...")
    rad_objects = generate_geometry_files(site_cfg, equip_db)  # string path
    sky_dir = prepare_sky_simulation(weather_df, site_cfg)

    scene_path = "radiance_scene"
    os.makedirs(scene_path, exist_ok=True)
    sensors_file = os.path.join(scene_path, "sensors.pts")

    with open(sensors_file, "w") as f:
        f.write("0.0 -4.0 0.5  0.0 -0.707 0.707\n")  # Front
        f.write("0.0 -4.0 0.5  0.0 0.707 -0.707\n")   # Back

    dual_results = []
    df_comp = pd.DataFrame()
    daylight = weather_df[weather_df['ghi'] > 10].head(24)
    bf = site_cfg.get('bifaciality_factor', 0.80)

    log_info(f"🚀 Pokrećem rendering za {len(daylight)} sati...")

    for timestamp, row in daylight.iterrows():
        try:
            # generate_sky vraća str (putanju do .sky fajla)
            sky_file_path = generate_sky(row, scene_path)
            if not sky_file_path:
                continue

            # FIX: rad_objects je već string, ne umotavamo ga u listu
            oct_file = build_octree(
                sky_file=sky_file_path,
                objects_file=rad_objects,
                output_oct=os.path.join(scene_path, "scene.oct"),
            )
            rad_irr = run_sensor_simulation(oct_file, sensors_file)

            if isinstance(rad_irr, (list, tuple)) and len(rad_irr) >= 2:
                try:
                    pvlib_val = poa_pvlib.at[timestamp, 'poa_global']
                except Exception:
                    pvlib_val = 0.0

                rad_front, rad_back = rad_irr[0], rad_irr[1]
                rad_total = rad_front + (rad_back * bf)

                dual_results.append({
                    'datetime': timestamp,
                    'PVLib_POA_W': pvlib_val,
                    'Radiance_Front_W': rad_front,
                    'Radiance_Back_W': rad_back,
                    'Radiance_Total_W': rad_total,
                    'Ambient_Temp': row.get('temp', row.get('temp_air', 20.0)),
                })

        except Exception as e:
            log_warning(f"Greška na {timestamp}: {e}")

    # 5. Spašavanje rezultata
    if dual_results:
        df_comp = pd.DataFrame(dual_results).set_index('datetime')
        os.makedirs("results", exist_ok=True)
        df_comp.to_csv("results/model_comparison.csv")
        log_success("✅ Dualna simulacija uspješno završena.")
    else:
        log_error("❌ Simulacija nije generisala rezultate!")

    return df_comp


def main():
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    log_header("RURALSTAR HYBRID - BILEĆA CASE STUDY")

    try:
        os.makedirs("results", exist_ok=True)

        # Učitavanje: scenariji posebno, site_config posebno
        scenarios = load_scenarios()
        equip = load_equipment_data()
        full_cfg = load_full_config()
        site_cfg = full_cfg.get('site_config', {})

        # 1. Pokretanje poređenja modela (PVLib vs Radiance)
        comp_df = run_dual_simulation(
            "..\\data\\bileca_cemerno.epw", scenarios, equip, site_cfg
        )

        if not comp_df.empty:
            log_info("🔋 Simuliram hibridni sistem (Baterije/Potrošnja)...")

            comp_df['production_w'] = comp_df['Radiance_Total_W']

            scenario_name = list(scenarios.keys())[0]
            final_data = simulate_energy_balance(
                comp_df, scenarios[scenario_name], equip
            )

            output_path = "results/final_simulation_output.csv"
            final_data.to_csv(output_path)
            log_success(f"💾 Podaci sačuvani u {output_path}")

            generate_pro_report(output_path, full_cfg)
            log_success("🏆 PRO IZVJEŠTAJ GENERISAN!")
        else:
            log_error(
                "Glavni DataFrame je prazan. "
                "Provjeri EPW fajl i Radiance putanje."
            )

    except Exception as e:
        log_error(f"Kritična greška u glavnom programu: {e}")


if __name__ == "__main__":
    main()

