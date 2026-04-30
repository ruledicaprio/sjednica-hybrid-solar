import pandas as pd
import numpy as np
import pvlib
from typing import Dict, Any, Tuple
from logger import log_info, log_warning, log_success, log_error
from datetime import datetime
# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DAY_START = 8   # 08:00 — business hours boost window start
DAY_END   = 17  # 17:00 — business hours boost window end

RAN_HARD_CAP_W  = 900.0   # Absolute RAN ceiling including boost
MPLS_RESERVE_KWH = 14.4   # 72h × 200W — reserved for Scenario C autonomy

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _is_day(hour: int) -> bool:
    """True during business hours (08:00–17:00)."""
    return DAY_START <= hour < DAY_END


def calculate_poa_irradiance_simple(
    df_weather: pd.DataFrame, tilt: float, azimuth: float,
    lat: float, lon: float
) -> pd.Series:
    """PVLib POA irradiance fallback — used when Radiance results are absent."""
    log_info("Računam solarne pozicije i irradijancu (PVLib fallback)...")
    solpos = pvlib.solarposition.get_solarposition(df_weather.index, lat, lon)
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


def _calc_pv_power(row: pd.Series, scenario: Dict, equipment: Dict) -> float:
    """
    Compute PV output (W) for one hour.
    Uses poa_front / poa_back if present, otherwise falls back to production_w.
    Applies bifaciality, panel efficiency, area, count.
    """
    panel    = equipment['panels']['Huawei_IPV540-M1A']
    n_panels = scenario.get('n_panels', 12)
    bf       = scenario.get('bifaciality_factor',
               equipment['system_parameters'].get('bifaciality_factor', 0.80))
    eff      = panel['efficiency']
    area     = panel['area_m2']
    max_p    = n_panels * panel['power_wp'] * 1.5  # 150 % STC safety cap

    if 'poa_front' in row.index and row.get('poa_front', 0) > 0:
        front = float(row.get('poa_front', 0))
        back  = float(row.get('poa_back',  0))
        # Sanity clamp — Radiance can produce spikes
        front = max(0.0, min(front, 2500.0))
        back  = max(0.0, min(back,  1000.0))
        gen_w = (front + back * bf) * area * eff * n_panels
    elif 'production_w' in row.index:
        gen_w = float(row.get('production_w', 0))
    else:
        gen_w = 0.0

    return max(0.0, min(gen_w, max_p))


def _battery_capacity_wh(scenario: Dict, equipment: Dict) -> Tuple[float, float, float]:
    """
    Returns (total_wh, soc_min, soc_max) for the PowerCube battery bank.
    Scenario B adds the MTS9302 bank on the shared bus.
    """
    batt_model = scenario.get('battery_model', 'ESM-48150B1')
    batt_conf  = equipment['batteries'][batt_model]
    n_batt     = scenario.get('n_battery_modules', 6)
    powercube_wh = batt_conf['energy_kwh'] * n_batt * 1000.0

    mts_wh = 0.0
    if scenario.get('has_mts') and 'mts_battery_model' in scenario:
        mts_conf   = equipment['batteries'][scenario['mts_battery_model']]
        mts_wh     = mts_conf['total_energy_kwh'] * 1000.0  # 2×7.68 = 15 360 Wh

    total_wh = powercube_wh + mts_wh
    soc_min  = batt_conf.get('min_soc', 0.15)
    soc_max  = batt_conf.get('max_soc', 0.95)
    return total_wh, soc_min, soc_max


# ---------------------------------------------------------------------------
# Load calculators — one per scenario
# ---------------------------------------------------------------------------

def _load_scenario_a(hour: int, lp: Dict) -> float:
    """
    Scenario A: RAN + ancillaries + genset standby loads.
    No MPLS, no MTS.
    """
    ran_base = lp.get('RAN_base_w', 670.0)
    ran_w    = ran_base * lp.get('RAN_day_boost', 1.20) if _is_day(hour) else ran_base
    ran_w    = min(ran_w, RAN_HARD_CAP_W)

    monitoring_w = lp.get('Monitoring_w', 7.0)     # 70W * 0.1 duty
    icc_w        = lp.get('ICC_w', 50.0)
    cooling_w    = lp.get('Cooling_w', 100.0)
    trickle_w    = lp.get('Genset_trickle_w', 3.0)  # always on
    heater_w     = lp.get('Genset_heater_w', 15.0)  # 50W * 0.3 duty

    return ran_w + monitoring_w + icc_w + cooling_w + trickle_w + heater_w


