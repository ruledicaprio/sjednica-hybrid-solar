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
    Vraća listu iradijacija u W/m2, jedna vrijednost po senzoru (redoslijed kao u
    .pts fajlu - ovdje: [prednja strana, zadnja strana]). Poziv u run_simulation.py
    očekuje tačno ovo (rad_irr[0], rad_irr[1]) - vraćanje jedne prosječne vrijednosti
    umjesto liste (kako je ranije pisalo ovdje) tiho je odbacivalo svaki rezultat
    (isinstance(rad_irr, (list, tuple)) je uvijek bilo False za float), pa je puna
    24-satna simulacija prolazila kroz Radiance ali završavala s praznim DataFrame-om.
    """
    if not octree_file or not os.path.exists(octree_file):
        return []

    # rtrace parametri za preciznu simulaciju (-I+ je mod za iradijaciju)
    # -n paralelizuje po zrakama; sa svega 2 senzora (prednja/zadnja strana panela)
    # korisno je najviše -n 2, veći broj procesa samo besposleno čeka.
    cmd = [
        'rtrace', '-I+', '-h',
        '-n', '2',     # paralelni procesi (ograničeno brojem senzora, ne jezgara)
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

        return irradiances

    except Exception as e:
        log_error(f"rtrace greška: {e}")
        return []