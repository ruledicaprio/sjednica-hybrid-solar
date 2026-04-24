import os
import subprocess
from typing import List, Dict, Any
from logger import log_info, log_success, log_error

def build_octree(sky_file: str, object_files: List[str], scene_path: str) -> str:
    """
    Spaja nebo i objekte u .oct fajl spreman za simulaciju.
    """
    oct_name = os.path.basename(sky_file).replace(".rad", ".oct")
    oct_path = os.path.join(scene_path, oct_name)
    
    # Komanda oconv spaja sve elemente
    command = ["oconv", sky_file] + object_files
    
    try:
        with open(oct_path, "wb") as f:
            subprocess.run(command, stdout=f, check=True)
        return oct_path
    except Exception as e:
        log_error(f"Greška pri kreiranju octree fajla: {e}")
        return ""

def run_sensor_simulation(oct_file: str, sensors_file: str) -> List[float]:
    """
    Ispaljuje zrake na senzore (panele) i vraća vrijednosti zračenja (W/m2).
    """
    # rtrace parametri:
    # -I+: računaj iradijaciju (W/m2)
    # -h: bez zaglavlja
    # -ab 3: 3 odbijanja (ključno za bifacijalnu analizu)
    command = [
        "rtrace", "-I+", "-h", "-ab", "3", "-ad", "2048", "-as", "1024", oct_file
    ]
    
    try:
        with open(sensors_file, "r") as s_in:
            result = subprocess.check_output(command, stdin=s_in).decode('utf-8')
        
        # Radiance vraća RGB (3 vrijednosti), uzimamo prosjek kao iradijaciju
        irradiances = []
        for line in result.splitlines():
            vals = [float(v) for v in line.split()]
            if vals:
                avg_irr = (vals[0] + vals[1] + vals[2]) / 3.0
                irradiances.append(avg_irr)
        return irradiances
    except Exception as e:
        log_error(f"Simulacija nije uspjela: {e}")
        return []