def _load_scenario_b(hour: int, lp: Dict, genset_running: bool) -> float:
    """
    Scenario B: RAN + MPLS + SMU parasitic + genset auxiliaries.
    Both trickle (3W) and heater (50W*0.3=15W) always active.
    Genset aux (50W*0.2=10W) active only while engine is running.
    """
    ran_base  = lp.get('RAN_base_w', 670.0)
    ran_w     = ran_base * lp.get('RAN_day_boost', 1.20) if _is_day(hour) else ran_base
    ran_w     = min(ran_w, RAN_HARD_CAP_W)

    mpls_base = lp.get('MPLS_base_w', 200.0)
    mpls_w    = mpls_base * lp.get('MPLS_day_boost', 1.10) if _is_day(hour) else mpls_base

    monitoring_w     = lp.get('Monitoring_w', 7.0)
    icc_w            = lp.get('ICC_w', 50.0)
    cooling_w        = lp.get('Cooling_w', 100.0)
    smu_w            = lp.get('SMU_parasitic_w', 40.0)
    trickle_w        = lp.get('Genset_trickle_w', 3.0)
    heater_w         = lp.get('Genset_heater_w', 15.0)
    aux_running_w    = lp.get('Genset_aux_running_w', 10.0) if genset_running else 0.0

    return (ran_w + mpls_w + monitoring_w + icc_w +
            cooling_w + smu_w + trickle_w + heater_w + aux_running_w)


def _load_scenario_c(hour: int, lp: Dict, rru_shed: bool) -> Tuple[float, float, float]:
    """
    Scenario C: RAN + MPLS in PowerCube. No genset, no MTS.
    Returns (total_load_w, ran_component_w, mpls_component_w).
    When rru_shed=True, RAN drops to MMU-only (200W).
    """
    if rru_shed:
        ran_w = lp.get('RAN_shed_w', 200.0)
    else:
        ran_base = lp.get('RAN_base_w', 670.0)
        ran_w    = ran_base * lp.get('RAN_day_boost', 1.20) if _is_day(hour) else ran_base
        ran_w    = min(ran_w, RAN_HARD_CAP_W)

    mpls_base = lp.get('MPLS_base_w', 200.0)
    mpls_w    = mpls_base * lp.get('MPLS_day_boost', 1.10) if _is_day(hour) else mpls_base

    monitoring_w = lp.get('Monitoring_w', 7.0) if not rru_shed else 0.0
    icc_w        = lp.get('ICC_w', 50.0)
    cooling_w    = lp.get('Cooling_w', 100.0)  if not rru_shed else 0.0

    total_w = ran_w + mpls_w + monitoring_w + icc_w + cooling_w
    return total_w, ran_w, mpls_w


# ---------------------------------------------------------------------------
# Scenario simulators
# ---------------------------------------------------------------------------

def _run_scenario_a(df: pd.DataFrame, scenario: Dict, equipment: Dict) -> pd.DataFrame:
    """Scenario A — PowerCube baseline with genset backup."""
    log_info("▶  Scenario A: PowerCube RAN + genset...")
    lp = scenario.get('load_profile', {})
    total_wh, soc_min, soc_max = _battery_capacity_wh(scenario, equipment)
    gen_conf = equipment['generators'].get('FG_Wilson_P13.5-6', {})
    soc = soc_max

    rows = []
    for ts, row in df.iterrows():
        hour    = ts.hour
        pv_w    = _calc_pv_power(row, scenario, equipment)
        load_w  = _load_scenario_a(hour, lp)
        net_wh  = pv_w - load_w

        soc += net_wh / total_wh
        gen_kwh = 0.0
        genset_running = False

        if soc < soc_min:
            deficit_wh = (soc_min - soc) * total_wh
            gen_kwh    = deficit_wh / 1000.0
            soc        = soc_min
            genset_running = True

        soc = min(soc, soc_max)
        fuel_l = gen_kwh * gen_conf.get('fuel_consumption_l_kwh_50_load', 0.35)

        rows.append({
            'scenario': 'A_PowerCube',
            'pv_w': pv_w,
            'load_w': load_w,
            'soc_pct': soc * 100,
            'generator_kwh': gen_kwh,
            'fuel_liters': fuel_l,
            'genset_running': genset_running,
            'rru_shed': False,
            'blackout_risk': False,
        })

    return pd.DataFrame(rows, index=df.index)


