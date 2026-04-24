import subprocess
import os
import pandas as pd
import numpy as np
from logger import log_info, log_error, log_success

def build_octree(sky_file, objects_file, output_oct="scene.oct"):
    """
    Kreira octree fajl koristeći oconv. 
    VAŽNO: objects_file ne smije sadržati 'box' primitiv!
    """
    if not os.path.exists(sky_file) or not os.path.exists(objects_file):
        log_error(f"Fajlovi nedostaju: {sky_file} ili {objects_file}")
        return None

    cmd = ['oconv', sky_file, objects_file]
    
    try:
        with open(output_oct, 'wb') as f:
            result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, check=True)
        return output_oct
    except subprocess.CalledProcessError as e:
        log_error(f"Radiance oconv crash: {e.stderr.decode()}")
        return None

def run_sensor_simulation(octree_file, sensor_file):
    """
    Pokreće rtrace simulaciju za senzore definisane u .pts fajlu.
    Vraća prosječnu iradijaciju u W/m2.
    """
    if not octree_file or not os.path.exists(octree_file):
        return 0.0

    # rtrace parametri za preciznu simulaciju (-I+ je mod za iradijaciju)
    cmd = [
        'rtrace', '-I+', '-h', 
        '-ab', '3',    # Broj ambijentalnih odbitaka
        '-ad', '2048', # Ambient divisions
        '-as', '1024', # Ambient samples
        octree_file
    ]

    try:
        with open(sensor_file, 'r') as s_in:
            process = subprocess.run(cmd, stdin=s_in, capture_output=True, text=True, check=True)
        
        # Radiance vraća RGB vrijednosti; za iradijaciju koristimo standardni 179 faktor konverzije 
        # ili direktno čitamo ako je podešeno. Ovdje parsiramo prosjek svih senzora.
        lines = process.stdout.strip().split('\n')
        irradiances = []
        for line in lines:
            vals = line.split()
            if len(vals) >= 3:
                # W/m2 = (0.265*R + 0.670*G + 0.065*B) * 179 (ako je photometric)
                # Ali sa -I+ rtrace često vraća direktne vrijednosti
                avg_val = (float(vals[0]) + float(vals[1]) + float(vals[2])) / 3.0
                irradiances.append(avg_val)
        
        return np.mean(irradiances) if irradiances else 0.0
        
    except Exception as e:
        log_error(f"rtrace greška: {e}")
        return 0.0