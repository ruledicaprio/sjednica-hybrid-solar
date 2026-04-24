import os
import json
from typing import Dict, Any
from logger import log_info, log_error

def load_json_file(filename: str) -> Dict[str, Any]:
    """Generička funkcija za učitavanje JSON fajla."""
    base_path = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(base_path, filename)
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Fajl nije pronađen: {filepath}")
        
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_equipment_data() -> Dict[str, Any]:
    """Učitava bazu opreme."""
    log_info("Učitavam equipment_database.json...")
    return load_json_file('equipment_database.json')

def load_scenarios() -> Dict[str, Any]:
    """Učitava konfiguraciju scenarija."""
    log_info("Učitavam scenarios_config.json...")
    return load_json_file('scenarios_config.json')