def _run_scenario_b(df: pd.DataFrame, scenario: Dict, equipment: Dict) -> pd.DataFrame:
    """Scenario B — MTS9302 + PowerCube shared bus, RAN + MPLS, genset backup."""
    log_info("▶  Scenario B: MTS9302 + PowerCube shared bus + genset...")
    lp = scenario.get('load_profile', {})
    total_wh, soc_min, soc_max = _battery_capacity_wh(scenario, equipment)
    gen_conf = equipment['generators'].get('FG_Wilson_P13.5-6', {})
    soc = soc_max

    rows = []
    for ts, row in df.iterrows():
        hour           = ts.hour
        pv_w           = _calc_pv_power(row, scenario, equipment)
        genset_running = False  # will update after SoC check
        load_w         = _load_scenario_b(hour, lp, genset_running=False)
        net_wh         = pv_w - load_w

        soc += net_wh / total_wh
        gen_kwh = 0.0

        if soc < soc_min:
            deficit_wh     = (soc_min - soc) * total_wh
            gen_kwh        = deficit_wh / 1000.0
            soc            = soc_min
            genset_running = True
            # Recalculate load with genset aux included
            load_w = _load_scenario_b(hour, lp, genset_running=True)

        soc = min(soc, soc_max)
        fuel_l = gen_kwh * gen_conf.get('fuel_consumption_l_kwh_50_load', 0.35)

        rows.append({
            'scenario': 'B_MTS9302',
            'pv_w': pv_w,
            'load_w': load_w,
            'soc_pct': soc * 100,
            'generator_kwh': gen_kwh,
            'fuel_liters': fuel_l,
            'genset_running': genset_running,
            'rru_shed': False,
            'blackout_risk': False,
        })

    return pd.DataFrame(rows, index=df.index)


def _run_scenario_c(df: pd.DataFrame, scenario: Dict, equipment: Dict) -> pd.DataFrame:
    """
    Scenario C — PV-only, RAN + MPLS, no genset.
    Load shedding: RRUs drop to MMU-only when SoC reserve for 72h MPLS autonomy
    (14.4 kWh) is breached. Blackout risk flagged when even MMU-only cannot be
    sustained.
    DoD cap: 85 % (soc_min raised to 1 - 0.85 = 0.15, but usable limited by
    MPLS reserve).
    """
    log_info("▶  Scenario C: PV-only RAN + MPLS, load shedding active...")
    lp = scenario.get('load_profile', {})
    total_wh, soc_min, soc_max = _battery_capacity_wh(scenario, equipment)

    # DoD = 85 % → usable = total * 0.85
    usable_wh       = total_wh * scenario.get('autonomy', {}).get('dod_max', 0.85)
    mpls_reserve_wh = MPLS_RESERVE_KWH * 1000.0  # 14 400 Wh

    # SoC level below which we enter RRU shedding to protect MPLS reserve
    shed_soc_threshold = soc_min + (mpls_reserve_wh / total_wh)

    soc = soc_max
    rows = []

    for ts, row in df.iterrows():
        hour = ts.hour

        # Determine shedding state BEFORE computing load
        rru_shed      = soc <= shed_soc_threshold
        blackout_risk = soc <= soc_min

        load_w, ran_w, mpls_w = _load_scenario_c(hour, lp, rru_shed)
        pv_w   = _calc_pv_power(row, scenario, equipment)
        net_wh = pv_w - load_w

        soc += net_wh / total_wh
        soc  = max(soc_min, min(soc, soc_max))

        rows.append({
            'scenario': 'C_PVOnly',
            'pv_w': pv_w,
            'load_w': load_w,
            'ran_w': ran_w,
            'mpls_w': mpls_w,
            'soc_pct': soc * 100,
            'generator_kwh': 0.0,
            'fuel_liters': 0.0,
            'genset_running': False,
            'rru_shed': rru_shed,
            'blackout_risk': blackout_risk,
        })

    n_shed     = sum(r['rru_shed']      for r in rows)
    n_blackout = sum(r['blackout_risk'] for r in rows)
    log_warning(f"  RRU shed hours: {n_shed} | Blackout-risk hours: {n_blackout}")

    return pd.DataFrame(rows, index=df.index)


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def simulate_energy_balance(
    df: pd.DataFrame,
    scenario_config: Dict[str, Any],
    equipment: Dict[str, Any]
) -> pd.DataFrame:
    """
    Single-scenario entry point (called from run_simulation.py for backwards
    compatibility). Dispatches to the correct engine based on scenario keys.
    """
    assert isinstance(df.index, pd.DatetimeIndex), "Indeks mora biti DatetimeIndex"
    name = scenario_config.get('description', 'unknown')
    log_info(f"🔋 Simuliram energetski balans: {name}")

    if scenario_config.get('has_mts'):
        return _run_scenario_b(df, scenario_config, equipment)
    elif not scenario_config.get('has_genset') and scenario_config.get('has_mpls'):
        return _run_scenario_c(df, scenario_config, equipment)
    else:
        return _run_scenario_a(df, scenario_config, equipment)


