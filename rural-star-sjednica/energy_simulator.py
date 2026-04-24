import pandas as pd
import numpy as np
import pvlib
from logger import log_info, log_warning

def calculate_poa_irradiance_simple(row, tilt, azimuth):
    """Pojednostavljena funkcija za fallback (bez .values grešaka)."""
    lat, lon = 42.94483338639821, 18.323625614573174
    
    # Solarna pozicija
    solpos = pvlib.solarposition.get_solarposition(row.name, lat, lon)
    zenith = float(solpos['apparent_zenith'].iloc[0])
    azimuth_sun = float(solpos['azimuth'].iloc[0])
    
    dni = float(row.get('dni', 0) or 0)
    dhi = float(row.get('dhi', 0) or 0)
    ghi = float(row.get('ghi', 0) or 0)
    
    poa = pvlib.irradiance.get_total_irradiance(
        surface_tilt=tilt,
        surface_azimuth=azimuth,
        solar_zenith=zenith,
        solar_azimuth=azimuth_sun,
        dni=dni,
        ghi=ghi,
        dhi=dhi
    )
    return float(poa['poa_global'].iloc[0])

def simulate_energy_balance(config, equipment, weather_df, radiance_results=None):
    """
    Simulira energetski bilans sat po sat.
    """
    log_info("Pokrećem detaljnu energetsku simulaciju...")
    
    # Parametri
    n_panels = config.get('n_panels', 12)
    panel_power = equipment['panels']['Huawei_IPV540-M1A']['power_wp']
    panel_area = equipment['panels']['Huawei_IPV540-M1A']['area_m2']
    efficiency = equipment['panels']['Huawei_IPV540-M1A']['efficiency']
    bifaciality = equipment['system_parameters'].get('bifaciality_factor', 0.80)
    
    # Baterija
    batt_capacity_kwh = config.get('battery_capacity_kwh', 46.08) # 6x150Ah @ 48V
    soc_min = 0.15
    soc_max = 0.95
    soc = 0.50
    
    # Potrošači
    load_base = config.get('load_base_w', 820.0)
    cooling_factor = config.get('load_cooling_factor', 0.0)
    cooling_power = config.get('cooling_power_w', 0.0)
    
    # Generator
    gen_power_kw = config.get('gen_power_kw', 13.5)
    gen_fuel_eff = config.get('gen_fuel_eff_l_kwh', 0.35)
    gen_runtime = 0
    fuel_consumed = 0.0
    
    # Rezultati
    pv_gen_wh = 0.0
    load_cons_wh = 0.0
    min_soc = 1.0
    sum_soc = 0.0
    blackout_hours = 0
    
    df = weather_df.copy()
    
    # Priprema irradijance
    if radiance_results is not None and not radiance_results.empty:
        log_info("Koristim Radiance rezultate za irradijancu.")
        df['poa_front'] = radiance_results['poa_front']
        df['poa_back'] = radiance_results['poa_back']
        df['poa_total'] = df['poa_front'] + (df['poa_back'] * bifaciality)
    else:
        log_warning("Nema Radiance rezultata. Koristim PVLib fallback.")
        tilt = config.get('tilt_angle', 45.0)
        azimuth = config.get('azimuth_angle', 180.0) # Jug
        poa_list = []
        for idx, row in df.iterrows():
            poa_list.append(calculate_poa_irradiance_simple(row, tilt, azimuth))
        df['poa_total'] = poa_list
        df['poa_front'] = df['poa_total'] # Fallback pretpostavka
        df['poa_back'] = df['poa_total'] * 0.1

    # Petlja sat po sat
    for i, row in df.iterrows():
        # 1. Proizvodnja
        poa = float(row['poa_total']) # Osiguraj float
        p_dc = poa * panel_area * n_panels * efficiency # W
        pv_gen_wh += p_dc
        
        # 2. Potrošnja
        temp = float(row.get('temp_air', 20.0))
        cooling_load = cooling_power if (cooling_factor > 0 and temp > 25) else 0.0
        total_load = load_base + cooling_load
        load_cons_wh += total_load
        
        # 3. Bilans
        net_energy = p_dc - total_load # Wh
        
        # 4. Baterija
        if net_energy > 0:
            # Punjenje
            energy_to_store = net_energy
            max_charge = (soc_max - soc) * batt_capacity_kwh * 1000
            if energy_to_store > max_charge:
                energy_to_store = max_charge # Ostatak se gubi
            soc += energy_to_store / (batt_capacity_kwh * 1000)
        else:
            # Pražnjenje
            energy_needed = abs(net_energy)
            max_discharge = (soc - soc_min) * batt_capacity_kwh * 1000
            
            if energy_needed <= max_discharge:
                soc -= energy_needed / (batt_capacity_kwh * 1000)
            else:
                # Nedostatak energije -> Generator
                deficit = energy_needed - max_discharge
                soc = soc_min
                
                # Pokreni generator
                gen_energy_kwh = deficit / 1000.0
                # Generator radi minimalno 15 min ili dok ne pokrije deficit
                runtime_h = max(0.25, gen_energy_kwh / gen_power_kw) 
                gen_runtime += runtime_h * 60 # minuti
                fuel_consumed += gen_energy_kwh * gen_fuel_eff
                
                # Ako generator ne može pokriti deficit (rijetko), blackout
                if gen_energy_kwh < deficit/1000.0: # Provjera snage
                     # U ovom jednostavnom modelu pretpostavljamo da generator uvijek pokriva
                     pass

        # Statistika
        if soc < min_soc: min_soc = soc
        sum_soc += soc
        if soc <= soc_min and net_energy < 0 and gen_power_kw == 0: # Ako nema generatora
            blackout_hours += 1
            
        # Sigurnosne granice
        soc = max(soc_min, min(soc_max, soc))

    avg_soc = (sum_soc / len(df)) * 100
    
    results = {
        'pv_generation_wh': int(pv_gen_wh),
        'load_consumption_wh': int(load_cons_wh),
        'generator_runtime_minutes': int(gen_runtime),
        'fuel_consumption_liters': float(fuel_consumed),
        'min_soc_percent': float(min_soc * 100),
        'avg_soc_percent': float(avg_soc),
        'blackout_hours': int(blackout_hours)
    }
    
    return results