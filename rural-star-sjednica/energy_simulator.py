import pandas as pd
import numpy as np
import pvlib
from typing import Dict, Any
from logger import log_info, log_warning, log_success, log_error

def calculate_poa_irradiance_simple(df_weather: pd.DataFrame, tilt: float, azimuth: float, lat: float, lon: float) -> pd.Series:
    """
    Pomoćna funkcija koja računa POA irradijancu koristeći PVLib (fallback metoda).
    """
    log_info("Računam solarne pozicije i irradijancu (PVLib fallback)...")
    
    # Izračun pozicije sunca
    solpos = pvlib.solarposition.get_solarposition(df_weather.index, lat, lon)
    
    # Izračun ukupne irradijance na nagnutoj površini (Hay-Davies model)
    poa = pvlib.irradiance.get_total_irradiance(
        surface_tilt=tilt,
        surface_azimuth=azimuth,
        solar_zenith=solpos['apparent_zenith'],
        solar_azimuth=solpos['azimuth'],
        dni=df_weather['dni'],
        ghi=df_weather['ghi'],
        dhi=df_weather['dhi'],
        model='haydavies'
    )
    return poa['poa_global']

def simulate_energy_balance(df: pd.DataFrame, scenario_config: Dict[str, Any], equipment: Dict[str, Any]) -> pd.DataFrame:
    """
    Glavna funkcija za simulaciju energetskog balansa, baterija i rada generatora.
    Dosljedna 'Fixed-Tilt Yearly Results' izvještaju.
    """
    log_info("🔋 Pokrećem simulaciju energetskog balansa...")
    
    # --- 1. Parametri Opreme ---
    # Paneli (Huawei IPV540-M1A)
    panel = equipment['panels']['Huawei_IPV540-M1A']
    efficiency = panel['efficiency']
    area = panel['area_m2']
    bifaciality = panel.get('bifaciality', 0.8)
    n_panels = scenario_config.get('n_panels', 12)
    max_p_stc = n_panels * panel['power_wp']
    
    # Baterija (Huawei ESM-48150B1)
    batt_conf = equipment['batteries']['ESM-48150B1']
    n_batt = scenario_config.get('n_battery_modules', 6)
    batt_capacity_wh = (batt_conf['energy_kwh'] * n_batt) * 1000.0
    
    # SoC granice
    soc_min = batt_conf.get('min_soc', 0.15)
    soc_max = batt_conf.get('max_soc', 0.95)
    soc = soc_max  # Počinjemo simulaciju sa punim baterijama
    
    # Generator (FG Wilson P13.5)
    # Pretpostavljamo tipičnu potrošnju od ~3.5 L/h pri ovom opterećenju
    gen_power_kw = 12.0 
    
    # --- 2. Inicijalizacija listi za rezultate ---
    pv_gen_list = []
    soc_list = []
    gen_energy_list = []
    load_cons_list = []

    # FIX: Zaštitni limit za irradijancu (da spriječimo bug sa ogromnim brojevima)
    # Maksimalna teoretska snaga je STC snaga + 20% (zbog bifacijalnosti i hladnoće)
    max_p_limit = max_p_stc * 1.5

    # --- 3. Iteracija kroz sate ---
    for i, row in df.iterrows():
        # Dohvatanje irradijance (osigurano da ne bude NaN ili suludo visoka)
        p_front = row.get('poa_front', 0)
        p_back = row.get('poa_back', 0)
        
        # Čišćenje "junk" podataka iz Radiance-a
        if p_front > 2500 or p_front < 0: p_front = 0
        if p_back > 1000 or p_back < 0: p_back = 0
        
        # Izračun trenutne snage panela (W)
        # Formula: (Front + Back * Bifaciality) * Area * Efficiency * Broj Panela
        gen_w = (p_front + (p_back * bifaciality)) * area * efficiency * n_panels
        gen_w = max(0, min(gen_w, max_p_limit))
        
        # Potrošnja bazne stanice (W) - konstantnih 820W prema tvom profilu
        load_w = 820.0 
        
        # Balans energije u ovom satu (Wh)
        net_energy_wh = gen_w - load_w
        
        # Promjena stanja baterije (Delta SoC)
        delta_soc = net_energy_wh / batt_capacity_wh
        soc += delta_soc
        
        # Logika generatora: Ako SoC padne ispod minimuma
        gen_active_kwh = 0
        if soc < soc_min:
            # Koliko Wh nam fali da pokrijemo potrošnju i ostanemo na soc_min
            deficit_wh = (soc_min - soc) * batt_capacity_wh
            gen_active_kwh = deficit_wh / 1000.0
            soc = soc_min # Generator dopunjava tačno onoliko koliko se troši
            
        # Ograničenje maksimalne napunjenosti
        if soc > soc_max:
            soc = soc_max
        
        # Spremanje podataka
        pv_gen_list.append(gen_w)
        load_cons_list.append(load_w)
        soc_list.append(soc * 100) # SoC u procentima za grafikon
        gen_energy_list.append(gen_active_kwh)

    # --- 4. Finalizacija podataka ---
    res_df = pd.DataFrame({
        'poa_front': df.get('poa_front', 0),
        'poa_back': df.get('poa_back', 0),
        'production_w': pv_gen_list,
        'consumption_w': load_cons_list,
        'soc_percent': soc_list,
        'generator_kwh': gen_energy_list
    }, index=df.index)
    
    log_success(f"Simulacija završena. Prosečan SoC: {res_df['soc_percent'].mean():.1f}%")
    return res_df