def simulate_all_scenarios(
    df: pd.DataFrame,
    full_config: Dict[str, Any],
    equipment: Dict[str, Any]
) -> pd.DataFrame:
    """
    Runs all three scenarios and returns a single combined DataFrame with a
    'scenario' column for easy comparison. Saves per-scenario CSVs too.

    Usage:
        from energy_simulator import simulate_all_scenarios
        combined = simulate_all_scenarios(weather_df, full_config, equipment)
        combined.to_csv('results/all_scenarios.csv')
    """
    import os
    os.makedirs('results', exist_ok=True)

    scenario_keys = {
        'A': 'scenario_A_PowerCube',
        'B': 'scenario_B_MTS9302',
        'C': 'scenario_C_PVOnly',
    }

    frames = []
    for label, key in scenario_keys.items():
        if key not in full_config:
            log_warning(f"Scenario {label} ({key}) nije pronađen u konfiguraciji — preskačem.")
            continue

        sc = full_config[key]
        log_info(f"━━━ Scenario {label}: {sc.get('description', key)} ━━━")

        if label == 'A':
            res = _run_scenario_a(df, sc, equipment)
        elif label == 'B':
            res = _run_scenario_b(df, sc, equipment)
        else:
            res = _run_scenario_c(df, sc, equipment)

        # Per-scenario CSV
        csv_path = f"results/scenario_{label}_results.csv"
        res.to_csv(csv_path)
        log_success(f"  💾 Sačuvano: {csv_path}")

        frames.append(res)

    combined = pd.concat(frames)

    # Summary table
    log_info("\n📊 GODIŠNJI SAŽETAK:")
    for sc_name, grp in combined.groupby('scenario'):
        pv_kwh  = grp['pv_w'].sum() / 1000
        load_kwh = grp['load_w'].sum() / 1000
        gen_kwh  = grp['generator_kwh'].sum()
        fuel_l   = grp['fuel_liters'].sum()
        shed_h   = grp['rru_shed'].sum()
        risk_h   = grp['blackout_risk'].sum()
        log_success(
            f"  {sc_name}: PV={pv_kwh:.0f}kWh | Load={load_kwh:.0f}kWh | "
            f"Genset={gen_kwh:.0f}kWh | Fuel={fuel_l:.0f}L | "
            f"RRU_shed={shed_h}h | Blackout_risk={risk_h}h"
        )

    combined.to_csv('results/all_scenarios_comparison.csv')
    log_success("✅ Kombinirani CSV: results/all_scenarios_comparison.csv")

    return combined