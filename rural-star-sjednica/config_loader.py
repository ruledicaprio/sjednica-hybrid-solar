import os
import json
from typing import Dict, Any
from logger import log_info, log_error

# Keys in site_config.json that are NOT scenario definitions.
# These are filtered out so load_scenarios() returns only runnable scenarios.

_NON_SCENARIO_KEYS = {
    'site_config',
    'geometry_params',
    'latitude', 'longitude', 'altitude',
    'tilt_angle', 'azimuth_angle', 'albedo',
    'bifaciality_factor', 'module_clearance_height',
    'battery_capacity_kwh', 'gen_power_kw', 'n_panels',
}

def load_json_file(filename: str) -> Dict[str, Any]:
    """Generic loader for any JSON config file."""
    base_path = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(base_path, filename)

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Fajl nije pronađen: {filepath}")

    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_equipment_data() -> Dict[str, Any]:
    """Loads equipment_db.json."""
    log_info("Učitavam equipment_db.json...")
    return load_json_file('equipment_db.json')


def load_scenarios() -> Dict[str, Any]:
    """
    Loads site_config.json and returns ONLY the scenario blocks
    (keys starting with 'scenario_'), stripping out site metadata,
    geometry params, and flat top-level keys that run_simulation.py
    would otherwise mistake for a scenario.
    """
    log_info("Učitavam site_config.json (samo scenariji)...")
    raw = load_json_file('site_config.json')

    scenarios = {
        k: v for k, v in raw.items()
        if k not in _NON_SCENARIO_KEYS and isinstance(v, dict)
        and k.startswith('scenario_')
    }

    if not scenarios:
        log_error("Nisu pronađeni scenariji u site_config.json! "
                  "Svaki scenario mora početi s 'scenario_'.")
        raise ValueError("Nema scenarija u konfiguraciji.")

    log_info(f"Učitani scenariji: {list(scenarios.keys())}")
    return scenarios


def load_full_config() -> Dict[str, Any]:
    """
    Returns the complete site_config.json as-is.
    Useful for modules that need geometry_params, site_config block, etc.
    """
    return load_json_file('site_config.json')